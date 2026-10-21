#!/usr/bin/env python3
"""REPORT section 1: the consecutive trust_mutants sweeps of one item whose Lean inputs were identical.

    uv run python docs/speed/tmrescore/measure.py

Reads every version of each item's evidence JSON in the repository's history (all refs, the checkpoint stashes
included; git only reads), one run per distinct blob, in the order it was first committed. For each two consecutive
runs of one item it diffs lean/ and the --test files between the two runs' `head`s, and prints one table row. Only
the committed state is seen: a run on uncommitted changes reads as its `head`.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PATHS = ["docs/act-phrases/ap-1d/trust-mutants.json", "docs/act-phrases/ap-1d/trust-mutants-raw.json",
         "docs/defeasible/df-1ac/trust-mutants.json", "docs/math-evidence-me-2/trust-mutants.json",
         "docs/math-evidence-me-6b/trust-mutants.json", "docs/math-evidence/me-9b/trust-mutants.json",
         "docs/scope/sc-1ad/trust-mutants.json", "docs/scope/sc-3ab/trust-mutants.json"]


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False).stdout


def runs(path: str) -> list[dict]:
    seen, out = set(), []
    for line in reversed(git("log", "--all", "--since=2026-10-18", "--format=%H %cI", "--", path).splitlines()):
        commit, when = line.split()
        blob = git("rev-parse", "--verify", "-q", f"{commit}:{path}").strip()
        if not blob or blob in seen:
            continue
        seen.add(blob)
        try:
            data = json.loads(git("cat-file", "-p", blob))
        except json.JSONDecodeError:
            continue
        mutants = data.get("mutants", [])
        ran = sum(m.get("status") != "NOT RUN" for m in mutants)
        out.append({"when": when, "head": data.get("head", ""), "base": data.get("base", ""), "ran": ran,
                    "seconds": data.get("seconds"), "tests": data.get("tests", []), "deep": data.get("deep"),
                    "max": data.get("max_mutants")})
    return out


def identical(a: dict, b: dict) -> tuple[bool, str]:
    paths = ["lean", *(t if t.startswith("lean/") or "/" in t else f"lean/{t}" for t in a["tests"] + b["tests"])]
    if a["head"] == b["head"]:
        return True, "same head"
    changed = git("diff", "--name-only", a["head"], b["head"], "--", *paths).split()
    tool = bool(git("diff", "--name-only", a["head"], b["head"], "--", "tools/trust_mutants.py").split())
    note = (f"{len(changed)} files differ" if changed else "lean/ and --test equal") + ("; tool differs" if tool else "")
    return not changed, note


def main() -> None:
    print("| item | first | second | mutants run | identical inputs | second took (min) | note |")
    print("|---|---|---|---|---|---|---|")
    for path in PATHS:
        item = path.split("/")[-2] + ("-raw" if "raw" in path else "")
        found = runs(path)
        for a, b in zip(found, found[1:]):
            same, note = identical(a, b)
            if a["base"] != b["base"]:
                note += "; base differs"
            if (a["tests"], a["deep"], a["max"]) != (b["tests"], b["deep"], b["max"]):
                note += "; options differ"
            minutes = round(b["seconds"] / 60) if isinstance(b["seconds"], (int, float)) else "?"
            print(f"| {item} | {a['head'][:9]} | {b['head'][:9]} | {b['ran']} | {'y' if same else 'n'} | {minutes} "
                  f"| {note} |")


if __name__ == "__main__":
    main()
