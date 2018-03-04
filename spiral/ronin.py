'''Ronin: an identifier splitter based on the Samurai algorithm

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

Ronin is a Python module that implements an approach that was originally
based on Samurai, described in the following paper:

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
help produce more "natural" splits.  Ronin has a number of notable changes
compared to Samurai and many tunable parameters.

Usage
-----

Note #1: for fastest performance, using the optimization options provided by
the Python interpreter (i.e., the options -O or -OO).

Note #2: If you do not call init() separately, then the first time you call
ronin.split(...) it will call init() itself.  This will make the first call
to split(...)  take much longer to run than subsequent invocation.  Please
rest assured that this is only a one-time startup cost for a given session.

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
    ronin.init(global_freq = myfrequencies)
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
turn on logging by setting the logging level to "logging.DEBUG" before
importing the Ronin module.  Here is an example:

  import logging
  logging.basicConfig(level = logging.DEBUG, format = '')
  from spiral import ronin

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
modified algorithm, I chose "Ronin" (a name referring to a drifter samurai
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

import bisect
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
    logging.basicConfig(level = logging.INFO)
    logger = logging.getLogger('Ronin')
    def log(s, *other_args): logger.debug('Ronin: ' + s.format(*other_args))

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
except:
    sys.path.append("..")

try:
    from .frequencies import *
    from .simple_splitters import heuristic_split, elementary_split
    from .constants import *
except:
    from frequencies import *
    from simple_splitters import heuristic_split, elementary_split
    from constants import *


# Global constants.
# .............................................................................

# If the caller doesn't supply a frequency table, we use a default one.
# The file needs to be kept in the same directory as this Python module file.

try:
    _DEFAULT_FREQ_DIR = os.path.dirname(__file__)
except:
    _DEFAULT_FREQ_DIR = os.path.dirname('.')
_DEFAULT_FREQ_PICKLE = os.path.join(_DEFAULT_FREQ_DIR, 'data/frequencies.pklz')
'''Pickle file storing the default global frequency table shipped with this
module.  This constant is only read by ronin.init(...).'''


# Main class
# .............................................................................

class Ronin(object):
    _dictionary           = None
    _stemmer              = None
    _frequencies          = None
    _highest_freq         = None
    _length_cutoff        = None
    _min_short_freq       = None
    _low_freq_cutoff      = None
    _normal_exponent      = None
    _dict_word_exponent   = None
    _camel_bias           = None
    _split_bias           = 0.0000005
    _split_bias_threshold = 0
    _exact_case           = False

    # The default parameter values came from optimizing against the INTT data
    # set/oracle, then doing some hand tweaking.  The final score for INTT was:
    #    INTT:   17387/18772 (92.62%)
    # Using the Ludiso oracle/data set as a test set, with the same parameter
    # values, the following is the accuracy:
    #    Ludiso: 2231/2663   (83.78%)
    # It's possible to optimize against both data sets simultaneously and
    # gain slightly improved scores that way, but then testing against either
    # one would not be a reasonable test of accuracy -- it would be more of a
    # test of recall.  I feel it's more fair to use one for training and the
    # other for testing.
    #
    # Other notes: setting camel_bias=0 improves scores on INTT slightly, but
    # slightly worsens the score for Ludiso and worsens splits on some
    # inverse camel-case identifiers like "GPSmodule".
    #
    def init(self, frequencies=None, exact_case=False, low_freq_cutoff=339,
             length_cutoff=2, min_short_string_freq=273000,
             normal_exponent=0.3147, dict_word_exponent=0.1918,
             camel_bias=1, split_bias=0.000005):
        '''Initialize internal frequency files for the Ronin split() function.
        Note: the first time this function is called, it will take noticeable
        time because it will load a global frequency table (unless one is
        provided to override the default) and some NLTK dictionaries.

        Parameter 'frequencies' should be a dictionary where the keys are the
        terms and the values are integers representing the number of times
        the term appears in the code base.  A term that appears once will
        have a value of 1, a term that appears twice will have a value of 2,
        etc.  (Note that generating the global table is not a trivial
        undertaking.  It requires mining a large number of source code
        repositories to extract identifiers of classes, functions, variables,
        etc., then splitting them to produce individual identifier fragments,
        and finally curating the result manually.)  If not provided, Ronin will
        use a default table.

        Parameter 'exact_case' indicates whether the identifiers in the
        frequency table should be kept as-is, or whether only the lower-case
        form of the identifiers should be kept.  If False (the default),
        different case variations will be discarded and the maximum frequency
        of any case variation of a given identifier will be kept.  (E.g., if
        both 'foo' with frequency 20 and 'FOO' with frequency 1000 are
        present, the final table will have an entry for 'foo' with value
        1000.)  If True, all the case variants in the frequency table will be
        kept, and during scoring, the following alternatives will be tried in
        this order when searching for tokens in the table: try exact case
        match first, then capitalizing the token ('fOoO' -> 'Fooo'), and
        finally lower-casing the token ('Foo' or 'FOO' -> 'foo').  The first
        match will be returned.

        This init function also accepts a number of optional arguments that
        control internal parameter values.  The default values were
        determined by numerical optimization in conjunction with the default
        global frequency table shipped with Ronin.  In case you want to try
        searching for other values for a particular application, init()
        offers the following adjustable parameters, but beware that the
        values for optimal performance depend very much on the specific
        global frequency table you use and finding good values requires
        optimizing all the parameters simultaneously.

         * 'length_cutoff': sets a lower limit for string lengths, such that
           the frequency for any string shorter or equal to 'length_cutoff'
           needs to be higher than 'min_short_string_freq' or else it's taken
           to be 0 instead.

         * 'min_short_string_freq': minimum frequency of a short string that
           will be accepted.  If a string in the frequency table is shorter
           than 'length_cutoff' and its frequency value is lower than this,
           then its value will be taken as 0 instead.

         * 'low_freq_cutoff': used when scoring strings lacking camel case
           transitions, this is a cut-off value below which a given frequency
           value in the frequency table is treated as being 0.  This needs to
           have a value greater than 0 to have any effect.  For example, if
           the cutoff is set to 10, any frequency less than or equal to 10
           will be given a score of 0.  This threshold tends to counteract
           noisiness in global frequency tables created from a large number
           of disparate sofware projects.  (Note: the default frequency table
           provided with Ronin does not have entries with values less than 10
           in order to keep the file size small, but a full table is also
           provided with Spiral.  See the 'spiral/data' subdirectory of the
           package.)

         * 'normal_exponent': the value of an exponent in the formula used
           to adjust the frequency scores before they are used in the splitter
           algorithm.

         * 'dict_word_exponent': the value of an exponent in the formula used
           to adjust the frequency scores before they are used in the splitter
           algorithm, for the case when the token is a dictionary word.

         * 'camel_bias': multiplier used in a score comparison while deciding
           where to split string segments with an upper-to-lower case
           transition.

         * 'split_bias': when non-zero, this makes Ronin use an alternate
           splitting condition that is more "relaxed" when splitting
           identfiers without camel-case transitions.  This helps in some
           situations, but it also tends to cause more spurious splits.  A
           value of zero turns this off.  A non-zero value needs to be
           extremely small to have any effect.

        An optimization utility is included in the Spiral source code
        distribution, to help find parameter values for the above.

        '''
        if __debug__: log('init()')
        if not self._frequencies:
            if not frequencies:
                if __debug__: log('  loading frequency pickle {}'
                                  .format(_DEFAULT_FREQ_PICKLE))
                if os.path.exists(_DEFAULT_FREQ_PICKLE):
                    frequencies = frequencies_from_pickle(_DEFAULT_FREQ_PICKLE)
                else:
                    raise ValueError('Cannot read frequencies pickle file "{}"'
                                     .format(_DEFAULT_FREQ_PICKLE))
            if exact_case:
                self._frequencies = frequencies
            else:
                newdict = {}
                for key, value in frequencies.items():
                    lc_key = key.lower()
                    if lc_key in newdict:
                        newdict[lc_key] = max(value, newdict[lc_key])
                    else:
                        newdict[lc_key] = value
                self._frequencies = newdict
        self._exact_case = exact_case
        self._highest_freq = max(self._frequencies.values())
        self._split_bias = split_bias
        self._split_bias_threshold = self._split_bias * self._highest_freq
        self._low_freq_cutoff = low_freq_cutoff
        self._length_cutoff = length_cutoff
        self._min_short_freq = min_short_string_freq
        self._normal_exponent = normal_exponent
        self._dict_word_exponent = dict_word_exponent
        self._camel_bias = camel_bias
        if not self._dictionary:
            if __debug__: log('  initializing dictionary and stemmer')
            from nltk.corpus import words as nltk_words
            from nltk.corpus import wordnet as nltk_wordnet
            from nltk.stem import SnowballStemmer
            # Note: I also tried adding the words from /usr/share/dict/web,
            # but the only additional words it had that were not already in
            # the next two dicts were people's proper names. Not useful.
            self._dictionary = set(nltk_words.words())
            self._dictionary.update(nltk_wordnet.all_lemma_names())
            self._dictionary.update(special_computing_terms)
            self._stemmer = SnowballStemmer('english')
        # Generate scoring function based on exact case flag.  Do it here so
        # we don't have to keep testing the variable at run-time.
        if exact_case:
            def score_function(token):
                lc_token = token.lower()
                if lc_token in common_terms_with_numbers:
                    return self._highest_freq
                if token in self._frequencies:
                    return self._frequencies[token]
                cap_token = token.capitalize()
                if cap_token in self._frequencies:
                    return self._frequencies[cap_token]
                if lc_token in self._frequencies:
                    return self._frequencies[lc_token]
                return 0
        else:
            def score_function(token):
                lc_token = token.lower()
                if lc_token in common_terms_with_numbers:
                    return self._highest_freq
                if lc_token in self._frequencies:
                    return self._frequencies[lc_token]
                return 0
        self._score = score_function
        if __debug__:
            log('  frequency table has {} entries', len(self._frequencies))
            log('  highest frequency = {}', self._highest_freq)
            log('  dictionary has {} entries', len(self._dictionary))
            log('  split bias threshold = {}', self._split_bias_threshold)
            log('  low frequency cutoff = {}', self._low_freq_cutoff)
            log('  length cutoff = {}', self._length_cutoff)
            log('  minimum short string frequency = {}', self._min_short_freq)
            log('  normal exponent = {}', self._normal_exponent)
            log('  dictionary word exponent = {}', self._dict_word_exponent)
            log('  camel bias = {}', self._camel_bias)
            log('  exact_case = {}', self._exact_case)


    def split(self, identifier, keep_numbers=True):
        '''Split the given identifier string at token boundaries using a
        combination of heuristics and token frequency tables.  This function
        produces a list of strings as its output.

        Parameter 'keep_numbers' determines the handling of numbers.  When
        True, all digits are kept.  When False, the behavior is as follows:
        leading digits are removed from the identifier string but other
        digits are retained, then hard + camel-case splitting is performed,
        then (1) embedded digits are removed if they appear at the tail ends
        of tokens in the split, but not if they appear in the middle of
        tokens or are recognized as being part of common abbreviations such
        as 'utf8'; and (2) tokens that consist ONLY of digits are removed.
        The result may be more suitable for text analysis or machine learning.

        If you have a set of frequencies for your project, you can supply
        them to the function init(...) once, before making calls to split().
        This function will otherwise use a built-in global table of
        frequencies.

        Note: calling init(...) is optional, but if you do not call it, then
        this function will call it the first time it is invoked.  Consequently,
        the first time split(...) is called, you may experience a noticeable
        delay while it calls init(...) to load various data files.  Subsequent
        invocations of split(...) will not be as slow.

        The Ronin algorithm is a significant modification of the Samurai
        algorithm described by Eric Enslen, Emily Hill, Lori Pollock and
        K. Vijay-Shanker in a 2009 paper titled "Mining source code to
        automatically split identifiers for software analysis" (Proceedings
        of the 6th IEEE International Working Conference on Mining Software
        Repositories, 2009).
        '''
        splits = []
        if not self._frequencies:
            self.init()
        if __debug__: log('split "{}" (keep num: {})', identifier, keep_numbers)
        initial_list = heuristic_split(identifier, keep_numbers=keep_numbers)
        if __debug__: log('initial split = {}', initial_list)
        for s in initial_list:
            if __debug__: log('considering {}', s)
            if self._recognized(s):
                if __debug__: log('{} is a recognized token; using it as-is', s)
                splits = splits + [s]
                continue
            # Look for upper-to-lower case transitions.
            transition = re.search(r'[A-Z][a-z]', s)
            if not transition:
                if __debug__: log('no upper-to-lower case transition in {}', s)
                parts = [s]
            else:
                i = transition.start(0)
                if __debug__: log('case transition: {}{}', s[i], s[i+1])
                camel = s[i:] if i > 0 else s
                camel_score = self._score(camel)
                if __debug__: log('{} score = {}', camel, camel_score)
                alt = s[i+1:]
                # Logically, this next comparison should use the raw_score
                # rather than the adjusted or rescaled score.  Yet doing that
                # leads to worse performance even after optimizing the
                # parameters, and I don't know why.  Using the adjusted score
                # here seems like an apples-to-oranges comparison because of
                # the heavy rescaling applied by _adjusted_score().  Still,
                # the optimization results are clear and consistent.
                alt_score = self._adjusted_score(alt) * self._camel_bias
                if camel_score >= alt_score:
                    if __debug__: log('{} >= {} ==> include uppercase letter',
                                      camel_score, alt_score)
                    parts = [s[0:i], s[i:]] if i > 0 else [s]
                else:
                    if __debug__: log("{} < {} ==> don't include uppercase letter",
                                      camel_score, alt_score)
                    parts = [s[0:i+1], s[i+1:]]
                if __debug__: log('split outcome: {}', parts)
            splits = splits + parts

        if __debug__: log('turning over to _same_case_split: {}', splits)
        results = []
        for token in splits:
            token_score = self._adjusted_score(token)
            results = results + self._same_case_split(token, token_score)
        if __debug__: log('final results: {}', results)
        return results


    def _same_case_split(self, s, score_ns = .0000005, recursed = False):
        if self._recognized(s):
            if __debug__: log('{} is recognized; using it as-is', s)
            return [s]
        new_split = None
        max_score = -1
        max_index = len(s) - 1
        threshold = max(self._adjusted_score(s), score_ns)
        if __debug__: log('_same_case_split on {}, threshold {}', s, threshold)
        other_splits = []
        i = 0
        while i < max_index:
            i += 1
            left    = s[0:i]
            right   = s[i:]
            score_l = self._adjusted_score(left)
            score_r = self._adjusted_score(right)
            prefix  = self._is_prefix(left) or self._is_suffix(right)
            break_r = score_r > threshold
            break_l = score_l > threshold
            if self._split_bias > 0:
                break_l = break_l or (len(left) <= self._length_cutoff
                                      and score_r > self._split_bias_threshold)

            if __debug__: log('|{} : {}| score l = {:.4f} r = {:.4f}'
                              ' split l:r = {:1b}:{:1b} prfx = {:1b}'
                              ' th = {:4f} max_s = {:.4f}',
                              left, right, score_l, score_r, break_l,
                              break_r, prefix, threshold, max_score)

            if prefix:
                continue
            if break_l and break_r:
                if __debug__: log('--> case 1')
                if (score_l + score_r) > max_score:
                    if __debug__: log('({} + {}) > {}', score_l, score_r, max_score)
                    max_score = score_l + score_r
                    new_split = [left, right]
                    if __debug__: log('case 1 split result: {}', new_split)
                else:
                    if __debug__: log('no split for case 1')
            elif break_l:
                if __debug__: log('--> case 2 -- recursive call on "{}"', right)
                tmp = self._same_case_split(right, score_ns, recursed = True)
                if tmp[0] != right:
                    new_split = [left] + tmp
                    if __debug__: log('case 2 split result: {}', tmp)
                else:
                    if __debug__: log('no split for case 2')
            elif (break_r and not recursed and not new_split and self._recognized(right)
                  and (len(left) <= self._length_cutoff or self._recognized(left))):
                # Case where the left side doesn't exceed the threshold but the
                # right side is a recognized term.
                if __debug__: log('--> case 3 -- recognized "{}"', right)
                bisect.insort(other_splits, (score_r, [left, right]))

        if new_split:
            result = new_split
        elif other_splits:
            # We didn't find a split using our primary approach, but we have
            # potential alternative splits.  Pick the highest-scored one.
            result = other_splits[-1][1]
        else:
            result = [s]
        if __debug__: log('<-- returning {}', result)
        return result


    def _rescaled_score(self, token):
        '''Return the rescaled score for the given 'token', without applying
        the thresholding step that _adjusted_score() applies.'''
        return self._rescale(token, self._score(token))


    def _adjusted_score(self, token):
        '''Return the thresholded, adjusted score for the given 'token'.'''
        length = len(token)
        if length == 0:
            return 0
        score_value = self._score(token)
        if length <= self._length_cutoff:
            if score_value <= self._min_short_freq:
                return 0
        if score_value <= self._low_freq_cutoff:
            return 0
        return self._rescale(token, score_value)


    def _rescale(self, token, score_value):
        '''Rescale the given token score value.'''
        if self._recognized(token):
            return math.pow(score_value, self._dict_word_exponent)
        else:
            return math.pow(score_value, self._normal_exponent)


    def _recognized(self, token):
        tlower = token.lower()
        return (tlower in common_terms_with_numbers
                or tlower in special_computing_terms
                or self._stem(tlower) in special_computing_terms
                or self._in_dictionary(token))


    def _in_dictionary(self, word):
        if len(word) <= 1:
            # Counting single-letter words turns out to be unhelpful.
            return False
        word = word.lower()
        return (word in self._dictionary or self._stem(word) in self._dictionary)


    def _stem(self, token):
        # The NLTK stemmer sometimes gives weird results, and the particular
        # case of weird technical terms ending in 's' has been most troublesome.
        if len(token) > 1 and token[-1:] == 's':
            return token[:-1]
        else:
            return self._stemmer.stem(token)


    def _is_prefix(self, s):
        return s.lower() in prefixes


    def _is_suffix(self, s):
        return s.lower() in suffixes


# Module entry points.
# .............................................................................

_RONIN_INSTANCE = Ronin()

# The following are the functions we tell people to use:

init  = _RONIN_INSTANCE.init
split = _RONIN_INSTANCE.split
