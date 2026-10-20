#!/usr/bin/env python3
"""Run 20261019T0600Z: the ledger changes of this run, as a function on the carried ledger (a list of entries, one per unit).

* audit repair of 20261018T1800Z (u0042.presupposition UNFAITHFUL: its English was the quoted fallback): u0042.presupposition and u0043.s02.p2 are re-expressed with the sort noun
  “principal type of Claude” (repair_20261019T0600Z.py); both stay CHECKED, the English is new.
* the audit's small faults: triggers for u0277 and u0294 (definite), u0235's claim no longer exceeds its `pre`.
* PS-0p steps 3 and 5 again, now that the premise check stays `model`: u0286 CHECKED (+29 B), u0032 OPEN (+38 B), both offered to the audit.

Nothing here touches a document; `apply_plans.py` and `repair_20261019T0600Z.py` do that.
"""
from __future__ import annotations

import copy

import ledger_1800 as L

NOTE_U0042 = ("QT-0p (quantities plan, DRI QT2; content docs/research/evidence/quantities/qt0p/constitution-u0042-u0043.ve.md on research/quantities-p1), re-expressed in this run as the repair of the "
              "audit of 20261018T1800Z (UNFAITHFUL: the English was the quoted fallback). The heading's presupposition is that Claude has exactly three types of principals and nothing more: three "
              "pairwise different principal types that are Claude's, and every one of Claude's types is among them. It names none of them (u0043.s02 does). Claude's types are now a sort, "
              "`principal_type`, with the noun “principal type of Claude”, so the English says “principal type of Claude” and no predicate or quoted name is needed. The closure is over that sort, which "
              "holds Claude's types only, never over all principal types, which the source does not state. The plan's content wording (a predicate) is replaced; the meaning is the plan's.")
NOTE_P2 = ("QT-0p, re-expressed in this run (same cause as u0042.presupposition). Anthropic, operators and users are pairwise different, and every principal type of Claude is one of them. The three "
           "constants are of the sort `principal_type` (“principal type of Claude”); `operators` and `users` are constants, not the sorts `operator` and `user`, and the rendered English parses back "
           "to the same formula (checked in this run's round trip). That each is one of Claude's types is carried by the sort. The previous quoted-name wording is gone.")
NOTE_U0286 = ("PS-0p step 3: the heading “Acknowledging open problems” takes for granted that there are open problems (factive with an object). Predicate `open_problem` worded “{0} is unsolved”, fence "
              "“Some thing is unsolved.” (`∃x open_problem(x)`), CHECKED, +29 B. It was offered and reverted in 20261018T1800Z because the whole-document premise check went UNKNOWN; after the repair of "
              "QT-0p's wording (a sort instead of a predicate) the check stays `model` (evidence/ps0p/premise-variants-0600Z.json). The English says “unsolved”, not “open problem”: it is the plan's wording. "
              "Claimed only if the audit accepts it.")
NOTE_U0032 = ("PS-0p step 5, class B: the heading “What constitutes genuine helpfulness” takes for granted that something constitutes genuine helpfulness (wh-title). Predicate `genuine_helpfulness` "
              "worded “{0} is helpful” (the lint refuses “constitutes genuine helpfulness”, TEMPLATE_SHAPE, and “is genuinely helpful”, UNARY_MODIFIER), so the English drops “genuine” and “constitutes”; the "
              "open term `genuine_helpfulness` keeps them (the thing constitutes genuine helpfulness; what counts is open). Fence “Some thing is helpful.” (`∃x genuine_helpfulness(x)`), OPEN, +38 B. "
              "Offered and reverted in 20261018T1800Z for the same premise-check reason as u0286; now it stays `model`. Claimed only if the audit accepts it.")
CLAIM_U0235 = "Claude has a nature."


def apply(ledger, english):
    """Returns (changed unit ids, the units' roles). `ledger` is edited in place."""
    by = {e["id"]: e for e in ledger}
    changed = []
    # --- audit repair of QT-0p
    for uid, note, key in (("u0042.presupposition", NOTE_U0042, "u0042.presupposition"), ("u0043.s02.p2", NOTE_P2, "u0043.s02.p2")):
        e = by[uid]
        assert e["status"] == "CHECKED" and "claude_principal_type" in e["checked_english"], uid
        e["checked_english"] = english[key]
        e["note"] = note
        e["audit_repair"] = {"audit": "20261018T1800Z", "verdict": "UNFAITHFUL" if uid == "u0042.presupposition" else "flagged (same English)",
                             "cause": "the English was the quoted fallback `Y1 is classified as \"claude_principal_type\"`, which PS-0p rejects",
                             "repair": "the sort `principal_type` has the noun “principal type of Claude”; the predicate is removed; the English now reads as ordinary English"}
        assert "claude_principal_type" not in e["checked_english"] and "classified as" not in e["checked_english"]
        changed.append(uid)
    # --- u0286 (step 3): CHECKED
    e = by["u0286.presupposition"]
    assert e["status"] == "UNFORMALISED"
    prev_claim, prev_mf = e["presupposed_claim"], e["missing_feature"]
    for k in ("presupposed_claim", "missing_feature", "offered_and_reverted"):
        e.pop(k, None)
    keep = [b for b in e.get("other_blockers", []) if b != "other:presupposition"]   # the scope tags stay; the carrier is assumed now
    e.pop("other_blockers", None)
    if keep:
        e["other_blockers"] = keep
    e.update({"status": "CHECKED", "kind": "asserted", "support": "assumption", "claimed": True, "note": NOTE_U0286, "checked_english": english["u0286.presupposition"],
              "carrier": "assumed", "trigger": "factive", "trigger_words": "Acknowledging", "previous_status": "UNFORMALISED", "previous_missing_feature": prev_mf,
              "previous_presupposed_claim": prev_claim, "offered_to_audit": True, "plan_repair": {"plan": "presupposition", "item": "PS-0p step 3"}})
    changed.append("u0286.presupposition")
    # --- u0032 (step 5, class B): OPEN
    e = by["u0032.presupposition"]
    assert e["status"] == "UNFORMALISED"
    prev_claim, prev_mf = e["presupposed_claim"], e["missing_feature"]
    for k in ("presupposed_claim", "missing_feature", "offered_and_reverted"):
        e.pop(k, None)
    keep = [b for b in e.get("other_blockers", []) if b != "other:presupposition"]   # the scope tags stay; the carrier is assumed now
    e.pop("other_blockers", None)
    if keep:
        e["other_blockers"] = keep
    e.update({"status": "OPEN", "kind": "asserted", "support": "assumption", "claimed": True, "note": NOTE_U0032, "open_terms": ["genuine_helpfulness"],
              "checked_english": english["u0032.presupposition"], "carrier": "assumed", "trigger": "wh-title", "trigger_words": "What", "previous_status": "UNFORMALISED",
              "previous_missing_feature": prev_mf, "previous_presupposed_claim": prev_claim, "offered_to_audit": True,
              "plan_repair": {"plan": "presupposition", "item": "PS-0p step 5"}})
    changed.append("u0032.presupposition")
    # --- the audit's small fault on u0235: the claim exceeded its `pre`
    e = by["u0235.presupposition"]
    assert e["status"] == "UNFORMALISED" and e["presupposed_claim"] == "Claude has a nature to discuss."
    e["previous_presupposed_claim"] = e["presupposed_claim"]
    e["presupposed_claim"] = CLAIM_U0235
    e["audit_repair"] = {"audit": "20261018T1800Z", "verdict": "small fault", "cause": "the recorded claim “Claude has a nature to discuss.” said more than the trigger's `pre`",
                         "repair": "the claim is “Claude has a nature.”, equal to the trigger's `pre`"}
    changed.append("u0235.presupposition")
    for uid in ("u0277", "u0294"):
        by[uid]["audit_repair"] = {"audit": "20261018T1800Z", "verdict": "small fault", "cause": "the definite trigger had no entry in `presupposition_triggers`",
                                   "repair": "the entry is added (carrier unresolved); the unit stays a LABELLED heading"}
        changed.append(uid)
    return changed


EXTRA_TRIGGERS = {
    "u0277": {"words": "The", "class": "definite", "pre": "There is an existential frontier.", "carrier": "unresolved"},
    "u0294": {"words": "the word", "class": "definite", "pre": "There is a word “constitution”.", "carrier": "unresolved"},
}
