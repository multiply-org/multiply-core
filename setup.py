#!/usr/bin/env python

from setuptools import setup

requirements = [
    'gdal',
    'osr'
]

setup(name='multiply-core',
      version='0.1',
      description='MULTIPLY Core',
      author='MULTIPLY Team',
      packages=['multiply_core', 'multiply_core.util'],
      install_requires=requirements
)