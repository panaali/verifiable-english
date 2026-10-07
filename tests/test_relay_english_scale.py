"""lf-10bc recheck: the 60-act reached-default repro renders from Lean's report line.

`x_permitted` denies by default; one rule permits it when ∃y∃z∃w(¬link(x,y) ∧ ¬link(z,w) ∧
link(w,x)). With `link` empty and 60 acts, Lean reports `reachable` at a0; the English used
to evaluate the default itself under a 1,000,000-step limit and raised. It now formats Lean's
line (its witness tuple and completed `value`).

This module is not one of wire-contract-s5 7.1's recorded globs (`tests/test_norm*`,
`tests/test_*contract*`): its source is not in batch 10b's norm-defaults differential corpus,
which the batch's fuzzer-gate evidence compares with the base, so it is listed for the next
corpus refresh (docs/lean-first/b10b/DELTA.md).
"""
from tests.test_norm_defaults import environment, permission, rule
from tests.test_norm_defaults_relay_english import render_cpu_bounded
from ve.ast import And, Binary, Exists, Not, Var
from ve.norm_defaults import UnspecifiedDocument, report


def _link_document():
    env = environment({"link": {"arguments": ["act", "act"], "description": "link"},
                       "x_permitted": permission("deny")})
    guard = Exists("act", Exists("act", Exists("act", And(Not(Binary("link", Var(3), Var(2))), And(
        Not(Binary("link", Var(1), Var(0))), Binary("link", Var(0), Var(3)))))))
    return UnspecifiedDocument(env, [rule("permit-x", "x_permitted", True, guard)])


def test_sixty_act_gap_renders_lean_reachable_witness():
    document = _link_document()
    raw = {"complete": True, "domains": {"act": [f"a{i}" for i in range(60)]}, "constants": {},
           "relations": {"link": []}}
    (line,) = report(document, model=raw)["report"]
    assert (line["reached"], line["witness"]["tuple"], line["value"]) == ("reachable", ["a0"], "no")
    (sentence,) = render_cpu_bounded(document, raw, line, ("gap_sentence",))
    assert sentence == "No rule decides whether a0 may be done; the default decides that a0 must not be done."
