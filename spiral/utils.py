# =============================================================================
# @file    data_utils.py
# @brief   CASICS Spiral internal utilities for dealing with data
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/casics/spiral
# =============================================================================

import collections

def msg(string, *other_args):
    '''Like the standard print(), but treats the first argument as a string
    with format specifiers, and also flushes the output immediately. Flushing
    immediately is useful when piping the output of a script, because Python
    by default will buffer the output in that situation and this makes it
    very difficult to see what is happening in real time.
    '''
    print(string.format(*other_args), flush=True)


def flatten(lst):
    '''Recursively flatten a list of lists.  From the answer by user Christian
    here: https://stackoverflow.com/a/2158532/743730'''
    for el in lst:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el
