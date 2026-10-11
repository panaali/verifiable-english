"""docs/eff-tests/REPORT.md: every number regenerated from the saved evidence in docs/eff-tests/evidence/.

The evidence is saved (suite summaries, the difffuzz run's work, seeded bugs, the cache's entries, the branch's
commits at report time), so these checks hold after syncs with main and after the merge; nothing here reads git.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from tools import difffuzz

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/eff-tests"
EVIDENCE = DOCS / "evidence"
REPORT = (DOCS / "REPORT.md").read_text()
RUNS = {"before": "before", "after-cold": "after, cold cache", "after-warm": "after, warm cache"}


def evidence(name):
    return json.loads((EVIDENCE / name).read_text())


def suite(label):
    return evidence(f"suite-{label}.json")


def seconds(value):
    return f"{value:,.0f} s"


@pytest.mark.parametrize("label", RUNS)
def test_each_suite_row_is_its_saved_summary(label):
    run = suite(label)
    load = run["load"]
    row = (f"| {RUNS[label]} | {run['commit'][:8]} | {seconds(run['wall_seconds'])} "
           f"({run['wall_seconds'] / 60:.1f} min) | {load['median']:.1f} ({load['min']:.1f}-{load['max']:.1f}) | "
           f"{seconds(run['sum_test_seconds'])} | {run['outcomes']['passed']:,} | {run['outcomes']['failed']} |")
    assert row in REPORT
    assert len(run["failed"]) == run["outcomes"]["failed"] + run["outcomes"]["error"]
    # The three runs ran one command, the one the report names (the JUnit path, under /tmp, aside).
    command = run["command"].split(" --junitxml=")[0]
    assert {suite(other)["command"].split(" --junitxml=")[0] for other in RUNS} == {command}
    assert f"`{command}`" in REPORT


@pytest.mark.parametrize("label", RUNS)
def test_each_summary_is_its_saved_junit(label):
    """The summary's counts and sum are those of the run's own JUnit record, saved beside it."""
    with gzip.open(EVIDENCE / f"suite-{label}-junit.xml.gz") as handle:
        cases = list(ET.parse(handle).getroot().iter("testcase"))
    run = suite(label)
    assert len(cases) == run["tests"] == sum(run["outcomes"].values())
    assert round(sum(float(case.get("time", 0)) for case in cases)) == run["sum_test_seconds"]
    failed = sum(any(child.tag in ("failure", "error") for child in case) for case in cases)
    assert failed == run["outcomes"]["failed"] + run["outcomes"]["error"]


def test_the_failures_and_cpu_seconds_stated_are_saved():
    assert suite("before")["failed"] == ["tests/test_difffuzz.py::test_ci_run"]
    assert suite("after-cold")["failed"] == ["tests/test_nested_pytest.py::test_every_pytest_command_is_built_by_the_builder"]
    assert suite("after-warm")["failed"] == []
    assert f"at load up to {suite('before')['load']['max']:.1f}" in REPORT
    totals = {}
    for label in ("after-cold", "after-warm"):
        cpu = suite(label)["properties"]["tests/test_difffuzz.py::test_ci_run"]["cpu_seconds"]
        parts = json.loads(cpu.replace("'", '"'))
        totals[label] = round(parts["python"] + parts["children"], 1)
        assert totals[label] > 300  # the old limit would have failed this run
    assert f"recorded {totals['after-cold']:.1f} s (cold) and {totals['after-warm']:.1f} s (warm) of CPU" in REPORT


def test_the_per_test_times_stated_are_saved():
    corpus = "tests/test_wire_gate_corpus.py::test_gate_corpus_holds_every_test_input_of_every_unit"
    times = [suite(label)["watched"][corpus] for label in RUNS]
    assert "took {:,.1f} s before, {:,.1f} s cold and {:,.1f} s warm".format(*times) in REPORT
    domain = "tests/test_enum_domains.py::test_every_field_keeps_its_domain"
    assert f"took {suite('before')['watched'][domain]:,.1f} s as one test" in REPORT
    shards = [max(time for name, time in suite(label)["watched"].items() if name.startswith(domain + "["))
              for label in ("after-cold", "after-warm")]
    assert "longest shard took {:,.1f} s cold and {:,.1f} s warm".format(*shards) in REPORT
    assert all(name.startswith(domain + "[") for label in ("after-cold", "after-warm")
               for name in suite(label)["watched"] if name.startswith(domain))


def test_the_warm_run_read_the_stored_record():
    """A hit refreshes its entry's time and stores nothing: during the warm run one entry's time changed and
    no entry was written."""
    cache = evidence("run-cache.json")
    run = cache["after_warm_run"]
    assert run["commit"] == suite("after-warm")["commit"]
    during = [entry for entry in cache["entries"] if run["started"] <= entry["modified"] <= run["ended"]]
    assert len(during) == 1 and during[0]["entry"].endswith(".json.gz")
    assert all(entry["modified"] < run["started"] for entry in cache["entries"] if entry not in during)


def test_the_work_table_is_the_saved_run_and_the_limits():
    run = evidence("difffuzz-ci-work.json")
    for kind, limit in difffuzz.WORK_LIMIT.items():
        assert f"| {kind} | {run['work'][kind]:,} | {limit:,} |" in REPORT
        assert 1.2 <= limit / run["work"][kind] <= 1.3, kind  # "about 1.25 times"
    assert set(run["work"]) == set(difffuzz.WORK_LIMIT)
    mutants = sum(sum(counts.values()) for counts in run["mutants"].values())
    assert run["work"]["inputs"] == mutants + run["baseline_entries"]
    assert (f"The {run['work']['inputs']:,} inputs are the {mutants:,} sampled mutants plus the "
            f"{run['baseline_entries']} baseline entries") in REPORT
    assert f"took {sum(run['cpu_seconds'].values()):.1f} CPU seconds" in REPORT
    # The counts of the comment beside WORK_LIMIT are this run's.
    source = (ROOT / "tools/difffuzz.py").read_text()
    work = run["work"]
    assert (f"({work['inputs']:,} inputs, {work['python_calls']:,} Python calls, {work['runner_requests']} runner "
            f"requests with {work['runner_cases']:,}") in source.replace("\n# ", " ")


def test_every_seeded_bug_is_in_the_table_with_tests_that_exist():
    bugs = evidence("seeded-bugs.json")["bugs"]
    pinned = set(json.loads((ROOT / "tools/gate-collection.json").read_text()))
    assert [bug["id"] for bug in bugs] == [f"M{i}" for i in range(1, len(bugs) + 1)]
    for bug in bugs:
        assert (ROOT / bug["file"]).is_file()
        assert all(test in pinned for test in bug["failed"]), bug["failed"]
        count = len(bug["failed"])
        assert f"| {bug['id']} | {bug['file']} |" in REPORT
        assert REPORT.split(f"| {bug['id']} | {bug['file']} |")[1].split("\n")[0].endswith(
            f"| {count} test{'s' if count > 1 else ''} |"), bug["id"]


def test_the_commit_list_is_the_saved_one():
    saved = evidence("commits.json")
    assert saved["range"] == "main..HEAD --no-merges"
    listed = REPORT.split("## Commits")[1]
    lines = [line[2:] for line in listed.splitlines() if line.startswith("- ")]
    assert lines == [f"{commit['sha'][:8]} {commit['subject']}" for commit in reversed(saved["commits"])]
    # Every suite run's commit is the base or a commit of the branch.
    shas = {commit["sha"] for commit in saved["commits"]}
    assert suite("before")["commit"].startswith(saved["base"])
    assert {suite(label)["commit"] for label in ("after-cold", "after-warm")} <= shas
