#!/usr/bin/env python3
"""ap-2b seeded bugs: plant each in lean/VE/Acts/Grammar.lean with its proofs cut (so a fixture must catch it, not a
proof), build VE.Acts.RuleExamples, record the failing `#guard` lines of RuleExamples.lean (KILLED) or Lean's refusal
of Grammar.lean itself (REFUSED, for a data type's constructor dropped), restore the file from git, and write
mutants.json beside this script. Run from the repository root: `python3 docs/act-phrases/ap-2b/seed_bugs.py`."""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN, SRC = ROOT / "lean", "lean/VE/Acts/Grammar.lean"
TEST = "lean/VE/Acts/RuleExamples.lean"
PROOFS = "/-! ### `grammar_wf` (5.6) -/"
# (id, definition, behaviour, before, after)
BUGS = [
    ("premodifier-middle-item", "globalRules", "the plan's seeded bug: a third premodifier edge rule; A8 (G8) has 3",
     "⟨.E1X, [adv]⟩, ⟨.E1X, [adv]⟩]", "⟨.E1X, [adv]⟩, ⟨.E1X, [adv]⟩, ⟨.E1X, [adv]⟩]"),
    ("marker-without-words", "globalRules", "W2: `MK \"\"` with an empty right side, so the grammar is not well formed",
     "f.markers ++ f.mods)).filter (· ≠ \"\")))", "f.markers ++ f.mods)).filter (fun _ => true)))"),
    ("no-never-rules", "closed", "5.2's last paragraph: no `X → never` rule", "(fun x => !rs.any (·.lhs == x))", "(fun _ => false)"),
    ("adverb-as-filler", "fillExcl", "1.4: an adverb is not a filler word", "\"be\"] ++ V.adverbs ++", "\"be\"] ++"),
    # review ap-2b F1: the two middle words of the literal list, which no fixture refused
    ("to-as-filler", "fillExcl", "1.4: *to* is not a filler word (review ap-2b F1)", "\"nor\", \"to\", \"be\"]",
     "\"nor\", \"be\"]"),
    ("nor-as-filler", "fillExcl", "1.4: *nor* is not a filler word (review ap-2b F1)", "\"nor\", \"to\", \"be\"]",
     "\"to\", \"be\"]"),
    ("start-not-S", "build", "the start symbol is S", "start := names.idxOf .S", "start := names.idxOf .SINGLE"),
    ("rank-coord-0", "NT.rank", "W3: COORD ranks above its first items", "  | .COORD | .F _ .O", "  | .F _ .O"),
    ("grammar-unclosed", "grammar", "the grammar is the closed schema", "build (closed (schema V))", "build (schema V)"),
    ("nt-none", "RSym.nt?", "a nonterminal symbol names its nonterminal", "  | .n x => some x", "  | .n _ => none"),
    ("kw-as-fill", "kwSyms", "a head's or marker's word is a `kw` terminal", "(fun w => .t (.kw w))", "(fun w => .t (.fill [w]))"),
    ("many1-once", "many1", "one or more", "[⟨X, [x]⟩, ⟨X, [x, .n X]⟩]", "[⟨X, [x]⟩]"),
    ("tail-no-comma-join", "tail", "a comma before the join word", "lasts.map (fun x => ⟨X, [.t .comma, .n .J, x]⟩)", "[]"),
    ("items-shared-drop-last", "items", "an adverb on both sides of a shared function word",
     ", [.FW, a, c], [a, .FW, a, c]]", ", [.FW, a, c]]"),
    ("frame-object-list-split", "frameRules", "a joined object that is not split is `O → PL`",
     "if objSplit then r .OS [x .PL] else r .O [x .PL]", "r .OS [x .PL]"),
    ("schema-first-frame-only", "schema", "every frame's rules", "V.frames.zipIdx.flatMap", "(V.frames.take 1).zipIdx.flatMap"),
    ("Core-drop-rnr", "Core", "data type: a constructor dropped", "inductive Core | bare | own | last | rnr", "inductive Core | bare | own | last"),
    ("FNT-drop-REt", "FNT", "data type: a constructor dropped", "| RE | REt | REP", "| RE | REP"),
    ("NT-drop-E1S", "NT", "data type: a constructor dropped", "| E1X | E1S | SINGLE", "| E1X | SINGLE"),
    ("RSym-drop-t", "RSym", "data type: a constructor dropped", "inductive RSym | t (a : Term) | n (x : NT)", "inductive RSym | n (x : NT)"),
    ("RuleS-drop-rhs", "RuleS", "data type: a field dropped", "  lhs : NT\n  rhs : List RSym\n", "  lhs : NT\n"),
]


def lake(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PATH=os.path.expanduser("~/.elan/bin") + os.pathsep + os.environ["PATH"])
    return subprocess.run(["lake", *args], cwd=LEAN, env=env, capture_output=True, text=True)


def main() -> int:
    original = (ROOT / SRC).read_text()
    cut = original[:original.index(PROOFS)] + "end VE.Acts\n"
    rows = []
    try:
        for bug, definition, behaviour, before, after in BUGS:
            assert cut.count(before) == 1, bug
            (ROOT / SRC).write_text(cut.replace(before, after))
            out = lake("build", "VE.Acts.RuleExamples")
            text = out.stdout + out.stderr
            blocks = re.split(r"(?m)^(?=error: )", text)
            guards = sorted({int(m.group(1)) for b in blocks if "did not evaluate to `true`" in b
                             for m in [re.match(r"error: (?:\./)*\S*RuleExamples\.lean:(\d+)", b)] if m})
            refused = [m.group(1) for b in blocks for m in [re.match(r"error: (?:\./)*\S*Grammar\.lean:(\d+)", b)] if m]
            status = "REFUSED" if refused else "KILLED" if guards and out.returncode else "SURVIVED"
            rows.append({"id": bug, "language": "Lean", "file": SRC, "definition": "VE.Acts." + definition,
                         "behaviour": behaviour, "status": status,
                         "test": f"{TEST}:{','.join(map(str, guards))}" if guards else f"{SRC}:{refused[0]}" if refused else ""})
            print(status, bug, rows[-1]["test"], flush=True)
    finally:
        (ROOT / SRC).write_text(original)
        subprocess.run(["git", "checkout", "--", SRC], cwd=ROOT, check=True)
    restored = lake("build", "VE.Acts.RuleExamples")
    (Path(__file__).parent / "mutants.json").write_text(json.dumps(
        {"restored_build_returncode": restored.returncode, "mutants": rows}, indent=1, ensure_ascii=False) + "\n")
    return 0 if restored.returncode == 0 and all(r["status"] != "SURVIVED" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
