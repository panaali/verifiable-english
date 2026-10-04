"""The pinned gate collection must be the gate's real collection, and a difference
must list every added and removed ID with the documented refresh."""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from tools import gate, gate_collection, nested_pytest

REFRESH = "uv run python tools/gate_collection.py --write"


def test_gate_baseline_is_the_gate_collection():
    # The merge train's verify runs this, so it fails on the merge that forgot
    # the baseline instead of the release gate failing later on main.
    collected = gate_collection.collect(prebuilt=True)
    expected = json.loads(gate.COLLECTION.read_text())
    added, removed = gate_collection.difference(expected, collected)
    assert not (added or removed), gate.collection_difference(added, removed)
    assert gate.COLLECTION.read_text() == gate_collection.baseline_text(collected)


def test_refresh_is_the_documented_one():
    assert gate.REFRESH == REFRESH
    assert REFRESH in (gate.ROOT / "README.md").read_text()


@pytest.fixture
def repository(tmp_path):
    (tmp_path / "pytest.ini").write_text("[pytest]\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_one.py").write_text("def test_kept(): pass\ndef test_dropped(): pass\n")
    return tmp_path


def assert_lists(text, added, removed):
    # Every ID, not a sample: compose-s1 merged 210 tests without the baseline.
    lines = text.splitlines()
    assert lines[0].endswith(f"{len(added)} collected but not pinned, "
                             f"{len(removed)} pinned but not collected.")
    expected = ((["Collected but not pinned:"] + [f"  {nodeid}" for nodeid in added] if added else [])
                + (["Pinned but not collected:"] + [f"  {nodeid}" for nodeid in removed] if removed else []))
    assert lines[1:-1] == expected
    assert f"`{REFRESH}`" in lines[-1]


def test_report_lists_every_added_and_removed_id_and_the_refresh(repository):
    expected = gate_collection.collect(repository)
    assert expected == ["tests/test_one.py::test_kept", "tests/test_one.py::test_dropped"]
    (repository / "tests/test_one.py").write_text("def test_kept(): pass\n")
    cases = [f"'c{index}'" for index in range(12)]
    (repository / "tests/test_two.py").write_text(
        f"import pytest\n@pytest.mark.parametrize('case', [{', '.join(cases)}])\n"
        "def test_new(case): pass\n")
    added, removed = gate_collection.difference(expected, gate_collection.collect(repository))
    assert added == sorted(f"tests/test_two.py::test_new[c{index}]" for index in range(12))
    assert removed == ["tests/test_one.py::test_dropped"]
    assert_lists(gate.collection_difference(added, removed), added, removed)


@pytest.mark.parametrize("added,removed", [(["tests/a.py::test_new"], []),
                                           ([], ["tests/a.py::test_gone"])],
                         ids=["only added", "only removed"])
def test_report_lists_one_sided_differences(added, removed):
    assert_lists(gate.collection_difference(added, removed), added, removed)


def test_gate_fails_with_the_same_listing():
    # The release gate and the suite's guard give the author one message.
    collected = ["tests/a.py::test_a", "tests/b.py::test_new"]
    events = {"collected": collected, "selected": collected, "deselected": [],
              "collection_reports": [],
              "tests": {nodeid: {"outcome": "passed"} for nodeid in collected}}
    result = {"counts": {}, "failures": [], "skips": []}
    expected = ["tests/a.py::test_a", "tests/b.py::test_old"]
    gate.interpret_pytest(result, events, {"optional_tests": [], "deselected_tests": []}, expected)
    assert {"stage": "coverage", "reason": gate.collection_difference(
        ["tests/b.py::test_new"], ["tests/b.py::test_old"])} in result["failures"]


# Each changes which IDs the gate collects only through pytest's discovery
# rules, which the guard must apply exactly as the gate's own run does: with
# the rule the file is (or is not) collected, and without it the reverse.
DISCOVERY = {
    "python_files": ({"pytest.ini": "[pytest]\npython_files = check_*.py\n"},
                     "tests/check_three.py", True),
    "collect_ignore": ({"tests/conftest.py": "collect_ignore = ['test_three.py']\n"},
                       "tests/test_three.py", False),
    "norecursedirs": ({"pytest.ini": "[pytest]\nnorecursedirs = skipped\n"},
                      "tests/skipped/test_three.py", False),
}


@pytest.mark.parametrize("rules,path,collected", DISCOVERY.values(), ids=DISCOVERY)
def test_collection_applies_the_gates_discovery_rules(repository, rules, path, collected):
    (repository / path).parent.mkdir(parents=True, exist_ok=True)
    (repository / path).write_text("def test_hidden(): pass\n")
    for name, text in rules.items():
        (repository / name).write_text(text)
    assert (f"{path}::test_hidden" in gate_collection.collect(repository)) == collected
    (repository / "pytest.ini").write_text("[pytest]\n")
    (repository / "tests/conftest.py").unlink(missing_ok=True)
    assert (f"{path}::test_hidden" in gate_collection.collect(repository)) != collected


GENERATED = ("import pathlib, pytest\nGENERATED = pathlib.Path(__file__).with_name('generated.txt')\n"
             "GENERATED.write_text('{case}')\n"
             "@pytest.mark.parametrize('case', [GENERATED.read_text()])\n"
             "def test_generated(case): pass\n")
IMPORTING = ("import pytest\nfrom ve_gate_generated_case import CASE\n"
             "@pytest.mark.parametrize('case', [CASE])\ndef test_generated(case): pass\n")
# The changed source of a parameter: the test module, whose bytecode pytest
# rewrites and caches, or a module it imports, whose bytecode Python caches.
SOURCES = {
    "test module": ({}, "tests/test_two.py", GENERATED),
    "imported module": ({"tests/test_two.py": IMPORTING}, "tests/ve_gate_generated_case.py",
                        "CASE = '{case}'\n"),
}
# Where the bytecode cached for the earlier source came from.
EARLIER = ("an earlier collection", "an ordinary pytest run")


def ordinary_pytest_run(repository):
    env = {name: value for name, value in os.environ.items()
           if name not in ("PYTHONPYCACHEPREFIX", "PYTHONDONTWRITEBYTECODE")}
    subprocess.run(nested_pytest.command(["-p", "no:cacheprovider", "--collect-only", "-q", "tests"]),
                   cwd=repository, env=nested_pytest.environment(env), capture_output=True, check=True,
                   timeout=HANG_TIMEOUT)


def gate_run_collection(repository, scratch):
    # The gate's own pytest run, in its environment, collecting only.
    env = gate.gate_environment(scratch)
    output = scratch / "events.json"
    env.update(PATH=os.environ["PATH"], PYTHONPATH=str(gate.ROOT), VE_GATE_PYTEST_RESULT=str(output))
    subprocess.run(gate.collection_command([sys.executable]), cwd=repository, env=env, capture_output=True,
                   timeout=HANG_TIMEOUT)
    return json.loads(output.read_text())["collected"]


# Both compare their collection with the baseline: the suite's guard and the gate.
COLLECTORS = {"guard": lambda repository, scratch: gate_collection.collect(repository),
              "gate": gate_run_collection}


@pytest.mark.parametrize("earlier", EARLIER)
@pytest.mark.parametrize("files,changed,template", SOURCES.values(), ids=SOURCES)
@pytest.mark.parametrize("collector", COLLECTORS.values(), ids=COLLECTORS)
def test_collection_reflects_the_tree_now_not_cached_bytecode(repository, tmp_path_factory, collector,
                                                               files, changed, template, earlier):
    # A same-size change within the same second leaves the source's recorded
    # size and whole-second mtime as they were, so cached bytecode looks
    # current: only a fresh compile yields the parameter now in the tree. The
    # mtime is set back exactly, so the same second is not left to timing.
    for name, text in files.items():
        (repository / name).write_text(text)
    source = repository / changed
    source.write_text(template.format(case="y"))
    if earlier == "an earlier collection":
        ids = collector(repository, tmp_path_factory.mktemp("scratch"))
        assert "tests/test_two.py::test_generated[y]" in ids
    else:
        ordinary_pytest_run(repository)
        assert any(source.parent.joinpath("__pycache__").glob(f"{source.stem}.*.pyc"))
    before = source.stat()
    source.write_text(template.format(case="z"))
    os.utime(source, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert source.stat().st_size == before.st_size
    ids = collector(repository, tmp_path_factory.mktemp("scratch"))
    assert [nodeid for nodeid in ids if "test_generated" in nodeid] == [
        "tests/test_two.py::test_generated[z]"]


@pytest.mark.parametrize("body", [
    "import pytest\npytest.skip('backend unavailable', allow_module_level=True)\n",
    "import ve_gate_absent_test_backend\n",
], ids=["module skip", "import error"])
def test_collection_refuses_a_module_dropped_at_collection(repository, body):
    # A baseline taken from such a collection would silently drop its tests.
    (repository / "tests/test_three.py").write_text(body + "def test_hidden(): pass\n")
    with pytest.raises(gate_collection.CollectionError, match="tests/test_three.py"):
        gate_collection.collect(repository)
