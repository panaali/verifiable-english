"""The pinned gate collection must be the gate's real collection, and a merge that
changes the tests without it must be named."""
from __future__ import annotations

import json
import os
import subprocess

import pytest

from tools import gate, gate_collection


def test_gate_baseline_is_the_gate_collection():
    # The merge train's verify runs this, so it fails on the merge that forgot
    # the baseline instead of the release gate failing later on main.
    collected = gate_collection.collect(prebuilt=True)
    expected = json.loads(gate.COLLECTION.read_text())
    added, removed = gate_collection.difference(expected, collected)
    assert not (added or removed), gate_collection.report(added, removed)
    assert gate.COLLECTION.read_text() == gate_collection.baseline_text(collected)


def git(root, *args):
    subprocess.run(["git", "-c", "user.name=VE test", "-c", "user.email=ve@example.invalid",
                    *args], cwd=root, check=True, capture_output=True)


@pytest.fixture
def repository(tmp_path):
    (tmp_path / "pytest.ini").write_text("[pytest]\n")
    (tmp_path / ".gitignore").write_text(".pytest_cache/\n__pycache__/\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_one.py").write_text("def test_kept(): pass\ndef test_dropped(): pass\n")
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "tests with their baseline")
    return tmp_path


def commit(root, files, message):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if text is None:
            path.unlink()
        else:
            path.write_text(text)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)


def merge(root, files, message="Merge feature (forgot the baseline)"):
    git(root, "checkout", "-q", "-b", "feature")
    commit(root, files, "feature tests")
    git(root, "checkout", "-q", "main")
    git(root, "merge", "-q", "--no-ff", "feature", "-m", message)
    git(root, "branch", "-q", "-d", "feature")


def assert_named(text, merge_name, added, removed):
    assert all(nodeid in text for nodeid in added + removed)
    lines = [line for line in text.splitlines() if line.startswith(("Collected", "Pinned"))]
    assert lines == ([f"Collected but not pinned, from {merge_name}: {len(added)}"] if added else []) + (
        [f"Pinned but not collected, from {merge_name}: {len(removed)}"] if removed else [])


def merged(root):
    found = subprocess.run(["git", "log", "-1", "--format=%h %s"], cwd=root,
                           check=True, capture_output=True, text=True)
    return found.stdout.strip()


def test_report_names_the_merge_that_changed_tests_without_the_baseline(repository):
    # compose-s1 merged 210 tests into main without them; the gate then
    # reported only counts and IDs, not where they came from.
    expected = gate_collection.collect(repository)
    assert expected == ["tests/test_one.py::test_kept", "tests/test_one.py::test_dropped"]
    merge(repository, {"tests/test_one.py": "def test_kept(): pass\n", "tests/test_two.py":
                       "import pytest\n@pytest.mark.parametrize('case', ['x', 'y'])\ndef test_new(case): pass\n"})
    added, removed = gate_collection.difference(expected, gate_collection.collect(repository))
    assert added == ["tests/test_two.py::test_new[x]", "tests/test_two.py::test_new[y]"]
    assert removed == ["tests/test_one.py::test_dropped"]
    text = gate_collection.report(added, removed, repository)
    assert_named(text, merged(repository), added, removed)


PARAMETRISED = ("import pytest\n@pytest.mark.parametrize('case', {cases})\n"
                "def test_new(case): pass\n")
# Each changes IDs without changing how often a test function's name occurs
# in its file, so the commit that brought the test in is not the one to name.
CHANGES = {
    "parameter": ({"tests/test_two.py": PARAMETRISED.format(cases=["x", "y"])},
                  {"tests/test_two.py": PARAMETRISED.format(cases=["x", "z"])},
                  ["tests/test_two.py::test_new[z]"], ["tests/test_two.py::test_new[y]"]),
    "class": ({"tests/test_two.py": "class TestOld:\n    def test_new(self): pass\n"},
              {"tests/test_two.py": "class TestNew:\n    def test_new(self): pass\n"},
              ["tests/test_two.py::TestNew::test_new"], ["tests/test_two.py::TestOld::test_new"]),
    "nested class": ({"tests/test_two.py": "class TestOuter:\n    class TestOld:\n"
                                           "        def test_new(self): pass\n"},
                     {"tests/test_two.py": "class TestOuter:\n    class TestNew:\n"
                                           "        def test_new(self): pass\n"},
                     ["tests/test_two.py::TestOuter::TestNew::test_new"],
                     ["tests/test_two.py::TestOuter::TestOld::test_new"]),
    "data file": ({"tests/test_two.py": "import pathlib, pytest\n"
                   "CASES = sorted(p.stem for p in (pathlib.Path(__file__).parent / 'cases').glob('*.txt'))\n"
                   "@pytest.mark.parametrize('case', CASES)\ndef test_new(case): pass\n",
                   "tests/cases/a.txt": "", "tests/cases/b.txt": ""},
                  {"tests/cases/b.txt": None, "tests/cases/c.txt": ""},
                  ["tests/test_two.py::test_new[c]"], ["tests/test_two.py::test_new[b]"]),
    "conftest fixture": ({"tests/conftest.py": "import pytest\n@pytest.fixture(params=['x', 'y'])\n"
                          "def case(request): return request.param\n",
                          "tests/test_two.py": "def test_new(case): pass\n"},
                         {"tests/conftest.py": "import pytest\n@pytest.fixture(params=['x', 'z'])\n"
                          "def case(request): return request.param\n"},
                         ["tests/test_two.py::test_new[z]"], ["tests/test_two.py::test_new[y]"]),
    "moved file": ({"tests/test_two.py": "def test_new(): pass\n"},
                   {"tests/test_two.py": None,
                    "tests/test_three.py": "def test_new(): pass\ndef test_later(): pass\n"},
                   ["tests/test_three.py::test_later", "tests/test_three.py::test_new"],
                   ["tests/test_two.py::test_later", "tests/test_two.py::test_new"]),
}


@pytest.mark.parametrize("change", CHANGES.values(), ids=CHANGES)
def test_report_names_the_merge_whatever_changed_the_ids(repository, change):
    # Found by looking up only the function's name, every one of these was
    # blamed on the commit pinning the test correctly, never on the merge.
    pinned, changed, added, removed = change
    commit(repository, pinned, "tests pinned with their baseline")
    # A later commit changing the same file, with its own baseline, is not named either.
    later = "def test_later(): pass\n"
    commit(repository, {"tests/test_two.py": (repository / "tests/test_two.py").read_text() + later},
           "a later test with its baseline")
    expected = gate_collection.collect(repository)
    merge(repository, {name: text + later if name == "tests/test_two.py" and text else text
                       for name, text in changed.items()})
    assert gate_collection.difference(expected, gate_collection.collect(repository)) == (added, removed)
    assert_named(gate_collection.report(added, removed, repository), merged(repository), added, removed)


def test_report_names_an_uncommitted_change_and_ids_never_collected(repository):
    expected = gate_collection.collect(repository) + ["tests/test_one.py::test_never"]
    (repository / "tests/test_one.py").write_text("def test_kept(): pass\ndef test_uncommitted(): pass\n")
    added, removed = gate_collection.difference(expected, gate_collection.collect(repository))
    assert added == ["tests/test_one.py::test_uncommitted"]
    assert removed == ["tests/test_one.py::test_dropped", "tests/test_one.py::test_never"]
    assert gate_collection.introduced_by(added, removed, repository) == {
        "tests/test_one.py::test_uncommitted": "no commit (an uncommitted change)",
        "tests/test_one.py::test_dropped": "no commit (an uncommitted change)",
        "tests/test_one.py::test_never": "no commit (never collected on first-parent history)"}


def test_report_names_the_root_commit_for_an_id_it_brought_in(repository):
    assert gate_collection.introduced_by(["tests/test_one.py::test_kept"], [], repository) == {
        "tests/test_one.py::test_kept": merged(repository)}


def test_report_does_not_take_a_shallow_clones_oldest_commit_for_the_root(repository, tmp_path_factory):
    merge(repository, {"tests/test_one.py": "def test_kept(): pass\ndef test_new(): pass\n"})
    clone = tmp_path_factory.mktemp("clone") / "repository"
    git(repository, "clone", "-q", "--depth", "1", repository.as_uri(), str(clone))
    assert gate_collection.introduced_by(["tests/test_one.py::test_kept"], [], clone) == {
        "tests/test_one.py::test_kept": "no commit in the shallow clone's history"}


def test_report_stops_at_a_commit_git_cannot_check_out(repository):
    root = merged(repository)
    merge(repository, {"tests/test_one.py": "def test_kept(): pass\ndef test_new(): pass\n"})
    blob = subprocess.run(["git", "rev-parse", "HEAD^1:tests/test_one.py"], cwd=repository,
                          check=True, capture_output=True, text=True).stdout.strip()
    (repository / ".git/objects" / blob[:2] / blob[2:]).unlink()
    assert gate_collection.introduced_by(["tests/test_one.py::test_kept"], [], repository) == {
        "tests/test_one.py::test_kept": f"no commit found ({root} could not be collected)"}


def test_report_stops_at_a_commit_it_cannot_collect(repository):
    # Its IDs there are unknown, so no older commit may be named instead.
    commit(repository, {"tests/test_one.py": "import ve_gate_absent_test_backend\n"}, "broken")
    broken = merged(repository)
    merge(repository, {"tests/test_one.py": "def test_kept(): pass\n"})
    assert gate_collection.introduced_by(["tests/test_one.py::test_kept"], [], repository) == {
        "tests/test_one.py::test_kept": f"no commit found ({broken} could not be collected)"}


def test_past_trees_are_collected_with_their_own_modules_and_without_toolchains(
        repository, tmp_path_factory, monkeypatch):
    # A tree's own `tools` package must not hide the gate's plugin, and an old
    # conftest that builds the backends must not find them to build with.
    toolchain = tmp_path_factory.mktemp("toolchain")
    (toolchain / "lake").write_text("#!/bin/sh\nexit 1\n")
    (toolchain / "lake").chmod(0o755)
    monkeypatch.setenv("PATH", f"{toolchain}{os.pathsep}{os.environ['PATH']}")
    commit(repository, {"tools/__init__.py": "",
                        "tests/conftest.py": "import shutil\ndef pytest_sessionstart(session):\n"
                        "    assert shutil.which('lake') is None, 'would build the backends'\n"},
           "an old conftest that builds")
    merge(repository, {"tests/conftest.py": None, "tests/test_one.py":
                       "def test_kept(): pass\ndef test_dropped(): pass\ndef test_new(): pass\n"})
    named = gate_collection.introduced_by(gate_collection.collect(repository), [], repository)
    assert named["tests/test_one.py::test_new"] == merged(repository)
    root = subprocess.run(["git", "log", "--format=%h %s", "--max-parents=0"], cwd=repository,
                          check=True, capture_output=True, text=True).stdout.strip()
    assert named["tests/test_one.py::test_kept"] == root


@pytest.mark.parametrize("body", [
    "import pytest\npytest.skip('backend unavailable', allow_module_level=True)\n",
    "import ve_gate_absent_test_backend\n",
], ids=["module skip", "import error"])
def test_collection_refuses_a_module_dropped_at_collection(repository, body):
    # A baseline taken from such a collection would silently drop its tests.
    (repository / "tests/test_three.py").write_text(body + "def test_hidden(): pass\n")
    with pytest.raises(gate_collection.CollectionError, match="tests/test_three.py"):
        gate_collection.collect(repository)
