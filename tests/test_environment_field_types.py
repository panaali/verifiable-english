"""Wrong-typed top-level environment fields (the env-profiles directive).

Each top-level field of each envelope (the frozen v0, closure and order
envelopes, the route, and the route with each profile block) is replaced by a
value of each JSON kind, and `profiles` also by arrays of non-strings. No entry
point that takes environment JSON raises anything but a `VEError`; every
checker rejects; where a checker's first failure is a type check, Python's
diagnostic class and text are Lean's; and the Python and Lean authorities
agree. The first failing example was `profiles` a number or a Boolean, which
raised `TypeError` in `Environment`.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess

import pytest

from ve.backends.diagnostics import checker_error
from ve.environment import Environment
from ve.errors import VEError
from ve.wire import canonical_json
from tests import probe_matrix as pm

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin"
RUST = Path(os.environ.get("VE_RUST_BINARY", str(ROOT / "rust/target/release/ve")))

KINDS = {"number": 7, "boolean": True, "null": None, "string": "x", "array": [], "object": {}}
ELEMENTS = {"array-of-numbers": [1], "array-of-booleans": [True], "array-of-arrays": [[]],
            "array-of-objects": [{}], "mixed-array": ["relational-fol@0", 1]}
FIELDS = ("language", "profile", "profiles", "spec_revision", "vocabulary",
          "speech_acts", "alternatives", "risk", "unit_schema", "units")
# The envelopes Lean's `environment` mode decodes, and the profile blocks each
# block route decodes (the type diagnostics are compared on these fields).
ENVELOPES = ("route", "v0", "closure", "order")
BLOCKS = {"speech": ("speech_acts",), "alternatives": ("alternatives",),
          "risk": ("alternatives", "risk"), "w6": ("unit_schema", "units")}
# Lean's type diagnostics (`Json.getStr?`, `getArr?`, `getObj?`, `profilesOf`
# and the block decoders), as Python's `VEError.to_dict()` reads them.
TYPE_DIAGNOSTICS = {
    ("InvalidInput", "String expected"), ("InvalidInput", "array expected"),
    ("InvalidInput", "object expected"),
    ("UnsupportedProfile", "profiles must be a sorted unique array"),
    ("InvalidInput", "InvalidInput: speech_acts block"), ("InvalidInput", "InvalidInput: alternatives.block"),
    ("InvalidInput", "InvalidInput: risk.block"), ("InvalidInput", "units must be an object"),
}


def _speech():
    vocabulary = {
        "sorts": {s: {"description": s, "verbalisation": {"singular": s, "plural": s + "s"}}
                  for s in ("user", "token")},
        "predicates": {"share_permitted": {"arguments": ["user", "token"], "description": "share",
                                           "regulated": {"role": "permission", "default": "allow",
                                                         "act": "{0} share {1}"}}},
        "constants": {"alice": {"sort": "user", "description": "alice"},
                      "token1": {"sort": "token", "description": "token1"}}}
    return {"language": "ve.core@0.2", "spec_revision": pm.SPEC_REVISION,
            "profiles": ["norms@0", "relational-fol@0", "speech-acts@0"],
            "speech_acts": {"task": "t1", "addressee": {"sort": "user", "constant": "alice"},
                            "definites": {"the token": "token1"}},
            "vocabulary": vocabulary}


def _alternatives(risk=False):
    raw = {"language": "ve.core@0.2", "spec_revision": pm.SPEC_REVISION,
           "profiles": ["alternatives@0", "norms@0", "relational-fol@0", *(["risk@0"] if risk else [])],
           "vocabulary": {
               "sorts": {name: {"description": name} for name in ("chooser", "action", "harm")},
               "predicates": {
                   "available": {"arguments": ["action", "chooser"], "description": "available",
                                 "verbalisation": "{0} is available to {1}"},
                   "leads_to": {"arguments": ["action", "harm"], "description": "leads",
                                "verbalisation": "{0} leads to {1}"},
                   "prevent_required": {"arguments": ["chooser", "harm"], "description": "prevent",
                                        "regulated": {"role": "obligation", "default": "deny",
                                                      "act": "{0} prevent {1}"}}},
               "constants": {"outage": {"sort": "harm", "description": "outage"}}},
           "alternatives": {"chooser": "chooser", "action": "action", "harm": "harm",
                            "available": "available", "leads_to": "leads_to", "outcomes": "signed"}}
    if risk:
        raw["risk"] = {"severity": {"sort": "severity", "classes": ["severe", "minor"],
                                    "more_severe": [["severe", "minor"]], "unranked": [], "decided_by": "team"},
                       "harm_classes": [["outage", "severe"]], "unexamined": "possible"}
    return raw


def _w6():
    return {"language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
            "spec_revision": pm.SPEC_REVISION,
            "vocabulary": {"sorts": {"item": {"description": "an item"}},
                           "predicates": {"reported": {"arguments": ["$int"], "argument_units": {"0": "bp"},
                                                       "description": "reported percentage"}},
                           "constants": {"rate": {"sort": "$int", "unit": "bp", "description": "reported rate"}}},
            "unit_schema": "ve-units@1",
            "units": {"bp": {"scale": "100", "display": {"kind": "percent"}}}}


def _legacy(kind):
    raw = pm.raw_environment(())
    raw.pop("profiles")
    if kind == "v0":
        raw.update(language="ve.core@0", profile="relational-fol@0", spec_revision="ve-v0-draft-2026-09-20")
    elif kind == "closure":
        raw.update(language="ve.core@0.1", profiles=["closure@0", "relational-fol@0"],
                   spec_revision="ve-v0.1-closure-2026-09-21")
    else:
        raw.update(language="ve.core@0.1", profiles=["order@0", "relational-fol@0"],
                   spec_revision="ve-v0.1-order-2026-09-22")
    return raw


BASES = {"route": lambda: pm.raw_environment(()), "v0": lambda: _legacy("v0"),
         "closure": lambda: _legacy("closure"), "order": lambda: _legacy("order"),
         "speech": _speech, "alternatives": _alternatives, "risk": lambda: _alternatives(risk=True),
         "w6": _w6}


def wrong_typed():
    """(base, field, kind, environment JSON) for every base, field and kind."""
    for base in BASES:
        for field in FIELDS:
            values = {**KINDS, **(ELEMENTS if field == "profiles" else {})}
            for kind, value in values.items():
                data = BASES[base]()
                data[field] = deepcopy(value)
                yield base, field, kind, data


CASES = [pytest.param(base, field, data, id=f"{base}-{field}-{kind}")
         for base, field, kind, data in wrong_typed()]


def outcome(build):
    """A rejection's diagnostic; any other exception fails the test (the directive's class)."""
    try:
        built = build()
    except VEError as exc:
        return exc.to_dict()
    except Exception as exc:  # noqa: BLE001 - an uncaught exception is the defect under test
        pytest.fail(f"uncaught {type(exc).__name__}: {exc}")
    pytest.fail(f"accepted a wrong-typed environment: {built!r}")


def pair(diagnostic):
    return diagnostic["code"], diagnostic["message"]


def test_the_bases_are_valid(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "python")
    for build in BASES.values():
        Environment(build())


@pytest.mark.parametrize("base, field, data", CASES)
def test_python_rejects_every_wrong_type_with_a_diagnostic(monkeypatch, base, field, data):
    monkeypatch.setenv("VE_AUTHORITY", "python")
    outcome(lambda: Environment(data))


@pytest.mark.parametrize("base, field, data", CASES)
def test_every_python_entry_taking_environment_json_raises_only_diagnostics(monkeypatch, tmp_path,
                                                                            base, field, data):
    """The routing that reads an environment's profiles or language before its
    decoder runs (documents, bundles, admission, the soft, rights and readings
    environments) never raises past the decoder's diagnostic."""
    from ve.admission import admit_document
    from ve.bundle import check_bundle
    from ve.document import load_document, stored_identities
    from ve.readings_s1 import S1Environment
    from ve.rights import RightsEnvironment
    from ve.softnorms import SoftEnvironment
    monkeypatch.setenv("VE_AUTHORITY", "python")
    for build in (SoftEnvironment, RightsEnvironment, S1Environment,
                  lambda d: admit_document(d, {"units": []}),
                  lambda d: check_bundle({"version": "ve-bundle@0", "environment": d, "lemmas": []})):
        outcome(lambda: build(deepcopy(data)))
    for extra in ({}, {"couplings": []}, {"completions": []}):
        path = tmp_path / "doc.ve.md"
        front = {"format": "ve-document@1", "environment": data, "units": [], **extra}
        path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\nText.\n")
        outcome(lambda: load_document(path))
        outcome(lambda: stored_identities(path.read_bytes()))
    # A `ve-document@2` text's identities are decoded without its Lean admission.
    front = {"format": "ve-document@2", "environment": data, "units": [], "discourse": {}}
    outcome(lambda: stored_identities(b"---\n" + json.dumps(front).encode() + b"\n---\nText.\n"))


lean_service = pytest.mark.skipif(not (BIN / "ve_service").exists(), reason="Lean service has not been built")


@lean_service
@pytest.mark.parametrize("base, field, data", CASES)
def test_python_and_lean_authorities_agree(monkeypatch, base, field, data):
    from ve.backends import validation
    from ve.bundle import check_bundle
    monkeypatch.setattr(validation, "_ACCEPTED", {})
    expected = []
    for authority in ("python", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        expected.append((outcome(lambda: Environment(data)),
                         outcome(lambda: check_bundle({"version": "ve-bundle@0", "environment": data,
                                                       "lemmas": []}))))
    assert expected[0] == expected[1]


def lean_environment_mode(data):
    from ve.backends import lean_runner
    return outcome(lambda: lean_runner.run("environment", [{"id": "e", "environment": data}]))


def lean_block_route(base, data):
    """The diagnostic of the Lean route that decodes `base`'s profile block."""
    binary, case = {
        "speech": ("ve_speech_acts_route", {"kind": "speech-elaborate", "document": {"units": []}}),
        "alternatives": ("ve_alternatives_route", {"kind": "alt-validate", "norms": []}),
        "risk": ("ve_risk_route", {"kind": "risk-elaborate", "norms": []}),
        "w6": ("ve_quantity", {"kind": "document", "document": {"units": []}}),
    }[base]
    if not (BIN / binary).exists():
        pytest.skip(f"{binary} has not been built")
    try:
        payload = canonical_json([{"id": "c", "environment": data, **case}])
    except VEError as exc:
        # Not on the restricted wire (null): no Lean runner can read it.
        return {"code": exc.code, "message": "not on the restricted wire"}
    done = subprocess.run([str(BIN / binary), "-"], input=payload, capture_output=True, timeout=600)
    assert done.returncode in (0, 1), done.stderr
    [row] = json.loads(done.stdout)
    assert row["status"] == "error", row
    return checker_error(row["error"]).to_dict()


@lean_service
@pytest.mark.parametrize("base, field, data", CASES)
def test_type_diagnostics_are_leans(monkeypatch, base, field, data):
    """Every Lean decoder rejects; when Lean's or Python's first failure is a
    type check, the two diagnostics are equal in class and text. Lean's
    `environment` mode is compared on the envelopes it decodes; each block
    route on its own block's fields."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    python = pair(outcome(lambda: Environment(data)))
    if base in ENVELOPES:
        lean = pair(lean_environment_mode(data))
    elif field in BLOCKS[base]:
        lean = pair(lean_block_route(base, data))
    else:
        return
    if python in TYPE_DIAGNOSTICS or lean in TYPE_DIAGNOSTICS:
        assert python == lean


LEAN_ROUTES = {
    "ve_norms_route": {"kind": "norms-elaborate", "norms": []},
    "ve_soft_norms_route": {"kind": "soft-elaborate", "norms": []},
    "ve_rights_route": {"kind": "rights-elaborate", "document": {"units": []}},
    "ve_readings_route": {"kind": "readings-validate", "document": {"units": [], "reading_sets": []}},
    "ve_norm_defaults_route": {"kind": "norm-defaults-elaborate", "norms": []},
    "ve_reports_route": {"kind": "reports-elaborate", "document": {"units": []}},
    "ve_speech_acts_route": {"kind": "speech-elaborate", "document": {"units": []}},
    "ve_alternatives_route": {"kind": "alt-validate", "norms": []},
    "ve_risk_route": {"kind": "risk-elaborate", "norms": []},
    "ve_quantity": {"kind": "document", "document": {"units": []}},
    "ve_conformance": {"kind": "check", "ast": ["top"]},
}


@pytest.mark.parametrize("binary", sorted(LEAN_ROUTES))
def test_every_lean_route_rejects_every_wrong_type_without_panicking(binary):
    """Each Lean route decodes the environment of a case with `Except`: every
    wrong-typed environment is a rejection row, never a panic (null is not on
    the restricted wire)."""
    if not (BIN / binary).exists():
        pytest.skip(f"{binary} has not been built")
    batch = [{"id": f"{base}-{field}-{kind}", "environment": data, **LEAN_ROUTES[binary]}
             for base, field, kind, data in wrong_typed() if kind != "null"]
    done = subprocess.run([str(BIN / binary), "-"], input=json.dumps(batch).encode(), capture_output=True,
                          timeout=600)
    assert done.returncode == 1 and b"PANIC" not in done.stderr, done.stderr[-2000:]
    rows = json.loads(done.stdout)
    assert [row["id"] for row in rows] == [case["id"] for case in batch]
    assert [row["id"] for row in rows if row["status"] != "error"] == []


def test_rust_rejects_every_wrong_type_without_crashing(rust_executable):
    """Rust's environment decoder (evaluation and search only) rejects each
    wrong-typed environment with a diagnostic row; JSON null is refused at the
    restricted wire before any case is read."""
    cases, nulls = [], []
    for base, field, kind, data in wrong_typed():
        case = {"id": f"{base}-{field}-{kind}", "kind": "check", "environment": data, "ast": ["top"]}
        (nulls if kind == "null" else cases).append(case)
    done = subprocess.run([str(rust_executable), "conformance", "-"], input=json.dumps(cases),
                          capture_output=True, text=True, timeout=600)
    assert done.returncode == 1, done.stderr
    rows = json.loads(done.stdout)
    assert [row["id"] for row in rows] == [case["id"] for case in cases]
    assert [row["id"] for row in rows if row["status"] != "error"] == []
    for case in nulls:
        done = subprocess.run([str(rust_executable), "conformance", "-"], input=json.dumps([case]),
                              capture_output=True, text=True, timeout=60)
        assert done.returncode == 2 and "null" in done.stderr.lower(), (case["id"], done.stderr)


@pytest.fixture(scope="module")
def rust_executable():
    import shutil
    from tools import rust_build
    if os.environ.get("VE_RUST_PREBUILT"):
        assert RUST.is_file(), f"gate Rust build missing: {RUST}"
        return RUST
    cargo = shutil.which("cargo")
    if cargo is None:
        pytest.skip("cargo is required for the Rust decoder")
    built = subprocess.run([cargo, "build", "-j", "2", "--locked", "--release",
                            "--manifest-path", str(ROOT / "rust/Cargo.toml")],
                           cwd=ROOT, env=rust_build.cargo_env(), capture_output=True, text=True, timeout=600)
    assert built.returncode == 0, built.stdout + built.stderr
    return RUST
