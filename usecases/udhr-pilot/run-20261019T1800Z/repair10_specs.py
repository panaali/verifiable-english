"""Audit repairs for the 2026-10-10T0600Z run (previous-20261009T1800Z/AUDIT.md: 20/20 sampled + 16/20 changed faithful; u049 u073 u105b u105c rejected).

The audit found four units that kept ONE reading although the English itself supports more than one (readings come from the words only):

* u049 "to leave any country, including his own, and to return to his country": "his own" / "his country" is the country of nationality
  or the country of residence (the same two meanings u077 already offers). Both occurrences are read alike inside one candidate.
* u073 "freedom of peaceful assembly and association": "peaceful" qualifies assembly alone, or both assembly and association.
* u105b, u105c "freely to participate ..., to enjoy the arts, and to share in scientific advancement": "freely" qualifies "participate" alone
  (u105a, the same in both readings), or all three. u105a is unchanged: "freely to participate" holds on both readings.

Each right stays ONE entitlement per reading (who holds it, nothing more); no duty reading is added.
"""
from __future__ import annotations

import repair_specs as RS

NEW = {}        # unit -> [(candidate id, spec, why)]
ORDER = {}
REASON = {}
UNSPEC = ("Completion 'unspecified' (norm-defaults@0): where the rule's guard fails, or the party is not one the rule names, the case is "
          "UNDECIDED, never 'not required' and never permitted; strict force, because the source states no exception.")


def add(unit, cid, spec, why):
    NEW.setdefault(unit, []).append((cid, spec, why + " " + UNSPEC))


NOBEARER = "The words name no one who must act, so the candidate names no bearer (the responsibility stays unspecified)."

# ---- u049: Article 13(2)
for _kind, _sing in (("nationality", "country of nationality"), ("residence", "country of residence")):
    add("u049", f"entitlement_{_kind}", RS.entitlement(
        "u049", f"entitlement_{_kind}", f"has_the_right_to_leave_and_return_{_kind}",
        f"{{0}} has the right to leave any country including their {_sing} as well as to return to it",
        f"The person has the right to leave any country, including the person's {_sing}, and to return to the person's {_sing}", []),
        f"Entitlement reading of Article 13(2) with 'his own' and 'his country' both read as the {_sing}: every person has the right to "
        f"leave any country, including that one, and to return to it. {NOBEARER} 'His country' is the only thing the words leave to a "
        "reading; nationality and residence are the two meanings the English phrase has (the same two readings as u077).")
ORDER["u049"] = ["entitlement_nationality", "entitlement_residence"]
REASON["u049"] = ("audit: CHECKED hid the unresolved 'his country' (nationality or residence) inside one opaque predicate; it is now a "
                  "reading set with one entitlement per meaning, as in u077")

# ---- u073: Article 20(1)
add("u073", "peaceful_assembly_and_association", RS.entitlement(
    "u073", "peaceful_assembly_and_association", "right_to_peaceful_assembly_and_any_association",
    "{0} has the right to freedom of peaceful assembly as well as to freedom of association",
    "The person has the right to freedom of peaceful assembly and to freedom of association (association not said to be peaceful)", []),
    "Entitlement reading of Article 20(1) in which 'peaceful' qualifies 'assembly' alone: every person has the right to freedom of peaceful "
    f"assembly and to freedom of association. {NOBEARER}")
add("u073", "peaceful_both", RS.entitlement(
    "u073", "peaceful_both", "right_to_peaceful_assembly_and_peaceful_association",
    "{0} has the right to freedom of peaceful assembly as well as to freedom of peaceful association",
    "The person has the right to freedom of peaceful assembly and to freedom of peaceful association", []),
    "Entitlement reading of Article 20(1) in which 'peaceful' qualifies both 'assembly' and 'association': every person has the right to "
    f"freedom of peaceful assembly and to freedom of peaceful association. {NOBEARER}")
ORDER["u073"] = ["peaceful_assembly_and_association", "peaceful_both"]
REASON["u073"] = ("audit: CHECKED left the scope of 'peaceful' (assembly alone, or assembly and association) unresolved; it is now a "
                  "reading set with one entitlement per scope")

# ---- u105b, u105c: Article 27(1)
for _u, _what, _stem_free, _free_v, _free_d, _stem_plain, _plain_v, _plain_d in (
    ("u105b", "enjoy the arts", "has_the_right_freely_to_enjoy_the_arts", "{0} has the right freely to enjoy the arts",
     "The person has the right freely to enjoy the arts", "has_the_right_to_enjoy_the_arts_unqualified",
     "{0} has the right to enjoy the arts", "The person has the right to enjoy the arts (no 'freely' attached)"),
    ("u105c", "share in scientific advancement and its benefits", "has_right_freely_share_scientific_advancement",
     "{0} has the right freely to share in scientific advancement as well as its benefits",
     "The person has the right freely to share in scientific advancement and its benefits",
     "has_right_share_scientific_advancement_unqualified",
     "{0} has the right to share in scientific advancement as well as its benefits",
     "The person has the right to share in scientific advancement and its benefits (no 'freely' attached)")):
    add(_u, "freely_attaches", RS.entitlement(_u, "freely_attaches", _stem_free, _free_v, _free_d, []),
        f"Entitlement reading of Article 27(1) in which 'freely' qualifies every right in the list ('participate', 'enjoy', 'share'): every "
        f"person has the right freely to {_what}. {NOBEARER}")
    add(_u, "freely_participate_only", RS.entitlement(_u, "freely_participate_only", _stem_plain, _plain_v, _plain_d, []),
        f"Entitlement reading of Article 27(1) in which 'freely' qualifies 'participate' alone (the first right; u105a): every person has the "
        f"right to {_what}, with no 'freely' in the words that state this right. {NOBEARER}")
    ORDER[_u] = ["freely_attaches", "freely_participate_only"]
    REASON[_u] = ("audit: only the reading in which 'freely' qualifies all three rights was kept; the words also support 'freely' "
                  "qualifying 'participate' alone, so the unit is now a reading set with both")
AUDIT_REJECTED = ["u049", "u073", "u105b", "u105c"]
