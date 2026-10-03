"""The `norms@0` wire table in shadow (wire-contract-s5.md 2.3, 2.5, 8.1): the legacy validator still owns the
verdict; the Python engine names the first check of the table that fails."""

from copy import deepcopy
import json
from pathlib import Path
import shutil

import pytest

from conformance.wire_contract_faults import catalogue, expected_record
from conformance.wire_contract_faults_norms import ATOM, REACH, balanced, base, nots
from tools import wire_contract as wire_tool
from ve.ast import _Decoder
from ve.errors import UnsupportedProfile, VEError
from ve.norms_contract import (OUTSIDE, REGISTRY, Refused, legacy_validation, norm_source, syntax_walk)
from ve.wire import loads_json
from ve.wire_contract.engine import CLEAN, Fault, load, run

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "ve/wire_contract"
CONTRACT = load("norms@0")
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
    """B with one edit applied: `edit(environment, norms)`."""
    def build():
        raw, norms = base()
        edit(raw, norms)
        return raw, norms
    return build


def guard(i, formula):
    return change(lambda raw, norms: norms[i]["norm"].update(guard=deepcopy(formula)))


def _n2(raw, norms):
    raw["profiles"] = ["relational-fol@0"]
    for entry in raw["vocabulary"]["predicates"].values():
        entry.pop("regulated", None)


def _n3(raw, norms):
    norms.extend({"norm": {**deepcopy(norms[0]["norm"]), "name": f"r{i}"}} for i in range(3, 257))


def _n21(raw, norms):
    for i in (0, 1):
        norms[i]["norm"]["guard"] = balanced([ATOM] * 1667)
    norms[1]["norm"]["unless"] = []


def _n25(raw, norms):
    norms[:] = [{"norm": {"name": f"r{i}", "predicate": "x_required", "sign": True, "guard": ["top"],
                          "unless": [], "over": [f"r{i - 1}"] if i else []}} for i in range(17)]


def _n26(raw, norms):
    norms[0]["norm"]["guard"] = ["unary", "x_permitted", ["var", 0]]
    norms[1]["norm"]["guard"] = ["unary", "x_required", ["var", 0]]


def _n38(raw, norms):
    raw["profiles"] = ["data@0", "norms@0", "relational-fol@0"]
    norms[0]["norm"]["guard"] = ["forall", "$string", ["top"]]


def _n39(raw, norms):
    _n21(raw, norms)
    norms[2]["norm"]["guard"] = ["unary", "d", ["var", 0]]


def both(*edits):
    return lambda raw, norms: [edit(raw, norms) for edit in edits]


def _set(i, field, value):
    return lambda raw, norms: norms[i]["norm"].update({field: deepcopy(value)})


def record(check, phase, code, cls, path, text=None, args=None):
    value = {"contract": "norms@0", "revision": CONTRACT["revision"], "check": check, "phase": phase,
             "code": code, "class": cls, "path": path}
    if text is not None:
        value.update(text=text, args=args or {})
    return value


IR = "NORMS_INVALID_RULE_FIELDS"
# The fixtures of 8.1: each source, and its expected record (written by hand from 2.3 and 2.5) or "clean".
# An inherited record has no `text`: its text is each language's own (base spec D8). N14 is struck.
FIXTURES = {
    "N1": (change(lambda raw, norms: None), "clean"),
    "N1-empty": (change(lambda raw, norms: norms.clear()), "clean"),
    "N2": (change(_n2), record("2.1", "profiles", "NORMS_PROFILE_REQUIRED", "InvalidInput", "/environment/profiles",
                               "UnsupportedProfile: norms@0 is required")),
    "N3": (change(_n3), record("2.2", "profiles", "NORMS_RESOURCE_LIMIT", "ResourceLimit", "/norms",
                               "ResourceLimit: rules")),
    "N4": (change(lambda raw, norms: norms[1].update(extra=1)),
           record("3.1", "rule-shape", "NORMS_INVALID_UNIT", "InvalidInput", "/norms/1",
                  "InvalidInput: expected norm object")),
    "N5": (change(lambda raw, norms: norms[0].update(norm=[])),
           record("3.2", "rule-shape", "NORMS_INVALID_UNIT", "InvalidInput", "/norms/0/norm",
                  "InvalidInput: expected norm object")),
    "N6": (change(lambda raw, norms: norms[2]["norm"].pop("over")),
           record("3.3", "rule-shape", IR, "InvalidInput", "/norms/2/norm", "InvalidInput: invalid norm fields")),
    "N7": (change(_set(1, "unless", {})),
           record("3.4", "rule-shape", IR, "InvalidInput", "/norms/1/norm/unless",
                  "InvalidInput: unless and over must be arrays")),
    "N8": (change(_set(2, "over", ["a0", 7])),
           record("3.7", "rule-shape", IR, "InvalidInput", "/norms/2/norm/over/1",
                  "InvalidInput: rule predicate and precedence edges must be strings")),
    "N9": (guard(0, nots(65, ["top"])),
           record("3.8a", "rule-shape", "NORMS_RESOURCE_LIMIT", "ResourceLimit", "/norms/0/norm/guard")),
    "N10": (guard(0, 5), record("3.8b", "rule-shape", "NORMS_INVALID_FORMULA", "SyntaxError", "/norms/0/norm/guard")),
    "N11": (change(_set(1, "unless", [ATOM, 5])),
            record("3.9b", "rule-shape", "NORMS_INVALID_FORMULA", "SyntaxError", "/norms/1/norm/unless/1")),
    "N12": (change(_set(0, "name", "A0")),
            record("4.1", "rules", "NORMS_INVALID_NAME", "InvalidInput", "/norms/0/norm/name",
                   "InvalidInput: invalid rule name 'A0'", {"value": "A0"})),
    "N13": (change(_set(2, "name", "a0")),
            record("4.2", "rules", "NORMS_DUPLICATE_DECLARATION", "DuplicateDeclaration", "/norms/2/norm/name",
                   "DuplicateDeclaration: rule a0", {"value": "a0"})),
    "N15": (change(_set(0, "predicate", "c")),
            record("4.4", "rules", "NORMS_UNKNOWN_PREDICATE", "InvalidInput", "/norms/0/norm/predicate",
                   "UnknownSymbol: regulated predicate c", {"value": "c"})),
    "N16": (change(_set(1, "sign", "no")),
            record("4.5", "rules", IR, "InvalidInput", "/norms/1/norm/sign",
                   "InvalidInput: invalid sign or too many carve-outs")),
    "N17": (change(_set(1, "unless", [ATOM] * 9)),
            record("4.6", "rules", IR, "InvalidInput", "/norms/1/norm/unless",
                   "InvalidInput: invalid sign or too many carve-outs")),
    "N18": (guard(0, ["binary", "c", ["var", 0], ["var", 0]]),
            record("4.7a", "rules", "NORMS_TYPE_MISMATCH", "TypeMismatch", "/norms/0")),
    "N19": (guard(0, ["unary", "d", ["var", 0]]),
            record("4.7b", "rules", "NORMS_UNKNOWN_SYMBOL", "UnknownSymbol", "/norms/0")),
    "N20": (guard(0, ["unary", "c", ["var", 1]]),
            record("4.7c", "rules", "NORMS_UNBOUND_VARIABLE", "UnboundVariable", "/norms/0")),
    "N21": (change(_n21), record("4.7d", "rules", "NORMS_RESOURCE_LIMIT", "ResourceLimit", "/norms/2")),
    "N22": (change(_set(2, "over", ["zz"])),
            record("5.1", "references", "NORMS_UNKNOWN_RULE", "InvalidInput", "/norms/2/norm/over/0",
                   "UnknownRule: rule zz", {"value": "zz"})),
    "N23": (change(_set(2, "over", ["b1"])),
            record("5.2", "references", "NORMS_PRECEDENCE_ACROSS_PREDICATES", "InvalidInput",
                   "/norms/2/norm/over/0",
                   "PrecedenceAcrossPredicates: rule c2 on x_required, rule b1 on x_permitted",
                   {"rule": "c2", "predicate": "x_required", "value": "b1", "parent_predicate": "x_permitted"})),
    "N24": (change(_set(0, "over", ["c2"])),
            record("6.1", "semantic", "NORMS_DEPENDENCY_CYCLE", "InvalidInput", "/norms",
                   "DependencyCycle: a0, c2", {"detail": "a0, c2"})),
    "N25": (change(_n25), record("6.2", "semantic", "NORMS_RESOURCE_LIMIT", "ResourceLimit", "/norms",
                                 "ResourceLimit: precedence depth")),
    "N26": (change(_n26), record("6.3", "semantic", "NORMS_DEPENDENCY_CYCLE", "InvalidInput", "/norms",
                                 "DependencyCycle: x_permitted, x_required", {"detail": "x_permitted, x_required"})),
    "N27": (change(both(lambda raw, norms: norms[1].update(extra=1), _set(2, "name", "a0"))),
            record("3.1", "rule-shape", "NORMS_INVALID_UNIT", "InvalidInput", "/norms/1",
                   "InvalidInput: expected norm object")),
    "N28": (change(both(_set(0, "predicate", "c"), _set(1, "name", "B1"))),
            record("4.4", "rules", "NORMS_UNKNOWN_PREDICATE", "InvalidInput", "/norms/0/norm/predicate",
                   "UnknownSymbol: regulated predicate c", {"value": "c"})),
    "N29": (change(both(_set(0, "name", "A0"), _set(0, "predicate", "c"))),
            record("4.1", "rules", "NORMS_INVALID_NAME", "InvalidInput", "/norms/0/norm/name",
                   "InvalidInput: invalid rule name 'A0'", {"value": "A0"})),
    "N30": (change(both(_set(1, "unless", {}), _set(1, "sign", "no"))),
            record("3.4", "rule-shape", IR, "InvalidInput", "/norms/1/norm/unless",
                   "InvalidInput: unless and over must be arrays")),
    "N31": (change(_set(1, "unless", [ATOM, ["unary", "d", ["var", 0]]])),
            record("4.7b", "rules", "NORMS_UNKNOWN_SYMBOL", "UnknownSymbol", "/norms/1")),
    # The review wrote `["var", -1]`; a negative integer is outside the engine's JSON domain (`_domain`:
    # 0 to 2^53 - 1), on which `run` reports clean for the whole root, so the index is a Boolean, which
    # `_Decoder` refuses with the same class and text.
    "N32": (guard(0, ["unary", "c", ["var", True]]),
            record("3.8b", "rule-shape", "NORMS_INVALID_FORMULA", "SyntaxError", "/norms/0/norm/guard")),
    "N33": (guard(0, ["unary", 7, ["var", 0]]),
            record("4.7b", "rules", "NORMS_UNKNOWN_SYMBOL", "UnknownSymbol", "/norms/0")),
    "N34": (guard(0, ["eq", ["const", 5], ["var", 0]]),
            record("4.7b", "rules", "NORMS_UNKNOWN_SYMBOL", "UnknownSymbol", "/norms/0")),
    "N35": (guard(0, ["forall", 5, ["top"]]),
            record("4.7b", "rules", "NORMS_UNKNOWN_SYMBOL", "UnknownSymbol", "/norms/0")),
    "N36": (guard(0, ["and", REACH, nots(65, ["top"])]),
            record("3.8b", "rule-shape", "NORMS_INVALID_FORMULA", "SyntaxError", "/norms/0/norm/guard")),
    "N37": (guard(0, ["and", nots(65, ["top"]), REACH]),
            record("3.8a", "rule-shape", "NORMS_RESOURCE_LIMIT", "ResourceLimit", "/norms/0/norm/guard")),
    "N38": (change(_n38), record("4.7e", "rules", "NORMS_UNSUPPORTED_PROFILE", "UnsupportedProfile", "/norms/0")),
    "N39": (change(_n39), record("4.7d", "rules", "NORMS_RESOURCE_LIMIT", "ResourceLimit", "/norms/2")),
    "N40": (change(lambda raw, norms: raw["vocabulary"]["predicates"]["c"].update(
        defined={"arguments": ["assistant"], "body": ["top"]})),
            record("1.1", "environment", "NORMS_INVALID_ENVIRONMENT", "InvalidInput", "/environment")),
}
# Python's legacy class on the exempt fixtures (2.12): another class than the record's.
EXEMPT = {"N32": "UnboundVariable", "N36": "ResourceLimit"}
# Python's legacy text where the fixture names it (8.1).
LEGACY_TEXTS = {"N33": "Unknown predicate 7", "N34": "Unknown constant 5", "N35": "Unknown binder sort 5",
                "N38": "$string quantification requires data stage 2"}
GOLDEN = {name: expected for name, (_, expected) in FIXTURES.items()}


def fixture_sources():
    """The sources of the fixtures of 8.1, for the gate's corpus."""
    return [(name, *build()) for name, (build, _) in FIXTURES.items()]


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_fixture_of_8_1(name):
    build, expected = FIXTURES[name]
    raw, norms = build()
    error = legacy(raw, norms)
    outcome = diagnose(raw, norms)
    if expected == "clean":
        assert error is None and outcome is CLEAN
        return
    assert error is not None and isinstance(outcome, Fault), (error, outcome)
    got = outcome.record
    assert {key: got[key] for key in expected if key not in ("text", "args")} == {
        key: value for key, value in expected.items() if key not in ("text", "args")}
    if "text" in expected:
        assert (got["text"], got["args"]) == (expected["text"], expected["args"])
    else:
        assert got["args"] == {"message": got["text"]}
    # The class rule (2.12): the record's class is the legacy code, except on the exempt fixtures.
    if name in EXEMPT:
        assert error.code == EXEMPT[name] != got["class"]
    elif got["check"] != "1.1":
        assert error.code == got["class"]
    if name in LEGACY_TEXTS:
        assert str(error) == LEGACY_TEXTS[name] == got["text"]


def test_non_first_order_tag_reads_invalid_indexed_formula():
    """J10: at a non-first-order tag Python's message is `invalid indexed formula`, whatever follows."""
    raw, norms = FIXTURES["N36"][0]()
    record = diagnose(raw, norms).record
    assert record["text"] == "invalid indexed formula"
    assert str(legacy(raw, norms)) == "AST exceeds depth or node budget"


def test_node_counts_of_n21():
    """Open point 6: each guard of N21 has 5,000 nodes, within its rule's decoding budget, and the three
    rules' guards and carve-outs pass 10,000 at unit 2's guard."""
    raw, norms = FIXTURES["N21"][0]()
    assert syntax_walk(norms[0]["norm"]["guard"]) == 5000
    assert str(legacy(raw, norms)) == "AST exceeds 10,000 nodes"


def first_order_formulas():
    """Formulas whose name positions hold strings, refused or not, for the syntax walk's agreement."""
    yield from (["top"], ATOM, ["binary", "c", ["var", 0], ["const", "k"]], ["eq", ["var", 0], ["var", 1]],
                ["forall", "assistant", ["exists", "user", ATOM]], nots(64, ["top"]), nots(65, ["top"]),
                ["unary", "c", ["var", -1]], ["unary", "c", ["var", True]], ["unary", "c", ["var", 2 ** 53]],
                ["unary", "c"], [], ["frob"], 5, ["and", ["top"]], ["unary", "c", ["unary", "c", ["var", 0]]],
                balanced([ATOM] * 3334), balanced([ATOM] * 3333), ["eq", ["num", "1"], ["var", 0]])


@pytest.mark.parametrize("index", range(19))
def test_syntax_walk_agrees_with_the_decoder_on_first_order_formulas(index):
    """2.5: on a formula without a non-first-order tag the walk refuses the node at which `_Decoder` raises,
    with its text, and the budget member exactly where `_Decoder` raises `ResourceLimit`."""
    formula = list(first_order_formulas())[index]
    try:
        _Decoder().decode(formula)
        decoded = None
    except VEError as exc:
        decoded = exc
    try:
        syntax_walk(formula)
        refused = None
    except Refused as exc:
        refused = exc
    if formula == ["eq", ["num", "1"], ["var", 0]]:
        assert decoded is None and refused.message == "invalid indexed formula"
        return
    assert (decoded is None) == (refused is None)
    if decoded is not None:
        assert refused.message == str(decoded)
        assert (refused.member == "a") == (decoded.code == "ResourceLimit")


def test_examples_are_clean_and_accepted():
    for path in sorted((DIRECTORY / "examples/norms@0").glob("*.json")):
        value = json.loads(path.read_text())
        assert legacy(value["environment"], value["norms"]) is None
        assert diagnose(value["environment"], value["norms"]) is CLEAN


def test_every_catalogue_fault_alone_gives_its_expected_record_in_python():
    """Tier 0 of the gate, in Python: each fault of the catalogue alone is rejected by the legacy validator
    and the engine reports the expected record (the oracle's, from the hand-written check and path)."""
    for fault in catalogue("norms@0"):
        raw, norms = fault.source()
        error = legacy(raw, norms)
        outcome = diagnose(raw, norms)
        assert error is not None and isinstance(outcome, Fault), fault.name
        expected = expected_record(CONTRACT, fault)
        got = outcome.record
        assert {key: got[key] for key in expected} == expected, fault.name


def test_adapter_builds_the_root_and_refuses_cases_outside_the_domain():
    """2.2 and L5, in Python: the root of each case kind; an `admission` case selects the active units; a case
    whose `norms` is not an array, or whose environment lists `closure@0` or `norm-defaults@0`, is outside the
    unit's domain."""
    raw, norms = base()
    for kind in ("norms-elaborate", "norms-conflict", "norms-certificate"):
        assert norm_source({"kind": kind, "environment": raw, "norms": norms}) == {"environment": raw,
                                                                                   "norms": norms}
    document = {"units": [{"id": f"u{i}", "span": [i, i + 1], "kind": "norm", "content": n}
                          for i, n in enumerate(norms)] + [{"id": "q", "kind": "quoted", "content": norms[0]}],
                "graph": {"root": "r", "nodes": []}}
    assert norm_source({"kind": "admission", "environment": raw, "document": document})["norms"] == norms
    with pytest.raises(UnsupportedProfile, match="case kind soft-elaborate has no wire contract input"):
        norm_source({"kind": "soft-elaborate", "environment": raw, "norms": norms})
    closure = deepcopy(raw)
    closure["profiles"] = ["closure@0", "norms@0", "relational-fol@0"]
    defaults = deepcopy(raw)
    defaults["profiles"] = ["norm-defaults@0", "norms@0", "relational-fol@0"]
    for environment, value in ((raw, "x"), (closure, norms), (defaults, norms), (raw, [1])):
        with pytest.raises(UnsupportedProfile) as raised:
            norm_source({"kind": "norms-elaborate", "environment": environment, "norms": value})
        assert str(raised.value) == OUTSIDE


def test_rule_name_class_is_the_validators():
    """T8, in Python: `rule_name` admits `a-b` and refuses `a_b`, `A` and a 65-byte name, as `_NAME` and the
    64-byte bound of `NormDocument` do."""
    from ve.wire_contract.engine import _name
    assert _name("a-b", NAMES["rule_name"]) and _name("a" * 64, NAMES["rule_name"])
    assert not any(_name(value, NAMES["rule_name"]) for value in ("a_b", "A", "a" * 65, "", "1a", "a-B"))


def test_a_renamed_hook_without_a_fault_is_wc08(tmp_path, monkeypatch):
    """T6: `norms@0.json` with hook 4.4 renamed `predicate_is_regulated`, without a catalogue fault for it, is
    `WC08`; the committed tree has no finding for 4.3 (gap G3)."""
    assert wire_tool.process(wire_tool.DATA) == []
    copy = tmp_path / "ve/wire_contract"
    shutil.copytree(DIRECTORY, copy, ignore=shutil.ignore_patterns("__pycache__"))
    path = copy / "norms@0.json"
    text = path.read_text().replace('"hook": "regulated_predicate"', '"hook": "predicate_is_regulated"')
    path.write_text(text)
    findings = wire_tool.process(copy, catalogue={"norms@0": set()})
    assert any(": WC08: " in finding for finding in findings)


def test_golden_records_are_current():
    """The hand-derived records of 8.1, materialised for review (`conformance/wire_contract_golden.py --unit`)."""
    from conformance.wire_contract_golden import ROOT as REPORTS, unit_reports
    for filename, body in unit_reports("norms@0").items():
        assert json.loads((REPORTS / filename).read_text()) == body
