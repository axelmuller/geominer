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

gse_summary = dsm[['gse','summary']].drop_duplicates()
gse_summary['sentences'] = gse_summary.summary.apply(nltk.sent_tokenize)
gse_summary = gse_summary[['gse', 'sentences']]
gse_sentences = gse_summary.groupby('gse').sentences.apply(lambda x: pd.DataFrame([item for sublist in x.values for item in sublist]))
gse_sentences.columns = ['sentences']
gse_sentences['sentences'] = gse_sentences.sentences.apply(nltk.word_tokenize)

gse_sentences['sentences'] = gse_sentences.sentences.apply(nltk.pos_tag)

gse_words = gse_sentences.groupby(gse_sentences.index).sentences.apply(lambda x: pd.DataFrame([item for sublist in x.values for item in sublist]))

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

# TODO
# vectorize words with tensorflow
