"""Seeded bugs for test speed B3: one per behaviour the batch claims. Each is applied alone, its test is run (it
must fail), and the source is restored and checked byte for byte. Writes `evidence/mutants.json`.

    uv run python docs/test-speed-b3/mutants.py
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import nested_pytest  # noqa: E402

HERE = Path(__file__).resolve().parent
TOOL, TEST = "tools/since_pass.py", "tests/test_since_pass.py"

# (id, behaviour, original, mutant, test)
MUTANTS = [
    ("pass_off_the_branch", "a pass that is not an ancestor of HEAD is not a base",
     "        if is_ancestor(root, found.commit, head) and is_ancestor(root, base, found.commit):",
     "        if is_ancestor(root, base, found.commit):",
     "test_a_pass_outside_the_branchs_history_since_the_merge_base_is_not_a_base"),
    ("pass_before_the_merge_base", "a pass before the merge base (main's, or before a sync) is not a base",
     "        if is_ancestor(root, found.commit, head) and is_ancestor(root, base, found.commit):",
     "        if is_ancestor(root, found.commit, head):",
     "test_a_pass_of_main_before_the_merge_base_is_not_a_base"),
    ("tree_unbound", "a gate row is a base only when its tree is its commit's",
     "        if rev(root, f\"{found.commit}^{{commit}}\") != found.commit \\\n"
     "                or rev(root, f\"{found.commit}^{{tree}}\") != found.tree:",
     "        if rev(root, f\"{found.commit}^{{commit}}\") != found.commit:",
     "test_a_row_whose_tree_is_not_its_commits_or_whose_commit_is_absent_is_not_a_base"),
    ("farthest_pass", "the pass closest to HEAD is the base",
     "    chosen = min(eligible, key=lambda found: (distance(root, found.commit, head), -found.time.timestamp()))",
     "    chosen = max(eligible, key=lambda found: (distance(root, found.commit, head), -found.time.timestamp()))",
     "test_the_pass_closest_to_head_is_the_base"),
    ("step_bound_off_by_one", "a full run (today's base) is forced after 5 steps, not before",
     "    if steps > MAX_STEPS:", "    if steps >= MAX_STEPS:",
     "test_more_than_max_steps_since_the_pass_forces_todays_base"),
    ("age_bound_doubled", "a full run (today's base) is forced after 24 h",
     "    if age > MAX_AGE or age < timedelta(0):", "    if age > 2 * MAX_AGE or age < timedelta(0):",
     "test_a_pass_older_than_a_day_or_in_the_future_forces_todays_base"),
    ("future_pass", "a pass recorded in the future is not trusted",
     "    if age > MAX_AGE or age < timedelta(0):", "    if age > MAX_AGE:",
     "test_a_pass_older_than_a_day_or_in_the_future_forces_todays_base"),
    ("failed_gate_is_a_pass", "only a passed full gate or a passed rerun is a pass (R13)",
     'PASSES = {("passed", "full"), ("rerun-passed", "rerun-failed")}',
     'PASSES = {("passed", "full"), ("rerun-passed", "rerun-failed"), ("failed", "full")}',
     "test_a_rerun_that_passed_is_a_pass_and_a_failed_gate_is_not"),
    ("unbound_gate_record", "after-gate refuses a record of another tree or of a dirty worktree",
     '    if result.get("dirty") is not False:\n        return "the gate did not run on a clean worktree"\n',
     "",
     "test_after_gate_refuses_a_record_not_of_this_clean_head"),
    ("every_failure_covered", "a failure outside the rule's selection is a miss",
     '        return nodeid.split("::", 1)[0] in plan["selected"]', "        return True",
     "test_a_failure_is_outside_a_selection_unless_its_file_is_selected"),
    ("saved_outside_trusted", "check recomputes each row's misses and never trusts the saved lists",
     '    if row["outside"] != recomputed or row["counted"] is not counted(row):',
     '    if row["counted"] is not counted(row):',
     "test_check_refuses_every_retyped_rebound_or_dropped_field"),
    ("nine_items_activate", "activation needs 10 items",
     '            "active": len(items) >= ACTIVATION_ITEMS and not misses}',
     '            "active": len(items) >= ACTIVATION_ITEMS - 1 and not misses}',
     "test_fewer_items_or_a_miss_keeps_todays_base"),
    ("a_miss_activates", "a single miss keeps the rule inactive",
     '            "active": len(items) >= ACTIVATION_ITEMS and not misses}',
     '            "active": len(items) >= ACTIVATION_ITEMS}',
     "test_fewer_items_or_a_miss_keeps_todays_base"),
    ("full_rows_count", "a row whose rule selected everything is not evidence",
     '    return row["decision"]["rule"] == "since-pass" and plan is not None and not plan["full"]',
     '    return row["decision"]["rule"] == "since-pass" and plan is not None',
     "test_rows_whose_rule_selected_everything_do_not_count"),
    ("shadow_rule_used", "base prints today's merge base while the rule is in shadow",
     '            chosen = decision["base"] if active and decision["rule"] == "since-pass" else decision["merge_base"]',
     '            chosen = decision["base"] if decision["rule"] == "since-pass" else decision["merge_base"]',
     "test_fewer_items_or_a_miss_keeps_todays_base"),
    ("planner_not_the_base_plan", "the shadow's plan is select_tests' plan for pass..HEAD",
     '    return select_tests.select(paths, base=base, after=head, coverage="auto")',
     '    return select_tests.select(paths, base=base, after=None, coverage="auto")',
     "test_plan_between_is_the_select_tests_base_plan"),
]


def run(test: str) -> int:
    command = nested_pytest.command(["-q", "-p", "no:cacheprovider", "-p", "no:randomly", f"{TEST}::{test}"],
                                    python=[sys.executable])
    env = nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1")
    return subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode


def main() -> int:
    rows = []
    path = ROOT / TOOL
    for name, behaviour, original, mutant, test in MUTANTS:
        before = path.read_bytes()
        text = before.decode()
        if text.count(original) != 1:
            raise SystemExit(f"{name}: the original text is not in {TOOL} exactly once")
        try:
            path.write_text(text.replace(original, mutant))
            code = run(test)
        finally:
            path.write_bytes(before)
        if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(before).digest():
            raise SystemExit(f"{name}: {TOOL} was not restored")
        rows.append({"id": name, "behaviour": behaviour, "file": TOOL, "test": f"{TEST}::{test}", "exit": code,
                     "caught": code == 1})
        print(f"{name}: {TOOL}: {test} exit {code} ({'caught' if code == 1 else 'MISSED'})", flush=True)
    clean = {test: run(test.split("::", 1)[1]) for test in sorted({row["test"] for row in rows})}
    (HERE / "evidence/mutants.json").write_text(json.dumps(
        {"mutants": rows, "clean": clean, "language": "Python"}, indent=1) + "\n")
    missed = [row["id"] for row in rows if not row["caught"]] + [test for test, code in clean.items() if code]
    print(f"{len(rows) - len(missed)} of {len(rows)} caught; clean source passes: {not any(clean.values())}")
    return 1 if missed else 0


if __name__ == "__main__":
    raise SystemExit(main())
