"""Hand-written W1 counterexamples from norms spec 10.1."""
import pytest

from ve.ast import Binary, Not, Top, Unary, Var
from ve.background import background
from ve.environment import Environment
from ve.errors import InvalidModel, VEError
from ve.model import FiniteModel
from ve.norms import Norm, NormDocument, check_conflict, check_witness
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.evaluate import _Evaluator


def environment(predicates, sorts=("act",), base=None):
    return Environment({"language": LANGUAGE, "profiles": ["norms@0", "relational-fol@0"],
                        "spec_revision": SPEC_REVISION,
                        "vocabulary": {"sorts": {s: {"description": s} for s in sorts},
                                       "predicates": {**(base or {}), **predicates}, "constants": {}}})


def permission(default="deny", *, act="{0} be done", args=("act",)):
    return {"arguments": list(args), "description": "permission",
            "regulated": {"role": "permission", "default": default, "act": act}}


def obligation(default="deny", dual="permitted", *, act="{0} be done", args=("act",)):
    reg = {"role": "obligation", "default": default, "act": act}
    if dual is not None:
        reg["permission"] = dual
    return {"arguments": list(args), "description": "obligation", "regulated": reg}


def rule(name, predicate, sign, guard=None, *, unless=(), over=()):
    return Norm(name, predicate, sign, Top() if guard is None else guard, tuple(unless), tuple(over))


def model(doc, **relations):
    env = doc.base_environment()
    return FiniteModel.from_dict(env, {"complete": True,
                                       "domains": {s: [s + "0"] for s in env.sorts},
                                       "constants": {},
                                       "relations": {p: relations.get(p, []) for p in env.predicates}})


def value(doc, predicate, row, base_model):
    sorts = doc.env.predicates[predicate].arguments
    bindings = tuple(zip(reversed(sorts), reversed(row)))
    return _Evaluator(doc.base_environment(), base_model, 100000, trace=False).formula(
        doc.outcome(predicate, base=True), bindings)[0]


def test_pair_rule_and_default_counterexamples():
    env = environment({"required": obligation(), "permitted": permission()})
    must = NormDocument(env, [rule("must", "required", True)])
    witness = check_conflict(must, model=model(must))
    assert (witness.status, witness.target, witness.tuple) == ("CONFLICT", "required->permitted", ("act0",))
    assert "act act0" in witness.situation

    env = environment({"required": obligation("allow"), "permitted": permission()})
    default = NormDocument(env, [])
    assert check_conflict(default, model=model(default)).target == "required->permitted"

    repaired = NormDocument(environment({"required": obligation(), "permitted": permission()}),
                            [rule("must", "required", True), rule("may", "permitted", True)])
    assert check_conflict(repaired, prove=True).status == "CONFLICT-FREE"
    assert value(repaired, "required", ("act0",), model(repaired))
    assert value(repaired, "permitted", ("act0",), model(repaired))


def test_grandchild_diamond_and_carved_out_descendant():
    env = environment({"permitted": permission()})
    grandchild = NormDocument(env, [rule("r1", "permitted", False),
                                    rule("r2", "permitted", False, over=("r1",)),
                                    rule("r3", "permitted", True, over=("r2",))])
    assert value(grandchild, "permitted", ("act0",), model(grandchild))
    assert check_conflict(grandchild, prove=True).status == "CONFLICT-FREE"
    diamond = NormDocument(env, [rule("r1", "permitted", False),
                                 rule("r2", "permitted", False, over=("r1",)),
                                 rule("r3", "permitted", False, over=("r1",)),
                                 rule("r4", "permitted", True, over=("r2", "r3"))])
    _, _, selected = diamond.selection("permitted")
    evaluator = _Evaluator(diamond.base_environment(), model(diamond), 100000, trace=False)
    assert {n for n, f in selected.items() if evaluator.formula(f, (("act", "act0"),))[0]} == {"r4"}
    carved = NormDocument(env, [rule("r1", "permitted", False),
                                rule("r2", "permitted", False, unless=(Top(),), over=("r1",)),
                                rule("r3", "permitted", True, over=("r2",))])
    assert value(carved, "permitted", ("act0",), model(carved))


def test_exception_has_own_guard_and_carve_out_is_silent():
    base = {"monday": {"arguments": ["act"], "description": "monday"},
            "on_call": {"arguments": ["act"], "description": "on call"}}
    env = environment({"permitted": permission()}, base=base)
    monday, call = Unary("monday", Var(0)), Unary("on_call", Var(0))
    doc = NormDocument(env, [rule("ban", "permitted", False, monday),
                             rule("release", "permitted", True, call, over=("ban",))])
    tuesday = model(doc, on_call=[["act0"]])
    assert value(doc, "permitted", ("act0",), tuesday)
    carve = NormDocument(env, [rule("ban", "permitted", False, unless=(call,))])
    exception = NormDocument(env, [rule("ban", "permitted", False),
                                  rule("release", "permitted", True, call, over=("ban",))])
    assert not value(carve, "permitted", ("act0",), tuesday)
    assert value(exception, "permitted", ("act0",), tuesday)
    independent = NormDocument(env, [*exception.rules, rule("other-ban", "permitted", False)])
    assert check_conflict(independent, model=tuesday).status == "CONFLICT"


def test_mixed_sort_tuple_stays_in_argument_order():
    base = {"relation": {"arguments": ["state", "person"], "description": "relation"}}
    env = environment({"permitted": permission(act="{0} help {1}", args=("state", "person"))},
                      sorts=("state", "person"), base=base)
    guard = Binary("relation", Var(1), Var(0))
    doc = NormDocument(env, [rule("yes", "permitted", True, guard),
                             rule("no", "permitted", False, guard)])
    witness = check_conflict(doc, model=model(doc, relation=[["state0", "person0"]]))
    assert witness.target == "permitted" and witness.tuple == ("state0", "person0")
    assert "state state0, person person0" in witness.situation
    assert "rule yes permits; rule no forbids" in witness.situation
    assert check_witness(doc, "permitted", model(doc, relation=[["state0", "person0"]]),
                         ["state0", "person0"])
    with pytest.raises(VEError, match="wrong length or sort"):
        check_witness(doc, "permitted", model(doc, relation=[["state0", "person0"]]),
                      ["person0", "state0"])


def test_same_sign_overlap_is_not_conflict():
    env = environment({"permitted": permission()})
    doc = NormDocument(env, [rule("first", "permitted", True),
                             rule("second", "permitted", True)])
    witness = model(doc)
    assert doc.overlap_witnesses(witness) == (("first", "second", ("act0",)),)
    assert check_conflict(doc, prove=True).status == "CONFLICT-FREE"


def test_lower_permission_guard_and_exhausted_budget():
    env = environment({"required": obligation(), "permitted": permission()})
    guarded = rule("must", "required", True, Unary("permitted", Var(0)))
    with_permission = NormDocument(env, [rule("may", "permitted", True), guarded])
    without_permission = NormDocument(env, [guarded])
    assert with_permission.order == ("permitted", "required")
    assert check_conflict(with_permission, prove=True).status == "CONFLICT-FREE"
    assert check_conflict(without_permission, prove=True).status == "CONFLICT-FREE"
    assert value(with_permission, "required", ("act0",), model(with_permission))
    assert not value(without_permission, "required", ("act0",), model(without_permission))
    exhausted = check_conflict(with_permission, model=model(with_permission), max_evaluations=0)
    assert (exhausted.status, exhausted.detail) == ("UNKNOWN", "MAX_EVALUATIONS")


def test_precedence_across_predicates_rejected():
    env = environment({"permitted": permission(),
                       "required": obligation(dual="permitted")})
    with pytest.raises(VEError, match="PrecedenceAcrossPredicates"):
        NormDocument(env, [rule("ban", "permitted", False),
                           rule("duty", "required", True, over=("ban",))])


def test_cycles_duals_and_profile_model():
    env = environment({"permitted": permission()})
    with pytest.raises(VEError, match="DependencyCycle: permitted"):
        NormDocument(env, [rule("self", "permitted", True, Not(Unary("permitted", Var(0))))])
    with pytest.raises(VEError, match="DependencyCycle"):
        NormDocument(env, [rule("a", "permitted", True, over=("b",)),
                           rule("b", "permitted", False, over=("a",))])
    with pytest.raises(VEError, match="MissingPermissionDual"):
        environment({"required": obligation(dual=None), "permitted": permission()})
    with pytest.raises(VEError, match="DualActMismatch"):
        environment({"required": obligation(act="{0} enter"),
                     "permitted": permission(act="{0} leave")})
    env = environment({"required": obligation(), "permitted": permission()})
    assert len([p for p in background(env) if p.generator == "profile"]) == 1
    with pytest.raises(InvalidModel, match="required relation"):
        FiniteModel.from_dict(env, {"complete": True, "domains": {"act": ["a"]},
                                    "constants": {},
                                    "relations": {"required": [["a"]], "permitted": []}})
