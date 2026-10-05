"""The `norm-defaults@0` wire table in shadow (wire-contract-s5.md 2.4, 8.2): `UnspecifiedDocument` still owns
the verdict; the Python engine names the first check of the table that fails, `norms@0`'s under its include."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from conformance.wire_contract_faults import catalogue, expected_record
from conformance.wire_contract_faults_norm_defaults import LONG, base
from conformance.wire_contract_faults_norms import ATOM, balanced
from ve.errors import UnsupportedProfile, VEError
from ve.norm_defaults_contract import REGISTRY, legacy_validation, norm_defaults_source
from ve.norms_contract import OUTSIDE
from ve.wire import loads_json
from ve.wire_contract.engine import CLEAN, Fault, load, run

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "ve/wire_contract"
CONTRACT = load("norm-defaults@0")
LIMITS = loads_json((DIRECTORY / "limits.json").read_bytes())
NAMES = loads_json((DIRECTORY / "names.json").read_bytes())


def diagnose(environment, norms):
    return run(CONTRACT, {"environment": environment, "norms": norms}, registry=REGISTRY, limits=LIMITS,
               names=NAMES)


def legacy(environment, norms):
    try:
        legacy_validation(deepcopy(environment), deepcopy(norms))
    except VEError as exc:
        return exc
    return None


def change(edit):
    def build():
        raw, norms = base()
        edit(raw, norms)
        return raw, norms
    return build


def _set(i, field, value):
    return lambda raw, norms: norms[i]["norm"].update({field: deepcopy(value)})


def _d6(raw, norms):
    raw["vocabulary"]["predicates"].update(
        {f"b{i}": {"arguments": ["assistant"], "description": "b"} for i in range(253)})


def _d7(raw, norms):
    norms.extend({"norm": {"name": f"r{i}", "predicate": "x_required", "sign": True, "guard": ["top"],
                           "unless": [], "over": []}} for i in range(3, 256))


def _d8(raw, norms):
    predicates = raw["vocabulary"]["predicates"]
    predicates[LONG] = predicates.pop("x_permitted")
    predicates["x_required"]["regulated"]["permission"] = LONG
    for unit in norms:
        if unit["norm"]["predicate"] == "x_permitted":
            unit["norm"]["predicate"] = LONG


def _d10(raw, norms):
    norms[:] = [{"norm": {"name": f"r{i}", "predicate": "x_permitted", "sign": True, "guard": ["top"],
                          "unless": [], "over": [f"r{i - 1}"] if i else []}} for i in range(16)]


def both(*edits):
    return lambda raw, norms: [edit(raw, norms) for edit in edits]


def record(check, phase, code, cls, path, text=None, args=None):
    value = {"contract": "norm-defaults@0", "revision": CONTRACT["revision"], "check": check, "phase": phase,
             "code": code, "class": cls, "path": path}
    if text is not None:
        value.update(text=text, args=args or {})
    return value


R = "NORM_DEFAULTS_RESOURCE_LIMIT"
# The fixtures of 8.2: each source, and its expected record (written by hand from 2.4) or "clean".
FIXTURES = {
    "D1": (change(lambda raw, norms: None), "clean"),
    "D1-empty": (change(lambda raw, norms: norms.clear()), "clean"),
    "D2": (change(_set(1, "unless", {})),
           record("w1-shape/3.4", "rule-shape", "NORMS_INVALID_RULE_FIELDS", "InvalidInput", "/norms/1/norm/unless",
                  "InvalidInput: unless and over must be arrays")),
    "D3": (change(_set(2, "name", "a0")),
           record("w1/4.2", "norms", "NORMS_DUPLICATE_DECLARATION", "DuplicateDeclaration", "/norms/2/norm/name",
                  "DuplicateDeclaration: rule a0", {"value": "a0"})),
    "D4": (change(_set(1, "name", "unsaid--x")),
           record("w1/4.3", "norms", "NORMS_RESERVED_NAME", "InvalidInput", "/norms/1/norm/name",
                  "InvalidInput: reserved name unsaid--x", {"value": "unsaid--x"})),
    "D5": (change(_set(0, "over", ["c2"])),
           record("w1/6.1", "norms", "NORMS_DEPENDENCY_CYCLE", "InvalidInput", "/norms", "DependencyCycle: a0, c2",
                  {"detail": "a0, c2"})),
    "D6": (change(_d6), record("5.1", "limits", R, "ResourceLimit", "", "ResourceLimit: vocabulary size")),
    "D7": (change(_d7), record("5.2", "limits", R, "ResourceLimit", "", "ResourceLimit: rules")),
    "D8": (change(_d8), record("5.3", "limits", R, "ResourceLimit", "", "ResourceLimit: unspecified name length")),
    "D9": (change(_set(0, "guard", balanced([ATOM] * 3332))),
           record("6.1", "fill", R, "ResourceLimit", "", "ResourceLimit: AST exceeds 10,000 nodes")),
    "D10": (change(_d10), record("6.2", "fill", R, "ResourceLimit", "", "ResourceLimit: precedence depth")),
    "D11": (change(_set(0, "guard", balanced([ATOM] * 3320))),
            record("6.3", "fill", R, "ResourceLimit", "", "ResourceLimit: fill premise unsaid:pair:x_required,x_permitted",
                   {"label": "unsaid:pair:x_required,x_permitted"})),
    "D12": (change(both(_d8, _set(2, "over", ["b1"]))),
            record("w1/5.2", "norms", "NORMS_PRECEDENCE_ACROSS_PREDICATES", "InvalidInput", "/norms/2/norm/over/0",
                   f"PrecedenceAcrossPredicates: rule c2 on x_required, rule b1 on {LONG}",
                   {"rule": "c2", "predicate": "x_required", "value": "b1", "parent_predicate": LONG})),
    "D13": (change(both(_d10, _d8)),
            record("5.3", "limits", R, "ResourceLimit", "", "ResourceLimit: unspecified name length")),
}
# Python's legacy text before the switch, where 6 lists it.
LEGACY_TEXTS = {"D6": "vocabulary size", "D7": "rules", "D8": "unspecified name length",
                "D9": "ResourceLimit: AST exceeds 10,000 nodes", "D10": "precedence depth",
                "D11": "fill premise unsaid:pair:x_required,x_permitted", "D3": "rule a0"}
GOLDEN = {name: expected for name, (_, expected) in FIXTURES.items()}


def fixture_sources():
    return [(name, *build()) for name, (build, _) in FIXTURES.items()]


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_fixture_of_8_2(name):
    build, expected = FIXTURES[name]
    raw, norms = build()
    error = legacy(raw, norms)
    outcome = diagnose(raw, norms)
    if expected == "clean":
        assert error is None and outcome is CLEAN
        return
    assert error is not None and isinstance(outcome, Fault), (error, outcome)
    assert outcome.record == expected
    assert error.code == expected["class"]
    if name in LEGACY_TEXTS:
        assert str(error) == LEGACY_TEXTS[name]


def test_node_counts_of_d9_and_d11():
    """Open point 6: D9's guard has 9,995 nodes and D11's 9,959, each within W1's budget of its rule."""
    from ve.norms_contract import syntax_walk
    assert syntax_walk(balanced([ATOM] * 3332)) == 9995 and syntax_walk(balanced([ATOM] * 3320)) == 9959


def test_examples_are_clean_and_accepted():
    for path in sorted((DIRECTORY / "examples/norm-defaults@0").glob("*.json")):
        value = json.loads(path.read_text())
        assert legacy(value["environment"], value["norms"]) is None
        assert diagnose(value["environment"], value["norms"]) is CLEAN


def test_every_catalogue_fault_alone_gives_its_expected_record_in_python():
    """Tier 0 of the gate, in Python, with every included check under its include."""
    for fault in catalogue("norm-defaults@0"):
        raw, norms = fault.source()
        error = legacy(raw, norms)
        outcome = diagnose(raw, norms)
        assert error is not None and isinstance(outcome, Fault), fault.name
        expected = expected_record(CONTRACT, fault)
        got = outcome.record
        assert {key: got[key] for key in expected} == expected, fault.name


def test_adapter_builds_the_root_and_refuses_cases_outside_the_domain():
    raw, norms = base()
    assert norm_defaults_source({"kind": "norm-defaults-elaborate", "environment": raw, "norms": norms}) == {
        "environment": raw, "norms": norms}
    with pytest.raises(UnsupportedProfile, match="case kind norms-elaborate has no wire contract input"):
        norm_defaults_source({"kind": "norms-elaborate", "environment": raw, "norms": norms})
    plain = deepcopy(raw)
    plain["profiles"] = ["norms@0", "relational-fol@0"]
    soft = deepcopy(raw)
    soft["profiles"] = ["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]
    for environment in (plain, soft):
        with pytest.raises(UnsupportedProfile) as raised:
            norm_defaults_source({"kind": "norm-defaults-elaborate", "environment": environment, "norms": norms})
        assert str(raised.value) == OUTSIDE


def test_registry_reuses_the_included_hooks_by_name():
    """2.5: the included checks run with the same Python functions as in `norms@0`."""
    from ve.norms_contract import REGISTRY as NORMS
    assert all(REGISTRY.hooks[name] is hook for name, hook in NORMS.hooks.items())
    assert all(REGISTRY.classifiers[name] is classifier for name, classifier in NORMS.classifiers.items())


def test_golden_records_are_current():
    from conformance.wire_contract_golden import ROOT as REPORTS, unit_reports
    for filename, body in unit_reports("norm-defaults@0").items():
        assert json.loads((REPORTS / filename).read_text()) == body
