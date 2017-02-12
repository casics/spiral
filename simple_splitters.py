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
