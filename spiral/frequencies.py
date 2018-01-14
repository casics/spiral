'''
frequencies: code to handle word frequencies
'''


# Main code.
# .............................................................................

def frequencies_from_csv_file(filename, threshold=None, filter_words=None):
    '''Read a table of frequencies (as a Python dictionary) from a CSV file.
    Parameter 'threshold' sets a minimum frequency value for entries to keep.
    Entries with frequency values less than the given 'threshold' value will
    be discarded.  Parameter 'filter_word' is a set of words (dictionary keys)
    that should be ignored.  Entries that are found in 'filter_words' will be
    discarded.  Returns a dictionary of the results.
    '''
    import csv
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, fieldnames=['word','frequency'])
            frequencies = {}
            for row in reader:
                word = row['word']
                frequency = int(row['frequency'])
                if threshold and frequency < threshold:
                    continue
                if filter_words and word in filter_words:
                    continue
                frequencies[word] = frequency
            return frequencies
    except Exception as err:
        return {}


def frequencies_from_pickle(filename, threshold=None, filter_words=None):
    '''Read a table of frequencies (as a Python dictionary) from a pickle file.
    If the file name ends in the extension .pklz, it's assumed to be a gzip'ed
    pickle file; otherwise, it's assumed to be an uncompressed pickle file.
    Parameter 'threshold' sets a minimum frequency value for entries to keep.
    Entries with frequency values less than the given 'threshold' value will
    be discarded.  Parameter 'filter_word' is a set of words (dictionary keys)
    that should be ignored.  Entries that are found in 'filter_words' will be
    discarded.  Returns a dictionary of the results.
    '''
    import pickle
    data = {}
    try:
        if filename.endswith('.pklz'):
            import gzip
            with gzip.open(filename, 'rb') as pickle_file:
                data = pickle.load(pickle_file)
        else:
            with open(filename, 'rb') as pickle_file:
                data = pickle.load(pickle_file)
        if threshold:
            data = {k : v for k, v in data if v < threshold}
        if filter_words:
            data = {k : v for k, v in data if k not in filter_words}
        return data
    except Exception as err:
        return {}


def save_frequencies_to_pickle(data, filename):
    '''Write data to a pickle file.  If the file ends in the extension .pklz,
    it's assumed to be a gzip'ed pickle file; otherwise, it's assumed to be
    an uncompressed pickle file.
    '''
    import pickle
    try:
        if filename.endswith('.pklz'):
            import gzip
            with gzip.open(filename, 'wb') as pickle_file:
                pickle.dump(data, pickle_file)
        else:
            with open(filename, 'wb') as pickle_file:
                pickle.dump(data, pickle_file)
    except IOError as err:
        raise SystemExit('encountered error trying to dump pickle {}'.format(filename))
    except pickle.PickleError as err:
        raise SystemExit('pickling error for {}'.format(filename))
