# =============================================================================
# @file    data_utils.py
# @brief   CASICS Spiral internal utilities for dealing with data
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/casics/spiral
# =============================================================================

def msg(string, *other_args):
    '''Like the standard print(), but treats the first argument as a string
    with format specifiers, and also flushes the output immediately. Flushing
    immediately is useful when piping the output of a script, because Python
    by default will buffer the output in that situation and this makes it
    very difficult to see what is happening in real time.
    '''
    print(string.format(*other_args), flush=True)


# Based on http://stackoverflow.com/a/10824484/743730
def flatten(iterable):
    '''Flatten a list produced by an iterable.  Non-recursive.'''
    iterator, sentinel, stack = iter(iterable), object(), []
    while True:
        value = next(iterator, sentinel)
        if value is sentinel:
            if not stack:
                break
            iterator = stack.pop()
        elif isinstance(value, str):
            yield value
        else:
            try:
                new_iterator = iter(value)
            except TypeError:
                yield value
            else:
                stack.append(iterator)
                iterator = new_iterator
