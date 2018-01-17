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
        assert ronin.split('somevar')        == ['some', 'var']
        assert ronin.split('argv')           == ['argv']
        assert ronin.split('usage_getdata')  == ['usage', 'get', 'data']
        assert ronin.split('GPSmodule')      == ['GPS', 'module']
        assert ronin.split('ABCFooBar')      == ['ABC', 'Foo', 'Bar']
        assert ronin.split('getMAX')         == ['get', 'MAX']
        assert ronin.split('SqlList')        == ['Sql', 'List']
        assert ronin.split('ASTVisitor')     == ['AST', 'Visitor']
        assert ronin.split('isnumber')       == ['is', 'number']
        assert ronin.split('isbetterfile')   == ['is', 'better', 'file']
        assert ronin.split('threshold')      == ['threshold']
        assert ronin.split('initdb')         == ['init', 'db']
        assert ronin.split('terraindata')    == ['terrain', 'data']
        assert ronin.split('trigname')       == ['trig', 'name']
        assert ronin.split('undirected')     == ['undirected']
        assert ronin.split('usemap')         == ['use', 'map']
        assert ronin.split('versionend')     == ['version', 'end']
        assert ronin.split('updatecpu')      == ['update', 'cpu']
        assert ronin.split('textnode')       == ['text', 'node']
        assert ronin.split('mixmonitor')     == ['mix', 'monitor']
        assert ronin.split('connectpath')    == ['connect', 'path']
        assert ronin.split('httpexceptions') == ['http', 'exceptions']
        assert ronin.split('finditer')       == ['find', 'iter']
        assert ronin.split('readcmd')        == ['read', 'cmd']
        assert ronin.split('needsibm')       == ['needs', 'ibm']
        assert ronin.split('cmdextdir')      == ['cmd', 'ext', 'dir']
        assert ronin.split('isinstance')     == ['is', 'instance']
        assert ronin.split('getint')         == ['get', 'int']
        assert ronin.split('getinteger')     == ['get', 'integer']
        assert ronin.split('hostloader')     == ['host', 'loader']
        assert ronin.split('tagcount')       == ['tag', 'count']
