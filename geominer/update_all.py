from my_funs import *
import time
import sys

old_stdout = sys.stdout
log_file = open('update_all.log', 'w')
time_ini = time.time()

# sqlite3 and GEOmetadb, download db using R 
import sqlite3 
conn = sqlite3.connect('GEOmetadb.sqlite')
# the next line address UTF8 issues
#conn.text_factory = bytes
conn.text_factory = lambda x: str(x, 'latin1')


# getting relevant data from GEOmetadb
# get gses with from relevant techniques
#gse = pd.read_sql_query("SELECT * FROM gse ", conn)

time0 = time.time()
print('reading gse table')
gse = pd.read_sql_query("SELECT * FROM gse;", conn)
print('reading gsm table')
gsm = pd.read_sql_query("SELECT * FROM gsm;", conn) 
time1 = time.time()
print('tables read in ', time1-time0, ' seconds.')

#rename series_id column of gsm table to gse
gsm.rename(columns={'series_id': 'gse'}, inplace=True)

#join gse and gsm
print('merging gse and gsm tables')
gsem = pd.merge(gse, gsm, on='gse')
gsem.set_index('gse', inplace=True)


# create a df with all ontologies integrated, identified terms and parent terms
print('updating dataframe')
time0 = time.time()
df = update_all(gsem, '/home/axel/Documents/ontologies/ont_selection' )
time1 = time.time()
print('time to update df: ', time1-time0, ' seconds.')

# write to csv
print('writing dataframe to file')
df.to_csv("gsem_selection_onts.tsv", sep="\t")

time_end = time.time()
print('All done! The whole procedure took ', time_end - time_ini, 'seconds.')
log_file.close()


