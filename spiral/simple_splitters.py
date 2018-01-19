'''simple_splitters: simple identifier splitters

This exports a number of simple splitter functions whose behaviors are
sightly different depending on what assumptions are made about identifier
patterns.  All are simple in the sense that they do not make complicated
inferences about the string and at most (in the cause of heuristic_split) use
fixed dictionaries of predefined terms to enhance performance.

The following table illustrates the differences between the different splitters
implemented in this file.  The first column shows the input string; the
remaining columns show the results of the different X_split() functions.

input        pure_camel    safe_simple  simple        elementary     heuristic
-------      -------       -------      -------       -------        -------
alllower     alllower      alllower     alllower      alllower       alllower
ALLUPPER     ALLUPPER      ALLUPPER     ALLUPPER      ALLUPPER       ALLUPPER
a_delimiter  a_delimiter   a delimiter  a delimiter   a delimiter    a delimiter
a.delimiter  a.delimiter   a delimiter  a delimiter   a delimiter    a delimiter
a$delimiter  a$delimiter   a delimiter  a delimiter   a delimiter    a delimiter
a:delimiter  a:delimiter   a delimiter  a delimiter   a delimiter    a delimiter
a_fooBar     a_foo Bar     a foo Bar    a foo Bar     a foo Bar      a foo Bar
fooBar       foo Bar       foo Bar      foo Bar       foo Bar        foo Bar
FooBar       Foo Bar       Foo Bar      Foo Bar       Foo Bar        Foo Bar
Foobar       Foobar        Foobar       Foobar        Foobar         Foobar
fooBAR       foo BAR       fooBAR       foo BAR       foo BAR        foo BAR
fooBARbif    foo BARbif    fooBARbif    foo BARbif    foo BARbif     foo BARbif
fooBARzBif   foo BARz Bif  fooBARzBif   foo BARz Bif  foo BARz Bif   foo BARz Bif
ABCfoo       ABCfoo        ABCfoo       ABCfoo        ABCfoo         ABCfoo
ABCFoo       ABCFoo        ABCFoo       ABCFoo        ABCFoo         ABCFoo
ABCFooBar    ABCFoo Bar    ABCFooBar    ABCFoo Bar    ABCFoo Bar     ABCFoo Bar
ABCfooBar    ABCfoo Bar    ABCfooBar    ABCfoo Bar    ABCfoo Bar     ABCfoo Bar
fooBar2day   foo Bar2day   foo Bar2day  foo Bar2day   foo Bar 2 day  foo Bar 2 day
fooBar2Day   foo Bar2Day   foo Bar2Day  foo Bar2Day   foo Bar 2 Day  foo Bar 2 Day
fooBAR2day   foo BAR2day   fooBAR2day   foo BAR2day   foo BAR 2 day  foo BAR 2 day
fooBAR2Day   foo BAR2Day   fooBAR2Day   foo BAR2Day   foo BAR 2 Day  foo BAR 2 Day
foo3000      foo3000       foo3000      foo3000       foo 3000       foo 3000
99foo3000    99foo3000     99foo3000    99foo3000     99 foo 3000    99 foo 3000
foo2Bar      foo2Bar       foo2Bar      foo2Bar       foo 2 Bar      foo 2 Bar
foo2bar2     foo2bar2      foo2bar2     foo2bar2      foo 2 bar 2    foo 2 bar 2
Foo2Bar2     Foo2Bar2      Foo2Bar2     Foo2Bar2      Foo 2 Bar 2    Foo 2 Bar 2
MyInt32      My Int32      My Int32     My Int32      My Int 32      My Int32
MyInt42      My Int42      My Int42     My Int42      My Int 42      My Int 42
MyInt32Var   My Int32Var   My Int32Var  My Int32Var   My Int 32 Var  My Int32 Var
2ndvar       2ndvar        2ndvar       2ndvar        2 ndvar        2nd var
the2ndvar    the2ndvar     the2ndvar    the2ndvar     the 2 ndvar    the 2nd var
the2ndVar    the2nd Var    the2nd Var   the2nd Var    the 2 nd Var   the 2nd Var
row10        row10         row10        row10         row 10         row 10
utf8         utf8          utf8         utf8          utf 8          utf8
aUTF8var     a UTF8var     aUTF8var     a UTF8var     a UTF 8 var    a UTF8 var
J2SE4me      J2SE4me       J2SE4me      J2SE4me       J 2 SE 4 me    J2SE 4 me
IPv4addr     IPv4addr      IPv4addr     IPv4addr      IPv 4 addr     IPv4 addr
'''

import re
import string
import sys

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(os.path.join(os.path.dirname(__file__), "../spiral"))
except:
    sys.path.append("..")
    sys.path.append("../spiral")

try:
    from .constants import *
    from .utils import flatten
except:
    from constants import *
    from utils import flatten


# Global definitions.
# .............................................................................

_delimiter_chars = '$~_.:/@'
_two_capitals    = re.compile(r'[A-Z][A-Z]')
_camel_case      = re.compile(r'((?<=[a-z])[A-Z])')


# Delimiter-based splitter.
# .............................................................................
#
# This does nothing fancy. It splits by explicit delimiter characters like '_'.

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

def pure_camelcase_split(identifier, safe=False):
    '''Split identifiers by forward camel case only, i.e., lower-to-upper
    case transitions.  This means it will split fooBarBaz into 'foo', 'Bar'
    and 'Baz', but it won't change SQLlite or similar identifiers. It also
    ignores delimiter characters.  It will not split identifies that have
    multiple adjacent uppercase letters unless parameter 'safe' is True; for
    example, 'setAVariable' -> ['set', 'AVariable'] with the default value of
    safe == False, but 'setAVariable' -> ['setAVariable'] if safe == True.
    (The rationale is "better safe than sorry" for cases that cannot be split
    without a dictionary or heuristics.)
    '''
    if safe and re.search(_two_capitals, identifier):
        return [identifier]
    return re.sub(_camel_case, r' \1', identifier).split()


# Safe simple splitter.
# .............................................................................

_hard_splitter = str.maketrans(_delimiter_chars, ' '*len(_delimiter_chars))

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
    return list(flatten(pure_camelcase_split(token, safe=True) for token in parts))


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
    split_str = str.translate(identifier, _hard_splitter)
    split_str = re.sub(r'(\d+)', r' \1 ', split_str)
    return re.sub(_camel_case, r' \1', split_str).split()


# Not-so-safe, not-so-simple splitter.
# .............................................................................

_exceptions_re = re.compile(r'(' + '|'.join(common_terms_with_numbers) + ')', re.I)
_common_suffixes = tuple(common_suffix_numbers)

def heuristic_split(identifier, keep_numbers=True, exceptions=None):
    '''Split identifiers by hard delimiters such as underscores, digits, and
    forward camel case only, i.e., lower-to-upper case transitions.  This
    means it will split fooBarBaz into 'foo', 'Bar' and 'Baz', and foo2bar
    into 'foo' and 'bar, but it won't change SQLlite or similar identifiers.
    Unlike safe_simple_split(), this will split identifiers that may have
    sequences of all upper-case letters if there is a lower-to-upper case
    transition somewhere.  Example: heuristic_split('aFastNDecoder') will
    produce ['a', 'Fast', 'NDecoder'] even though "NDecoder" may be more
    correctly split as 'N' 'Decoder'.  If keep_numbers=False, leading digits
    are removed from the identifier string before processing; embedded digits
    are removed if they appear at the tail ends of tokens, but not if they
    appear in the middle of tokens or are recognized as being exceptions
    defined by the set in parameter 'exceptions'.  (The default set of
    exceptions are common terms with embedded numbers such as 'utf8'.)
    Tokens that consist ONLY of digits are removed.
    '''
    if exceptions:
        exceptions_re = re.compile(r'(' + '|'.join(exceptions) + ')', re.I)
    else:
        exceptions = common_terms_with_numbers
        exceptions_re = _exceptions_re

    preliminary = str.translate(identifier, _hard_splitter)
    preliminary = re.sub(exceptions_re, r' \1 ', preliminary)
    preliminary = re.sub(_camel_case, r' \1', preliminary)
    if keep_numbers:
        # Unfortunately gnarly and hard-to-read expression.  Did this for the
        # sake of speed.  Basic idea: keep each token that is in the exceptions
        # list or ends with a common suffix; otherwise, split the token by digits
        # and clean up the resulting digit strings.
        parts = flatten(s if (s.lower() in exceptions
                              or (not s[0].isdigit() and s.endswith(_common_suffixes)))
                        else filter(bool, re.split(r'(\d+)', s))
                        for s in preliminary.split())
    else:
        # Variation of the previous thing that will remove leading and trailing
        # digits of tokens, possibly removing the tokens altogether if the only
        # characters it has are digits.
        parts = flatten(s.strip() if (s.lower() in exceptions
                                      or (not s[0].isdigit() and s.endswith(_common_suffixes)))
                        else filter(bool, [t.lstrip(string.digits).rstrip(string.digits)
                                           for t in re.split(r'\d+', s)])
                        for s in preliminary.split())
    return list(parts)
