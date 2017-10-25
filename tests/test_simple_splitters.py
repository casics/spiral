#!/usr/bin/env python3

import pytest
import sys
import glob

sys.path.append('../')
sys.path.append('../../common')
sys.path.append('../../extractor')

from simple_splitters import *

class TestClass:
    def test_camel_split(self, capsys):
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

    def test_simple_split(self, capsys):
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
