"""The relay never accepts a Lean cardinality answer that is not an answer to its request (quantities QT-A4, R8). Genuine
answers of each case kind are mutated one and two faults at a time (every member dropped, emptied, retyped, duplicated,
reordered, an index out of range): every mutant is `CheckerUnavailable` or changes nothing the relay returns."""
from __future__ import annotations

import copy
import json
import random

import pytest

from tests.lean_build import lean_build
from tests.subprocesses import HANG_TIMEOUT
from tests.test_cardinality_lean import CASES, ENV, FA1, GRAPH, text
from ve import cardinality
from ve.backends import relay
from ve.backends.lean_service import LeanService, case_digest, case_texts
from ve.backends.service_schema import Invalid, check_response
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
    """Every member of a JSON value to `depth`, with its path, and of a list its first and last rows: a deeper node of a
    formula, or a middle row, is one more node of its kind."""
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
    """Each member dropped, retyped and emptied; each list's rows duplicated, reordered and dropped; each string shifted."""
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


def _answered(monkeypatch, row, *, call=0):
    """The Lean service answers `row` to the `call`th `rows` of the relay; every other runs."""
    seen = []

    def rows(mode, cases, **options):
        seen.append(mode)
        return [copy.deepcopy(row)] if len(seen) - 1 == call else REAL_ROWS(mode, cases, **options)
    monkeypatch.setattr(relay, "rows", rows)


@pytest.fixture(scope="module")
def ids():
    """Python's identities of the request: a function of the request alone, so one per environment serves every mutant."""
    return {key: cardinality.identities(value) for key, value in (
        ("fa1", FA1["environment"]), ("cm", CM["environment"]), ("graph", ENV))}


@pytest.fixture
def genuine(monkeypatch, ids):
    """A case kind's genuine row and its answer; `identities` looked up, not recomputed per mutant."""
    table = {FA1["environment"]["profiles"].__repr__(): ids["fa1"], ENV["profiles"].__repr__(): ids["graph"]}
    monkeypatch.setattr(cardinality, "identities", lambda environment: table[environment["profiles"].__repr__()])
    seen = []

    def recording(mode, cases, **options):
        seen.append(REAL_ROWS(mode, cases, **options))
        return seen[-1]

    def of(kind):
        with monkeypatch.context() as patch:
            patch.setattr(relay, "rows", recording)
            answer = CALLS[kind]()
        return seen[-1 if kind != "admission" else -2][0], answer
    return of


def _lean_s(name):
    """What R8 leaves to Lean, typed by the schema and not bound: another wording of a line, a countermodel's verdict and
    the sizes it reports, each the same type; the schema refuses each retype before the relay reads it."""
    return name.startswith(("('paraphrase',)", "('assumptions',", "('refutes',)")) or (
        name.startswith("('sizes',") and "'size'" in name and ("out of range" in name or ":= 7" in name or ":= 999" in name))


def _verdict(call, answer):
    try:
        return "same" if call() == answer else "changed"
    except CheckerUnavailable:
        return "unavailable"


@pytest.mark.parametrize("kind", list(CALLS))
def test_every_one_fault_mutant_is_refused_or_changes_nothing(monkeypatch, genuine, kind):
    row, answer = genuine(kind)
    assert _verdict(CALLS[kind], answer) == "same"
    accepted = []
    for name, mutant in _mutants(row):
        _answered(monkeypatch, mutant)
        if _verdict(CALLS[kind], answer) == "changed" and not _lean_s(name):
            accepted.append(name)
    assert not accepted


@pytest.mark.parametrize("kind", list(CALLS))
def test_two_faults_at_a_time_are_refused_or_change_nothing(monkeypatch, genuine, kind):
    row, answer = genuine(kind)
    rng, pool, accepted = random.Random(f"qt-a4 {kind}"), list(_mutants(row)), []
    for name, first in rng.sample(pool, min(120, len(pool))):
        nodes = list(_nodes(first))
        if nodes:
            fault, path = rng.choice(RETYPED + (_replaced,)), rng.choice(nodes)[0]
            other = f"{path} := {fault!r}"
            _answered(monkeypatch, _replaced(first, path, fault))
            if _verdict(CALLS[kind], answer) == "changed" and not (_lean_s(name) or _lean_s(other)):
                accepted.append((name, other))
    assert not accepted


@pytest.mark.parametrize("name, change", [
    ("a region renamed", lambda r: r["regions"]["constants"][0].update(constant="cardinality__fomc_policymaker__absent")),
    ("a region's bits shifted", lambda r: r["regions"]["constants"][0].update(bits="1")),
    ("a region of another sort", lambda r: r["regions"]["constants"][0].update(sort="user")),
    ("a region row duplicated", lambda r: r["regions"]["constants"].append(r["regions"]["constants"][0])),
    ("a region row dropped", lambda r: r["regions"]["constants"].pop()),
    ("a region table reordered", lambda r: r["regions"]["constants"].reverse()),
    ("a predicate undeclared", lambda r: r["regions"]["predicates"]["fomc_policymaker"].__setitem__(0, "absent")),
    ("a predicate on another sort", lambda r: r["regions"]["predicates"]["fomc_policymaker"].__setitem__(0, "curious")),
    ("a counted sort undeclared", lambda r: r["regions"]["predicates"].update(absent=[])),
    ("a bridge dropped", lambda r: r["erased"]["premises"].pop(4)),
    ("a bridge duplicated", lambda r: r["erased"]["premises"].insert(4, r["erased"]["premises"][4]))])
def test_the_region_table_and_problem_are_bound(monkeypatch, genuine, name, change):
    row, _ = genuine("admission")
    mutant = copy.deepcopy(row)
    change(mutant)
    _answered(monkeypatch, mutant)
    with pytest.raises(CheckerUnavailable):
        CALLS["admission"]()


@pytest.mark.parametrize("name, change", [
    ("a leaf duplicated", lambda r: r["report"]["leaves"].append(r["report"]["leaves"][0])),
    ("a leaf dropped", lambda r: r["report"]["leaves"].pop()),
    ("the leaves reordered", lambda r: r["report"]["leaves"].reverse()),
    ("the leaves emptied", lambda r: r["report"]["leaves"].clear()),
    ("a leaf that is no node", lambda r: r["report"]["leaves"][0].update(name="absent")),
    ("the deduction as a leaf", lambda r: r["report"]["leaves"][0].update(r["report"]["root"]))])
def test_a_report_s_rows_are_bound_and_its_id_recomputed(monkeypatch, genuine, name, change):
    """qt-a3d's gap: the schema types `report_id` and has `uniqueStrings` only, so a duplicated leaf row is the relay's.
    Each mutant also carries the `report_id` it would need, so the row checks answer for themselves."""
    row, answer = genuine("document")
    mutant = copy.deepcopy(row)
    change(mutant)
    _answered(monkeypatch, mutant)
    with pytest.raises(CheckerUnavailable):
        CALLS["document"]()
    forged = cardinality.digest(f"ve-report-{cardinality.identities(ENV).identity_version}\n", {
        "environment_id": row["environment_id"], "w6_environment_id": row["w6_environment_id"],
        "w6_target_environment_id": row["w6_target_environment_id"], "document": GRAPH["document"],
        "report": mutant["report"]})
    _answered(monkeypatch, {**mutant, "report_id": forged})
    with pytest.raises(CheckerUnavailable):
        CALLS["document"]()


def test_object_key_order_is_no_part_of_an_answer(monkeypatch, genuine):
    row, answer = genuine("admission")
    reversed_row = {key: row[key] for key in reversed(list(row))}
    reversed_row["regions"] = {key: row["regions"][key] for key in reversed(list(row["regions"]))}
    _answered(monkeypatch, reversed_row)
    assert cardinality._same(CALLS["admission"](), answer)


def test_a_certificate_verdict_is_typed_and_a_search_is_lean_s(monkeypatch, genuine):
    """`prove` reads Lean's verdict on what it found: a refusal is no certificate, and a verdict of another type no answer."""
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
    return (doc["source_id"], doc["document_id"], doc["units"], doc["cardinality"], doc["lean"])


def test_every_mutant_of_a_document_row_is_refused_or_changes_nothing(part):
    raw, path, row = part
    answer = _shown(_lean_document(raw, path, row, admitted=True))
    assert answer[3]["report"]["root"]["name"] == "root"
    accepted = []
    for name, mutant in _mutants({k: v for k, v in row.items() if k not in ("source",)}):
        try:
            if _shown(_lean_document(raw, path, {"source": row["source"], **mutant}, admitted=True)) != answer:
                accepted.append(name)
        except CheckerUnavailable:
            pass
    # A unit's status and the coverage's counts are Lean's; the receiver checks them against each other and the request.
    assert not [name for name in accepted if "status" not in name]


def test_a_document_row_answers_the_case_it_asked(part):
    """The report is there exactly when `check` asked for it, and its statement is the unit's."""
    raw, path, row = part
    with pytest.raises(CheckerUnavailable):
        _lean_document(raw, path, row, admitted=False)
    with pytest.raises(CheckerUnavailable):
        _lean_document(raw, path, {k: v for k, v in row.items() if k != "cardinality"}, admitted=True)
    unit = copy.deepcopy(row)
    unit["units"][0]["content"]["formula"] = ["quantity", ["top"]]
    with pytest.raises(CheckerUnavailable):
        _lean_document(raw, path, unit, admitted=True)


def test_the_document_schema_types_the_report(part):
    """`document.json`: each member of the report and of a statement unit is typed, before the relay reads it."""
    raw = part[0].decode("utf-8")
    cases = [{"id": "document", "document": raw, "admit": True}]
    body = json.dumps(cases, ensure_ascii=False)
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as service:
        _, response = service.exchange("document", body, 1, timeout=HANG_TIMEOUT)
    request = {"id": response["id"], "mode": "document", "cases": cases,
               "digests": [case_digest(t) for t in case_texts(body)], "bytes": len(body.encode())}
    check_response("document", response, request)
    row = response["results"][0]["result"]
    for path, value in _nodes({"cardinality": row["cardinality"], "units": row["units"][:1]}):
        if path[0] == "units" and path[:3] != ("units", 0, "content"):
            continue
        for other in (_replaced, 7, True, None, {}, 1.5, [[[]]]):
            if other is _replaced and (path[-1] in ("content", "cardinality") or type(path[-1]) is int):
                continue  # optional members and a list's rows: which of them a request has is the relay's (above)
            mutated = copy.deepcopy(response)
            mutated["results"][0]["result"] = _replaced(row, path, other)
            with pytest.raises(Invalid):
                check_response("document", mutated, request)
