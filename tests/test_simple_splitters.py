#!/usr/bin/env python3

import os
import pytest
import sys
from   time import time

thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(thisdir, '..'))

from spiral import *

class TestClass:
    def test_safe_camelcase_split(self, capsys):
        assert safe_camelcase_split('lower')          == ['lower']
        assert safe_camelcase_split('fooBar')         == ['foo', 'Bar']
        assert safe_camelcase_split('FooBar')         == ['Foo', 'Bar']
        assert safe_camelcase_split('Foobar')         == ['Foobar']
        assert safe_camelcase_split('ABCFooBar')      == ['ABCFooBar']
        assert safe_camelcase_split('FOOOBAR')        == ['FOOOBAR']
        assert safe_camelcase_split('getMAX')         == ['getMAX']
        assert safe_camelcase_split('ASTVisitor')     == ['ASTVisitor']
        assert safe_camelcase_split('SqlList')        == ['Sql', 'List']
        assert safe_camelcase_split('jLabel')         == ['j', 'Label']


    def test_safe_simple_split(self, capsys):
        assert safe_simple_split('fooBar2day')     == ['foo', 'Bar', 'day']
        assert safe_simple_split('foo_bar')        == ['foo', 'bar']
        assert safe_simple_split('foo_bar2day')    == ['foo', 'bar', 'day']
        assert safe_simple_split('foo_2day')       == ['foo', 'day']
        assert safe_simple_split('foo_bar2')       == ['foo', 'bar']
        assert safe_simple_split('foo.bar2FooBar') == ['foo', 'bar', 'Foo', 'Bar']
        assert safe_simple_split('lower')          == ['lower']
        assert safe_simple_split('fooBar')         == ['foo', 'Bar']
        assert safe_simple_split('FooBar')         == ['Foo', 'Bar']
        assert safe_simple_split('Foobar')         == ['Foobar']
        assert safe_simple_split('ABCFooBar')      == ['ABCFooBar']
        assert safe_simple_split('FOOOBAR')        == ['FOOOBAR']
        assert safe_simple_split('getMAX')         == ['getMAX']
        assert safe_simple_split('ASTVisitor')     == ['ASTVisitor']
        assert safe_simple_split('SqlList')        == ['Sql', 'List']
        assert safe_simple_split('jLabel')         == ['j', 'Label']
        assert safe_simple_split('aFastNDecoder')  == ['aFastNDecoder']


    def test_simple_split(self, capsys):
        assert simple_split('fooBar2day')    == ['foo', 'Bar', 'day']
        assert simple_split('SQLlite')       == ['SQLlite']
        assert simple_split('aFastNDecoder') == ['a', 'Fast', 'NDecoder']
        assert simple_split('getMAX')        == ['get', 'MAX']
