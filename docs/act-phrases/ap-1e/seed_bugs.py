"""Seeded bugs of ap-1e: each makes a theorem or a `#guard` of `LexicalProofs.lean` false and must break it.

    uv run python docs/act-phrases/ap-1e/seed_bugs.py [--only ID ...]

A mutant replaces one exact text of a Lean file (it must occur once) and builds `VE.Acts.LexicalProofs`. It is
killed only when the build fails with an error in `LexicalProofs.lean` inside one of the targets the mutant names:
a theorem (the theorem or a lemma of its proof) or `#guard` (a fixture line). An error in the mutated definition
itself, or only in an earlier lemma, never counts. `why` is an input on which the mutant makes the target false.
Results go to `mutants.json` beside this script; `--only` replaces the rows it runs.
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
HEAD = re.compile(r"^(?:theorem|def|instance) (\S+)|^(#guard)\b")
GROUP = ("group_expand", "group_maximal", "group_range", "group_spec")
UNIQUE = ("grouped_fixed", "grouped_ne_nil", "grouped_fixed_head", "grouped_unique")
GUARD = ("#guard",)

# (id, definition, file, old, new, targets that must break, why)
MUTANTS = [
    ("group-rest", "group", LEX, "| none => t :: group ps n rest", "| none => t :: rest", GROUP,
     "phrase 'b c' in tokens [a, b, c]: after the ungrouped 'a', 'b c' stays ungrouped"),
    ("group-empty", "group", LEX, "fun i => !(ps.getD i []).isEmpty && (ps.getD i [])", "fun i => (ps.getD i [])",
     GROUP, "phrases [[], 'seek asylum']: the empty phrase 0 is grouped, a fixed token naming no phrase"),
    ("lex-fuel", "lex", LEX, "pure (group ps ts.length ts)", "pure (group ps (ts.length - 1) ts)", ("lex_spec",),
     "'{0} seek asylum' with phrase 'seek asylum': the fuel ends before the phrase"),
    ("rawLex-fixed", "pieceToks", LEX, "| some i => Tok.slot i", "| some i => Tok.fixed i", ("rawLex_plain",),
     "'{0} vote': rawLex makes the slot a fixed token"),
    ("expand-fixed", "expand", PROOF, "| .fixed i => ps.getD i []", "| .fixed i => []", GUARD,
     "phrase 'seek asylum' grouped: written out it loses its words"),
    ("expand-plain", "expand", PROOF, "    | t => [t]", "    | _ => []", GUARD,
     "[{0}, fixed 1, ',', fixed 0, now]: written out it keeps only the phrases"),
    ("Grouped-written", "Grouped", PROOF, "(ps[i]).isPrefixOf (t :: expand ps post) = false\n\ntheorem",
     "(ps[i]).isPrefixOf (t :: post) = false\n\ntheorem", ("group_spec",) + GUARD,
     "phrases ['seek asylum', 'to seek'] on 'to seek asylum' grouped [to, fixed 0]: 'to seek' starts at 'to'"),
    ("Grouped-range", "Grouped", PROOF, "t = .fixed i → ps.getD i [] ≠ []) ∧", "t = .fixed i → True) ∧",
     UNIQUE + GUARD, "phrase [] declared: [] and [fixed 0] both group []"),
    ("Grouped-empty", "Grouped", PROOF, "\n    ∀ i (hi : i < ps.length), ps[i] ≠ [] →",
     "\n    ∀ i (hi : i < ps.length),", ("group_spec",) + GUARD,
     "phrases [[], 'seek asylum'] on [{0}, seek]: the empty phrase is a prefix of every list"),
    ("Grouped-plain", "Grouped", PROOF, "t :: post <:+ g → (∀ i, t ≠ .fixed i) →\n", "t :: post <:+ g →\n",
     ("group_spec",) + GUARD, "phrases ['seek asylum', [fixed 0]] on 'seek asylum' grouped [fixed 0]"),
]


def target_at(text: str, line: int) -> str:
    """The theorem, definition or `#guard` whose source holds `line` (the last header at or above it)."""
    for row in reversed(text.splitlines()[:line]):
        if m := HEAD.match(row):
            return m.group(1) or m.group(2)
    return ""


def build(env) -> subprocess.CompletedProcess:
    return subprocess.run(["lake", "build", "VE.Acts.LexicalProofs"], cwd=ROOT / "lean", env=env,
                          capture_output=True, text=True)


def run(mutant, env) -> dict:
    ident, definition, path, old, new, targets, why = mutant
    target = ROOT / path
    text = target.read_text()
    assert text.count(old) == 1, f"{ident}: {old!r} occurs {text.count(old)} times in {path}"
    target.write_text(text.replace(old, new))
    try:
        proc = build(env)
        mutated = (ROOT / PROOF).read_text()
    finally:
        subprocess.run(["git", "checkout", "--", path], cwd=ROOT, check=True)
    errors = [(m, target_at(mutated, int(m.group(1)))) for m in ERROR.finditer(proc.stdout + proc.stderr)]
    found = [(m, where) for m, where in errors if where in targets]
    test = "; ".join(f"{PROOF}:{m.group(1)} ({where}): {m.group(2)[:70]}" for m, where in found[:3])
    return {"id": ident, "definition": definition, "file": path, "mutation": [old, new], "why": why,
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
    if args.only:
        fresh = {r["id"]: r for r in results}
        old = {r["id"]: r for r in json.loads(saved.read_text())}
        results = [fresh.get(m[0]) or old[m[0]] for m in MUTANTS if m[0] in fresh or m[0] in old]
    saved.write_text("[\n" + ",\n".join(" " + json.dumps(r, ensure_ascii=False) for r in results) + "\n]\n")
    assert build(env).returncode == 0, "the restored tree does not build"
    raise SystemExit(0 if all(r["killed"] for r in results) else 1)


if __name__ == "__main__":
    main()
