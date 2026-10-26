#!/usr/bin/env python3
"""REPORT section 1a: the consecutive trust_mutants sweeps of one item, Oct 20-26, and whether the change between
them was check-only.

    uv run python docs/speed/tmchecks/measure.py

Reads every version of each item's evidence JSON in the repository's history (all refs; git only reads), one run
per distinct blob, in the order it was first committed, and sc-1b's three reruns as the task gives them (sc-1b
committed no evidence JSON; its 5a0051f93 run is the saved copy). For two consecutive runs of one item it diffs
lean/ and the --test files between the two runs' `head`s. The change is check-only when every changed file is a
module of lean/ outside every selected declaration's file and import closure (the selected declarations are the
second run's `definitions`; the closure is read at the second head with `check_lean_imports.imports`), an outside
--test file, or a generated inventory (`INVENTORIES`), and the base and options are the same."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from check_lean_imports import imports  # noqa: E402

INVENTORIES = {"lean/declarations.txt", "lean/statements.txt", "lean/predicates.txt", "lean/axioms.txt"}
SINCE = "2026-10-20"
SAVED = Path("/home/seyran/code/manage-agents/reviews/speed-tmchecks-inputs/sc-1b-5a0051f93.json")
# sc-1b's three reruns, as the task gives them (ended, minutes): 34e1a60d1 -> 5a0051f93 -> 24504cdd5, and the first
# of the three after b548c10d2 (the 08:36Z sweep on the Mac log, 2526 s)
GIVEN = [("sc-1b", "b548c10d2", "34e1a60d1", "11:03Z", 60), ("sc-1b", "34e1a60d1", "5a0051f93", "12:18Z", 67),
         ("sc-1b", "5a0051f93", "24504cdd5", "running from 12:25Z", None)]


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False).stdout


def runs(path: str) -> list[dict]:
    seen, out = set(), []
    for line in reversed(git("log", "--all", f"--since={SINCE}", "--format=%H %cI", "--", path).splitlines()):
        commit, when = line.split()
        blob = git("rev-parse", "--verify", "-q", f"{commit}:{path}").strip()
        if not blob or blob in seen:
            continue
        seen.add(blob)
        try:
            data = json.loads(git("cat-file", "-p", blob))
        except json.JSONDecodeError:
            continue
        out.append({"when": when, "head": data.get("head", ""), "base": data.get("base", ""),
                    "mutants": sum(m.get("status") != "NOT RUN" for m in data.get("mutants", [])),
                    "seconds": data.get("seconds"), "tests": data.get("tests", []), "deep": data.get("deep"),
                    "definitions": [d.split(": ")[0] for d in data.get("definitions", [])]})
    return out


def closure(head: str, files: list[str]) -> set[str]:
    """`files` and every module of lean/ they import, transitively, at `head`."""
    names = [n for n in git("ls-tree", "-r", "--name-only", head, "--", "lean").split() if n.endswith(".lean")]
    module = {n.removeprefix("lean/").removesuffix(".lean").replace("/", "."): n for n in names}
    seen, todo = set(files), list(files)
    while todo:
        try:
            found = imports(git("show", f"{head}:{todo.pop()}"))
        except ValueError:
            continue
        new = {module[x] for x in found if x in module} - seen
        seen |= new
        todo += new
    return seen


def check_only(a: dict, b: dict) -> tuple[bool, str]:
    tests = [t if t.startswith("lean/") or "/" in t else f"lean/{t}" for t in a["tests"] + b["tests"]]
    changed = git("diff", "--name-only", a["head"], b["head"], "--", "lean", *tests).split()
    if not changed:
        return False, "lean/ and --test equal (identical inputs: speed-tmrescore's case)"
    if (a["base"], a["tests"], a["deep"]) != (b["base"], b["tests"], b["deep"]):
        return False, f"{len(changed)} files differ; base or options differ"
    reach = closure(b["head"], b["definitions"])
    inside = [f for f in changed if f in reach]
    other = [f for f in changed if f not in reach and not f.endswith(".lean") and f not in INVENTORIES
             and f not in tests]
    note = f"{len(changed)} files differ: " + ", ".join(sorted(changed)[:4]) + (" ..." if len(changed) > 4 else "")
    if inside:
        return False, note + f"; {len(inside)} in a selected file or its closure ({inside[0]})"
    if other:
        return False, note + f"; {other[0]} is no module, --test file or inventory"
    return True, note


def main() -> None:
    paths = sorted({n for n in git("log", "--all", f"--since={SINCE}", "--name-only", "--format=", "--",
                                   "docs/**/trust-mutants*.json").split() if not n.endswith("-allow.json")})
    print("| item | first | second | mutants | check-only | second took (min) | note |")
    print("|---|---|---|---|---|---|---|")
    for path in paths:
        item = path.split("/")[-2] + path.split("/")[-1].removeprefix("trust-mutants").removesuffix(".json")
        found = runs(path)
        for a, b in zip(found, found[1:]):
            same, note = check_only(a, b)
            minutes = round(b["seconds"] / 60) if isinstance(b["seconds"], (int, float)) else "?"
            print(f"| {item} | {a['head'][:9]} | {b['head'][:9]} | {b['mutants']} | {'y' if same else 'n'} | {minutes} "
                  f"| {note} |")
    saved = json.loads(SAVED.read_text())
    given = {"head": "", "base": saved["base"], "tests": saved["tests"], "deep": saved["deep"],
             "definitions": [d.split(": ")[0] for d in saved["definitions"]]}
    for item, first, second, ended, minutes in GIVEN:
        same, note = check_only({**given, "head": first}, {**given, "head": second})
        print(f"| {item} (given) | {first} | {second} | {len(saved['mutants'])} | {'y' if same else 'n'} | "
              f"{minutes if minutes is not None else '~65 (as the last)'} | ended {ended}; {note} |")


if __name__ == "__main__":
    main()
