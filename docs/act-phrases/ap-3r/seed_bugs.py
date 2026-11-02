#!/usr/bin/env python3
"""ap-3r's seeded bugs: plant each bug, build the three fixture modules, record the failing theorem or `#guard` lines
(KILLED), restore the file, and write mutants.json beside this script. One plant per claimed behaviour and at least one
per new or changed trusted definition (`tools/trust_map.py`: `freeTable` in Table.lean, the new fixture definitions).
A plant in the table breaks the table's own equations first, which stops the build in Table.lean; each plant is
therefore built three ways (a plant in Grammar.lean or Elaborate.lean the first and last, a fixture plant the first): as planted; with the table's proofs replaced by `sorry`, so TableExamples' guards show it;
and with that plus the upstream fixture modules' `#guard`s turned into `#eval`s, so the guards of ElaborateExamples and
ReadingsExamples show it on their own. Run from the repository root:
`python3 docs/act-phrases/ap-3r/seed_bugs.py [ids...]`."""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN = ROOT / "lean"
TB, EL, GR = "lean/VE/Acts/Table.lean", "lean/VE/Acts/Elaborate.lean", "lean/VE/Acts/Grammar.lean"
TE, EE, RE = "lean/VE/Acts/TableExamples.lean", "lean/VE/Acts/ElaborateExamples.lean", "lean/VE/Acts/ReadingsExamples.lean"
UPSTREAM = [TE, "lean/VE/Acts/RuleExamples.lean", "lean/VE/Acts/MeaningExamples.lean"]
TARGETS = ["VE.Acts.TableExamples", "VE.Acts.ElaborateExamples", "VE.Acts.ReadingsExamples"]
# the proofs a plant breaks first, replaced by `sorry` after the planted build so the guards show the plant
SORRY = {TB: ("  rcases hop with h | h <;> subst h <;> rfl", "  sorry"),
         EL: ((ROOT / EL).read_text().split("table op A = [R] := by\n", 1)[1].split("\n\ntheorem", 1)[0], "  sorry")}
OWN_T = "  | .all false true ps => [ps.map Simple.atom]\n"
OWN_F = "  | .all false false ps => [ps.map Simple.atom, [.whole (.all false false ps)]]\n"
# (file, id, definition, behaviour, before, after)
BUGS = [
    (TB, "own-to-restored", "freeTable", "the own-*to* exception restored: one split reading for every `all false _`",
     OWN_T + OWN_F, "  | .all false _ ps => [ps.map Simple.atom]\n"),
    (TB, "together-dropped", "freeTable", "the together reading dropped from the revised cell",
     OWN_F, "  | .all false false ps => [ps.map Simple.atom]\n"),
    (TB, "together-wrong-whole", "freeTable", "the together reading is a whole of another join (shared *to*)",
     OWN_F, "  | .all false false ps => [ps.map Simple.atom, [.whole (.all true false ps)]]\n"),
    (TB, "split-marker-together", "freeTable", "a split marker's *and* under *may* gains a together reading",
     OWN_T, "  | .all false true ps => [ps.map Simple.atom, [.whole (.all false true ps)]]\n"),
    (TB, "right-only-dropped", "table", "under *has the right to* only, the cell loses its together reading",
     "  | .right, A => freeTable A", "  | .right, .all false false ps => [ps.map Simple.atom]\n  | .right, A => freeTable A"),
    (GR, "e1x-all-dropped", "globalRules", "the plan's AP-4 seeded bug, moved to rs_u055 (DRI 2026-11-01 ap-3r-spec "
     "item 2): the pre-modifier's `all` reading is dropped, so S4 must be refused",
     "[⟨.E1X, [adv], .edge .first⟩, ⟨.E1X, [adv], .edge .all⟩]", "[⟨.E1X, [adv], .edge .first⟩]"),
    (EL, "norms-split-again", "ruleReading", "the norms route splits the revised cell again (its split reading taken)",
     "    | [R] => .ok R\n", "    | [R] => .ok R\n    | [R, [.whole (.all false false _)]] => .ok R\n"),
    (RE, "eachOrTogether-order", "VE.Acts.ReadingsExamples.eachOrTogether", "the expected readings in another order",
     ":= [atoms A, [.whole A]]", ":= [[.whole A], atoms A]"),
    (RE, "together105-text", "VE.Acts.ReadingsExamples.together105", "S1/S8's pinned F11 text names another reading",
     "  \"(not each on its own).\"", "  \"(not each way on its own).\""),
    (RE, "e055x-denied-act", "VE.Acts.ReadingsExamples.e055x", "S3b's environment declares another denial",
     "  (\"denied\", \"permission\", \"deny\", \"{0} be denied the right to change their nationality\"),\n  (\"denied_arb",
     "  (\"denied\", \"permission\", \"deny\", \"{0} be denied the right to keep their nationality\"),\n  (\"denied_arb"),
    (RE, "u055x-no-extra", "VE.Acts.ReadingsExamples.u055x", "S3b's third candidate is not added",
     "     ⟨\"both_acts\", some (.norm (rl \"u055-b\" \"denied_arbitrarily\" false)), [], []⟩] ++ extra⟩]",
     "     ⟨\"both_acts\", some (.norm (rl \"u055-b\" \"denied_arbitrarily\" false)), [], []⟩]⟩]"),
    (RE, "other-listed", "VE.Acts.ReadingsExamples.other", "the unlisted set takes rs_u055's id",
     "def other : Item := .set ⟨\"rs_other\"", "def other : Item := .set ⟨\"rs_u055\""),
    (EE, "seekP-object", "VE.Acts.ElaborateExamples.seekP", "E17's first act loses its object's words",
     "[(\"\", .one (w \"asylum from persecution\"))], []⟩\ndef enjoyP", "[(\"\", .one (w \"asylum\"))], []⟩\ndef enjoyP"),
    (EE, "enjoyP-head", "VE.Acts.ElaborateExamples.enjoyP", "E17's second act has another head",
     "def enjoyP : Atom := ⟨true, false, [\"enjoy\"]", "def enjoyP : Atom := ⟨true, false, [\"keep\"]"),
    (EE, "e17-sign", "VE.Acts.ElaborateExamples.e17", "E17's rule is a plain predicate with sign false (no modal word)",
     "[nd \"r051\" \"p051\" true]", "[nd \"r051\" \"p051\" false]"),
    (EE, "sick-filler", "VE.Acts.ElaborateExamples.sick", "E16's atom has another cause",
     "(\"in the event of\", .one (w \"sickness\"))], []⟩\n", "(\"in the event of\", .one (w \"illness\"))], []⟩\n"),
]


def build() -> tuple[int, list[str]]:
    p = subprocess.run(["lake", "build", *TARGETS], cwd=LEAN, capture_output=True, text=True)
    lines = re.findall(r"^error: (VE/[^:]+\.lean:\d+):", p.stdout + p.stderr, re.M)
    return p.returncode, sorted(set("lean/" + x for x in lines), key=lambda s: (s.split(":")[0], int(s.split(":")[1])))


def main() -> None:
    only = set(sys.argv[1:])
    out = ROOT / "docs/act-phrases/ap-3r/mutants.json"
    rows = json.loads(out.read_text())["mutants"] if out.exists() and only else []
    rows = [r for r in rows if r["id"] not in only]
    for f, mid, defn, beh, before, after in BUGS:
        if only and mid not in only:
            continue
        files = sorted({f, TB, EL, *UPSTREAM})
        saved = {u: (ROOT / u).read_text() for u in files}
        assert saved[f].count(before) == 1, (mid, saved[f].count(before))
        failing: list[str] = []
        rcs = []
        try:
            stages = {TB: ("planted", "sorry", "isolated"), GR: ("planted", "isolated"), EL: ("planted", "isolated")}
            for stage in stages.get(f, ("planted",)):
                for u, t in saved.items():
                    t = t.replace(before, after) if u == f else t
                    if stage != "planted" and u in SORRY:
                        t = t.replace(*SORRY[u])
                    if stage == "isolated" and u in UPSTREAM:
                        t = t.replace("#guard", "#eval")
                    (ROOT / u).write_text(t)
                rc, fl = build()
                rcs.append(rc)
                failing += [x for x in fl if x not in failing]
        finally:
            for u, t in saved.items():
                (ROOT / u).write_text(t)
        name = defn if "." in defn else f"VE.Acts.{defn}"
        rows.append({"id": mid, "language": "Lean", "file": f, "definition": name, "behaviour": beh,
                     "status": "KILLED" if rcs[0] != 0 and failing else "SURVIVED", "test": ", ".join(failing)})
        print(mid, rows[-1]["status"], rows[-1]["test"], flush=True)
    order = [b[1] for b in BUGS]
    rows.sort(key=lambda r: order.index(r["id"]) if r["id"] in order else len(order))
    rc, _ = build()
    out.write_text(json.dumps({"item": "ap-3r", "command": "python3 docs/act-phrases/ap-3r/seed_bugs.py",
                               "restored_build_returncode": rc, "mutants": rows}, indent=1, ensure_ascii=False) + "\n")
    sys.exit(0 if rc == 0 and all(r["status"] == "KILLED" for r in rows) else 1)


if __name__ == "__main__":
    main()
