"""Bloom Filter: Probabilistic set membership testing for large sets"""

import array
import math
import os
import random
import mmh3
from filter import Filter

class Array_backend(object):
    """
    Backend storage for our "array of bits" using a python array of integers
    """
    effs = 2 ** 32 - 1

    def __init__(self, num_bits):
        self.num_bits = num_bits
        self.num_words = (self.num_bits + 31) // 32
        self.array_ = array.array('L', [0]) * self.num_words

    def is_set(self, bitno):
        """Return true iff bit number bitno is set"""
        wordno, bit_within_wordno = divmod(bitno, 32)
        mask = 1 << bit_within_wordno
        return self.array_[wordno] & mask

    def set(self, bitno):
        """set bit number bitno to true"""
        wordno, bit_within_wordno = divmod(bitno, 32)
        mask = 1 << bit_within_wordno
        self.array_[wordno] |= mask

    def clear(self, bitno):
        """clear bit number bitno - set it to false"""
        wordno, bit_within_wordno = divmod(bitno, 32)
        mask = Array_backend.effs - (1 << bit_within_wordno)
        self.array_[wordno] &= mask

    # It'd be nice to do __iand__ and __ior__ in a base class, but
    # that'd be Much slower

    def __iand__(self, other):
        assert self.num_bits == other.num_bits

        for wordno in range(self.num_words):
            self.array_[wordno] &= other.array_[wordno]

        return self

    def __ior__(self, other):
        assert self.num_bits == other.num_bits

        for wordno in range(self.num_words):
            self.array_[wordno] |= other.array_[wordno]

        return self

def get_filter_bitno_probes(bloom_filter, key):
    """
    Apply num_probes_k hash functions to key.

    Generate the array index and bitmask corresponding to each result
    """

    # Convert the key to bytes if it's a string, integer, or float
    if isinstance(key, (str, int, float)):
        key = str(key).encode()

    # Check if the key is a bytes-like object
    if not isinstance(key, (bytes, bytearray)):
        raise TypeError('Sorry, I do not know how to hash this type')

    seed1 = 42
    seed2 = 97

    hash_value1 = mmh3.hash_bytes(key, seed=seed1)
    hash_value2 = mmh3.hash_bytes(key, seed=seed2)
    hash_int1 = int.from_bytes(hash_value1, byteorder='big', signed=True)
    hash_int2 = int.from_bytes(hash_value2, byteorder='big', signed=True)

    # Generate k hash functions by combining the two hash values
    for probeno in range(1, bloom_filter.num_probes_k + 1):
        combined_hash = hash_int1 + probeno * hash_int2
        bit_index = combined_hash % bloom_filter.num_bits_m
        yield bit_index

class BloomFilter(Filter):
    """Probabilistic set membership testing for large sets"""
    def __init__(self,
                 max_elements=10000,
                 error_rate=0.1,
                 probe_bitnoer=get_filter_bitno_probes):
        # pylint: disable=R0913
        # R0913: We want a few arguments
        if max_elements <= 0:
            raise ValueError('ideal_num_elements_n must be > 0')
        if not (0 < error_rate < 1):
            raise ValueError('error_rate_p must be between 0 and 1 exclusive')

        self.error_rate_p = error_rate
        # With fewer elements, we should do very well. With more elements, our
        # error rate "guarantee" drops rapidly.
        self.ideal_num_elements_n = int(max_elements)

        numerator = (
            -1
            * self.ideal_num_elements_n
            * math.log(self.error_rate_p)
        )
        denominator = math.log(2) ** 2
        real_num_bits_m = numerator / denominator
        self.num_bits_m = int(math.ceil(real_num_bits_m))

        self.backend = Array_backend(self.num_bits_m)

        # AKA num_offsetters
        # Verified against
        # https://en.wikipedia.org/wiki/Bloom_filter#Probability_of_false_positives
        real_num_probes_k = (
            (self.num_bits_m / self.ideal_num_elements_n)
            * math.log(2)
        )
        self.num_probes_k = int(math.ceil(real_num_probes_k))
        self.probe_bitnoer = probe_bitnoer

    def __repr__(self):
        return (
            'BloomFilter(ideal_num_elements_n=%d, error_rate_p=%f, '
            + 'num_bits_m=%d)'
        ) % (
            self.ideal_num_elements_n,
            self.error_rate_p,
            self.num_bits_m,
        )

    def add(self, key):
        """Add an element to the filter"""
        for bitno in self.probe_bitnoer(self, key):
            self.backend.set(bitno)

    def __iadd__(self, key):
        self.add(key)
        return self

    def _match_template(self, bloom_filter):
        """
        Compare a sort of signature for two bloom filters.

        Used in preparation for binary operations
        """
        return (self.num_bits_m == bloom_filter.num_bits_m
                and self.num_probes_k == bloom_filter.num_probes_k
                and self.probe_bitnoer == bloom_filter.probe_bitnoer)

    def union(self, bloom_filter):
        """Compute the set union of two bloom filters"""
        self.backend |= bloom_filter.backend

    def __ior__(self, bloom_filter):
        self.union(bloom_filter)
        return self

    def intersection(self, bloom_filter):
        """Compute the set intersection of two bloom filters"""
        self.backend &= bloom_filter.backend

    def __iand__(self, bloom_filter):
        self.intersection(bloom_filter)
        return self

    def __contains__(self, key):
        for bitno in self.probe_bitnoer(self, key):
            if not self.backend.is_set(bitno):
                return False
        return True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.backend = None

    def __del__(self):
        if self.backend is not None:
            self.backend = None