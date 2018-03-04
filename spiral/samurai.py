'''
samurai: implementation of the Samurai algorithm for identifier splitting

Introduction
------------

Natural language processing (NLP) methods are increasingly being applied to
source code analysis for various purposes.  The methods rely on terms
(identifiers and other textual strings) extracted from program source code
and comments.  The methods often work better if, instead of raw identifiers,
real words are used as features; that is, "get" and "integer" are often better
features for NLP tools than the string "getInteger".  This leads to the
need for automated methods for splitting identifiers of classes, functions,
variables, and other entities into word-like constituents.  A number of
methods have been proposed an implemented to perform identifier splitting.

Samurai is a Python module that implements a splitter known as Samurai,
published by Eric Enslen, Emily Hill, Lori Pollock and K. Vijay-Shanker from
the University of Delaware in 2009.

  Enslen, E., Hill, E., Pollock, L., & Vijay-Shanker, K. (2009).  Mining
  source code to automatically split identifiers for software analysis.  In
  Proceedings of the 6th IEEE International Working Conference on Mining
  Software Repositories (MSR'09) (pp. 71-80).

The implementation in the present Python module was created by the author
from the description of the algorithm published in the paper.  Assuming my
interpretation of the Enslen et al.'s algorithm is correct, this
implementation is faithful to the algorithm described in the paper.

Usage
-----

Note: for fastest performance, using the optimization options provided by the
Python interpreter (i.e., the options -O or -OO).

The simplest way to use this module in a Python program is to import the
module from the Spiral package and then call samurai.split() with a
string. For example,

    from spiral import samurai
    result = samurai.split('someidentifier')

The function split(...) produces a list of strings as its output.  It will do
its best-guess at how a given identifier should be split using a built-in
table of term frequencies, prefixes, and suffixes.  The built-in table of
term frequencies came from an analysis of 20,000 randomly selected software
projects in GitHub that contained at least one Python source code file.

Samurai performs best when it is provided with project-specific tables of
term frequencies.  If you have a set of frequencies for your project, you can
supply them to the function init(...) once, before making any calls to
split().  (This is done so that the cost of computations involved in the
frequencies is only done once.)  Use the keyword argument 'local_freq'

    from spiral import samurai
    samurai.init(local_freq=myfrequencies)
    result = samurai.split('someidentifier')

The format of the value given to 'local_freq' should be a dictionary where
the keys are the terms and the values are integers representing the number of
times the term appears in the code base.  A term that appears once will have
a value of 1, a term that appears twice will have a value of 2, etc.  Some
terms for large code bases can have values that go into the hundreds of
thousands; this is okay, as Samurai will normalize the values.

You can also change the global frequency table that Samurai uses.  This can
be passed using the keyword argument 'global_freq' to init(...):

    samurai.init(global_freq=globalfrequencies, local_freq=projectfrequencies)

Note that generating the global table is not a trivial undertaking.  It
requires mining source code repositories to extract identifiers of classes,
functions, variables, etc., splitting them to produce individual identifier
fragments, and finally curating the result manually.

Tracing the algorithm
---------------------

To print what the splitter is doing while processing a given string, you can
turn on logging by setting the logging level to "logging.DEBUG" before
importing the samurai module.  Here is an example:

  import logging
  logging.basicConfig(level=logging.DEBUG, format='')
  from spiral import samurai

Logging will be printed to the standard output stream.  Note: this will only
work if you do NOT use the -O option to the Python interpreter.

Optimization
------------

This module wraps all logging code with the Python __debug__ compile-time
symbol, so that you can use the -O flag to Python to make it omit the code
completely.  This is more efficient than simply setting the logging level.

Authors
-------

Michael Hucka <mhucka@caltech.edu>

Copyright
---------

Copyright (c) 2017 by the California Institute of Technology.  This software
was developed as part of the CASICS project, the Comprehensive and Automated
Software Inventory Creation System.  For more, visit http://casics.org.
'''

import math
import os
import re
import sys

# NOTE: to turn on debugging, make sure python -O was *not* used to start
# python, then set the logging level to DEBUG *before* loading this module.
# Conversely, to optimize out all the debugging code, use python -O or -OO
# and everything inside "if __debug__" blocks will be entirely compiled out.
if __debug__:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('samurai')
    def log(s, *other_args): logger.debug('samurai: ' + s.format(*other_args))

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
except:
    sys.path.append("..")

try:
    from .frequencies import *
    from .simple_splitters import simple_split
    from .constants import prefixes, suffixes
except:
    from frequencies import *
    from simple_splitters import simple_split
    from constants import prefixes, suffixes


# Global constants.
# .............................................................................

# If the caller doesn't supply a frequency table, we use a default one.
# The file needs to be kept in the same directory as this Python module file.

try:
    _DEFAULT_FREQ_DIR = os.path.dirname(__file__)
except:
    _DEFAULT_FREQ_DIR = os.path.dirname('.')
_DEFAULT_FREQ_PICKLE = os.path.join(_DEFAULT_FREQ_DIR, 'data/frequencies.pklz')


# Main class
# .............................................................................

class Samurai(object):
    _global_freq = None
    _local_freq  = None

    def init(self, local_freq=None, global_freq=None):
        '''Initialize internal frequency files for the Samurai split() function.
        Parameter 'local_freq' should be a dictionary where the keys are the
        terms and the values are integers representing the number of times
        the term appears in the code base.  A term that appears once will
        have a value of 1, a term that appears twice will have a value of 2,
        etc.  Similarly, 'glocal_freq' should be a dictionary for global
        frequencies of all terms in a large sample of code bases.
        '''
        if __debug__: log('init_samurai()')
        if local_freq:
            self._local_freq = local_freq
        if global_freq:
            self._global_freq = global_freq
        if not self._global_freq:
            if os.path.exists(_DEFAULT_FREQ_PICKLE):
                self._global_freq = frequencies_from_pickle(_DEFAULT_FREQ_PICKLE)
            else:
                raise ValueError('Cannot read default frequencies pickle file "{}"'
                                 .format(_DEFAULT_FREQ_PICKLE))


    def split(self, identifier):
        '''Split the given identifier string at token boundaries using a
        combination of heuristics and token frequency tables.  This function
        produces a list of strings as its output.  The Samurai algorithm is
        described by Eric Enslen, Emily Hill, Lori Pollock and
        K. Vijay-Shanker in a 2009 paper titled "Mining source code to
        automatically split identifiers for software analysis" (Proceedings
        of the 6th IEEE International Working Conference on Mining Software
        Repositories, 2009).

        If you have a set of frequencies for your project, you can supply
        them to the function init(...) once, before making calls to split().
        This function will otherwise use a built-in global table of
        frequencies.
        '''
        splits = []
        if __debug__: log('splitting {}', identifier)
        if not self._global_freq:
            self.init()
        score = self._generate_scoring_function()
        for s in simple_split(identifier):
            # Look for upper-to-lower case transitions
            transition = re.search(r'[A-Z][a-z]', s)
            if not transition:
                if __debug__: log('no upper-to-lower case transition in {}', s)
                parts = [s]
            else:
                i = transition.start(0)
                if __debug__: log('case transition: {}{}', s[i], s[i+1])
                if i > 0:
                    camel_score = score(s[i:])
                    if __debug__: log('"{}" score {}', s[i:], camel_score)
                else:
                    camel_score = score(s)
                    if __debug__: log('"{}" score {}', s, camel_score)
                alt = s[i+1:]
                alt_score = score(alt)
                if __debug__: log('"{}" alt score {}', alt, alt_score)
                if camel_score > math.sqrt(alt_score):
                    if __debug__: log('{} > {} ==> better to include uppercase letter',
                                      camel_score, math.sqrt(alt_score))
                    if i > 0:
                        parts = [s[0:i], s[i:]]
                    else:
                        parts = [s]
                else:
                    if __debug__: log('not better to include uppercase letter')
                    parts = [s[0:i+1], s[i+1:]]
                if __debug__: log('split outcome: {}', parts)
            splits = splits + parts

        if __debug__: log('turning over to _same_case_split: {}', splits)
        results = []
        for token in splits:
            if __debug__: log('splitting {}', token)
            results = results + self._same_case_split(token, score, score(token))
        if __debug__: log('final results: {}', results)
        return results


    def _same_case_split(self, s, score, score_ns=0.0000005):
        if len(s) < 2:
            if __debug__: log('"{}" cannot be split; returning as-is', s)
            return [s]

        split     = None
        n         = len(s)
        i         = 0
        max_score = -1
        threshold = max(score(s), score_ns)
        if __debug__: log('_same_case_split on {}, threshold {}', s, threshold)
        while i < n:
            left       = s[0:i]
            right      = s[i:n]
            score_l    = score(left)
            score_r    = score(right)
            prefix     = self._is_prefix(left) or self._is_suffix(right)
            to_split_l = math.sqrt(score_l) > threshold
            to_split_r = math.sqrt(score_r) > threshold

            if __debug__: log('|{} : {}| l = {} r = {} split_l = {:1b} split_r'
                              ' = {:1b} prefix = {:1b} threshold = {} max_score = {}',
                              left, right, math.sqrt(score_l), math.sqrt(score_r),
                              to_split_l, to_split_r, prefix, threshold, max_score)

            if not prefix and to_split_l and to_split_r:
                if __debug__: log('--> case 1')
                if (score_l + score_r) > max_score:
                    if __debug__: log('({} + {}) > {}', score_l, score_r, max_score)
                    max_score = score_l + score_r
                    split = [left, right]
                    if __debug__: log('case 1 split result: {}', split)
                else:
                    if __debug__: log('no split for case 1')
            elif not prefix and to_split_l:
                if __debug__: log('--> case 2 -- recursive call on "{}"', s[i:n])
                tmp = self._same_case_split(right, score, score_ns)
                if tmp[0] != right:
                    split = [left] + tmp
                    if __debug__: log('case 2 split result: {}', split)
                else:
                    if __debug__: log('no split for case 2')
            i += 1
        result = split if split else [s]
        if __debug__: log('<-- returning {}', result)
        return result


    def _generate_scoring_function(self):
        '''Returns a closure that computes a score using the frequency tables
        with which the splitter has been initialized.
        '''
        if self._local_freq:
            log_all_freq = math.log10(sum(self._local_freq.values()))
            def scoring_function(w):
                local_f  = self._local_freq[w] if w in self._local_freq else 0
                global_f = self._global_freq[w] if w in self._global_freq else 0
                if w not in self._global_freq:
                    return local_f
                if w not in self._local_freq:
                    return global_f/log_all_freq
                else:
                    return local_f + global_f/log_all_freq
        else:
            def scoring_function(w):
                return self._global_freq[w] if w in self._global_freq else 0
        return scoring_function


    def _is_prefix(self, s):
        return s.lower() in prefixes


    def _is_suffix(self, s):
        return s.lower() in suffixes


# Module entry points.
# .............................................................................

_SAMURAI_INSTANCE = Samurai()

# The following are the functions we tell people to use:

init  = _SAMURAI_INSTANCE.init
split = _SAMURAI_INSTANCE.split
