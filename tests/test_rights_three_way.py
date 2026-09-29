"""The three independent rights/soft regeneration paths agree on fixture shapes."""

from conformance.rights_three_way import run


def test_rights_three_way_fixtures():
    assert run()["passed"] == 9
