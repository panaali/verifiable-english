"""Repaired candidates of the units the 2026-10-05T1800Z audit rejected (previous-20261005T1800Z/AUDIT.md), and the units with the same defect.

The audit sampled 20 units and rejected four (16/20 faithful). Its reasons and the repairs:

* u035 `tribunal_claim`: competence was a property of the tribunal alone, so a tribunal competent for one case owed a remedy for
  every violation. Repair: a binary base relation `is_competent_for` (tribunal, violation) in the guard; a tribunal owes a remedy
  only for a violation it is competent for (elsewhere UNDECIDED). The open term competent still says what competence is.
* u098 `person_attends`: the duty bound every human unconditionally. Repair: the duty is guarded by a base predicate on the
  person, "elementary education is compulsory for the person" (for whom it is, and until what age or completion, is the open term
  compulsory); elsewhere UNDECIDED. `guardian_ensures` keeps its parent-or-guardian relation and takes the same guard, so a
  guardian is bound only for a person in their care for whom the education is compulsory.
* u048 and u063: the combined (noninterference plus protection) State candidate was removed last run because the act phrase could
  not carry the source's whole phrase in 80 bytes. The act phrase is not the only place the phrase can stand: a duty over a State
  and a *right* (one person's right of the kind the unit names, a case sort whose noun and description are the source's own
  words) needs an act of a few words ("avoid denying as well as secure {1}"), so the whole phrase is kept (a three-place
  predicate would need nary@0, which cannot sit beside norm-defaults@0). The same case form replaces u048's and u063's other duty
  candidates, whose acts also shortened the phrase ("within each state"; "alone as well as jointly"), and u063's positive duty
  required actual ownership by everyone, a strengthening of "the right to own": it now secures the right.
* the same removal had hit u066, u073, u084a and u105a, whose combined candidate is restored the same way.
"""
from __future__ import annotations

import udhr_specs as U
from companions_nd import VIOLATION, VIOLATES
from udhr_specs import PERSON, V0, V1, base, case_sort, duty, norm, regulated, slug, sort
from ve.ast import And, Binary, Unary

UNSPEC = U.UNSPEC
AUDIT_REJECTED = ["u035", "u048", "u063", "u098"]
RESTORED_COMBINED = ["u066", "u073", "u084a", "u105a"]
REPAIRED = sorted(set(AUDIT_REJECTED) | set(RESTORED_COMBINED))
NEW_CANDIDATES: dict[str, list[tuple[str, dict, str]]] = {}
REPLACED: dict[str, list[str]] = {"u035": ["tribunal_claim"], "u098": ["person_attends", "guardian_ensures"],
                                  "u048": ["state_negative", "anyone_negative", "state_positive"],
                                  "u063": ["state_negative", "anyone_negative", "state_positive"]}
ADDED: dict[str, list[str]] = {u: ["state_combined"] for u in ("u048", "u063", *RESTORED_COMBINED)}
REASON = {
    "u035": "the tribunal duty took competence as a property of the tribunal alone, so a tribunal competent for one case owed "
            "remedies for unrelated violations; competence is now a relation between the tribunal and the violation",
    "u098": "the person's duty applied to every human; it is now guarded by 'elementary education is compulsory for the person' (open "
            "term compulsory), and the guardian duty takes the same guard besides the parent-or-guardian relation",
    "u048": "the combined noninterference-and-protection candidate had been removed and the other duties shortened the phrase; the "
            "duties are now over the right itself (the source's whole phrase is the noun of the right), with the combined candidate restored",
    "u063": "the combined candidate had been removed, the positive duty required actual ownership by everyone, and the acts shortened "
            "the phrase; the duties are now over the right itself, the positive duty secures the right, the combined candidate is restored",
    **{u: "the combined noninterference-and-protection candidate had been removed because the act phrase could not carry the whole "
          "phrase; restored as a duty over the right itself (the source's whole phrase is the noun of the right)" for u in RESTORED_COMBINED},
}


def add(unit, cid, spec, why):
    NEW_CANDIDATES.setdefault(unit, []).append((cid, spec, why + " " + UNSPEC))


# ---- u035: Article 8 ---------------------------------------------------------------------------------------------------
TRIBUNAL = sort("tribunal", "tribunals", "a tribunal")
_COMPETENT = "is_competent_for"
add("u035", "tribunal_claim", dict(
    sorts={"tribunal": TRIBUNAL, "violation": VIOLATION},
    predicates={
        "is_national": base(["tribunal"], "The tribunal is a national tribunal", "{0} is national"),
        _COMPETENT: base(["tribunal", "violation"], "The tribunal is competent for the violation (the open term competent)",
                         "{0} is competent for {1}"),
        "violates_granted_fundamental_right": VIOLATES,
        "provide_effective_remedy_required": regulated(
            ["tribunal", "violation"], "obligation",
            "The tribunal is required to provide the victim of the violation with an effective remedy",
            "{0} provide the victim of {1} with an effective remedy")},
    rule=norm("tribunal-provides-effective-remedy", "provide_effective_remedy_required", True,
              And(And(Unary("is_national", V1), Binary(_COMPETENT, V1, V0)), Unary("violates_granted_fundamental_right", V0))),
    open=["effective", "competent", "fundamental_rights_granted"], soft=False,
    witnesses=[
        ({"tribunal": ["t0", "t1", "t2"], "violation": ["v0", "v1"]},
         {"is_national": [["t0"], ["t1"]], _COMPETENT: [["t0", "v0"], ["t1", "v1"], ["t2", "v0"]],
          "violates_granted_fundamental_right": [["v0"], ["v1"]]},
         [("provide_effective_remedy_required", ("t0", "v0"), ("SETTLED", True)),
          ("provide_effective_remedy_required", ("t1", "v1"), ("SETTLED", True)),
          ("provide_effective_remedy_required", ("t0", "v1"), ("UNDECIDED", None)),
          ("provide_effective_remedy_required", ("t1", "v0"), ("UNDECIDED", None)),
          ("provide_effective_remedy_required", ("t2", "v0"), ("UNDECIDED", None))])]),
    "Article 8 read as a duty of a competent national tribunal to provide the victim of an act violating a fundamental right with an "
    "effective remedy. Competence is a relation between the tribunal and the violation (the base predicate 'is competent for'; the "
    "open term competent says what it is): a tribunal that is competent for one violation owes nothing, by this rule, for a violation "
    "it is not competent for, which is UNDECIDED. National is a property of the tribunal.")

# ---- u098: Article 26(1) -----------------------------------------------------------------------------------------------
_SCOPE = "elementary_education_is_compulsory_for"
_SCOPE_BASE = base(["person"], "Elementary education is compulsory for the person (for whom it is compulsory, up to what age and until "
                   "what completion is the open term compulsory)", "elementary education is compulsory for {0}")
add("u098", "person_attends", U.scoped_person_duty(
    "u098", "person_attends", "attend_compulsory_elementary_education_required", "{0} attend compulsory elementary education",
    "The person is required to attend elementary education that is compulsory for the person", _SCOPE,
    _SCOPE_BASE["description"], _SCOPE_BASE["verbalisation"], ["compulsory"]),
    "Article 26(1) read as a duty on a person to attend the elementary education that is compulsory for them. The duty applies only to "
    "a person for whom elementary education is compulsory (the base predicate 'elementary education is compulsory for'; who that is, "
    "up to what age and until what completion are factors of the open term compulsory, so none is invented); for any other person "
    "the case is UNDECIDED, so no duty is placed on those the compulsion does not reach.")


def _guardian_duty():
    rel = "is_parent_or_guardian_of"
    stem = "see_to_compulsory_elementary_education_required"
    spec = dict(
        sorts={"guardian": sort("guardian", "guardians", "a parent or guardian of a person"), "person": PERSON},
        predicates={rel: base(["guardian", "person"], "The guardian is a parent or guardian of the person",
                              "{0} is a parent or guardian of {1}"),
                    _SCOPE: _SCOPE_BASE,
                    stem: regulated(["guardian", "person"], "obligation",
                                    "The parent or guardian is required to see that the person in their care attends elementary "
                                    "education that is compulsory for the person",
                                    "{0} see that {1} attends compulsory elementary education")},
        rule=norm("u098-guardian-ensures", stem, True, And(Binary(rel, V1, V0), Unary(_SCOPE, V0))),
        open=["compulsory"], soft=False)
    spec["witnesses"] = [(
        {"guardian": ["g0", "g1"], "person": ["p0", "p1"]},
        {rel: [["g0", "p0"], ["g0", "p1"]], _SCOPE: [["p0"]]},
        [(stem, ("g0", "p0"), ("SETTLED", True)),
         (stem, ("g0", "p1"), ("UNDECIDED", None)),       # in care, but education is not compulsory for p1
         (stem, ("g1", "p0"), ("UNDECIDED", None)),       # compulsory for p0, but g1 is not p0's guardian
         (stem, ("g1", "p1"), ("UNDECIDED", None))])]
    return spec


add("u098", "guardian_ensures", _guardian_duty(),
    "Article 26(1) read as a duty of a parent or guardian to see that the person in their care attends the elementary education that "
    "is compulsory for that person. The duty applies only where the guardian is a parent or guardian of the person (the base relation "
    "'is a parent or guardian of') and elementary education is compulsory for the person (the base predicate, open term compulsory); "
    "in any other case it is UNDECIDED.")


# ---- the rights as a case sort: the source's whole phrase is the noun of the right ------------------------------------------------
# unit -> (phrase after "the right", the unit's opens)
# the noun the English view can print (no comma, no 'and', no article, no 'each'): the source's words with 'as well as' for 'and'
# and without commas and articles; the sort's description keeps the source's phrase exactly. u048's phrase has 'each state', which
# the view cannot print as a noun, so its view falls back to 'entity of sort "right"' (the description carries the phrase)
RIGHT_NOUN = {
    "u048": "to freedom of movement as well as residence within the borders of each state",
    "u063": "to own property alone as well as in association with others",
    "u066": "to freedom of thought conscience as well as religion",
    "u073": "to freedom of peaceful assembly as well as association",
    "u084a": "to work",
    "u105a": "freely to participate in cultural life of community",
}
RIGHT_PHRASE = {
    "u048": "to freedom of movement and residence within the borders of each state",
    "u063": "to own property alone as well as in association with others",
    "u066": "to freedom of thought, conscience and religion",
    "u073": "to freedom of peaceful assembly and association",
    "u084a": "to work",
    "u105a": "freely to participate in the cultural life of the community",
}


def right_case(uid):
    phrase = RIGHT_PHRASE[uid]
    case = case_sort(f"right {RIGHT_NOUN[uid]}", f"rights {RIGHT_NOUN[uid]}",
                     f"one person's right {phrase} (one element for each holder of the right the sentence gives to everyone)",
                     {}, ("top",), [[]])
    case["name"] = "right"
    return case


def right_duty(uid, cid, stem, act, wording):
    kind, neg, pos, lib, opens = U.RIGHTS[uid]
    return duty(uid, cid, stem, act, f"The bearer is required to {wording} the right {RIGHT_PHRASE[uid]}",
                bearer="state" if cid.startswith("state") else "anyone", arity="case", case=right_case(uid), opens=opens)


_NOTE = ("The duty is over the right itself (one person's right {phrase}): the sort's description carries the source's whole phrase, so "
         "no word of it is dropped for the 80-byte act limit; the noun the English view prints writes 'as well as' for 'and' and leaves "
         "out commas and articles (the view's limit), and for u048 the view falls back to a generic noun. ")
for uid in ("u048", "u063"):
    phrase = RIGHT_PHRASE[uid]
    note = _NOTE.format(phrase=phrase)
    add(uid, "state_negative", right_duty(uid, "state_negative", f"avoid_denying_right_{uid}_required", "{0} avoid denying {1}",
                                          "avoid denying"),
        note + "Claim reading as noninterference: every State must avoid denying each person's right; the source names no bearer and "
               "no polarity, so this is the translator's candidate.")
    add(uid, "anyone_negative", right_duty(uid, "anyone_negative", f"avoid_denying_right_{uid}_required", "{0} avoid denying {1}",
                                           "avoid denying"),
        note + "Claim reading as noninterference: every State, group and person must avoid denying each person's right; the source "
               "names no bearer and no polarity, so this is the translator's candidate.")
    add(uid, "state_positive", right_duty(uid, "state_positive", f"secure_right_{uid}_required", "{0} secure {1}", "secure"),
        note + "Claim reading as protection: every State must secure each person's right (the right itself, not any particular "
               "exercise of it: nobody is required to become an owner, to move, or to reside anywhere because of this reading).")
for uid in ("u048", "u063", *RESTORED_COMBINED):
    note = _NOTE.format(phrase=RIGHT_PHRASE[uid])
    add(uid, "state_combined", right_duty(uid, "state_combined", f"avoid_denying_and_secure_right_{uid}_required",
                                          "{0} avoid denying as well as secure {1}", "avoid denying as well as secure"),
        note + "Claim reading combining noninterference with protection in one duty: every State must avoid denying as well as secure "
               "each person's right. The two parts bind together (one act phrase), unlike the separate noninterference and protection "
               "candidates, which are alternatives.")
