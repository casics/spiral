'''
Ronin: identifier splitter based on the Samurai algorithm

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
as Samurai, published by Eric Enslen, Emily Hill, Lori Pollock and
K. Vijay-Shanker from the University of Delaware in 2009.

  Enslen, E., Hill, E., Pollock, L., & Vijay-Shanker, K. (2009).  Mining
  source code to automatically split identifiers for software analysis.  In
  Proceedings of the 6th IEEE International Working Conference on Mining
  Software Repositories (MSR'09) (pp. 71-80).

The implementation in the present Python module was created by the author
from the description of the algorithm published in the paper, then modified
based on ideas derived from experiences with Samurai.

Usage
-----

Note #1: for fastest performance, using the optimization options provided by
the Python interpreter (i.e., the options -O or -OO).

Note #2: If you do not call init(...) separately, then the first time you
call ronin.split(...) it will call init(...) itself.  This will make split(...)
take much longer to run than subsequent invocation.  Please rest assured that
this is only a one-time startup cost.

The simplest way to use this module in a Python program is to import the
module from the Spiral package and then call ronin.split() with a string. For
example,

    from spiral import ronin
    result = ronin.split('someidentifier')

The function split(...) produces a list of strings as its output.  It will do
its best-guess at how a given identifier should be split using a built-in
table of term frequencies, prefixes, and suffixes.  The built-in table of
term frequencies came from an analysis of 20,000 randomly selected software
projects in GitHub that contained at least one Python source code file.

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
(2009) for their identifier splitting algorithm.  Ronin is almost identical
to Samurai, but it would be inappropriate to call this implementation Samurai
too.  In an effort to imply the lineage of this modified algorithm, I chose
"ronin" (a name referring to a drifter samurai without a master, during the
Japanese feudal period).

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

_LEN_1_MIN_FACTOR = 0.02
'''Factor used in a formula to calculate the score given to all single-character
strings.  The formula sets the score value based on the values of all strings
in the frequency table, as follows:

   score = _LEN_1_MIN_FACTOR*(min(frequency of all single-char strings))

This score is then used anytime a string of length 1 is score; the actual score
of the string in the frequency table is ignored when splitting identifiers.
This approach is meant to compensate for the fact that single characters tend
to have quite high frequency scores, and as a consequence, cause the splitter
to be overly-aggressive in accepting some splits.
'''

_IGNORED_FREQ_THRESHOLD = 10
'''Cut-off value below which a frequency in the frequency table is treated as
being 0.  This needs to have a value greater than 0 to have any effect.  This
threshold tends to counteract noisiness in global frequency tables created from
a large number of disparate sofware projects.
'''

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
    _global_freq        = None
    _local_freq         = None
    _dictionary         = None
    _stemmer            = None
    _len_1_string_score = 50

    def init(self, local_freq=None, global_freq=None):
        '''Initialize internal frequency files for the Ronin split() function.
        Parameter 'local_freq' should be a dictionary where the keys are the
        terms and the values are integers representing the number of times
        the term appears in the code base.  A term that appears once will
        have a value of 1, a term that appears twice will have a value of 2,
        etc.  Similarly, 'glocal_freq' should be a dictionary for global
        frequencies of all terms in a large sample of code bases.

        Note: the first time this function is called, it will take noticeable
        time because it loads a number of data files.
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

            self._dictionary = set(nltk_words.words())
            self._dictionary.update(nltk_wordnet.all_lemma_names())
            self._stemmer = SnowballStemmer('english')
        self._len_1_string_score = (_LEN_1_MIN_FACTOR * min(
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
        # if len(s) < 2:
        #     if __debug__: log('"{}" cannot be split; returning as-is', s)
        #     return [s]

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


    def _rescale(self, token, value):
        if len(token) == 1:
            return self._len_1_string_score
        if value <= _IGNORED_FREQ_THRESHOLD:
            return 0
        if self._in_dictionary(token):
            return value
        return math.sqrt(value)


    def _in_dictionary(self, word):
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
