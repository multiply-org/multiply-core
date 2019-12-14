from abc import ABCMeta, abstractmethod
import gdal
import logging
import numpy as np
import os
from typing import List, Optional

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"


logger = logging.getLogger('Writer')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
logging_handler = logging.StreamHandler()
logging_handler.setLevel(logging.INFO)
logging_handler.setFormatter(formatter)
logger.addHandler(logging_handler)


class Writer(metaclass=ABCMeta):

    def __init__(self, file_names: List[str], geo_transform: tuple, projection: str, width: int, height: int,
                 num_bands: Optional[List[int]], data_types: Optional[List[str]]):
        self.init(file_names, geo_transform, projection, width, height, num_bands, data_types)

    @abstractmethod
    def init(self, file_names: List[str], geo_transform: tuple, projection: str, width: int, height: int,
             num_bands: Optional[List[int]] = None, data_types: Optional[List[str]] = None):
        pass

    @abstractmethod
    def write(self, data: List[np.array], width: Optional[int] = None, height: Optional[int] = None,
              offset_x: Optional[int] = 0, offset_y: Optional[int] = 0):
        pass

    @abstractmethod
    def close(self):
        pass


class GeoTiffWriter(Writer):

    def init(self, file_names: List[str], geo_transform: tuple, projection: str, width: int, height: int,
             num_bands: Optional[List[int]] = None, data_types: Optional[List[str]] = None):
        if num_bands is None or len(num_bands) == 0:
            num_bands = [1] * len(file_names)
        elif len(num_bands) != len(file_names):
            raise ValueError('List with number of bands must be of same size as list of file names')
        self.num_bands = num_bands
        if data_types is None or len(data_types) == 0:
            data_types = ['Float'] * len(file_names)
        elif len(data_types) != len(file_names):
            raise ValueError('List with data types must be of same size as list of file names')
        gdal_data_types = []
        for data_type in data_types:
            gdal_data_types.append(self._get_gdal_data_type(data_type))
        self._width = width
        self._height = height
        drv = gdal.GetDriverByName('GTiff')
        self._file_names = file_names
        # self._destination_data_sets = []
        for i, file_name in enumerate(file_names):
            parent_dir = os.path.dirname(file_name)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            if not file_name.endswith('.tif') and not file_name.endswith('tiff'):
                file_name = file_name + '.tif'
            if not os.path.exists(file_name):
            # if os.path.exists(file_name):
            #     data_set = gdal.OpenShared(file_name, gdal.GA_Update)
            # else:
                data_set = drv.Create(file_name, width, height, num_bands[i], gdal_data_types[i],
                                  ['COMPRESS=DEFLATE', 'BIGTIFF=YES', 'PREDICTOR=1', 'TILED=YES'])
                data_set.SetProjection(projection)
                data_set.SetGeoTransform(geo_transform)
                data_set = None
            # self._destination_data_sets.append(data_set)

    @staticmethod
    def _get_gdal_data_type(data_type: str) -> str:
        if data_type == 'Float':
            return gdal.GDT_Float32
        elif data_type == 'Double':
            return gdal.GDT_Float64
        elif data_type == 'Int':
            return gdal.GDT_Int32
        raise ValueError('Data Type {} not supported.'.format(data_type))

    def write(self, data: List[np.array], width: Optional[int] = None, height: Optional[int] = None,
              offset_x: Optional[int] = 0, offset_y: Optional[int] = 0):
        # assert len(data) == len(self._destination_data_sets)
        assert len(data) == len(self._file_names)
        if width is None:
            width = self._width
        if height is None:
            height = self._height
        for i, d in enumerate(data):
            if d.shape == (width * height,):
                d = d.reshape(height, width)
            elif d.shape == (self.num_bands[i], width * height):
                d = d.reshape(self.num_bands[i], height, width)
            if d.shape == (self.num_bands[i], height, width) and self.num_bands[i] == 1:
                d = d.reshape(height, width)
            logger.info(f'Expecting height {height} and width {width} as {(height, width)}, receiving {d.shape}')
            assert d.shape == (height, width) or d.shape == (self.num_bands[i], height, width)
            dataset = gdal.OpenShared(self._file_names[i], gdal.GA_Update)
            if self.num_bands[i] > 1:
                for band in range(self.num_bands[i]):
                    # self._destination_data_sets[i].GetRasterBand(band + 1).WriteArray(d[band],
                    dataset.GetRasterBand(band + 1).WriteArray(d[band],
                                                                                      xoff=offset_x, yoff=offset_y)
            else:
                # self._destination_data_sets[i].GetRasterBand(1).WriteArray(d, xoff=offset_x, yoff=offset_y)
                dataset.GetRasterBand(1).WriteArray(d, xoff=offset_x, yoff=offset_y)
            # self._destination_data_sets[i].FlushCache()
            dataset.FlushCache()
            dataset = None


    def close(self):
        pass
        # for dataset in self._destination_data_sets:
        #     dataset = None
        # self._destination_data_sets = None
