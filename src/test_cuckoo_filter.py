#!/usr/bin/python
# coding=utf-8

# pylint: disable=superfluous-parens
# superfluous-parens: Parentheses are good for clarity and portability

"""Unit tests for cuckoo_filter"""

import dbm
import math
import os
import random
import sys
import time
import unittest
import cuckoo_filter
from testutils import *

class TestCuckooFilter(unittest.TestCase):
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
        """Some quick automatic tests for the cuckoo filter class"""

        divisor = 100000

        cuckoo = cuckoo_filter.CuckooFilter(
            max_elements=values.length() * max_elements_multiple,
            error_rate=error_rate
        )

        message = f'\ndescription: {description} bucket_size: {cuckoo.bucket_size} fingerprint_size: {cuckoo.fingerprint_size}\n'

        sys.stdout.write(message)

        print('starting to add values to an empty cuckoo filter')
        for valueno, value in enumerate(values.generator()):
            if valueno % divisor == 0:
                print('adding valueno %d' % valueno)
            cuckoo.add(value)

        print('testing all known members')
        include_in_count = sum(
            include in cuckoo
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
                if candidate in cuckoo:
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

    def test_states(self):
        self._test('states', States(), trials=100000, error_rate=0.01)

    def test_random(self):
        self._test('random', Random_content(), trials=10000, error_rate=0.1)
        self._test('random', Random_content(), trials=100000, error_rate=1E-4)
        self._test('random', Random_content(), trials=10000, error_rate=0.1)

        filename = 'bloom-cuckoo-rm-me'
        self._test(
            'random',
            Random_content(),
            trials=10000,
            error_rate=0.1,

        )

    @unittest.skipUnless(os.environ.get('TEST_RUNTIME_PERF', ''), "disabled")
    def test_runtime_performance(self):
        """Performance tests for CuckooFilter class"""
        db_name = '../performance/cuckoo-filter'
        for exponent in range(7):  # testing up to 1 million total elements
            for error_rate in [0.05, 0.02, 0.01, 0.005]:
                for max_elements_multiple in [1.1, 1.2, 1.5, 2]:
                    max_num = int(2 * 10 ** exponent) # testing even numbers up to max_num
                    elements = max_num//2

                    description = f"Cuckoo Filter with {elements} elements, error rate {error_rate}, max_elements {max_elements_multiple * elements}"
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

        
        output_file = "../performance/cuckoo-filter.txt"
        key_values = []
        with dbm.open(db_name, 'c') as database:
            with open(output_file, 'w') as output:
                for key in database.keys():
                    value = database[key].decode()
                    key_values.append([key.decode(), float(value)])
                key_values.sort(key=lambda x: x[1])
                for key, value in key_values:
                    output.write(f"{key}: {value}\n")

    def test_fingerprint_size(self):
        # test prob count ok
        cuckoo = cuckoo_filter.CuckooFilter(1000000, error_rate=.99)
        assert cuckoo.fingerprint_size >= 1

if __name__ == '__main__':
    unittest.main()
