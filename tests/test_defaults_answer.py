"""The relay never takes a Lean `defaults-*` row that is not an answer to the request it sent (R8; defeasible plan
DF-1b). Genuine answers of the service are mutated one and two faults at a time (each member dropped, emptied,
retyped, duplicated or reordered, a label swapped for another case's, a pair moved): every mutant is
`CheckerUnavailable` or changes nothing the relay shows. Then each binding check on both sides of its boundary."""
from __future__ import annotations

import copy
from itertools import combinations

import pytest

from tests.test_defaults_lean import DOCS, UNLESS_URGENT, X_ALL, asked, sent_kind
from ve import defaults
from ve.backends import relay
from ve.errors import CheckerUnavailable

RETYPED = (7, True, None, [], {}, "x")
# Another case's labels and names (DF-ε's switch, a rule and a decider no fixture here has): the swaps.
SWAPS = ("default:switch:r1:user", "r9", "operator")
# Genuine answers: (fixture, conclusion, kind) for each kind and verdict the relay reads.
GENUINE = [("alpha", X_ALL, "defaults-certificate"), ("beta", X_ALL, "defaults-model"),
           ("beta", UNLESS_URGENT, "defaults-certificate"), ("gamma", X_ALL, "defaults-coherence"),
           ("gamma", X_ALL, "defaults-certificate"), ("gamma2", X_ALL, "defaults-coherence"),
           ("delta", X_ALL, "defaults-certificate")]


def _genuine(monkeypatch, name, conclusion, kind):
    """The case, Lean's row and the binding's inputs: the same source's elaborate labels and targets, and its
    exception tables."""
    _, sent = asked(monkeypatch, name, conclusion)
    elaborated = sent_kind(sent, "defaults-elaborate")[1]
    case, row = sent_kind(sent, kind)
    return (case, row, [label for label, _ in elaborated["default_premises"]], elaborated["coherence_targets"],
            defaults.soft_source(case))


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
            if type(other) is not type(value):
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


def _shown(case, labels, targets, source):
    try:
        return defaults._shown(defaults.answer(case, labels, targets, source))
    except CheckerUnavailable:
        return None


@pytest.mark.parametrize("name, conclusion, kind", GENUINE, ids=[f"{g[0]}-{g[2]}" for g in GENUINE])
def test_mutants_never_pass_as_answers(monkeypatch, name, conclusion, kind):
    case, genuine, *inputs = _genuine(monkeypatch, name, conclusion, kind)
    answered = {"row": genuine}
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **options: [copy.deepcopy(answered["row"])])
    shown = _shown(case, *inputs)
    assert shown is not None
    faults = list(_faults(genuine))
    accepted = []
    for depth, edits in [(1, [(f,) for f in faults]), (2, combinations(faults, 2))]:
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


# -- each binding on both sides of its boundary (bind_* read the request and the row only)

def _refused(bind, *args):
    with pytest.raises(CheckerUnavailable, match="not an answer to the defaults request"):
        bind(*args)


def test_forced_condition_index_rule_and_tuple(monkeypatch):
    case, row, _, _, source = _genuine(monkeypatch, "beta", X_ALL, "defaults-model")
    [entry] = row["forced"]
    entity = entry["tuple"][0]
    assert defaults.bind_model(case, row, source) is row  # condition 0 of one stated condition
    for change in ({"condition": 1}, {"rule": "r9"}, {"tuple": []}, {"tuple": [entity, entity]}, {"tuple": ["z"]}):
        _refused(defaults.bind_model, case, {**row, "forced": [{**entry, **change}]}, source)
    # every exception that holds in the model, and only those: none dropped, none added
    _refused(defaults.bind_model, case, {**row, "forced": []}, source)
    _refused(defaults.bind_model, case, {**row, "forced": [entry, entry]}, source)
    # a strict rule is no default rule; a second condition of a two-condition rule is in range, a third is not
    strict = copy.deepcopy(case)
    strict["norms"][0]["norm"].pop("mode")
    _refused(defaults.bind_model, strict, row, source)
    two = copy.deepcopy(case)
    two["norms"][0]["norm"]["exception"]["sufficient"].append(["top"])
    assert defaults.bind_model(two, {**row, "forced": [{**entry, "condition": 1}]}, source)
    _refused(defaults.bind_model, two, {**row, "forced": [{**entry, "condition": 2}]}, source)


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
        _refused(defaults.bind_model, case(rows), swapped, source)
    _refused(defaults.bind_model, case([["a", "u"]]), {**row, "situation": {"filling": {"t": [["z"]]}}}, source)


def test_assumptions_and_basis(monkeypatch):
    case, row, labels, _, _ = _genuine(monkeypatch, "delta", X_ALL, "defaults-certificate")
    assert len(row["assumptions"]) > 1 and defaults.bind_certificate(case, row, labels) is row
    for assumptions in (row["assumptions"][::-1], [*row["assumptions"], "default:switch:r1:user"],
                        [row["assumptions"][0]] * 2):
        _refused(defaults.bind_certificate, case, {**row, "assumptions": assumptions}, labels)
    assert defaults.bind_certificate(case, {**row, "assumptions": row["assumptions"][1:]}, labels)
    # `needs` only with a strict countermodel; `unsettled` and `strict` without one
    bare = {k: v for k, v in case.items() if k != "strict_model"}
    _refused(defaults.bind_certificate, bare, row, labels)
    assert defaults.bind_certificate(bare, {**row, "basis": "unsettled"}, labels)
    # `strict` exactly when no assumption is kept
    _refused(defaults.bind_certificate, bare, {**row, "basis": "strict"}, labels)
    assert defaults.bind_certificate(bare, {**row, "basis": "strict", "assumptions": []}, labels)
    _refused(defaults.bind_certificate, bare, {**row, "basis": "unsettled", "assumptions": []}, labels)
    _refused(defaults.bind_certificate, case, {**row, "reason": "no certificate"}, labels)
    unknown = {"verdict": "UNKNOWN", "reason": "no certificate"}
    assert defaults.bind_certificate(case, unknown, labels)
    _refused(defaults.bind_certificate, case, {**unknown, "reason": ""}, labels)


def test_pairs_and_collision(monkeypatch):
    case, row, _, targets, _ = _genuine(monkeypatch, "gamma2", X_ALL, "defaults-coherence")
    assert len(row["pairs"]) == 2 and defaults.bind_coherence(case, row, targets) is row
    _refused(defaults.bind_coherence, case, {**row, "pairs": row["pairs"][::-1]}, targets)
    case, row, _, targets, _ = _genuine(monkeypatch, "gamma", X_ALL, "defaults-coherence")
    collision = row["collision"]
    assert defaults.bind_coherence(case, row, targets) is row
    for change in ({"rules": ["r2", "r1"]}, {"deciders": ["operator"]}, {"deciders": ["assistant"] * 2},
                   {"deciders": ["assistant", "unstated", "operator"]}, {"deciders": []}, {"tuple": []}):
        _refused(defaults.bind_coherence, case, {**row, "collision": {**collision, **change}}, targets)
    for deciders in (["unstated"], ["assistant", "unstated"]):
        assert defaults.bind_coherence(case, {**row, "collision": {**collision, "deciders": deciders}}, targets)
    _refused(defaults.bind_coherence, {k: v for k, v in case.items() if k != "collision"}, row, targets)


def test_elaborate_labels_and_targets(monkeypatch):
    case, row, _, _, source = _genuine(monkeypatch, "gamma2", X_ALL, "defaults-elaborate")
    assert defaults.bind_elaborate(case, row, source) is row
    [first, second] = row["coherence_targets"]
    for targets in ([first, first], [["r1", "r9", first[2]], second], [second, first], [first], []):
        _refused(defaults.bind_elaborate, case, {**row, "coherence_targets": targets}, source)
    _refused(defaults.bind_elaborate, case, {**row, "default_premises": row["default_premises"][:1] * 2}, source)


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
            return [copy.deepcopy(answered["row"])]
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
