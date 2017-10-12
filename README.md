# geominer
Mining GEO metadata for useful information

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
