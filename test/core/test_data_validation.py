from datetime import datetime
from multiply_core.observations.data_validation import S2L1CValidator, AWSS2L1Validator, ModisMCD43Validator, \
    ModisMCD15A2HValidator, CamsValidator, S2AEmulatorValidator, S2BEmulatorValidator, WVEmulatorValidator, \
    AsterValidator, get_valid_types, CamsTiffValidator, VariableValidator, S2L2Validator, S1SlcValidator, \
    S1SpeckledValidator
from shapely.geometry import Polygon
from shapely.wkt import loads

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

VALID_AWS_S2_DATA = './test/test_data/s2_aws/15/F/ZX/2016/12/31/1'
VALID_CAMS_TIFF_DATA = './test/test_data/2018_10_23/'
VALID_S2_PATH = './test/test_data/S2A_OPER_PRD_MSIL1C_PDMC_20150714T123646_R019_V20150704T102427_20150704T102427.SAFE'
ANOTHER_VALID_S2_PATH = './test/test_data/S2B_MSIL1C_20180819T100019_N0206_R122_T32TQR_20180819T141300'
VALID_S2L2_PATH = './test/test_data/S2A_MSIL1C_20170605T105031_N0205_R051_T30SWJ_20170605T105303-ac'
ANOTHER_VALID_S2L2_PATH = './test/test_data/S2B_MSIL1C_20180819T100019_N0206_R122_T32TQR_20180819T141300-ac'


def test_s1_slc_validator_get_relative_path():
    validator = S1SlcValidator()

    assert '' == validator.get_relative_path(
        '/some/path/S1A_IW_SLC__1SDH_20140502T170314_20140502T170344_000421_0004CC_1A90')


def test_s1_slc_validator_name():
    validator = S1SlcValidator()
    assert 'S1_SLC' == validator.name()


def test_s1_slc_is_valid():
    validator = S1SlcValidator()

    assert validator.is_valid('S1A_IW_SLC__1SDH_20140502T170314_20140502T170344_000421_0004CC_1A90')
    assert validator.is_valid('S1A_EW_SLC__1SDH_20140502T170314_20140502T170344_000421_0004CC_1A90.SAFE')
    assert validator.is_valid('S1B_WV_SLC__1SDH_20140502T170314_20140502T170344_000421_0004CC_1A90.SAFE')
    assert validator.is_valid('S1A_S9_SLC__1SDH_20140502T170314_20140502T170344_000421_0004CC_1A90')

    assert not validator.is_valid('S2A_IW_SLC__1SDH_20140502T170314_20140502T170344_000421_0004CC_1A90')
    assert not validator.is_valid('S1A_IW_GRD__1SDH_20140502T170314_20140502T170344_000421_0004CC_1A90.SAFE')
    assert not validator.is_valid('S1A_S10_SLC__1SDH_20140502T170314_20140502T170344_000421_0004CC_1A90')
    assert not validator.is_valid('dtsfrghgj')


def test_s1_slc_get_file_pattern():
    validator = S1SlcValidator()
    assert '(S1A|S1B)_(IW|EW|WV|(S[1-9]{1}))_SLC__1([A-Z]{3})_([0-9]{8}T[0-9]{6})_([0-9]{8}T[0-9]{6})_.*.(SAFE)?' \
           == validator.get_file_pattern()


def test_s1_slc_is_valid_for():
    validator = S1SlcValidator()
    s1_path = 'S1A_IW_SLC__1SDH_20140502T170314_20140502T170344_000421_0004CC_1A90'
    other_s1_path = 'S1A_IW_SLC__1SDH_20160607T170314_20160607T170344_000421_0004CC_1A90'
    assert validator.is_valid_for(s1_path, Polygon(), datetime(2014, 5, 1), datetime(2014, 5, 3))
    assert not validator.is_valid_for(s1_path, Polygon(), datetime(2014, 4, 30), datetime(2014, 5, 1))
    assert not validator.is_valid_for(s1_path, Polygon(), datetime(2014, 5, 3), datetime(2014, 5, 4))
    assert validator.is_valid_for(other_s1_path, Polygon(), datetime(2016, 6, 6), datetime(2016, 6, 8))
    assert not validator.is_valid_for(other_s1_path, Polygon(), datetime(2016, 6, 5), datetime(2016, 6, 6))
    assert not validator.is_valid_for(other_s1_path, Polygon(), datetime(2016, 6, 8), datetime(2018, 6, 9))


def test_s1_speckled_validator_get_relative_path():
    validator = S1SpeckledValidator()

    assert '' == validator.get_relative_path(
        '/some/path/S1A_IW_SLC__1SDV_20170525T170030_20170525T170057_016741_01BCE3_9B0A_GC_RC_No_Su_Co_speckle.nc')


def test_s1_speckled_validator_name():
    validator = S1SpeckledValidator()
    assert 'S1_Speckled' == validator.name()


def test_s1_speckled_is_valid():
    validator = S1SpeckledValidator()

    assert validator.is_valid(
        'S1A_IW_SLC__1SDV_20170525T170030_20170525T170057_016741_01BCE3_9B0A_GC_RC_No_Su_Co_speckle.nc')
    assert validator.is_valid(
        'S1A_IW_SLC__1SDH_20140502T170314_20140502T170344_000421_0004CC_1A90_GC_RC_No_Su_Co_speckle.nc')
    assert validator.is_valid(
        'S1B_IW_SLC__1SDV_20170524T170804_20170524T170831_005743_00A0F5_841A_GC_RC_No_Su_Co_speckle.nc')

    assert not validator.is_valid('S1A_IW_SLC__1SDV_20170525T170030_20170525T170057_016741_01BCE3_9B0A')
    assert not validator.is_valid(
        'S2B_IW_SLC__1SDV_20170524T170804_20170524T170831_005743_00A0F5_841A_GC_RC_No_Su_Co_speckle.nc')
    assert not validator.is_valid(
        'S1A_IW_SLC__1SDH_20140502T170314_20140502T170344_000421_0004CC_1A90_GC_RC_No_Su_Co.nc')
    assert not validator.is_valid('dtsfrghgj')


def test_s1_speckled_get_file_pattern():
    validator = S1SpeckledValidator()
    assert '(S1A|S1B)_(IW|EW|WV|(S[1-9]{1}))_SLC__1([A-Z]{3})_([0-9]{8}T[0-9]{6})_' \
           '([0-9]{8}T[0-9]{6})_.*._GC_RC_No_Su_Co_speckle.nc' == validator.get_file_pattern()


def test_s1_speckled_is_valid_for():
    validator = S1SpeckledValidator()
    s1_speckled_path = 'S1A_IW_SLC__1SDH_20140502T170314_20140502T170344_000421_0004CC_1A90_GC_RC_No_Su_Co_speckle.nc'
    other_s1_speckled_path = \
        'S1B_IW_SLC__1SDV_20170524T170804_20170524T170831_005743_00A0F5_841A_GC_RC_No_Su_Co_speckle.nc'
    assert validator.is_valid_for(s1_speckled_path, Polygon(), datetime(2014, 5, 1), datetime(2014, 5, 3))
    assert not validator.is_valid_for(s1_speckled_path, Polygon(), datetime(2014, 4, 30), datetime(2014, 5, 1))
    assert not validator.is_valid_for(s1_speckled_path, Polygon(), datetime(2014, 5, 3), datetime(2014, 5, 4))
    assert validator.is_valid_for(other_s1_speckled_path, Polygon(), datetime(2017, 5, 23), datetime(2017, 5, 25))
    assert not validator.is_valid_for(other_s1_speckled_path, Polygon(), datetime(2017, 5, 21), datetime(2017, 5, 23))
    assert not validator.is_valid_for(other_s1_speckled_path, Polygon(), datetime(2017, 5, 25), datetime(2017, 5, 27))


def test_aws_s2_validator_matches_pattern():
    validator = AWSS2L1Validator()

    assert validator._matches_pattern('/29/S/QB/2017/9/4/0')
    assert validator._matches_pattern(VALID_AWS_S2_DATA)
    assert not validator._matches_pattern('fcsfzvdbt/chvs/201')


def test_aws_s2_validator_is_valid():
    validator = AWSS2L1Validator()

    assert validator.is_valid(VALID_AWS_S2_DATA)


def test_aws_s2_validator_get_relative_path():
    validator = AWSS2L1Validator()

    assert '29/S/QB/2017/9/4/0' == validator.get_relative_path('/the/non/relative/part/29/S/QB/2017/9/4/0')


def test_s2_validator_name():
    validator = S2L1CValidator()
    assert 'S2_L1C' == validator.name()


def test_s2_is_valid():
    validator = S2L1CValidator()
    assert validator.is_valid(VALID_S2_PATH)
    assert not validator.is_valid('S2A_OPER_PRD_MSIL1C_PDMC_20150714T123646_R019_V20150704T102427_20150704T102427.SAFE')
    assert not validator.is_valid(
        './test/test_data/S2B_OPER_PRD_MSIL1C_PDMC_20150714T123646_R019_V20150704T102427_20150704T102427.SAFE')
    assert validator.is_valid(ANOTHER_VALID_S2_PATH)
    assert not validator.is_valid('S2B_MSIL1C_20180819T100019_N0206_R122_T32TQR_20180819T141300')
    assert not validator.is_valid('./test/test_data/S2A_MSIL1C_20180819T100019_N0206_R122_T32TQR_20180819T141300')


def test_s2_get_relative_path():
    validator = S2L1CValidator()
    assert 'S2A_OPER_PRD_MSIL1C_PDMC_20150714T123646_R019_V20150704T102427_20150704T102427.SAFE' \
           == validator.get_relative_path(VALID_S2_PATH)
    assert 'S2B_MSIL1C_20180819T100019_N0206_R122_T32TQR_20180819T141300' \
           == validator.get_relative_path(ANOTHER_VALID_S2_PATH)


def test_s2_get_file_pattern():
    validator = S2L1CValidator()
    assert '(S2A|S2B|S2_)_(([A-Z|0-9]{4})_[A-Z|0-9|_]{4})?([A-Z|0-9|_]{6})_(([A-Z|0-9|_]{4})_)?([0-9]{8}T[0-9]{6})_.*.(SAFE)?' \
           == validator.get_file_pattern()


def test_s2_is_valid_for():
    validator = S2L1CValidator()
    assert validator.is_valid_for(VALID_S2_PATH, Polygon(), datetime(2015, 7, 13), datetime(2015, 7, 15))
    assert not validator.is_valid_for(VALID_S2_PATH, Polygon(), datetime(2015, 7, 12), datetime(2015, 7, 13))
    assert not validator.is_valid_for(VALID_S2_PATH, Polygon(), datetime(2015, 7, 15), datetime(2015, 7, 16))
    assert validator.is_valid_for(ANOTHER_VALID_S2_PATH, Polygon(), datetime(2018, 8, 18), datetime(2018, 8, 20))
    assert not validator.is_valid_for(ANOTHER_VALID_S2_PATH, Polygon(), datetime(2018, 8, 17), datetime(2018, 8, 18))
    assert not validator.is_valid_for(ANOTHER_VALID_S2_PATH, Polygon(), datetime(2018, 8, 20), datetime(2018, 8, 21))


def test_s2l2_validator_name():
    validator = S2L2Validator()
    assert 'S2_L2' == validator.name()


def test_s2l2_is_valid():
    validator = S2L2Validator()
    assert validator.is_valid(VALID_S2L2_PATH)
    assert validator.is_valid(ANOTHER_VALID_S2L2_PATH)
    assert not validator.is_valid('S2A_MSIL1C_20170605T105031_N0205_R051_T30SWJ_20170605T105303-ac')
    assert not validator.is_valid(
        './test/test_data/S2B_MSIL1C_20170605T105031_N0205_R051_T30SWJ_20170605T105303-ac')
    assert not validator.is_valid(VALID_S2_PATH)
    assert not validator.is_valid(ANOTHER_VALID_S2_PATH)


def test_s2l2_get_relative_path():
    validator = S2L2Validator()
    assert 'S2A_MSIL1C_20170605T105031_N0205_R051_T30SWJ_20170605T105303-ac' \
           == validator.get_relative_path(VALID_S2L2_PATH)

def test_s2l2_get_file_pattern():
    validator = S2L2Validator()
    assert '(S2A|S2B|S2_)_(([A-Z|0-9]{4})_[A-Z|0-9|_]{4})?([A-Z|0-9|_]{6})_(([A-Z|0-9|_]{4})_)?([0-9]{8}T[0-9]{6})_.*.(SAFE)?-ac' \
           == validator.get_file_pattern()


def test_s2l2_is_valid_for():
    validator = S2L2Validator()
    assert validator.is_valid_for(VALID_S2L2_PATH, Polygon(), datetime(2017, 6, 4), datetime(2017, 6, 6))
    assert not validator.is_valid_for(VALID_S2L2_PATH, Polygon(), datetime(2017, 6, 3), datetime(2017, 6, 4))
    assert not validator.is_valid_for(VALID_S2L2_PATH, Polygon(), datetime(2017, 6, 6), datetime(2017, 6, 7))


def test_modis_mcd_43_validator_is_valid():
    validator = ModisMCD43Validator()

    assert validator.is_valid('MCD43A1.A2017250.h17v05.006.2017261201257.hdf')
    assert validator.is_valid('MCD43A1.A2017250.h17v05.006.herebesomething.hdf')
    assert validator.is_valid('MCD43A1.A2001001.h00v00.006.herebesomething.hdf')
    assert validator.is_valid('MCD43A1.A2017365.h35v17.006.herebesomething.hdf')
    assert validator.is_valid('MCD43A1.A2016366.h35v17.006.herebesomething.hdf')
    assert validator.is_valid('some/path/MCD43A1.A2016366.h35v17.006.herebesomething.hdf')
    assert not validator.is_valid('MCD43A1.A1999275.h35v17.006.herebesomething.hdf')
    assert not validator.is_valid('MCD43A1.A2002475.h35v17.006.herebesomething.hdf')
    assert not validator.is_valid('MCD43A1.A2002275.h40v17.006.herebesomething.hdf')
    assert not validator.is_valid('MCD43A1.A2002275.h10v20.006.herebesomething.hdf')


def test_modis_mcd_15_validator_name():
    validator = ModisMCD15A2HValidator()

    assert 'MCD15A2H.006' == validator.name()


def test_modis_mcd_15_validator_is_valid():
    validator = ModisMCD15A2HValidator()

    assert validator.is_valid('MCD15A2H.A2017250.h17v05.006.2017261201257.hdf')
    assert validator.is_valid('MCD15A2H.A2017250.h17v05.006.herebesomething.hdf')
    assert validator.is_valid('MCD15A2H.A2001001.h00v00.006.herebesomething.hdf')
    assert validator.is_valid('MCD15A2H.A2017365.h35v17.006.herebesomething.hdf')
    assert validator.is_valid('MCD15A2H.A2016366.h35v17.006.herebesomething.hdf')
    assert validator.is_valid('some/path/MCD15A2H.A2016366.h35v17.006.herebesomething.hdf')
    assert not validator.is_valid('MCD15A2H.A1999275.h35v17.006.herebesomething.hdf')
    assert not validator.is_valid('MCD15A2H.A2002475.h35v17.006.herebesomething.hdf')
    assert not validator.is_valid('MCD15A2H.A2002275.h40v17.006.herebesomething.hdf')
    assert not validator.is_valid('MCD15A2H.A2002275.h10v20.006.herebesomething.hdf')


def test_modis_mcd_15_validator_get_relative_path():
    validator = ModisMCD15A2HValidator()

    assert '' == validator.get_relative_path('some/path/MCD15A2H.A2016366.h35v17.006.herebesomething.hdf')


def test_modis_mcd_15_validator_get_file_pattern():
    validator = ModisMCD15A2HValidator()

    assert 'MCD15A2H.A20[0-9][0-9][0-3][0-9][0-9].h[0-3][0-9]v[0-1][0-9].006.*.hdf' == validator.get_file_pattern()


def test_cams_tiff_name():
    validator = CamsTiffValidator()
    assert 'CAMS_TIFF' == validator.name()


def test_cams_tiff_is_valid():
    validator = CamsTiffValidator()

    assert validator.is_valid(VALID_CAMS_TIFF_DATA)
    assert not validator.is_valid('./test/test_data/2018_10_24/')


def test_cams_tiff_validator_get_relative_path():
    validator = CamsTiffValidator()

    assert '2016_04_21' == validator.get_relative_path('/the/non/relative/part/2016_04_21/')


def test_cams_tiff_get_file_pattern():
    validator = CamsTiffValidator()

    assert '20[0-9][0-9]_[0-1][0-9]_[0-3][0-9]' == validator.get_file_pattern()


def test_cams_tiff_is_valid_for():
    validator = CamsTiffValidator()

    assert validator.is_valid_for(VALID_CAMS_TIFF_DATA, Polygon(), datetime(2018, 10, 20), datetime(2018, 10, 25))
    assert not validator.is_valid_for(VALID_CAMS_TIFF_DATA, Polygon(), datetime(2018, 10, 20), datetime(2018, 10, 22))
    assert not validator.is_valid_for('/some/path/2016-09-14', Polygon(), datetime(2016, 9, 1), datetime(2016, 9, 10))


def test_cams_name():
    validator = CamsValidator()
    assert 'CAMS' == validator.name()


def test_cams_is_valid():
    validator = CamsValidator()

    assert validator.is_valid('2017-09-14.nc')
    assert validator.is_valid('/some/path/2017-09-14.nc')
    assert not validator.is_valid('2017-09-14')
    assert not validator.is_valid('1000-29-34.nc')


def test_cams_get_file_pattern():
    validator = CamsValidator()

    assert '20[0-9][0-9]-[0-1][0-9]-[0-3][0-9].nc' == validator.get_file_pattern()


def test_cams_is_valid_for():
    validator = CamsValidator()

    assert validator.is_valid_for('2017-09-14.nc', Polygon(), datetime(2017, 9, 14), datetime(2017, 9, 14))
    assert validator.is_valid_for('2017-09-14.nc', Polygon(), datetime(2017, 9, 13), datetime(2017, 9, 15))
    assert validator.is_valid_for('/some/path/2017-09-14.nc', Polygon(), datetime(2017, 9, 13), datetime(2017, 9, 15))
    assert not validator.is_valid_for('2017-09-14.nc', Polygon(), datetime(2017, 9, 10), datetime(2017, 9, 12))


def test_s2a_emulator_name():
    validator = S2AEmulatorValidator()

    assert 'ISO_MSI_A_EMU' == validator.name()


def test_s2a_is_valid():
    validator = S2AEmulatorValidator()

    assert validator.is_valid('isotropic_MSI_emulators_correction_xap_S2A.pkl')
    assert validator.is_valid('isotropic_MSI_emulators_correction_xbp_S2A.pkl')
    assert validator.is_valid('isotropic_MSI_emulators_correction_xcp_S2A.pkl')
    assert validator.is_valid('isotropic_MSI_emulators_optimization_xap_S2A.pkl')
    assert validator.is_valid('isotropic_MSI_emulators_optimization_xbp_S2A.pkl')
    assert validator.is_valid('isotropic_MSI_emulators_optimization_xcp_S2A.pkl')
    assert validator.is_valid('/some/path/isotropic_MSI_emulators_optimization_xcp_S2A.pkl')
    assert not validator.is_valid('isotropic_MSI_emulators_optimization_xdp_S2A.pkl')


def test_s2a_get_file_pattern():
    validator = S2AEmulatorValidator()

    assert 'isotropic_MSI_emulators_(?:correction|optimization)_x[a|b|c]p_S2A.pkl' == validator.get_file_pattern()


def test_s2b_emulator_name():
    validator = S2BEmulatorValidator()

    assert 'ISO_MSI_B_EMU' == validator.name()


def test_s2b_is_valid():
    validator = S2BEmulatorValidator()

    assert validator.is_valid('isotropic_MSI_emulators_correction_xap_S2B.pkl')
    assert validator.is_valid('isotropic_MSI_emulators_correction_xbp_S2B.pkl')
    assert validator.is_valid('isotropic_MSI_emulators_correction_xcp_S2B.pkl')
    assert validator.is_valid('isotropic_MSI_emulators_optimization_xap_S2B.pkl')
    assert validator.is_valid('isotropic_MSI_emulators_optimization_xbp_S2B.pkl')
    assert validator.is_valid('isotropic_MSI_emulators_optimization_xcp_S2B.pkl')
    assert validator.is_valid('/some/path/isotropic_MSI_emulators_optimization_xcp_S2B.pkl')
    assert not validator.is_valid('isotropic_MSI_emulators_optimization_xdp_S2B.pkl')


def test_s2b_get_file_pattern():
    validator = S2BEmulatorValidator()

    assert 'isotropic_MSI_emulators_(?:correction|optimization)_x[a|b|c]p_S2B.pkl' == validator.get_file_pattern()


def test_wv_emulator_name():
    validator = WVEmulatorValidator()

    assert 'WV_EMU' == validator.name()


def test_wv_is_valid():
    validator = WVEmulatorValidator()

    assert validator.is_valid('wv_MSI_retrieval_S2A.pkl')
    assert validator.is_valid('wv_MSI_retrieval_S2A.pkl')
    assert validator.is_valid('/some/path/wv_MSI_retrieval_S2A.pkl')
    assert not validator.is_valid('wv_MSI_ratrieval_S2A.pkl')


def test_wv_get_file_pattern():
    validator = WVEmulatorValidator()

    assert 'wv_MSI_retrieval_S2A.pkl' == validator.get_file_pattern()


def test_aster_name():
    validator = AsterValidator()

    assert 'ASTER' == validator.name()


def test_aster_is_valid():
    validator = AsterValidator()

    assert validator.is_valid('ASTGTM2_N00E000_dem.tif')
    assert validator.is_valid('ASTGTM2_S11W111_dem.tif')
    assert validator.is_valid('/some/path/ASTGTM2_S11W111_dem.tif')
    assert not validator.is_valid('ASTGTM2_W11S111_dem.tif')
    assert not validator.is_valid('ASTGTM2_N90E200_dem.tif')


def test_aster_get_file_pattern():
    validator = AsterValidator()

    assert 'ASTGTM2_[N|S][0-8][0-9][E|W][0|1][0-9][0-9]_dem.tif' == validator.get_file_pattern()


def test_aster_is_valid_for():
    validator = AsterValidator()

    polygon = loads('POLYGON((134.20 12.09, 133.91 12.09, 133.91 11.94, 134.2 11.94, 134.20 12.09))')
    assert validator.is_valid_for('ASTGTM2_N12E134_dem.tif', polygon, datetime(1000, 1, 1), datetime(1000, 1, 3))
    assert validator.is_valid_for('ASTGTM2_N11E134_dem.tif', polygon, datetime(1000, 1, 1), datetime(1000, 1, 3))
    assert validator.is_valid_for('ASTGTM2_N11E133_dem.tif', polygon, datetime(1000, 1, 1), datetime(1000, 1, 3))
    assert validator.is_valid_for('ASTGTM2_N12E133_dem.tif', polygon, datetime(1000, 1, 1), datetime(1000, 1, 3))
    assert validator.is_valid_for('/some/path/ASTGTM2_N12E133_dem.tif', polygon, datetime(1000, 1, 1),
                                  datetime(1000, 1, 3))
    assert not validator.is_valid_for('ASTGTM2_N13E133_dem.tif', polygon, datetime(1000, 1, 1), datetime(1000, 1, 3))


def test_variable_validator_name():
    validator = VariableValidator('cvgfs')

    assert 'cvgfs' == validator.name()


def test_variable_validator_is_valid():
    validator = VariableValidator('cvgfs')

    assert validator.is_valid('s2_cvgfs_A2018-05-10.tif')
    assert validator.is_valid('something/something/cvgfs_A2017111.tif')
    assert validator.is_valid('cvgfs_A2017111.tif')
    assert not validator.is_valid('something/something/cvfgfs_A2017111.tif')
    assert not validator.is_valid('something/something/cvgfs_A2017111.jpg')
    assert not validator.is_valid('something/something/cvgfs_A2017400.tif')
    assert validator.is_valid('something/cvgfs_20171010.tif')
    assert validator.is_valid('something/cvgfs_20171010_20171011.tif')


def test_variable_validator_get_relative_path():
    validator = VariableValidator('cvgfs')

    assert '' == validator.get_relative_path('something/something/cvgfs_A2017111.tif')


def test_variable_validator_get_file_pattern():
    validator = VariableValidator('cvgfs')

    assert '.*cvgfs_(A)?20[0-9][0-9](-)?([0-3][0-9][0-9]|[0-1][0-9](-)?[0-3][0-9]|' \
           '[0-1][0-9](-)?[0-3][0-9]_20[0-9][0-9](-)?[0-1][0-9](-)?[0-3][0-9]).tif' == validator.get_file_pattern()


def test_variable_validator_is_valid_for():
    validator = VariableValidator('cvgfs')

    polygon = loads('POLYGON((134.20 12.09, 133.91 12.09, 133.91 11.94, 134.2 11.94, 134.20 12.09))')

    assert validator.is_valid_for('st/cvgfs_A2017111.tif', polygon, datetime(2017, 4, 20), datetime(2017, 4, 22))
    assert not validator.is_valid_for('st/cvgfs_A2017111.tif', polygon, datetime(2017, 4, 22), datetime(2017, 4, 23))
    assert not validator.is_valid_for('st/cvgfs_A2017111.tif', polygon, datetime(2017, 4, 19), datetime(2017, 4, 20))
    assert validator.is_valid_for('st/cvgfs_20171011.tif', polygon, datetime(2017, 10, 10), datetime(2017, 10, 12))
    assert not validator.is_valid_for('st/cvgfs_20171011.tif', polygon, datetime(2017, 10, 12), datetime(2017, 10, 13))
    assert not validator.is_valid_for('st/cvgfs_20171011.tif', polygon, datetime(2017, 10, 9), datetime(2017, 10, 10))

    assert validator.is_valid_for('st/cvgfs_20171011_20171012.tif',
                                  polygon, datetime(2017, 10, 10), datetime(2017, 10, 13))
    assert validator.is_valid_for('st/cvgfs_20171011_20171012.tif',
                                  polygon, datetime(2017, 10, 10), datetime(2017, 10, 11))
    assert validator.is_valid_for('st/cvgfs_20171011_20171012.tif',
                                  polygon, datetime(2017, 10, 12), datetime(2017, 10, 14))

    assert not validator.is_valid_for('st/cvgfs_20171011_20171012.tif',
                                      polygon, datetime(2017, 10, 9), datetime(2017, 10, 10))
    assert not validator.is_valid_for('st/cvgfs_20171011_20171012.tif',
                                      polygon, datetime(2017, 10, 13), datetime(2017, 10, 14))


def test_get_valid_types():
    valid_types = get_valid_types()

    assert 12 <= len(valid_types)
    assert 'AWS_S2_L1C' in valid_types
    assert 'AWS_S2_L2' in valid_types
    assert 'MCD43A1.006' in valid_types
    assert 'MCD15A2H.006' in valid_types
    assert 'CAMS' in valid_types
    assert 'CAMS_TIFF' in valid_types
    assert 'ISO_MSI_A_EMU' in valid_types
    assert 'ISO_MSI_B_EMU' in valid_types
    assert 'WV_EMU' in valid_types
    assert 'ASTER' in valid_types
    assert 'S2_L1C' in valid_types
    assert 'S2_L2' in valid_types
