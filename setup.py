#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup


setup(
    name="AMQ-Library",
    version="1.0.0",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    author="Aadil Manazir",
    keywords="probabilistic set datastructure",
    url='https://github.com/aadilmanazir/AMQ-library',
)
