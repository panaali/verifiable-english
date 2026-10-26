#!/usr/bin/env python3
"""Check the eff-20261026-1 stop decision against the raw tool output it rests on; exit 1 on any missing, failed or
skipped row. Nothing is compared with a number copied from evidence.json: the pairs are recomputed from the corpus
replay (replay/, read through replay.py's `derive`, the one owner of the rule) and the times from the four sweeps
(cost/), and evidence.json must state what they give.

    python3 docs/infra/eff-20261026-1/check.py
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from replay import COLUMNS, derive, measured, trees  # noqa: E402

UNMEASURED = ("CANNOT RUN", "NOT RUN")


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)


def corpus(data: dict, bad: list[str]) -> int:
    """Every row replayed at both trees, its columns what the raw files give; the SURVIVOR -> KILLED pairs."""
    pairs = 0
    if not data["corpus"]:
        bad.append("the corpus is empty")
    for row in data["corpus"]:
        rows = [r for r in data["corpus"] if r["item"] == row["item"]]
        name = f"{row['item']}/{row['id']}"
        shown = git("show", f"{row['reviewed_head']}:{row['file']}")
        if shown.returncode or row["before"] not in shown.stdout:
            bad.append(f"{name}: the reviewed tree does not hold its `before` text")
        if not str(row.get("replay_note", "")).strip():
            bad.append(f"{name}: no replay_note says why its replay mutant is (or is not) the reviewer's form")
        if not measured(row["item"], rows):
            bad.append(f"{name}: skipped (a plan or a run its plan asks for is missing)")
            continue
        try:
            got = derive(row, rows)
            for kind, commit in trees(row).items():
                plan = json.loads((HERE / "replay" / f"{row['item']}-{kind}-plan.json").read_text())
                if plan["tree"] != commit:
                    bad.append(f"{name}: the {kind} plan read {plan['tree'][:12]}, not {commit[:12]}")
        except (OSError, KeyError, ValueError, IndexError) as error:
            bad.append(f"{name}: not replayed ({type(error).__name__}: {error})")
            continue
        if any(v in UNMEASURED for v in (got["reviewed_verdict"], got["fixed_verdict"])):
            bad.append(f"{name}: a verdict was not measured: {got['reviewed_verdict']}, {got['fixed_verdict']}")
        if row["replay"] is not None and got["reviewed_verdict"] == "NOT GENERATED":
            bad.append(f"{name}: its replay mutant is no mutant the tool writes at the reviewed tree")
        if wrong := {k: (row.get(k), got[k]) for k in COLUMNS if row.get(k) != got[k]}:
            bad.append(f"{name}: evidence.json does not state the replay (recorded, measured): {wrong}")
        pairs += got["pair"]
    return pairs


def sweep(item: str, spec: dict, which: str, bad: list[str]) -> dict:
    """One cost sweep: its JSON, run on the runner (its log) over the HEAD with every mutant run."""
    data = json.loads((HERE / spec[which]).read_text())
    log = (HERE / spec[which]).with_suffix(".log").read_text()
    if data["head"] != spec["head"]:
        bad.append(f"{item} {which}: swept {data['head'][:12]}, not {spec['head'][:12]}")
    if not re.search(rf"summary: ran on ve-mac-1 .*HEAD {spec['head'][:8]} ", log):
        bad.append(f"{item} {which}: its log shows no run on ve-mac-1 of {spec['head'][:8]}")
    if data["counts"]["NOT RUN"] or not data["mutants"]:
        bad.append(f"{item} {which}: {data['counts']['NOT RUN']} mutants NOT RUN of {len(data['mutants'])}")
    if data["classes"] != (["trusted"] if which == "default" else ["all"]):
        bad.append(f"{item} {which}: --classes {data['classes']}")
    return data


def cost(data: dict, bad: list[str]) -> dict[str, dict]:
    """Rule 2: per HEAD, the widened sweep's time against the default sweep's, the same options; and the default's
    mutants keep their verdicts in the widened sweep (its trusted part)."""
    out = {}
    for item, spec in data["cost"]["heads"].items():
        default, wide = (sweep(item, spec, w, bad) for w in ("default", "all"))
        if differ := [k for k in ("base", "jobs", "max_mutants", "deep", "tests") if default[k] != wide[k]]:
            bad.append(f"{item}: the two sweeps differ in {differ}")

        def verdicts(rows: list[dict]) -> Counter:
            return Counter((m["file"], m["line"], m["definition"], m["operator"], m["before"], m["after"],
                            m["raw_status"]) for m in rows)
        if verdicts(default["mutants"]) != verdicts([m for m in wide["mutants"] if m["trusted"]]):
            bad.append(f"{item}: the widened sweep's trusted mutants are not the default's, with its verdicts")
        out[item] = {"default_seconds": default["seconds"], "all_seconds": wide["seconds"],
                     "default_mutants": len(default["mutants"]), "all_mutants": len(wide["mutants"]),
                     "ratio": round(wide["seconds"] / default["seconds"], 2)}
    return out


def main() -> int:
    data = json.loads((HERE / "evidence.json").read_text())
    stop, bad = data["stop_rule"], []
    pairs = corpus(data, bad)
    times = cost(data, bad)
    if stop.get("pairs") != pairs:
        bad.append(f"evidence.json stop_rule pairs {stop.get('pairs')}, measured {pairs}")
    if stop.get("times") != times:
        bad.append(f"evidence.json stop_rule times {stop.get('times')}, measured {times}")
    slow = [i for i, t in times.items() if t["ratio"] > stop["ratio_limit"] or t["all_seconds"] > stop["seconds_limit"]]
    fired = [rule for rule, hit in (("pairs", pairs < stop["pairs_needed"]), ("time", bool(slow))) if hit]
    if stop.get("fired") != fired or stop.get("decision", "").startswith("STOP") != bool(fired):
        bad.append(f"evidence.json says {stop.get('fired')} / {stop.get('decision')!r}; the measurements fire {fired}")
    for issue in bad:
        print(issue)
    print(f"pairs {pairs} of {len(data['corpus'])} rows (stop below {stop['pairs_needed']}); widened/default "
          + ", ".join(f"{i} {t['ratio']}x ({t['all_seconds']} s / {t['default_seconds']} s)" for i, t in times.items())
          + f" (stop above {stop['ratio_limit']}x or {stop['seconds_limit']} s); fired: {fired or 'none'}; "
          f"{len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
