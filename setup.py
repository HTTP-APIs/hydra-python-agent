#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for the Python implementation of LD Patch
"""

from setuptools import setup

from ast import literal_eval

def get_version(source='hydra/__init__.py'):
    """
    Retrieve version number without importing the script.
    """
    with open(source) as pyfile:
        for line in pyfile:
            if line.startswith('__version__'):
                return literal_eval(line.partition('=')[2].lstrip())
    raise ValueError("VERSION not found")

README = ''
with open('README.rst', 'r') as f:
    README = f.read()

INSTALL_REQ = []
with open('requirements.txt', 'r') as f:
    # Get requirements depencies as written in the file
    INSTALL_REQ = [ i[:-1] for i in f if i[0] != "#" ]

setup(name = 'python-hydra-agent',
      version = get_version(),
      #package_dir = {'': 'lib'},
      packages = ['hydra'],
      description = 'A Hydra implementation for Python',
      long_description = README,
      author='W3C Hydra Contributors',
      author_email='public-hydra@w3.org',
      license='LGPL v3',
      platforms='OS Independant',
      url='https://github.com/HTTP-APIs/python-hydra-agent',
      include_package_data=True,
      install_requires=INSTALL_REQ,
      scripts=[],
     )
