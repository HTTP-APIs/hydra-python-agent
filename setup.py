#!/usr/bin/env python
"""Setup script for Python Hydra Agent."""

from setuptools import setup, find_packages

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements
    from pip.download import PipSession


install_requires = parse_requirements('requirements.txt', session=PipSession())
dependencies = [str(package.req) for package in install_requires]

setup(name='hydra-python-agent',
      include_package_data=True,
      version='0.0.1',
      description='A Hydra agent using Python and Redis',
      author='W3C HYDRA development group',
      author_email='public-hydra@w3.org',
      url='https://github.com/HTTP-APIs/python-hydra-agent',
      python_requires='>=3',
      install_requires=dependencies,
      packages=find_packages(
          exclude=['hydra','examples','test*','python_whihydra_agent.egg-info']),
      package_dir={'hydra_agent':
                   'hydra_agent'},
      )
