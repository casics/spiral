#!/usr/bin/env python3 -O

import os
import pytest
import sys
from   time import time

thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(thisdir, '..'))

from spiral import *

class TestClass:
    def test_ronin(self, capsys):
        assert ronin_split('somevar')       == ['some', 'var']
        assert ronin_split('argv')          == ['argv']
        assert ronin_split('usage_getdata') == ['usage', 'get', 'data']
        assert ronin_split('GPSmodule')     == ['GPS', 'module']
        assert ronin_split('bigTHING')      == ['big', 'THING']
        assert ronin_split('ABCFooBar')     == ['ABC', 'Foo', 'Bar']
        assert ronin_split('getMAX')        == ['get', 'MAX']
        assert ronin_split('SqlList')       == ['Sql', 'List']
        assert ronin_split('ASTVisitor')    == ['AST', 'Visitor']
        assert ronin_split('isnumber')      == ['is', 'number']
        assert ronin_split('isbetterfile')  == ['is', 'better', 'file']
        assert ronin_split('threshold')     == ['threshold']
        assert ronin_split('iskeyword')     == ['is', 'keyword']
        assert ronin_split('initdb')        == ['init', 'db']
        assert ronin_split('terraindata')   == ['terrain', 'data']
        assert ronin_split('trigname')      == ['trig', 'name']
        assert ronin_split('undirected')    == ['undirected']
        assert ronin_split('usemap')        == ['use', 'map']
        assert ronin_split('versionend')    == ['version', 'end']
        assert ronin_split('updatecpu')     == ['update', 'cpu']
        assert ronin_split('textnode')      == ['text', 'node']
        assert ronin_split('sandcx')        == ['sand', 'cx']
        assert ronin_split('mixmonitor')    == ['mix', 'monitor']
        assert ronin_split('connectpath')   == ['connect', 'path']


        # assert ronin_split('mpegts')        == ['mpegts']
        # assert ronin_split('itervalues') == ['itervalues']
        # assert ronin_split('autocommit') == ['autocommit']
        # assert ronin_split('httpexceptions') == ['httpexceptions']
        # assert ronin_split('FOOOBAR') == ['FO', 'OO', 'BAR']
        # assert ronin_split('finditer') == ['finditer']
        # assert ronin_split('fileio') == ['fileio']
        # assert ronin_split('imhand')        == ['imhand']
        # assert ronin_split('treservations') == ['tres', 'erv', 'at', 'ions']
        # assert ronin_split('NSTEMPLATEMATCHREFSET_METER') == ['NST', 'EMP', 'LATE', 'MATCH', 'REF', 'SET', 'METER']
        # assert ronin_split('vframe') == ['vf', 'ra', 'me']
        # assert ronin_split('vqgen') == ['vqgen']
        # assert ronin_split('sampfmt') == ['samp', 'fmt']
        # assert ronin_split('sampy') == ['sam', 'py']
        # assert ronin_split('readcmd') == ['read', 'cmd']
        # assert ronin_split('uval') == ['uval']
