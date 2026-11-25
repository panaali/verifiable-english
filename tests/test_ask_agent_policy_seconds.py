"""`ve ask` on the 26-rule agent policy answers in seconds (backlog row ask-agent-policy-seconds).

Before this change the untrusted tableau search (`ve.entailment._Searcher`) memoised its search keys with
`functools.lru_cache`, which hashes the whole formula on every lookup; on the agent-policy documents (55 background
premises, deep guards) the search spent nearly all its time hashing (about 119 000 formula-node hashes per search
step) and `ve ask a-rules.ve.md "May every action be performed?"` gave no answer in 600 s. The memos are now keyed by
identity (`_IdentityMemo`), and the closing check buckets formulas by a memoised hash (about 140 hashes per step).
These tests pin that work, not a time (speed is measured outside the suite: reviews of the row record the seconds),
and that the search makes the same choices as the equality-keyed memos it replaced: the change is speed only, so no
answer changes.
"""
from __future__ import annotations

import dataclasses
from functools import lru_cache
from pathlib import Path

from hypothesis import given, settings, strategies as st

import ve.ast as A
from ve import entailment as E
from tests.test_ask_cli import cli
from tests.test_entailment_properties import ENV, formula

ROOT = Path(__file__).resolve().parents[1]
A_RULES = ROOT / "usecases/question-answering/agent-policy/a-rules.ve.md"


class _Recording(E._Searcher):
    """The searcher with every visited node recorded, in visit order: its depth and a copy of its branch."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visits = []

    def search(self, branch, depth=0):
        self.visits.append((depth, branch.copy()))
        return super().search(branch, depth)


class _Reference(_Recording):
    """The searcher with the memos it had before: equality-keyed `lru_cache`s and the plain `hash`."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance_key = lru_cache(maxsize=4096)(E._instance_key)
        self.connection_key = lru_cache(maxsize=4096)(E._connection_key)
        self.ground_connections = lru_cache(maxsize=4096)(E._ground_connections)
        self.formula_hash = hash


def _run(cls, env, premises, conclusion, steps):
    searcher = cls(steps, env.closure, env=env)
    try:
        outcome = ("trace", searcher.prove(E._initial_branch(env, premises, conclusion)))
    except (E._Budget, RecursionError) as error:
        outcome = ("stopped", type(error).__name__)
    return outcome, searcher.steps, searcher.visits


def _same_search(env, premises, conclusion, steps):
    """The new memos and the old ones visit the same branches in the same order and end the same way; on every
    visited branch the bucketed closing check agrees with the plain equality test (one bucket for every formula)."""
    new = _run(_Recording, env, premises, conclusion, steps)
    old = _run(_Reference, env, premises, conclusion, steps)
    assert new[0] == old[0] and new[1] == old[1]
    assert new[2] == old[2]
    memo = E._IdentityMemo(hash)
    for _, branch in new[2]:
        assert E._closed(branch, memo) == E._closed(branch, hash) == E._closed(branch, lambda f: 0)


def _a_rules_packages():
    """The two conflict-package searches of a-rules, as `_FilledChoiceDocument._packages` sets them up."""
    from ve.ask import _zero_generator
    from ve.ast import Not
    from ve.document import load_document
    from ve.norms import _bind
    gen = _zero_generator(load_document(A_RULES))
    fill = gen._base_fill()
    assert [target for target, _, _ in gen.targets] == ["permitted", "report_required"]
    for _, sorts, target_formula in gen.targets:
        conclusion = _bind(Not(target_formula), sorts)
        yield gen.base, E._validate_inputs(gen.base, fill, conclusion, background=False), conclusion


@given(st.lists(formula(), max_size=3), formula())
@settings(max_examples=150, deadline=None)
def test_identity_memos_make_the_same_search_as_equality_memos(premises, conclusion):
    """Same visits in the same order, same steps, same trace or the same stop, on random small problems."""
    premises = E._validate_inputs(ENV, premises, conclusion)
    _same_search(ENV, premises, conclusion, 400)


def test_identity_memos_make_the_same_search_on_the_agent_policy_packages():
    """The conflict-package searches of a-rules (the large premises the change is for), both targets: the same
    visits, steps and outcome within a budget small enough for the old memos to finish."""
    for env, premises, conclusion in _a_rules_packages():
        _same_search(env, premises, conclusion, 150)


def test_the_search_does_not_rehash_whole_formulas_per_step(monkeypatch):
    """The defect, measured as work rather than time: formula-node hashes per search step on the a-rules
    `permitted` package search. The old memos took about 119 000 per step, the identity memos about 140."""
    count = [0]
    for cls in vars(A).values():
        if isinstance(cls, type) and dataclasses.is_dataclass(cls) and cls.__module__ == A.__name__ \
                and cls.__hash__ is not None:
            def counted(self, _hash=cls.__hash__):
                count[0] += 1
                return _hash(self)
            monkeypatch.setattr(cls, "__hash__", counted)
    env, premises, conclusion = next(_a_rules_packages())
    searcher = E._Searcher(300, env.closure, env=env)
    count[0] = 0
    try:
        searcher.prove(E._initial_branch(env, premises, conclusion))
    except E._Budget:
        pass
    assert searcher.steps == 300
    assert count[0] / searcher.steps < 2_000, count[0] / searcher.steps


def test_identity_memo_returns_the_functions_value_across_hits_misses_and_clears():
    """A memo emptied at its limit still answers every call with the function's value, by identity or not."""
    def walk(item, *rest):
        return (E._instance_key(item), rest)
    memo = E._IdentityMemo(walk, signed=True, limit=2)
    f, g = A.Unary("p", A.Var(0)), A.Unary("q", A.Var(0))
    items = [E._Signed(f, True, ("c:a",)), E._Signed(f, True, ("c:b",)), E._Signed(g, False, ("c:a",)),
             E._Signed(f, True, ("c:a",)), E._Signed(A.Unary("p", A.Var(0)), True, ("c:a",))]
    for item in items * 2:
        assert memo(item) == walk(item) and memo(item, True) == walk(item, True)
    assert len(memo.entries) <= 2


def test_closed_buckets_by_hash_but_closes_only_on_equal_formulas():
    """A memoised hash that puts two different formulas in one bucket does not close the branch."""
    a, b = A.Unary("p", A.Const("x")), A.Unary("q", A.Const("x"))
    branch = E._Branch([E._Signed(a, True), E._Signed(b, False)], {"c:x": "item"}, set(), set())
    assert not E._closed(branch, lambda f: 0)
    branch.formulas.append(E._Signed(a, False))
    assert E._closed(branch, lambda f: 0)


def test_ve_ask_answers_the_26_rule_agent_policy():
    """The question the row names gets Lean's answer (no time bound here: the default hang guard only): VE could
    not decide, and says why (the conflict check of the rules is not found within the search budget)."""
    done = cli(A_RULES, "May every action be performed?")
    assert done.returncode == 3, (done.stdout, done.stderr)
    assert done.stdout.splitlines() == ["You asked whether every action may be performed.",
                                        "VE could not decide this.",
                                        "VE could not check that the rules never contradict each other."]
