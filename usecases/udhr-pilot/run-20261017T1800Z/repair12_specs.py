"""Audit repair for the 2026-10-12T1800Z run (previous-20261012T0600Z/AUDIT.md: 19/20 sampled + 4/4 changed faithful; u081 rejected).

* u081 "Everyone, as a member of society, has the right to social security": the words give the capacity in which each person holds the
  right ("as a member of society"). The earlier form read every person as a member of society and kept the phrase only in the source
  quotation, so the formal meaning lost it. The unit is still ONE entitlement (who holds it, nothing more; no duty on anyone), but its
  predicate now says it ("has the right to social security as a member of society"), and "member of society" is a named open term (nothing
  in the text says who counts as a member of society, or who decides).
"""
from __future__ import annotations

import udhr_specs as U
import repair_specs as RS

NEW = {}
ORDER = {}
REASON = {}
UNSPEC = U.UNSPEC

MEMBER_TERM = {
    "arguments": [], "decided_by": "unstated", "factors": ["what being a member of society consists in"],
    "jurisdiction": "universal", "name": "member_of_society", "necessary": [], "precedents": [], "sufficient": [], "version": 1}

NEW["u081"] = [("entitlement", RS.entitlement(
    "u081", "entitlement", "has_the_right_to_social_security_as_a_member_of_society",
    "{0}, as a member of society, has the right to social security",
    "The person, as a member of society, has the right to social security", ["social_security", "member_of_society"]),
    "Entitlement reading of Article 22, first sentence: every person, as a member of society, has the right to social security. The "
    "predicate carries the words 'as a member of society' (the capacity in which each person holds the right); what counts as a member of "
    "society is the open term member_of_society and what social security covers is the open term social_security. The source names no one "
    "who must do anything, so the candidate names no bearer (a plain regulated predicate the rule makes true of every person); the "
    f"responsibility stays unspecified. {UNSPEC}")]
ORDER["u081"] = ["entitlement"]
REASON["u081"] = ("the audit found that 'as a member of society' was kept only in the quotation; the predicate now carries it and "
                  "'member of society' is a named open term; still one entitlement, no bearer")
AUDIT_REJECTED = ["u081"]
