#!/usr/bin/env python3
'''Find parameter values for Nostril.

Introduction
------------

This uses a multiobjective optimization approach to tune the parameter values
for Ronin.  It uses the Python package Platypus.  The objective function
minimized by this script is the number of failures to correctly split
identifiers from one or more oracle files.

Usage
-----

This is a simple script that you run by executing it on the command line:

  ./optimize.py ../../tests/data/intt.tsv:lower ../../tests/data/ludiso.tsv

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
from   termcolor import colored
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


# Global variables.
# .............................................................................

# List of dictionaries, each with keys 'file', 'name', 'lowercase', and 'cases'
tests  = []

# List of integers.
lowest = []


# Objective function.
# .............................................................................

def find_parameters(vars):
    global tests
    global lowest

    var_low_freq_cutoff       = vars[0]
    # A length_cutoff of 2 is consistently the best performing in all my
    # tests, and in addition, allowing 1 sometimes leads to *extremely* long
    # times to split some identifiers.  So I've stopped trying to vary this.
    var_length_cutoff         = 2 #vars[1]
    var_min_short_string_freq = vars[2]*10
    var_normal_exponent       = vars[3]
    var_dict_word_exponent    = vars[4]
    var_camel_bias            = vars[5]
    # Platypus seems to have trouble with varying really small decimals, so I
    # use a larger number in the setup and then divide here to make it smaller.
    var_split_bias            = vars[6]/1000

    ronin.init(low_freq_cutoff=var_low_freq_cutoff,
               length_cutoff=var_length_cutoff,
               min_short_string_freq=var_min_short_string_freq,
               normal_exponent=var_normal_exponent,
               dict_word_exponent=var_dict_word_exponent,
               camel_bias=var_camel_bias,
               split_bias=var_split_bias)

    results = []
    failures_text = ''
    for index, test_set in enumerate(tests):
        name = test_set['name']
        failures = 0
        lowercase_comparison = test_set['lowercase']
        for id, expected in test_set['cases'].items():
            result = ronin.split(id)
            if lowercase_comparison and result:
                result = [x.lower() for x in result]
            if result != expected:
                failures += 1
        results.append(failures)

        if index != 0:
            failures_text += ' '
        if failures <= lowest[index]:
            lowest[index] = failures
            failures_text += '{}: {}'.format(name, colorcode(failures, ['cyan', 'bold']))
        else:
            failures_text += '{}: {}'.format(name, failures)

    msg('{} f_cut = {} len_cut = {} min_sh_f = {} n_exp = {:.4f}'
        ' d_exp = {:.4f} camel_bias = {:.4f} split_bias = {:.8f}'
        .format(failures_text, var_low_freq_cutoff, var_length_cutoff,
                var_min_short_string_freq, var_normal_exponent,
                var_dict_word_exponent, var_camel_bias, var_split_bias))

    return results


# Code to run the optimization.
# .............................................................................

@plac.annotations(
    optimizer = ('Platypus algorithm to use',               'option', 'a'),
    runs      = ('number of runs to do',                    'option', 'r'),
    threads   = ('number of threads to use',                'option', 't'),
    seed      = ('set the random seed explicitly',          'option', 'S'),
    inputs    = 'files of test cases',
)

def main(optimizer='IBEA', threads=6, runs=15000, seed=None, *inputs):
    '''Files of test cases should be files in TSV format.  The file name can
end in the suffix ':lower' to indicate that the strings produced by splitting
should be lower-cased before the results are compared to the expected values.

Known names of optimization algorithms for use with the -a argument:
  CMAES
  EpsMOA
  GDE3
  IBEA
  MOEAD
  NSGAII
  NSGAIII
  OMOPSO
  SMPSO
  SPEA2

NSGAIII is supposed to be one of the best, but I've gotten better parameter
values from IBEA.  See the following page for the list of Platypus optimizers:
http://platypus.readthedocs.io/en/latest/experimenter.html
'''
    global tests
    global lowest

    if not inputs:
        raise SystemExit('Need to provide paths to files of test cases')
    algorithm = getattr(sys.modules['platypus'], optimizer)
    if not algorithm:
        raise SystemExit('Unrecognized Platypus algorithm: {}'.format(algorithm))
    msg('Using {}'.format(optimizer))

    # Read each test file in turn and create an entry in the 'tests' list.
    for file in inputs:
        test_set = {}
        test_set['lowercase'] = file.endswith(':lower')
        file = file.rstrip(':lower')
        test_set['file'] = file
        name = os.path.basename(file)
        name = name[:name.rfind('.tsv')]
        test_set['name'] = name
        test_set['cases'] = {}
        with open(file, 'r') as inputfile:
            for line in inputfile:
                (id, expected) = line.rstrip().split('\t')
                test_set['cases'][id] = expected.split(',')
        tests.append(test_set)
    msg('Read {} sets of test cases'.format(len(tests)))

    # Create array of running lowest scores.
    for test_set in tests:
        lowest.append(10000000)         # Just needs to be some high number.

    # Define our problem: N variables and M objectives.
    args =  [Integer(0, 500),      # low_freq_cutoff
             Integer(0, 3),        # length cutoff (but see above)
             Integer(5000, 50000), # min_short_freq/10
             Real(0.05, 0.8),      # normal_exponent
             Real(0.05, 0.8),      # dict_word_exponent
             Real(0, 10),          # camel_bias
             Real(0, 0.01)]        # split_bias*1000

    problem = Problem(len(args), len(tests))
    problem.function = find_parameters
    problem.types[:] = args

    # Let's get it done.
    start = time()
    threads = int(threads)
    runs = int(runs)
    if seed:
        random.seed(seed)
    # Need custom variator to mix integers with reals in Platypus.
    variator = CompoundOperator(SBX(), HUX(), PM(), BitFlip())
    with ProcessPoolEvaluator(threads) as evaluator:
        # Some additional args are necessary for some Platypus algorithms.
        # This is a grungy way to do it, but oh well.
        if optimizer == 'NSGAIII':
            runner = algorithm(problem, evaluator=evaluator, variator=variator,
                               divisions_outer=25)
        elif optimizer == 'EpsMOEA':
            runner = algorithm(problem, evaluator=evaluator, variator=variator,
                               epsilons=0.05)
        elif optimizer == 'OMOPSO':
            runner = algorithm(problem, evaluator=evaluator, epsilons=0.05)
        else:
            runner = algorithm(problem, evaluator=evaluator, variator=variator)
        runner.run(runs)
    msg('Done after {}s'.format(time() - start))

    arg0_decoder = problem.types[0].decode
    arg1_decoder = problem.types[1].decode
    arg2_decoder = problem.types[2].decode

    with open('optimization-results-' + optimizer + '.txt', "w") as f:
        with redirect_stdout(f):
            for solution in runner.result:
                o = solution.objectives
                v = solution.variables
                msg('scores = {} low_freq_cutoff = {}, length_cutoff = {}'
                    ' min_short_freq = {} norm_exp = {:.5f}'
                    ' dict_exp = {:.5f} camel_bias = {:.5f} split_bias = {:.9f}'
                    # Note: MAKE SURE TO MATCH MULTIPLIERS USED IN find_parameters()
                    .format(o, arg0_decoder(v[0]), arg1_decoder(v[1]),
                            arg2_decoder(v[2])*10, v[3], v[4], v[5], v[6]/1000))


# Utility functions.
# .............................................................................

def update_progress(progress):
    '''Value of "progress" should be a float from 0 to 1.'''
    six.print_('\r[{0:10}] {1:.0f}%'.format('#' * int(progress * 10),
                                            progress*100), end='', flush=True)

def msg(text, flags=None, colorize=True):
    '''Like the standard print(), but flushes the output immediately and
    colorizes the output by default. Flushing immediately is useful when
    piping the output of a script, because Python by default will buffer the
    output in that situation and this makes it very difficult to see what is
    happening in real time.
    '''
    if colorize:
        sys.stdout.write(colorcode(text, flags))
        sys.stdout.write('\n')
        # print(colorcode(text, flags), flush=True)
    else:
        sys.stdout.write(text)
        sys.stdout.write('\n')
        # print(text, flush=True)


def colorcode(text, flags=None, colorize=True):
    (prefix, color, attributes) = color_codes(flags)
    if colorize:
        if attributes and color:
            return colored(text, color, attrs=attributes)
        elif color:
            return colored(text, color)
        elif attributes:
            return colored(text, attrs=attributes)
        else:
            return text
    elif prefix:
        return prefix + ': ' + text
    else:
        return text


def color_codes(flags):
    color  = ''
    prefix = ''
    attrib = []
    if type(flags) is not list:
        flags = [flags]
    if 'error' in flags:
        prefix = 'ERROR'
        color = 'red'
    if 'warning' in flags:
        prefix = 'WARNING'
        color = 'yellow'
    if 'yellow' in flags:
        color = 'yellow'
    if 'info' in flags:
        color = 'green'
    if 'white' in flags:
        color = 'white'
    if 'blue' in flags:
        color = 'blue'
    if 'grey' in flags:
        color = 'grey'
    if 'cyan' in flags:
        color = 'cyan'
    if 'underline' in flags:
        attrib.append('underline')
    if 'bold' in flags:
        attrib.append('bold')
    if 'reverse' in flags:
        attrib.append('reverse')
    if 'dark' in flags:
        attrib.append('dark')
    return (prefix, color, attrib)


# Entry point.
# .............................................................................

if __name__ == '__main__':
    plac.call(main)
