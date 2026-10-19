"""Seeded bugs of ap-1a: at least one per new trusted definition (R16), each planted, built and restored.

    uv run python docs/act-phrases/ap-1a/seed_bugs.py [--only ID ...]

Each mutant replaces one exact text in one file (it must occur once), builds `VE.Acts.LexicalExamples` (its
import closure holds `VE.Acts.Lexical` and `VE.Norms.Wire`) or runs its check, and restores the file from git.
A mutant is killed when the build fails at a `#guard` of `LexicalExamples.lean` or at a proof, or when its check
exits non-zero; the result names the first failing line. The results go to `mutants.json` beside this script.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
LEX, WIRE, POLICY = "lean/VE/Acts/Lexical.lean", "lean/VE/Norms/Wire.lean", "tools/layer_policy.py"
BUILD = ["lake", "build", "VE.Acts.LexicalExamples"]
IMPORTS = ["uv", "run", "python", "tools/check_lean_imports.py"]
COMPAT = ["lake", "-d", "lean", "build", "VE.Acts.Compat"]  # the proof of wording_subject_first, not the fixtures

# (id, definition, file, old, new, check); check None is BUILD
MUTANTS = [
    ("joinWords-nor", "joinWords", LEX, '["and", "or", "nor", "for"]', '["and", "or", "for"]', None),
    ("joinWords-for", "joinWords", LEX, '["and", "or", "nor", "for"]', '["and", "or", "nor"]', None),
    ("clauseWords-all", "clauseWords", LEX, "actReserved.filter (fun w => !joinWords.contains w)", "actReserved", None),
    ("maxActBytes", "maxActBytes", LEX, "def maxActBytes : Nat := 400", "def maxActBytes : Nat := 401", None),
    ("maxPhraseBytes", "maxPhraseBytes", LEX, "def maxPhraseBytes : Nat := 300", "def maxPhraseBytes : Nat := 299", None),
    ("maxPhrases", "maxPhrases", LEX, "def maxPhrases : Nat := 128", "def maxPhrases : Nat := 127", None),
    ("fold-codepoint", "fold", LEX, "c.toNat == 0x2019", "c.toNat == 0x2018", None),
    ("normal-no-fold", "normal", LEX, '" ".intercalate (words (fold s))', '" ".intercalate (words s)', None),
    ("dropComma-keeps", "dropComma", LEX, "then w.dropRight 1 else w", "then w else w", None),
    ("slotOf-length", "slotOf?", LEX, "w.length ≥ 3", "w.length ≥ 2", None),
    ("slotOf-digits", "slotOf?", LEX, "if d.all Char.isDigit then", "if true then", None),
    ("pieceToks-no-comma", "pieceToks", LEX, "then [t, Tok.comma] else [t]", "then [t] else [t]", None),
    ("pieceToks-inner-comma", "pieceToks", LEX, "body.isEmpty || body.contains ','", "body.isEmpty", None),
    ("rawLex-final-comma", "rawLex", LEX, 'if ts.getLast? == some Tok.comma then throw "comma"', "", None),
    ("phraseToks-bytes", "phraseToks", LEX, "n.utf8ByteSize > maxPhraseBytes", "n.utf8ByteSize ≥ maxPhraseBytes", None),
    ("phraseToks-clause", "phraseToks", LEX, "if clauseWords.contains w.toLower then", "if clauseWords.contains w then", None),
    ("phraseToks-two-words", "phraseToks", LEX, "unless nw ≥ 2 do", "unless nw ≥ 1 do", None),
    ("phraseToks-last-edge", "phraseToks", LEX, "edgeOk ts.head? && edgeOk ts.getLast?", "edgeOk ts.head?", None),
    ("clash-self", "clash", LEX, "(k != 0 || p != q)", "(p != q)", None),
    ("clash-suffix", "clash", LEX, "(r.isPrefixOf q || q.isPrefixOf r)", "(q.isPrefixOf r)", None),
    ("clash-contained", "clash", LEX, "(r.isPrefixOf q || q.isPrefixOf r)", "(r.isPrefixOf q)", None),
    ("decodeFixed-limit", "decodeFixed", LEX, "fx.length > maxPhrases", "fx.length ≥ maxPhrases", None),
    ("decodeFixed-twice", "decodeFixed", LEX, "if i < j ∧ p = q then", "if i < j ∧ p = q ∧ i = 0 then", None),
    ("fixedOk-true", "fixedOk", LEX, "def fixedOk (fx : List String) : Bool := (decodeFixed fx).isOk",
     "def fixedOk (_fx : List String) : Bool := true", None),
    ("group-short", "group", LEX, ".fixed i :: group ps n ((t :: rest).drop (ps.getD i []).length)",
     ".fixed i :: group ps n ((t :: rest).drop 1)", None),
    ("lex-no-group", "lex", LEX, "pure (group ps ts.length ts)", "pure ts", None),
    ("check-start", "check", LEX, 'unless act.startsWith "{0} " && slots', "unless slots", None),
    ("check-bytes", "check", LEX, "act.utf8ByteSize ≤ maxActBytes", "act.utf8ByteSize < maxActBytes", None),
    ("check-clause-comma", "check", LEX, "clauseWords.contains (dropComma w).toLower", "clauseWords.contains w.toLower",
     None),
    ("check-join-accepted", "check", LEX,
     '| some (.word w) => throw s!"InvalidInput: act phrase for {name} joins acts with \'{w}\' outside a fixed phrase"',
     "| some (.word _) => pure act", None),
    ("check-comma-passes", "check", LEX, "| .word w => joinWords.contains w.toLower | .comma => true | _ => false",
     "| .word w => joinWords.contains w.toLower | .comma => false | _ => false", None),
    ("check-join-case", "check", LEX, "| .word w => joinWords.contains w.toLower", "| .word w => joinWords.contains w",
     None),
    ("Form.text-swap", "Form.text", LEX, '| .right => "has the right"', '| .right => "is entitled"', None),
    ("Form.ofText-entitled", "Form.ofText?", LEX, 'else if s == "is entitled" then', 'else if s == "is entitled to" then',
     None),
    ("wording-drop", "wording", LEX, "act.drop 4", "act.drop 3", None),
    ("wording-subject", "wording", LEX, ':= "{0} " ++ f.text', ':= "{1} " ++ f.text', COMPAT),
    ("canonicalActIn-profile", "canonicalActIn", WIRE,
     'if profiles.contains "acts@0" then VE.Acts.Lexical.check', 'if profiles.contains "acts@1" then VE.Acts.Lexical.check',
     None),
    ("decodeRegulatedIn-off", "decodeRegulatedIn", WIRE, 'decodeRegulatedWith (profiles.contains "acts@0")',
     "decodeRegulatedWith false", None),
    ("decodeRegulatedWith-plain-fields", "decodeRegulatedWith", WIRE, "(if acts && role == .plain then [\"act\", \"form\"]",
     "(if role == .plain then [\"act\", \"form\"]", None),
    ("decodeRegulatedWith-both-or-neither", "decodeRegulatedWith", WIRE,
     'if keys.contains "act" != keys.contains "form" then', 'if keys.contains "act" && !keys.contains "form" then', None),
    ("decodeRegulatedWith-form", "decodeRegulatedWith", WIRE, "VE.Acts.Lexical.Form.ofText?).isNone",
     "VE.Acts.Lexical.Form.ofText?).isNone && false", None),
    ("decodeRegulatedWith-plain-act", "decodeRegulatedWith", WIRE, "role == .plain && !(acts && keys.contains \"act\")",
     "role == .plain && !acts", None),
    ("layer-policy", "lean_layer", POLICY, '"VE.Acts.LexicalBase", "VE.Acts.Lexical", ', "", IMPORTS),
]


THEOREMS = "/-! ### Theorems (4.3) -/"


def run(mutant, fixtures_only: bool = False) -> dict:
    ident, definition, path, old, new, check = mutant
    target = ROOT / path
    text = target.read_text()
    assert text.count(old) == 1, f"{ident}: {old!r} occurs {text.count(old)} times in {path}"
    mutated = text.replace(old, new)
    if fixtures_only:
        mutated = mutated[:mutated.index(THEOREMS)] + "end VE.Acts.Lexical\n"
    target.write_text(mutated)
    env = {**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}
    try:
        cwd = ROOT if check else ROOT / "lean"
        proc = subprocess.run(check or BUILD, cwd=cwd, env=env, capture_output=True, text=True)
    finally:
        subprocess.run(["git", "checkout", "--", path], cwd=ROOT, check=True)
    out = proc.stdout + proc.stderr
    if check:
        found = re.search(r"error: (VE/\S+\.lean:\d+):\d+: (.*)", out)
        failed = (f"lean/{found.group(1)}: {found.group(2)[:120]}" if found else
                  next((line for line in out.splitlines() if "outward" in line), out.strip()[-200:]))
    else:
        found = re.search(r"error: (VE/\S+\.lean:\d+):\d+: (.*)", out)
        failed = f"lean/{found.group(1)}: {found.group(2)[:120]}" if found else ""
    result = {"id": ident, "definition": definition, "file": path, "mutation": [old, new],
              "test": failed, "killed": proc.returncode != 0}
    if not fixtures_only and path == LEX and failed.startswith(LEX):
        # caught by a proof of Lexical.lean: plant it again without the proofs, so a fixture must catch it too
        again = run(mutant, fixtures_only=True)
        result["fixtures_only"] = again["test"]
        result["killed"] = result["killed"] and again["killed"]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    chosen = [m for m in MUTANTS if not args.only or m[0] in args.only]
    results = [run(m) for m in chosen]
    for r in results:
        print(("KILLED  " if r["killed"] else "SURVIVED"), r["id"], "|", r["test"], "|", r.get("fixtures_only", ""))
    if not args.only:
        (Path(__file__).parent / "mutants.json").write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n")
    subprocess.run(BUILD, cwd=ROOT / "lean", env={**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"},
                   check=True, capture_output=True)
    raise SystemExit(0 if all(r["killed"] for r in results) else 1)


if __name__ == "__main__":
    main()
