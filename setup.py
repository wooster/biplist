#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

import os

setup(
    name = 'biplist',
    version = '0.2',
    url = 'https://github.com/wooster/biplist',
    download_url = 'https://github.com/wooster/biplist/downloads/biplist-0.2.tar.gz',
    license = 'BSD',
    description = "biplist is a library for reading/writing binary plists.",
    long_description = 
    """`biplist` is a binary plist parser/generator for Python.

Binary Property List (plist) files provide a faster and smaller serialization
format for property lists on OS X. This is a library for generating binary
plists which can be read by OS X, iOS, or other clients.

This module requires Python 2.6 or higher.""",
    author = 'Andrew Wooster',
    author_email = 'andrew@planetaryscale.com',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],    
    setup_requires = ['nose', 'coverage'],
    test_suite = 'nose.collector',
    install_requires = [
    ],
)
