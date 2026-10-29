"""A merged gate is a full gate only after every planned test was accounted for."""
from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools import batch_evidence, gate, gate_collection, gate_shards, test_schedule


IDS = ["tests/a.py::test_one", "tests/a.py::test_two", "tests/b.py::test_skip",
       "tests/c.py::test_three", "tests/d.py::test_four"]
POLICY = {"optional_tests": [{"nodeid": "tests/b.py::test_skip", "reason": "optional"}],
          "deselected_tests": []}
OUTCOMES = {node: ({"outcome": "skipped", "reason": "optional"} if node.endswith("test_skip")
                   else {"outcome": "passed"}) for node in IDS}


def records(n):
    estimates = test_schedule.Estimates({IDS[0]: 9.0, IDS[1]: 2.0, IDS[2]: 5.0, IDS[3]: 3.0}, 0.1)
    plan = gate_shards.plan(IDS, estimates, n)
    rows = []
    for k in range(1, n + 1):
        ran = gate_shards.share(plan, k)
        events = {"collected": ran, "selected": ran, "deselected": [], "collection_reports": [],
                  "tests": {node: OUTCOMES[node] for node in ran}}
        row = {"schema_version": 1, "commit_sha": "a" * 40, "tree_sha": "b" * 40,
               "dirty": False, "mode": "shard", "status": "shard-passed",
               "runner": {"system": "Linux", "machine": "x86_64", "node": f"worker{k}"},
               "toolchains": {"lean": "4.24.0", "paths": {"uv": f"/tmp/worker{k}/uv"}},
               "environment": {}, "stages": list(gate.REQUIRED_STAGES) if k == 1 else
               ["toolchains", "lean_build", "pytest"], "counts": {}, "skips": [], "failures": [],
               "collection": {"collected_zlib": gate_collection.encode_ids(IDS), "head_ids": len(IDS)},
               "shard": {"k": k, "n": n, "digest": plan["digest"], "plan": plan,
                         "collected": plan["collected"], "ran": ran, "seconds": 1.0},
               "pytest_seconds": {node: float(index + 1) for index, node in enumerate(ran)},
               "quarantine": {"enabled": True, "day": "2026-10-12", "active": [], "expired": [],
                              "retried": {}}}
        gate.interpret_pytest(row, events, POLICY, ran, families=())
        if k == 1:
            row["counts"].update(rust_passed=2, rust_ignored=0)
        rows.append(row)
    return rows


@pytest.mark.parametrize("n", [1, 2, 3])
def test_merged_counts_and_collection_match_unsharded_fixture(n):
    rows = records(n)
    merged = gate_shards.merge_records(rows)
    full = {"counts": {}, "skips": [], "failures": []}
    gate.interpret_pytest(full, {"collected": IDS, "selected": IDS, "deselected": [],
                                 "collection_reports": [], "tests": OUTCOMES}, POLICY, IDS, families=())
    assert merged["status"] == "passed", merged["failures"]
    assert gate_collection.decode_ids(merged["collection"]["collected_zlib"]) == IDS
    assert {key: merged["counts"][key] for key in full["counts"]} == full["counts"]
    assert merged["failures"] == full["failures"]
    assert merged["skips"] == full["skips"]
    assert merged["durations"]["tests"] == len(IDS)


def test_failed_test_is_reported_in_merged_full_record():
    rows = records(2)
    target = IDS[-1]
    owner = next(row for row in rows if target in row["shard"]["ran"])
    owner["status"] = "failed"
    owner["counts"]["passed"] -= 1
    owner["counts"]["failed"] += 1
    owner["failures"].append({"stage": "pytest", "nodeid": target, "reason": "assert false"})
    merged = gate_shards.merge_records(rows)
    assert merged["status"] == "failed"
    assert merged["counts"]["failed"] == 1
    assert merged["failures"] == owner["failures"]


@pytest.mark.parametrize("missing", [1, 2, 3])
def test_merge_cli_refuses_any_missing_shard(tmp_path, missing):
    paths = []
    for index, row in enumerate(records(3), 1):
        if index != missing:
            path = tmp_path / f"shard-{index}.json"
            path.write_text(json.dumps(row))
            paths.append(path)
    output = tmp_path / "merged.json"
    done = subprocess.run([sys.executable, str(gate.ROOT / "tools/gate.py"), "--merge-shards",
                           *(str(path) for path in paths), "--output", str(output)],
                          cwd=gate.ROOT, capture_output=True, text=True)
    assert done.returncode == 1
    merged = json.loads(output.read_text())
    assert merged["status"] == "failed"
    assert "missing shard" in merged["failures"][0]["reason"]


def test_merge_cli_writes_one_full_record(tmp_path):
    paths = []
    for index, row in enumerate(records(2), 1):
        path = tmp_path / f"shard-{index}.json"
        path.write_text(json.dumps(row))
        paths.append(path)
    output = tmp_path / "gate-result.json"
    done = subprocess.run([sys.executable, str(gate.ROOT / "tools/gate.py"), "--merge-shards",
                           *(str(path) for path in reversed(paths)), "--output", str(output)],
                          cwd=gate.ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    merged = json.loads(output.read_text())
    assert merged["status"] == "passed"
    assert merged["mode"] == "full"
    assert merged["stages"] == list(gate.REQUIRED_STAGES)
    assert merged["shards"]["n"] == 2
    assert [row["k"] for row in merged["shards"]["runs"]] == [1, 2]


@pytest.mark.parametrize("change,word", [
    (lambda row: row.update(commit_sha="c" * 40), "commit"),
    (lambda row: row.update(tree_sha="c" * 40), "tree"),
    (lambda row: row["shard"].update(digest="0" * 64), "digest"),
    (lambda row: row["shard"].update(n=3), "N"),
    (lambda row: row["runner"].update(machine="aarch64"), "platform"),
    (lambda row: row["toolchains"].update(lean="other"), "toolchains"),
    (lambda row: row["quarantine"].update(enabled=False), "quarantine"),
    (lambda row: row["shard"].update(ran=[]), "ran IDs"),
    (lambda row: row["shard"].update(collected="bad"), "collection"),
    (lambda row: row["collection"].update(collected_zlib="bad"), "full collection"),
    (lambda row: row["shard"].update(n=True), "N"),
    (lambda row: row["counts"].update(selected=True), "incomplete test events"),
    (lambda row: row.update(collection=[]), "full collection"),
    (lambda row: row.update(quarantine=[]), "quarantine"),
    (lambda row: row["quarantine"].update(retried=[]), "quarantine"),
    (lambda row: row.update(mode="full"), "schema or mode"),
    (lambda row: row.update(status="failed"), "without a reason"),
])
def test_merge_refuses_mismatched_or_empty_shard(change, word):
    rows = records(2)
    change(rows[1])
    merged = gate_shards.merge_records(rows)
    assert merged["status"] == "failed"
    assert word in merged["failures"][0]["reason"]


def test_merge_refuses_missing_or_malformed_test_events():
    rows = records(2)
    owner = next(row for row in rows if row["counts"]["skipped"])
    owner["skips"] = []
    merged = gate_shards.merge_records(rows)
    assert merged["status"] == "failed"
    assert "incomplete skip events" in merged["failures"][0]["reason"]

    rows = records(2)
    owner = next(row for row in rows if row["counts"]["skipped"])
    owner["skips"][0]["allowed"] = 1
    merged = gate_shards.merge_records(rows)
    assert merged["status"] == "failed"
    assert "incomplete skip events" in merged["failures"][0]["reason"]

    rows = records(2)
    owner = next(row for row in rows if IDS[-1] in row["shard"]["ran"])
    owner["counts"]["passed"] -= 1
    owner["counts"]["failed"] += 1
    owner["status"] = "failed"
    owner["failures"] = [{"stage": "gate", "reason": "suite failed"}]
    merged = gate_shards.merge_records(rows)
    assert merged["status"] == "failed"
    assert "incomplete failure events" in merged["failures"][0]["reason"]


@pytest.mark.parametrize("mutation", [
    lambda rows: next(row for row in rows if row["skips"])["skips"][0].update(allowed=False),
    lambda rows: rows[0]["counts"].update(rust_passed=0),
    lambda rows: rows[0]["counts"].update(rust_passed=True),
    lambda rows: rows[0]["counts"].update(rust_ignored=1),
    lambda rows: rows[0]["counts"].update(rust_ignored=False),
    lambda rows: rows[0]["quarantine"]["retried"].update({IDS[0]: {"suite": "failed", "alone": "failed"}}),
    lambda rows: rows[0]["quarantine"]["retried"].update({IDS[0]: {"suite": "failed", "alone": "passed"},
                                                            IDS[1]: {"suite": "failed", "alone": "no result"}}),
])
def test_passing_merge_rejects_contradictory_skip_retry_and_native_evidence(mutation):
    rows = records(2)
    assert gate_shards.merge_records(rows)["status"] == "passed"
    mutation(rows)
    merged = gate_shards.merge_records(rows)
    assert merged["status"] == "failed"
    assert merged["failures"][0]["stage"] == "shards"


def test_merge_accepts_retry_of_active_quarantine_test():
    rows = records(2)
    for row in rows:
        row["quarantine"].update(day="2026-10-12", active=[IDS[0]])
    owner = next(row for row in rows if IDS[0] in row["shard"]["ran"])
    owner["quarantine"]["retried"][IDS[0]] = {"suite": "failed", "alone": "passed"}
    merged = gate_shards.merge_records(rows)
    assert merged["status"] == "passed", merged["failures"]
    assert merged["quarantine"]["retried"] == owner["quarantine"]["retried"]


def test_merge_accepts_disabled_quarantine_without_retries():
    rows = records(2)
    for row in rows:
        row["quarantine"] = {"enabled": False, "active": [], "expired": [], "retried": {}}
    merged = gate_shards.merge_records(rows)
    assert merged["status"] == "passed", merged["failures"]


@pytest.mark.parametrize("change", [
    lambda rows: [row["quarantine"].update(enabled=False) for row in rows],
    lambda rows: [row["quarantine"].update(active=[IDS[1]]) for row in rows],
    lambda rows: [row["quarantine"].update(active=[]) for row in rows],
    lambda rows: [row["quarantine"].update(enabled=0) for row in rows],
])
def test_merge_refuses_retry_without_enabled_active_quarantine(change):
    rows = records(2)
    for row in rows:
        row["quarantine"].update(day="2026-10-12", active=[IDS[0]])
    owner = next(row for row in rows if IDS[0] in row["shard"]["ran"])
    owner["quarantine"]["retried"][IDS[0]] = {"suite": "failed", "alone": "passed"}
    change(rows)
    merged = gate_shards.merge_records(rows)
    assert merged["status"] == "failed"
    assert merged["failures"][0]["stage"] == "shards"


def test_plan_is_repeatable_and_partitions_each_collected_id_once():
    estimates = test_schedule.Estimates({IDS[0]: 9.0, IDS[2]: 5.0}, 0.1)
    first = gate_shards.plan(IDS, estimates, 3)
    assert first == gate_shards.plan(IDS, estimates, 3)
    assert gate_shards.validate_plan(first) == IDS
    assert sorted(node for k in range(1, 4) for node in gate_shards.share(first, k)) == sorted(IDS)
    assert all(gate_shards.share(first, k) for k in range(1, 4))


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("live", [False, True])
def test_gate_runs_full_collection_and_only_its_share(tmp_path, monkeypatch, n, live):
    live_id = "tests/live.py::test_live"
    all_ids = [*IDS, live_id] if live else IDS
    root = tmp_path / "project"
    root.mkdir()
    (root / "rust/target/release").mkdir(parents=True)
    rust = root / "rust/target/release/ve"
    rust.write_bytes(b"binary")
    rust.chmod(0o755)
    for name in gate.LEAN_BINARIES:
        binary = root / "lean/.lake/build/bin" / name
        binary.parent.mkdir(parents=True, exist_ok=True)
        binary.write_bytes(b"binary")
        binary.chmod(0o755)
    policy = root / "policy.json"
    policy.write_text(json.dumps({"version": 1, **POLICY,
                                  "deselected_tests": ([{"nodeid": live_id,
                                                         "reason": "Calls real model CLIs; excluded by the non-live gate."}]
                                                       if live else [])}))
    monkeypatch.setattr(gate, "ROOT", root)
    monkeypatch.setattr(gate, "POLICY", policy)
    monkeypatch.setattr(gate, "REQUIRED_FAMILIES", ())
    monkeypatch.setattr(gate, "source_identity", lambda env: ("a" * 40, False))
    monkeypatch.setattr(gate, "tree_identity", lambda env: "b" * 40)
    monkeypatch.setattr(gate, "check_toolchains", lambda result, env: None)
    monkeypatch.setattr(gate, "check_python_project", lambda result, env: None)
    monkeypatch.setattr(gate.lake_outputs, "drop_stale", lambda *args, **kwargs: None)
    monkeypatch.setattr(gate.lake_outputs, "stale", lambda *args, **kwargs: [])
    monkeypatch.setattr(gate.rust_build, "pinned_digests", lambda path: {gate.rust_build.digest(rust)})
    monkeypatch.setattr(gate, "read_trust", lambda path: {})
    monkeypatch.setattr(gate, "record_collection", lambda *args, **kwargs: "written")
    monkeypatch.setattr(gate, "base_collection", lambda result, *args:
                        (result.update(collection={"base": "c" * 40, "base_ids": len(all_ids)}) or all_ids, None))
    monkeypatch.setattr(gate.gate_shards.gate_collection, "merge_base", lambda **kwargs: "c" * 40)
    monkeypatch.setattr(gate, "suite_durations", lambda result, env, path:
                        path.write_text(test_schedule.durations_text({IDS[0]: 9, IDS[2]: 5}, source="fixture")))

    @contextmanager
    def cargo(env, target_dir):
        yield env, root

    monkeypatch.setattr(gate, "isolated_cargo", cargo)
    runs = []

    def fake_command(args, *, env, stage, cwd=None):
        if stage == "native Rust tests":
            return "test result: ok. 2 passed; 0 failed; 0 ignored;"
        if stage == gate.TRUST_STAGE:
            Path(args[-1]).write_text("{}")
        if stage == "Python collection":
            Path(env["VE_GATE_PYTEST_RESULT"]).write_text(json.dumps({
                "collected": all_ids, "selected": IDS, "deselected": [live_id] if live else [],
                "collection_reports": []}))
        if stage == "Python suite":
            selected = (json.loads(Path(env["VE_GATE_PYTEST_IDS_FILE"]).read_text())
                        if "VE_GATE_PYTEST_IDS_FILE" in env else IDS)
            runs.append(selected)
            Path(env["VE_GATE_PYTEST_RESULT"]).write_text(json.dumps({
                "tests": {node: OUTCOMES[node] for node in selected},
                "seconds": {node: 1.0 for node in selected}, "workers": {"gw0": selected}}))
        return ""

    monkeypatch.setattr(gate, "command", fake_command)
    unsharded = tmp_path / "unsharded.json"
    monkeypatch.setattr(sys, "argv", ["gate.py", "--output", str(unsharded)])
    assert gate.main() == 0
    baseline = json.loads(unsharded.read_text())
    rows = []
    for k in range(1, n + 1):
        output = tmp_path / f"shard{k}.json"
        monkeypatch.setattr(sys, "argv", ["gate.py", "--shard", f"{k}/{n}", "--output", str(output)])
        assert gate.main() == 0
        rows.append(json.loads(output.read_text()))
    assert rows[0]["stages"] == list(gate.REQUIRED_STAGES)
    assert all(row["stages"] == ["toolchains", "lean_build", "pytest"] for row in rows[1:])
    assert sorted(node for run in runs[1:] for node in run) == sorted(IDS)
    assert all(row["shard"]["collected"] == rows[0]["shard"]["collected"] for row in rows)
    merged = gate_shards.merge_records(rows)
    assert merged["status"] == baseline["status"] == "passed"
    assert merged["counts"] == baseline["counts"]
    assert merged["failures"] == baseline["failures"]
    assert merged["skips"] == baseline["skips"]
    assert merged["collection"]["collected_zlib"] == baseline["collection"]["collected_zlib"]
    assert gate_collection.decode_ids(merged["collection"]["collected_zlib"]) == sorted(all_ids)
    assert merged["counts"]["deselected"] == int(live)
    assert batch_evidence.gate_problems("a" * 40, merged) == []
    note = gate_collection.record_text("a" * 40, "b" * 40, all_ids, result=merged)
    assert gate_collection.parse_record(note, "a" * 40, "b" * 40) == sorted(all_ids)
