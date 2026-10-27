"""The relay never takes a Lean `defaults-*` row that is not an answer to the request it sent (R8; defeasible plan
DF-1b). Genuine answers of the service are mutated one and two faults at a time (each member dropped, emptied,
retyped, duplicated or reordered, a label swapped for another case's, a pair moved): every mutant is
`CheckerUnavailable` or changes nothing the relay shows. Then each binding check on both sides of its boundary."""
from __future__ import annotations

import copy
import json
import re
from itertools import combinations

import pytest

from tests.test_defaults_lean import DOCS, UNLESS_URGENT, X_ALL, asked, sent_kind
from ve import defaults
from ve.backends import relay
from ve.backends.lean_service import _decode_json
from ve.errors import CheckerUnavailable

DEEP: list = []
for _ in range(10_000):
    DEEP = [DEEP]
RETYPED = (7, 1.5, True, None, [], {}, "x", "\ud800", DEEP)
# Another case's labels and names (DF-ε's switch, a rule and a decider no fixture here has): the swaps.
SWAPS = ("default:switch:r1:user", "r9", "operator")
# Genuine answers: (fixture, conclusion, kind) for each kind and verdict the relay reads.
GENUINE = [("alpha", X_ALL, "defaults-certificate"), ("beta", X_ALL, "defaults-model"),
           ("beta", UNLESS_URGENT, "defaults-certificate"), ("gamma", X_ALL, "defaults-coherence"),
           ("gamma", X_ALL, "defaults-certificate"), ("gamma2", X_ALL, "defaults-coherence"),
           ("delta", X_ALL, "defaults-certificate")]


_GENUINE: dict = {}


def _genuine(monkeypatch, name, conclusion, kind):
    """The case, Lean's row and the binding's inputs: the same source's elaborate labels and targets, and its
    exception tables. Asked once per session (a copy each call), so a seeded bug of the binding
    (tests/test_defaults_checks.py) runs the binding alone."""
    key = (name, json.dumps(conclusion), kind)
    if key not in _GENUINE:
        _, sent = asked(monkeypatch, name, conclusion)
        elaborated = sent_kind(sent, "defaults-elaborate")[1]
        case, row = sent_kind(sent, kind)
        _GENUINE[key] = (case, row, [label for label, _ in elaborated["default_premises"]],
                         elaborated["coherence_targets"], defaults.soft_source(case))
    return copy.deepcopy(_GENUINE[key])


def _nodes(value, path=()):
    """Every member to the depth of a formula's root (`default_premises/i/1`): a formula is mutated whole."""
    yield path, value
    children = (() if len(path) == 3 else value.items() if type(value) is dict else
                enumerate(value) if type(value) is list else ())
    for key, child in children:
        yield from _nodes(child, (*path, key))


def _set(row, path, value):
    out = copy.deepcopy(row)
    parent = out
    for step in path[:-1]:
        parent = parent[step]
    if value is _set:
        del parent[path[-1]]
    else:
        parent[path[-1]] = value
    return out


def _faults(row):
    """One-fault mutants as (path, value) edits, `_set` as the value dropping the member: each member dropped, each
    value emptied or retyped (to another JSON type), each string swapped for another case's label or name, each
    list's element duplicated and the list reordered (a pair moved), an index pushed out of range."""
    for path, value in _nodes(row):
        if not path:
            continue
        if type(path[-1]) is str:
            yield path, _set
        for other in RETYPED:
            if type(other) is not type(value) or other == "\ud800":
                yield path, other
        if type(value) in (str, list, dict) and value:
            yield path, type(value)()
        if type(value) is str and path[-1] != "reason":  # Lean's text, not a label (its shape types it `str`)
            yield from ((path, other) for other in SWAPS if other != value)
        if type(value) is int and type(value) is not bool:
            yield path, value + 1
        if type(value) is list and value:
            for other in ([value[0], *value], [*value, value[-1]], value[::-1]):
                if other != value:
                    yield path, other


def _transported(row):
    """The row as the service's transport hands it on (`LeanService` decodes each line with `_decode_json`): a value no
    JSON line holds (a lone surrogate, nesting past the runtime's limit) is a malformed response there."""
    try:
        return _decode_json(json.dumps(row))
    except (ValueError, RecursionError):
        raise CheckerUnavailable("CheckerUnavailable: malformed response") from None


def _shown(case, labels, targets, source):
    try:
        return defaults._shown(defaults.answer(case, labels, targets, source))
    except CheckerUnavailable:
        return None


@pytest.mark.parametrize("name, conclusion, kind", GENUINE, ids=[f"{g[0]}-{g[2]}" for g in GENUINE])
def test_mutants_never_pass_as_answers(monkeypatch, name, conclusion, kind):
    case, genuine, *inputs = _genuine(monkeypatch, name, conclusion, kind)
    answered = {"row": genuine}
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **options: [_transported(answered["row"])])
    shown = _shown(case, *inputs)
    assert shown is not None
    faults = list(_faults(genuine))
    shallow = [fault for fault in faults if fault[1] is not DEEP]  # a 10k-deep list is one fault only
    accepted = []
    for depth, edits in [(1, [(f,) for f in faults]), (2, combinations(shallow, 2))]:
        for edit in edits:
            try:
                mutant = genuine
                for path, value in edit:
                    mutant = _set(mutant, path, value)
            except (KeyError, IndexError, TypeError):
                continue  # the second fault's path is gone after the first
            if mutant == genuine:
                continue
            answered["row"] = mutant
            seen = _shown(case, *inputs)
            if seen is not None and seen != shown:
                accepted.append((depth, edit))
    assert not accepted, accepted[:5]


# -- each binding on both sides of its boundary (bind_* read the request and the row only). Each refusal names the
#    check that refuses it, and each fixture breaks that check alone, so every check is needed by some fixture
#    (tests/test_defaults_checks.py deletes each one in turn).

def _refused(what, bind, *args):
    with pytest.raises(CheckerUnavailable, match=rf"not an answer to the defaults request \({re.escape(what)}[):]"):
        bind(*args)


def test_run_binds_the_row_to_its_case(monkeypatch):
    case, genuine, *_ = _genuine(monkeypatch, "beta", X_ALL, "defaults-model")
    answered = {}
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **options: [answered["row"]])
    answered["row"] = genuine
    assert defaults.run(case) == genuine
    # the shape binds the row's id to the case's
    for row in ({**genuine, "id": "other"}, {k: v for k, v in genuine.items() if k != "verdict"}):
        answered["row"] = row
        _refused("shape", defaults.run, case)


def test_forced_condition_index_rule_and_tuple(monkeypatch):
    case, row, _, _, source = _genuine(monkeypatch, "beta", X_ALL, "defaults-model")
    [entry] = row["forced"]
    entity = entry["tuple"][0]
    assert defaults.bind_model(case, row, source) is row  # condition 0 of one stated condition
    for change, what in (({"condition": 1}, "forced condition"), ({"rule": "r9"}, "forced rule"),
                         ({"tuple": []}, "forced tuple"), ({"tuple": [entity, entity]}, "forced tuple"),
                         ({"tuple": ["z"]}, "forced tuple")):
        _refused(what, defaults.bind_model, case, {**row, "forced": [{**entry, **change}]}, source)
    # every exception that holds in the model, and only those: none dropped, none added, none twice
    _refused("forced exceptions", defaults.bind_model, case, {**row, "forced": []}, source)
    _refused("forced order", defaults.bind_model, case, {**row, "forced": [entry, entry]}, source)
    # a strict rule is no default rule; a second condition of a two-condition rule is in range, a third is not
    strict = copy.deepcopy(case)
    strict["norms"][0]["norm"].pop("mode")
    _refused("forced rule", defaults.bind_model, strict, row, source)
    two = copy.deepcopy(case)
    two["norms"][0]["norm"]["exception"]["sufficient"].append(["top"])
    assert defaults.bind_model(two, {**row, "forced": [{**entry, "condition": 1}]}, source)
    _refused("forced condition", defaults.bind_model, two, {**row, "forced": [{**entry, "condition": 2}]}, source)
    # a situation and `forced` exactly with DOES-NOT-FOLLOW; the situation's entities are the model's
    _refused("verdict", defaults.bind_model, case, {k: v for k, v in row.items() if k != "situation"}, source)
    _refused("verdict", defaults.bind_model, case, {k: v for k, v in row.items() if k != "forced"}, source)
    unknown = {"id": row["id"], "status": "ok", "verdict": "UNKNOWN", "reason": "no countermodel"}
    assert defaults.bind_model(case, unknown, source) is unknown
    _refused("verdict", defaults.bind_model, case, {**unknown, "situation": row["situation"]}, source)
    _refused("verdict", defaults.bind_model, case, {**unknown, "situation": row["situation"], "forced": []}, source)
    _refused("verdict", defaults.bind_model, case,
             {k: v for k, v in row.items() if k not in ("situation", "forced")}, source)
    [table] = row["situation"]["filling"] or ["unsaid__x_required"]
    _refused("situation", defaults.bind_model, case, {**row, "situation": {"filling": {table: [["z"]]}}}, source)
    assert defaults.bind_model(case, {**row, "situation": {"filling": {table: [[entity]]}}}, source)


_BETA2: dict = {}


def _beta2(monkeypatch):
    """Lean's DOES-NOT-FOLLOW row on DF-β2 (two rules, two conditions) in a model of two entities where every
    exception holds: four `forced` entries, in rule order and then the model's entity order."""
    if not _BETA2:
        environment, norms = DOCS["beta2"]
        model = {"filling": {}, "model": {"complete": True, "constants": {}, "domains": {"assistant": ["e1", "e2"]},
                                          "relations": {"calm": [["e1"], ["e2"]], "urgent": [["e1"], ["e2"]],
                                                        "soft__excepted__r1": [["e1"], ["e2"]],
                                                        "soft__excepted__r2": [["e1"], ["e2"]]}}}
        case = {"id": "m", "kind": "defaults-model", "environment": environment, "norms": norms, "premises": [],
                "conclusion": X_ALL, "model": model}
        _BETA2["genuine"] = (case, defaults.run(case), defaults.soft_source(case))
    return copy.deepcopy(_BETA2["genuine"])


def test_forced_order_rule_then_tuple(monkeypatch):
    case, row, source = _beta2(monkeypatch)
    r1e1, r1e2, r2e1, r2e2 = row["forced"]
    assert [(e["rule"], e["tuple"]) for e in row["forced"]] == [
        ("r1", ["e1"]), ("r1", ["e2"]), ("r2", ["e1"]), ("r2", ["e2"])]
    assert defaults.bind_model(case, row, source) is row
    for forced in ([r1e2, r1e1, r2e1, r2e2], [r2e1, r2e2, r1e1, r1e2], row["forced"][::-1]):
        _refused("forced order", defaults.bind_model, case, {**row, "forced": forced}, source)


def test_forced_tuple_sorts():
    """A tuple of the act's sorts in order, each entity in its sort's domain: the swapped tuple is refused, even where
    the model's table holds it; a situation's entity outside the model is refused."""
    source = {"excepted": {"r1": "e"}}

    def case(rows):
        return {"environment": {"vocabulary": {"predicates": {"p": {"arguments": ["agent", "user"]}}}},
                "norms": [{"norm": {"name": "r1", "predicate": "p", "mode": "default",
                                    "exception": {"sufficient": [1]}}}],
                "model": {"model": {"domains": {"agent": ["a"], "user": ["u"]}, "relations": {"e": rows}}}}
    row = {"verdict": "DOES-NOT-FOLLOW", "situation": {"filling": {}},
           "forced": [{"rule": "r1", "condition": 0, "tuple": ["a", "u"]}]}
    assert defaults.bind_model(case([["a", "u"]]), row, source) is row
    swapped = {**row, "forced": [{"rule": "r1", "condition": 0, "tuple": ["u", "a"]}]}
    for rows in ([["a", "u"]], [["u", "a"]]):
        _refused("forced tuple", defaults.bind_model, case(rows), swapped, source)
    _refused("situation", defaults.bind_model, case([["a", "u"]]), {**row, "situation": {"filling": {"t": [["z"]]}}},
             source)


def test_assumptions_and_basis(monkeypatch):
    case, row, labels, _, _ = _genuine(monkeypatch, "delta", X_ALL, "defaults-certificate")
    assert len(row["assumptions"]) > 1 and defaults.bind_certificate(case, row, labels) is row
    for assumptions in (row["assumptions"][::-1], [*row["assumptions"], "default:switch:r1:user"],
                        [row["assumptions"][0]] * 2):
        _refused("assumptions", defaults.bind_certificate, case, {**row, "assumptions": assumptions}, labels)
    assert defaults.bind_certificate(case, {**row, "assumptions": row["assumptions"][1:]}, labels)
    # `needs` only with a strict countermodel; `unsettled` and `strict` without one
    bare = {k: v for k, v in case.items() if k != "strict_model"}
    _refused("basis", defaults.bind_certificate, bare, row, labels)
    assert defaults.bind_certificate(bare, {**row, "basis": "unsettled"}, labels)
    # `strict` exactly when no assumption is kept
    _refused("assumptions", defaults.bind_certificate, bare, {**row, "basis": "strict"}, labels)
    assert defaults.bind_certificate(bare, {**row, "basis": "strict", "assumptions": []}, labels)
    _refused("assumptions", defaults.bind_certificate, bare, {**row, "basis": "unsettled", "assumptions": []}, labels)
    # `basis`, `form` and `assumptions` exactly with FOLLOWS, a reason exactly without it, and never empty
    _refused("verdict", defaults.bind_certificate, case, {**row, "reason": "no certificate"}, labels)
    _refused("verdict", defaults.bind_certificate, case, {k: v for k, v in row.items() if k != "form"}, labels)
    unknown = {"verdict": "UNKNOWN", "reason": "no certificate"}
    assert defaults.bind_certificate(case, unknown, labels)
    _refused("verdict", defaults.bind_certificate, case, {**unknown, "form": "short"}, labels)
    _refused("verdict", defaults.bind_certificate, case, {"verdict": "UNKNOWN"}, labels)
    _refused("reason", defaults.bind_certificate, case, {**unknown, "reason": ""}, labels)


def test_pairs_and_collision(monkeypatch):
    case, row, _, targets, _ = _genuine(monkeypatch, "gamma2", X_ALL, "defaults-coherence")
    assert len(row["pairs"]) == 2 and defaults.bind_coherence(case, row, targets) is row
    _refused("pairs", defaults.bind_coherence, case, {**row, "pairs": row["pairs"][::-1]}, targets)
    case, row, _, targets, _ = _genuine(monkeypatch, "gamma", X_ALL, "defaults-coherence")
    collision = row["collision"]
    assert defaults.bind_coherence(case, row, targets) is row
    for change, what in (({"deciders": ["operator"]}, "collision deciders"),
                         ({"deciders": ["assistant"] * 2}, "collision deciders"),
                         ({"deciders": []}, "collision deciders"), ({"tuple": []}, "collision tuple")):
        _refused(what, defaults.bind_coherence, case, {**row, "collision": {**collision, **change}}, targets)
    for deciders in (["unstated"], ["assistant", "unstated"]):
        assert defaults.bind_coherence(case, {**row, "collision": {**collision, "deciders": deciders}}, targets)
    # the collision's rules: the request's witness (none sent, another pair) and a coherence target, each alone
    _refused("collision rules", defaults.bind_coherence, {k: v for k, v in case.items() if k != "collision"}, row,
             targets)
    swapped = {**case, "collision": {**case["collision"], "rules": ["r2", "r1"]}}
    _refused("collision rules", defaults.bind_coherence, swapped, row, targets)
    _refused("collision rules", defaults.bind_coherence, swapped,
             {**row, "collision": {**collision, "rules": ["r2", "r1"]}}, targets)
    # the situation's entities are the witness model's
    [table] = row["situation"]["filling"]
    entity = collision["tuple"][0]
    assert defaults.bind_coherence(case, {**row, "situation": {"filling": {table: [[entity]]}}}, targets)
    _refused("situation", defaults.bind_coherence, case, {**row, "situation": {"filling": {table: [["z"]]}}},
             targets)
    # three deciders, each distinct and named by the two rules (DF-γ′): at most two
    case, row, _, targets, _ = _genuine(monkeypatch, "gamma'", X_ALL, "defaults-coherence")
    assert row["collision"]["deciders"] == ["assistant", "operator"]
    _refused("collision deciders", defaults.bind_coherence, case,
             {**row, "collision": {**row["collision"], "deciders": ["assistant", "operator", "unstated"]}}, targets)


def test_elaborate_labels_and_targets(monkeypatch):
    case, row, _, _, source = _genuine(monkeypatch, "gamma2", X_ALL, "defaults-elaborate")
    assert defaults.bind_elaborate(case, row, source) is row
    [first, second] = row["coherence_targets"]
    for targets in ([first, first], [["r1", "r9", first[2]], second], [second, first], [first], []):
        _refused("coherence targets", defaults.bind_elaborate, case, {**row, "coherence_targets": targets}, source)
    _refused("default premises", defaults.bind_elaborate, case,
             {**row, "default_premises": row["default_premises"][:1] * 2}, source)


# The tests above, which tests/test_defaults_checks.py runs against each seeded bug of the binding.
BOTH_SIDES = (test_run_binds_the_row_to_its_case, test_forced_condition_index_rule_and_tuple,
              test_forced_order_rule_then_tuple, test_forced_tuple_sorts, test_assumptions_and_basis,
              test_pairs_and_collision, test_elaborate_labels_and_targets)


@pytest.mark.parametrize("name", ["alpha", "gamma"])
def test_elaborate_mutants_lose_evidence_at_most(monkeypatch, name):
    """`defaults-elaborate` is the search's input and the label set assumptions bind to; its labels and formulas are
    Lean's to generate, so no binding of Python's can check them, but Lean binds every certificate and model the search
    builds from them to its own regeneration. So each one-fault mutant is `CheckerUnavailable`, changes nothing `ask`
    shows, or loses the search evidence: each verdict shown is UNKNOWN or the genuine one, never another."""
    genuine_out, sent = asked(monkeypatch, name)
    _, genuine = sent_kind(sent, "defaults-elaborate")
    real, answered = relay.decide, {}

    def decide(mode, cases, **options):
        if cases[0].get("kind") == "defaults-elaborate":
            return [_transported(answered["row"])]
        return real(mode, cases, **options)
    monkeypatch.setattr(relay, "decide", decide)
    found = []
    for path, value in _faults(genuine):
        answered["row"] = _set(genuine, path, value)
        try:
            out = defaults.ask(*DOCS[name], [], X_ALL)
        except CheckerUnavailable:
            continue
        verdicts = [(o["answer"]["verdict"], o.get("coherence", {}).get("verdict")) for o in (out, genuine_out)]
        if out != genuine_out and any(v not in ("UNKNOWN", g) for v, g in zip(*verdicts)):
            found.append((path, value, out))
    assert not found, found[:3]
