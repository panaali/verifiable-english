"""Repairs of the 2026-10-08 audits of run-20261008T0600Z (AUDIT.md: sampled 15/20, full audit of the other 34: 17/34 faithful).

Rules applied (lead, 2026-10-08): RIGHTS ARE NOT DUTIES TO PROVIDE; READINGS COME FROM THE WORDS ONLY; never list an unsettled
question that the text does not raise; do not narrow a general phrase; keep what the text states as stated.

* "has the right to X" keeps the entitlement, the liberty where X is something one does, and the claim that X not be denied
  (bearer-less). The `claim_positive` and `claim_combined` readings (someone must enable, secure, assist or provide X) are gone
  everywhere, also from u096 (education), which the audit accepted but which had the same defect.
* u035: the tribunal claim distributes a remedy to every competent tribunal for every qualifying violation, which the text does not
  state: gone; the entitlement is the single reading.
* u046: `*_any` ignored 'arbitrary' in "such interference" (u045a: *arbitrary* interference): gone.
* u081: the resources clause is part of the entitlement to realization (u082), not of the right to social security: that reading is gone,
  and so is its open term from u081.
* u098: the guard 'education is compulsory for the person' made the duty depend on what it states; the single reading is now unguarded:
  every person must receive elementary education (of no stated party); the open term `compulsory` listed questions the text does not
  raise (who makes it compulsory, up to what age) and is gone.
* u100b: the open term `rights_and_freedoms_set_forth` narrowed "human rights and fundamental freedoms" to the Declaration's: gone.
* open-term factors the text does not raise are removed: u020 (whether a territory's status is the country's), u027 (whether punishment
  is covered: "treatment or punishment" is stated), u110 (whether the community exists: "the community in which ..." takes it for granted).
"""
from __future__ import annotations

import udhr_specs as U
from udhr_specs import PERSON, norm, regulated, slug, sort
from ve.ast import Top

UNSPEC = U.UNSPEC
NOBEARER = ("The words name no one who must act, so this reading names no bearer and mentions no State, group or person; nothing "
            "is said of anyone's duty.")


def claim(unit, cid, stem, act, opens):
    """An obligation whose one argument is the person: 'it is required, of no stated party, that the person <act>'."""
    assert len(act.encode()) <= 80, (unit, cid, len(act.encode()), act)
    desc = "It is required, of no stated party, that the person " + act[len("{0} "):]
    spec = dict(sorts={"person": PERSON}, predicates={stem: regulated(["person"], "obligation", desc, act)},
                rule=norm(slug(f"{unit}-{cid}"), stem, True, Top()), open=list(opens), soft=False)
    spec["witnesses"] = [({"person": ["p0"]}, {}, [(stem, ("p0",), ("SETTLED", True))])]
    return spec


REMOVE = {}
for _u in ("u022a", "u022b", "u022c", "u048", "u063", "u066", "u070", "u073", "u084a", "u084b", "u096", "u105a", "u105b", "u105c"):
    REMOVE[_u] = ["claim_positive", "claim_combined"]
REMOVE["u087"] = ["claim_positive"]
REMOVE["u046"] = ["entitlement_any", "claim_any"]
REMOVE["u035"] = ["tribunal_claim"]
REMOVE["u081"] = ["claim_within_resources"]

REASON = {u: "the claim readings that make someone enable, secure, assist or provide the object of the right (claim_positive, "
             "claim_combined) are gone: 'has the right to X' says who holds the right and nothing more; the entitlement, the "
             "negative claim and the liberty (where X is something one does) remain" for u in REMOVE}
REASON["u087"] = REASON["u087"].replace("claim_positive, claim_combined", "claim_positive")
REASON["u046"] = ("the readings `entitlement_any` and `claim_any` are gone: they dropped 'arbitrary' from 'such interference' (Article 12: "
                  "arbitrary interference), extending the right to non-arbitrary interference; the two readings left keep 'arbitrary'")
REASON["u035"] = ("the `tribunal_claim` reading is gone: it required every competent national tribunal to give a remedy for every "
                  "qualifying violation, a distribution the text does not state; the entitlement (everyone has the right to an effective "
                  "remedy by the competent national tribunals) is the one reading the words support")
REASON["u081"] = ("the `claim_within_resources` reading is gone: it moved the clause 'in accordance with the organization and resources of "
                  "each State', which belongs to the entitlement to realization (u082), into the right to social security, and dropped "
                  "'organization'; the open term organization_and_resources_of_each_state leaves u081")

# new or replaced companions: unit -> [(candidate id, builder args, why)]
NEW = {}
U098_ACT = "{0} receive elementary education"
NEW["u098"] = [("person_receives", claim("u098", "person_receives", "elementary_education_received_required", U098_ACT, []),
                "Article 26(1), 'Elementary education shall be compulsory': what is compulsory is required of those it applies to; the "
                "words say neither for whom nor until what age nor who makes it compulsory, so the reading is unguarded: every person is "
                "required to receive elementary education, of no stated party. " + UNSPEC)]
REASON["u098"] = ("the guard 'elementary education is compulsory for the person' is gone (it made attendance required only where education "
                  "was already compulsory for someone, allowing no compulsory education at all) and so is the open term `compulsory`, "
                  "which listed who makes it compulsory and up to what age, questions the text does not raise; one reading is left: every "
                  "person is required to receive elementary education")

COURSE = "course_of_education"
_u100b = dict(
    sorts={COURSE: sort("course of education", "courses of education", "one course of education")},
    predicates={"education_directed_to_respect_for_rights_required": regulated(
        [COURSE], "obligation",
        "The course of education is required to be directed to the strengthening of respect for human rights and fundamental "
        "freedoms", "{0} be directed to strengthen respect of human rights plus fundamental freedoms")},
    rule=norm("u100b-unassigned", "education_directed_to_respect_for_rights_required", True, Top()),
    open=[], soft=False,
    witnesses=[({COURSE: ["c0"]}, {}, [("education_directed_to_respect_for_rights_required", ("c0",), ("SETTLED", True))])])
NEW["u100b"] = [("unassigned", _u100b,
                 "Article 26(2): 'and to the strengthening of respect for human rights and fundamental freedoms', with no one assigned to "
                 "direct education; the subject and 'shall' are carried from u100a (not a checked reference): every course of education is "
                 "required to be directed so. The words say 'human rights and fundamental freedoms' generally, so no question about which "
                 "rights is raised. " + NOBEARER + " " + UNSPEC)]
REASON["u100b"] = ("the open term `rights_and_freedoms_set_forth` is gone: it narrowed the general phrase 'human rights and fundamental "
                   "freedoms' to those set forth in the Declaration; the act phrase and the reading are otherwise as before")

# open terms: unit -> new unit meaning; term -> new factors; terms dropped when unused
OPEN_OF_UNIT = {"u081": ["social_security"], "u098": [], "u100b": []}
DROP_TERMS = ["compulsory"]                    # `organization_and_resources_of_each_state` stays: u082 / u114? checked in repair7.py
NEW_FACTORS = {
    "status_of_country_or_territory": ["what the political status of the country or territory is",
                                       "what the jurisdictional status of the country or territory is",
                                       "what the international status of the country or territory is"],
    "ill_treatment": ["which treatment or punishment is cruel", "which treatment or punishment is inhuman",
                      "which treatment or punishment is degrading"],
    "community_of_full_development": ["which community that is, for each person",
                                      "whether it is the same community for every person"],
}
REPAIR_NOTES = {
    "u020": "open-term factor removed: whether the status of a territory counts as the country's (the text names both)",
    "u027": "open-term factor removed: whether punishment is covered (the text says 'treatment or punishment')",
    "u110": "open-term factor removed: whether the community exists (the sentence takes it for granted)",
}
REPAIRED = sorted({*REMOVE, *NEW, *REPAIR_NOTES})
AUDIT_REJECTED = sorted("u020 u022a u046 u063 u105b u022b u022c u027 u035 u048 u066 u070 u073 u081 u084a u084b u087 u098 u100b u105a u105c u110".split())
