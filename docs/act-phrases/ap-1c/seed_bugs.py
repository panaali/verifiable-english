"""Seeded bugs of ap-1c: each makes `check_extends` false, and must break its proof; planted, built and restored.

    uv run python docs/act-phrases/ap-1c/seed_bugs.py [--only ID ...]

A Lean mutant replaces one exact text of `lean/VE/Acts/Lexical.lean` (it must occur once) and builds
`VE.Acts.Compat`. It is killed when the build fails in `Compat.lean` or `LexicalProofs.lean` (the proof of
`check_extends` and its lemmas), not in the mutated file itself. `why` is an act today's `canonicalAct` accepts,
without *nor*, that the mutated `check` refuses or rewrites, so the theorem is false under the mutant. The Python
mutant is killed when `tools/check_lean_imports.py` fails. Results go to `mutants.json` beside this script.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
LEX, POLICY = "lean/VE/Acts/Lexical.lean", "tools/layer_policy.py"
BUILD = ["lake", "build", "VE.Acts.Compat"]
IMPORTS = ["uv", "run", "python", "tools/check_lean_imports.py"]
PROOFS = re.compile(r"error: (VE/Acts/(?:Compat|LexicalProofs)\.lean:\d+):\d+: (.*)")

# (id, definition, file, old, new, why); file POLICY runs IMPORTS instead of BUILD
MUTANTS = [
    ("check-start", "check", LEX, 'unless act.startsWith "{0} " &&', 'unless act.startsWith "{0}  " &&',
     "every act: '{0} vote'"),
    ("check-slots", "check", LEX, "slots == (List.range arity).map toString",
     "slots == (List.range (arity + 1)).map toString", "'{0} vote' at arity 1"),
    ("check-two-words", "check", LEX, "ws.length ≥ 2 &&", "ws.length ≥ 3 &&", "'{0} vote'"),
    ("maxActBytes", "maxActBytes", LEX, "def maxActBytes : Nat := 400", "def maxActBytes : Nat := 79",
     "an act of 80 characters"),
    ("joinWords-extra", "joinWords", LEX, '["and", "or", "nor", "for"]', '["and", "or", "nor", "for", "the"]',
     "'{0} read the news'"),
    ("normal-spacing", "normal", LEX, '" ".intercalate (words (fold s))', '"  ".intercalate (words (fold s))',
     "'{0} seek asylum' read as '{0}  seek  asylum'"),
    ("fold-letter", "fold", LEX, "if c.toNat == 0x2019 then", "if c.toNat == 0x2019 || c == 'z' then",
     "'{0} seize land' read as '{0} sei'e land'"),
    ("dropComma-letter", "dropComma", LEX, 'if w.endsWith "," then', 'if w.endsWith "e" then',
     "'{0} note' read as the clause word 'not'"),
    ("pieceToks-hyphen", "pieceToks", LEX, "body.isEmpty || body.contains ','",
     "body.isEmpty || body.contains ',' || body.contains '-'", "'{0} re-enter'"),
    ("rawLex-length", "rawLex", LEX, 'if ts.getLast? == some Tok.comma then throw "comma"',
     'if ts.length > 4 then throw "comma"', "'{0} seek asylum in other countries'"),
    ("group-comma", "group", LEX, "| some i => .fixed i :: group ps n", "| some i => .comma :: group ps n",
     "'{0} seek asylum' with the fixed phrase 'seek asylum'"),
    ("layer-policy", "lean_layer", POLICY, '"VE.Acts.LexicalProofs", ', "",
     "VE.Acts.LexicalProofs falls to layer 3 under VE.Acts.Compat (layer 2)"),
]


def run(mutant) -> dict:
    ident, definition, path, old, new, why = mutant
    target = ROOT / path
    text = target.read_text()
    assert text.count(old) == 1, f"{ident}: {old!r} occurs {text.count(old)} times in {path}"
    target.write_text(text.replace(old, new))
    env = {**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}
    try:
        lean = path != POLICY
        proc = subprocess.run(BUILD if lean else IMPORTS, cwd=ROOT / "lean" if lean else ROOT, env=env,
                              capture_output=True, text=True)
    finally:
        subprocess.run(["git", "checkout", "--", path], cwd=ROOT, check=True)
    out = proc.stdout + proc.stderr
    if lean:
        found = PROOFS.search(out)
        test = f"lean/{found.group(1)}: {found.group(2)[:100]}" if found else ""
    else:
        test = next((line.strip() for line in out.splitlines() if "outward" in line), "")
    return {"id": ident, "definition": definition, "file": path, "mutation": [old, new], "why": why,
            "test": test, "killed": proc.returncode != 0 and bool(test)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    results = [run(m) for m in MUTANTS if not args.only or m[0] in args.only]
    for r in results:
        print("KILLED  " if r["killed"] else "SURVIVED", r["id"], "|", r["test"])
    if not args.only:
        lines = ",\n".join(" " + json.dumps(r, ensure_ascii=False) for r in results)
        (Path(__file__).parent / "mutants.json").write_text("[\n" + lines + "\n]\n")
    env = {**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}
    subprocess.run(BUILD, cwd=ROOT / "lean", env=env, check=True, capture_output=True)
    raise SystemExit(0 if all(r["killed"] for r in results) else 1)


if __name__ == "__main__":
    main()
