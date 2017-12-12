'''
simple_splitters: simple identifier splitters

This exports a number of simple splitter functions whose behaviors are sightly
different depending on what assumptions are made about identifier patterns.
None of these make inferences or expand identifiers.
'''

import re
import sys

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
except:
    sys.path.append("..")

try:
    from .utils import flatten
except:
    from utils import flatten


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

_hard_split_chars = '~_.:0123456789'
_hard_splitter = str.maketrans(_hard_split_chars, ' '*len(_hard_split_chars))

def safe_simple_split(identifier):
    '''Split identifiers by hard delimiters such as underscores, digits, and
    forward camel case only, i.e., lower-to-upper case transitions.  This
    means it will split fooBarBaz into 'foo', 'Bar' and 'Baz', and foo2bar
    into 'foo' and 'bar, but it won't change SQLlite or similar identifiers.
    Does not split identifies that have multiple adjacent uppercase
    letters anywhere in them, because doing so is risky if the uppercase
    letters are not an acronym.  Example: aFastNDecoder -> ['aFastNDecoder'].
    Contrast this to simple_split('aFastNDecoder'), which will produce
    ['a', 'Fast', 'NDecoder'] even though "NDecoder" may be more properly split
    as 'N' 'Decoder'.
    '''
    parts = str.translate(identifier, _hard_splitter).split(' ')
    return list(flatten(safe_camelcase_split(token) for token in parts))


# Not-so-safe simple splitter
# .............................................................................

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
