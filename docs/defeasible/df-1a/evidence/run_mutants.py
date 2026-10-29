#!/usr/bin/env python3
"""Run df-1a's seeded bugs (docs/defeasible/df-1a/mutants.json) against the fixtures' `#guard`s alone.

Each mutant edits one definition of lean/VE/Defaults/Premises.lean. The run joins the mutated definitions, with every
theorem removed (a mutant must fail a guard, not a proof), and the body of lean/VE/Defaults/Examples.lean into one file
and elaborates it with `lake env lean`. The unmutated control must pass every guard; each mutant must fail at least
the guards its entry names, and no mutant may fail anywhere but at a `#guard`. An entry with `theorems` (a mutant of a
`Prop`, which no `#guard` can evaluate) keeps every theorem and must fail inside each theorem it names. A mutants file
may name another `source` and `fixtures` (paths under lean/), the theorems a definition of the source uses (`keep`),
and the source's own module, whose import the joined file drops. Usage, from the repository root, with another item's
mutants file as the optional argument:

    python3 docs/defeasible/df-1a/evidence/run_mutants.py > docs/defeasible/df-1a/evidence/mutants.out
    python3 docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-1ab/mutants.json > docs/defeasible/df-1ab/evidence/mutants.out
    python3 docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-1ac/mutants.json > docs/defeasible/df-1ac/evidence/mutants.out
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


def without_theorems(src: str, used: tuple[str, ...] = ()) -> str:
    """Drop each top-level `theorem` with its docstring, but those in `used`: a chunk starts at a non-indented line
    after a blank one."""
    chunks, cur = [], []
    for line in src.splitlines(keepends=True):
        if line.strip() and not line[0].isspace() and (not cur or not cur[-1].strip()):
            chunks.append(cur)
            cur = []
        cur.append(line)
    chunks.append(cur)
    keep = [c for c in chunks if not any(l.startswith("theorem ") and l.split()[1] not in used for l in c)]
    return "".join(l for c in keep for l in c)


def run(premises: str, examples: str, keep: bool = False, used: tuple[str, ...] = (), module: str = "") -> list[str]:
    """The text of each failing `#guard`, `THEOREM <name>` for an error inside a kept theorem, or the error."""
    src = premises if keep else without_theorems(premises, used)
    imports = [l for l in (src + "\n" + examples).splitlines() if l.startswith("import ") and l != f"import {module}"]
    body = lambda s: "\n".join(l for l in s.splitlines() if not l.startswith("import "))
    text = "\n".join(dict.fromkeys(imports)) + "\n" + body(src) + "\n" + body(examples)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "Mutant.lean"
        path.write_text(text)
        done = subprocess.run(["lake", "env", "lean", str(path)], cwd=LEAN, capture_output=True, text=True)
    lines = text.splitlines()
    failed = []
    for m in re.finditer(r"Mutant\.lean:(\d+):\d+: error: (.*)", done.stdout + done.stderr):
        n = int(m.group(1)) - 1
        src = lines[n]
        owner = next((l for l in reversed(lines[: n + 1]) if l[:1].isalpha() or l.startswith("#")), "")
        if src.startswith("#guard"):
            failed.append(src.strip()[:90])
        elif keep and owner.startswith("theorem "):
            failed.append("THEOREM " + owner.split()[1])
        else:
            failed.append("NOT A GUARD: " + m.group(2)[:90])
    return failed


def main() -> int:
    spec = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else HERE.parent / "mutants.json").read_text())
    premises = (LEAN / spec.get("source", "VE/Defaults/Premises.lean")).read_text()
    examples = (LEAN / spec.get("fixtures", "VE/Defaults/Examples.lean")).read_text()
    used, module = tuple(spec.get("keep", [])), spec.get("module", "VE.Defaults.Premises")
    entries = spec["mutants"]
    ok = True
    control = run(premises, examples, used=used, module=module)
    print(f"control: {len(control)} failures")
    ok &= not control
    for e in entries:
        if "find" not in e:
            print(f"{e['id']} {e['definition']}: not run here ({e['test']})")
            continue
        assert premises.count(e["find"]) == 1, e["id"]
        failed = run(premises.replace(e["find"], e["replace"]), examples, keep="theorems" in e, used=used, module=module)
        hit = [x for x in e["guards"] if any(g.startswith(x[:90]) for g in failed)]
        hit += [t for t in e.get("theorems", []) if "THEOREM " + t in failed]
        want = len(e["guards"]) + len(e.get("theorems", []))
        good = failed and all(not g.startswith("NOT A GUARD") for g in failed) and len(hit) == want
        ok &= bool(good)
        print(f"{e['id']} {e['definition']}: {'FAILS' if good else 'SURVIVES'} {len(failed)} guards")
        for g in failed:
            print("   ", g)
    print("ALL MUTANTS FAIL THEIR GUARDS" if ok else "SOME MUTANT SURVIVES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
