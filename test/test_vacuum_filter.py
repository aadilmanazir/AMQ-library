#!/usr/bin/python
# coding=utf-8

# pylint: disable=superfluous-parens
# superfluous-parens: Parentheses are good for clarity and portability

"""Unit tests for vacuum_filter"""

from vacuum_filter import VacuumFilter
from testutils import *

class TestVacuumFilter(unittest.TestCase):
    def test_states(self):
        test_filter_states(VacuumFilter)

    def test_random(self):
        test_filter_random(VacuumFilter)

    def test_fingerprint_size(self):
        # test prob count ok
        vacuum = VacuumFilter(1000000, error_rate=.99)
        assert vacuum.fingerprint_size >= 1

    @unittest.skipUnless(os.environ.get('TEST_PERF', ''), "disabled")
    def test_performance(self):
        test_filter_performance(VacuumFilter, "vacuum-filter")

if __name__ == '__main__':
    unittest.main()
