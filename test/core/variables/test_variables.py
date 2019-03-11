from multiply_core.variables import get_registered_variable, get_registered_variables, Variable

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


def test_create_variable_from_dict():
    dict_variables = {'short_name': 'rtfgt6', 'display_name': 'cgfyg', 'unit': 'sdfew', 'description': 'rgwdrfeb',
                      'range': 'tvfegz', 'applications': ['cvgzrf', 'twrfg', 'dtft']}
    variable = Variable(dict_variables)

    assert not variable is None
    assert 'rtfgt6' == variable.short_name
    assert 'cgfyg' == variable.display_name
    assert 'sdfew' == variable.unit
    assert 'rgwdrfeb' == variable.description
    assert 'tvfegz' == variable.range
    assert 3 == len(variable.applications)
    assert 'cvgzrf' == variable.applications[0]
    assert 'twrfg' == variable.applications[1]
    assert 'dtft' == variable.applications[2]


def test_get_registered_variables():
    variables = get_registered_variables()
    assert len(variables) > 0


def test_get_registered_variable():
    variable = get_registered_variable('')
    assert variable is None
    variable = get_registered_variable('rvghhz')
    assert variable is None
    variable = get_registered_variable('h')
    assert 'h' == variable.short_name
    assert 'hotspot parameter' == variable.display_name
