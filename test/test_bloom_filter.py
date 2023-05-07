#!/usr/bin/python
# coding=utf-8

# pylint: disable=superfluous-parens
# superfluous-parens: Parentheses are good for clarity and portability

"""Unit tests for bloom_filter"""

from bloom_filter import BloomFilter
from testutils import *

class TestBloomFilter(unittest.TestCase):
    def test_states(self):
        test_filter_states(BloomFilter)

    def test_random(self):
        test_filter_random(BloomFilter)

    def test_and(self):
        """Test the & operator"""

        abc = BloomFilter(max_elements=100, error_rate=0.01)
        for character in ['a', 'b', 'c']:
            abc += character

        bcd = BloomFilter(max_elements=100, error_rate=0.01)
        for character in ['b', 'c', 'd']:
            bcd += character

        abc &= bcd

        self.assertNotIn('a', abc)
        self.assertIn('b', abc)
        self.assertIn('c', abc)
        self.assertNotIn('d', abc)

    def test_or(self):
        """Test the | operator"""

        abc = BloomFilter(max_elements=100, error_rate=0.01)
        for character in ['a', 'b', 'c']:
            abc += character

        bcd = BloomFilter(max_elements=100, error_rate=0.01)
        for character in ['b', 'c', 'd']:
            bcd += character

        abc |= bcd

        self.assertIn('a', abc)
        self.assertIn('b', abc)
        self.assertIn('c', abc)
        self.assertIn('d', abc)
        self.assertNotIn('e', abc)
        
    def test_probe_count(self):
        # test prob count ok
        bloom = BloomFilter(1000000, error_rate=.99)
        self.assertEqual(bloom.num_probes_k, 1)

    @unittest.skipUnless(os.environ.get('TEST_PERF', ''), "disabled")
    def test_performance(self):
        test_filter_performance(BloomFilter, "bloom-filter")

if __name__ == '__main__':
    unittest.main()
