#!/usr/bin/env python3
"""ap-2c seeded bugs: plant each in its file (Readings.lean with its theorems cut, so a fixture must catch it, not a
proof), build VE.Acts.MeaningExamples, record the failing `#guard` lines of MeaningExamples.lean (KILLED), Lean's
refusal of the planted file (REFUSED: a data type's constructor dropped, or a statement's proof), restore the file
from git, and write mutants.json beside this script. Run from the repository root:
`python3 docs/act-phrases/ap-2c/seed_bugs.py`."""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN, TEST = ROOT / "lean", "lean/VE/Acts/MeaningExamples.lean"
M, R, G = "lean/VE/Acts/Meaning.lean", "lean/VE/Acts/Readings.lean", "lean/VE/Acts/Grammar.lean"
CUT = {R: "/-- One meaning (design debate)"}
# a plant in the rule table fails RuleExamples' raw guards first (ap-2b's evidence), which would stop the build before
# MeaningExamples: for it, those guards are evaluated without failing, so the meaning's guards are the evidence
QUIET = {G: "lean/VE/Acts/RuleExamples.lean"}
# (file, id, definition, behaviour, before, after)
BUGS = [
    (G, "premodifier-middle-item", "globalRules", "the plan's seeded bug: a third premodifier rule; A8 has 3 meanings",
     "⟨.E1X, [adv]⟩, ⟨.E1X, [adv]⟩]", "⟨.E1X, [adv]⟩, ⟨.E1X, [adv]⟩, ⟨.E1X, [adv]⟩]"),
    (M, "Att-drop-all", "Att", "data type: a constructor dropped", "inductive Att | own | all", "inductive Att | own"),
    (M, "Elt-drop-mod", "Elt", "data type: a constructor dropped", " | mod (md : Modifier)\n", "\n"),
    (M, "Piece-drop-list", "Piece", "data type: a constructor dropped", "  | list (j : Join) (ps : List Part) |", "  |"),
    (M, "add-arg-first", "Atom.add", "an element goes after the atom's others", "a.args ++ [(m, fl)]", "[(m, fl)] ++ a.args"),
    (M, "add-mod-dropped", "Atom.add", "a modifier is added", "a.mods ++ [md]", "a.mods"),
    (M, "all-as-own", "addPiece", "an element read over all goes to every atom", "a == .all || i == k", "i == k"),
    (M, "split-first-member", "addPiece", "a split construct makes one atom per member", "es.map x.add", "es.take 1 |>.map x.add"),
    (M, "nor-as-or", "joinAct", "*nor* is `any true`", "  | .nor => .any true sp", "  | .nor => .any false sp"),
    (M, "and-unshared", "joinAct", "*and* keeps `shared`", "  | .and => .all shared sp", "  | .and => .all false sp"),
    (M, "be-as-to", "baseAtom", "*be* is read", "(fw.map (·.2)).getD false", "(fw.map (·.1)).getD false"),
    (M, "single-unshared", "singleAct", "a split construct's *and* is `all true`", "joinAct true sp j as", "joinAct false sp j as"),
    (M, "single-to-first", "singleAct", "after a split, an edge's near end is the last part",
     "addPiece (as.length - 1) as p", "addPiece 0 as p"),
    (M, "coord-own-fw", "coordAct", "later items take the first's shared function words",
     "if shared then fw0 else fw", "fw"),
    (M, "coord-first-item", "coordAct", "each element goes to its own item", "es.foldl (addPiece i) as", "es.foldl (addPiece 0) as"),
    (M, "list-keeps-join", "listOf", "a list's members are the pieces but its join word", "cs.filter (!· matches .j _)", "cs"),
    (M, "item-no-fw", "itemOf", "an item's function words", "cs.findSome? (fun | .fw t b => some (t, b) | _ => none)", "none"),
    (M, "d9-no-last", "applyRule", "D9 (i): a long last part is refused", "(long ps.head? || long ps.getLast?)", "long ps.head?"),
    (M, "d9-no-first", "applyRule", "D9 (i): a long first part is refused", "(long ps.head? || long ps.getLast?)", "long ps.getLast?"),
    (M, "d9-also-repeated", "applyRule", "D9 (i) is for a marker written once (`PL`), not `RL`",
     "if r.lhs matches .F _ .PL && ", "if "),
    (M, "edge-second-near", "applyRule", "an edge's second rule reads over all", "if second then Att.all else .own", ".own"),
    (M, "rnr-args-own", "applyRule", "a shared-object list's last arguments go to every item",
     "| .F _ .PX, _, _ | .C .rnr, _, _ =>", "| .F _ .PX, _, _ =>"),
    (M, "split-not-split", "applyRule", "a split marker's list is a split construct",
     "| .F _ (.LST m true), _, [.list j ps] => some [.split j true", "| .F _ (.LST m true), _, [.list j ps] => some [.split j false"),
    (M, "fixed-as-slot", "piecesOf", "a fixed phrase is a fixed part", "some [.part (.fixed i)]", "some [.part (.slot i)]"),
    (M, "second-never", "piecesOf", "the second of two alike rules is told apart", "rs.extract (i - 1) i == #[r]", "false"),
    (M, "kids-reversed", "piecesOf", "children in order", "kids.attach.mapM", "kids.attach.reverse.mapM"),
    (M, "no-object-check", "atomOk", "an object exactly when the frame lists \"\"",
     "(a.args.filter (·.1 == \"\")).length == (if f.markers.contains \"\" then 1 else 0) &&", "true &&"),
    (M, "no-marker-check", "atomOk", "every argument marker is the frame's", "a.args.all (f.markers.contains ·.1) &&", "true &&"),
    (M, "no-mod-check", "atomOk", "every modifier marker is the frame's", ".prep m _ => f.mods.contains m", ".prep _ _ => true"),
    (M, "no-adverb-check", "atomOk", "every adverb is declared", ".adv w => V.adverbs.contains w", ".adv _ => true"),
    (M, "join-of-one", "actOk", "a join has at least two atoms", "2 ≤ ps.length", "1 ≤ ps.length"),
    (M, "meaning-no-actOk", "meaning", "the meaning is refused unless every atom fits", "if actOk V A then", "if true then"),
    (R, "readings-budget-0", "readings", "the step budget is passed on", "readingsIn (grammar V) (meaning V) N b ts",
     "readingsIn (grammar V) (meaning V) N 0 ts"),
    (R, "read-budget-0", "read", "the step budget is passed on", "readIn (grammar V) (meaning V) N b ts",
     "readIn (grammar V) (meaning V) N 0 ts"),
    (R, "analyse-never", "analyse", "one `one` meaning is its atom", "| .ok (.one a) => some a | _ => none", "| _ => none"),
    (R, "Derived-true", "Derived", "a meaning is derived (tied to derived_iff, spec 5.6's text: its theorems refuse the plant)",
     ":= DerivedIn (grammar V) (meaning V) ts A", ":= True"),
]


def lake(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PATH=os.path.expanduser("~/.elan/bin") + os.pathsep + os.environ["PATH"])
    return subprocess.run(["lake", *args], cwd=LEAN, env=env, capture_output=True, text=True)


def main() -> int:
    only = sys.argv[1:]  # ids to rerun; their rows replace the old ones in mutants.json
    out_json = Path(__file__).parent / "mutants.json"
    rows = [r for r in json.loads(out_json.read_text())["mutants"] if r["id"] not in only] if only else []
    for src, bug, definition, behaviour, before, after in BUGS:
        if only and bug not in only:
            continue
        original = (ROOT / src).read_text()
        quiet = QUIET.get(src)
        # the statement-only plant keeps the theorems, so their refusal is the evidence
        text0 = original if src not in CUT or bug == "Derived-true" else \
            original[:original.index(CUT[src])] + "end VE.Acts\n"
        try:
            assert text0.count(before) == 1, bug
            (ROOT / src).write_text(text0.replace(before, after))
            if quiet:
                (ROOT / quiet).write_text((ROOT / quiet).read_text().replace("#guard ", "#eval "))
            out = lake("build", "VE.Acts.MeaningExamples")
        finally:
            (ROOT / src).write_text(original)
            subprocess.run(["git", "checkout", "--", src] + ([quiet] if quiet else []), cwd=ROOT, check=True)
        text = out.stdout + out.stderr
        blocks = re.split(r"(?m)^(?=error: )", text)
        guards = sorted({int(m.group(1)) for b in blocks if "did not evaluate to `true`" in b
                         for m in [re.match(r"error: (?:\./)*\S*MeaningExamples\.lean:(\d+)", b)] if m})
        name = Path(src).name
        refused = [m.group(1) for b in blocks for m in [re.match(rf"error: (?:\./)*\S*{name}:(\d+)", b)] if m]
        status = "REFUSED" if refused else "KILLED" if guards and out.returncode else "SURVIVED"
        rows.append({"id": bug, "language": "Lean", "file": src, "definition": "VE.Acts." + definition,
                     "behaviour": behaviour, "status": status,
                     "test": f"{TEST}:{','.join(map(str, guards))}" if guards else f"{src}:{refused[0]}" if refused else ""})
        print(status, bug, rows[-1]["test"], flush=True)
    restored = lake("build", "VE.Acts.MeaningExamples")
    order = [b[1] for b in BUGS]
    rows.sort(key=lambda r: order.index(r["id"]))
    out_json.write_text(json.dumps(
        {"restored_build_returncode": restored.returncode, "mutants": rows}, indent=1, ensure_ascii=False) + "\n")
    return 0 if restored.returncode == 0 and all(r["status"] != "SURVIVED" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
