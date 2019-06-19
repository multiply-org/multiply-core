from pathlib import Path
from typing import List, Optional

import json
import logging
import os
import pkg_resources

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

ALL_FORWARD_MODELS = []
FORWARD_MODELS_FILE_NAME = 'forward_models.txt'
MULTIPLY_DIR_NAME = '.multiply'


class ForwardModel(object):

    def __init__(self, model_as_dict: dict):
        self._short_name = model_as_dict['id']
        self._name = model_as_dict['name']
        self._description = model_as_dict['description']
        self._authors = model_as_dict['model_authors']
        self._url = model_as_dict['model_url']
        self._input_type = model_as_dict['input_type']
        self._variables = model_as_dict['variables']

    def __repr__(self):
        return 'Forward Model:\n' \
               '  Id: {}, \n' \
               '  Name: {}, \n' \
               '  Description: {}, \n' \
               '  Model Authors: {}, \n' \
               '  Model URL: {}, \n' \
               '  Input Type: {}, \n' \
               '  Variables: {}\n'.format(self.id, self.name, self.description, self.authors, self.url,
                                          self.input_type, self.variables)

    @property
    def id(self) -> str:
        return self._short_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def authors(self) -> List[str]:
        return self._authors

    @property
    def url(self) -> str:
        return self._url

    @property
    def input_type(self) -> str:
        return self._input_type

    @property
    def variables(self) -> List[str]:
        return self._variables

    # noinspection PyUnresolvedReferences
    def equals(self, other: object) -> bool:
        """
        Checks whether another object is equal to this variable.
        :param other:
        :return:
        """
        return type(other) == ForwardModel and self.id == other.id and self.name == other.display_name \
               and self.description == other.description and self.input_type == other.input_type


def _get_default_forward_models_file() -> str:
    multiply_home_dir = _get_multiply_home_dir()
    forward_models_file = '{0}/{1}'.format(multiply_home_dir, FORWARD_MODELS_FILE_NAME)
    if not os.path.exists(forward_models_file):
        open(forward_models_file, 'w+')
    return forward_models_file


def _get_multiply_home_dir() -> str:
    home_dir = str(Path.home())
    multiply_home_dir = '{0}/{1}'.format(home_dir, MULTIPLY_DIR_NAME)
    if not os.path.exists(multiply_home_dir):
        os.mkdir(multiply_home_dir)
    return multiply_home_dir


def register_forward_model(forward_model_file: str):
    forward_models_registry_file = _get_default_forward_models_file()
    _register_forward_model(forward_model_file, forward_models_registry_file)


def _register_forward_model(forward_model_file: str, forward_models_registry_file: str):
    _read_forward_model(forward_model_file)  # to validate
    if os.path.exists(forward_models_registry_file):
        mode = "a"
    else:
        mode = "w"
    with(open(forward_models_registry_file, mode)) as registry_file:
        registry_file.write(forward_model_file + '\n')


def get_forward_models() -> List[ForwardModel]:
    forward_models_file = _get_default_forward_models_file()
    return _get_forward_models(forward_models_file)


def _get_forward_models(forward_models_file: str) -> List[ForwardModel]:
    forward_models = []
    with(open(forward_models_file, 'r')) as file:
        file_paths = file.readlines()
        for file_path in file_paths:
            file_path = file_path.rstrip()
            if not os.path.exists(file_path):
                logging.warning(f'Could not find forward model file {file_path}')
                continue
            forward_models.append(_read_forward_model(file_path))
    return forward_models


def _read_forward_model(model_file: str) -> ForwardModel:
    with(open(model_file, 'r')) as file:
        forward_model = json.load(file)
        return ForwardModel(forward_model)
