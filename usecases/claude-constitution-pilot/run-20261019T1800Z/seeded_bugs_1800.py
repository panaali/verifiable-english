#!/usr/bin/env python3
"""Run 20261019T1800Z: the seeded faults of this run's claims (no product code in Lean, Python or Rust was changed; the claims are the translator's).

    uv run python usecases/claude-constitution-pilot/run-20261019T1800Z/seeded_bugs_1800.py

Faults planted in memory on the formulas the run's fences parse to: each mutated formula must render to different English than the ledger's, a stale English or note must trip the assertion that
guards it, and a mutated document must change the check. Writes evidence/seeded-bugs.json."""
from __future__ import annotations
import copy, json, subprocess, sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(RUN))
from ve.ast import formula_from_data  # noqa: E402
from ve.english import parse_english, render_english  # noqa: E402
from ve.environment import Environment  # noqa: E402
import ledger_1800z as L3  # noqa: E402

meta = json.loads((RUN / "translation-without-content.ve.md").read_bytes().split(b"---\n", 2)[1])
env = Environment.from_dict(meta["environment"])
ledger = {e["id"]: e for e in json.load(open(RUN / "units.json"))}
out = []


def english_of(a):
    return "Checked reading: " + render_english(formula_from_data(env, a), env) + "."


good = ["exists", "entity", ["binary", "core_value_of", ["var", 0], ["const", "claude"]]]
assert english_of(good) == ledger["u0013.presupposition"]["checked_english"], english_of(good)
assert [__import__("ve.ast", fromlist=["formula_to_data"]).formula_to_data(env, f) for f in parse_english(env, L3.FENCE["u0013"]).formulas] == [good]


def caught(claim, planted, file, check, failure):
    out.append({"claim": claim, "planted": planted, "file": file, "failing_check": check, "failure": failure, "restored": "in-memory fault; the file was not touched"})
    print("failed as it should:", claim)


# 1. u0013 presupposes that there is a core value of Claude (an existential): turned into a universal
bad = ["forall", "entity", ["binary", "core_value_of", ["var", 0], ["const", "claude"]]]
assert english_of(bad) != ledger["u0013.presupposition"]["checked_english"]
caught("u0013.presupposition says that there is a core value of Claude", "the existential turned into “for every thing”", "translation-without-content.ve.md (fence of the unit)",
       "finish_20261019T1800Z.py: the exact-English assertion on the unit (`Checked reading: There is a thing that is a core value of claude.`)", f"rendered English: {english_of(bad)[:90]}")
# 2. u0013: the owner changed (a core value of Anthropic instead of Claude's)
bad = ["exists", "entity", ["binary", "core_value_of", ["var", 0], ["const", "claude"]]]
bad[2][3] = ["const", "anthropic"]
try:
    english_of(bad)
except Exception as exc:   # `anthropic` has the sort principal_type, `core_value_of` takes two things: Lean's typing check refuses the formula
    caught("u0013.presupposition is about Claude's core values, not another party's", "the owner constant replaced by `anthropic`", "translation-without-content.ve.md (fence of the unit)",
           "Lean's typing check of the formula (ve.ast.formula_from_data)", f"{type(exc).__name__}: {str(exc)[:90]}")
else:
    raise SystemExit("the changed owner was NOT caught")
# 3. u0013: the relation swapped for another noun (guideline of claude)
bad = copy.deepcopy(good); bad[2][1] = "nature_of"
try:
    e = english_of(bad)
except Exception as exc:
    caught("u0013.presupposition says core value, not nature", "the predicate replaced by nature_of (not in the document without the other units)", "translation-without-content.ve.md", "Lean's typing check", f"{type(exc).__name__}: {str(exc)[:90]}")
else:
    raise SystemExit("an undeclared predicate was NOT caught")
# 4. the stale reason must not survive: the ledger step refuses a ledger whose u0013 note is not the old one
stale = [{**e} for e in json.load(open(RUN / "units.json"))]
try:
    L3.apply(stale, {"u0013.presupposition": "x"})
except AssertionError as exc:
    caught("the ledger step applies once: u0013 must start as the old “not admitted” unit", "the ledger step run twice on its own output", "ledger_1800z.py",
           "ledger_1800z.apply's assertion on the old status and note", f"AssertionError: {str(exc)[:80]}")
else:
    raise SystemExit("a second application was NOT caught")
# 5. a mutated DOCUMENT: the fence of u0013 turned into a universal in a scratch copy changes the document's English (Lean renders it), and the check still loads, so the English comparison is what guards it
raw = (RUN / "translation.ve.md").read_bytes()
fence = b"```ve u0013.presupposition\nSome thing is a core value of claude.\n```\n"
assert raw.count(fence) == 1
scratch = RUN / "scratch-seeded"
scratch.mkdir(exist_ok=True)
(scratch / "mutant.ve.md").write_bytes(raw.replace(fence, b"```ve u0013.presupposition\nEvery thing is a core value of claude.\n```\n"))
proc = subprocess.run([sys.executable, "-m", "ve", "document", "render", str((scratch / "mutant.ve.md").relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True)
assert proc.returncode == 0 and "Every thing is a core value of claude" in proc.stdout and "There is a thing that is a core value of claude" not in proc.stdout
out.append({"claim": "the document's rendering of u0013 states the existence of a core value", "planted": "the fence turned into “Every thing is a core value of claude.” in a scratch copy of translation.ve.md",
            "file": "scratch copy (deleted afterwards)", "failing_check": "finish_20261019T1800Z.py: block_after(render, 'Claude’s core values') == 'Checked reading: There is a thing that is a core value of claude.'",
            "failure": "the rendering reads “Every thing is a core value of claude.”", "restored": "scratch copy deleted; the run's translation was not touched"})
print("failed as it should: mutated document")
(scratch / "mutant.ve.md").unlink(); scratch.rmdir()
(RUN / "evidence").mkdir(exist_ok=True)
doc = {"needed_for_product_code": False,
       "why": "no product code (Lean, Python, Rust) was changed: this run adds and changes files under usecases/ only (lean/.lake and rust/target in the worktree are ignored build products; `git diff ve-green-et-3b -- ve lean rust` is empty). "
              "The claims below are the translator's; each was planted and caught.",
       "translation_faults": out,
       "premise_check_note": "the premise-check dependence on identifiers (evidence/ps6r/premise-variants.json) is a measurement of VE's search budget, not a seeded fault"}
(RUN / "evidence/seeded-bugs.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print(len(out), "faults, all caught")
