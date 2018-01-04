'''
frequencies: code to handle word frequencies
'''


# Main code.
# .............................................................................

def frequencies_from_csv_file(filename, filter_words=None):
    import csv
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, fieldnames=['word','frequency'])
            frequencies = {}
            for row in reader:
                if filter_words and row['word'] in filter_words:
                    continue
                frequencies[row['word']] = int(row['frequency'])
            return frequencies
    except Exception as err:
        return {}


def frequencies_from_pickle(filename, filter_words=None):
    '''Read a pickle file.  If the file ends in the extension .pklz, it's
    assumed to be a gzip'ed pickle file; otherwise, it's assumed to be an
    uncompressed pickle file.
    '''
    import pickle
    try:
        if filename.endswith('.pklz'):
            import gzip
            with gzip.open(filename, 'rb') as pickle_file:
                return pickle.load(pickle_file)
        else:
            with open(filename, 'rb') as pickle_file:
                return pickle.load(pickle_file)
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
                pickle.dump(frequencies, pickle_file)
    except IOError as err:
        raise SystemExit('encountered error trying to dump pickle {}'.format(filename))
    except pickle.PickleError as err:
        raise SystemExit('pickling error for {}'.format(filename))
