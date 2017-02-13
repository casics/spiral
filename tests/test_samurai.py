#!/usr/bin/env python3

import pytest
import sys
import glob

sys.path.append('../')
sys.path.append('../../common')
sys.path.append('../../extractor')

from samurai import *

class TestClass:
    def test_same_case_split(self, capsys):
        pass
