"""
Description
===========

This module contains MULTIPLY Data Checkers and default implementations. The purpose of these is to define whether
a file is of a given type or not.
"""


__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


from abc import ABCMeta, abstractmethod
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

class AWS_S2_Validator(DataValidator):

    def __init__(self):
        self.AWS_S2_PATTERN = '.*/[0-9]{1,2}/[A-Z]/[A-Z]{2}/20[0-9][0-9]/[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}'
        self.AWS_S2_MATCHER = re.compile(self.AWS_S2_PATTERN)
        self._expected_files = ['B01.jp2', 'B02.jp2', 'B03.jp2', 'B04.jp2', 'B05.jp2', 'B06.jp2', 'B07.jp2', 'B08.jp2',
                               'B8A.jp2', 'B09.jp2', 'B10.jp2', 'B11.jp2', 'B12.jp2', 'metadata.xml']

    @classmethod
    def name(cls) -> str:
        return 'AWS_S2_L1C'

    def is_valid(self, path: str) -> bool:
        if not self.matches_pattern(path):
            return False
        for file in self._expected_files:
            if not os.path.exists(path + '/' + file):
                return False
        return True

    def matches_pattern(self, path: str) -> bool:
        return self.AWS_S2_MATCHER.match(path) is not None

# TODO replace this with framework
VALIDATORS.append(AWS_S2_Validator())


def add_validator(validator: DataValidator):
    VALIDATORS.append(validator)


def get_valid_type(path: str) -> str:
    for validator in VALIDATORS:
        if validator.is_valid(path):
            return validator.name()
    return ''
