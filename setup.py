#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup


setup(
    name="bloom-filter",
    version="1.3",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    author="Harshad Sharma",
    author_email="harshad@sharma.io",
    description='Pure Python Bloom Filter module',
    long_description=open('README.rst').read(),
    license="MIT",
    keywords="probabilistic set datastructure",
    url='https://github.com/hiway/python-bloom-filter',
    platforms='Cross platform',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
)
