"""Audit repairs for the 2026-10-12T0600Z run (previous-20261010T0600Z/AUDIT.md: 18/20 sampled + 2/4 changed faithful; u061, u105b, u105c rejected).

* u061 "and is entitled to protection by society and the State.": the words say what the family is entitled to ("protection by society
  and the State") and name no one who must act and no pairing of society and State with the family; the unit is ONE entitlement (who
  holds it, nothing more), as for every other "has the right" / "is entitled" unit.
* u105b, u105c "to enjoy the arts" / "and to share in scientific advancement and its benefits": the scope of "freely" is one question over
  the list, not two. A meaning in which "freely" qualifies the sharing but not the enjoying of the arts is not a meaning of the sentence, so
  the two reading sets are coupled on one axis (composition S1 couplings): a reading of the declaration takes "freely" on all three rights
  or on the first only, for both units together.
"""
from __future__ import annotations

import udhr_specs as U
import repair_specs as RS

NEW = {}
ORDER = {}
REASON = {}
UNSPEC = U.UNSPEC
NOBEARER = "The words name no one who must act, so the candidate names no bearer (the responsibility stays unspecified)."

FAMILY = U.case_sort("family", "families", "a family", {}, ("top",), [[]])
NEW["u061"] = [("entitlement", RS.entitlement(
    "u061", "entitlement", "is_entitled_to_protection_by_society_and_the_state",
    "{0} is entitled to protection by society and the State",
    "The family is entitled to protection by society and the State", ["protection_of_the_family"], case=FAMILY),
    "Entitlement reading of Article 16(3), second clause: every family (the subject of the previous clause, u060, which the clause "
    "continues with 'and is') is entitled to protection by society and the State. It says what the family is entitled to; it names no one "
    "who must act, so the candidate names no bearer and states no duty on any State or on society. What counts as protection is the open "
    f"term protection_of_the_family. {UNSPEC}")]
ORDER["u061"] = ["entitlement"]
REASON["u061"] = ("the unit is the family's entitlement to protection by society and the State, once, as the words say it "
                  "(who holds the right, nothing more); it names no one who must act")

COUPLED = {"u105b": "rs_u105b", "u105c": "rs_u105c"}
AXIS = "freely_scope"
LABEL = {"freely_attaches": "all_three_rights", "freely_participate_only": "participate_only"}
REASON["u105b"] = REASON["u105c"] = ("the scope of 'freely' is one choice over the list of Article 27(1), so the two reading sets are "
                                      "coupled on the axis freely_scope: a reading of the declaration takes 'freely' on all three rights, or "
                                      "on 'participate' alone, for u105b and u105c together")
AUDIT_REJECTED = ["u061", "u105b", "u105c"]
