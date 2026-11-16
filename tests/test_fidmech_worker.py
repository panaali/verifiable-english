"""fid-mech-b3: the isolated worker (plan section 6) on a toy use case, with no Lean.

The toy (tests/data/fidmech/worker/usecases/anthropic-rsp/run.py.txt) answers ALL only on a clean, freshly imported
module; a mutant, a use-case module global that survived the purge, or a leaked global outside usecases/ turns it
NONE. Deadlines are injected (a clock, a raised timeout), never waited out.
"""
from __future__ import annotations

import shutil
import sys
import types
from contextlib import nullcontext
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT
from tools.fidmech import worker as W

FIXTURE = Path(__file__).resolve().parent / "data" / "fidmech" / "worker"
RUN = "anthropic-rsp/run.py"
ORIGINAL = (FIXTURE / "usecases" / (RUN + ".txt")).read_text()
MUTANT = W.Mutant("m-toy", {RUN: ORIGINAL.replace("\nMUTATED = False\n", "\nMUTATED = True\n")})


@pytest.fixture
def toy(tmp_path):
    """The toy worktree: the fixture's usecases/ with run.py.txt as run.py (no .py file is kept under tests/data)."""
    root = tmp_path / "toy"
    shutil.copytree(FIXTURE, root)
    (root / "usecases" / (RUN + ".txt")).rename(root / "usecases" / RUN)
    return root


def toy_worker(tmp_path, **options):
    options.setdefault("fresh", False)
    return W.Worker("anthropic-rsp", tmp_path / "toy", tmp_path / "scratch", **options)


def answers(outcome):
    return outcome.projection.answers


def test_the_defaults_are_the_plans():
    assert (W.SENTINEL_EVERY, W.TIMEOUT_FACTOR) == (20, 10)
    assert W.DEFAULT_FRESH is True  # measured: a fresh process costs under 2x a warm run (REPORT section 4)


def test_a_mutant_runs_in_a_scratch_copy_and_the_module_is_purged_after(tmp_path, toy):
    worker = toy_worker(tmp_path)
    before = set(sys.modules)
    baseline, mutant, again = worker.run(W.BASELINE), worker.run(MUTANT, HANG_TIMEOUT), worker.run(W.BASELINE)
    assert answers(baseline)["Q1"] == (("ve", "ALL"),) == answers(again)["Q1"]
    assert answers(mutant)["Q1"] == (("ve", "NONE"),)
    assert baseline.projection.rules == {"Q1": ("r-toy",), "Q2": ()}
    assert baseline.projection.atoms == {"Q1": (("stated", "s", "c1"),), "Q2": ()}
    assert not {name for name in set(sys.modules) - before if name.startswith("fidmech_")}
    assert (tmp_path / "toy" / "usecases" / RUN).read_text() == ORIGINAL != MUTANT.edits[RUN]
    assert sys.path.count(str(tmp_path)) == 0 and not [p for p in sys.path if "scratch" in p]
    assert not (tmp_path / "scratch").exists() or not any((tmp_path / "scratch").iterdir())


def test_a_clean_batch_kills_the_mutant_and_every_sentinel_holds(tmp_path, toy):
    batch = W.run_batch(toy_worker(tmp_path), [MUTANT, W.Mutant("m-same")], sentinel_every=1)
    assert batch.status == "ok" and batch.sentinels == [True, True]
    assert {k: (o.status, o.sentinel_ok) for k, o in batch.outcomes.items()} == {"m-toy": ("ok", True),
                                                                               "m-same": ("ok", True)}
    assert answers(batch.outcomes["m-toy"])["Q1"] != answers(batch.baseline)["Q1"]


def test_a_leaked_module_global_makes_the_batch_invalid(tmp_path, toy, monkeypatch):
    """Plan 10 'sentinel' plant: the mutant sets a global of a module outside usecases/, which the purge cannot
    reach; every later baseline reads it, so each sentinel differs, the mutant is re-queued once and the batch is
    INVALID."""
    probe = types.ModuleType("fidmech_leak_probe")
    probe.STATE = {}
    monkeypatch.setitem(sys.modules, "fidmech_leak_probe", probe)
    batch = W.run_batch(toy_worker(tmp_path), [MUTANT], sentinel_every=1)
    assert probe.STATE == {"leaked": True}
    assert batch.status == "INVALID"
    assert batch.sentinels == [False, False]
    assert batch.outcomes["m-toy"].sentinel_ok is False


def test_a_sentinel_failure_requeues_each_result_since_the_last_good_one_once(tmp_path, toy):
    """A transient sentinel failure: the results since the last good sentinel run again and stand when the next
    sentinel holds."""
    script = iter(["base", "m1", "m2", "BAD", "m3", "m1", "base", "m2", "base"])
    calls = []

    def evaluate(mutant, limit):
        step = next(script)
        calls.append((mutant.id, step))
        return {"answer": "other" if step == "BAD" else "base" if mutant is W.BASELINE else mutant.id}

    worker = toy_worker(tmp_path, evaluate=evaluate)
    batch = W.run_batch(worker, [W.Mutant("m1"), W.Mutant("m2"), W.Mutant("m3")], sentinel_every=2)
    assert [c[0] for c in calls] == ["baseline", "m1", "m2", "baseline", "m3", "m1", "baseline", "m2", "baseline"]
    assert batch.sentinels == [False, True, True]
    assert batch.status == "ok"
    assert {k: o.sentinel_ok for k, o in batch.outcomes.items()} == {"m1": True, "m2": True, "m3": True}


def test_a_result_invalid_twice_stays_invalid_and_a_differing_last_baseline_fails_the_batch(tmp_path, toy):
    def evaluate(mutant, limit):
        return {"answer": "first" if worker.runs == 1 else "drifted"}

    worker = toy_worker(tmp_path, evaluate=evaluate)
    batch = W.run_batch(worker, [W.Mutant("m1")], sentinel_every=20)
    assert batch.status == "INVALID" and batch.sentinels == [False, False]
    assert batch.outcomes["m1"].sentinel_ok is False


class Clock:
    """An injected clock: each reading advances by the next step."""

    def __init__(self, *steps):
        self.now, self.steps = 0.0, list(steps)

    def __call__(self):
        self.now += self.steps.pop(0) if self.steps else 0.0
        return self.now


def test_a_run_past_ten_times_the_baseline_is_an_error(tmp_path, toy):
    # baseline: start 0, end 3 s (limit 30 s); the mutant: start, then 31 s later; the last sentinel: 3 s.
    clock = Clock(0, 3, 0, 31, 0, 3)
    worker = toy_worker(tmp_path, evaluate=lambda mutant, limit: {"answer": "base"}, clock=clock,
                        deadline=lambda seconds: nullcontext())
    batch = W.run_batch(worker, [W.Mutant("slow")])
    slow = batch.outcomes["slow"]
    assert (slow.status, slow.projection) == ("error", None)
    assert slow.error == "timeout: ran 31.0 s over the limit 30.0 s"
    assert batch.status == "ok" and batch.sentinels == [True]


def test_a_raised_timeout_is_an_error_and_resets_the_lean_pool(tmp_path, toy):
    resets = []

    def evaluate(mutant, limit):
        if mutant.id == "hung":
            raise W.MutantTimeout(f"ran over {limit:.0f} s")
        return {"answer": "base"}

    worker = toy_worker(tmp_path, evaluate=evaluate, reset=lambda: resets.append(True))
    batch = W.run_batch(worker, [W.Mutant("hung"), W.Mutant("fine")])
    assert batch.outcomes["hung"].status == "error" and batch.outcomes["hung"].error.startswith("timeout: ran over")
    assert batch.outcomes["fine"].status == "ok" and resets == [True] and batch.status == "ok"


def test_an_exception_or_a_system_exit_of_the_mutant_is_an_error(tmp_path, toy):
    def evaluate(mutant, limit):
        if mutant.id == "exit":
            raise SystemExit("case X has alternatives")
        if mutant.id == "boom":
            raise KeyError("K9")
        return {"answer": "base"}

    batch = W.run_batch(toy_worker(tmp_path, evaluate=evaluate), [W.Mutant("exit"), W.Mutant("boom")])
    assert {k: o.error for k, o in batch.outcomes.items()} == {"exit": "SystemExit: case X has alternatives",
                                                               "boom": "KeyError: 'K9'"}


def test_the_real_alarm_raises_the_timeout_in_the_main_thread():
    with pytest.raises(W.MutantTimeout, match="ran over"):
        with W.alarm(HANG_TIMEOUT):
            W.signal.raise_signal(W.signal.SIGALRM)
    with W.alarm(None):
        pass


def test_a_fresh_process_gives_the_warm_projection(tmp_path, toy):
    fresh = toy_worker(tmp_path, fresh=True, name="fresh")
    warm = toy_worker(tmp_path, name="warm")
    for mutant in (W.BASELINE, MUTANT):
        assert fresh.run(mutant, HANG_TIMEOUT).projection == warm.run(mutant, HANG_TIMEOUT).projection


def test_an_edit_outside_the_tree_and_duplicate_mutant_ids_are_refused(tmp_path, toy):
    with pytest.raises(ValueError, match="outside usecases"):
        W.scratch_tree(tmp_path / "toy", tmp_path / "s", {"../escape.py": "x"})
    with pytest.raises(ValueError, match="not unique"):
        W.run_batch(toy_worker(tmp_path, evaluate=lambda m, limit: {}), [W.Mutant("a"), W.Mutant("a")])
    with pytest.raises(ValueError, match="no adapter"):
        W.Worker("toy", tmp_path / "toy", tmp_path)
