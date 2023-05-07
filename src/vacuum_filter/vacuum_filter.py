"""
Vacuum Filter from https://www.vldb.org/pvldb/vol13/p197-wang.pdf
"""
import os
import random
import math
from ../cuckoo_filter import bucket
import utils
from filter import Filter

class VacuumFilter(Filter):
    """
    Implements insert, delete, and contains operations for the vacuum filter.
    """

    def __init__(self, max_elements, bucket_size=4, error_rate=0.01, max_displacements=500):
        """
        Initialize the VacuumFilter object.
        """
        self.max_elements = max_elements  # n
        self.bucket_size = bucket_size
        self.num_buckets = math.ceil(self.max_elements / self.bucket_size)  # m
        self.buckets = [bucket.Bucket(size=bucket_size)
                        for _ in range(self.num_buckets)]
        self.alternate_ranges = self._select_ranges()  # L
        self.size = 0  # k

        self.error_rate = error_rate
        self.fingerprint_size = math.ceil(math.log2(self.bucket_size) +
                                          math.log2(1 / self.error_rate) + 1)
        self.fingerprint = lambda item: utils.fingerprint(item, self.fingerprint_size)  # H'
        self.max_displacements = max_displacements

    def __contains__(self, item):
        return self.contains(item)

    def __len__(self):
        return self.size

    def __repr__(self):
        return f"<VaccumFilter: n={self.max_elements}, size={self.size}>"

    def _select_ranges(self, num_groups=4):
        """
        Initialize the multi-range alternate function.

        Items are divided into four groups of roughly equal size, and each
        group uses its own alternate range (the length of a chunk). AR sizes
        are chosen to balance load factors and locality.
        """
        alt_ranges = [0] * num_groups
        for i in range(num_groups):
            L = 1
            while not self._load_factor_test(0.95, 1 - i / num_groups, L):
                L = L * 2
            alt_ranges[i] = L
        alt_ranges[num_groups - 1] *= 2
        return alt_ranges

    def _load_factor_test(self, target_load_factor, inserted_items_ratio, alternate_range):
        # n = number of items
        num_items = self.max_elements
        # c = number of chunks = ceil(n / (4 alpha L))
        num_chunks = math.ceil(num_items / (4 * target_load_factor * alternate_range))
        # m = number of buckets = cL
        num_buckets = num_chunks * alternate_range
        # N = number of inserted items = L * (4nr)
        num_inserted_items = target_load_factor * 4 * num_buckets * inserted_items_ratio
        # N/c
        inserted_per_chunk = num_inserted_items / num_chunks

        estimated_max_load = inserted_per_chunk + 1.5 * math.sqrt(2 * items_per_chunk + 0.693147181 * math.log2(num_chunks))  # ln 2 * log_2
        chunk_capacity_lower_bound = 3.88 * target_load_factor  # 4 * 0.97
        return estimated_max_load < chunk_capacity_lower_bound

    def add(self, item):
        """
        Add an item into the filter.

        :param item: Item to be inserted.
        :return: True if insert is successful; VacuumFilterFullException if
        filter is full.
        """
        fingerprint = self.fingerprint(item)
        f = fingerprint
        i = self._get_index(item)
        j = self._get_alternate_index(i, fingerprint)

        if self.buckets[i].insert(f) or self.buckets[j].insert(f):
            self.size += 1
            return True

        eviction_index = random.choice([i, j])
        for _ in range(self.max_displacements):
            for f_prime in self.buckets[eviction_index]:
                j_prime = self._get_alternate_index(eviction_index, f_prime)
                if not self.buckets[j_prime].is_full():
                    f = self.buckets[j_prime].swap(f)
                    if self.buckets[j_prime].insert(f):
                        self.size += 1
                        return True
            f = self.buckets[eviction_index].swap(f)
            eviction_index = self._get_alternate_index(eviction_index, f)

        raise Exception('Insert operation failed. Filter is full.')

    def _get_index(self, item):
        index = utils.hash_code(item, self.num_buckets)
        return index

    def _get_alternate_index(self, index, fingerprint):
        alt_index = index
        finger_hash = utils.fingerprint(fingerprint)
        if self.size < 262144:  # 2 ** 18
            m = self.num_buckets
            delta = finger_hash % m
            alt_index = (index - delta) % m
            # to prevent overflow
            alt_index = (m - 1 - alt_index + delta) % m
        else:
            curr_range = self.alternate_ranges[fingerprint % 4]
            alt_index = index ^ (finger_hash % curr_range)
        return alt_index

    def contains(self, item):
        """
        Check if the filter contains the item.

        :param item: Item to check its presence in the filter.
        :return: True, if item is in the filter; False, otherwise.
        """
        fingerprint = self.fingerprint(item)
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
        fingerprint = self.fingerprint(item)
        i = self._get_index(item)
        j = self._get_alternate_index(i, fingerprint)

        if not self.contains(item):
            return False
        if self.buckets[i].delete(fingerprint) or self.buckets[j].delete(fingerprint):
            self.size -= 1
            return True
        return False
