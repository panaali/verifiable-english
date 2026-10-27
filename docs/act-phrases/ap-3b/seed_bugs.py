"""ap-3b seeded bugs and the constructor sweep: plant each one, show that the fixtures fail, restore the file.

    uv run python docs/act-phrases/ap-3b/seed_bugs.py

Two kinds of rows, each planted in a file this item changed and run against `lake build VE.Acts.TableExamples`:

* `BUGS`: one bug per claimed behaviour, and at least one in every new definition of Linearize.lean and of
  Table.lean's paraphrase section (`DEFS` lists them; the script refuses to run when one has no bug);
* the sweep (`SWEEPS`): inside the new definitions, every constructor of `Op`, `Role`, `Tok` and every join word
  replaced by each of its siblings, one occurrence at a time.

Table.lean's theorems are cut before every build (`cut_theorems`), so a bug is shown to break a fixture, not only a
proof. A row is KILLED when a `#guard` of TableExamples.lean fails, INVALID when Lean refuses the mutated text itself
(a redundant or missing case, a type error), SURVIVOR when the build passes. Every BUGS row must be KILLED; a sweep
row must be KILLED or INVALID, or be listed in `EQUIVALENT` with its reason. Writes mutants.json beside this file.
Run it on a clean tree with the Lean build up to date. (Carried over from ap-3's wip/ap-3b, 9c5bb9fe0.)
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
LIN, TABLE = "lean/VE/Acts/Linearize.lean", "lean/VE/Acts/Table.lean"

# The new definitions of this item: every one must carry at least one bug below.
DEFS = {
    LIN: ["joinWord", "Part.toks", "listToks", "Filler.toks", "Atom.normal", "tokStr", "tokText", "Atom.withTo",
          "Atom.text", "partAct"],
    TABLE: ["listText", "Act.text", "Simple.text", "Op.inf", "modalText", "sentence", "paraphrase", "numbered",
            "firstEqualPair", "distinctTexts", "paraphrases"],
}

# (id, file, definition, from, to, claim)
BUGS = [
    # B1 rendering of a part's act (5.5)
    ("part-act-always-to", LIN, "partAct",
     "Atom.text fx (some (role == .plain)) a", "Atom.text fx (some true) a",
     "B1 a permission's part has no infinitive to (G6's parts)"),
    ("join-word-nor-as-or", LIN, "joinWord", '  | .nor => "nor"', '  | .nor => "or"', "B1 a nor list renders nor"),
    ("part-words-first-only", LIN, "Part.toks", "  | .words ws => ws.map Tok.word",
     "  | .words ws => (ws.take 1).map Tok.word", "B1 a words part renders every word"),
    ("list-two-comma", LIN, "listToks", "  | [p, q] => p.toks ++ [Tok.word (joinWord j)] ++ q.toks",
     "  | [p, q] => p.toks ++ [Tok.comma] ++ q.toks", "B1 a list of two is joined by its join word"),
    ("list-many-no-comma", LIN, "listToks", "  | p :: rest => p.toks ++ [Tok.comma] ++ listToks j rest",
     "  | p :: rest => p.toks ++ listToks j rest", "B1 a list of three or more takes commas"),
    ("filler-one-dropped", LIN, "Filler.toks", "  | .one p => p.toks", "  | .one _ => []",
     "B1 a one-part filler renders"),
    ("to-word-misspelt", LIN, "Atom.normal", '(if a.toWord then [Tok.word "to"] else [])',
     '(if a.toWord then [Tok.word "so"] else [])', "B1 the infinitive to"),
    ("be-word-dropped", LIN, "Atom.normal", '(if a.beWord then [Tok.word "be"] else [])', "([] : List Tok)",
     "B1 be"),
    ("prep-marker-dropped", LIN, "Atom.normal", ".prep m p => (wordsOf m).map Tok.word ++ p.toks",
     ".prep m p => p.toks", "B1 a prepositional modifier keeps its marker"),
    ("object-after-markers", LIN, "Atom.normal", '(a.args.filter (fun x => x.1 == "")).flatMap (fun x => x.2.toks) ++',
     "", "B1 the object is rendered, before the marked arguments"),
    ("slot-number-shifted", LIN, "tokStr", '  | .slot i => "{" ++ toString i ++ "}"',
     '  | .slot i => "{" ++ toString (i + 1) ++ "}"', "B1 a slot renders as itself"),
    ("fixed-not-folded", LIN, "tokStr", '  | .fixed i => Lexical.normal (fx.getD i "")', '  | .fixed i => fx.getD i ""',
     "B1 a fixed phrase renders canonical (the curly apostrophe of A19 read as ')"),
    ("text-separator", LIN, "tokText", '    | _ => if acc.isEmpty then tokStr fx t else acc ++ " " ++ tokStr fx t) ""',
     '    | _ => if acc.isEmpty then tokStr fx t else acc ++ "  " ++ tokStr fx t) ""', "B1 one space between tokens"),
    ("comma-spaced", LIN, "tokText", '    | .comma => acc ++ ","', '    | .comma => acc ++ " ,"',
     "B1 a comma attaches to the token before it"),
    ("with-to-ignored", LIN, "Atom.withTo", "{ a with toWord := inf.getD a.toWord }", "a",
     "B1 the modal's form sets to"),
    ("with-to-default-true", LIN, "Atom.withTo", "{ a with toWord := inf.getD a.toWord }",
     "{ a with toWord := inf.getD true }", "B1 with no form, to as read (Atom.text … none)"),
    ("text-without-fixed", LIN, "Atom.text", "tokText fx (a.withTo inf).normal", "tokText [] (a.withTo inf).normal",
     "B1 fixed phrases render as declared"),
    # B2 paraphrases (2.2, 6.2): E9 and P12n exactly
    ("list-text-many-as-two", TABLE, "listText", '  | x :: rest => x ++ ", " ++ listText j rest',
     '  | x :: rest => x ++ " " ++ j ++ " " ++ listText j rest', "B2 a whole join of three takes commas"),
    ("list-text-two-comma", TABLE, "listText", '  | [x, y] => x ++ " " ++ j ++ " " ++ y', '  | [x, y] => x ++ ", " ++ y',
     "B2 a whole join of two takes its join word (E9 reading 2)"),
    ("act-text-nor-as-or", TABLE, "Act.text", '(if nor then "nor" else "or")', '"or"',
     "B2 a whole nor join reads nor"),
    ("act-text-subject-kept", TABLE, "Act.text", '  | .all _ _ ps => "{0} " ++ listText "and" (ps.map (fun a => (Atom.text fx inf a).drop 4))',
     '  | .all _ _ ps => "{0} " ++ listText "and" (ps.map (fun a => (Atom.text fx inf a).drop 3))',
     "B2 each atom of a whole and join after its subject"),
    ("simple-whole-no-form", TABLE, "Simple.text", "  | .whole A => Act.text fx inf A", "  | .whole A => Act.text fx none A",
     "B2 a whole join takes the modal's to on each atom (is entitled to … or to …)"),
    ("right-without-to", TABLE, "Op.inf", "  | .right => true", "  | .right => false",
     "B2 to after has the right and is entitled"),
    ("right-default-entitled", TABLE, "modalText", "  | .right, f => (f.getD .right).text",
     "  | .right, f => (f.getD .entitled).text", "B2 has the right when the form is not known (the spec's default)"),
    ("must-not-as-must", TABLE, "modalText", '  | .mustNot, _ => "must not"', '  | .mustNot, _ => "must"',
     "B2 must not (P12n)"),
    ("sentence-no-subject", TABLE, "sentence", '  "{0} " ++ modalText op f ++ " " ++ (Simple.text fx (some op.inf) x).drop 4',
     '  modalText op f ++ " " ++ (Simple.text fx (some op.inf) x).drop 4', "B2 each sentence names its subject"),
    ("paraphrase-no-gloss", TABLE, "paraphrase",
     '  | [.whole A] => sentence fx op f (.whole A) ++ ", as one act done in any one of these ways (not each way on its own)."',
     '  | [.whole A] => sentence fx op f (.whole A) ++ "."', "B2 a whole join by or carries its gloss (E9)"),
    ("paraphrase-and-gloss-as-or", TABLE, "paraphrase",
     '  | [.whole (.all s sp ps)] => sentence fx op f (.whole (.all s sp ps)) ++ ", as one act done together (not each on its own)."',
     '  | [.whole (.all s sp ps)] => sentence fx op f (.whole (.all s sp ps)) ++ ", as one act done in any one of these ways (not each way on its own)."',
     "B2 a whole join by and carries its own gloss (P12n)"),
    ("paraphrase-two-semicolon", TABLE, "paraphrase", '  | [x, y] => sentence fx op f x ++ ", and " ++ sentence fx op f y ++ "."',
     '  | [x, y] => sentence fx op f x ++ "; and " ++ sentence fx op f y ++ "."', "B2 a split of two (E9 reading 1)"),
    ("paraphrase-many-last-dropped", TABLE, "paraphrase", '(xs.getLast?.map (sentence fx op f)).getD ""', '""',
     "B2 a split of three or more ends with its last act"),
    ("numbered-from-zero", TABLE, "numbered", "toString (i + 1)", "toString i", "B2 readings numbered from 1 (E9)"),
    # B3 distinct texts (D-32)
    ("equal-paraphrases-listed", TABLE, "firstEqualPair",
     "  | k, t :: ts => if ts.contains t then some (k, k + 1 + ts.idxOf t) else firstEqualPair (k + 1) ts",
     "  | k, t :: ts => firstEqualPair (k + 1) ts", "B3 two readings that read the same are refused"),
    ("equal-pair-second-off", TABLE, "firstEqualPair", "some (k, k + 1 + ts.idxOf t)", "some (k, k + ts.idxOf t)",
     "B3 D-32 names the second reading of the pair"),
    ("equal-pair-from-zero", TABLE, "distinctTexts", "  match firstEqualPair 1 ts with", "  match firstEqualPair 0 ts with",
     "B3 D-32 counts readings from 1"),
    ("distinct-texts-reversed", TABLE, "distinctTexts", "  | none => .ok ts", "  | none => .ok ts.reverse",
     "B3 distinct texts pass unchanged, in order"),
    ("paraphrases-unchecked", TABLE, "paraphrases", "  distinctTexts what (Rs.map (paraphrase fx op f))",
     "  .ok (Rs.map (paraphrase fx op f))", "B3 the paraphrases of one listing go through distinctTexts"),
]

# The sweep: (family, siblings as written, file, definitions searched).
OPS = [".must", ".needNot", ".may", ".mustNot", ".right"]
ROLES = [".obligation", ".permission", ".plain"]
TOKS = ["Tok.slot", "Tok.fixed", "Tok.word", "Tok.comma", ".slot", ".fixed", ".word", ".comma"]
SWEEPS = [
    ("op", OPS, TABLE, ["Op.inf", "modalText"]),
    ("role", ROLES, LIN, ["partAct"]),
    ("tok", TOKS, LIN, ["Part.toks", "listToks", "Atom.normal", "tokStr", "tokText"]),
    ("join", ['"and"', '"or"', '"nor"'], LIN, ["joinWord"]),
    ("joinctor", [".and", ".or", ".nor"], LIN, ["joinWord"]),
    ("join", ['"and"', '"or"', '"nor"'], TABLE, ["Act.text"]),
]

# Sweep rows that change no answer, with the reason.
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
    """The source range of `def <name>`: from its line to the next blank line or docstring."""
    m = re.search(rf"^def {re.escape(name)}\b.*?(?=\n\n|\n/--)", text, re.S | re.M)
    if not m:
        sys.exit(f"no definition {name}")
    return m.start(), m.end()


def verdict(proc):
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
    if path != TABLE:
        table = ROOT / TABLE
        table.write_text(cut_theorems(table.read_text()))
    else:
        text = cut_theorems(text)
    (ROOT / path).write_text(text)


def restore():
    subprocess.run(["git", "checkout", "--", LIN, TABLE], cwd=ROOT, check=True)


def main():
    if subprocess.run(["git", "status", "--porcelain", "--", "lean"], cwd=ROOT, capture_output=True,
                      text=True).stdout.strip():
        sys.exit("the tree is not clean under lean/")
    bare = [d for f, ds in DEFS.items() for d in ds if not any(b[1] == f and b[2] == d for b in BUGS)]
    if bare:
        sys.exit(f"new definitions without a seeded bug: {bare}")
    rows = []
    for name, path, d, old, new, claim in BUGS:
        text = (ROOT / path).read_text()
        lo, hi = region(text, d)
        if text.count(old) != 1 or not lo <= text.index(old) < hi:
            sys.exit(f"{name}: the text to mutate is not once in {d} of {path}")
        try:
            plant(path, text.replace(old, new))
            proc = run()
        finally:
            restore()
        status, out = verdict(proc)
        rows.append({"id": name, "kind": "bug", "language": "Lean", "file": path, "definition": d,
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
                    status, out = verdict(proc)
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
