"""
Description
===========

This module contains MULTIPLY Data Checkers and default implementations. The purpose of these is to define whether
a file is of a given type or not.
"""


__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


from abc import ABCMeta, abstractmethod


class DataChecker(metaclass=ABCMeta):

    @classmethod
    def name(cls) -> str:
        """The name of the data type supported by this checker."""

    @abstractmethod
    def is_valid(self, path: str) -> bool:
        """Whether the data at the given path is a valid data product for the type."""

class AWS_S2_Checker(DataChecker):

    @classmethod
    def name(cls) -> str:
        return 'AWS_S2_L1C'

    def is_valid(self, path: str) -> bool:
        return True