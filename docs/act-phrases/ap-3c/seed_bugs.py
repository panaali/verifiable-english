"""ap-3c seeded bugs: plant each one in Elaborate.lean, show that a fixture fails, restore the file.

    uv run python docs/act-phrases/ap-3c/seed_bugs.py

Every new definition of lean/VE/Acts/Elaborate.lean carries at least one bug (`DEFS`; the script refuses to run when
one has none). The file's theorems are cut before every build, so a bug must break a fixture of
ElaborateExamples.lean, not only a proof. A row is KILLED when `lake build VE.Acts.ElaborateExamples` fails in
ElaborateExamples.lean only (a failed `#guard`, or a fixture the mutated type no longer elaborates), INVALID when
Elaborate.lean itself is refused, SURVIVOR when the build passes. Every row must be KILLED. Writes mutants.json beside
this file. Run it on a clean tree with the Lean build up to date.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "mutants.json"
SRC = "lean/VE/Acts/Elaborate.lean"
TEST = "lean/VE/Acts/ElaborateExamples.lean"
DEFS = ["ActsDoc", "SplitMap", "partPred", "partRule", "dualOf", "ruleReading", "readingOf", "splitAtoms", "partsOf",
        "splitMap", "partNames", "splitReg", "splitNode", "splitEnv", "splitDoc", "refsOk", "namesOk", "partsDistinct",
        "elaborateMap", "elaborate"]

# (id, definition, from, to, claim)
BUGS = [
    ("acts-doc-fields-reordered", "ActsDoc", "  U : VE.NormDefaults.UDoc\n  V : Vocab\n",
     "  V : Vocab\n  U : VE.NormDefaults.UDoc\n", "C1 the document's fields as 6.3 lists them"),
    ("split-map-fields-swapped", "SplitMap", "  preds : List (String × String × Nat)\n  /-- generated `<rule>-a<i>`, its source rule, i -/\n  rules :",
     "  rules : List (String × String × Nat)\n  /-- generated `<rule>-a<i>`, its source rule, i -/\n  preds :",
     "C2 the map's predicates and rules (E1)"),
    ("part-pred-one-underscore", "partPred", 'p ++ "__" ++ toString i', 'p ++ "_" ++ toString i', "C2 part names p__i"),
    ("part-rule-no-a", "partRule", 'n ++ "-a" ++ toString i', 'n ++ "-" ++ toString i', "C2 part rule names N-ai"),
    ("dual-of-obligation-none", "dualOf", "    | .obligation, some m => some m", "    | .obligation, some m => none",
     "C1 an obligation's rules and its dual's read alike (E7)"),
    ("dual-of-permission-none", "dualOf",
     "    | .permission, _ => (T.regulated.find? (fun o => o.role == .obligation && o.permission == some p)).map (·.name)",
     "    | .permission, _ => none", "C1 a permission's rules and its obligation's read alike (E7)"),
    ("rule-reading-sign-ignored", "ruleReading", "(opOf · N.sign)", "(opOf · true)", "C1 D-21: plain, sign false (E10)"),
    ("rule-reading-first-listed-only", "ruleReading", 's!"rule {N.name}" Rs >>=', 's!"rule {N.name}" (Rs.take 1) >>=',
     "C1 D-23 lists every reading (E9)"),
    ("rule-reading-d23-prefix", "ruleReading", "has more than one reading: ", "has two readings: ",
     "C1 D-23's text exactly (E9)"),
    ("reading-of-unequal-accepted", "readingOf", "if rest.all (· == R) then .ok R", "if true then .ok R",
     "C1 D-24 (E7)"),
    ("reading-of-dual-ignored", "readingOf", "N.pred == p || some N.pred == d", "N.pred == p",
     "C1 the dual's rules read the act too (E7)"),
    ("reading-of-no-rule-accepted", "readingOf", '    | [] => .error s!"InvalidInput: the joined act of {p} has no rule to read it by"',
     "    | [] => .ok []", "C1 D-20"),
    ("split-atoms-one", "splitAtoms", "if 2 ≤ atoms.length", "if 1 ≤ atoms.length",
     "C2 a reading of one atom does not split"),
    ("parts-from-zero", "partsOf", ".zipIdx 1", ".zipIdx 0", "C2 parts indexed from 1 (E1)"),
    ("split-map-index-one", "splitMap", "(partPred r.name x.2, r.name, x.2)", "(partPred r.name x.2, r.name, 1)",
     "C2 the map's index (E1)"),
    ("part-names-kept-dropped", "partNames", "  | [] => [p]", "  | [] => []",
     "C3 an unspecified predicate that does not split stays (E5)"),
    ("split-reg-act-kept", "splitReg", "act := some (partAct D.fixed r.role x.1)", "act := r.act",
     "C2 each part's act is its atom's (E1)"),
    ("split-reg-dual-unmapped", "splitReg", "permission := r.permission.map (partPred · x.2)",
     "permission := r.permission", "C2 a part's dual is the dual's part (E7)"),
    ("split-reg-kept-dropped", "splitReg", "  | [] => [r]\n", "  | [] => []\n", "C2 a predicate that does not split is kept (E2)"),
    ("split-node-kept-dropped", "splitNode", "  | [] => [N]\n", "  | [] => []\n", "C2 a rule that does not split is kept (E2)"),
    ("split-node-over-unmapped", "splitNode", "over := N.over.map (partRule · x.2)", "over := N.over",
     "C2 precedence splits pairwise (E4)"),
    ("split-env-part-undeclared", "splitEnv", "      | some x => D.U.D.E.predicates x.2.1",
     "      | some _ => D.U.D.E.predicates q", "C2 parts declared with the source's sorts (E1)"),
    ("split-env-source-kept", "splitEnv", "if M.preds.any (·.2.1 == q) then none else", "",
     "C2 a split source is undeclared (E1)"),
    ("split-doc-unspec-unsplit", "splitDoc", "unspec := D.U.unspec.flatMap (partNames D)", "unspec := D.U.unspec",
     "C3 an unspecified predicate's parts are unspecified (E5)"),
    ("refs-carve-outs-unchecked", "refsOk", "(N.guard :: N.carveOuts).any split", "[N.guard].any split",
     "C4 D-25 for an exception (E6)"),
    ("refs-definitions-unchecked", "refsOk", "D.U.D.T.definitions.find? (fun d => split d.body)",
     "D.U.D.T.definitions.find? (fun _ => false)", "C4 D-25 for a definition (E6)"),
    ("names-unspec-unchecked", "namesOk", "D.U.unspec.contains q || ", "", "C4 D-26: a part name already unspecified"),
    ("names-regulated-unchecked", "namesOk", "|| D.U.D.T.regulated.any (·.name == q) ||", "||",
     "C4 D-26: a part name already regulated"),
    ("names-bytes-65", "namesOk", "q.utf8ByteSize > VE.Limits.maxIdentifierBytes",
     "q.utf8ByteSize > VE.Limits.maxIdentifierBytes + 1", "C4 D-26: E8's boundary"),
    ("names-rule-used-unchecked", "namesOk", "D.U.D.T.nodes.any (·.name == n) || ", "",
     "C4 D-26: a part rule name already used"),
    ("names-part-count-unchecked", "namesOk", "|| qs.count q > 1", "", "C4 D-26: two parts of one name"),
    ("parts-distinct-unchecked", "partsDistinct", "!decide ((partsOf D r.name).map (partAct D.fixed r.role ·.1)).Nodup",
     "false", "C4 D-27 (E16)"),
    ("elaborate-map-refs-skipped", "elaborateMap", "  refsOk D\n", "", "C4 step 2 runs (E6's text)"),
    ("elaborate-map-validate-skipped", "elaborateMap", "  VE.Norms.validate U'.D\n", "",
     "C4 step 5 runs with its own texts (E12)"),
    ("elaborate-map-backstop-rules", "elaborateMap", " && M.rules.all (fun x => !U'.D.T.nodes.any (·.name == x.2.1))", "",
     "C4 the backstop: a split rule keeps no name"),
    ("elaborate-map-steps-swapped", "elaborateMap", "  refsOk D\n  namesOk D\n", "  namesOk D\n  refsOk D\n",
     "C4 the checks' order: step 2 before step 3"),
    ("elaborate-map-steps-34-swapped", "elaborateMap", "  namesOk D\n  partsDistinct D\n",
     "  partsDistinct D\n  namesOk D\n", "C4 the checks' order: step 3 before step 4"),
    ("elaborate-map-steps-12-swapped", "elaborateMap", "  let _ ← D.acts.mapM fun x => readingOf D x.1 x.2\n  refsOk D\n",
     "  refsOk D\n  let _ ← D.acts.mapM fun x => readingOf D x.1 x.2\n", "C4 the checks' order: step 1 before step 2"),
    ("elaborate-source", "elaborate", "(elaborateMap D).map (·.1)", "(elaborateMap D).map (fun _ => D.U)",
     "C2 elaborate is the map's document (E1)"),
]


def cut_theorems(text):
    start = text.index("/-! ### Theorems (6.6) -/")
    return text[:start] + "end VE.Acts\n"


def verdict(proc):
    out = proc.stdout + proc.stderr
    if proc.returncode == 0:
        return "SURVIVOR", ""
    errors = [line for line in out.splitlines() if "error:" in line]
    if any("VE/Acts/Elaborate.lean" in line for line in errors):
        return "INVALID", errors[0][:300]
    failing = [line for line in errors if "ElaborateExamples.lean" in line]
    return ("KILLED", failing[0][:300]) if failing else ("INVALID", (errors or [out[-300:]])[0][:300])


def main():
    missing = [d for d in DEFS if not any(b[1] == d for b in BUGS)]
    if missing:
        sys.exit(f"no bug for {missing}")
    src = ROOT / SRC
    original = src.read_text()
    base = cut_theorems(original)
    rows = []
    try:
        for bug_id, defn, old, new, claim in BUGS:
            if base.count(old) != 1:
                sys.exit(f"{bug_id}: the text to replace occurs {base.count(old)} times")
            src.write_text(base.replace(old, new))
            proc = subprocess.run(["lake", "build", "VE.Acts.ElaborateExamples"], cwd=ROOT / "lean",
                                  capture_output=True, text=True, check=False)
            result, detail = verdict(proc)
            rows.append({"id": bug_id, "file": SRC, "definition": defn, "claim": claim, "test": TEST,
                         "result": result, "detail": detail})
            print(f"{result:9} {bug_id}")
    finally:
        src.write_text(original)
    restored = subprocess.run(["lake", "build", "VE.Acts.ElaborateExamples"], cwd=ROOT / "lean",
                              capture_output=True, text=True, check=False)
    OUT.write_text(json.dumps({"restored_build": restored.returncode, "bugs": rows}, indent=2) + "\n")
    bad = [r["id"] for r in rows if r["result"] != "KILLED"]
    if bad or restored.returncode:
        sys.exit(f"not killed: {bad}; restored build exit {restored.returncode}")


if __name__ == "__main__":
    main()
