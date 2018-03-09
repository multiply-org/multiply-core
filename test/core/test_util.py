import multiply_core.util.util as util
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
