"""Lean's side of AP-7: `phraseReadings` over every sample phrase under its declared vocabulary, modal included.

    python3 docs/act-phrases/ap-7/dump.py [--vocab-only]

Writes a Lean file to a temporary directory and runs it with `lake env lean` in lean/; Lean decides every outcome and
writes every reading's English (`paraphrase`, Table.lean). Per phrase: `refused` (with Lean's diagnostic) when the
vocabulary fails `checkVocab` or the act fails the act check's conditions 1 to 5 or its lexing (`checkWith`, as
`checkAct` runs them for a joined act), `limit`, `none` (no reading), or `ok` with the readings; beside each, Lean's
raw derivation count and meaning count (a phrase that parses but has no meaning was refused by the meaning: D9 (i) or
a frame misfit). Writes lean-readings.json. `--vocab-only` prints `checkVocab`'s outcomes and nothing else (the one
check allowed before the vocabularies are frozen, PRE-REGISTRATION.md). No model call.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORPUS = ROOT / "docs/act-phrases/ap-2/evidence/n-measurement.json"
OPS = {"must": ".must", "mustNot": ".mustNot", "may": ".may", "right": ".right"}
HEADER = """import VE.Acts.Wire
import VE.Acts.GrammarExamples
open Lean VE.Acts VE.Acts.Examples

def out (status : String) (rest : List (String × Json) := []) : Json :=
  Json.mkObj (("status", Json.str status) :: rest)
def vocabOnly (V : Vocab) : Json :=
  match checkVocab V with | .ok () => out "ok" | .error e => out "refused" [("diagnostic", Json.str e)]
def ap7 (fx : List String) (V : Vocab) (op : Op) (arity : Nat) (s : String) : Json :=
  match checkVocab V with
  | .error e => out "refused" [("diagnostic", Json.str e)]
  | .ok () =>
    match Lexical.checkWith (fun act ts => (pure (act, ts) : Except String (String × List Lexical.Tok))) fx "the phrase"
      arity (Json.str s) with
    | .error e => out "refused" [("diagnostic", Json.str e)]
    | .ok (_, ts) =>
      let raw := match VE.Grammar.parse (grammar V) rawCap stepBudget ts.toArray with
        | some trees => Json.num trees.length | none => Json.null
      let meanings := match readings V rawCap stepBudget ts.toArray with
        | .ok As => Json.num As.length | .limit => Json.null
      let counts := [("raw", raw), ("meanings", meanings)]
      match phraseReadings V op rawCap stepBudget ts.toArray with
      | .limit => out "limit" counts
      | .ok [] => out "none" counts
      | .ok Rs => out "ok" (counts ++ [("readings", Json.arr (Rs.map (Json.str ∘ paraphrase fx op none)).toArray)])
"""


def vocabularies() -> list[dict]:
    """Each sample phrase with its declared phrase, fixed phrases, frames and adverbs (its corpus row's, if named)."""
    rows = {r["id"]: r for r in json.loads(CORPUS.read_text())["rows"]}
    sample = json.loads((HERE / "sample.json").read_text())
    keys = ("phrase", "fixed", "frames", "adverbs")
    return [p | {k: rows[p["corpus"]][k] for k in keys} if "corpus" in p else p for p in sample]


def lean_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def lean_list(xs: list[str]) -> str:
    return "[" + ", ".join(map(lean_str, xs)) + "]"


def call(p: dict, vocab_only: bool) -> str:
    frames = ", ".join(f"fr {lean_str(h)} {lean_list(m)} {lean_list(s)} {lean_list(mods)}"
                       for h, m, s, mods in p["frames"])
    vocab = f"(⟨[{frames}], {lean_list(p['adverbs'])}⟩ : Vocab)"
    if vocab_only:
        return f"vocabOnly {vocab}"
    arity = len(set(re.findall(r"\{(\d+)\}", p["phrase"])))
    return f"ap7 {lean_list(p['fixed'])} {vocab} {OPS[p['op']]} {arity} {lean_str(p['phrase'])}"


def run(vocab_only: bool = False) -> list[dict]:
    phrases = vocabularies()
    body = HEADER + "\n#eval IO.println (Json.compress (Json.arr #[\n  " + ",\n  ".join(
        call(p, vocab_only) for p in phrases) + "]))\n"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "Ap7Dump.lean"
        path.write_text(body)
        env = os.environ | {"PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}
        done = subprocess.run(["lake", "env", "lean", str(path)], cwd=ROOT / "lean", capture_output=True, text=True,
                              env=env)
    if done.returncode:
        raise SystemExit(f"lean failed:\n{done.stdout[-4000:]}\n{done.stderr[-4000:]}")
    outcomes = json.loads(done.stdout.strip().splitlines()[-1])
    return [{"id": p["id"], "op": p["op"], "phrase": p["phrase"]} | o for p, o in zip(phrases, outcomes, strict=True)]


if __name__ == "__main__":
    if sys.argv[1:] == ["--vocab-only"]:
        for row in run(vocab_only=True):
            print(row["id"], row["status"], row.get("diagnostic", ""))
    elif sys.argv[1:]:
        raise SystemExit("usage: dump.py [--vocab-only]")
    else:
        rows = run()
        (HERE / "lean-readings.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
        for row in rows:
            print(row["id"], row["status"], len(row.get("readings", [])))
