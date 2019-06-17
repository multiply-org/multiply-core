from shapely.wkt import loads

import gdal
import osr
import multiply_core.util.reproject as reproject
import pytest

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

S2_FILE = './test/test_data/T32UME_20170910T104021_B10.jp2'
ALA_TIFF_FILE = './test/test_data/Priors_ala_125_[50_60N]_[000_010E].tiff'

EPSG_4326_WKT = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]'
EPSG_32632_WKT = 'PROJCS["WGS 84 / UTM zone 32N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32632"]]'
EPSG_32232_WKT = 'PROJCS["WGS 72 / UTM zone 32N",GEOGCS["WGS 72",DATUM["World Geodetic System 1972",SPHEROID["WGS 72",6378135.0,298.26,AUTHORITY["EPSG","7043"]],TOWGS84[0.0,0.0,4.5,0.0,0.0,0.554,0.219],AUTHORITY["EPSG","6322"]],PRIMEM["Greenwich",0.0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.017453292519943295],AXIS["Geodetic longitude",EAST],AXIS["Geodetic latitude",NORTH],AUTHORITY["EPSG","4322"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["central_meridian",9.0],PARAMETER["latitude_of_origin",0.0],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000.0],PARAMETER["false_northing",0.0],UNIT["m",1.0],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32232"]]'


def test_reproject_to_wgs84():
    roi = 'POLYGON((685700. 6462200., 685700. 6470700., 697660. 6470700., 697660. 6462200., 685700. 6462200.))'
    roi_grid = 'EPSG:3301'
    transformed_roi = reproject.reproject_to_wgs84(roi, roi_grid)
    transformed_roi = loads(transformed_roi)
    expected_roi = loads('POLYGON ((27.1647563115467534 58.2611263320005577, 27.1716005869326196 58.3373581174386473, '
                         '27.3755330955532621 58.3321196269764286, 27.3682501734918766 58.2558991181697223, '
                         '27.1647563115467534 58.2611263320005577))')
    assert transformed_roi.almost_equals(expected_roi)


def test_transform_coordinates_0():
    ala_dataset = gdal.Open(ALA_TIFF_FILE)
    ala_srs = reproject.get_spatial_reference_system_from_dataset(ala_dataset)
    s2_dataset = gdal.Open(S2_FILE)
    s2_srs = reproject.get_spatial_reference_system_from_dataset(s2_dataset)

    coords = [-0.0013889, 60.0013885,
              -0.0013889, 50.0038300,
              9.9986114, 60.0013885,
              9.9986114, 50.0038300]
    transformed_coordinates = reproject.transform_coordinates(ala_srs, s2_srs, coords)
    assert 8 == len(transformed_coordinates)
    assert pytest.approx(-144583.384), transformed_coordinates[0]
    assert pytest.approx(6685755.131), transformed_coordinates[1]
    assert pytest.approx(-144583.384), transformed_coordinates[2]
    assert pytest.approx(5539163.063), transformed_coordinates[3]
    assert pytest.approx(571659.159), transformed_coordinates[4]
    assert pytest.approx(6685755.131), transformed_coordinates[5]
    assert pytest.approx(571659.159), transformed_coordinates[6]
    assert pytest.approx(5539163.063), transformed_coordinates[7]


def test_transform_coordinates_1():
    ala_dataset = gdal.Open(ALA_TIFF_FILE)
    ala_srs = reproject.get_spatial_reference_system_from_dataset(ala_dataset)
    s2_dataset = gdal.Open(S2_FILE)
    s2_srs = reproject.get_spatial_reference_system_from_dataset(s2_dataset)

    coords = [-0.0013889, 60.0013885, 9.9986114, 50.0038300]
    transformed_coordinates = reproject.transform_coordinates(ala_srs, s2_srs, coords)
    assert 4 == len(transformed_coordinates)
    assert pytest.approx(-144583.384), transformed_coordinates[0]
    assert pytest.approx(6685755.131), transformed_coordinates[1]
    assert pytest.approx(571659.159), transformed_coordinates[2]
    assert pytest.approx(5539163.063), transformed_coordinates[3]


def test_get_spatial_reference_system_from_dataset():
    ala_dataset = gdal.Open(ALA_TIFF_FILE)
    ala_srs = reproject.get_spatial_reference_system_from_dataset(ala_dataset)
    assert EPSG_4326_WKT == ala_srs.ExportToWkt()

    s2_dataset = gdal.Open(S2_FILE)
    s2_srs = reproject.get_spatial_reference_system_from_dataset(s2_dataset)
    assert EPSG_32632_WKT == s2_srs.ExportToWkt()


def test_get_target_resolutions():
    ala_dataset = gdal.Open(ALA_TIFF_FILE)
    x_resolution, y_resolution = reproject.get_target_resolutions(ala_dataset)
    assert pytest.approx(0.00277778) == x_resolution
    assert pytest.approx(0.0027771) == y_resolution

    s2_dataset = gdal.Open(S2_FILE)
    x_resolution, y_resolution = reproject.get_target_resolutions(s2_dataset)
    assert 60 == x_resolution
    assert 60 == y_resolution


def test_get_resampling():
    ala_dataset = gdal.Open(ALA_TIFF_FILE)
    bounds = [-9.220204779005144, 48.98786207315579, -8.220204897166695, 49.28786209826107]
    bounds_srs = osr.SpatialReference()
    bounds_srs.ImportFromWkt(EPSG_32232_WKT)
    dest_srs = osr.SpatialReference()
    dest_srs.ImportFromWkt(EPSG_32632_WKT)
    assert 'bilinear' == reproject._get_resampling(ala_dataset, bounds, 100.0, 100.0, bounds_srs, dest_srs)
    assert 'average' == reproject._get_resampling(ala_dataset, bounds, 1000.0, 1000.0, bounds_srs, dest_srs)


def test_need_to_sample_up():
    ala_dataset = gdal.Open(ALA_TIFF_FILE)
    bounds = [-9.220204779005144, 48.98786207315579, -8.220204897166695, 49.28786209826107]
    bounds_srs = osr.SpatialReference()
    bounds_srs.ImportFromWkt(EPSG_32232_WKT)
    dest_srs = osr.SpatialReference()
    dest_srs.ImportFromWkt(EPSG_32632_WKT)
    assert reproject._need_to_sample_up(ala_dataset, bounds, 100.0, 100.0, bounds_srs, dest_srs)
    assert not reproject._need_to_sample_up(ala_dataset, bounds, 1000.0, 1000.0, bounds_srs, dest_srs)


def test_get_dist_measure():
    assert 8.0 == pytest.approx(reproject._get_dist_measure([50.0, 10.0, 100.0, 50.0], 25.0, 10.0))


def test_reproject_image():
    destination_srs = osr.SpatialReference()
    destination_srs.ImportFromWkt(EPSG_32232_WKT)
    bounds_srs = osr.SpatialReference()
    bounds_srs.SetWellKnownGeogCS('EPSG:4326')
    bounds = [7.8, 53.5, 8.8, 53.8]
    reprojected_dataset = reproject.reproject_dataset(S2_FILE, bounds, x_res=50, y_res=100,
                                                      destination_srs=destination_srs,
                                                      bounds_srs=bounds_srs,
                                                      resampling_mode=None)
    assert 1328 == reprojected_dataset.RasterXSize
    assert 327 == reprojected_dataset.RasterYSize
    assert EPSG_32232_WKT == reprojected_dataset.GetProjection()
    geo_transform = reprojected_dataset.GetGeoTransform()
    assert 6 == len(geo_transform)
    assert pytest.approx(420392.4558445791) == geo_transform[0]
    assert 50.0 == geo_transform[1]
    assert 0.0 == geo_transform[2]
    assert pytest.approx(5961284.037740353) == geo_transform[3]
    assert 0.0 == geo_transform[4]
    assert -100.0 == geo_transform[5]
    assert 1 == reprojected_dataset.RasterCount
    raster_band = reprojected_dataset.GetRasterBand(1)
    raster_data = raster_band.ReadAsArray()
    assert 8 == raster_data[0][0]
    assert 14 == raster_data[94][285]
