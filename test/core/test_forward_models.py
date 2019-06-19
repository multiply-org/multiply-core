import os

from multiply_core.models.forward_models import _get_forward_models, _read_forward_model, _register_forward_model

PATH_TO_A_FORWARD_MODEL_REGISTRY_FILE = './test/test_data/a_forward_model_registry.txt'
PATH_TO_A_FORWARD_MODEL_METADATA_FILE = './test/test_data/metadata.json'
PATH_TO_ANOTHER_FORWARD_MODEL_METADATA_FILE = './test/test_data/another_meta_data.json'
PATH_TO_ANOTHER_FORWARD_MODEL_REGISTRY_FILE = './test/test_data/another_forward_model_registry.txt'


def test_get_forward_models():
    forward_models = _get_forward_models(PATH_TO_A_FORWARD_MODEL_REGISTRY_FILE)

    assert 1 == len(forward_models)
    assert 's2_prosail' == forward_models[0].id
    assert 'PROSAIL for Sentinel-2' == forward_models[0].name
    assert 'Coupling of PROSPECT leaf optical properties model and SAIL canopy bidirectional reflectance model. ' \
           'It links the spectral variation of canopy reflectance, which is mainly related to leaf biochemical ' \
           'contents, with its directional variation, which is primarily related to canopy architecture and ' \
           'soil/vegetation contrast.' == forward_models[0].description
    assert '' == forward_models[0].authors
    assert 'http://teledetection.ipgp.jussieu.fr/prosail/' == forward_models[0].url
    assert 'S2_L1C' == forward_models[0].input_type
    expected_variables = ["n", "cab", "car", "cb", "cw", "cdm", "lai", "ala", "bsoil", "psoil"]
    assert all([a == b for a, b in zip(forward_models[0].variables, expected_variables)])


def test_read_forward_model():
    forward_model = _read_forward_model(PATH_TO_A_FORWARD_MODEL_METADATA_FILE)

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


def test_register_forward_model():
    try:
        _register_forward_model(PATH_TO_ANOTHER_FORWARD_MODEL_METADATA_FILE, PATH_TO_ANOTHER_FORWARD_MODEL_REGISTRY_FILE)
        _register_forward_model(PATH_TO_A_FORWARD_MODEL_METADATA_FILE, PATH_TO_ANOTHER_FORWARD_MODEL_REGISTRY_FILE)

        forward_models = _get_forward_models(PATH_TO_ANOTHER_FORWARD_MODEL_REGISTRY_FILE)

        assert 2 == len(forward_models)
        assert 'another_model' == forward_models[0].id
        assert 'Another model for a made up data type' == forward_models[0].name
        assert 'No words. No words.' == forward_models[0].description
        assert '' == forward_models[0].authors
        assert 'http://frgdtgeh.io' == forward_models[0].url
        assert 'a made up data type' == forward_models[0].input_type
        expected_variables = ["n"]
        assert all([a == b for a, b in zip(forward_models[0].variables, expected_variables)])

        assert 's2_prosail' == forward_models[1].id
        assert 'PROSAIL for Sentinel-2' == forward_models[1].name
        assert 'Coupling of PROSPECT leaf optical properties model and SAIL canopy bidirectional reflectance model. ' \
               'It links the spectral variation of canopy reflectance, which is mainly related to leaf biochemical ' \
               'contents, with its directional variation, which is primarily related to canopy architecture and ' \
               'soil/vegetation contrast.' == forward_models[1].description
        assert '' == forward_models[1].authors
        assert 'http://teledetection.ipgp.jussieu.fr/prosail/' == forward_models[1].url
        assert 'S2_L1C' == forward_models[1].input_type
        expected_variables = ["n", "cab", "car", "cb", "cw", "cdm", "lai", "ala", "bsoil", "psoil"]
        assert all([a == b for a, b in zip(forward_models[1].variables, expected_variables)])

    finally:
        if os.path.exists(PATH_TO_ANOTHER_FORWARD_MODEL_REGISTRY_FILE):
            os.remove(PATH_TO_ANOTHER_FORWARD_MODEL_REGISTRY_FILE)
