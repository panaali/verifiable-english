"""EXP-G1's fixture checks can fail: each mutant in `experiments/exp-g1/run.py` is caught by the check it names.

Review F1 (exp-g1): "the conclusion needs both packs" was backed by `!certOK … [weighingC] (certAt 0 0)` and the same
for attitudes, which refuse whatever the packs say (with one pack, the trace's index 2 is out of range). The claim is
now `single_pack_refuted`, a model of each pack's `X` alone where the conclusion fails, and `run.py` plants a pack that
alone entails the conclusion, once per pack and once as the review's probe. This test elaborates the scratch file and
every mutant of `run.py`'s table with `run.py`'s own planting and verdict, and checks the saved evidence against the
same table.
"""
from __future__ import annotations

from functools import partial
import importlib.util
import json
import shutil
import subprocess

import pytest

import lean_pool
from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, ROOT, lean_build

_SPEC = importlib.util.spec_from_file_location("exp_g1_run", ROOT / "experiments/exp-g1/run.py")
run = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(run)

NAMES = [m[0] for m in run.MUTANTS]
TESTS = {m[0]: m[4] for m in run.MUTANTS}
SINGLE_PACK = {"weighing-alone-entails", "attitudes-alone-entails", "review-probe-F1"}


@pytest.fixture(scope="module")
def lake():
    path = shutil.which("lake")
    if path is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    return path


def _elaborate(lake: str, tmp_path, source: str) -> subprocess.CompletedProcess:
    file = tmp_path / "ExpG1.lean"
    file.write_text(source)
    return subprocess.run([lake, "env", "lean", str(file)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)


def _unmutated() -> str:
    return run.SRC.read_text()


def _mutant(name: str) -> str:
    return run.mutant(_unmutated(), name)


SOURCES = {"test_the_scratch_file_elaborates_cleanly": _unmutated, "test_every_mutant_is_caught_by_its_check": _mutant}


@pytest.fixture(scope="module")
def elaborated(lake, request, tmp_path_factory):
    return lean_pool.elaborate_selected(request, SOURCES, partial(_elaborate, lake),
                                        lambda: tmp_path_factory.mktemp("exp-g1-pool"))


@pytest.fixture
def elaborate(lake, elaborated):
    return lambda tmp_path, source: lean_pool.result(elaborated, source, lambda: _elaborate(lake, tmp_path, source))


def test_the_scratch_file_elaborates_cleanly(elaborate, tmp_path):
    done = elaborate(tmp_path, _unmutated())
    out = done.stdout + done.stderr
    assert done.returncode == 0 and "error" not in out and "sorryAx" not in out, out[:4000]
    assert "'ExpG1.single_pack_refuted' depends on axioms" in out


@pytest.mark.parametrize("name", NAMES)
def test_every_mutant_is_caught_by_its_check(elaborate, tmp_path, name):
    source = _mutant(name)
    assert source != _unmutated(), f"{name} changes nothing"
    done = elaborate(tmp_path, source)
    caught, failing = run.verdict(source, done.returncode, done.stdout + done.stderr, TESTS[name])
    assert caught, f"{name} survives {TESTS[name]!r}; failing: {failing}"


def test_each_pack_alone_has_a_mutant_that_entails_the_conclusion():
    """F1's class: a claim that a check refutes needs a mutant where the claim is false, aimed at that check."""
    assert SINGLE_PACK <= set(NAMES)
    assert {TESTS[n] for n in SINGLE_PACK} == {"theorem single_pack_refuted"}


def test_the_verdict_needs_the_named_check_to_fail():
    source = "def a : Nat := 1\n#guard a == 1\ntheorem t : True := trivial\n"
    guard_error = "/tmp/ExpG1.lean:2:0: error: Expression\n"
    assert run.verdict(source, 1, guard_error, "#guard a")[0]
    assert not run.verdict(source, 1, guard_error, "theorem t")[0], "a failure elsewhere does not catch it"
    assert not run.verdict(source, 0, "", "#guard a")[0], "a mutant that compiles survives"
    assert not run.verdict(source, 1, "", "#guard a")[0], "no located error, no catch"


def test_the_saved_evidence_is_the_runner_table_all_caught():
    rows = json.loads((run.OUT / "mutants.json").read_text())
    assert [r["name"] for r in rows] == NAMES
    for r in rows:
        assert r["test"] == TESTS[r["name"]] and r["rc"] != 0 and r["caught"] is True, r
    head = (run.OUT / "lean-run.txt").read_text().splitlines()
    assert head[1] == "rc=0" and not any("sorryAx" in line or ": error" in line for line in head)
    assert any(line.startswith("'ExpG1.single_pack_refuted' depends on axioms") for line in head)
