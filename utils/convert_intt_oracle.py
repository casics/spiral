#!/usr/bin/env python3
# =============================================================================
# @file    convert_intt_oracle.py
# @brief   Take the INTT test files and create a create a single TSV file
# @author  Michael Hucka
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/casics/extractor
#
# =============================================================================

import csv
import glob
import math
import pickle
import plac
import re
import sys

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
except:
    sys.path.append("..")


# Main
# .............................................................................

@plac.annotations(
    debug      = ('drop into ipdb opening files',            'flag',   'd'),
    inputdir   = ('directory of INTT *-reference.txt files', 'option', 'i'),
    outputfile = ('output file',                             'option', 'o'),
    pickle     = ('output as pickle file (default: csv)',    'flag',   'p'),
)

def convert_file(inputdir=None, outputfile=None, debug=False, pickle=False):
    expected = {}
    total = 0
    if debug:
        import ipdb; ipdb.set_trace()
    files = inputdir + '/' + '*-reference.txt'
    for file in glob.glob(files):
        with open(file, 'r') as input:
            try:
                for line in input:
                    (identifier, result) = line.split()
                    expected[identifier] = [x for x in result.split('-')]
                    total += 1
            except Exception as err:
                print('Problem in file {} for {}: {}'.format(file, line, err))

    if pickle:
        with open(outputfile, 'wb') as pickle_file:
            pickle.dump(expected, pickle_file)
    else:
        with open(outputfile, 'w') as file:
            for k, v in expected.items():
                file.write(k)
                file.write('	')
                file.write(','.join(v))
                file.write('\n')
    print('{} tokens written to {}'.format(total, outputfile))



if __name__ == '__main__':
    plac.call(convert_file)
