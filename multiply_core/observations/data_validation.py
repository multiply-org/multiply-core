"""
Description
===========

This module contains MULTIPLY Data Checkers and default implementations. The purpose of these is to define whether
a file is of a given type or not.
"""


__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


from abc import ABCMeta, abstractmethod
from shapely.geometry import Polygon
from typing import List, Optional
from datetime import datetime
import re
import os

VALIDATORS = []


class DataTypeConstants(object):
    AWS_S2_L1C = 'AWS_S2_L1C'
    AWS_S2_L2 = 'AWS_S2_L2'
    MODIS_MCD_43 = 'MCD43A1.006'
    CAMS = 'CAMS'
    CAMS_TIFF = 'CAMS_TIFF'
    S2A_EMULATOR = 'ISO_MSI_A_EMU'
    S2B_EMULATOR = 'ISO_MSI_B_EMU'
    WV_EMULATOR = 'WV_EMU'
    ASTER = 'ASTER'


class DataValidator(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """The name of the data type supported by this checker."""

    @abstractmethod
    def is_valid(self, path: str) -> bool:
        """Whether the data at the given path is a valid data product for the type."""

    @abstractmethod
    def get_relative_path(self, path:str) -> str:
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


class AWSS2L1Validator(DataValidator):

    def __init__(self):
        self.BASIC_AWS_S2_PATTERN = '/[0-9]{1,2}/[A-Z]/[A-Z]{2}/20[0-9][0-9]/[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}'
        self.BASIC_AWS_S2_MATCHER = re.compile(self.BASIC_AWS_S2_PATTERN)
        self.AWS_S2_PATTERN = '.*/[0-9]{1,2}/[A-Z]/[A-Z]{2}/20[0-9][0-9]/[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}'
        self.AWS_S2_MATCHER = re.compile(self.AWS_S2_PATTERN)
        self._expected_files = ['B01.jp2', 'B02.jp2', 'B03.jp2', 'B04.jp2', 'B05.jp2', 'B06.jp2', 'B07.jp2', 'B08.jp2',
                                'B8A.jp2', 'B09.jp2', 'B10.jp2', 'B11.jp2', 'B12.jp2', 'metadata.xml']

    @classmethod
    def name(cls) -> str:
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

    def get_relative_path(self, path:str) -> str:
        start_pos, end_pos = self.BASIC_AWS_S2_MATCHER.search(path).regs[0]
        return path[start_pos + 1:end_pos]

    def get_file_pattern(self) -> str:
        return self.BASIC_AWS_S2_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        raise NotImplementedError()


class AWSS2L2Validator(DataValidator):

    def __init__(self):
        self._expected_files = [['B01_sur.tif', 'B01_sur.tiff'], ['B02_sur.tif', 'B02_sur.tiff'],
                                ['B03_sur.tif', 'B03_sur.tiff'], ['B04_sur.tif', 'B04_sur.tiff'],
                                ['B05_sur.tif', 'B05_sur.tiff'], ['B06_sur.tif', 'B06_sur.tiff'],
                                ['B07_sur.tif', 'B07_sur.tiff'], ['B08_sur.tif', 'B08_sur.tiff'],
                                ['B8A_sur.tif', 'B8A_sur.tiff'], ['B09_sur.tif', 'B09_sur.tiff'],
                                ['B10_sur.tif', 'B10_sur.tiff'], ['B11_sur.tif', 'B11_sur.tiff'],
                                ['B12_sur.tif', 'B12_sur.tiff'], ['metadata.xml']]

    @classmethod
    def name(cls) -> str:
        return DataTypeConstants.AWS_S2_L2

    def is_valid(self, path: str) -> bool:
        for files in self._expected_files:
            found = False
            for file in files:
                if os.path.exists(path + '/' + file):
                    found = True
                    break
            if not found:
                return False
        return True

    def get_relative_path(self, path:str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return ''

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        return True # we are not checking paths here


class ModisMCD43Validator(DataValidator):

    def __init__(self):
        self.MCD_43_PATTERN = 'MCD43A1.A20[0-9][0-9][0-3][0-9][0-9].h[0-3][0-9]v[0-1][0-9].006.*.hdf'
        self.MCD_43_MATCHER = re.compile(self.MCD_43_PATTERN)

    @classmethod
    def name(cls) -> str:
        return DataTypeConstants.MODIS_MCD_43

    def is_valid(self, path: str) -> bool:
        end_of_path = path.split('/')[-1]
        return self.MCD_43_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return self.MCD_43_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        # todo implement
        raise NotImplementedError()


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

    @classmethod
    def name(cls) -> str:
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
            if path.endswith('/'):
                end_of_path = path.split('/')[-2]
            else:
                end_of_path = path.split('/')[-1]
            cams_time = datetime.strptime(end_of_path, '%Y_%m_%d')
            return start_time <= cams_time <= end_time
        return False


class CamsValidator(DataValidator):

    def __init__(self):
        self.CAMS_NAME_PATTERN = '20[0-9][0-9]-[0-1][0-9]-[0-3][0-9].nc'
        self.CAMS_NAME_MATCHER = re.compile(self.CAMS_NAME_PATTERN)

    @classmethod
    def name(cls) -> str:
        return DataTypeConstants.CAMS

    def is_valid(self, path: str) -> bool:
        end_of_path = path.split('/')[-1]
        return self.CAMS_NAME_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return self.CAMS_NAME_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        if self.is_valid(path):
            end_of_path = path.split('/')[-1]
            cams_time = datetime.strptime(end_of_path[:-3], '%Y-%m-%d')
            return start_time <= cams_time <= end_time
        return False


class S2AEmulatorValidator(DataValidator):

    def __init__(self):
        self.EMULATOR_NAME_PATTERN = 'isotropic_MSI_emulators_(?:correction|optimization)_x[a|b|c]p_S2A.pkl'
        self.EMULATOR_NAME_MATCHER = re.compile(self.EMULATOR_NAME_PATTERN)

    @classmethod
    def name(cls) -> str:
        return DataTypeConstants.S2A_EMULATOR

    def is_valid(self, path: str) -> bool:
        end_of_path = path.split('/')[-1]
        return self.EMULATOR_NAME_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self):
        return self.EMULATOR_NAME_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        return self.is_valid(path)


class S2BEmulatorValidator(DataValidator):

    def __init__(self):
        self.EMULATOR_NAME_PATTERN = 'isotropic_MSI_emulators_(?:correction|optimization)_x[a|b|c]p_S2B.pkl'
        self.EMULATOR_NAME_MATCHER = re.compile(self.EMULATOR_NAME_PATTERN)

    @classmethod
    def name(cls) -> str:
        return DataTypeConstants.S2B_EMULATOR

    def is_valid(self, path: str) -> bool:
        end_of_path = path.split('/')[-1]
        return self.EMULATOR_NAME_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return self.EMULATOR_NAME_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        return self.is_valid(path)


class WVEmulatorValidator(DataValidator):

    def __init__(self):
        self.WV_NAME_PATTERN = 'wv_MSI_retrieval_S2A.pkl'
        self.WV_NAME_MATCHER = re.compile(self.WV_NAME_PATTERN)

    @classmethod
    def name(cls) -> str:
        return DataTypeConstants.WV_EMULATOR

    def is_valid(self, path: str) -> bool:
        end_of_path = path.split('/')[-1]
        return self.WV_NAME_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self) -> str:
        return self.WV_NAME_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        return self.is_valid(path)


class AsterValidator(DataValidator):

    def __init__(self):
        self.ASTER_NAME_PATTERN = 'ASTGTM2_[N|S][0-8][0-9][E|W][0|1][0-9][0-9]_dem.tif'
        self.ASTER_NAME_MATCHER = re.compile(self.ASTER_NAME_PATTERN)

    @classmethod
    def name(cls) -> str:
        return DataTypeConstants.ASTER

    def is_valid(self, path: str) -> bool:
        end_of_path = path.split('/')[-1]
        return self.ASTER_NAME_MATCHER.match(end_of_path) is not None

    def get_relative_path(self, path: str) -> str:
        return ''

    def get_file_pattern(self):
        return self.ASTER_NAME_PATTERN

    def is_valid_for(self, path: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]):
        if not self.is_valid(path):
            return False
        min_lon, min_lat, max_lon, max_lat = roi.bounds
        end_of_path = path.split('/')[-1]
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


# TODO replace this with framework
VALIDATORS.append(AWSS2L1Validator())
VALIDATORS.append(AWSS2L2Validator())
VALIDATORS.append(ModisMCD43Validator())
VALIDATORS.append(CamsValidator())
VALIDATORS.append(CamsTiffValidator())
VALIDATORS.append(S2AEmulatorValidator())
VALIDATORS.append(S2BEmulatorValidator())
VALIDATORS.append(WVEmulatorValidator())
VALIDATORS.append(AsterValidator())


def add_validator(validator: DataValidator):
    VALIDATORS.append(validator)


def get_valid_type(path: str) -> str:
    for validator in VALIDATORS:
        if validator.is_valid(path):
            return validator.name()
    return ''


def is_valid(path: str, type: str) -> bool:
    for validator in VALIDATORS:
        if validator.name() == type:
            return validator.is_valid(path)
    return False


def get_relative_path(path: str, type: str):
    for validator in VALIDATORS:
        if validator.name() == type:
            return validator.get_relative_path(path)
    return ''


def get_file_pattern(type: str) -> str:
    for validator in VALIDATORS:
        if validator.name() == type:
            return validator.get_file_pattern()
    return ''


def is_valid_for(path: str, type: str, roi: Polygon, start_time: Optional[datetime], end_time: Optional[datetime]) \
        -> bool:
    for validator in VALIDATORS:
        if validator.name() == type:
            return validator.is_valid_for(path, roi, start_time, end_time)
    return False


def get_valid_types() -> List[str]:
    """Returns the names of all data types which can be valid."""
    valid_types = []
    for validator in VALIDATORS:
        valid_types.append(validator.name())
    return valid_types


def get_data_type_path(data_type: str, path: str) -> str:
    """
    :param data_type: The data type of
    :param path: Path to a file.
    :return: The part of the path which is relevant for a product to be identified as product of this type. None,
    if data type is not found.
    """
    for validator in VALIDATORS:
        if validator.name() == data_type:
            return validator.get_relative_path(path)
    return ''
