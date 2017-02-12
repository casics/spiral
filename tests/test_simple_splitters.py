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
