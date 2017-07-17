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

gse_summary = dsm[['gse','summary']].drop_duplicates()
gse_summary['sentences'] = gse_summary.summary.apply(nltk.sent_tokenize)
gse_summary = gse_summary[['gse', 'sentences']]
gse_sentences = gse_summary.groupby('gse').sentences.apply(lambda x: pd.DataFrame([item for sublist in x.values for item in sublist]))
gse_sentences.columns = ['sentences']
gse_sentences['sentences'] = gse_sentences.sentences.apply(nltk.word_tokenize)

gse_sentences['sentences'] = gse_sentences.sentences.apply(nltk.pos_tag)

gse_words = gse_sentences.groupby(gse_sentences.index).sentences.apply(lambda x: pd.DataFrame([item for sublist in x.values for item in sublist]))

gse_words.columns = ['word', 'pos_tag']
