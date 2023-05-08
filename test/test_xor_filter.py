#!/usr/bin/python
# coding=utf-8

"""Unit tests for xor_filter"""

from xor_filter import XorFilter
from testutils import *

class TestXorFilter(unittest.TestCase):
    def test_states(self):
        test_filter_states(XorFilter)

    def test_random(self):
        test_filter_random(XorFilter)

    def test_performance(self):
        test_filter_performance(XorFilter, "xor-filter")

if __name__ == '__main__':
    unittest.main()
