"""ap-3 seeded bugs and hand mutants: plant each one, build the fixtures, restore the file.

    uv run python docs/act-phrases/ap-3/seed_bugs.py

`BUGS` are one bug per claimed behaviour (the table, the ops) and one per table cell. The sweep replaces every `Op`
in `opOf` and `table`, one occurrence at a time, by each other `Op`. Table.lean's theorems are cut first, so a row is
shown to break a fixture, not only a proof. KILLED: every Lean error is a failed `#guard` of TableExamples.lean;
INVALID: Lean refuses the mutated text (a redundant or missing case); SURVIVOR: the build passes. Every bug must be
KILLED, every sweep row KILLED or INVALID. The type rows (review F1) are the data-type mutants of
`tests/test_acts_tree_mutants.py`, generated from Lean's reading of `Tree.lean`'s and `Table.lean`'s types, one row per
mutant: KILLED (only the fixtures fail) or REFUSED (Lean refuses the trusted code that names the constructor or field),
never SURVIVOR. Writes mutants.json beside this file; run it on a clean lean/.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
from tests import test_acts_tree_mutants as types  # noqa: E402
TABLE = "lean/VE/Acts/Table.lean"
LAKE = ["lake", "build", "VE.Acts.TableExamples"]

BUGS = [  # (id, from, to, claim)
    ("must-distributes-over-or", "  | .must, .any nor sp ps => if nor || sp then [] else [[.whole (.any nor sp ps)]]",
     "  | .must, .any nor sp ps => if nor then [] else [ps.map Simple.atom]",
     "the plan's seeded bug: T8, must on a split marker's or, has no reading"),
    ("must-or-nor-refused-only", "if nor || sp then []", "if sp then []", "must on nor has no reading"),
    ("must-and-one-act", "  | .must, .all _ _ ps => [ps.map Simple.atom]", "  | .must, .all s sp ps => [[.whole (.all s sp ps)]]",
     "must distributes over and"),
    ("must-not-and-always-split",
     "if sp then [ps.map Simple.atom] else [ps.map Simple.atom, [.whole (.all s sp ps)]]", "[ps.map Simple.atom]",
     "T9: must not on an unsplit and reads each, or only doing both"),
    ("must-not-or-one-act", "  | .mustNot, .any _ _ ps => [ps.map Simple.atom]",
     "  | .mustNot, .any n s ps => [[.whole (.any n s ps)]]", "T1, T3: prohibition distributes over or and nor"),
    ("need-not-reads", "  | .needNot, _ => []", "  | .needNot, A => freeTable A", "T10: need not on a join has no reading"),
    ("free-own-to-together", "  | .all false _ ps => [ps.map Simple.atom]",
     "  | .all false sp ps => [ps.map Simple.atom, [.whole (.all false sp ps)]]", "T6: may with own to splits"),
    ("free-split-and-together", "  | .all true true ps => [ps.map Simple.atom]",
     "  | .all true true ps => [ps.map Simple.atom, [.whole (.all true true ps)]]", "may on a split marker's and: each"),
    ("free-shared-split-only", "  | .all true false ps => [ps.map Simple.atom, [.whole (.all true false ps)]]",
     "  | .all true false ps => [ps.map Simple.atom]", "may with a shared to: each, or both together"),
    ("free-nor-reads", "  | .any true _ _ => []", "  | .any true _ ps => [ps.map Simple.atom]", "T4: nor under may has no reading"),
    ("free-split-or-one-act", "  | .any false true ps => [ps.map Simple.atom]",
     "  | .any false true ps => [ps.map Simple.atom, [.whole (.any false true ps)]]", "T7: a split marker's or, each"),
    ("free-or-one-act-only", "  | .any false false ps => [ps.map Simple.atom, [.whole (.any false false ps)]]",
     "  | .any false false ps => [[.whole (.any false false ps)]]", "T5: may with or reads each way, or one act"),
    ("free-one-dropped", "  | .one a => [[.atom a]]\n  | .all false", "  | .one _ => []\n  | .all false",
     "freeTable on a simple act (its own guard)"),
    ("table-one-dropped", "  | _, .one a => [[.atom a]]", "  | _, .one _ => []", "T2: a simple act is its one reading"),
    ("prohibition-is-need-not", "  | .permission, false => some .mustNot", "  | .permission, false => some .needNot",
     "ops: a permission with sign false is must not"),
    ("plain-false-has-op", "  | .plain, false => none", "  | .plain, false => some .right", "ops: plain, sign false, has none"),
]


def build():
    env = dict(os.environ, PATH=str(Path.home() / ".elan/bin") + os.pathsep + os.environ["PATH"])
    return subprocess.run(LAKE, cwd=ROOT / "lean", env=env, capture_output=True, text=True)


def cut_theorems(text):
    out, skipping = [], False
    for line in text.splitlines(keepends=True):
        if line and not line[0].isspace():
            skipping = line.startswith("theorem ")
        if not skipping:
            out.append(line)
    return "".join(out)


def attempt(text):
    try:
        (ROOT / TABLE).write_text(cut_theorems(text))
        proc = build()
    finally:
        subprocess.run(["git", "checkout", "--", TABLE], cwd=ROOT, check=True)
    out = proc.stdout + proc.stderr
    where = set(re.findall(r"error: (\S+\.lean):\d+", out))
    lines = [ln for ln in out.splitlines() if "error" in ln or "did not evaluate" in ln][:4]
    if proc.returncode == 0:
        return "SURVIVOR", lines
    if where == {"VE/Acts/TableExamples.lean"} and "did not evaluate to `true`" in out:
        return "KILLED", lines
    return ("INVALID" if where and "VE/Acts/TableExamples.lean" not in where else "UNKNOWN"), lines


def type_rows():
    lake = shutil.which("lake", path=str(Path.home() / ".elan/bin") + os.pathsep + os.environ["PATH"])
    where = Path(tempfile.mkdtemp())
    try:
        done = types._elaborate(lake, where, "ApTreeDump", types.DUMP.replace(
            "@MODULES@", "[" + ", ".join(f"`{m}" for m in types.MODULES) + "]"))
        dump = json.loads(done.stdout)
        shapes = {"types": {d["type"].rsplit(".", 1)[1]: d for d in dump if "type" in d},
                  "theorems": [d for d in dump if "theorem" in d]}
        rows = []
        for name in types.TYPES:
            entry = shapes["types"][name]
            for mid, (status, found) in types.run_type(lake, where, shapes, name).items():
                rows.append({"id": f"type-{name}-{mid.replace(' ', '-')}", "kind": "type", "language": "Lean",
                             "file": f"lean/{entry['module'].replace('.', '/')}.lean", "definition": entry["type"],
                             "mutation": mid, "status": status,
                             "test": f"tests/test_acts_tree_mutants.py::test_every_mutant_of_a_data_type_is_killed_or_refused[{name}]",
                             "output": [f"{m}: {text.splitlines()[0]}" for m, _, text in found[:2]]})
                print(f"{rows[-1]['id']:52} {status}", flush=True)
        return rows
    finally:
        shutil.rmtree(where)


def main():
    if subprocess.run(["git", "status", "--porcelain", "--", "lean"], cwd=ROOT, capture_output=True, text=True).stdout:
        sys.exit("the tree is not clean under lean/")
    text, rows = (ROOT / TABLE).read_text(), []
    for rid, old, new, claim in BUGS:
        if text.count(old) != 1:
            sys.exit(f"{rid}: the text to mutate occurs {text.count(old)} times")
        status, out = attempt(text.replace(old, new))
        rows.append({"id": rid, "kind": "bug", "language": "Lean", "file": TABLE, "claim": claim,
                     "mutation": {"from": old.strip(), "to": new.strip()},
                     "test": "lean/VE/Acts/TableExamples.lean", "status": status, "output": out})
        print(f"{rid:36} {status}", flush=True)
    ops = [".must", ".needNot", ".may", ".mustNot", ".right"]
    pat = re.compile("|".join(re.escape(o) + r"(?![A-Za-z])" for o in ops))
    for d in ["opOf", "table"]:
        m0 = re.search(rf"^def {d}\b.*?(?=\n\n)", text, re.S | re.M)
        for k, m in enumerate(pat.finditer(text, m0.start(), m0.end())):
            for o in ops:
                if o == m.group(0):
                    continue
                status, out = attempt(text[:m.start()] + o + text[m.end():])
                rid = f"sweep-{d}-{k}-{o[1:]}"
                rows.append({"id": rid, "kind": "sweep", "language": "Lean", "file": TABLE, "definition": f"VE.Acts.{d}",
                             "mutation": {"from": m.group(0), "to": o, "occurrence": k},
                             "test": "lean/VE/Acts/TableExamples.lean", "status": status, "output": out})
                print(f"{rid:36} {status}", flush=True)
    restored = build().returncode  # the oleans of the restored tree: the type rows read their ranges from Lean
    rows += type_rows()
    allowed = {"bug": ("KILLED",), "sweep": ("KILLED", "INVALID"), "type": ("KILLED", "REFUSED")}
    ok = all(r["status"] in allowed[r["kind"]] for r in rows)
    counts = {s: sum(r["status"] == s for r in rows) for s in sorted({r["status"] for r in rows})}
    (Path(__file__).parent / "mutants.json").write_text(json.dumps(
        {"restored_build_exit": restored, "all_failed": ok, "counts": counts, "rows": rows}, indent=1,
        ensure_ascii=False) + "\n")
    if not ok or restored != 0:
        sys.exit("a seeded bug or a sweep mutant survived, or the restored build failed")


if __name__ == "__main__":
    main()
