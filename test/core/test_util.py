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
