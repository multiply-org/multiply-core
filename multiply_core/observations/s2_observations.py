from gdal import Open
import _pickle as cPickle
import glob
import os
import numpy as np
import scipy.sparse as sp
import xml.etree.ElementTree as ET

from multiply_core.observations import Observations, ObservationData
from multiply_core.util import FileRef, Reprojection
from typing import List, Tuple

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

EMULATOR_BAND_MAP = [2, 3, 4, 5, 6, 7, 8, 9, 12, 13]


def parse_xml(filename: str) -> Tuple[float, float, float, float]:
    """Parses the XML metadata file to extract view/incidence
    angles. The file has grids and all sorts of stuff, but
    here we just average everything, and you get
    1. SZA
    2. SAA
    3. VZA
    4. VAA.
    """
    with open(filename, 'r') as f:
        tree = ET.parse(filename)
        root = tree.getroot()

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
    return cPickle.load(open(emulator_file, 'rb'))


#todo enable this to work with s2 data in safe format
class S2Observations(Observations):

    def __init__(self, file_refs: List[FileRef], reprojection: Reprojection, emulator_folder: str,
                 required_band_names: List[str]):
        self._file_refs = file_refs
        self._reprojection = reprojection
        self._required_band_names = required_band_names
        self._meta_data_infos = []
        self._band_emulators = []
        self._bands_per_observation = []
        for file_ref in self._file_refs:
            meta_data_file = os.path.join(file_ref.url, "metadata.xml")
            sza, saa, vza, vaa = parse_xml(meta_data_file)
            self._meta_data_infos.append(dict(zip(["sza", "saa", "vza", "vaa"], [sza, saa, vza, vaa])))
            self._band_emulators.append(_prepare_band_emulators(emulator_folder, sza, saa, vza, vaa))
            self._bands_per_observation.append(len(self._required_band_names))

    def get_band_data(self, date_index: int, band_index: int) -> ObservationData:
        band_name = self._required_band_names[band_index]
        data_set_base_url = self._file_refs[date_index].url
        data_set_url = '{}/{}'.format(data_set_base_url, band_name)
        data_set = Open(data_set_url)
        reprojected_data_set = self._reprojection.reproject(data_set)
        reprojected_data = reprojected_data_set.ReadAsArray()
        mask = reprojected_data > 0
        reprojected_data = np.where(mask, reprojected_data / 10000., 0)

        uncertainty = _get_uncertainty(reprojected_data, mask)
        band_emulator = self._get_band_emulator(date_index, band_index)

        observation_data = ObservationData(observations=reprojected_data, uncertainty=uncertainty, mask=mask,
                                           metadata=self._meta_data_infos[date_index], emulator=band_emulator)
        return observation_data

    def _get_band_emulator(self, date_index: int, band_index: int):
        date_band_emulators = self._band_emulators[date_index]
        if date_band_emulators is not None:
            return date_band_emulators["S2A_MSI_{:02d}".format(EMULATOR_BAND_MAP[band_index])]
        return None

    @property
    def bands_per_observation(self):
        return self._bands_per_observation
