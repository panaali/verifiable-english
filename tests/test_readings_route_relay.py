"""The readings route relays Lean (docs/LEAN-FIRST-PLAN.md rule 2, lean-first batch 3).

`ve.readings_route.validate` returns `ve_readings_route`'s `readings-validate` row, or raises its diagnostic with
Lean's text verbatim; no Python regeneration or Rust replay is compared with it. A row that is malformed or not
bound to the request (its sets, versions, candidates in order, readings and situations) is `CheckerUnavailable`,
never a rejection and never an admission. The English of the report reads Lean's findings, and a construction of
the English that fails on a document Lean admitted is `CheckerUnavailable`.
"""
from __future__ import annotations

import copy

import pytest

import ve.readings_route as route
from tests.test_readings_s1_document import default, s1_document, strict
from tests.test_readings_s1_lean import LEAN, env_k, k1_document
from ve.document import check_document
from ve.errors import CheckerUnavailable, VEError

DECISION_ONLY = "It is not certified that these two readings differ only where"


@pytest.fixture(scope="module")
def lean():
    if not LEAN.exists():
        pytest.skip("ve_readings_route is not built")
    return LEAN


def units_of(document):
    return [{"id": u["id"], "kind": u.get("kind"), **({"content": u["content"]} if "content" in u else {})}
            for u in document["units"]]


@pytest.fixture(scope="module")
def k1(lean):
    """K1's request and Lean's genuine row for it."""
    raw = env_k()
    document, sid = k1_document(raw)
    row = route.validate(raw, units_of(document), document["reading_sets"])
    assert row["status"] == "ok" and row["content_bearing"] is True
    return raw, document, sid, row


def answering(monkeypatch, row):
    """The route's transport answers `row` (one case), as Lean's runner would."""
    monkeypatch.setattr(route, "run_readings_cases", lambda executable, cases: [copy.deepcopy(row)])


def test_a_genuine_row_is_returned_as_lean_wrote_it(k1):
    raw, document, _, row = k1
    lean_row = route.run_lean([{"id": "readings-s1", "kind": "readings-validate", "environment": raw,
                                "document": route.document_wire(units_of(document), document["reading_sets"])}])[0]
    assert row == lean_row


def test_an_error_row_is_raised_with_leans_text(monkeypatch, k1):
    raw, document, _, _ = k1
    text = "ReadingInterface: rs1: a text no Python code writes"
    answering(monkeypatch, {"id": "readings-s1", "status": "error", "error": text})
    with pytest.raises(VEError) as caught:
        route.validate(raw, units_of(document), document["reading_sets"])
    assert type(caught.value) is VEError and str(caught.value) == text


def _set(row):
    return row["sets"][0]


def _drop(path):
    def mutate(row):
        parent = row
        for key in path[:-1]:
            parent = parent[key]
        del parent[path[-1]]
    return mutate


def _put(path, value):
    def mutate(row):
        parent = row
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = value
    return mutate


CANDIDATE = ("sets", 0, "candidates", 1)
PAIR = ("sets", 0, "pairs", 0, "pair")
UNBOUND = {
    "content_bearing dropped": _drop(("content_bearing",)),
    "content_bearing a string": _put(("content_bearing",), "true"),
    "content_bearing false beside sets": _put(("content_bearing",), False),
    "sets dropped": _drop(("sets",)),
    "sets an object": _put(("sets",), {}),
    "an extra member": _put(("extra",), 1),
    "set entry duplicated": lambda row: row["sets"].append(copy.deepcopy(_set(row))),
    "set entry not an object": _put(("sets", 0), "rs1"),
    "set id not requested": _put(("sets", 0, "set"), "rs2"),
    "set version not requested": _put(("sets", 0, "version"), 2),
    "set version a boolean": _put(("sets", 0, "version"), True),
    "set findings dropped": _drop(("sets", 0, "findings")),
    "set findings not strings": _put(("sets", 0, "findings"), [7]),
    "candidates emptied": _put(("sets", 0, "candidates"), []),
    "candidates reordered": lambda row: _set(row)["candidates"].reverse(),
    "candidate duplicated": lambda row: _set(row)["candidates"].append(copy.deepcopy(_set(row)["candidates"][1])),
    "candidate id not the reading's": _put(CANDIDATE + ("id",), "strict"),
    "candidate index a boolean": _put(CANDIDATE + ("index",), True),
    "candidate index a string": _put(CANDIDATE + ("index",), "1"),
    "candidate pending a number": _put(CANDIDATE + ("pending",), 0),
    "candidate document_hash dropped": _drop(CANDIDATE + ("document_hash",)),
    "candidate document_hash a number": _put(CANDIDATE + ("document_hash",), 7),
    "candidate owned an object": _put(CANDIDATE + ("owned",), {}),
    "candidate owned entry without name": _drop(CANDIDATE + ("owned", 0, "name")),
    "candidate owned key a string": _put(CANDIDATE + ("owned", 0, "key"), "excepted"),
    "candidate findings null": _put(CANDIDATE + ("findings",), None),
    "pending candidate with a hash": lambda row: _set(row)["candidates"][1].update(pending=True),
    "pairs an object": _put(("sets", 0, "pairs"), {}),
    "pair reading not in the set": _put(("sets", 0, "pairs", 0, "reading"), "third"),
    "pair of a reading with itself": _put(("sets", 0, "pairs", 0, "other"), "strict"),
    "pair without facts": _drop(("sets", 0, "pairs", 0, "pair")),
    "pair situation not recorded": _put(PAIR + ("situation",), "0" * 64),
    "pair witness outside the pair": _put(PAIR + ("witness",), "third"),
    "pair separated a string": _put(PAIR + ("separated",), "true"),
    "pair separated dropped": _drop(PAIR + ("separated",)),
    "pair witness_admissible null": _put(PAIR + ("witness_admissible",), None),
    "pair witness_value a number": _put(PAIR + ("witness_value",), 0),
    "pair other_value a string": _put(PAIR + ("other_value",), "true"),
    "pair with an extra fact": _put(PAIR + ("certified",), True),
}


@pytest.mark.parametrize("fault", sorted(UNBOUND))
def test_a_row_not_bound_to_the_request_is_unavailable(monkeypatch, k1, fault):
    """Build checklist 4: Lean's genuine row with one field dropped, emptied, duplicated or retyped (a boolean
    for an integer included), or naming what the request does not hold, is an operational failure."""
    raw, document, _, row = k1
    bad = copy.deepcopy(row)
    UNBOUND[fault](bad)
    answering(monkeypatch, bad)
    with pytest.raises(CheckerUnavailable, match="ve_readings_route returned an invalid answer"):
        route.validate(raw, units_of(document), document["reading_sets"])


def test_a_row_without_content_bearing_sets_is_bound_only_alone(monkeypatch, k1):
    raw, document, _, _ = k1
    answering(monkeypatch, {"id": "readings-s1", "status": "ok", "content_bearing": False})
    assert route.validate(raw, units_of(document), document["reading_sets"])["content_bearing"] is False
    answering(monkeypatch, {"id": "readings-s1", "status": "ok", "content_bearing": False, "sets": []})
    with pytest.raises(CheckerUnavailable):
        route.validate(raw, units_of(document), document["reading_sets"])


def _filtered(monkeypatch, code):
    """The route with Lean's findings of `code` removed from its rows, as if Lean had not found them."""
    real = route.run_readings_cases

    def run(executable, cases):
        rows = real(executable, cases)
        for row in rows:
            for entry in row.get("sets", []):
                entry["findings"] = [f for f in entry["findings"] if not f.startswith(code + ":")]
        return rows
    monkeypatch.setattr(route, "run_readings_cases", run)


def test_the_decision_only_sentence_follows_leans_finding(tmp_path, monkeypatch, lean):
    """E14's last sentence (E25) is shown exactly when Lean reports `SeparatedByDecisionOnly` for the twins: Python
    no longer decides it (its `decision_only` was deleted in batch 3)."""
    path = s1_document(tmp_path, [strict(), default()])
    [pair] = check_document(path)["readings"]["sets"][0]["pairs"]
    assert pair["wording"] == "E14" and DECISION_ONLY in pair["text"]
    _filtered(monkeypatch, "SeparatedByDecisionOnly")
    [pair] = check_document(path)["readings"]["sets"][0]["pairs"]
    assert pair["wording"] == "E14" and DECISION_ONLY not in pair["text"]


def test_a_construction_failure_after_lean_admitted_is_unavailable(tmp_path, monkeypatch, lean):
    """Rule 2: Lean validates, Python constructs. Python's construction of the English failing on a document Lean
    admitted is a bug, reported as `CheckerUnavailable`, never as a rejection of the document."""
    path = s1_document(tmp_path, [strict(), default()])

    class Broken:
        def __init__(self, environment, document):
            raise KeyError("predicates")
    monkeypatch.setattr(route, "Decoded", Broken)
    with pytest.raises(CheckerUnavailable, match="ReadingsConstruction: .* KeyError"):
        check_document(path)
