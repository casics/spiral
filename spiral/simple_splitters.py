'''
simple_splitters: simple identifier splitters

This exports a number of simple splitter functions whose behaviors are sightly
different depending on what assumptions are made about identifier patterns.
None of these make inferences or expand identifiers.
'''

import re
import string
import sys

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
except:
    sys.path.append("..")

try:
    from .constants import *
    from .utils import flatten
except:
    from constants import *
    from utils import flatten


# Delimiter-based splitter.
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


_digit_splitter = str.maketrans(string.digits, ' '*len(string.digits))

def digit_split(identifier):
    '''Split identifier at digits only.'''
    parts = str.translate(identifier, _digit_splitter).split(' ')
    parts = [p for p in parts if p]
    return parts


# Safe camel case splitter.
# .............................................................................

_two_capitals = re.compile(r'[A-Z][A-Z]')
_camel_case   = re.compile(r'((?<=[a-z0-9])[A-Z])')

def safe_camelcase_split(identifier):
    '''Split identifiers by forward camel case only, i.e., lower-to-upper case
    transitions.  This means it will split fooBarBaz into 'foo', 'Bar' and
    'Baz', but it won't change SQLlite or similar identifiers.  Does not
    split identifies that have multiple adjacent uppercase letters.'''
    if re.search(_two_capitals, identifier):
        return [identifier]
    return re.sub(_camel_case, r' \1', identifier).split()


# Safe simple splitter.
# .............................................................................

_hard_split_chars = '$~_.:/'
_hard_splitter = str.maketrans(_hard_split_chars, ' '*len(_hard_split_chars))

def safe_simple_split(identifier):
    '''Split identifiers by hard delimiters ('_', '$', '~', '.', ':') and
    forward camel case only, i.e., lower-to-upper case transitions.  This
    means it will split fooBarBaz into 'foo', 'Bar' and 'Baz', but it won't
    split SQLlite or similar identifiers.  Does not split identifies that
    have multiple adjacent uppercase letters anywhere in them, because doing
    so is risky if the uppercase letters are not an acronym.  Example:
    aFastNDecoder -> ['aFastNDecoder'].  Digits are not removed from strings
    nor treated as delimiters, although a capital letter after a digit is
    considered equivalent to a camel case transition; for example,
    'foo_bar2Biff' will be split as ['foo', 'bar2', 'Biff'].
    '''
    parts = str.translate(identifier, _hard_splitter).split()
    return list(flatten(safe_camelcase_split(token) for token in parts))


# Not-so-safe simple splitter.
# .............................................................................

def simple_split(identifier):
    '''Split identifiers by hard delimiters such as underscores, digits, and
    forward camel case only, i.e., lower-to-upper case transitions.  This
    means it will split fooBarBaz into 'foo', 'Bar' and 'Baz', and foo2bar
    into 'foo' and 'bar, but it won't change SQLlite or similar identifiers.
    Unlike safe_simple_split(), this will split identifiers that may have
    sequences of all upper-case letters if there is a lower-to-upper case
    transition somewhere.  Example: simple_split('aFastNDecoder') will
    produce ['a', 'Fast', 'NDecoder'] even though "NDecoder" may be more
    correctly split as 'N' 'Decoder'.
    '''
    transformed = str.translate(identifier, _hard_splitter)
    parts = re.split(r'(\d+)', transformed)
    return list(flatten(re.sub(_camel_case, r' \1', token).split() for token in parts))


# Not-so-safe, not-so-simple splitter.
# .............................................................................

def heuristic_split(identifier):
    '''Split identifiers by hard delimiters such as underscores, digits, and
    forward camel case only, i.e., lower-to-upper case transitions.  This
    means it will split fooBarBaz into 'foo', 'Bar' and 'Baz', and foo2bar
    into 'foo' and 'bar, but it won't change SQLlite or similar identifiers.
    Unlike safe_simple_split(), this will split identifiers that may have
    sequences of all upper-case letters if there is a lower-to-upper case
    transition somewhere.  Example: heuristic_split('aFastNDecoder') will
    produce ['a', 'Fast', 'NDecoder'] even though "NDecoder" may be more
    correctly split as 'N' 'Decoder'.  Leading digits are removed from the
    identifier string before processing; embedded digits are removed if they
    appear at the tail ends of tokens, but not if they appear in the middle
    of tokens or are recognized as being part of common abbreviations such as
    'utf8'.  Tokens that consist ONLY of digits are removed.
    '''
    parts = str.translate(identifier.lstrip(string.digits), _hard_splitter)
    return _filter_digit_strings(re.sub(_camel_case, r' \1', parts).split())


# Internal utilities.
# .............................................................................

_only_digits = re.compile(r'\d')
_non_digits  = re.compile(r'\D')
_recognized_suffixes = re.compile(r'\D' + '|'.join(common_suffix_numbers))

def _filter_digit_strings(lst):
    results = []
    for token in lst:
        if token.lower() in common_terms_with_numbers:
            results.append(token)
        elif re.search(_recognized_suffixes, token):
            results.append(token)
        elif re.search(_non_digits, token):
            results.append(token.rstrip(string.digits))
        elif not re.search(_only_digits, token):
            results.append(token)
    return results
