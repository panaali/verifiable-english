"""The Lean wire contract engine (service mode `diagnose`) on the engine corpus of docs/spec/wire-contract.md 8.1.

The expected records are the hand-derived ones of the spec's "Expected" column (E1 to E36, Lean side),
written out whole: check, phase, code, class, path, text and args. Records are compared as canonical
JSON bytes (spec 2.7). The tables are `lean/VE/WireContract/Tables/Corpus.lean`.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

from tests import lean_routes
from ve.errors import VEError
from ve.wire import canonical_json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_lean_imports import diagnostic_only_violation, imports  # noqa: E402

LEAN = ROOT / "lean/.lake/build/bin/ve_service"

BASE = {"doc": {"items": [{"name": "a", "tags": ["x", "y"]}, {"name": "b", "tags": []}],
                "mode": "open", "owner": "root", "refs": ["a"], "table": {"k": 1},
                "part": {"x": 1, "ys": ["u"]}, "seed": 7}}


@pytest.fixture(scope="module")
def lean():
    if not LEAN.exists():
        pytest.skip("the Lean service has not been built")
    return LEAN


def diagnose(unit, roots):
    cases = [{"id": f"c{n}", "kind": "corpus", **root} for n, root in enumerate(roots)]
    rows = lean_routes.diagnose(unit, cases)
    assert [row["id"] for row in rows] == [case["id"] for case in cases]
    assert all(row["status"] == "ok" for row in rows)
    return rows


def outcome(row):
    if row["outcome"] == "clean":
        assert set(row) == {"id", "status", "outcome"}
        return "clean"
    assert row["outcome"] == "fault" and set(row) == {"id", "status", "outcome", "diagnostic"}
    return canonical_json(row["diagnostic"])


def record(check, phase, code, cls, path, text, args=None, contract="demo@0"):
    return canonical_json({"contract": contract, "revision": 1, "check": check, "phase": phase, "code": code,
                           "class": cls, "path": path, "text": text, "args": args or {}})


def shape(check, path, text, args=None):
    return record(check, "shape", "DEMO_SHAPE", "InvalidInput", path, text, args)


def changed(edit):
    root = copy.deepcopy(BASE)
    edit(root["doc"])
    return root


def reversed_members(value):
    """The same value, every object's members written in reverse order (E2)."""
    if isinstance(value, dict):
        return "{" + ",".join(json.dumps(k) + ":" + reversed_members(v) for k, v in reversed(value.items())) + "}"
    if isinstance(value, list):
        return "[" + ",".join(reversed_members(v) for v in value) + "]"
    return json.dumps(value)


def setter(**members):
    def edit(doc):
        for key, value in members.items():
            if value is DELETE:
                del doc[key]
            else:
                doc[key] = value
    return edit


DELETE = object()


def item(n, **members):
    def edit(doc):
        doc["items"][n].update(members)
    return edit


def both(*edits):
    def edit(doc):
        for e in edits:
            e(doc)
    return edit


A100 = "a" * 100
DEMO = {
    "E1": (BASE, "clean"),
    "E3": (changed(both(setter(mode="shut"), item(0, name="A!"))), shape("1.4", "/doc/mode", 'Shape: mode "shut"',
                                                                        {"value": '"shut"'})),
    "E4": (changed(setter(refs=DELETE)), shape("1.1", "/doc", "Shape: document")),
    "E5": (changed(setter(zzz=1)), shape("1.1", "/doc", "Shape: document")),
    "E6a": ({"doc": []}, shape("1.1", "/doc", "Shape: document")),
    "E6b": ({}, shape("1.1", "/doc", "Shape: document")),
    "E7": (changed(setter(items={})), shape("1.2", "/doc/items", "Shape: items")),
    "E8": (changed(setter(items=[{"name": n, "tags": []} for n in "abcd"])),
           record("1.3", "shape", "DEMO_LIMIT", "ResourceLimit", "/doc/items", "Limit: 4 items, at most 3",
                  {"count": "4", "limit": "3"})),
    "E9": (changed(setter(refs=["a", 3])), shape("1.5", "/doc/refs", "Shape: refs")),
    "E10": (changed(setter(mode="closed", note="n")), shape("1.6", "/doc", "Shape: a closed document has a note")),
    "E11": (changed(setter(owner=DELETE)), shape("1.7", "/doc", "Shape: an open document has no owner")),
    "E12": (changed(setter(owner="admin")), shape("1.8", "/doc/owner", "Shape: owner admin", {"value": "admin"})),
    "E13": (changed(setter(mode="closed", owner=DELETE)), "clean"),
    "E14": (changed(setter(refs=["a", "self"])), shape("1.9", "/doc/refs", "Shape: refs names self")),
    "E15": (changed(setter(note="n", refs=["b"])), shape("1.10", "/doc/refs", "Shape: a note needs the ref a")),
    "E16": (changed(both(item(0, tags=[1]), item(1, name="B"))),
            record("2.1d", "items", "DEMO_SHAPE", "InvalidInput", "/doc/items/0/tags", "Shape: tags of a",
                   {"name": "a"})),
    "E17": (changed(both(item(0, tags=["y", "x"]), item(1, name="a"))),
            record("2.1c", "items", "DEMO_DUPLICATE", "DuplicateDeclaration", "/doc/items/1/name", "Duplicate: a",
                   {"value": "a"})),
    "E18": (changed(both(item(0, name="A"), item(1, name="B"))),
            record("2.1b", "items", "DEMO_NAME", "InvalidInput", "/doc/items/0/name", "Name: A", {"value": "A"})),
    "E19a": (changed(item(0, name=7)),
             record("2.1b", "items", "DEMO_NAME", "InvalidInput", "/doc/items/0/name", "Name: 7", {"value": "7"})),
    "E19b": (changed(item(0, name="a__b")),
             record("2.1b", "items", "DEMO_NAME", "InvalidInput", "/doc/items/0/name", "Name: a__b",
                    {"value": "a__b"})),
    "E19c": (changed(item(0, name="abcdefghi")),
             record("2.1b", "items", "DEMO_NAME", "InvalidInput", "/doc/items/0/name", "Name: abcdefghi",
                    {"value": "abcdefghi"})),
    "E20": (changed(item(1, tags=["long", "ok"])),
            record("2.2b", "items", "DEMO_LIMIT", "ResourceLimit", "/doc/items/1/tags/0", "Limit: tag long of b",
                   {"value": "long", "name": "b"})),
    "E21": (changed(setter(table={"\U0001F600": 1, "ｚ": 1})),
            record("2.3a", "items", "DEMO_NAME", "InvalidInput", "/doc/table/ｚ", "Name: ｚ",
                   {"key": "ｚ"})),
    "E22": (changed(setter(table={"k": "s"})),
            record("2.3b", "items", "DEMO_SHAPE", "InvalidInput", "/doc/table/k", 'Shape: table entry k is "s"',
                   {"key": "k", "value": '"s"'})),
    "E23": (changed(setter(table={"k": A100})),
            record("2.3b", "items", "DEMO_SHAPE", "InvalidInput", "/doc/table/k",
                   'Shape: table entry k is "' + "a" * 79 + "...", {"key": "k", "value": '"' + "a" * 79 + "..."})),
    "E24": (changed(setter(refs=["a", "c"])),
            record("3.1", "references", "DEMO_UNKNOWN", "UnknownSymbol", "/doc/refs/1", "Unknown: c",
                   {"value": "c"})),
    "E25": (changed(both(item(0, tags=["a", "b", "c"]), item(1, tags=["d", "e"]))),
            record("3.2", "references", "DEMO_LIMIT", "ResourceLimit", "", "Limit: 5 tags", {"count": "5"})),
    "E26": (changed(setter(part={"x": 1, "ys": ["u", 2]})),
            record("3.3/b2", "references", "INNER_BAD", "InvalidInput", "/doc/part/ys/1", "Inner: y 1",
                   {"index": "1"})),
    "E27": (changed(setter(seed="s")),
            record("3.4/b1", "references", "DEMO_SEMANTIC", "InvalidInput", "/doc", 'Inner: x is "s"',
                   {"value": '"s"', "inner_path": "/x"})),
    "E28": (changed(setter(items=[{"name": "z", "tags": []}, {"name": "bad", "tags": []}], refs=["z"])),
            record("4.1", "semantic", "DEMO_SEMANTIC", "InvalidInput", "", "Semantic: bad, z", {"names": "bad, z"})),
    "E29a": (changed(setter(refs=["a", "a", "b"])),
             record("4.3a", "semantic", "DEMO_SEMANTIC", "InvalidInput", "", "Semantic: first 3", {"n": "3"})),
    "E29b": (changed(setter(refs=["a", "b"])),
             record("4.3b", "semantic", "DEMO_SEMANTIC", "InvalidInput", "", "Semantic: second")),
    "E30": (changed(setter(refs=["a", "a", "b", "b"])), "clean"),
    "E31": (changed(setter(items=[], refs=[], table={})), "clean"),
    "E32": (changed(setter(table=DELETE, part=DELETE, seed=DELETE)), "clean"),
    # Beyond the numbered cases (coverage rule of 8.1): pointer escaping of `~` and `/` in a key.
    "X1": (changed(setter(table={"a/b~": 1})),
           record("2.3a", "items", "DEMO_NAME", "InvalidInput", "/doc/table/a~1b~0", "Name: a/b~", {"key": "a/b~"})),
    # `exact_keys` with an extra key, and `sorted_unique` on a repeat and on a descent.
    "X2": (changed(item(1, x=1)),
           record("2.1a", "items", "DEMO_SHAPE", "InvalidInput", "/doc/items/1", "Shape: item 1", {"index": "1"})),
    "X3": (changed(item(0, tags=["y", "x"])),
           record("2.2a", "items", "DEMO_SHAPE", "InvalidInput", "/doc/items/0/tags", "Shape: tags of a are not sorted",
                  {"name": "a"})),
    "X4": (changed(item(0, tags=["x", "x"])),
           record("2.2a", "items", "DEMO_SHAPE", "InvalidInput", "/doc/items/0/tags", "Shape: tags of a are not sorted",
                  {"name": "a"})),
}

DEFER = {
    "E33": ({"v": "x", "w": "x"}, record("d1", "first", "DEFER_SHAPE", "InvalidInput", "/v", "Defer: v",
                                          contract="defer@0")),
    "E34": ({"v": 1, "w": "x"}, record("d3", "second", "DEFER_SHAPE", "InvalidInput", "/w", "Defer: w",
                                        contract="defer@0")),
    "E35": ({"v": 1, "w": 2, "note": "lean"},
            record("d2", "second", "DEFER_SHAPE", "InvalidInput", "", "Defer: lean only", contract="defer@0")),
    "E36": ({"v": 1, "w": 2}, "clean"),
}


@pytest.mark.parametrize("name", sorted(DEMO))
def test_demo_corpus(lean, name):
    root, expected = DEMO[name]
    assert outcome(diagnose("demo@0", [root])[0]) == expected


def test_demo_corpus_one_batch(lean):
    """The same cases in one call, so that one batch's rows keep their order."""
    rows = diagnose("demo@0", [root for root, _ in DEMO.values()])
    assert [outcome(row) for row in rows] == [expected for _, expected in DEMO.values()]


def test_member_order_never_matters(lean):
    """E2: every object's members written in reverse order gives the same outcome as written."""
    text = "[" + reversed_members({"id": "E2", "kind": "corpus", **BASE}) + "]"
    assert [outcome(row) for row in lean_routes.diagnose_text("demo@0", text)] == ["clean"]
    edited = DEMO["E22"][0]
    rows = lean_routes.diagnose_text("demo@0", "[" + reversed_members({"id": "E22", **edited}) + "]")
    assert [outcome(row) for row in rows] == [DEMO["E22"][1]]


@pytest.mark.parametrize("name", sorted(DEFER))
def test_defer_corpus_in_lean(lean, name):
    """Lean never defers: it implements `lean_only`, which Python lacks (E33 to E36, Lean column)."""
    root, expected = DEFER[name]
    assert outcome(diagnose("defer@0", [root])[0]) == expected


def test_inner_contract_alone(lean):
    rows = diagnose("inner@0", [{"x": 1, "ys": ["u"]}, {"x": 1, "ys": ["u", 3]}, {"x": True}])
    assert [outcome(row) for row in rows] == [
        "clean",
        record("b2", "body", "INNER_BAD", "InvalidInput", "/ys/1", "Inner: y 1", {"index": "1"}, "inner@0"),
        record("b1", "body", "INNER_BAD", "InvalidInput", "/x", "Inner: x is true", {"value": "true"}, "inner@0"),
    ]


def test_runner_errors(lean):
    """Spec 4.2 in the service: an unknown unit is an error row with the runner's text (the one-shot
    runner exited 2 with it), a batch the restricted decoder refuses is a request error, and a case
    beyond the depth limit is an error row."""
    [unknown] = lean_routes.diagnose("nope@0", [{"id": "u"}])
    assert unknown == {"id": "u", "status": "error", "error": "UnsupportedProfile: no wire contract nope@0"}
    [unnamed] = lean_routes.rows("diagnose", [{"id": "v"}])
    assert unnamed == {"id": "v", "status": "error", "error": "InvalidInput: a diagnose case names its unit"}
    with pytest.raises(VEError):
        lean_routes.diagnose_text("demo@0", '[{"id": "ok", "doc": null}]')
    deep = '{"id": "deep", "doc": ' + "[" * 300 + "]" * 300 + "}"
    rows = lean_routes.diagnose_text("demo@0", "[" + deep + ', {"id": "fine"}]')
    assert rows[0] == {"status": "error", "case_index": 0, "error": "ResourceLimit: JSON depth exceeds 256"}
    assert rows[1]["status"] == "ok" and rows[1]["outcome"] == "fault"


def test_diagnostic_only_import_rule():
    """Spec 7.3 and fixture L14: only the engine's own modules, the service's diagnose mode `VE.Service.Diagnose`
    (the one-shot root `DiagnoseMain` before lean-first batch 1) and (the engine only) `VE.Audit` may import
    `VE.WireContract.*`; the tree keeps the rule."""
    assert diagnostic_only_violation("VE.SoftNorms.Run", "VE.WireContract.Engine")
    assert diagnostic_only_violation("VE", "VE.WireContract.Table")
    assert diagnostic_only_violation("VE.Audit", "VE.WireContract.Diagnose")
    assert diagnostic_only_violation("Main", "VE.WireContract.Diagnose")
    assert diagnostic_only_violation("VE.Audit", "VE.WireContract.Engine") is None
    assert diagnostic_only_violation("DiagnoseMain", "VE.WireContract.Diagnose")
    assert diagnostic_only_violation("VE.Service.Diagnose", "VE.WireContract.Diagnose") is None
    assert diagnostic_only_violation("VE.Service.Protocol", "VE.WireContract.Diagnose")
    assert diagnostic_only_violation("VE.WireContract.Diagnose", "VE.WireContract.Engine") is None
    assert diagnostic_only_violation("VE.SoftNorms.Run", "VE.WireContracts") is None
    lean = ROOT / "lean"
    found = []
    for path in lean.rglob("*.lean"):
        if ".lake" in path.parts:
            continue
        importer = ".".join(path.relative_to(lean).with_suffix("").parts)
        found += [m for imported in imports(path.read_text())
                  if (m := diagnostic_only_violation(importer, imported)) is not None]
    assert found == []
