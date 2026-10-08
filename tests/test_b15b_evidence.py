"""Recompute batch 15b report numbers from saved evidence, never live Git."""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/lean-first/b15b"
EVIDENCE = HERE / "evidence"
PROPERTIES = ("order", "first_witness", "charging", "counts", "exhaustion", "deadline")


def saved(name: str):
    return json.loads((EVIDENCE / name).read_text())


def report() -> str:
    return (HERE / "REPORT.md").read_text()


def _rule3():
    spec = importlib.util.spec_from_file_location("b15b_rule3", HERE / "rule3.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _passes(record: dict) -> dict:
    """Each property recomputed from a record's base and head answers, not read from its `passes`."""
    base, head = record["base"], record["head"]
    if "evaluations" in base:
        return {"order": head["models_checked"] == base["models_checked"] and head["status"] == base["status"],
                "first_witness": record["passes"]["first_witness"],  # models are not kept in the record
                "charging": head["evaluations"] == base["evaluations"],
                "counts": head["models_checked"] == base["models_checked"],
                "exhaustion": head["status"] == base["status"] and (
                    base["status"] in ("Found", "NotFound") or head["detail"] == base["detail"]),
                "deadline": head["wall_s"] <= record["deadline_s"]}
    # A prover's order: its emitted status, certificate and step count with Lean's self-replay (review B4).
    return {"order": head["prover"] == base["prover"], "first_witness": head["valid"] == base["valid"],
            "charging": head["steps"] == base["steps"], "counts": head["status"] == base["status"],
            "exhaustion": head["below"] == base["below"], "deadline": head["wall_s"] <= record["deadline_s"]}


def table(rows: list[dict]) -> str:
    """The report's rule-3 table, rendered from the saved rows."""
    lines = ["| Operation | Queries | Order | First witness | Charging | Counts | Exhaustion | Deadline (s) "
             "| Base wall, total / slowest query (s) | Head wall, total / slowest query (s) |",
             "|---|---:|---|---|---|---|---|---:|---:|---:|"]
    for row in rows:
        marks = ["pass" if p not in row["failing"] else f"FAIL ({len(row['failing'][p])})" for p in PROPERTIES]
        lines.append(f"| {row['operation']} | {row['queries']} | " + " | ".join(marks[:5])
                     + f" | {row['deadline_s']:g}: {marks[5]} | {row['base']['wall_s']:.3f} / "
                     f"{row['base']['max_wall_s']:.3f} | {row['head']['wall_s']:.3f} / "
                     f"{row['head']['max_wall_s']:.3f} |")
    return "\n".join(lines)


def test_rule3_rows_are_recomputed_from_the_saved_records():
    record = saved("rule3.json")
    records = [r for r in record["records"] if "passes" in r]
    for r in records:
        assert _passes(r) == r["passes"], r["id"]
    assert _rule3().summary(record["records"]) == record["rows"]
    rows = record["rows"]
    assert [row["operation"] for row in rows] == list(_rule3().OPERATIONS)
    assert record["condition_holds"] == all(row["passes"] for row in rows)
    # Every row is measured on its corpus: the 28 search fixtures (and their guarded and distinguishing
    # variants), the bluedot query, the order queries and the three certificate cohorts.
    queries = {row["operation"]: row["queries"] for row in rows}
    assert queries["countermodel search"] == 28 and queries["guarded countermodel search"] == 56
    assert queries["distinguishing-model search"] == 28 and queries["bluedot countermodel search"] == 1
    assert all(n > 0 for n in queries.values())
    assert table(rows) in report()


def test_certificate_rows_measure_the_whole_cohorts():
    """Every prover query of each cohort generator is a record (review B4: not the first 40 of each)."""
    import sys
    sys.path.insert(0, str(ROOT / "conformance"))
    import certificates
    import closure_certificates
    import order
    records = saved("rule3.json")["records"]
    count = lambda operation: sum(r["operation"] == operation for r in records)
    assert count("order prover replay") == sum(n for _, n in order.GENERATORS.values()) == 690
    assert count("tableau prover replay") >= 320 + 320 + 160
    assert count("closure prover replay") >= len(closure_certificates.reviewer_queries()[1])
    assert certificates.SEED and order.SEED
    proved = [r for r in records if r.get("certificate") is True]
    assert len(proved) == sum(row["queries"] for row in saved("rule3.json")["rows"] if "prover" in row["operation"])
    for r in proved:
        for side in ("base", "head"):
            assert r[side]["prover"]["status"] == "Found" and len(r[side]["prover"]["certificate_sha256"]) == 64
    operations = ("tableau prover replay", "closure prover replay", "order prover replay")
    totals = [count(operation) for operation in operations]
    yielded = [sum(r["operation"] == operation for r in proved) for operation in operations]
    assert (f"{totals[0]}, {totals[1]} and\n{totals[2]} queries, of which {yielded[0]}, {yielded[1]} and "
            f"{yielded[2]} yield a certificate") in report()


def test_the_report_states_the_failing_rows_and_keeps_the_three_duplicates():
    record = saved("rule3.json")
    failing = [row for row in record["rows"] if not row["passes"]]
    assert record["condition_holds"] is False and failing
    text = report()
    for row in failing:
        for prop, ids in row["failing"].items():
            for case in ids:
                r = next(r for r in record["records"] if r["id"] == case and r["operation"] == row["operation"])
                ratio = r["head"]["wall_s"] / r["deadline_s"]
                assert f"{r['head']['wall_s']:.1f} s against its {r['deadline_s']:g} s deadline" in text
                assert f"{ratio:.1f} times" in text
                assert f"base {r['base']['wall_s']:.2f} s" in text
    for kept in ("`eval.rs`", "order evaluator", "Python replay"):
        assert kept in text.split("## Unfinished", 1)[1]


def test_saved_commit_list_and_line_totals_match_frozen_numstat():
    snapshot = saved("change-metrics.json")
    assert re.fullmatch(r"[0-9a-f]{40}\.\.[0-9a-f]{40} --no-merges", snapshot["range"])
    assert snapshot["range"] == snapshot["base"] + ".." + snapshot["implementation_head"] + " --no-merges"
    assert len(snapshot["commits"]) == len(set(snapshot["commits"])) >= 2
    assert snapshot["commits"][-1] == snapshot["implementation_head"]
    files = snapshot["files"]
    totals = snapshot["totals"]
    assert totals["added"] == sum(f["added"] for f in files)
    assert totals["deleted"] == sum(f["deleted"] for f in files)
    assert totals["lean_added"] == sum(f["added"] for f in files if f["path"].endswith(".lean"))
    assert totals["python_decision_deleted"] == sum(
        f["deleted"] for f in files if f["path"].startswith("ve/") and f["path"].endswith(".py"))
    assert totals["rust_deleted"] == sum(
        f["deleted"] for f in files if f["path"].startswith("rust/") and f["path"].endswith(".rs"))
    text = report()
    for label, value in (("Lean lines added", totals["lean_added"]),
                         ("Total lines deleted", totals["deleted"]),
                         ("Python lines deleted in `ve/`", totals["python_decision_deleted"]),
                         ("Rust lines deleted", totals["rust_deleted"])):
        assert f"{label}: **{value}**" in text, label
    assert all(c[:8] in text for c in snapshot["commits"])


def test_saved_corpus_comparison_matches_its_raw_recordings():
    records = saved("ab-recordings.json")
    for side in ("base-ab", "head-ab"):
        digest, rows, size = hashlib.sha256(), 0, 0
        with gzip.open(EVIDENCE / f"{side}.jsonl.gz", "rb") as stream:
            for line in stream:
                json.loads(line)
                digest.update(line)
                size += len(line)
                rows += 1
        assert {"bytes": size, "rows": rows, "sha256": digest.hexdigest()} == records[side]
    comparison = saved("ab-compare.json")
    assert comparison["unlisted"] == 0
    assert sum(comparison["records"].values()) == records["head-ab"]["rows"]
    assert comparison["records"]["pilots/default"] > 0
    text = report()
    assert f"{comparison['totals']['same']:,} of {records['head-ab']['rows']:,}" in text
    assert f"{comparison['records']['pilots/default']} historical pilot rows" in text


def test_saved_fuzz_comparison_does_not_grow_the_baseline():
    comparison = saved("difffuzz-ab.json")
    runs = comparison["runs"]
    assert len(runs) == 15
    assert {row["run"] for row in runs} == {"--ci"} | {f"--deep 1 --seed 202609{day}" for day in range(23, 31)} | {
        f"--deep 1 --seed 202610{day:02d}" for day in range(1, 7)}
    # Rust no longer answers the parser, label and dependency-order surfaces: fewer findings, never more.
    assert all(row["new"][1] <= row["new"][0] and row["baseline_seen"][1] <= row["baseline_seen"][0]
               and row["not_reproduced"] == [0, 0] for row in runs)
    head_only = saved("difffuzz-head-only.json")["runs"]
    assert len(head_only) == len(runs)
    renamed = [entry for run in head_only.values() for entry in run["head_only"]]
    # Every head-only signature is a base finding of the same seed and mutation, with the same Python and
    # Lean answers and Rust gone from its engines.
    for entry in renamed:
        assert entry["base"] is not None and entry["base"] != entry["head"]
        assert {k: v for k, v in entry["base_answers"].items() if k != "rust"} == {
            k: v for k, v in entry["answers"].items() if k != "rust"}
        assert "rust" not in entry["engines"]
    text = report()
    assert f"{len(renamed)} head-only signature" in text
    assert "no head-only signature that is a new disagreement" in text


def test_saved_mutants_each_fail_their_named_tests():
    mutants = (EVIDENCE / "mutants.txt").read_text()
    commit = re.match(r"source commit: ([0-9a-f]{40}); clean: True\n", mutants)
    assert commit is not None
    names = re.findall(r"^## (.+)$", mutants, re.M)
    assert len(names) >= 6 and names[-1] == "restored"
    for name in names[:-1]:
        part = mutants.split(f"## {name}\n", 1)[1].split("\n## ", 1)[0]
        assert "build exit: 0; focused pytest exit: 1" in part, name
        assert "FAILED " in part, name
        assert f"`{name}`" in report(), name
    restored = mutants.split("## restored\n", 1)[1]
    assert "clean build exit: 0; focused pytest exit: 0" in restored and "FAILED" not in restored
