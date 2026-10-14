"""Constant display words are outside the readings pilot's v0 vocabulary shape."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from ve.environment import Environment
from ve.errors import VEError


def _environment(profiles):
    return {"language": "ve.core@0.2", "profiles": profiles,
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"person": {"description": "person"}}, "predicates": {},
                           "constants": {"alice": {"sort": "person", "description": "Alice"}}}}


def test_readings_constant_verbalisation_uses_v0_field_diagnostic():
    raw = _environment(["norms@0", "readings@1", "relational-fol@0"])
    Environment(raw)
    changed = deepcopy(raw)
    changed["vocabulary"]["constants"]["alice"]["verbalisation"] = "Alice"
    with pytest.raises(VEError, match=r"fields do not match: expected \[sort, description\], got \[description, sort, verbalisation\]"):
        Environment(changed)


def test_soft_constant_display_extension_still_admitted():
    raw = _environment(["norms@0", "relational-fol@0", "soft-norms@0"])
    raw["vocabulary"]["soft"] = {"parties": [], "ranks": [], "outranks": [], "ties": [],
                                  "outranking": {"mode": "strict"}}
    raw["vocabulary"]["constants"]["alice"]["verbalisation"] = "Alice"
    assert Environment(raw).constants["alice"].verbalisation == "Alice"


def test_v0_constant_field_differential_python_rust():
    """The v0 field rule that the readings pilot keeps has the same refusal on both decoders."""
    raw = _environment(["relational-fol@0"])
    raw["language"] = "ve.core@0"
    raw["profile"] = "relational-fol@0"
    raw.pop("profiles")
    raw["spec_revision"] = "ve-v0-draft-2026-09-20"
    Environment(raw)
    changed = deepcopy(raw)
    changed["vocabulary"]["constants"]["alice"]["verbalisation"] = "Alice"
    with pytest.raises(VEError, match=r"expected \[sort, description\]"):
        Environment(changed)
    request = {"id": "constant-display", "kind": "check", "environment": changed, "ast": [["top"]]}
    binary = Path(__file__).resolve().parents[1] / "rust/target/release/ve"
    result = subprocess.run([str(binary), "conformance"], input=json.dumps([request]),
                            capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert result.returncode == 1
    row, = json.loads(result.stdout)
    assert row["status"] == "error"
    assert row["error"] == {"code": "InvalidInput", "message": 'expected exactly fields ["sort", "description"]'}
