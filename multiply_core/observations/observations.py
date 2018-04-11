"""
Description
===========

This module defines the interface to MULTIPLY observations.
"""
from abc import ABCMeta, abstractmethod

import numpy as np
import scipy.sparse as sp
from typing import List

from multiply_core.util import FileRef, Reprojection

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


class Observations(metaclass=ABCMeta):
    """The interface to an Observations object. An observations object allows to access any EO data that comes from a
    file."""

    @abstractmethod
    def get_band_data(self, date_index: int, band_index: int) -> ObservationData:
        """
        This method returns
        :param date_index: The temporal index of the products represented by the Observations class. This index is used
        to identify the product.
        :param band_index: The index of the band within the product.
        :return: An ObservationData product according to the input.
        """

    @property
    @abstractmethod
    def bands_per_observation(self):
        """Returns an array containing the number of bands this observations object provides access to per date."""

