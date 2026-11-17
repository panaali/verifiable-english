"""Taking several leaves out of a guard at once (tools/fidmech/structural.py `prune`; fid-mech-b4 review F1).

widen-quantifier dropped its restricting conjuncts one path at a time; each drop collapsed a parent, so the paths still
to drop pointed elsewhere: two restricting conjuncts crashed the document's run (AttributeError outside REFUSED) or,
where a stale path landed on an Or leaf, dropped the wrong subformula silently. `prune` reads every path on the
original tree in one walk and `drop` is its one-path case, so the class is checked here on every tree shape up to six
leaves and every subset of leaves, with Or nodes as leaves of the And tree.
"""
from __future__ import annotations

import itertools
import json
from dataclasses import replace
from pathlib import Path

import pytest

from tools.fidmech import structural as S
from ve import ast

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "data" / "fidmech"
needs_lean = pytest.mark.skipif(not (ROOT / "lean/.lake/build/bin/ve_service").exists(),
                                reason="the Lean service is not built")


def shapes(items, kind):
    """Every `kind` tree over `items` in order (every bracketing)."""
    if len(items) == 1:
        yield items[0]
        return
    for cut in range(1, len(items)):
        for left in shapes(items[:cut], kind):
            for right in shapes(items[cut:], kind):
                yield kind(left, right)


def atoms(n):
    """n distinct leaves; every third an Or (a leaf of the And tree whose own paths must never be followed)."""
    out = []
    for i in range(n):
        a = ast.Unary(f"p{i}", ast.Var(0))
        out.append(ast.Or(a, ast.Unary(f"q{i}", ast.Var(1))) if i % 3 == 2 else a)
    return out


def leaf_values(formula, kind):
    return [] if isinstance(formula, ast.Top) else [S.leaf(formula, p) for p in S.leaves(formula, kind)]


@pytest.mark.parametrize("n", range(1, 7))
def test_prune_keeps_exactly_the_other_leaves_in_order_for_every_shape_and_subset(n):
    for tree in shapes(atoms(n), ast.And):
        paths = S.leaves(tree, ast.And)
        assert len(paths) == n
        for k in range(n + 1):
            for gone in itertools.combinations(paths, k):
                pruned = S.prune(tree, gone)
                kept = [S.leaf(tree, p) for p in paths if p not in gone]
                assert leaf_values(pruned, ast.And) == kept, (tree, gone)
                assert isinstance(pruned, ast.Top) == (not kept)
                assert S.prune(tree, reversed(gone)) == pruned  # the order paths are named in is irrelevant


def test_drop_is_prune_of_one_path_on_and_and_or_trees():
    for kind in (ast.And, ast.Or):
        for tree in shapes(atoms(4), kind):
            for p in S.leaves(tree, kind):
                assert S.drop(tree, p) == S.prune(tree, (p,))
                assert leaf_values(S.drop(tree, p), kind) == [S.leaf(tree, q) for q in S.leaves(tree, kind) if q != p]


def test_the_reviewers_two_stale_path_shapes():
    """And(And(r, r), b) crashed; And(And(Or(r, r), b), r) dropped the Or's left half and kept the Or's right half
    (the old sequential drop): both must leave b alone."""
    r, b = ast.Unary("r", ast.Var(0)), ast.Binary("b", ast.Var(1), ast.Var(0))
    assert S.prune(ast.And(ast.And(r, r), b), [(0, 0), (0, 1)]) == b
    assert S.prune(ast.And(ast.And(ast.Or(r, r), b), r), [(0, 0), (1,)]) == b


# ---- through ops_of on a parsed rule (the parse asks Lean) ---------------------------------------------------------

def rows_cond():
    from ve.softnorms import SoftEnvironment
    env = SoftEnvironment(json.loads((DATA / "wording-inputs" / "anthropic-rsp" / S.ENVIRONMENT).read_text()))
    text = (DATA / "structural" / "anthropic-rsp" / S.RULES).read_text(encoding="utf-8")
    return env, S.parse(env, next(b.text for b in S.rule_blocks(text) if b.id == "rows-cond"))


def widened(rule, env, guard):
    edited = replace(rule, core=replace(rule.core, guard=guard))
    return [e.core.guard for op, _, e in S.ops_of(edited, env) if op == "widen-quantifier"]


@needs_lean
def test_probe_f1_two_restricting_conjuncts_are_dropped_together():
    env, rule = rows_cond()
    g = rule.core.guard
    assert widened(rule, env, ast.And(ast.And(g.left, g.left), g.right)) == [g.right]


@needs_lean
def test_widen_quantifier_keeps_exactly_the_non_restricting_conjuncts_on_every_shape():
    """rows-cond's guard is `listed(threshold) and crossed(situation, threshold)`; its first conjunct restricts the
    second variable alone. Every bracketing of up to five such conjuncts, an Or of restricting ones among them, keeps
    exactly the others in order, written back as a line that parses to the edit."""
    env, rule = rows_cond()
    g = rule.core.guard
    restrict, other, either = g.left, g.right, ast.Or(g.left, g.left)
    for n in range(2, 6):
        for pick in itertools.product((restrict, other, either), repeat=n):
            if other not in pick or pick.count(other) == n:
                continue
            for tree in shapes(list(pick), ast.And):
                (guard,) = widened(rule, env, tree)
                assert leaf_values(guard, ast.And) == [other] * pick.count(other), tree
    edited = replace(rule, core=replace(rule.core, guard=ast.And(ast.And(either, other), restrict)))
    (mutant,) = [e for op, _, e in S.ops_of(edited, env) if op == "widen-quantifier"]
    assert S.same_edit(mutant, S.parse(env, S.render(mutant, env)))
