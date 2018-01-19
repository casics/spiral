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
line consisting of a token, some whitespace, and an integer; alternatively,
the input file can be a csv file in which the first column has the tokens and
the second column has the frequencies.  The output format is based on the
file extension: .csv for a CSV file, .pklz for a compressed pickle file.
'''
    if not inputfile:
        raise SystemExit('Missing input file argument.')
    if not outputfile:
        raise SystemExit('Missing output file argument.')
    if inputfile.endswith('.csv'):
        delimiter = ','
    else:
        delimiter = (' ', '\t')
    try:
        data = {}
        with open(inputfile, 'r') as input:
            if debug:
                import ipdb; ipdb.set_trace()
            total = 0
            kept = 0
            for line in input:
                total += 1
                (token, frequency) = line.split(delimiter)
                if filter(token):
                    continue
                data[token] = int(frequency)
                kept += 1
            print('{} strings read, {} kept.'.format(total, kept))
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
        print('Output saved in {}.'.format(outputfile))
    except Exception as err:
        print(err)


# Note: do not try to filter things that have mixed case and naively might be
# thought to be multiword identifiers.  I did this originally, thinking it
# would be safe to filter out strings that start with a capital letter and
# then have at least one more capital letter followed by a lowercase letter,
# such as "ABCFoo".  Unfortunately this will catch things like LaTeX and
# PDFLaTeX, which people do write in mixed case.  This would be bad for our
# goals.  I can see no safe way of automatically filtering out multiword
# strings, so this only filters really obviously undesirable stuff.

def filter(s):
    '''Return True if the token should be filtered out.'''
    # Filter out pure numbers.
    # Fast number detector from https://stackoverflow.com/a/23639915/743730
    if s.replace('.', '', 1).isdigit():
        return True
    # Filter out stuff like "e545", "line23", "case2" etc.  Yes, there's a
    # risk this will catch some acronyms that I'm not aware of, but I think the
    # risk is low enough that it's okay to do this.  Besides, for Spiral, we
    # have a separate list of acronyms, and so they will be handled elsewhere.
    elif re.search('^(e|error|page|line|case|test)[0-9]+$', s, re.IGNORECASE):
        return True
    else:
        return False


# Entry point.
# .............................................................................

if __name__ == '__main__':
    plac.call(main)
