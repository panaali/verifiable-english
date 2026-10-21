"""Seeded bugs of ap-1d: each makes a theorem of `LexicalProofs.lean` false and must break its proof.

    uv run python docs/act-phrases/ap-1d/seed_bugs.py [--only ID ...]

A mutant replaces one exact text of a Lean file (it must occur once) and builds `VE.Acts.LexicalProofs`. It is
killed only when the build fails with an error in `LexicalProofs.lean` inside one of the theorems the mutant names
(the theorem or a lemma of its proof; Lean reports every failed declaration), so an error in the mutated
definition itself, or only in an earlier lemma, never counts.
`why` is an input on which the mutated definition makes the theorem false. Results go to `mutants.json` beside
this script; `--only` replaces the rows it runs.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
LEX, PROOF = "lean/VE/Acts/Lexical.lean", "lean/VE/Acts/LexicalProofs.lean"
ERROR = re.compile(r"error: VE/Acts/LexicalProofs\.lean:(\d+):\d+: (.*)")
SPEC, NO_CLAUSE = ("check_iff", "check_spec"), ("check_no_clause",)
UNIQUE = ("decodeFixed_ok", "clash_of_overlap", "fixedOk_unique")

# (id, definition, file, old, new, theorems that must break, why)
MUTANTS = [
    ("check-start", "check", LEX, 'unless act.startsWith "{0} " &&', "unless true &&", SPEC,
     "'vote {0} now' at arity 1: `check` accepts it, `Accepts` asks for the start '{0} '"),
    ("check-size", "check", LEX, "unless act.utf8ByteSize ≤ maxActBytes do", "unless act.utf8ByteSize < maxActBytes do",
     SPEC, "an act of exactly 400 bytes: `Accepts` holds, `check` refuses it"),
    ("clauseWords-slot", "clauseWords", LEX, "def clauseWords : List String := VE.Norms.Wire.actReserved.filter",
     'def clauseWords : List String := "slot" :: VE.Norms.Wire.actReserved.filter', NO_CLAUSE,
     "'{0} play the slot': `check` exempts the word 'slot', which is now a clause word"),
    ("decodeFixed-twice", "decodeFixed", LEX, "if i < j ∧ p = q then throw", "if i < j ∧ p = q ∧ i = 0 then throw",
     UNIQUE, "fixed phrases ['a b', 'c d', 'c d']: the two 'c d' occur at one place"),
    ("decodeFixed-self", "decodeFixed", LEX, "if (i = j ∧ clash p p = true) ∨",
     "if (i = j ∧ clash p p = true ∧ i > 0) ∨", UNIQUE,
     "fixed phrase 'free to be free' first: it occurs at 0 and 3 of 'free to be free to be free'"),
    ("clash-start", "clash", LEX, "(k != 0 || p != q) &&", "(k != 0) &&", UNIQUE,
     "fixed phrases ['seek asylum', 'seek asylum now']: both occur at 0 of 'seek asylum now'"),
    ("Accepts-words", "Accepts", PROOF, "(List.range k).map toString ∧ 2 ≤ ws.length ∧",
     "(List.range k).map toString ∧ 3 ≤ ws.length ∧", SPEC, "'{0} vote': `check` accepts it, `Accepts` asks 3 words"),
]


def theorem_at(text: str, line: int) -> str:
    """The theorem whose source holds `line` (the last `theorem` header at or above it)."""
    names = [m.group(1) for m in re.finditer(r"^theorem (\S+)", "\n".join(text.splitlines()[:line]), re.M)]
    return names[-1] if names else ""


def build(env) -> subprocess.CompletedProcess:
    return subprocess.run(["lake", "build", "VE.Acts.LexicalProofs"], cwd=ROOT / "lean", env=env,
                          capture_output=True, text=True)


def run(mutant, env) -> dict:
    ident, definition, path, old, new, theorems, why = mutant
    target = ROOT / path
    text = target.read_text()
    assert text.count(old) == 1, f"{ident}: {old!r} occurs {text.count(old)} times in {path}"
    target.write_text(text.replace(old, new))
    try:
        proc = build(env)
        mutated = (ROOT / PROOF).read_text()
    finally:
        subprocess.run(["git", "checkout", "--", path], cwd=ROOT, check=True)
    errors = [(m, theorem_at(mutated, int(m.group(1)))) for m in ERROR.finditer(proc.stdout + proc.stderr)]
    found = next(((m, where) for m, where in errors if where in theorems), None)
    test = f"{PROOF}:{found[0].group(1)} ({found[1]}): {found[0].group(2)[:90]}" if found else ""
    return {"id": ident, "definition": definition, "file": path, "mutation": [old, new], "why": why,
            "theorems": list(theorems), "test": test, "killed": proc.returncode != 0 and found is not None}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    env = {**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}
    results = [run(m, env) for m in MUTANTS if not args.only or m[0] in args.only]
    for r in results:
        print("KILLED  " if r["killed"] else "SURVIVED", r["id"], "|", r["test"])
    saved = Path(__file__).parent / "mutants.json"
    if args.only:
        fresh = {r["id"]: r for r in results}
        old = {r["id"]: r for r in json.loads(saved.read_text())}
        results = [fresh.get(m[0]) or old[m[0]] for m in MUTANTS if m[0] in fresh or m[0] in old]
    saved.write_text("[\n" + ",\n".join(" " + json.dumps(r, ensure_ascii=False) for r in results) + "\n]\n")
    assert build(env).returncode == 0, "the restored tree does not build"
    raise SystemExit(0 if all(r["killed"] for r in results) else 1)


if __name__ == "__main__":
    main()
