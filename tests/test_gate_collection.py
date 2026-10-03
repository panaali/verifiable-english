"""The pinned gate collection must be the gate's real collection, and a merge that
changes the tests without it must be named."""
from __future__ import annotations

import json
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


def test_report_names_the_merge_that_changed_tests_without_the_baseline(repository):
    # compose-s1 merged 210 tests into main without them; the gate then
    # reported only counts and IDs, not where they came from.
    expected = gate_collection.collect(repository)
    assert expected == ["tests/test_one.py::test_kept", "tests/test_one.py::test_dropped"]
    git(repository, "checkout", "-q", "-b", "feature")
    (repository / "tests/test_one.py").write_text("def test_kept(): pass\n")
    (repository / "tests/test_two.py").write_text(
        "import pytest\n@pytest.mark.parametrize('case', ['x', 'y'])\ndef test_new(case): pass\n")
    git(repository, "add", ".")
    git(repository, "commit", "-q", "-m", "feature tests")
    git(repository, "checkout", "-q", "main")
    git(repository, "merge", "-q", "--no-ff", "feature", "-m", "Merge feature (forgot the baseline)")
    added, removed = gate_collection.difference(expected, gate_collection.collect(repository))
    assert added == ["tests/test_two.py::test_new[x]", "tests/test_two.py::test_new[y]"]
    assert removed == ["tests/test_one.py::test_dropped"]
    text = gate_collection.report(added, removed, repository)
    assert "Collected but not pinned, from " in text and "Pinned but not collected, from " in text
    for line in text.splitlines():
        if line.startswith(("Collected", "Pinned")):
            assert line.endswith("Merge feature (forgot the baseline): " + ("2" if "Collected" in line else "1"))
    assert all(nodeid in text for nodeid in added + removed)


@pytest.mark.parametrize("body", [
    "import pytest\npytest.skip('backend unavailable', allow_module_level=True)\n",
    "import ve_gate_absent_test_backend\n",
], ids=["module skip", "import error"])
def test_collection_refuses_a_module_dropped_at_collection(repository, body):
    # A baseline taken from such a collection would silently drop its tests.
    (repository / "tests/test_three.py").write_text(body + "def test_hidden(): pass\n")
    with pytest.raises(gate_collection.CollectionError, match="tests/test_three.py"):
        gate_collection.collect(repository)
