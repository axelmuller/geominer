from my_funs import *


# sqlite3 and GEOmetadb, download db using R 
import sqlite3 
conn = sqlite3.connect('GEOmetadb.sqlite')
# the next line address UTF8 issues
#conn.text_factory = bytes
conn.text_factory = lambda x: str(x, 'latin1')


# getting relevant data from GEOmetadb
# get gses with from relevant techniques
#gse = pd.read_sql_query("SELECT * FROM gse ", conn)

gse = pd.read_sql_query("SELECT * FROM gse WHERE type = 'Expression profiling by array' OR type = 'Expression profiling by high throughput sequencing';", conn)

# get gsms from relevant species
species = ("Homo sapiens", "Mus musculus", "Rattus norvegicus",
             "Rattus rattus",
             "Mus musculus;	Rattus norvegicus",
             "Mus musculus;	Rattus rattus",
             "Homo sapiens;	Mus musculus")
gsm = pd.read_sql_query("SELECT * FROM gsm WHERE organism_ch1 in "+str(species)+" OR source_name_ch1 in "+str(species) , conn) 

#rename series_id column of gsm table to gse
gsm.rename(columns={'series_id': 'gse'}, inplace=True)

#join gse and gsm
gsem = pd.merge(gse, gsm, on='gse')
gsem_selection = gsem[['title_x', 'gse', 'submission_date_x', 'summary',
                       'type_x', 'organism_ch1']].drop_duplicates()
gsem_selection.set_index('gse', inplace=True)

# get list of ontologies
owls =  get_owls('/home/axel/Documents/ontologies/ont_selection') 

# create a df with all ontologies integrated, identified terms and parent terms
df = update_all(gsem_selection, owls)

# write to csv
df.to_csv("gsem_selection_onts.tsv", sep="\t")
