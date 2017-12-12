'''
frequencies: code to handle word frequencies
'''

import csv
import enchant
import math
import os
import pickle
import re
from   scipy.interpolate import interp1d
import sys


# Global variables.
# .............................................................................

_interpolated    = None
_raw_frequencies = None
_total_frequency = 0

_frequencies_dir    = os.path.dirname(__file__)
_frequencies_pickle = os.path.join(_frequencies_dir, 'frequencies.pickle')
_frequencies_csv    = os.path.join(_frequencies_dir, 'frequencies.csv')


# Main code.
# .............................................................................

def frequencies_from_file(filename=_frequencies_csv, filter_words=None):
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, fieldnames=['word','frequency'])
            frequencies = {}
            total = 0
            for row in reader:
                if filter_words and row['word'] in filter_words:
                    continue
                value = int(row['frequency'])
                frequencies[row['word']] = value
                total += value
            return (frequencies, total)
    except Exception as err:
        return ({}, 0)


def frequencies_from_pickle(filename=_frequencies_pickle, filter_words=None):
    try:
        with open(filename, 'rb') as saved_elements:
            frequencies = pickle.load(saved_elements)
            total = pickle.load(saved_elements)
            return (frequencies, total)
    except Exception as err:
        return ({}, None)


def save_frequencies_to_pickle(frequencies, total, filename=_frequencies_pickle):
    try:
        with open(filename, 'wb') as pickle_file:
            pickle.dump(frequencies, pickle_file)
            pickle.dump(total, pickle_file)
    except IOError as err:
        raise SystemExit('encountered error trying to dump pickle {}'.format(filename))
    except pickle.PickleError as err:
        raise SystemExit('pickling error for {}'.format(filename))


def init_word_frequencies():
    global _interpolated, _raw_frequencies, _total_frequency
    try:
        if os.path.exists(_frequencies_pickle):
            (_raw_frequencies, _total_frequency) = frequencies_from_pickle()
        else:
            (_raw_frequencies, _total_frequency) = frequencies_from_file()
            save_frequencies_to_pickle(_raw_frequencies, _total_frequency)
    except:
        raise SystemExit('unable to initialize word frequencies:')
    # _interpolated = interp1d([0, total], [0, 1])


def word_frequency(w):
    global _interpolated, _raw_frequencies, _total_frequency
    # return _interpolated(_raw_frequencies[w]) if w in _raw_frequencies else 0
    if not _raw_frequencies:
        init_word_frequencies()
    return int(_raw_frequencies[w]) if w in _raw_frequencies else 0
