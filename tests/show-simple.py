#!/usr/bin/env python3
# =============================================================================
# @file    show-simple.py
# @brief   Show differences in behaviors of the simple splitters
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/casics/spiral
# =============================================================================

import os
import sys

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
except:
    sys.path.append("..")

from spiral.simple_splitters import pure_camelcase_split, safe_simple_split
from spiral.simple_splitters import simple_split, elementary_split
from spiral.simple_splitters import heuristic_split

cases = [
    'alllower',
    'ALLUPPER',
    'a_delimiter',
    'a.delimiter',
    'a$delimiter',
    'a:delimiter',
    'a_fooBar',
    'fooBar',
    'FooBar',
    'Foobar',
    'fooBAR',
    'fooBARbif',
    'fooBARbifBaz',
    'ABCfoo',
    'ABCFoo',
    'ABCFooBar',
    'ABCfooBar',
    'fooBar2day',
    'fooBar2Day',
    'fooBAR2day',
    'fooBAR2Day',
    'Foo2Bar',
    '2foo2bar',
    '2Foo2bar',
    '2Foo2Bar',
    '2foo2bar2',
    'The2ndVar',
    'row10',
    'utf8',
    'aUTF8var',
    'J2SE4me',
    'IPv4addr',
]

def use(splitter, s):
    return ' '.join(splitter(s)).ljust(16)

print('input'.ljust(16) + 'pure_camel'.ljust(16) + 'safe_simple'.ljust(16)
      + 'simple'.ljust(16) + 'elementary'.ljust(16) + 'heuristic'.ljust(16))
print('-------'.ljust(16) + '-------'.ljust(16) + '-------'.ljust(16)
      + '-------'.ljust(16) + '-------'.ljust(16) + '-------'.ljust(16))
for s in cases:
    print(s.ljust(16)
          + use(pure_camelcase_split, s)
          + use(safe_simple_split, s)
          + use(simple_split, s)
          + use(elementary_split, s)
          + use(heuristic_split, s))
