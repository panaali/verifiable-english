"""Batch 16b's report numbers come from its saved evidence (docs/lean-first/b16b/evidence/), never from live git:
the generated block of DELTA.md is regenerated, the prose numbers are checked against the same files, and the
evidence itself must show what the gate requires."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/lean-first/b16b"
EVIDENCE = HERE / "evidence"
sys.path.insert(0, str(HERE))

import report  # noqa: E402


def load(name):
    return json.loads((EVIDENCE / name).read_text())


def test_generated_block_is_the_saved_evidence():
    text = (HERE / "DELTA.md").read_text()
    assert text[text.index(report.BEGIN):text.index(report.END) + len(report.END)] == report.block()


def test_scope_is_a_saved_commit_list():
    scope = load("scope.json")
    assert scope["range"] == "main..HEAD --no-merges" and scope["captured_head"] in scope["commits"]
    assert all(re.fullmatch(r"[0-9a-f]{40}", c) for c in [scope["base"], *scope["commits"]])
    assert {row["commit"] for row in scope["numstat"]} <= set(scope["commits"])
    metrics = report.metrics()
    assert metrics["lean_added"] > 0 and metrics["python_added"] > 0


def test_ab_has_no_unlisted_difference_and_lists_only_other_decoders_texts():
    ab, delta = load("ab.json"), json.loads((HERE / "delta.json").read_text())
    assert ab["unlisted"] == 0
    assert ab["listed"] == {klass: len(entries) for klass, entries in delta.items()}
    assert sum(ab["totals"].values()) == sum(ab["records"].values())
    assert delta["availability"] == []
    for entry in delta["order"] + delta["verdict"]:
        assert entry["corpus"] == "document" and entry["owner"] in ("environment", "formula", "admission")
        assert "raised" in entry["base"] and "raised" in entry["head"]
    for entry in delta["verdict"]:
        assert entry["base"]["raised"]["code"] == entry["head"]["raised"]["code"]
    assert {entry["corpus"] for entry in delta["unavailable"]} == {"pilots"}


def test_fuzzer_baseline_does_not_grow():
    fuzz = load("difffuzz.json")
    assert fuzz["ci"]["passed"] and fuzz["ci"]["new"] == 0 and fuzz["ci"]["unreviewed"] == 0
    assert fuzz["ci"]["document_inputs"]["one-fault"] > 0
    assert len(fuzz["seeds"]) == 14
    assert all(row["head_only"] == 0 and row["head_new"] == row["base_new"] for row in fuzz["seeds"])


def test_every_seeded_fault_was_caught_and_restored():
    mutants = load("mutants.json")
    assert mutants["service_build_restored"] is True
    rows = mutants["mutants"]
    assert len(rows) >= 3 and all(row["caught"] and row["exit"] == 1 for row in rows)
    tests = (ROOT / "tests/test_document_lean_switch.py").read_text()
    assert all(f"def {row['test']}(" in tests for row in rows)
    assert all(row["failed"][0].split("::")[1].startswith(row["test"]) for row in rows)


def test_prose_numbers_are_the_saved_ones():
    text = " ".join((HERE / "DELTA.md").read_text().split())
    share = load("share.json")
    pilots, rights, defaults, documents = (share[k] for k in ("pilots", "rights", "norm_defaults", "document"))
    assert (f"Lean decides {pilots['lean']} of the {pilots['documents']} pilot documents, none of the "
            f"{rights['documents']:,} rights or {defaults['documents']:,} norm-defaults corpus documents, and "
            f"{documents['lean']} of the {documents['documents']:,} document-corpus texts") in text
    assert rights["lean"] == defaults["lean"] == 0
    restricted = "retained: front matter outside the restricted JSON reader"
    assert (f"keep {documents['other'][restricted]} document-corpus texts, {rights['other'][restricted]} rights "
            f"documents and {pilots['other'][restricted]} pilots") in text
    assert f"norm-defaults {pilots['other']['retained: document checks under norm-defaults@0 need its Lean profile route']} pilots" in text
    ab = load("ab.json")
    assert f"{ab['listed']['wording']} wording pairs and {ab['listed']['order']} order records" in text
    assert f"{ab['listed']['verdict']} verdict-class records" in text


def test_suite_line_is_the_saved_gate_run():
    suite = load("suite.json")
    assert suite["status"] == "passed" and suite["dirty"] is False and suite["failures"] == []
    assert suite["counts"]["failed"] == 0 and suite["stages"][-1] == "pytest"
    counts = suite["counts"]
    line = (f"`tools/gate.py` at `{suite['commit'][:8]}` in a clean worktree: passed, {counts['passed']:,} passed, "
            f"{counts['skipped']} allowed skips, 0 failed of {counts['collected']:,} collected")
    assert line in " ".join((HERE / "REPORT.md").read_text().split())
    assert suite["commit"] == load("scope.json")["captured_head"]
