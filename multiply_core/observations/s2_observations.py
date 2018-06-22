from gdal import Open
import _pickle as cPickle
import glob
import os
import numpy as np
import scipy.sparse as sp
import xml.etree.ElementTree as eT

from multiply_core.observations import ProductObservations, ObservationData, ProductObservationsCreator, data_validation
from multiply_core.util import FileRef, Reprojection
from typing import Tuple

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

# todo exchange this
EMULATOR_BAND_MAP = [2, 3, 4, 5, 6, 7, 8, 9, 12, 13]
BAND_NAMES = ['B02_sur.tif', 'B03_sur.tif', 'B04_sur.tif', 'B05_sur.tif', 'B06_sur.tif', 'B07_sur.tif',
              'B08_sur.tif', 'B8A_sur.tif', 'B09_sur.tif', 'B12_sur.tif']


def _get_xml_root(xml_file_name: str):
    tree = eT.parse(xml_file_name)
    return tree.getroot()


def extract_angles_from_metadata_file(filename: str) -> Tuple[float, float, float, float]:
    """Parses the XML metadata file to extract view/incidence
    angles. The file has grids and all sorts of stuff, but
    here we just average everything, and you get
    1. SZA
    2. SAA
    3. VZA
    4. VAA.
    """
    root = _get_xml_root(filename)
    sza = 0.
    saa = 0.
    vza = []
    vaa = []
    for child in root:
        for x in child.findall("Tile_Angles"):
            for y in x.find("Mean_Sun_Angle"):
                if y.tag == "ZENITH_ANGLE":
                    sza = float(y.text)
                elif y.tag == "AZIMUTH_ANGLE":
                    saa = float(y.text)
            for s in x.find("Mean_Viewing_Incidence_Angle_List"):
                for r in s:
                    if r.tag == "ZENITH_ANGLE":
                        vza.append(float(r.text))
                    elif r.tag == "AZIMUTH_ANGLE":
                            vaa.append(float(r.text))

    return sza, saa, float(np.mean(vza)), float(np.mean(vaa))


def extract_tile_id(filename: str) -> str:
    """Parses the XML metadata file to extract the tile id."""
    root = _get_xml_root(filename)
    for child in root:
        for x in child.findall("TILE_ID"):
            return x.text


def _get_uncertainty(rho_surface: np.array, mask: np.array) -> sp.lil_matrix:
    r_mat = rho_surface * 0.05
    r_mat[np.logical_not(mask)] = 0.
    N = mask.ravel().shape[0]
    r_mat_sp = sp.lil_matrix((N, N))
    r_mat_sp.setdiag(1. / (r_mat.ravel()) ** 2)
    return r_mat_sp.tocsr()


def _prepare_band_emulators(emulator_folder: str, sza: float, saa: float, vza: float, vaa: float):
    emulator_files = glob.glob(os.path.join(emulator_folder, "*.pkl"))
    if len(emulator_files) == 0:
        return None
    emulator_files.sort()
    raa = vaa - saa
    vzas = np.array([float(s.split("_")[-3])
                     for s in emulator_files])
    szas = np.array([float(s.split("_")[-2])
                     for s in emulator_files])
    raas = np.array([float(s.split("_")[-1].split(".")[0])
                     for s in emulator_files])
    e1 = szas == szas[np.argmin(np.abs(szas - sza))]
    e2 = vzas == vzas[np.argmin(np.abs(vzas - vza))]
    e3 = raas == raas[np.argmin(np.abs(raas - raa))]
    iloc = np.where(e1 * e2 * e3)[0][0]
    emulator_file = emulator_files[iloc]
    return cPickle.load(open(emulator_file, 'rb'), encoding='latin1')


class S2Observations(ProductObservations):

    def __init__(self, file_ref: FileRef, reprojection: Reprojection, emulator_folder: str):
        self._file_ref = file_ref
        self._reprojection = reprojection
        # self._bands_per_observation = []
        meta_data_file = os.path.join(file_ref.url, "metadata.xml")
        sza, saa, vza, vaa = extract_angles_from_metadata_file(meta_data_file)
        self._meta_data_infos = dict(zip(["sza", "saa", "vza", "vaa"], [sza, saa, vza, vaa]))
        self._band_emulator = _prepare_band_emulators(emulator_folder, sza, saa, vza, vaa)
        self._bands_per_observation = len(BAND_NAMES)

    def _get_data_set_url(self, band_index: int) -> str:
        band_name = BAND_NAMES[band_index]
        data_set_base_url = self._file_ref.url
        data_set_url = '{}/{}'.format(data_set_base_url, band_name)
        if not os.path.exists(data_set_url):
            data_set_url = '{}/{}f'.format(data_set_base_url, band_name)
        return data_set_url

    def get_band_data(self, band_index: int) -> ObservationData:
        data_set_url = self._get_data_set_url(band_index)
        data_set = Open(data_set_url)
        reprojected_data_set = self._reprojection.reproject(data_set)
        reprojected_data = reprojected_data_set.ReadAsArray()
        mask = reprojected_data > 0
        reprojected_data = np.where(mask, reprojected_data / 10000., 0)

        uncertainty = _get_uncertainty(reprojected_data, mask)
        band_emulator = self._get_band_emulator(band_index)

        observation_data = ObservationData(observations=reprojected_data, uncertainty=uncertainty, mask=mask,
                                           metadata=self._meta_data_infos, emulator=band_emulator)
        return observation_data

    def _get_band_emulator(self, band_index: int):
        date_band_emulators = self._band_emulator
        if date_band_emulators is not None:
            s2_band = bytes("S2A_MSI_{:02d}".format(EMULATOR_BAND_MAP[band_index]), 'latin1')
            return date_band_emulators[s2_band]
        return None

    @property
    def bands_per_observation(self):
        return self._bands_per_observation


class S2ObservationsCreator(ProductObservationsCreator):

    @classmethod
    def can_read(cls, file_ref: FileRef) -> bool:
        return data_validation.AWSS2L2Validator().is_valid(file_ref.url)

    @classmethod
    def create_observations(cls, file_ref: FileRef, reprojection: Reprojection, emulator_folder: str) -> \
            ProductObservations:
        """
        Creates an Observations object for the given fileref object.
        :param file_ref: A reference to a file containing data.
        :param reprojection: A Reprojection object to reproject the data
        :param emulator_folder: A folder containing the emulators for the observations.
        :return: An Observations object that encapsulates the data.
        """
        return S2Observations(file_ref, reprojection, emulator_folder)
