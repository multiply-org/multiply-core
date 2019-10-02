"""
Description
===========

This module defines the interface to MULTIPLY observations.
"""
from abc import ABCMeta, abstractmethod
from datetime import datetime

import logging
import numpy as np
import pkg_resources
import scipy.sparse as sp
from typing import List, Optional, Union

from multiply_core.util import FileRef, Reprojection, get_time_from_string
from .data_validation import get_valid_type
from ..models.forward_models import get_forward_models

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

LOG = logging.getLogger(__name__ + ".Sentinel2_Observations")
LOG.setLevel(logging.INFO)
if not LOG.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - ' +
                                  '%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    LOG.addHandler(ch)
LOG.propagate = False


class ObservationData(object):
    """A class encapsulating the access to an Observations object."""

    def __init__(self, observations: np.array, uncertainty: sp.lil_matrix, mask: np.array, metadata: dict, emulator):
        self._observations = observations
        self._uncertainty = uncertainty
        self._mask = mask
        self._metadata = metadata
        self._emulator = emulator

    @property
    def observations(self) -> np.array:
        return self._observations

    @property
    def uncertainty(self):
        return self._uncertainty

    @property
    def mask(self):
        return self._mask

    @property
    def metadata(self):
        return self._metadata

    @property
    def emulator(self):
        return self._emulator


class ProductObservations(metaclass=ABCMeta):
    """The interface to an Observations object. An observations object allows to access any EO data that comes from a
    file."""

    @abstractmethod
    def get_band_data_by_name(self, band_name: str, retrieve_uncertainty: bool = True) -> ObservationData:
        """
        This method returns
        :param band_name: The name of the band.
        :return: An ObservationData product according to the input.
        """

    @abstractmethod
    def get_band_data(self, band_index: int, retrieve_uncertainty: bool = True) -> ObservationData:
        """
        This method returns
        :param band_index: The index of the band within the product.
        :return: An ObservationData product according to the input.
        """

    @property
    @abstractmethod
    def bands_per_observation(self) -> int:
        """Returns the number of bands this observations object provides access to."""

    @property
    @abstractmethod
    def data_type(self) -> str:
        """The type of data accessed by this observations class."""

    @abstractmethod
    def set_no_data_value(self, band: Union[str, int], no_data_value: float):
        """Sets a new no data value to a band."""

    @abstractmethod
    def read_granule(self) -> (List[np.array], np.array, np.float, np.float, np.float, List[np.array]):
        """Reads """


class ProductObservationsCreator(metaclass=ABCMeta):
    """The interface to an ObservationsCreator object. There shall be one for every Observations object. It is used to
    create an Observations object from a file."""

    @classmethod
    def can_read(cls, file_ref: FileRef) -> bool:
        """
        Whether the Observations can read from the referenced file.
        :param file_ref: The referenced file
        :return: True, if the observations can be read
        """

    @classmethod
    def create_observations(cls, file_ref: FileRef, reprojection: Optional[Reprojection],
                            emulator_folder: Optional[str]) -> ProductObservations:
        """
        Creates an Observations object for the given fileref object.
        :param reprojection: A Reprojection object to reproject the data
        :param emulator_folder: A folder containing the emulators for the observations.
        :param file_ref: A reference to a file containing data.
        :return: An Observations object that encapsulates the data.
        """


class ObservationsWrapper(object):
    """An Observations Object. Allows external components to access EO data."""

    def __init__(self):
        self._observations = {}
        self.dates = []  # datetime objects
        self.bands_per_observation = {}

    def add_observations(self, product_observations: ProductObservations, date: str):
        bands_per_observation = product_observations.bands_per_observation
        date = get_time_from_string(date)
        self.dates.append(date)
        self._observations[date] = product_observations
        self.bands_per_observation[date] = bands_per_observation

    def get_band_data_by_name(self, date: datetime, band_name: str, retrieve_uncertainty: bool = True) -> ObservationData:
        """
        This method returns
        :param date: The time of the products represented by the Observations class. It is used to identify the product.
        :param band_name: The name of the band within the product.
        :return: An ObservationData product according to the input.
        """
        return self._observations[date].get_band_data_by_name(band_name, retrieve_uncertainty)

    def get_band_data(self, date: datetime, band_index: int, retrieve_uncertainty: bool = True) -> ObservationData:
        """
        This method returns
        :param date: The time of the products represented by the Observations class. It is used to identify the product.
        :param band_index: The index of the band within the product.
        :return: An ObservationData product according to the input.
        """
        return self._observations[date].get_band_data(band_index, retrieve_uncertainty)

    def set_no_data_value(self, date: datetime, band: Union[str, int], no_data_value: float):
        self._observations[date].set_no_data_value(band, no_data_value)

    def bands_per_observation(self, date: datetime) -> int:
        """Returns an array containing the number of bands this observations object provides access to per date."""
        return self._observations[date].bands_per_observation

    def get_num_observations(self) -> int:
        """Returns the number of observations wrapped by this class. Also corresponds to the number of date_indexes."""
        return len(self._observations)

    def get_data_type(self, date: datetime) -> str:
        """
        Returns the data type of the observations from the given date.
        :param date: The time of the products represented by the Observations class. It is used to identify the product.
        :return: The data type of the observations on the given date
        """
        return self._observations[date].data_type

    def read_granule(self, date: datetime) -> (List[np.array], np.array, np.float, np.float, np.float, List[np.array]):
        granule = self._observations[date].read_granule()
        if granule[0] is None:
            LOG.info(f"{str(date):s} -> No clear observations")
        return granule


class ObservationsFactory(object):

    def __init__(self):
        self.OBSERVATIONS_CREATOR_REGISTRY = []
        registered_observations_creators = pkg_resources.iter_entry_points('observations_creators')
        for registered_observations_creator in registered_observations_creators:
            self.add_observations_creator_to_registry(observations_creator=registered_observations_creator.load())

    def add_observations_creator_to_registry(self, observations_creator: ProductObservationsCreator):
        self.OBSERVATIONS_CREATOR_REGISTRY.append(observations_creator)

    def _create_observations(self, file_ref: FileRef, reprojection: Optional[Reprojection],
                             emulator_folder: Optional[str]) -> ProductObservations:
        for observations_creator in self.OBSERVATIONS_CREATOR_REGISTRY:
            if observations_creator.can_read(file_ref):
                observations = observations_creator.create_observations(file_ref, reprojection, emulator_folder)
                return observations

    def create_observations(self, file_refs: List[FileRef], reprojection: Optional[Reprojection] = None,
                            forward_model_names: Optional[List[str]] = None) -> \
            ObservationsWrapper:
        observations_wrapper = ObservationsWrapper()
        self.sort_file_ref_list(file_refs)
        for file_ref in file_refs:
            emulators_dir = None
            if forward_model_names is not None:
                forward_models = get_forward_models()
                data_type = get_valid_type(file_ref.url)
                for forward_model_name in forward_model_names:
                    for forward_model in forward_models:
                        if forward_model.id == forward_model_name and forward_model.input_type == data_type:
                            emulators_dir = forward_model.model_dir
                            break
                    if emulators_dir is not None:
                        break
            observations = self._create_observations(file_ref, reprojection, emulators_dir)
            if observations is not None:
                observations_wrapper.add_observations(observations, file_ref.start_time)
        return observations_wrapper

    @staticmethod
    def _start_time(file_ref: FileRef):
        return file_ref.start_time

    def sort_file_ref_list(self, file_refs: List[FileRef]):
        file_refs.sort(key=self._start_time)
