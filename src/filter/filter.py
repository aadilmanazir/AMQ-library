"""
Filter Class Type
"""


class Filter:
    def add(self, item):
        raise NotImplementedError("The 'add' method must be implemented in the subclass")

    def __contains__(self, item):
        raise NotImplementedError("The '__contains__' method must be implemented in the subclass")