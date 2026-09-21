import difflib

from ve_experiments.e1 import build
from ve_experiments.e1.pilot import HIDDEN, to_items
from ve_experiments.e1.prompts import cell_name, conditions, e1b_prompt, judge_prompt
from ve_experiments.e1.views import VIEWS, render


def dev_candidates(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "OUT", tmp_path)
    cands = build.build("dev", use_llm=False)
    for c in cands:
        c["explanation"] = "Explanation text."
    return cands


def test_candidates_are_valid_and_blind(tmp_path, monkeypatch):
    cands = dev_candidates(tmp_path, monkeypatch)
    assert len({c["id"] for c in cands}) == len(cands)
    from ve_experiments.e1 import attacks as A

    for c in cands:
        faithful = next(x for x in cands if x["group"] == c["group"] and x["kind"] == "faithful:canonical")["ast"]
        if c["label"] == "bad":
            m = c["distinguishing_model"]
            assert A.evaluate(c["ast"], m) != A.evaluate(faithful, m)
            assert A.symbols(c["ast"]) == A.symbols(faithful)
            assert render(c["environment"], c["ast"], "ve_strict") != render(c["environment"], faithful, "ve_strict")
        assert [A.evaluate(c["ast"], m) for m in c["e1b_models"]] == c["e1b_truth"]
    # every dev base item has good and bad candidates, and several attack families
    fams = {c.get("family_of_attack") for c in cands if c["label"] == "bad"}
    assert {"quantifier_swap", "dropped_conjunct", "argument_reversal", "weakened_exception", "vacuous_domain",
            "and_or_swap", "implication_reversal"} <= fams  # fmt: skip


def test_cells_differ_only_in_the_rendered_statement(tmp_path, monkeypatch):
    c = dev_candidates(tmp_path, monkeypatch)[5]
    prompts = {v: judge_prompt(c, v, "attacker") for v in VIEWS}
    for v in VIEWS:
        statement = render(c["environment"], c["ast"], v)
        assert prompts[v].count(statement) == 1
        assert prompts[v].replace(statement, "<S>") == prompts["fol_symbols"].replace(render(c["environment"], c["ast"], "fol_symbols"), "<S>")
    with_expl, without = judge_prompt(c, "ve_strict", "attacker"), judge_prompt(c, "ve_strict", "none")
    added = [d for d in difflib.ndiff(without.splitlines(), with_expl.splitlines()) if d.startswith(("+", "-"))]
    assert all(d.startswith("+") for d in added) and any("Explanation text." in d for d in added)


def test_hidden_fields_never_reach_a_prompt(tmp_path, monkeypatch):
    cands = dev_candidates(tmp_path, monkeypatch)
    items = to_items(cands)
    for it in items[:20]:
        visible = it.visible()
        assert not set(visible) & set(HIDDEN) and "label" not in visible
        for cond in conditions():
            p = cond.build_prompt(visible)
            assert it.id not in p and "faithful:" not in p and "mech:" not in p
    assert cell_name("ve_strict", "attacker") in {c.name for c in conditions()}
    assert "Situation 2" in e1b_prompt(cands[0], "ve_natural")
