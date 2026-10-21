#!/usr/bin/env python3
"""Run 20261020T0600Z: the ledger changes of this run, as a function on the carried ledger.

No feature merged since ve-green-et-3b lets a document say something new (FEATURE-REVIEW.md), so no unit changes status or content. The only changes are ledger notes, from the audit of
20261019T1800Z (AUDIT-20261019T1800Z-received.md, "Faults to fix before claiming (no verdict change)"), all on units that are not claimed:

* u0235 (“Claude’s nature”): a singular possessive takes for granted existence AND uniqueness (as u0002's “the mission of”); the recorded claim and the fence gave existence only. Claim, trigger `pre` and the
  expressible fence are now the enumerated uniqueness form.
* u0095, u0002: the fences' owner was `anthropic`, the constant of the sort principal_type (“Anthropic, as a type of principal”); the guidelines and the mission belong to the company. The fences now name a
  separate constant of the sort thing for the company.
* u0013 (claimed, unchanged): “of claude” in lower case is not repairable by a wording: a constant must be a lower-case ASCII identifier (evidence/owner-probe.json). Recorded as a finding only, so the entry
  (and its audit-verified status) is not touched.

All three corrected fences are measured by owner_probe.py (parse, render, round trip); none is added to the document, so the document, the premise check and every probe are those of the previous run.
"""
from __future__ import annotations

import ledger_1800z as L3

COMPANY = "anthropiccompany"
FENCE = {
    "u0095": f"Some thing is a guideline of {COMPANY}.",
    "u0002": ("There is a first thing such that both of the following hold:\n  (a) the first thing is a mission of " + COMPANY + ";\n"
              "  (b) for every second thing that is a mission of " + COMPANY + ", the second thing is the same as the first thing."),
    "u0235": ("There is a first thing such that both of the following hold:\n  (a) the first thing is a nature of claude;\n"
              "  (b) for every second thing that is a nature of claude, the second thing is the same as the first thing."),
}
CLAIM_U0235 = "Claude has exactly one nature."
AUDIT = "20261019T1800Z"
_WHY_NOT = ("it is expressible alone (evidence/owner-probe.json: the fence parses, renders and round-trips) but not claimed: together with u0013, u0286 and u0245 the whole-document premise check is UNKNOWN "
            "(the Rust enumerator's 10,000-model budget, evidence/ps6r/premise-variants.json), and the DRI has not accepted UNKNOWN for the constitution's premise check")
NOTE_U0095 = ("Expressible since ps-6r (“{0} is a guideline of {1}”). Audit repair of the owner (audit " + AUDIT + "): the guidelines belong to the company, not to `anthropic`, which the document declares as "
              "“Anthropic, as a type of principal” (sort principal_type). The fence now names a separate constant `" + COMPANY + "` of the sort thing: “" + FENCE["u0095"] + "” (the predicate would take two "
              "things; `∃x guideline_of(x, " + COMPANY + ")`). Existence only, as the plural “guidelines” takes for granted. Not claimed: " + _WHY_NOT + ".")
NOTE_U0002 = ("Expressible since ps-6r (“{0} is a mission of {1}”), as the enumerated uniqueness form the definite “the mission of” calls for (exactly one: a first thing is a mission of the owner and every second "
              "thing that is a mission of the owner is the same as the first). Audit repair of the owner (audit " + AUDIT + "): the mission belongs to the company, not to `anthropic` (a type of principal); the fence "
              "now names the separate constant `" + COMPANY + "` of the sort thing. Not claimed: " + _WHY_NOT + ".")
NOTE_U0235 = ("Expressible since ps-6r (“{0} is a nature of {1}”). Audit repair (audit " + AUDIT + "): “Claude’s nature” is a singular possessive, so it takes for granted existence and uniqueness (as u0002's "
              "definite); the earlier claim and fence gave existence only. The recorded claim, the trigger's `pre` and the fence are now the uniqueness form: “" + FENCE["u0235"].replace("\n", " ") + "” "
              "(`∃x (nature_of(x, claude) ∧ ∀y (nature_of(y, claude) → y = x))`). Not claimed: " + _WHY_NOT + ".")


def apply(ledger):
    """`ledger` is edited in place. Returns the ids of the units this run changed (ledger notes only; no status or content changes)."""
    by = {e["id"]: e for e in ledger}
    changed = []
    for uid, note in (("u0095.presupposition", NOTE_U0095), ("u0002.presupposition", NOTE_U0002), ("u0235.presupposition", NOTE_U0235)):
        e = by[uid]
        assert e["status"] == "UNFORMALISED" and e["missing_feature"] == "other:premise-check-budget", uid
        assert e["note"] in (L3.NOTE_U0095, L3.NOTE_U0002, L3.NOTE_U0235), uid
        e["note"] = note
        e["expressible_with"] = {**e["expressible_with"], "fence": FENCE[uid.split(".")[0]], "previous_fence": e["expressible_with"]["fence"],
                                 "owner": ("the company, constant `" + COMPANY + "` (sort thing)" if uid != "u0235.presupposition" else "Claude, constant `claude` (sort thing)")}
        if "audit_repair" in e:
            e["earlier_audit_repair"] = e["audit_repair"]
        e["audit_repair"] = {"audit": AUDIT, "verdict": "fault, no verdict change",
                             "cause": ("the fence's owner `anthropic` is the type of principal; the " + ("guidelines" if uid.startswith("u0095") else "mission") + " belong to the company"
                                       if uid != "u0235.presupposition" else "a singular possessive takes for granted existence and uniqueness; the claim and fence gave existence only"),
                             "repair": "ledger note, claim and fence corrected; the unit stays UNFORMALISED (other:premise-check-budget), 0 B claimed"}
        changed.append(uid)
    e = by["u0235.presupposition"]
    e["previous_presupposed_claim"] = e["presupposed_claim"]
    e["presupposed_claim"] = CLAIM_U0235
    assert len(e["presupposition_triggers"]) == 1
    return changed
