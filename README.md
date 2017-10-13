# geominer
Mining GEO metadata for useful information

## Ontologies
The ontologies are generally obtained through bioportal.
http://bioportal.bioontology.org/ontologies/DOID
There are some small dummy ontologies in geominer/geominer that can be used for development

## Downloading GEOmetadb's sqlite database
This scripts here take advantage of GEOmetadb's sqlite database. GEOmetadb is a package for R provided by BIOCONDUCTOR.
The script get_new_geometadb.r will download the newest database can be run with the following command:

```bash
Rscript get_new_geometadb.r
```

## Creating a csv file for GoogleBigQuery
This CSV file contains data from GSE, GSM, ontology IDs that match to terms used in the GSE-summary field and their parents.
The script to run is: update_all.py
The script needs some user inputs:
The user needs to specify the directory that contains all the ontologies that will be used. The user should also name the output file
and the name for a logfile. Currently the created logfile is empty though.

```bash
python update_all.py
```
## Bash script for automation
The script update_script.sh is a bash script that combines the previous two scripts and zips the output csv.

```bash
bash update_script.sh
```

Uploading the output file to GoogleBigQuery could be included into the script but it might be more prudent not to do so for the time being.

## Uploading to GoogleBigQuery
Below is some sample code:
```bash
bq load --autodetect --skip_leading_rows=1 geo_meta.summary_onts gsem_9onts_2.csv.gz
```
--autodect takes care of the scheme 
--skip_leading_rows=1 removes the header
the next field specifies the destination table 
and the last item is the file to be uploaded, zipped files are accepted.


## Tables currently in GoogleBigQuery
All tables are under geo_meta:
combined onts: This table contains gse as identifier, a field with all ontology gse.summary hits, and a field with all ontology hits parents(regressive) 
gsem: gse and gsm tables from GEOmetadb merged (1.8 million rows at the moment), lots of redundancy on gse level, good for getting all the relevant experiments (gsm) 
ontology_hits: same as combined_onts, but separated by ontology
onts: three fields: list of names and synonymes, ontology ids, ontology 
The field names should be changed to something more meaningful
summary_onts: join of gsem and ontology_hits
