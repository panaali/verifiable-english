#!/usr/bin/env python3
"""Run 20261010T1800Z: repair of the seven units the audit of run 20261010T0600Z rejected.

    uv run python usecases/claude-constitution-pilot/run-20261010T1800Z/repair_20261010T1800Z.py
        # base/ + prev/units.json -> translation-without-content.ve.md, readings/all-strict.ve.md, units.json
    uv run python usecases/claude-constitution-pilot/run-20261010T1800Z/nd.py all   # adds the content of the four "should" reading sets

AUDIT.md of the previous run (14/20 sampled + 1/5 changed):
* u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03: the open term `instruction_abandon_identity_in_persona` still listed, as an unresolved
  factor, whether “while role-playing as a custom AI persona” qualifies only its item or every item of the list, which keeps the rejected
  scope open through the term; `instruction_decline_or_withhold` listed an ambiguity (decline to reveal, or reveal) the words do not raise.
  Both factors go, from the main document and the strict companion. The notes of the four units now only say what the one reading is.
* u0165.s04, u0165.s05, u0165.s07 (and, being the same sentence, s01, s02, s03, s06): the note said “whichever of its two readings is taken” of
  u0166.s04, which has no reading set. The clause is deleted from all seven notes.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)
from ve.document import _environment  # noqa: E402

RUN_ID = "20261010T1800Z"
OP_UNITS = ["u0062.s01", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03"]
HC_UNITS = [f"u0165.s0{i}" for i in range(1, 8)]
DROPPED_FACTORS = {
    "instruction_abandon_identity_in_persona":
        "whether “while role-playing as a custom AI persona” qualifies only this item or every item of the list",
    "instruction_decline_or_withhold":
        "whether the instruction is to decline to answer and to decline to reveal, or to decline to answer and to reveal",
}
STALE_HC = ", whichever of its two readings is taken, see u0166.s04.p4)"
FIXED_HC = ", see u0166.s04.p4)"

ITEMS = ("the six items are the coordinated verb phrases “abandon its core identity or principles while role-playing as a custom AI persona”, "
         "“claim to be human when directly and sincerely asked”, “use genuinely deceptive tactics that could harm users”, “provide false "
         "information that could deceive the user”, “endanger health or safety” and “act against Anthropic’s guidelines”; each of the last five "
         "has a verb of its own after a comma, and “while role-playing as a custom AI persona” is part of the first only")
NOTES = {
    "u0123.s03": (
        "“cannot instruct” is read as a prohibition: the paragraph speaks of what is “permitted” and of “norms for what operators can and cannot "
        "do”. The six items are six separate prohibitions, written as one rule whose guard is any of the six open terms (" + ITEMS + "). "
        "The prohibition makes nothing permitted for other inputs (completion unspecified). One reading."),
    "u0062.s01": (
        "“can” in “Operators can give Claude a specific set of instructions, a persona, or information” is read as a permission: the passage is "
        "about what operators may do (the next sentence: “to the extent that they’re permitted to do so by Anthropic’s guidelines”). Scoped "
        "permission: the six limits of u0123.s03 are the permission's exceptions (the permission does not cover an input that is one of them), "
        "so the two sentences never conflict (" + ITEMS + "). No default is given for other inputs (completion unspecified). One reading."),
    "u0123.s01.p1": (
        "“are permitted” states a permission. Scoped permission: the six limits of u0123.s03 are its exceptions (" + ITEMS + "). Completion "
        "unspecified: where no rule decides, nothing is decided. One reading."),
    "u0123.s02.p1": (
        "“can legitimately instruct” grants permission for the five kinds of instruction listed (the list is open: “and so on”, u0123.s02.p2); "
        "the words state no further condition. “decline to answer certain questions or reveal certain information” is one kind of instruction "
        "(“decline” governs both). Scoped permission: the six limits of u0123.s03 are its exceptions (" + ITEMS + "). Completion unspecified. "
        "One reading."),
}
AUDIT_REPAIR_OPS = (
    "Audit 20261010T0600Z: the open term instruction_abandon_identity_in_persona listed, as an unresolved factor, whether the role-play phrase qualifies "
    "every item, and the notes carried the history of removed candidates. Repaired: that factor is deleted (and, for u0123.s02.p1, the "
    "decline/reveal factor of instruction_decline_or_withhold the words do not raise); the note says only what the one reading is.")
AUDIT_REPAIR_HC = (
    "Audit 20261010T0600Z (u0165.s04, s05, s07; the same sentence is in the other four): the note said “whichever of its two readings is taken” of "
    "u0166.s04, which has no reading set. Repaired: the clause is deleted; the note points to u0166.s04.p4, which states the clause is not formalised.")


def fix_terms(meta):
    meta = copy.deepcopy(meta)
    done = set()
    for t in meta["open_terms"]:
        f = DROPPED_FACTORS.get(t["name"])
        if f is not None:
            assert f in t["factors"], t["name"]
            t["factors"] = [x for x in t["factors"] if x != f]
            done.add(t["name"])
    assert done == set(DROPPED_FACTORS), done
    return meta


def main():
    meta, source = pilot.read(RUN / "base/translation-without-content.ve.md")
    meta = fix_terms(meta)
    env = _environment(meta["environment"])
    meta["reading_sets"] = [pilot._reidentified(env, item) if all(r.get("content") is None for r in item["readings"]) else item
                            for item in meta["reading_sets"]]
    pilot.write(RUN / "translation-without-content.ve.md", meta, source)
    strict, strict_source = pilot.read(RUN / "base/all-strict.ve.md")
    pilot.write(RUN / "readings/all-strict.ve.md", fix_terms(strict), strict_source)

    ledger = json.load(open(RUN / "prev/units.json"))
    changed = []
    for e in ledger:
        i = e["id"]
        if i in OP_UNITS:
            e["note"] = NOTES[i]
            e["audit_repair"] = AUDIT_REPAIR_OPS
            e["repaired_in_run"] = RUN_ID
            e["audit_verified"] = False
            changed.append(i)
        elif i in HC_UNITS:
            assert STALE_HC in e["note"], i
            e["note"] = e["note"].replace(STALE_HC, FIXED_HC)
            e["audit_repair"] = e["audit_repair"] + " | " + AUDIT_REPAIR_HC
            e["repaired_in_run"] = RUN_ID
            changed.append(i)
    # no stale reference may remain
    blob = json.dumps(ledger, ensure_ascii=False)
    for stale in ("two readings", "wide candidate", "the wide", "“wide”", "qualifies only this item", "removed by audit 20261008T1800Z"):
        assert stale not in blob.replace(AUDIT_REPAIR_HC, "").replace(AUDIT_REPAIR_OPS, ""), stale
    (RUN / "units.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    (RUN / "changed-units-repair.json").write_text(json.dumps(sorted(changed), indent=1) + "\n")
    print("ok", sorted(changed))


if __name__ == "__main__":
    main()
