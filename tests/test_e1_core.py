import random

import pytest

from ve_experiments.e1 import attacks as A
from ve_experiments.e1.templates import BY_ID, DEV_TEMPLATES, SCORED_TEMPLATES, TEMPLATES, to_wire
from ve_experiments.e1.views import VIEWS, check, legend, render
from ve_experiments.e1.vocab import BINDINGS, DEV_FAMILIES, SCORED_FAMILIES

CASES = [(t, v) for t in TEMPLATES for v in BINDINGS]


@pytest.mark.parametrize("t,v", CASES, ids=lambda x: getattr(x, "id", getattr(x, "name", "")))
def test_every_template_type_checks_and_renders_in_all_views(t, v):
    env, f = v.environment(), to_wire(t.formula(v))
    texts = {view: render(env, f, view) for view in VIEWS}
    assert len(VIEWS) == 5 and len(set(texts.values())) >= 4
    assert legend(env)  # raises if the legend differs between views
    assert t.prose(v) and "{" not in t.prose(v)


def test_splits_are_disjoint_and_cover_everything():
    assert not set(DEV_TEMPLATES) & set(SCORED_TEMPLATES) and not set(DEV_FAMILIES) & set(SCORED_FAMILIES)
    assert set(DEV_TEMPLATES) | set(SCORED_TEMPLATES) == set(BY_ID)
    assert {v.family for v in BINDINGS} == set(DEV_FAMILIES) | set(SCORED_FAMILIES)


def test_quantifier_swap_through_implication_is_the_intended_formula():
    v = BINDINGS[0]
    f = to_wire(BY_ID["t01_each_has_some"].formula(v))
    swaps = [g for k, _, g in A.mechanical_attacks(f) if k == "quantifier_swap"]
    assert swaps == [to_wire(BY_ID["t02_one_for_all"].formula(v))]
    back = [g for k, _, g in A.mechanical_attacks(swaps[0]) if k == "quantifier_swap"]
    # exists b forall a (P(a) -> R(b,a))  ->  forall a exists b (P(a) -> R(b,a))
    assert back == [["forall", "service", ["exists", "engineer", ["implies", ["unary", "deployed", ["var", 1]], ["binary", "maintains", ["var", 0], ["var", 1]]]]]]


@pytest.mark.parametrize("t,v", [(t, BINDINGS[i % len(BINDINGS)]) for i, t in enumerate(TEMPLATES)], ids=lambda x: getattr(x, "id", ""))
def test_attacks_are_distinguished_and_rewrites_are_not(t, v):
    env, f = v.environment(), to_wire(t.formula(v))
    kinds = set()
    for kind, _, g in A.mechanical_attacks(f):
        try:
            check(env, g)
        except Exception:
            assert kind == "argument_reversal"  # only ill-sorted reversals may fail
            continue
        cmp = A.compare(f, g, env["vocabulary"], seed="t")
        if cmp["model"] is not None:
            assert A.evaluate(f, cmp["model"]) != A.evaluate(g, cmp["model"])
            kinds.add(kind)
    assert kinds, "every template needs at least one valid mechanical attack"
    for name, g in A.equivalent_rewrites(f):
        check(env, g)
        assert A.compare(f, g, env["vocabulary"], seed="r", n=300)["model"] is None, name


def test_direction_labels():
    v = BINDINGS[0]
    env = v.environment()
    f = to_wire(BY_ID["t04_some_and_all"].formula(v))
    assert A.compare(f, f[2], env["vocabulary"], "d")["direction"] == "weaker"  # existence conjunct dropped
    assert A.compare(f[2], f, env["vocabulary"], "d")["direction"] == "stronger"


def test_random_models_have_unique_ids_across_sorts():
    for v in BINDINGS:
        m = A.random_model(v.environment()["vocabulary"], random.Random(1))
        ids = [x for d in m["domains"].values() for x in d]
        assert len(ids) == len(set(ids))
