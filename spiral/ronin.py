'''Ronin: identifier splitter based on the Samurai algorithm

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

Ronin is a Python module that implements a variation of the algorithm known
as Samurai, described in the following paper:

  Enslen, E., Hill, E., Pollock, L., & Vijay-Shanker, K. (2009).  Mining
  source code to automatically split identifiers for software analysis.  In
  Proceedings of the 6th IEEE International Working Conference on Mining
  Software Repositories (MSR'09) (pp. 71-80).

The implementation of Ronin in the present Python module was created by the
author from the description of the algorithm published in the paper, then
modified based on ideas derived from experiences with Samurai.  A significant
goal in Ronin was to produce a splitter that had acceptable performance
without having to use a local frequency table derived from a source code base
being processed.  Ronin uses only a global frequency table derived from
mining tens of thousands of GitHub project repositories containing Python
source code files.  It also uses a dictionary of English words (from NLTK) to
help produce more "natural" splits.

Usage
-----

Note #1: for fastest performance, using the optimization options provided by
the Python interpreter (i.e., the options -O or -OO).

Note #2: If you do not call init(...) separately, then the first time you
call ronin.split(...) it will call init(...) itself.  This will make the
first call to split(...)  take much longer to run than subsequent invocation.
Please rest assured that this is only a one-time startup cost.

The simplest way to use this module in a Python program is to import the
module from the Spiral package and then call ronin.split(...) with a
string.  For example,

    from spiral import ronin
    result = ronin.split('someidentifier')

The function split(...) produces a list of strings as its output.  It will do
its best-guess at how a given identifier should be split using a built-in
table of term frequencies, prefixes, and suffixes.  The built-in table of
term frequencies came from an analysis of over 46,000 randomly selected
software projects in GitHub that contained at least one Python source code
file.

Ronin's performance can be tuned by providing it with a different table of
term frequencies.  If you want to experiment with using a different set of
global frequencies, you can supply them to the function init(...) once,
before making any calls to split(...).  (This is done so that the cost of
computations involved in the frequencies is only done once.)  Use the keyword
argument 'global_freq':

    from spiral import ronin
    ronin.init(global_freq=myfrequencies)
    result = ronin.split('someidentifier')

The format of the value given to 'global_freq' should be a dictionary where
the keys are the terms and the values are integers representing the number of
times the term appears in the code base.  A term that appears once will have
a value of 1, a term that appears twice will have a value of 2, etc.  Ronin
will normalize the values.  (Do NOT normalize the values yourself, as this
will confuse the algorithm.)  Note that generating the global table is not a
trivial undertaking.  It requires mining a large number of source code
repositories to extract identifiers of classes, functions, variables, etc.,
then splitting them to produce individual identifier fragments, and finally
curating the result manually.

Finally, init(...) accepts additional arguments for tuning some other
parameters that control how it calculates costs of splitting identifiers.
The default values of the parameters were determined using numerical
optimization methods.  Please see the documentation for init(...) for more
information.

Tracing the algorithm
---------------------

To print what the splitter is doing while processing a given string, you can
turn on logging by setting the logging level to "logging.DEBUG".  Search for
logging.basicConfig(...) in the code below and change the line

    logging.basicConfig(level=logging.INFO,  format='ronin: %(message)s')
to
    logging.basicConfig(level=logging.DEBUG, format='ronin: %(message)s')

Logging will be printed to the standard output stream.  Note: this will only
work if you do NOT use the -O option to the Python interpreter.

Optimization
------------

This module wraps all logging code with the Python __debug__ compile-time
symbol, so that you can use the -O flag to Python to make it omit the code
completely.  This is more efficient than simply setting the logging level.

Explanation of the name
-----------------------

The name "Ronin" is a play on the use of the name "Samurai" by Enslen et al.
(2009) for their identifier splitting algorithm.  The bulk of Ronin is
identical to Samurai, but it would be inappropriate to call this
implementation Samurai too.  In an effort to imply the lineage of this
modified algorithm, I chose "ronin" (a name referring to a drifter samurai
without a master, during the Japanese feudal period).

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

# NOTE: to turn on debugging, make sure python -O was *not* used when this
# file was byte-compiled, and then change logging.INFO to logging.DEBUG below.
# Conversely, to optimize out all the debugging code, use python -O or -OO
# and everything inside "if __debug__" blocks will be entirely compiled out.
if __debug__:
    import logging
    logging.basicConfig(level=logging.INFO, format='ronin: %(message)s')
    logger = logging.getLogger('')
    def log(s, *other_args): logger.debug(s.format(*other_args))

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
except:
    sys.path.append("..")

try:
    from .frequencies import *
    from .simple_splitters import simple_split
except:
    from frequencies import *
    from simple_splitters import simple_split


# Global constants.
# .............................................................................

# If the caller doesn't supply a frequency table, we use a default one.
# The file needs to be kept in the same directory as this Python module file.

try:
    _DEFAULT_FREQ_DIR = os.path.dirname(__file__)
except:
    _DEFAULT_FREQ_DIR = os.path.dirname('.')
_DEFAULT_FREQ_PICKLE = os.path.join(_DEFAULT_FREQ_DIR, 'frequencies.pklz')
'''Pickle file storing the default global frequency table shipped with this
module.  This constant is only read by Ronin.init(...).'''

# The list of prefixes from the web page for Samurai,
# https://hiper.cis.udel.edu/Samurai/Samurai.html
#
# Enslen, E., Hill, E., Pollock, L., & Vijay-Shanker, K. (2009).
# Mining source code to automatically split identifiers for software analysis.
# In Proceedings of the 6th IEEE International Working Conference on Mining
# Software Repositories (MSR'09) (pp. 71-80).
#
# Note: Samurai uses both a list of prefixes and a list of suffixes, but in
# my testing with Ronin (which has a number of algorithmic changes compared
# to Samurai), using an optimization approach to find parameter values,
# Ronin's performance was not improved by using the suffix test.  This may be
# due to Ronin's use of a dictionary check, which Samurai doesn't use, or due
# to other changes.  Ronin doesn't use the suffix test for that reason.

_PREFIX_LIST = ['afro', 'ambi', 'amphi', 'ana', 'anglo', 'apo', 'astro', 'bi',
                'bio', 'circum', 'cis', 'co', 'col', 'com', 'con', 'contra',
                'cor', 'cryo', 'crypto', 'de', 'de', 'demi', 'di', 'dif',
                'dis', 'du', 'duo', 'eco', 'electro', 'em', 'en', 'epi',
                'euro', 'ex', 'franco', 'geo', 'hemi', 'hetero', 'homo',
                'hydro', 'hypo', 'ideo', 'idio', 'il', 'im', 'infra', 'inter',
                'intra', 'ir', 'iso', 'macr', 'mal', 'maxi', 'mega', 'megalo',
                'micro', 'midi', 'mini', 'mis', 'mon', 'multi', 'neo', 'omni',
                'paleo', 'para', 'ped', 'peri', 'poly', 'pre', 'preter',
                'proto', 'pyro', 're', 'retro', 'semi', 'socio', 'supra',
                'sur', 'sy', 'syl', 'sym', 'syn', 'tele', 'trans', 'tri',
                'twi', 'ultra', 'un', 'uni']


# Main class
# .............................................................................

class Ronin(object):
    _dictionary       = None
    _stemmer          = None

    _global_freq        = None
    _length_cutoff      = None
    _min_short_freq     = None
    _low_freq_cutoff    = None
    _normal_exponent    = None
    _dict_word_exponent = None
    _permissive         = True

    def init(self, global_freq=None, low_freq_cutoff=1850,
             length_cutoff=2, min_short_string_freq=500000,
             normal_exponent=0.25, dict_word_exponent=0.5, permissive=True):
        '''Initialize internal frequency files for the Ronin split() function.
        Note: the first time this function is called, it will take noticeable
        time because it will load a large default global frequency table
        (unless one is provided to override the default).

        Parameter 'global_freq' should be a dictionary where the keys are the
        terms and the values are integers representing the number of times
        the term appears in the code base.  A term that appears once will
        have a value of 1, a term that appears twice will have a value of 2,
        etc.  (Note that generating the global table is not a trivial
        undertaking.  It requires mining a large number of source code
        repositories to extract identifiers of classes, functions, variables,
        etc., then splitting them to produce individual identifier fragments,
        and finally curating the result manually.)

        This initialization function also accepts a number of optional
        arguments that control internal parameter values.  Their default
        values were determined by numerical optimization in conjunction with
        the default global frequency table shipped with Ronin.  In case you
        want to try searching for other values for a particular application,
        init() offers the following adjustable parameters, but beware that the
        values for optimal performance depend very much on the specific global
        frequency table you use:

         * 'length_cutoff': sets a lower limit for string lengths, such
           that the score for any string shorter or equal to 'length_cutoff'
           needs to be higher than 'min_short_string_freq' or else it's taken
           to be 0 instead.

         * 'min_short_string_freq': minimum frequency of a short string that
           will be accepted.  If a string in the frequency table is shorter
           than 'length_cutoff' and its frequency value is higher than this,
           then its value will be taken as 0 instead.

         * 'low_freq_cutoff': a cut-off value below which a given
           frequency value in the frequency table is treated as being 0.
           This needs to have a value greater than 0 to have any effect.  For
           example, if the cutoff is set to 10, any frequency less than or
           equal to 10 will be given a score of 0.  This threshold tends to
           counteract noisiness in global frequency tables created from a
           large number of disparate sofware projects.

         * 'normal_exponent': the value of an exponent in the formula used
           to adjust the frequency scores before they are used in the splitter
           algorithm.  See the internal function _rescale() to understand how
           this is used.

         * 'dict_word_exponent': the value of an exponent in the formula used
           to adjust the frequency scores before they are used in the splitter
           algorithm, for the case when the token is a dictionary word.  See
           the internal function _rescale() to understand how this is used.

         * 'permissive': when True, this makes Ronin use an alternate splitting
           condition in _same_case_split() that is more "relaxed" than when the
           value is False.  In the author's experience, True produces slightly
           more natural splits, but to be fair, what constitutes "natural" to
           the author may not be natural to other people.  (The original
           algorithm for Samurai, on which Ronin is based, uses the equivalent
           of False.)
        '''
        if __debug__: log('init()')
        if global_freq:
            self._global_freq = global_freq
        if not self._global_freq:
            if __debug__: log('loading frequency pickle {}'
                              .format(_DEFAULT_FREQ_PICKLE))
            if os.path.exists(_DEFAULT_FREQ_PICKLE):
                self._global_freq = frequencies_from_pickle(_DEFAULT_FREQ_PICKLE)
            else:
                raise ValueError('Cannot read default frequencies pickle file "{}"'
                                 .format(_DEFAULT_FREQ_PICKLE))

        if not self._dictionary:
            if __debug__: log('initializing dictionary and stemmer')
            from nltk.corpus import words as nltk_words
            from nltk.corpus import wordnet as nltk_wordnet
            from nltk.stem import SnowballStemmer
            # Note: I also tried adding the words from /usr/share/dict/web,
            # but the only additional words it had that were not already in
            # the next two dicts were people's proper names. Not useful.
            self._dictionary = set(nltk_words.words())
            self._dictionary.update(nltk_wordnet.all_lemma_names())
            self._stemmer = SnowballStemmer('english')

        self._low_freq_cutoff = low_freq_cutoff
        self._length_cutoff = length_cutoff
        self._min_short_freq = min_short_string_freq
        self._normal_exponent = normal_exponent
        self._dict_word_exponent = dict_word_exponent
        self._permissive = permissive


    def split(self, identifier):
        '''Split the given identifier string at token boundaries using a
        combination of heuristics and token frequency tables.  This function
        produces a list of strings as its output.  The Ronin algorithm is a
        modification of the Samurai described by Eric Enslen, Emily Hill,
        Lori Pollock and K. Vijay-Shanker in a 2009 paper titled "Mining
        source code to automatically split identifiers for software analysis"
        (Proceedings of the 6th IEEE International Working Conference on
        Mining Software Repositories, 2009).

        If you have a set of frequencies for your project, you can supply
        them to the function init(...) once, before making calls to split().
        This function will otherwise use a built-in global table of
        frequencies.

        Note: calling init(...) is optional, but if you do not call it, then
        this function will call it the first time it is invoked.  Consequently,
        the first time split(...) is called, you may experience a noticeable
        delay while it calls init(...) to load various data files.  Subsequent
        invocations of split(...) will not be as slow.
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
                if camel_score >= self._rescale(alt, alt_score):
                    if __debug__: log('{} > {} ==> better to include uppercase letter',
                                      camel_score, self._rescale(alt, alt_score))
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


    def _same_case_split(self, s, score, score_ns=.0000005):
        n = len(s)
        if n > 1 and self._in_dictionary(s):
            if __debug__: log('{} is a dictionary word; using it as-is', s)
            return [s]
        i         = 0
        split     = None
        max_score = -1
        threshold = max(self._rescale(s, score(s)), score_ns)
        if __debug__: log('_same_case_split on {}, threshold {}', s, threshold)
        while i < n:
            left       = s[0:i]
            right      = s[i:n]
            score_l    = self._rescale(left, score(left))
            score_r    = self._rescale(right, score(right))
            prefix     = self._is_prefix(left)
            to_split_l = score_l > threshold
            to_split_r = score_r > threshold

            if __debug__: log('|{} : {}| score l = {:6f} r = {:6f}'
                              ' split l:r = {:1b}:{:1b}'
                              ' prefix = {:1b} th = {} max_score = {}',
                              left, right, score_l, score_r,
                              to_split_l, to_split_r, prefix, threshold, max_score)

            try_alternate = (not prefix and to_split_l)
            if not prefix and ((self._permissive and (to_split_l or to_split_r))
                               or (to_split_l and to_split_r)):
                if not self._permissive:
                    try_alternate = False
                if __debug__: log('--> case 1')
                if (score_l + score_r) > max_score:
                    if __debug__: log('({} + {}) > {}', score_l, score_r, max_score)
                    max_score = score_l + score_r
                    split = [left, right]
                    if __debug__: log('case 1 split result: {}', split)
                else:
                    if __debug__: log('no split for case 1')
                    if self._permissive:
                        try_alternate = True
            if try_alternate:
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
        def scoring_function(w):
            if w in self._global_freq:
                return self._global_freq[w]
            else:
                w = w.lower()
                if w in self._global_freq:
                    return self._global_freq[w]
                else:
                    return 0

        return scoring_function


    def _rescale(self, token, score_value):
        if len(token) <= self._length_cutoff:
            if score_value <= self._min_short_freq:
                return 0
        if score_value <= self._low_freq_cutoff:
            return 0
        elif self._in_dictionary(token):
            return math.pow(score_value, self._dict_word_exponent)
        else:
            return math.pow(score_value, self._normal_exponent)


    def _in_dictionary(self, word):
        word = word.lower()
        return (word in self._dictionary
                or self._stemmer.stem(word) in self._dictionary)


    def _is_prefix(self, s):
        return s.lower() in _PREFIX_LIST


    def _is_suffix(self, s):
        return s.lower() in _SUFFIX_LIST


# Module entry points.
# .............................................................................

_RONIN_INSTANCE = Ronin()

# The following are the functions we tell people to use:

init  = _RONIN_INSTANCE.init
split = _RONIN_INSTANCE.split
