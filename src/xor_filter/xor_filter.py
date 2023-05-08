import array
import math
import os
import random
import mmh3
import numpy as np

def _mmh3_hash(data, seed):
    """
    Generate MurmurHash3 hash for data in bytes with a given seed
    :param data: Data to generate MurmurHash3 hash for
    :param seed: Seed for the MurmurHash3 hash function
    """
    if not isinstance(data, (str, int, float)):
        raise TypeError("Data must be of type str, int, or float")
    else:
        data = str(data).encode()

    h = mmh3.hash_bytes(data, seed=seed)
    return int.from_bytes(h, byteorder='big', signed=True)

def get_fingerprint(seed, size_bits):
    """
    Generate a [2 ** size_bits]-valued hash function using the given seed.
    """
    def h(data):
        hash = _mmh3_hash(data, seed)
        mask = (1 << size_bits) - 1
        return hash & mask
    return h

def get_hash_funcs(seeds, size):
    """
    Generate three independent hash functions with different ranges.
    """
    c1 = math.floor(size / 3)
    c2 = math.floor(2 * size / 3)
    h0 = lambda data: (_mmh3_hash(data, seeds[0]) % c1)
    h1 = lambda data: c1 + (_mmh3_hash(data, seeds[1]) % (c2 - c1))
    h2 = lambda data: c2 + (_mmh3_hash(data, seeds[2]) % (size - c2))
    return h0, h1, h2



class XorFilter:
    """
    Approximate membership query for large immutable sets
    from https://dl.acm.org/doi/fullHtml/10.1145/3376122
    """

    def __init__(self, max_elements, error_rate, keys):
        self.max_elements = max_elements
        self.error_rate = error_rate  # eps
        self.size = math.floor(1.23 * len(keys)) + 32  # c
        self.num_bits = 1 + math.ceil(-math.log2(self.error_rate))  # k
        # 2^{-k} < eps, or k > -log_2(eps)

        fingerprint_seed = 123
        self.fingerprint = get_fingerprint(fingerprint_seed, self.num_bits)

        h0, h1, h2 = None, None, None
        success, stack = False, []
        while not success:
            seeds = random.sample(range(1 << 31), 3)
            if fingerprint_seed in seeds:
                continue
            h0, h1, h2 = get_hash_funcs(seeds, self.size)
            success, stack = self._map_keys(keys, h0, h1, h2)

        self.h0, self.h1, self.h2 = h0, h1, h2
        # self.backend = array.array('I', [0] * self.size)
        self.backend = np.empty(self.size, dtype=int)
        self._assign_values(stack)

    def _map_keys(self, keys, h0, h1, h2):
        hash_keys = [set() for _ in range(self.size)]
        for key in keys:
            hash_keys[h0(key)].add(key)
            hash_keys[h1(key)].add(key)
            hash_keys[h2(key)].add(key)
        queue = []
        for i in range(self.size):
            if len(hash_keys[i]) == 1:
                queue.append(i)
        stack = []
        while queue:
            index = queue.pop(0)
            if len(hash_keys[index]) == 1:
                key = next(iter(hash_keys[index]))
                stack.append((key, index))
                hash_keys[h0(key)].remove(key)
                if len(hash_keys[h0(key)]) == 1:
                    queue.append(h0(key))
                hash_keys[h1(key)].remove(key)
                if len(hash_keys[h1(key)]) == 1:
                    queue.append(h1(key))
                hash_keys[h2(key)].remove(key)
                if len(hash_keys[h2(key)]) == 1:
                    queue.append(h2(key))
        if len(stack) == len(keys):
            return True, stack
        return False, []

    def _assign_values(self, stack):
        for key, index in reversed(stack):
            self.backend[index] = 0
            self.backend[index] = self.fingerprint(key) ^ self._expected_fingerprint(key)

    def _expected_fingerprint(self, key):
        return self.backend[self.h0(key)] ^ self.backend[self.h1(key)] ^ self.backend[self.h2(key)]

    def __len__(self):
        return self.size

    def __repr__(self):
        return "<XorFilter: n=%d, error_rate=%f, num_bits=%d>" % (
            self.size,
            self.error_rate,
            self.num_bits,
        )

    def contains(self, key):
        """
        Check whether the given element is contained in the filter.
        """
        return key in self

    def __contains__(self, key):
        return self.fingerprint(key) == self._expected_fingerprint(key)
