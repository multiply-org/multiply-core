from multiply_core.updates import _is_newer_than


def test_is_newer_than():
    assert _is_newer_than('v0.4', 'v0.3')
    assert not _is_newer_than('v0.4', 'v0.4')
    assert not _is_newer_than('v0.4', 'v0.5')
    assert _is_newer_than('v0.4.1', 'v0.4')
    assert not _is_newer_than('v0.4.1', 'v0.4.1')
    assert not _is_newer_than('v0.4.1', 'v0.4.2')
    assert _is_newer_than('v0.4', 'v0.3.2')
    assert _is_newer_than('v1', 'v0.4.2')
    assert not _is_newer_than('v1.4.2', 'v2')
