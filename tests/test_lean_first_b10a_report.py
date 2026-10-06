"""Lean-first batch 10a: the tables of `docs/lean-first/b10a/DELTA.md` are rendered from the evidence files
(build checklist 20), the corpus A/B found no difference, every paired run exited cleanly, and every seeded bug
was caught (build checklist 13)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B10A = ROOT / "docs/lean-first/b10a"


def _report():
    spec = importlib.util.spec_from_file_location("lean_first_b10a_report", B10A / "report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tool(name):
    spec = importlib.util.spec_from_file_location(name, B10A / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _evidence(name):
    return json.loads((B10A / "evidence" / name).read_text())


def test_delta_tables_are_generated_from_the_evidence():
    report = _report()
    text = (B10A / "DELTA.md").read_text()
    assert report.BEGIN in text and report.END in text
    assert text.split(report.BEGIN, 1)[1].split(report.END, 1)[0] == report.render()


def test_the_ab_found_no_difference_over_every_corpus():
    compare, records = _evidence("ab-compare.json"), _evidence("ab-records.json")
    assert compare["differences"] == [] and compare["unlisted"] == 0
    assert set(compare["totals"]) == {"same"} and compare["totals"]["same"] == sum(compare["records"].values())
    assert {name.split("/")[0] for name in compare["records"]} == {"conformance", "discourse", "pilots", "probe",
                                                                  "readings"}
    assert records["base"]["by_corpus"] == records["head"]["by_corpus"] == compare["records"]


def test_fourteen_date_seeds_preserve_the_differential_result():
    evidence = _evidence("fuzzer-seeds.json")
    assert evidence["base_commit"].startswith("2ce1134e")
    assert evidence["baseline_sha256"]
    assert [row["seed"] for row in evidence["seeds"]] == [*range(20260921, 20260931),
                                                           *range(20261001, 20261005)]
    assert all(not row["differences"] for row in evidence["seeds"])
    assert all(row["base_exit"] == row["head_exit"] for row in evidence["seeds"])
    assert all(row["base_new"] == row["head_new"] for row in evidence["seeds"])
    assert all(row["base_not_reproduced"] == row["head_not_reproduced"] == 0
               for row in evidence["seeds"])
    assert all(sum(sum(counts.values()) for counts in row["mutants"].values()) > 25000
               for row in evidence["seeds"])
    assert all(row["base_trace"] == row["head_trace"] and
               {name: trace["count"] for name, trace in row["base_trace"].items()} ==
               {name: sum(counts.values()) for name, counts in row["mutants"].items()}
               for row in evidence["seeds"])


def test_fuzzer_gate_detects_changed_verdicts_with_equal_summaries(tmp_path, monkeypatch):
    """Recheck B: the real report generator can retain identical totals and finding signatures when
    Lean's per-input verdict changes. The preservation gate must detect either kind of change."""
    from tools import difffuzz as df

    gate, tracer = _tool("fuzzer_gate"), _tool("trace_fuzzer")
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"format": df.FORMAT, "entries": []}))
    monkeypatch.setattr(df, "sample", lambda surface, seeds, *args: [(seed, []) for seed in seeds])
    monkeypatch.setattr(df, "MINIMISE_LIMIT", 0)

    class VerdictProbe(df.Surface):
        name = "requests"

        def __init__(self, values, all_engines):
            self.values, self.all_engines = values, all_engines

        def seeds(self):
            return [df.Seed("requests", "core/evaluate", "same-input", {"id": "same-input"})]

        def answers(self, items):
            return [{engine: df.ok({"values": self.values if self.all_engines or engine == "lean"
                                    else [True, True]}) for engine in df.ENGINES} for _ in items]

        def text_fixed(self, *args):
            return False

    def report(values, all_engines):
        surface = VerdictProbe(values, all_engines)
        result, trace = tracer.trace_run(df, lambda: df._fuzz(
            {"requests": surface}, ["requests"], 1, 20260921, baseline, False, lambda _: None))
        result["trace"], result["exit"] = trace, int(not result["passed"])
        assert trace["requests"]["count"] == sum(result["mutants"]["requests"].values())
        return result

    for all_engines in (False, True):
        base, head = report([True, False], all_engines), report([False, True], all_engines)
        assert all(base[key] == head[key] for key in gate.COMPARE)
        assert {entry["signature"] for entry in base["new"]} == \
               {entry["signature"] for entry in head["new"]}
        assert base["trace"]["requests"]["inputs_sha256"] == head["trace"]["requests"]["inputs_sha256"]
        assert base["trace"]["requests"]["answers_sha256"] != head["trace"]["requests"]["answers_sha256"]
        assert gate.compare(base, head) == ["trace"]


def test_every_timed_run_exited_cleanly_on_both_sides():
    runs = _evidence("timing-route.json")["runs"] + _evidence("timing.json")["runs"]
    assert runs and all(run["exit"] == 0 for run in runs)
    for what in {run["what"] for run in runs}:
        assert {run["side"] for run in runs if run["what"] == what} == {"base", "head"}


def test_every_seeded_bug_was_caught():
    bugs = _evidence("seeded-bugs.json")
    assert len(bugs) >= 3
    for name, result in bugs.items():
        assert result.get("build") == "failed" or (result["returncode"] == 1 and result["failed"]), name
