"""Lean's readings answers fuzzed against the route's check (lf-3 review B1 and B2, build checklist 4 and 5).

Every genuine `readings-validate` row of a corpus (K1's twins, K5's shared fixed table, K19's rights chain with chain
findings, K20's two sets, a pending candidate, K4's act-only finding, three readings with assertions, K12, K14's
witness against a side that owns a key, K6's fixed rule, K13's `holds` probe with a null value) is mutated at every node: each member dropped, each list reversed and each
element duplicated or removed, an extra member added, and each node replaced by 7, true, false, null, -1, "", "x",
[] (a list emptied), {} and a value nested 10,000 deep; then two faults at once. Each mutant must raise `CheckerUnavailable` from `validate`'s check and nothing else (never a `TypeError`,
never a rejection), unless it changes only what Lean alone decides and the check cannot know (`LEAN_DECIDED`: a
candidate's generated keys and chain findings, the other side's completion, which pairs are findings), and then it
is well formed. The transport's strict JSON reader is tested on repeated members and deep nesting.
"""
from __future__ import annotations

import copy
import json

import pytest

import ve.readings_route as route
from tests import lean_routes
from tests.test_readings_s1_document import default, s1_document, strict
from tests.test_readings_s1_lean import (EXCEPTED, M0, Q0, entry, env_k, env_rights, k1_document, norm,
                                         norm_object, reading, reading_set, situation_id)
from ve.backends.lean_service import _decode_json
from ve.document import check_document
from ve.errors import CheckerUnavailable

ASKS_ALL = ["forall", "agent", ["forall", "user", ["binary", "asks", ["var", 1], ["var", 0]]]]
ASKS = ["binary", "asks", ["var", 1], ["var", 0]]
NOT_ASKS = ["forall", "agent", ["forall", "user", ["not", ["binary", "asks", ["var", 1], ["var", 0]]]]]


def _deep(n=10_000):
    value = []
    for _ in range(n):
        value = [value]
    return value


REPLACEMENTS = (7, True, False, None, -1, "", "x", [], {}, "deep")


def units_of(document):
    return [{"id": u["id"], "kind": u.get("kind"), **({"content": u["content"]} if "content" in u else {})}
            for u in document["units"]]


def _k_requests():
    """The K requests of tests/test_readings_s1_lean.py that Lean admits, as (environment, document)."""
    raw = env_k()
    yield raw, k1_document(raw)[0]
    be_kind = ("u0", norm("be-kind", "help_required", True, "default"))
    shared = {"key": {"excepted": "be-kind"}, "tuples": [["a", "u"]]}
    yield raw, k1_document(raw, situation=entry(M0, "default", Q0, False, fixed=[shared], decisions=[EXCEPTED]),
                           fixed_units=[be_kind])[0]
    sigma2 = entry(M0, "default", {"outcome": {"predicate": "help_required", "tuple": ["a", "u"]}}, False,
                   decisions=[{"key": {"excepted": "be-kind"}, "tuples": [["a", "u"]]}])
    sid2 = situation_id(raw, sigma2)
    rs2 = reading_set("rs2", "u2", [
        reading("strict", norm("be-kind", "help_required", True), {"default": sid2}),
        reading("default", norm("be-kind", "help_required", True, "default"), {"strict": sid2})], {sid2: sigma2})
    yield raw, k1_document(raw, extra_sets=[rs2])[0]
    hedged = reading("hedged", ASKS_ALL, {"strict": "any-token"}, kind=["hedged", "probably", "asserted"])
    yield raw, {"units": [{"id": "u1"}], "reading_sets": [reading_set("rs1", "u1", [
        reading("strict", norm("no-deception", "avoid_required", True), {"hedged": "any-token"}), hedged], {})]}
    rights = env_rights()
    arbitrary = ["binary", "arbitrary_arrest", ["var", 1], ["var", 0]]

    def claim(mode):
        return {"right": {"name": "r9", "holder": "person", "guard": ["top"], "lines": [
            {"kind": "claim", "norm": norm_object("no-arbitrary-arrest", "arrest_permitted", False, mode,
                                                  guard=arbitrary)}]}}
    base = {"domains": {"state": ["texas"], "person": ["ann", "bob"]}, "constants": {},
            "relations": {"arbitrary_arrest": [["texas", "ann"]], "journalist": []}}
    sigma = entry(base, "default", {"outcome": {"predicate": "arrest_permitted", "tuple": ["texas", "ann"]}}, True,
                  decisions=[{"key": {"excepted": "no-arbitrary-arrest"}, "tuples": [["texas", "ann"]]}])
    sid = situation_id(rights, sigma)
    l29 = {"limitation": {"name": "l29", "scope": "all", "kinds": "all", "decided_by": "unstated", "factors": [],
                          "conditions": [
                              {"name": "determined_by_law", "role": "necessary",
                               "verbalisation": "the limitation is determined by law"},
                              {"name": "solely_for_permitted_purpose", "role": "necessary",
                               "verbalisation": "the limitation is solely for a permitted purpose"}]}}
    rs9 = reading_set("rs9", "u9", [reading("strict", claim("strict"), {"default": sid}, kind="right"),
                                    reading("default", claim("default"), {"strict": sid}, kind="right")],
                      {sid: sigma})
    yield rights, {"units": [{"id": "u9"}, {"id": "u29", "kind": "limitation", "content": l29}],
                   "reading_sets": [rs9]}


def _holds(reading_set):
    """K13: the pair recorded with the `holds` probe (tests/test_readings_s1_document.py)."""
    sigma = {"base": M0, "fixed": [], "witness": "strict", "decisions": [], "probe": "holds", "value": True}
    sid = situation_id(env_k(), sigma)
    out = copy.deepcopy(reading_set)
    for r in out["readings"]:
        r["admission"]["distinguishing_models"] = {o["id"]: sid for o in out["readings"] if o["id"] != r["id"]}
    out["situations"] = {sid: sigma}
    return out


@pytest.fixture(scope="module")
def corpus(tmp_path_factory):
    """(case, row) for every genuine ok `readings-validate` answer Lean gives on the corpus, recorded at the route's
    transport (S2's cases on the same transport, `readings-elaborate` and the verdict routes, are not S1's answer)."""
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service is not built")
    recorded = []
    real = route.rows

    def recording(mode, cases, **options):
        rows = real(mode, cases, **options)
        recorded.extend((case, copy.deepcopy(row)) for case, row in zip(cases, rows)
                        if row["status"] == "ok" and case["kind"] == "readings-validate")
        return rows
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(route, "rows", recording)
        for raw, document in _k_requests():
            route.validate(raw, units_of(document), document["reading_sets"])
        tmp = tmp_path_factory.mktemp("readings-corpus")
        for name, candidates in (
                ("k1", [strict(), default()]),
                ("k4", [("avoid", norm("avoid-x", "avoid_required", True), "norm"),
                        ("help", norm("help-x", "help_required", True), "norm")]),
                ("three", [("asks", ASKS_ALL, "asserted"), ("not-asks", NOT_ASKS, "asserted"), strict()]),
                ("k12", [("assert", ASKS_ALL, "asserted"), strict()]),
                ("k14", [strict(), default(sufficient=[ASKS], necessary=[["bottom"]])])):
            (tmp / name).mkdir()
            check_document(s1_document(tmp / name, candidates))
        (tmp / "k6").mkdir()
        check_document(s1_document(tmp / "k6", [strict(), default()],
                                   fixed=[("u0", norm("never-avoid", "avoid_required", False))]))
        (tmp / "k13").mkdir()
        check_document(s1_document(tmp / "k13", [("assert", ASKS_ALL, "asserted"), strict()], situations=_holds))
    assert len(recorded) == 12
    return recorded


def test_the_corpus_covers_every_shape(corpus):
    """The corpus exercises what the check binds: pending candidates, owned and shared keys, chain findings,
    both set findings, fixed tables and decisions, `other_value` present and absent, two sets, several pairs."""
    sets = [s for _, row in corpus if row["content_bearing"] for s in row["sets"]]
    candidates = [c for s in sets for c in s["candidates"]]
    facts = [p["pair"] for s in sets for p in s["pairs"]]
    situations = [e for case, _ in corpus for R in case["document"]["reading_sets"]
                  for e in R.get("situations", {}).values()]
    assert any(c["pending"] for c in candidates)
    assert any(c.get("owned") for c in candidates) and any(c.get("shared") for c in candidates)
    assert any(c.get("findings") for c in candidates)
    assert {f.split(":")[0] for s in sets for f in s["findings"]} == set(route.FINDING_RANK)
    assert any(e["fixed"] for e in situations) and any(e["decisions"] for e in situations)
    assert any("other_value" in f for f in facts) and any("other_value" not in f for f in facts)
    assert any(len(row.get("sets", [])) > 1 for _, row in corpus)
    assert max(len(s["pairs"]) for s in sets) >= 6


def _paths(value, path=()):
    yield path
    if type(value) is dict:
        for key, item in value.items():
            yield from _paths(item, path + (key,))
    elif type(value) is list:
        for n, item in enumerate(value):
            yield from _paths(item, path + (n,))


def _at(row, path):
    for key in path:
        row = row[key]
    return row


def _mutants(row):
    """(path, label, mutant) for every one- fault mutation of the row."""
    for path in _paths(row):
        node = _at(row, path)
        for value in REPLACEMENTS:
            if path:
                mutant = copy.deepcopy(row)
                _at(mutant, path[:-1])[path[-1]] = _deep() if value == "deep" else copy.deepcopy(value)
                yield path, f"replaced by {value!r}", mutant
        if path and type(path[-1]) is str:
            mutant = copy.deepcopy(row)
            del _at(mutant, path[:-1])[path[-1]]
            yield path, "dropped", mutant
        if path and type(path[-1]) is int:
            mutant = copy.deepcopy(row)
            parent = _at(mutant, path[:-1])
            parent.insert(path[-1], copy.deepcopy(parent[path[-1]]))
            yield path, "duplicated", mutant
            mutant = copy.deepcopy(row)
            del _at(mutant, path[:-1])[path[-1]]
            yield path, "removed", mutant
        if type(node) is list and len(node) > 1:
            mutant = copy.deepcopy(row)
            _at(mutant, path).reverse()
            yield path, "reversed", mutant
        if type(node) is dict:
            mutant = copy.deepcopy(row)
            _at(mutant, path)["extra"] = 1
            yield path, "extra member", mutant


# What Lean alone decides, which the request cannot bind: a candidate's generated keys (`owned`, `shared`), its
# hash and chain findings, the other side's completion, and which pairs are findings (the module docstring of
# ve/readings_route.py). Path patterns: `*` is any list index, and a pattern matches its descendants too.
LEAN_DECIDED = (
    ("sets", "*", "candidates", "*", "owned"),
    ("sets", "*", "candidates", "*", "shared"),
    ("sets", "*", "candidates", "*", "findings"),
    ("sets", "*", "pairs", "*", "pair", "other_admissible"),
    ("sets", "*", "pairs", "*", "pair", "other_value"),
    ("sets", "*", "findings"),
)


def _lean_decided(path):
    shape = tuple("*" if type(key) is int else key for key in path)
    return any(shape[:len(pattern)] == pattern for pattern in LEAN_DECIDED)


def test_every_mutant_of_a_genuine_answer_is_unavailable(corpus):
    """Build checklist 4 and 5: no mutant escapes as anything but `CheckerUnavailable`, and a mutant the check
    accepts changed only what Lean alone decides, into a well-formed row."""
    accepted, escaped, count = [], [], 0
    for case, row in corpus:
        route._check(row, case)
        for path, label, mutant in _mutants(row):
            count += 1
            try:
                route._check(mutant, case)
            except CheckerUnavailable:
                continue
            except Exception as exc:  # noqa: BLE001 - the point is that nothing else escapes
                escaped.append((path, label, type(exc).__name__))
                continue
            if mutant != row and not (_lean_decided(path) and route.ROW(mutant)):
                accepted.append((case["document"]["reading_sets"][0]["id"], path, label))
    assert count > 5_000
    assert escaped == []
    assert accepted == []


def _category(value):
    return "null" if value is None else type(value).__name__


def test_the_schema_alone_refuses_every_type_fault(corpus):
    """Each layer holds on its own (build checklist 13): the schema refuses every replacement that changes a
    node's JSON type, outside the two the producer allows (a null or Boolean `other_value`, a list emptied), and
    an empty `sets` or `candidates`."""
    for case, row in corpus:
        assert route.ROW(row)
        for path, label, mutant in _mutants(row):
            if not label.startswith("replaced") or not path:
                continue
            old, new = _at(row, path), _at(mutant, path)
            if _category(old) == _category(new) or (path[-1] == "other_value" and new in (None, True, False)):
                continue
            if new == [] and type(old) is list:
                continue
            assert not route.ROW(mutant), (path, label)
        if row["content_bearing"]:
            for path in (("sets",), ("sets", 0, "candidates")):
                mutant = copy.deepcopy(row)
                _at(mutant, path[:-1])[path[-1]] = []
                assert not route.ROW(mutant), path


def test_the_binding_alone_refuses_every_well_typed_mutant(corpus):
    """A mutant the schema passes is refused by the binding deliberately (`_Invalid`), not by a crash that the
    containment happens to catch."""
    for case, row in corpus:
        for path, label, mutant in _mutants(row):
            if mutant == row or _lean_decided(path) or not route.ROW(mutant) or path == ("id",):
                continue
            with pytest.raises(route._Invalid):
                route._bind(mutant, case["document"])
        if row["content_bearing"]:
            with pytest.raises(route._Invalid):
                route._bind({"id": row["id"], "status": "ok", "content_bearing": False}, case["document"])


@pytest.mark.parametrize("error", [TypeError, KeyError, ValueError, AttributeError, IndexError, RecursionError])
def test_a_failure_of_the_check_itself_is_contained(monkeypatch, corpus, error):
    case, row = corpus[0]

    def failing(row, document):
        raise error("injected")
    monkeypatch.setattr(route, "_bind", failing)
    with pytest.raises(CheckerUnavailable, match="the Lean readings route returned an invalid answer"):
        route._check(row, case)


def _two_faults(row):
    """Two type faults at once, at the first and last leaf of each set: the second must not mask the first."""
    leaves = [p for p in _paths(row) if p and type(_at(row, p)) not in (dict, list)]
    for first in leaves[:20]:
        for second in leaves[-20:]:
            if first != second:
                mutant = copy.deepcopy(row)
                _at(mutant, first[:-1])[first[-1]] = {}
                _at(mutant, second[:-1])[second[-1]] = 7
                yield mutant


def test_two_fault_mutants_are_unavailable(corpus):
    for case, row in corpus:
        for mutant in _two_faults(row):
            with pytest.raises(CheckerUnavailable):
                route._check(mutant, case)


@pytest.mark.parametrize("stdout", [
    '[{"id": "c", "status": "ok", "status": "ok"}]',
    '[{"id": "c", "status": "ok", "content_bearing": NaN}]',
    "[" * 100_000 + "]" * 100_000,
    '[{"id": "c", "status": "ok"}',
])
def test_the_transport_reads_strict_json(stdout):
    """A repeated member (the last would win in `json.loads`), a non-JSON number, nesting past the runtime limit
    and truncated output are no answer to the service's client (`_decode_json`: `ValueError`, which `LeanService`
    makes `CheckerUnavailable`), never a `RecursionError` or a silently chosen value."""
    with pytest.raises(ValueError):
        _decode_json(stdout.encode())


def test_the_transport_still_reads_every_genuine_answer(corpus):
    """Lean's rows carry `null` (an unknown `witness_value` or `other_value`), which `ve.wire.loads_json` refuses:
    the strict reader must still read every genuine answer."""
    assert any("null" in json.dumps(row) for _, row in corpus)
    for _, row in corpus:
        assert _decode_json(json.dumps([row]).encode()) == [row]


def test_a_pair_lean_never_answers_is_not_rendered(tmp_path, monkeypatch, corpus):
    """lf-3 review B1: `separated: false` on a genuine K1 row used to reach the English, which then said "They
    differ here". The document path now reports the route unavailable instead."""
    path = s1_document(tmp_path, [strict(), default()])
    real = route.rows

    def unseparated(mode, cases, **options):
        rows = real(mode, cases, **options)
        for row in rows:
            for s in row.get("sets", []):
                for p in s["pairs"]:
                    p["pair"]["separated"] = False
        return rows
    monkeypatch.setattr(route, "rows", unseparated)
    with pytest.raises(CheckerUnavailable, match="the Lean readings route returned an invalid answer"):
        check_document(path)
