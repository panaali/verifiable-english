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


def _chain(chain):
    """A readings@1 environment on each chain of `VE.Readings.Wire.decodeEnvironment`, with one constant."""
    raw = _environment({"norms": ["norms@0", "readings@1", "relational-fol@0"],
                        "soft": ["norms@0", "readings@1", "relational-fol@0", "soft-norms@0"],
                        "rights": ["norms@0", "readings@1", "relational-fol@0", "rights@0", "soft-norms@0"]}[chain])
    if chain == "rights":
        raw["vocabulary"]["rights"] = {"holders": ["person"], "bearers": ["person"], "protected": [], "alters": {}}
    return raw


@pytest.mark.parametrize("chain", ["norms", "soft", "rights"])
def test_readings_constant_verbalisation_on_every_chain(chain):
    """Review F3 of jt-crossplan-fixes: X3 is the norms chain's v0 rule, decided by the lower decoder; the soft and
    rights chains keep DF-19's display field under readings@1 as they do without it."""
    raw = _chain(chain)
    raw["vocabulary"]["constants"]["alice"]["verbalisation"] = "Alice"
    if chain == "norms":
        with pytest.raises(VEError, match=r"^fields do not match: expected \[sort, description\], "
                                          r"got \[description, sort, verbalisation\]$"):
            Environment(raw)
    else:
        assert Environment(raw).constants["alice"].verbalisation == "Alice"


@pytest.mark.parametrize("chain", ["norms", "soft", "rights"])
def test_readings_literal_constant_keeps_its_display_words(chain):
    """Review F3 (b): a `$string` literal admits a `verbalisation` (Route/Wire.lean `literalEntry`) on every chain."""
    raw = _chain(chain)
    raw["vocabulary"]["constants"]["hello"] = {"sort": "$string", "verbalisation": "hello"}
    assert Environment(raw).constants["hello"].verbalisation == "hello"


@pytest.mark.parametrize("chain, message", [
    ("norms", r"^fields do not match: expected \[sorts, predicates, constants\], got \[predicates, sorts\]$"),
    ("soft", r"^InvalidInput: invalid vocabulary$"), ("rights", r"^InvalidInput: invalid vocabulary$")])
def test_readings_missing_constants_keeps_the_chain_diagnostic(chain, message):
    """Review F3 (a), R1: a vocabulary without `constants` keeps each chain's own diagnostic of the base, the
    norms chain's naming the expected and the present fields (never "property not found: constants")."""
    raw = _chain(chain)
    del raw["vocabulary"]["constants"]
    with pytest.raises(VEError, match=message):
        Environment(raw)


def test_readings_constant_verbalisation_keeps_the_decoder_fault_order():
    """Review F3 (c), R2: the refusal is the vocabulary decoder's, at the constant's place in its order: a bad
    predicate or an earlier constant's unknown sort is reported first, as without the display field."""
    raw = _chain("norms")
    constants = raw["vocabulary"]["constants"]
    constants["alice"]["verbalisation"] = "Alice"
    constants["aaron"] = {"sort": "nobody", "description": "Aaron"}
    with pytest.raises(VEError, match=r"^unknown constant sort: aaron$"):
        Environment(raw)
    del constants["aaron"]
    raw["vocabulary"]["predicates"]["knows"] = {"arguments": ["nobody"], "description": "knows"}
    with pytest.raises(VEError, match=r"^UnknownSymbol: Undeclared predicate argument sort: 'nobody'$"):
        Environment(raw)


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
