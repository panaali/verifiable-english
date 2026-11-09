#!/usr/bin/env python3
"""ap-5 seeded bugs and mutants: plant each in lean/VE/Acts/Specialise.lean with its theorems cut (so a fixture must
catch it, not a proof), build VE.Acts.SpecialiseExamples, record the failing `#guard` lines (KILLED), restore the file
from git, and write mutants.json beside this script. Run from the repository root with Specialise.lean committed:
`python3 docs/act-phrases/ap-5/seed_bugs.py [id ...]`."""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN, SRC, TEST = ROOT / "lean", "lean/VE/Acts/Specialise.lean", "lean/VE/Acts/SpecialiseExamples.lean"
CUT = "/-! ### The statements of spec 8 -/"
# (id, definition, behaviour, before, after); the first four are the task's seeded bugs
BUGS = [
    ("no-restrictive-mods", "specialises", "seeded bug: an extra modifier must be restrictive",
     "(a.mods.filter (fun x => !b.mods.contains x)).all (Modifier.restrictive ρ)", "true"),
    ("no-head", "specialises", "seeded bug: the same head", "a.head == b.head &&", "true &&"),
    ("premise-reversed", "specPremises", "seeded bug: the premise runs from the specific act to the general one",
     ".implies (VE.Norms.atom x.1.name x.1.sorts) (VE.Norms.atom y.1.name x.1.sorts)",
     ".implies (VE.Norms.atom y.1.name x.1.sorts) (VE.Norms.atom x.1.name x.1.sorts)"),
    ("plain-premise", "specPremises", "seeded bug: plain entitlements get no premise", "x.1.role != .plain && ", ""),
    ("fields-swapped", "Restrictive", "markers first, then adverbs", "  markers : List String\n  adverbs : List String",
     "  adverbs : List String\n  markers : List String"),
    ("adv-always", "Modifier.restrictive", "an adverb is restrictive when declared", "| .adv w => ρ.adverbs.contains w",
     "| .adv _ => true"),
    ("prep-as-adverb", "Modifier.restrictive", "a modifier marker is declared among the markers",
     "| .prep m _ => ρ.markers.contains m", "| .prep m _ => ρ.adverbs.contains m"),
    ("markers-first-only", "Modifier.restrictive", "every declared marker counts", "| .prep m _ => ρ.markers.contains m",
     "| .prep m _ => (ρ.markers.take 1).contains m"),
    ("adverbs-last-only", "Modifier.restrictive", "every declared adverb counts", "| .adv w => ρ.adverbs.contains w",
     "| .adv w => (ρ.adverbs.reverse.take 1).contains w"),
    ("no-to", "specialises", "the same *to*", "a.toWord == b.toWord && ", ""),
    ("no-be", "specialises", "the same *be*", "a.beWord == b.beWord && ", ""),
    ("not-reflexive", "specialises", "an act specialises itself", "a.toWord == b.toWord && ", "a != b && a.toWord == b.toWord && "),
    ("no-args-subset", "specialises", "every argument of `b` is one of `a`", "b.args.all (a.args.contains ·) && ", ""),
    ("b-args-last-only", "specialises", "every argument of `b`, not only its last", "b.args.all (a.args.contains ·)",
     "(b.args.reverse.take 1).all (a.args.contains ·)"),
    ("no-mods-subset", "specialises", "every modifier of `b` is one of `a`", "b.mods.all (a.mods.contains ·) &&", "true &&"),
    ("b-mods-first-only", "specialises", "every modifier of `b`, not only its first", "b.mods.all (a.mods.contains ·)",
     "(b.mods.take 1).all (a.mods.contains ·)"),
    ("b-mods-drop-last", "specialises", "every modifier of `b`, its last too", "b.mods.all (a.mods.contains ·)",
     "b.mods.dropLast.all (a.mods.contains ·)"),
    ("a-mods-first-only", "specialises", "a modifier of `b` is any modifier of `a`", "(a.mods.contains ·)",
     "((a.mods.take 1).contains ·)"),
    ("no-restrictive-args", "specialises", "an extra argument's marker must be restrictive",
     "(a.args.filter (fun x => !b.args.contains x)).all (fun x => ρ.markers.contains x.1) &&", "true &&"),
    ("extra-args-first-only", "specialises", "every extra argument must be restrictive",
     "(a.args.filter (fun x => !b.args.contains x)).all", "((a.args.filter (fun x => !b.args.contains x)).take 1).all"),
    ("arg-markers-first-only", "specialises", "every declared marker counts for an argument",
     "(fun x => ρ.markers.contains x.1)", "(fun x => (ρ.markers.take 1).contains x.1)"),
    ("extra-mods-first-only", "specialises", "every extra modifier must be restrictive",
     "(a.mods.filter (fun x => !b.mods.contains x)).all", "((a.mods.filter (fun x => !b.mods.contains x)).take 1).all"),
    ("extra-mods-drop-last", "specialises", "every extra modifier, the last too",
     "(a.mods.filter (fun x => !b.mods.contains x)).all", "(a.mods.filter (fun x => !b.mods.contains x)).dropLast.all"),
    ("extra-mods-b-first-only", "specialises", "a modifier is extra unless `b` has it anywhere", "!b.mods.contains x",
     "!(b.mods.take 1).contains x"),
    ("first-of-many", "declaredOnce", "a name declared twice is not read", "  | [r] => some r", "  | r :: _ => some r"),
    ("last-of-many", "declaredOnce", "a name declared twice is not read",
     "match E.T.regulated.filter (·.name == n) with\n  | [r] => some r\n  | _ => none",
     "(E.T.regulated.filter (·.name == n)).getLast?"),
    ("two-roles", "specPremises", "both predicates have one role", "x.1.role == y.1.role && ", ""),
    ("unequal-sorts", "specPremises", "both predicates have equal sorts", "x.1.sorts == y.1.sorts && ", ""),
    ("sorts-length", "specPremises", "equal sorts, not only as many", "x.1.sorts == y.1.sorts",
     "x.1.sorts.length == y.1.sorts.length"),
    ("a-eq-b", "specPremises", "no premise from an act to itself", "x.2 != y.2 &&", "true &&"),
    ("no-specialises", "specPremises", "a premise only when `a ⊑ b`", "\n        specialises ρ x.2 y.2 then", " true then"),
    ("premises-first-only", "specPremises", "every premise, not only the first (trust_mutants M059)",
     "  ds.flatMap fun x => ds.filterMap fun y =>", "  List.take 1 <| ds.flatMap fun x => ds.filterMap fun y =>"),
    ("premises-last-only", "specPremises", "every premise, not only the last (trust_mutants M108)",
     "  ds.flatMap fun x => ds.filterMap fun y =>",
     "  List.reverse <| List.take 1 <| List.reverse <| ds.flatMap fun x => ds.filterMap fun y =>"),
    ("extra-args-drop-first", "specialises", "`a`'s first argument may be extra (trust_mutants M132)",
     "(a.args.filter (fun x => !b.args.contains x))", "((a.args.drop 1).filter (fun x => !b.args.contains x))"),
    ("binders-reversed", "specPremises", "the binders in declared order", "VE.Norms.bindAll x.1.sorts (",
     "VE.Norms.bindAll x.1.sorts.reverse ("),
]


def lake(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PATH=os.path.expanduser("~/.elan/bin") + os.pathsep + os.environ["PATH"])
    return subprocess.run(["lake", *args], cwd=LEAN, env=env, capture_output=True, text=True)


def main() -> int:
    only = sys.argv[1:]  # ids to rerun; their rows replace the old ones in mutants.json
    out_json = Path(__file__).parent / "mutants.json"
    rows = [r for r in json.loads(out_json.read_text())["mutants"] if r["id"] not in only] if only else []
    original = (ROOT / SRC).read_text()
    try:  # control: the cut text with no plant must build and pass every guard, else every plant would look KILLED
        (ROOT / SRC).write_text(original[:original.index(CUT)] + "end VE.Acts\n")
        control = lake("build", "VE.Acts.SpecialiseExamples")
    finally:
        (ROOT / SRC).write_text(original)
        subprocess.run(["git", "checkout", "--", SRC], cwd=ROOT, check=True)
    if control.returncode:
        print("CONTROL FAILED", (control.stdout + control.stderr)[-2000:])
        return 1
    for bug, definition, behaviour, before, after in BUGS:
        if only and bug not in only:
            continue
        original = (ROOT / SRC).read_text()
        text0 = original[:original.index(CUT)] + "end VE.Acts\n"
        try:
            assert text0.count(before) == 1, bug
            (ROOT / SRC).write_text(text0.replace(before, after))
            out = lake("build", "VE.Acts.SpecialiseExamples")
        finally:
            (ROOT / SRC).write_text(original)
            subprocess.run(["git", "checkout", "--", SRC], cwd=ROOT, check=True)
        blocks = re.split(r"(?m)^(?=error: )", out.stdout + out.stderr)
        guards = sorted({int(m.group(1)) for b in blocks if "did not evaluate to `true`" in b
                         for m in [re.match(r"error: (?:\./)*\S*SpecialiseExamples\.lean:(\d+)", b)] if m})
        refused = [m.group(1) for b in blocks for m in [re.match(r"error: (?:\./)*\S*Specialise\.lean:(\d+)", b)] if m]
        status = "REFUSED" if refused else "KILLED" if guards and out.returncode else "SURVIVED"
        rows.append({"id": bug, "language": "Lean", "file": SRC, "definition": "VE.Acts." + definition,
                     "behaviour": behaviour, "status": status,
                     "test": f"{TEST}:{','.join(map(str, guards))}" if guards else f"{SRC}:{refused[0]}" if refused else ""})
        print(status, bug, rows[-1]["test"], flush=True)
    restored = lake("build", "VE.Acts.SpecialiseExamples")
    order = [b[0] for b in BUGS]
    rows.sort(key=lambda r: order.index(r["id"]))
    body = ",\n".join("  " + json.dumps(r, ensure_ascii=False) for r in rows)
    out_json.write_text(f'{{"control_build_returncode": {control.returncode}, '
                        f'"restored_build_returncode": {restored.returncode}, "mutants": [\n{body}\n]}}\n')
    return 0 if restored.returncode == 0 and all(r["status"] == "KILLED" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
