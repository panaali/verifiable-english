#!/usr/bin/env python3
"""ap-2bc's seeded bugs: plant each bug, then record what fails. (a) The fixtures: RenderExamples' `#guard`s, checked
on a copy of lean/VE/Acts/RenderExamples.lean whose `NormalUnique` import and instance examples are blanked (line
numbers kept), so that a plant which breaks a proof still reaches the guards. (b) The proofs: `lake build
VE.Acts.NormalUnique` (with NormalProofs, NormalInverse and NormalBlocks), whose failing declarations are recorded.
Then restore the file from git, rebuild VE.Acts.RenderExamples and write mutants.json beside this script. Run from the
repository root: `python3 docs/act-phrases/ap-2bc/seed_bugs.py [ids...]` (ids rerun only those rows)."""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN = ROOT / "lean"
L, M = "lean/VE/Acts/Linearize.lean", "lean/VE/Acts/Meaning.lean"
P, R = "lean/VE/Acts/NormalProofs.lean", "lean/VE/Acts/RenderExamples.lean"
S, G, I = "lean/VE/Acts/Syntax.lean", "lean/VE/Acts/Grammar.lean", "lean/VE/Acts/NormalInverse.lean"
PROOFS = ("NormalProofs", "NormalInverse", "NormalBlocks", "NormalUnique")
REPEATED = ("a.canon.args.flatMap (fun x => match x.2 with\n"
            "    | .joined j ps => ps.zipIdx.flatMap (fun (p, i) => (if i == 0 then [] else\n"
            "        if i + 1 == ps.length then [Tok.word (joinWord j)] else [Tok.comma]) ++ (wordsOf x.1).map Tok.word ++ p.toks)\n"
            "    | .one p => (wordsOf x.1).map Tok.word ++ p.toks)")
# (file, id, definition, behaviour, before, after)
BUGS = [
    (M, "d9-dropped", "VE.Acts.normalOk", "`longEnd` dropped: a joined filler with a long first or last part is accepted",
     "2 ≤ ps.length && !longEnd ps", "2 ≤ ps.length"),
    (L, "canon-args-kept", "VE.Acts.Atom.canon", "the object is not put first",
     'args := a.args.filter (·.1 == "") ++ a.args.filter (·.1 != "")', "args := a.args"),
    (L, "normal-marker-repeated", "VE.Acts.Atom.normal", "a joined filler is written with its marker repeated",
     "a.canon.args.flatMap (fun x => (wordsOf x.1).map Tok.word ++ x.2.toks)", REPEATED),
    (P, "spans-short", "VE.Acts.NormalProofs.spans", "the derivation list misses the spans that end at the last token",
     "(List.range (w.size + 1)).flatMap", "(List.range w.size).flatMap"),
    (R, "vk1-reserved", "VE.Acts.RenderExamples.Vk1", "the canon family's vocabulary declares the reserved *then*",
     'def Vk1 : Vocab := ⟨Vk.frames, ["now"]⟩', 'def Vk1 : Vocab := ⟨Vk.frames, ["now", "then"]⟩'),
    # (3), the uniqueness half (review F1): each condition the argument rests on, dropped
    (M, "split-joined-accepted", "VE.Acts.normalOk",
     "a joined filler under a split marker is accepted (it reads as a split construct, a join of atoms)",
     "!f.split.contains m && 2 ≤ ps.length", "2 ≤ ps.length"),
    (S, "marker-prefix-unchecked", "VE.Acts.checkVocab", "one marker of a frame may begin another (`MK m` no longer "
     "fixes the marker)", "n != m && (wordsOf m).isPrefixOf (wordsOf n)", "n != m && false"),
    (S, "head-overlap-unchecked", "VE.Acts.checkVocab", "one head may begin another (`HD` no longer fixes the frame)",
     "g.head != f.head && f.head.isPrefixOf g.head", "g.head != f.head && false"),
    (G, "fill-marker-first", "VE.Acts.fillExcl", "a marker's first word is a filler word (a filler run no longer stops "
     "at the next element)", "V.adverbs ++ (f.markers ++ f.mods).filterMap (fun m => (wordsOf m).head?) ++",
     "V.adverbs ++"),
    (I, "tail-join-comma", "VE.Acts.NormalProofs.tailToks", "a list's last part is read after a comma, not its join word",
     "| [q] => .word (joinWord j) :: q.toks", "| [q] => .comma :: q.toks"),
]
GUARDS = LEAN / "VE/Acts/SeedRenderGuards.lean"


def lake(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PATH=os.path.expanduser("~/.elan/bin") + os.pathsep + os.environ["PATH"])
    return subprocess.run(["lake", *args], cwd=LEAN, env=env, capture_output=True, text=True)


def guard_copy() -> None:
    """RenderExamples without the NormalUnique import and the instance examples, each line kept (blanked): after the
    instances' section header, only the `#guard`s (with their continuation lines), `Vk1` and the namespace's end."""
    lines = (ROOT / R).read_text().splitlines()
    cut = next(i for i, l in enumerate(lines) if l.startswith("/-! ### `read_normal` and `normal_derived` at each"))
    keep = [("" if l == "import VE.Acts.NormalUnique" else l) for l in lines[:cut]]
    tail, guard = [], False
    for l in lines[cut:]:
        guard = l.startswith("#guard") or (guard and l.startswith("  "))
        tail.append(l if guard or l.startswith("def Vk1") or l.startswith("end ") else "")
    GUARDS.write_text("\n".join(keep + tail) + "\n")


def failures(out: subprocess.CompletedProcess, name: str, real: str) -> list[str]:
    """The lines of `name` with an error, as `lake build` (`error: path:line`) or `lean` (`path:line:col: error`)
    prints them, reported against the file `real`."""
    text = out.stdout + out.stderr
    found = re.findall(rf"(?m)^error: (?:\./)*\S*?{name}:(\d+)", text) + \
        re.findall(rf"(?m)^(?:\./)*\S*?{name}:(\d+):\d+: error", text)
    return [f"{real}:{n}" for n in sorted(set(found), key=int)]


def main() -> int:
    only = sys.argv[1:]
    out_json = Path(__file__).parent / "mutants.json"
    rows = [r for r in json.loads(out_json.read_text())["mutants"] if r["id"] not in only] if only else []
    for src, bug, definition, behaviour, before, after in BUGS:
        if only and bug not in only:
            continue
        original = (ROOT / src).read_text()
        try:
            assert original.count(before) == 1, bug
            (ROOT / src).write_text(original.replace(before, after))
            guard_copy()
            dep = lake("build", "VE.Acts.MeaningExamples")
            fixtures = [f"lean/VE/Acts/{m.group(1)}.lean:{m.group(2)}"
                        for b in re.split(r"(?m)^(?=error: )", dep.stdout + dep.stderr)
                        for m in [re.match(r"error: (?:\./)*\S*?(\w+Examples)\.lean:(\d+)", b)] if m]
            if not dep.returncode:
                fixtures = failures(lake("env", "lean", str(GUARDS.relative_to(LEAN))), r"SeedRenderGuards\.lean", R)
            built = lake("build", "VE.Acts.NormalUnique")
            proofs = [f for name in PROOFS for f in failures(built, rf"{name}\.lean", f"lean/VE/Acts/{name}.lean")]
        finally:
            subprocess.run(["git", "checkout", "--", src], cwd=ROOT, check=True)
            GUARDS.unlink(missing_ok=True)
        tests = sorted(set(fixtures)) + proofs
        status = "KILLED" if tests else "SURVIVED"
        rows.append({"id": bug, "language": "Lean", "file": src, "definition": definition, "behaviour": behaviour,
                     "status": status, "test": ", ".join(tests), "fixtures": sorted(set(fixtures)), "proofs": proofs})
        print(status, bug, rows[-1]["test"], flush=True)
    restored = lake("build", "VE.Acts.RenderExamples")
    order = [b[1] for b in BUGS]
    rows.sort(key=lambda r: order.index(r["id"]))
    out_json.write_text(json.dumps(
        {"restored_build_returncode": restored.returncode, "mutants": rows}, indent=1, ensure_ascii=False) + "\n")
    return 0 if restored.returncode == 0 and all(r["status"] == "KILLED" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
