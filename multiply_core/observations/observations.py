"""
Description
===========

This module defines the interface to MULTIPLY observations.
"""
from abc import ABCMeta, abstractmethod

import numpy as np
import pkg_resources
import scipy.sparse as sp
from typing import List

from multiply_core.util import FileRef, Reprojection, get_time_from_string

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"


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
    def get_band_data(self, band_index: int) -> ObservationData:
        """
        This method returns
        :param band_index: The index of the band within the product.
        :return: An ObservationData product according to the input.
        """

    @property
    @abstractmethod
    def bands_per_observation(self):
        """Returns an array containing the number of bands this observations object provides access to per date."""


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
    def create_observations(cls, file_ref: FileRef, reprojection: Reprojection, emulator_folder: str) -> \
            ProductObservations:
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
        self._observations = []
        self.dates = []  # datetime objects
        self.bands_per_observation = []

    def add_observations(self, product_observations: ProductObservations, date: str):
        bands_per_observation = product_observations.bands_per_observation
        self._observations.append(product_observations)
        date = get_time_from_string(date)
        self.dates.append(date)
        self.bands_per_observation.append(bands_per_observation)

    def get_band_data(self, date_index: int, band_index: int) -> ObservationData:
        """
        This method returns
        :param date_index: The temporal index of the products represented by the Observations class. This index is used
        to identify the product.
        :param band_index: The index of the band within the product.
        :return: An ObservationData product according to the input.
        """
        return self._observations[date_index].get_band_data(band_index)

    def bands_per_observation(self, date_index: int):
        """Returns an array containing the number of bands this observations object provides access to per date."""
        return self._observations[date_index].bands_per_observation

    def get_num_observations(self) -> int:
        """Returns the number of observations wrapped by this class. Also corresponds to the number of date_indexes."""
        return len(self._observations)


class ObservationsFactory(object):

    def __init__(self):
        self.OBSERVATIONS_CREATOR_REGISTRY = []
        registered_observations_creators = pkg_resources.iter_entry_points('observations_creators')
        for registered_observations_creator in registered_observations_creators:
            self.add_observations_creator_to_registry(observations_creator=registered_observations_creator.load())

    def add_observations_creator_to_registry(self, observations_creator: ProductObservationsCreator):
        self.OBSERVATIONS_CREATOR_REGISTRY.append(observations_creator)

    def _create_observations(self, file_ref: FileRef, reprojection: Reprojection, emulator_folder: str) -> \
            ProductObservations:
        for observations_creator in self.OBSERVATIONS_CREATOR_REGISTRY:
            if observations_creator.can_read(file_ref):
                observations = observations_creator.create_observations(file_ref, reprojection, emulator_folder)
                return observations

    def create_observations(self, file_refs: List[FileRef], reprojection: Reprojection, emulator_folder: str) -> \
            ObservationsWrapper:
        observations_wrapper = ObservationsWrapper()
        self.sort_file_ref_list(file_refs)
        for file_ref in file_refs:
            observations = self._create_observations(file_ref, reprojection, emulator_folder)
            if observations is not None:
                observations_wrapper.add_observations(observations, file_ref.start_time)
        return observations_wrapper

    @staticmethod
    def _start_time(file_ref: FileRef):
        return file_ref.start_time

    def sort_file_ref_list(self, file_refs: List[FileRef]):
        file_refs.sort(key=self._start_time)
