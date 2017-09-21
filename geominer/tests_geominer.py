import pytest   
from my_funs import *
import pronto

ont = pronto.Ontology('dummy_ontology.obo')

def test_obo_split():
    """Perform unit test on obo_split """
    # probably not necessary since it relies on a properly imported ontology
    pass

################################################################################
# a bunch of test for get_ontology_names
def test_get_ontology_names_names():
    """test if get_ontology_names identifies name correctly."""

    assert get_ontology_names('testing:test_name', ont) == {'testing:test_name': ['my_name']}

def test_get_ontology_names_synonymesExact():
    """test if get_ontology_names identifies synonyms correctly."""

    assert get_ontology_names('testing:test_synonymExact', ont) == {'testing:test_synonymExact': ['exact_synonym']}

def test_get_ontology_names_synonymesRelated():
    """test if get_ontology_names identifies related synonyms correctly."""

    assert get_ontology_names('testing:test_synonymRelated', ont) == {'testing:test_synonymRelated': ['related_synonym']}

def test_get_ontology_names_and_synonymes():
    """ test if functions gets both name and its synonyms correctly."""

    assert get_ontology_names('testing:test_nameandsynonyms' , ont) == {'testing:test_nameandsynonyms': ['my_name', 'exact_synonym', 'related_synonym']}

def test_get_ontology_names_from_comments():
    """ test if synonyms hidden in comment field are picked up """
    assert get_ontology_names('testing:test_otherdesignations', ont) == {'testing:test_otherdesignations': ['preferred_name', 'alternative name1', 'alternative name2']}

################################################################################

def test_create_ont_dict():
    """ requires correctly loaded ontology as input, also requires 
    function get_ontology_names to work. """
    pass

def test_get_ont_name():
    """ unit test for get_ont_name()"""
    assert get_ont_name('my_ontology.ont') == 'my_ontology'
    assert get_ont_name('path/to/another_ontology.obo') == 'another_ontology'
    assert get_ont_name('path/to/other_format.txt') == 'other_format'
    assert get_ont_name('path/to/more_letter_filetype.text') == 'more_letter_filetype'
    assert get_ont_name('path/to/no_filetype') == None
    







