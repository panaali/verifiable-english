#!/usr/bin/env python3
"""Run df-1b's seeded bugs (docs/defeasible/df-1b/mutants.json) in place: plant each, run its test, restore the file.
A bug fails when its test fails. Usage, from the repository root:
uv run python docs/defeasible/df-1b/evidence/run_mutants.py > docs/defeasible/df-1b/evidence/mutants.out"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def failed(test):
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", test], cwd=ROOT,
                          capture_output=True, text=True)
    return done.returncode != 0, (done.stdout.strip().splitlines() or [""])[-1]


spec = json.loads((ROOT / "docs/defeasible/df-1b/mutants.json").read_text())
ok = True
for test in dict.fromkeys(e["test"] for e in spec["mutants"]):
    fails, last = failed(test)
    print(f"control {test}: {'FAILS' if fails else 'passes'} ({last})")
    ok &= not fails
for e in spec["mutants"]:
    path = ROOT / e["file"]
    text = path.read_text()
    assert text.count(e["find"]) == 1, e["id"]
    path.write_text(text.replace(e["find"], e["replace"]))
    try:
        fails, last = failed(e["test"])
    finally:
        path.write_text(text)
    ok &= fails
    print(f"{e['id']} {e['file']}: {'FAILS' if fails else 'SURVIVES'} {e['test']} ({last})")
print("ALL MUTANTS FAIL THEIR TESTS" if ok else "SOME MUTANT SURVIVES")
sys.exit(0 if ok else 1)
