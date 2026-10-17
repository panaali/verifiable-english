"""Wrong-typed top-level environment fields (the env-profiles directive).

Each top-level field of each envelope (the frozen v0, closure and order
envelopes, the route, and the route with each profile block) is replaced by a
value of each JSON kind, and `profiles` also by arrays of non-strings. No entry
point that takes environment JSON raises anything but a `VEError`; every
checker rejects; where a checker's first failure is a type check, Python's
diagnostic class and text are Lean's; and the Python and Lean authorities
agree. The first failing example was `profiles` a number or a Boolean, which
raised `TypeError` in `Environment`.

env-profiles-looprecheck1 extended the class: each block route is compared on
every field of its envelope, every nested value of each fixture is replaced by
each kind, and the rights and reports blocks are compared with their Lean
routes field by field.
"""
from __future__ import annotations

from copy import deepcopy
import itertools
import json
import os
from pathlib import Path
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from ve.backends.diagnostics import checker_error
from tests import lean_routes
from ve.backends.relay import rejection
from ve.environment import Environment
from ve.errors import VEError
from ve.wire import canonical_json
from conformance.risk import agent_ops
from tests import probe_matrix as pm

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin"
RUST = Path(os.environ.get("VE_RUST_BINARY", str(ROOT / "rust/target/release/ve")))

KINDS = {"number": 7, "boolean": True, "null": None, "string": "x", "array": [], "object": {}}
ELEMENTS = {"array-of-numbers": [1], "array-of-booleans": [True], "array-of-arrays": [[]],
            "array-of-objects": [{}], "mixed-array": ["relational-fol@0", 1]}
FIELDS = ("language", "profile", "profiles", "spec_revision", "vocabulary",
          "speech_acts", "alternatives", "risk", "unit_schema", "units")
# Lean's type diagnostics (`Json.getStr?`, `getArr?`, `getObj?`, `profilesOf`
# and the block decoders), as Python's `VEError.to_dict()` reads them.
TYPE_DIAGNOSTICS = {
    ("InvalidInput", "String expected"), ("InvalidInput", "array expected"),
    ("InvalidInput", "object expected"),
    ("UnsupportedProfile", "UnsupportedProfile: profiles must be a sorted unique array"),
    ("InvalidInput", "InvalidInput: speech_acts block"), ("InvalidInput", "InvalidInput: alternatives.block"),
    ("InvalidInput", "InvalidInput: risk.block"), ("InvalidInput", "units must be an object"),
    ("InvalidInput", "InvalidInput: environment vocabulary"),
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


def _reports():
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "relational-fol@0", "reports@0"],
            "spec_revision": pm.SPEC_REVISION,
            "vocabulary": {"reports": {"holders": ["person", "text"], "evidence": "evidence"},
                           "sorts": {s: {"description": s} for s in ("person", "text", "evidence")},
                           "predicates": {"safe": {"arguments": ["person"], "description": "safe"}},
                           "constants": {"article": {"sort": "text", "description": "article"},
                                         "e1": {"sort": "evidence", "description": "evidence"}}}}


BASES = {"route": lambda: pm.raw_environment(()), "v0": lambda: _legacy("v0"),
         "closure": lambda: _legacy("closure"), "order": lambda: _legacy("order"),
         "speech": _speech, "alternatives": _alternatives, "risk": lambda: _alternatives(risk=True),
         "w6": _w6, "risk-units": agent_ops, "reports": _reports}


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
    decoder runs (documents, bundles, admission, the soft and rights
    environments) never raises past the decoder's diagnostic. The readings
    environment (`S1Environment`) is no entry since lean-first batch 3: it only
    builds what Lean's readings route admitted, and the route decides
    (`test_readings_route_relay.py`); it still never crashes
    (`test_every_nested_value_of_every_kind_raises_only_diagnostics`)."""
    from ve.admission import admit_document
    from ve.bundle import check_bundle
    from ve.document import load_document, stored_identities
    from ve.rights import RightsEnvironment
    from ve.softnorms import SoftEnvironment
    monkeypatch.setenv("VE_AUTHORITY", "python")
    for build in (SoftEnvironment, RightsEnvironment,
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
    from ve.backends import relay
    return outcome(lambda: relay.decide("environment", [{"id": "e", "environment": data}]))


# The Lean decoder of each route and a case that reaches its environment decoder.
ROUTE_CASES = {
    "speech": ("ve_speech_acts_route", {"kind": "speech-elaborate", "document": {"units": []}}),
    "alternatives": ("ve_alternatives_route", {"kind": "alt-validate", "norms": []}),
    "risk": ("ve_risk_route", {"kind": "risk-elaborate", "document": {"norms": []}}),
    "quantity": ("ve_quantity", {"kind": "document", "document": {"units": []}}),
    "reports": ("ve_reports_route", {"kind": "reports-elaborate", "document": {"units": []}}),
}


def lean_route(data):
    """The Lean route that decodes an environment, read from the environment
    itself (a mutated envelope may no longer say which base it came from):
    a frozen envelope's language (`isLegacy`) and every envelope no block route
    takes go to the `environment` mode ("envelope"); otherwise the profiles
    choose when they are an array of strings (risk@0, alternatives@0,
    speech-acts@0, reports@0, in that order), else the blocks the envelope
    carries (risk, alternatives, speech_acts); then the W6 fields choose the
    quantity route."""
    if data.get("language") in ("ve.core@0", "ve.core@0.1"):
        return "envelope"
    profiles = data.get("profiles")
    if type(profiles) is list and all(type(p) is str for p in profiles):
        chosen = [route for profile, route in (("risk@0", "risk"), ("alternatives@0", "alternatives"),
                                               ("speech-acts@0", "speech"), ("reports@0", "reports"))
                  if profile in profiles]
    else:
        chosen = [route for block, route in (("risk", "risk"), ("alternatives", "alternatives"),
                                             ("speech_acts", "speech")) if block in data]
    if chosen:
        return chosen[0]
    return "quantity" if {"unit_schema", "units"} & set(data) else "envelope"


def lean_route_rows(route, environments):
    """The diagnostic `(code, message)` (or `("ok", "")`) of Lean's `route`
    decoder for each environment, in one batch (none may be JSON null)."""
    if route == "envelope":
        from ve.backends.lean_service import LeanServicePool
        pool = LeanServicePool()
        try:
            rows = pool.run("environment", [{"id": str(i), "environment": e} for i, e in enumerate(environments)])
        finally:
            pool.close()
    else:
        binary, case = ROUTE_CASES[route]
        batch = [{"id": str(i), "environment": e, **case} for i, e in enumerate(environments)]
        status, rows, stderr = _answer(binary, batch)
        assert status in (0, 1) and "PANIC" not in stderr, stderr[-2000:]
    assert [row["id"] for row in rows] == [str(i) for i in range(len(environments))]
    # The service's rows carry Lean's code; the one-shot routes' leave it in the text's prefix.
    return [pair((rejection(row["code"], row["error"]) if "code" in row else checker_error(row["error"])).to_dict())
            if row["status"] == "error" else ("ok", "") for row in rows]


def lean_diagnostic(data):
    """The diagnostic of the owning Lean environment endpoint."""
    try:
        canonical_json(data)
    except VEError as exc:
        # Not on the restricted wire (null): no Lean runner can read it.
        return exc.code, "not on the restricted wire"
    [row] = lean_route_rows("envelope", [data])
    return row


@pytest.mark.parametrize("value", [7, True, []])
def test_non_object_environment_raises_ve_error(value):
    with pytest.raises(VEError):
        Environment(value)


@lean_service
@pytest.mark.parametrize("base, field, data", CASES)
def test_type_diagnostics_are_leans(monkeypatch, base, field, data):
    """Every Lean decoder rejects; when Lean's or Python's first failure is a
    type check, the two diagnostics are equal in class and text. Each envelope
    is compared with the Lean route that decodes it (`lean_route`) on every
    field, the common ones included (env-profiles-looprecheck1: `language` 7 on
    an extended envelope, the quantity route's `profiles` and the speech
    route's `vocabulary`; env-profiles-directive3: the reports route's
    `vocabulary`)."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    python = pair(outcome(lambda: Environment(data)))
    lean = lean_diagnostic(data)
    assert lean[0] != "ok", (lean_route(data), data)
    if python in TYPE_DIAGNOSTICS or lean in TYPE_DIAGNOSTICS:
        assert python == lean, lean_route(data)


# Pairs of fields, each replaced by a value of each kind or removed: a check
# Python reads in a different order from the route that decodes the envelope
# shows as two different first diagnostics (env-profiles-directive3).
PAIR_KINDS = {**{kind: value for kind, value in KINDS.items() if kind != "null"}, "missing": None}


def _paired(base):
    for first, second in itertools.combinations(FIELDS, 2):
        for (kind1, value1), (kind2, value2) in itertools.product(PAIR_KINDS.items(), repeat=2):
            data = BASES[base]()
            for field, kind, value in ((first, kind1, value1), (second, kind2, value2)):
                if kind == "missing":
                    data.pop(field, None)
                else:
                    data[field] = deepcopy(value)
            if data != BASES[base]():
                yield f"{first}={kind1},{second}={kind2}", data


@lean_service
@pytest.mark.parametrize("base", sorted(BASES))
def test_pairs_of_wrong_typed_fields_have_the_routes_diagnostics(monkeypatch, base):
    """Every pair of top-level fields of every envelope, each a value of each
    JSON kind or absent: Python's first diagnostic is the Lean route's when
    either is a type diagnostic. The first failing examples
    (env-profiles-directive3) were `language` 7 with `profiles` 7 on the speech
    and alternatives envelopes, where Python reported the language before the
    profiles the block routes read first."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    cases = list(_paired(base))
    python = {}
    for name, data in cases:
        try:
            Environment(deepcopy(data))
            python[name] = ("ok", "")
        except VEError as exc:
            python[name] = pair(exc.to_dict())
    lean = dict(zip([name for name, _ in cases],
                    lean_route_rows("envelope", [data for _, data in cases])))
    accepted = [name for name, _ in cases if "ok" in (python[name][0], lean[name][0])
                and python[name] != lean[name]]
    differing = [(name, python[name], lean[name]) for name, _ in cases
                 if (python[name] in TYPE_DIAGNOSTICS or lean[name] in TYPE_DIAGNOSTICS)
                 and python[name] != lean[name]]
    assert accepted == []
    assert differing == [], "\n".join(map(str, differing[:60]))


@pytest.mark.parametrize("base, field, value, expected", [
    *[(base, "language", 7, "String expected") for base in ("speech", "alternatives", "risk", "w6", "risk-units")],
    ("w6", "profiles", 7, "array expected"), ("w6", "profiles", True, "array expected"),
    ("w6", "profiles", [[]], "String expected"),
    ("speech", "vocabulary", 7, "InvalidInput: environment vocabulary"),
    ("speech", "vocabulary", {}, "InvalidInput: environment vocabulary"),
])
def test_looprecheck1_examples_have_the_routes_diagnostics(monkeypatch, base, field, value, expected):
    """env-profiles-looprecheck1's failing examples, without Lean: the route
    that decodes each envelope gives these texts (checked against Lean above)."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    data = BASES[base]()
    data[field] = value
    assert pair(outcome(lambda: Environment(data))) == ("InvalidInput", expected)


@pytest.mark.parametrize("base, changes, expected", [
    *[("reports", {"vocabulary": value}, ("UnsupportedProfile", "UnsupportedProfile: reports@0 needs a reports block"))
      for value in (7, True, [], "x")],
    *[(base, {"language": 7, "profiles": 7}, ("UnsupportedProfile", "UnsupportedProfile: profiles must be a sorted unique array"))
      for base in ("speech", "alternatives", "risk", "risk-units")],
])
def test_directive3_examples_have_the_routes_diagnostics(monkeypatch, base, changes, expected):
    """env-profiles-directive3's failing examples, without Lean: a reports
    envelope whose vocabulary is not an object has no reports block
    (VE.Attribution.Wire reads the block first), and the block routes read
    the profiles before the language (checked against Lean above)."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    data = BASES[base]()
    data.update(changes)
    assert pair(outcome(lambda: Environment(data))) == expected


def _rights():
    from tests.test_rights import rights_env
    return rights_env()


# Fixtures whose nested blocks the top-level matrix does not reach.
NESTED_BASES = {**BASES, "rights": _rights,
                "layers": lambda: pm.raw_environment(("data@0", "definitions@0", "documents@1", "norms@0")),
                "nary": lambda: pm.raw_environment(("closure@0", "nary@0"))}
NESTED_KINDS = {"number": 7, "boolean": True, "string": "x", "array": [], "object": {},
                "array-of-numbers": [1], "array-of-arrays": [[]], "array-of-objects": [{}],
                "object-of-arrays": {"k": []}}


def _paths(value, prefix=()):
    if prefix:
        yield prefix
    if type(value) is dict:
        for key, item in value.items():
            yield from _paths(item, (*prefix, key))
    elif type(value) is list:
        for index, item in enumerate(value):
            yield from _paths(item, (*prefix, index))


def _replaced(data, path, value):
    target = data
    for step in path[:-1]:
        target = target[step]
    target[path[-1]] = deepcopy(value)
    return data


@pytest.mark.parametrize("base", sorted(NESTED_BASES))
def test_every_nested_value_of_every_kind_raises_only_diagnostics(monkeypatch, base):
    """Every value at every depth of each fixture, replaced by a value of each
    JSON kind: the environment decoders and the document identities raise only
    `VEError`. The first failing examples (env-profiles-looprecheck1) were
    `vocabulary.rights.holders` `[[]]`, which raised `TypeError` in
    `RightsEnvironment` and `stored_identities`; the class also held the
    reports block's `holders` and a definition body's predicate name."""
    from ve.document import stored_identities
    from ve.readings_s1 import S1Environment
    from ve.rights import RightsEnvironment
    from ve.softnorms import SoftEnvironment
    monkeypatch.setenv("VE_AUTHORITY", "python")

    def identities(data):
        front = {"format": "ve-document@1", "environment": data, "units": []}
        return stored_identities(b"---\n" + json.dumps(front).encode() + b"\n---\nText.\n")

    crashes = []
    for path in _paths(NESTED_BASES[base]()):
        for kind, value in NESTED_KINDS.items():
            data = _replaced(NESTED_BASES[base](), path, value)
            for entry in (Environment, SoftEnvironment, RightsEnvironment, S1Environment, identities):
                try:
                    entry(deepcopy(data))
                except VEError:
                    pass
                except Exception as exc:  # noqa: BLE001 - an uncaught exception is the defect under test
                    crashes.append(f"{'/'.join(map(str, path))} {kind} {getattr(entry, '__name__', entry)}: "
                                   f"{type(exc).__name__}: {exc}")
    assert crashes == []


def _same_diagnostic(diagnostic):
    """Code and message, the message without a leading `<code>: ` (Lean's
    checker texts carry it, Python's `DuplicateDeclaration` does not)."""
    code, message = pair(diagnostic)
    return code, message.removeprefix(f"{code}: ")


BLOCK_KINDS = {**NESTED_KINDS, "mixed-array": ["person", 1], "unknown": ["nobody"], "duplicate": ["person", "person"]}


def _rights_cases():
    for key in ("holders", "bearers", "protected", "alters"):
        for kind, value in BLOCK_KINDS.items():
            if key == "protected" and kind == "duplicate":
                # Python refuses a repeated name, Lean checks each: a separate DRI
                # decision, logged in ARCH-ROADMAP (manage-agents/ARCH-ROADMAP.md),
                # so not compared here.
                continue
            yield f"{key}-{kind}", ("vocabulary", "rights", key), value
    for key in ("holder_slot", "status", "recognition"):
        for kind, value in BLOCK_KINDS.items():
            yield f"alters.{key}-{kind}", ("vocabulary", "rights", "alters", "person_may_act", key), value
    for kind, value in BLOCK_KINDS.items():
        yield f"alters-entry-{kind}", ("vocabulary", "rights", "alters", "person_may_act"), value


def _block_matrix(binary, case, base, cases):
    """Python's diagnostic and the Lean route's for each case of a nested block."""
    names, python, batch = [], [], []
    for name, path, value in cases:
        data = base()
        if path[-2] == "person_may_act":
            data["vocabulary"]["rights"]["alters"] = {"person_may_act": {"holder_slot": 0, "status": "person_may_act"}}
        _replaced(data, path, value)
        names.append(name)
        try:
            case["build"](deepcopy(data))
            python.append(("ok", ""))  # an empty `protected` or `alters` is valid
        except VEError as exc:
            python.append(_same_diagnostic(exc.to_dict()))
        batch.append({"id": name, "environment": data, **case["row"]})
    status, rows, stderr = _answer(binary, batch)
    assert status in (0, 1), stderr[-2000:]
    assert [row["id"] for row in rows] == names
    lean = [_same_diagnostic(checker_error(row["error"]).to_dict()) if row["status"] == "error" else ("ok", "")
            for row in rows]
    return [(name, p, q) for name, p, q in zip(names, python, lean) if p != q]


def test_rights_block_diagnostics_are_leans(monkeypatch):
    """Each field of the rights block and of an `alters` entry, as each JSON
    kind: Python's `RightsEnvironment` rejects with `ve_rights_route`'s
    diagnostic (`decodeRightsBlock`'s types before the soft environment, then
    `checkBlock`'s order). The first failing example was `holders` `[[]]`."""
    from ve.rights import RightsEnvironment
    monkeypatch.setenv("VE_AUTHORITY", "python")
    case = {"build": RightsEnvironment, "row": {"kind": "rights-elaborate", "document": []}}
    assert _block_matrix("ve_rights_route", case, _rights, list(_rights_cases())) == []


def test_reports_block_diagnostics_are_leans(monkeypatch):
    """The reports block's `holders` and `evidence` as each JSON kind: Python's
    `Environment` rejects with `ve_reports_route`'s diagnostic (the block's
    types before the vocabulary; `holders` 1 to 8 distinct, then declared)."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    cases = [(f"{key}-{kind}", ("vocabulary", "reports", key), value)
             for key in ("holders", "evidence") for kind, value in BLOCK_KINDS.items()]
    case = {"build": Environment, "row": {"kind": "reports-elaborate", "document": {"units": []}}}
    assert _block_matrix("ve_reports_route", case, _reports, cases) == []


@pytest.mark.parametrize("value", [[], {}, ["x"], {"k": []}])
def test_definition_body_with_a_non_string_name_is_rejected_by_both(monkeypatch, value):
    """A definition body whose predicate name is not a string raised
    `TypeError` while its dependencies were collected; Python and Lean both
    reject it now, with Python's elaborator's text (lf-14c review F2: Python's
    decoder keeps the name and its typing check rejects the body)."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    data = pm.raw_environment(("definitions@0",))
    data["vocabulary"]["predicates"]["derived"]["defined"]["body"][1] = value
    assert pair(outcome(lambda: Environment(data))) == (
        "InvalidInput", "Definition derived: the body is not a typed formula over the symbols below it")
    if (BIN / "ve_service").exists():
        lean_environment_mode(data)  # fails the test unless Lean rejects too


LEAN_ROUTES = {
    "ve_norms_route": {"kind": "norms-elaborate", "norms": []},
    "ve_soft_norms_route": {"kind": "soft-elaborate", "norms": []},
    "ve_rights_route": {"kind": "rights-elaborate", "document": {"units": []}},
    "ve_readings_route": {"kind": "readings-validate", "document": {"units": [], "reading_sets": []}},
    "ve_norm_defaults_route": {"kind": "norm-defaults-elaborate", "norms": []},
    "ve_reports_route": {"kind": "reports-elaborate", "document": {"units": []}},
    "ve_speech_acts_route": {"kind": "speech-elaborate", "document": {"units": []}},
    "ve_alternatives_route": {"kind": "alt-validate", "norms": []},
    "ve_risk_route": {"kind": "risk-elaborate", "document": {"norms": []}},
    "ve_quantity": {"kind": "document", "document": {"units": []}},
    "ve_conformance": {"kind": "check", "ast": ["top"]},
}


def _answer(binary, batch):
    """(exit status, rows, stderr) of a Lean route on `batch`: the one-shot `ve_conformance`, or the
    service mode of a statement-layer route (`tests/lean_routes.py`)."""
    if binary != "ve_conformance":
        return lean_routes.run(binary, batch)
    done = subprocess.run([str(BIN / binary), "-"], input=json.dumps(batch).encode(), capture_output=True,
                          timeout=HANG_TIMEOUT)
    return done.returncode, json.loads(done.stdout), done.stderr.decode(errors="replace")


@pytest.mark.live_service
@pytest.mark.parametrize("binary", sorted(LEAN_ROUTES))
def test_every_lean_route_rejects_every_wrong_type_without_panicking(binary):
    """Each Lean route decodes the environment of a case with `Except`: every
    wrong-typed environment is a rejection row, never a panic (null is not on
    the restricted wire)."""
    batch = [{"id": f"{base}-{field}-{kind}", "environment": data, **LEAN_ROUTES[binary]}
             for base, field, kind, data in wrong_typed() if kind != "null"]
    status, rows, stderr = _answer(binary, batch)
    assert status == 1 and "PANIC" not in stderr, stderr[-2000:]
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
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 1, done.stderr
    rows = json.loads(done.stdout)
    assert [row["id"] for row in rows] == [case["id"] for case in cases]
    assert [row["id"] for row in rows if row["status"] != "error"] == []
    for case in nulls:
        done = subprocess.run([str(rust_executable), "conformance", "-"], input=json.dumps([case]),
                              capture_output=True, text=True, timeout=HANG_TIMEOUT)
        assert done.returncode == 2 and "null" in done.stderr.lower(), (case["id"], done.stderr)


@pytest.mark.live_service
@pytest.mark.parametrize("binary", sorted(LEAN_ROUTES))
def test_every_lean_route_reads_every_nested_value_without_panicking(binary):
    """The nested matrix above on each Lean route: one row per case, each a
    result or a rejection, and no panic."""
    batch = [{"id": f"{base}-{'/'.join(map(str, path))}-{kind}",
              "environment": _replaced(NESTED_BASES[base](), path, value), **LEAN_ROUTES[binary]}
             for base in sorted(NESTED_BASES) for path in _paths(NESTED_BASES[base]())
             for kind, value in NESTED_KINDS.items()]
    status, rows, stderr = _answer(binary, batch)
    assert status in (0, 1) and "PANIC" not in stderr, stderr[-2000:]
    assert [row["id"] for row in rows] == [case["id"] for case in batch]
    assert {row["status"] for row in rows} <= {"ok", "error"}


def test_rust_reads_every_nested_value_of_every_kind_without_crashing(rust_executable):
    """The nested matrix above on Rust's environment decoder: one row per case,
    each a verdict or a diagnostic, and no panic (some replacements, such as a
    description `"x"`, are valid)."""
    cases = [{"id": f"{base}-{'/'.join(map(str, path))}-{kind}", "kind": "check", "ast": ["top"],
              "environment": _replaced(NESTED_BASES[base](), path, value)}
             for base in sorted(NESTED_BASES) for path in _paths(NESTED_BASES[base]())
             for kind, value in NESTED_KINDS.items()]
    done = subprocess.run([str(rust_executable), "conformance", "-"], input=json.dumps(cases),
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode in (0, 1) and "panicked" not in done.stderr, done.stderr[-2000:]
    rows = json.loads(done.stdout)
    assert [row["id"] for row in rows] == [case["id"] for case in cases]
    assert {row["status"] for row in rows} <= {"ok", "error"}


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
                           cwd=ROOT, env=rust_build.cargo_env(), capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert built.returncode == 0, built.stdout + built.stderr
    return RUST
