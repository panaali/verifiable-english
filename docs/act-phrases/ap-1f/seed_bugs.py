"""Seeded bugs of ap-1f: each makes `decodeRegulated_plain` (or its helper `ite_ok_cases`) false and must break it.

    uv run python docs/act-phrases/ap-1f/seed_bugs.py [--only ID ...]

A mutant replaces exact texts of `lean/VE/Norms/Wire.lean` (each must occur once) and builds `VE.Norms.Wire`. It is
killed only when the build fails with an error in `Wire.lean` inside one of the theorems the mutant names. An error
in the mutated definition itself, or only in another theorem, never counts. `why` is an input on which the mutant
makes the target false. Results go to `mutants.json` beside this script; `--only` replaces the rows it runs.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
WIRE = "lean/VE/Norms/Wire.lean"
ERROR = re.compile(r"error: VE/Norms/Wire\.lean:(\d+):\d+: (.*)")
HEAD = re.compile(r"^(?:theorem|def) (\S+)")
PLAIN = ("decodeRegulated_plain",)

# (id, definition, [(old, new)], targets that must break, why)
MUTANTS = [
    ("plain-some", "decodeRegulatedWith", [("then pure none", "then pure (some name)")], PLAIN,
     "{role: plain, default: allow}: the plain predicate p decodes with the act 'p'"),
    ("acts-on", "decodeRegulated", [("decodeRegulatedWith false canonicalAct", "decodeRegulatedWith true canonicalAct")],
     PLAIN, "{role: plain, default: allow, act: '{0} vote', form: 'base'}: today's decoder reads the act"),
    ("plain-act-key", "decodeRegulatedWith",
     [('(if acts && role == .plain then ["act", "form"] else [])', '(if role == .plain then ["act", "form"] else [])'),
      ('!(acts && keys.contains "act")', '!keys.contains "act"')], PLAIN,
     "{role: plain, default: allow, act: '{0} vote'}: the act key is allowed and read without acts@0"),
    ("ite-swap", "ite_ok_cases", [("(c ∧ a = .ok r) ∨ (¬c ∧ b = .ok r)", "(c ∧ b = .ok r) ∨ (¬c ∧ a = .ok r)")],
     ("ite_ok_cases",), "if True then .ok 1 else .ok 2 is .ok 1, not .ok 2"),
]


def target_at(text: str, line: int) -> str:
    """The theorem or definition whose source holds `line` (the last header at or above it)."""
    for row in reversed(text.splitlines()[:line]):
        if m := HEAD.match(row):
            return m.group(1)
    return ""


def build(env) -> subprocess.CompletedProcess:
    return subprocess.run(["lake", "build", "VE.Norms.Wire"], cwd=ROOT / "lean", env=env, capture_output=True,
                          text=True)


def run(mutant, env) -> dict:
    ident, definition, edits, targets, why = mutant
    target = ROOT / WIRE
    text = target.read_text()
    mutated = text
    for old, new in edits:
        assert mutated.count(old) == 1, f"{ident}: {old!r} occurs {mutated.count(old)} times in {WIRE}"
        mutated = mutated.replace(old, new)
    target.write_text(mutated)
    try:
        proc = build(env)
    finally:
        subprocess.run(["git", "checkout", "--", WIRE], cwd=ROOT, check=True)
    errors = [(m, target_at(mutated, int(m.group(1)))) for m in ERROR.finditer(proc.stdout + proc.stderr)]
    found = [(m, where) for m, where in errors if where in targets]
    test = "; ".join(f"{WIRE}:{m.group(1)} ({where}): {m.group(2)[:70]}" for m, where in found[:3])
    return {"id": ident, "definition": definition, "file": WIRE, "mutation": edits, "why": why,
            "targets": list(targets), "test": test, "killed": proc.returncode != 0 and bool(found)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    env = {**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}
    results = [run(m, env) for m in MUTANTS if not args.only or m[0] in args.only]
    for r in results:
        print("KILLED  " if r["killed"] else "SURVIVED", r["id"], "|", r["test"])
    saved = Path(__file__).parent / "mutants.json"
    if args.only and saved.exists():
        fresh, seeded = {r["id"]: r for r in results}, {r["id"]: r for r in json.loads(saved.read_text())}
        results = [fresh.get(m[0]) or seeded[m[0]] for m in MUTANTS if m[0] in fresh or m[0] in seeded]
    saved.write_text("[\n" + ",\n".join(" " + json.dumps(r, ensure_ascii=False) for r in results) + "\n]\n")
    assert build(env).returncode == 0, "the restored tree does not build"
    raise SystemExit(0 if all(r["killed"] for r in results) else 1)


if __name__ == "__main__":
    main()
