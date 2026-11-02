"""The relay never accepts a Lean cardinality answer that is not an answer to its request (quantities QT-A4, R8). Genuine
answers of each case kind are mutated one and two faults at a time (each member dropped, emptied, retyped, duplicated,
reordered, an index out of range): every mutant is `CheckerUnavailable` or changes nothing the relay returns."""
from __future__ import annotations

import copy
import random

import pytest

from tests.test_cardinality_lean import CASES, ENV, FA1, GRAPH, TOP, text
from ve import cardinality
from ve.backends import relay
from ve.document.lean import _lean_answer, _lean_document
from ve.errors import CheckerUnavailable

REAL_ROWS = relay.rows
RETYPED = (7, True, None, [], {}, 1.5, "\ud800", "absent", -1, 999, ["x"], [[[[[]]]]])
CM = CASES["fa1b-countermodel"]
PROBLEM = (FA1["environment"], FA1["premises"], FA1["conclusion"])
CALLS = {"admission": lambda: cardinality.admission(*PROBLEM),
         "certificate": lambda: cardinality.check_certificate(*PROBLEM, CASES["fa1-certificate"]["certificate"]),
         "countermodel": lambda: cardinality.countermodel(CM["environment"], CM["premises"], CM["conclusion"], CM["model"]),
         "document": lambda: cardinality.document(ENV, GRAPH["document"]),
         "paraphrase": lambda: cardinality.paraphrase(FA1["environment"], FA1["premises"][0])}


def _nodes(value, path=(), depth=5):
    """Each member to `depth`, with its path, and a list's first and last rows: a deeper formula node or a middle row is
    one more of its kind."""
    if path:
        yield path, value
    if depth and type(value) is dict:
        for key, child in value.items():
            yield from _nodes(child, (*path, key), depth - 1)
    elif depth and type(value) is list:
        for index in sorted({0, len(value) - 1}) if value else ():
            yield from _nodes(value[index], (*path, index), depth - 1)


def _replaced(row, path, value):
    out = copy.deepcopy(row)
    parent = out
    for step in path[:-1]:
        parent = parent[step]
    if value is _replaced:
        del parent[path[-1]]
    else:
        parent[path[-1]] = value
    return out


def _mutants(row):
    for path, value in _nodes(row):
        yield f"{path} dropped", _replaced(row, path, _replaced)
        for other in RETYPED:
            if other != value or type(other) is not type(value):
                yield f"{path} := {other!r}", _replaced(row, path, other)
        if type(value) is str:
            yield f"{path} := ''", _replaced(row, path, "")
            yield f"{path} shifted", _replaced(row, path, value + "0")
        if type(value) is int and type(value) is not bool:
            yield f"{path} out of range", _replaced(row, path, value + 1)
        if type(value) is list and value:
            for name, other in (("emptied", []), ("first duplicated", [value[0], *value]), ("reversed", value[::-1]),
                                ("last duplicated", [*value, value[-1]]), ("first dropped", value[1:])):
                if other != value:
                    yield f"{path} {name}", _replaced(row, path, other)


def _answered(monkeypatch, row, call=0):
    """The Lean service answers `row` to the relay's `call`th `rows` (to all of them when it is None); every other runs."""
    seen = []

    def rows(mode, cases, **options):
        seen.append(mode)
        return [copy.deepcopy(row)] if call is None or len(seen) - 1 == call else REAL_ROWS(mode, cases, **options)
    monkeypatch.setattr(relay, "rows", rows)


@pytest.fixture
def genuine(monkeypatch):
    """A case kind's genuine row and answer; `identities`, a function of the request alone, looked up per mutant."""
    table = {tuple(e["profiles"]): cardinality.identities(e) for e in (FA1["environment"], ENV)}
    monkeypatch.setattr(cardinality, "identities", lambda environment: table[tuple(environment["profiles"])])
    seen = []

    def recording(mode, cases, **options):
        seen.append(REAL_ROWS(mode, cases, **options))
        return seen[-1]

    def of(kind):
        with monkeypatch.context() as patch:
            patch.setattr(relay, "rows", recording)
            answer = CALLS[kind]()
        return seen[0][0], answer
    return of


def _lean_s(name):
    """What R8 leaves to Lean, typed by the schema and bound to nothing: another wording of a line and a countermodel's
    verdict and sizes, each of the same type (`test_cardinality_service.py` retypes each)."""
    return name.startswith(("('paraphrase',)", "('assumptions',", "('refutes',)")) or (
        name.startswith("('sizes',") and "'size'" in name and any(x in name for x in ("out of range", ":= 7", ":= 999")))


def _changed(call, answer) -> bool:
    try:
        return not cardinality._same(call(), answer)
    except CheckerUnavailable:
        return False


@pytest.mark.parametrize("kind", list(CALLS))
def test_every_one_fault_mutant_is_refused_or_changes_nothing(monkeypatch, genuine, kind):
    row, answer = genuine(kind)
    assert not _changed(CALLS[kind], answer)
    accepted = []
    for name, mutant in _mutants(row):
        _answered(monkeypatch, mutant)
        if _changed(CALLS[kind], answer) and not _lean_s(name):
            accepted.append(name)
    assert not accepted


@pytest.mark.parametrize("kind", list(CALLS))
def test_two_faults_at_a_time_are_refused_or_change_nothing(monkeypatch, genuine, kind):
    row, answer = genuine(kind)
    rng, pool, accepted = random.Random(f"qt-a4 {kind}"), list(_mutants(row)), []
    for name, first in rng.sample(pool, min(120, len(pool))):
        if nodes := list(_nodes(first)):
            fault, path = rng.choice((*RETYPED, _replaced)), rng.choice(nodes)[0]
            other = f"{path} := {fault!r}"
            _answered(monkeypatch, _replaced(first, path, fault))
            if _changed(CALLS[kind], answer) and not (_lean_s(name) or _lean_s(other)):
                accepted.append((name, other))
    assert not accepted


@pytest.mark.parametrize("change", [
    lambda r: r["regions"]["constants"][0].update(constant="cardinality__fomc_policymaker__absent"),
    lambda r: r["regions"]["constants"][0].update(bits="1"),
    lambda r: r["regions"]["constants"][0].update(sort="user"),
    lambda r: r["regions"]["constants"].append(r["regions"]["constants"][0]),
    lambda r: r["regions"]["constants"].pop(),
    lambda r: r["regions"]["constants"].reverse(),
    lambda r: r["regions"]["predicates"]["fomc_policymaker"].__setitem__(0, "absent"),
    lambda r: r["regions"]["predicates"]["fomc_policymaker"].__setitem__(0, "curious"),
    lambda r: r["regions"]["predicates"]["fomc_policymaker"].reverse(),
    lambda r: r["regions"]["predicates"].update(absent=[]),
    lambda r: r["erased"]["premises"].pop(4),
    lambda r: r["erased"]["premises"].insert(4, r["erased"]["premises"][4])],
    ids=["renamed", "bits", "sort", "duplicated", "dropped", "reordered", "undeclared", "other-sort", "predicates-reversed",
         "counted-sort", "bridge-dropped", "bridge-duplicated"])
def test_the_region_table_and_problem_are_bound(monkeypatch, genuine, change):
    row, _ = genuine("admission")
    mutant = copy.deepcopy(row)
    change(mutant)
    _answered(monkeypatch, mutant)
    with pytest.raises(CheckerUnavailable):
        CALLS["admission"]()


def test_a_renamed_region_is_refused_by_the_relay_itself(monkeypatch, genuine):
    """The seeded bug's fixture (plan QT-A4): a service answering every call alike, so Lean's confirmation cannot help, and
    the name changed in the table and its size alike, so only the binding to the request's sort and bits refuses it."""
    row, _ = genuine("countermodel")
    mutant = copy.deepcopy(row)
    mutant["regions"]["constants"][0]["constant"] = mutant["sizes"][0]["constant"] = "cardinality__fomc_policymaker__absent"
    _answered(monkeypatch, mutant, call=None)
    with pytest.raises(CheckerUnavailable, match="region"):
        CALLS["countermodel"]()


def _another_statement(statement):
    """Another statement under its own, correct meaning id: only the comparison with the request refuses it."""
    ids = cardinality.identities(FA1["environment"])
    statement.update(formula=TOP["formula"], meaning_id=cardinality.digest(f"ve-meaning-{ids.identity_version}\n", {
        "environment_id": ids.environment_id, "ast": TOP}))


@pytest.mark.parametrize("kind, change", [
    ("admission", lambda r: r["regions"]["constants"].reverse()),
    ("admission", lambda r: _another_statement(r["premises"][0])),
    ("countermodel", lambda r: r["sizes"].pop()),
    ("countermodel", lambda r: r["sizes"].reverse()),
    ("countermodel", lambda r: r["sizes"][0].update(size=True)),
    ("countermodel", lambda r: r["sizes"][0].update(size=-1)),
    ("countermodel", lambda r: r["sizes"][0].update(size="3"))],
    ids=["table-reordered", "another-statement", "sizes-dropped", "sizes-reordered", "size-bool", "size-negative", "size-text"])
def test_the_relay_s_own_checks_hold_when_lean_cannot_confirm(monkeypatch, genuine, kind, change):
    """A service answering every call alike: Lean's confirmation sees the same row, so each of these is the binder's."""
    row, _ = genuine(kind)
    mutant = copy.deepcopy(row)
    change(mutant)
    _answered(monkeypatch, mutant, call=None)
    with pytest.raises(CheckerUnavailable):
        CALLS[kind]()


@pytest.mark.parametrize("change", [
    lambda r: r["report"]["leaves"].append(r["report"]["leaves"][0]),
    lambda r: r["report"]["leaves"].pop(),
    lambda r: r["report"]["leaves"].reverse(),
    lambda r: r["report"]["leaves"].clear(),
    lambda r: r["report"]["leaves"][0].update(name="absent"),
    lambda r: r["report"]["leaves"][0].update(r["report"]["root"])],
    ids=["duplicated", "dropped", "reordered", "emptied", "no-node", "the-deduction"])
def test_a_report_s_rows_are_bound_with_and_without_a_matching_id(monkeypatch, genuine, change):
    """qt-a3d's gap: the schema has `uniqueStrings` only, so a duplicated leaf row is the relay's. The second mutant also
    carries the `report_id` it would need, so the row check answers for itself."""
    row, _ = genuine("document")
    mutant = copy.deepcopy(row)
    change(mutant)
    forged = cardinality.digest(f"ve-report-{cardinality.identities(ENV).identity_version}\n", {
        **{k: row[k] for k in ("environment_id", "w6_environment_id", "w6_target_environment_id")},
        "document": GRAPH["document"], "report": mutant["report"]})
    for answered in (mutant, {**mutant, "report_id": forged}):
        _answered(monkeypatch, answered)
        with pytest.raises(CheckerUnavailable):
            CALLS["document"]()


def test_object_key_order_is_no_part_of_an_answer(monkeypatch, genuine):
    row, answer = genuine("admission")
    _answered(monkeypatch, {**{key: row[key] for key in reversed(list(row))}, "regions": dict(reversed(row["regions"].items()))})
    assert cardinality._same(CALLS["admission"](), answer)


def test_a_search_s_verdict_is_lean_s_and_typed(monkeypatch, genuine):
    """A verdict of another type is no answer: `prove` reads Lean's replay of what it found (`rows` calls 0 and 1 admit)."""
    row, _ = genuine("certificate")
    _answered(monkeypatch, {**row, "valid": False}, call=2)
    assert cardinality.prove(*PROBLEM) is None
    _answered(monkeypatch, {**row, "valid": 1}, call=2)
    with pytest.raises(CheckerUnavailable):
        cardinality.prove(*PROBLEM)


@pytest.fixture
def part(tmp_path, monkeypatch):
    """A part document as sent, its path and Lean's genuine row, with `identities` looked up per mutant."""
    raw = text(GRAPH["document"]["nodes"])
    path = tmp_path / "part.ve.md"
    path.write_bytes(raw)
    row = _lean_answer(raw, True, tmp_path, {})
    known = cardinality.identities(ENV)
    monkeypatch.setattr(cardinality, "identities", lambda environment: known)
    return raw, path, row


def _shown(doc):
    return doc["source_id"], doc["document_id"], doc["units"], doc["cardinality"], doc["lean"]


def test_every_mutant_of_a_document_row_is_refused_or_changes_nothing(part):
    raw, path, row = part
    answer = _shown(_lean_document(raw, path, row, admitted=True))
    assert answer[3]["report"]["root"]["name"] == "root"
    accepted = []
    for name, mutant in _mutants(row):
        try:
            if _shown(_lean_document(raw, path, mutant, admitted=True)) != answer:
                accepted.append(name)
        except CheckerUnavailable:
            pass
    assert not accepted


def test_a_document_row_answers_the_case_it_asked(part):
    """The report is there exactly when `check` asked for it, and a unit's statement is the authored one."""
    raw, path, row = part
    with pytest.raises(CheckerUnavailable):
        _lean_document(raw, path, row, admitted=False)
    with pytest.raises(CheckerUnavailable):
        _lean_document(raw, path, {k: v for k, v in row.items() if k != "cardinality"}, admitted=True)
    other = copy.deepcopy(row)
    other["units"][0]["content"]["formula"] = ["quantity", ["top"]]
    with pytest.raises(CheckerUnavailable):
        _lean_document(raw, path, other, admitted=True)
