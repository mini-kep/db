"""
Variable labels splitting code.
"""

import itertools


SEP = '_'


def split_label(label, sep=SEP):
    return extract_varname(label, sep), extract_unit(label, sep)


def extract_varname(label, sep=SEP):
    words = label.split(sep)
    return sep.join(itertools.takewhile(lambda word: word.isupper(), words))


def extract_unit(label, sep=SEP):
    words = label.split(sep)
    return sep.join(itertools.dropwhile(lambda word: word.isupper(), words))
