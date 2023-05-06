#!/usr/bin/python
# coding=utf-8

# pylint: disable=superfluous-parens
# superfluous-parens: Parentheses are good for clarity and portability

"""Unit tests for bloom_filter"""

import dbm
import math
import os
import random
import sys
import time
import unittest
import bloom_filter  
from testutils import *

class TestBloomFilter(unittest.TestCase):
    def _test(
        self,
        description, 
        values, 
        trials, 
        error_rate,
        max_elements_multiple=2,
        test_false_positives=True
    ):
        # pylint: disable=R0913,R0914
        # R0913: We want a few arguments
        # R0914: We want some local variables too.  This is just test code.
        """Some quick automatic tests for the bloom filter class"""

        divisor = 100000

        bloom = bloom_filter.BloomFilter(
            max_elements=values.length() * max_elements_multiple,
            error_rate=error_rate,
        )

        message = '\ndescription: %s num_bits_m: %s num_probes_k: %s\n'
        filled_out_message = message % (
            description,
            bloom.num_bits_m,
            bloom.num_probes_k,
        )

        sys.stdout.write(filled_out_message)

        print('starting to add values to an empty bloom filter')
        for valueno, value in enumerate(values.generator()):
            if valueno % divisor == 0:
                print('adding valueno %d' % valueno)
            bloom.add(value)

        print('testing all known members')
        include_in_count = sum(
            include in bloom
            for include in values.generator()
        )
        self.assertEqual(include_in_count, values.length())

        if not test_false_positives:
            return

        print('testing random non-members')
        false_positives = 0
        for trialno in range(trials):
            if trialno % divisor == 0:
                print(
                    'trialno progress: %d / %d' % (trialno, trials),
                    file=sys.stderr,
                )
            while True:
                candidate = ''.join(random.sample(CHARACTERS, 5))
                # If we accidentally found a member, try again
                if values.within(candidate):
                    continue
                if candidate in bloom:
                    # print('false positive: %s' % candidate)
                    false_positives += 1
                break

        actual_error_rate = float(false_positives) / trials

        self.assertLess(
            actual_error_rate, error_rate,
            "Too many false positives: actual: %s, expected: %s" % (
                actual_error_rate,
                error_rate,
            ),
        )

    def test_and(self):
        """Test the & operator"""

        abc = bloom_filter.BloomFilter(max_elements=100, error_rate=0.01)
        for character in ['a', 'b', 'c']:
            abc += character

        bcd = bloom_filter.BloomFilter(max_elements=100, error_rate=0.01)
        for character in ['b', 'c', 'd']:
            bcd += character

        abc &= bcd

        self.assertNotIn('a', abc)
        self.assertIn('b', abc)
        self.assertIn('c', abc)
        self.assertNotIn('d', abc)

    def test_or(self):
        """Test the | operator"""

        abc = bloom_filter.BloomFilter(max_elements=100, error_rate=0.01)
        for character in ['a', 'b', 'c']:
            abc += character

        bcd = bloom_filter.BloomFilter(max_elements=100, error_rate=0.01)
        for character in ['b', 'c', 'd']:
            bcd += character

        abc |= bcd

        self.assertIn('a', abc)
        self.assertIn('b', abc)
        self.assertIn('c', abc)
        self.assertIn('d', abc)
        self.assertNotIn('e', abc)

    def test_states(self):
        self._test('states', States(), trials=100000, error_rate=0.01)

    def test_random(self):
        self._test('random', Random_content(), trials=10000, error_rate=0.1)
        self._test('random', Random_content(), trials=100000, error_rate=1E-4)
        self._test('random', Random_content(), trials=10000, error_rate=0.1)

        filename = 'bloom-filter-rm-me'
        self._test(
            'random',
            Random_content(),
            trials=10000,
            error_rate=0.1,

        )

    @unittest.skipUnless(os.environ.get('TEST_RUNTIME_PERF', ''), "disabled")
    def test_runtime_performance(self):
        """Performance tests for BloomFilter class"""
        db_name = '../performance/bloom-filter'
        for exponent in range(7):  # testing up to 1 million total elements
            for error_rate in [0.05, 0.02, 0.01, 0.005]:
                for max_elements_multiple in [1.1, 1.2, 1.5, 2]:
                    max_num = int(2 * 10 ** exponent) # testing even numbers up to max_num
                    elements = max_num//2

                    description = f"Bloom Filter with {elements} elements, error rate {error_rate}, max_elements {max_elements_multiple * elements}"
                    key = description
                    with dbm.open(db_name, 'c') as database:
                        if key.encode() in database.keys():
                            continue

                    time0 = time.time()
                    self._test(
                        f"Performance: {description}",
                        Evens(max_num),
                        trials=elements,
                        error_rate=error_rate,
                        max_elements_multiple=max_elements_multiple,
                        test_false_positives=False
                    )
                    time1 = time.time()
                    delta_t = time1 - time0
            
                    with dbm.open(db_name, 'c') as database:
                        database[key] = '%f' % delta_t

        
        output_file = "../performance/bloom-filter.txt"
        key_values = []
        with dbm.open(db_name, 'c') as database:
            with open(output_file, 'w') as output:
                for key in database.keys():
                    value = database[key].decode()
                    key_values.append([key.decode(), float(value)])
                key_values.sort(key=lambda x: x[1])
                for key, value in key_values:
                    output.write(f"{key}: {value}\n")

    def test_probe_count(self):
        # test prob count ok
        bloom = bloom_filter.BloomFilter(1000000, error_rate=.99)
        self.assertEqual(bloom.num_probes_k, 1)


if __name__ == '__main__':
    unittest.main()
