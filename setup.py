#!/usr/bin/env python3
# =============================================================================
# @file    setup.py
# @brief   Cloison setup file
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/casics/nostril
# =============================================================================

import os
from   setuptools import setup, find_packages
import sys

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'requirements.txt')) as f:
    reqs = f.read().rstrip().splitlines()

setup(
    name=nostril.__version__.__title__.lower(),
    description=nostril.__version__.__description__,
    long_description='Cloison (CLeaver Of Identifiers in SOurce code coNtent) provides methods for splitting and expanding identifiers found in source code files.',
    keywords="program-analysis text-processing machine-learning",
    version=nostril.__version__.__version__,
    url=nostril.__version__.__url__,
    author=nostril.__version__.__author__,
    author_email=nostril.__version__.__email__,
    license=nostril.__version__.__license__,
    packages=['cloison'],
    install_requires=reqs,
    platforms='any',
)
