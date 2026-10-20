"""ap-2 seeded bugs: plant each bug, show that its check fails, restore the file.

    uv run python docs/act-phrases/ap-2/seed_bugs.py

Each row plants one bug in a file this item changed (one per claimed behaviour, in each changed language), runs the
check that must fail, and restores the file from git. A bug in Read.lean is caught first by its proofs; so that the
fixtures are shown to catch it too, it is planted a second time with the proofs section cut out (`fixtures_only`), and
GrammarExamples.lean must then fail. Writes docs/act-phrases/ap-2/mutants.json. Run it on a clean tree with the Lean
build up to date.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "mutants.json"
LAKE = ["lake", "build", "VE.Acts.GrammarExamples"]
IMPORTS = ["python3", "tools/check_lean_imports.py"]

MUTANTS = [
    ("raw-cap-off-by-one", "lean/VE/Acts/Read.lean", "  | some ts => if N ≤ ts.length then .limit else",
     "  | some ts => if N < ts.length then .limit else", LAKE,
     "a saturated parse (N raw derivations) is listed: LG2, LG6 and the toy's N raw guard"),
    ("readings-limit-off-by-one", "lean/VE/Acts/Read.lean", "      if L < ms.length then .limit else .ok ms",
     "      if L ≤ ms.length then .limit else .ok ms", LAKE,
     "exactly 64 readings are refused: LG4 and the toy's 64 readings guard"),
    ("firsts-keeps-duplicates", "lean/VE/Acts/Read.lean", "  | x :: xs => x :: (firsts xs).filter (· ≠ x)",
     "  | x :: xs => x :: firsts xs", LAKE, "equal meanings listed twice: nodup_firsts, LG7 and the firsts guard"),
    ("read-picks-first-of-many", "lean/VE/Acts/Read.lean", "  | .ok (A :: B :: _) => .many A B",
     "  | .ok (A :: _ :: _) => .ok A", LAKE,
     "two meanings read as one: readIn_many and the hidden-meaning guard"),
    ("derived-ignores-meaning", "lean/VE/Acts/Read.lean",
     "  ∃ d, Derives G (.n G.start) ts d ∧ ∃ c, μ () d = .ok (A, c, ())",
     "  ∃ d, Derives G (.n G.start) ts d", LAKE, "DerivedIn without the meaning: readingsIn_exact does not prove"),
    ("raw-cap-255", "lean/VE/Acts/Read.lean", "def rawCap : Nat := 256", "def rawCap : Nat := 255", LAKE,
     "N measured as 256: the N−1 raw guard (255 derivations, one reading)"),
    ("markers-not-canonical", "lean/VE/Acts/Syntax.lean",
     "    if let some m := (ms f).find? (fun m => m != \" \".intercalate (wordsOf m) || wordsOf m == []) then",
     "    if let some m := (ms f).find? (fun m => wordsOf m == []) then", LAKE,
     "31l dropped for spaced markers: FR2 and the ' in' guard (FR1 still fails 31l by its empty words)"),
    ("split-not-in-markers", "lean/VE/Acts/Syntax.lean",
     "    if let some m := f.split.find? (!f.markers.contains ·) then",
     "    if let some m := f.split.find? (fun _ => false) then", LAKE, "31i dropped: FR6"),
    ("slot-accepts-subject", "lean/VE/Acts/Syntax.lean", "  | .slot, .slot (_ + 1) => true",
     "  | .slot, .slot _ => true", LAKE, "the terminal `slot` accepts {0}: the terminals guard"),
    ("acts-not-surface-layer", "tools/layer_policy.py", '"VE.Senses.", "VE.Question.", "VE.Acts.")',
     '"VE.Senses.", "VE.Question.")', IMPORTS,
     "VE.Acts.* falls to layer 2 and imports VE.Grammar.* (layer 3): tools/check_lean_imports.py"),
]


def run(cmd):
    env = dict(os.environ, PATH=str(Path.home() / ".elan/bin") + os.pathsep + os.environ["PATH"])
    cwd = ROOT / "lean" if cmd is LAKE else ROOT
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


def failing_lines(out):
    keep = [ln for ln in out.splitlines() if "error" in ln.lower() or "did not evaluate" in ln or "FAIL" in ln
            or "->" in ln]
    return keep[:6]


def main():
    if subprocess.run(["git", "status", "--porcelain", "--", "lean", "tools"], cwd=ROOT, capture_output=True,
                      text=True).stdout.strip():
        sys.exit("the tree is not clean under lean/ and tools/")
    rows = []
    for name, path, old, new, cmd, claim in MUTANTS:
        file = ROOT / path
        text = file.read_text()
        if text.count(old) != 1:
            sys.exit(f"{name}: the line to mutate occurs {text.count(old)} times in {path}")
        file.write_text(text.replace(old, new))
        try:
            proc = run(cmd)
            fixtures = None
            if path.endswith("Read.lean") and name != "derived-ignores-meaning":
                mutated = text.replace(old, new)
                cut = mutated[:mutated.index("section Proofs")] + "end VE.Acts\n"
                file.write_text(cut)
                only = run(LAKE)
                fixtures = {"exit": only.returncode, "failed": only.returncode != 0
                            and "GrammarExamples.lean" in only.stdout + only.stderr,
                            "output": failing_lines(only.stdout + only.stderr)}
        finally:
            subprocess.run(["git", "checkout", "--", path], cwd=ROOT, check=True)
        rows.append({"fixtures_only": fixtures, "id": name, "language": "Python" if path.endswith(".py") else "Lean", "file": path,
                     "mutation": {"from": old.strip(), "to": new.strip()}, "claim": claim,
                     "test": " ".join(cmd), "exit": proc.returncode, "failed": proc.returncode != 0,
                     "output": failing_lines(proc.stdout + proc.stderr)})
        print(f"{name:28} exit {proc.returncode}")
    restored = run(LAKE)
    result = {"restored_build_exit": restored.returncode,
              "all_failed": all(r["failed"] and (r["fixtures_only"] or {"failed": True})["failed"] for r in rows),
              "rows": rows}
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    if not result["all_failed"] or restored.returncode != 0:
        sys.exit("a seeded bug did not fail its check, or the restored build failed")


if __name__ == "__main__":
    main()
