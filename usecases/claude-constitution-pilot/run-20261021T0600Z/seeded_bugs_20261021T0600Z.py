#!/usr/bin/env python3
"""Run 20261021T0600Z: the seeded faults of this run's claims. No product code (Lean, Python, Rust) was changed (the pilot only reads the tag), so there is no fault to plant in a changed language; the claims
are the translator's (the audit repairs):
  (1) u0168.s01: the guard binds the acting instance;
  (2) u0156.s03: the frame term binds the instance and the user;
  (3) u0036.s05 / u0263.s04.p2 / u0013.presupposition are not claimed (the claimed bytes are 2,951);
  (4) the rendering of the document no longer contains the sentence that words a defeasible candidate's silence as “is not required to”.

    uv run python usecases/claude-constitution-pilot/run-20261021T0600Z/seeded_bugs_20261021T0600Z.py

Each fault is planted in a scratch copy or in memory (the previous run's documents are in prev/) and must be caught by a named check. Writes evidence/seeded-bugs.json."""
from __future__ import annotations

import copy
import json
import subprocess
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


# 1. u0168.s01 binds the instance: the previous run's document (guard on the situation only) makes another instance firm too
prev_doc = load_document(RUN / "prev/readings/all-strict.ve.md")["norm_defaults"]
model = pu.situation2(prev_doc, {"seemingly_compelling_argument_to_cross_line": [["situation0"]]}, {"claude_instance": 2})
fault = status(prev_doc, model, "firmness_required", ["claude_instance1", "situation0"])
now_doc = load_document(RUN / "readings/all-strict.ve.md")["norm_defaults"]
model2 = pu.situation2(now_doc, {"seemingly_compelling_argument_to_cross_line": [["claude_instance0", "situation0"]]}, {"claude_instance": 2})
good = status(now_doc, model2, "firmness_required", ["claude_instance1", "situation0"])
assert fault == "SETTLED yes" and good == "UNDECIDED", (fault, good)
caught("u0168.s01: only an instance that faces the seemingly compelling argument must remain firm", "the guard on the situation alone (the previous run's document prev/readings/all-strict.ve.md)", "prev/readings/all-strict.ve.md",
       "probe_unspecified.py binding point “u0168.s01: another instance of Claude in the same situation, which does not face it” (expected UNDECIDED), asserted by finish_20261021T0600Z.py apply_repairs", f"another instance is {fault} instead of {good}")

# 2. u0156.s03: the frame binds the user: the previous frame term (instance only) forbids deceiving every user
prev_frame = load_document(RUN / "prev/readings/all-strict-in-frame.ve.md")["norm_defaults"]
m_prev = pu.situation2(prev_frame, {fr.FRAME_TERM: [["claude_instance0"]]}, {"claude_instance": 2, "user": 2})
fault = status(prev_frame, m_prev, "system_prompt_deception_permitted", ["claude_instance0", "user1"])
frame_doc = load_document(RUN / "readings/all-strict-in-frame.ve.md")["norm_defaults"]
m_now = pu.situation2(frame_doc, {fr.FRAME_TERM: [["claude_instance0", "user0"]]}, {"claude_instance": 2, "user": 2})
good = status(frame_doc, m_now, "system_prompt_deception_permitted", ["claude_instance0", "user1"])
assert fault == "SETTLED no" and good == "UNDECIDED", (fault, good)
caught("u0156.s03: a request made toward one user governs that user and no other", "the frame term on the instance alone (the previous run's prev/readings/all-strict-in-frame.ve.md)", "prev/readings/all-strict-in-frame.ve.md",
       "probe_frame.py binding point “the same instance toward another user” (expected UNDECIDED), asserted by finish_20261021T0600Z.py (frame-probe binding statuses)", f"the other user is {fault} instead of {good}")

# 3. the claimed bytes are 2,951: put u0036.s05 (or u0013.presupposition) back to its covered status in a copy of the previous ledger
prev_units = json.load(open(RUN / "prev/units.json"))
prev_metrics = json.load(open(RUN / "prev/metrics.json"))
COVERED = old.COVERED
claimed = lambda es: sum(e["span"][1] - e["span"][0] for e in es if e["status"] in COVERED and e.get("claimed", True) is not False)
now_units = json.load(open(RUN / "units.json"))
assert claimed(prev_units) == prev_metrics["claimed_covered_bytes"] == 3158 and claimed(now_units) == 2951
mut = copy.deepcopy(now_units)
victim = next(e for e in mut if e["id"] == "u0036.s05")
victim["status"] = "READINGS"
assert claimed(mut) == 2951 + 68
caught("u0036.s05, u0263.s04.p2 and u0013.presupposition are not claimed (2,951 B claimed)", "u0036.s05 set back to READINGS in a copy of units.json", "scratch copy of units.json",
       "finish_20261021T0600Z.py: `assert claimed == pm[\"claimed_covered_bytes\"] - sum(lost_bytes.values()) == 2951`", f"claimed bytes {claimed(mut)} != 2951")

# 4. the rendering no longer says “is not required to” for a defeasible candidate's silence: the previous document does
proc = subprocess.run([sys.executable, "-m", "ve", "document", "render", str((RUN / "prev/translation.ve.md").relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True)
assert proc.returncode == 0
assert proc.stdout.count(", c is not required to.") == 2
now_render = (RUN / "rendered-raw.md").read_text()
assert ", c is not required to." not in now_render
caught("the document's rendering has no sentence that turns a defeasible candidate's silence into “c is not required to”", "the previous document (prev/translation.ve.md), which holds the reading sets of u0036.s05 and u0263.s04.p2", "prev/translation.ve.md",
       "`ve document render` output searched for “, c is not required to.” (finish_20261021T0600Z.py asserts the two sentences carry other.silence-display)", "2 occurrences in the previous document's rendering, 0 in this run's")
doc = {"needed_for_product_code": False,
       "why": "no product code (Lean, Python, Rust) was changed: this run adds files under usecases/ only (lean/.lake and rust/target in the worktree are ignored build products; `git diff ve-green-sc-1ac -- ve lean rust` is empty). "
              "The claims below are the translator's; each was planted and caught.",
       "languages_changed": [], "translation_faults": out}
(RUN / "evidence/seeded-bugs.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print(len(out), "faults, all caught")
