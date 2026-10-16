"""Repaired candidates of the units the 2026-10-04T1800Z audit rejected, and of the units that carry the same defect.

The audit (previous-1800Z/AUDIT.md) rejected u033a, u073, u084a, u084c and u100b (15 of 20 sampled units faithful). Its reasons:

* u033a, u084c, u073, u084a: the "anyone" positive candidates made every State, group and person responsible for giving everyone
  protection, conditions of work, the freedoms of assembly and association, or work, which the source does not assign; no
  candidate was an entitlement with the responsibility left unspecified; u073 and u084a had no reading combining noninterference
  with protection. u084a's positive candidate also turned the right to work into an obligation to provide work.
* u100b: every person and group was given an unconditional duty to direct education; the rendered act dropped "fundamental" from
  "fundamental freedoms".

Repair, the same pattern that the previous run applied to Article 3, Article 12(2), 15(1) and 23(4) (and that the audit accepted
for u022a): the universal positive candidate is removed; a bearer-less entitlement (a plain regulated predicate the rule makes
true of every holder) is added; the State candidates stay, with a State reading that combines noninterference with protection
where the right has both; noninterference stays offered for every State, group and person; liberties stay.

The 16 other right units listed as a known gap in the previous summary (u029, u032, u033b, u048, u049, u063, u066, u070, u081,
u084b, u084d, u096, u105a-c) and u100a (the sentence before u100b) are repaired the same way, not because they were sampled but
because the audit's reasons apply to them word for word. Candidates that keep their meaning are reused byte for byte from
udhr_specs.CANDIDATES.
"""
from __future__ import annotations

import re

import udhr_specs as U
from repair_specs import entitlement
from udhr_specs import OR, Top, V0, base, case_sort, duty, norm, regulated, sort

AUDIT_REJECTED = ["u033a", "u073", "u084a", "u084c", "u100b"]
SAME_DEFECT = ["u029", "u032", "u033b", "u048", "u049", "u063", "u066", "u070", "u081", "u084b", "u084d", "u096", "u105a",
               "u105b", "u105c", "u100a"]
REPAIRED = sorted(AUDIT_REJECTED + SAME_DEFECT)
CANDIDATES: dict[str, list[tuple[str, dict, str]]] = {}
UNSPEC = U.UNSPEC


def add(unit, cid, spec, why):
    CANDIDATES.setdefault(unit, []).append((cid, spec, why + " " + UNSPEC))


# entitlement wording per right unit: (predicate name, verbalisation, description)
ENTITLEMENT = {
    "u029": ("has_the_right_to_recognition_as_a_person", "{0} has the right to recognition everywhere as a person before the law",
             "The person has the right to recognition everywhere as a person before the law"),
    "u032": ("is_entitled_to_equal_protection_of_the_law", "{0} is entitled to equal protection of the law without any discrimination",
             "The person is entitled to equal protection of the law without any discrimination"),
    "u033a": ("is_entitled_to_protection_against_discrimination",
              "{0} is entitled to equal protection against any discrimination in violation of this Declaration",
              "The person is entitled to equal protection against any discrimination in violation of this Declaration"),
    "u033b": ("is_entitled_to_protection_against_incitement",
              "{0} is entitled to equal protection against any incitement to such discrimination",
              "The person is entitled to equal protection against any incitement to discrimination in violation of this Declaration"),
    "u048": ("has_the_right_to_movement_and_residence",
             "{0} has the right to freedom of movement as well as residence within the borders of each state",
             "The person has the right to freedom of movement and residence within the borders of each state"),
    "u049": ("has_the_right_to_leave_and_return",
             "{0} has the right to leave any country including their own as well as to return to their country",
             "The person has the right to leave any country, including their own, and to return to their country"),
    "u063": ("has_the_right_to_own_property", "{0} has the right to own property alone as well as in association with others",
             "The person has the right to own property alone as well as in association with others"),
    "u066": ("has_the_right_to_thought_conscience_religion",
             "{0} has the right to freedom of thought conscience as well as religion",
             "The person has the right to freedom of thought, conscience and religion"),
    "u070": ("has_the_right_to_opinion_and_expression", "{0} has the right to freedom of opinion as well as expression",
             "The person has the right to freedom of opinion and expression"),
    "u073": ("has_the_right_to_assembly_and_association",
             "{0} has the right to freedom of peaceful assembly as well as association",
             "The person has the right to freedom of peaceful assembly and association"),
    "u081": ("has_the_right_to_social_security", "{0} has the right to social security",
             "The person has the right to social security"),
    "u084a": ("has_the_right_to_work", "{0} has the right to work", "The person has the right to work"),
    "u084b": ("has_the_right_to_free_choice_of_employment", "{0} has the right to free choice of employment",
              "The person has the right to free choice of employment"),
    "u084c": ("has_the_right_to_just_and_favourable_conditions_of_work",
              "{0} has the right to just as well as favourable conditions of work",
              "The person has the right to just and favourable conditions of work"),
    "u084d": ("has_the_right_to_protection_against_unemployment", "{0} has the right to protection against unemployment",
              "The person has the right to protection against unemployment"),
    "u096": ("has_the_right_to_education", "{0} has the right to education", "The person has the right to education"),
    "u105a": ("has_the_right_to_take_part_in_cultural_life",
              "{0} has the right freely to take part in the cultural life of the community",
              "The person has the right freely to take part in the cultural life of the community"),
    "u105b": ("has_the_right_to_enjoy_the_arts", "{0} has the right freely to enjoy the arts",
              "The person has the right freely to enjoy the arts"),
    "u105c": ("has_the_right_to_share_in_scientific_advancement",
              "{0} has the right freely to share in scientific advancement as well as its benefits",
              "The person has the right freely to share in scientific advancement and its benefits"),
}

# the State reading that combines noninterference with protection in one act phrase (80 bytes at most; the connectives or
# "freedom of" that do not fit are dropped from this act only, and the candidate's admission text says so)
COMBINED = {
    "u048": ("avoid_denying_and_secure_movement_and_residence_required",
             "{0} avoid denying as well as secure {1} freedom of movement as well as residence", ""),
    "u063": ("avoid_barring_and_secure_property_required",
             "{0} avoid barring as well as secure {1} owning property alone as well as jointly",
             " 'with others' is shortened to 'jointly'."),
    "u066": ("avoid_and_secure_thought_conscience_religion_required",
             "{0} avoid denying as well as secure {1} freedom of thought conscience religion",
             " The three freedoms are listed without a connective."),
    "u070": ("avoid_denying_and_secure_opinion_and_expression_required",
             "{0} avoid denying as well as secure {1} freedom of opinion as well as expression", ""),
    "u073": ("avoid_and_secure_assembly_and_association_required",
             "{0} avoid denying as well as secure {1} peaceful assembly as well as association",
             " 'Freedom of' is left out of this act phrase (80-byte limit); the entitlement and the other candidates carry it."),
    "u084a": ("avoid_barring_and_enable_work_required", "{0} avoid barring as well as enable work by {1}", ""),
    "u084b": ("avoid_and_secure_free_choice_of_employment_required",
              "{0} avoid restricting as well as secure the free choice of employment of {1}", ""),
    "u096": ("avoid_barring_and_secure_education_required", "{0} avoid barring as well as secure {1} education", ""),
    "u105a": ("avoid_barring_and_secure_cultural_life_required",
              "{0} avoid barring as well as secure {1} free participation in cultural life",
              " 'Of the community' is left out of this act phrase (80-byte limit); the other candidates carry it."),
    "u105b": ("avoid_barring_and_secure_enjoyment_of_the_arts_required",
              "{0} avoid barring as well as secure {1} the enjoyment of the arts", ""),
}
# units whose single "claim" candidate is a noninterference duty (so every State, group and person remains a bearer)
NEGATIVE_CLAIM = {"u049"}
OPEN_TERMS = {uid: spec[4] for uid, spec in U.RIGHTS.items()}

_HAS_NO_BEARER = ("the source names no one who must do anything, so the candidate names no bearer (a plain regulated predicate the "
                  "rule makes true of every person); the responsibility stays unspecified")


def _text(uid):
    return U.RIGHT_TEXT[uid]


for uid in sorted(set(REPAIRED) - {"u100a", "u100b"}):
    kind, neg, pos, lib, opens = U.RIGHTS[uid]
    text = _text(uid)
    stem, verb, desc = ENTITLEMENT[uid]
    add(uid, "entitlement", entitlement(uid, "entitlement", stem, verb, desc, opens),
        f"Entitlement reading of {text}: every person has it; {_HAS_NO_BEARER}. This is what 'everyone has the right' says "
        "without choosing who must act.")
    old = {cid: (spec, why) for cid, spec, why in U.CANDIDATES[uid]}
    keep = ["state_negative", "anyone_negative", "state_positive", "state_claim", "state_claim_within_resources", "liberty"]
    if uid in NEGATIVE_CLAIM:
        keep.append("anyone_claim")
    if uid == "u084a":
        keep.remove("state_positive")
    for cid in keep:
        if cid in old:
            add_spec, add_why = old[cid]
            CANDIDATES.setdefault(uid, []).append((cid, add_spec, add_why))
    if uid == "u084a":
        add(uid, "state_positive",
            duty(uid, "state_positive", "enable_work_required", "{0} enable {1} to work",
                 "The bearer is required to enable the person to work", bearer="state", arity="person", opens=opens),
            "Claim reading of the right to work as enabling: every State must enable each holder to work (the opportunity, not the "
            "provision of a job). Only States carry the positive duty; a universal duty of every State, group and person to provide "
            "work, or to provide a job to each holder, would strengthen the source.")
    if uid in COMBINED:
        cstem, cact, note = COMBINED[uid]
        add(uid, "state_combined",
            duty(uid, "state_combined", cstem, cact, f"The bearer is required to {cact[len('{0} '):].replace('{1}', 'the person')}",
                 bearer="state", arity="person", opens=opens),
            f"Claim reading of {text} combining noninterference with protection: every State must {cact[len('{0} '):].replace('{1}', 'each holder')} "
            f"(one act phrase, so the combination is one duty).{note}")

# ---- u100a, u100b: Article 26(2) ------------------------------------------------------------------------------------------
_EDUCATION = sort("education", "educations", "one provision of education")
CANDIDATES.setdefault("u100a", []).extend(c for c in U.CANDIDATES["u100a"] if c[0] == "state")
_stem = "is_directed_to_full_development_of_the_personality"
add("u100a", "education",
    dict(sorts={"education": _EDUCATION},
         predicates={_stem: {"arguments": ["education"],
                             "description": "The education is directed to the full development of the human personality",
                             "verbalisation": "{0} is directed to the full development of the human personality",
                             "regulated": {"role": "plain", "default": "unspecified"}}},
         rule=norm("education-directed-to-development", _stem, True, Top()),
         open=["full_development_of_the_human_personality"], soft=False,
         witnesses=[({"education": ["e0"]}, {}, [(_stem, ("e0",), ("SETTLED", True))])]),
    "Article 26(2), first purpose, as a statement about education itself: education is directed to the full development of the human "
    "personality. The passive names no one who directs it, so the candidate names no bearer (a plain regulated predicate the rule "
    "makes true of every education); the responsibility stays unspecified. The universal 'every State, group and person must direct "
    "education' candidate of the previous run is removed.")

_OBJECT = case_sort(
    "object of respect", "objects of respect",
    "one object of the respect that education is to strengthen: the human rights, or the fundamental freedoms",
    {"is_human_rights": "The object is the human rights", "is_fundamental_freedoms": "The object is the fundamental freedoms"},
    OR(("p", "is_human_rights"), ("p", "is_fundamental_freedoms")), [["is_human_rights"], ["is_fundamental_freedoms"], []])
add("u100b", "state",
    duty("u100b", "state", "direct_education_to_strengthen_respect_required", "{0} direct education to strengthen respect of {1}",
         "The bearer is required to direct education to strengthen respect of the human rights and of the fundamental freedoms",
         bearer="state", arity="case", case=_OBJECT, opens=["rights_and_freedoms_set_forth"]),
    "Article 26(2), second purpose: 'and to the strengthening of respect for human rights and fundamental freedoms' read as a duty on "
    "every State to direct education to strengthen respect of the human rights, and of the fundamental freedoms (the two objects are "
    "the guard's explicit list; 'fundamental' is in the second object). The passive names no one who directs education; only States "
    "carry the duty here, so no universal individual duty is invented. The subject and 'shall' are carried from u100a (not a checked "
    "reference).")
add("u100b", "education",
    entitlement("u100b", "education", "education_strengthens_respect_of", "education is directed to strengthen respect of {0}",
                "Education is directed to strengthen respect of the object", ["rights_and_freedoms_set_forth"], case=_OBJECT),
    "Article 26(2), second purpose, as a statement about education itself: education is directed to strengthen respect of the human "
    "rights, and of the fundamental freedoms. The passive names no one who directs it, so the candidate names no bearer (a plain "
    "regulated predicate the rule makes true of each object listed); the responsibility stays unspecified.")

REASON = {
    "u033a": "the 'anyone' candidate made every State, group and person give everyone equal protection against discrimination; "
             "now an entitlement with no bearer and the State candidate",
    "u073": "the 'anyone' positive candidate made everyone responsible for securing assembly and association, and neither an "
            "entitlement nor a noninterference-with-protection reading existed; now both, the State positive stays",
    "u084a": "the positive candidates obliged every person and group (and the State, to provide work) to give everyone work; now an "
             "entitlement, a State duty to enable work, and a State reading combining noninterference with enabling",
    "u084c": "the 'anyone' candidate made every State, group and person secure just and favourable conditions of work; now an "
             "entitlement with no bearer and the State candidate",
    "u100b": "every person and group was given an unconditional duty to direct education, and the act dropped 'fundamental' from "
             "'fundamental freedoms'; now a State duty over two listed objects (human rights; fundamental freedoms) and a bearer-less "
             "statement about education",
}
_SAME = ("same defect as the rejected right units (an 'anyone' positive candidate no source sentence assigns, no entitlement with the "
         "responsibility left unspecified): ")
for _u in SAME_DEFECT:
    if _u == "u100a":
        REASON[_u] = _SAME + "now a State duty and a bearer-less statement about education; the universal candidate is removed"
    else:
        _kind = U.RIGHTS[_u][0]
        REASON[_u] = _SAME + ("the universal positive candidate is removed, an entitlement is added" +
                              (", with a State reading combining noninterference with protection" if _u in COMBINED else ""))
