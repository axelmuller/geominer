
def explode(reference, column, df):
    """ The explode function works on columns that store lists.
    Applying the function yields a dataframe where each list element
    is in a separate row. The index is created by using a groupby
    statement on the reference"""
    out_df = df.groupby(reference).column.apply(lambda x: 
          pd.DataFrame([item for sublist in x.values for item in sublist]))
    return(out_df)

"""
the following function isn't suitable for use in Pandas.
the processes need to be broken up. 
def ie_preprocess(document):
    apply nltk tools to documents
    sentences = sent_tokenize(document)
    sentences = [word_tokenize(sent) for sent in sentences]
    sentences = [pos_tag(sent) for sent in sentences]
    return(sentences)

# break summary down into sentences
gse_summary['sentences'] = gse_summary.summary.apply(nltk.sent_tokenize)

# explode this so that each sentence is in a row of its own 

gse_summary = gse_summary[[0,2]] 

gse_summary = gse_summary.groupby('gse').sentences.apply(lambda x: pd.DataFrame([item for sublist in x.values for item in sublist]))


"""

