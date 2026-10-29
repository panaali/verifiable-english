"""Readings unless an exception applies (docs/spec/defeasible-PLAN.md 2.4 and batch DF-3; spec docs/spec/defeasible.md
3.9, 7.4 and 8.3): the `default` member of `readings-verdicts` under the soft completion, through the service and
`ve document readings --assume-no-exception`.

Lean decides every row, fold, basis, assumption, collision and English row (`lean/VE/Readings/DefaultVerdicts.lean`);
Python generates each choice's evidence (`_FilledChoiceDocument.default_case`), binds the member to the request
(`_check_default`) and renders Lean's rows (`ve.defaults_english.readings`). Fixtures: DF-ν (spec 8.3, ALL with the
default reading's assumption), DF-ρ (CONFLICT from the gate only, DE7), DF-τ (a strict conflict: no member) and a
document without a default rule (no member, plan F-DF2); F-DF2's corpus is `Readings/DefaultVerdictsExamples.lean`.
"""
from __future__ import annotations

import copy
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from tests import lean_routes
from tests.subprocesses import HANG_TIMEOUT
from tests.test_document import unit, write_doc
from tests.test_readings_s1_document import SHALL, candidate
from tests.test_readings_s1_lean import SOFT_PROFILES, env_k, norm
from ve.errors import CheckerUnavailable, VEError

QUERY = ["forall", "agent", ["forall", "user", ["binary", "avoid_required", ["var", 1], ["var", 0]]]]

LABEL = "default:exception:no-deception"
DE8 = "Under every reading, the conclusion follows under the assumptions listed for that reading."
DE2U = ("This assumes that the exception to rule no-deception does not apply. The text names no case where it applies, "
        "and no one who decides.")
DE7 = ("Rules no-deception and permit-deception conflict here unless one of them gives way: e0 must avoid deceiving e0, "
       "and e0 need not avoid deceiving e0. The text ranks neither above the other, and names no exception that "
       "applies here.")
DE7AU = "The text names no one who decides which rule gives way."


def test_df3_approved_statements_match_the_built_lean_declarations():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "docs/defeasible/df-1ac/evidence/compare_statements.py"),
         "lean/VE/Readings/DefaultVerdicts.lean", "7.4"],
        cwd=root, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert result.returncode == 0, result.stderr
    assert result.stdout.endswith("17 OK, 0 not OK\n"), result.stdout


@pytest.fixture(scope="module", autouse=True)
def service():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def soft_document(tmp_path, sets, fixed=()):
    """A document under the soft completion (K's environment, `avoid_required` unspecified): one open set per
    `(set id, sentence, [(reading id, content)])`, then fixed norm units `(unit id, sentence, content)`; every pair's
    situation is the generator's, on Lean's filled frame (`readings-elaborate`)."""
    from ve.readings_route import document_wire, run_lean
    from ve.readings_s1 import record_situations, search
    from ve.softnorms import SoftEnvironment
    raw = env_k(profiles=("norm-defaults@0", *SOFT_PROFILES))
    raw["vocabulary"]["predicates"]["avoid_required"]["regulated"]["default"] = "unspecified"
    env = SoftEnvironment(raw)
    text, units, reading_sets = b"", [], []
    for n, (set_id, sentence, readings) in enumerate(sets, 1):
        line = sentence + b"\n"
        units.append(unit(f"u{n}", len(text), len(text) + len(line), "norm", "specified"))
        text += line
        rs = [candidate(env, set_id, cid, content) for cid, content in readings]
        for r in rs:
            r["admission"]["distinguishing_models"] = {o["id"]: "pending" for o in rs if o["id"] != r["id"]}
        reading_sets.append({"id": set_id, "unit": f"u{n}", "version": 1, "status": "open", "readings": rs})
    for uid, sentence, content in fixed:
        line = sentence + b"\n"
        units.append(unit(uid, len(text), len(text) + len(line), "norm", "specified", content))
        text += line
    pending = document_wire([{"id": u["id"], "kind": u["kind"], "content": u["content"]} for u in units], reading_sets)
    [filled] = run_lean([{"id": "e", "kind": "readings-elaborate", "environment": raw, "document": pending}])
    assert filled["status"] == "ok", filled
    recorded = []
    for R in reading_sets:
        found = search(raw, pending, R["id"], filled=filled)
        recorded.append(record_situations(R, {k: v for k, v in found.items() if v is not None}))
    return write_doc(tmp_path, text, units, environment_json=raw, reading_sets=recorded)


K1 = ("rs1", SHALL, [("strict", norm("no-deception", "avoid_required", True)),
                     ("default", norm("no-deception", "avoid_required", True, "default"))])
RS2 = ("rs2", b"Agents may deceive users.", [("help", norm("help", "help_required", True)),
                                              ("permit", norm("permit-deception", "avoid_required", False, "default"))])


def route_of(path):
    from ve.document import load_document
    from ve.readings_verdicts import context
    return context(load_document(path))


def cli(path, tmp_path, *extra):
    from ve.document import main
    conclusion = tmp_path / "conclusion.json"
    conclusion.write_text(json.dumps(QUERY))
    out = io.StringIO()
    with redirect_stdout(out):
        assert main(["readings", str(path), "--conclusion", str(conclusion), *extra]) == 0
    return json.loads(out.getvalue())


@pytest.fixture(scope="module")
def nu(tmp_path_factory):
    """DF-ν: K1 under the soft completion (RD-9's F-SD1), the route and its answer with the member."""
    tmp = tmp_path_factory.mktemp("nu")
    path = soft_document(tmp, [K1])
    route = route_of(path)
    return path, route, route.default_answer(QUERY)


@pytest.fixture(scope="module")
def rho(tmp_path_factory):
    """DF-ρ: K1 and a second set whose default reading collides with K1's, unranked, without a strict conflict."""
    tmp = tmp_path_factory.mktemp("rho")
    path = soft_document(tmp, [K1, RS2])
    route = route_of(path)
    return path, route, route.default_answer(QUERY)


def rows(member):
    return [(e["choice"], e["conflict"], e["query"], e.get("basis"), e.get("assumptions")) for e in member["per_choice"]]


# -- DF-ν: the default fold ALL beside RD-9's SOME (spec 8.3)

def test_df_nu_default_fold_all_with_the_default_readings_assumption(nu):
    _, _, row = nu
    assert row["result"]["verdict"] == "SOME", row["result"]
    assert [e["conflict"] for e in row["per_choice"]] == ["CONFLICT-FREE", "CONFLICT-FREE"]
    member = row["default"]
    assert (member["conflict"], member["verdict"]) == ("CONFLICT-FREE", "ALL")
    assert rows(member) == [([["rs1", 0]], "CONFLICT-FREE", "proved", "strict", []),
                            ([["rs1", 1]], "CONFLICT-FREE", "proved", "needs", [LABEL])]
    assert member["english"] == [{"row": "DE8"}, {"row": "assumptions", "choice": [["rs1", 1]]}]


def test_default_query_respects_readings_budget_after_cached_free_gate(tmp_path, monkeypatch):
    """An exhausted query cannot reuse the standalone defaults search's larger limits."""
    from ve.readings_verdicts import BUDGET

    route = route_of(soft_document(tmp_path, [K1]))
    assert route.conflict_answer()["result"]["status"] == "CONFLICT-FREE"
    for key in BUDGET:
        monkeypatch.setitem(BUDGET, key, 0)
    answer = route.default_answer(QUERY)
    assert answer["result"]["verdict"] == "UNKNOWN"
    assert answer["default"]["verdict"] == "UNKNOWN"
    assert {entry["query"] for entry in answer["default"]["per_choice"]} == {"UNKNOWN"}


def test_default_query_with_adequate_budget_is_all(nu):
    """The same query retains its checked positive answer with the ordinary budget."""
    _, route, _ = nu
    assert route.default_answer(QUERY)["default"]["verdict"] == "ALL"


def test_df_nu_english_is_de8_then_the_default_readings_de2(nu, tmp_path):
    path, _, _ = nu
    data = cli(path, tmp_path, "--assume-no-exception")
    assert data["verdict"] == "SOME" and data["default"]["verdict"] == "ALL"
    assert data["default_english"] == [DE8, f"Under sentence 1 read as *should*: {DE2U}"]
    assert "english" not in data["default"]
    # the strict answer is RD-9's, unchanged by the flag
    assert data["english"] == cli(path, tmp_path)["english"]


def test_without_the_request_asking_there_is_no_member(nu):
    """`assume_no_exception` false or absent: RD-9's answer exactly (F-DF2's strict fold, byte for byte)."""
    _, route, row = nu
    case = copy.deepcopy(route.requests[id(row)])
    from ve.readings_route import run_lean
    answers = []
    for value in (None, False):
        asked = {k: v for k, v in case.items() if k != "assume_no_exception"}
        if value is not None:
            asked["assume_no_exception"] = value
        [answer] = run_lean([asked])
        answers.append(answer)
    assert answers[0] == answers[1] and "default" not in answers[0]
    assert {k: v for k, v in row.items() if k != "default"} == answers[0]


# -- DF-ρ: a default-fold CONFLICT comes from the gate only (DE7 per choice)

def test_df_rho_default_conflict_from_the_gate_only(rho):
    _, _, row = rho
    assert row["result"]["verdict"] == "SOME"
    assert all(e["conflict"] == "CONFLICT-FREE" for e in row["per_choice"]) and len(row["per_choice"]) == 4
    member = row["default"]
    assert (member["conflict"], member["verdict"]) == ("CONFLICT", "UNKNOWN")
    gate = [e for e in member["per_choice"] if e["conflict"] != "CONFLICT-FREE"]
    assert [e["choice"] for e in gate] == [[["rs1", 1], ["rs2", 1]]] and gate[0]["conflict"] == "CONFLICT"
    assert gate[0]["collision"]["rules"] == ["no-deception", "permit-deception"]
    assert gate[0]["collision"]["deciders"] == ["unstated"]
    assert member["english"] == [{"row": "DE7", "choice": [["rs1", 1], ["rs2", 1]]}]


def test_df_rho_english_is_de7_under_the_colliding_reading_never_a_contradiction(rho, tmp_path):
    path, _, _ = rho
    data = cli(path, tmp_path, "--assume-no-exception")
    assert data["default_english"] == [
        f"Under sentence 1 read as *should* and sentence 2 read as *Every agent generally need not avoid deceiving each "
        f"user*: {DE7}", DE7AU]
    assert not any("CONFLICT" in line or "contradict" in line for line in data["english"] + data["default_english"])


# -- the member is present exactly when asked, the strict fold is FREE and some choice has a default premise

def test_df_tau_a_strict_conflict_leaves_no_member(tmp_path):
    """DF-τ: K1 and the fixed strict rule "allow-deception" on −avoid_required: RD-9's answer stands alone."""
    allow = norm("allow-deception", "avoid_required", False)
    route = route_of(soft_document(tmp_path, [K1], fixed=[("u9", b"Agents may deceive users.", allow)]))
    row = route.default_answer(QUERY)
    assert any(e["conflict"] != "CONFLICT-FREE" for e in row["per_choice"]), row["per_choice"]
    assert "default" not in row


def test_without_a_default_premise_there_is_no_member(tmp_path):
    """Both sides of F-DF2's condition: a FREE strict fold without any no-exception premise shows no member."""
    plain = ("rs1", SHALL, [("strict", norm("no-deception", "avoid_required", True)),
                            ("help", norm("help", "help_required", True))])
    route = route_of(soft_document(tmp_path, [plain]))
    row = route.default_answer(QUERY)
    assert all(e["conflict"] == "CONFLICT-FREE" for e in row["per_choice"]), row["per_choice"]
    assert "default" not in row


def test_the_flag_elsewhere_is_rd9s_answer(nu):
    """Only `assume_no_exception: true` on the query question asks: another question or value is RD-9's answer."""
    from ve.readings_route import run_lean
    _, route, row = nu
    case = {k: v for k, v in route.requests[id(row)].items() if k != "assume_no_exception"}
    for question in ("conflict", "premises", "query"):
        [plain] = run_lean([{**case, "question": question}])
        values = ("yes", 1, None) + ((True,) if question != "query" else ())
        for value in values:
            [asked] = run_lean([{**case, "question": question, "assume_no_exception": value}])
            assert asked == plain and "default" not in asked, (question, value)


def test_under_names_readings_and_other_flags_are_refused(nu, tmp_path):
    path, _, _ = nu
    data = cli(path, tmp_path, "--assume-no-exception", "--under", "rs1:1")
    assert data["verdict"] == "NONE" and data["default"]["verdict"] == "ALL"
    assert [e["choice"] for e in data["default"]["per_choice"]] == [[["rs1", 1]]]
    with pytest.raises(VEError, match="--sentence"):
        cli(path, tmp_path, "--assume-no-exception", "--sentence", "u1")


# -- the binding (R8): every field of the member retyped or rebound is refused

def _bound(route, row, mutate):
    from ve.readings_verdicts.binding import _check_answer
    case, forged = copy.deepcopy(route.requests[id(row)]), copy.deepcopy(row)
    mutate(forged, case)
    _check_answer(forged, case, route.frame(case))


def _set(path, value):
    def mutate(row, case):
        target = row
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return mutate


def _drop(path):
    def mutate(row, case):
        target = row
        for key in path[:-1]:
            target = target[key]
        del target[path[-1]]
    return mutate


NU_FORGERIES = {
    "member absent": _drop(["default"]),
    "conflict retyped": _set(["default", "conflict"], 1),
    "verdict retyped": _set(["default", "verdict"], "all"),
    "per_choice not a list": _set(["default", "per_choice"], {}),
    "a row dropped": lambda row, case: row["default"]["per_choice"].pop(),
    "a row repeated": lambda row, case: row["default"]["per_choice"].append(row["default"]["per_choice"][0]),
    "rows reordered": lambda row, case: row["default"]["per_choice"].reverse(),
    "a choice the request has not": _set(["default", "per_choice", 1, "choice"], [["rs1", 2]]),
    "a choice of another set": _set(["default", "per_choice", 1, "choice"], [["rs9", 1]]),
    "query retyped": _set(["default", "per_choice", 1, "query"], True),
    "basis retyped": _set(["default", "per_choice", 1, "basis"], "default"),
    "basis without proved": _set(["default", "per_choice", 1, "query"], "refuted"),
    "a label the choice has not": _set(["default", "per_choice", 1, "assumptions"], ["default:exception:help"]),
    "a label of another choice's kind": _set(["default", "per_choice", 1, "assumptions"], ["default:switch:x:y"]),
    "a label twice": _set(["default", "per_choice", 1, "assumptions"], [LABEL, LABEL]),
    "assumptions retyped": _set(["default", "per_choice", 1, "assumptions"], LABEL),
    "a label on the strict reading": _set(["default", "per_choice", 0, "assumptions"], [LABEL]),
    "strict with assumptions": _set(["default", "per_choice", 1, "basis"], "strict"),
    "needs without the strict countermodel": lambda row, case: case["evidence"][1].pop("countermodel"),
    "an English row of no member choice": _set(["default", "english", 1, "choice"], [["rs1", 2]]),
    "assumptions shown for a strict reading": _set(["default", "english", 1, "choice"], [["rs1", 0]]),
    "DE12 for a needs reading": _set(["default", "english", 1, "row"], "DE12"),
    "DE7 without a collision": _set(["default", "english", 1, "row"], "DE7"),
    "an English row retyped": _set(["default", "english", 0], "DE8"),
    "a member not asked for": lambda row, case: case.pop("assume_no_exception"),
}


@pytest.mark.parametrize("name", sorted(NU_FORGERIES))
def test_df_nu_every_forged_field_is_refused(nu, name):
    _, route, row = nu
    with pytest.raises(CheckerUnavailable):
        _bound(route, row, NU_FORGERIES[name])


def test_df_nu_the_genuine_answer_binds(nu, rho):
    for _, route, row in (nu, rho):
        _bound(route, row, lambda row, case: None)


def _gate(row):
    return next(i for i, e in enumerate(row["default"]["per_choice"]) if "collision" in e)


RHO_FORGERIES = {
    "collision rules not a colliding pair": lambda row, case, i: row["default"]["per_choice"][i]["collision"].update(
        rules=["no-deception", "help"]),
    "collision rules swapped": lambda row, case, i: row["default"]["per_choice"][i]["collision"].update(
        rules=["permit-deception", "no-deception"]),
    "collision tuple outside the model": lambda row, case, i: row["default"]["per_choice"][i]["collision"].update(
        tuple=["e9", "e0"]),
    "collision tuple of the wrong arity": lambda row, case, i: row["default"]["per_choice"][i]["collision"].update(
        tuple=["e0"]),
    "deciders not the rules'": lambda row, case, i: row["default"]["per_choice"][i]["collision"].update(
        deciders=["assistant"]),
    "situation outside the model": lambda row, case, i: row["default"]["per_choice"][i]["situation"].update(
        filling={"unsaid__avoid_required": [["e7", "e0"]]}),
    "situation undeclared filling table": lambda row, case, i: row["default"]["per_choice"][i]["situation"].update(
        filling={"absent": [["e0"]]}),
    "situation wrong filling arity": lambda row, case, i: row["default"]["per_choice"][i]["situation"].update(
        filling={"unsaid__avoid_required": [["e0"]]}),
    "situation missing empty filling table": lambda row, case, i: row["default"]["per_choice"][i]["situation"].update(
        filling={}),
    "collision on a FREE row": lambda row, case, i: row["default"]["per_choice"][i].update(conflict="CONFLICT-FREE"),
    "collision without its situation": lambda row, case, i: row["default"]["per_choice"][i].pop("situation"),
    "collision the request did not send": lambda row, case, i: next(
        e for e in case["evidence"] if e["choice"] == row["default"]["per_choice"][i]["choice"])["default"].pop(
        "collision"),
    "DE7 on a choice without a collision": lambda row, case, i: row["default"]["english"][0].update(
        choice=row["default"]["per_choice"][0]["choice"]),
    "member beside a strict conflict": lambda row, case, i: row["per_choice"][0].update(conflict="UNKNOWN"),
}


@pytest.mark.parametrize("name", sorted(RHO_FORGERIES))
def test_df_rho_every_forged_collision_field_is_refused(rho, name):
    _, route, row = rho
    i = _gate(row)
    with pytest.raises(CheckerUnavailable):
        _bound(route, row, lambda row, case: RHO_FORGERIES[name](row, case, i))
