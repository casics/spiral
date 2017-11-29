#!/usr/bin/env python3
#
# @file    id_splitters.py
# @brief   ID splitters
# @author  Michael Hucka
#
# <!---------------------------------------------------------------------------
# Copyright (C) 2015 by the California Institute of Technology.
# This software is part of CASICS, the Comprehensive and Automated Software
# Inventory Creation System.  For more information, visit http://casics.org.
# ------------------------------------------------------------------------- -->

import re
import sys

sys.path.append('../common')

from utils import *
from logger import *


# Delimiter-based splitter
# .............................................................................
#
# This does nothing fancy. It splits by explicit delimiter characters like '_'.

_delimiter_chars = '_.:'
_delimiter_splitter = str.maketrans(_delimiter_chars, ' '*len(_delimiter_chars))

def delimiter_split(identifier):
    '''Split identifier by explicit delimiters only.'''
    parts = str.translate(identifier, _delimiter_splitter).split(' ')
    parts = [p for p in parts if p]
    return parts


_digit_chars = '0123456789'
_digit_splitter = str.maketrans(_digit_chars, ' '*len(_digit_chars))

def digit_split(identifier):
    '''Split identifier at digits only.'''
    parts = str.translate(identifier, _digit_splitter).split(' ')
    parts = [p for p in parts if p]
    return parts


# Safe camel case splitter
# .............................................................................

_two_capitals = re.compile(r'[A-Z][A-Z]')
_camel_case   = re.compile(r'((?<=[a-z])[A-Z])')

def safe_camelcase_split(identifier):
    '''Split identifiers by forward camel case only, i.e., lower-to-upper case
    transitions.  This means it will split fooBarBaz into 'foo', 'Bar' and
    'Baz', but it won't change SQLlite or similar identifiers.  Does not
    split identifies that have multiple adjacent uppercase letters.'''
    if re.search(_two_capitals, identifier):
        return [identifier]
    return re.sub(_camel_case, r' \1', identifier).split()


# Safe simple splitter
# .............................................................................

_hard_split_chars = '_.:0123456789'
_hard_splitter = str.maketrans(_hard_split_chars, ' '*len(_hard_split_chars))

def safe_simple_split(identifier):
    '''Split identifiers by hard delimiters such as underscores, digits, and
    forward camel case only, i.e., lower-to-upper case transitions.  This
    means it will split fooBarBaz into 'foo', 'Bar' and 'Baz', and foo2bar
    into 'foo' and 'bar, but it won't change SQLlite or similar identifiers.
    Does not split identifies that have multiple adjacent uppercase
    letters.
    '''
    parts = str.translate(identifier, _hard_splitter).split(' ')
    return list(flatten(safe_camelcase_split(token) for token in parts))


# Not-so-safe simple splitter
# .............................................................................

_hard_split_chars = '~_.:0123456789'
_hard_splitter = str.maketrans(_hard_split_chars, ' '*len(_hard_split_chars))

def simple_split(identifier):
    '''Split identifiers by hard delimiters such as underscores, digits, and
    forward camel case only, i.e., lower-to-upper case transitions.  This
    means it will split fooBarBaz into 'foo', 'Bar' and 'Baz', and foo2bar
    into 'foo' and 'bar, but it won't change SQLlite or similar identifiers.
    Unlike safe_simple_split(), this will split identifiers that may have
    sequences of all upper-case letters if there is a lower-to-upper case
    transition somewhere.  Example: ABCtestSplit -> ['ABCtest', 'Split'].
    '''
    parts = str.translate(identifier, _hard_splitter)
    return re.sub(_camel_case, r' \1', parts).split()
