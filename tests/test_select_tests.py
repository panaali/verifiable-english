"""tools/select_tests.py --impacted, the fast path: changed files select the tests they can affect.

Every test file must be selected by a change to at least one source path (an import, a
native checker it starts, a data path it names, or tools/select_tests.py EXTRA_SOURCES),
so that the fast path can run it at all; unknown inputs select the full suite.
"""
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT


@pytest.fixture(scope="module")
def selector():
    with pytest.MonkeyPatch.context() as patch:
        import conftest
        patch.syspath_prepend(str(conftest.ROOT / "tools"))  # as the tool runs
        import select_tests
        yield select_tests


def tracked(selector):
    listed = subprocess.run(["git", "ls-files", "-z"], cwd=selector.ROOT, capture_output=True,
                            check=True, timeout=HANG_TIMEOUT).stdout.decode().split("\0")
    return [path for path in listed if path and not path.startswith("tests/test_")
            and (selector.ROOT / path).is_file()]


def test_every_test_file_is_reachable_from_a_source_path(selector):
    tests = [path.relative_to(selector.ROOT).as_posix() for path in selector.TESTS]
    sources, unreached = {}, []
    files = None
    for test in tests:
        imported = sorted(f for f in selector.closure(test) if f != test and not f.startswith("tests/test_"))
        if imported:
            sources[test] = imported[0]
            continue
        files = files if files is not None else tracked(selector)
        found = next((path for path in files if selector.reaches(test, path)), None)
        if found is None:
            unreached.append(test)
        else:
            sources[test] = found
    assert unreached == [], ("no source path selects these test files; name their sources in "
                             "tools/select_tests.py EXTRA_SOURCES")
    # The fast path itself selects each through its source, without the full fallback.
    for test in ("tests/test_evidence_bounds.py", "tests/test_precommit_hook.py",
                 "tests/test_agent_policy_rerun.py", "tests/test_coverage_dashboard.py"):
        plan = selector.impacted([sources[test]])
        assert not plan["fallback"] and test in plan["selected"], (test, sources[test])


@pytest.mark.parametrize("changed, expected", [
    # Native changes select their conformance tests.
    ("lean/VE/Norms/Wire.lean", {"tests/test_lean_conformance.py", "tests/test_soft_norms_lean.py"}),
    ("rust/ve/src/main.rs", {"tests/test_rust_conformance.py", "tests/test_p0_three_way.py",
                             "tests/test_nary_differential.py"}),
    # Data, tools and helpers select the tests that name or import them.
    ("usecases/asimov-laws/rules.ve", {"tests/test_asimov_laws.py"}),
    ("tools/hooks/precommit.py", {"tests/test_precommit_hook.py", "tests/test_hang_guards.py"}),
    ("tests/subprocesses.py", {"tests/test_cpu_bounds.py", "tests/test_hang_guards.py"}),
    ("tools/bench/baseline.py", {"tests/test_bench_baselines.py"}),
], ids=["lean", "rust", "use case", "hook", "test helper", "bench"])
def test_changes_select_the_tests_that_depend_on_them(selector, changed, expected):
    plan = selector.impacted([changed])
    assert not plan["fallback"]
    assert expected <= set(plan["selected"]), expected - set(plan["selected"])
    assert set(plan["always"]) <= set(plan["selected"])


@pytest.mark.parametrize("changed", ["tests/conftest.py", "tests/subprocesses.py", "tools/rust_build.py",
                                     "ve/surface/unambiguity.py"])
def test_what_the_conftest_loads_selects_every_test_below_it(selector, changed):
    """Review: a change to tests/conftest.py selected 18 of 214 files. pytest imports each
    conftest.py for every test below it, so a change to it, or to what it imports,
    selects them all."""
    assert changed in selector.closure("tests/conftest.py")
    plan = selector.impacted([changed])
    assert not plan["fallback"] and plan["selected_count"] == plan["full_count"]


def test_a_conftest_in_a_test_directory_joins_its_tests_closure(selector, tmp_path, monkeypatch):
    (tmp_path / "tests/deep").mkdir(parents=True)
    for conftest in ("conftest.py", "tests/conftest.py", "tests/deep/conftest.py"):
        (tmp_path / conftest).write_text("")
    (tmp_path / "tests/deep/test_x.py").write_text("")
    (tmp_path / "tests/test_y.py").write_text("")
    monkeypatch.setattr(selector, "ROOT", tmp_path)
    # Which conftest files join, each standing for its own (cached, real-tree) closure.
    monkeypatch.setattr(selector, "closure", lambda relative: frozenset({relative}))
    found = selector.test_closure.__wrapped__
    assert found("tests/deep/test_x.py") == {"tests/deep/test_x.py", "conftest.py", "tests/conftest.py",
                                             "tests/deep/conftest.py"}
    assert found("tests/test_y.py") == {"tests/test_y.py", "conftest.py", "tests/conftest.py"}


def test_narrow_changes_select_few_tests(selector):
    """The fast path is fast where the code is narrow (the product's modules import one
    another widely, so a kernel change still selects most of the suite)."""
    for changed in ("usecases/asimov-laws/rules.ve", "tools/hooks/precommit.py", "tools/bench/baseline.py"):
        assert selector.impacted([changed])["selected_count"] < 40, changed


def test_unknown_or_unreached_inputs_select_the_full_suite(selector):
    for paths in ([], ["new-unmapped-format.xyz"], ["ve/__init__.py"], ["ve/deleted_module.py"]):
        plan = selector.impacted(paths)
        assert plan["fallback"] and plan["selected_count"] == plan["full_count"], paths


def test_a_script_no_test_reaches_is_reported(selector, monkeypatch):
    monkeypatch.setattr(selector, "reaches", lambda test, changed: False)
    plan = selector.impacted(["tools/bench/baseline.py"])
    assert not plan["fallback"] and plan["scripts_without_tests"] == ["tools/bench/baseline.py"]
    assert plan["selected"] == sorted(plan["always"])
