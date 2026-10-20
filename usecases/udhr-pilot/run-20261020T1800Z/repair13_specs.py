"""Plan-directed repairs and audit repairs for the 2026-10-14T1800Z run (language at ve-green-repo-map-untracked).

Nothing here is a feature upgrade: no construct a translator can write has merged since the previous run. Every unit below
changes for one of these reasons.

* AUDIT (20261013T0600Z, AUDIT.md): u049 and u077 were UNFAITHFUL. Both fixed "his country" to nationality or residence
  (a two-candidate reading set) and said those two exhaust the phrase. The words do not say which country is meant, so the
  set is gone: each unit is ONE reading with the open term `own_country` (which country is a person's own country).
* QT-0p (DRI QT2, quantities plan item QT-0p, UDHR part): u097 "Education shall be free, at least in the elementary and
  fundamental stages." becomes a duty with no bearer, as u098 is (evidence/quantities-p1/udhr-u097.ve.md).
* AP-0 item 1 (DRI 2026-10-13 19:20Z, act-phrases plan): u085, u091 and u106 as in research/act-phrases-p1
  (evidence/act-phrases-p1/*.entitlement.ve.md). u039 failed the blind audit and is NOT landed.

The research documents are read from the copies under evidence/ (the branch heads recorded in evidence/SOURCES.md), so the
content is exactly theirs; only the witnesses are written here.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"


def research(path):
    raw = Path(path).read_bytes()
    _, front, source = raw.split(b"---\n", 2)
    meta = json.loads(front)
    [unit] = meta["units"]
    return {"sorts": meta["environment"]["vocabulary"]["sorts"], "predicates": meta["environment"]["vocabulary"]["predicates"],
            "rule": unit["content"], "open": list(unit["meaning"]["open"]), "open_terms": meta["open_terms"], "source": source}


UNSPEC = ("Completion 'unspecified' (norm-defaults@0): where the rule's guard fails, or the party is not one the rule names, the case is "
          "UNDECIDED, never 'not required' and never permitted; strict force, because the source states no exception.")

NEW: dict[str, tuple[str, dict, str]] = {}      # unit -> (candidate id, spec, why)
REASON: dict[str, str] = {}
PLAN: dict[str, dict] = {}                      # unit -> {"plan": ..., "item": ...}
NEW_TERMS: dict[str, dict] = {}                 # open term name -> term (only the ones the translation lacks)


def term(name, factors):
    return {"arguments": [], "decided_by": "unstated", "factors": factors, "jurisdiction": "universal", "name": name,
            "necessary": [], "precedents": [], "sufficient": [], "version": 1}


# ---- u097 (QT-0p) --------------------------------------------------------------------------------------------------------------
Q = research(EVIDENCE / "quantities-p1" / "udhr-u097.ve.md")
Q["witnesses"] = [(
    {"education_kind": ["elem", "fund", "both", "higher"]},
    {"is_elementary": [["elem"], ["both"]], "is_fundamental": [["fund"], ["both"]]},
    [("education_free_required", ("elem",), ("SETTLED", True)),        # control: elementary
     ("education_free_required", ("fund",), ("SETTLED", True)),        # control: fundamental
     ("education_free_required", ("both",), ("SETTLED", True)),        # control: both
     ("education_free_required", ("higher",), ("UNDECIDED", None))])]  # probe: higher education, neither stage
NEW["u097"] = ("free_required", Q, (
    "Article 26(1), 'Education shall be free, at least in the elementary and fundamental stages': an impersonal passive, written as "
    "u098 is. Education of an elementary or of a fundamental stage (the guard; the words do not say the two stages differ) is "
    "required to be free, of no stated party: the sentence names no one who must make it free, and this reading adds no one. What it "
    "is for education to be free is the open term free_education. 'At least' says the stated stages are the minimum extent and leaves "
    "the other stages unsaid: for a stage that is neither elementary nor fundamental the rule says nothing, so the case is UNDECIDED "
    "(it is neither required nor forbidden to be free). " + UNSPEC))
REASON["u097"] = ("quantities plan QT-0p (DRI QT2): was UNFAITHFUL-by-absence (UNFORMALISED, quantities); now a bearer-less duty over the "
                  "translation's own education_kind, guard elementary-or-fundamental, 'free' an open term; one reading")
PLAN["u097"] = {"plan": "quantities", "item": "QT-0p (UDHR part: u097)"}
NEW_TERMS["free_education"] = Q["open_terms"][0]

# ---- u085, u091, u106 (AP-0 item 1) --------------------------------------------------------------------------------------------
A85 = research(EVIDENCE / "act-phrases-p1" / "u085.entitlement.ve.md")
A85["witnesses"] = [({"person": ["p0"]}, {}, [("has_the_right_to_equal_pay_for_equal_work", ("p0",), ("SETTLED", True))])]
NEW["u085"] = ("entitlement", A85, (
    "Article 23(2): every person has the right to equal pay for equal work, without any discrimination. The whole act phrase is the "
    "predicate's wording ('without any discrimination' and 'equal pay for equal work' are in it); which work is equal and which pay "
    "is equal is the open term equal_pay_for_equal_work, and what counts as discrimination is the open term discrimination. The "
    "source names no one who must do anything, so the reading names no bearer (a plain regulated predicate the rule makes true of "
    "every person). " + UNSPEC))
REASON["u085"] = ("act-phrases AP-0 item 1: was UNFORMALISED (act-phrase grammar); the whole act phrase is one entitlement predicate "
                  "with two open terms; blind audit FAITHFUL")
PLAN["u085"] = {"plan": "act-phrases", "item": "AP-0 item 1"}
NEW_TERMS["equal_pay_for_equal_work"] = A85["open_terms"][0]

A91 = research(EVIDENCE / "act-phrases-p1" / "u091.entitlement.ve.md")
A91["witnesses"] = [({"person": ["p0"]}, {}, [("has_the_right_to_an_adequate_standard_of_living", ("p0",), ("SETTLED", True))])]
NEW["u091"] = ("entitlement", A91, (
    "Article 25(1), first clause: every person has the right to a standard of living adequate for the health and well-being of "
    "themselves and of their family, including food, clothing, housing and medical care and necessary social services. The whole "
    "act phrase, the beneficiary clause and the list, is the predicate's wording; what standard of living is adequate is the open "
    "term adequate_standard_of_living. The source names no one who must do anything, so the reading names no bearer. " + UNSPEC))
REASON["u091"] = ("act-phrases AP-0 item 1: was UNFORMALISED (act-phrase grammar); the whole act phrase is one entitlement predicate "
                  "with one open term; blind audit FAITHFUL")
PLAN["u091"] = {"plan": "act-phrases", "item": "AP-0 item 1"}
NEW_TERMS["adequate_standard_of_living"] = A91["open_terms"][0]

A106 = research(EVIDENCE / "act-phrases-p1" / "u106.entitlement.ve.md")
A106["witnesses"] = [(
    {"person": ["p0", "p1"], "production": ["w0", "w1", "w2"]},
    {"is_author_of": [["p0", "w0"], ["p0", "w1"], ["p1", "w2"]], "is_scientific_literary_or_artistic": [["w0"], ["w2"]]},
    [("has_the_right_to_protection_of_interests_in", ("p0", "w0"), ("SETTLED", True)),     # author of a production of the kinds
     ("has_the_right_to_protection_of_interests_in", ("p0", "w1"), ("UNDECIDED", None)),   # author, production not of those kinds
     ("has_the_right_to_protection_of_interests_in", ("p1", "w0"), ("UNDECIDED", None)),   # not the author
     ("has_the_right_to_protection_of_interests_in", ("p1", "w2"), ("SETTLED", True))])]
NEW["u106"] = ("entitlement", A106, (
    "Article 27(2): every person has the right to the protection of the moral and material interests resulting from any scientific, "
    "literary or artistic production of which the person is the author. The production is an argument of the right (the guard: the "
    "person is its author and it is scientific, literary or artistic; the three kinds are one predicate, as the words give them as "
    "alternatives); which moral and material interests result from a production is the open term moral_and_material_interests. The "
    "source names no one who must protect them, so the reading names no bearer. " + UNSPEC))
REASON["u106"] = ("act-phrases AP-0 item 1: was UNFORMALISED (act-phrase grammar); an entitlement over person and production, guarded by "
                  "authorship and the production's kinds, one open term; blind audit FAITHFUL (the kinds are merged into one predicate)")
PLAN["u106"] = {"plan": "act-phrases", "item": "AP-0 item 1"}
NEW_TERMS["moral_and_material_interests"] = A106["open_terms"][0]


# ---- u049, u077 (audit repair) ---------------------------------------------------------------------------------------------------
def entitlement(unit, stem, verbalisation, desc, opens):
    return {"sorts": {"person": {"description": "a human person", "verbalisation": {"plural": "people", "singular": "person"}}},
            "predicates": {stem: {"arguments": ["person"], "description": desc, "verbalisation": verbalisation,
                                  "regulated": {"role": "plain", "default": "unspecified"}}},
            "rule": {"norm": {"guard": ["top"], "name": f"{unit}-entitlement", "over": [], "predicate": stem, "sign": True, "unless": []}},
            "open": list(opens), "witnesses": [({"person": ["p0"]}, {}, [(stem, ("p0",), ("SETTLED", True))])]}


OWN_COUNTRY = term("own_country", ["which country is a person's own country (the words say 'his own' and 'his country', not which relation makes a "
                                   "country someone's own)"])
NEW_TERMS["own_country"] = OWN_COUNTRY

NEW["u049"] = ("entitlement", entitlement(
    "u049", "has_right_to_leave_and_return_to_own_country",
    "{0} has the right to leave any country, including their own, and to return to their country",
    "The person has the right to leave any country, including their own, and to return to their country", ["own_country"]), (
    "Article 13(2): every person has the right to leave any country, including their own, and to return to their country. ONE reading. "
    "The words 'his own' and 'his country' do not say which relation makes a country someone's own (nationality, residence, origin, "
    "any other tie), so the translation fixes none of them and does not say that a list of relations is complete: which country is "
    "a person's own is the open term own_country. The source names no one who must do anything, so the reading names no bearer. "
    + UNSPEC))
REASON["u049"] = ("audit 20261013T0600Z (UNFAITHFUL): the two-candidate set (nationality, residence) claimed to exhaust 'his country'; "
                  "replaced by one entitlement with the open term own_country")
PLAN["u049"] = None

NEW["u077"] = ("entitlement", entitlement(
    "u077", "has_right_to_equal_public_service_in_own_country",
    "{0} has the right of equal access to public service in their country",
    "The person has the right of equal access to public service in their country", ["own_country"]), (
    "Article 21(2): every person has the right of equal access to public service in their country. ONE reading. The words 'his "
    "country' do not say which relation makes a country someone's own (nationality, residence, origin, any other tie), so the "
    "translation fixes none of them and does not say that a list of relations is complete: which country is a person's own is the "
    "open term own_country. The source names no one who must do anything, so the reading names no bearer. " + UNSPEC))
REASON["u077"] = ("audit 20261013T0600Z (UNFAITHFUL): the two-candidate set (nationality, residence) claimed to exhaust 'his country'; "
                  "replaced by one entitlement with the open term own_country")
PLAN["u077"] = None

AUDIT_REPAIRED = ["u049", "u077"]
PLAN_REPAIRS = {u: p for u, p in PLAN.items() if p}
ORDER = ["u049", "u077", "u085", "u091", "u097", "u106"]
