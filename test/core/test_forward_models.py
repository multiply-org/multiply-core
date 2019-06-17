from multiply_core.models.forward_models import _read_forward_model

import pytest

PATH_TO_TEST_FORWARD_MODEL_FILE = './test/test_data/metadata.json'


def test_read_forward_model():
    forward_model = _read_forward_model(PATH_TO_TEST_FORWARD_MODEL_FILE)

    assert 's2_prosail' == forward_model.id
    assert 'PROSAIL for Sentinel-2' == forward_model.name
    assert 'Coupling of PROSPECT leaf optical properties model and SAIL canopy bidirectional reflectance model. ' \
           'It links the spectral variation of canopy reflectance, which is mainly related to leaf biochemical ' \
           'contents, with its directional variation, which is primarily related to canopy architecture and ' \
           'soil/vegetation contrast.' == forward_model.description
    assert '' == forward_model.authors
    assert 'http://teledetection.ipgp.jussieu.fr/prosail/' == forward_model.url
    assert 'S2_L1C' == forward_model.input_type
    expected_variables = ["n", "cab", "car", "cb", "cw", "cdm", "lai", "ala", "bsoil", "psoil"]
    assert all([a == b for a, b in zip(forward_model.variables, expected_variables)])
