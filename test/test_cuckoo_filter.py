#!/usr/bin/python
# coding=utf-8

# pylint: disable=superfluous-parens
# superfluous-parens: Parentheses are good for clarity and portability

"""Unit tests for cuckoo_filter"""

from cuckoo_filter import CuckooFilter
from testutils import *

class TestCuckooFilter(unittest.TestCase):
    def test_states(self):
        test_filter_states(CuckooFilter)

    def test_random(self):
        test_filter_random(CuckooFilter)

    def test_fingerprint_size(self):
        # test prob count ok
        cuckoo = CuckooFilter(1000000, error_rate=.99)
        assert cuckoo.fingerprint_size >= 1

    @unittest.skipUnless(os.environ.get('TEST_PERF', ''), "disabled")
    def test_performance(self):
        test_filter_performance(CuckooFilter, "cuckoo-filter")

if __name__ == '__main__':
    unittest.main()
