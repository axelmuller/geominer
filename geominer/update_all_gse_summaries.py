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
gse = pd.read_sql_query("SELECT gse, summary FROM gse;", conn)
gse.set_index('gse', inplace=True)


# create a df with all ontologies integrated, identified terms and parent terms
print('updating dataframe')
time0 = time.time()
df = update_all(gse, '/home/axel/Documents/ontologies/ont_selection' )
#df.drop('summary', axis=1, inplace=True)
time1 = time.time()
print('time to update df: ', time1-time0, ' seconds.')

#add results to gsem
#new_columns = df.columns
#gse_copy = gse.copy()
#gse_copy[new_columns] = df

# write to csv
print('writing dataframe to file')
df.to_csv("gse_summary_9onts.csv")

time_end = time.time()
print('All done! The whole procedure took ', time_end - time0, 'seconds.')
log_file.close()


