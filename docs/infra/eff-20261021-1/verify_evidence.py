#!/usr/bin/env python3
"""Check the eff-20261021-1 stop decision against the raw tool output it rests on; exit 1 on any failed or unmeasured
row. Nothing is compared with a number copied from evidence.json: both stop rules are recomputed from the sweeps
(lean-only.json, pytest-attempt.json) and the corpus replay (replay/, read through replay.py's `derive`), and
evidence.json must state what they give."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from replay import TOOLS, derive, trees  # noqa: E402

PAIRS_NEEDED, TIMES = 8, 3  # the task's two stop rules


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)


def timing(stop: dict, lean: dict, attempt: dict, bad: list[str]) -> bool:
    """Rule 2: the pytest phase alone against the Lean-only sweep of the same tree, jobs and mutants."""
    same = ("head", "base", "jobs", "max_mutants", "deep", "tests")
    if differ := [k for k in same if lean[k] != attempt[k]]:
        bad.append(f"the two sweeps differ in {differ}")
    if lean["pytest"] or not attempt["pytest"]:
        bad.append("lean-only.json must run no pytest and pytest-attempt.json some")
    for arg in attempt["pytest"]:  # review F1: the reviewed tree's own fixture tests
        path, _, node = arg.partition("::")
        shown = git("show", f"{attempt['head']}:{path}")
        if shown.returncode or node and f"def {node.split('[')[0]}(" not in shown.stdout:
            bad.append(f"--pytest {arg} is not a test of {attempt['head'][:12]}")
        if "[" in node and node.rsplit("[", 1)[1][:-1] not in git("grep", "-h", "-F", node.rsplit("[", 1)[1][:-1],
                                                                 attempt["head"], "--", "tests").stdout:
            bad.append(f"--pytest {arg}: no such parameter at {attempt['head'][:12]}")
    phases = attempt.get("phases", {})
    if phases.get("pytest_control") != "PASS":
        bad.append(f"the pytest control did not pass: {phases.get('pytest_control')}")
    survived = {m["id"] for m in lean["mutants"] if m["raw_status"] == "SURVIVOR"}
    tested = {m["id"] for m in attempt["mutants"] if m.get("pytest_executables")}
    if not survived or tested != survived:
        bad.append(f"the pytest phase built and tested {len(tested)} mutants, not the {len(survived)} Lean SURVIVORs")
    lean_rows = {m["id"]: m for m in lean["mutants"]}
    for m in attempt["mutants"]:
        other = lean_rows.get(m["id"], {})
        if (m["operator"], m["before"], m["after"]) != (other.get("operator"), other.get("before"), other.get("after")):
            bad.append(f"{m['id']}: the two sweeps ran other mutants")
        elif m["id"] not in survived and m["raw_status"] != other["raw_status"]:
            bad.append(f"{m['id']}: the Lean phase judged it otherwise in the two sweeps")
    ratio = phases.get("pytest_seconds", 0) / lean["seconds"]
    got = {"lean_only_seconds": lean["seconds"], "lean_phase_seconds": phases.get("lean_seconds"),
           "pytest_phase_seconds": phases.get("pytest_seconds"),
           "pytest_control_seconds": phases.get("pytest_control_seconds"), "ratio": round(ratio, 2),
           "pytest_kills": attempt["counts"]["KILLED-BY-PYTEST"]}
    if wrong := {k: (stop.get(k), v) for k, v in got.items() if stop.get(k) != v}:
        bad.append(f"evidence.json stop_rule does not state the sweeps (recorded, measured): {wrong}")
    return ratio > TIMES


def corpus(data: dict, bad: list[str]) -> int:
    """Rule 1: every row measured in both trees under both tools; the SURVIVOR -> KILLED pairs counted."""
    pairs = 0
    for row in data["corpus"]:
        rows = [r for r in data["corpus"] if r["item"] == row["item"]]
        name = f"{row['item']}/{row['id']}"
        shown = git("show", f"{row['reviewed_head']}:{row['file']}")
        if shown.returncode or row["before"] not in shown.stdout:
            bad.append(f"{name}: reviewed source text missing")
        try:
            got = derive(row, rows)
            for kind, commit in trees(row).items():
                for tool in TOOLS:
                    plan = json.loads((HERE / "replay" / f"{row['item']}-{kind}-{tool}-plan.json").read_text())
                    if plan["tree"] != commit:
                        bad.append(f"{name}: the {kind} {tool} plan read {plan['tree'][:12]}, not {commit[:12]}")
        except (OSError, KeyError, ValueError) as error:
            bad.append(f"{name}: not replayed ({type(error).__name__}: {error})")
            continue
        if any(s in ("NOT RUN", "CANNOT RUN") for k in got["measured"].values() for s in k.values()):
            bad.append(f"{name}: a verdict was not measured: {got['measured']}")
        if wrong := {k: (row.get(k), v) for k, v in got.items() if row.get(k) != v}:
            bad.append(f"{name}: evidence.json does not state the replay (recorded, measured): {wrong}")
        pairs += got["pair"]
    return pairs


def main() -> int:
    data = json.loads((HERE / "evidence.json").read_text())
    lean = json.loads((HERE / "lean-only.json").read_text())
    attempt = json.loads((HERE / "pytest-attempt.json").read_text())
    stop, bad = data["stop_rule"], []
    slow = timing(stop, lean, attempt, bad)
    pairs = corpus(data, bad)
    if stop.get("pairs") != pairs:
        bad.append(f"evidence.json stop_rule pairs {stop.get('pairs')}, measured {pairs}")
    fired = [rule for rule, hit in (("pairs", pairs < PAIRS_NEEDED), ("time", slow)) if hit]
    if stop.get("fired") != fired or stop.get("decision", "").startswith("STOP") != bool(fired):
        bad.append(f"evidence.json says {stop.get('fired')} / {stop.get('decision')!r}; the measurements fire {fired}")
    for issue in bad:
        print(issue)
    print(f"pairs {pairs} (stop below {PAIRS_NEEDED}); pytest phase {stop.get('ratio')}x the Lean-only sweep "
          f"(stop above {TIMES}x); fired: {fired or 'none'}; {len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
