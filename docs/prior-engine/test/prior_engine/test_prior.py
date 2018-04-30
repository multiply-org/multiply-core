# import sys
import os
import pytest
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(myPath + '/../../multiply_prior_engine/')
from multiply_prior_engine.prior import Prior
from multiply_prior_engine.prior_engine import PriorEngine
from multiply_prior_engine.soilmoisture_prior import SoilMoisturePrior


def test_priorengine_init():
    P = PriorEngine(config='./test/prior_engine/test_config_prior.yml',
                    datestr='2017-01-01',
                    variables=['sm'])

    assert P.configfile is not None
    assert type(P.configfile) is str
    # assert type(P.priors) is dict


def test_priorengine_get_priors():
    P = PriorEngine(config='./test/prior_engine/test_config_prior.yml',
                    datestr='2017-01-01',
                    variables=['sm'])
    assert type(P.get_priors()) is dict


def test_sm_prior_init():
    with pytest.raises(AssertionError,
                       message=("Expecting AssertionError \
                                --> no config specified")):
        SoilMoisturePrior()


def test_sm_prior_no_ptype():
    with pytest.raises(AssertionError,
                       message=("Expecting AssertionError \
                                --> no config specified")):
        SoilMoisturePrior()


def test_sm_prior_invalid_ptype():
    with pytest.raises(AssertionError,
                       message=("Expecting AssertionError \
                                --> no config specified")):
        SoilMoisturePrior(ptype='climatologi')


def test_calc_config():
    P = PriorEngine(config='./test/prior_engine/test_config_prior.yml',
                    datestr='2017-01-01',
                    variables=['sm'])
    S = SoilMoisturePrior(config=P.config,
                          ptype='climatology')
    assert type(S.config) is dict



# def test_roughness():
#     lut_file = tempfile.mktemp(suffix='.lut')
#    lc_file = tempfile.mktemp(suffix='.nc')
#     gen_file(lut_file)
#     gen_file(lc_file)
#     P = RoughnessPrior(ptype='climatology',
#                        lut_file=lut_file,
#                        lc_file=lc_file)
