#!/usr/bin/env python

from setuptools import setup

setup(name='multiply-dummy',
      version='0.1',
      description='MULTIPLY Dummy',
      author='MULTIPLY Team',
      packages=['multiply_dummy'],
      entry_points={
          'console_scripts': [
              'example = cli_example.cli_example:main'
          ]
      }
     )