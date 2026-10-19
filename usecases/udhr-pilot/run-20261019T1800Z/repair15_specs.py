"""Audit repair for the 2026-10-17T1800Z run (language at ve-green-fu-ar2-decoders).

The 20261017T0600Z audit (AUDIT.md, u037 UNFAITHFUL): in "arbitrary arrest, detention or exile" the word "arbitrary" can stand
before all three nouns or before "arrest" alone, and the run gave u037 only the wide reading (it gives two readings to u055,
u073 and u105 for the same structure). The audit named u027 as having the same structure: in "cruel, inhuman or degrading
treatment or punishment" the three adjectives can stand before both nouns or before "treatment" alone. Both units become a reading
set of two norm candidates over the same regulated act; nothing is added from outside the words (the narrower scope of the
modifier is a reading of the word order, nothing more), and the explicitly listed items (arrest, detention, exile; treatment,
punishment) stay as checked structure. No predicate, sort or open term is new: the two readings differ only in the guard.
"""
from __future__ import annotations

import repair6_specs as R6
import udhr_specs as U
from udhr_specs import AND, OR, case_sort

NEW = {}        # unit -> [(candidate id, spec, why)]
ORDER = {}      # unit -> final candidate order
REASON = {}
AUDIT_REJECTED = ["u037"]
NAMED_BY_AUDIT = ["u027"]


def add(unit, cid, spec, why):
    NEW.setdefault(unit, []).append((cid, spec, why + " " + R6.NOBEARER + " " + U.UNSPEC))


def case(base_case, guard, extra_examples):
    return {**base_case, "guard": guard, "examples": [*base_case["examples"], *extra_examples]}


# ---- u037: Article 9 -------------------------------------------------------------------------------------------------------------
C37 = case(U.U037_CASE, None, [["is_arrest"], ["is_exile"]])
for cid, guard, what in (
        ("arbitrary_over_all", AND(OR(("p", "is_arrest"), ("p", "is_detention"), ("p", "is_exile")), ("p", "is_arbitrary")),
         "'arbitrary' is read over all three acts: an arrest, a detention and an exile that is arbitrary are not permitted; a "
         "measure that is not arbitrary is not decided by this rule"),
        ("arbitrary_arrest_only", OR(AND(("p", "is_arrest"), ("p", "is_arbitrary")), ("p", "is_detention"), ("p", "is_exile")),
         "'arbitrary' is read over 'arrest' alone, with 'detention' and 'exile' bare nouns: an arbitrary arrest is not permitted, "
         "and a detention or an exile is not permitted whether or not it is arbitrary")):
    add("u037", cid, R6.forbidden("u037", cid, "arrest_detention_or_exile_permitted", "{0} take place",
                                  "The arbitrary arrest, detention or exile of a person is permitted to take place", C37,
                                  ["arbitrary"], guard=guard),
        "Article 9: 'No one shall be subjected to arbitrary arrest, detention or exile': " + what + "; the source's word order "
        "admits both. What makes a measure arbitrary is the open term (in the second reading it qualifies the arrest only).")
ORDER["u037"] = ["arbitrary_over_all", "arbitrary_arrest_only"]
REASON["u037"] = ("the 20261017T0600Z audit: the scope of 'arbitrary' over 'arrest, detention or exile' is a reading of the word order and "
                  "u037 had only the wide one; a second candidate keeps 'arbitrary' on 'arrest' alone")

# ---- u027: Article 5 (named by the same audit) ---------------------------------------------------------------------------------
_ADJ = OR(OR(("p", "is_cruel"), ("p", "is_inhuman")), ("p", "is_degrading"))
C27 = case(U.U027_CASE, None, [["is_punishment"], ["is_treatment"]])
for cid, guard, what in (
        ("adjectives_over_both", OR(("p", "is_torture"), AND(_ADJ, OR(("p", "is_treatment"), ("p", "is_punishment")))),
         "'cruel, inhuman or degrading' is read over both 'treatment' and 'punishment': a subjection to torture, and to treatment or "
         "punishment that is cruel, inhuman or degrading, are not permitted"),
        ("adjectives_treatment_only", OR(("p", "is_torture"), AND(_ADJ, ("p", "is_treatment")), ("p", "is_punishment")),
         "'cruel, inhuman or degrading' is read over 'treatment' alone, with 'punishment' a bare noun: a subjection to torture, to "
         "cruel, inhuman or degrading treatment, and to punishment (cruel, inhuman or degrading or not) is not permitted")):
    add("u027", cid, R6.forbidden("u027", cid, "subjection_to_ill_treatment_permitted", "{0} take place",
                                  "The subjection of a person to torture, or to cruel, inhuman or degrading treatment or punishment, "
                                  "is permitted to take place", C27, ["ill_treatment"], guard=guard),
        "Article 5: 'No one shall be subjected to torture or to cruel, inhuman or degrading treatment or punishment': " + what +
        "; the source's word order admits both. Punishment is explicitly covered in both. Which treatment or punishment counts as "
        "cruel, inhuman or degrading stays the open term.")
ORDER["u027"] = ["adjectives_over_both", "adjectives_treatment_only"]
REASON["u027"] = ("named by the 20261017T0600Z audit as having u037's structure: the scope of 'cruel, inhuman or degrading' over "
                  "'treatment or punishment' is a reading of the word order; a second candidate keeps the adjectives on 'treatment' alone")
