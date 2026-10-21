#!/usr/bin/env python3
"""Run 20261019T0600Z: the seeded faults of this run's claims (no product code in Lean, Python or Rust was changed; the claims are the translator's).

    uv run python usecases/claude-constitution-pilot/run-20261019T0600Z/seeded_bugs_0600.py [cheap|closure]

`cheap`: faults planted in memory (a mutated formula must render to different English than the ledger's; a stale English or trigger must trip the assertion that guards it); writes
evidence/seeded/seeded-cheap-0600.json. `closure`: the closure of u0043.s02.p2 removed in a scratch copy (run it from a scratch run directory: nd.py all, then the no-fourth query), recorded by hand.
"""
from __future__ import annotations
import copy, json, sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(RUN))
from ve.ast import formula_from_data  # noqa: E402
from ve.english import render_english  # noqa: E402
from ve.environment import Environment  # noqa: E402
import ledger_0600 as L2  # noqa: E402

meta = json.loads((RUN / "translation-without-content.ve.md").read_bytes().split(b"---\n", 2)[1])
env = Environment.from_dict(meta["environment"])
ledger = {e["id"]: e for e in json.load(open(RUN / "units.json"))}
units = {u["id"]: u for u in meta["units"]}
ast = {"u0042.presupposition": units["u0042.presupposition"]["content"]["ast"],
       "u0043.s02.p2": next(p for p in units["u0043.s02"]["parts"] if p["id"] == "u0043.s02.p2")["content"]["ast"]}
out = []


def english_of(a):
    return "Checked reading: " + render_english(formula_from_data(env, a), env) + "."   # the document rendering ends the statement with a full stop


def expected(uid):
    return ledger[uid]["checked_english"]


# the unmutated formulas render to the ledger's English (so a difference below is the fault's)
for uid, a in ast.items():
    assert english_of(a) == expected(uid), uid


def caught(claim, planted, file, check, failure):
    out.append({"claim": claim, "planted": planted, "file": file, "failing_check": check, "failure": failure, "restored": "in-memory fault; the file was not touched"})
    print("failed as it should:", claim)


def drop_conjunct_43(a):
    b = copy.deepcopy(a)
    b[2][2] = b[2][2][2]   # remove "operators != users"
    return b


def drop_closure(a):
    b = copy.deepcopy(a)
    b[2][2][2] = ["eq", ["const", "operators"], ["const", "operators"]]   # replace the closure by a trivial truth
    return b


# 1. u0043.s02.p2: the closure over Claude's types removed (the claim "no fourth type")
bad = drop_closure(ast["u0043.s02.p2"])
assert english_of(bad) != expected("u0043.s02.p2")
caught("u0043.s02.p2 closes over Claude's types: every principal type of Claude is Anthropic, operators or users", "the closure replaced by a trivial equality", "translation-without-content.ve.md (u0043.s02.p2 content)",
       "the exact-English comparison of the rendered formula with the ledger's checked_english (this script); the no-fourth query on the scratch build is in evidence/seeded/sb1-closure-removed-no-fourth-result.json",
       "rendered English no longer contains “for every principal type of Claude”")
# 2. u0042: a distinctness conjunct dropped
bad = copy.deepcopy(ast["u0042.presupposition"]); inner = bad[2][2][2]
bad[2][2][2] = inner[2]       # drop the first conjunct "P1 differs from P2"
assert english_of(bad) != expected("u0042.presupposition")
caught("u0042.presupposition says the three types are pairwise different", "the first distinctness conjunct (P1 differs from P2) removed", "translation-without-content.ve.md (u0042.presupposition content)",
       "the exact-English comparison of the rendered formula with the ledger's checked_english", "rendered English lacks “it is not the case that P1 is the same as P2”")
# 3. u0042: a witness dropped (two types instead of three)
bad = copy.deepcopy(ast["u0042.presupposition"])
assert bad[0] == "exists" and bad[2][0] == "exists"
bad = ["exists", bad[1], bad[2][2]]
try:
    english_of(bad)
except Exception as exc:   # the remaining variable indices no longer fit: Lean's typing check refuses the formula before any English is written
    caught("u0042.presupposition says there are three types, not two", "one existential removed", "translation-without-content.ve.md (u0042.presupposition content)",
           "Lean's typing check of the formula (ve.ast.formula_from_data)", f"{type(exc).__name__}: {str(exc)[:80]}")
else:
    raise SystemExit("the dropped existential was NOT caught")
# 4. u0286 and u0032: the existential turned into a universal
for uid, pred in (("u0286.presupposition", "open_problem"), ("u0032.presupposition", "genuine_helpfulness")):
    a = ["exists", "entity", ["unary", pred, ["var", 0]]]
    assert "There is a thing that is" in english_of(a)
    bad = ["forall", "entity", ["unary", pred, ["var", 0]]]
    assert english_of(bad) != english_of(a)
    caught(f"{uid} presupposes that there is such a thing (an existential)", "the existential turned into “for every thing”", "translation-without-content.ve.md (fence of the unit)",
           "finish_20261019T0600Z.py: the exact-English assertion on the unit (`startswith(\"Checked reading: There is a thing that is unsolved\")` / `Open reading: `)", f"rendered English: {english_of(bad)[:80]}")
# 5. the repair must not leave the quoted fallback
ledger_list = list(json.load(open(RUN / "units.json")))
stale = {"u0042.presupposition": 'Checked reading: There is a type of principal named Y1 such that Y1 is classified as "claude_principal_type"', "u0043.s02.p2": 'Y1 is classified as "claude_principal_type"',
         "u0286.presupposition": "x", "u0032.presupposition": "x"}
try:
    L2.apply(copy.deepcopy([{**e, "checked_english": e.get("checked_english", "")} for e in ledger_list]), stale)
except AssertionError as exc:
    caught("the English of u0042.presupposition and u0043.s02.p2 is ordinary English, not the quoted fallback", "the old fallback English handed to the ledger step", "ledger_0600.py",
           "ledger_0600.apply's assertion on the fallback", f"AssertionError: {str(exc)[:120]}")
else:
    raise SystemExit("the stale English was NOT caught")
(RUN / "evidence/seeded").mkdir(exist_ok=True)
(RUN / "evidence/seeded/seeded-cheap-0600.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(len(out), "faults, all caught")
