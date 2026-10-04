"""tools/bench: the CPU-time benchmarks that replaced the suite's speed assertions.

The benchmarks themselves run nightly and on demand (`pytest tools/bench/test_perf.py`),
never here; these tests check that a stored baseline can fail a measurement.
"""
import json
from pathlib import Path

from tools.bench import baseline

ROOT = Path(__file__).resolve().parents[1]
STORED = json.loads((ROOT / "tools/bench/baselines.json").read_text())


def test_a_measurement_over_its_allowance_or_without_a_baseline_fails():
    stored = {"tolerance": 1.0, "slack_seconds": 0.5, "baselines": {"a::cpu": 2.0}}
    assert baseline.allowed(2.0, stored) == 4.5
    assert baseline.over({"a::cpu": 4.5}, stored) == []
    assert baseline.over({"a::cpu": 4.51}, stored) == ["a::cpu: 4.51 CPU s, baseline 2.0, allowed 4.500"]
    assert baseline.over({"b::cpu": 0.0}, stored) == [
        "b::cpu: no baseline (run with --update-baselines and commit it)"]
    assert baseline.updated(stored, {"b::cpu": 1.0})["baselines"] == {"a::cpu": 2.0, "b::cpu": 1.0}


def test_the_stored_baselines_cover_every_benchmark_that_replaced_a_suite_assertion():
    keys = STORED["baselines"]
    assert type(STORED["tolerance"]) is float and type(STORED["slack_seconds"]) is float
    assert all(type(value) is float and value >= 0 for value in keys.values())
    for prefix in ("test_precommit_large_staged_change::", "test_soft_exponential_unfoldings_are_refused_cheaply[",
                   "test_kernel_bounded_batches[w6a-generator]::", "test_kernel_bounded_batches[w6a-route-limits]::"):
        assert any(key.startswith(prefix) for key in keys), prefix


def test_the_testspeed_report_shows_the_recorded_runs():
    """docs/testspeed-report.md: every measured number is regenerated from tools/bench/results."""
    from tools.bench import suite_time
    report = (ROOT / "docs/testspeed-report.md").read_text()

    def block(name):
        return report.split(f"<!-- {name} -->\n", 1)[1].split(f"\n<!-- /{name} -->", 1)[0]
    assert block("runs") == suite_time.table()
    assert block("slowest") == suite_time.slowest("suite-before.json")
    assert block("slowest-after") == suite_time.slowest("suite-after-n32.json")
    assert block("most-cpu") == suite_time.most_cpu("suite-after-auto.json")
