#!/usr/bin/env python

from setuptools import setup

requirements = [
    'gdal',
    'numpy',
    'osr',
    'pytest',
    'shapely',
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
      entry_points={
          'observations_creators': [
              's2_observation_creator = multiply_core.observations:s2_observations.S2ObservationsCreator',
          ],
      },
      install_requires=requirements
      )
