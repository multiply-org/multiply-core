from abc import ABCMeta, abstractmethod
from typing import List, Optional
from pathlib import Path
import glob
import json
import os
import pkg_resources

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

MULTIPLY_DIR_NAME = '.multiply'
AUX_DATA_PROVIDER_FILE_NAME = 'aux_data_provider.json'
AUX_DATA_PROVIDERS = []
DEFAULT_AUX_DATA_PROVIDER_NAME = 'DEFAULT'


class AuxDataProvider(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """
        :return: The name of the file system implementation.
        """

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

    @classmethod
    def name(cls):
        return DEFAULT_AUX_DATA_PROVIDER_NAME

    def list_elements(self, base_folder: str, pattern: [Optional[str]] = '*') -> List[str]:
        return glob.glob(f'{base_folder}/{pattern}')

    def assure_element_provided(self, name: str) -> bool:
        return os.path.exists(name)


def _set_up_aux_data_provider_registry():
    if len(AUX_DATA_PROVIDERS) > 0:
        return
    aux_data_provider_entry_points = pkg_resources.iter_entry_points('aux_data_providers')
    for aux_data_provider_entry in aux_data_provider_entry_points:
        AUX_DATA_PROVIDERS.append(aux_data_provider_entry.load())


def _get_multiply_home_dir() -> str:
    home_dir = str(Path.home())
    multiply_home_dir = f'{home_dir}/{MULTIPLY_DIR_NAME}'
    if not os.path.exists(multiply_home_dir):
        os.mkdir(multiply_home_dir)
    return multiply_home_dir


def _get_aux_data_provider_file() -> str:
    multiply_home_dir = _get_multiply_home_dir()
    path_to_aux_data_provider_file = f'{multiply_home_dir}/{AUX_DATA_PROVIDER_FILE_NAME}'
    return path_to_aux_data_provider_file


def _get_aux_data_provider(path_to_file: str) -> AuxDataProvider:
    if os.path.exists(path_to_file):
        with open(path_to_file, "r") as aux_data_provider_file:
            aux_data_provider_dict = json.load(aux_data_provider_file)
            if 'aux_data_provider' in aux_data_provider_dict:
                for aux_data_provider in AUX_DATA_PROVIDERS:
                    if aux_data_provider_dict['aux_data_provider'] == aux_data_provider.name():
                        return aux_data_provider
    return DefaultAuxDataProvider()


def get_aux_data_provider() -> AuxDataProvider:
    _set_up_aux_data_provider_registry()
    aux_data_provider_file = _get_aux_data_provider_file()
    return _get_aux_data_provider(aux_data_provider_file)


def _add_aux_data_provider(aux_data_provider: AuxDataProvider):
    AUX_DATA_PROVIDERS.append(aux_data_provider)
