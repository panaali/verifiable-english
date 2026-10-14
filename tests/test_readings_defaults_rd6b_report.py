"""RD-6b report checks against committed evidence, independent of the current git graph."""

from __future__ import annotations

import copy
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/readings-defaults/rd6b"
EVIDENCE = HERE / "evidence"
# The approved branch head, and the ve-integration commit merged into it after review.
RD6B_HEAD = "e1319b36477d9de8cb83b6df4b4d372186cb4b3d"
MERGED_BASE = "f05474685f3df4313d0b264c32cf1cf673a17d97"
RD6B_APPROVED = "6b66f08721003c390f9180ed84dfe911fe9869b6"  # the approved head merged into ve-integration by 8b9927f2


def saved():
    summary = json.loads((EVIDENCE / "summary.json").read_text())
    for name, digest in summary["sha256"].items():
        assert hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() == digest, name
    gate = json.loads((EVIDENCE / "gate-code.json").read_text())
    comparison = json.loads((EVIDENCE / "ab-compare.json").read_text())
    delta = json.loads((EVIDENCE / "ab-delta.json").read_text())
    bench = json.loads((EVIDENCE / "latency.json").read_text())
    mutants = json.loads((EVIDENCE / "seeded-bugs.json").read_text())
    retries = json.loads(gzip.decompress((EVIDENCE / "ab-retries.json.gz").read_bytes()))
    records = {
        side: [json.loads(line) for line in gzip.decompress((EVIDENCE / f"ab-{side}.jsonl.gz").read_bytes()).splitlines()]
        for side in ("base", "head")
    }
    return summary, gate, comparison, delta, bench, mutants, retries, records


def expected_lines(summary, gate, comparison, bench, mutants):
    counts = gate["counts"]
    lean = summary["lean"]
    total = sum(comparison["records"].values())
    lines = [
        f"pinned merge-base commit `{summary['base_merge_commit']}`",
        f"`main` was `{summary['main_at_code_head']}`",
        f"Build completed successfully ({lean['build_jobs']} jobs)",
        f"PASS: {lean['audit_sources']} source files; {lean['audit_theorems']} named theorem declarations",
        f"PASS: {lean['statements']} statements; 0 added, removed or changed",
        f"{lean['rd6b_declarations']} approved declarations; 0 pending",
        f"Full gate on clean code head `{summary['code_head']}`: {counts['passed']} passed, {counts['skipped']} skipped, "
        f"{counts['failed']} failed, of {counts['collected']} collected ({counts['deselected']} live test deselected)",
        f"Rust: {counts['rust_passed']} passed, {counts['rust_ignored']} ignored",
        f"Readings and pilots: {total} records; {comparison['totals']['same']} identical; "
        f"{comparison['totals']['verdict']} route/payload differences; "
        f"{comparison['totals']['wording']} scratch-path wording differences; {comparison['unlisted']} unlisted",
        f"All {comparison['totals']['verdict']} changed pilot records",
        f"Five pilot checks hit the Rust subprocess",
    ]
    lines.extend(
        f"| `{name}` | {row['calls_per_side']} | {row['base_cpu_ms']:.3f} | {row['head_cpu_ms']:.3f} |"
        for name, row in bench["samples"].items()
    )
    lines.extend(f"| `{commit['sha'][:8]}` | {commit['subject']} |" for commit in summary["commits_before_report"])
    lines.extend(
        f"| {mutant['mutant']} | `{mutant['file']}` | `{mutant['test']}` | exit {mutant['exit_code']} |"
        for mutant in mutants
    )
    return lines


def mismatches(report, summary, gate, comparison, bench, mutants):
    return [line for line in expected_lines(summary, gate, comparison, bench, mutants) if line not in report]


def test_report_numbers_and_commit_rows_match_saved_evidence():
    summary, gate, comparison, _, bench, mutants, _, _ = saved()
    assert mismatches((HERE / "DELTA.md").read_text(), summary, gate, comparison, bench, mutants) == []
    assert gate["status"] == "passed" and gate["dirty"] is False
    assert gate["commit_sha"] == summary["code_head"] == bench["head_commit"]
    assert gate["counts"] == summary["gate_counts"]
    assert gate["counts"]["passed"] + gate["counts"]["skipped"] + gate["counts"]["failed"] == gate["counts"]["selected"]
    assert gate["counts"]["selected"] + gate["counts"]["deselected"] == gate["counts"]["collected"]
    assert gate["failures"] == []


def test_saved_commit_list_is_complete_for_the_gated_code():
    summary, *_ = saved()
    commits = summary["commits_before_report"]
    assert commits and len(commits) == len({item["sha"] for item in commits})
    assert all(re.fullmatch(r"[0-9a-f]{40}", item["sha"]) for item in commits)
    assert all(item["subject"].startswith("readings-defaults RD-6b: ") for item in commits)
    assert commits[-1]["sha"] == summary["code_head"]
    assert re.fullmatch(r"[0-9a-f]{40}", summary["base_merge_commit"])
    assert re.fullmatch(r"[0-9a-f]{40}", summary["main_at_code_head"])


def test_saved_ab_records_are_complete_and_every_delta_is_reviewed():
    summary, _, comparison, delta, _, _, retries, records = saved()
    assert comparison["records"] == summary["ab_records"] == {"pilots/default": 454, "readings/default": 1137}
    assert comparison["totals"] == summary["ab_totals"] == {"same": 1555, "verdict": 29, "wording": 7}
    assert comparison["unlisted"] == summary["ab_unlisted"] == 0
    assert len(comparison["differences"]) == 36
    assert all(len(records[side]) == 1591 for side in ("base", "head"))
    assert all({(row["corpus"], row["authority"], row["case"], row["op"]) for row in records[side]}
               == {(row["corpus"], row["authority"], row["case"], row["op"]) for row in records["base"]}
               for side in ("base", "head"))
    assert len(delta["verdict"]) == 29 and len(delta["wording"]) == 1
    assert not delta["order"] and not delta["availability"] and not delta["unavailable"]
    for difference in comparison["differences"]:
        assert difference["listed"] is True
        if difference["class"] == "verdict":
            base = difference["base"]["stdout"]["readings"]
            head = difference["head"]["stdout"]["readings"]
            assert difference["corpus"] == "pilots"
            assert (base["route"], head["route"]) == ("enumerated", "superposed")
            assert base["conflict"]["status"] == head["conflict"]["status"]
            assert {key: difference[key] for key in ("corpus", "authority", "case", "op", "base", "head")} in delta["verdict"]
        else:
            assert difference["class"] == "wording" and difference["base"]["exit"] == difference["head"]["exit"] == 1
            assert difference["base"]["stdout"] == difference["head"]["stdout"] == ""
            assert {side: difference[side]["stderr"][0] for side in ("base", "head")} in delta["wording"]
            assert all("Cannot read sense pack" in difference[side]["stderr"][0] for side in ("base", "head"))
    assert len(retries) == 5
    assert all("timed out after" in str(item["original"]) and item["retry"]["exit"] == 0 for item in retries)


def test_saved_latency_and_seeded_bugs():
    summary, _, _, _, bench, mutants, _, _ = saved()
    assert bench["pass"] is summary["latency_pass"] is True
    assert len(bench["samples"]) == 3
    assert all(row["calls_per_side"] == 500 and row["head_cpu_ms"] <= 1.2 * row["base_cpu_ms"]
               for row in bench["samples"].values())
    assert len(mutants) == summary["seeded_bugs"] == 3
    assert len({mutant["mutant"] for mutant in mutants}) == 3
    for mutant in mutants:
        assert mutant["exit_code"] != 0 and mutant["failed"] is True and "FAILED" in mutant["tail"]
        assert (ROOT / mutant["file"]).is_file()
        path, name = mutant["test"].split("::", 1)
        name = name.split("[", 1)[0]
        assert re.search(rf"^def {re.escape(name)}\(", (ROOT / path).read_text(), re.M)


def test_report_check_rejects_mutated_saved_numbers_commits_and_failures():
    summary, gate, comparison, _, bench, mutants, _, _ = saved()
    report = (HERE / "DELTA.md").read_text()
    for section, name in (("lean", "build_jobs"), ("lean", "audit_theorems"),
                          ("lean", "statements"), ("lean", "rd6b_declarations")):
        altered = copy.deepcopy(summary)
        altered[section][name] += 1
        assert mismatches(report, altered, gate, comparison, bench, mutants)
    altered = copy.deepcopy(summary)
    altered["commits_before_report"][0]["sha"] = "0" * 40
    assert mismatches(report, altered, gate, comparison, bench, mutants)
    altered = copy.deepcopy(gate)
    altered["counts"]["passed"] += 1
    assert mismatches(report, summary, altered, comparison, bench, mutants)
    altered = copy.deepcopy(comparison)
    altered["totals"]["verdict"] += 1
    assert mismatches(report, summary, gate, altered, bench, mutants)
    altered = copy.deepcopy(bench)
    first = next(iter(altered["samples"].values()))
    first["head_cpu_ms"] += 1
    assert mismatches(report, summary, gate, comparison, altered, mutants)
    altered = copy.deepcopy(mutants)
    altered[0]["exit_code"] = 0
    assert mismatches(report, summary, gate, comparison, bench, altered)


# ---------------------------------------------------------------------------------------------------------------
# Review round 1 (rd-6b-review.final.md): the 29 changed pilot records recorded again on the round's head and on
# the base, one process at a time (tools/lean_first_diff.py `pilot_check`), and the trust growth.

ROUND1_ADDED = {("readings", "conflict", "choices"), ("premises", "gaps")}


def round1_records(side):
    text = gzip.decompress((EVIDENCE / f"round1-pilots-{side}.jsonl.gz").read_bytes()).decode()
    return {row["case"]: row for row in map(json.loads, text.splitlines())}


def members(old, new, path=()):
    """(path, how) of every member `new` adds, removes or changes against `old`."""
    if type(old) is dict and type(new) is dict:
        for key in sorted(set(old) | set(new)):
            if key not in old:
                yield path + (key,), "added"
            elif key not in new:
                yield path + (key,), "removed"
            else:
                yield from members(old[key], new[key], path + (key,))
    elif old != new:
        yield path, "changed"


def round1_lines():
    head, base = round1_records("head"), round1_records("base")
    slower = sorted(case for case in head if head[case]["wall_seconds"] > 1.2 * base[case]["wall_seconds"] + 1)
    return [f"29 changed pilot records recorded again, one process at a time: {round(sum(r['wall_seconds'] for r in head.values()))} s "
            f"on this round's head, {round(sum(r['wall_seconds'] for r in base.values()))} s on the base",
            f"{len(slower)} of them more than 20% slower than the base"], slower


def test_round1_pilots_keep_the_base_statuses_and_the_previous_english():
    """Every changed pilot record, on the round's head: Lean's route, the base's conflict and premise statuses, the
    previous head's status text and English line for line; against the previous head only the per-choice conflict
    statuses and Lean's gaps of the shown premise model are added."""
    _, _, _, delta, _, _, _, _ = saved()
    previous = {row["case"]: row for row in delta["verdict"]}
    head, base = round1_records("head"), round1_records("base")
    assert set(head) == set(base) == set(previous) and len(head) == 29
    added = set()
    for case, row in head.items():
        assert row["source_sha256"] == base[case]["source_sha256"]
        report, before = row["outcome"]["stdout"], previous[case]["head"]["stdout"]
        assert row["outcome"]["exit"] == 0 and report["readings"]["route"] == "superposed", case
        for side in (base[case]["outcome"]["stdout"], previous[case]["base"]["stdout"]):
            assert report["readings"]["conflict"]["status"] == side["readings"]["conflict"]["status"], case
            assert report["premises"]["status"] == side["premises"]["status"], case
        assert (report["readings"]["status"], report["readings"]["english"]) == \
            (before["readings"]["status"], before["readings"]["english"]), case
        changes = list(members(before, report))
        assert all(how == "added" for _, how in changes), (case, changes)
        added |= {path for path, _ in changes}
        conflict = report["readings"]["conflict"]
        if "choices" in conflict:
            assert len(conflict["choices"]) == report["readings"]["choice_count"]
            if conflict["status"] == "CONFLICT-FREE":
                assert {c["status"] for c in conflict["choices"]} == {"CONFLICT-FREE"}
    assert added == ROUND1_ADDED
    lines, slower = round1_lines()
    text = (HERE / "DELTA.md").read_text()
    assert all(line in text for line in lines), lines
    assert all(f"`{case.rsplit('/', 1)[-1]}`" in text for case in slower)


def test_trust_growth_is_rd6b_entry_and_listed_for_signature():
    """Review B1 of rd-6b: the saved reviewed tree matches its trust baseline, and the growth from the pinned merge
    base is exactly the baseline's RD-6b entry, as DELTA.md states
    it: S +0, V +142, of which +16 under R6 and +126 awaiting the DRI's signature. The entry is the reviewed
    measurement at the branch head before the merge of ve-integration f0547468; the merge's entry carries the
    same growth over the merged base."""
    from tools import trust_map
    summary, *_ = saved()
    reviewed = json.loads(subprocess.check_output(
        ["git", "show", f"{RD6B_HEAD}:docs/trust-baseline.json"], cwd=ROOT))
    baseline = json.loads((ROOT / "docs/trust-baseline.json").read_text())
    reviewed_tree, problems, _ = trust_map.measure_rev(RD6B_HEAD)
    parent, parent_problems, _ = trust_map.measure_rev(summary["base_merge_commit"])
    merged, merged_problems, _ = trust_map.measure_rev(MERGED_BASE)
    assert not problems and not parent_problems and not merged_problems
    assert reviewed["files"] == reviewed_tree and baseline["signed"] == []
    entry = reviewed["history"][-1]
    assert entry["change"].startswith("readings-defaults RD-6b: ")
    assert entry["rebaselined_from"] == trust_map.budget(trust_map.totals(parent))
    assert entry["to"] == trust_map.budget(reviewed["totals"])
    assert entry in baseline["history"]
    merge = next(row for row in baseline["history"]
                 if row["change"].startswith(f"Merge ve-integration {MERGED_BASE[:8]} "))
    assert merge["change"].startswith(f"Merge ve-integration {MERGED_BASE[:8]} ")
    assert merge["rebaselined_from"] == trust_map.budget(trust_map.totals(merged))
    for step in (entry, merge):
        growth = {key: step["to"][key] - step["rebaselined_from"][key] for key in ("K", "S", "V")}
        assert growth == {"K": 0, "S": 0, "V": 142}
    # The approved head's last merge entry; later merges into other branches append their own entries after it.
    approved = json.loads(subprocess.check_output(
        ["git", "show", f"{RD6B_APPROVED}:docs/trust-baseline.json"], cwd=ROOT))
    current_merge = approved["history"][-1]
    assert current_merge["change"].startswith("Merge ve-integration 7478b23d ")
    assert current_merge in baseline["history"]
    assert current_merge["rebaselined_from"] == merge["to"]
    assert current_merge["to"] == trust_map.budget(approved["totals"])
    assert {key: current_merge["to"][key] - current_merge["rebaselined_from"][key]
            for key in ("K", "S", "V")} == {"K": 0, "S": 87, "V": 471}
    text = (HERE / "DELTA.md").read_text()
    assert "K +0, S +0, V +142" in text and "+16 under R6" in text and "+126 awaiting the DRI's signature" in text
