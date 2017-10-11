import pandas as pd
from flashtext.keyword import KeywordProcessor
from pronto import *
import re
import glob
import numpy as np
import time
from numba import jit
from multiprocessing.pool import ThreadPool
pool = ThreadPool()


def ont2df(path_to_ontology):
    """ Function for for creating a pandas dataframe from an ontology.          
    the df has 3 columns, name of ontology, ontology id, and value """
    ont = load_ont(path_to_ontology)
    ont_name = path_to_ontology.split('/')[-1].split('.')[0]  
    ont_dict = create_ont_dict(ont)
    columns = ['ontology', 'ont_id', 'names']
    out_df = ontdict2ontdf(ont_dict)
    out_df['ontology'] = ont_name
    return(out_df)

def allonts2df(path_to_ont_directory):
    """ Function for joining output of 1ont2df() into one df"""
    onts = get_onts(path_to_ont_directory)
    columns = ['ontology', 'ont_id', 'names']
    out_df = pd.DataFrame(columns=columns)
    for ont in onts:
        df_ont = ont2df(ont)
        out_df = out_df.append(df_ont)
    return(out_df)


def create_ont_df(path_to_ontology):
    ont = load_ont(path_to_ontology)
    ont_name = get_ont_name(path_to_ontology)
    ont_dict = create_ont_dict(ont)
    return(ont_dict)
    df_out = pd.DataFrame.from_dict(ont_dict, orient = 'index')
    df_out['names'] = df_out[df_out.columns].values.tolist()
    df_out = df_out['names'].reset_index()
    df_out.columns = [ont_id, values]
    df_out.name = df_out.apply(lambda row: set(row['name']), axis = 1)
    return(df_out)





# integrate ontology
def new_ont_parallel(path_to_ontology, df, column):
    """ automate integration of new ontology,
    requires local copy of ontology,
    will search for ontology terms, yield column with ontology id 
    and another column with its parents.
    requires:
        flashtext
        from pronto import import *
        pandas as pd
        my_functions as mf
        """
    
    ont = load_ont(path_to_ontology)
    ont_name = get_ont_name(path_to_ontology)
    ont_dict = create_ont_dict(ont)
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_dict(ont_dict)

    temp = df[column].apply(lambda x:
                                    set(keyword_processor.extract_keywords(x)))
    ont_rparents = get_recursive_parents(df, ont_name, ont)
    df[ont_name + '_parents'] = ont_rparents.apply(lambda x:                    
                                  set([elem for subl in x for elem in           
                                       subl])).fillna('no_hit')   
    return(df)





def explode(reference, column, df):
    """ The explode function works on columns that store lists.
    Applying the function yields a dataframe where each list element
    is in a separate row. The index is created by using a groupby
    statement on the reference"""
    out_df = df.groupby(df.loc[reference], axis=1)[column].apply(lambda x:
          pd.DataFrame([item for sublist in x.values for item in sublist]))
    out_df.columns = [column]
    out_df = out_df.reset_index(reference)
    return(out_df)

def implode(reference, column, df):
    keys,values=df.sort_values(reference).values.T
    ukeys,index=np.unique(keys,True)
    arrays=np.split(values,index[1:])
    df2=pd.DataFrame({reference:ukeys,column:[list(a) for a in arrays]})
    return df2

def obo_split(ont_id, ontology):
    inp = ontology[ont_id].obo.split("\n")
    return(inp)

def flattern(A):
    """ flattens list of lists, superior to 
    [elem for subl in x for elem in subl] because it handles a mixture of 
    strings and lists without splitting the strings."""
    rt = []
    for i in A:
        if isinstance(i,list): rt.extend(flattern(i))
        else: rt.append(i)
    return rt

#######################

# using @jit will make this function fail
# ValueError: cannot compute fingerprint of empty list
def get_ontology_names(ont_id, ontology):
    """ get name and all its synonymes for each entry 
    """
    inp = obo_split(ont_id, ontology)
    ont_dict = {}
    ont_names = []
    for e in inp:    
        re_name = re.compile('(name: )(.*)')
        name = re.search(re_name, e)
        if name != None and len(name.group(2)) > 0:
            ont_names.append(name.group(2))
        re_synonym = re.compile('(synonym: )(".*")(:?.*)')
        synonym = re.match(re_synonym, e)
        if synonym != None:
            ont_names.append(synonym.group(2).strip('"'))

        # the next if statement addresses the issue of OGG mentioning
        # synonymes in comments
        re_comment = re.compile('(comment: Other designations:\s*)(.+)')
        comment = re.search(re_comment, e)
        if comment != None:
            comment = comment.group(2).lower().strip().split('|')
            ont_names.append(comment)

    ont_names = flattern(ont_names)
    ont_dict[ont_id] = ont_names
    return(ont_dict)

def ontdict2ontdf(ont_dict, ont_id = 'ont_id', values = 'name'):
    """ Creates a dataframe from a ontology dictionary,
    column titles for ids and value columns are optional, recommended to
    keep the values column as is, ont_id should be changed to the name
    of the ontology with an _id suffix."""
    df_out = pd.DataFrame.from_dict(ont_dict, orient = 'index')
    df_out['names'] = df_out[df_out.columns].values.tolist()
    df_out = df_out['names'].reset_index()
#    id_column_name = str(ont_name) + '_id'
    #df_out.columns = [id_column_name, 'name']
    df_out.columns = [ont_id, values]
    df_out.name = df_out.apply(lambda row: set(row['name']), axis = 1)
    df_out.index = df_out[ont_id]
#    df_out.drop(ont_id, axis=1, inplace=True)
    return(df_out)                                                              
                     


def create_ont_dict(ont):
    """takes pronto loaded ontology as input, returns dictionary
    requires: pronto
    """
    ont_ids = []
    for term in ont:
        ont_ids.append(term.id)
    ont_dict = {}
    for i in ont_ids:
        ont_dict.update(get_ontology_names(i, ont))
    return(ont_dict)

def get_ont_id(ref, ont_column_name, df, ont_df, ont_id='ont_id', 
               values='name'):
    """add_ont_id takes a reference column, a column that contains
    the identified ontology term, and a dataframe as well as the ont_id
    and ont_names columns of an ontology dataframe. This depends on 
    df having a single index which serves as a ref.
    This function yields a series that with ref as index that can be added 
    to a corresponding dataframe.
    df[mycolumn] = get_ont_id(...) """
    df[ref] = df.index 
    temp_ref = explode(ref, ont_column_name, df)
    ont_df_expl = explode(ont_id, values, ont_df)
    temp_ref = pd.merge(temp_ref, ont_df_expl, left_on=ont_column_name,
                        right_on=values)
    temp_ref = temp_ref[[ref, ont_id]]
    temp_ref = implode(ref, ont_id, temp_ref)
    temp_ref.index = temp_ref[ref]
    temp_ref.drop(ref, axis=1, inplace=True)
    return(temp_ref)

def get_recursive_parents(df, ont_id_column, ont):
    """ get parents of all ontology terms recursively
    out put as series with same index as df"""
    ref = df.index.name
    out = df[ont_id_column][df[ont_id_column].notnull()].apply(lambda y: 
                                                 [ont[i].rparents().id for i in y]) 
    out = out.groupby(level=ref, as_index=True ).agg(sum)
    ########## unlist out and remove duplicates, maybe limit to id value
    return(out)

def get_recursive_children(df, ont_id_column, ont):
    """ get parents of all ontology terms recursively
    out put as series with same index as df"""
    ref = df.index.name
    out = df[ont_id_column][df[ont_id_column].notnull()].apply(lambda y: 
                                                 [ont[i].rchildren().id for i in y]) 
    out = out.groupby(level=ref, as_index=True ).agg(sum)
    ########## unlist out and remove duplicates, maybe limit to id value
    return(out)

def get_onts(path_to_ont_directory):
    """get list of all .owl and .obo files with path
    requires glob"""
    owls = glob.glob(path_to_ont_directory + '/*.owl')
    obos = glob.glob(path_to_ont_directory + '/*.obo')
    onts = obos + owls 
    return(onts)

# get ontology paths
def get_ontology_path(path_to_ont_directory):
    """ returns full paths of ontologies"""
    onts = get_onts(path_to_ont_directory)
#    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 

# load ontology using pronto
def load_ont(path_to_ontology):
    """ loads ontology, requires pronto"""

    ont = path_to_ontology.split('/')[-1].split('.')[0]
    ont_name = ont
    ont = Ontology(path_to_ontology)
    return(ont)

# get ontology name from path

def get_ont_name(path_to_ontology):
    """ gets the name of an ontology (or file) from a path,
    requires re """
    ont_name = re.search('(/?)(\w+)(\.\w{3})', path_to_ontology)
    if ont_name is not None:
        ont_name = ont_name.group(2)

    return(ont_name)
    
# integrate ontology
def new_ont(path_to_ontology, df, column):
    """ automate integration of new ontology,
    requires local copy of ontology,
    will search for ontology terms, yield column with ontology id 
    and another column with its parents.
    requires:
        flashtext
        from pronto import import *
        pandas as pd
        my_functions as mf
        """
    
    ont = load_ont(path_to_ontology)
    ont_name = get_ont_name(path_to_ontology)
    ont_dict = create_ont_dict(ont)
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_dict(ont_dict)

    df[ont_name] = df[column].apply(lambda x:
                                    set(keyword_processor.extract_keywords(x)))
    ont_rparents = get_recursive_parents(df, ont_name, ont)
    df[ont_name + '_parents'] = ont_rparents.apply(lambda x:                    
                                  set([elem for subl in x for elem in           
                                       subl])).fillna('no_hit')   
    return(df)


def update_all(df, path_to_ont_directory):                                                       
    onts = get_onts(path_to_ont_directory)
    for ont in onts:                                                            
        ont_file = re.search('(\/)(\w+\.\w{3}$)',ont).group(2)
        print('working on ', ont_file)
        time0 = time.time()
        df = new_ont(ont, df, 'summary')                                        
        time1 = time.time()
        print(ont_file, ' completed in ', time1 - time0, 'seconds.')

    return(df) 




