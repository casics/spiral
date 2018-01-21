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
from nltk.corpus import words as nltk_words
from nltk.corpus import wordnet as nltk_wordnet
from nltk.stem import SnowballStemmer

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


# Filter.
# .............................................................................
# The code below is an attempt to algorithmically remove stuff that is not
# desirable in a frequency table.  This is a very conservative effort;
# ideally, far more stuff would be filtered out, but it's difficult to
# come up with filter rules that won't remove stuff that should be kept.
# I also didn't want to resort to manual editing of the frequency table because
# that would produce idiosyncratic results and would not be reproducible.
#
# Note: be careful about filtering things that have mixed case and naively
# might be thought to be multiword identifiers.  I did this originally,
# thinking it would be safe to filter out strings that start with a capital
# letter and then have at least one more capital letter followed by a
# lowercase letter, such as "ABCFoo".  Unfortunately this will catch things
# like LaTeX and PDFLaTeX, which people do write in mixed case.  This would
# be bad for our goals.  The code below does a limited version of this that
# (based on experimentation) does a reasonable job of removing one kind of
# pattern.

dictionary = set(nltk_words.words())
dictionary.update(nltk_wordnet.all_lemma_names())
stemmer = SnowballStemmer('english')

# The following exceptions were obtained while trying to find ways of filtering
# out obvious junk from the frequency table generated from 46k repos.  There
# are probably other exceptions that should be here but were missed, and if
# we had a different set of repos, we'd probably catch different exceptions.
# This is imperfect, but IMHO better than nothing.

exceptions = {'ipython', 'caching', 'revoked', 'doxygen', 'cpython',
              'slashless', 'python2', 'python3', 'exotica', 'mathematica',
              'chunker', 'arctanh', 'arcsinh', 'arccosh', 'arcsech',
              'coursera', 'activex', 'butterworth', 'utorrent', 'minimap',
              'xdisplay', 'xwindows', 'icontact', 'icalendar', 'jinja2',
              'crypto', 'kmeans', 'interp', 'approx', 'swift2', 'swift3',
              'latin5', 'iframe', 'sensei', 'jquery', 'gunzip', 'xapian',
              'xenstore', 'csharp', 'eeprom', 'iomega', 'asynchronously',
              'wunderground', 'texinfo', 'pdb', 'imdb', 'gdb', 'ipdb',
              'mongodb', 'dynamodb', 'mysqldb', 'bsddb', 'innodb', 'couchdb'
              'zodb', 'pydb', 'uuid', 'uid'}

def filter(s):
    '''Return True if the token should be filtered out.'''
    # Filter out pure numbers.
    # Fast number detector from https://stackoverflow.com/a/23639915/743730
    if s.replace('.', '', 1).isdigit():
        print('dropping {}'.format(s))
        return True
    # Filter out strings containing 3 upper case followed by 4 lower case
    # letters or vice versa.  This is a conservative test for one kind of
    # multiword string that seems to produce few-to-no false positives in my
    # testing.
    if (re.search('[A-Z][A-Z][A-Z][a-z][a-z][a-z][a-z]', s)
        or re.search('[A-Z][A-Z][A-Z][A-Z][a-z][a-z][a-z]', s)):
        print('dropping {}'.format(s))
        return True

    # Remaining tests are all based on lower case version of string.
    s = s.lower()

    # Skip exceptions.
    if s in exceptions:
        return False

    # Filter out stuff like "e545", "line23", "case2" etc.  Yes, there's a
    # risk this will catch some acronyms that I'm not aware of, but I think the
    # risk is low enough that it's okay to do this.  Besides, for Spiral, we
    # have a separate list of acronyms, and so they will be handled elsewhere.
    if re.search('^(e|error|page|line|case|test)[0-9]+$', s):
        print('dropping {}'.format(s))
        return True

    # Remove things that are reognizable words bracketed by a single letter,
    # such as "openerp" or 'xflush'. This requires care, because some things
    # are tokens we do want in the frequency table, so the rules below are
    # very strict and there's an exceptions table.  Note: don't remove things
    # only because they have a number at the end.  Example: lib2to3 should be
    # left in the frequency table.
    if len(s) > 5 and s not in dictionary and stemmer.stem(s) not in dictionary:
        if s[1:] in dictionary and not s.startswith('pre'):
            print('dropping {}'.format(s, s[1:]))
            return True
        if s[:-1] in dictionary and s[-1] not in ['s', 'r', 'd', 'g', 'y']:
            print('dropping {}'.format(s, s[:-1]))
            return True

    # Remove things that end with certain strings that are recognizable as
    # common contractions for separate words.
    if ((len(s) > 2 and s.endswith('db'))
        or (len(s) > 4 and s.endswith('info'))
        or (len(s) > 3 and s.endswith('ptr'))
        or (len(s) > 7 and s.endswith('pointer'))
        or (len(s) > 2 and s.endswith('id') and s not in dictionary)):
        print('dropping {}'.format(s))
        return True

    return False


# Entry point.
# .............................................................................

if __name__ == '__main__':
    plac.call(main)
