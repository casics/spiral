'''__main__: main entry point for command-line interface

This module implements a command-line interface to Spiral.  It allows users
to invoke Spiral splitters from terminal shell command lines, to explore the
splitters or use them as part of toolchains.

Authors
-------

Michael Hucka <mhucka@caltech.edu>

Copyright
---------

Copyright (c) 2017 by the California Institute of Technology.  This software
was developed as part of the CASICS project, the Comprehensive and Automated
Software Inventory Creation System.  For more, visit http://casics.org.
'''

import os
import plac
import sys

import spiral
from spiral import ronin
from spiral import samurai
from spiral.simple_splitters import pure_camelcase_split, safe_simple_split
from spiral.simple_splitters import simple_split, elementary_split
from spiral.simple_splitters import heuristic_split


# Global constants.
# ......................................................................

_available_splitters = {'ronin': (ronin.init, ronin.split),
                        'samurai': (samurai.init, samurai.split),
                        'pure_camelcase_split': (None, pure_camelcase_split),
                        'safe_simple_split': (None, safe_simple_split),
                        'simple_split': (None, simple_split),
                        'elementary_split': (None, elementary_split),
                        'heuristic_split': (None, heuristic_split)}


# Main program.
# ......................................................................

@plac.annotations(
    file        = ('read input from a file',                     'option', 'f'),
    list        = ('list available splitters',                   'flag',   'l'),
    splitter    = ('run named splitter, e.g. "ronin"',           'option', 's'),
    version     = ('print version info and exit',                'flag',   'V'),
    strings     = 'text string(s) to split',
)

def main(list=False, file=None, version=False, splitter='ronin', *strings):
    '''Spiral is "SPlitters for IdentifieRs: A Library".  It implements many
identifier splitting algorithms.  This command-line program provides a very
simple interface to run Spiral's splitters, for testing and exploration.

IMPORTANT: this is NOT meant to be the normal interface to using Spiral.
Spiral is a package meant to be used by other Python programs.  When you run
this command-line program, it needs to load a large data file internally
and this will cause a noticeable start-up delay.  In normal usage, inside an
application program, Spiral would only load the data files once at first
invocation and subsequent calls to Spiral splitters would not be so slow.
However, since this command-line program cannot save the internal data across
invocations, the startup cost occurs every time.  Please rest assured that
this startup delay is only a one-time cost and not typical for normal Spiral
usage.

The input to this program can be one or more strings on the command line,
or (using the -f argument) a file of strings.  If given a file of
strings, it will analyze each line in the file separately.

The splitter to be used can be specified using the -s option.  Use the -l
option to print a list of the splitters available.

The optional argument -v will make this program display version information
and exit without doing anything more.
'''
    # Process arguments
    if version:
        print('{} version {}'.format(spiral.__title__, spiral.__version__))
        print('Author: {}'.format(spiral.__author__))
        print('URL: {}'.format(spiral.__url__))
        print('License: {}'.format(spiral.__license__))
        sys.exit()
    if list:
        print('Available splitters:')
        for name, _ in sorted(_available_splitters.items()):
            print('  ' + name)
        sys.exit()
    if splitter and splitter not in _available_splitters:
        raise SystemExit('Unrecognized splitter: "{}"'.format(splitter))
    if not file and not strings:
        raise SystemExit('Need a file or string as input. Use -h to get help.')
    if strings and strings[0].startswith('-'):
        # If it starts with a dash and we get to this point, it's not an arg
        # recognized by plac and it's probably not a string meant to be split.
        raise SystemExit('Unrecognized argument "{}". (Hint: use -h to get help.)'
                         .format(strings[0]))

    # Let's do this thing.
    if file:
        if os.path.exists(file):
            with open(file) as f:
                split(f.readlines(), _available_splitters[splitter])
        elif os.path.exists(os.path.join(os.getcwd(), file)):
            with open(os.path.join(os.getcwd(), file)) as f:
                split(f.readlines(), _available_splitters[splitter])
        else:
            raise ValueError('Cannot find file "{}"'.format(file))
    else:
        split(strings, _available_splitters[splitter])


def split(string_list, splitter_functions):
    init, split = splitter_functions
    if init:
        init()
    for s in [string.rstrip() for string in string_list]:
        print('{}: {}'.format(s, split(s)))


if __name__ == '__main__':
    plac.call(main)



# For Emacs users
# ......................................................................
# Local Variables:
# mode: python
# python-indent-offset: 4
# End:
