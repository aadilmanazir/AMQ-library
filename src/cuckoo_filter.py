"""
Cuckoo Filter
"""

import random
import math
import bucket
import hashutils

class CuckooFilter(object):
    """
    Cuckoo Filter class.

    Implements insert, delete and contains operations for the filter.
    """

    def __init__(self, max_elements, error_rate = 0.01, bucket_size=4, max_displacements=500):
        """
        Initialize CuckooFilter object.

        :param max_elements: Size of the Cuckoo Filter
        :param error_rate: Maximum desired error rate
        :param bucket_size: Number of entries in a bucket
        """

        self.max_elements = math.ceil(max_elements)
        # set self.num_buckets to the nearest power of 2 greater than or equal to self.max_elements/bucket_size
        self.num_buckets = 2 ** math.ceil(math.log2(math.ceil(max_elements / bucket_size)))
        self.bucket_size = bucket_size
        # fingerprint_size in bits, pg 8 of https://www.cs.cmu.edu/~dga/papers/cuckoo-conext2014.pdf
        self.fingerprint_size = math.ceil(math.log2(1/error_rate) + math.log2(2 * bucket_size))
        self.max_displacements = max_displacements
        self.buckets = [bucket.Bucket(size=bucket_size)
                        for _ in range(self.num_buckets)]
        self.size = 0
        self.error_rate = error_rate

    def __repr__(self):
        return '<CuckooFilter: max_elements=' + str(self.max_elements) + \
               ', size=' + str(self.size) + ', fingerprint size=' + \
               str(self.fingerprint_size) + ' byte(s)>'

    def __len__(self):
        return self.size

    def __contains__(self, item):
        return self.contains(item)

    def _get_index(self, item):
        index = hashutils.hash_code(item, self.num_buckets)
        return index

    def _get_alternate_index(self, index, fingerprint):
        alt_index = (index ^ hashutils.hash_code(fingerprint, self.num_buckets)) 
        return alt_index

    def add(self, item):
        """
        Add an item into the filter.

        :param item: Item to be inserted.
        :return: True if insert is successful; CuckooFilterFullException if
        filter is full.
        """
        fingerprint = hashutils.fingerprint(item, self.fingerprint_size)
        i = self._get_index(item)
        j = self._get_alternate_index(i, fingerprint)

        if self.buckets[i].insert(fingerprint) or self.buckets[j].insert(fingerprint):
            self.size += 1
            return True

        eviction_index = random.choice([i, j])
        f = fingerprint
        for _ in range(self.max_displacements):
            f = self.buckets[eviction_index].swap(f)
            eviction_index = self._get_alternate_index(eviction_index, f)
            if self.buckets[eviction_index].insert(f):
                self.size += 1
                return True

        # Filter is full
        raise Exception('Insert operation failed. Filter is full.')

    def contains(self, item):
        """
        Check if the filter contains the item.

        :param item: Item to check its presence in the filter.
        :return: True, if item is in the filter; False, otherwise.
        """
        fingerprint = hashutils.fingerprint(item, self.fingerprint_size)
        i = self._get_index(item)
        j = self._get_alternate_index(i, fingerprint)

        return fingerprint in self.buckets[i] or fingerprint in self.buckets[j]

    def delete(self, item):
        """
        Delete an item from the filter.

        To delete an item safely, it must have been previously inserted.
        Otherwise, deleting a non-inserted item might unintentionally remove
        a real, different item that happens to share the same fingerprint.

        :param item: Item to delete from the filter.
        :return: True, if item is found and deleted; False, otherwise.
        """
        fingerprint = hashutils.fingerprint(item, size=self.fingerprint_size)
        i = self._get_index(item)
        j = self._get_alternate_index(i, fingerprint)
        if self.buckets[i].delete(fingerprint) or self.buckets[j].delete(fingerprint):
            self.size -= 1
            return True
        return False