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
    return [item["label"] for item in row["soft"] + row.get("rights", [])]


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
    "zeta": (lambda: zcase(DOCS["zeta"], "x_permitted", ["a"]),
             {"zone": "byDefault", "value": True, "form": "short", "forced_all": [], "completions": [[]]}, None),
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
    # the binding's other sides: two rows in order, a record entry set false, a premise's own label
    "closed_two": (lambda: zcase(_closed(), "x_required", ["b"], ("a", "b"), obs=[
        {"outcome": "x_required", "tuple": [e], "value": False} for e in ("a", "b")]),
                   {"zone": "byDefault", "value": False, "form": "short", "forced_all": [
                       {"rule": "r1", "tuple": ["a"]}, {"rule": "r1", "tuple": ["b"]}], "completions": [[
                           {"row": "DE10f", "rule": "r1", "tuple": ["a"]}, {"row": "DE10f", "rule": "r1", "tuple": ["b"]}]]},
                   None),
    "epsilon_two": (lambda: zcase(DOCS["epsilon"], "x_permitted", ["a"], record=[
        {"decision": {"excepted": "r1"}, "tuple": ["a"], "value": False}, *OFF]), {
        "zone": "byDefault", "value": True, "form": "short", "forced_all": [], "completions": [
            [{"row": "DE13", "decision": {"off": "r1", "party": "user"}, "tuple": ["a"]}]]}, None),
    "beta_none": (lambda: zcase(DOCS["beta"], "x_required", ["a"], on={"urgent": [["a"]]}, record=[
        {"decision": {"excepted": "r1"}, "tuple": ["a"], "value": False}]),
                  {"zone": "noCompletion", "labels": ["soft:exception:r1:sufficient:0"]}, []),
    # review F2: the query observed both ways: no completion, which an observed query allows
    "observed_twice": (lambda: zcase(_lam(), "instructs", ["o2"], ("o1", "o2"), "operator", obs=[
        {"outcome": "instructs", "tuple": ["o2"], "value": value} for value in (True, False)]),
                       {"zone": "noCompletion", "labels": ["observed"]}, []),
}


def _closed():
    """DF-α with `x_required` closed (`deny`)."""
    environment, norms = copy.deepcopy(DOCS["alpha"])
    environment["vocabulary"]["predicates"]["x_required"]["regulated"]["default"] = "deny"
    return environment, norms
_ROWS: dict = {}


def genuine(name):
    """The request, Lean's bound row, X's labels and the source's decisions, asked once per session (a copy each
    call), so a seeded bug of the binding (tests/test_defaults_checks.py) runs the binding alone."""
    if name not in _ROWS:
        case = CASES[name][0]()
        labels, source = x_labels(case), defaults.zone_source(case)
        _ROWS[name] = (case, defaults.answer(case, labels, source=source), labels, source)
    return copy.deepcopy(_ROWS[name])


@pytest.mark.parametrize("name", CASES)
def test_each_zone_is_lean_s_and_reads_as_spec_4_says(name):
    case, row, *_ = genuine(name)
    expected, english = CASES[name][1:]
    assert expected is None or {k: v for k, v in row.items() if k not in ("id", "status")} == expected
    if english is not None:
        shown = defaults_english.sentences(case, row)
        assert [s for s, e in zip(shown, english) if e is not None] == [e for e in english if e is not None]
        assert len(shown) == len(english)
        assert not any(word in " ".join(shown) for word in ("soft__", "default:", "completion", "true decision"))


def test_de10f_only_from_forced_all_and_never_from_unknown_or_no_completion():
    for name in CASES:
        case, row, *_ = genuine(name)
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
    case, row, labels, source = genuine(name)
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
    ("forced exception", "mu", lambda r: r["forced_all"][0].update(tuple=["o9"])),
    ("forced exception", "zeta", lambda r: r["forced_all"].append({"rule": "r0", "tuple": ["a"]})),
    ("forced row", "mu", lambda r: r["completions"][0].clear()),
    ("record", "delta_outw", lambda r: r["completions"][0].clear()),
    ("reason", "budget", lambda r: r.update(reason="")),
    ("forced exceptions", "mu", lambda r: r["forced_all"].append(dict(r["forced_all"][0]))),
    ("exception", "xi1", lambda r: r["completions"][0][0].update(tuple=["b"])),
    ("stated condition", "xi1", lambda r: r["completions"][0][0].update(condition=1)),
    ("assumed decision", "epsilon_off", lambda r: r["completions"][0][0]["decision"].update(party="operator")),
    ("assumed decision", "epsilon_off", lambda r: r["completions"][0][0].update(tuple=["b"])),
    ("assumed decision", "epsilon_off", lambda r: r["completions"][0][0].update(tuple="a")),
    ("assumed decision", "epsilon_off", lambda r: r["completions"][0][0].update(tuple=["a", "a"])),
    ("assumed decision", "mu", lambda r: r["completions"][0][0].update(row="DE13", decision={"excepted": "g1"})),
    ("decision rows", "epsilon_off", lambda r: r["completions"][0].append(r["completions"][0][0])),
    ("decision rows", "closed_two", lambda r: r["completions"][0].reverse()),
    ("completions", "mu1", lambda r: r["completions"].append(r["completions"][0])),
    ("completions", "mu1", lambda r: r["completions"].__setitem__(1, r["completions"][0])),
    ("completions", "mu1", lambda r: r["completions"][0].clear()),
    ("completions", "xi", lambda r: r["completions"].clear()),
    ("labels", "no_completion", lambda r: r.update(labels=["soft:exception:g9"])),
    ("labels", "no_completion", lambda r: r.update(labels=["observed", "observed"])),
    ("labels", "no_completion", lambda r: r.update(labels=[])),
    ("recorded false", "epsilon_two", lambda r: r["completions"][0].insert(0, {
        "row": "DE13", "decision": {"excepted": "r1"}, "tuple": ["a"]})),
    ("observed outcome", "closed_two", lambda r: r.update(value=True)),
]
# review F2: Lean's genuine row against a request whose record or observations contradict it (a request-value
# comparison, no recomputation): a decision the record sets false shown as DE11, DE10f (with its `forced_all` entry),
# or DE13 for an exception, a switch and a ranking; a zone other than the observed query's value
CONTRADICTED = [
    ("recorded false", "xi1", lambda c: c["record"].append({"decision": {"excepted": "r1"}, "tuple": ["a"], "value": False})),
    ("recorded false", "mu", lambda c: c["record"].append({"decision": {"excepted": "g1"}, "tuple": ["o1"], "value": False})),
    ("recorded false", "mu1", lambda c: c["record"].append({"decision": {"excepted": "r2"}, "tuple": ["a"], "value": False})),
    ("recorded false", "epsilon_off", lambda c: c["record"][0].update(value=False)),
    ("recorded false", "delta_outw", lambda c: c["record"][0].update(value=False)),
    ("observed outcome", "closed_two", lambda c: c["observations"][1].update(value=True)),
    ("observed outcome", "mu1", lambda c: c["observations"].append({"outcome": "p", "tuple": ["a"], "value": True})),
    ("observed outcome", "mu1b", lambda c: c["observations"].append({"outcome": "p", "tuple": ["a"], "value": False})),
]


def test_every_genuine_row_binds():
    for name in CASES:
        case, row, labels, source = genuine(name)
        assert defaults.bind_zone(case, copy.deepcopy(row), source, labels) == row, name


def test_each_binding_refuses_its_tampered_field():
    for what, name, tamper in TAMPERED:
        case, row, labels, source = genuine(name)
        tamper(row)
        with pytest.raises(CheckerUnavailable, match=rf"\({what}\)"):
            defaults.bind_zone(case, row, source, labels)


def test_each_binding_refuses_a_row_its_request_contradicts():
    for what, name, contradict in CONTRADICTED:
        case, row, labels, source = genuine(name)
        contradict(case)
        with pytest.raises(CheckerUnavailable, match=rf"\({what}\)"):
            defaults.bind_zone(case, row, source, labels)


def test_review_f2_probe_a_switch_recorded_false_is_not_shown():
    """PROBE F2 as the review gave it: DF-ε's row showing the user's switch, against a record that sets it false."""
    environment, norms = DOCS["epsilon"]
    case = dict(environment=environment, norms=norms, model={"domains": {"assistant": ["a"]}},
                record=[{"decision": {"off": "r1", "party": "user"}, "tuple": ["a"], "value": False}])
    with pytest.raises(CheckerUnavailable):
        defaults.bind_zone(case, CASES["epsilon_off"][1], {"decisions": {("off", "r1", "user"): ["assistant"]}}, [])


def test_answer_binds_a_zone_through_its_kind(monkeypatch):
    """`answer` asks for the zone's own source when none is given, and binds the row as a zone."""
    case, row, labels, _ = genuine("epsilon_off")
    real = relay.decide
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **options: [row] if mode == defaults.MODE else
                        real(mode, cases, **options))
    assert defaults.answer(case, labels) == row


# Read by tests/test_defaults_checks.py: every check of `bind_zone` is needed by one of these.
BOTH_SIDES = (test_every_genuine_row_binds, test_each_binding_refuses_its_tampered_field,
              test_each_binding_refuses_a_row_its_request_contradicts, test_answer_binds_a_zone_through_its_kind)

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


def test_review_f3_the_committed_words_are_the_lean_generators_output():
    """Review F3: DE10 to DE13's words are Lean's (`zoneHeads`, `zoneLineWords`, `zoneJoins` in
    `lean/VE/Defaults/ZoneWire.lean`): `ve/defaults_words.json` is what `ZoneWordsMain.lean` prints now, checked by
    the generator itself, unmocked. elan's `lake` is the fallback when PATH has none."""
    import os
    import subprocess
    import sys
    from pathlib import Path
    from subprocesses import HANG_TIMEOUT
    root = Path(__file__).resolve().parents[1]
    environ = {**os.environ, "PATH": os.environ.get("PATH", "") + os.pathsep + str(Path.home() / ".elan/bin")}
    done = subprocess.run([sys.executable, str(root / "tools/defaults_words.py"), "--check"], cwd=root, env=environ,
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, (done.stdout, done.stderr)


def test_review_f3_every_zone_sentence_is_lean_s_words_filled(monkeypatch):
    """Review F3: Python words none of DE10 to DE13 (nor DE11 after DE6′): with each of Lean's rows and joins marked,
    every sentence of every fixture is one marked row, its slots filled, and every row of the table is shown by some
    fixture; with the table's words changed, the English changes with them."""
    table = defaults_english._words()
    marked = {"heads": [{**h, "words": f"<{h['row']}:{h['form']}>" + h["words"]} for h in table["heads"]],
              "lines": [{**w, "sentence": f"<{w['row']}:{w['kind']}>" + w["sentence"],
                         "inline": f"[{w['row']}:{w['kind']}]" + w["inline"]} for w in table["lines"]],
              "joins": {key: f"|{word}|" for key, word in table["joins"].items()}}
    monkeypatch.setattr(defaults_english, "_words", lambda: marked)
    used = set()
    for name in CASES:
        case, row, *_ = genuine(name)
        for sentence in defaults_english.sentences(case, row):
            assert sentence.startswith("<"), (name, sentence)
            used.add(sentence[1:sentence.index(">")])
        for lines in row.get("completions", []) if row["zone"] == "leftTo" else []:
            assert all(f"[{line['row']}:" in " ".join(defaults_english.sentences(case, row)) for line in lines)
    expected = {f"{h['row']}:{h['form']}" for h in table["heads"]} | {f"{w['row']}:{w['kind']}" for w in table["lines"]}
    # DE11 and DE13 for an exception are shown inside DE10″ only by some fixtures; the rest each lead a sentence
    assert expected - used <= {"DE10″:long", "DE13:excepted"}, expected - used
