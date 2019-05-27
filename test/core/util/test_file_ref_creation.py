from multiply_core.util.file_ref_creation import FileRefCreation, VariableFileRefCreator

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


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


def test_file_ref_creation_get_file_ref():
    file_ref_creation = FileRefCreation()
    file_ref_creation.add_file_ref_creator(VariableFileRefCreator('zfegth'))

    file_ref = file_ref_creation.get_file_ref('zfegth', 'something/zfegth_A2000001.tif')

    assert file_ref is not None
    assert 'something/zfegth_A2000001.tif' == file_ref.url
    assert '2000-01-01' == file_ref.start_time
    assert '2000-01-01' == file_ref.end_time
    assert 'image/tiff' == file_ref.mime_type
