import pytest
from ve import Environment, parse
from experiments.E2E4.fol import FOLRenderError, render_formula, render_sequent

P=["unary","p",["const","a"]]
Q=["unary","q",["const","a"]]
R=["unary","r",["const","a"]]

def test_invalid_edge_keeps_rule_consequent_distinct_from_conclusion():
    shown=render_sequent([P,["implies",P,Q]],R)
    assert shown=="p(a), (p(a) -> q(a)) |- r(a)"
    assert "p(a) -> r(a)" not in shown

def test_accepts_formula_objects_directly():
    env=Environment.from_dict({"language":"ve.core@0","profile":"relational-fol@0","spec_revision":"ve-v0-draft-2026-09-20","vocabulary":{
        "sorts":{"thing":{"description":"Things"}},"predicates":{"p":{"arguments":["thing"],"description":"P"}},
        "constants":{"a":{"sort":"thing","description":"a"}}}})
    formula=parse(env,"if (@a is p), then (not (@a is p)).\n").formulas[0]
    assert render_formula(formula)=="(p(a) -> not (p(a)))"

def test_covers_every_formula_to_data_constructor_deterministically():
    data=["forall","thing",["exists","thing",["and",
        ["binary","rel",["var",1],["var",0]],
        ["or",["not",["eq",["var",0],["const","a"]]],
              ["implies",["top"],["bottom"]]]]]]
    expected="(forall x0:thing. (exists x1:thing. (rel(x0, x1) and (not ((x1 = a)) or (true -> false)))))"
    assert render_formula(data)==expected
    assert render_formula(data)==expected

@pytest.mark.parametrize("bad", [[], ["var",0], ["unary","p"], ["mystery"]])
def test_rejects_malformed_or_nonformula_nodes(bad):
    with pytest.raises(FOLRenderError): render_formula(bad)
