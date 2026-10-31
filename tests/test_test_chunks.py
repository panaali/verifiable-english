"""eff-20261030-1: a selected run runs a heavy test file as several pytest processes ("chunks"), each a disjoint part
of the file's collected tests, and the file passes only when every chunk passes and every collected test ran in
exactly one chunk (tools/test_chunks.py, tools/select_tests.py `record_ordered`, the hook in tests/conftest.py).

The same tests run, each exactly once: the rule is a partition (property over generated node lists), a chunk that
fails, a test no chunk ran and a test two chunks ran each fail the file, the map keeps one entry per file with the
union of its chunks' edges, and a --full run never chunks. The nested runs use a tiny synthetic tests tree.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

from hypothesis import given, settings, strategies as st
import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import nested_pytest  # noqa: E402
import run_order  # noqa: E402
import select_tests  # noqa: E402
import test_chunks  # noqa: E402
import test_map  # noqa: E402

NODEIDS = st.lists(st.text(st.sampled_from("abc[]-:/._1"), min_size=1, max_size=8).map(lambda s: f"tests/t.py::{s}"),
                   max_size=40)
SECONDS = st.dictionaries(st.text(st.sampled_from("abc"), min_size=1, max_size=3).map(lambda s: f"tests/t.py::{s}"),
                          st.floats(min_value=0, max_value=1e4, allow_nan=False), max_size=10)


# --- the rule: one pure function ---

@settings(max_examples=300, deadline=None)
@given(NODEIDS, st.integers(min_value=1, max_value=5), SECONDS)
def test_the_parts_cover_every_node_exactly_once(nodeids, count, seconds):
    parts = test_chunks.partition(nodeids, count, seconds)
    every = [nodeid for part in parts for nodeid in part]
    assert len(parts) == count
    assert sorted(every) == sorted(set(nodeids))  # each node once, none lost, none added
    assert [test_chunks.chunk(nodeids, index, count, seconds) for index in range(1, count + 1)] == parts


@settings(max_examples=100, deadline=None)
@given(NODEIDS, st.integers(min_value=1, max_value=5), SECONDS, st.randoms(use_true_random=False))
def test_the_parts_do_not_depend_on_collection_order(nodeids, count, seconds, rng):
    shuffled = list(nodeids)
    rng.shuffle(shuffled)
    assert test_chunks.partition(shuffled, count, seconds) == test_chunks.partition(nodeids, count, seconds)


def test_one_chunk_keeps_every_node_and_round_robin_without_seconds():
    nodeids = [f"tests/t.py::test_{n}" for n in "edcba"]
    assert test_chunks.partition(nodeids, 1) == [sorted(nodeids)]
    assert test_chunks.partition(nodeids, 2) == [["tests/t.py::test_a", "tests/t.py::test_c", "tests/t.py::test_e"],
                                                 ["tests/t.py::test_b", "tests/t.py::test_d"]]


def test_recorded_seconds_balance_the_parts():
    nodeids = [f"tests/t.py::test_{n}" for n in "abcdef"]
    seconds = {"tests/t.py::test_a": 100.0, "tests/t.py::test_b": 60.0, "tests/t.py::test_c": 50.0}
    parts = test_chunks.partition(nodeids, 2, seconds)
    load = [sum(seconds.get(nodeid, 0.0) for nodeid in part) for part in parts]
    assert load == [100.0, 110.0]  # longest first, each to the lighter part: a | b c
    assert parts[0] == ["tests/t.py::test_a", "tests/t.py::test_d", "tests/t.py::test_f"]  # then round-robin


@pytest.mark.parametrize("text", ["0/2", "3/2", "1/0", "1", "a/b", "1/2/3", "-1/2", " ", "1/02x"])
def test_a_malformed_setting_is_refused(text):
    with pytest.raises(ValueError):
        test_chunks.setting(text)


def test_labels_round_trip_and_plain_units_are_not_labels():
    assert test_chunks.parse_label(test_chunks.label("tests/test_a.py", 2, 3)) == ("tests/test_a.py", 2, 3)
    for text in ("tests/test_a.py", "tests/test_a.py::chunk(3/2)", "tests/test_a.py::chunk(0/2)",
                 "tests/test_a.py::test_x", "tests/test_a.py::chunk(1/2)x"):
        assert test_chunks.parse_label(text) is None
    with pytest.raises(ValueError):
        test_chunks.label("tests/test_a.py", 3, 2)


# --- the hook: a chunk process keeps its part, deselecting the rest ---

TREE = {
    "conftest.py": "from tools import test_chunks\n\n\ndef pytest_configure(config):\n"
                   "    test_chunks.register(config, dict)\n",
    "tests/test_many.py": """
        import os

        import pytest


        @pytest.mark.parametrize("n", range(7))
        def test_n(n):
            assert "VE_TEST_CHUNK" not in os.environ  # taken out before any test, so no child inherits it


        class TestBox:
            def test_inside(self):
                pass


        def test_fails_when_asked():
            assert os.environ.get("FAIL_MANY") != "1"
        """,
    "tests/test_small.py": "def test_small():\n    pass\n",
}


def project(tmp_path: Path, files: dict[str, str] = TREE) -> Path:
    for name, text in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(textwrap.dedent(text))
    return tmp_path


def pytest_run(root: Path, *arguments: str, **settings: str) -> subprocess.CompletedProcess:
    command = nested_pytest.command(["-q", "-p", "no:cacheprovider", *arguments], python=[sys.executable])
    environment = nested_pytest.environment(os.environ, PYTHONPATH=str(ROOT), **settings)
    return subprocess.run(command, cwd=root, env=environment, text=True, capture_output=True, timeout=HANG_TIMEOUT)


def listed(result: subprocess.CompletedProcess) -> list[str]:
    return [line for line in result.stdout.splitlines() if "::" in line and not line.startswith(" ")]


def test_each_chunk_runs_its_part_and_together_they_run_every_test(tmp_path):
    root = project(tmp_path)
    whole = listed(pytest_run(root, "--collect-only", "tests/test_many.py"))
    assert len(whole) == 9
    ran = []
    for index in (1, 2, 3):
        result = pytest_run(root, "-rA", "tests/test_many.py", VE_TEST_CHUNK=f"{index}/3")
        assert result.returncode == 0, result.stdout + result.stderr
        kept = [line.split(" ", 1)[1] for line in result.stdout.splitlines() if line.startswith("PASSED ")]
        assert sorted(kept) == test_chunks.chunk(whole, index, 3)
        assert f"{9 - len(kept)} deselected" in result.stdout  # pytest's own deselect report
        ran += kept
    assert sorted(ran) == sorted(whole)


@pytest.mark.parametrize("setting", [None, "1/1"])
def test_unset_or_one_chunk_runs_every_test(tmp_path, setting):
    root = project(tmp_path)
    result = pytest_run(root, "tests/test_many.py", **({"VE_TEST_CHUNK": setting} if setting else {}))
    assert result.returncode == 0 and "9 passed" in result.stdout and "deselected" not in result.stdout


def test_the_chunk_applies_after_marker_deselection(tmp_path):
    """`-m` deselects first, then the chunk splits what is left: the parts are those of the listing a unit gets."""
    root = project(tmp_path, {**TREE, "pytest.ini": "[pytest]\nmarkers =\n    slow: x\n",
                              "tests/test_many.py": "import pytest\n\n\n@pytest.mark.slow\ndef test_0slow():\n"
                                                    "    pass\n\n\ndef test_a():\n    pass\n\n\ndef test_b():\n"
                                                    "    pass\n\n\ndef test_c():\n    pass\n"})
    whole = listed(pytest_run(root, "--collect-only", "-m", "not slow", "tests/test_many.py"))
    # Split before `-m`, chunk 1 would be test_b alone (0slow, b | a, c); after it, it is test_a and test_c.
    assert test_chunks.chunk(whole, 1, 2) == ["tests/test_many.py::test_a", "tests/test_many.py::test_c"]
    for index in (1, 2):
        kept = listed(pytest_run(root, "--collect-only", "-m", "not slow", "tests/test_many.py",
                                 VE_TEST_CHUNK=f"{index}/2"))
        assert kept == test_chunks.chunk(whole, index, 2)


@pytest.mark.parametrize("setting, message", [("3/2", "expected <i>/<k>"), ("x", "expected <i>/<k>")])
def test_a_bad_setting_is_a_usage_error(tmp_path, setting, message):
    result = pytest_run(project(tmp_path), "tests/test_small.py", VE_TEST_CHUNK=setting)
    assert result.returncode == 4 and message in result.stderr


def test_a_chunk_under_xdist_is_a_usage_error(tmp_path):
    command = nested_pytest.command(["-q", "-p", "no:cacheprovider", "tests/test_small.py"], workers=2,
                                    python=[sys.executable])
    environment = nested_pytest.environment(os.environ, PYTHONPATH=str(ROOT), VE_TEST_CHUNK="1/2")
    result = subprocess.run(command, cwd=project(tmp_path), env=environment, text=True, capture_output=True,
                            timeout=HANG_TIMEOUT)
    assert result.returncode == 4 and "not under xdist" in result.stderr


def test_the_suites_conftest_applies_the_chunk():
    """The suite's own hook (tests/conftest.py), on this file's own collection."""
    def collect(**settings):
        result = subprocess.run(
            nested_pytest.command(["-q", "-p", "no:cacheprovider", "--collect-only", "tests/test_test_chunks.py"],
                                  python=[sys.executable]),
            cwd=ROOT, env=nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1", **settings), text=True,
            capture_output=True, timeout=HANG_TIMEOUT)
        assert result.returncode == 0, result.stdout + result.stderr
        return listed(result)

    whole = collect()
    parts = [collect(VE_TEST_CHUNK=f"{index}/2") for index in (1, 2)]
    assert whole and all(parts) and sorted(parts[0] + parts[1]) == sorted(whole)
    assert not set(parts[0]) & set(parts[1])


def test_a_nested_run_never_inherits_the_chunk():
    assert "VE_TEST_CHUNK" not in nested_pytest.environment({"VE_TEST_CHUNK": "1/2"})
    environ = {"VE_TEST_CHUNK": "1/2"}

    class Config:
        class option:
            numprocesses = None

        class pluginmanager:
            registered = []

            @classmethod
            def register(cls, plugin, name):
                cls.registered.append(name)

    test_chunks.register(Config, dict, environ)
    assert environ == {} and Config.pluginmanager.registered == ["ve-test-chunk"]
    test_chunks.register(Config, dict, environ)  # unset: nothing registered
    assert Config.pluginmanager.registered == ["ve-test-chunk"]


# --- the check: every collected test in exactly one chunk ---

LISTING = [f"tests/t.py::test_{n}" for n in "abcde"]


def parts(count: int = 2) -> dict[int, list[str]]:
    return dict(enumerate(test_chunks.partition(LISTING, count), start=1))


def test_chunks_that_run_their_parts_pass_the_check():
    assert select_tests.chunk_problems("tests/t.py", 2, LISTING, parts(), {}) == []
    assert select_tests.chunk_problems("tests/t.py", 3, LISTING, {2: parts(3)[2]}, {}) == []  # a shard's part


def test_a_test_no_chunk_ran_fails_the_check():
    ran = parts()
    ran[2] = ran[2][:-1]
    problems = select_tests.chunk_problems("tests/t.py", 2, LISTING, ran, {})
    assert any("ran in no chunk" in problem for problem in problems)
    assert any("did not run 1 of its tests" in problem for problem in problems)


def test_a_test_two_chunks_ran_fails_the_check():
    ran = parts()
    ran[2] = [*ran[2], ran[1][0]]
    problems = select_tests.chunk_problems("tests/t.py", 2, LISTING, ran, {})
    assert any("more than one chunk" in problem for problem in problems)
    ran = parts()
    ran[1] = [*ran[1], ran[1][0]]
    assert any("ran twice" in problem for problem in select_tests.chunk_problems("tests/t.py", 2, LISTING, ran, {}))


def test_a_missing_report_a_failed_listing_or_an_extra_test_fails_the_check():
    assert select_tests.chunk_problems("tests/t.py", 2, None, parts(), {})
    assert select_tests.chunk_problems("tests/t.py", 2, LISTING, {**parts(), 2: None}, {})
    assert select_tests.chunk_problems("tests/t.py", 2, LISTING, {**parts(), 2: [*parts()[2], "tests/t.py::x"]}, {})


def test_a_rule_that_loses_a_test_fails_the_check_even_on_one_chunk(monkeypatch):
    partition = test_chunks.partition
    monkeypatch.setattr(test_chunks, "partition", lambda *a, **k: [part[:-1] for part in partition(*a, **k)])
    lossy = dict(enumerate(test_chunks.partition(LISTING, 2), start=1))
    assert any("exactly one of" in problem for problem in select_tests.chunk_problems("tests/t.py", 2, LISTING,
                                                                                      {1: lossy[1]}, {}))


def chunk_result(exit_code: int, functions: set, seconds: float) -> dict:
    return {"f": functions, "r": {f"read{seconds}"}, "d": set(), "x": set(), "m": set(), "p": set(), "v": set(),
            "opaque": [], "exit": exit_code, "seconds": seconds}


def test_the_map_entry_of_a_chunked_file_is_the_union_of_its_chunks():
    done = {1: chunk_result(0, {("ve/a.py", "one")}, 10.0), 2: chunk_result(0, {("ve/b.py", "two")}, 5.5)}
    folded = select_tests.fold_chunks("tests/t.py", 2, done, [])
    assert folded["exit"] == 0 and folded["seconds"] == 15.5 and not folded["partial"]
    data = test_map.build_map({"tests/t.py": folded}, "c" * 40)
    assert data["tests"] == ["tests/t.py"]  # one unit per file, as without chunks
    assert data["functions"] == {"ve/a.py": {"one": [0]}, "ve/b.py": {"two": [0]}}
    assert sorted(data["reads"]) == ["read10.0", "read5.5"] and data["status"]["tests/t.py"]["seconds"] == 15.5


@pytest.mark.parametrize("exits, problems, expected", [
    ((0, 1), [], 1), ((1, 0), [], 1), ((0, 0), ["gap"], 1), ((5, 5), [], 5), ((0, 5), [], 0), ((0, 0), [], 0),
    ((0, "timeout"), [], "timeout")])
def test_a_failed_chunk_or_a_problem_fails_the_folded_unit(exits, problems, expected):
    done = {index: chunk_result(code, set(), 1.0) for index, code in enumerate(exits, start=1)}
    assert select_tests.fold_chunks("tests/t.py", len(exits), done, problems)["exit"] == expected


# --- the decision: which units are chunked, into how many ---

def test_only_measured_units_over_the_threshold_are_chunked_and_capped():
    seconds = {"tests/test_a.py": select_tests.CHUNK_SECONDS + 1, "tests/test_b.py": select_tests.CHUNK_SECONDS,
               "tests/test_c.py": 100 * select_tests.CHUNK_TARGET_SECONDS, "tests/test_unmeasured.py": 1e6}
    decisions = {unit: {} for unit in seconds if unit != "tests/test_unmeasured.py"}
    counts = select_tests.chunk_counts(sorted(seconds), seconds, decisions)
    assert "tests/test_b.py" not in counts and counts["tests/test_c.py"] == select_tests.MAX_CHUNKS
    assert "tests/test_unmeasured.py" not in counts
    assert counts["tests/test_a.py"] == min(select_tests.MAX_CHUNKS, -(-seconds["tests/test_a.py"]
                                                                       // select_tests.CHUNK_TARGET_SECONDS))
    assert select_tests.chunk_counts(sorted(seconds), seconds, {}) == {}  # no measured rows: nothing chunked
    capped = {"tests/test_c.py": {"max_chunks": 2}}
    assert select_tests.chunk_counts(["tests/test_c.py"], seconds, capped) == {"tests/test_c.py": 2}


def test_a_setup_dominated_file_is_never_chunked():
    seconds = {"tests/test_a.py": 1e6}
    assert select_tests.chunk_counts(["tests/test_a.py"], seconds, {"tests/test_a.py": {"never": True}}) == {}
    assert select_tests.chunk_counts(["tests/test_a.py"], seconds, {"tests/test_a.py": {"never": False}})
    decisions = select_tests.chunk_decisions()
    never = sorted(unit for unit, row in decisions.items() if row.get("never"))
    assert decisions and select_tests.chunk_counts(never, {unit: 1e6 for unit in never}, decisions) == {}


def test_a_malformed_decisions_file_chunks_nothing(tmp_path):
    for text in ("", "[]", '{"format": "other", "files": {}}', '{"format": "ve-test-chunks@1", "files": [1]}'):
        (tmp_path / "chunks.json").write_text(text)
        assert select_tests.chunk_decisions(tmp_path / "chunks.json") == {}


# --- the plan: --chunk-heavy lists chunks; without it the plan is unchanged ---

def fixed_plan(tmp_path: Path) -> dict:
    path = tmp_path / "map.json.gz"
    test_map.write_map(test_map.build_map({"tests/test_big.py": chunk_result(0, {("ve/a.py", "f")}, 2000.0),
                                           "tests/test_small.py": chunk_result(0, {("ve/a.py", "f")}, 10.0)}, "c" * 40), path)
    return {"selected": ["tests/test_big.py", "tests/test_small.py"], "changed": [], "commands": [],
            "lean_build": False, "rust_build": False, "full": False, "map": {"commit": "c" * 40, "path": str(path)},
            "selected_count": 2}


@pytest.mark.parametrize("option", [[], ["--chunk-heavy"]])
def test_the_plan_lists_chunks_only_with_the_option(tmp_path, monkeypatch, capsys, option):
    plan = fixed_plan(tmp_path)
    monkeypatch.setattr(select_tests, "select", lambda *a, **k: json.loads(json.dumps(plan)))
    monkeypatch.setattr(select_tests, "chunk_decisions", lambda path=None: {
        "tests/test_big.py": {"wall_seconds": 100.0, "setup_seconds": 20.0}})
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "x", "--static", "--json", *option])
    assert select_tests.main() == 0
    out = capsys.readouterr().out
    if not option:
        assert out == json.dumps(plan, indent=2) + "\n"  # byte for byte
        return
    printed = json.loads(out)
    labels = [f"tests/test_big.py::chunk({index}/4)" for index in range(1, 5)]
    assert printed["selected"] == [*labels, "tests/test_small.py"]
    assert printed["chunk_seconds"] == {label: 2000.0 * (0.2 + 0.8 / 4) for label in labels}
    assert {key: value for key, value in printed.items() if key not in ("selected", "chunk_seconds")} == {
        key: value for key, value in plan.items() if key != "selected"}


def test_with_defer_heavy_the_plan_defers_whole_files_then_chunks_the_rest(tmp_path, monkeypatch, capsys):
    path = tmp_path / "deferring-map.json.gz"
    test_map.write_map(test_map.build_map({unit: chunk_result(0, {("ve/a.py", "f")}, seconds) for unit, seconds in [
        ("tests/test_big.py", 2000.0), ("tests/test_weak.py", 2000.0), ("tests/test_small.py", 10.0)]}, "c" * 40), path)
    plan = {**fixed_plan(tmp_path), "selected": ["tests/test_big.py", "tests/test_small.py", "tests/test_weak.py"],
            "map": {"commit": "c" * 40, "path": str(path)}, "selected_count": 3,
            "reasons": {"tests/test_big.py": ["ve/a.py:f"], "tests/test_small.py": ["ve/a.py:f"],
                        "tests/test_weak.py": ["imports ve/a.py (static)"]}}
    monkeypatch.setattr(select_tests, "select", lambda *a, **k: json.loads(json.dumps(plan)))
    monkeypatch.setattr(select_tests.run_order, "last_failed", lambda **_: {})
    monkeypatch.setattr(select_tests, "chunk_decisions", lambda path=None: {
        unit: {"wall_seconds": 100.0, "setup_seconds": 20.0} for unit in ("tests/test_big.py", "tests/test_weak.py")})
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "x", "--static", "--json",
                                      "--chunk-heavy", "--defer-heavy"])
    assert select_tests.main() == 0
    printed = json.loads(capsys.readouterr().out)
    assert list(printed["deferred"]) == ["tests/test_weak.py"]  # a deferred file is never chunked
    assert printed["selected"] == [*chunked("tests/test_big.py", 4), "tests/test_small.py"]


@pytest.mark.parametrize("other", ["--full", "--impacted", "--no-record", "--tier=light"])
def test_the_chunk_option_is_for_a_recorded_selected_run(monkeypatch, capsys, other):
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "x", "--chunk-heavy", other])
    with pytest.raises(SystemExit):
        select_tests.main()
    assert "--chunk-heavy is for a recorded selected run" in capsys.readouterr().err


# --- a recorded run: the chunks run in the pool; the file is one unit ---

def recording(monkeypatch, tmp_path: Path, files: dict[str, str] = TREE) -> Path:
    root = project(tmp_path / "root", files)
    monkeypatch.setenv("PYTHONPATH", str(ROOT))
    monkeypatch.setattr(test_map, "ROOT", root)
    monkeypatch.setattr(test_map, "site_packages", lambda: tmp_path)
    monkeypatch.setattr(test_map, "install_hook", lambda site: None)
    monkeypatch.setattr(test_map, "remove_hook", lambda site: None)
    monkeypatch.setattr(test_map, "tracked_paths", lambda: set())
    unit_command = test_map.unit_command
    monkeypatch.setattr(test_map, "unit_command", lambda unit, options=(): [
        sys.executable, *unit_command(unit, options)[len(select_tests.UV_PYTHON):]])
    return root


def chunked(file: str, count: int) -> list[str]:
    return [test_chunks.label(file, index, count) for index in range(1, count + 1)]


@pytest.mark.parametrize("count", [2, 3])
def test_a_chunked_file_passes_as_one_unit(tmp_path, monkeypatch, capsys, count):
    recording(monkeypatch, tmp_path)
    results, failures = select_tests.record_ordered([*chunked("tests/test_many.py", count), "tests/test_small.py"],
                                                    tmp_path / "work", 2, 0, set())
    assert sorted(results) == ["tests/test_many.py", "tests/test_small.py"] and failures["tests/test_many.py"] == []
    assert results["tests/test_many.py"]["exit"] == 0 and results["tests/test_many.py"]["chunks"] == count
    assert "each of its 9 tests ran in exactly one chunk" in capsys.readouterr().out


def test_a_failed_chunk_fails_the_unit(tmp_path, monkeypatch):
    recording(monkeypatch, tmp_path)
    monkeypatch.setenv("FAIL_MANY", "1")
    results, failures = select_tests.record_ordered(chunked("tests/test_many.py", 3), tmp_path / "work", 2, 0, set())
    assert results["tests/test_many.py"]["exit"] == 1
    assert failures["tests/test_many.py"] == ["tests/test_many.py::test_fails_when_asked"]


def test_a_test_missing_from_every_chunk_fails_the_unit(tmp_path, monkeypatch, capsys):
    recording(monkeypatch, tmp_path)
    collected = select_tests.collected_tests
    monkeypatch.setattr(select_tests, "collected_tests", lambda files, jobs: {
        file: [*listing, f"{file}::test_ghost"] for file, listing in collected(files, jobs).items()})
    results, failures = select_tests.record_ordered(chunked("tests/test_many.py", 2), tmp_path / "work", 2, 0, set())
    assert results["tests/test_many.py"]["exit"] == 1 and failures["tests/test_many.py"] == ["tests/test_many.py"]
    assert "1 collected tests ran in no chunk: tests/test_many.py::test_ghost" in capsys.readouterr().out


def test_a_test_run_by_two_chunks_fails_the_unit(tmp_path, monkeypatch, capsys):
    """A tree whose hook ignores the chunk: every chunk runs the whole file."""
    recording(monkeypatch, tmp_path, {**TREE, "conftest.py": "import os\n\nos.environ.pop('VE_TEST_CHUNK', None)\n"})
    results, failures = select_tests.record_ordered(chunked("tests/test_many.py", 2), tmp_path / "work", 2, 0, set())
    assert results["tests/test_many.py"]["exit"] == 1 and failures["tests/test_many.py"] == ["tests/test_many.py"]
    assert "tests ran in more than one chunk" in capsys.readouterr().out


def test_maxfail_stops_across_chunks_as_across_units(tmp_path, monkeypatch):
    """One job: chunk 1 of 3 holds the failing test, so the stop leaves chunks 2 and 3 and the next unit unstarted;
    the file has no result (it did not run to the end) but keeps its failed test."""
    recording(monkeypatch, tmp_path)
    monkeypatch.setenv("FAIL_MANY", "1")
    labels = chunked("tests/test_many.py", 3)
    first = next(label for label in labels if "tests/test_many.py::test_fails_when_asked" in test_chunks.chunk(
        select_tests.collected_tests(["tests/test_many.py"], 1)["tests/test_many.py"],
        test_chunks.parse_label(label)[1], 3))
    ordered = [first, *[label for label in labels if label != first], "tests/test_small.py"]
    results, failures = select_tests.record_ordered(ordered, tmp_path / "work", 1, 1, set())
    assert results == {} and failures == {"tests/test_many.py": ["tests/test_many.py::test_fails_when_asked"]}
    results, failures = select_tests.record_ordered(ordered, tmp_path / "work2", 1, 0, set())
    assert sorted(results) == ["tests/test_many.py", "tests/test_small.py"]  # without the stop: every chunk


def test_junit_cases_are_the_node_ids_of_the_file(tmp_path):
    root = project(tmp_path)
    report = tmp_path / "junit.xml"
    pytest_run(root, *run_order.junit_options(report), "tests/test_many.py")
    whole = listed(pytest_run(root, "--collect-only", "tests/test_many.py"))
    assert [nodeid for nodeid, _ in run_order.junit_cases(report, "tests/test_many.py")] == whole
    assert {outcome for _, outcome in run_order.junit_cases(report, "tests/test_many.py")} == {"passed"}
    assert run_order.junit_cases(tmp_path / "absent.xml", "tests/test_many.py") is None


# --- a full run never chunks ---

def test_a_full_run_never_chunks(tmp_path, monkeypatch):
    seen = []
    status = {"tests/test_big.py": {"exit": 0, "seconds": 1e6, "opaque": []}}
    coverage = select_tests.Coverage({**test_map.build_map({}, "c" * 40), "status": status})
    monkeypatch.setattr(select_tests, "resolve_map", lambda base, path: coverage)
    monkeypatch.setattr(select_tests, "chunk_decisions", lambda path=None: {"tests/test_big.py": {}})
    monkeypatch.setattr(test_map, "working_tree_id", lambda: "t" * 40)
    monkeypatch.setattr(test_map, "build_natives", lambda: None)
    monkeypatch.setattr(test_map, "write_map", lambda data, path: None)
    monkeypatch.setattr(run_order, "state_path", lambda: tmp_path / "state.json")
    monkeypatch.setattr(select_tests, "working_changes", lambda commit: ({}, {}))
    monkeypatch.setattr(select_tests, "uncertain_units", lambda *a: set())
    monkeypatch.setattr(select_tests.source_graph, "load", lambda root: None)
    monkeypatch.setattr(select_tests, "units", lambda: ["tests/test_big.py"])
    monkeypatch.setattr(select_tests, "record_ordered", lambda ordered, *a: (
        seen.append(ordered), ({"tests/test_big.py": {**chunk_result(0, set(), 1.0)}}, {"tests/test_big.py": []}))[1])
    plan = {"selected": ["tests/test_big.py"], "changed": [], "map": {"commit": "c" * 40, "path": "m"},
            "commands": [], "lean_build": False}
    assert select_tests.run(plan, full=True, jobs=1) == 0
    assert select_tests.run(plan, jobs=1) == 0
    assert seen == [["tests/test_big.py"], chunked("tests/test_big.py", select_tests.MAX_CHUNKS)]
    with pytest.raises(ValueError, match="a full run never chunks"):
        select_tests.run({**plan, "selected": chunked("tests/test_big.py", 2)}, full=True, jobs=1)


# --- the failed-unit line keeps the format the orchestrator's parsers read ---

# The orchestrator's parsers of select_tests' unit lines (outside this repository; review eff-20261030-1 F1):
# chain-gate.sh and review-ready.py match this and split the node ids on ", "; mac-pytest.sh greps the head and
# strips "; log .*".
CHAIN_GATE_LINE = r"^FAILED \S+ \(exit [^)]*\): (.*); log \S+$"
MAC_PYTEST_HEAD = r"^FAILED [^ ]+ \(exit [^)]*\): "


def parsed_ids(output: str) -> dict[str, set[str]]:
    """The node ids each parser takes from a run's output: chain-gate/review-ready, then mac-pytest."""
    import re
    lines = output.splitlines()
    chain = {x.strip() for line in lines if (m := re.match(CHAIN_GATE_LINE, line))
             for x in m.group(1).split(", ") if x.strip()}
    mac = {x.strip() for line in lines if re.match(MAC_PYTEST_HEAD, line)
           for x in re.sub(r"; log .*", "", re.sub(MAC_PYTEST_HEAD, "", line)).split(",") if x.strip()}
    return {"chain": chain, "mac": mac}


def run_failing(tmp_path, monkeypatch, capsys, results: dict, failures: dict, logs: list[str],
                held: set[str] = frozenset()) -> str:
    def record(ordered, work, *rest):
        for label in logs:
            (work / (label.replace("/", "__") + ".log")).write_text(f"tail of {label}\n")
        return results, failures
    monkeypatch.setattr(select_tests, "record_ordered", record)
    monkeypatch.setattr(test_map, "working_tree_id", lambda: "t" * 40)
    monkeypatch.setattr(test_map, "build_natives", lambda: None)
    monkeypatch.setattr(test_map, "write_map", lambda data, path: None)
    monkeypatch.setattr(run_order, "state_path", lambda: tmp_path / "state.json")
    (tmp_path / "work").mkdir()
    monkeypatch.setattr(select_tests.tempfile, "mkdtemp", lambda prefix: str(tmp_path / "work"))
    selected = sorted({label.split("::")[0] for label in logs} | set(results) | set(failures))
    select_tests.run_recorded({"selected": selected, "changed": [], "map": None}, 1, 0, set(held), chunked=False)
    return capsys.readouterr().out


def test_a_failed_unit_line_ends_in_its_log(tmp_path, monkeypatch, capsys):
    unit = "tests/test_select_tests.py"
    out = run_failing(tmp_path, monkeypatch, capsys, {unit: chunk_result(1, set(), 1.0)},
                      {unit: [f"{unit}::test_a", f"{unit}::test_b"]}, [unit])
    assert parsed_ids(out) == {"chain": {f"{unit}::test_a", f"{unit}::test_b"}} | {
        "mac": {f"{unit}::test_a", f"{unit}::test_b"}}
    line = next(line for line in out.splitlines() if line.startswith("FAILED "))
    assert line.endswith(f"; log {tmp_path / 'work' / 'tests__test_select_tests.py.log'}")
    assert f"tail of {unit}" in out


def test_a_chunked_unit_line_names_its_first_chunk_log_and_prints_every_tail(tmp_path, monkeypatch, capsys):
    unit, labels = "tests/test_many.py", chunked("tests/test_many.py", 3)
    out = run_failing(tmp_path, monkeypatch, capsys, {unit: chunk_result(1, set(), 1.0)},
                      {unit: [f"{unit}::test_n[1]"]}, labels)
    assert parsed_ids(out) == {"chain": {f"{unit}::test_n[1]"}, "mac": {f"{unit}::test_n[1]"}}
    line = next(line for line in out.splitlines() if line.startswith("FAILED "))
    assert line.rsplit("; log ", 1)[1].endswith(labels[0].replace("/", "__") + ".log")
    assert all(f"tail of {label}" in out for label in labels)


def test_a_stopped_chunked_unit_line_keeps_the_format(tmp_path, monkeypatch, capsys):
    # The run stopped before the file's other chunks ended: no folded result, but the failures of the chunks that
    # ended still reach every parser, and the note sits in the exit, not among the node ids.
    unit, labels = "tests/test_many.py", chunked("tests/test_many.py", 2)
    out = run_failing(tmp_path, monkeypatch, capsys, {}, {unit: [f"{unit}::test_a"]}, labels[:1])
    assert parsed_ids(out) == {"chain": {f"{unit}::test_a"}, "mac": {f"{unit}::test_a"}}
    assert f"(exit {select_tests.STOPPED_EXIT}): " in out


def test_a_quarantined_unit_line_is_no_failure_to_the_parsers(tmp_path, monkeypatch, capsys):
    unit = "tests/test_select_tests.py"
    out = run_failing(tmp_path, monkeypatch, capsys, {unit: chunk_result(1, set(), 1.0)},
                      {unit: [f"{unit}::test_a"]}, [unit], held={f"{unit}::test_a"})
    assert parsed_ids(out) == {"chain": set(), "mac": set()}
    assert "QUARANTINED (fails under load; not counted) tests/test_select_tests.py (exit 1): " in out


@given(st.lists(st.from_regex(r"tests/test_[a-z]{1,8}\.py::test_[a-z0-9_\[\]-]{1,12}", fullmatch=True),
                min_size=1, max_size=5, unique=True),
       st.sampled_from([0, 1, 2, "timeout", select_tests.STOPPED_EXIT]))
def test_every_unit_line_round_trips_through_the_parsers(nodeids, exit):
    line = select_tests.unit_line("FAILED", "tests/test_x.py", exit, nodeids, Path("/w/tests__test_x.py.log"))
    assert parsed_ids(line) == {"chain": set(nodeids), "mac": set(nodeids)}
