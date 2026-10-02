"""Hand-derived format-1 cases from wire-contract.md section 8.1."""

from copy import deepcopy
import json
from pathlib import Path
import shutil

import pytest

from ve.errors import VEError
from ve.wire import loads_json
from ve.wire_contract.engine import CLEAN, Deferred, Fault, Registry, load, matches, overlay, run
from tools.wire_contract import english_table, process, wording


DIRECTORY = Path(__file__).resolve().parents[1] / "conformance/wire-contract/contracts"
CONTRACTS = {unit: load(unit, directory=DIRECTORY) for unit in ("demo@0", "inner@0", "defer@0")}
LIMITS = loads_json((DIRECTORY / "limits.json").read_bytes())
NAMES = loads_json((DIRECTORY / "names.json").read_bytes())


def _registry():
    def no_bad_name(root, items):
        names = [v for _, v in matches(root, items, "/doc/items/*/name")]
        return {"names": names} if "bad" in names else None
    def demo_rules(root, items):
        refs = root["doc"].get("refs", [])
        count = len(refs) if type(refs) is list else 0
        return ({3: ("4.3a", {"n": 3}), 2: ("4.3b", {}),
                 4: ("4.3z", {})}).get(count)
    return Registry().register(
        hooks={"no_bad_name": no_bad_name}, classifiers={"demo_rules": demo_rules},
        views={"part_view": lambda d: {"x": d["seed"] if type(d) is dict and "seed" in d else 0}})


def _run(unit, root, registry=None):
    return run(CONTRACTS[unit], root, registry=registry or _registry(), contracts=CONTRACTS,
               limits=LIMITS, names=NAMES)


BASE = {"doc": {"items": [{"name": "a", "tags": ["x", "y"]},
                          {"name": "b", "tags": []}], "mode": "open", "owner": "root",
                "refs": ["a"], "table": {"k": 1}, "part": {"x": 1, "ys": ["u"]},
                "seed": 7}}


def _case(change):
    value = deepcopy(BASE)
    change(value["doc"])
    return value


def _reversed_objects(value):
    if type(value) is dict:
        return {key: _reversed_objects(item) for key, item in reversed(list(value.items()))}
    if type(value) is list:
        return [_reversed_objects(item) for item in value]
    return value


CASES = [
    ("E1", BASE, None),
    ("E2", _reversed_objects(BASE), None),
    ("E3", _case(lambda d: (d.update(mode="shut"), d["items"][0].update(name="A!"))),
     ("1.4", "/doc/mode", 'Shape: mode "shut"')),
    ("E4", _case(lambda d: d.pop("refs")), ("1.1", "/doc", "Shape: document")),
    ("E5", _case(lambda d: d.update(zzz=1)), ("1.1", "/doc", "Shape: document")),
    ("E6", {"doc": []}, ("1.1", "/doc", "Shape: document")),
    ("E6b", {}, ("1.1", "/doc", "Shape: document")),
    ("E7", _case(lambda d: d.update(items={})), ("1.2", "/doc/items", "Shape: items")),
    ("E8", _case(lambda d: d.update(items=[{"name": x, "tags": []}
                                                for x in "abcd"])),
     ("1.3", "/doc/items", "Limit: 4 items, at most 3")),
    ("E9", _case(lambda d: d.update(refs=["a", 3])), ("1.5", "/doc/refs", "Shape: refs")),
    ("E10", _case(lambda d: d.update(mode="closed", note="n")),
     ("1.6", "/doc", "Shape: a closed document has a note")),
    ("E11", _case(lambda d: d.pop("owner")),
     ("1.7", "/doc", "Shape: an open document has no owner")),
    ("E12", _case(lambda d: d.update(owner="admin")),
     ("1.8", "/doc/owner", "Shape: owner admin")),
    ("E13", _case(lambda d: (d.update(mode="closed"), d.pop("owner"))), None),
    ("E14", _case(lambda d: d.update(refs=["a", "self"])),
     ("1.9", "/doc/refs", "Shape: refs names self")),
    ("E15", _case(lambda d: d.update(note="n", refs=["b"])),
     ("1.10", "/doc/refs", "Shape: a note needs the ref a")),
    ("E16", _case(lambda d: (d["items"][0].update(tags=[1]), d["items"][1].update(name="B"))),
     ("2.1d", "/doc/items/0/tags", "Shape: tags of a")),
    ("E17", _case(lambda d: (d["items"][0].update(tags=["y", "x"]),
                            d["items"][1].update(name="a"))),
     ("2.1c", "/doc/items/1/name", "Duplicate: a")),
    ("E18", _case(lambda d: (d["items"][0].update(name="A"), d["items"][1].update(name="B"))),
     ("2.1b", "/doc/items/0/name", "Name: A")),
    ("E19", _case(lambda d: d["items"][0].update(name=7)),
     ("2.1b", "/doc/items/0/name", "Name: 7")),
    ("E19b", _case(lambda d: d["items"][0].update(name="a__b")),
     ("2.1b", "/doc/items/0/name", "Name: a__b")),
    ("E19c", _case(lambda d: d["items"][0].update(name="abcdefghi")),
     ("2.1b", "/doc/items/0/name", "Name: abcdefghi")),
    ("E20", _case(lambda d: d["items"][1].update(tags=["long", "ok"])),
     ("2.2b", "/doc/items/1/tags/0", "Limit: tag long of b")),
    ("E21", _case(lambda d: d.update(table={"😀": 1, "ｚ": 1})),
     ("2.3a", "/doc/table/ｚ", "Name: ｚ")),
    ("E22", _case(lambda d: d.update(table={"k": "s"})),
     ("2.3b", "/doc/table/k", 'Shape: table entry k is "s"')),
    ("E23", _case(lambda d: d.update(table={"k": "a" * 100})),
     ("2.3b", "/doc/table/k", 'Shape: table entry k is "' + "a" * 79 + "...")),
    ("E24", _case(lambda d: d.update(refs=["a", "c"])),
     ("3.1", "/doc/refs/1", "Unknown: c")),
    ("E25", _case(lambda d: (d["items"][0].update(tags=["a", "b", "c"]),
                            d["items"][1].update(tags=["d", "e"]))),
     ("3.2", "", "Limit: 5 tags")),
    ("E26", _case(lambda d: d.update(part={"x": 1, "ys": ["u", 2]})),
     ("3.3/b2", "/doc/part/ys/1", "Inner: y 1")),
    ("E27", _case(lambda d: d.update(seed="s")),
     ("3.4/b1", "/doc", 'Inner: x is "s"')),
    ("E28", _case(lambda d: d.update(items=[{"name": "z", "tags": []},
                                               {"name": "bad", "tags": []}], refs=["z"])),
     ("4.1", "", "Semantic: bad, z")),
    ("E29a", _case(lambda d: d.update(refs=["a", "a", "b"])),
     ("4.3a", "", "Semantic: first 3")),
    ("E29b", _case(lambda d: d.update(refs=["a", "b"])),
     ("4.3b", "", "Semantic: second")),
    ("E30", _case(lambda d: d.update(refs=["a", "a", "b", "b"])), None),
    ("E31", _case(lambda d: d.update(items=[], refs=[], table={})), None),
    ("E32", _case(lambda d: (d.pop("table"), d.pop("part"), d.pop("seed"))), None),
]


@pytest.mark.parametrize("label,root,expected", CASES, ids=lambda value: value if type(value) is str else None)
def test_corpus(label, root, expected):
    outcome = _run("demo@0", root)
    if expected is None:
        assert outcome is CLEAN, label
    else:
        assert isinstance(outcome, Fault), label
        assert (outcome.record["check"], outcome.record["path"], outcome.record["text"]) == expected
        assert outcome.record["contract"] == "demo@0"
        assert outcome.record["revision"] == 1


def test_deferred_and_overlay():
    assert _run("defer@0", {"v": "x", "w": "x"}).record["check"] == "d1"
    assert _run("defer@0", {"v": 1, "w": "x"}) == Deferred("d2")
    outcome = _run("defer@0", {"v": 1, "w": 2, "note": "lean"})
    assert outcome == Deferred("d2")
    assert overlay(CONTRACTS["defer@0"], VEError("legacy says no"), outcome) == {
        "contract": "defer@0", "revision": 1, "deferred": "d2", "text": "legacy says no"}
    assert overlay(CONTRACTS["demo@0"], VEError("legacy says no"), CLEAN)["check"] == "residual"
    assert overlay(CONTRACTS["demo@0"], None, outcome) is None


def test_view_inner_path_and_recode():
    outcome = _run("demo@0", _case(lambda d: d.update(seed="s")))
    assert outcome.record["code"] == "DEMO_SEMANTIC"
    assert outcome.record["class"] == "InvalidInput"
    assert outcome.record["args"] == {"value": '"s"', "inner_path": "/x"}


def test_locks_and_wordings():
    assert process(DIRECTORY) == []
    check = CONTRACTS["demo@0"]["phases"][1]["checks"][0]["checks"][2]
    assert wording(check, inside=True) == (
        "the item's `name`, when present, differs from the same value of every earlier item of this group.")
    table = english_table(CONTRACTS["demo@0"], limits=LIMITS)
    assert "No check of this phase runs unless every check of the earlier phases holds" in table
    assert "For each member of `/doc/items/*`, in order" in table


def test_engine_json_replays_hand_derived_cases():
    fixture = json.loads((DIRECTORY.parent / "engine.json").read_text())
    assert len(fixture) == len(CASES)
    for item, (label, root, expected) in zip(fixture, CASES):
        assert item == {"id": label, "root": root, "expected": None if expected is None else
                        {"check": expected[0], "path": expected[1], "text": expected[2]}}
        outcome = _run("demo@0", item["root"])
        if item["expected"] is None:
            assert outcome is CLEAN
        else:
            assert isinstance(outcome, Fault)
            assert all(outcome.record[key] == value for key, value in item["expected"].items())


def test_lock_detects_edit_and_requires_revision(tmp_path):
    directory = tmp_path / "contracts"
    shutil.copytree(DIRECTORY, directory)
    path = directory / "inner@0.json"
    value = json.loads(path.read_text())
    value["codes"]["INNER_BAD"]["summary"] = "Changed summary"
    path.write_text(json.dumps(value))
    assert any("WC10" in finding for finding in process(directory))
    assert any("higher revision" in finding for finding in process(directory, write=True))
    value["revision"] += 1
    path.write_text(json.dumps(value))
    assert process(directory, write=True) == []
    assert process(directory) == []
