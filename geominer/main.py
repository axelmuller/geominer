from pronto import *
from nltk.corpus import wordnet as wn
import nltk
import re
import pprint
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random

import load_input 
from pronto import * 
import pandas as pd
# PyEnchant - a spell checker   
# this doesn't work under Anaconda.
# import enchant
# d = enchant.Dict("en_US")
import functools
import my_funs as mf


### from load_input.py
#  load a gene ontology (not go) 
ogg = Ontology("/home/axel/Documents/ontologies/ogg-merged.owl")
# Get children of: OGG:2060009606: protein-coding gene of Homo sapiens
pcg_hs = ogg['OGG:2060009606'].children.name
# turn elements of pcg_hs to lower case:
pcg_hs = [i.lower() for i in pcg_hs]


# Reading in diabetes series matrix
# This tsv file was produced using R and GEO-metadb
dsm = pd.read_table('/home/axel/projects/hirn/beta_cells/beta_R/nursa_grant/diabetes_series_matrix.tsv')
gse_summary = dsm[['gse','summary']].drop_duplicates()
###

# tokenize summaries to sentences

gse_summary['sentences'] = gse_summary.summary.apply(nltk.sent_tokenize)
gse_summary = gse_summary[['gse', 'sentences']]

# create a dataframe with gse and individual sentences
df_gse_sentences = gse_summary.groupby('gse').sentences.apply(lambda x: pd.DataFrame([item for sublist in x.values for item in sublist]))
# name index
df_gse_sentences.index.names =  ['gse', 'sentence_number']
df_gse_sentences.columns = ['sentence']                                           
# convert indices to columns
df_gse_sentences = df_gse_sentences.reset_index(level = ['gse',
                                           'sentence_number'])
# apply word tokenization and position tagging
df_gse_sentences['sentences'] = df_gse_sentences.sentence.apply(nltk.word_tokenize)
df_gse_sentences['sentences'] = df_gse_sentences.sentence.apply(nltk.pos_tag)
gse_words = df_    gse_sentences.groupby(gse_sentences.index).sentences.apply(lambda x: pd.DataFrame([item for sublist in x.values for item in sublist]))
gse_words.columns = ['word', 'pos_tag']

# convert words to lower case words
gse_words.word = gse_words.word.str.lower()
# the next step is necessary since str.lower() introduced 
# instance of type <class 'pandas.core.series.Series'>
gse_words = pd.DataFrame(gse_words)

# name index 
gse_words.index.names =  ['gse_sentence_number', 'word_in_sentence']
# convert indices to columns
gse_words = gse_words.reset_index(level = ['gse_sentence_number',
                                           'word_in_sentence'])

# name new index
gse_words.index.names = ['count']

# split gse_sentence_number into gse and sentence number column
# create a new dataframe with the split columns
df_temp = pd.DataFrame([x for x in gse_words.gse_sentence_number])
df_temp.index.names = ['count']
df_temp = df_temp.rename(columns = {0: 'gse', 1: 'sentence'})

# join df_temp with gse_words on index, exclude first column
gse_words_temp = df_temp.merge(gse_words[gse_words.columns[1:]], 
                               right_index = True, left_index = True)


# check if word is a human gene, pcg_hs
#gse_words['hs_gene'] =  np.where(~gse_words.pos_tag.str.contains('(NN.*)'), 0,
                             #np.where(gse_words['word'].isin(pcg_hs), 1, 0)

# this doesn't seem to do the job, try a join of two dataframes.
# Firts turn pcg_hs into a dataframe

df_pcg_hs = pd.DataFrame(pcg_hs, columns = ['gene'])


# merge and keep rows that don't match and match on nouns only

gse_words_temp['noun'] = gse_words_temp['word'][
    gse_words_temp.pos_tag.str.contains('NN', regex = True)]



df_gse_words = gse_words_temp.reset_index().merge(df_pcg_hs, 
                                             how = 'left',  
                                             right_on = 'gene', 
                                             left_on = 'noun')

# check if word is a real English word, PyEnchant should do the trick
# but there are some issues installing the dictionaries. NLTK might 
# offer alternatives, such as wordnet.
# It turns out that PyEnchant works with python as installed on the 
# system and fails within anaconda. Using an NLTK corpus may be
# sufficient for this purpose
# english_vocab = set(w.lower() for w in nltk.corpus.words.words())
# english_vocab contains 234377 entries but it doesn't handle plural forms,
# hence, wordnet might be a better choice.

df_gse_words['synsets'] = df_gse_words['word'].map(lambda x: wn.synsets(x))
df_gse_words['is_english'] = df_gse_words['synsets'].map(lambda x: len(x) > 0)

# TODO
# check if word or noun is in other ontologies, start with CHEBI

# Chemical Entities of Biological Interest
# Use [Chemical Entities of Biological Interest
# Ontology](http://bioportal.bioontology.org/ontologies/CHEBI) to 
# identify molecules in summaries

chebi = Ontology("/home/axel/Documents/ontologies/chebi.owl")

chebi_names = []
for e in chebi:
    chebi_names.append(e.name)

chebi_ids = []
for term in chebi:
    chebi_ids.append(term.id)

molecules_dict = {}
for i in chebi_ids:
    molecules_dict.update(mf.get_molecule_names(i))

all_molecules = set([item for sublist in list(molecules_dict.values()) 
                     for item in sublist])

single_word_molecules = set()
multi_word_molecules = set()

some_whitespace = re.compile('\w*[\s\W]\w*')

#for i in all_molecules:
for i in all_molecules:
    if re.match(some_whitespace, i):
        multi_word_molecules.update([i])
    else:
        single_word_molecules.update([i])
        
df_gse_words['word_is_molecule'] = df_gse_words['word'].map(
    lambda x: x in single_word_molecules)

"""
#############################################################################
###
# create a noun phrase dataframe
###
# for now I'll be using sentences to find occurrences of ontology terms
# NLTK utilizes PENN TREEBANK tags 
# https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
# list of grammatical structures to be joined for noun-phrases:
######
# the following grammar needs to be improved !!!!!!!!!!!!
#####
np_components = ["NN", "NNP", "NNS", "NNPS", "JJ", "JJR", "JJS", 
                 "VBN", "PRP", "PRP$", "SYM", "CD"]

# some need to be removed, DT, PRP.*, 

grammar = r'NP: {<SYM|VBN|VBG|CD|JJ.*|WP.*|FW|NN.*>+}'
cp = nltk.RegexpParser(grammar, loop = 2)

df_gse_sentences['np_tagging'] = df_gse_sentences.sentences.apply(lambda x:
                                                                cp.parse(x))

df_gse_sentences['np_list'] = df_gse_sentences.sentences.apply(
    lambda x: extract_noun_phrases(x, 'NP'))


df_gse_nps = df_gse_sentences.groupby(
    'gse').np_list.apply(lambda x: pd.DataFrame(
        [item for sublist in x.values for item in sublist]))

df_gse_nps.index.names =  ['gse', 'np_in_sentence'] 
df_gse_nps.columns =  ['np'] 

df_gse_nps = df_gse_nps.reset_index(level = ['gse',                 
                                           'np_in_sentence']) 


# check noun phrases for presence of chebi names or synonymes

#############################################################################
"""

"""
   The code below works but is too slow to work with CHEBI try 
   smaller ontology in the meantime


# Check sentences for occurrences of CHEBI terms


# remove non letters in all_molecules to dots
re_all_molecules = []
for i in all_molecules:
    re_all_molecules.append(re.sub('[^a-zA-Z]+', '.*', i))


# turn list of re_all_molecules into a single regex expression 

big_regex_all_molecules = '|'.join(re_all_molecules)

regex = re.compile(big_regex_all_molecules)


df_gse_sentences['chebi'] = df_gse_sentences.sentence.str.findall(
    regex)
"""

# Check sentences of occurrences of disease terms

doid = Ontology('/home/axel/Documents/ontologies/doid.owl')

doid_ids = []
for term in doid:
    doid_ids.append(term.id)

disease_dict = {}
for i in doid_ids:
    disease_dict.update(get_ontology_names(i, doid))

disease_names = np.array([item for sublist in disease_dict.values() 
                     for item in sublist])

# remove all entries that contain breakets and other characters that may clash
# with regular expressions
special_characters = re.compile(r'\[|\(')
disease_names_with_special_characters = disease_names[
    [i for i, x in enumerate(disease_names) 
     if re.search(special_characters, x)]]


# the disease Ankylosing spondylitis also occurs as 'as' in the list
# this needs to be removed
diseases = set(disease_names) - set(disease_names_with_special_characters) -{'as'}

#diseases_sample = random.sample(diseases, 100)

# create a compiled regex
# make sure to flank the regexes to make sure that acronymes such as 
# 'ess', 'Ad', ... don't yield random hits
# use word boundary character \b for this
word_boundary = re.compile('^|$')
# note the r'\\b' otherwise \b turns into \x08
diseases = [word_boundary.sub(r'\\b', expr) for expr in diseases]


disease_regex = '|'.join(diseases)


compiled_disease_regex = re.compile(disease_regex, re.I)

df_gse_sentences['disease'] = df_gse_sentences.sentence.str.findall(compiled_disease_regex)

#identified diseases
unique_diseases = set([item for sublist in df_gse_sentences.disease for item in sublist])



# uberon

uberon_ont = Ontology('/home/axel/Documents/ontologies/uberon.owl')
uberon = Ontology('/home/axel/Documents/ontologies/uberon.owl')
uberon_ids = []
for term in uberon:
    uberon_ids.append(term.id)

uberon_dict = {}
for i in uberon_ids:
    uberon_dict.update(get_ontology_names(i, uberon))

uberon_names = np.array([item for sublist in uberon_dict.values()             
                     for item in sublist])

uberon_names_with_special_characters = uberon_names[                          
    [i for i, x in enumerate(uberon_names)                                     
     if re.search(special_characters, x)]]           

uberon = [word_boundary.sub(r'\\b', expr) for expr in uberon]  
uberon_regex = '|'.join(uberon)
compiled_uberon_regex = re.compile(uberon_regex, re.I)
df_gse_sentences['uberon'] = df_gse_sentences.sentence.str.findall(compiled_uberon_regex)

unique_uberons = set([item for sublist in df_gse_sentences.uberon for item in sublist])



# cell ontology: cl


cl = Ontology('/home/axel/Documents/ontologies/cl.owl')
cl_ids = []
for term in cl:
    cl_ids.append(term.id)

cl_dict = {}
for i in cl_ids:
    cl_dict.update(get_ontology_names(i, cl))

cl_names = np.array([item for sublist in cl_dict.values()
                     for item in sublist])

cl_names_with_special_characters = cl_names[
    [i for i, x in enumerate(cl_names)
     if re.search(special_characters, x)]]

cl = set(cl_names) - set(cl_names_with_special_characters)


cl = [word_boundary.sub(r'\\b', expr) for expr in cl]
cl_regex = '|'.join(cl)
compiled_cl_regex = re.compile(cl_regex, re.I)
df_gse_sentences['cl'] = df_gse_sentences.sentence.str.findall(compiled_cl_regex)

unique_cls = set([item for sublist in df_gse_sentences.cl for item in sublist])

# human genes in sentences use pcg_hs 
# note this approach does without position tagging, hence, lots of false
# positives

re_pcg_hs = [word_boundary.sub(r'\\b', expr) for expr in pcg_hs]
re_pcg_hs = '|'.join(re_pcg_hs)
re_pcg_hs = re.compile(re_pcg_hs, re.I)

df_gse_sentences['human_gene'] = df_gse_sentences.sentence.str.findall(re_pcg_hs)

# mesh medical subject headings


# extracting useful data
# this will need to be revisited, just some short term solution to 
# provide first batch of datasets

# group by gses prior to merging with dsm

df_gse_summary_analysis = df_gse_sentences[['gse',  'disease', 'uberon', 'cl',
                                            'human_gene']].groupby('gse', as_index=False).agg(sum)

df_gse_mining = pd.merge(dsm, df_gse_summary_analysis, on=['gse',
                                                           'gse']).drop_duplicates('gse')
df_gse_mining = df_gse_mining[['title.x', 'gse', 'submission_date.x', 'pubmed_id', 'summary', 'type.x', 'source_name_ch1', 'organism_ch1', 'molecule_ch1', 'technology', 'pancreas','signaling',  'data_lines', 'disease', 'uberon', 'cl']] 


list_of_diabetes_diseases = [
 'Diabetes Mellitus',
 'Diabetes mellitus',
 'Diabetic Neuropathy',
 'Diabetic Retinopathy',
 'Diabetic neuropathy',
 'Diabetic retinopathy',
     'Gestational Diabetes',
 'Gestational diabetes mellitus',
 'Glucose intolerance',
 'Insulin-dependent Diabetes Mellitus',
 'Hyperinsulinemia',
 'Langerhans-cell histiocytosis',
 'MODY',
     'Proliferative diabetic retinopathy',
 'Type 1 diabetes mellitus',
 'Type 2 Diabetes Mellitus',
 'Type 2 diabetes mellitus',
 'Type I Diabetes Mellitus',
 'Type II diabetes mellitus',
     'diabetes insipidus',
 'diabetes mellitus',
 'diabetic nephropathy',
 'diabetic neuropathy',
 'diabetic retinopathy',
 'gestational diabetes',
 'glucose intolerance',
'hyperinsulinemia',
 'hyperinsulinemic hypoglycemia',
 'hyperinsulinism',
 'hypoglycaemia',
 'hypoglycemia',
     'metabolic disease',
 'mitochondrial disease',
 'obesity',
 'pancreatitis',
 'prediabetes',
 'proliferative diabetic retinopathy',
 'type 1 diabetes mellitus',
 'type 2 diabetes mellitus',
 'type I diabetes mellitus']

diseases2exlude =(set(unique_diseases) - set(list_of_diabetes_diseases))

gene_hits = df_gse_words[['gse', 'gene']]
gene_hits = gene_hits.dropna(how='any')

gene_hits = gene_hits.groupby('gse').gene.apply(set).reset_index()

#gene_hits = gene_hits.groupby('gse').gene.apply(','.join).reset_index()

df_gse_mining = pd.merge(df_gse_mining, gene_hits, on=['gse', 'gse'], how = 'outer')

# selection criteria 
minimum_lines_of_data = 1000 
target_organism = 'Homo sapiens'
target_diseases = ['type 1 diabetes mellitus', 'type I diabetes mellitus',
                   'type 2 diabetes mellitus', 'diabetes mellitus']
# check type.x field for technology
target_technology = ['Expression profiling by array']


# conditions
c_1 = df_gse_mining.organism_ch1 == target_organism
c_2 = df_gse_mining.data_lines > minimum_lines_of_data
c_3 = df_gse_mining['disease'].apply(lambda x: any(i in x for i in target_diseases)) == True
c_6 = df_gse_mining['disease'].apply(lambda x: any(i in x for i in diseases2exlude)) == False

c_4 = df_gse_mining.signaling == 1
c_5 = df_gse_mining.pancreas == 1
c_7 = df_gse_mining['type.x'] == target_technology[0] 


my_selection = df_gse_mining[conjunction(c_1, c_2, c_4, c_5, c_6)]

df_gse_mining[df_gse_mining['disease'].apply(lambda x: any(i in x for i in
                                                           target_diseases))
              & df_gse_mining['organism_ch1' == target_organism]]




# TODO
# write function that deals with all of the ontology integration
# get ontology ids for each hit.
# get parents and children for each hit (id and name)

