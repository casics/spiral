# -*- python-indent-offset: 4 -*-
'''
logger: custom utilities for logging messages in CASICS.

'''
__version__ = '1.0.0'
__author__  = 'Michael Hucka <mhucka@caltech.edu>'
__email__   = 'mhucka@caltech.edu'
__license__ = 'GPLv3'

import colorlog
import logging
import os
import sys

# It's true that loggers are already handled as singletons by the 'logging'
# package, but I couldn't get figure out how to get initialization to happen
# when using the typical "log = logging.getLogger(...)" calls.

# This implements the Singleton metaclass from Chapter 9 of the book "Python
# Cookbook" 3rd edition by David Beazly & Brian K. Jones (O'Reilly, 2013),
# modified to work in Python 2 following an example in StackOverflow here:
# http://stackoverflow.com/a/6798042/743730

class Singleton(type):
    """Singleton metaclass.  Usage example:

    class Spam(metaclass=Singleton):
        def __init__(self):
            print('foo')
    """

    def __init__(self, *args, **kwargs):
        self.__instance = None
        super(Singleton, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super(Singleton, self).__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


class Logger(metaclass=Singleton):
    _logger  = None
    _logfile = None
    _outlog  = None

    def __init__(self, name=None, file=None, console=False):
        if self._logger:
            return
        if not name:
            name = sys.argv[0] if len(sys.argv) > 1 else 'log'
            if name.rfind('.') > 0:
                name = name[:name.rfind('.')]
        if not file:
            file = name + '.log'
        if os.path.isfile(file):
            os.rename(file, file + '.old')
        self.configure_logging(name, file, console)


    def configure_logging(self, name, file, console):
        # File logger.
        self._logfile  = file
        self._logger   = logging.getLogger(name)
        file_handler   = logging.FileHandler(file)
        file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)
        self._outlog   = file_handler.stream

        # Default logging level.
        self._logger.setLevel(logging.INFO)

        # Special handling for Pyro4: turn off its handler b/c we have ours.
        logging.getLogger('Pyro4').addHandler(logging.NullHandler())

        # Console logger.
        if console:
            stream_handler = colorlog.StreamHandler()
            # Don't send color codes inside Emacs shell buffers.
            if os.environ['TERM'] != 'dumb':
                colorlog.escape_codes['lightgreen'] = '\x1b[2m\x1b[32m'
                stream_handler.setFormatter(colorlog.ColoredFormatter(
                    '%(log_color)s%(asctime)s [%(levelname)s] %(message)s',
                    log_colors={
                        'DEBUG'    : 'lightgreen',
                        'INFO'     : 'green',
                        'WARNING'  : 'yellow',
                        'ERROR'    : 'red',
                        'CRITICAL' : 'red,bg_white',
                    },
                    style='%'
                ))
            else:
                stream_handler.setFormatter(colorlog.ColoredFormatter(
                    '%(asctime)s [%(levelname)s] %(message)s',
                ))
            self._logger.addHandler(stream_handler)


    def get_log(self):
        return self


    def set_level(self, level):
        def record_level():
            self.info('Logging level set to {}'.format(level))

        if level == 'debug':
            self._logger.setLevel(colorlog.colorlog.logging.DEBUG)
            record_level()
        elif level == 'info':
            self._logger.setLevel(colorlog.colorlog.logging.INFO)
            record_level()
        elif level == 'error':
            self._logger.setLevel(colorlog.colorlog.logging.ERROR)
            record_level()
        else:
            self.error('Ignoring unrecognized level: {}'.format(level))


    def debug(self, msg):
        self._logger.debug(msg)


    def info(self, msg):
        self._logger.info(msg)


    def warn(self, msg):
        self._logger.warning(msg)


    def error(self, msg):
        '''Ignorable error.'''
        self._logger.error(msg)


    def fail(self, msg):
        '''Unignorable error.'''
        self._logger.critical(msg)
        self._logger.critical('Exiting.')
        raise SystemExit(msg)


    def log_stream(self):
        return self._outlog
