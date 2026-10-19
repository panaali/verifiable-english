"""Repaired candidates of the units the 2026-10-06T1800Z audit rejected (previous-20261006T1800Z/AUDIT.md), and the units with the same defect.

The audit sampled 20 units and rejected three (17/20 faithful). Its reasons and the repairs:

* u099b ("and higher education shall be equally accessible to all on the basis of merit."): the only candidate made it a duty of
  every State, a bearer the passive does not assign. New candidate `unassigned`: an obligation over the *person* ("all") whose act
  is that the person be given equal access to higher education on the basis of merit, with no bearer at all; the State candidate
  stays as the reading that assigns the duty to States. The same defect (a passive with no agent) is in u099a, u100a and u100b,
  which get the same bearer-less candidate (an obligation over the thing the sentence is about).
* u105c ("and to share in scientific advancement and its benefits."): the State candidate required securing every person an actual
  share (a strengthening of a right to share, which is an opportunity), and noninterference and the combined reading were absent.
  The State candidates are now duties over the right itself (as u048, u063 and u105a): avoid denying it, secure it (the right, not
  any actual share), and both together; the anyone noninterference candidate is added; entitlement and liberty are as before.
* u110 ("1. Everyone has duties to the community in which alone the free and full development of his personality is possible."): the
  two norm candidates turned "has duties" into an obligation to perform whatever duties one has, without saying that any exist.
  Repaired in repair5.py: three *asserted* readings over a community sort (a duty-owing relation and a development-possible-in
  relation), which keep the existence of the community and of the duties as part of what is asserted.
"""
from __future__ import annotations

import repair4_specs as R4
import udhr_specs as U
from companions import sort
from udhr_specs import V0, case_bases, case_sort, holds, norm, regulated, slug, ast

UNSPEC = U.UNSPEC
AUDIT_REJECTED = ["u099b", "u105c", "u110"]
SAME_DEFECT = ["u099a", "u100a", "u100b"]
REPAIRED = sorted(set(AUDIT_REJECTED) | set(SAME_DEFECT))
NEW_CANDIDATES: dict[str, list[tuple[str, dict, str]]] = {}
ADDED = {"u099a": ["unassigned"], "u099b": ["unassigned"], "u100a": ["unassigned"], "u100b": ["unassigned"],
         "u105c": ["state_negative", "anyone_negative", "state_positive", "state_combined"]}
REMOVED = {"u105c": ["state_claim"], "u110": ["restrictive", "describing"]}
REASON = {
    "u099b": "the only candidate made it a duty of every State, a bearer the passive does not assign; added a reading with no bearer "
             "(an obligation that every person be given equal access to higher education on the basis of merit)",
    "u099a": "same defect as u099b (a passive with no agent had only a State candidate); added a bearer-less reading (an obligation on "
             "technical education and on professional education to be made generally available)",
    "u100a": "same defect as u099b (a passive with no agent); added a bearer-less reading (an obligation on education to be directed "
             "to the full development of the human personality)",
    "u100b": "same defect as u099b (a passive with no agent); added a bearer-less reading (an obligation on education to be directed "
             "to strengthen respect of human rights and fundamental freedoms)",
    "u105c": "the State candidate required securing every person an actual share, strengthening the right to share into an outcome, "
             "and the noninterference and combined readings were missing; the State readings are now duties over the right itself "
             "(avoid denying it, secure it, both together) and the anyone noninterference reading is added",
    "u110": "the norm candidates read 'has duties' as an obligation to perform whatever duties one has without saying that any exist, "
            "and the relative clause was a guard or an open-term description; the readings now assert that every person has duties "
            "to a community in which that person's free and full development alone is possible (one community per person, one "
            "community for everyone) or to the community the clause identifies, as asserted formulas",
}


def add(unit, cid, spec, why):
    NEW_CANDIDATES.setdefault(unit, []).append((cid, spec, why + " " + UNSPEC))


def unassigned(unit, cid, stem, act, desc, *, case, opens):
    """An obligation over the thing the sentence is about, with no bearer at all (the passive names none)."""
    predicates = {stem: regulated([case["name"]], "obligation", desc, act), **case_bases(case)}
    spec = dict(sorts={case["name"]: case["sort"]}, predicates=predicates,
                rule=norm(slug(f"{unit}-{cid}"), stem, True, ast(case["guard"], V0, V0)), open=list(opens), soft=False)
    elems = [f"c{i}" for i in range(len(case["examples"]))]
    rels = {n: [[e] for e, trues in zip(elems, case["examples"]) if n in trues] for n in case["bases"]}
    checks = [(stem, (e,), ("SETTLED", True) if holds(case["guard"], set(), set(t)) else ("UNDECIDED", None))
              for e, t in zip(elems, case["examples"])]
    spec["witnesses"] = [({case["name"]: elems}, rels, checks)]
    return spec


NOBEARER = ("The sentence is a passive with no agent, so this reading names no bearer: it says the thing is required, of no stated "
            "party. Nothing is said of any State, group or person, and no one is made to do anything by it.")

# ---- u099a / u099b / u100a / u100b: passives without an agent ---------------------------------------------------------
KIND = case_sort(
    "education kind", "education kinds", "one kind of education",
    {"is_technical": "The education is technical education", "is_professional": "The education is professional education"},
    U.OR(("p", "is_technical"), ("p", "is_professional")), [["is_technical"], ["is_professional"], []])
add("u099a", "unassigned", unassigned(
    "u099a", "unassigned", "education_generally_available_required", "{0} be made generally available",
    "The education is required to be made generally available", case=KIND, opens=["generally_available"]),
    "Article 26(1): 'Technical and professional education shall be made generally available', with no one assigned to make it so: "
    "technical education, and professional education (the two named kinds are the guard's explicit list), are each required to be "
    "made generally available. " + NOBEARER)

ALL = case_sort("person", "people", "a human person", {}, ("top",), [[]])
add("u099b", "unassigned", unassigned(
    "u099b", "unassigned", "equal_access_to_higher_education_required", "{0} be given equal access to higher education on the basis of merit",
    "It is required, of no stated party, that the person be given equal access to higher education on the basis of merit",
    case=ALL, opens=["merit"]),
    "Article 26(1): 'higher education shall be equally accessible to all on the basis of merit', with no one assigned to make it so: "
    "for every person ('all'), equal access to higher education on the basis of merit (the open term merit) is required. " + NOBEARER)

COURSE = case_sort("course of education", "courses of education", "one course of education", {}, ("top",), [[]])
add("u100a", "unassigned", unassigned(
    "u100a", "unassigned", "education_directed_to_personality_required", "{0} be directed to the full development of the human personality",
    "The course of education is required to be directed to the full development of the human personality", case=COURSE,
    opens=["full_development_of_the_human_personality"]),
    "Article 26(2): 'Education shall be directed to the full development of the human personality', with no one assigned to direct "
    "it: every course of education is required to be directed so. " + NOBEARER)
add("u100b", "unassigned", unassigned(
    "u100b", "unassigned", "education_directed_to_respect_for_rights_required",
    "{0} be directed to strengthen respect of human rights as well as freedoms",
    "The course of education is required to be directed to the strengthening of respect for human rights and fundamental freedoms",
    case=COURSE, opens=["rights_and_freedoms_set_forth"]),
    "Article 26(2): 'and to the strengthening of respect for human rights and fundamental freedoms', with no one assigned to direct "
    "education; the subject and 'shall' are carried from u100a (not a checked reference): every course of education is required to "
    "be directed so. " + NOBEARER)

# ---- u105c: the right itself ------------------------------------------------------------------------------------------------
R4.RIGHT_NOUN["u105c"] = "freely to share in scientific advancement as well as its benefits"
R4.RIGHT_PHRASE["u105c"] = "freely to share in scientific advancement and its benefits"
_NOTE = R4._NOTE.format(phrase=R4.RIGHT_PHRASE["u105c"])
add("u105c", "state_negative", R4.right_duty("u105c", "state_negative", "avoid_denying_right_u105c_required", "{0} avoid denying {1}",
                                             "avoid denying"),
    _NOTE + "Claim reading as noninterference: every State must avoid denying each person's right; the source names no bearer and no "
            "polarity, so this is the translator's candidate. It requires no actual share for anyone.")
add("u105c", "anyone_negative", R4.right_duty("u105c", "anyone_negative", "avoid_denying_right_u105c_required", "{0} avoid denying {1}",
                                              "avoid denying"),
    _NOTE + "Claim reading as noninterference: every State, group and person must avoid denying each person's right; the source names "
            "no bearer and no polarity, so this is the translator's candidate.")
add("u105c", "state_positive", R4.right_duty("u105c", "state_positive", "secure_right_u105c_required", "{0} secure {1}", "secure"),
    _NOTE + "Claim reading as protection: every State must secure each person's right (the right itself, the opportunity to share, not "
            "an actual share: nobody is required to receive any advancement or benefit because of this reading).")
add("u105c", "state_combined", R4.right_duty("u105c", "state_combined", "avoid_denying_and_secure_right_u105c_required",
                                             "{0} avoid denying as well as secure {1}", "avoid denying as well as secure"),
    _NOTE + "Claim reading combining noninterference with protection in one duty: every State must avoid denying as well as secure "
            "each person's right. The two parts bind together (one act phrase), unlike the separate noninterference and protection "
            "candidates, which are alternatives.")
