'''Spiral: SPlitters for IdentifieRs: A Library

Natural language processing (NLP) methods are increasingly being applied to
source code analysis for various purposes.  The methods rely on terms
(identifiers and other textual strings) extracted from program source code
and comments.  The methods often work better if, instead of raw identifiers,
real words are used as features; that is, "get" and "integer" are often better
features for NLP tools than the string "getInteger".  This leads to the
need for automated methods for splitting identifiers of classes, functions,
variables, and other entities into word-like constituents.  A number of
methods have been proposed an implemented to perform identifier splitting.

Spiral is a Python 3 package that implements numerous identifier splitting
algorithms.  It provides some basic naive splitting algorithms, such as a
straightforward camel-case splitter, as well as more elaborate heuristic
splitters, such as an algorithm we call Ronin (originally based on an
algorithm called Samurai by Enslen, Hill, Pollock and Vija-Shanker [2009]).

Authors
-------

Michael Hucka <mhucka@caltech.edu>

Copyright
---------

Copyright (c) 2017 by the California Institute of Technology.  This software
was developed as part of the CASICS project, the Comprehensive and Automated
Software Inventory Creation System.  For more, visit http://casics.org.
'''

from .__version__ import __version__, __title__, __description__, __url__
from .__version__ import __author__, __email__
from .__version__ import __license__, __copyright__

# Supporting modules.
from .frequencies import frequencies_from_csv_file, frequencies_from_pickle
from .frequencies import save_frequencies_to_pickle

# Simple splitters.
from .simple_splitters import delimiter_split, digit_split, pure_camelcase_split
from .simple_splitters import safe_simple_split, simple_split, elementary_split
from .simple_splitters import heuristic_split

# Advanced splitters.
from . import samurai
from . import ronin
