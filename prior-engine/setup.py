#!/usr/bin/env python

from setuptools import setup

requirements = [
    'python-dateutil',
    'gdal',
    'matplotlib',
    'numpy',
    'pyyaml',
    'shapely'
]

__version__ = None
with open('multiply_prior_engine/version.py') as f:
    exec(f.read())

setup(name='multiply-prior-engine',
      version=__version__,
      description='MULTIPLY Prior Engine',
      author='MULTIPLY Team',
      packages=['multiply_prior_engine'],
      # entry_points={
      #     'file_system_plugins': [
      #         'local_file_system = multiply_data_access:local_file_system.LocalFileSystemAccessor',
      #     ],
      #     'meta_info_provider_plugins': [
      #         'json_meta_info_provider = multiply_data_access:json_meta_info_provider.JsonMetaInfoProviderAccessor',
      #     ],
      # },
      install_requires=requirements
)
