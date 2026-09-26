import pytest

from ve.adapters.gatekeeper import is_exempt, tables
from ve.errors import VEError


def test_gatekeeper_exemption_uses_verified_globs():
    patterns = ["registry.example/*", "*/trusted:v1"]
    records = tables(patterns, ["registry.example/a:v2", "other/trusted:v1", "other/a:v1"])
    assert is_exempt("registry.example/a:v2", patterns, records).value is True
    assert is_exempt("other/trusted:v1", patterns, records).value is True
    assert is_exempt("other/a:v1", patterns, records).value is False
    assert is_exempt("other/a:v1", patterns, None).value is None
    with pytest.raises(VEError, match="outside"):
        is_exempt("unknown:v1", patterns, records)
    changed = (records[1], records[0])
    with pytest.raises(VEError, match="different glob"):
        is_exempt("other/a:v1", patterns, changed)
