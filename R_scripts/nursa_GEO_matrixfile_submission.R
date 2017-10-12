# submit GEO data with matrix file to NURSA
# author: Axel Müller
# 08/25/2016

# Make sure you are using R 3.3 or newer,
# the scrip also makes use of the following terminal commands:
# gunzip, tar, ls, grep, mv,
# Not sure if this works on Windows. I assume it should on Windows10
# write.xlsx can run out of memory, when writing the data to an xlsx file.
# I wrote it to a tsv file and used gnumeric's ssconvert to create xlsx file
# and merge the xlsx file that contains the metadata. Again, this might
# work on Windows 10 but probably not on previous Windows versions.
# GEOmetadb.sqlite should be in the same working directory, if this is not the
# case the following statement in the main script:
# con <- dbConnect(SQLite(),'GEOmetadb.sqlite')
# needs to be adjusted accordingly.
#
# Required user input:
# a sample excel spreadsheet:
sample_xlsx <- "/home/axel/projects/hirn/beta_cell/nursa/388.0.xlsx"

# GSE8873 is a series that contains a matrix file
series <- "GSE8873"

# Add some more information, eventually querying GEOmetaDB should take care
# of this:

tissue <- "islets and ductal cells"
genotype <- "NA"
# the list assigned to treat should have the control condition first, thus
# it should look like this:
# treat <- c("control", "some_condition")
# note:
# Use underscores instead of spaces!
treat <- c("control", "CD40L")
strain <- "NA"
ex_time <- "NA"


################################################################################
# ideally no user input required below:
################################################################################
# libraries

library(readxl)
library(rowr)
library(dplyr)
library(tidyr)
library(stringr)
library(xlsx)
library(magrittr)
library(readr)
library(tibble)
library(data.table)
library(feather)

# the following library is hosted on github
# library(devtools);
# install_github(repo="skranz/dplyrExtras")
library(dplyrExtras)


# the following libraries from bioconductor, installation requires:
# source("https://bioconductor.org/biocLite.R")
# and for example:
# biocLite("genomes")
#
library(genomes)

library(GEOmetadb)
# GEOmetadb requires an sqlite file
if(!file.exists('GEOmetadb.sqlite')) getSQLiteFile()
con <- dbConnect(SQLite(),'GEOmetadb.sqlite')
library(GEOquery)

################################################################################
# nursa specifics, read in sample dataset from NURSA
#

data_set_nursa <-
  read_excel(sample_xlsx,
             sheet = 1, col_names = FALSE)
data_set_nursa

experiment_nursa <-
  read_excel(sample_xlsx,
             sheet = 2, col_names = TRUE)
experiment_nursa

data_nursa <-
  read_excel(sample_xlsx,
             sheet = 3, col_names = TRUE)
data_nursa


# the table TiSSUES contains a number of lookup tables
# distributed in several areas. As a consequence of sticking
# individual tables into the same sheet, some column headers might be
# duplicated, hence I chose col_names = FALSE.

tissues_nursa <-
  read_excel(sample_xlsx,
             sheet = 4, col_names = FALSE)

# tissue lookup
tissues_lookup <- tissues_nursa %>%
  select(X0, X1) %>%
  na.omit()
colnames(tissues_lookup) <- tissues_lookup[1,]
tissues_lookup <- tissues_lookup[-1,]

# molecule lookup
molecule_lookup <- tissues_nursa %>%
  select(X3, X4) %>%
  na.omit()
colnames(molecule_lookup) <- molecule_lookup[1,]
molecule_lookup <- molecule_lookup[-1,]

# species lookup
species_lookup <- tissues_nursa %>%
  select(X8, X9) %>%
  na.omit()
colnames(species_lookup) <- species_lookup[1,]
species_lookup <- species_lookup[-1,]
# add scientific names to table:
SPECIES_SCIENTIFICNAME <- c("Mus musculus", "Homo sapiens", "Rattus norvegicus")

species_lookup <- cbind(species_lookup, SPECIES_SCIENTIFICNAME)

# dataset type lookup
data_type_lookup <- tissues_nursa %>%
  select(X6, X7) %>%
  # these columns also contain time units, which can be removed easily
  na.omit()

colnames(data_type_lookup) <- data_type_lookup[1,]
data_type_lookup <- data_type_lookup[-1,]


# ligand lookup
ligands_lookup <-
  read_excel("/home/axel/projects/hirn/beta_cell/nursa/388.0.xlsx",
                             sheet = 6, col_names = TRUE)
################################################################################


### parse meta data
################################################################################
# get info for dataset sheet:
#

# the following method of acquiring dataset names leads to complications
# as each sample may end up with a different name, ideally that shouldn't be the
# case.

dataset_name <- series

get_series_title <- paste("SELECT title",
                          "FROM gse",
                          "WHERE gse = ",
                          paste("'", series, "'", sep = ""),
                          sep = " ")
dataset_name <- dbGetQuery(con, get_series_title)

get_dataset_description <- paste("SELECT summary",
                                 "FROM gse",
                                 "WHERE gse = ",
                                 paste("'", series, "'", sep = ""),
                                 sep = " ")
dataset_descriptions <- dbGetQuery(con, get_dataset_description)

get_dataset_type <- paste("SELECT type",
                          "FROM gse",
                          "WHERE gse = ",
                          paste("'", series, "'", sep = ""),
                          sep = " ")
dataset_type <- dbGetQuery(con, get_dataset_type)

get_dataset_species <- paste("SELECT DISTINCT(organism_ch1)",
                             "FROM gsm",
                             "WHERE series_id LIKE ",
                             paste("'%", series, "%'", sep = ""),
                             sep = " ")
dataset_species <- dbGetQuery(con, get_dataset_species)

dataset_source <- gsub("'", "", series)

DatasetID <- "NA"
Comments <- "NA"
Dataset_type_id <- "NA"

dataset_sheet_headers <- c("PMID", "Dataset Name", "Dataset description",
                           "Dataset Type", "Dataset ID", "Data Source",
                           "Species", "Comments", "Datset Type ID")

Dataset_sheet <- cbind.fill(PMID, dataset_name, dataset_descriptions,
                            dataset_type, DatasetID, dataset_source,
                            dataset_species, Comments, Dataset_type_id)

colnames(Dataset_sheet) <- dataset_sheet_headers

Dataset_sheet <- Dataset_sheet %>%
  distinct()

Dataset_sheet <- t(Dataset_sheet)

Dataset_sheet <- as.data.frame(Dataset_sheet)

Dataset_sheet <- rownames_to_column(Dataset_sheet, var = "rowname")

################################################################################
# get data for Experiment sheet
# important note the field series id can contain a list! Hence, the need to
# use LIKE.

get_gsms <- paste("SELECT gsm",
                  "FROM gsm",
                  "WHERE series_id LIKE ",
                  paste("'%", series, "%'", sep = ""),
                  sep = " ")
gsms <- dbGetQuery(con, get_gsms)

# add ticks to gsms for later queries
gsms_ticks <- list()

for (i in gsms){
  gsms_ticks[i] <- paste("'", i, "'", sep = "")
}

################################################################################
# Download processed data
geo_ids <- unlist(gsms)

data_folders <- unlist(gsms)
# for now any number will do, use GSM-number without letters
internal_experiment_id <- list()
for (i in seq_along(data_folders)){
  internal_experiment_id[[i]] <- gsub("[A-Z]", "", data_folders[i], perl = TRUE)
}
internal_experiment_id <- unlist(internal_experiment_id)

# LOF loss of function should be 1 for knock-outs.
LOF <- list()
for (i in seq_along(gsms_ticks)){
  LOF[[i]] <- 0
}
LOF <- unlist(LOF)
public_experiment <- list()

get_series_summaries <- paste("SELECT title",
                              "FROM gse",
                              "WHERE gse = ",
                              paste("'", series, "'", sep = ""),
                              sep = " ")
long_experiment_name <- dbGetQuery(con, get_series_summaries)
}
long_experiment_name <- unlist(long_experiment_name)

temp <- unlist(str_split(long_experiment_name, " "))
temp <- paste(temp[1:5], collapse = " ")
temp <- temp[!is.na(temp)]
short_experiment_name <- temp

short_experiment_name <- unlist(short_experiment_name)

get_series_summaries <- paste("SELECT summary",
                              "FROM gse",
                              "WHERE gse = ",
                              paste("'", series, "'", sep = ""),
                              sep = " ")
series_summaries <- dbGetQuery(con, get_series_summaries)

series_summaries <- unlist(series_summaries)

tissue_cell_line <- list()
for (i in seq_along(gsms_ticks)){
  get_source_tissue <- paste('SELECT source_name_ch1',
                             'FROM gsm',
                             'WHERE gsm = ',
                             gsms_ticks[i],
                             sep = ' ')
  tissue_cell_line[[i]] <- dbGetQuery(con, get_source_tissue)
}
tissue_cell_line <- unlist(tissue_cell_line)

comments_experiment <- list()

regulatory_molecule_I <- list()
regulatory_molecule_II <- list()
regulatory_molecule_III <- list()

regulatory_ligand_1 <- list()
concentration_1 <- list()
concentration_unit_1 <- list()
time_1 <- list()
time_unit_1 <- list()

regulatory_ligand_1 <- list()
concentration_1 <- list()
concentration_unit_1 <- list()
time_1 <- list()
time_unit_1 <- list()

regulatory_ligand_2 <- list()
concentration_2 <- list()
concentration_unit_2 <- list()
time_2 <- list()
time_unit_2 <- list()

regulatory_ligand_3 <- list()
concentration_3 <- list()
concentration_unit_3 <- list()
time_3 <- list()
time_unit_3 <- list()

regulatory_ligand_4 <- list()
concentration_4 <- list()
concentration_unit_4 <- list()
time_4 <- list()
time_unit_4 <- list()

regulatory_ligand_5 <- list()
concentration_5 <- list()
concentration_unit_5 <- list()
time_5 <- list()
time_unit_5 <- list()

tissuesource <- list()

for (i in seq_along(dataset_species)){
  species_id[[i]] <- species_lookup %>%
    filter(SPECIES_SCIENTIFICNAME == dataset_species[i]) %>%
    select(ID)
}
species_id <- unlist(species_id)

reg_mol_id_1 <- list()
reg_mol_id_2 <- list()
reg_mol_id_3 <- list()

reg_ligand_id_1 <- list()
reg_ligand_id_2 <- list()
reg_ligand_id_3 <- list()
reg_ligand_id_4 <- list()
reg_ligand_id_5 <- list()

experiment_sheet <-
  cbind.fill(internal_experiment_id,LOF,public_experiment,
             short_experiment_name,long_experiment_name,series_summaries,
             tissue_cell_line,dataset_species, dataset_source,
             comments_experiment,regulatory_molecule_I,regulatory_molecule_II,
             regulatory_molecule_III,regulatory_ligand_1,concentration_1,
             concentration_unit_1,time_1,time_unit_1,regulatory_ligand_1,
             concentration_1,concentration_unit_1,time_1,time_unit_1,
             regulatory_ligand_2,concentration_2,concentration_unit_2,time_2,
             time_unit_2,regulatory_ligand_3,concentration_3,
             concentration_unit_3,time_3,time_unit_3,regulatory_ligand_4,
             concentration_4,concentration_unit_4,time_4,time_unit_4,
             regulatory_ligand_5,concentration_5,concentration_unit_5,
             time_5,time_unit_5,tissuesource,reg_mol_id_1,reg_mol_id_2,
             reg_mol_id_3,reg_ligand_id_1,reg_ligand_id_2,reg_ligand_id_3,
             reg_ligand_id_4,reg_ligand_id_5)

colnames(experiment_sheet) <- colnames(experiment_nursa)

################################################################################
# use matrix file to create data_sheet

# download the matrix file
getGEO(series, destdir = getwd(), getGPL = FALSE, AnnotGPL = FALSE)


# The tsv_file has an ID column and the experimental values. To match the ID
# number with a gene the supplementary files are needed
# they are downloaded with the following command:
getGEOSuppFiles(series)

# this downloads a filelist and a .raw.tar file which contains the raw data of
# each run and an annotation file

list_raw_data <- paste("ls ",
                       series,
                       "/*RAW.tar",
                       sep = "")
raw_data <- system(list_raw_data, intern = TRUE)
list_raw_files <- paste("less ",
                        series,
                        "/*RAW.tar",
                        sep = "")
raw_files <- system(list_raw_files, intern= TRUE)
annotation_file <- unlist(strsplit(raw_files[1], "\\s+", perl = TRUE))
annotation_file <- annotation_file[length(annotation_file)]

# expand .tar file
untar <- paste("tar -C",
               series,
               "-xvf",
               raw_data,
               sep = " ")
system(untar)

gunzip_annotation_file <- paste("gunzip ",
                                series,
                                "/",
                                annotation_file,
                                sep = "")


system(gunzip_annotation_file)
annotation_file <- gsub("\\.gz", "", annotation_file)

edited_annotations <- paste(series,
                            "/",
                            series,
                            "_",
                            annotation_file,
                            ".tsv",
                            sep = "")

edit_annotation_file <- paste("grep -Ev '\\^PLATFORM|^#' ",
                              series,
                              "/",
                              annotation_file,
                              " > ",
                              edited_annotations,
                              sep = "")

system(edit_annotation_file)

annotations <- read_tsv(edited_annotations, col_names = TRUE)

annotations %<>% select(ID, GB_ACC)
annotations %>% head()

# the matrix file is stored in a .soft file
# figure out name of file
# easy as there should be only one .soft file in the working directory

list_matrix <- paste("ls *matrix.txt.gz")
matrixfile <- system(list_matrix, intern = TRUE)

gunzip(matrixfile)
matrixfile <- system("ls *matrix.txt", intern = TRUE)

# create a grep command to extract the values
# the matrix file labels annotation lines with an !
# there is also at least one empty line, both types of lines
# need to be removed to yield tab-separated values

tsv_file <- paste(series, "tsv", sep = ".")

grep_command <- paste("grep -Ev '!|^$'",
                      matrixfile,
                      ">",
                      tsv_file,
                      sep = " ")
system(grep_command)


data <- read_tsv(tsv_file, col_names = TRUE)

mv_tsv_file <- paste("mv ",
                     tsv_file,
                     " ",
                     series,
                     sep = "")
system(mv_tsv_file)
mv_matrixfile <- paste("mv ",
                       matrixfile,
                       " ",
                       series,
                       sep = "")
system(mv_matrixfile)



data %<>% inner_join(annotations, by = c( "ID_REF" =  "ID"))

data <- data[c(length(data), seq(2, length(data) - 1))]

data %<>% filter(!is.na(GB_ACC))



# create targets_df

# perform queries for each sample:
#
sample_infos <- list()
for (i in (seq_along(colnames(data))-1)){
  i <- i + 1
  sq <- paste("SELECT title, gsm, source_name_ch1",
              "FROM gsm",
              "WHERE gsm = ",
              paste("'",
                    colnames(data[i]),
                    "'",
                    sep = ""),
              sep = " ")
  # sample info
  si <- dbGetQuery(con, sq)
  sample_infos[[i]] <- si
}

sample_infos

pre_target <- bind_rows(sample_infos)

pre_target$tissue <- tissue
pre_target$treat <- c(treat[2], treat[1], treat[2], treat[1], treat[2], treat[1])
pre_target$genotype <- genotype
pre_target$time <- ex_time
pre_target$strain <- strain
pre_target$rep <- c(1, 1, 2, 2, 3, 3)

targets <- pre_target %>%
  select(title, gsm, tissue, genotype, time, treat, rep)



target_colnames <- c("sample", "geo", "tissue", "strain", "genotype", "time",
                     "treat", "rep")

colnames(targets) <- target_colnames

# remove all NAs this is necessary for the PCA

data <- na.omit(data)
# data <- as.data.frame(data)
# rownames(data) <- data$GB_ACC
# data <- data[,-1]

# convert the dat object into a data matrix. necessary for later steps
#dat <- as.matrix(data)
dat <- as.matrix(data)

# use GB_ACC column as rownames, this is important later

rownames(dat) <- dat[,1]
dat <- dat[,-1]
class(dat) <- "numeric"

## follow NURSA instructions from here
##

library(limma)
library(affycoretools)

# visualize the entire set of normalized data values in a PCA plot to
# asses quality
plotPCA(dat,groups=factor(targets$treat),
        groupnames=levels(factor(targets$treat)),addtext=targets$rep)

# create a design matrix and fit a linear analysis model without an intercept
design<-model.matrix(~0+factor(targets$treat))
colnames(design)<-levels(factor(targets$treat))

fit <- lmFit(dat,design)

# create a contrast matrix which will calculate the FCs of choice
contrast_command <- paste(treat[2],
                          "vs",
                          treat[1],
                          " = ",
                          treat[2],
                          " - ",
                          treat[1],
                          " ,levels = design",
                          sep = "")
contrast.matrix <- makeContrasts(contrast_command)

fit2 <- contrasts.fit(fit,contrast.matrix)
fit3 <- eBayes(fit2)

# use topTable to create a dataframe
table_fit <- topTable(fit3, number = length(fit3))

# remember all of the FCs in this file will be on a log2 scale.


################################################################################
# write output to excel file

output_file_name <- paste(series,
                          ".xlsx",
                          sep = "")

write.xlsx(Dataset_sheet, file = output_file_name,
           row.names = FALSE,
           col.names = FALSE,
           sheetName = "Dataset")
write.xlsx(experiment_sheet, file = output_file_name,
           row.names = FALSE,
           sheetName = "Experiment", append = TRUE)

# write.xlsx runs out of memory, using gnumeric's ssconvert instead,
# see below, if gnumeric is not an option, this can be tried instead:
# write.xlsx(data_sheet, file = output_file_name,
#             row.names = FALSE,
#             sheetName = "Data points", append = TRUE)


table_fit <- as.data.frame(table_fit)
write_tsv(table_fit, "data_sheet.tsv")
ssconvert_command <- paste("ssconvert data_sheet.tsv",
                           "temp.xlsx", sep = " ")

system(ssconvert_command)

# Next the two excel files are merged using gnumeric's ssconvert_merge command
ssconvert_merge <- paste("ssconvert", output_file_name,
                         "temp.xlsx", "--merge-to", "out.xlsx",
                         sep = " ")
system(ssconvert_merge)


