"""Rule-3 work units count every candidate Lean evaluated, including a batch suffix."""
import importlib.util
import json
from pathlib import Path

from ve.backends import rust_jsonl

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rule3_measurement", ROOT / "docs/lean-first/b2/rule3.py")
rule3 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rule3)


def test_search_1_2_counts_all_three_evaluated_candidates(tmp_path, monkeypatch):
    query = next(row for row in json.loads((ROOT / "conformance/search.json").read_text())
                 if row["id"] == "search_1_2")
    enumerator = tmp_path / "enumerator"
    enumerator.write_text("#!/usr/bin/env python3\n"
                          "import json, sys\n"
                          "sys.stdin.readline()\n"
                          "print(json.dumps({'models': [{}, {}, {}], 'exhausted': True}), flush=True)\n")
    enumerator.chmod(0o755)
    monkeypatch.setattr(rust_jsonl, "run", lambda case, **kw:
                        {"status": "Found", "models_checked": 1, "evaluations": 1, "model": None})

    class Meter:
        def run(self, mode, cases):
            values = [[True, False], [True, True], [True, True]] if cases[0]["ast"] != [["top"]] else [[True]] * 3
            return ([{"status": "ok", "values": value} for value in values],
                    {"lean_cpu": 0.003, "wall": 0.004, "bytes": 100, "requests": 1})

    row = rule3.search_query(Meter(), query, 256, enumerator)
    assert row["candidates"] == 1
    assert row["evaluated_candidates"] == 3
    assert row["lean_cpu_per_candidate_ms"] == 1.0


def test_rule3_report_numbers_come_from_record():
    record = json.loads((ROOT / "docs/lean-first/b2/rule3.json").read_text())
    report = (ROOT / "docs/lean-first/b2/DELTA.md").read_text()
    blue = next(row for row in record["search"] if row["corpus"] == "bluedot")
    policy = record["agent_policy_evaluations"]
    certificates = record["agent_policy_certificates"]
    assert f"load {record['load']}" in report
    assert f"{blue['lean_cpu_s']:.3f} s" in report
    assert f"{blue['decoding_cpu_s']:.3f} / {blue['semantic_cpu_s']:.3f}" in report
    assert f"{policy['cases']:,} Rust evaluation cases" in report
    assert f"in {policy['requests']} requests" in report
    assert f"{certificates['steps']} nodes" in report
