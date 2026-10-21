#!/usr/bin/env python3
"""Run 20261019T1800Z: the ledger changes of this run, as a function on the carried ledger (a list of entries, one per unit).

* FEATURE UPGRADE (ps-6r merged: the idioms “{0} is a core value / guideline / mission / nature of {1}”): u0013.presupposition (“Claude’s core values”) is CHECKED (+24 B). The other three headings the
  idioms make expressible (u0095, u0002, u0235) parse and check alone, but together with u0013 the whole-document premise check is UNKNOWN, so they stay UNFORMALISED with the new reason.
* AUDIT REPAIR (audit of 20261019T0600Z): u0032.presupposition UNFAITHFUL (its English drops “genuine” and “constitutes”): back to UNFORMALISED, 38 B not claimed.
* REMOVE EVERY TRACE: the note “relational-noun wording not admitted” (u0013, u0095, u0002, u0235) and “waits for PS-6r” (u0083) are replaced; the open term `genuine_helpfulness` is no longer a declared term.

Nothing here touches a document; `repair_20261019T1800Z.py` does that.
"""
from __future__ import annotations

import ledger_1800 as L

FENCE = {"u0013": "Some thing is a core value of claude.",
         "u0095": "Some thing is a guideline of anthropic.",
         "u0002": ("There is a first thing such that both of the following hold:\n  (a) the first thing is a mission of anthropic;\n"
                   "  (b) for every second thing that is a mission of anthropic, the second thing is the same as the first thing."),
         "u0235": "Some thing is a nature of claude."}

NOTE_U0013 = ("Feature upgrade (ps-6r merged: the idiom “{0} is a core value of {1}” is admitted by the English lint, evidence/ps6r/wording-lint.json). The heading “Claude’s core values” takes for "
              "granted that Claude has core values (a possessive). Predicate `core_value_of` (two things) worded “{0} is a core value of {1}”, fence “Some thing is a core value of claude.” "
              "(`∃x core_value_of(x, claude)`), CHECKED, +24 B: the existence of a core value of Claude, nothing more (not how many, not which). The lower-case “claude” is how the document's English "
              "writes a constant inside a sentence. It is the one of the four ps-6r headings that the whole-document premise check admits (evidence/ps6r/premise-variants.json); the premise check stays "
              "`model`. Claimed only if the audit accepts it.")
_WHY_NOT = ("with its fence the unit parses and checks alone (evidence/ps6r/premise-variants.json), but together with u0013, u0286 and u0245 the whole-document premise check is UNKNOWN: the Rust "
            "enumerator tries relation subsets by size, then in the order of the used atoms (sorted by predicate name), within 10,000 models; each existential needs one true atom, so a fourth true atom is "
            "out of its budget, and only one extra existential fits (u0013, whose predicate sorts first among the four). The DRI has not accepted UNKNOWN for the constitution's premise check, so the "
            "unit stays UNFORMALISED")
NOTE_U0095 = ("Expressible since ps-6r (“{0} is a guideline of {1}”; the second argument has the sort of the constant `anthropic`, so Anthropic is one constant), fence “" + FENCE["u0095"] +
              "” (`∃x guideline_of(x, anthropic)`), but not claimed: " + _WHY_NOT + ".")
NOTE_U0002 = ("Expressible since ps-6r (“{0} is a mission of {1}”; the second argument has the sort of the constant `anthropic`), as the enumerated uniqueness form the definite “the mission of” calls for "
              "(exactly one: a first thing is a mission of anthropic and every second thing that is a mission of anthropic is the same as the first), but not claimed: " + _WHY_NOT + ". The recorded "
              "claim and the trigger's `pre` were made equal in this run (“exactly one mission”; the claim said “a mission”).")
NOTE_U0235 = ("Expressible since ps-6r (“{0} is a nature of {1}”), fence “" + FENCE["u0235"] + "” (`∃x nature_of(x, claude)`), but not claimed: " + _WHY_NOT + ".")
NOTE_U0083 = ("class B item, not offered: ps-6r (merged) admits “{0} is a core value of {1}” only; the heading says “values other than helpfulness”, not “core values” and not of anyone, so a claim with "
              "that wording would add “core” and an owner the heading does not state (the loss that made the audit reject u0032), and no wording for “value” alone is admitted")
NOTE_U0032 = ("PS-0p step 5, class B: offered in 20261019T0600Z as OPEN (`∃x genuine_helpfulness(x)`, “Some thing is helpful.”) and rejected by the audit of that run (UNFAITHFUL: the English drops "
              "“genuine” and “constitutes”, so it says something different). Reverted to UNFORMALISED (38 B not claimed); the predicate, its open term and its fence are removed with every trace (`open_terms` on this entry is a ledger-only pointer, as on the other UNFORMALISED entries that name the term). ps-6r "
              "adds only four relational nouns (core value, guideline, mission, nature): there is still no admitted wording for “constitutes genuine helpfulness” (TEMPLATE_SHAPE, evidence/ps0p/wording-lint.json)")
NOTE_NOT_ADMITTED_STALE = L.NOTE_RELATIONAL


def apply(ledger, english):
    """`ledger` is edited in place. Returns the ids of the units this run changed, by role."""
    by = {e["id"]: e for e in ledger}
    out = {"feature_upgrade": [], "audit_repair": [], "ledger_note": []}

    # --- u0013: CHECKED (feature upgrade)
    e = by["u0013.presupposition"]
    assert e["status"] == "UNFORMALISED" and e["note"] == NOTE_NOT_ADMITTED_STALE
    prev_claim, prev_mf = e["presupposed_claim"], e["missing_feature"]
    for k in ("presupposed_claim", "missing_feature", "plan_repair"):
        e.pop(k, None)
    keep = [b for b in e.get("other_blockers", []) if b != "other:presupposition"]
    e.pop("other_blockers", None)
    if keep:
        e["other_blockers"] = keep
    e.update({"status": "CHECKED", "kind": "asserted", "support": "assumption", "claimed": True, "note": NOTE_U0013, "checked_english": english["u0013.presupposition"],
              "carrier": "assumed", "trigger": "possessive", "trigger_words": "Claude’s", "previous_status": "UNFORMALISED", "previous_missing_feature": prev_mf,
              "previous_presupposed_claim": prev_claim, "offered_to_audit": True,
              "feature_upgrade": {"feature": "ps-6r", "what": "the idiom “{0} is a core value of {1}” (ve/english_vocabulary.py IDIOMS[2]) lets the heading's presupposition be written in VE English",
                                  "bytes": e["span"][1] - e["span"][0]}})
    out["feature_upgrade"].append("u0013.presupposition")

    # --- u0095, u0002, u0235: expressible, not claimed (premise check)
    for uid, note in (("u0095.presupposition", NOTE_U0095), ("u0002.presupposition", NOTE_U0002), ("u0235.presupposition", NOTE_U0235)):
        e = by[uid]
        assert e["status"] == "UNFORMALISED" and e["note"] == NOTE_NOT_ADMITTED_STALE, uid
        e["previous_missing_feature"] = e["missing_feature"]
        e["missing_feature"] = "other:premise-check-budget"
        e["note"] = note
        e["expressible_with"] = {"feature": "ps-6r", "fence": FENCE[uid.split(".")[0]], "blocked_by": "the whole-document premise check is UNKNOWN with it (evidence/ps6r/premise-variants.json)"}
        e.pop("plan_repair", None)
        out["ledger_note"].append(uid)
    e = by["u0002.presupposition"]
    e["previous_presupposed_claim"] = e["presupposed_claim"]
    e["presupposed_claim"] = "Anthropic has exactly one mission."   # equal to the trigger's `pre` (the claim said “a mission”)

    # --- u0083: the stale “waits for PS-6r”
    e = by["u0083.presupposition"]
    assert "waits for PS-6r" in e["note"]
    e["note"] = NOTE_U0083
    out["ledger_note"].append("u0083.presupposition")

    # --- u0032: audit repair
    e = by["u0032.presupposition"]
    assert e["status"] == "OPEN" and e["open_terms"] == ["genuine_helpfulness"]
    for k in ("kind", "support", "claimed", "checked_english", "carrier", "trigger", "trigger_words", "previous_status", "previous_missing_feature", "previous_presupposed_claim",
              "offered_to_audit", "plan_repair", "other_blockers"):
        e.pop(k, None)
    e["open_terms"] = ["genuine_helpfulness"]   # a ledger-only pointer again, as before 20261019T0600Z (the phase-1 instrument lists it): the document declares no such term
    e.update({"status": "UNFORMALISED", "missing_feature": "other:discourse", "presupposed_claim": "Something constitutes genuine helpfulness.", "note": NOTE_U0032,
              "audit_repair": {"audit": "20261019T0600Z", "verdict": "UNFAITHFUL",
                               "cause": "the English “Some thing is helpful.” dropped “genuine” and “constitutes”, so it was weaker than the heading's presupposition",
                               "repair": "reverted to UNFORMALISED (other.discourse); the predicate genuine_helpfulness, its open term and its fence are removed; 38 B not claimed"}})
    out["audit_repair"].append("u0032.presupposition")
    return out
