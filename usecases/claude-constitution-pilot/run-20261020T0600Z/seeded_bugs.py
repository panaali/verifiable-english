#!/usr/bin/env python3
"""Run 20261018T1800Z: the cheap seeded faults of this run's pilot scripts (no product code in Lean, Python or Rust was changed; the claims below are the translator's).

    uv run python usecases/claude-constitution-pilot/run-20261018T1800Z/seeded_bugs.py

Each fault is planted in memory (or in a scratch copy), the check that guards the claim is run, and it must fail; the real files are never touched. Writes evidence/seeded/seeded-cheap.json.
The two faults that need `nd.py all` (QT-0p's closure, PS-0p's existential) were planted in scratch directories and are recorded by hand in evidence/seeded-bugs.json.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))
import apply_plans as A  # noqa: E402
import finish_20261018T1800Z as F  # noqa: E402
import ledger_1800 as L  # noqa: E402

out = []


def expect_failure(claim, planted, file, check, fn):
    try:
        fn()
    except AssertionError as exc:
        out.append({"claim": claim, "planted": planted, "file": file, "failing_check": check, "failure": f"AssertionError: {str(exc)[:200]}", "restored": "in-memory fault; the file was not touched"})
        print("failed as it should:", claim)
        return
    raise SystemExit(f"the planted fault was NOT caught: {claim}")


# 1. QT-0p: the spans of the two parts of u0043.s02 are checked against the pinned source
meta, _ = A.read(RUN / "prev/translation-without-content.ve.md")
def qt_span():
    saved = dict(A.QT_PARTS)
    A.QT_PARTS["u0043.s02.p1"] = [23587, 23601]   # 14 bytes: “At the moment,” without its space
    try:
        A.qt0p(copy.deepcopy(meta))
    finally:
        A.QT_PARTS.update(saved)
expect_failure("the hedge “At the moment, ” is the 15 bytes 23587-23602 of the pinned source (QT-0p step 4)", "p1 given as 14 bytes", "apply_plans.py QT_PARTS", "apply_plans.qt0p's partition assertion", qt_span)

# 2. QT-0p: a unit whose span changed since the plan's measurement is refused
def qt_unit_span():
    m = copy.deepcopy(meta)
    for u in m["units"]:
        if u["id"] == "u0043.s01":
            u["span"] = [u["span"][0], u["span"][1] - 1]
    A.qt0p(m)
expect_failure("the three units' spans and kinds are unchanged since the plan (QT-0p step 1)", "u0043.s01 one byte short", "translation-without-content.ve.md", "apply_plans.qt0p's step-1 assertion", qt_unit_span)

# 3. PS-0p step 4: the lexical false positives of the census (remainder, discoveries, returned to the orchestrator) are dropped, exactly three
census = json.load(open(RUN / "evidence/ps0p/ledger-triggers-constitution.json"))
source = (RUN.parent / "source/claude-constitution.md").read_bytes()
def filter_off():
    saved = set(L.FALSE_FULL_WORDS)
    L.FALSE_FULL_WORDS.clear()
    try:
        _, dropped, _ = L.triggers_for_ledger(json.load(open(RUN / "prev/units.json")), census, source)
        assert [(d["unit"], d["words"]) for d in dropped] == F.EXPECTED_DROPPED, dropped
    finally:
        L.FALSE_FULL_WORDS.update(saved)
expect_failure("the census's false positives “discoveries” and “returned to the orchestrator” are dropped (PS-0p step 4)", "the false-word set emptied", "ledger_1800.py FALSE_FULL_WORDS",
               "finish_20261018T1800Z.py: assert dropped == EXPECTED_DROPPED", filter_off)

# 4. PS-0p step 1: no title keeps its presupposed_claim
def claim_left():
    led = json.load(open(RUN / "prev/units.json"))
    led = L.qt0p(led, {"u0042.presupposition": "x", "u0043.s02.p2": "y"})
    L.ps0p_notes(led)
    by = {e["id"]: e for e in led}
    by["u0207.presupposition"]["presupposed_claim"] = "Broad safety is desired for Claude."
    F.assert_no_traces(by)
expect_failure("a title records no `presupposed_claim` (PS-0p step 1; REMOVE EVERY TRACE)", "u0207's claim put back", "units.json (in memory)", "finish_20261018T1800Z.py: assert_no_traces", claim_left)

# 5. JT-0p: the order of decision (an exception_to_ placeholder is `exception`; “knowingly” is `attitude`)
def wrong_class():
    classes = {"exception_to_asking_for_clarification": "judgment"}
    F.check_rules(classes, ["exception_to_asking_for_clarification"])
expect_failure("an exception_to_… placeholder is class `exception` (JT-0p rule 2)", "its class set to judgment", "finish_20261018T1800Z.py JT classes", "finish_20261018T1800Z.py: check_rules", wrong_class)
def wrong_attitude():
    F.check_rules({"knowingly_engages_4": "classification"}, ["knowingly_engages_4"])
expect_failure("“knowingly engages” is class `attitude` (JT-0p rule 1)", "knowingly_engages_4 set to classification", "finish_20261018T1800Z.py JT classes", "finish_20261018T1800Z.py: check_rules", wrong_attitude)

# 6. PS-0p step 4/3: u0245's wording is one the lint admits without changing an existing wording (checkpoint)
import checkpoint  # noqa: E402,F401
(RUN / "evidence/seeded").mkdir(exist_ok=True)
(RUN / "evidence/seeded/seeded-cheap.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(len(out), "faults caught")
