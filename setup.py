#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for the Python implementation of LD Patch
"""

from setuptools import setup, find_packages

#from ast import literal_eval

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements
    from pip.download import PipSession


install_requires = parse_requirements('requirements.txt', session=PipSession())
dependencies = [str(package.req) for package in install_requires]


setup(name = 'python-hydra-agent',
      include_package_data=True,
      version = '0.0.1',
      description = 'A Hydra implementation for Python',
      author='W3C Hydra Contributors',
      author_email='public-hydra@w3.org',
      url='https://github.com/HTTP-APIs/python-hydra-agent',
      python_requires='>=3',
      install_requires=dependencies,
      packages=find_packages(
          exclude=['hydra','examples','test*','python_hydra_agent.egg-info']),
      package_dir = {'hydra_redis':
                     'hydra_redis'},


      license='LGPL v3',

     )
