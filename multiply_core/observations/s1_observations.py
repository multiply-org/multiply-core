import numpy as np
import scipy.sparse as sp

from multiply_core.observations import Observations, ObservationData
from multiply_core.util import FileRef, Reprojection
from typing import List

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

WRONG_VALUE = -999.0  # TODO tentative missing value

class S1Observations(Observations):

    @property
    def bands_per_observation(self):
        return 2

    def __init__(self, file_refs: List[FileRef], reprojection: Reprojection,
                 emulators: dict={'VV': 'SOmething', 'VH': 'Other'}):
        self._polarisations = ['VV', 'VH']
        self._file_refs = file_refs
        self._reprojection = reprojection
        self._emulators = emulators

    def get_band_data(self, date_index: int, band_index: int) -> ObservationData:
        data_set = self._file_refs[date_index]
        polarisation = self._polarisations[band_index]
        sigma_band_name = 'sigma0_{:s}'.format(polarisation)
        sigma_band = data_set.GetRasterBand(sigma_band_name)
        sigma = sigma_band.ReadAsArray()
        uncertainty = self._calculate_uncertainty(sigma)
        mask = self._get_mask(sigma)
        R_mat = uncertainty
        R_mat[np.logical_not(mask)] = 0.
        N = mask.ravel().shape[0]
        R_mat_sp = sp.lil_matrix((N, N))
        R_mat_sp.setdiag(1. / (R_mat.ravel()) ** 2)
        R_mat_sp = R_mat_sp.tocsr()

        theta_band = data_set.GetRasterBand("theta")
        theta = theta_band.ReadAsArray()
        metadata = {'incidence_angle': theta}

        emulator = self._emulators[polarisation]

        return ObservationData(observations=sigma, uncertainty=R_mat_sp, mask=mask,
                               metadata=metadata, emulator=emulator)

    def _calculate_uncertainty(self, backscatter: np.array):
        """
        Calculation of the uncertainty of Sentinel-1 input data

        Radiometric uncertainty of Sentinel-1 Sensors are within 1 and 0.5 dB

        Calculate Equivalent Number of Looks (ENL) of input dataset leads to
        uncertainty of scene caused by speckle-filtering/multi-looking
        :param backscatter: backscatter values
        :return:
        """

        # first approximation of uncertainty (1 dB)
        unc = backscatter * 0.05

        # need to find a good way to calculate ENL
        # self.ENL = (backscatter.mean()**2) / (backscatter.std()**2)

        return unc

    def _get_mask(self, backscatter):
        """
        Mask for selection of pixels

        Get a True/False array with the selected/unselected pixels
        :param backscatter:
        :return:
        """
        mask = np.ones_like(backscatter, dtype=np.bool)
        mask[backscatter == WRONG_VALUE] = False
        return mask