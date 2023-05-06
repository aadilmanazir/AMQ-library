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

    h = mmh3.hash64(data, seed)
    return abs(h[0])  # Only use the first 64-bit hash value


def _int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')


def _bytes_to_int(x):
    return int.from_bytes(x, byteorder='big')


def fingerprint(data, size):
    """
    Get fingerprint of a string using MurmurHash3 64-bit hash and truncate it to
    'size' bytes.
    :param data: Data to get fingerprint for
    :param size: Size in bytes to truncate the fingerprint
    :return: fingerprint of 'size' bytes
    """
    seed = 42  # Arbitrary seed value for MurmurHash3
    fp = _int_to_bytes(_mmh3_hash(data, seed))
    return _bytes_to_int(fp[:size])


def hash_code(data):
    """Generate hash code using mmh3.hash() function.
    :param data: Data to generate hash code for
    """
    if not isinstance(data, (str, int, float)):
        raise TypeError("Data must be of type str, int, or float")

    data_str = str(data)
    seed = 97  # Arbitrary seed value for MurmurHash3
    return abs(mmh3.hash(data_str, seed))