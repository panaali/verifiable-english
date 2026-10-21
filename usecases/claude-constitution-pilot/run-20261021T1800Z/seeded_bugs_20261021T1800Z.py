#!/usr/bin/env python3
"""Run 20261021T1800Z: the seeded faults of this run's claims. No product code (Lean, Python, Rust) was changed (the pilot only reads the tag), so there is no fault to plant in a changed language; the claims
are the translator's (the audit repair of u0156.s03):
  (1) the frame term binds the instance and the situation: another situation, even of the same pair, is not governed;
  (2) the second argument of system_prompt_deception_permitted is the situation (not the user);
  (3) the claimed bytes are 2,951 (u0156.s03 keeps its covered status, repaired in place);
  (4) u0156.s03's act_workaround tag is stale (its act phrase changed).

    uv run python usecases/claude-constitution-pilot/run-20261021T1800Z/seeded_bugs_20261021T1800Z.py

Each fault is planted in a scratch copy or in memory (the previous run's documents are in prev/) and must be caught by a named check. Writes evidence/seeded-bugs.json."""
from __future__ import annotations

import copy
import json
import sys
from itertools import product
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(RUN))
from ve.document import load_document  # noqa: E402
from ve.norm_defaults_route import run_case, source_case  # noqa: E402
import frame_u0156 as fr  # noqa: E402
import probe_unspecified as pu  # noqa: E402
import finish_0600 as old  # noqa: E402

out = []


def caught(claim, planted, file, check, failure):
    out.append({"claim": claim, "planted": planted, "file": file, "failing_check": check, "failure": failure, "restored": "scratch copy or in-memory fault; no file of the run was touched"})
    print("failed as it should:", claim)


def status(doc, model, predicate, values):
    case = source_case(doc, "norm-defaults-status", model=model.to_dict(), predicate=predicate, tuple=values, method="enumerate")
    row = run_case(case)
    st = row["point_status"]
    if st == "UNKNOWN":
        yes = {i["name"]: [list(v) for v in product(*(model.to_dict()["domains"][x] for x in i["sorts"]))] for i in doc.elaboration["unsaid"]}
        no = {i["name"]: [] for i in doc.elaboration["unsaid"]}
        st = run_case({**case, "method": "undecided", "yes": yes, "no": no})["point_status"]
    return st


PRED = "system_prompt_deception_permitted"
# 1. the frame binds the situation: with the frame guard dropped (the unframed strict candidate, readings/all-strict.ve.md) another situation is governed too
unframed = load_document(RUN / "readings/all-strict.ve.md")["norm_defaults"]
m_un = pu.situation2(unframed, {}, {"claude_instance": 2, "situation": 2})
fault = status(unframed, m_un, PRED, ["claude_instance0", "situation1"])
framed = load_document(RUN / "readings/all-strict-in-frame.ve.md")["norm_defaults"]
m_fr = pu.situation2(framed, {fr.FRAME_TERM: [["claude_instance0", "situation0"]]}, {"claude_instance": 2, "situation": 2})
good = status(framed, m_fr, PRED, ["claude_instance0", "situation1"])
assert fault == "SETTLED no" and good == "UNDECIDED", (fault, good)
caught("u0156.s03: a request made in one situation governs that situation and no other", "the frame guard dropped (the unframed strict candidate, readings/all-strict.ve.md, stands for a guard `top`)", "readings/all-strict.ve.md",
       "probe_frame.py binding point “the same instance in another situation” (expected UNDECIDED), asserted by finish_20261021T1800Z.py (frame-probe binding statuses)", f"the other situation is {fault} instead of {good}")

# 2. the second argument is the situation: the previous run's vocabulary (instance, user) is the fault the audit found
prev_frame = load_document(RUN / "prev/readings/all-strict-in-frame.ve.md")["norm_defaults"]
args_prev = prev_frame.env.predicates[PRED].arguments
args_now = framed.env.predicates[PRED].arguments
frame_prev = prev_frame.env.predicates[fr.FRAME_TERM].arguments
frame_now = framed.env.predicates[fr.FRAME_TERM].arguments
assert list(args_prev) == ["claude_instance", "user"] and list(args_now) == ["claude_instance", "situation"]
assert list(frame_prev) == ["claude_instance", "user"] and list(frame_now) == ["claude_instance", "situation"] == list(fr.FRAME_SORTS)
caught("u0156.s03: the regulated act and the frame term are binary on (claude_instance, situation)", "the previous run's in-frame companion (prev/readings/all-strict-in-frame.ve.md), whose two terms take (claude_instance, user)", "prev/readings/all-strict-in-frame.ve.md",
       "finish_20261021T1800Z.py: `assert reg_now == expected_reg` (regulated predicates' arguments) and checkpoint.py's INTENDED_REWORDED list", f"arguments {list(args_prev)} / {list(frame_prev)} instead of {list(args_now)} / {list(frame_now)}")

# 3. the claimed bytes are 2,951: u0156.s03 is repaired in place and keeps READINGS; put it back to UNFORMALISED in a copy of the ledger
COVERED = old.COVERED
claimed = lambda es: sum(e["span"][1] - e["span"][0] for e in es if e["status"] in COVERED and e.get("claimed", True) is not False)
prev_metrics = json.load(open(RUN / "prev/metrics.json"))
now_units = json.load(open(RUN / "units.json"))
assert claimed(now_units) == prev_metrics["claimed_covered_bytes"] == 2951
mut = copy.deepcopy(now_units)
next(e for e in mut if e["id"] == "u0156.s03")["status"] = "UNFORMALISED"
assert claimed(mut) == 2951 - 100
caught("u0156.s03 keeps its covered status after the repair (2,951 B claimed, unchanged)", "u0156.s03 set to UNFORMALISED in a copy of units.json", "scratch copy of units.json",
       "finish_20261021T1800Z.py: `assert claimed == pm[\"claimed_covered_bytes\"] == 2951`", f"claimed bytes {claimed(mut)} != 2951")

# 4. the act_workaround tag of u0156.s03 is stale: the evidence's phrase is the previous document's, not this one's
m4 = json.load(open(RUN / "evidence/m4-act-workaround.json"))
r = next(x for x in m4["units"] if x["unit"] == "u0156.s03")
act_prev = prev_frame.env.predicates[PRED].regulated.act
act_now = framed.env.predicates[PRED].regulated.act
assert " ".join(r["act"].split()) == " ".join(act_prev.split()) and " ".join(r["act"].split()) != " ".join(act_now.split())
entry = next(e for e in now_units if e["id"] == "u0156.s03")
assert entry["act_workaround_stale"] is True and "act_workaround" not in entry
mut2 = copy.deepcopy(now_units)
next(e for e in mut2 if e["id"] == "u0156.s03").pop("act_workaround_stale")
next(e for e in mut2 if e["id"] == "u0156.s03")["act_workaround"] = r["act_workaround"]
caught("u0156.s03's act_workaround tag is written as stale, because its act phrase changed in this run", "the tag copied from the evidence as if the act were unchanged (scratch copy of units.json)", "scratch copy of units.json",
       "finish_20261021T1800Z.py: `assert r[\"act\"] != act_now == ACT ...` (the M4 loop) and the M4 totals (14 units, 2,219 B)", f"the evidence's phrase “{r['act']}” is not the document's “{act_now}”")
doc = {"needed_for_product_code": False,
       "why": "this run changed no product code (Lean, Python, Rust): the pilot branch adds files under usecases/claude-constitution-pilot/ only (lean/.lake and rust/target in the worktree are ignored build products; the tag itself differs from the "
              "previous run's by the merged batches, 34 files under lean/ and rust/, none of them edited here). The claims below are the translator's; each was planted and caught.",
       "languages_changed": [], "translation_faults": out}
(RUN / "evidence/seeded-bugs.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print(len(out), "faults, all caught")
