"""B1's input and its check (docs/spec/scope-PLAN.md, benchmarks B1 and C11): the case `tools/bench/scope_b1.py`
builds is F1-doc's block over the full pinned constitution, and a run whose layout is not C11's is reported, not
timed. The timing itself is `tools/bench/test_perf.py::test_scope_b1`, never the suite."""
from __future__ import annotations

import hashlib
import json

import pytest

from tools.bench import scope_b1 as B


def _parts(text: str):
    end = text.index("\n---\n", 4)
    return json.loads(text[4:end]), text[end + 5:].encode()


def test_b1_is_f1s_block_over_the_pinned_constitution():
    front, source = B.pinned()
    meta, body = _parts(B.case()["document"])
    f1, excerpt = _parts(B.F1.read_text())
    assert body == source and len(body) == B.SOURCE_BYTES and hashlib.sha256(body).hexdigest() == B.SOURCE_SHA256
    assert [u["id"] for u in meta["units"]] == [u["id"] for u in front["units"]] and len(meta["units"]) == B.UNITS
    ours = {u["id"]: u for u in f1["units"]}
    at = body.index(excerpt)
    for unit, pilot in zip(meta["units"], front["units"]):
        assert unit["span"] == pilot["span"]
        if unit["id"] in ours:
            s, e = ours[unit["id"]]["span"]
            assert unit == {**ours.pop(unit["id"]), "span": [s + at, e + at]} and body[s + at:e + at] == excerpt[s:e]
        else:
            assert unit == pilot
    assert not ours and meta["scope"] == f1["scope"] and "scope@0" in meta["environment"]["profiles"]
    for kind, entries in f1["environment"]["vocabulary"].items():
        assert all(meta["environment"]["vocabulary"][kind][k] == v for k, v in entries.items())
    assert all(t in meta["open_terms"] for t in f1["open_terms"])


ROWS = [{"id": "a", "span": [0, 3], "item": None, "midLine": False, "lead": True, "label": False, "para": 0},
        {"id": "b", "span": [3, 7], "item": 0, "midLine": False, "lead": False, "label": False, "para": 1}]


@pytest.mark.parametrize("field, value", [("id", "c"), ("span", [3, 8]), ("item", 1), ("midLine", True),
                                          ("lead", True), ("label", True), ("para", 2)])
def test_every_layout_field_is_in_the_hash(field, value):
    assert B.layout_sha256([ROWS[0], {**ROWS[1], field: value}]) != B.layout_sha256(ROWS)


def test_a_run_that_is_not_b1_is_reported(monkeypatch):
    monkeypatch.setattr(B, "LAYOUT_SHA256", B.layout_sha256(ROWS))
    good = {"layout": ROWS, "lead": B.LEAD, "run": B.F1_RUN, "governFast": {"ok": B.GOVERNED}}
    assert B.problems(good, True) == [] and B.problems({**good, "governFast": None}, False) == []
    assert B.problems({"error": "ScopeOrphanPart: u0165.s01"}, False) == \
        ["the scope block does not decode: ScopeOrphanPart: u0165.s01"]
    changed = B.problems({**good, "layout": [ROWS[0], {**ROWS[1], "para": 2}]}, True)
    assert len(changed) == 1 and changed[0].startswith("the layout is not C11's")
    assert len(B.problems({**good, "run": B.F1_RUN[:-1]}, True)) == 1
    assert len(B.problems({**good, "lead": "u0164.s01"}, True)) == 1
    for answer in ({"ok": B.GOVERNED[:-1]}, {"error": "ScopeNoEffect: g1"}, None):
        assert len(B.problems({**good, "governFast": answer}, True)) == 1
        assert B.problems({**good, "governFast": answer}, False) == []
