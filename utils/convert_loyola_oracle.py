#!/usr/bin/env python3.4
#
# @file    convert_loyola_oracle.py
# @brief   Take the Loyola U. Delaware identifier "oracle" set and convert it.
# @author  Michael Hucka
#
# <!---------------------------------------------------------------------------
# Copyright (C) 2015 by the California Institute of Technology.
# This software is part of CASICS, the Comprehensive and Automated Software
# Inventory Creation System.  For more information, visit http://casics.org.
# ------------------------------------------------------------------------- -->

import csv
import math
import pickle
import plac
import re
import sys

sys.path.append('../common')

from utils import *
from logger import *


# Main
# .............................................................................

def convert_file(inputfile=None, outputfile=None, debug=False, loglevel='info'):
    log = Logger(os.path.splitext(sys.argv[0])[0], console=True).get_log()
    if debug:
        log.set_level('debug')
    else:
        log.set_level(loglevel)
    expected = {}
    try:
        if debug:
            import ipdb; ipdb.set_trace()
        with open(inputfile, 'r') as input:
            total = 0
            for line in input:
                (_, token, _, _, _, _, result, *_) = line.split()
                expected[token] = [x for x in result.split('-') if not x.isdigit()]
                total += 1
        with open(outputfile, 'wb') as pickle_file:
            pickle.dump(expected, pickle_file)
            log.info('{} tokens written to {}'.format(total, outputfile))
    except Exception as err:
        log.error(err)


convert_file.__annotations__ = dict(
    debug      = ('drop into ipdb opening files', 'flag',   'd'),
    inputfile  = ('input text file',              'option', 'i'),
    outputfile = ('output CSV file',              'option', 'o'),
    loglevel   = ('logging level: "debug" or "info"', 'option', 'L'),
)

if __name__ == '__main__':
    plac.call(convert_file)
