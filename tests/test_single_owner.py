"""A differential never compares an engine with itself (lean-first batch 15b, review B2).

Python has no search since batch 15b: `find_countermodel` runs Rust's under every authority. Shadow records
and three-way tests that compared "Python" with Rust there compared Rust with Rust and could not fail. One
table names the single-owner operations (`dispatch.SINGLE_OWNER`); `execute` refuses them and any pair of
identical implementations, `owned` runs them, and the differential harnesses read the same table.
"""
from __future__ import annotations

import pytest

from conformance import three_way
from tools import difffuzz
from tools import difffuzz_corpus as corpus
from ve.backends import dispatch


def test_execute_refuses_a_comparison_of_one_implementation_with_itself():
    def run():
        return 1
    for op in dispatch.SINGLE_OWNER:
        with pytest.raises(ValueError, match="one implementation"):
            dispatch.execute(op, {}, lambda: 1, lean=lambda: 2)
    with pytest.raises(ValueError, match="one implementation"):
        dispatch.execute("evaluate", {}, run, lean=run)
    with pytest.raises(ValueError, match="one implementation"):
        dispatch.execute("evaluate", {}, run, rust=run)
    with pytest.raises(ValueError, match="not a single-owner"):
        dispatch.owned("evaluate", run)


RUST_OWNED = sorted(op for op, engine in dispatch.SINGLE_OWNER.items() if engine == "rust")
SELECTIONS = ["python", "lean", "rust-experimental", "shadow"]


def test_the_lean_owned_operations_are_the_single_owner_table_s_lean_rows():
    """Lean-first batch 13b: the core operations are Lean's, and the table names no other engine."""
    assert {op for op, engine in dispatch.SINGLE_OWNER.items() if engine == "lean"} == dispatch.LEAN_OWNED
    assert set(dispatch.SINGLE_OWNER.values()) == {"lean", "rust"}
    assert RUST_OWNED == ["countermodel_search", "distinguishing_model"]


@pytest.mark.parametrize("op", sorted(dispatch.SINGLE_OWNER))
def test_single_owner_operations_write_no_shadow_record(op, monkeypatch, tmp_path):
    log = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    seen = []
    monkeypatch.setattr(dispatch, "observers", [lambda name, authority: seen.append((name, authority))])
    assert dispatch.owned(op, lambda: "answer") == "answer"
    expected = "lean" if op in dispatch.LEAN_OWNED else "shadow"
    assert seen == [(op, expected)] and not log.exists()


@pytest.mark.parametrize("op", sorted(dispatch.LEAN_OWNED))
@pytest.mark.parametrize("selected", SELECTIONS)
def test_a_lean_owned_operation_is_lean_s_under_every_selection(op, selected, monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", selected)
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", f"{op}={selected},countermodel_check=python")
    seen = []
    monkeypatch.setattr(dispatch, "observers", [lambda name, authority: seen.append((name, authority))])

    def run():
        # Its constituents run on Lean: a composing rule reads Lean-checked parts only.
        assert dispatch.authority_for("countermodel_check") == "lean"
        return 7

    assert dispatch.owned(op, run) == 7
    assert seen == [(op, "lean")]
    assert dispatch.authority_for("countermodel_check") == "python"
    with pytest.raises(ValueError, match="one implementation"):
        dispatch.execute(op, {}, lambda: 1, lean=lambda: 2)


@pytest.mark.parametrize("op", RUST_OWNED)
@pytest.mark.parametrize("selected", SELECTIONS)
def test_single_owner_pins_constituents_and_restores_selection(op, selected, monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "python")
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", f"{op}={selected},countermodel_check=rust-experimental")
    expected = "python" if selected == "shadow" else selected

    def run():
        assert dispatch.authority_for("countermodel_check") == expected
        return 7

    assert dispatch.owned(op, run) == 7
    assert dispatch.authority_for("countermodel_check") == "rust-experimental"
    with pytest.raises(RuntimeError, match="owner failed"):
        dispatch.owned(op, lambda: (_ for _ in ()).throw(RuntimeError("owner failed")))
    assert dispatch.authority_for("countermodel_check") == "rust-experimental"


def _reached(case):
    """The single-owner operations `python_verdict` dispatches for `case`."""
    seen = []
    original = dispatch.observers
    dispatch.observers = [lambda name, authority: seen.append(name)]
    try:
        three_way.python_verdict(case)
    finally:
        dispatch.observers = original
    return {op for op in seen if op in dispatch.SINGLE_OWNER}


def test_every_request_kind_reaching_a_single_owner_is_classified():
    by_kind = {}
    for _, kind, case, _ in corpus.requests():
        by_kind.setdefault(kind, []).append(case)
    assert set(difffuzz.REQUEST_VALUES) <= set(by_kind)
    reaching = {kind for kind, cases in by_kind.items()
                if any(_reached(case) for case in cases[:8])}
    assert "search" in reaching
    assert reaching == set(three_way.KIND_OPERATIONS) | set(three_way.KIND_COMPOSED) & reaching
    for kind in three_way.KIND_OPERATIONS:
        assert three_way.python_owner(kind) == dispatch.SINGLE_OWNER[three_way.KIND_OPERATIONS[kind]]


def test_difffuzz_never_compares_a_single_owner_value_with_its_owner():
    surface = difffuzz.Requests()
    seeds = surface.seeds()
    assert any(three_way.python_owner(seed.meta["kind"]) for seed in seeds)
    for seed in seeds:
        owner = three_way.python_owner(seed.meta["kind"])
        compared = surface.value_compared(seed, "python")
        assert compared is (owner is None or owner not in seed.engines), seed.id
        if owner is not None:
            assert owner in seed.engines and not compared, seed.id
