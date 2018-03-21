'''Ronin: an identifier splitter based on the Samurai algorithm

Introduction
------------

Spiral is a Python 3 package that implements numerous identifier splitting
algorithms.  Identifier splitting is the task of breaking apart program
identifier strings such as 'getInt' or 'readUTF8stream' into component
tokens: ['get', 'int'] and ['read', 'utf8', 'stream'].  The need for
splitting identifiers arises in a variety of contexts, including natural
language processing (NLP) methods applied to source code analysis and program
comprehension.

Ronin is a Python module that implements an approach that was originally
based on Samurai, described in the following paper:

  Enslen, E., Hill, E., Pollock, L., & Vijay-Shanker, K. (2009).  Mining
  source code to automatically split identifiers for software analysis.  In
  Proceedings of the 6th IEEE International Working Conference on Mining
  Software Repositories (MSR'09) (pp. 71-80).

The implementation of Ronin in the present Python module was created by the
author from the description of the algorithm published in the paper, then
modified repeatedly in an attempt to improve performance.  A significant goal
in Ronin was to produce a splitter that had acceptable performance without
having to use a local frequency table derived from a source code base being
processed.  Ronin uses only a global frequency table derived from mining tens
of thousands of GitHub project repositories containing Python source code
files.  It also uses a dictionary of English words (from NLTK) to help
produce more "natural" splits.  Ronin has many notable changes compared to
Samurai and many tunable parameters.

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
argument 'frequencies':

    from spiral import ronin
    ronin.init(frequencies = myfrequencies)
    result = ronin.split('someidentifier')

The format of the value given to 'frequencies' should be a dictionary where
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

from   bisect import insort
import math
from   nltk.stem import SnowballStemmer
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
    _DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
except:
    _DATA_DIR = os.path.dirname('./data')

_DEFAULT_FREQ_PICKLE = os.path.join(_DATA_DIR, 'frequencies.pklz')
'''Pickle file storing the default global frequency table shipped with this
module.  This constant is only read by ronin.init(...).'''

_DICTIONARY_PICKLE = os.path.join(_DATA_DIR, 'dictionary.pklz')
'''Pickle file storing the dictionary used by Ronin.  See the code in
init() for the exact contents, but to summarize, it's comprised of some NLTK
dictionaries and the special_computing_terms set from constants.py'''


# Main class
# .............................................................................

class Ronin(object):
    _dictionary         = None
    _stemmer            = None
    _frequencies        = None
    _highest_freq       = None
    _length_cutoff      = None
    _short_min_freq     = None
    _low_freq_cutoff    = None
    _normal_exponent    = None
    _dict_word_exponent = None
    _camel_bias         = None
    _recognition_bias   = 0.0000003635
    _biased_threshold   = 0
    _alt_exponent       = 1
    _exact_case         = False

    # The default parameter values came from optimizing against the INTT data
    # set/oracle, then doing some hand-tweaking of the parameter values.
    # The final score for INTT was:
    #    INTT:   17287/18772 (92.09%)
    # Using the Ludiso oracle/data set as a test set, with the same parameter
    # values, the following is the accuracy:
    #    Ludiso: 2248/2663   (84.42%)
    #
    # Many of the "failures" against these sets of identifiers are actually
    # not failures, but cases that Ronin clearly gets a more correct answer
    # or where there is a legitimate difference in interpretation.  Examples:
    #
    #   Token            Ludiso               Ronin
    #   --------         ----------------     -------------
    #   fread            fread                f, read
    #   a.ecart_         a, ecart             a, e, cart
    #   ReadUtf8Z        Read, Utf, 8, Z      Read, Utf8, Z
    #   MAPI_BCC         MAPI, BCC            M, API, BCC
    #   GetWSIsEnabled   Get, WSIs, Enabled   Get, WS, Is, Enabled
    #
    # Names like 'fread' could be considered appropriate to leave alone, but
    # 'fread' actually stands for 'file read' and thus IMHO it makes sense to
    # split it -- splitting identifiers into meaningful tokens is the purpose
    # of Ronin, after all.
    #
    # Some other differences with Ludiso are due to Ronin splitting terms
    # that are more typically considered separate words but are treated as
    # one word in Ludiso, or vice versa.  Examples:
    #
    #   Token                Ludiso                  Ronin
    #   --------             ----------------        -------------
    #   FF_LOSS_COLORSPACE   FF, LOSS, COLORSPACE    FF, LOSS, COLOR, SPACE
    #   m_bFilenameMode      m, b, File, name, Mode  m, b, Filename, Mode
    #
    # (The main entry in Wikipedia for "color space" is two words, while for
    # "filename" it is indeed one word.)  So, Ronin's performance may
    # actually be better than the pure numbers imply.  However, without going
    # through every Ludiso case and manually reinterpreting the splits, we
    # can't say for sure whether it really is.
    #
    # All that aside, it is definitely the case that Ronin gets many cases
    # wrong.  It is not perfect by any means.
    #
    # Other notes:
    #
    # * Ronin is tuned for splitting program identifiers, which is NOT the
    #   same as splitting strings of concatenated words.  With its default
    #   parameter values, it is not good at splitting strings like
    #   "driveourtrucks" which are not composed of tokens commonly
    #   encountered in source code contexts.
    #
    # * Ronin was trained on source code repositories containing Python code.
    #   The default frequency table may not be optimal for splitting things
    #   that come from non-Python source files, although the test results on
    #   Ludiso and INTT show that it is pretty good on non-Python content.
    #
    # * Reducing the value of parameter low_freq_cutoff increases Ronin's
    #   tendency to split tokens, but at the expense of worsening scores on
    #   the INTT and Ludiso data sets.  However, it's notable that reducing
    #   the value to something like 10 makes Ronin more likely to split
    #   concatenated word strings like "driveourtrucks" or "societynamebank".
    #
    def init(self, frequencies = None, exact_case = False,
             low_freq_cutoff = 340, length_cutoff = 2, short_min_freq = 286540,
             normal_exponent = 0.1527, dict_word_exponent = 0.1228,
             camel_bias = 8.6319, recognition_bias = 0.0000003635,
             alt_exponent = 1.2165):
        '''Initialize internal frequency files for the Ronin split() function.
        Note: the first time this function is called, it will take noticeable
        time because it will load a global frequency table (unless one is
        provided to override the default) and some NLTK dictionaries.

        Parameter 'frequencies' should be a dictionary where the keys are the
        terms and the values are integers representing the number of times
        the term appears in the code base.  A term that appears once will
        have a value of 1, a term that appears twice will have a value of 2,
        etc.  If not provided, Ronin will use a default table.  (Note that
        generating the global table is not a trivial undertaking.  It
        requires mining a large number of source code repositories to extract
        identifiers of classes, functions, variables, etc., then splitting
        them to produce individual identifier fragments, and finally curating
        the result manually.)

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
        optimizing all the parameters simultaneously -- a compute-intensive
        process:

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

         * 'length_cutoff': sets a lower limit for string lengths, such that
           the frequency for any string shorter or equal to 'length_cutoff'
           needs to be higher than 'short_min_freq' or else the
           frequency value is taken to be 0 instead.

         * 'short_min_freq': minimum frequency of a short string that
           will be accepted.  If a string in the frequency table is shorter
           than 'length_cutoff' and its frequency value is lower than this,
           then its value will be taken as 0 instead.

         * 'normal_exponent': the value of an exponent in the formula used
           to adjust the frequency scores before they are used in the splitter
           algorithm.

         * 'dict_word_exponent': the value of an exponent in the formula used
           to adjust the frequency scores before they are used in the splitter
           algorithm, for the case when the token is a dictionary word.

         * 'camel_bias': multiplier used in a score comparison when deciding
           where to split string segments with an upper-to-lower case
           transition.

         * 'recognition_bias': multiplier used in a score comparison when a
           token is recognized (e.g., due to being a dictionary word or being
           defined in a list of common special terms).  This factor is
           multiplied by the highest frequency in the frequency table, so if
           the highest frequency is very large, the value of recognition_bias
           needs to be extremely small to have any effect.

         * 'alt_exponent': an exponent used in rescaling scores when there is
           more than one possible split to choose from.

        Changing only a single parameter value is unlikely to yield good
        results.  Beware of testing changes on a few chosen examples: you may
        be able to get acceptable results for those few cases but will likely
        find that performance worsens on other cases.  Adjusting parameter
        values is really best done using multiparameter optimization methods.
        An optimization utility is included in the Spiral source code
        distribution, to help find parameter values for the above.
        '''
        if __debug__: log('init()')
        if not self._frequencies:
            if not frequencies:
                if __debug__: log('... loading frequency pickle {}'
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
        self._recognition_bias = recognition_bias
        self._biased_threshold = self._recognition_bias * self._highest_freq
        self._low_freq_cutoff = low_freq_cutoff
        self._length_cutoff = length_cutoff
        self._short_min_freq = short_min_freq
        self._normal_exponent = normal_exponent
        self._dict_word_exponent = dict_word_exponent
        self._camel_bias = camel_bias
        self._alt_exponent = alt_exponent
        if not self._dictionary:
            if os.path.exists(_DICTIONARY_PICKLE):
                if __debug__: log('... loading pickled dictionary {}'
                                  .format(_DICTIONARY_PICKLE))
                import gzip, pickle
                with gzip.open(_DICTIONARY_PICKLE, 'rb') as pickle_file:
                    self._dictionary = pickle.load(pickle_file)
            else:
                if __debug__: log('... initializing dictionary and stemmer')
                from nltk.corpus import words as nltk_words
                from nltk.corpus import wordnet as nltk_wordnet
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
            log('... frequency table has {} entries', len(self._frequencies))
            log('... highest frequency = {}', self._highest_freq)
            log('... dictionary has {} entries', len(self._dictionary))
            log('... exact_case = {}', self._exact_case)
            log('... low frequency cutoff = {}', self._low_freq_cutoff)
            log('... length cutoff = {}', self._length_cutoff)
            log('... short string min frequency = {}', self._short_min_freq)
            log('... normal exponent = {}', self._normal_exponent)
            log('... dictionary word exponent = {}', self._dict_word_exponent)
            log('... camel bias = {}', self._camel_bias)
            log('... recognition bias = {}', self._recognition_bias)
            log('... biased threshold = {}', self._biased_threshold)
            log('... alt exponent = {}', self._alt_exponent)


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
        camel = False
        if not self._frequencies:
            self.init()
        if __debug__: log('split "{}" (keep num: {})', identifier, keep_numbers)
        initial_list = heuristic_split(identifier, keep_numbers=keep_numbers)
        if __debug__: log('initial split = {}', initial_list)
        for s in initial_list:
            if __debug__: log('considering "{}"', s)
            if self._recognized(s):
                if __debug__: log('"{}" is a recognized token; using it as-is', s)
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
                if __debug__: log('"{}" score = {}', camel, camel_score)
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
                    if __debug__: log('"{}" >= {} ==> include uppercase letter',
                                      camel_score, alt_score)
                    parts = [s[0:i], s[i:]] if i > 0 else [s]
                else:
                    if __debug__: log("\"{}\" < {} ==> don't include uppercase letter",
                                      camel_score, alt_score)
                    parts = [s[0:i+1], s[i+1:]]
                if __debug__: log('split outcome: {}', parts)
            splits = splits + parts

        results = []
        for token in splits:
            score = self._adjusted_score(token)
            results = results + self._same_case_split(token, score)[1]
        if __debug__: log('final results: {}', results)
        return results


    def _same_case_split(self, s, score_ns = .0000005, level = 0):
        # Returns a tuple of (max_score, split).
        # 'level' is to detect recursive calls, and also indent debug output.
        if __debug__: sp = ' '*(3*level)
        if __debug__: log('{}same_case_split "{}", th {:.3f}', sp, s, score_ns)
        if self._recognized(s):
            if __debug__: log('{}recognized "{}" -- returning as-is', sp, s)
            return (score_ns, [s])
        new_split = None
        max_index = len(s) - 1
        max_score = -1
        threshold = max(self._adjusted_score(s), score_ns)
        splits = []
        i = 0
        while i < max_index:
            i += 1
            left, right = s[0:i], s[i:]
            prefix = self._is_prefix(left) or (len(s) > 5 and self._is_suffix(right))

            if prefix:
                if __debug__: log('{}"{}" or "{}" is pref/suf', sp, left, right)
                continue

            score_l = self._adjusted_score(left)
            score_r = self._adjusted_score(right)
            break_r = score_r > threshold
            break_l = score_l > threshold
            either_score = max(score_l, score_r)

            if __debug__: log('{}|{} : {}| score l = {:.3f} r = {:.3f}'
                              ' split l:r = {:1b}:{:1b} prfx = {:1b}:{:1b}'
                              ' th = {:.3f} max_s = {:.3f}',
                              sp, left, right, score_l, score_r,
                              break_l, break_r, self._is_prefix(left),
                              self._is_suffix(right), threshold, max_score)

            if break_l and break_r:
                if __debug__: log('{}case 1 -- both sides', sp)
                if (score_l + score_r) > max_score:
                    if __debug__: log('{}({} + {}) > {}', sp, score_l, score_r, max_score)
                    max_score = score_l + score_r
                    new_split = [left, right]
                    insort(splits, (max_score, new_split))
                    if __debug__: log('{}case 1: split {}', sp, new_split)
                else:
                    if __debug__: log('{}case 1: no split', sp)
            elif break_l:
                if (either_score > self._biased_threshold and self._recognized(right)):
                    if __debug__: log('{}case 2 prefer "{}"', sp, right)
                    insort(splits, (either_score, [left, right]))
                else:
                    if __debug__: log('{}case 3 -- recursive call on "{}"', sp, right)
                    ts, tmp = self._same_case_split(right, score_ns, level + 1)
                    if tmp[0] != right:
                        new_split = [left] + tmp
                        insort(splits, (ts/len(new_split), new_split))
                        if __debug__: log('{}case 3: split result {}', sp, tmp)
                    elif self._special_case(right):
                        max_score = either_score
                        insort(splits, (either_score, [left, right]))
                        if __debug__: log('{}case 3: recognized "{}"', sp, right)
                    else:
                        if __debug__: log('{}case 3: no split', sp)
            elif break_r and (self._recognized(left)
                              or len(left) <= self._length_cutoff
                              or self._special_case(right)):
                if either_score > self._biased_threshold:
                    if __debug__: log('{}case 4: score {:.3f}', sp, either_score)
                    insort(splits, (score_r/len(left), [left, right]))
                elif self._recognized(right):
                    if __debug__: log('{}case 5: recognized "{}"', sp, right)
                    insort(splits, (score_r, [left, right]))

        if __debug__: log('{}done looking for splits', sp)
        if splits:
            alt_score, alt_split = splits[-1]
            scaled_score = alt_score/math.pow(len(alt_split), self._alt_exponent)
            if scaled_score >= score_ns:
                if __debug__: log('{}using alt split {}', sp, alt_score)
                result = splits[-1]
            else:
                if __debug__: log('{}using original {}', sp, s)
                result = (score_ns, [s])
        else:
            result = (max_score, [s])
        if __debug__: log('{}returning {}', sp, result)
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
        if length <= self._length_cutoff and not self._special_case(token):
            if score_value <= self._short_min_freq:
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
        return self._special_case(tlower) or self._in_dictionary(tlower)


    def _special_case(self, token):
        return (token in common_terms_with_numbers
                or token in special_computing_terms
                or self._stem(token) in special_computing_terms)


    def _in_dictionary(self, word):
        if len(word) <= 1:
            # Counting single-letter words turns out to be unhelpful.
            return False
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
