#!/usr/bin/env python3
# =============================================================================
# @file    create_frequency_file.py
# @brief   Create a frequency.csv or frequency.pklz from raw token frequencies
# @author  Michael Hucka
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/casics/extractor
# =============================================================================

import csv
import math
import plac
import re
import sys

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), "../spiral"))
except:
    sys.path.append("../spiral")

import frequencies


# Main
# .............................................................................

@plac.annotations(
    debug      = ('drop into ipdb opening files',        'flag',   'd'),
    inputfile  = ('input text file',                     'option', 'i'),
    outputfile = ('output file',                         'option', 'o'),
)

def main(inputfile=None, outputfile=None, debug=False):
    '''The intput file should be a plain-text table of frequencies, with each
line consisting of a token, some whitespace, and an integer.  The output
format is based on the file extension: .csv for a CSV file, .pklz for a
compressed pickle file.
'''
    if not inputfile:
        raise SystemExit('Missing input file argument.')
    if not outputfile:
        raise SystemExit('Missing output file argument.')
    try:
        data = {}
        with open(inputfile, 'r') as input:
            if debug:
                import ipdb; ipdb.set_trace()
            total = 0
            for line in input:
                (token, frequency) = line.split()
                data[token] = int(frequency)
                total += 1
        print('{} read lines from {}'.format(total, inputfile))
        if outputfile.endswith('.csv'):
            with open(outputfile, 'w') as output:
                for token, frequency in sorted(data.items(), reverse=True,
                                               key=lambda x: x[1]):
                    output.write(token)
                    output.write(',')
                    output.write(str(frequency))
                    output.write('\n')
        else:
            frequencies.save_frequencies_to_pickle(data, outputfile)
    except Exception as err:
        print(err)


# Entry point.
# .............................................................................

if __name__ == '__main__':
    plac.call(main)
