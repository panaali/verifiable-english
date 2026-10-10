"""Repairs of the 2026-10-08T1800Z audit (AUDIT.md of run-20261008T1800Z: 16/20 faithful; u020 u052 u055 u098 rejected).

Rules applied (lead, 2026-10-08/09): READINGS COME FROM THE WORDS ONLY; RIGHTS ARE NOT DUTIES TO PROVIDE; never list a question the text
does not raise; an impersonal source gets no personal obligation.

* u020: the sort and the predicate said the distinction was made "against" a person (an adverse-treatment restriction the source does
  not state: "no distinction shall be made on the basis of ..." covers any distinction on those grounds). The distinction is now any
  distinction made on the basis of the status of the country or territory to which a person belongs.
* u052: the open-term factors were questions the sentence does not raise (who classifies crimes, which purposes "count", the authenticity
  of elections). Each term now has one factor in the sentence's own words.
* u055: "arbitrary" carried legality / reasonableness / procedural safeguards (outside knowledge): one factor in the words. The two scopes of
  "arbitrarily" regulated two different act predicates after the merge renamed one of them (an artefact of integrate.py's act rewrite, now
  applied before the name test): both readings now regulate the same act, only the guard (the scope of "arbitrarily") differs.
* u098: "Elementary education shall be compulsory." is an impersonal passive. The personal reading ("every person must receive elementary
  education") gave a recipient scope and a personal duty the sentence does not state; it is replaced by the bearer-less obligation over the
  thing the sentence is about (elementary education is required to be compulsory), as the sibling units u099a/u099b/u100a/u100b state their
  passives, and the unit is OPEN on the term `compulsory` (one factor: what it is for elementary education to be compulsory).
* u054 (same defect as the words-only rule): the open term `bearer_of_the_nationality_duty` asked which State must grant the nationality, a
  duty-bearer question a right does not raise; it is gone and the predicate description no longer mentions a duty.
* the same kind of added question is removed from the factors of free_and_full_consent (who the intending spouses are), persecution
  (whether persecution that is only threatened counts), protection_of_the_family (what society owes as distinct from the State),
  duties_to_the_community (which duties the community may require), aimed_at_destruction_of_rights (whether purpose or effect decides)
  and merit (who judges merit).
"""
from __future__ import annotations

import udhr_specs as U
from udhr_specs import V0, ast, case_bases, case_sort, holds, norm, prohibition, regulated, slug

UNSPEC = U.UNSPEC


def forbidden(unit, cid, stem, act, desc, case, opens):
    """'No distinction shall be made ...': the act itself is not permitted; the case sort's guard picks the forbidden cases."""
    return prohibition(unit, cid, stem, act, desc, case, opens)


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


NOBEARER = ("The sentence names no one who must act, so this reading names no bearer: nothing is said of any State, group or person, "
            "and no one is made to do anything by it.")

# ---- u020 -------------------------------------------------------------------------------------------------------------------
U020_CASE = case_sort(
    "distinction", "distinctions",
    "one distinction made on the basis of the status of the country or territory to which a person belongs, whether it be independent, "
    "trust, non-self-governing or under any other limitation of sovereignty",
    {"based_on_political_status": "The distinction is based on the political status of the country or territory",
     "based_on_jurisdictional_status": "The distinction is based on the jurisdictional status of the country or territory",
     "based_on_international_status": "The distinction is based on the international status of the country or territory"},
    U.OR(("p", "based_on_political_status"), ("p", "based_on_jurisdictional_status"), ("p", "based_on_international_status")),
    [["based_on_political_status"], ["based_on_jurisdictional_status"], ["based_on_international_status"], []])
U020 = forbidden("u020", "prohibited", "distinction_by_country_status_permitted", "{0} be made",
                 "The distinction on the basis of the status of the country or territory to which a person belongs is permitted to "
                 "be made", U020_CASE, ["status_of_country_or_territory"])
U020_WHY = ("Article 2, second sentence: 'no distinction shall be made on the basis of the political, jurisdictional or international "
            "status of the country or territory to which a person belongs': any distinction on one of those three statuses is not "
            "permitted (the three statuses are the guard's explicit list; 'whether independent, trust, non-self-governing or under any "
            "other limitation of sovereignty' sets no condition); the sentence does not say whom the distinction is made against. "
            + NOBEARER + " " + UNSPEC)

# ---- u098 -------------------------------------------------------------------------------------------------------------------
U.VERB["is_elementary"] = "{0} is elementary"
KIND = case_sort(
    "education kind", "education kinds", "one kind of education",
    {"is_elementary": "The education is elementary"},
    ("p", "is_elementary"), [["is_elementary"], []])
U098 = unassigned("u098", "unassigned", "elementary_education_compulsory_required", "{0} be compulsory",
                  "The education is required to be compulsory", case=KIND, opens=["compulsory"])
U098_WHY = ("Article 26(1), 'Elementary education shall be compulsory': an impersonal passive. Elementary education (the kind of "
            "education the guard picks out) is required to be compulsory, of no stated party; the sentence says neither for whom it is "
            "compulsory nor who makes it so, and this reading adds neither. What it is for education to be compulsory is the open term. "
            + NOBEARER + " " + UNSPEC)
U098_TERM = {"arguments": [], "decided_by": "unstated", "factors": ["what it is for elementary education to be compulsory"],
             "jurisdiction": "universal", "name": "compulsory", "necessary": [], "precedents": [], "sufficient": [], "version": 1}

# ---- open-term factors, in the words of the sentences that use them -------------------------------------------------------------
NEW_FACTORS = {
    "arbitrary": ["what it is for an act to be arbitrary"],
    "genuine": ["what it is for a prosecution to arise genuinely from a crime or an act"],
    "non_political_crime": ["what makes a crime non-political"],
    "contrary_to_un_purposes_and_principles": ["what it is to be contrary to the purposes and principles of the United Nations"],
    "persecution": ["what counts as persecution"],
    "free_and_full_consent": ["what makes consent free", "what makes consent full"],
    "protection_of_the_family": ["what counts as protection of the family"],
    "duties_to_the_community": ["which duties are meant"],
    "aimed_at_destruction_of_rights": ["what it is to aim at the destruction of a right or freedom"],
    "merit": ["what counts as merit"],
}
DROP_TERMS = ["bearer_of_the_nationality_duty"]
OPEN_OF_UNIT = {"u054": []}
REASON = {
    "u020": "the distinction was made 'against' a person: an adverse-treatment restriction the source does not state; the distinction is "
            "now any distinction made on the basis of the status of the country or territory to which a person belongs",
    "u098": "the personal reading (every person must receive elementary education) gave a recipient scope and a personal duty the "
            "impersonal sentence does not state; it is replaced by the bearer-less obligation that elementary education be compulsory, "
            "with the open term `compulsory` (one factor)",
}
AUDIT_REJECTED = ["u020", "u052", "u055", "u098"]
FACTOR_REPAIRED = {
    "u052": "open-term factors in the sentence's own words (who classifies crimes, which purposes 'count', election authenticity are gone)",
    "u055": "open-term factor in the words (legality / reasonableness / procedural safeguards are gone); both scope readings now regulate "
            "one act",
}
SAME_DEFECT = {
    "u037": "factor of `arbitrary` (shared term)", "u045a": "factor of `arbitrary` (shared term)", "u046": "factor of `arbitrary` (shared term)",
    "u064": "factor of `arbitrary` (shared term)", "u054": "duty-bearer open term removed from a right",
    "u051": "factor of `persecution`", "u059": "factor of `free_and_full_consent`", "u061": "factor of `protection_of_the_family`",
    "u110": "factor of `duties_to_the_community`", "u114": "factor of `aimed_at_destruction_of_rights`", "u099b": "factor of `merit`",
    "u112": "factor of `contrary_to_un_purposes_and_principles`",
}

# ---- positive claims still standing (found by this run's self-check against the lead's rule 'rights are not duties to provide') -----
# 'Everyone has the right to X' says who holds the right and nothing more. These candidates made someone secure, give or protect the
# object of the right (an outcome to be provided); the 2026-10-08 repairs removed the same kind from twenty other units.
REMOVE = {
    "u032": ["claim"], "u033a": ["claim"], "u033b": ["claim"], "u046": ["claim_arbitrary"], "u077": ["claim_nationality", "claim_residence"],
    "u081": ["claim"], "u084c": ["claim"], "u084d": ["claim"],
}
REMOVE_REASON = ("the claim reading is gone: it required of no stated party that the object of the right be given, secured or protected "
                 "(a duty to provide), which 'has the right to X' / 'is entitled to X' does not say; the entitlement"
                 " (and, for u077, its two readings of 'his country') remain")
