from pathlib import Path
from multiply_core.util import get_aux_data_provider
from typing import Dict, List, Optional

import json
import logging
import os

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

ALL_FORWARD_MODELS = []
FORWARD_MODELS_FILE_NAME = 'forward_models.txt'
MULTIPLY_DIR_NAME = '.multiply'


class ForwardModel(object):

    def __init__(self, model_dir: str, model_id: str, name: str, description: str, model_data_type: str,
                 inference_engine_type: str, variables: List[str], required_priors: List[str],
                 model_authors: Optional[List[str]] = None, model_url: Optional[str] = None,
                 input_bands: Optional[List[str]] = None, input_band_indices: Optional[List[int]] = None):
        self._model_dir = model_dir
        self._short_name = model_id
        self._name = name
        self._description = description
        self._model_data_type = model_data_type
        self._inference_engine_type = inference_engine_type
        self._variables = variables
        self._required_priors = required_priors
        self._authors = []
        if model_authors is not None:
            self._authors = model_authors
        self._url = ''
        if model_url is not None:
            self._url = model_url
        self._input_bands = []
        if input_bands is not None:
            self._input_bands = input_bands
        self._input_band_indices = []
        if input_band_indices is not None:
            self._input_band_indices = input_band_indices

    def __repr__(self):
        return 'Forward Model:\n' \
               '  Id: {}, \n' \
               '  Name: {}, \n' \
               '  Description: {}, \n' \
               '  Model Authors: {}, \n' \
               '  Model URL: {}, \n' \
               '  Model Data Type: {}, \n' \
               '  Variables: {}\n'.format(self.id, self.name, self.description, self.authors, self.url,
                                          self.model_data_type, self.variables)

    @property
    def model_dir(self) -> str:
        return self._model_dir

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
    def inference_engine_type(self) -> str:
        return self._inference_engine_type

    @property
    def authors(self) -> List[str]:
        return self._authors

    @property
    def url(self) -> str:
        return self._url

    @property
    def model_data_type(self) -> str:
        return self._model_data_type

    @property
    def input_bands(self) -> List[str]:
        return self._input_bands

    @property
    def input_band_indices(self) -> List[int]:
        return self._input_band_indices

    @property
    def variables(self) -> List[str]:
        return self._variables

    @property
    def required_priors(self) -> List[str]:
        return self._required_priors

    def as_dict(self) -> Dict:
        return {'id': self.id, 'name': self.name, 'description': self.description, 'model_authors': self.authors,
                'model_url': self.url, 'input_type': self.model_data_type, 'input_bands': self.input_bands,
                'input_band_indices': self.input_band_indices, 'variables': self.input_band_indices,
                'required_priors': self.required_priors}

    # noinspection PyUnresolvedReferences
    def equals(self, other: object) -> bool:
        """
        Checks whether another object is equal to this forward model.
        :param other:
        :return:
        """
        return type(other) == ForwardModel and self.id == other.id and self.name == other.display_name \
               and self.description == other.description and self.model_data_type == other.input_type \
               and self.input_bands == other.input_bands and self.input_band_indices == other.input_band_indices


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


def get_forward_model(model_name: str) -> Optional[ForwardModel]:
    models = get_forward_models()
    for model in models:
        if model.id == model_name:
            return model


def _get_forward_models(forward_models_file: str) -> List[ForwardModel]:
    aux_data_provider = get_aux_data_provider()
    forward_models = []
    with(open(forward_models_file, 'r')) as file:
        file_paths = file.readlines()
        for file_path in file_paths:
            file_path = file_path.rstrip()
            if not aux_data_provider.assure_element_provided(file_path):
                logging.warning(f'Could not find forward model file {file_path}')
                continue
            forward_models.append(_read_forward_model(file_path))
    return forward_models


def _read_forward_model(model_file: str) -> ForwardModel:
    with(open(model_file, 'r')) as file:
        forward_model_path = os.path.abspath(os.path.join(model_file, os.pardir)).replace('\\', '/')
        model = json.load(file)
        model_authors = None
        if 'model_authors' in model:
            model_authors = model['model_authors']
        model_url = None
        if 'model_url' in model:
            model_url = model['model_url']
        input_bands = None
        if 'input_bands' in model:
            input_bands = model['input_bands']
        input_band_indices = None
        if 'input_band_indices' in model:
            input_band_indices = model['input_band_indices']
        return ForwardModel(model_dir=forward_model_path, model_id=model['id'], name=model['name'],
                            description=model["description"], model_data_type=model['model_data_type'],
                            inference_engine_type=model['inference_engine_type'], variables=model['variables'],
                            required_priors=model['required_priors'], model_authors=model_authors, model_url=model_url,
                            input_bands=input_bands, input_band_indices=input_band_indices)
