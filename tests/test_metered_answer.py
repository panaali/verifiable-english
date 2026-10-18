"""The `metered` relay never shows a trace binding the request does not hold (lf-18 review F1; DRI-RULINGS R8 (b),
FINDING-CLASSES 4 and 15). Genuine traces of Lean's metered evaluator are mutated one and two faults at a time in
their bindings (each binding's sort, entity and index rebound to a value the request's model does not hold, or to
one of another sort, retyped, dropped, duplicated and reordered); every mutant is `CheckerUnavailable` from the
reader `ve.evaluate.read_evaluation`, or every binding it shows is still an entity of its sort in the request's
model, and nothing else escapes. Which entity of the model a node binds is Lean's (R8: semantic consistency is
the encoder's), so a mutant that swaps one entity of the model for another may be shown. Through the public
`evaluate`, the reviewer's probe (every binding renamed in the service's answer) is refused."""
import copy
import itertools

import pytest

import ve.backends.lean_service as lean_service
from ve import Environment, FiniteModel
from ve.ast import Exists, Forall, Unary, Var, _to_data
from ve.backends import relay
from ve.errors import CheckerUnavailable
from ve.evaluate import evaluate, read_evaluation
from ve.profiles import SPEC_REVISION

RAW = {"language": "ve.core@0.2", "profiles": ["relational-fol@0"], "spec_revision": SPEC_REVISION,
       "vocabulary": {"sorts": {"item": {"description": "item"}, "place": {"description": "place"}},
                      "predicates": {"base": {"arguments": ["item"], "description": "base"},
                                     "near": {"arguments": ["item", "place"], "description": "near"}},
                      "constants": {}}}
MODEL = {"complete": True, "domains": {"item": ["i", "j"], "place": ["p"]}, "constants": {},
         "relations": {"base": [["i"]], "near": [["i", "p"]]}}
FORMULAS = {
    "every": Forall("item", Unary("base", Var(0))),
    "some": Exists("item", Unary("base", Var(0))),
    # two locals: every binding list has an inner `place` and an outer `item`
    "nested": Forall("item", Exists("place", Unary("base", Var(1)))),
}
RETYPED = (7, True, None, [], {}, "", 1.5)


def _case(formula):
    return {"id": "evaluate", "kind": "evaluate-budgeted", "environment": RAW, "model": MODEL,
            "ast": [_to_data(formula)], "max_evaluations": 1000, "max_trace_nodes": 1000, "trace": True}


@pytest.fixture(scope="module")
def genuine():
    cases = {name: _case(formula) for name, formula in FORMULAS.items()}
    rows = relay.rows("metered", list(cases.values()))
    return {name: (case, row) for (name, case), row in zip(cases.items(), rows)}


def _sites(row):
    """(row index, binding index) of every binding of a genuine trace."""
    return [(r, b) for r, node in enumerate(row["evaluation"]["explanation"]) for b in range(len(node["bindings"]))]


def _faults(row):
    """One-fault mutators of a trace's bindings, each a function of a row copy."""
    out = []
    for r, b in _sites(row):
        def at(mutated, r=r):
            return mutated["evaluation"]["explanation"][r]["bindings"]
        for field, values in (("sort", ("nosort", "place", "item", "", "zz-not-in-request")),
                              ("local_id", ("nobody", "p", "i", "j", "")),
                              ("debruijn_index", (b + 1, b - 1, 99))):
            for value in (*values, *RETYPED):
                out.append((f"{r}/{b}/{field}={value!r}",
                            lambda m, at=at, b=b, field=field, value=value: at(m)[b].__setitem__(field, value)))
            out.append((f"{r}/{b}/{field} dropped", lambda m, at=at, b=b, field=field: at(m)[b].pop(field)))
        out.append((f"{r}/{b} extra member", lambda m, at=at, b=b: at(m)[b].__setitem__("extra", "x")))
        out.append((f"{r}/{b} dropped", lambda m, at=at, b=b: at(m).pop(b)))
        out.append((f"{r}/{b} duplicated", lambda m, at=at, b=b: at(m).insert(b, copy.deepcopy(at(m)[b]))))
        out.append((f"{r}/{b} retyped", lambda m, at=at, b=b: at(m).__setitem__(b, "x")))
        out.append((f"{r} reordered", lambda m, at=at: at(m).reverse()))
    return out


def _outcome(case, row):
    try:
        return read_evaluation(row, case)
    except CheckerUnavailable:
        return "refused"


def _walk(node):
    yield node
    for child in node.children:
        yield from _walk(child)


def _bound(result) -> bool:
    """Whether every binding a read trace shows is an entity of its sort in the request's model."""
    return all(entity in MODEL["domains"].get(sort, ())
               for node in _walk(result.explanation) for sort, entity in node.bindings)


@pytest.mark.parametrize("name", sorted(FORMULAS))
def test_genuine_traces_are_read_and_bind_only_the_models_entities(genuine, name):
    case, row = genuine[name]
    result = read_evaluation(copy.deepcopy(row), case)
    assert result.explanation is not None and _sites(row) and _bound(result)


@pytest.mark.parametrize("name", sorted(FORMULAS))
def test_every_one_and_two_fault_binding_mutant_is_refused_or_still_bound(genuine, name):
    case, row = genuine[name]
    faults = _faults(row)
    accepted = []
    for chosen in itertools.chain(((f,) for f in faults), itertools.combinations(faults[::3], 2)):
        mutated = copy.deepcopy(row)
        for _, fault in chosen:
            fault(mutated)
        if mutated == row:
            continue
        outcome = _outcome(case, mutated)
        if outcome != "refused" and not _bound(outcome):
            accepted.append([label for label, _ in chosen])
    assert accepted == []


@pytest.mark.parametrize("field,value", [("sort", "nosort"), ("local_id", "nobody"), ("sort", "place"),
                                         ("local_id", "p")])
def test_a_binding_outside_the_request_model_is_refused(genuine, field, value):
    """An unknown sort or entity, and an entity of the request that is of another sort, are no answer."""
    case, row = genuine["every"]
    mutated = copy.deepcopy(row)
    node = next(node for node in mutated["evaluation"]["explanation"] if node["bindings"])
    node["bindings"][0][field] = value
    with pytest.raises(CheckerUnavailable, match="unbound Lean trace bindings"):
        read_evaluation(mutated, case)


def test_the_reviewers_probe_is_refused_through_evaluate(monkeypatch):
    """PROBE F1: the service's answer with every trace binding renamed to `nosort`/`nobody` reaches the public
    `evaluate` (it was accepted and shown); now it is CheckerUnavailable."""
    def rename(value):
        if isinstance(value, dict):
            if "debruijn_index" in value:
                value.update(sort="nosort", local_id="nobody")
            for item in value.values():
                rename(item)
        elif isinstance(value, list):
            for item in value:
                rename(item)
        return value
    decode = lean_service._decode_json
    monkeypatch.setattr(lean_service, "_decode_json", lambda line: rename(decode(line)))
    env = Environment(RAW)
    model = FiniteModel.from_dict(env, MODEL)
    with pytest.raises(CheckerUnavailable):
        evaluate(env, FORMULAS["every"], model, trace=True)
    monkeypatch.setattr(lean_service, "_decode_json", decode)
    assert evaluate(env, FORMULAS["every"], model, trace=True).explanation is not None
