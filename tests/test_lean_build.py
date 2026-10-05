"""`tests/lean_build.py`: a fixture naming a Lean target the lakefile lacks fails, prebuilt or not."""
from __future__ import annotations

import pytest

from tests import lean_build as module
from tests.lean_build import UnknownTarget, check_targets, lean_build, lean_targets


@pytest.mark.parametrize("prebuilt", ["", "1"])
def test_a_deleted_target_fails_before_any_build(monkeypatch, prebuilt):
    """lf-1 review C: `ve_norms_route` was deleted in batch 1 but still named by a fixture, which
    only prebuilt (gate) runs skipped past."""
    monkeypatch.setenv("VE_LEAN_PREBUILT", prebuilt)
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: pytest.fail("lake ran"))
    with pytest.raises(UnknownTarget, match="ve_norms_route"):
        lean_build("ve_service", "ve_norms_route")


def test_targets_are_the_lakefiles(tmp_path):
    lakefile = tmp_path / "lakefile.toml"
    lakefile.write_text('defaultTargets = ["A"]\n[[lean_lib]]\nname = "A"\n[[lean_exe]]\nname = "a_exe"\nroot = "A"\n')
    assert lean_targets(lakefile) == {"A": "lean_lib", "a_exe": "lean_exe"}
    assert check_targets(["a_exe"], lakefile) == {"a_exe": "lean_exe"}
    with pytest.raises(UnknownTarget):
        check_targets(["a_exe", "b_exe"], lakefile)


def test_the_service_and_its_test_tools_are_targets():
    assert {"ve_service", "ve_conformance", "ve_english_run", "ve_response_decode"} <= set(lean_targets())
