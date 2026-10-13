"""Repaired candidates of the units the 2026-10-05T0600Z audit rejected (previous-20261005T0600Z/AUDIT.md), and the units with the same defect.

The audit sampled 20 units and rejected four (16/20 faithful). Its reasons and the repairs:

* u098 `guardian_ensures`: the unconditional guard obliged every guardian to see that every person attends, though the admission
  text promised a guardian-dependent relationship. Repair: a base relation `is_parent_or_guardian_of` (guardian, person) is the
  rule's guard, so a guardian is bound only for the persons in their care; elsewhere the case is UNDECIDED.
* u073 `state_combined`: the act dropped "freedom of" to fit the 80-byte act limit, so it said "secure peaceful assembly and
  association" rather than the freedoms. The full phrase needs 91 bytes. Repair: the candidate is removed. The same defect (a
  combined act that drops or rewrites words of the source's phrase) is in u048 (drops "within each state"), u063 (rewrites "with
  others" as "jointly"), u066 (drops the connective), u084a (drops "from") and u105a (drops "of the community"), so those five
  combined candidates are removed as well; u070, u084b, u096 and u105b carry the whole phrase and stay.
* u051: no entitlement with the responsibility unspecified, and the two duty candidates were guarded by exposure to persecution,
  which narrows "everyone's right to seek asylum from persecution" to persons already persecuted. Repair: an entitlement is added;
  the duties lose the guard (every person is a holder); "from persecution" moves into the act (which has no room for "in other
  countries", so "abroad" stands for it); the liberty stays as it was.
* u112 `exercise_unprotected`: quantified over exercises of any right or freedom, but the sentence is about "these rights and
  freedoms". Repair: the main document's vocabulary gains `exercise_of_declared_right`, and the formula limits the claim to such
  exercises. The norm candidate (`exercise_prohibited`) already carried the restriction as a guard.
"""
from __future__ import annotations

import udhr_specs as U
from repair2_specs import ENTITLEMENT
from repair_specs import entitlement
from udhr_specs import (PERSON, Top, V0, V1, base, duty, norm, regulated, slug, sort)
from ve.ast import Binary

UNSPEC = U.UNSPEC
AUDIT_REJECTED = ["u051", "u073", "u098", "u112"]
# combined (noninterference + protection) candidates whose act phrase does not carry the source's whole phrase
DROP_COMBINED = {
    "u048": "the act left out 'within the borders of each state'",
    "u063": "the act rewrote 'with others' as 'jointly'",
    "u066": "the act left out the connective between the three freedoms",
    "u073": "the act left out 'freedom of' (the whole phrase needs 91 bytes; the limit is 80); this is what the audit rejected",
    "u084a": "the act left out 'from' (the barred thing), so 'avoid barring ... work by' no longer said what is barred",
    "u105a": "the act left out 'of the community'",
}
REPAIRED = sorted(set(AUDIT_REJECTED) | set(DROP_COMBINED))
NEW_CANDIDATES: dict[str, list[tuple[str, dict, str]]] = {}   # unit -> candidates replaced or added (id, spec, why)
REMOVED: dict[str, list[str]] = {"u051": ["state_avoid", "anyone_avoid"], "u098": ["guardian_ensures"],
                                 **{u: ["state_combined"] for u in DROP_COMBINED}}
REASON = {
    "u051": "the duties were guarded by exposure to persecution, narrowing everyone's right; no entitlement with the responsibility "
            "unspecified; now an entitlement, the two duties for every holder, and the unchanged liberty",
    "u073": "the combined candidate's act dropped 'freedom of' (80-byte limit); removed",
    "u098": "the guardian duty had an unconditional guard, so it bound every guardian for every person; now guarded by the relation "
            "'is a parent or guardian of'",
    "u112": "the unprotected-exercise formula covered any right or freedom; now only exercises of the rights and freedoms set forth in "
            "this Declaration",
    **{u: "same defect as u073's combined candidate (" + why + "); removed" for u, why in DROP_COMBINED.items() if u != "u073"},
}


def add(unit, cid, spec, why):
    NEW_CANDIDATES.setdefault(unit, []).append((cid, spec, why + " " + UNSPEC))


# ---- u051: Article 14(1) ---------------------------------------------------------------------------------------------------
_OPEN = ["persecution"]
add("u051", "entitlement",
    entitlement("u051", "entitlement", "has_the_right_to_seek_and_enjoy_asylum",
                "{0} has the right to seek as well as enjoy in other countries asylum from persecution",
                "The person has the right to seek and to enjoy in other countries asylum from persecution", _OPEN),
    "Entitlement reading of Article 14(1): every person has the right to seek and to enjoy in other countries asylum from persecution; "
    "the source names no one who must do anything, so the candidate names no bearer (a plain regulated predicate the rule makes true "
    "of every person); the responsibility stays unspecified, and no condition (such as already suffering persecution) narrows who "
    "holds it.")
_ACT = "{0} leave {1} free to seek as well as enjoy asylum from persecution abroad"
for _b, _who in (("state", "every State"), ("anyone", "every State, group and person")):
    add("u051", f"{_b}_avoid",
        duty("u051", f"{_b}_avoid", "avoid_barring_asylum_required", _ACT,
             "The bearer is required to leave the person free to seek and to enjoy asylum from persecution abroad",
             bearer=_b, arity="person", opens=_OPEN),
        f"Claim reading of Article 14(1) as noninterference: {_who} must leave each holder free to seek as well as enjoy asylum from "
        "persecution abroad. Every person is a holder; no guard narrows the duty to persons already persecuted (the open term "
        "persecution says what 'persecution' is). 'Abroad' stands for 'in other countries' (80-byte act limit). No positive duty to "
        "grant asylum is a candidate." + (" The source names no bearer, so the duty is also read on every group and person."
                                          if _b == "anyone" else ""))


# ---- u098: Article 26(1) -----------------------------------------------------------------------------------------------------
GUARDIAN = sort("guardian", "guardians", "a parent or guardian of a person")


def guardian_duty(unit, cid, stem, act, desc, opens):
    """An obligation of a guardian towards a person, in force only where the guardian is a parent or guardian of the person."""
    rel = "is_parent_or_guardian_of"
    spec = dict(sorts={"guardian": GUARDIAN, "person": PERSON},
                predicates={rel: base(["guardian", "person"], "The guardian is a parent or guardian of the person",
                                      "{0} is a parent or guardian of {1}"),
                            stem: regulated(["guardian", "person"], "obligation", desc, act)},
                rule=norm(slug(f"{unit}-{cid}"), stem, True, Binary(rel, V1, V0)), open=list(opens), soft=False)
    spec["witnesses"] = [({"guardian": ["g0", "g1"], "person": ["p0", "p1"]}, {rel: [["g0", "p0"]]},
                          [(stem, ("g0", "p0"), ("SETTLED", True)), (stem, ("g0", "p1"), ("UNDECIDED", None)),
                           (stem, ("g1", "p0"), ("UNDECIDED", None))])]
    return spec


add("u098", "guardian_ensures",
    guardian_duty("u098", "guardian_ensures", "see_to_compulsory_elementary_education_required",
                  "{0} see that {1} attends compulsory elementary education",
                  "The parent or guardian is required to see that the person in their care attends elementary education that is "
                  "compulsory for the person", ["compulsory"]),
    "Article 26(1) read as a duty of a parent or guardian to see that the person in their care attends the elementary education that "
    "is compulsory for that person. The rule applies only where the guardian is a parent or guardian of the person (the base relation "
    "'is a parent or guardian of'); for any other guardian and person the case is UNDECIDED, so no duty is invented for unrelated "
    "people. For whom education is compulsory is the open term compulsory.")

# ---- u112: Article 29(3), the formula over exercises ----------------------------------------------------------------------
U112_DECLARED = ("exercise_of_declared_right", {"arguments": ["exercise"],
                                                "description": "The exercise is an exercise of a right or freedom set forth in this Declaration"})
U112_CONTENT = ["forall", "exercise",
                ["implies",
                 ["and", ["unary", "exercise_of_declared_right", ["var", 0]], ["unary", "exercise_contrary_to_un", ["var", 0]]],
                 ["not", ["unary", "right_protects_exercise", ["var", 0]]]]]
U112_WHY = ("Article 29(3) read as a limit on the rights' scope: no right or freedom set forth in this Declaration protects an exercise "
            "of one of them that is contrary to UN purposes and principles. A formula over single exercises (not persons), so one "
            "contrary exercise removes protection from that exercise only; exercises of other rights, and exercises that are not "
            "contrary, are left as they were. The restriction to 'these rights and freedoms' is the predicate "
            "exercise_of_declared_right (the open term rights_and_freedoms_set_forth).")
