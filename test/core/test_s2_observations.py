import osr

from multiply_core.util import Reprojection, FileRef
from multiply_core.observations import S2Observations

S2_FILE = './test/test_data/T32UME_20170910T104021_B10.jp2'
S2_AWS_BASE_FILE = './test/test_data/product_in_aws_format/'
EMULATOR_FOLDER = './test/test_data/emulator_folder/'
EPSG_32232_WKT = 'PROJCS["WGS 72 / UTM zone 32N",GEOGCS["WGS 72",DATUM["World Geodetic System 1972",SPHEROID["WGS 72",6378135.0,298.26,AUTHORITY["EPSG","7043"]],TOWGS84[0.0,0.0,4.5,0.0,0.0,0.554,0.219],AUTHORITY["EPSG","6322"]],PRIMEM["Greenwich",0.0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.017453292519943295],AXIS["Geodetic longitude",EAST],AXIS["Geodetic latitude",NORTH],AUTHORITY["EPSG","4322"]],PROJECTION["Transverse_Mercator",AUTHORITY["EPSG","9807"]],PARAMETER["central_meridian",9.0],PARAMETER["latitude_of_origin",0.0],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000.0],PARAMETER["false_northing",0.0],UNIT["m",1.0],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32232"]]'

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

def test_bands_per_observation():
    destination_srs = osr.SpatialReference()
    destination_srs.ImportFromWkt(EPSG_32232_WKT)
    bounds_srs = osr.SpatialReference()
    bounds_srs.SetWellKnownGeogCS('EPSG:4326')
    bounds = [7.8, 53.5, 8.8, 53.8]
    reprojection = Reprojection(bounds=bounds, x_res=50, y_res=100, destination_srs=destination_srs,
                                bounds_srs=bounds_srs, resampling_mode=None)
    file_refs = [FileRef(url=S2_AWS_BASE_FILE, start_time='2017-09-10', end_time='2017-09-10',
                        mime_type='unknown mime type')]
    required_band_names = ['B02_sur.tiff', 'B03_sur.tiff', 'B04_sur.tiff', 'B05_sur.tiff', 'B06_sur.tiff', 'B07_sur.tiff',
                           'B08_sur.tiff', 'B8A_sur.tiff', 'B09_sur.tiff', 'B12_sur.tiff']
    s2_observations = S2Observations(file_refs, reprojection, emulator_folder=EMULATOR_FOLDER,
                                     required_band_names=required_band_names)

    assert len(s2_observations.bands_per_observation) == 1
    assert s2_observations.bands_per_observation[0] == 10


def test_get_band_data():
    destination_srs = osr.SpatialReference()
    destination_srs.ImportFromWkt(EPSG_32232_WKT)
    bounds_srs = osr.SpatialReference()
    bounds_srs.SetWellKnownGeogCS('EPSG:4326')
    bounds = [7.8, 53.5, 8.8, 53.8]
    reprojection = Reprojection(bounds=bounds, x_res=50, y_res=100, destination_srs=destination_srs,
                                bounds_srs=bounds_srs, resampling_mode=None)
    file_refs = [FileRef(url=S2_AWS_BASE_FILE, start_time='2017-09-10', end_time='2017-09-10',
                        mime_type='unknown mime type')]
    required_band_names = ['B02_sur.tiff', 'B03_sur.tiff', 'B04_sur.tiff', 'B05_sur.tiff', 'B06_sur.tiff',
                           'B07_sur.tiff', 'B08_sur.tiff', 'B8A_sur.tiff', 'B09_sur.tiff', 'B12_sur.tiff']
    s2_observations = S2Observations(file_refs, reprojection, emulator_folder=EMULATOR_FOLDER,
                                     required_band_names=required_band_names)
    s2_observation_data = s2_observations.get_band_data(0, 3)
    assert (327, 1328) == s2_observation_data.observations.shape
    assert 4, len(s2_observation_data.metadata.keys())
    assert 'sza' in s2_observation_data.metadata.keys()
    assert 61.3750584241536, s2_observation_data.metadata['sza']
    assert 'saa' in s2_observation_data.metadata.keys()
    assert 160.875894634785, s2_observation_data.metadata['saa']
    assert 'vza' in s2_observation_data.metadata.keys()
    assert 2.776727292381147, s2_observation_data.metadata['vza']
    assert 'vaa' in s2_observation_data.metadata.keys()
    assert 177.40153095962427, s2_observation_data.metadata['vaa']
    assert (327, 1328) == s2_observation_data.mask.shape
    assert (434256, 434256) == s2_observation_data.uncertainty.shape
