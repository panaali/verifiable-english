"""Norm candidates under norm-defaults@0: every completion is `unspecified`, every scope sits in a checked guard.

The 2026-10-01 run kept a prohibition or a duty as a norm over a sort whose *description* carried the source's
conditions (prose-scoped), with a declared completion (`allow`/`deny`) that the source never states. Here the
scope is a guard over declared base predicates and the completion is `unspecified`, so VE reports every case the
text does not decide as UNDECIDED. A document cannot enable norm-defaults@0 together with soft-norms@0 or rights@0
(ve/document.py: "norm-defaults@0 documents on the soft and rights routes await the Lean route"), so these
candidates are companion documents (one unit, source = the unit's exact bytes) cited by the main document's
reading sets, as in companions.py.

Predicates have at most two arguments and act phrases at most 80 bytes of plain words (no and/or/for/if/is/no/not),
so a case argument stands for a whole case (an act, a determination) and a long clause can force UNFORMALISED.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from ve.ast import And, Binary, Not, Or, Top, Unary, Var
from ve.ast import _to_data as data

from companions import SPEC_REVISION, UNSTATED, environment, sort

PROFILES = ("documents@1", "norm-defaults@0", "norms@0", "relational-fol@0")
V0, V1 = Var(0), Var(1)  # the last argument is Var(0), the one before it Var(1)

BEARER = sort("bearer", "bearers", "a State, group or person")
PERSON = sort("person", "people", "a human person")


def base(arguments, description, verbalisation):
    return {"arguments": arguments, "description": description, "verbalisation": verbalisation}


def regulated(arguments, role, description, act):
    return {"arguments": arguments, "description": description,
            "regulated": {"role": role, "default": "unspecified", "act": act}}


ACT = sort("act", "acts", "an act of a State, group or person")
FACES_PERSECUTION = base(
    ["person"],
    "The person suffers persecution or is threatened with it (the open term persecution; whether persecution that is "
    "only threatened counts is one of its factors), whether or not the person has begun to seek asylum",
    "{0} suffers or is threatened with persecution")
VIOLATION = sort("violation", "violations",
                 "one violation of one person's right by one act: the person is its victim, the act is what violated the right")
VIOLATES = base(["violation"], "The violation is of a fundamental right granted to its victim by the constitution or by law",
                "{0} violates a fundamental right granted to its victim by the constitution or by law")


def norm(name, predicate, sign, guard=None):
    return {"norm": {"guard": data(Top() if guard is None else guard), "name": name, "over": [],
                     "predicate": predicate, "sign": sign, "unless": []}}


# Article 29(2): "everyone shall be subject only to such limitations as are determined by law solely for the purpose of
# securing ... and of meeting ...". Repaired after the 2026-10-02T1800Z audit (the duty sat on the right holder and a
# limitation was tied to no person and no right): the duty is on a bearer (a State, or any State, group or person), who
# must avoid imposing a limitation; a limitation here is one limitation on one person's exercise of one right or
# freedom, so the affected person and the right are the element's own (the language has no relation from a limitation to
# a right line: limitation scope names rights, which are open sets). The conditions are necessary, never sufficient:
# the rule bars every limitation that misses a condition and leaves every other limitation open (UNDECIDED).
# Two readings of "solely for the purpose of A and of B" (one or both of the two aims, only these; or both aims), two
# forces for "shall" (strict; defeasible, with an open exception) and two bearers.
LIMITATION = sort("limitation", "limitations",
                  "one limitation on one person's exercise of one right or freedom set forth in this Declaration, "
                  "imposed by someone: the person and the right are the limitation's own")
IS_STATE_BASE = base(["bearer"], "The bearer is a State", "{0} is a State")
U111_BASE = {
    "is_determined_by_law": base(["limitation"], "The limitation is determined by law", "{0} is determined by law"),
    "serves_recognition_of_rights_of_others": base(
        ["limitation"], "The limitation is for the purpose of securing due recognition and respect for the rights and "
        "freedoms of others", "{0} serves securing due recognition and respect for the rights and freedoms of others"),
    "serves_just_requirements": base(
        ["limitation"], "The limitation is for the purpose of meeting the just requirements of morality, public order "
        "and the general welfare in a democratic society",
        "{0} serves meeting the just requirements of morality, public order and the general welfare in a democratic "
        "society"),
    "serves_any_other_purpose": base(["limitation"], "The limitation also serves a purpose other than these two",
                                     "{0} serves any other purpose"),
}
U111_FREE = {"avoid_imposing_limitation_required": {
    "arguments": ["bearer", "limitation"],
    "description": "The bearer is required to avoid imposing the limitation on the person whose exercise of a right or "
                   "freedom it limits",
    "regulated": {"role": "obligation", "default": "unspecified", "act": "{0} avoid imposing {1} on anyone"}}}
U111_OPEN = ["determined_by_law", "due_recognition_and_respect", "just_requirements", "morality", "public_order",
             "general_welfare", "democratic_society"]


def _u111_guard(both, state):
    aims = And(Unary("serves_recognition_of_rights_of_others", V0), Unary("serves_just_requirements", V0)) if both \
        else Or(Unary("serves_recognition_of_rights_of_others", V0), Unary("serves_just_requirements", V0))
    miss = Not(And(Unary("is_determined_by_law", V0), And(Not(Unary("serves_any_other_purpose", V0)), aims)))
    return And(Unary("is_state", V1), miss) if state else miss


def _u111_witnesses(both, state):
    # l0 serves only the first aim, l1 is not determined by law, l2 serves both aims, l3 serves another purpose too;
    # b0 is a State, b1 is not
    rels = {"is_determined_by_law": [["l0"], ["l2"], ["l3"]],
            "serves_recognition_of_rights_of_others": [["l0"], ["l1"], ["l2"], ["l3"]],
            "serves_just_requirements": [["l2"]], "serves_any_other_purpose": [["l3"]],
            "is_state": [["b0"]]}
    def status(b, i, v):
        return ("avoid_imposing_limitation_required", (b, f"l{i}"),
                ("SETTLED", True) if v else ("UNDECIDED", None))
    checks = [status("b0", 0, both), status("b0", 1, True), status("b0", 2, False), status("b0", 3, True),
              status("b1", 1, not state)]
    return [({"bearer": ["b0", "b1"], "limitation": ["l0", "l1", "l2", "l3"]}, rels, checks)]


def _u111(both, soft, state):
    free = copy.deepcopy(U111_FREE)
    rule = norm("limits-by-law-for-listed-aims" + ("-state" if state else "-anyone"),
                "avoid_imposing_limitation_required", True, _u111_guard(both, state))
    if soft:
        free["avoid_imposing_limitation_required"]["regulated"]["default"] = "deny"
        rule["norm"].update(mode="default", exception={"decided_by": UNSTATED, "factors": [], "necessary": [],
                                                       "sufficient": []})
    return dict(sorts={"bearer": BEARER, "limitation": LIMITATION}, predicates={**U111_BASE, "is_state": IS_STATE_BASE, **free},
                rule=rule, open=U111_OPEN, soft=soft, witnesses=[] if soft else _u111_witnesses(both, state))


U111_SPECS = {f"{force}_{aims}_{bearer}": _u111(aims == "both_aims", force == "default", bearer == "state")
              for force in ("strict", "default") for aims in ("listed_aims", "both_aims")
              for bearer in ("state", "anyone")}


# spec = (sorts, predicates, rule, open terms the unit names, in-scope and out-of-scope witness situations)
# A witness situation is (domains, relations, [(predicate, row, expected status)]) checked in build.py.
SPECS = {
    "u074": {"prohibition": dict(
        sorts={"actor": sort("actor", "actors", "a person, group, or institution capable of compelling a person"),
               "person": PERSON},
        predicates={"compel_association_membership_permitted": regulated(
            ["actor", "person"], "permission",
            "The actor is permitted to compel the person to belong to an association",
            "{0} compel {1} to belong to an association")},
        rule=norm("no-compelled-association-membership", "compel_association_membership_permitted", False),
        open=[],
        witnesses=[({"actor": ["a0"], "person": ["p0"]}, {}, [
            ("compel_association_membership_permitted", ("a0", "p0"), ("SETTLED", False))])])},
    "u017": {"strict": dict(
        sorts={"human_being": sort("human being", "human beings", "a human being")},
        predicates={"act_in_brotherhood_required": regulated(
            ["human_being"], "obligation",
            "The human being is required to act towards each other human being in a spirit of brotherhood",
            "{0} act towards each other human being in a spirit of brotherhood")},
        rule=norm("brotherhood-strict", "act_in_brotherhood_required", True),
        open=["spirit_of_brotherhood"],
        witnesses=[({"human_being": ["h0"]}, {}, [("act_in_brotherhood_required", ("h0",), ("SETTLED", True))])])},
    "u052": {"invocation_barred": dict(
        sorts={"person": PERSON,
               "prosecution": sort("prosecution", "prosecutions", "a prosecution of a person")},
        predicates={
            "arises_from_non_political_crime": base(
                ["prosecution"], "The prosecution genuinely arises from a non-political crime",
                "{0} genuinely arises from a non-political crime"),
            "arises_from_acts_contrary_to_un": base(
                ["prosecution"],
                "The prosecution genuinely arises from acts contrary to the purposes and principles of the "
                "United Nations", "{0} genuinely arises from acts contrary to the purposes and principles of the "
                                  "United Nations"),
            "invoke_asylum_right_in_case_permitted": regulated(
                ["person", "prosecution"], "permission",
                "The person is permitted to invoke the right to seek and to enjoy asylum (Article 14, paragraph 1) "
                "in the case of the prosecution",
                "{0} invoke the right to seek as well as enjoy asylum in the case of {1}")},
        rule=norm("asylum-not-invocable-in-the-case-of-such-prosecutions", "invoke_asylum_right_in_case_permitted",
                  False, Or(Unary("arises_from_non_political_crime", V0), Unary("arises_from_acts_contrary_to_un", V0))),
        open=["genuine", "non_political_crime", "contrary_to_un_purposes_and_principles"],
        witnesses=[
            ({"person": ["p0"], "prosecution": ["x0", "x1"]},
             {"arises_from_non_political_crime": [["x0"]]},
             [("invoke_asylum_right_in_case_permitted", ("p0", "x0"), ("SETTLED", False)),
              ("invoke_asylum_right_in_case_permitted", ("p0", "x1"), ("UNDECIDED", None))])])},
    "u112": {"exercise_prohibited": dict(
        sorts={"exercise": sort("exercise", "exercises",
                                "one exercise of a right or freedom by a person on one occasion")},
        predicates={
            "exercise_of_declared_right": base(
                ["exercise"], "The exercise is an exercise of a right or freedom set forth in this Declaration",
                "{0} is an exercise of a right or freedom set forth in this Declaration"),
            "exercise_contrary_to_un": base(
                ["exercise"], "The exercise is contrary to the purposes and principles of the United Nations",
                "{0} is contrary to the purposes and principles of the United Nations"),
            "exercise_permitted": regulated(["exercise"], "permission", "The exercise is permitted to be carried out",
                                            "{0} be carried out")},
        rule=norm("no-exercise-contrary-to-un", "exercise_permitted", False,
                  And(Unary("exercise_of_declared_right", V0), Unary("exercise_contrary_to_un", V0))),
        open=["rights_and_freedoms_set_forth", "contrary_to_un_purposes_and_principles"],
        witnesses=[
            ({"exercise": ["e0", "e1"]},
             {"exercise_of_declared_right": [["e0"], ["e1"]], "exercise_contrary_to_un": [["e0"]]},
             [("exercise_permitted", ("e0",), ("SETTLED", False)),
              ("exercise_permitted", ("e1",), ("UNDECIDED", None))])])},
    "u114": {"interpretive_ban": dict(
        sorts={"interpretation": sort("interpretation", "interpretations",
                                      "an interpretation of this Declaration")},
        predicates={
            "implies_right_to_destroy_declared_rights": base(
                ["interpretation"],
                "The interpretation implies, for a State, group or person, a right to engage in an activity or to "
                "perform an act aimed at the destruction of a right or freedom set forth in this Declaration",
                "{0} implies, for a State, group or person, a right to engage in an activity or to perform an act "
                "aimed at the destruction of a right or freedom set forth in this Declaration"),
            "interpretation_permitted": regulated(["interpretation"], "permission",
                                                  "The interpretation of this Declaration is permitted",
                                                  "{0} be adopted")},
        rule=norm("no-interpretation-implying-a-right-to-destroy-rights", "interpretation_permitted", False,
                  Unary("implies_right_to_destroy_declared_rights", V0)),
        open=["rights_and_freedoms_set_forth", "aimed_at_destruction_of_rights"],
        witnesses=[
            ({"interpretation": ["i0", "i1"]}, {"implies_right_to_destroy_declared_rights": [["i0"]]},
             [("interpretation_permitted", ("i0",), ("SETTLED", False)),
              ("interpretation_permitted", ("i1",), ("UNDECIDED", None))])])},
    # ------------------------------------------------------------ the units the 2026-10-01T1800Z audit rejected
    "u035": {  # Article 8 (repaired after the 2026-10-02T1800Z audit): one element per victim and act, the victim named in the act phrase
        "tribunal_claim": dict(
            sorts={"tribunal": sort("tribunal", "tribunals", "a tribunal"), "violation": VIOLATION},
            predicates={
                "is_competent": base(["tribunal"], "The tribunal is competent", "{0} is competent"),
                "is_national": base(["tribunal"], "The tribunal is a national tribunal", "{0} is national"),
                "violates_granted_fundamental_right": VIOLATES,
                "provide_effective_remedy_required": regulated(
                    ["tribunal", "violation"], "obligation",
                    "The tribunal is required to provide the victim of the violation with an effective remedy",
                    "{0} provide the victim of {1} with an effective remedy")},
            rule=norm("tribunal-provides-effective-remedy", "provide_effective_remedy_required", True,
                      And(And(Unary("is_competent", V1), Unary("is_national", V1)),
                          Unary("violates_granted_fundamental_right", V0))),
            open=["effective", "competent", "fundamental_rights_granted"],
            witnesses=[
                ({"tribunal": ["t0", "t1", "t2"], "violation": ["v0", "v1"]},
                 {"is_competent": [["t0"], ["t1"]], "is_national": [["t0"], ["t2"]],
                  "violates_granted_fundamental_right": [["v0"]]},
                 [("provide_effective_remedy_required", ("t0", "v0"), ("SETTLED", True)),
                  ("provide_effective_remedy_required", ("t1", "v0"), ("UNDECIDED", None)),
                  ("provide_effective_remedy_required", ("t0", "v1"), ("UNDECIDED", None))])]),
        "state_claim": dict(
            sorts={"state": sort("state", "states", "a State"), "violation": VIOLATION},
            predicates={
                "violates_granted_fundamental_right": VIOLATES,
                "ensure_remedy_by_tribunals_required": regulated(
                    ["state", "violation"], "obligation",
                    "The State is required to ensure that competent national tribunals give the victim of the violation "
                    "an effective remedy",
                    "{0} ensure competent national tribunals give {1}'s victim an effective remedy")},
            rule=norm("state-ensures-effective-remedy-by-tribunals", "ensure_remedy_by_tribunals_required", True,
                      Unary("violates_granted_fundamental_right", V0)),
            open=["effective", "competent", "fundamental_rights_granted"],
            witnesses=[
                ({"state": ["s0"], "violation": ["v0", "v1"]}, {"violates_granted_fundamental_right": [["v0"]]},
                 [("ensure_remedy_by_tribunals_required", ("s0", "v0"), ("SETTLED", True)),
                  ("ensure_remedy_by_tribunals_required", ("s0", "v1"), ("UNDECIDED", None))])])},
    "u051": {  # Article 14(1): "seek and enjoy" in both duties; the guard is the asylum seeking or enjoying, not being persecuted
        "liberty": dict(
            sorts={"person": PERSON},
            predicates={"seek_asylum_from_persecution_permitted": regulated(
                ["person"], "permission",
                "The person is permitted to seek and to enjoy in other countries asylum from persecution",
                "{0} seek as well as enjoy asylum from persecution in other countries")},
            rule=norm("person-may-seek-and-enjoy-asylum", "seek_asylum_from_persecution_permitted", True),
            open=["persecution"],
            witnesses=[({"person": ["p0"]}, {},
                        [("seek_asylum_from_persecution_permitted", ("p0",), ("SETTLED", True))])]),
        "state_avoid": dict(
            sorts={"state": sort("state", "states", "a State"), "person": PERSON},
            predicates={
                "faces_persecution": FACES_PERSECUTION,
                "avoid_barring_asylum_required": regulated(
                    ["state", "person"], "obligation",
                    "The State is required to avoid barring the person from seeking as well as enjoying asylum in "
                    "other countries",
                    "{0} avoid barring {1} from seeking as well as enjoying asylum in other countries")},
            rule=norm("state-avoids-barring-asylum", "avoid_barring_asylum_required", True,
                      Unary("faces_persecution", V0)),
            open=["persecution"],
            witnesses=[
                ({"state": ["s0"], "person": ["p0", "p1"]}, {"faces_persecution": [["p0"]]},
                 [("avoid_barring_asylum_required", ("s0", "p0"), ("SETTLED", True)),
                  ("avoid_barring_asylum_required", ("s0", "p1"), ("UNDECIDED", None))])]),
        "anyone_avoid": dict(
            sorts={"bearer": BEARER, "person": PERSON},
            predicates={
                "faces_persecution": FACES_PERSECUTION,
                "avoid_barring_asylum_required": regulated(
                    ["bearer", "person"], "obligation",
                    "The bearer is required to avoid barring the person from seeking as well as enjoying asylum in "
                    "other countries",
                    "{0} avoid barring {1} from seeking as well as enjoying asylum in other countries")},
            rule=norm("anyone-avoids-barring-asylum", "avoid_barring_asylum_required", True,
                      Unary("faces_persecution", V0)),
            open=["persecution"],
            witnesses=[
                ({"bearer": ["b0", "b1"], "person": ["p0", "p1"]}, {"faces_persecution": [["p0"]]},
                 [("avoid_barring_asylum_required", ("b0", "p0"), ("SETTLED", True)),
                  ("avoid_barring_asylum_required", ("b1", "p0"), ("SETTLED", True)),
                  ("avoid_barring_asylum_required", ("b0", "p1"), ("UNDECIDED", None))])])},
    "u077": {  # Article 21(2): "his country" is a relation between a country and the person, read two ways
        "nationality_country_claim": dict(
            sorts={"country": sort("country", "countries", "a country"), "person": PERSON},
            predicates={
                "has_as_national": base(
                    ["country", "person"], "The country counts the person among its nationals",
                    "{0} has as national {1}"),
                "give_equal_access_to_public_service_required": regulated(
                    ["country", "person"], "obligation",
                    "The country is required to give the person equal access to public service in the person's country",
                    "{0} give {1} equal access to public service in their country")},
            rule=norm("nationality-country-gives-equal-access", "give_equal_access_to_public_service_required",
                      True, Binary("has_as_national", V1, V0)),
            open=[],
            witnesses=[
                ({"country": ["c0", "c1"], "person": ["p0"]}, {"has_as_national": [["c0", "p0"]]},
                 [("give_equal_access_to_public_service_required", ("c0", "p0"), ("SETTLED", True)),
                  ("give_equal_access_to_public_service_required", ("c1", "p0"), ("UNDECIDED", None))])]),
        "residence_country_claim": dict(
            sorts={"country": sort("country", "countries", "a country"), "person": PERSON},
            predicates={
                "has_as_resident": base(
                    ["country", "person"], "The country counts the person among its residents",
                    "{0} has as resident {1}"),
                "give_equal_access_to_public_service_required": regulated(
                    ["country", "person"], "obligation",
                    "The country is required to give the person equal access to public service in the person's country",
                    "{0} give {1} equal access to public service in their country")},
            rule=norm("residence-country-gives-equal-access", "give_equal_access_to_public_service_required",
                      True, Binary("has_as_resident", V1, V0)),
            open=[],
            witnesses=[
                ({"country": ["c0", "c1"], "person": ["p0"]}, {"has_as_resident": [["c1", "p0"]]},
                 [("give_equal_access_to_public_service_required", ("c1", "p0"), ("SETTLED", True)),
                  ("give_equal_access_to_public_service_required", ("c0", "p0"), ("UNDECIDED", None))])])},
    # ------------------------------------------------------------ the units the 2026-10-02T0600Z audit rejected
    "u054": {  # Article 15(1): an entitlement, not an accomplished fact; the bearer is an open relation (repaired after the 2026-10-02T1800Z audit)
        "claim": dict(
            sorts={"bearer": BEARER, "person": PERSON},
            predicates={
                "owes_nationality_to": base(
                    ["bearer", "person"],
                    "The bearer is a State, if any, that owes the person a nationality; the source names none, so which "
                    "State that is, if any, is the open term bearer_of_the_nationality_duty",
                    "{0} owes {1} a nationality"),
                "grant_nationality_required": regulated(
                    ["bearer", "person"], "obligation", "The bearer is required to grant the person a nationality",
                    "{0} grant {1} a nationality")},
            rule=norm("whoever-owes-a-nationality-grants-it", "grant_nationality_required", True,
                      Binary("owes_nationality_to", V1, V0)),
            open=["bearer_of_the_nationality_duty"],
            witnesses=[({"bearer": ["b0", "b1"], "person": ["p0"]}, {"owes_nationality_to": [["b0", "p0"]]},
                        [("grant_nationality_required", ("b0", "p0"), ("SETTLED", True)),
                         ("grant_nationality_required", ("b1", "p0"), ("UNDECIDED", None))])]),
        "liberty": dict(
            sorts={"person": PERSON},
            predicates={"have_nationality_permitted": regulated(
                ["person"], "permission", "The person is permitted to have a nationality", "{0} have a nationality")},
            rule=norm("person-may-have-a-nationality", "have_nationality_permitted", True),
            open=[],
            witnesses=[({"person": ["p0"]}, {}, [("have_nationality_permitted", ("p0",), ("SETTLED", True))])])},
    "u111": U111_SPECS,
    # ------------------------------------------------------------ units that norm-defaults@0 newly makes expressible
    "u061": {"claim": dict(  # Article 16(3), second clause; the subject (the family) is read from u060
        sorts={"family": sort("family", "families", "a family"), "bearer": BEARER},
        predicates={
            "is_society": base(["bearer"], "The bearer is society", "{0} is society"),
            "is_state": base(["bearer"], "The bearer is a State", "{0} is a State"),
            "protect_required": regulated(["bearer", "family"], "obligation",
                                          "The bearer is required to protect the family", "{0} protect {1}")},
        rule=norm("society-and-state-protect-the-family", "protect_required", True,
                  Or(Unary("is_society", V1), Unary("is_state", V1))),
        open=["protection_of_the_family"],
        witnesses=[
            ({"family": ["f0"], "bearer": ["b0", "b1", "b2"]}, {"is_society": [["b0"]], "is_state": [["b1"]]},
             [("protect_required", ("b0", "f0"), ("SETTLED", True)),
              ("protect_required", ("b1", "f0"), ("SETTLED", True)),
              ("protect_required", ("b2", "f0"), ("UNDECIDED", None))])])},
    "u110": {"duty": dict(  # Article 29(1)
        sorts={"person": PERSON, "community": sort("community", "communities", "a community")},
        predicates={
            "is_sole_setting_of_full_development": base(
                ["community", "person"],
                "The community is the community in which alone the free and full development of the person's "
                "personality is possible",
                "{0} alone enables the free and full development of {1}"),
            "perform_duties_required": regulated(["person", "community"], "obligation",
                                                 "The person is required to perform the duties the person has to "
                                                 "the community", "{0} perform duties to {1}")},
        rule=norm("duties-to-the-community-of-full-development", "perform_duties_required", True,
                  Binary("is_sole_setting_of_full_development", V0, V1)),
        open=["duties_to_the_community", "free_and_full_development"],
        witnesses=[
            ({"person": ["p0"], "community": ["m0", "m1"]}, {"is_sole_setting_of_full_development": [["m0", "p0"]]},
             [("perform_duties_required", ("p0", "m0"), ("SETTLED", True)),
              ("perform_duties_required", ("p0", "m1"), ("UNDECIDED", None))])])},
}


NEW_OPEN_TERMS = [
    {"arguments": [], "decided_by": UNSTATED, "factors": ["which State, if any, must grant the nationality",
                                                           "whether birth, descent or residence decides"],
     "jurisdiction": "universal", "name": "bearer_of_the_nationality_duty", "necessary": [], "precedents": [],
     "sufficient": [], "version": 1},
    {"arguments": [], "decided_by": UNSTATED, "factors": ["what counts as protection of the family",
                                                           "what society owes as distinct from the State"],
     "jurisdiction": "universal", "name": "protection_of_the_family", "necessary": [], "precedents": [],
     "sufficient": [], "version": 1},
    {"arguments": [], "decided_by": UNSTATED, "factors": ["which duties the community may require", "who decides"],
     "jurisdiction": "universal", "name": "duties_to_the_community", "necessary": [], "precedents": [],
     "sufficient": [], "version": 1},
    {"arguments": [], "decided_by": UNSTATED, "factors": ["what counts as free and full development of a personality"],
     "jurisdiction": "universal", "name": "free_and_full_development", "necessary": [], "precedents": [],
     "sufficient": [], "version": 1},
]


def write_companion(directory: Path, unit_id: str, candidate: str, source: bytes, open_terms: list) -> Path:
    spec = SPECS[unit_id][candidate]
    profiles = (*(p for p in PROFILES if not spec.get("soft") or p != "norm-defaults@0"),
                *(("soft-norms@0",) if spec.get("soft") else ()))
    meta = {"format": "ve-document@1",
            "environment": environment(profiles, spec["sorts"], spec["predicates"]),
            "open_terms": [copy.deepcopy(t) for t in open_terms if t["name"] in spec["open"]],
            "units": [{"content": spec["rule"], "id": f"{unit_id}_{candidate}", "kind": "norm",
                       "meaning": ({"open": list(spec["open"])} if spec["open"] else "specified"),
                       "span": [0, len(source)], "support": "none"}]}
    path = directory / f"{unit_id}.{candidate}.ve.md"
    path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2).encode()
                     + b"\n---\n" + source)
    return path
