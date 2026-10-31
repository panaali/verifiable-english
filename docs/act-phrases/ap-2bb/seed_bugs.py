#!/usr/bin/env python3
"""ap-2bb's seeded bugs: plant each bug in the Lean file this item changed, build VE.Acts.RenderExamples, record the
failing `#guard` lines (KILLED; a plant that changes `Atom.normal` or the meaning fails the guards of the modules
RenderExamples imports first, which stops the build there), restore the file from git, and write mutants.json beside
this script. Run from the repository root: `python3 docs/act-phrases/ap-2bb/seed_bugs.py [ids...]`."""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN = ROOT / "lean"
L, M = "lean/VE/Acts/Linearize.lean", "lean/VE/Acts/Meaning.lean"
# (file, id, definition, behaviour, before, after)
BUGS = [
    (L, "canon-args-kept", "Atom.canon", "the object is not moved first",
     'args := a.args.filter (·.1 == "") ++ a.args.filter (·.1 != "")', "args := a.args"),
    (L, "canon-object-last", "Atom.canon", "the object after the other arguments",
     'args := a.args.filter (·.1 == "") ++ a.args.filter (·.1 != "")',
     'args := a.args.filter (·.1 != "") ++ a.args.filter (·.1 == "")'),
    (L, "canon-mods-kept", "Atom.canon", "the adverbs are not moved before the prepositional modifiers",
     "mods := a.mods.filter (· matches .adv _) ++ a.mods.filter (!· matches .adv _)", "mods := a.mods"),
    (L, "normal-args-raw", "Atom.normal", "the normal form writes the arguments in the atom's order, not canon's",
     "a.canon.args.flatMap", "a.args.flatMap"),
    (M, "parts-joined-empty", "Filler.parts", "a joined filler's parts are not checked",
     ".joined _ ps => ps", ".joined _ _ => []"),
    (M, "nonempty-dropped", "normalOk", "an empty words part is accepted",
     "| .words ws => !ws.isEmpty && ws.all", "| .words ws => ws.all"),
    (M, "filler-words-dropped", "normalOk", "any word is accepted in a words part",
     "ws.all (fun w => !(fillExcl V f).contains w.toLower)", "true"),
    (M, "filler-words-case", "normalOk", "the filler words are compared without lower-casing",
     "!(fillExcl V f).contains w.toLower", "!(fillExcl V f).contains w"),
    (M, "subject-slot-allowed", "normalOk", "the subject slot {0} is accepted as a part",
     "| .slot i => i != 0", "| .slot _ => true"),
    (M, "nodup-dropped", "normalOk", "a repeated argument marker is accepted",
     "decide (a.args.map (·.1)).Nodup &&\n", ""),
    (M, "split-joined-allowed", "normalOk", "a joined filler under a split marker is accepted",
     "!f.split.contains m && 2", "2"),
    (M, "two-parts-dropped", "normalOk", "a joined filler of fewer than two parts is accepted",
     "2 ≤ ps.length && !longEnd ps", "!longEnd ps"),
    (M, "two-parts-one", "normalOk", "a joined filler of one part is accepted",
     "2 ≤ ps.length", "1 ≤ ps.length"),
    (M, "d9-dropped", "normalOk", "a joined filler with a long first or last part is accepted",
     "2 ≤ ps.length && !longEnd ps", "2 ≤ ps.length"),
    (M, "no-frame-accepted", "normalOk", "an atom whose head no frame declares is accepted",
     "  | none => false\n  | some f =>\n    atomOk", "  | none => true\n  | some f =>\n    atomOk"),
    (M, "atomOk-dropped", "normalOk", "an atom that does not fit its frame is accepted",
     "    atomOk V a &&\n", ""),
    (M, "longEnd-first-only", "longEnd", "D9 (i) checks the first part only",
     "long ps.head? || long ps.getLast?", "long ps.head?"),
    (M, "longEnd-one-word", "longEnd", "D9 (i) refuses a one-word end",
     "some (.words (_ :: _ :: _)) => true", "some (.words (_ :: _)) => true"),
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
        try:
            assert original.count(before) == 1, bug
            (ROOT / src).write_text(original.replace(before, after))
            out = lake("build", "VE.Acts.RenderExamples")
        finally:
            subprocess.run(["git", "checkout", "--", src], cwd=ROOT, check=True)
        blocks = re.split(r"(?m)^(?=error: )", out.stdout + out.stderr)
        guards = sorted({f"lean/VE/Acts/{m.group(1)}.lean:{m.group(2)}" for b in blocks
                         if "did not evaluate to `true`" in b
                         for m in [re.match(r"error: (?:\./)*\S*?(\w+Examples)\.lean:(\d+)", b)] if m})
        refused = [b.splitlines()[0] for b in blocks if b.startswith("error: ") and Path(src).name in b.splitlines()[0]]
        status = "REFUSED" if refused else "KILLED" if guards and out.returncode else "SURVIVED"
        rows.append({"id": bug, "language": "Lean", "file": src, "definition": "VE.Acts." + definition,
                     "behaviour": behaviour, "status": status, "test": ", ".join(guards) or "; ".join(refused)})
        print(status, bug, rows[-1]["test"], flush=True)
    restored = lake("build", "VE.Acts.RenderExamples")
    order = [b[1] for b in BUGS]
    rows.sort(key=lambda r: order.index(r["id"]))
    out_json.write_text(json.dumps(
        {"restored_build_returncode": restored.returncode, "mutants": rows}, indent=1, ensure_ascii=False) + "\n")
    return 0 if restored.returncode == 0 and all(r["status"] == "KILLED" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
