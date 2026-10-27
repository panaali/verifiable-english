#!/usr/bin/env python3
"""Run df-1ae's seeded bugs (docs/defeasible/df-1ae/mutants.json) in place.

The route's fixtures (`Defaults/RouteExamples.lean`, `ResponseShape/DefaultsExamples.lean`) import the compiled
runner, so a bug is planted in its product file under lean/ itself, with that file's theorems removed but those in
`keep` (a mutant must fail a `#guard`, not a proof; df-1a's `without_theorems`), and `lake build <target>` runs. The
control (each file with its theorems removed, no bug) must build; each mutant must fail every `#guard` its entry
names (a guard's first line, to 90 characters), and nowhere but at a `#guard`. Every file is restored after each run.
Usage, from the repository root: python3 docs/defeasible/df-1ae/evidence/run_mutants.py > docs/defeasible/df-1ae/evidence/mutants.out
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LEAN = ROOT / "lean"
sys.path.insert(0, str(ROOT / "docs/defeasible/df-1a/evidence"))
from run_mutants import without_theorems  # noqa: E402


def run(path: Path, text: str, target: str, keep: tuple[str, ...]) -> list[str]:
    original = path.read_text()
    path.write_text(without_theorems(text, keep))
    try:
        done = subprocess.run(["lake", "build", target], cwd=LEAN, capture_output=True, text=True)
        failed = []
        for m in re.finditer(r"error: ([\w/.]+\.lean):(\d+):\d+: (.*)", done.stdout + done.stderr):
            line = (LEAN / m.group(1)).read_text().splitlines()[int(m.group(2)) - 1]
            failed.append(line.strip()[:90] if line.startswith("#guard") else f"NOT A GUARD: {m.group(1)}: {m.group(3)[:80]}")
        if done.returncode and not failed:
            failed.append("NOT A GUARD: build failed")
        return failed
    finally:
        path.write_text(original)


def main() -> int:
    spec = json.loads((ROOT / "docs/defeasible/df-1ae/mutants.json").read_text())
    keep = tuple(spec["keep"])
    ok = True
    for file, target in dict.fromkeys((e["file"], e["target"]) for e in spec["mutants"]):
        control = run(ROOT / file, (ROOT / file).read_text(), target, keep)
        print(f"control {file} ({target}): {len(control)} failures")
        ok &= not control
    for e in spec["mutants"]:
        path = ROOT / e["file"]
        text = path.read_text()
        assert text.count(e["find"]) == 1, e["id"]
        failed = run(path, text.replace(e["find"], e["replace"]), e["target"], keep)
        good = failed and all(not g.startswith("NOT A GUARD") for g in failed) and all(
            g[:90] in failed for g in e["guards"])
        ok &= bool(good)
        print(f"{e['id']} {e['definition']}: {'FAILS' if good else 'SURVIVES'} {len(failed)} guards")
        for g in failed:
            print("   ", g)
    subprocess.run(["lake", "build", "VE.Defaults.RouteExamples", "ResponseShape.DefaultsExamples"], cwd=LEAN,
                   capture_output=True)
    print("ALL MUTANTS FAIL THEIR GUARDS" if ok else "SOME MUTANT SURVIVES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
