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


def fingerprint(data, size_bits):
    """
    Get fingerprint of a string using MurmurHash3 64-bit hash and truncate it to
    'size_bits' bits.
    :param data: Data to get fingerprint for
    :param size_bits: Size in bits to truncate the fingerprint
    :return: fingerprint of 'size_bits' bits
    """
    seed = 42  # Arbitrary seed value for MurmurHash3
    fp = _int_to_bytes(_mmh3_hash(data, seed))
    
    # Calculate the number of bytes required to store 'size_bits' bits
    size_bytes = (size_bits + 7) // 8
    
    # Truncate the fingerprint to 'size_bytes' bytes
    truncated_fp = fp[:size_bytes]

    # Convert the truncated fingerprint back to an integer
    truncated_fp_int = _bytes_to_int(truncated_fp)

    # Remove extra bits (if any) from the fingerprint to get the exact 'size_bits' bits
    num_extra_bits = size_bytes * 8 - size_bits
    if num_extra_bits > 0:
        truncated_fp_int >>= num_extra_bits

    return truncated_fp_int


def hash_code(data):
    """Generate hash code using mmh3.hash() function.
    :param data: Data to generate hash code for
    """
    if not isinstance(data, (str, int, float)):
        raise TypeError("Data must be of type str, int, or float")

    data_str = str(data)
    seed = 97  # Arbitrary seed value for MurmurHash3
    return abs(mmh3.hash(data_str, seed))