import numpy as np
import os
import re
import scipy.sparse as sp

from multiply_core.util import FileRef
from multiply_core.observations import ObservationData, ProductObservations, ProductObservationsCreator, ObservationsFactory

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

DUMMY_FILE = './test/test_data/dfghztm_2018_dvfgbh'


def test_sort_file_ref_list():
    file_refs = [FileRef(url='loc1', start_time='2017-06-04', end_time='2017-06-07', mime_type='unknown mime type'),
                 FileRef(url='loc2', start_time='2017-06-01', end_time='2017-06-06', mime_type='unknown mime type'),
                 FileRef(url='loc3', start_time='2017-06-03', end_time='2017-06-10', mime_type='unknown mime type'),
                 FileRef(url='loc4', start_time='2017-06-02', end_time='2017-06-09', mime_type='unknown mime type'),
                 FileRef(url='loc5', start_time='2017-06-05', end_time='2017-06-08', mime_type='unknown mime type')]
    observations_factory = ObservationsFactory()
    observations_factory.sort_file_ref_list(file_refs)
    assert 5, len(file_refs)
    assert 'loc2', file_refs[0]
    assert 'loc4', file_refs[1]
    assert 'loc3', file_refs[2]
    assert 'loc1', file_refs[3]
    assert 'loc5', file_refs[4]


def test_create_observations():

    class DummyObservations(ProductObservations):

        def get_band_data(self, band_index: int) -> ObservationData:
            return ObservationData(observations=np.array([0.5]), uncertainty=sp.lil_matrix((1, 1)), mask=np.array([0]),
                                   metadata={}, emulator=None)

        @property
        def bands_per_observation(self):
            return 15

    class DummyObservationsCreator(ProductObservationsCreator):
        DUMMY_PATTERN = 'dfghztm_[0-9]{4}_dvfgbh'
        DUMMY_PATTERN_MATCHER = re.compile('dfghztm_[0-9]{4}_dvfgbh')

        @classmethod
        def can_read(cls, file_ref: FileRef) -> bool:
            if os.path.exists(file_ref.url):
                file = open(file_ref.url, 'r')
                return cls.DUMMY_PATTERN_MATCHER.search(file.name) is not None

        @classmethod
        def create_observations(cls, file_ref: FileRef) -> ProductObservations:
            if cls.can_read(file_ref):
                return DummyObservations()
    observations_factory = ObservationsFactory()
    observations_factory.add_observations_creator_to_registry(DummyObservationsCreator())
    file_refs = [FileRef(url=DUMMY_FILE, start_time='2017-06-04', end_time='2017-06-07', mime_type='unknown mime type'),
                 FileRef(url='tzzg', start_time='2017-06-04', end_time='2017-06-07', mime_type='unknown mime type')]
    observations_wrapper = observations_factory.create_observations(file_refs)

    assert 1, observations_wrapper.get_num_observations()
    assert 15, observations_wrapper.bands_per_observation(0)
    data = observations_wrapper.get_band_data(0, 0)
    assert 1, len(data.observations)
    assert 0.5, data.observations[0]
