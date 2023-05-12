## AMQ-Library
This library provides python implementations for several solutions to the Approximate Membership Query problem. It also contains a correctness and performance testing framework.

Implemented solutions include:
- bloom filter
- cuckoo filter
- vaccuum filter
- xor filter

### Getting started
`pip install -r requirements.txt -e .`

### Running unit tests
`python3 test/test_bloom_filter.py`

`python3 test/test_cuckoo_filter.py`

`python3 test/test_vacuum_filter.py`

`python3 test/test_xor_filter.py`
