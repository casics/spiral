#!/usr/bin/env python3 -O

import os
import pytest
import sys
from   time import time

thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(thisdir, '..'))

from spiral import *

class TestClass:
    def test_samurai(self, capsys):
        assert samurai.split('somevar')                     == ['some', 'var']
        assert samurai.split('argv')                        == ['argv']
        # assert samurai.split('usage_getdata')             == ['usage', 'get', 'data']
        assert samurai.split('GPSmodule')                   == ['GPS', 'module']
        # assert samurai.split('bigTHING')                  == ['big', 'THING']
        assert samurai.split('ABCFooBar')                   == ['ABC', 'Foo', 'Bar']
        assert samurai.split('getMAX')                      == ['get', 'MAX']
        assert samurai.split('SqlList')                     == ['Sql', 'List']
        assert samurai.split('ASTVisitor')                  == ['AST', 'Visitor']
        assert samurai.split('isnumber')                    == ['is', 'number']
        # assert samurai.split('isbetterfile')              == ['is', 'better', 'file']
        assert samurai.split('threshold')                   == ['threshold']
        assert samurai.split('iskeyword')                   == ['is', 'keyword']
        assert samurai.split('initdb')                      == ['init', 'db']
        assert samurai.split('terraindata')                 == ['terrain', 'data']
        assert samurai.split('trigname')                    == ['trig', 'name']
        assert samurai.split('undirected')                  == ['undirected']
        assert samurai.split('usemap')                      == ['use', 'map']
        assert samurai.split('versionend')                  == ['version', 'end']
        assert samurai.split('updatecpu')                   == ['update', 'cpu']
        assert samurai.split('textnode')                    == ['text', 'node']
        assert samurai.split('sandcx')                      == ['sand', 'cx']
        assert samurai.split('mixmonitor')                  == ['mix', 'monitor']
        assert samurai.split('connectpath')                 == ['connect', 'path']
        assert samurai.split('mpegts')                      == ['mpeg', 'ts']
        assert samurai.split('itervalues')                  == ['itervalues']
        assert samurai.split('autocommit')                  == ['autocommit']
        assert samurai.split('httpexceptions')              == ['httpexceptions']
        assert samurai.split('FOOOBAR')                     == ['FOO', 'O', 'BAR']
        assert samurai.split('finditer')                    == ['find', 'iter']
        assert samurai.split('fileio')                      == ['file', 'io']
        #assert samurai.split('imhand')                     == ['imhand']
        #assert samurai.split('treservations')               == ['tres', 'erv', 'at', 'ions']
        assert samurai.split('NSTEMPLATEMATCHREFSET_METER') == ['NS', 'TEMPLATE', 'MATCH', 'REF', 'SET', 'METER']
        # assert samurai.split('vframe')                      == ['vf', 'ra', 'me']
        assert samurai.split('vqgen')                       == ['vqgen']
        assert samurai.split('sampfmt')                     == ['samp', 'fmt']
        assert samurai.split('sampy')                       == ['sam', 'py']
        assert samurai.split('readcmd')                     == ['read', 'cmd']
        #assert samurai.split('uval')                        == ['uval']
