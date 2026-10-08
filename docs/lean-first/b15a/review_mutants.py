"""Seed the batch 15a review's mutants one at a time, rebuild `ve_metered`, and
record which focused tests fail. Writes evidence/review-mutants.txt.

Usage: python docs/lean-first/b15a/review_mutants.py (from the repository root,
with the virtual environment and elan on PATH). The source is restored after
each mutant; the run ends with a clean build and a passing focused run.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import nested_pytest  # noqa: E402

OUT = Path(__file__).resolve().parent / "evidence/review-mutants.txt"
TESTS = ["tests/test_metered_differential.py", "tests/test_metered_lean.py"]

# (name, file, original text, mutated text): each original occurs exactly once.
MUTANTS = [
    ("existential-universal", "lean/VE/Route/NonVacuity.lean",
     "(path ++ [0]) universal false hits state\n        hits := hs",
     "(path ++ [0]) true false hits state\n        hits := hs"),
    ("clause-nesting", "lean/VE/Route/NonVacuity.lean",
     "if semantic && universal && !inClause then", "if semantic && universal then"),
    ("layered-defined-tables", "lean/VE/Core/Layers.lean",
     "(Json.mkObj (relations ++ tables)))", "(Json.mkObj relations))"),
    ("legacy-closure-family", "lean/VE/Service/Standalone.lean",
     "  | .closure _ => .closure\n  | .order _ => .order", "  | .closure _ => .fol\n  | .order _ => .order"),
    ("closure-document-count", "lean/VE/Route/MeteredRun.lean",
     "(·.work) limit fs ⟨0, {}⟩ }\n\ndef core", "(·.work + 1) limit fs ⟨0, {}⟩ }\n\ndef core"),
]


def run(command, env=None):
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, env=env)
    return done.returncode, done.stdout + done.stderr


def build():
    return run(["lake", "--dir", "lean", "build", "ve_metered"])[0]


def focused():
    code, output = run(nested_pytest.command(["-q", "-p", "no:cacheprovider", *TESTS]),
                       nested_pytest.environment(os.environ))
    failed = sorted({line.split(" - ")[0] for line in output.splitlines() if line.startswith("FAILED ")})
    summary = [line for line in output.splitlines() if " passed" in line or " failed" in line][-1:]
    return code, failed, summary


def main():
    code, head = run(["git", "rev-parse", "HEAD"])
    code_dirty, status = run(["git", "status", "--porcelain", "--", "lean", "tests"])
    assert code == 0 and code_dirty == 0
    lines = [f"source commit: {head.strip()}; lean/ and tests/ clean: {status.strip() == ''}", ""]
    for name, file, original, mutated in MUTANTS:
        path = ROOT / file
        source = path.read_text()
        assert source.count(original) == 1, (name, source.count(original))
        try:
            path.write_text(source.replace(original, mutated))
            built = build()
            code, failed, summary = focused()
        finally:
            path.write_text(source)
        lines += [f"## {name}", f"source mutation in {file}: {original!r} -> {mutated!r}",
                  f"build exit: {built}; focused pytest exit: {code}", *failed, *summary, ""]
    built = build()
    code, failed, summary = focused()
    lines += ["## restored", f"clean build exit: {built}; focused pytest exit: {code}", *failed, *summary]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
