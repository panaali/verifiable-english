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
     ".implies (VE.Norms.atom ra.name ra.sorts) (VE.Norms.atom rb.name ra.sorts)",
     ".implies (VE.Norms.atom rb.name ra.sorts) (VE.Norms.atom ra.name ra.sorts)"),
    ("plain-premise", "specPremises", "seeded bug: plain entitlements get no premise", "ra.role != .plain && ", ""),
    ("fields-swapped", "Restrictive", "markers first, then adverbs", "  markers : List String\n  adverbs : List String",
     "  adverbs : List String\n  markers : List String"),
    ("adv-always", "Modifier.restrictive", "an adverb is restrictive when declared", "| .adv w => ρ.adverbs.contains w",
     "| .adv _ => true"),
    ("prep-as-adverb", "Modifier.restrictive", "a modifier marker is declared among the markers",
     "| .prep m _ => ρ.markers.contains m", "| .prep m _ => ρ.adverbs.contains m"),
    ("no-to", "specialises", "the same *to*", "a.toWord == b.toWord && ", ""),
    ("no-be", "specialises", "the same *be*", "a.beWord == b.beWord && ", ""),
    ("no-args-subset", "specialises", "every argument of `b` is one of `a`", "b.args.all (a.args.contains ·) && ", ""),
    ("no-mods-subset", "specialises", "every modifier of `b` is one of `a`", "b.mods.all (a.mods.contains ·) &&", "true &&"),
    ("no-restrictive-args", "specialises", "an extra argument's marker must be restrictive",
     "(a.args.filter (fun x => !b.args.contains x)).all (fun x => ρ.markers.contains x.1) &&", "true &&"),
    ("first-of-many", "declaredOnce", "a name declared twice is not read", "  | [r] => some r", "  | r :: _ => some r"),
    ("two-roles", "specPremises", "both predicates have one role", "ra.role == rb.role && ", ""),
    ("unequal-sorts", "specPremises", "both predicates have equal sorts", "ra.sorts == rb.sorts && ", ""),
    ("a-eq-b", "specPremises", "no premise from an act to itself", "pa.2 != pb.2 &&", "true &&"),
    ("no-specialises", "specPremises", "a premise only when `a ⊑ b`", "\n          specialises ρ pa.2 pb.2 then", " true then"),
]


def lake(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PATH=os.path.expanduser("~/.elan/bin") + os.pathsep + os.environ["PATH"])
    return subprocess.run(["lake", *args], cwd=LEAN, env=env, capture_output=True, text=True)


def main() -> int:
    only = sys.argv[1:]  # ids to rerun; their rows replace the old ones in mutants.json
    out_json = Path(__file__).parent / "mutants.json"
    rows = [r for r in json.loads(out_json.read_text())["mutants"] if r["id"] not in only] if only else []
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
    out_json.write_text(json.dumps(
        {"restored_build_returncode": restored.returncode, "mutants": rows}, indent=1, ensure_ascii=False) + "\n")
    return 0 if restored.returncode == 0 and all(r["status"] == "KILLED" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
