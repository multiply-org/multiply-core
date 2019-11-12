import os

from multiply_core.util.aux_data_provider import DefaultAuxDataProvider

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


TEST_DATA_PATH = './test/test_data/2018_10_23/'


def test_list_elements():
    provider = DefaultAuxDataProvider()
    elements = provider.list_elements(TEST_DATA_PATH)
    assert 6 == len(elements)
    assert './test/test_data/2018_10_23\\2018_10_23_aod550.tif' in elements
    assert './test/test_data/2018_10_23\\2018_10_23_bcaod550.tif' in elements
    assert './test/test_data/2018_10_23\\2018_10_23_duaod550.tif' in elements
    assert './test/test_data/2018_10_23\\2018_10_23_gtco3.tif' in elements
    assert './test/test_data/2018_10_23\\2018_10_23_omaod550.tif' in elements
    assert './test/test_data/2018_10_23\\2018_10_23_suaod550.tif' in elements


def test_list_elements_with_pattern():
    provider = DefaultAuxDataProvider()
    elements = provider.list_elements(TEST_DATA_PATH, '*uaod*.tif')
    assert 2 == len(elements)
    assert './test/test_data/2018_10_23\\2018_10_23_duaod550.tif' in elements
    assert './test/test_data/2018_10_23\\2018_10_23_suaod550.tif' in elements


def test_assure_element_provided():
    provider = DefaultAuxDataProvider()
    provided = provider.assure_element_provided('./test/test_data/2018_10_23\\2018_10_23_duaod550.tif')
    assert provided
    assert os.path.exists('./test/test_data/2018_10_23\\2018_10_23_duaod550.tif')


def test_assure_element_provided_not():
    provider = DefaultAuxDataProvider()
    provided = provider.assure_element_provided('./test/test_data/2018_10_23\\2018_10_23_dumaod550.tif')
    assert not provided
    assert not os.path.exists('./test/test_data/2018_10_23\\2018_10_23_dumaod550.tif')
