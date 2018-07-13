"""
Description
===========

This module contains MULTIPLY Data Checkers and default implementations. The purpose of these is to define whether
a file is of a given type or not.
"""


__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


from abc import ABCMeta, abstractmethod
from typing import List
import re
import os

VALIDATORS = []


class DataValidator(metaclass=ABCMeta):

    @classmethod
    def name(cls) -> str:
        """The name of the data type supported by this checker."""

    @abstractmethod
    def is_valid(self, path: str) -> bool:
        """Whether the data at the given path is a valid data product for the type."""

    @abstractmethod
    def get_relative_path(self, path:str) -> str:
        """
        :param path: Path to a file.
        :return: The part of the path which is relevant for a product to be identified as product of this type.
        """


class AWSS2L1Validator(DataValidator):

    def __init__(self):
        self.BASIC_AWS_S2_PATTERN = '/[0-9]{1,2}/[A-Z]/[A-Z]{2}/20[0-9][0-9]/[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}'
        self.BASIC_AWS_S2_MATCHER = re.compile(self.BASIC_AWS_S2_PATTERN)
        self.AWS_S2_PATTERN = '.*/[0-9]{1,2}/[A-Z]/[A-Z]{2}/20[0-9][0-9]/[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}'
        self.AWS_S2_MATCHER = re.compile(self.AWS_S2_PATTERN)
        self._expected_files = ['B01.jp2', 'B02.jp2', 'B03.jp2', 'B04.jp2', 'B05.jp2', 'B06.jp2', 'B07.jp2', 'B08.jp2',
                                'B8A.jp2', 'B09.jp2', 'B10.jp2', 'B11.jp2', 'B12.jp2', 'metadata.xml']

    @classmethod
    def name(cls) -> str:
        return 'AWS_S2_L1C'

    def is_valid(self, path: str) -> bool:
        if not self._matches_pattern(path):
            return False
        for file in self._expected_files:
            if not os.path.exists(path + '/' + file):
                return False
        return True

    def _matches_pattern(self, path: str) -> bool:
        return self.AWS_S2_MATCHER.match(path) is not None

    def get_relative_path(self, path:str) -> str:
        start_pos, end_pos = self.BASIC_AWS_S2_MATCHER.search(path).regs[0]
        return path[start_pos + 1:end_pos]


class AWSS2L2Validator(DataValidator):

    def __init__(self):
        self._expected_files = [['B01_sur.tif', 'B01_sur.tiff'], ['B02_sur.tif', 'B02_sur.tiff'],
                                ['B03_sur.tif', 'B03_sur.tiff'], ['B04_sur.tif', 'B04_sur.tiff'],
                                ['B05_sur.tif', 'B05_sur.tiff'], ['B06_sur.tif', 'B06_sur.tiff'],
                                ['B07_sur.tif', 'B07_sur.tiff'], ['B08_sur.tif', 'B08_sur.tiff'],
                                ['B8A_sur.tif', 'B8A_sur.tiff'], ['B09_sur.tif', 'B09_sur.tiff'],
                                ['B10_sur.tif', 'B10_sur.tiff'], ['B11_sur.tif', 'B11_sur.tiff'],
                                ['B12_sur.tif', 'B12_sur.tiff'], ['metadata.xml']]

    @classmethod
    def name(cls) -> str:
        return 'AWS_S2_L2'

    def is_valid(self, path: str) -> bool:
        for files in self._expected_files:
            found = False
            for file in files:
                if os.path.exists(path + '/' + file):
                    found = True
                    break
            if not found:
                return False
        return True

    def get_relative_path(self, path:str) -> str:
        return ''


# TODO replace this with framework
VALIDATORS.append(AWSS2L1Validator())
VALIDATORS.append(AWSS2L2Validator())


def add_validator(validator: DataValidator):
    VALIDATORS.append(validator)


def get_valid_type(path: str) -> str:
    for validator in VALIDATORS:
        if validator.is_valid(path):
            return validator.name()
    return ''


def get_valid_types() -> List[str]:
    """Returns the names of all data types which can be valid."""
    valid_types = []
    for validator in VALIDATORS:
        valid_types.append(validator.name())
    return valid_types

def get_data_type_path(data_type: str, path: str) -> str:
    """
    :param data_type: The data type of
    :param path: Path to a file.
    :return: The part of the path which is relevant for a product to be identified as product of this type. None,
    if data type is not found.
    """
    for validator in VALIDATORS:
        if validator.name() == data_type:
            return validator.get_relative_path(path)
    return ''
