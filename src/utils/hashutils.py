import mmh3

MAX_64_INT = 2 ** 64
MAX_32_INT = 2 ** 32


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

def fingerprint(data, size_bits):
    """
    Get fingerprint of a string using MurmurHash3 64-bit hash and truncate it to
    'size_bits' bits.
    :param data: Data to get fingerprint for
    :param size_bits: Size in bits to truncate the fingerprint
    :return: fingerprint of 'size_bits' bits
    """
    seed = 42  # Arbitrary seed value for MurmurHash3
    fp = _mmh3_hash(data, seed)

    # Apply a bitwise AND operation to get the correct number of bits for the fingerprint
    mask = (1 << size_bits) - 1
    fp &= mask

    return fp


def hash_code(data, num_buckets):
    """Generate hash code using mmh3.hash() function.
    :param data: Data to generate hash code for
    """
    return _mmh3_hash(data, seed=97) % num_buckets