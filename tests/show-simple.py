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
    'fooBARzBif',
    'ABCfoo',
    'ABCFoo',
    'ABCFooBar',
    'ABCfooBar',
    'fooBar2day',
    'fooBar2Day',
    'fooBAR2day',
    'fooBAR2Day',
    'foo3000',
    '99foo3000',
    'foo2Bar',
    'foo2bar2',
    'Foo2Bar2',
    'MyInt32',
    'MyInt42',
    'MyInt32Var',
    '2ndvar',
    'the2ndvar',
    'the2ndVar',
    'row10',
    'utf8',
    'aUTF8var',
    'J2SE4me',
    'IPv4addr',
]

def use(splitter, s, width=15):
    return ' '.join(splitter(s)).ljust(width)

print('input'.ljust(14) + 'pure_camel'.ljust(14) + 'safe_simple'.ljust(14)
      + 'simple'.ljust(14) + 'elementary'.ljust(15) + 'heuristic'.ljust(15))
print('-------'.ljust(14) + '-------'.ljust(14) + '-------'.ljust(14)
      + '-------'.ljust(14) + '-------'.ljust(15) + '-------'.ljust(15))
for s in cases:
    print(s.ljust(14)
          + use(pure_camelcase_split, s, 14)
          + use(safe_simple_split, s, 14)
          + use(simple_split, s, 14)
          + use(elementary_split, s)
          + use(heuristic_split, s))
