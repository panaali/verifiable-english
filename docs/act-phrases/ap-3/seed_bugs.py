"""ap-3 seeded bugs and hand mutants: plant each one, show that the fixtures fail, restore the file.

    uv run python docs/act-phrases/ap-3/seed_bugs.py

Two kinds of rows, each planted in a file this item changed and run against `lake build VE.Acts.TableExamples`:

* `BUGS`: one bug per claimed behaviour, and one per new trusted definition that tools/trust_mutants.py does not
  mutate (it found no operator in it);
* the sweep (`SWEEPS`): inside each new trusted definition, every constructor of `Op`, `Role`, `Tok` and every join
  word replaced by each of its siblings, one occurrence at a time.

Table.lean's theorems are cut before every build (`cut_theorems`), so a bug is shown to break a fixture, not only a
proof. A row is KILLED when a `#guard` of TableExamples.lean fails, INVALID when Lean refuses the mutated text itself
(a redundant or missing case, a type error), SURVIVOR when the build passes. Every BUGS row must be KILLED; a sweep
row must be KILLED or INVALID, or be listed in `EQUIVALENT` with its reason. Writes mutants.json beside this file.
Run it on a clean tree with the Lean build up to date.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "mutants.json"
LAKE = ["lake", "build", "VE.Acts.TableExamples"]
SYNTAX, LIN, TABLE = "lean/VE/Acts/Syntax.lean", "lean/VE/Acts/Linearize.lean", "lean/VE/Acts/Table.lean"

# (id, file, from, to, claim): the claimed behaviours first (B1 to B4), then one per untouched definition.
BUGS = [
    ("must-distributes-over-or", TABLE,
     "  | .must, .any nor sp ps => if nor || sp then [] else [[.whole (.any nor sp ps)]]",
     "  | .must, .any nor sp ps => if nor then [] else [ps.map Simple.atom]",
     "B1 the table (the plan's seeded bug): T8, must on a split marker's or, has no reading"),
    ("must-not-and-always-split", TABLE,
     "  | .mustNot, .all s sp ps => if sp then [ps.map Simple.atom] else [ps.map Simple.atom, [.whole (.all s sp ps)]]",
     "  | .mustNot, .all s sp ps => [ps.map Simple.atom]",
     "B1 the table: T9, must not on an unsplit and has two readings"),
    ("prohibition-is-need-not", TABLE, "  | .permission, false => some .mustNot", "  | .permission, false => some .needNot",
     "B2 ops: a permission with sign false is must not (opOf guards)"),
    ("part-act-always-to", LIN, "def partAct (fx : List String) (role : VE.Norms.Role) (a : Atom) : String := Atom.text fx (some (role == .plain)) a",
     "def partAct (fx : List String) (role : VE.Norms.Role) (a : Atom) : String := Atom.text fx (some true) a",
     "B3 part rendering: a permission's part has no infinitive to (G6's parts)"),
    ("paraphrase-no-gloss", TABLE,
     "  | [.whole A] => sentence fx op f (.whole A) ++ \", as one act done in any one of these ways (not each way on its own).\"",
     "  | [.whole A] => sentence fx op f (.whole A) ++ \".\"",
     "B4 paraphrases: a whole join by or carries its gloss (E9's D-23 text)"),
    ("equal-paraphrases-listed", TABLE,
     "  | k, t :: ts => if ts.contains t then some (k, k + 1 + ts.idxOf t) else firstEqualPair (k + 1) ts",
     "  | k, t :: ts => firstEqualPair (k + 1) ts",
     "B4 paraphrases: two readings that read the same are refused (D-32 guards)"),
    ("join-word-nor-as-or", LIN, "  | .nor => \"nor\"", "  | .nor => \"or\"", "joinWord: a nor list renders nor"),
    ("filler-one-dropped", LIN, "  | .one p => p.toks", "  | .one _ => []", "Filler.toks: a one-part filler renders"),
    ("slot-number-shifted", LIN, "  | .slot i => \"{\" ++ toString i ++ \"}\"", "  | .slot i => \"{\" ++ toString (i + 1) ++ \"}\"",
     "tokStr: a slot renders as itself"),
    ("fixed-not-folded", LIN, "  | .fixed i => Lexical.normal (fx.getD i \"\")", "  | .fixed i => fx.getD i \"\"",
     "tokStr: a fixed phrase renders canonical (the curly apostrophe of A19 read as ')"),
    ("with-to-ignored", LIN, "def Atom.withTo (inf : Option Bool) (a : Atom) : Atom := { a with toWord := inf.getD a.toWord }",
     "def Atom.withTo (inf : Option Bool) (a : Atom) : Atom := a", "Atom.withTo: the modal's form sets to"),
    ("with-to-default-true", LIN, "def Atom.withTo (inf : Option Bool) (a : Atom) : Atom := { a with toWord := inf.getD a.toWord }",
     "def Atom.withTo (inf : Option Bool) (a : Atom) : Atom := { a with toWord := inf.getD true }",
     "Atom.withTo: with no form, to as read (Atom.text … none)"),
    ("text-without-fixed", LIN, "def Atom.text (fx : List String) (inf : Option Bool) (a : Atom) : String := tokText fx (a.withTo inf).normal",
     "def Atom.text (fx : List String) (inf : Option Bool) (a : Atom) : String := tokText [] (a.withTo inf).normal",
     "Atom.text: fixed phrases render as declared"),
    ("to-word-misspelt", LIN, "(if a.toWord then [Tok.word \"to\"] else [])", "(if a.toWord then [Tok.word \"so\"] else [])",
     "Atom.normal: the infinitive to"),
    ("be-word-dropped", LIN, "(if a.beWord then [Tok.word \"be\"] else [])", "([] : List Tok)", "Atom.normal: be"),
    ("text-separator", LIN, "    | _ => if acc.isEmpty then tokStr fx t else acc ++ \" \" ++ tokStr fx t) \"\"",
     "    | _ => if acc.isEmpty then tokStr fx t else acc ++ \"  \" ++ tokStr fx t) \"\"", "tokText: one space between tokens"),
    ("free-or-one-act-only", TABLE,
     "  | .any false false ps => [ps.map Simple.atom, [.whole (.any false false ps)]]",
     "  | .any false false ps => [[.whole (.any false false ps)]]", "freeTable: may with or reads each way, or one act"),
]

# The sweep: (family, siblings as written, files and definitions searched).
OPS = [".must", ".needNot", ".may", ".mustNot", ".right"]
ROLES = [".obligation", ".permission", ".plain"]
TOKS = ["Tok.slot", "Tok.fixed", "Tok.word", "Tok.comma", ".slot", ".fixed", ".word", ".comma"]
SWEEPS = [
    ("op", OPS, TABLE, ["opOf", "table"]),
    ("role", ROLES, TABLE, ["opOf"]),
    ("role", ROLES, LIN, ["partAct"]),
    ("tok", TOKS, LIN, ["Part.toks", "listToks", "Atom.normal", "tokStr", "tokText"]),
    ("join", ['"and"', '"or"', '"nor"'], LIN, ["joinWord"]),
    ("join", [".and", ".or", ".nor"], LIN, ["joinWord"]),
]

# Sweep rows that change no answer, with the reason (none so far).
EQUIVALENT: dict[str, str] = {}


def run():
    env = dict(os.environ, PATH=str(Path.home() / ".elan/bin") + os.pathsep + os.environ["PATH"])
    return subprocess.run(LAKE, cwd=ROOT / "lean", env=env, capture_output=True, text=True)


def cut_theorems(text):
    """Table.lean without its theorems: top-level chunks that begin with `theorem` are dropped."""
    out, skipping = [], False
    for line in text.splitlines(keepends=True):
        if line and not line[0].isspace():
            skipping = line.startswith("theorem ")
        if not skipping:
            out.append(line)
    return "".join(out)


def region(text, name):
    """The source range of `def <name>`: from its line to the next blank line."""
    m = re.search(rf"^def {re.escape(name)}\b.*?(?=\n\n)", text, re.S | re.M)
    if not m:
        sys.exit(f"no definition {name}")
    return m.start(), m.end()


def verdict(proc, path):
    """KILLED: every Lean error is in TableExamples.lean and one is a failed `#guard`; INVALID: an error in a
    product file (the mutated text, or a module above it); SURVIVOR: the build passes."""
    out = proc.stdout + proc.stderr
    if proc.returncode == 0:
        return "SURVIVOR", []
    lines = [ln for ln in out.splitlines() if "error" in ln.lower() or "did not evaluate" in ln][:4]
    where = set(re.findall(r"error: (\S+\.lean):\d+", out))
    if where == {"VE/Acts/TableExamples.lean"} and "did not evaluate to `true`" in out:
        return "KILLED", lines
    if where and "VE/Acts/TableExamples.lean" not in where:
        return "INVALID", lines
    return "UNKNOWN", lines


def plant(path, text):
    file = ROOT / path
    if path != TABLE:
        table = ROOT / TABLE
        table.write_text(cut_theorems(table.read_text()))
    else:
        text = cut_theorems(text)
    file.write_text(text)


def restore():
    subprocess.run(["git", "checkout", "--", SYNTAX, LIN, TABLE], cwd=ROOT, check=True)


def main():
    if subprocess.run(["git", "status", "--porcelain", "--", "lean"], cwd=ROOT, capture_output=True,
                      text=True).stdout.strip():
        sys.exit("the tree is not clean under lean/")
    rows = []
    for name, path, old, new, claim in BUGS:
        text = (ROOT / path).read_text()
        if text.count(old) != 1:
            sys.exit(f"{name}: the text to mutate occurs {text.count(old)} times in {path}")
        try:
            plant(path, text.replace(old, new))
            proc = run()
        finally:
            restore()
        status, out = verdict(proc, path)
        rows.append({"id": name, "kind": "bug", "language": "Lean", "file": path,
                     "mutation": {"from": old.strip(), "to": new.strip()}, "claim": claim,
                     "test": "lean/VE/Acts/TableExamples.lean (" + " ".join(LAKE) + ")", "status": status,
                     "output": out})
        print(f"{name:32} {status}", flush=True)
    for family, sibs, path, defs in SWEEPS:
        text = (ROOT / path).read_text()
        for d in defs:
            lo, hi = region(text, d)
            pat = re.compile("|".join(re.escape(s) + r"(?![A-Za-z])" for s in sorted(sibs, key=len, reverse=True)))
            for k, m in enumerate(pat.finditer(text, lo, hi)):
                for s in sibs:
                    if s == m.group(0) or s.startswith("Tok.") != m.group(0).startswith("Tok."):
                        continue
                    rid = f"sweep-{family}-{d}-{k}-{s.strip('.\"')}"
                    try:
                        plant(path, text[:m.start()] + s + text[m.end():])
                        proc = run()
                    finally:
                        restore()
                    status, out = verdict(proc, path)
                    if status == "SURVIVOR" and rid in EQUIVALENT:
                        status = "EQUIVALENT"
                    rows.append({"id": rid, "kind": "sweep", "language": "Lean", "file": path, "definition": d,
                                 "mutation": {"at": m.start(), "from": m.group(0), "to": s},
                                 "test": "lean/VE/Acts/TableExamples.lean", "status": status, "output": out,
                                 "reason": EQUIVALENT.get(rid)})
                    print(f"{rid:48} {status}", flush=True)
    restored = run()
    ok = all(r["status"] == "KILLED" for r in rows if r["kind"] == "bug") and \
        all(r["status"] in ("KILLED", "INVALID", "EQUIVALENT") for r in rows if r["kind"] == "sweep")
    result = {"restored_build_exit": restored.returncode, "all_failed": ok,
              "counts": {s: sum(r["status"] == s for r in rows) for s in sorted({r["status"] for r in rows})},
              "rows": rows}
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    if not ok or restored.returncode != 0:
        sys.exit("a seeded bug or a sweep mutant survived, or the restored build failed")


if __name__ == "__main__":
    main()
