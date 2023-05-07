#!/usr/bin/python
# coding=utf-8

# pylint: disable=superfluous-parens
# superfluous-parens: Parentheses are good for clarity and portability

"""Unit tests for bloom_filter"""

from bloom_filter import BloomFilter
from testutils import *

class TestBloomFilter(unittest.TestCase):
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

    def test_states(self):
        test_filter('states', States(), trials=100000, error_rate=0.01, filter_class=BloomFilter)

    def test_random(self):
        test_filter('random', Random_content(), trials=10000, error_rate=0.1, filter_class=BloomFilter)
        test_filter('random', Random_content(), trials=100000, error_rate=1E-4, filter_class=BloomFilter)
        test_filter('random', Random_content(), trials=10000, error_rate=0.1, filter_class=BloomFilter)

        filename = 'bloom-filter-rm-me'
        test_filter(
            'random',
            Random_content(),
            trials=10000,
            error_rate=0.1,
            filter_class=BloomFilter
        )


    def test_probe_count(self):
        # test prob count ok
        bloom = BloomFilter(1000000, error_rate=.99)
        self.assertEqual(bloom.num_probes_k, 1)

    @unittest.skipUnless(os.environ.get('TEST_PERF', ''), "disabled")
    def test_performance(self):
        """Performance tests for BloomFilter class"""
        path = '../performance/bloom-filter/'

        # Create path if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)

        runtime_db_name = path + 'runtime'
        space_db_name = path + 'space'

        for exponent in range(7):  # testing up to 1 million total elements
            for error_rate in [0.05, 0.02, 0.01, 0.005]:
                for max_elements_multiple in [1.1, 1.2, 1.3, 1.5, 2]:
                    max_num = int(2 * 10 ** exponent) # testing even numbers up to max_num
                    elements = max_num//2

                    description = f"Bloom Filter with {elements} elements, error rate {error_rate}, max_elements {max_elements_multiple * elements}"
                    key = description
                    with dbm.open(runtime_db_name, 'c') as database:
                        if key.encode() in database.keys():
                            continue

                    time0 = time.time()
                    total_size_in_bytes = test_filter(
                        f"Performance: {description}",
                        Evens(max_num),
                        trials=elements,
                        error_rate=error_rate,
                        filter_class=BloomFilter,
                        max_elements_multiple=max_elements_multiple,
                        performancetest_filter=True
                    )
                    time1 = time.time()
                    delta_t = time1 - time0
            
                    with dbm.open(runtime_db_name, 'c') as database:
                        database[key] = '%f' % delta_t

                    with dbm.open(space_db_name, 'c') as database:
                        database[key] = '%d' % total_size_in_bytes

        # Write runtime results to file
        output_file = path + 'runtime.txt'
        key_values = []
        with dbm.open(runtime_db_name, 'c') as database:
            with open(output_file, 'w') as output:
                for key in database.keys():
                    value = database[key].decode()
                    key_values.append([key.decode(), float(value)])
                key_values.sort(key=lambda x: x[1])
                for key, value in key_values:
                    output.write(f"{key}: {value}\n")

        output_file = path + 'space.txt'
        key_values = []
        with dbm.open(space_db_name, 'c') as database:
            with open(output_file, 'w') as output:
                for key in database.keys():
                    value = database[key].decode()
                    key_values.append([key.decode(), int(value)])
                key_values.sort(key=lambda x: x[1])
                for key, value in key_values:
                    output.write(f"{key}: {value}\n")


if __name__ == '__main__':
    unittest.main()
