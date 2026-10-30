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

from tests.test_defaults_lean import ALPHA_ENGLISH, DOCS, STRICT, UNLESS_URGENT, X_ALL, asked, env, rule, sent_kind, un
from ve import defaults
from ve.backends import relay
from ve.backends.lean_service import _decode_json
from ve.errors import CheckerUnavailable, VEError

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


def _model_case(environment, norms, domains, relations, conclusion=X_ALL):
    model = {"filling": {}, "model": {"complete": True, "constants": {}, "domains": domains, "relations": relations}}
    return {"id": "m", "kind": "defaults-model", "environment": environment, "norms": norms, "premises": [],
            "conclusion": conclusion, "model": model}


def _binary_env():
    """Plan 4.1's frame with the act `x_required(assistant, user)` and a binary `urgent`."""
    environment = env()
    vocabulary = environment["vocabulary"]
    vocabulary["sorts"]["user"] = {"description": "user"}
    for name in ("x_required", "x_permitted"):
        vocabulary["predicates"][name]["arguments"] = ["assistant", "user"]
        vocabulary["predicates"][name]["regulated"]["act"] = "{0} help {1}"
    vocabulary["predicates"]["urgent"] = {"arguments": ["assistant", "user"], "description": "urgent"}
    return environment


def _forced_cases():
    """(name, case) of `defaults-model` requests whose order no name order gives (review df-1b hunt 1): rules `rb`
    before `ra`, a domain `[e2, e1]`, a binary act in a two-by-two model, and DF-β2 with its exceptions at e1 only."""
    urgent = rule("rb", "x_required", True, sufficient=[un("urgent")])
    everything = [["a1", "u1"], ["a1", "u2"], ["a2", "u1"], ["a2", "u2"]]
    binary = ["binary", "urgent", ["var", 1], ["var", 0]]
    return [
        ("rules-rb-ra", _model_case(env(base=["urgent"]), [urgent, rule("ra", "x_required", True,
                                                                        sufficient=[un("urgent")])],
                                    {"assistant": ["e1"]}, {"urgent": [["e1"]], "soft__excepted__rb": [["e1"]],
                                                            "soft__excepted__ra": [["e1"]]})),
        ("domain-e2-e1", _model_case(env(base=["urgent"]), [{"norm": {**urgent["norm"], "name": "r1"}}],
                                     {"assistant": ["e2", "e1"]}, {"urgent": [["e1"], ["e2"]],
                                                                   "soft__excepted__r1": [["e1"], ["e2"]]})),
        ("binary-act", _model_case(_binary_env(), [rule("r1", "x_required", True, sufficient=[binary])],
                                   {"assistant": ["a1", "a2"], "user": ["u1", "u2"]},
                                   {"urgent": everything, "soft__excepted__r1": everything},
                                   ["forall", "assistant", ["forall", "user",
                                                            ["binary", "x_required", ["var", 1], ["var", 0]]]])),
        ("beta2-at-e1", _model_case(env(base=["calm", "urgent"]), DOCS["beta2"][1], {"assistant": ["e1", "e2"]},
                                    {"calm": [], "urgent": [["e1"]], "soft__excepted__r1": [["e1"]],
                                     "soft__excepted__r2": [["e1"]]})),
    ]


_FORCED: dict = {}


def test_forced_entries_in_the_requests_order(monkeypatch):
    """Lean lists the forced entries in the request's rule order, then the model's domain order, first coordinate
    major (`forcedAt`), whatever the names: each genuine row is the answer, and the same entries in name order or
    second-coordinate-major order are refused; an extra entry where no exception holds is refused (review df-1b
    hunt 1: the order's sort key and the exact set were tested on fixtures where name order is the request's)."""
    if not _FORCED:
        _FORCED.update({name: (case, defaults.run(case), defaults.soft_source(case))
                        for name, case in _forced_cases()})
    expected = {"rules-rb-ra": [("rb", 0, ["e1"]), ("ra", 0, ["e1"])],
                "domain-e2-e1": [("r1", 0, ["e2"]), ("r1", 0, ["e1"])],
                "binary-act": [("r1", 0, ["a1", "u1"]), ("r1", 0, ["a1", "u2"]), ("r1", 0, ["a2", "u1"]),
                               ("r1", 0, ["a2", "u2"])],
                "beta2-at-e1": [("r1", 1, ["e1"]), ("r2", 0, ["e1"])]}
    for name, (case, row, source) in copy.deepcopy(_FORCED).items():
        forced = row["forced"]
        assert [(e["rule"], e["condition"], e["tuple"]) for e in forced] == expected[name], name
        assert defaults.bind_model(case, row, source) is row
        if name == "binary-act":
            reordered = [[forced[0], forced[2], forced[1], forced[3]]]
        elif name == "beta2-at-e1":
            reordered = [forced[::-1]]
            _refused("forced exceptions", defaults.bind_model, case,
                     {**row, "forced": [forced[0], {**forced[0], "tuple": ["e2"]}, forced[1]]}, source)
            # a second entry for the same rule and tuple under another condition (hunt 2): each exception once
            _refused("forced order", defaults.bind_model, case,
                     {**row, "forced": [{**forced[0], "condition": 0}, *forced]}, source)
        else:
            reordered = [forced[::-1]]
        for other in reordered:
            _refused("forced order", defaults.bind_model, case, {**row, "forced": other}, source)


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
    # a sort the model has no domain for has no entity (review df-1b F10's sweep: each `.get` default is needed)
    lacking = case([["a", "u"]])
    del lacking["model"]["model"]["domains"]["user"]
    _refused("forced tuple", defaults.bind_model, lacking, row, source)
    # no stated condition: an exception object without `sufficient`, or none at all (no request Lean answers)
    for drop in ("sufficient", None):
        request = case([["a", "u"]])
        exception = request["norms"][0]["norm"]["exception"]
        exception.pop(drop) if drop else request["norms"][0]["norm"].pop("exception")
        _refused("forced condition", defaults.bind_model, request, row, source)
    # an exception table the model does not list holds nowhere; a table of a rule the request lacks is not read
    empty = {**row, "forced": []}
    assert defaults.bind_model(case([]), empty, source) is empty
    bare = case([])
    del bare["model"]["model"]["relations"]["e"]
    assert defaults.bind_model(bare, empty, source) is empty
    assert defaults.bind_model(case([["a", "u"]]), row, {"excepted": {"r1": "e", "r9": "e"}}) is row


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
    for deciders in (["unstated"], ["assistant", "unstated"]):  # DF-γ's rules both name the assistant
        _refused("collision deciders", defaults.bind_coherence, case,
                 {**row, "collision": {**collision, "deciders": deciders}}, targets)
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
    _refused("collision deciders", defaults.bind_coherence, case,
             {**row, "collision": {**row["collision"], "deciders": ["operator", "assistant"]}}, targets)


@pytest.mark.parametrize("kind,fixture", [("defaults-coherence", "gamma"), ("defaults-model", "beta")])
@pytest.mark.parametrize("filling", [{"absent": [["e0"]]}, {"unsaid__x_required": [["e0", "e0"]]}, {}])
def test_situation_filling_tables_and_tuples_are_bound(monkeypatch, kind, fixture, filling):
    case, row, _, targets, source = _genuine(monkeypatch, fixture, X_ALL, kind)
    forged = {**row, "situation": {"filling": filling}}
    if kind == "defaults-coherence":
        _refused("situation", defaults.bind_coherence, case, forged, targets)
    else:
        _refused("situation", defaults.bind_model, case, forged, source)


# -- the collision's deciders, cell by cell (review df-1b F10): a rule's own `decided_by`, else the document's
#    `exception_decider`, else "unstated" (docs/spec/soft-norms.md 1.2; Lean `SoftNorms.Wire.exceptionDecider`), and
#    one decider when the two rules' are the same, otherwise both in pair order (Lean `giveWayDeciders`).

def _decider_doc(own, document, soft=True):
    """DF-γ with each rule's `decided_by` `own` (a list, one per rule; None: absent) and the document's
    `exception_decider` `document` (None: absent; no soft block at all when not `soft`)."""
    environment = env({**STRICT, **({"exception_decider": document} if document else {})})
    if not soft:
        del environment["vocabulary"]["soft"]
    norms = [rule("r1", "x_required", True, decider=own[0]), rule("r2", "x_permitted", False, decider=own[1])]
    for norm, decider in zip(norms, own):
        if decider is None:
            del norm["norm"]["exception"]["decided_by"]
    return environment, norms


# (cell, the rules' own deciders, the document's, whether it has a soft block, the deciders Lean names), each a
# genuine DF-γ collision. Every cell where a rule's own decider is absent has the document's.
DECIDER_CELLS = [
    ("own-and-document", ["assistant", "assistant"], "operator", True, ["assistant"]),
    ("own-only", ["assistant", "assistant"], None, True, ["assistant"]),
    ("own-no-soft-block", ["assistant", "assistant"], None, False, ["assistant"]),
    ("document-only", [None, None], "operator", True, ["operator"]),
    ("own-unstated", ["unstated", "unstated"], "operator", True, ["unstated"]),
    ("mixed", ["assistant", None], "operator", True, ["assistant", "operator"]),
    ("mixed-reversed", [None, "assistant"], "operator", True, ["operator", "assistant"]),
]
# The deciders a row may name in a cell: the expected one, the other source's, "unstated", an unrelated name, and
# pairs of them in each order.
NAMES = ("assistant", "operator", "unstated", "nobody")
CANDIDATES = [[a] for a in NAMES] + [[a, b] for a in NAMES for b in NAMES if a != b]
_DECIDER_ROWS: dict = {}


def _decider_genuine(monkeypatch, cell):
    """Lean's genuine `defaults-coherence` case and row on the cell's document, and the coherence targets (asked once
    per session, a copy each call)."""
    name, own, document, soft, _ = cell
    if name not in _DECIDER_ROWS:
        monkeypatch.setitem(DOCS, f"deciders-{name}", _decider_doc(own, document, soft))
        _, sent = asked(monkeypatch, f"deciders-{name}")
        case, row = sent_kind(sent, "defaults-coherence")
        _DECIDER_ROWS[name] = (case, row, sent_kind(sent, "defaults-elaborate")[1]["coherence_targets"])
    return copy.deepcopy(_DECIDER_ROWS[name])


def test_collision_deciders_truth_table(monkeypatch):
    """In every cell, Lean's genuine row names the expected deciders and the relay accepts exactly those: the other
    source's, "unstated", an unrelated name and every other pair are refused. The cell with neither source is Lean's
    diagnostic (MissingExceptionDecider), so no row of it reaches the relay; its request expects "unstated" alone."""
    for cell in DECIDER_CELLS:
        case, row, targets = _decider_genuine(monkeypatch, cell)
        assert row["collision"]["deciders"] == cell[-1], cell[0]
        assert defaults.bind_coherence(case, row, targets) is row
        for deciders in CANDIDATES:
            tampered = {**row, "collision": {**row["collision"], "deciders": deciders}}
            if deciders == cell[-1]:
                assert defaults.bind_coherence(case, tampered, targets)
            else:
                _refused("collision deciders", defaults.bind_coherence, case, tampered, targets)
    monkeypatch.setitem(DOCS, "deciders-none", _decider_doc([None, None], None))
    with pytest.raises(VEError, match="MissingExceptionDecider: rule r1"):
        asked(monkeypatch, "deciders-none")
    case, row, targets = _decider_genuine(monkeypatch, DECIDER_CELLS[3])
    without_key, without_block = copy.deepcopy(case), copy.deepcopy(case)
    del without_key["environment"]["vocabulary"]["soft"]["exception_decider"]
    del without_block["environment"]["vocabulary"]["soft"]
    for request in (without_key, without_block):
        for deciders in CANDIDATES:
            tampered = {**row, "collision": {**row["collision"], "deciders": deciders}}
            if deciders == ["unstated"]:
                assert defaults.bind_coherence(request, tampered, targets)
            else:
                _refused("collision deciders", defaults.bind_coherence, request, tampered, targets)
    # a rule's exception object absent (no request Lean answers: a default rule has one) is a decider absent too
    for norm in case["norms"]:
        del norm["norm"]["exception"]
    assert defaults.bind_coherence(case, row, targets) is row


def test_collision_refused_field_by_field(monkeypatch):
    """The one condition the relay accepts a collision on, refused field by field: each member of the collision wrong
    in turn (its rules, its tuple, its deciders, its situation), and each source of the deciders missing in turn from
    the request while the row keeps Lean's answer to the full one."""
    cell = DECIDER_CELLS[0]
    case, row, targets = _decider_genuine(monkeypatch, cell)
    collision, entity = row["collision"], row["collision"]["tuple"][0]
    assert defaults.bind_coherence(case, row, targets) is row
    for change, what in (({"rules": ["r2", "r1"]}, "collision rules"), ({"tuple": ["z"]}, "collision tuple"),
                         ({"tuple": [entity, entity]}, "collision tuple"),
                         ({"deciders": ["operator"]}, "collision deciders")):
        _refused(what, defaults.bind_coherence, case, {**row, "collision": {**collision, **change}}, targets)
    [table] = row["situation"]["filling"] or ["unsaid__x_required"]
    _refused("situation", defaults.bind_coherence, case, {**row, "situation": {"filling": {table: [["z"]]}}}, targets)
    # the rule's own decider missing: the document's ("operator") is expected, Lean's "assistant" is refused
    for index in range(len(case["norms"])):
        own = copy.deepcopy(case)
        del own["norms"][index]["norm"]["exception"]["decided_by"]
        _refused("collision deciders", defaults.bind_coherence, own, row, targets)
    # the document's decider missing: the rules' own still decide; both missing: "unstated"
    bare = copy.deepcopy(case)
    del bare["environment"]["vocabulary"]["soft"]["exception_decider"]
    assert defaults.bind_coherence(bare, row, targets) is row
    for norm in bare["norms"]:
        del norm["norm"]["exception"]["decided_by"]
    _refused("collision deciders", defaults.bind_coherence, bare, row, targets)
    assert defaults.bind_coherence(bare, {**row, "collision": {**collision, "deciders": ["unstated"]}}, targets)
    # Lean's answer to the request without the rules' own deciders is the document's
    _, document_row, _ = _decider_genuine(monkeypatch, DECIDER_CELLS[3])
    assert document_row["collision"]["deciders"] == ["operator"]


def test_situation_entities_of_every_sort():
    """Each filling tuple follows the declared sorts, including two distinct sorts."""
    case = {"environment": {"vocabulary": {"predicates": {
        "p": {"arguments": ["agent", "user"], "regulated": {"default": "unspecified"}}}}}}
    witness = {"model": {"domains": {"agent": ["a"], "user": ["u"]}}}
    defaults._situation(case, {"situation": {"filling": {"unsaid__p": [["a", "u"]]}}}, witness)
    for filling in ({"unsaid__p": [["u", "a"]]}, {"unsaid__p": [["a"]]},
                    {"unsaid__p": [["z", "u"]]}, {"unsaid__p": [], "absent": []}, {}):
        _refused("situation", defaults._situation, case, {"situation": {"filling": filling}}, witness)
    missing = copy.deepcopy(witness)
    del missing["model"]["domains"]["user"]
    _refused("situation", defaults._situation, case,
             {"situation": {"filling": {"unsaid__p": [["a", "u"]]}}}, missing)


_HUNT2: dict = {}


def _hunt2(monkeypatch):
    """Lean's genuine rows on requests the fixtures above do not send (review df-1b hunt 2): DF-α's certificate request
    with a `strict_model` that is no strict countermodel (its own `model`), and DF-γ2's coherence request whose
    collision witness names the second colliding pair."""
    if not _HUNT2:
        case, _, labels, _, _ = _genuine(monkeypatch, "alpha", X_ALL, "defaults-certificate")
        case = {**case, "strict_model": copy.deepcopy(case["model"])}
        _HUNT2["unsettled"] = (case, defaults.run(case), labels)
        case, _, _, targets, _ = _genuine(monkeypatch, "gamma2", X_ALL, "defaults-coherence")
        case = {**case, "collision": {**case["collision"], "rules": ["r1", "r3"]}}
        _HUNT2["second-pair"] = (case, defaults.run(case), targets)
    return copy.deepcopy(_HUNT2)


def test_needs_only_with_a_strict_model_not_exactly_with_one(monkeypatch):
    """A `strict_model` that is no strict countermodel leaves the basis `unsettled` (Lean's `basisOf`): `needs` asks for
    a strict model, but a strict model does not ask for `needs`."""
    case, row, labels = _hunt2(monkeypatch)["unsettled"]
    assert (row["verdict"], row["basis"]) == ("FOLLOWS", "unsettled")
    assert defaults.bind_certificate(case, row, labels) is row


def test_a_collision_on_any_colliding_pair(monkeypatch):
    """A collision names any of the coherence targets, not only the first: Lean's genuine COLLISION on DF-γ2's second
    pair is the answer."""
    case, row, targets = _hunt2(monkeypatch)["second-pair"]
    assert (row["verdict"], row["collision"]["rules"]) == ("COLLISION", ["r1", "r3"])
    assert [m for m, *_ in targets] == ["r1", "r1"] and defaults.bind_coherence(case, row, targets) is row


def test_assumptions_in_the_elaborations_label_order(monkeypatch):
    """`ask` binds a certificate's assumptions to the elaboration's labels in Lean's order, the request's rule order,
    not name order: rules `rb` then `ra`, each guarded by one side of `calm`, need both exceptions, in that order."""
    calm = rule("rb", "x_required", True)
    calm["norm"]["guard"] = un("calm")
    other = rule("ra", "x_required", True)
    other["norm"]["guard"] = ["not", un("calm")]
    monkeypatch.setitem(DOCS, "rb-ra", (env(base=["calm"]), [calm, other]))
    out, _ = asked(monkeypatch, "rb-ra")
    assert out["answer"] == {"verdict": "FOLLOWS", "basis": "needs", "form": "short",
                             "assumptions": ["default:exception:rb", "default:exception:ra"],
                             "deciders": ["assistant"]}


def test_elaborate_labels_and_targets(monkeypatch):
    case, row, _, _, source = _genuine(monkeypatch, "gamma2", X_ALL, "defaults-elaborate")
    assert defaults.bind_elaborate(case, row, source) is row
    [first, second] = row["coherence_targets"]
    for targets in ([first, first], [["r1", "r9", first[2]], second], [second, first], [first], []):
        _refused("coherence targets", defaults.bind_elaborate, case, {**row, "coherence_targets": targets}, source)
    _refused("default premises", defaults.bind_elaborate, case,
             {**row, "default_premises": row["default_premises"][:1] * 2}, source)
    # two premises under one label, their formulas kept (review df-1b hunt 2: labels are distinct, not entries)
    relabelled = copy.deepcopy(row)
    relabelled["default_premises"][1][0] = relabelled["default_premises"][0][0]
    _refused("default premises", defaults.bind_elaborate, case, relabelled, source)


def test_deciders_are_typed_and_bound_on_both_rows(monkeypatch):
    case, row, _, _, source = _genuine(monkeypatch, "gamma2", X_ALL, "defaults-elaborate")
    assert row["deciders"] == ["assistant"]
    assert defaults.bind_elaborate(case, row, source) is row
    for names in ([], ["absent"], ["assistant", "assistant"], ["assistant", "absent"]):
        _refused("deciders", defaults.bind_elaborate, case, {**row, "deciders": names}, source)
    case, row, labels, *_ = _genuine(monkeypatch, "alpha", X_ALL, "defaults-certificate")
    assert row["deciders"] == ["assistant"]
    assert defaults.bind_certificate(case, row, labels) is row
    for names in ([], ["absent"], ["assistant", "assistant"], ["assistant", "absent"]):
        _refused("deciders", defaults.bind_certificate, case, {**row, "deciders": names}, labels)


def test_soft_source_is_the_exception_tables(monkeypatch):
    """`soft_source` reads the exception tables of the source's soft elaboration, and no other decision (DF-ε's switch
    is an `off` decision of r1): a `defaults-model` answer asked without a source binds to them, so Lean's genuine
    DF-β2 row with its four forced entries is the answer."""
    assert defaults.soft_source({"environment": DOCS["epsilon"][0], "norms": DOCS["epsilon"][1]}) == {
        "pairs": [], "excepted": {"r1": "soft__excepted__r1"}}
    case, row, source = _beta2(monkeypatch)
    assert source == {"pairs": [], "excepted": {"r1": "soft__excepted__r1", "r2": "soft__excepted__r2"}}
    real = relay.decide
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **options: [row] if mode == defaults.MODE else
                        real(mode, cases, **options))
    assert defaults.answer(case) == row


def test_answer_binds_each_kind_with_its_binding(monkeypatch):
    """`answer` binds each kind's row with that kind's binding (review df-1b F9's class: an `if ...: return` is a check
    too): each genuine row through the relay is the answer, and a fault only its own binding refuses is refused
    through `answer`, so no kind reaches another kind's binding or none."""
    rows = [(*_genuine(monkeypatch, name, X_ALL, kind), member, what)
            for name, kind, member, what in (("gamma2", "defaults-elaborate", "coherence_targets", "coherence targets"),
                                             ("gamma2", "defaults-coherence", "pairs", "pairs"),
                                             ("delta", "defaults-certificate", "assumptions", "assumptions"))]
    case, row, source = _beta2(monkeypatch)
    rows.append((case, row, (), (), source, "forced", "forced order"))
    answered = {}
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **options: [answered["row"]])
    for case, row, labels, targets, source, member, what in rows:
        kind = case["kind"]
        answered["row"] = row
        assert defaults.answer(case, labels, targets, source) == row, kind
        answered["row"] = {**row, member: row[member][::-1]}
        _refused(what, defaults.answer, case, labels, targets, source)


def test_strict_answer_only_when_lean_says_valid(monkeypatch):
    """`ask` shows the strict answer only when Lean's layered check says `valid` is true (review df-1b F9). DF-ζ's
    strict certificate is valid; the same certificate with its trace cut to one `close` is one Lean replays and rejects
    (a genuine `valid: false` row), and then the default question is asked, never the strict answer shown; DF-α's
    search finds no strict certificate, so the default question is asked without the strict one."""
    out, sent = asked(monkeypatch, "zeta")
    assert out == {"question": "strict", "valid": True, "deciders": ["assistant"],
                   "english": ["This holds whatever the assistant decides."]}
    assert sent_kind(sent, "norm-defaults-certificate")[1]["valid"] is True
    found = defaults._Search.certificate

    def cut(search, X, gamma, phi):
        certificate = found(search, X, gamma, phi)
        return {**certificate, "trace": {"rule": "close"}} if X is search.X else certificate
    with monkeypatch.context() as patch:
        patch.setattr(defaults._Search, "certificate", cut)
        out, sent = asked(monkeypatch, "zeta")
    assert sent_kind(sent, "norm-defaults-certificate")[1]["valid"] is False
    assert (out["question"], out["kind"]) == ("default", "defaults-certificate"), out
    out, sent = asked(monkeypatch, "alpha")
    assert out == {"question": "default", "kind": "defaults-certificate", "answer": {
        "verdict": "FOLLOWS", "basis": "needs", "form": "short", "assumptions": ["default:exception:r1"],
        "deciders": ["assistant"]},
        "english": ALPHA_ENGLISH}
    assert not any(case.get("kind") == "norm-defaults-certificate" for case, _ in sent)


# The tests above, which tests/test_defaults_checks.py runs against each seeded bug of the binding.
BOTH_SIDES = (test_run_binds_the_row_to_its_case, test_forced_condition_index_rule_and_tuple,
              test_forced_order_rule_then_tuple, test_forced_entries_in_the_requests_order, test_forced_tuple_sorts, test_assumptions_and_basis,
              test_pairs_and_collision, test_collision_deciders_truth_table, test_collision_refused_field_by_field,
              test_situation_entities_of_every_sort, test_elaborate_labels_and_targets,
              test_soft_source_is_the_exception_tables, test_needs_only_with_a_strict_model_not_exactly_with_one,
              test_a_collision_on_any_colliding_pair, test_answer_binds_each_kind_with_its_binding,
              test_assumptions_in_the_elaborations_label_order, test_strict_answer_only_when_lean_says_valid)


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
