"""tools/mutants.py, the seeded-mutant harness, on throwaway modules under tmp_path.

A mutant counts as killed only when a named test FAILS on it after passing without it; a surviving mutant,
a test that already fails, a collection error and a find text that is missing or ambiguous all fail the
harness; a command mutant is killed by a non-zero exit. The mutated file is restored to its exact bytes in
every case, including an exception inside the mutation. A mutant of the same length as the source, run within
the second of the baseline's import, still runs (Python's bytecode cache keys on size and mtime in seconds:
`x * 2` -> `x * 3` in the command test).
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mutants as M  # noqa: E402

MODULE = "def double(x):\n    return x * 2\n\n\ndef unused(x):\n    return x\n"
TESTS = "from mod import double\n\n\ndef test_double():\n    assert double(3) == 6\n\n\ndef test_other():\n    pass\n"


@pytest.fixture
def tree(tmp_path):
    (tmp_path / "mod.py").write_text(MODULE)
    (tmp_path / "test_mod.py").write_text(TESTS)
    return tmp_path


def run(tree, **mutant):
    before = (tree / "mod.py").read_bytes()
    row = M.run({"id": "M", "file": "mod.py", **mutant}, root=tree)
    assert (tree / "mod.py").read_bytes() == before
    return row


def test_a_mutant_the_named_test_catches_is_killed(tree):
    row = run(tree, find="x * 2", replace="x * 3", tests=["test_mod.py::test_double"])
    assert row["killed"] and row["killed_by"] == ["test_mod.py::test_double"]
    assert row["baseline_exit"] == 0 and row["mutant_exit"] == 1


def test_a_mutant_no_named_test_catches_survives(tree):
    row = run(tree, find="return x\n", replace="return x + 1\n", tests=["test_mod.py::test_double"])
    assert not row["killed"] and row["problem"] == "the mutant survives"
    # Another test failing is not a kill of the named one.
    row = run(tree, find="x * 2", replace="x * 3", tests=["test_mod.py::test_other"])
    assert not row["killed"]


def test_a_collection_error_is_not_a_kill(tree):
    row = run(tree, find="return x * 2", replace="return x *", tests=["test_mod.py::test_double"])
    assert not row["killed"] and row["mutant_exit"] != 1


def test_a_test_that_fails_without_the_mutant_proves_nothing(tree):
    (tree / "test_mod.py").write_text(TESTS.replace("== 6", "== 7"))
    row = run(tree, find="x * 2", replace="x * 3", tests=["test_mod.py::test_double"])
    assert not row["killed"] and row["problem"] == "the tests fail without the mutant"


@pytest.mark.parametrize("find", ["x * 5", "return x"])
def test_a_find_text_that_is_missing_or_ambiguous_is_refused(tree, find):
    with pytest.raises(M.MutantError, match="occurs [02] times"):
        run(tree, find=find, replace="0", tests=["test_mod.py::test_double"])


def test_a_command_mutant_is_killed_by_a_non_zero_exit(tree):
    check = ["python", "-c", "import sys; sys.path.insert(0, '.'); from mod import double; "
                             "sys.exit(double(3) != 6)"]
    assert run(tree, find="x * 2", replace="x * 3", command=check)["killed"]
    assert not run(tree, find="return x\n", replace="return x + 1\n", command=check)["killed"]
    with pytest.raises(M.MutantError, match="either tests or a command"):
        run(tree, find="x * 2", replace="x * 3", command=check, tests=["test_mod.py::test_double"])


def test_the_file_is_restored_when_the_run_raises(tree):
    before = (tree / "mod.py").read_bytes()
    with pytest.raises(RuntimeError):
        with M.applied(tree / "mod.py", "x * 2", "x * 3"):
            assert "x * 3" in (tree / "mod.py").read_text()
            raise RuntimeError
    assert (tree / "mod.py").read_bytes() == before


def test_a_mutated_file_never_keeps_its_mtime_and_gets_it_back(tree):
    """Python reuses a .pyc whose source has the same size and whole-second mtime; the mutant moves it."""
    path = tree / "mod.py"
    before = path.stat()
    with M.applied(path, "x * 2", "x * 3"):
        assert int(path.stat().st_mtime) != int(before.st_mtime)
    assert path.stat().st_mtime_ns == before.st_mtime_ns


def test_main_fails_on_a_survivor_and_writes_evidence(tree, tmp_path, monkeypatch):
    monkeypatch.setattr(M, "ROOT", tree)
    monkeypatch.setattr(M.run, "__defaults__", (True, tree))
    spec = tmp_path / "mutants.json"
    evidence = tmp_path / "evidence.json"
    killed = {"id": "K", "file": "mod.py", "find": "x * 2", "replace": "x * 3", "tests": ["test_mod.py::test_double"]}
    survivor = {"id": "S", "file": "mod.py", "find": "return x\n", "replace": "return x + 1\n",
                "tests": ["test_mod.py::test_double"]}
    spec.write_text(json.dumps({"mutants": [killed]}))
    assert M.main([str(spec), "--evidence", str(evidence)]) == 0
    assert [row["killed"] for row in json.loads(evidence.read_text())["mutants"]] == [True]
    spec.write_text(json.dumps({"mutants": [killed, survivor]}))
    assert M.main([str(spec)]) == 1
    assert M.main([str(spec), "--id", "K"]) == 0
    spec.write_text(json.dumps({"mutants": []}))
    assert M.main([str(spec)]) == 1  # nothing ran: no evidence of anything
