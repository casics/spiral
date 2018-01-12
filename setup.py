#!/usr/bin/env python3
# =============================================================================
# @file    setup.py
# @brief   Spiral setup file
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/casics/spiral
# =============================================================================

import os
from   setuptools import setup, find_packages
import sys

import spiral

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'requirements.txt')) as f:
    reqs = f.read().rstrip().splitlines()

setup(
    name=spiral.__version__.__title__.lower(),
    description=spiral.__version__.__description__,
    long_description='Spiral (SPlitters for IdentifieRs: A Library) provides methods for splitting and expanding identifiers found in source code files.',
    keywords="program-analysis text-processing machine-learning",
    version=spiral.__version__.__version__,
    url=spiral.__version__.__url__,
    author=spiral.__version__.__author__,
    author_email=spiral.__version__.__email__,
    license=spiral.__version__.__license__,
    packages=['spiral'],
    data_files=[('spiral', ['spiral/frequencies.pickle', 'spiral/frequencies.csv'])],
    install_requires=reqs,
    platforms='any',
)
