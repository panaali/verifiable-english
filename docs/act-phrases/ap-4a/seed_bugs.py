#!/usr/bin/env python3
"""ap-4a's seeded bugs: plant each bug in the Lean file this item changed, build VE.Acts.ReadingsExamples, record the
failing `#guard` or theorem lines (KILLED), restore the file, and write mutants.json beside this script. A plant that
changes the rule table fails the guards of the modules ReadingsExamples imports first, which stops the build there;
an `isolate` plant also turns those modules' `#guard`s into `#eval`s for its build, so the new A5 to A12 guards show
the bug on their own. Run from the repository root: `python3 docs/act-phrases/ap-4a/seed_bugs.py [ids...]`."""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN = ROOT / "lean"
G, M, R = "lean/VE/Acts/Grammar.lean", "lean/VE/Acts/Meaning.lean", "lean/VE/Acts/Readings.lean"
UPSTREAM = ["lean/VE/Acts/RuleExamples.lean", "lean/VE/Acts/MeaningExamples.lean"]
# (file, id, definition, behaviour, before, after, isolate)
BUGS = [
    (G, "e1x-all-dropped", "globalRules", "the pre-modifier's `all` reading is dropped (the plan's seeded bug)",
     "[⟨.E1X, [adv], .edge .first⟩, ⟨.E1X, [adv], .edge .all⟩]", "[⟨.E1X, [adv], .edge .first⟩]", False),
    (G, "e1x-all-dropped-isolated", "globalRules", "as e1x-all-dropped, upstream guards off: A8 fails on its own",
     "[⟨.E1X, [adv], .edge .first⟩, ⟨.E1X, [adv], .edge .all⟩]", "[⟨.E1X, [adv], .edge .first⟩]", True),
    (G, "e1x-all-as-first", "globalRules", "the pre-modifier's second rule reads over the first item too",
     "⟨.E1X, [adv], .edge .all⟩]", "⟨.E1X, [adv], .edge .first⟩]", False),
    (G, "trailing-all-as-last", "frameRules", "a trailing edge's second rule reads over the last item too",
     "⟨.F h y, rhs, .edge .all⟩]", "⟨.F h y, rhs, .edge .last⟩]", False),
    (G, "trailing-all-dropped", "frameRules", "a trailing edge's `all` rule is dropped",
     "[⟨.F h y, rhs, .edge .last⟩, ⟨.F h y, rhs, .edge .all⟩]", "[⟨.F h y, rhs, .edge .last⟩]", False),
    (G, "middle-edge", "globalRules", "a later item's adverb attaches over all (AP-2's middle-item bug)",
     "⟨.L false c, [.n .ADVSO, .n (.C c)], .shape⟩", "⟨.L false c, [.n .ADVSO, .n (.C c)], .edge .all⟩", False),
    (G, "attachOf-shape-all", "attachOf", "a rule of no edge kind attaches over all",
     "  | .shape => none\n", "  | .shape => some .all\n", False),
    (G, "edgeLhs-first-anywhere", "edgeLhs", "`first` is allowed at any left side",
     "  | .first => (x matches .E1X)\n", "  | .first => true\n", False),
    (G, "edgeLhs-all-trailing-only", "edgeLhs", "`all` only at trailing edges (the spec docstring's reading)",
     "  | .all => x matches .E1X | .F _ .TE", "  | .all => x matches .F _ .TE", False),
    (M, "applyRule-own", "applyRule", "the meaning ignores the kind: every element reads over its own item",
     "let att := if attachOf r.kind == some .all then Att.all else .own", "let att := Att.own", False),
    (R, "phrase-limit-65", "phraseReadings", "65 lists are listed",
     "if maxReadings < Rs.length then .limit else .ok Rs", "if maxReadings + 1 < Rs.length then .limit else .ok Rs",
     False),
    (R, "phrase-limit-64", "phraseReadings", "64 lists are refused",
     "if maxReadings < Rs.length then .limit else .ok Rs", "if maxReadings ≤ Rs.length then .limit else .ok Rs", False),
    (R, "phrase-no-dedup", "phraseReadings", "equal lists are listed twice",
     "let Rs := firsts (As.flatMap (table op))", "let Rs := As.flatMap (table op)", False),
    (R, "phrase-limit-passed", "phraseReadings", "the readings' limit outcome is listed as no reading",
     "  | .limit => .limit\n  | .ok As =>", "  | .limit => .ok []\n  | .ok As =>", False),
    (R, "phrase-table-ignored", "phraseReadings", "the modal is ignored: every meaning reads as its atoms",
     "let Rs := firsts (As.flatMap (table op))",
     "let Rs := firsts (As.map (fun | .one a => [Simple.atom a] | .all _ _ ps | .any _ _ ps => ps.map .atom))", False),
]


def build() -> tuple[int, list[str]]:
    p = subprocess.run(["lake", "build", "VE.Acts.ReadingsExamples"], cwd=LEAN, capture_output=True, text=True)
    lines = re.findall(r"^error: (VE/[^:]+\.lean:\d+):", p.stdout + p.stderr, re.M)
    return p.returncode, sorted(set("lean/" + x for x in lines), key=lambda s: (s.split(":")[0], int(s.split(":")[1])))


def main() -> None:
    only = set(sys.argv[1:])
    out = ROOT / "docs/act-phrases/ap-4a/mutants.json"
    rows = json.loads(out.read_text())["mutants"] if out.exists() and only else []
    rows = [r for r in rows if r["id"] not in only]
    for f, mid, defn, beh, before, after, isolate in BUGS:
        if only and mid not in only:
            continue
        path = ROOT / f
        text = path.read_text()
        assert text.count(before) == 1, (mid, text.count(before))
        saved = {u: (ROOT / u).read_text() for u in UPSTREAM} if isolate else {}
        try:
            path.write_text(text.replace(before, after))
            for u, t in saved.items():
                (ROOT / u).write_text(t.replace("#guard", "#eval"))
            rc, failing = build()
        finally:
            path.write_text(text)
            for u, t in saved.items():
                (ROOT / u).write_text(t)
        rows.append({"id": mid, "language": "Lean", "file": f, "definition": f"VE.Acts.{defn}", "behaviour": beh,
                     "status": "KILLED" if rc != 0 and failing else "SURVIVED", "test": ", ".join(failing)})
        print(mid, rows[-1]["status"], rows[-1]["test"], flush=True)
    rc, failing = build()
    out.write_text(json.dumps({"restored_build_returncode": rc, "mutants": rows}, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
