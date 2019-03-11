from typing import List, Optional
import pkg_resources
import yaml

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

ALL_VARIABLES = []


class Variable(object):

    def __init__(self, variable_as_dict: dict):
        self._short_name = variable_as_dict['short_name']
        self._display_name = variable_as_dict['display_name']
        self._unit = variable_as_dict['unit']
        self._description = variable_as_dict['description']
        self._range = variable_as_dict['range']
        self._applications = variable_as_dict['applications']

    @property
    def short_name(self) -> str:
        return self._short_name

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def description(self) -> str:
        return self._description

    @property
    def range(self) -> str:
        return self._range

    @property
    def applications(self) -> List[str]:
        return self._applications


def get_default_variables():
    return yaml.safe_load(pkg_resources.resource_stream(__name__, 'default_variables_library.yaml'))


def _set_up_variable_registry():
    variable_entry_points = pkg_resources.iter_entry_points('variables')
    for variable_entry in variable_entry_points:
        variable_dict_list_function = variable_entry.load()
        variable_dict_list = variable_dict_list_function()
        for variable_dict in variable_dict_list:
            ALL_VARIABLES.append(Variable(variable_dict['Variable']))


def get_registered_variables() -> List[Variable]:
    _set_up_variable_registry()
    return ALL_VARIABLES


def get_registered_variable(variable_name: str) -> Optional[Variable]:
    """
    :param variable_name: The name of the requested variable.
    :return: The requested variable if registered, otherwise None.
    """
    _set_up_variable_registry()
    for variable in ALL_VARIABLES:
        if variable_name == variable.short_name:
            return variable
    return None
