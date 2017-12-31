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
source code files.

Usage
-----

Note #1: for fastest performance, using the optimization options provided by
the Python interpreter (i.e., the options -O or -OO).

Note #2: If you do not call init(...) separately, then the first time you
call ronin.split(...) it will call init(...) itself.  This will make the
first call to split(...)  take much longer to run than subsequent invocation.
Please rest assured that this is only a one-time startup cost.

The simplest way to use this module in a Python program is to import the
module from the Spiral package and then call ronin.split() with a string. For
example,

    from spiral import ronin
    result = ronin.split('someidentifier')

The function split(...) produces a list of strings as its output.  It will do
its best-guess at how a given identifier should be split using a built-in
table of term frequencies, prefixes, and suffixes.  The built-in table of
term frequencies came from an analysis of randomly selected software projects
in GitHub that contained at least one Python source code file.

Ronin's performance can be tuned by providing it with a project-specific table
of term frequencies.  If you have a set of frequencies for your project, you
can supply them to the function init(...) once, before making any calls to
split(...).  (This is done so that the cost of computations involved in the
frequencies is only done once.)  Use the keyword argument 'local_freq'

    from spiral import ronin
    ronin.init(local_freq=myfrequencies)
    result = ronin.split('someidentifier')

The format of the value given to 'local_freq' should be a dictionary where
the keys are the terms and the values are integers representing the number of
times the term appears in the code base.  A term that appears once will have
a value of 1, a term that appears twice will have a value of 2, etc.  Some
terms for large code bases can have values that go into the hundreds of
thousands or millions; this is okay, as Ronin will normalize the values.
(Do NOT normalize the values yourself, as this will confuse the algorithm.)

You can also change the global frequency table that Ronin uses.  This can
be passed using the keyword argument 'global_freq' to init(...):

    ronin.init(global_freq=globalfrequencies)

or together in combination with a local frequency table,

    ronin.init(global_freq=globalfrequencies, local_freq=projectfrequencies)

Note that generating the global table is not a trivial undertaking.  It
requires mining a large number of source code repositories to extract
identifiers of classes, functions, variables, etc., then splitting them to
produce individual identifier fragments, and finally curating the result
manually.

Finally, init() accepts additional arguments for tuning some other parameters
that control how it calculates costs of splitting identifiers.  The default
values of the parameters were determined using numerical optimization
methods.  Please see the documentation for init() for more information.

Tracing the algorithm
---------------------

To print what the splitter is doing while processing a given string, you can
turn on logging by setting the logging level to "logging.DEBUG".  Search for
logging.basicConfig(...) in the code below and change the line

    logging.basicConfig(level=logging.INFO,  format='ronin: %(message)s')
to
    logging.basicConfig(level=logging.DEBUG, format='ronin: %(message)s')

Logging will be printed to the standard output stream.  Note: this will only
work if you did not use the -O option to the Python interpreter.

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
    from .utils import msg
except:
    from frequencies import *
    from simple_splitters import simple_split
    from utils import msg


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
module.  This constant is only read by Ronin.init().'''

# The lists of prefixes and suffixes came from the web page for Samurai,
# https://hiper.cis.udel.edu/Samurai/Samurai.html
#
# Enslen, E., Hill, E., Pollock, L., & Vijay-Shanker, K. (2009).
# Mining source code to automatically split identifiers for software analysis.
# In Proceedings of the 6th IEEE International Working Conference on Mining
# Software Repositories (MSR'09) (pp. 71-80).

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

_SUFFIX_LIST = ['a', 'ac', 'acea', 'aceae', 'acean', 'aceous', 'ade', 'aemia',
                'agogue', 'aholic', 'al', 'ales', 'algia', 'amine', 'ana',
                'anae', 'ance', 'ancy', 'androus', 'andry', 'ane', 'ar',
                'archy', 'ard', 'aria', 'arian', 'arium', 'ary', 'ase',
                'athon', 'ation', 'ative', 'ator', 'atory', 'biont', 'biosis',
                'cade', 'caine', 'carp', 'carpic', 'carpous', 'cele', 'cene',
                'centric', 'cephalic', 'cephalous', 'cephaly', 'chory',
                'chrome', 'cide', 'clast', 'clinal', 'cline', 'coccus',
                'coel', 'coele', 'colous', 'cracy', 'crat', 'cratic',
                'cratical', 'cy', 'cyte', 'derm', 'derma', 'dermatous', 'dom',
                'drome', 'dromous', 'eae', 'ectomy', 'ed', 'ee', 'eer', 'ein',
                'eme', 'emia', 'en', 'ence', 'enchyma', 'ency', 'ene', 'ent',
                'eous', 'er', 'ergic', 'ergy', 'es', 'escence', 'escent',
                'ese', 'esque', 'ess', 'est', 'et', 'eth', 'etic', 'ette',
                'ey', 'facient', 'fer', 'ferous', 'fic', 'fication', 'fid',
                'florous', 'foliate', 'foliolate', 'fuge', 'ful', 'fy',
                'gamous', 'gamy', 'gen', 'genesis', 'genic', 'genous', 'geny',
                'gnathous', 'gon', 'gony', 'grapher', 'graphy', 'gyne',
                'gynous', 'gyny', 'ia', 'ial', 'ian', 'iana', 'iasis',
                'iatric', 'iatrics', 'iatry', 'ibility', 'ible', 'ic',
                'icide', 'ician', 'ick obsolete', 'ics', 'idae', 'ide', 'ie',
                'ify', 'ile', 'ina', 'inae', 'ine', 'ineae', 'ing', 'ini',
                'ious', 'isation', 'ise', 'ish', 'ism', 'ist', 'istic',
                'istical', 'istically', 'ite', 'itious', 'itis', 'ity', 'ium',
                'ive', 'ization', 'ize', 'kinesis', 'kins', 'latry', 'lepry',
                'ling', 'lite', 'lith', 'lithic', 'logue', 'logist', 'logy',
                'ly', 'lyse', 'lysis', 'lyte', 'lytic', 'lyze', 'mancy',
                'mania', 'meister', 'ment', 'merous', 'metry', 'mo', 'morph',
                'morphic', 'morphism', 'morphous', 'mycete', 'mycetes',
                'mycetidae', 'mycin', 'mycota', 'mycotina', 'ness', 'nik',
                'nomy', 'odon', 'odont', 'odontia', 'oholic', 'oic', 'oid',
                'oidea', 'oideae', 'ol', 'ole', 'oma', 'ome', 'ont', 'onym',
                'onymy', 'opia', 'opsida', 'opsis', 'opsy', 'orama', 'ory',
                'ose', 'osis', 'otic', 'otomy', 'ous', 'para', 'parous',
                'pathy', 'ped', 'pede', 'penia', 'phage', 'phagia', 'phagous',
                'phagy', 'phane', 'phasia', 'phil', 'phile', 'philia',
                'philiac', 'philic', 'philous', 'phobe', 'phobia', 'phobic',
                'phony', 'phore', 'phoresis', 'phorous', 'phrenia', 'phyll',
                'phyllous', 'phyceae', 'phycidae', 'phyta', 'phyte',
                'phytina', 'plasia', 'plasm', 'plast', 'plasty', 'plegia',
                'plex', 'ploid', 'pode', 'podous', 'poieses', 'poietic',
                'pter', 'rrhagia', 'rrhea', 'ric', 'ry', 's', 'scopy',
                'sepalous', 'sperm', 'sporous', 'st', 'stasis', 'stat',
                'ster', 'stome', 'stomy', 'taxy', 'th', 'therm', 'thermal',
                'thermic', 'thermy', 'thon', 'thymia', 'tion', 'tome', 'tomy',
                'tonia', 'trichous', 'trix', 'tron', 'trophic', 'tropism',
                'tropous', 'tropy', 'tude', 'ty', 'ular', 'ule', 'ure',
                'urgy', 'uria', 'uronic', 'urous', 'valent', 'virile',
                'vorous', 'xor', 'y', 'yl', 'yne', 'zoic', 'zoon', 'zygous',
                'zyme']


# Main class
# .............................................................................

class Ronin(object):
    _dictionary         = None
    _stemmer            = None

    _global_freq        = None
    _local_freq         = None
    _clamp_len_1_scores = True
    _len_1_score        = None
    _length_cutoff      = None
    _low_freq_cutoff    = None
    _rescale_exponent   = None

    def init(self, local_freq=None, global_freq=None, len_1_factor=0,
             low_frequency_cutoff=33, length_cutoff=2, rescale_exponent=0.535):
        '''Initialize internal frequency files for the Ronin split() function.
        Parameter 'local_freq' should be a dictionary where the keys are the
        terms and the values are integers representing the number of times
        the term appears in the code base.  A term that appears once will
        have a value of 1, a term that appears twice will have a value of 2,
        etc.  Similarly, 'glocal_freq' should be a dictionary for global
        frequencies of all terms in a large sample of code bases.

        Note: the first time this function is called, it will take noticeable
        time because it will load a large default global frequency table
        (unless one is provided to override the default).

        This initialization function also accepts a number of optional
        arguments that control internal parameter values.  Their default
        values were determined by numerical optimization in conjunction with
        the default global frequency table shipped with Ronin.  In case you
        want to try searching for other values for a particular application,
        init() offers the following adjustable parameters, but beware that the
        values for optimal performance depend on the specific global frequency
        table you use.

         * 'len_1_factor': sets the value of a factor used in a formula to
           calculate a fixed score given to all single-character strings.
           Setting this value to 0 makes all single-character strings have a
           score of 0.  Setting this value to -1 causes the formula to be
           ignored and the natural score of each length-1 string to be used
           instead.  Setting this value to something greater than 0 sets the
           score of every length-1 string to a value computed by the formula

             score = len_1_factor*(min(every frequency of all 1-char strings))

           The resulting value is then used anytime a string of length 1 is
           being scored; in other words, the actual frequency of the string
           in the frequency table is ignored when splitting identifiers, and
           the score used is this value instead.  The approach of clamping
           the scores of single-character strings is meant to compensate for
           the fact that single characters tend to have quite high frequency
           scores, and as a consequence, cause the splitter to be
           overly-aggressive in accepting some splits.

         * 'low_frequency_cutoff': a cut-off value below which a given
           frequency value in the frequency table is treated as being 0.
           This needs to have a value greater than 0 to have any effect.  For
           example, if the cutoff is set to 10, any frequency less than or
           equal to 10 will be given a score of 0.  This threshold tends to
           counteract noisiness in global frequency tables created from a
           large number of disparate sofware projects.

         * 'length_cutoff': sets a lower limit for string lengths, such
           that the score for any string shorter or equal to 'length_cutoff'
           will be set to 0 instead.

         * 'rescale_exponent': the value of an exponent in the formula used
           to adjust the frequency scores before they are used in the splitter
           algorithm.  See the internal function _rescale() to understand how
           this is used.
        '''
        if __debug__: log('init()')
        if local_freq:
            self._local_freq = local_freq
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

        self._low_freq_cutoff = low_frequency_cutoff
        self._length_cutoff = length_cutoff
        self._rescale_exponent = rescale_exponent
        if len_1_factor < 0:
            self._clamp_len_1_scores = False
        else:
            self._len_1_score = (len_1_factor * min(
                f for s, f in self._global_freq.items() if len(s) == 1))


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
                if camel_score > self._rescale(alt, alt_score):
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


    def _same_case_split(self, s, score, score_ns=0.0000005):
        if self._in_dictionary(s):
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
            to_split_l = self._rescale(left, score_l) > threshold
            to_split_r = self._rescale(right, score_r) > threshold

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


    def _rescale(self, token, score_value):
        if len(token) == 1:
            if self._clamp_len_1_scores:
                return self._len_1_score
        elif len(token) <= self._length_cutoff:
            return 0

        if score_value <= self._low_freq_cutoff:
            return 0
        else:
            return math.pow(score_value, self._rescale_exponent)


    def _in_dictionary(self, word):
        word = word.lower()
        return word in self._dictionary or self._stemmer.stem(word) in self._dictionary


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
