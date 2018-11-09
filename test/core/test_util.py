import multiply_core.util.util as util
import numpy as np
import pytest

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

MEAN_EARTH_RADIUS = 6372000


def test_compute_distance():
    bounds = [7.8, 53.5, 8.8, 53.8]
    lon_0 = bounds[0]
    lat_0 = bounds[1]
    lon_1 = bounds[2]
    lat_1 = bounds[3]
    assert pytest.approx(73878.9732269) == util.compute_distance(lon_0, lat_0, lon_1, lat_1, MEAN_EARTH_RADIUS)

    bounds = [7.8, 53.5, 7.8, 53.8]
    lon_0 = bounds[0]
    lat_0 = bounds[1]
    lon_1 = bounds[2]
    lat_1 = bounds[3]
    assert pytest.approx(33363.713981) == util.compute_distance(lon_0, lat_0, lon_1, lat_1, MEAN_EARTH_RADIUS)

    bounds = [8.8, 53.5, 8.8, 53.8]
    lon_0 = bounds[0]
    lat_0 = bounds[1]
    lon_1 = bounds[2]
    lat_1 = bounds[3]
    assert pytest.approx(33363.713981) == util.compute_distance(lon_0, lat_0, lon_1, lat_1, MEAN_EARTH_RADIUS)

    bounds = [7.8, 53.5, 8.8, 53.5]
    lon_0 = bounds[0]
    lat_0 = bounds[1]
    lon_1 = bounds[2]
    lat_1 = bounds[3]
    assert pytest.approx(66151.1151985) == util.compute_distance(lon_0, lat_0, lon_1, lat_1, MEAN_EARTH_RADIUS)

    bounds = [7.8, 53.8, 8.8, 53.8]
    lon_0 = bounds[0]
    lat_0 = bounds[1]
    lon_1 = bounds[2]
    lat_1 = bounds[3]
    assert pytest.approx(65682.1190225) == util.compute_distance(lon_0, lat_0, lon_1, lat_1, MEAN_EARTH_RADIUS)


def test_block_diag():
    matrices = []
    values_1 = np.array([0.01, 0.2, 0.01, 0.05, 0.01, 0.01, 0.50, 0.1, 0.1, 0.1])
    values_2 = np.array([0.02, 0.18, 0.04, 0.07, 0.02, 0.03, 0.30, 0.12, 0.12, 0.15])
    values_3 = np.array([0.005, 0.23, 0.02, 0.03, 0.04, 0.05, 0.40, 0.09, 0.13, 0.2])
    matrices.append(np.diag(values_1 ** 2).astype(np.float32))
    matrices.append(np.diag(values_2 ** 2).astype(np.float32))
    matrices.append(np.diag(values_3 ** 2).astype(np.float32))
    coo_matrix = util.block_diag(matrices)
    coo_matrix_array = coo_matrix.toarray()
    value_length = 10
    total_length = value_length * 3
    assert (total_length, total_length) == coo_matrix.shape
    for k in range(3):
        for i in range(value_length):
            for j in range(value_length):
                assert matrices[k][i][j] == coo_matrix_array[k * value_length + i][k * value_length + j]


def test_block_as_numpy_matrix():
    matrices = np.empty((3, 10, 10), dtype=np.float32)
    values_1 = np.array([0.01, 0.2, 0.01, 0.05, 0.01, 0.01, 0.50, 0.1, 0.1, 0.1])
    values_2 = np.array([0.02, 0.18, 0.04, 0.07, 0.02, 0.03, 0.30, 0.12, 0.12, 0.15])
    values_3 = np.array([0.005, 0.23, 0.02, 0.03, 0.04, 0.05, 0.40, 0.09, 0.13, 0.2])
    matrices[0] = np.diag(values_1 ** 2).astype(np.float32)
    matrices[1] = np.diag(values_2 ** 2).astype(np.float32)
    matrices[2] = np.diag(values_3 ** 2).astype(np.float32)
    coo_matrix = util.block_diag(matrices)
    coo_matrix_array = coo_matrix.toarray()
    value_length = 10
    total_length = value_length * 3
    assert (total_length, total_length) == coo_matrix.shape
    for k in range(3):
        for i in range(value_length):
            for j in range(value_length):
                assert matrices[k][i][j] == coo_matrix_array[k * value_length + i][k * value_length + j]


def test_are_polygons_almost_equal():
    polygon_1 = "POLYGON((5 5, 20 5, 20 20, 5 20, 5 5))"
    polygon_2 = "POLYGON((5 5, 5 20, 20 20, 20 5, 5 5))"
    polygon_3 = "POLYGON((5 5, 5 20, 19 19, 20 5, 5 5))"

    assert util.are_polygons_almost_equal(polygon_1, polygon_1)
    assert util.are_polygons_almost_equal(polygon_1, polygon_2)
    assert not util.are_polygons_almost_equal(polygon_1, polygon_3)
    assert not util.are_polygons_almost_equal(polygon_2, polygon_3)


def test_get_time_from_string_is_empty():
    assert util.get_time_from_string('') is None


def test_get_time_from_year_and_day_of_year_238():
    year = 2017
    doy = 238

    datetime = util.get_time_from_year_and_day_of_year(year, doy)
    assert 8 == datetime.month
    assert 26 == datetime.day


def test_get_time_from_year_and_day_of_year_151():
    year = 2017
    doy = 151

    datetime = util.get_time_from_year_and_day_of_year(year, doy)
    assert 5 == datetime.month
    assert 31 == datetime.day


def test_meta_info_provider_get_days_of_month():
    assert util.get_days_of_month(2017, 1) == 31
    assert util.get_days_of_month(2017, 2) == 28
    assert util.get_days_of_month(2017, 3) == 31
    assert util.get_days_of_month(2017, 4) == 30
    assert util.get_days_of_month(2017, 5) == 31
    assert util.get_days_of_month(2017, 6) == 30
    assert util.get_days_of_month(2017, 7) == 31
    assert util.get_days_of_month(2017, 8) == 31
    assert util.get_days_of_month(2017, 9) == 30
    assert util.get_days_of_month(2017, 10) == 31
    assert util.get_days_of_month(2017, 11) == 30
    assert util.get_days_of_month(2017, 12) == 31
    assert util.get_days_of_month(2016, 2) == 29
    assert util.get_days_of_month(2000, 2) == 29
    assert util.get_days_of_month(1900, 2) == 28
    assert util.get_days_of_month(1600, 2) == 29


def test_is_leap_year():
    assert util.is_leap_year(2004)
    assert not util.is_leap_year(2003)
    assert util.is_leap_year(2000)
    assert not util.is_leap_year(1900)


def test_get_mime_type():
    assert 'application/x-netcdf' == util.get_mime_type('ctfthdbdr.nc')
    assert 'application/zip' == util.get_mime_type('ctfthdbdr.zip')
    assert 'application/json' == util.get_mime_type('ctfthdbdr.json')
    assert 'unknown mime type' == util.get_mime_type('ctfthdbdr')
