"""The `defaults-zone` kind through the Lean service (defeasible plan 2.7 and batch DF-5; spec 3.8, 4 and 8.6).

Lean computes the zone, DE10's form, `forced_all` and the rows after DE10 (`lean/VE/Defaults/ZoneWire.lean`); the relay
binds them to the request (`ve.defaults.bind_zone`) and renders them (`ve.defaults_english.zone`). Each fixture is spec
8.6's, end to end; every one-fault mutant of each genuine row is refused or shown unchanged.
"""
from __future__ import annotations

import copy
import json

import pytest

from tests.test_defaults_answer import _faults, _set, _transported
from tests.test_defaults_lean import DOCS, STRICT, env, rule, un
from ve import defaults, defaults_english
from ve.backends import relay
from ve.errors import CheckerUnavailable, UnsupportedProfile, VEError
from ve.softnorms import SoftEnvironment, SoftNormDocument


def _lam():
    """DF-λ: plain `instructs(operator)`, unspecified; g1, decided by the operator."""
    environment = env({"parties": ["operator"], **STRICT})
    environment["vocabulary"].update(sorts={"operator": {"description": "operator"}}, predicates={"instructs": {
        "arguments": ["operator"], "description": "instructs", "regulated": {"role": "plain", "default": "unspecified"}}})
    return environment, [rule("g1", "instructs", True, decider="operator")]


def _mu1():
    """DF-μ′: plain `p`, unspecified; r1 (+, guard `cond_a`) and r2 (−, guard `cond_b`)."""
    environment = env(base=["cond_a", "cond_b"])
    environment["vocabulary"]["predicates"] = {"p": {"arguments": ["assistant"], "description": "p", "regulated": {
        "role": "plain", "default": "unspecified"}}, **{c: {"arguments": ["assistant"], "description": c}
                                                       for c in ("cond_a", "cond_b")}}
    return environment, [{"norm": {**rule(name, "p", sign)["norm"], "guard": un(guard)}}
                         for name, sign, guard in (("r1", True, "cond_a"), ("r2", False, "cond_b"))]


def _pi():
    """DF-π: DF-α with `x_permitted` unspecified."""
    environment, norms = copy.deepcopy(DOCS["alpha"])
    environment["vocabulary"]["predicates"]["x_permitted"]["regulated"]["default"] = "unspecified"
    return environment, norms


def zcase(doc, outcome, at, sit=("a",), sort="assistant", on=None, obs=(), record=()):
    """A `defaults-zone` request: the situation (its decision tables empty), the record, the observations, the query."""
    environment, norms = doc
    relations = {**{n: [] for n in SoftNormDocument(SoftEnvironment(environment), norms).decisions}, **(on or {})}
    return {"id": "z", "kind": "defaults-zone", "environment": environment, "norms": norms,
            "model": {"complete": True, "domains": {sort: list(sit)}, "constants": {}, "relations": relations},
            "record": list(record), "observations": list(obs), "query": {"outcome": outcome, "tuple": list(at)}}


def x_labels(case):
    """X's labels: the layered `norm-defaults-elaborate` row's packs."""
    row = defaults.run({"id": "e", "kind": "norm-defaults-elaborate", "environment": case["environment"],
                        "norms": case["norms"]})
    return [label for label, _ in row["soft"] + row.get("rights", [])]


OBS_O1 = [{"outcome": "instructs", "tuple": ["o1"], "value": False}]
OFF = [{"decision": {"off": "r1", "party": "user"}, "tuple": ["a"], "value": True}]
OUTW = [{"decision": {"outweighs": "x_permitted", "lower": "helpfulness", "higher": "safety"}, "tuple": ["a"],
         "value": True}]
HEAD = "With no {} here that could be dropped, alone or together, "
# (fixture, request, Lean's zone fields without id and status, the English)
CASES = {
    "mu": (lambda: zcase(_lam(), "instructs", ["o2"], ("o1", "o2"), "operator", obs=OBS_O1),
           {"zone": "byDefault", "value": True, "form": "short", "forced_all": [{"rule": "g1", "tuple": ["o1"]}],
            "completions": [[{"row": "DE10f", "rule": "g1", "tuple": ["o1"]}]]},
           [HEAD.format("exceptions") + "o2 is instructs.", "The facts here force the exception to rule g1 for o1."]),
    "mu1": (lambda: zcase(_mu1(), "p", ["a"], on={"cond_a": [["a"]], "cond_b": [["a"]]}),
            {"zone": "leftTo", "form": "short", "forced_all": [], "completions": [
                [{"row": "DE13", "decision": {"excepted": "r2"}, "tuple": ["a"]}],
                [{"row": "DE13", "decision": {"excepted": "r1"}, "tuple": ["a"]}]]},
            [HEAD.format("exceptions") + "the answer depends on which rule gives way: the exception to rule r2 "
             "applies to a, or the exception to rule r1 applies to a."]),
    "mu2": (lambda: zcase(DOCS["gamma"], "x_permitted", ["a"]),
            {"zone": "leftTo", "form": "short", "forced_all": [], "completions": [
                [{"row": "DE13", "decision": {"excepted": "r2"}, "tuple": ["a"]}],
                [{"row": "DE13", "decision": {"excepted": "r1"}, "tuple": ["a"]}]]}, None),
    "delta_z": (lambda: zcase(DOCS["delta"], "x_required", ["a"]),
                {"zone": "byDefault", "value": True, "form": "long", "forced_all": [], "completions": [[]]},
                [HEAD.format("assumptions") + "a must do x."]),
    "xi": (lambda: zcase(DOCS["alpha"], "x_required", ["a"]),
           {"zone": "byDefault", "value": True, "form": "short", "forced_all": [], "completions": [[]]}, None),
    "pi1": (lambda: zcase(_pi(), "x_required", ["a"]),
            {"zone": "byDefault", "value": True, "form": "short", "forced_all": [], "completions": [[]]}, None),
    "xi1": (lambda: zcase(DOCS["beta"], "x_permitted", ["a"], on={"urgent": [["a"]]}),
            {"zone": "byDefault", "value": True, "form": "short", "forced_all": [{"rule": "r1", "tuple": ["a"]}],
             "completions": [[{"row": "DE11", "rule": "r1", "condition": 0, "tuple": ["a"]}]]},
            [None, "The text's own exception to rule r1 applies here: a is urgent."]),
    "epsilon_off": (lambda: zcase(DOCS["epsilon"], "x_permitted", ["a"], record=OFF),
                    {"zone": "byDefault", "value": True, "form": "short", "forced_all": [], "completions": [
                        [{"row": "DE13", "decision": {"off": "r1", "party": "user"}, "tuple": ["a"]}]]},
                    [None, "This assumes that the user has turned rule r1 off for a."]),
    "delta_outw": (lambda: zcase(DOCS["delta"], "x_required", ["a"], record=OUTW),
                   {"zone": "byDefault", "value": False, "form": "short", "forced_all": [], "completions": [[
                       {"row": "DE13", "decision": {"outweighs": "x_permitted", "lower": "helpfulness",
                                                    "higher": "safety"}, "tuple": ["a"]}]]},
                   [None, "This assumes that, on do x, the helpfulness consideration outweighs the safety "
                          "consideration."]),
    "mu1b": (lambda: zcase(_mu1(), "p", ["a"], on={"cond_a": [], "cond_b": []}), {"zone": "notSaid"}, []),
    "no_completion": (lambda: zcase(_lam(), "instructs", ["o2"], ("o1", "o2"), "operator", obs=OBS_O1, record=[
        {"decision": {"excepted": "g1"}, "tuple": ["o1"], "value": False}]),
                      {"zone": "noCompletion", "labels": ["observed"]}, []),
    "budget": (lambda: zcase(_lam(), "instructs", ["o0"], tuple(f"o{i}" for i in range(13)), "operator"),
               {"zone": "unknown", "reason": "budget: 26 open atoms, over 12"}, []),
}
_ROWS: dict = {}


def genuine(name):
    """The request and Lean's bound row, asked once per session (a copy each call)."""
    if name not in _ROWS:
        case = CASES[name][0]()
        _ROWS[name] = (case, defaults.answer(case, x_labels(case)))
    return copy.deepcopy(_ROWS[name])


@pytest.mark.parametrize("name", CASES)
def test_each_zone_is_lean_s_and_reads_as_spec_4_says(name):
    case, row = genuine(name)
    expected, english = CASES[name][1:]
    assert {k: v for k, v in row.items() if k not in ("id", "status")} == expected
    if english is not None:
        shown = defaults_english.sentences(case, row)
        assert [s for s, e in zip(shown, english) if e is not None] == [e for e in english if e is not None]
        assert len(shown) == len(english)
        assert not any(word in " ".join(shown) for word in ("soft__", "default:", "completion", "true decision"))


def test_de10f_only_from_forced_all_and_never_from_unknown_or_no_completion():
    for name in CASES:
        case, row = genuine(name)
        shown = " ".join(defaults_english.sentences(case, row))
        forced = {(e["rule"], tuple(e["tuple"])) for e in row.get("forced_all", [])}
        rows = [line for lines in row.get("completions", []) for line in lines if line["row"] == "DE10f"]
        assert all((line["rule"], tuple(line["tuple"])) in forced for line in rows)
        if row["zone"] in ("unknown", "noCompletion", "notSaid"):
            assert "forced_all" not in row and "The facts here force" not in shown and not shown


def test_weighing_documents_are_refused():
    environment, norms = DOCS["alpha"]
    environment = {**environment, "profiles": sorted([*environment["profiles"], "weighing@0"])}
    with pytest.raises(UnsupportedProfile, match="weighing@0"):
        defaults.answer(zcase((environment, norms), "x_required", ["a"]))


@pytest.mark.parametrize("name", ["mu", "mu1", "xi1", "epsilon_off", "delta_outw", "no_completion", "budget"])
def test_mutants_never_pass_as_answers(monkeypatch, name):
    case, row = genuine(name)
    labels, source = x_labels(case), defaults.soft_source(case)
    answered = {"row": row}
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **options: [_transported(answered["row"])])
    accepted = []
    for path, value in _faults(row):
        answered["row"] = mutant = _set(row, path, value)
        try:
            shown = defaults.answer(case, labels, source=source)
        except CheckerUnavailable:
            continue
        # R8: a retyped or rebound field is refused; Lean's own choices (`value`, `form`, `zone`, which default
        # completion `leftTo` shows first) are its theorems'
        if shown != row and path[0] not in ("value", "form", "zone") and path != ("completions",) or (
                path == ("completions",) and sorted(map(json.dumps, value)) != sorted(map(json.dumps, row[path[0]]))):
            accepted.append((path, value, json.dumps(mutant)[:200]))
    assert not accepted, accepted[:5]


TAMPERED = [
    ("forced exception", "mu", lambda r: r["forced_all"][0].update(rule="g9")),
    ("forced row", "mu", lambda r: r["completions"][0].clear()),
    ("record", "delta_outw", lambda r: r["completions"][0].clear()),
    ("reason", "budget", lambda r: r.update(reason="")),
    ("forced exceptions", "mu", lambda r: r["forced_all"].append(dict(r["forced_all"][0]))),
    ("exception", "xi1", lambda r: r["completions"][0][0].update(tuple=["b"])),
    ("stated condition", "xi1", lambda r: r["completions"][0][0].update(condition=1)),
    ("assumed decision", "epsilon_off", lambda r: r["completions"][0][0]["decision"].update(party="operator")),
    ("decision rows", "epsilon_off", lambda r: r["completions"][0].append(r["completions"][0][0])),
    ("assumed decision", "mu", lambda r: r["completions"][0][0].update(row="DE13", decision={"excepted": "g1"})),
    ("completions", "mu1", lambda r: r["completions"].append(r["completions"][0])),
    ("labels", "no_completion", lambda r: r.update(labels=["soft:exception:g9"])),
]


@pytest.mark.parametrize("what, name, tamper", TAMPERED, ids=[f"{t[0]}-{t[1]}" for t in TAMPERED])
def test_each_binding_refuses_its_tampered_field_and_keeps_the_genuine_row(what, name, tamper):
    case, row = genuine(name)
    labels, source = x_labels(case), defaults.soft_source(case)
    assert defaults.bind_zone(case, copy.deepcopy(row), source, labels) == row
    tamper(row)
    with pytest.raises(CheckerUnavailable, match=rf"\({what}\)"):
        defaults.bind_zone(case, row, source, labels)


REQUEST_PATHS = [("model",), ("record",), ("observations",), ("query",), ("query", "outcome"), ("query", "tuple"),
                 ("record", 0), ("record", 0, "decision"), ("record", 0, "tuple"), ("record", 0, "value"),
                 ("observations", 0, "outcome"), ("observations", 0, "value")]


@pytest.mark.parametrize("path", REQUEST_PATHS, ids=["/".join(map(str, p)) for p in REQUEST_PATHS])
def test_each_request_member_retyped_or_dropped_is_refused_by_lean(path):
    case = zcase(DOCS["epsilon"], "x_permitted", ["a"], record=OFF,
                 obs=[{"outcome": "x_permitted", "tuple": ["a"], "value": True}])
    for value in (7, True, None, [], {}, "x", _set):
        mutant = _set(case, path, value)
        if mutant == case or path in (("record",), ("observations",)) and value == [] or type(path[-1]) is int and value is _set:
            continue  # the request itself, an empty list of facts, a list with one element fewer: all well formed
        with pytest.raises(VEError):
            defaults.answer(mutant)
