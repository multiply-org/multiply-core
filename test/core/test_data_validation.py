from multiply_core.observations.data_validation import AWSS2L1Validator, ModisMCD43Validator, get_valid_types

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

VALID_AWS_S2_DATA = './test/test_data/s2_aws/15/F/ZX/2016/12/31/1'


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


def test_modis_mcd_43_validator_is_valid():
    validator = ModisMCD43Validator()

    assert validator.is_valid('MCD43A1.A2017250.h17v05.006.2017261201257.hdf')
    assert validator.is_valid('MCD43A1.A2017250.h17v05.006.herebesomething.hdf')
    assert validator.is_valid('MCD43A1.A2001001.h00v00.006.herebesomething.hdf')
    assert validator.is_valid('MCD43A1.A2017365.h35v17.006.herebesomething.hdf')
    assert validator.is_valid('MCD43A1.A2016366.h35v17.006.herebesomething.hdf')
    assert not validator.is_valid('MCD43A1.A1999275.h35v17.006.herebesomething.hdf')
    assert not validator.is_valid('MCD43A1.A2002475.h35v17.006.herebesomething.hdf')
    assert not validator.is_valid('MCD43A1.A2002275.h40v17.006.herebesomething.hdf')
    assert not validator.is_valid('MCD43A1.A2002275.h10v20.006.herebesomething.hdf')


def test_get_valid_types():
    valid_types = get_valid_types()

    assert 3 == len(valid_types)
    assert 'AWS_S2_L1C' == valid_types[0]
    assert 'AWS_S2_L2' == valid_types[1]
    assert 'MCD43A1.006' == valid_types[2]

