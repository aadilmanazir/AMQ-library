import math

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