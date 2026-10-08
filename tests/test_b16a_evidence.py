"""Batch 16a report checks read committed snapshots, never moving Git refs."""

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/lean-first/b16a/evidence"
REPORT = ROOT / "docs/lean-first/b16a/REPORT.md"


def saved(name):
    return json.loads((EVIDENCE / name).read_text())


def scope_and_report():
    scope = saved("scope.json")
    report = REPORT.read_text()
    assert scope["range"] == "main..HEAD --no-merges"
    assert scope["commits"] and scope["captured_head"] == scope["commits"][0]
    assert len(scope["commits"]) == len(set(scope["commits"]))
    assert all(re.fullmatch(r"[0-9a-f]{40}", item) for item in scope["commits"])
    assert all(item["commit"] in scope["commits"] for item in scope["files"])
    assert "Source commits (saved): " + ", ".join(scope["commits"]) in report
    return scope, report


def test_report_line_counts_use_saved_main_range():
    scope, report = scope_and_report()
    files = scope["files"]
    assert scope["totals"] == {
        "added": sum(item["added"] for item in files),
        "deleted": sum(item["deleted"] for item in files),
        "lean_added": sum(item["added"] for item in files if item["path"].endswith(".lean")),
        "python_deleted": sum(item["deleted"] for item in files if item["path"].endswith(".py")),
    }
    assert f"Total lines deleted: {scope['totals']['deleted']}" in report
    assert f"Lean lines added: {scope['totals']['lean_added']}" in report
    assert f"Python lines deleted: {scope['totals']['python_deleted']}" in report


def test_report_gate_numbers_use_saved_clean_run():
    scope, report = scope_and_report()
    gate = saved("gate.json")
    counts = gate["counts"]
    assert gate["commit_sha"] == scope["captured_head"]
    assert gate["status"] == "passed" and gate["dirty"] is False
    assert counts["selected"] == counts["passed"] + counts["skipped"] + counts["failed"]
    assert counts["failed"] == 0 and gate["failures"] == []
    assert f"Full gate: passed; {counts['passed']} passed, {counts['skipped']} skipped" in report
    assert f"Rust: {counts['rust_passed']} passed" in report


def test_report_ab_numbers_use_saved_public_outcomes():
    _, report = scope_and_report()
    ab = saved("ab.json")
    assert ab["differences"] == [] and ab["unlisted"] == 0
    assert ab["totals"] == {"same": sum(ab["records"].values())}
    assert f"A/B identical: {ab['totals']['same']} public outcomes" in report
    assert f"Pilots identical: {ab['records']['pilots/default']} documents" in report


def test_report_difffuzz_numbers_use_saved_baselines():
    _, report = scope_and_report()
    ci = saved("difffuzz-ci.json")
    dates = saved("seeds.json")["rows"]
    assert ci["passed"] is True and ci["new"] == []
    assert ci["baseline"]["unreviewed"] == [] and ci["baseline"]["not_reproduced"] == []
    assert len(dates) == 14 and len({item["seed"] for item in dates}) == 14
    assert all(item["head_new"] == item["base_new"] and item["head_only"] == 0
               and item["head_signature_sha256"] == item["base_signature_sha256"]
               for item in dates)
    assert f"CI baseline: {ci['baseline']['entries']} entries, 0 new signatures" in report
    assert f"Date seeds: {len(dates)} paired; {sum(item['head_new'] for item in dates)} inherited signatures; 0 head-only" in report


def test_report_mutants_use_saved_failures():
    _, report = scope_and_report()
    mutants = saved("mutants.json")
    assert len(mutants) >= 3
    assert len({item["mutant"] for item in mutants}) == len(mutants)
    assert all(item["build_exit"] == 0 and item["test_exit"] != 0
               and "FAILED " in item["failure_excerpt"] for item in mutants)
    assert f"Seeded mutants: {len(mutants)} failed as expected" in report
    assert all(item["mutant"] in report for item in mutants)


# ---------------------------------------------------------------- review fix 1 (evidence/fix1)

FIX = EVIDENCE / "fix1"


def fix_saved(name):
    return json.loads((FIX / name).read_text())


def fix_scope_and_report():
    scope = fix_saved("scope.json")
    report = REPORT.read_text()
    assert scope["commits"] and scope["captured_head"] == scope["commits"][0]
    assert all(re.fullmatch(r"[0-9a-f]{40}", item) for item in scope["commits"])
    assert scope["measured_code_head"] in scope["commits"]
    # The commits after the measurement are listed with their files, none of them checker or service code.
    later = scope["commits"][:scope["commits"].index(scope["measured_code_head"])]
    assert sorted(scope["after_measurement"]) == sorted(later)
    assert all(not path.startswith(("ve/", "lean/VE/", "rust/")) for files in scope["after_measurement"].values()
               for path in files)
    assert "Fix commits (saved): " + ", ".join(scope["commits"]) in report
    return scope, report


def test_fix_report_line_counts_are_the_saved_net_diff():
    scope, report = fix_scope_and_report()
    files = scope["net_files"]
    source = [item for item in files if not item["generated"]]
    assert scope["totals"] == {
        "added": sum(item["added"] for item in files), "deleted": sum(item["deleted"] for item in files),
        "source_added": sum(item["added"] for item in source), "source_deleted": sum(item["deleted"] for item in source),
        "lean_added": sum(item["added"] for item in source if item["path"].endswith(".lean")),
        "python_deleted": sum(item["deleted"] for item in source if item["path"].endswith(".py"))}
    totals = scope["totals"]
    assert f"Net lines: {totals['added']} added, {totals['deleted']} deleted" in report
    assert f"{totals['source_added']} added, {totals['source_deleted']} deleted" in report
    assert f"Lean source lines added: {totals['lean_added']}" in report
    assert f"Python lines deleted: {totals['python_deleted']} (bug fixes" in report


def test_fix_report_ab_and_fuzz_numbers_are_saved():
    scope, report = fix_scope_and_report()
    ab = fix_saved("ab.json")
    assert ab["head"] == scope["measured_code_head"] and ab["differences"] == [] and ab["unlisted"] == 0
    assert ab["totals"] == {"same": sum(ab["records"].values())}
    assert f"A/B identical: {ab['totals']['same']} public outcomes" in report
    assert f"pilots identical: {ab['records']['pilots/default']} documents" in report
    ci = fix_saved("difffuzz-ci.json")
    assert ci["passed"] is True and ci["new"] == [] and ci["commit"] == scope["captured_head"]
    assert ci["baseline"]["unreviewed"] == [] and ci["baseline"]["not_reproduced"] == []
    assert sum(ci["corpus"]["document"].values()) > 0 and ci["answers"]["document"]["lean:ok"] > 0
    assert f"Difffuzz CI: {ci['baseline']['entries']} baseline entries, 0 new signatures" in report
    assert f"the `document` surface ran {sum(ci['mutants']['document'].values())} inputs" in report
    deep = fix_saved("deep-document.json")
    assert deep and all(row["passed"] and row["new"] == [] and row["scale"] == 10 for row in deep)
    inputs = sum(sum(row["mutants"].values()) for row in deep)
    assert f"Deep document fuzz: {len(deep)} seeds at 10 times the CI sample, {inputs} inputs, 0 new" in report


def test_fix_report_mutants_are_saved_failures():
    _, report = fix_scope_and_report()
    saved_mutants = fix_saved("mutants.json")
    mutants = saved_mutants["mutants"]
    assert len(mutants) >= 3 and saved_mutants["restored_build_exit"] == 0
    assert len({item["mutant"] for item in mutants}) == len(mutants)
    assert all(item["build_exit"] == 0 and item["test_exit"] != 0 and item["failure_excerpt"].startswith("FAILED ")
               and item["test"].split("::")[1] in item["failure_excerpt"] for item in mutants)
    assert f"Fix seeded mutants: {len(mutants)} failed as expected" in report
    assert all(item["mutant"] in report for item in mutants)


def test_fix_report_suite_numbers_are_the_saved_run():
    scope, report = fix_scope_and_report()
    suite = fix_saved("suite.json")
    totals = suite["totals"]
    assert totals == {k: sum(run[k] for run in suite["runs"]) for k in ("passed", "skipped", "failed")}
    assert totals["failed"] == 0 and suite["rust"]["failed"] == 0
    assert totals["passed"] + totals["skipped"] + len(suite["excluded"]) == suite["collection"]
    # The suite ran on a commit after the captured scope: its later commits are evidence only.
    assert suite["commit"] not in scope["commits"] or suite["commit"] == scope["captured_head"]
    assert (f"{totals['passed']} passed, {totals['skipped']} skipped, {totals['failed']} failed, of the gate's "
            f"{suite['collection']} collected tests") in report
    assert f"Rust: {suite['rust']['passed']} passed." in report
