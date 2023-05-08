import random

class Bucket(object):
    def __init__(self, size=4):
        self.size = size
        self.bucket = []

    def __repr__(self):
        return '<Bucket: ' + str(self.bucket) + '>'

    def __contains__(self, item):
        return item in self.bucket

    def __len__(self):
        return len(self.bucket)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self):
            value = self.bucket[self.index]
            self.index += 1
            return value
        else:
            raise StopIteration

    def insert(self, item):
        """
        Insert a fingerprint into the bucket
        :param item:
        :return:
        """
        if not self.is_full():
            self.bucket.append(item)
            return True
        return False

    def delete(self, item):
        """
        Delete a fingerprint from the bucket.
        :param item:
        :return:
        """
        try:
            del self.bucket[self.bucket.index(item)]
            return True
        except ValueError:
            return False

    def is_full(self):
        return len(self) == self.size

    def swap(self, item):
        """
        Swap fingerprint with a random entry stored in the bucket and return
        the swapped fingerprint
        :param item:
        :return:
        """
        index = random.choice(range(len(self)))
        swapped_item = self.bucket[index]
        self.bucket[index] = item
        return swapped_item

    def place(self, item, old_item):
        """
        Put fingerprint into bucket at the location of the old fingerprint.
        :param item:
        :param old_item:
        """
        self.bucket.remove(old_item)
        self.insert(item)
