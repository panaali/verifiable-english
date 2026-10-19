#!/usr/bin/env python3
"""Run df-1a's seeded bugs (docs/defeasible/df-1a/mutants.json) against the fixtures' `#guard`s alone.

Each mutant edits one definition of lean/VE/Defaults/Premises.lean. The run joins the mutated definitions, with every
theorem removed (a mutant must fail a guard, not a proof), and the body of lean/VE/Defaults/Examples.lean into one file
and elaborates it with `lake env lean`. The unmutated control must pass every guard; each mutant must fail at least
the guards its entry names, and no mutant may fail anywhere but at a `#guard`. Usage, from the repository root:

    python3 docs/defeasible/df-1a/evidence/run_mutants.py > docs/defeasible/df-1a/evidence/mutants.out
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LEAN = ROOT / "lean"
HERE = Path(__file__).resolve().parent


def without_theorems(src: str) -> str:
    """Drop each top-level `theorem` with its docstring: a chunk starts at a non-indented line after a blank one."""
    chunks, cur = [], []
    for line in src.splitlines(keepends=True):
        if line.strip() and not line[0].isspace() and (not cur or not cur[-1].strip()):
            chunks.append(cur)
            cur = []
        cur.append(line)
    chunks.append(cur)
    keep = [c for c in chunks if not any(l.startswith("theorem ") for l in c)]
    return "".join(l for c in keep for l in c)


def run(premises: str, examples: str) -> list[str]:
    """The text of each failing `#guard` (or the error, when something else fails)."""
    body = examples.split("\n", 1)[1]
    text = without_theorems(premises) + "\n" + body
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "Mutant.lean"
        path.write_text(text)
        done = subprocess.run(["lake", "env", "lean", str(path)], cwd=LEAN, capture_output=True, text=True)
    lines = text.splitlines()
    failed = []
    for m in re.finditer(r"Mutant\.lean:(\d+):\d+: error: (.*)", done.stdout + done.stderr):
        src = lines[int(m.group(1)) - 1]
        failed.append(src.strip()[:90] if src.startswith("#guard") else "NOT A GUARD: " + m.group(2)[:90])
    return failed


def main() -> int:
    premises = (LEAN / "VE/Defaults/Premises.lean").read_text()
    examples = (LEAN / "VE/Defaults/Examples.lean").read_text()
    entries = json.loads((HERE.parent / "mutants.json").read_text())["mutants"]
    ok = True
    control = run(premises, examples)
    print(f"control: {len(control)} failures")
    ok &= not control
    for e in entries:
        if "find" not in e:
            print(f"{e['id']} {e['definition']}: not run here ({e['test']})")
            continue
        assert premises.count(e["find"]) == 1, e["id"]
        failed = run(premises.replace(e["find"], e["replace"]), examples)
        hit = [g for g in failed if any(g.startswith(x[:90]) for x in e["guards"])]
        good = failed and all(not g.startswith("NOT A GUARD") for g in failed) and len(hit) == len(e["guards"])
        ok &= bool(good)
        print(f"{e['id']} {e['definition']}: {'FAILS' if good else 'SURVIVES'} {len(failed)} guards")
        for g in failed:
            print("   ", g)
    print("ALL MUTANTS FAIL THEIR GUARDS" if ok else "SOME MUTANT SURVIVES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
