import re
import spacy
import numpy as np
from spacy.tokenizer import Tokenizer
from spacy.tokens import Doc

# NLP utils functions

camel_case_infix_re = re.compile(r'''[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))''')
underscore_infix_re = re.compile(r'''_''')


def camel_case_tokenizer(nlp):
    return Tokenizer(nlp.vocab, infix_finditer=camel_case_infix_re.finditer)


def underscore_tokenizer(nlp):
    return Tokenizer(nlp.vocab, infix_finditer=underscore_infix_re.finditer)


def initialize_nlp(corpus):
    """Initialize spacy with a given corpus name"""
    return spacy.load(corpus, disable=["tagger", "parser", "ner"])


def initialize_tokenizer(nlp, type):
    """Initialize spacy's tokenizer according to the type provided"""
    if type == 'underscore':
        nlp.tokenizer = underscore_tokenizer(nlp)
    elif type == 'camel':
        nlp.tokenizer = camel_case_tokenizer(nlp)
    return nlp


def tokenize_list(nlp, data, lower=False):
    """
    @todo: documentation
    """
    data_tokenized = []
    for item in data:
        if lower:
            data_tokenized.append(' '.join(token.text.lower() for token in nlp.tokenizer(item)))
        else:
            data_tokenized.append(' '.join(token.text for token in nlp.tokenizer(item)))
    return data_tokenized


def lemmatize_list(nlp, data):
    """
    @todo: documentation
    """
    lenghts = np.cumsum([0] + list(map(len, data)))
    flat_data = [item for subl in data for item in subl]
    doc = Doc(nlp.vocab, words=flat_data)

    lemmatized = []
    for idx in range(1, len(lenghts)):
        span = doc[lenghts[idx - 1] : lenghts[idx]]
        lemmatized.append([token.lemma_.lower() for token in span])
    return lemmatized


def strings_to_list(data):
    tkn_list = []
    for item in data:
        for x in item.split():
            tkn_list.append(x)
    return tkn_list
