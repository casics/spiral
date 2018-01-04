#!/usr/bin/env python3 -OO
'''Find parameter values for Nostril.

Introduction
------------

This uses a multiobjective optimization approach to tune the parameter values
for the arguments of `generate_nonsense_detector()`.  It uses the Python
package Platypus, specifically its implementation of the multiobjective
optimization algorithm NSGA-II ("Non-dominated Sorting Genetic Algorithm").
The objective functions minimize by this script are the errors on a
combination of positive and negative examples of nonsense strings.

The nature of the optimization problem is such that it is not possible to
find an optimal behavior for the nonsense string evaluator: the evaluator
will always produce some number of false positives on real identifier strings
and some number of false negatives on random text strings, and pushing one
number lower will push the other one higher.  The optimization process here
will do its best, but will ultimately only result in a surface and we have to
pick what matters to us subjectively.  The result of running this
optimization script will be a file containing a list of lines of values.
Each line will have a set of false positive and false negative values and the
parameter values that led to those particular results.  In the final usage of
this optimization script, I sorted these results and then picked a
(subjective) balance of very low false positives and some not-too-high false
negatives.

Usage
-----

This is a simple script that you run by executing it on the command line:

  ./optimize.py

The output is written to a file named `optimization-output.txt`.  You have to
sort the lines of the file, then look at the results and decide which
combination of false positives and false negatives you're willing to accept,
and finally, read off the corresponding parameter values.

Authors
-------

Michael Hucka <mhucka@caltech.edu>

Copyright
---------

Copyright (c) 2017 by the California Institute of Technology.  This software
was developed as part of the CASICS project, the Comprehensive and Automated
Software Inventory Creation System.  For more, visit http://casics.org.

'''

from   contextlib import redirect_stdout
import humanize
import os
import plac
from   platypus import *
import re
import string
import sys
from   time import time

if '__file__' in globals():
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(thisdir, '../'))
    sys.path.append(os.path.join(thisdir, '../..'))
    sys.path.append(os.path.join(thisdir, '../spiral'))
else:
    sys.path.append('../')
    sys.path.append('../..')
    sys.path.append('../spiral')

from spiral import ronin

# Global variables
# .............................................................................

cases = {}

# Objective function
# .............................................................................

def find_parameters(vars):
    global cases

    var_low_freq_cutoff       = int(vars[0])
    var_length_cutoff         = 2
    var_min_short_string_freq = int(vars[1])*100000
    var_normal_exponent       = vars[2]
    var_dict_word_exponent    = vars[3]
    #var_permissive           = vars[4][0] # param will be a list of booleans
    var_permissive            = True

    ronin.init(low_freq_cutoff=var_low_freq_cutoff,
               length_cutoff=var_length_cutoff,
               min_short_string_freq=var_min_short_string_freq,
               normal_exponent=var_normal_exponent,
               dict_word_exponent=var_dict_word_exponent,
               permissive=var_permissive)

    failures = 0
    for id, expected in cases.items():
        result = ronin.split(id)
        if result != expected:
            failures += 1

    print('{} failures: freq_cutoff = {} len_cutoff = {} '
          'short_freq = {} normal_exp = {:05f} dict_exp = {:05f} '
          'perm = {}'
          .format(failures, var_low_freq_cutoff, var_length_cutoff,
                  var_min_short_string_freq, var_normal_exponent,
                  var_dict_word_exponent, var_permissive),
          flush=True)
    return [failures]


# Platypus hacks.
# .............................................................................

# This is a cheat to allow mixing Real and Integer types for the variables.
# Platypus's definition of Real is very simple and Integer can be made quite
# compatible with it, but Platypus' default definition of Integer is not, and
# if you mix Real and Integer in the variables list, you will get an error.
# The hack below relies on the fact that Platypus checks all the other
# variables against the type of the first one.  So, we make an Integer type
# that is based on Real and use that type as a variable other than the first
# variable in the list.  (Hey, don't judge me for this, okay?)

class MyInteger(Real):
    def __init__(self, range_min, range_max):
        super(Type, self).__init__()
        self.elements = range(range_min, range_max)
        self.min_value = range_min
        self.max_value = range_max - 1

    def rand(self):
        indices = list(range(1, len(self.elements)))
        random.shuffle(indices)
        return self.elements[indices[0]]

    def __str__(self):
        return "MyInteger(%d, %d)" % (len(self.elements), self.size)


# Code to run the optimization.
# .............................................................................

# Define our problem: N variables and M objectives.

problem = Problem(4, 1)
problem.function = find_parameters
problem.types[:] = [MyInteger(0, 3000),  # low_freq_cutoff
                    MyInteger(1, 15), # min_short_freq
                    Real(0.2, 0.7),      # normal_exponent
                    Real(0.2, 1.0)]      # dict_word_exponent
                    #Binary(1)]           # permissive

@plac.annotations(
    input    = ('Loyola data file file in TSV format', 'option', 'i'),
    threads  = ('number of threads to use',            'option', 't'),
    runs     = ('number of runs to do',                'option', 'r'),
    splitter = ('splitter to run: "ronin", "samurai"', 'option', 's'),
)

def main(input=None, threads=6, runs=20000, splitter='ronin'):
    global cases

    if not input:
        raise SystemExit('Need to provide path to Loyola results file')
    with open(input, 'r') as inputfile:
        for line in inputfile:
            (id, expected) = line.rstrip().split('\t')
            cases[id] = expected.split(',')

    print('Running NSGAII', flush=True)
    start = time()
    threads = int(threads)
    runs = int(runs)
    with ProcessPoolEvaluator(threads) as evaluator:
        algorithm = NSGAII(problem, evaluator=evaluator)
        algorithm.run(runs)
    print('Done after {}s'.format(time() - start), flush=True)

    with open('optimize-results.txt', "w") as f:
        with redirect_stdout(f):
            for solution in algorithm.result:
                o = solution.objectives
                v = solution.variables
                print('score = {},'
                      ' low_freq_cutoff = {}, length_cutoff = {}'
                      ' min_short_freq = {} normal_exponent = {:05f}'
                      ' dict_word_exponent = {:05f} permissive = {}'.
                      format(o[0], v[0], 2, v[1], v[2], v[3], True), flush=True)


if __name__ == '__main__':
    plac.call(main)
