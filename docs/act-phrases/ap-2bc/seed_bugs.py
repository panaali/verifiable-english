#!/usr/bin/env python3
"""ap-2bc's seeded bugs: plant each bug, then record what fails. (a) The fixtures: RenderExamples' `#guard`s, checked
on a copy of lean/VE/Acts/RenderExamples.lean whose `NormalProofs` import and instance examples are blanked (line
numbers kept), so that a plant which breaks a proof still reaches the guards. (b) The proofs: `lake build
VE.Acts.NormalProofs`, whose failing declarations are recorded. Then restore the file from git, rebuild
VE.Acts.RenderExamples and write mutants.json beside this script. Run from the repository root:
`python3 docs/act-phrases/ap-2bc/seed_bugs.py [ids...]` (ids rerun only those rows)."""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN = ROOT / "lean"
L, M = "lean/VE/Acts/Linearize.lean", "lean/VE/Acts/Meaning.lean"
P, R = "lean/VE/Acts/NormalProofs.lean", "lean/VE/Acts/RenderExamples.lean"
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
]
GUARDS = LEAN / "VE/Acts/SeedRenderGuards.lean"


def lake(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PATH=os.path.expanduser("~/.elan/bin") + os.pathsep + os.environ["PATH"])
    return subprocess.run(["lake", *args], cwd=LEAN, env=env, capture_output=True, text=True)


def guard_copy() -> None:
    """RenderExamples without the NormalProofs import and the instance examples, each line kept (blanked)."""
    lines = (ROOT / R).read_text().splitlines()
    cut = next(i for i, l in enumerate(lines) if l.startswith("/-! ### `normal_derived` at each family"))
    keep = [("" if l == "import VE.Acts.NormalProofs" else l) for l in lines[:cut]]
    tail = [l if l.startswith("#guard") or l.startswith("def Vk1") or l.startswith("end ") else "" for l in lines[cut:]]
    GUARDS.write_text("\n".join(keep + tail) + "\n")


def failures(out: subprocess.CompletedProcess, name: str, real: str) -> list[str]:
    blocks = re.split(r"(?m)^(?=error: )", out.stdout + out.stderr)
    return sorted({f"{real}:{m.group(1)}" for b in blocks
                   for m in [re.match(rf"error: (?:\./)*\S*?{name}:(\d+)", b)] if m}, key=lambda s: int(s.split(":")[1]))


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
            proofs = failures(lake("build", "VE.Acts.NormalProofs"), r"NormalProofs\.lean", P)
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
