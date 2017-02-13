#!/usr/bin/env python3.4
#
# @file    samurai.py
# @brief   Implementation of the Samurai algorithm for identifier splitting
# @author  Michael Hucka
#
# <!---------------------------------------------------------------------------
# Copyright (C) 2015 by the California Institute of Technology.
# This software is part of CASICS, the Comprehensive and Automated Software
# Inventory Creation System.  For more information, visit http://casics.org.
# ------------------------------------------------------------------------- -->

import csv
import enchant
import math
import plac
import re
from   scipy.interpolate import interp1d
import sys

sys.path.append('../common')

from utils import *
from logger import *
from simple_splitters import simple_split


# Global constants.
# .............................................................................

# I tried using NLTK's dictionary for the dictionary checks, but it was much
# slower than using PyEnchant's.
#    from nltk.corpus import words as nltk_words
#    dictionary = nltk_words.words()

_dictionary = enchant.Dict()

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

_interpolated = None
_raw_frequencies = None


# Main functions.
# .............................................................................


def same_case_split(s, score_ns=0.0000005):
    '''Modified version of sameCaseSplit() from the paper by Enslen et al.
    Modifications: (1) if the given string 's' is a single character, return
    it right away; (2) if the given string 's' is a common dictionary word,
    return it without splitting it; and (3) when checking if the left side of
    a candidate split is a prefix, also check if the right side is a common
    dictionary word.
    '''
    log = Logger().get_log()

    if len(s) < 2:
        log.debug('"{}" cannot be split; returning as-is'.format(s))
        return [s]
    elif len(s) > 1 and in_dictionary(s):
        log.debug('"{}" is a dictionary word; returning as-is'.format(s))
        return [s]

    split     = None
    n         = len(s)
    i         = 0
    max_score = -1
    threshold = max(score(s), score_ns)
    log.debug('threshold score = {}'.format(threshold))
    while i < n:
        left       = s[0:i]
        right      = s[i:n]
        score_l    = score(left)
        score_r    = score(right)
        prefix     = (is_prefix(left) and not in_dictionary(right)) or is_suffix(right)
        to_split_l = rescale(score_l) > threshold
        to_split_r = rescale(score_r) > threshold

        log.debug('|{} : {}| l = {} r = {} split_l = {:1b} split_r = {:1b} prefix = {:1b} threshold = {} max_score = {}'
                  .format(left, right, rescale(score_l), rescale(score_r), to_split_l, to_split_r, prefix, threshold, max_score))

        if not prefix and to_split_l and to_split_r:
            log.debug('--> case 1')
            if (score_l + score_r) > max_score:
                log.debug('({} + {}) > {}'.format(score_l, score_r, max_score))
                max_score = score_l + score_r
                split = [left, right]
                log.debug('case 1 split result: {}'.format(split))
            else:
                log.debug('no split for case 1')
        elif not prefix and to_split_l:
            log.debug('--> case 2 -- recursive call on "{}"'.format(s[i:n]))
            tmp = same_case_split(right, score_ns)
            if tmp[0] != right:
                split = [left] + tmp
                log.debug('case 2 split result: {}'.format(split))
            else:
                log.debug('no split for case 2')
        i += 1
    result = split if split else [s]
    log.debug('<-- returning {}'.format(result))
    return result


def mixed_case_split(identifier):
    log = Logger().get_log()
    splits = []
    log.debug('splitting {}'.format(identifier))
    for s in simple_split(identifier):
        # Look for upper-to-lower case transitions
        transition = re.search(r'[A-Z][a-z]', s)
        if not transition:
            log.debug('no upper-to-lower case transition in {}'.format(s))
            parts = [s]
        else:
            i = transition.start(0)
            log.debug('case transition: {}{}'.format(s[i], s[i+1]))
            if i > 0:
                camel_score = score(s[i:])
                log.debug('"{}" score {}'.format(s[i:], camel_score))
            else:
                camel_score = score(s)
                log.debug('"{}" score {}'.format(s, camel_score))
            alt_score = score(s[i+1:])
            log.debug('"{}" alt score {}'.format(s[i+1:], alt_score))
            if camel_score > rescale(alt_score):
                log.debug('{} > {} ==> better to include uppercase letter'
                          .format(camel_score, rescale(alt_score)))
                if i > 0:
                    parts = [s[0:i], s[i:]]
                else:
                    parts = [s]
            else:
                log.debug('not better to include uppercase letter')
                parts = [s[0:i+1], s[i+1:]]
            log.debug('split outcome: {}'.format(parts))
        splits = splits + parts

    log.debug('turning over to same_case_split: {}'.format(splits))
    results = []
    for token in splits:
        log.debug('splitting {}'.format(token))
        results = results + same_case_split(token, score(token))
    log.debug('final results: {}'.format(results))
    return results


# Utilities.
# .............................................................................

def rescale(value):
    return math.sqrt(value)
#    return value
#    return math.log(value) if value > 0 else 0


def in_dictionary(word):
    return _dictionary.check(word.lower())


def is_prefix(s):
    return s.lower() in prefix_list


def is_suffix(s):
    return s.lower() in suffix_list


def score(w):
    return 0 if not w else word_frequency(w)


def frequencies_from_file(filename, filter_words=None):
    log = Logger().get_log()
    try:
        log.debug('reading word frequencies from {}'.format(filename))
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, fieldnames=['word','frequency'])
            frequencies = {}
            total = 0
            for row in reader:
                if filter_words and row['word'] in filter_words:
                    continue
                value = int(row['frequency'])
                frequencies[row['word']] = value
                total += value
            log.debug('read {} entries'.format(len(frequencies)))
            return (frequencies, total)
    except Exception as err:
        log.error(err)
        return ({}, 0)


def init_word_frequencies():
    global _interpolated, _raw_frequencies
    (_raw_frequencies, total) = frequencies_from_file('frequencies.csv')
    _interpolated = interp1d([0, total], [0, 1])


def word_frequency(w):
    global _interpolated, _raw_frequencies
    # return _interpolated(_raw_frequencies[w]) if w in _raw_frequencies else 0
    return int(_raw_frequencies[w]) if w in _raw_frequencies else 0


# Quick test interface.
# .............................................................................

def run_cases(bias):
    msg('-- {}'.format(bias) + '-'*70)
    print(same_case_split('finditer', bias))
    print(same_case_split('isnumber', bias))
    print(same_case_split('isbetterfile', bias))
    print(same_case_split('threshold', bias))
    print(same_case_split('iskeyword', bias))
    print(same_case_split('fileio', bias))
    print(same_case_split('initdb', bias))
    print(same_case_split('terraindata', bias))   # terrain data
    print(same_case_split('treservations', bias)) # treservations
    print(same_case_split('trigname', bias))
    print(same_case_split('undirected', bias))
    print(same_case_split('usemap', bias))
    print(same_case_split('versionend', bias))
    print(same_case_split('vframe', bias))
    print(same_case_split('vqgen', bias))
    print(same_case_split('sampfmt', bias)) # samp fmt
    print(same_case_split('sampy', bias))   # sampy
    print(same_case_split('readcmd', bias))
    print(same_case_split('uval', bias))
    print(same_case_split('updatecpu', bias))
    print(same_case_split('textnode', bias))
    print(same_case_split('sandcx', bias)) # sandcx
    print(same_case_split('mpegts', bias)) # mpeg ts
    print(same_case_split('mixmonitor', bias))
    print(same_case_split('imhand', bias)) # im hand
    print(same_case_split('connectpath', bias))


def run_test(debug=False, loglevel='info'):

    '''Test word_extractor.py.'''
    log = Logger(os.path.splitext(sys.argv[0])[0], console=True).get_log()
    if debug:
        log.set_level('debug')
    else:
        log.set_level(loglevel)

    init_word_frequencies()
    print(mixed_case_split('GPSmodule'))
    print(mixed_case_split('bigTHING'))
    print(mixed_case_split('ABCFooBar'))
    print(mixed_case_split('getMAX'))
    print(mixed_case_split('FOOOBAR'))
    print(mixed_case_split('SqlList'))
    print(mixed_case_split('ASTVisitor'))
    print(mixed_case_split('finditer'))
    print(mixed_case_split('isnumber'))
    print(mixed_case_split('isbetterfile'))
    print(mixed_case_split('threshold'))
    print(mixed_case_split('iskeyword'))
    print(mixed_case_split('fileio'))
    print(mixed_case_split('initdb'))
    print(mixed_case_split('terraindata'))   # terrain data
    print(mixed_case_split('treservations')) # treservations
    print(mixed_case_split('trigname'))
    print(mixed_case_split('undirected'))
    print(mixed_case_split('usemap'))
    print(mixed_case_split('versionend'))
    print(mixed_case_split('vframe'))
    print(mixed_case_split('vqgen'))
    print(mixed_case_split('sampfmt')) # samp fmt
    print(mixed_case_split('sampy'))   # sampy
    print(mixed_case_split('readcmd'))
    print(mixed_case_split('uval'))
    print(mixed_case_split('updatecpu'))
    print(mixed_case_split('textnode'))
    print(mixed_case_split('sandcx')) # sandcx
    print(mixed_case_split('mpegts')) # mpeg ts
    print(mixed_case_split('mixmonitor'))
    print(mixed_case_split('imhand')) # im hand
    print(mixed_case_split('connectpath'))
    # # run_cases(0.0001)
    # # run_cases(0.00001)
    # # run_cases(0.00002)
    # # run_cases(0.00003)
    # # run_cases(0.00004)
    # # run_cases(0.00005)
    # # run_cases(0.00006)
    # # run_cases(0.00007)
    # # run_cases(0.00008)
    # # run_cases(0.00009)
    # # run_cases(0.000001)
    # # run_cases(0.000002)
    # # run_cases(0.000003)
    # # run_cases(0.000004)
    # # run_cases(0.000005)
    # # run_cases(0.000006)
    # # run_cases(0.000007)
    # # run_cases(0.000008)
    # # run_cases(0.000009)
    # # run_cases(0.0000095)
    # # run_cases(0.0000001)
    # # run_cases(0.0000005)
    # # run_cases(0.00000001)
    # # run_cases(0.000000001)
    # # run_cases(0.0000000001)

    if debug:
        import ipdb; ipdb.set_trace()

run_test.__annotations__ = dict(
    debug    = ('drop into ipdb after parsing',     'flag',   'd'),
    loglevel = ('logging level: "debug" or "info"', 'option', 'L'),
)

if __name__ == '__main__':
    plac.call(run_test)
