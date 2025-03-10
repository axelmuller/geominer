from my_funs import *
import time
import sys


# sqlite3 and GEOmetadb, download db using R 
import sqlite3 
conn = sqlite3.connect('GEOmetadb.sqlite')
# the next line address UTF8 issues
#conn.text_factory = bytes
conn.text_factory = lambda x: str(x, 'latin1')

######################################################################
# some user input required
######################################################################

path_to_ontologies = 'test_onts' # path to directory with ontologies
outfile = 'test_out.csv'
logfile = 'my_logfile.log'


######################################################################
old_stdout = sys.stdout
log_file = open(logfile, 'w')
time_ini = time.time()

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

# get unique summaries 
summary = gsem[['summary']].drop_duplicates()


# create a df with all ontologies integrated, identified terms and parent terms
print('updating dataframe')
time0 = time.time()
df = update_all(summary, '/home/axel/Documents/ontologies/ont_selection' )
=======
df = update_all(summary, path_to_ontologies)
df.drop('summary', axis=1, inplace=True)
time1 = time.time()
print('time to update df: ', time1-time0, ' seconds.')

#add results to gsem
new_columns = df.columns
# the following line can be uncommented for quick test runs
#gsem_copy = gsem.head(100)
#gsem_copy = gsem.copy()
#gsem_copy[new_columns] = df
# for quick test runs the next line needs to be commented out
gsem[new_columns] = df

# write to csv
print('writing dataframe to file')
<<<<<<< HEAD
# for quick test runs 
# gsem_copy.to_csv("jan15_test.csv")
# otherwise:
gsem.to_csv("jan15_test.csv")
=======
gsem_copy.to_csv(outfile)

time_end = time.time()
print('All done! The whole procedure took ', time_end - time0, 'seconds.')
log_file.close()


