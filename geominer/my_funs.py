import pronto
# define variables used in functions
chebi = Ontology("/home/axel/Documents/ontologies/chebi.owl")


####
"""
the following function is not working: 
    figure out how to call columns with variables!!
    """
def explode(reference, column, df):
    """ The explode function works on columns that store lists.
    Applying the function yields a dataframe where each list element
    is in a separate row. The index is created by using a groupby
    statement on the reference"""
    out_df = df.groupby(reference).column.apply(lambda x: 
          pd.DataFrame([item for sublist in x.values for item in sublist]))
    return(out_df)
####



def obo_split(ont_id, ontology):
    inp = ontology[ont_id].obo.split("\n")
    return(inp)


def get_ontology_names(ont_id, ontology):                                       
    inp = obo_split(ont_id, ontology)                                           
    ont_dict = {}                                                               
    ont_names = []                                                              
    for e in inp:                                                               
        if re.search(r'(synonym:)(.*)(EXACT.*$)', e) and re.match(r'(synonym:)(.+)(EXACT.*$)', e):                           
            e = (re.match(r'(synonym:)(.+)(EXACT.*$)', e)                       
                 .group(2)                                                      
                 .lower()                                                       
                )                                                               
            pattern = re.compile('\s*"\s*')                                     
            e = pattern.sub('', e)                                              
            ont_names.append(e)                                                 
        if re.search(r'(^name:)(.+)', e) and re.match(r'(name: )(.+)', e):                                       
            e = (re.match(r'(name: )(.+)', e)                                   
                 .group(2)                                                      
                 .lower()                                                       
            )                                                                   
            ont_names.append(e)                                                 
        ont_dict[ont_id] = ont_names                                            
    return(ont_dict)   

"""
def get_ontology_names(ont_id, ontology):
    inp = obo_split(ont_id, ontology)
    ont_dict = {}
    ont_names = []
    for e in inp:
        if re.search(r'(synonym:)(.*)(EXACT.*$)', e):
            e = (re.match(r'(synonym:)(.+)(EXACT.*$)', e)
                 .group(2)
                 .lower()
                )
            pattern = re.compile('\s*"\s*')
            e = pattern.sub('', e)
            ont_names.append(e)
        if re.search(r'(^name:)(.+)', e):
            e = (re.match(r'(name: )(.+)', e)
                 .group(2)
                 .lower()
            )
            ont_names.append(e)
        ont_dict[ont_id] = ont_names
    return(ont_dict)
"""
def get_simple_names(my_dict):
    """dictionary containing ids as keys and list of names as values serves as  
    input. Output are list of names that lack numbers. This yields simple molecule names"""
    ids = my_dict.keys()
    out_dict = {}
    for i in ids:
        names_list = my_dict[i]
        temp_names = []
        for n in names_list:
            if re.search(r'[0-9]', n) is None:
                temp_names.append(n)
        if len(temp_names) > 1:
            out_dict[i] = list(set(temp_names))
    return(out_dict)

def get_single_word_names(a_dict):
    """from dictionary values in list form, remove all entries that are longer
    than one word """
    out_dict = {}
    for k in a_dict:
        temp_list = []
        for i in a_dict[k]:
            if re.search(r' ', i) is None:
                temp_list.append(i)
        out_dict[k] = temp_list
    return(out_dict)

def match_single_word_molecules(word_dict, word_list):
    """check if word in annotated word list is present in molecule dictionary"""
    for i in word_list:
        # the dictionary values are lists hence dictionary.values()
        # yields a nested list that requires flattening.
        if i[0] in [item for sublist in word_dict.values() for item in sublist]:
            i.append(1)
        else:
            i.append(0)


def get_all_words_positively_mapped(list_with_features, position_of_feature):
    """get all positive hits for a given feature"""
    hits = []
    for i in list_with_features:
        if i[position_of_feature] == 1:
            hits.append(i)
    return(hits)

def extract_noun_phrases(tree, target_label):
    temp = []
    for subtree in tree.subtrees(filter = lambda t: t.label() == target_label):
        temp.append(' '.join([a for (a, b) in subtree.leaves()]))
    return(temp)

def find_regexes(regexlist):
    """go through list of regex expressions and check if any are present in
    column """
    df_temp = pd.DataFrame()
    for a, i in enumerate(regexlist):
        df_temp[a] = df_gse_sentences.sentence.str.findall(i)
    return(df_temp)

def rev_dict(dict):
    """ Function to reverse a dictionary """
    out_dict = {}
    for i in range(0, len(dict.keys())):
                   out_dict[(list(dict.values()))[i]] =  list(dict.keys())[i]
    return(out_dict)

# https://stackoverflow.com/questions/13611065/efficient-way-to-apply-multiple-filters-to-pandas-dataframe-or-series
def conjunction(*conditions):
    return functools.reduce(np.logical_and, conditions)


