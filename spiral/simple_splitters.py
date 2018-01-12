'''simple_splitters: simple identifier splitters

This exports a number of simple splitter functions whose behaviors are
sightly different depending on what assumptions are made about identifier
patterns.  All are simple in the sense that they do not make complicated
inferences about the string and at most (in the cause of heuristic_split) use
fixed dictionaries of predefined terms to enhance performance.

The following table illustrates the differences between the different splitters
implemented in this file.  The first column shows the input string; the
remaining columns show the results of the different X_split() functions.

input          pure_camel     safe_simple    simple          elementary      heuristic
-------        -------        -------        -------         -------         -------
alllower       alllower       alllower       alllower        alllower        alllower
ALLUPPER       ALLUPPER       ALLUPPER       ALLUPPER        ALLUPPER        ALLUPPER
a_delimiter    a_delimiter    a delimiter    a delimiter     a delimiter     a delimiter
a.delimiter    a.delimiter    a delimiter    a delimiter     a delimiter     a delimiter
a$delimiter    a$delimiter    a delimiter    a delimiter     a delimiter     a delimiter
a:delimiter    a:delimiter    a delimiter    a delimiter     a delimiter     a delimiter
a_fooBar       a_foo Bar      a foo Bar      a foo Bar       a foo Bar       a foo Bar
fooBar         foo Bar        foo Bar        foo Bar         foo Bar         foo Bar
FooBar         Foo Bar        Foo Bar        Foo Bar         Foo Bar         Foo Bar
Foobar         Foobar         Foobar         Foobar          Foobar          Foobar
fooBAR         fooBAR         fooBAR         foo BAR         foo BAR         foo BAR
fooBARbif      fooBARbif      fooBARbif      foo BARbif      foo BARbif      foo BARbif
fooBARbifBaz   fooBARbifBaz   fooBARbifBaz   foo BARbif Baz  foo BARbif Baz  foo BARbif Baz
ABCfoo         ABCfoo         ABCfoo         ABCfoo          ABCfoo          ABCfoo
ABCFoo         ABCFoo         ABCFoo         ABCFoo          ABCFoo          ABCFoo
ABCFooBar      ABCFooBar      ABCFooBar      ABCFoo Bar      ABCFoo Bar      ABCFoo Bar
ABCfooBar      ABCfooBar      ABCfooBar      ABCfoo Bar      ABCfoo Bar      ABCfoo Bar
fooBar2day     foo Bar2day    foo Bar2day    foo Bar2day     foo Bar 2 day   foo Bar2day
fooBar2Day     foo Bar2Day    foo Bar2Day    foo Bar2Day     foo Bar 2 Day   foo Bar2Day
fooBAR2day     fooBAR2day     fooBAR2day     foo BAR2day     foo BAR 2 day   foo BAR2day
fooBAR2Day     fooBAR2Day     fooBAR2Day     foo BAR2Day     foo BAR 2 Day   foo BAR2Day
Foo2Bar        Foo2Bar        Foo2Bar        Foo2Bar         Foo 2 Bar       Foo2Bar
2foo2bar       2foo2bar       2foo2bar       2foo2bar        2 foo 2 bar     foo2bar
2Foo2bar       2Foo2bar       2Foo2bar       2Foo2bar        2 Foo 2 bar     Foo2bar
2Foo2Bar       2Foo2Bar       2Foo2Bar       2Foo2Bar        2 Foo 2 Bar     Foo2Bar
2foo2bar2      2foo2bar2      2foo2bar2      2foo2bar2       2 foo 2 bar 2   foo2bar
The2ndVar      The2nd Var     The2nd Var     The2nd Var      The 2 nd Var    The2nd Var
row10          row10          row10          row10           row 10          row
utf8           utf8           utf8           utf8            utf 8           utf8
aUTF8var       aUTF8var       aUTF8var       a UTF8var       a UTF 8 var     a UTF8 var
J2SE4me        J2SE4me        J2SE4me        J2SE4me         J 2 SE 4 me     J2SE 4me
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


# Pure camel case splitter.
# .............................................................................

_two_capitals = re.compile(r'[A-Z][A-Z]')
_camel_case   = re.compile(r'((?<=[a-z])[A-Z])')

def pure_camelcase_split(identifier):
    '''Split identifiers by forward camel case only, i.e., lower-to-upper
    case transitions.  This means it will split fooBarBaz into 'foo', 'Bar'
    and 'Baz', but it won't change SQLlite or similar identifiers. It also
    ignores delimiter characters.  It will not split identifies that have
    multiple adjacent uppercase letters.
    '''
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
    return list(flatten(pure_camelcase_split(token) for token in parts))


# Not-so-safe simple splitter.
# .............................................................................

def simple_split(identifier):
    '''Split identifiers by hard delimiters such as underscores, and forward
    camel case only, i.e., lower-to-upper case transitions.  This means it
    will split fooBarBaz into 'foo', 'Bar' and 'Baz', and foo2bar into 'foo'
    and 'bar, but it won't change SQLlite or similar identifiers.  Unlike
    safe_simple_split(), this will split identifiers that may have sequences
    of all upper-case letters if there is a lower-to-upper case transition
    somewhere.  Example: simple_split('aFastNDecoder') will produce ['a',
    'Fast', 'NDecoder'] even though "NDecoder" may be more correctly split as
    'N' 'Decoder'.  It preserves digits and does not treat them specially.
    '''
    parts = str.translate(identifier, _hard_splitter).split()
    return list(flatten(re.sub(_camel_case, r' \1', token).split() for token in parts))


# Not-so-safe simple splitter.
# .............................................................................

def elementary_split(identifier):
    '''Split identifiers by hard delimiters such as underscores, digits, and
    forward camel case only, i.e., lower-to-upper case transitions.  This
    means it will split fooBarBaz into 'foo', 'Bar' and 'Baz', and foo2bar
    into 'foo' and 'bar, but it won't change SQLlite or similar identifiers.
    Unlike safe_simple_split(), this will split identifiers that may have
    sequences of all upper-case letters if there is a lower-to-upper case
    transition somewhere.  Example: simple_split('aFastNDecoder') will
    produce ['a', 'Fast', 'NDecoder'] even though "NDecoder" may be more
    correctly split as 'N' 'Decoder'.  Digits are treated as delimiters, but
    not otherwise recognized or removed.  For example, 'utf8_var' will be
    split into ['utf', '8', 'var'].  (Contrast this to heuristic_split().)
    '''
    transformed = str.translate(identifier, _hard_splitter)
    parts = re.split(r'(\d+)', transformed)
    return list(flatten(re.sub(_camel_case, r' \1', token).split() for token in parts))


# Not-so-safe, not-so-simple splitter.
# .............................................................................

_common_terms = re.compile(r'(' + '|'.join(common_terms_with_numbers) + ')', re.IGNORECASE)

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
    parts = re.sub(_common_terms, r' \1 ', parts)
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
