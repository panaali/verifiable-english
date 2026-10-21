#!/usr/bin/env python3
"""Run 20261020T0600Z: the seeded faults of this run's claims. No product code (Lean, Python, Rust) was changed (the pilot only reads the tag), so there is no fault to plant in a changed language; the claims
are the translator's: (1) the document is the previous run's, byte for byte; (2) the three corrected ledger fences (u0235 uniqueness, u0002 and u0095 owner) are what the notes say; (3) the ledger step applies once.

    uv run python usecases/claude-constitution-pilot/run-20261020T0600Z/seeded_bugs_20261020.py

Each fault is planted in memory or in a scratch copy and must be caught by a named check. Writes evidence/seeded-bugs.json."""
from __future__ import annotations
import copy, json, subprocess, sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(RUN))
from ve.ast import formula_from_data, formula_to_data  # noqa: E402
from ve.english import parse_english, render_english  # noqa: E402
from ve.environment import Environment  # noqa: E402
import ledger_20261020 as L4  # noqa: E402

probe = json.load(open(RUN / "evidence/owner-probe.json"))
meta = json.loads((RUN / "translation-without-content.ve.md").read_bytes().split(b"---\n", 2)[1])
voc = meta["environment"]["vocabulary"]
voc["constants"][L4.COMPANY] = {"sort": "entity", "description": "probe"}
for p in ("guideline", "mission", "nature"):
    voc["predicates"][f"{p}_of_probe"] = {"arguments": ["entity", "entity"], "description": "probe", "verbalisation": "{0} is a " + p + " of {1}"}
env = Environment.from_dict(meta["environment"])
out = []


def caught(claim, planted, file, check, failure):
    out.append({"claim": claim, "planted": planted, "file": file, "failing_check": check, "failure": failure, "restored": "in-memory fault or scratch copy; no file of the run was touched"})
    print("failed as it should:", claim)


def has(o, word):
    return word in json.dumps(o)


# 1. u0235 is existence and uniqueness: the existence-only form (the old fence) must be recognised as a different formula
unique = probe["u0235.unique"]["formulas"][0]
assert unique[0] == "exists" and has(unique, "forall") and has(unique, "nature_of_probe")
old = [formula_to_data(env, f) for f in parse_english(env, "Some thing is a nature of claude.").formulas][0]
assert old != unique and not has(old, "forall")
caught("u0235.presupposition's fence says exactly one nature (existence and uniqueness)", "the uniqueness clause dropped (the old existence-only fence “Some thing is a nature of claude.”)", "evidence/owner-probe.json / ledger_20261020.FENCE",
       "finish_20261020T0600Z.py: the formula of u0235.unique must be an existential with a universal inside (assertion on owner-probe.json)", f"formula without ‘forall’: {json.dumps(old)[:90]}")
# 2. u0095 and u0002: the owner is the company, not the principal type `anthropic`
bad = json.loads(json.dumps(probe["u0095.company"]["formulas"][0])); bad[2][3] = ["const", "anthropic"]
try:
    formula_from_data(env, bad)
except Exception as exc:  # `anthropic` has the sort principal_type; the predicate takes two things
    caught("u0095.presupposition's guideline belongs to the company, not to the type of principal `anthropic`", "the owner constant replaced by `anthropic`", "evidence/owner-probe.json / ledger_20261020.FENCE",
           "Lean's typing check of the formula (ve.ast.formula_from_data)", f"{type(exc).__name__}: {str(exc)[:90]}")
else:
    raise SystemExit("the principal-type owner was NOT caught")
fence_mut = L4.FENCE["u0002"].replace(L4.COMPANY, "anthropic")
assert "anthropic;" in fence_mut and L4.COMPANY not in fence_mut
try:
    parse_english(env, fence_mut)
except Exception as exc:
    caught("u0002.presupposition's mission belongs to the company", "the fence's owner changed to `anthropic` (not a thing)", "ledger_20261020.FENCE['u0002']", "the English parser against the probe vocabulary", f"{type(exc).__name__}: {str(exc)[:90]}")
else:
    raise SystemExit("the principal-type owner of u0002 was NOT caught")
# 3. the ledger step applies once: a second application is refused by its assertion on the old note
ledger = json.load(open(RUN / "units.json")) if (RUN / "units.json").exists() else None
prev = json.load(open(RUN / "prev/units.json"))
first = copy.deepcopy(prev)
assert L4.apply(first) == ["u0095.presupposition", "u0002.presupposition", "u0235.presupposition"]
try:
    L4.apply(first)
except AssertionError as exc:
    caught("the ledger step applies once to the previous run's ledger", "applied twice to its own output", "ledger_20261020.py", "ledger_20261020.apply's assertion on the old note", f"AssertionError: {str(exc)[:60]}")
else:
    raise SystemExit("a second application was NOT caught")
# 4. the document is the previous run's: one changed word in a scratch copy must break the byte comparison and change the rendering
raw = (RUN / "translation.ve.md").read_bytes()
prev_raw = (RUN / "prev/translation.ve.md").read_bytes()
assert raw == prev_raw
fence = b"```ve u0286.presupposition\nSome thing is unsolved.\n```\n"
assert raw.count(fence) == 1
scratch = RUN / "scratch-seeded"
scratch.mkdir(exist_ok=True)
mutant = scratch / "mutant.ve.md"
mutant.write_bytes(raw.replace(fence, b"```ve u0286.presupposition\nEvery thing is unsolved.\n```\n"))
assert mutant.read_bytes() != prev_raw
proc = subprocess.run([sys.executable, "-m", "ve", "document", "render", str(mutant.relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True)
assert proc.returncode == 0 and "Every thing is unsolved" in proc.stdout and "There is a thing that is unsolved" not in proc.stdout
out.append({"claim": "the translation is the previous run's, byte for byte, and u0286 says that there is an unsolved thing", "planted": "the fence of u0286 turned into “Every thing is unsolved.” in a scratch copy of translation.ve.md",
            "file": "scratch copy (deleted afterwards)", "failing_check": "finish_20261020T0600Z.py: `cmp` against prev/translation.ve.md (translation_byte_identical_to_previous_run) and block_after(render, 'Acknowledging open problems') == 'Checked reading: There is a thing that is unsolved.'",
            "failure": "the bytes differ and the rendering reads “Every thing is unsolved.”", "restored": "scratch copy deleted; the run's translation was not touched"})
print("failed as it should: mutated document")
mutant.unlink(); scratch.rmdir()
doc = {"needed_for_product_code": False,
       "why": "no product code (Lean, Python, Rust) was changed: this run adds files under usecases/ only (lean/.lake and rust/target in the worktree are ignored build products; `git diff ve-green-ap-1a -- ve lean rust` is empty). "
              "The claims below are the translator's; each was planted and caught.",
       "languages_changed": [], "translation_faults": out}
(RUN / "evidence/seeded-bugs.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print(len(out), "faults, all caught")
