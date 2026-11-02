"""ap-3dd seeded bugs: plant each one, show the proof and a named fixture fail, restore the files.

    uv run python docs/act-phrases/ap-3dd/seed_bugs.py

Each bug replaces one or more texts. Every bug is built twice:

- `proof`: `lake build VE.Acts.Faithful` on the bug alone. It must fail: the theorem does not survive it.
- `guard`: the theorem sections of Elaborate.lean, Decode.lean and Faithful.lean are cut and the `#guard`s of
  ElaborateExamples.lean and DecodeExamples.lean are switched off, so `lake build VE.Acts.FaithfulExamples` reaches this
  item's fixtures; a `#guard` of FaithfulExamples.lean must fail, and no other file. A bug in `readAs` or `IntendedActs`
  is planted in `readM` or `intendedActsB` too: otherwise the tie (`readAs_asStructure`, `intendedActsB_iff`) is what
  breaks, and the guards would not be shown to read the definition.

A row is KILLED when both fail so. Writes mutants.json beside this file; exit 1 unless every row is KILLED. Run it on a
clean tree with the Lean build up to date.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "mutants.json"
E, D, F, X = (f"lean/VE/Acts/{p}.lean" for p in ("Elaborate", "Decode", "Faithful", "FaithfulExamples"))
EX, DX = "lean/VE/Acts/ElaborateExamples.lean", "lean/VE/Acts/DecodeExamples.lean"
OVER = "over := N.over.map (partRule · x.2) }"

# (id, definition, claim, [(file, from, to), ...])
BUGS = [
    ("part-sign-flipped", "splitNode (elaborateMap)", "each part keeps its source's sign (deliverable 3)",
     [(E, OVER, "sign := if x.2 == 2 then !N.sign else N.sign, " + OVER)]),
    ("part-guard-dropped", "splitNode (elaborateMap)", "each part keeps its source's guard",
     [(E, OVER, "guard := .top, " + OVER)]),
    ("part-carve-outs-dropped", "splitNode (elaborateMap)", "each part keeps its source's carve-outs",
     [(E, OVER, "carveOuts := [], " + OVER)]),
    ("part-precedence-dropped", "splitNode (elaborateMap)", "precedence splits pairwise, read on each part",
     [(E, OVER, "over := [] }")]),
    ("part-default-flipped", "splitReg (elaborateMap)", "each part keeps its source's default",
     [(E, "act := some (partAct D.fixed r.role x.1),\n", "act := some (partAct D.fixed r.role x.1), "
       "allowByDefault := !r.allowByDefault,\n")]),
    ("read-as-reads-the-source", "readAs", "the source's relation is read as the part",
     [(F, "fun r vs => if r = p then S.relation q vs else S.relation r vs", "fun r vs => S.relation r vs"),
      (X, "if r = p then M.relations q else M.relations r", "M.relations r")]),
    ("read-as-reads-every-name", "readAs", "only the source's relation is reread",
     [(F, "fun r vs => if r = p then S.relation q vs else S.relation r vs", "fun _ vs => S.relation q vs"),
      (X, "if r = p then M.relations q else M.relations r", "M.relations q")]),
    ("intended-acts-first-part", "IntendedActs", "every part is read, not the first",
     [(F, "∀ q ∈ partNames D r.name, VE.Norms.IntendedAt", "∀ q ∈ (partNames D r.name).take 1, VE.Norms.IntendedAt"),
      (X, "(partNames D r.name).all fun q", "((partNames D r.name).take 1).all fun q")]),
    ("intended-acts-last-predicate-only", "IntendedActs", "every source predicate is read",
     [(F, "∀ r ∈ D.U.D.T.regulated, ∀ q ∈ partNames", "∀ r ∈ D.U.D.T.regulated.take 1, ∀ q ∈ partNames"),
      (X, "D.U.D.T.regulated.all fun r => (partNames", "(D.U.D.T.regulated.take 1).all fun r => (partNames")]),
    ("intended-acts-without-reading", "IntendedActs", "the source rules are read of the part",
     [(F, "VE.Norms.IntendedAt D.U.D.T r (readAs r.name q S)", "VE.Norms.IntendedAt D.U.D.T r S"),
      (X, "intendedB D.U.D.T r (readM r.name q M)", "intendedB D.U.D.T r M")]),
]
SILENCE = "\nlocal macro_rules | `(#guard $_:term) => `(section\nend)\n"


def cut(path, text):
    """Drop `path`'s theorem section; `#guard`s stay in FaithfulExamples.lean alone."""
    if path == F:
        return text[:text.index("/-! ### What `elaborateMap` leaves -/")] + "end VE.Acts\n"
    if path in (E, D):
        return text[:text.index("/-! ### Theorems")] + text[text.rindex("\nend VE."):]
    head, rest = re.match(r"(.*?\nnamespace [^\n]*\n)(.*)", text, re.S).groups()
    return head + SILENCE + rest


def build(target):
    env = {**os.environ, "PATH": os.path.expanduser("~/.elan/bin") + os.pathsep + os.environ["PATH"]}
    r = subprocess.run(["lake", "build", target], cwd=ROOT / "lean", env=env, capture_output=True, text=True)
    out = r.stdout + r.stderr
    errs = sorted(set(re.findall(r"error: (VE/\S+?\.lean:\d+):", out)))
    return r.returncode, errs, sorted(set(re.findall(r"error: (VE/\S+?\.lean:\d+):\d+: Expression\n", out)))


def plant(orig, edits, cuts=()):
    text = dict(orig)
    for path, old, new in edits:
        assert text[path].count(old) == 1, old
        text[path] = text[path].replace(old, new)
    for path in cuts:
        text[path] = cut(path, text[path])
    for path, t in text.items():
        (ROOT / path).write_text(t)


def main():
    orig = {p: (ROOT / p).read_text() for p in (E, D, F, X, EX, DX)}
    rows = []
    try:
        for bid, defn, claim, edits in BUGS:
            plant(orig, edits)
            pcode, perrs, _ = build("VE.Acts.Faithful")
            plant(orig, edits, (E, D, F, EX, DX))
            gcode, gerrs, guards = build("VE.Acts.FaithfulExamples")
            xfile = X.removeprefix("lean/")
            killed = pcode != 0 and bool(guards) and all(e.startswith(xfile) for e in gerrs)
            rows.append({"id": bid, "file": edits[0][0], "definition": defn, "claim": claim,
                         "status": "KILLED" if killed else "SURVIVOR" if gcode == 0 else "INVALID",
                         "proof_fails_at": perrs[:6], "test": guards[0] if guards else None, "guards": guards})
            print(rows[-1]["status"], bid, perrs[:3], len(guards), gerrs[:3], flush=True)
    finally:
        for p, t in orig.items():
            (ROOT / p).write_text(t)
    code, _, _ = build("VE.Acts.FaithfulExamples")
    OUT.write_text(json.dumps({"restored_build": code, "mutants": rows}, indent=1) + "\n")
    sys.exit(0 if code == 0 and all(r["status"] == "KILLED" for r in rows) else 1)


if __name__ == "__main__":
    main()
