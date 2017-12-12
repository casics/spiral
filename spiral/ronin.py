'''ronin: Modified version of the Samurai algorithm for identifier splitting

Introduction
------------

Natural language processing (NLP) methods are increasingly being applied to
source code analysis for various purposes.  The methods rely on terms
(identifiers and other textual strings) extracted from program source code
and comments.  The methods often work better if, instead of raw identifiers,
real words are used as features; that is, "get" and "string" are often better
features for NLP tools than an identifier "getString".  This leads to the
need for automated methods for splitting identifiers of classes, functions,
variables, and other entities into word-like constituents. A number of
methods have been proposed an implemented to perform identifier splitting.

Ronin is a Python module that implements a modified version of a splitter
known as Samurai, published by Eric Enslen, Emily Hill, Lori Pollock and
K. Vijay-Shanker from the University of Delaware in 2009.

  Enslen, E., Hill, E., Pollock, L., & Vijay-Shanker, K. (2009).  Mining
  source code to automatically split identifiers for software analysis.  In
  Proceedings of the 6th IEEE International Working Conference on Mining
  Software Repositories (MSR'09) (pp. 71-80).

The ronin algorithm is very similar to Samurai, and only introduces the
following modifications (1) if the given string S is a single character,
return it right away; (2) if the given string S is a common dictionary word,
return it without attempting to split it; (3) when checking if the left side
of a candidate split is a prefix, also check if the right side is a common
dictionary word; and (4) when calculating the score for to_split_l and
to_split_r, adjust the score slightly based on whether a word is a common
dictionary word or not.

Usage
-----

Note: for fastest performance, using the optimization options provided by the
Python interpreter (i.e., the options -O or -OO).

To use this module in a Python program, simply import Spiral and then call
ronin_split() with a string. For example,

    from spiral import ronin_split
    result = ronin_split('someidentifier')

The function ronin_split produces a list of strings as its output.  It will
do its best-guess at how a given identifier should be split using a built-in
table of term frequencies, prefixes, suffixes, and an English dictionary.

Tracing the algorithm
---------------------

To print what the splitter is doing while processing a given string, you can
turn on logging by setting the logging level to "logging.DEBUG".  Search for
logging.basicConfig(...) in the code below and change the line
    logging.basicConfig(level=logging.INFO,  format='samurai: %(message)s')
to
    logging.basicConfig(level=logging.DEBUG, format='samurai: %(message)s')
Logging will be printed to the standard output stream.  Note: this will only
work if you did not use the -O option to the Python interpreter.

This module wraps all logging code with the Python __debug__ compile-time
symbol, so that you can use the -O flag to Python to make it omit the code
completely.  This is more efficient than simply setting the logging level.

Explanation of the name
-----------------------

The name "ronin" is a play on the use of the name "Samurai" by Enslen et al.
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

import enchant
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
    logging.basicConfig(level=logging.INFO, format='samurai: %(message)s')
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

# I tried using NLTK's dictionary for the dictionary checks, but it was much
# slower than using PyEnchant's.
#    from nltk.corpus import words as nltk_words
#    dictionary = nltk_words.words()

_dictionary = enchant.Dict("en_US")

# The lists of prefixes and suffixes came from the web page for Samurai,
# https://hiper.cis.udel.edu/Samurai/Samurai.html
#
# Enslen, E., Hill, E., Pollock, L., & Vijay-Shanker, K. (2009).
# Mining source code to automatically split identifiers for software analysis.
# In Proceedings of the 6th IEEE International Working Conference on Mining
# Software Repositories (MSR'09) (pp. 71-80).

prefix_list = ['afro', 'ambi', 'amphi', 'ana', 'anglo', 'apo', 'astro', 'bi',
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

suffix_list = ['a', 'ac', 'acea', 'aceae', 'acean', 'aceous', 'ade', 'aemia',
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


# Main functions.
# .............................................................................

def ronin_split(identifier):
    splits = []
    if __debug__: log('splitting {}'.format(identifier))
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
            if camel_score > rescale(alt, alt_score):
                if __debug__: log('{} > {} ==> better to include uppercase letter',
                                  camel_score, rescale(alt, alt_score))
                if i > 0:
                    parts = [s[0:i], s[i:]]
                else:
                    parts = [s]
            else:
                if __debug__: log('not better to include uppercase letter')
                parts = [s[0:i+1], s[i+1:]]
            if __debug__: log('split outcome: {}', parts)
        splits = splits + parts

    if __debug__: log('turning over to same_case_split: {}', splits)
    results = []
    for token in splits:
        if __debug__: log('splitting {}', token)
        results = results + same_case_split(token, score(token))
    if __debug__: log('final results: {}', results)
    return results


def same_case_split(s, score_ns=0.0000005):
    '''Modified version of sameCaseSplit() from the paper by Enslen et al.
    Modifications: (1) if the given string 's' is a single character, return
    it right away; (2) if the given string 's' is a common dictionary word,
    return it without splitting it; (3) when checking if the left side of
    a candidate split is a prefix, also check if the right side is a common
    dictionary word; and (4) when calculating the score for to_split_l and
    to_split_r, adjust the score slightly, based on whether a word is a common
    dictionary word or not.
    '''

    if len(s) < 2:
        if __debug__: log('"{}" cannot be split; returning as-is', s)
        return [s]
    elif len(s) > 1 and in_dictionary(s):
        if __debug__: log('"{}" is a dictionary word; returning as-is', s)
        return [s]

    split     = None
    n         = len(s)
    i         = 0
    max_score = -1
    threshold = max(score(s), score_ns)
    if __debug__: log('threshold score = {}', threshold)
    while i < n:
        left       = s[0:i]
        right      = s[i:n]
        score_l    = score(left)
        score_r    = score(right)
        prefix     = is_prefix(left) or is_suffix(right)
        to_split_l = rescale(left, score_l) > threshold
        to_split_r = rescale(right, score_r) > threshold

        if __debug__: log('|{} : {}| l = {} r = {} split_l = {:1b} split_r = {:1b} prefix = {:1b} threshold = {} max_score = {}',
                          left, right, rescale(left, score_l), rescale(right, score_r), to_split_l, to_split_r, prefix, threshold, max_score)

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
            tmp = same_case_split(right, score_ns)
            if tmp[0] != right:
                split = [left] + tmp
                if __debug__: log('case 2 split result: {}', split)
            else:
                if __debug__: log('no split for case 2')
        i += 1
    result = split if split else [s]
    if __debug__: log('<-- returning {}', result)
    return result


# Utilities.
# .............................................................................

def rescale(token, value):
    if len(token) <= 1:
        return 0
    elif len(token) <= 4 and in_dictionary(token):
        return math.pow(value, 1.0/2)
    else:
        return math.pow(value, 1.0/2.5)


def in_dictionary(word):
    return _dictionary.check(word.lower())


def is_prefix(s):
    return s.lower() in prefix_list


def is_suffix(s):
    return s.lower() in suffix_list


def score(w):
    f = word_frequency(w)
    return 0 if f < 30 else f
    # return 0 if not w else word_frequency(w)
