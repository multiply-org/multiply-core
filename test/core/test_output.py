import gdal
from multiply_core.observations import GeoTiffWriter
import numpy as np
import os
from pytest import raises

GEOTIFF_WRITE_FOLDER = './test/test_data/geotiff'
GEO_TRANSFORM = (582414.9967658486, 120.0, 0.0, 4317096.927011872, 0.0, -120.0)
PROJECTION = 'PROJCS["UTM Zone 30, Northern Hemisphere",GEOGCS["WGS 84",DATUM["WGS_1984",' \
             'SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],' \
             'PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,' \
             'AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],' \
             'PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-3],PARAMETER["scale_factor",0.9996],' \
             'PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'


def test_geotiff_writer_create():
    file_names = [os.path.abspath('{}/name11.tif'.format(GEOTIFF_WRITE_FOLDER)),
                  os.path.abspath('{}/name12.tif'.format(GEOTIFF_WRITE_FOLDER)),
                  os.path.abspath('{}/name13.tif'.format(GEOTIFF_WRITE_FOLDER)),
                  os.path.abspath('{}/name14.tif'.format(GEOTIFF_WRITE_FOLDER)),
                  os.path.abspath('{}/name15.tif'.format(GEOTIFF_WRITE_FOLDER))]
    try:
        num_bands = [1, 2, 3, 1, 1]
        data_types = ['Float', 'Float', 'Double', 'Int', 'Double']
        writer = GeoTiffWriter(file_names, GEO_TRANSFORM, PROJECTION, 5, 5, num_bands, data_types=data_types)
        writer.close()
        assert writer is not None
    finally:
        for file_name in file_names:
            if os.path.exists(file_name):
                os.remove(file_name)


def test_geotiff_writer_create_invalid_num_bands():
    with raises(ValueError, message = 'List with number of bands must be of same size as list of file names'):
        file_names = [os.path.abspath('{}/name21.tif'.format(GEOTIFF_WRITE_FOLDER)),
                      os.path.abspath('{}/name22.tif'.format(GEOTIFF_WRITE_FOLDER)),
                      os.path.abspath('{}/name23.tif'.format(GEOTIFF_WRITE_FOLDER)),
                      os.path.abspath('{}/name24.tif'.format(GEOTIFF_WRITE_FOLDER)),
                      os.path.abspath('{}/name25.tif'.format(GEOTIFF_WRITE_FOLDER))]

        try:
            num_bands = [1, 2, 3, 1]
            data_types = ['Float', 'Float', 'Double', 'Int', 'Double']
            writer = GeoTiffWriter(file_names, GEO_TRANSFORM, PROJECTION, 3, 4, num_bands, data_types=data_types)
            writer.close()
        finally:
            for file_name in file_names:
                if os.path.exists(file_name):
                    os.remove(file_name)


def test_geotiff_writer_create_invalid_data_types():
    with raises(ValueError, message = 'Data Type dgfvbgf not supported.'):
        file_names = [os.path.abspath('{}/name31.tif'.format(GEOTIFF_WRITE_FOLDER)),
                      os.path.abspath('{}/name32.tif'.format(GEOTIFF_WRITE_FOLDER)),
                      os.path.abspath('{}/name33.tif'.format(GEOTIFF_WRITE_FOLDER)),
                      os.path.abspath('{}/name34.tif'.format(GEOTIFF_WRITE_FOLDER)),
                      os.path.abspath('{}/name35.tif'.format(GEOTIFF_WRITE_FOLDER))]
        try:
            num_bands = [1, 2, 3, 1, 1]
            data_types = ['Float', 'dgfvbgf', 'Double', 'Int', 'Double']
            writer = GeoTiffWriter(file_names, GEO_TRANSFORM, PROJECTION, 3, 4, num_bands, data_types=data_types)
            writer.close()
        finally:
            for file_name in file_names:
                if os.path.exists(file_name):
                    os.remove(file_name)


def test_geotiff_writer_create_invalid_number_of_data_types():
    with raises(ValueError, message = 'List with data types must be of same size as list of file names'):
        file_names = [os.path.abspath('{}/name41.tif'.format(GEOTIFF_WRITE_FOLDER)),
                      os.path.abspath('{}/name42.tif'.format(GEOTIFF_WRITE_FOLDER)),
                      os.path.abspath('{}/name43.tif'.format(GEOTIFF_WRITE_FOLDER)),
                      os.path.abspath('{}/name44.tif'.format(GEOTIFF_WRITE_FOLDER)),
                      os.path.abspath('{}/name45.tif'.format(GEOTIFF_WRITE_FOLDER))]
        try:
            num_bands = [1, 2, 3, 1, 1]
            data_types = ['Float', 'Double', 'Int', 'Double']
            writer = GeoTiffWriter(file_names, GEO_TRANSFORM, PROJECTION, 3, 4, num_bands, data_types=data_types)
            writer.close()
        finally:
            for file_name in file_names:
                if os.path.exists(file_name):
                    os.remove(file_name)


def test_geotiff_writer_write():
    file_names = [os.path.abspath('{}/name51.tif'.format(GEOTIFF_WRITE_FOLDER)),
                  os.path.abspath('{}/name52.tif'.format(GEOTIFF_WRITE_FOLDER)),
                  os.path.abspath('{}/name53.tif'.format(GEOTIFF_WRITE_FOLDER)),
                  os.path.abspath('{}/name54.tif'.format(GEOTIFF_WRITE_FOLDER)),
                  os.path.abspath('{}/name55.tif'.format(GEOTIFF_WRITE_FOLDER))]
    try:
        for file_name in file_names:
            assert not os.path.exists(file_name)
        num_bands = [1, 2, 3, 1, 1]
        data_types = ['Float', 'Float', 'Double', 'Int', 'Double']
        writer = GeoTiffWriter(file_names, GEO_TRANSFORM, PROJECTION, 3, 4, num_bands, data_types=data_types)
        data_list = [np.array([[0.70970884, 0.36247307, 0.66030969, 0.93471179],
                               [0.89365593, 0.63907102, 0.06156231, 0.69681795],
                               [0.67383079, 0.31445525, 0.83595899, 0.705263]]),
                     np.array([[[0.66830849, 0.35291152, 0.04349641, 0.62815067],
                       [0.75400669, 0.43327223, 0.64411265, 0.26457201],
                       [0.84955846, 0.40414402, 0.6676325, 0.33832645]],
                      [[0.43584521, 0.66741136, 0.70503737, 0.26677207],
                       [0.4960918, 0.32260832, 0.61456562, 0.35535548],
                       [0.83467162, 0.74859915, 0.70133653, 0.57041632]]]),
                     np.array([[[0.73339975, 0.78643665, 0.45069885, 0.74986861],
                       [0.67810782, 0.54938006, 0.26128632, 0.07936058],
                       [0.02278049, 0.8836243, 0.62162135, 0.45951421]],
                      [[0.70346187, 0.10926256, 0.67854529, 0.39645904],
                       [0.65467032, 0.56780106, 0.6622787, 0.39268321],
                       [0.60983543, 0.19075994, 0.36662241, 0.91810201]],
                      [[0.30012843, 0.60306739, 0.62558339, 0.3591911],
                       [0.37191895, 0.65078595, 0.3670538, 0.37250119],
                       [0.55795222, 0.01902248, 0.72941351, 0.57023361]]]),
                     np.array([[7, 3, 2, 5, 2, 14, 34, 1, 10, 2, 15, 5]]),
                     np.array([0.03280384, 0.94485231, 0.43253641, 0.29359502, 0.84187526, 0.50992254,
                      0.29902775, 0.48802801, 0.19521612, 0.16601624, 0.95941332, 0.90352063])]
        writer.write(data_list)
        writer.close()
        for file_name in file_names:
            assert os.path.exists(file_name)

            #todo assert data is read correctly
            # read_data = gdal.Open(file_name)
            # for i, data in enumerate(data_list):
            #     data = read_data.GetRasterBand(i + 1).ReadArray()

    finally:
        for file_name in file_names:
            if os.path.exists(file_name):
                os.remove(file_name)
