from multiply_core.util.file_ref_creation import FileRefCreation, S2L2FileRefCreator, VariableFileRefCreator

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


PATH_TO_S2_L2_FILE = './test/test_data/S2A_MSIL1C_20170605T105031_N0205_R051_T30SWJ_20170605T105303-ac'


def test_s2l2_file_ref_creator_name():
    file_ref_creator = S2L2FileRefCreator()

    assert 'S2_L2' == file_ref_creator.name()


def test_s2l2_file_ref_creator_create_file_ref():
    file_ref_creator = S2L2FileRefCreator()


    file_ref = file_ref_creator.create_file_ref(PATH_TO_S2_L2_FILE)

    assert file_ref is not None
    assert PATH_TO_S2_L2_FILE == file_ref.url
    assert '2017-06-05T10:50:31' == file_ref.start_time
    assert '2017-06-05T10:50:31' == file_ref.end_time
    assert 'application/x-directory' == file_ref.mime_type


def test_file_ref_creation_get_s2l2_file_ref():
    file_ref_creation = FileRefCreation()   # FileRefCreation contains S2L2Creator by default, no need to add it

    file_ref = file_ref_creation.get_file_ref('S2_L2', PATH_TO_S2_L2_FILE)

    assert file_ref is not None
    assert PATH_TO_S2_L2_FILE == file_ref.url
    assert '2017-06-05T10:50:31' == file_ref.start_time
    assert '2017-06-05T10:50:31' == file_ref.end_time
    assert 'application/x-directory' == file_ref.mime_type


def test_variable_file_ref_creator_name():
    file_ref_creator = VariableFileRefCreator('ascrtvg')

    assert 'ascrtvg' == file_ref_creator.name()


def test_variable_file_ref_creator_create_file_ref():
    file_ref_creator = VariableFileRefCreator('dzfgj')

    file_ref = file_ref_creator.create_file_ref('something/dzfgj_A2000001.tif')

    assert file_ref is not None
    assert 'something/dzfgj_A2000001.tif' == file_ref.url
    assert '2000-01-01' == file_ref.start_time
    assert '2000-01-01' == file_ref.end_time
    assert 'image/tiff' == file_ref.mime_type


def test_file_ref_creation_get_variable_file_ref():
    file_ref_creation = FileRefCreation()
    file_ref_creation.add_file_ref_creator(VariableFileRefCreator('zfegth'))

    file_ref = file_ref_creation.get_file_ref('zfegth', 'something/zfegth_A2000001.tif')

    assert file_ref is not None
    assert 'something/zfegth_A2000001.tif' == file_ref.url
    assert '2000-01-01' == file_ref.start_time
    assert '2000-01-01' == file_ref.end_time
    assert 'image/tiff' == file_ref.mime_type
