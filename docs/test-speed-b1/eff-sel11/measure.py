"""eff-sel11: the selected-test counts of the last merged branches, without and with the history-inventory rule.

    uv run python docs/test-speed-b1/eff-sel11/measure.py [--merges 10] [--output docs/test-speed-b1/eff-sel11/measure.json]

For each of the last `--merges` merges on main's first-parent line, the branch's own diff (its merge base with
main to the branch head, as a builder's `--base $(git merge-base HEAD main)` sees it) is planned by both selection
paths of the checked-out tools/select_tests.py: the map plan (the nearest cached coverage map of the base) and
`--impacted`. "before" is the same plan without the rule: the map plan less tests/test_history_tests.py when the
rule is its only reason, `--impacted` with `history_inventory` answering nothing. The numbers are saved once with
the commit they were measured on; nothing reads them live.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import select_tests  # noqa: E402


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def measure(merge: str) -> dict:
    main_side, branch = git("rev-parse", f"{merge}^1"), git("rev-parse", f"{merge}^2")
    base = git("merge-base", main_side, branch)
    paths = git("diff", "--no-renames", "--name-only", base, branch).splitlines()
    plan = select_tests.select(paths, base=base, after=branch)
    only_rule = plan["reasons"].get(select_tests.HISTORY_TEST) == [select_tests.HISTORY_REASON]
    after = select_tests.impacted(paths)
    rule = select_tests.history_inventory
    select_tests.history_inventory = lambda paths: []
    try:
        before = select_tests.impacted(paths)
    finally:
        select_tests.history_inventory = rule
    return {"merge": merge, "subject": git("log", "-1", "--format=%s", merge), "base": base, "branch": branch,
            "changed": len(paths), "history_inventory": plan["history_inventory"],
            "map": {"full": plan["full"], "after": plan["selected_count"],
                    "before": plan["selected_count"] - only_rule,
                    "has_lint": select_tests.HISTORY_TEST in plan["selected"], "added_by_rule": only_rule},
            "impacted": {"fallback": after["fallback"], "after": after["selected_count"],
                         "before": before["selected_count"],
                         "has_lint": select_tests.HISTORY_TEST in after["selected"],
                         "added_by_rule": select_tests.HISTORY_TEST not in before["selected"]
                         and select_tests.HISTORY_TEST in after["selected"]}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--merges", type=int, default=10)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("measure.json"))
    args = parser.parse_args()
    merges = git("log", "--merges", "--first-parent", "--format=%H", f"-{args.merges}", "main").splitlines()
    rows = []
    for merge in merges:
        rows.append(measure(merge))
        row = rows[-1]
        print(f"{row['subject'][:60]:60} map {row['map']['before']}->{row['map']['after']}"
              f"{' FULL' if row['map']['full'] else ''} impacted {row['impacted']['before']}->"
              f"{row['impacted']['after']} lint {row['map']['has_lint']}/{row['impacted']['has_lint']}", flush=True)
    data = {"measured_on": git("rev-parse", "HEAD"), "main": git("rev-parse", "main"), "rows": rows,
            "with_lint": {"map": sum(row["map"]["has_lint"] for row in rows),
                          "impacted": sum(row["impacted"]["has_lint"] for row in rows)},
            "added_by_rule": {"map": sum(row["map"]["added_by_rule"] for row in rows),
                              "impacted": sum(row["impacted"]["added_by_rule"] for row in rows)}}
    args.output.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({key: data[key] for key in ("with_lint", "added_by_rule")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
