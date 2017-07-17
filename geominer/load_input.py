from pronto import * 

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



