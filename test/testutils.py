import dbm
import math
import os
import random
import sys
import time
import unittest
import math
import random
from pympler import asizeof
from xor_filter import XorFilter

CHARACTERS = 'abcdefghijklmnopqrstuvwxyz1234567890'

class States(object):
    """Generate the USA's state names"""

    def __init__(self):
        pass

    states = """Alabama Alaska Arizona Arkansas California Colorado Connecticut
        Delaware Florida Georgia Hawaii Idaho Illinois Indiana Iowa Kansas
        Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota
        Mississippi Missouri Montana Nebraska Nevada NewHampshire NewJersey
        NewMexico NewYork NorthCarolina NorthDakota Ohio Oklahoma Oregon
        Pennsylvania RhodeIsland SouthCarolina SouthDakota Tennessee Texas Utah
        Vermont Virginia Washington WestVirginia Wisconsin Wyoming""".split()

    @staticmethod
    def generator():
        """Generate the states"""
        for state in States.states:
            yield state

    @staticmethod
    def within(value):
        """Is the value in our list of states?"""
        return value in States.states

    @staticmethod
    def length():
        """What is the length of our contained values?"""
        return len(States.states)

    def __len__(self):
        return len(States.states)

    def __iter__(self):
        return States.generator()


def random_string():
    """Generate a random, 10 character string - for testing purposes"""
    list_ = []
    for _ in range(10):
        character = CHARACTERS[int(random.random() * len(CHARACTERS))]
        list_.append(character)
    return ''.join(list_)


class Random_content(object):
    """Generated a bunch of random strings in sorted order"""

    random_content = [random_string() for dummy in range(1000)]

    def __init__(self):
        pass

    @staticmethod
    def generator():
        """Generate all values"""
        for item in Random_content.random_content:
            yield item

    @staticmethod
    def within(value):
        """Test for membership"""
        return value in Random_content.random_content

    @staticmethod
    def length():
        """How many members?"""
        return len(Random_content.random_content)

    def __len__(self):
        return len(Random_content.random_content)

    def __iter__(self):
        return Random_content.generator()


class Evens(object):
    """Generate a bunch of even numbers"""

    def __init__(self, maximum):
        self.maximum = maximum

    def generator(self):
        """Generate all values"""
        for value in range(self.maximum):
            if value % 2 == 0:
                yield str(value)

    def within(self, value):
        """Test for membership"""
        try:
            int_value = int(value)
        except ValueError:
            return False

        if int_value >= 0 and int_value < self.maximum and int_value % 2 == 0:
            return True
        else:
            return False

    def length(self):
        """How many members?"""
        return int(math.ceil(self.maximum / 2.0))

    def __len__(self):
        return self.length()

    def __iter__(self):
        return self.generator()


def test_filter(
    description,
    values,
    trials,
    error_rate,
    filter_class,
    max_elements_multiple=2,
    performance_test=False
):
    """
    Some quick automatic tests for a general filter class
    """
    sys.stdout.write(description + '\n')

    divisor = 100000

    filter_instance = None
    if filter_class != XorFilter:
        filter_instance = filter_class(
            max_elements=values.length() * max_elements_multiple,
            error_rate=error_rate
        )

        print('starting to add values to an empty filter')
        for valueno, value in enumerate(values.generator()):
            if valueno % divisor == 0:
                print('adding valueno %d' % valueno)
            filter_instance.add(value)
    else:
        print("Initializing filter with values")
        filter_instance = filter_class(
            max_elements=values.length() * max_elements_multiple,
            error_rate=error_rate,
            keys=values
        )

    print('testing all known members')
    include_in_count = sum(
        include in filter_instance
        for include in values.generator()
    )
    assert include_in_count == values.length(), "Not all values were included in the filter"

    if performance_test:
        total_size_in_bytes = asizeof.asizeof(filter_instance)
        return total_size_in_bytes

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
            if candidate in filter_instance:
                # print('false positive: %s' % candidate)
                false_positives += 1
            break

    actual_error_rate = float(false_positives) / trials

    assert actual_error_rate < error_rate, f"Too many false positives: actual: {actual_error_rate}, expected: {error_rate}"

def test_filter_states(filter_class):
    test_filter('states', States(), trials=100000, error_rate=0.01, filter_class=filter_class)

def test_filter_random(filter_class):
    test_filter('random', Random_content(), trials=10000, error_rate=0.1, filter_class=filter_class)
    test_filter('random', Random_content(), trials=100000, error_rate=1E-4, filter_class=filter_class)
    test_filter('random', Random_content(), trials=10000, error_rate=0.1, filter_class=filter_class)

    test_filter(
        'random',
        Random_content(),
        trials=10000,
        error_rate=0.1,
        filter_class=filter_class
    )

def test_filter_performance(filter_class, filter_name):
        """Performance tests for a general class"""
        path = f'performance/{filter_name}/'

        # Create path if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)

        runtime_db_name = path + 'runtime'
        space_db_name = path + 'space'

        for exponent in range(7):  # testing up to 1 million total elements
            for error_rate in [0.05, 0.02, 0.01, 0.005]:
                for max_elements_multiple in [1.1, 1.2, 1.3, 1.5, 2]:
                    max_num = int(2 * 10 ** exponent) # testing even numbers up to max_num
                    elements = max_num // 2
                    if filter_name == "vacuum-filter" and error_rate != 0.05:
                        continue
                    # if filter_name == "xor-filter" and exponent == 10 ** 6:
                    #     continue

                    description = f"{filter_name} with {elements} elements, error rate {error_rate}, max_elements {max_elements_multiple * elements}"
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
                        filter_class=filter_class,
                        max_elements_multiple=max_elements_multiple,
                        performance_test=True
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
