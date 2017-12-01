# =============================================================================
# @file    __init__.py
# @brief   CASICS Cloison package __init__ file
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/casics/cloison
# =============================================================================

from .__version__ import *
from .simple_splitters import delimiter_split, digit_split, safe_camelcase_split
from .simple_splitters import safe_simple_split, simple_split
from .samurai import same_case_split, samurai_split
