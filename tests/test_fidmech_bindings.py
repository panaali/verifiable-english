"""fid-mech-b3: the case-to-atom tables frozen in usecases/<doc>/fidmech/bindings.json (plan 2a).

The sha256 of each file is pinned here, not in the file: a re-binding shows as an edit of this test in review. The
loader rebuilds the exact Python types run.py used as literals; a malformed table is refused by name.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from tools.fidmech import bindings as B

ROOT = Path(__file__).resolve().parents[1]
PINNED = {
    "anthropic-rsp": "86d75856b65cbe63a47cd1893e91a31e6eb329d71ed2c8d2f2394bc77b55bc0e",
    "openai-preparedness": "f6155b130d91414abe2400202130dfafcae2a5e01185b8c8ba5c14e756b3920b",
    "safety-framework": "bfccca31e1df9d322ae37a0e7596ae0b8ae7d663cc341f89cd2187ce9360b7b0",
}
# Plan 2a's lists; FSF DM and SEC are read from SELECTION_ITEMS, SILENT_ITEMS keeps SEC by reference in run.py,
# and item_predicates()'s inline kinds are INLINE_ITEMS and CATCH_ALL_OWN (REPORT section 1).
TABLES = {
    "anthropic-rsp": ["OT", "SCENARIO_TERMS", "SCENARIOS", "COMPETITORS", "SITUATIONS", "CASE_ATOMS", "PREDICATES",
                      "K_LIMITS"],
    "openai-preparedness": ["LEVEL_IDS", "ACTIVITY", "OT", "SITUATIONS", "STATED_FALSE", "SOME_HIGH_LEVEL", "ATOMS",
                            "K_ITEMS", "ALL_OF", "SUBJECT", "WITNESS", "WITNESS_LEVELS", "WITNESS_RELATIONS",
                            "THRESHOLD_PREDICATES", "SAFEGUARD_PREDICATES_ADDED", "CRITICAL_PREDICATES"],
    "safety-framework": ["SELECTION_ITEMS", "SILENT_ITEMS", "INLINE_ITEMS", "CATCH_ALL_OWN"],
}
# The module attributes each run.py keeps, read from the bindings (tests/test_rsp_fidelity_fix.py reads RSP's).
ATTRIBUTES = {
    "anthropic-rsp": TABLES["anthropic-rsp"],
    "openai-preparedness": ["LEVEL_IDS", "ACTIVITY", "OT", "SITUATIONS", "STATED_FALSE", "SOME_HIGH_LEVEL", "ATOMS",
                            "K_ITEMS", "ALL_OF", "THRESHOLD_PREDICATES", "SAFEGUARD_PREDICATES",
                            "CRITICAL_PREDICATES", "SUBJECT", "WITNESS", "WITNESS_LEVELS", "WITNESS_RELATIONS"],
    "safety-framework": ["SELECTION_ITEMS", "DM", "SEC", "SILENT_ITEMS", "INLINE_ITEMS", "CATCH_ALL_OWN"],
}


def path(document):
    return ROOT / "usecases" / document / "fidmech" / "bindings.json"


@pytest.mark.parametrize("document", sorted(PINNED))
def test_each_bindings_file_has_its_pinned_sha256(document):
    assert hashlib.sha256(path(document).read_bytes()).hexdigest() == PINNED[document]


@pytest.mark.parametrize("document", sorted(PINNED))
def test_each_file_is_the_canonical_dump_of_its_tables_and_names_plan_2as_tables(document):
    data = json.loads(path(document).read_text())
    tables = B.load_bindings(path(document), document)
    assert list(tables) == TABLES[document]
    text = B.dump_bindings(document, data["frozen_from"], data["run_py_blob"],
                           {name: (data["tables"][name]["type"], value) for name, value in tables.items()})
    assert text == path(document).read_text()
    assert len(data["frozen_from"]) == len(data["run_py_blob"]) == 40


def deep_types(value):
    """The type tree of a value: (type name, member trees) for containers."""
    if isinstance(value, dict):
        return ("dict", tuple(sorted({deep_types(v) for v in value.values()})))
    if isinstance(value, (list, tuple, set)):
        return (type(value).__name__, tuple(sorted({deep_types(v) for v in value})))
    return (type(value).__name__,)


def test_the_loader_rebuilds_the_exact_python_types_of_the_literals():
    rsp, pf, fsf = (B.load_bindings(path(d), d) for d in ("anthropic-rsp", "openai-preparedness", "safety-framework"))
    assert deep_types(rsp["SITUATIONS"]) == ("dict", (("tuple", (("str",),)),))
    assert deep_types(rsp["COMPETITORS"]) == ("list", (("str",),))
    assert rsp["CASE_ATOMS"] == {"K20": (("develops_highly_capable", "c"),)}
    assert deep_types(rsp["SCENARIO_TERMS"]) == ("dict", (("dict", (("str",),)),))
    assert type(pf["SOME_HIGH_LEVEL"]) is set and type(pf["ALL_OF"]) is set
    assert pf["WITNESS_RELATIONS"] == {"C1": (("adjustment_area", "s", "biological_and_chemical"),)}
    assert type(pf["THRESHOLD_PREDICATES"]) is tuple
    assert fsf["SELECTION_ITEMS"]["DM"] == (("harm_mitigated", "severe_harm_mitigated", "significant_harm_mitigated"),
                                            True)
    assert fsf["SELECTION_ITEMS"]["FORBIDS"] == (("proceed",), False)
    assert fsf["INLINE_ITEMS"] == {"GOV": ("proceed",), "SILENT:CCA+GOV": ("assessed", "proceed"),
                                   "FORBIDS+L0": ("proceed",), "CHECKPOINT_MCCA": ("change_assessed",)}


@pytest.mark.parametrize("document", sorted(PINNED))
def test_run_py_keeps_each_table_as_a_module_attribute_read_from_the_bindings(document):
    source = (ROOT / "usecases" / document / "run.py").read_text()
    assert B.bound_names(source) == ATTRIBUTES[document]
    tables = B.load_bindings(path(document), document)
    values = B.module_tables(source, {"_B": tables})
    direct = [name for name in TABLES[document] if f'\n{name} = _B["{name}"]' in source]
    assert direct and all(values[name] is tables[name] for name in direct)
    assert B._subscripts(source) == set(TABLES[document])


TYPES = [
    ("str", "a", "a"), ("bool", True, True), ("int", 3, 3), ("list[str]", ["a"], ["a"]),
    ("set[str]", ["b", "a"], {"a", "b"}), ("tuple[str,...]", ["a", "b"], ("a", "b")),
    ("tuple[tuple[str,...],bool]", [["a"], False], (("a",), False)),
    ("dict[str,tuple[tuple[str,...],...]]", {"K": [["p", "c"]]}, {"K": (("p", "c"),)}),
    ("dict[str,dict[str,str]]", {"a": {"b": "c"}}, {"a": {"b": "c"}}),
]


@pytest.mark.parametrize("type_, data, value", TYPES)
def test_each_type_round_trips(type_, data, value):
    built = B.build(B.parse_type(type_), data, "t")
    assert built == value and deep_types(built) == deep_types(value)
    assert B.unbuild(built) == (sorted(data) if type_.startswith("set") else data)


@pytest.mark.parametrize("type_, data, message", [
    ("str", 1, "expected str"), ("bool", 0, "expected bool"), ("int", True, "expected int"),
    ("tuple[str,bool]", ["a"], "expected 2 members"), ("set[str]", ["a", "a"], "twice"),
    ("dict[str,str]", ["a"], "expected dict"), ("list[str]", ["a", 1], r"t\[1\]: expected str"),
])
def test_a_value_of_the_wrong_shape_is_refused_with_its_path(type_, data, message):
    with pytest.raises(B.BindingsError, match=message):
        B.build(B.parse_type(type_), data, "t")


@pytest.mark.parametrize("type_", ["float", "dict[int,str]", "list[str,str]", "tuple[...]", "list[str", "strx"])
def test_an_unknown_or_malformed_type_is_refused(type_):
    with pytest.raises(B.BindingsError, match="type"):
        B.parse_type(type_)


def test_a_type_that_loses_the_value_is_refused_at_dump():
    with pytest.raises(B.BindingsError, match="does not rebuild"):
        B.dump_bindings("d", "c", "b", {"T": ("tuple[str,...]", ["a"])})


@pytest.mark.parametrize("change, message", [
    (lambda d: d.update(schema="fidmech-bindings/0"), "schema"),
    (lambda d: d.update(extra=1), "keys"),
    (lambda d: d.update(document="other"), "document"),
    (lambda d: d.update(tables={}), "non-empty"),
    (lambda d: d.pop("run_py_blob"), "keys"),
    (lambda d: d.update(run_py_blob=7), "run_py_blob a blob"),
    (lambda d: d["tables"]["OT"].update(note="x"), "OT is not"),
    (lambda d: d["tables"]["SITUATIONS"]["value"].update(K2="x"), r"SITUATIONS\.K2: expected tuple"),
])
def test_a_malformed_bindings_file_is_refused_by_name(tmp_path, change, message):
    data = json.loads(path("anthropic-rsp").read_text())
    change(data)
    bad = tmp_path / "bindings.json"
    bad.write_text(json.dumps(data))
    with pytest.raises(B.BindingsError, match=message):
        B.load_bindings(bad, "anthropic-rsp")


OLD = '''X = 1
OT = {"OT2": "more_capable", "OT3": "exceeds"}
THRESHOLD = ("a", "b")
SAFE = THRESHOLD + ("c",)
K_LIMITS = {item: "limit" for item in ("K9", "K10")}
'''
NEW = '''X = 1
_B = load_bindings(HERE / "fidmech" / "bindings.json", "toy")
OT = _B["OT"]
THRESHOLD = _B["THRESHOLD"]
SAFE = THRESHOLD + _B["SAFE_ADDED"]
K_LIMITS = _B["K_LIMITS"]
INLINE = _B["INLINE"]
'''


def write_bindings(tmp_path, tables):
    case = tmp_path / "usecases" / "toy" / "fidmech"
    case.mkdir(parents=True)
    (case / "bindings.json").write_text(B.dump_bindings("toy", "abc", "def", tables))
    return case / "bindings.json"


def test_the_frozen_diff_compares_what_run_py_reads_with_the_literals_at_frozen_from(tmp_path):
    tables = {"OT": ("dict[str,str]", {"OT2": "more_capable", "OT3": "exceeds"}),
              "THRESHOLD": ("tuple[str,...]", ("a", "b")), "SAFE_ADDED": ("tuple[str,...]", ("c",)),
              "K_LIMITS": ("dict[str,str]", {"K9": "limit", "K10": "limit"}), "INLINE": ("list[str]", ["x"]),
              "UNREAD": ("list[str]", [])}
    lines = B.frozen_diff(write_bindings(tmp_path, tables), new_source=NEW, old_source=OLD)
    assert lines[1:] == ["  OT: same", "  THRESHOLD: same", "  SAFE: same", "  K_LIMITS: same",
                         "  INLINE: new name (no literal at frozen_from)", "  table UNREAD: not read by run.py"]


def test_the_frozen_diff_shows_a_changed_entry_and_a_changed_type(tmp_path):
    tables = {"OT": ("dict[str,str]", {"OT2": "more_capable", "OT3": "CHANGED"}),
              "THRESHOLD": ("list[str]", ["a", "b"]), "SAFE_ADDED": ("tuple[str,...]", ("c",)),
              "K_LIMITS": ("dict[str,str]", {"K9": "limit", "K10": "limit"}), "INLINE": ("list[str]", ["x"])}
    lines = B.frozen_diff(write_bindings(tmp_path, tables), new_source=NEW, old_source=OLD)
    assert [line.split(":")[0].strip() for line in lines if "DIFFERS" in line or "NOT EVALUATE" in line] == [
        "OT", "THRESHOLD", "SAFE"]


def test_run_py_names_the_loader_and_no_literal_of_a_moved_table_is_left():
    for document, names in TABLES.items():
        tree = ast.parse((ROOT / "usecases" / document / "run.py").read_text())
        literal = {node.targets[0].id for node in tree.body if isinstance(node, ast.Assign)
                   and isinstance(node.targets[0], ast.Name)
                   and isinstance(node.value, (ast.Dict, ast.Tuple, ast.List, ast.Set, ast.DictComp))
                   and not any(isinstance(n, ast.Name) and n.id == "_B" for n in ast.walk(node.value))}
        assert not literal & (set(names) | set(ATTRIBUTES[document])), document
