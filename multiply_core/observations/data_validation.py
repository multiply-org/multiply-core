"""
Description
===========

This module contains MULTIPLY Data Checkers and default implementations. The purpose of these is to define whether
a file is of a given type or not.
"""

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

from abc import ABCMeta, abstractmethod
from datetime import datetime
from multiply_core.util import get_time_from_string
from multiply_core.variables import get_registered_variables
from shapely.geometry import Polygon
from typing import List, Optional
import glob
import re
import os

DATA_VALIDATORS = {}


class DataTypeConstants(object):
    ASTER = 'ASTER'
    AWS_S2_L1C = 'AWS_S2_L1C'
    AWS_S2_L2 = 'AWS_S2_L2'
    CAMS = 'CAMS'
    CAMS_TIFF = 'CAMS_TIFF'
    MODIS_MCD_43 = 'MCD43A1.006'
    MODIS_MCD_15_A2 = 'MCD15A2H.006'
    S1_SLC = 'S1_SLC'
    S1_SPECKLED = 'S1_Speckled'
    S2A_EMULATOR = 'ISO_MSI_A_EMU'
    S2B_EMULATOR = 'ISO_MSI_B_EMU'
    S2_L1C = 'S2_L1C'
    S2_L2 = 'S2_L2'
    S3_L1_OLCI_RR = 'S3_L1_OLCI_RR'  # todo add data validator and metadata extractor
    S3_L1_OLCI_FR = 'S3_L1_OLCI_FR'  # todo add data validator and metadata extractor
    WV_EMULATOR = 'WV_EMU'


INPUT_TYPES = {DataTypeConstants.S2_L1C: {'name': "Sentinel-2 MSI L1C", "timeRange": ["06-23-2015", '']}}


def _get_end_of_path(path: str):
    path = path.replace('\\', '/')
    if path.endswith('/'):
        return path.split('/')[-2]
    return path.split('/')[-1]


class DataValidator(metaclass=ABCMeta):

    @abstractmethod
    def name(self) -> str:
        """The name of the data type supported by this checker."""

    @abstractmethod
    def is_valid(self, path: str) -> bool:
        """Whether the data at the given path is a valid data product for the type."""

    @abstractmethod
    def get_relative_path(self, path: str) -> str:
        """
        :param path: Path to a file.
        :return: The part of the path which is relevant for a product to be identified as product of this type.
        """

    @abstractmethod
    def get_file_pattern(self) -> str:
        """
        :return: the pattern used by the validator
        """

    @abstractmethod
    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]) \
            -> bool:
        """
        Returns true if the path is valid in the sense that the data intersects with the polygon and that it lies
        between the start time and the end time.
        :param path:
        :param roi:
        :param start_time:
        :param end_time:
        :return:
        """

    @abstractmethod
    def differs_by_name(cls) -> bool:
        """
        :return: True, if different items of this type will always have different names
        """


class S1SlcValidator(DataValidator):

    def __init__(self):
        self._S1_PATTERN = \
            '(S1A|S1B)_(IW|EW|WV|(S[1-9]{1}))_SLC__1([A-Z]{3})_([0-9]{8}T[0-9]{6})_([0-9]{8}T[0-9]{6})_.*.(SAFE)?'
        self._S1_MATCHER = re.compile(self._S1_PATTERN)
        self.TIME_PATTERN = '([0-9]{8}T[0-9]{6})'
        self.TIME_MATCHER = re.compile(self.TIME_PATTERN)

    def name(self) -> str:
        return DataTypeConstants.S1_SLC

    def is_valid(self, path: str) -> bool:
        end_of_path = _get_end_of_path(path)
        return self._S1_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return self._S1_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime],
                     end_time: Optional[datetime]) -> bool:
        if not self.is_valid(path):
            return False
        end_of_path = _get_end_of_path(path)
        date_part = ''
        for path_part in end_of_path.split('_'):
            if self.TIME_MATCHER.match(path_part) is not None:
                date_part = path_part
                break
        if date_part == '':
            return False
        try:
            time = get_time_from_string(date_part)
        except ValueError:
            return False
        if time is None:
            return False
        return start_time <= time <= end_time

    def differs_by_name(cls) -> bool:
        return False


class S1SpeckledValidator(DataValidator):

    def __init__(self):
        self._S1_SPECKLED_PATTERN = '(S1A|S1B)_(IW|EW|WV|(S[1-9]{1}))_SLC__1([A-Z]{3})_' \
                                    '([0-9]{8}T[0-9]{6})_([0-9]{8}T[0-9]{6})_.*._GC_RC_No_Su_Co_speckle.nc'
        self._S1_SPECKLED_MATCHER = re.compile(self._S1_SPECKLED_PATTERN)
        self.TIME_PATTERN = '([0-9]{8}T[0-9]{6})'
        self.TIME_MATCHER = re.compile(self.TIME_PATTERN)

    def name(self) -> str:
        return DataTypeConstants.S1_SPECKLED

    def is_valid(self, path: str) -> bool:
        end_of_path = _get_end_of_path(path)
        return self._S1_SPECKLED_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return self._S1_SPECKLED_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime],
                     end_time: Optional[datetime]) -> bool:
        if not self.is_valid(path):
            return False
        end_of_path = _get_end_of_path(path)
        date_part = ''
        for path_part in end_of_path.split('_'):
            if self.TIME_MATCHER.match(path_part) is not None:
                date_part = path_part
                break
        if date_part == '':
            return False
        try:
            time = get_time_from_string(date_part)
        except ValueError:
            return False
        if time is None:
            return False
        return start_time <= time <= end_time

    def differs_by_name(cls) -> bool:
        return False


class S2L1CValidator(DataValidator):

    def __init__(self):
        self.S2_PATTERN = '(S2A|S2B|S2_)_(([A-Z|0-9]{4})_[A-Z|0-9|_]{4})?([A-Z|0-9|_]{6})_(([A-Z|0-9|_]{4})_)?([0-9]{8}T[0-9]{6})_.*.(SAFE)?'
        self.S2_MATCHER = re.compile(self.S2_PATTERN)
        self.TIME_PATTERN = '([0-9]{8}T[0-9]{6})'
        self.TIME_MATCHER = re.compile(self.TIME_PATTERN)
        self._manifest_file_name = 'MTD_MSIL1C.xml'
        self._expected_files = [['B01_sur.tif', 'B01_sur.tiff'], ['B02_sur.tif', 'B02_sur.tiff'],
                                ['B03_sur.tif', 'B03_sur.tiff'], ['B04_sur.tif', 'B04_sur.tiff'],
                                ['B05_sur.tif', 'B05_sur.tiff'], ['B06_sur.tif', 'B06_sur.tiff'],
                                ['B07_sur.tif', 'B07_sur.tiff'], ['B08_sur.tif', 'B08_sur.tiff'],
                                ['B8A_sur.tif', 'B8A_sur.tiff'], ['B09_sur.tif', 'B09_sur.tiff'],
                                ['B10_sur.tif', 'B10_sur.tiff'], ['B11_sur.tif', 'B11_sur.tiff'],
                                ['B12_sur.tif', 'B12_sur.tiff'], ['metadata.xml']]

    def name(self) -> str:
        return DataTypeConstants.S2_L1C

    def is_valid(self, path: str) -> bool:
        end_of_path = _get_end_of_path(path)
        if not (self.S2_MATCHER.match(end_of_path) is not None and
                os.path.exists('{}/{}'.format(path, self._manifest_file_name))):
            return False
        for files in self._expected_files:
            for file in files:
                if len(glob.glob(f'{path}/*{file}')) > 0:
                    return False
        return True

    def get_relative_path(self, path: str) -> str:
        dir_name = self.S2_MATCHER.search(path)
        if dir_name is None:
            return ''
        startPos, endPos = dir_name.regs[0]
        return path[startPos:endPos]

    def get_file_pattern(self) -> str:
        return self.S2_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime],
                     end_time: Optional[datetime]) -> bool:
        if not self.is_valid(path):
            return False
        end_of_path = _get_end_of_path(path)
        date_part = ''
        for path_part in end_of_path.split('_'):
            if self.TIME_MATCHER.match(path_part) is not None:
                date_part = path_part
                break
        if date_part == '':
            return False
        try:
            time = get_time_from_string(date_part)
        except ValueError:
            return False
        if time is None:
            return False
        return start_time <= time <= end_time

    def differs_by_name(cls) -> bool:
        return False


class S2L2Validator(DataValidator):

    def __init__(self):
        self.S2_PATTERN = '(S2A|S2B|S2_)_(([A-Z|0-9]{4})_[A-Z|0-9|_]{4})?([A-Z|0-9|_]{6})_(([A-Z|0-9|_]{4})_)?([0-9]{8}T[0-9]{6})_.*.(SAFE)?-ac'
        self.S2_MATCHER = re.compile(self.S2_PATTERN)
        self.TIME_PATTERN = '([0-9]{8}T[0-9]{6})'
        self.TIME_MATCHER = re.compile(self.TIME_PATTERN)
        self._manifest_file_name = 'MTD_TL.xml'

    def name(self) -> str:
        return DataTypeConstants.S2_L2

    def is_valid(self, path: str) -> bool:
        end_of_path = _get_end_of_path(path)
        return self.S2_MATCHER.match(end_of_path) is not None and \
               os.path.exists('{}/{}'.format(path, self._manifest_file_name))

    def get_relative_path(self, path: str) -> str:
        dir_name = self.S2_MATCHER.search(path)
        if dir_name is None:
            return ''
        startPos, endPos = dir_name.regs[0]
        return path[startPos:endPos]

    def get_file_pattern(self) -> str:
        return self.S2_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime],
                     end_time: Optional[datetime]) -> bool:
        if not self.is_valid(path):
            return False
        end_of_path = _get_end_of_path(path)
        date_part = ''
        for path_part in end_of_path.split('_'):
            if self.TIME_MATCHER.match(path_part) is not None:
                date_part = path_part
                break
        if date_part == '':
            return False
        try:
            time = get_time_from_string(date_part)
        except ValueError:
            return False
        if time is None:
            return False
        return start_time <= time <= end_time

    def differs_by_name(cls) -> bool:
        return False


class AWSS2L1Validator(DataValidator):

    def __init__(self):
        self.BASIC_AWS_S2_PATTERN = '/[0-9]{1,2}/[A-Z]/[A-Z]{2}/20[0-9][0-9]/[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}'
        self.BASIC_AWS_S2_MATCHER = re.compile(self.BASIC_AWS_S2_PATTERN)
        self.AWS_S2_PATTERN = '.*/[0-9]{1,2}/[A-Z]/[A-Z]{2}/20[0-9][0-9]/[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}'
        self.AWS_S2_MATCHER = re.compile(self.AWS_S2_PATTERN)
        self._expected_files = ['B01.jp2', 'B02.jp2', 'B03.jp2', 'B04.jp2', 'B05.jp2', 'B06.jp2', 'B07.jp2', 'B08.jp2',
                                'B8A.jp2', 'B09.jp2', 'B10.jp2', 'B11.jp2', 'B12.jp2', 'metadata.xml']

    def name(self) -> str:
        return DataTypeConstants.AWS_S2_L1C

    def is_valid(self, path: str) -> bool:
        if not self._matches_pattern(path):
            return False
        for file in self._expected_files:
            if not os.path.exists(path + '/' + file):
                return False
        return True

    def _matches_pattern(self, path: str) -> bool:
        return self.AWS_S2_MATCHER.match(path) is not None

    def get_relative_path(self, path: str) -> str:
        dirs_names = self.BASIC_AWS_S2_MATCHER.search(path)
        if dirs_names is None:
            return ''
        start_pos, end_pos = dirs_names.regs[0]
        return path[start_pos + 1:end_pos]

    def get_file_pattern(self) -> str:
        return self.BASIC_AWS_S2_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        raise NotImplementedError()

    def differs_by_name(cls) -> bool:
        return False


class AWSS2L2Validator(DataValidator):

    def __init__(self):
        self._expected_files = [['B01_sur.tif', 'B01_sur.tiff'], ['B02_sur.tif', 'B02_sur.tiff'],
                                ['B03_sur.tif', 'B03_sur.tiff'], ['B04_sur.tif', 'B04_sur.tiff'],
                                ['B05_sur.tif', 'B05_sur.tiff'], ['B06_sur.tif', 'B06_sur.tiff'],
                                ['B07_sur.tif', 'B07_sur.tiff'], ['B08_sur.tif', 'B08_sur.tiff'],
                                ['B8A_sur.tif', 'B8A_sur.tiff'], ['B09_sur.tif', 'B09_sur.tiff'],
                                ['B10_sur.tif', 'B10_sur.tiff'], ['B11_sur.tif', 'B11_sur.tiff'],
                                ['B12_sur.tif', 'B12_sur.tiff'], ['metadata.xml']]

    def name(self) -> str:
        return DataTypeConstants.AWS_S2_L2

    def is_valid(self, path: str) -> bool:
        for files in self._expected_files:
            missing_file = None
            for file in files:
                missing_file = path + '/' + file
                if os.path.exists(path + '/' + file):
                    missing_file = None
                    break
            if missing_file is not None:
                return False
        return True

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return ''

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        return True  # we are not checking paths here

    def differs_by_name(cls) -> bool:
        return False


class ModisMCD43Validator(DataValidator):

    def __init__(self):
        self.MCD_43_PATTERN = 'MCD43A1.A20[0-9][0-9][0-3][0-9][0-9].h[0-3][0-9]v[0-1][0-9].006.*.hdf'
        self.MCD_43_MATCHER = re.compile(self.MCD_43_PATTERN)

    def name(self) -> str:
        return DataTypeConstants.MODIS_MCD_43

    def is_valid(self, path: str) -> bool:
        end_of_path = _get_end_of_path(path)
        return self.MCD_43_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return self.MCD_43_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        # todo implement
        raise NotImplementedError()

    def differs_by_name(cls) -> bool:
        return False


class ModisMCD15A2HValidator(DataValidator):

    def __init__(self):
        self.MCD_15_PATTERN = 'MCD15A2H.A20[0-9][0-9][0-3][0-9][0-9].h[0-3][0-9]v[0-1][0-9].006.*.hdf'
        self.MCD_15_MATCHER = re.compile(self.MCD_15_PATTERN)

    def name(self) -> str:
        return DataTypeConstants.MODIS_MCD_15_A2

    def is_valid(self, path: str) -> bool:
        end_of_path = _get_end_of_path(path)
        return self.MCD_15_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return self.MCD_15_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        # todo implement
        raise NotImplementedError()

    def differs_by_name(cls) -> bool:
        return False


class CamsTiffValidator(DataValidator):

    def __init__(self):
        self.BASIC_CAMS_NAME_PATTERN = '20[0-9][0-9]_[0-1][0-9]_[0-3][0-9]'
        self.BASIC_CAMS_NAME_MATCHER = re.compile(self.BASIC_CAMS_NAME_PATTERN)
        self.CAMS_NAME_PATTERN = '.*20[0-9][0-9]_[0-1][0-9]_[0-3][0-9]'
        self.CAMS_NAME_MATCHER = re.compile(self.CAMS_NAME_PATTERN)

        self._expected_file_patterns = ['20[0-9][0-9]_[0-1][0-9]_[0-3][0-9]_aod550.tif',
                                        '20[0-9][0-9]_[0-1][0-9]_[0-3][0-9]_bcaod550.tif',
                                        '20[0-9][0-9]_[0-1][0-9]_[0-3][0-9]_duaod550.tif',
                                        '20[0-9][0-9]_[0-1][0-9]_[0-3][0-9]_gtco3.tif',
                                        '20[0-9][0-9]_[0-1][0-9]_[0-3][0-9]_omaod550.tif',
                                        '20[0-9][0-9]_[0-1][0-9]_[0-3][0-9]_suaod550.tif',
                                        '20[0-9][0-9]_[0-1][0-9]_[0-3][0-9]_tcwv.tif']
        self._expected_file_matchers = [re.compile(pattern) for pattern in self._expected_file_patterns]

    def name(self) -> str:
        return DataTypeConstants.CAMS_TIFF

    def is_valid(self, path: str) -> bool:
        if not os.path.exists(path) or not os.path.isdir(path):
            return False
        if self.CAMS_NAME_MATCHER.search(path) is None:
            return False
        files_in_path = os.listdir(path)
        for file in files_in_path:
            found = False
            for matcher in self._expected_file_matchers:
                if matcher.match(file) is not None:
                    found = True
                    break
            if not found:
                return False
        return True

    def get_relative_path(self, path: str) -> str:
        start_pos, end_pos = self.BASIC_CAMS_NAME_MATCHER.search(path).regs[0]
        return path[start_pos:end_pos]

    def get_file_pattern(self) -> str:
        return self.BASIC_CAMS_NAME_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        if self.CAMS_NAME_MATCHER.search(path) is not None:
            end_of_path = _get_end_of_path(path)
            # if path.endswith('/'):
            #     end_of_path = path.split('/')[-2]
            # else:
            #     end_of_path = path.split('/')[-1]
            cams_time = datetime.strptime(end_of_path, '%Y_%m_%d')
            return start_time <= cams_time <= end_time
        return False

    def differs_by_name(cls) -> bool:
        return False


class CamsValidator(DataValidator):

    def __init__(self):
        self.CAMS_NAME_PATTERN = '20[0-9][0-9]-[0-1][0-9]-[0-3][0-9].nc'
        self.CAMS_NAME_MATCHER = re.compile(self.CAMS_NAME_PATTERN)

    def name(self) -> str:
        return DataTypeConstants.CAMS

    def is_valid(self, path: str) -> bool:
        end_of_path = _get_end_of_path(path)
        return self.CAMS_NAME_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return self.CAMS_NAME_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        if self.is_valid(path):
            end_of_path = _get_end_of_path(path)
            cams_time = datetime.strptime(end_of_path[:-3], '%Y-%m-%d')
            return start_time <= cams_time <= end_time
        return False

    def differs_by_name(cls) -> bool:
        return False


class S2AEmulatorValidator(DataValidator):

    def __init__(self):
        self.EMULATOR_NAME_PATTERN = 'isotropic_MSI_emulators_(?:correction|optimization)_x[a|b|c]p_S2A.pkl'
        self.EMULATOR_NAME_MATCHER = re.compile(self.EMULATOR_NAME_PATTERN)

    def name(self) -> str:
        return DataTypeConstants.S2A_EMULATOR

    def is_valid(self, path: str) -> bool:
        end_of_path = _get_end_of_path(path)
        return self.EMULATOR_NAME_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self):
        return self.EMULATOR_NAME_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        return self.is_valid(path)

    def differs_by_name(cls) -> bool:
        return True


class S2BEmulatorValidator(DataValidator):

    def __init__(self):
        self.EMULATOR_NAME_PATTERN = 'isotropic_MSI_emulators_(?:correction|optimization)_x[a|b|c]p_S2B.pkl'
        self.EMULATOR_NAME_MATCHER = re.compile(self.EMULATOR_NAME_PATTERN)

    def name(self) -> str:
        return DataTypeConstants.S2B_EMULATOR

    def is_valid(self, path: str) -> bool:
        end_of_path = _get_end_of_path(path)
        return self.EMULATOR_NAME_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return self.EMULATOR_NAME_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        return self.is_valid(path)

    def differs_by_name(cls) -> bool:
        return True


class WVEmulatorValidator(DataValidator):

    def __init__(self):
        self.WV_NAME_PATTERN = 'wv_MSI_retrieval_S2A.pkl'
        self.WV_NAME_MATCHER = re.compile(self.WV_NAME_PATTERN)

    def name(self) -> str:
        return DataTypeConstants.WV_EMULATOR

    def is_valid(self, path: str) -> bool:
        end_of_path = _get_end_of_path(path)
        return self.WV_NAME_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return self.WV_NAME_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        return self.is_valid(path)

    def differs_by_name(cls) -> bool:
        return True


class AsterValidator(DataValidator):

    def __init__(self):
        self.ASTER_NAME_PATTERN = 'ASTGTM2_[N|S][0-8][0-9][E|W][0|1][0-9][0-9]_dem.tif'
        self.ASTER_NAME_MATCHER = re.compile(self.ASTER_NAME_PATTERN)

    def name(self) -> str:
        return DataTypeConstants.ASTER

    def is_valid(self, path: str) -> bool:
        end_of_path = _get_end_of_path(path)
        return self.ASTER_NAME_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self):
        return self.ASTER_NAME_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        if not self.is_valid(path):
            return False
        min_lon, min_lat, max_lon, max_lat = roi.bounds
        end_of_path = _get_end_of_path(path)
        path_lat_id = end_of_path[8:9]
        path_lat = float(end_of_path[9:11])
        if path_lat_id == 'S':
            path_lat *= -1
        path_lon_id = end_of_path[11:12]
        path_lon = float(end_of_path[12:15])
        if path_lon_id == 'W':
            path_lon *= -1
        if min_lon > path_lon + 1 or max_lon < path_lon or min_lat > path_lat + 1 or max_lat < path_lat:
            return False
        return True

    def differs_by_name(cls) -> bool:
        return False


class VariableValidator(DataValidator):

    def __init__(self, variable_name: str):
        self.variable_name = variable_name
        self.VARIABLE_NAME_PATTERN = '{}_(A)?20[0-9][0-9]([0-3][0-9][0-9]|[0-1][0-9][0-1][0-9]|' \
                                     '[0-1][0-9][0-1][0-9]_20[0-9][0-9][0-1][0-9][0-1][0-9]).tif'.format(variable_name)
        self.VARIABLE_NAME_MATCHER = re.compile(self.VARIABLE_NAME_PATTERN)

    def name(self) -> str:
        return self.variable_name

    def is_valid(self, path: str) -> bool:
        end_of_path = _get_end_of_path(path)
        return self.VARIABLE_NAME_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self):
        return self.VARIABLE_NAME_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        if not self.is_valid(path):
            return False
        end_of_path = _get_end_of_path(path).replace('.tif', '')
        date_part_1 = end_of_path.split('_')[-2]
        date_part_2 = end_of_path.split('_')[-1]
        try:
            date_start_time = datetime.strptime(date_part_1, "%Y%m%d")
            date_end_time = datetime.strptime(date_part_2, "%Y%m%d")
            return start_time <= date_end_time and date_start_time <= end_time
        except ValueError:
            try:
                time = datetime.strptime(date_part_2, "A%Y%j")
                return start_time <= time <= end_time
            except ValueError:
                try:
                    time = datetime.strptime(date_part_2, "%Y%m%d")
                    return start_time <= time <= end_time
                except ValueError:
                    return False

    def differs_by_name(cls) -> bool:
        return False


def _set_up_validators():
    add_validator(AWSS2L1Validator())
    add_validator(AWSS2L2Validator())
    add_validator(ModisMCD43Validator())
    add_validator(ModisMCD15A2HValidator())
    add_validator(CamsValidator())
    add_validator(CamsTiffValidator())
    add_validator(S2AEmulatorValidator())
    add_validator(S2BEmulatorValidator())
    add_validator(WVEmulatorValidator())
    add_validator(AsterValidator())
    add_validator(S2L1CValidator())
    add_validator(S2L2Validator())
    add_validator(S1SlcValidator())
    add_validator(S1SpeckledValidator())
    variables = get_registered_variables()
    for variable in variables:
        add_validator(VariableValidator(variable.short_name))


def add_validator(validator: DataValidator):
    if validator.name() not in DATA_VALIDATORS:
        DATA_VALIDATORS[validator.name()] = validator


def get_valid_type(path: str) -> str:
    _set_up_validators()
    for validator in DATA_VALIDATORS.values():
        if validator.is_valid(path):
            return validator.name()
    return ''


def is_valid(path: str, data_type: str) -> bool:
    _set_up_validators()
    if data_type in DATA_VALIDATORS:
        return DATA_VALIDATORS[data_type].is_valid(path)
    return False


def get_relative_path(path: str, data_type: str):
    _set_up_validators()
    if data_type in DATA_VALIDATORS:
        return DATA_VALIDATORS[data_type].get_relative_path(path)
    return ''


def get_file_pattern(data_type: str) -> str:
    _set_up_validators()
    if data_type in DATA_VALIDATORS:
        return DATA_VALIDATORS[data_type].get_file_pattern()
    return ''


def is_valid_for(path: str, data_type: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]) \
        -> bool:
    _set_up_validators()
    if data_type in DATA_VALIDATORS:
        return DATA_VALIDATORS[data_type].is_valid_for(path, roi, start_time, end_time)
    return False


def get_valid_types() -> List[str]:
    """Returns the names of all data types which can be valid."""
    _set_up_validators()
    valid_types = []
    for validator in DATA_VALIDATORS.values():
        valid_types.append(validator.name())
    return valid_types


def get_data_type_path(data_type: str, path: str) -> str:
    """
    :param data_type: The data type of
    :param path: Path to a file.
    :return: The part of the path which is relevant for a product to be identified as product of this type. None,
    if data type is not found.
    """
    _set_up_validators()
    if data_type in DATA_VALIDATORS:
        return DATA_VALIDATORS[data_type].get_relative_path(path)
    return ''


def differs_by_name(data_type: str) -> bool:
    _set_up_validators()
    if data_type in DATA_VALIDATORS:
        return DATA_VALIDATORS[data_type].differs_by_name()
    return False
