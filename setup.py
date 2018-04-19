#!/usr/bin/env python

from setuptools import setup

requirements = [
    'gdal',
    'numpy',
    'osr',
    'pytest',
    'scipy'
]

__version__ = None
with open('multiply_core/version.py') as f:
    exec(f.read())

setup(name='multiply-core',
      version=__version__,
      description='MULTIPLY Core',
      author='MULTIPLY Team',
      packages=['multiply_core', 'multiply_core.util', 'multiply_core.observations'],
      install_requires=requirements
      )
