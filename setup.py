#!/usr/bin/env python
"""Setup script for Python Hydra Agent."""

from setuptools import setup, find_packages

try:
    # pip >=20
    from pip._internal.network.session import PipSession
    from pip._internal.req import parse_requirements
    install_requires = parse_requirements('requirements.txt',session=PipSession())
    dependencies = [str(package.requirement) for package in install_requires]
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.download import PipSession
        from pip._internal.req import parse_requirements       
    except ImportError:
        # pip <= 9.0.3
        from pip.download import PipSession
        from pip.req import parse_requirements

    install_requires = parse_requirements('requirements.txt',session=PipSession())
    dependencies = [str(package.req) for package in install_requires]

for package_index in range(len(dependencies)):
  if dependencies[package_index].startswith('git+'):
      dependencies[package_index] = dependencies[package_index].split('=')[1]

setup(name='hydra-python-agent',
      include_package_data=True,
      version='0.0.1',
      description='A Hydra agent using Python and Redis',
      author='Hydra Ecosystem',
      author_email='collective@hydraecosystem.org',
      url='https://github.com/HTTP-APIs/python-hydra-agent',
      python_requires='>=3',
      install_requires=dependencies,
      packages=find_packages(
          exclude=['hydra','examples','test*','python_whihydra_agent.egg-info']),
      package_dir={'hydra_agent':
                   'hydra_agent'},
      )