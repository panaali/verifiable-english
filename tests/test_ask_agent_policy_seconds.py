"""`ve ask` on the 26-rule agent policy answers in seconds (backlog row ask-agent-policy-seconds).

Before this change the untrusted tableau search (`ve.entailment._Searcher`) memoised its search keys with
`functools.lru_cache`, which hashes the whole formula on every lookup; on the agent-policy documents (55 background
premises, deep guards) the search spent nearly all its time hashing and `ve ask a-rules.ve.md "May every action be
performed?"` gave no answer in 600 s. The memos are now keyed by identity (`_IdentityMemo`), and the closing check
buckets formulas by a memoised hash. These tests pin the time bound and that the search makes the same choices as
the equality-keyed memos it replaced: the change is speed only, so no answer changes.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from hypothesis import given, settings, strategies as st

from ve import entailment as E
from tests.test_ask_cli import cli
from tests.test_entailment_properties import ENV, formula

ROOT = Path(__file__).resolve().parents[1]
A_RULES = ROOT / "usecases/question-answering/agent-policy/a-rules.ve.md"
# Measured on the change: about 33 s on the VM; before it, no answer in 600 s.
A_RULES_BOUND = 150


class _Recording(E._Searcher):
    """The searcher with every visited node recorded: its depth, its branch's formulas and its expanded and
    instantiated sets, in visit order."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visits = []

    def search(self, branch, depth=0):
        self.visits.append((depth, tuple(branch.formulas), frozenset(branch.expanded),
                            frozenset(branch.instantiated)))
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
    new = _run(_Recording, env, premises, conclusion, steps)
    old = _run(_Reference, env, premises, conclusion, steps)
    assert new[0] == old[0] and new[1] == old[1]
    assert new[2] == old[2]


@given(st.lists(formula(), max_size=3), formula())
@settings(max_examples=150, deadline=None)
def test_identity_memos_make_the_same_search_as_equality_memos(premises, conclusion):
    """Same visits in the same order, same steps, same trace or the same stop, on random small problems."""
    premises = E._validate_inputs(ENV, premises, conclusion)
    _same_search(ENV, premises, conclusion, 400)


def test_identity_memos_make_the_same_search_on_the_agent_policy_packages():
    """The conflict-package searches of a-rules (the large premises the change is for), both targets: the same
    visits, steps and outcome within a budget small enough for the old memos to finish."""
    from ve.ask import _zero_generator
    from ve.ast import Not
    from ve.document import load_document
    from ve.norms import _bind
    gen = _zero_generator(load_document(A_RULES))
    fill = gen._base_fill()
    assert [target for target, _, _ in gen.targets] == ["permitted", "report_required"]
    for _, sorts, target_formula in gen.targets:
        conclusion = _bind(Not(target_formula), sorts)
        premises = E._validate_inputs(gen.base, fill, conclusion, background=False)
        _same_search(gen.base, premises, conclusion, 150)


def test_closed_buckets_by_hash_but_closes_only_on_equal_formulas():
    """A memoised hash that puts two different formulas in one bucket does not close the branch."""
    from ve.ast import Unary, Const
    a, b = Unary("p", Const("x")), Unary("q", Const("x"))
    branch = E._Branch([E._Signed(a, True), E._Signed(b, False)], {"c:x": "item"}, set(), set())
    assert not E._closed(branch, lambda f: 0)
    branch.formulas.append(E._Signed(a, False))
    assert E._closed(branch, lambda f: 0)


def test_ve_ask_answers_the_26_rule_agent_policy_in_seconds(monkeypatch):
    """The question the row names gets Lean's answer within the bound, not a hang: VE could not decide, and says
    why (the conflict check of the rules is not found within the search budget)."""
    monkeypatch.setenv("VE_ASK_CLI_TIMEOUT", str(A_RULES_BOUND))
    done = cli(A_RULES, "May every action be performed?")
    assert done.returncode == 3, (done.stdout, done.stderr)
    assert done.stdout.splitlines() == ["You asked whether every action may be performed.",
                                        "VE could not decide this.",
                                        "VE could not check that the rules never contradict each other."]
