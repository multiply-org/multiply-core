"""
Description
===========

This module contains MULTIPLY Data Checkers and default implementations. The purpose of these is to define whether
a file is of a given type or not.
"""


__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


from abc import ABCMeta, abstractmethod


class DataValidator(metaclass=ABCMeta):

    @classmethod
    def name(cls) -> str:
        """The name of the data type supported by this checker."""

    @abstractmethod
    def is_valid(self, path: str) -> bool:
        """Whether the data at the given path is a valid data product for the type."""

class AWS_S2_Validator(DataValidator):
    # 29\S\QB\2017\9\4\0

    @classmethod
    def name(cls) -> str:
        return 'AWS_S2_L1C'

    def is_valid(self, path: str) -> bool:
        return False


class Validation(object):

    def __init__(self):
        self.validators = []
        # TODO replace this with framework
        self.validators.append(AWS_S2_Validator())

    def add_validator(self, validator: DataValidator):
        self.validators.append(validator)

    def get_valid_type(self, path: str) -> str:
        for validator in self.validators:
            if validator.is_valid(path):
                return validator.name()
        return ''
