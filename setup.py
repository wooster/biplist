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
    version = '0.1',
    url = 'https://github.com/wooster/biplist',
    download_url = 'https://github.com/wooster/biplist/downloads',
    license = 'BSD',
    description = "biplist is a library for reading/writing binary plists.",
    author = 'Andrew Wooster',
    author_email = 'andrew@planetaryscale.com',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    install_requires = [
    ],
)
