from abc import ABCMeta, abstractmethod
from typing import List, Optional
import glob
import os

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"


class AuxDataProvider(metaclass=ABCMeta):

    @abstractmethod
    def list_elements(self, base_folder: str, pattern: [Optional[str]]) -> List[str]:
        """
        Lists available elements
        :return:
        """

    @abstractmethod
    def assure_element_provided(self, name: str) -> bool:
        """
        Ensures that the element is provided.
        :param name: the element that shall be provided.
        :return:
        """


class DefaultAuxDataProvider(AuxDataProvider):

    def list_elements(self, base_folder: str, pattern: [Optional[str]] = '*') -> List[str]:
        return glob.glob(f'{base_folder}/{pattern}')

    def assure_element_provided(self, name: str) -> bool:
        return os.path.exists(name)
