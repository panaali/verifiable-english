"""ap-3d seeded bugs: plant each one, show that a fixture fails, restore the files.

    uv run python docs/act-phrases/ap-3d/seed_bugs.py

Each bug replaces one text in one product file. The theorem sections of Wire.lean, Elaborate.lean and Decode.lean
(from `/-! ### Theorems` to the namespace's `end`) are cut before every build, so a bug must break a fixture and not
only a proof; the other files' bugs leave their proofs true (texts and limits). A row is KILLED when
`lake build VE.Acts.DecodeExamples VE.Acts.ElaborateExamples` fails in an `*Examples.lean` file only, INVALID when a
product file is refused, SURVIVOR when the build passes. Writes mutants.json beside this file; exit 1 unless every
row is KILLED. Run it on a clean tree with the Lean build up to date.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "mutants.json"
CUT = ["lean/VE/Acts/Wire.lean", "lean/VE/Acts/Elaborate.lean", "lean/VE/Acts/Decode.lean"]
W, E, D, L, T, N = (f"lean/VE/{p}.lean" for p in
                    ("Acts/Wire", "Acts/Elaborate", "Acts/Decode", "Acts/Lexical", "Acts/Table", "NormDefaults/Wire"))

# (id, file, definition, from, to, claim)
BUGS = [
    ("joined-slot-unchecked", W, "joinedAct", "  if ts.any (fun t", "  if false && ts.any (fun t", "D-18"),
    ("joined-first-meaning-only", W, "joinedAct", '"the act phrase for {name}" As', '"the act phrase for {name}" (As.take 1)',
     "D-15 lists every meaning (G5d)"),
    ("joined-limit-as-none", W, "joinedAct", '  | .limit => throw s!"ResourceLimit: act phrase for {name} has too many',
     '  | .limit => throw s!"InvalidInput: act phrase for {name} has too many', "D-17 (L7)"),
    ("check-act-joined-refused", W, "checkAct", "    | .ok (act, ts) => (joinedAct fx V name ts).map",
     "    | .ok (act, ts) => (Except.error e : Except String Act).map", "A6, A7, A14 read from their text"),
    ("check-act-lexical-tree", W, "checkAct", "  | .ok a => .ok (a, none)", "  | .ok a => .ok (a, some (.one ⟨false, false, [], [], []⟩))",
     "checkAct_lexical: a lexical act has no tree"),
    ("check-with-comma-text", L, "checkWith", "ends with a comma\" else throw e", "ends in a comma\" else throw e",
     "conditions 1 to 5 keep their texts"),
    ("join-check-text", L, "joinCheck", "joins acts with '{w}' outside a fixed phrase", "joins acts with '{w}'",
     "condition 6 keeps D-4 on the norms route"),
    ("meaning-texts-subject-kept", T, "meaningTexts", "(Act.text fx none A).drop 4 ++", "(Act.text fx none A).drop 0 ++",
     "D-15's meanings without their subject (G5d)"),
    ("atoms-of-one", E, "atomsOf", "if 2 ≤ atoms.length", "if 1 ≤ atoms.length", "A7 stays one obligation"),
    ("splits-of-none", E, "splitsOf", "(x.1, atomsOf R)", "(x.1, none)", "A6 splits from step 1's readings"),
    ("part-names-in-kept-dropped", E, "partNamesIn", "  | [] => [p]", "  | [] => []", "E5: unsplit unspecified kept"),
    ("declared-after-no-parts", E, "declaredAfter", ".isSome).length + M.preds.length", ".isSome).length",
     "E13: the parts counted"),
    ("declared-after-sources-kept", E, "declaredAfter", "  D.declared - (D.U", "  D.declared + 0 * (D.U",
     "E13: the split sources not counted"),
    ("elaborate-map-step6-skipped", E, "elaborateMap", "  VE.NormDefaults.Wire.authorLimits (declaredAfter D sa M) U'",
     "  pure ()", "step 6 (E13 to E15)"),
    ("elaborate-map-steps-56-swapped", E, "elaborateMap",
     "  VE.Norms.validate U'.D\n  VE.NormDefaults.Wire.authorLimits (declaredAfter D sa M) U'",
     "  VE.NormDefaults.Wire.authorLimits (declaredAfter D sa M) U'\n  VE.Norms.validate U'.D", "step 5 before step 6"),
    ("author-limits-unspec-57", N, "authorLimits", "p.utf8ByteSize > 56", "p.utf8ByteSize > 57", "E14"),
    ("author-limits-rules-unspec", N, "authorLimits", "if U.D.T.nodes.length + U.unspec.length > 256",
     "if U.D.T.nodes.length > 256", "E15"),
    ("acts-of-dropped", D, "actsOf", "      pure (A.map (r.name, ·))", "      pure none", "the trees reach elaborateMap"),
    ("elaborate-source-acts-always", D, "elaborateSource", 'if s.src.ne.profiles.contains "acts@0" then', "if true then",
     "without acts@0 no act is read"),
    ("elaborate-source-declared-zero", D, "elaborateSource", "(VE.NormDefaults.Wire.declaredNames environment).length⟩",
     "0⟩", "declared from the environment"),
    ("elaborate-source-fixed-empty", D, "elaborateSource",
     "  let fx ← VE.Norms.Wire.actsFixed (VE.Norms.Wire.actsProfiles true environment) environment",
     "  let fx : List String := []", "the block's fixed phrases"),
    ("decode-norms-dropped", D, "decodeElaboratedU", "decodeSourceU environment norms >>=",
     "decodeSourceU environment (Json.arr #[]) >>=", "the source's rules are elaborated"),
]
DEFS = {W: ["joinedAct", "checkAct"], L: ["checkWith", "joinCheck"], T: ["meaningTexts"],
        E: ["atomsOf", "splitsOf", "partNamesIn", "declaredAfter", "elaborateMap"], N: ["authorLimits"],
        D: ["actsOf", "elaborateSource", "decodeElaboratedU"]}


def cut(text):
    i = text.index("/-! ### Theorems")
    j = text.rindex("\nend VE.")
    return text[:i] + text[j:]


def build():
    env = {**os.environ, "PATH": os.path.expanduser("~/.elan/bin") + os.pathsep + os.environ["PATH"]}
    r = subprocess.run(["lake", "build", "VE.Acts.DecodeExamples", "VE.Acts.ElaborateExamples"], cwd=ROOT / "lean",
                       env=env, capture_output=True, text=True)
    errs = sorted(set(re.findall(r"error: (VE/\S+?\.lean):", r.stdout + r.stderr)))
    return r.returncode, errs


def main():
    missing = [(f, d) for f, ds in DEFS.items() for d in ds if not any(b[1] == f and b[2] == d for b in BUGS)]
    if missing:
        sys.exit(f"definitions without a bug: {missing}")
    orig = {p: (ROOT / p).read_text() for p in {b[1] for b in BUGS} | set(CUT)}
    rows = []
    try:
        for bid, path, defn, old, new, claim in BUGS:
            text = {p: t for p, t in orig.items()}
            assert text[path].count(old) == 1, bid
            text[path] = text[path].replace(old, new)
            for p in CUT:
                text[p] = cut(text[p])
            for p, t in text.items():
                (ROOT / p).write_text(t)
            code, errs = build()
            status = ("SURVIVOR" if code == 0 else "KILLED" if errs and all(e.endswith("Examples.lean") for e in errs)
                      else "INVALID")
            rows.append({"id": bid, "file": path, "definition": defn, "claim": claim, "status": status, "tests": errs})
            print(status, bid, errs, flush=True)
    finally:
        for p, t in orig.items():
            (ROOT / p).write_text(t)
    code, errs = build()
    OUT.write_text(json.dumps({"restored_build": code, "mutants": rows}, indent=1) + "\n")
    sys.exit(0 if code == 0 and all(r["status"] == "KILLED" for r in rows) else 1)


if __name__ == "__main__":
    main()
