"""Tenant Fees Act 2019: the ENCODER's file for the CROSS-FAMILY question set (questions-enc.jsonl beside this file).
TEMPLATE: the frozen build's own cases.py with its case records removed. The build's description of the record shape:
Each case: "items" (the payments, contracts, loans or other requirements the questions name or the facts make relevant),
"facts" (the unary facts true of each item; every other FACTS entry is false, encode.py C1), "links" (binary facts),
"ints" (stated amounts and dates, and the annual rent), "questions" (qid -> item and form: permitted = "Is X a permitted
payment?", s1 = "Does section 1 allow ... to require X?", amount = Q2, repay = Q3), "judgement" (anything the encoder
decided beyond copying a stated fact: listed as "encoder judgement"). The late-rent caps come from bridge/bridges.jsonl.
UNSUPPORTED: in-scope questions the translation cannot carry (counted not correct, listed). PROBES: out-of-scope cases.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "3a2f1e2eadec53c6560bbbc8d9a234566179e5c0b2e31ade23e450394178ad0f"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

# fact bundles (each a list of FACTS names) ------------------------------------------------------------------------
PAY_T = ["is_payment", "payer_tenant"]                      # a payment required of the tenant
HD = PAY_T + ["by_or_for_tenant", "before_grant", "intended_schedule2", "for_tenancy_event"]  # a holding deposit
SEC = PAY_T + ["security_for_tenant", "for_tenancy_event"]  # money to be held as security (tenancy deposit)
# a default charge for late rent under a tenancy agreement term, to the landlord
DL = PAY_T + ["to_landlord", "default_payment", "late_rent", "ta_requires", "on_act_or_default_term"]
DL_AGENT = PAY_T + ["to_agent", "default_payment", "late_rent", "ta_requires", "on_act_or_default_term"]
AR = {"annual_rent": "15600.00"}


def Q(*rows):
    return [{"qid": qid, "item": item, "form": form} for (qid, item, form) in rows]


def rec(cid, items, facts, ints, questions, links=(), judgement=()):
    return {"id": cid, "items": list(items), "facts": facts, "links": list(links), "ints": ints,
            "questions": Q(*questions), "judgement": list(judgement)}


def hdcase(cid, forms, to="to_landlord", extra=(), ints=None, amt="300.00", judgement=()):
    """One holding deposit 'hd' received 1 March 2025; forms: the case's question forms in qid order."""
    return rec(cid, ["hd"], {"hd": HD + [to] + list(extra)},
               {**AR, "amt_hd": amt, "received_hd": "2025-03-01", **(ints or {})},
               [(f"{cid}-{i + 1}", "hd", f) for i, f in enumerate(forms)], judgement=judgement)


P123 = ("permitted", "amount", "repay")
R = ("repay",)

CASES = []

# ---- tenancy deposits (Sch. 1 para. 2) ----
for _cid, _rent, _amt, _to in (("T001", "15600.00", "1500.00", "to_landlord"),
                               ("T002", "49999.56", "4807.66", "to_landlord"),
                               ("T003", "50000.08", "5769.23", "to_agent"),
                               ("T004", "52000.00", "6000.01", "to_landlord")):
    CASES.append(rec(_cid, ["d"], {"d": SEC + [_to, "by_or_for_tenant", "ta_requires"]},
                     {"annual_rent": _rent, "amt_d": _amt, "taday_d": "2025-02-01"},
                     [(f"{_cid}-1", "d", "permitted"), (f"{_cid}-2", "d", "amount")]))

CASES += [
    rec("T005", ["clean", "ins", "elec", "comm"],
        {"clean": ["payer_tenant", "for_tenancy_event", "is_contract", "contract_third_party", "contract_service"],
         "ins": ["payer_tenant", "for_tenancy_event", "is_contract", "contract_third_party", "contract_insurance"],
         "elec": ["payer_tenant", "for_tenancy_event", "is_contract", "contract_third_party", "contract_service",
                  "contract_utility"],
         "comm": ["payer_tenant", "for_tenancy_event", "is_contract", "contract_third_party", "contract_service",
                  "contract_communication"]},
        dict(AR),
        [("T005-1", "clean", "s1"), ("T005-2", "ins", "s1"), ("T005-3", "elec", "s1"), ("T005-4", "comm", "s1")],
        judgement=["T005 the electricity and communication contracts are read as contracts for the provision of a "
                   "service (s. 1(3)); the renewal condition as s. 1(6)(a)."]),
    rec("T006", ["loan", "ref"],
        {"loan": ["is_loan", "payer_tenant", "for_tenancy_event"],
         "ref": PAY_T + ["to_landlord", "for_reference"]},
        {**AR, "amt_ref": "35.00"},
        [("T006-1", "loan", "s1"), ("T006-2", "ref", "s1"), ("T006-3", "ref", "amount")],
        judgement=["T006 the continuance condition on the loan is read as s. 1(6)(a)."]),
    rec("T007", ["store", "paint"],
        {"store": ["is_payment", "payer_for_tenant", "ta_requires", "other_agreement_term"],
         "paint": PAY_T + ["to_landlord", "ta_requires", "on_act_or_default_term"]},
        {**AR, "amt_store": "40.00", "amt_paint": "20.00"},
        [("T007-1", "store", "s1"), ("T007-2", "store", "amount"), ("T007-3", "paint", "s1"),
         ("T007-4", "paint", "amount")],
        judgement=["T007 the storage term is read as s. 1(6)(d) (other circumstances); the painting term as "
                   "s. 1(6)(b) (an act of the tenant), not a default."]),
    rec("T008", ["nc", "gla", "omar", "priya"],
        {"nc": ["is_payment", "to_landlord", "for_tenancy_event", "payer_lha", "payer_for_tenant"],
         "gla": ["is_payment", "to_landlord", "for_tenancy_event", "payer_gla", "payer_for_tenant"],
         "omar": ["is_payment", "to_landlord", "for_tenancy_event", "payer_for_authority"],
         "priya": ["is_payment", "to_landlord", "for_tenancy_event", "payer_for_tenant"]},
        {**AR, "amt_nc": "10.00", "amt_gla": "10.00", "amt_omar": "10.00", "amt_priya": "10.00"},
        [("T008-1", "nc", "s1"), ("T008-2", "nc", "amount"), ("T008-3", "gla", "s1"), ("T008-4", "gla", "amount"),
         ("T008-5", "omar", "s1"), ("T008-6", "omar", "amount"), ("T008-7", "priya", "s1"),
         ("T008-8", "priya", "amount")],
        judgement=["T008 the renewal condition is read as s. 1(6)(a); Omar is stated only to act for North Council, so "
                   "payer_for_tenant is not set for him."]),
    rec("T009", ["collect", "form", "insalt", "inscon", "attend", "visit"],
        {"collect": PAY_T + ["to_landlord", "for_tenancy_event", "offered_as_option"],
         "form": ["payer_tenant", "for_tenancy_event"],
         "insalt": PAY_T + ["to_landlord", "for_tenancy_event", "offered_as_option"],
         "inscon": ["payer_tenant", "for_tenancy_event", "is_contract", "contract_third_party", "contract_insurance"],
         "attend": PAY_T + ["to_landlord", "for_tenancy_event", "offered_as_option", "unreasonable_other"],
         "visit": ["payer_tenant", "for_tenancy_event"]},
        {**AR, "amt_collect": "25.00", "amt_insalt": "30.00", "amt_attend": "45.00"},
        [("T009-1", "collect", "s1"), ("T009-2", "collect", "amount"), ("T009-3", "insalt", "s1"),
         ("T009-4", "insalt", "amount"), ("T009-5", "attend", "s1"), ("T009-6", "attend", "amount")],
        links=[("alternative_to", "collect", "form"), ("alternative_to", "insalt", "inscon"),
               ("alternative_to", "attend", "visit")],
        judgement=["T009 the form delivery, the insurance contract and the attendance are entered as the other "
                   "requirements each option is linked to; the renewal conditions are read as s. 1(6)(a)."]),
    rec("T010", ["nuis", "comp"],
        {"nuis": PAY_T + ["to_landlord", "for_act_outside_agreement"],
         "comp": PAY_T + ["to_agent", "by_or_for_tenant", "damages"]},
        {**AR, "amt_nuis": "15.00", "amt_comp": "60.00"},
        [("T010-1", "nuis", "s1"), ("T010-2", "nuis", "amount"), ("T010-3", "comp", "permitted"),
         ("T010-4", "comp", "amount")]),
    rec("T011", ["key"],
        {"key": PAY_T + ["to_landlord", "on_act_or_default_term", "default_payment", "lost_key", "ta_requires",
                         "key_evidence"]},
        {**AR, "amt_key": "90.00", "keycost_key": "85.00"},
        [("T011-1", "key", "s1"), ("T011-2", "key", "amount")]),
    rec("T012", ["dev"],
        {"dev": PAY_T + ["to_agent", "on_act_or_default_term", "default_payment", "lost_key", "ta_requires"]},
        {**AR, "amt_dev": "25.00", "keycost_dev": "25.00"},
        [("T012-1", "dev", "permitted"), ("T012-2", "dev", "amount")]),
    rec("T013", ["late"], {"late": DL},
        {**AR, "amt_late": "10.00", "due_late": "2025-03-01", "paidfull_late": "2025-03-14"},
        [("T013-1", "late", "permitted"), ("T013-2", "late", "amount")],
        judgement=["T013 no base rate is stated, so no bridge input (late-rent cap) is given."]),
    rec("T014", ["late"], {"late": DL},
        {**AR, "amt_late": "2.50", "due_late": "2025-03-01", "paidfull_late": "2025-03-15"},
        [("T014-1", "late", "permitted"), ("T014-2", "late", "amount")]),
    rec("T015", ["hint", "mint"],
        {"hint": DL, "mint": DL_AGENT + ["earlier_other_charge"]},
        {**AR, "amt_hint": "2.66", "due_hint": "2025-03-01", "paidfull_hint": "2025-03-20",
         "amt_mint": "1.00", "due_mint": "2025-03-01", "paidfull_mint": "2025-03-20"},
        [("T015-1", "hint", "permitted"), ("T015-2", "hint", "amount"), ("T015-3", "mint", "permitted"),
         ("T015-4", "mint", "amount")]),
    rec("T016", ["mint", "hint"],
        {"mint": DL_AGENT, "hint": DL + ["earlier_other_charge"]},
        {**AR, "amt_mint": "2.68", "due_mint": "2025-03-01", "paidfull_mint": "2025-03-16",
         "amt_hint": "2.00", "due_hint": "2025-03-01", "paidfull_hint": "2025-03-16"},
        [("T016-1", "mint", "permitted"), ("T016-2", "mint", "amount"), ("T016-3", "hint", "permitted"),
         ("T016-4", "hint", "amount")]),
    rec("T017", ["var", "nov"],
        {"var": PAY_T + ["to_landlord", "for_variation", "at_tenant_request", "on_change_term", "ta_requires"],
         "nov": PAY_T + ["to_agent", "for_variation", "at_tenant_request", "on_change_term", "ta_requires"]},
        {**AR, "amt_var": "85.00", "varcost_var": "85.00", "amt_nov": "50.01", "varcost_nov": "40.00"},
        [("T017-1", "var", "s1"), ("T017-2", "var", "amount"), ("T017-3", "nov", "permitted"),
         ("T017-4", "nov", "amount")]),
    rec("T018", ["asg", "ctax", "cadm"],
        {"asg": PAY_T + ["to_landlord", "for_tenancy_event", "for_variation"],
         "ctax": PAY_T + ["to_billing_authority", "council_tax", "ta_requires", "other_agreement_term"],
         "cadm": PAY_T + ["to_landlord", "ta_requires", "other_agreement_term"]},
        {**AR, "amt_asg": "50.00", "amt_ctax": "120.00", "amt_cadm": "12.00"},
        [("T018-1", "asg", "s1"), ("T018-2", "asg", "amount"), ("T018-3", "ctax", "permitted"),
         ("T018-4", "ctax", "amount"), ("T018-5", "cadm", "s1"), ("T018-6", "cadm", "amount")],
        judgement=["T018 the council-tax and administration terms are read as s. 1(6)(d); the assignment charge as "
                   "s. 1(6)(a)."]),
    rec("T019", ["sup", "gd"],
        {"sup": PAY_T + ["to_landlord", "ta_requires", "utility_supply", "other_agreement_term"],
         "gd": PAY_T + ["to_landlord", "ta_requires", "green_deal", "other_agreement_term"]},
        {**AR, "amt_sup": "90.00", "amt_gd": "45.00"},
        [("T019-1", "sup", "permitted"), ("T019-2", "sup", "amount"), ("T019-3", "gd", "permitted"),
         ("T019-4", "gd", "amount")]),
    rec("T020", ["tv", "wat"],
        {"tv": PAY_T + ["to_bbc", "tv_licence", "ta_requires", "other_agreement_term"],
         "wat": PAY_T + ["to_landlord", "utility_supply", "by_or_for_tenant"]},
        {**AR, "amt_tv": "170.00", "amt_wat": "20.00"},
        [("T020-1", "tv", "permitted"), ("T020-2", "tv", "amount"), ("T020-3", "wat", "permitted"),
         ("T020-4", "wat", "amount")]),
]

# ---- holding deposits (Sch. 1 para. 3, Sch. 2) ----
CASES += [
    hdcase("T021", P123, extra=["entered_agreement"], ints={"taday_hd": "2025-03-10"}),
    hdcase("T022", P123, extra=["entered_agreement", "applied_with_consent"], amt="299.99",
           ints={"taday_hd": "2025-03-10", "applied6_hd": "200.00"}),
    hdcase("T023", P123, extra=["entered_agreement", "applied_with_consent"], amt="300.01",
           ints={"taday_hd": "2025-03-10", "applied6_hd": "300.01"}),
    rec("T024", ["hd"],
        {"hd": [f for f in HD if f != "payer_tenant"] + ["payer_for_tenant", "to_landlord", "entered_agreement",
                                                        "landlord_steps"]},
        {**AR, "amt_hd": "300.00", "received_hd": "2025-03-01", "taday_hd": "2025-03-15"},
        [("T024-1", "hd", "permitted"), ("T024-2", "hd", "amount"), ("T024-3", "hd", "repay")],
        judgement=["T024 Nora (acting on Leo's behalf) is the payer; Leo's consent is not the payer's consent, so "
                   "applied_with_consent is not set."]),
    hdcase("T025", P123, extra=["landlord_decided_not"], ints={"decideday_hd": "2025-03-14"}),
    hdcase("T026", P123, extra=["agreed_deadline"], ints={"agreedday_hd": "2025-03-20"}),
    hdcase("T027", R, extra=["false_info", "reasonably_entitled", "landlord_decided_not", "believes_exception",
                             "notice_given"],
           ints={"decideday_hd": "2025-03-05", "noticeday_hd": "2025-03-11"},
           judgement=["T027 the stated employment end date that differs from the actual one is read as false or "
                      "misleading information."]),
    hdcase("T028", R, extra=["false_info", "reasonably_entitled", "landlord_decided_not", "believes_exception",
                             "notice_given"],
           ints={"decideday_hd": "2025-03-05", "noticeday_hd": "2025-03-12"},
           judgement=["T028 the forged employer letter is read as false or misleading information (the stated "
                      "entitlement concerns the action of supplying it)."]),
    hdcase("T029", R, to="to_agent",
           extra=["agent_instructed", "ia_prohibited", "landlord_could_not_know", "agent_could_not_know",
                  "landlord_decided_not", "believes_exception", "notice_given"],
           ints={"decideday_hd": "2025-03-05", "noticeday_hd": "2025-03-10"}),
    hdcase("T030", R, to="to_agent",
           extra=["agent_instructed", "ia_prohibited", "landlord_could_not_know", "landlord_decided_not",
                  "believes_exception", "notice_given"],
           ints={"decideday_hd": "2025-03-05", "noticeday_hd": "2025-03-10"}),
    hdcase("T031", R, extra=["tenant_notified", "believes_exception", "notice_given"],
           ints={"tnotifyday_hd": "2025-03-14", "noticeday_hd": "2025-03-21"}),
    hdcase("T032", R, extra=["tenant_notified", "landlord_steps", "believes_exception", "notice_given"],
           ints={"tnotifyday_hd": "2025-03-15", "noticeday_hd": "2025-03-21"}),
    hdcase("T033", R, extra=["agent_instructed", "landlord_steps", "agent_steps", "tenant_failed_steps",
                             "believes_exception", "notice_given"],
           ints={"noticeday_hd": "2025-03-21"}),
    hdcase("T034", R, to="to_agent",
           extra=["agent_instructed", "landlord_steps", "agent_steps", "tenant_failed_steps", "believes_exception",
                  "notice_given"],
           ints={"noticeday_hd": "2025-03-21"}),
    hdcase("T035", R, extra=["agent_instructed", "landlord_steps", "tenant_failed_steps", "believes_exception",
                             "notice_given"],
           ints={"noticeday_hd": "2025-03-21"}),
    rec("T036", ["hd", "doc"],
        {"hd": HD + ["to_landlord", "tenant_notified", "believes_exception", "notice_given"],
         "doc": ["is_payment", "payer_for_tenant", "to_landlord", "for_tenancy_event"]},
        {**AR, "amt_hd": "300.00", "received_hd": "2025-03-01", "tnotifyday_hd": "2025-03-10",
         "noticeday_hd": "2025-03-20", "amt_doc": "40.00", "reqday_doc": "2025-03-03"},
        [("T036-1", "doc", "s1"), ("T036-2", "doc", "amount"), ("T036-3", "hd", "repay")],
        links=[("imposed_for", "doc", "hd")],
        judgement=["T036 the fee condition on the grant is read as s. 1(6)(a), imposed on Nora (guarantor, a relevant "
                   "person) in relation to the deposit's proposed tenancy."]),
    hdcase("T037", R, to="to_agent",
           extra=["agent_instructed", "unreasonable_behaviour", "tenant_notified", "believes_exception",
                  "notice_given"],
           ints={"tnotifyday_hd": "2025-03-10", "noticeday_hd": "2025-03-20"},
           judgement=["T037 Mira's stated behaviour of 3 March 2025 (towards Nora, acting for Leo) is entered as "
                      "unreasonable_behaviour, read as before the deadline."]),
    rec("T038", ["h1", "h2"],
        {"h1": HD + ["to_landlord"], "h2": HD + ["to_landlord"]},
        {**AR, "amt_h1": "100.00", "received_h1": "2025-03-01", "amt_h2": "100.00", "received_h2": "2025-03-03"},
        [("T038-1", "h1", "permitted"), ("T038-2", "h1", "amount"), ("T038-3", "h1", "repay"),
         ("T038-4", "h2", "permitted"), ("T038-5", "h2", "amount"), ("T038-6", "h2", "repay")],
        links=[("earlier_same", "h2", "h1")]),
    rec("T039", ["h1", "h2"],
        {"h1": HD + ["to_landlord", "tenant_notified", "believes_exception", "notice_given"],
         "h2": HD + ["to_landlord", "tenant_notified", "believes_exception", "notice_given"]},
        {**AR, "amt_h1": "100.00", "received_h1": "2025-03-01", "tnotifyday_h1": "2025-03-05",
         "noticeday_h1": "2025-03-20", "amt_h2": "100.00", "received_h2": "2025-03-08",
         "tnotifyday_h2": "2025-03-10", "noticeday_h2": "2025-03-27"},
        [("T039-1", "h1", "repay"), ("T039-2", "h2", "permitted"), ("T039-3", "h2", "amount"),
         ("T039-4", "h2", "repay")],
        links=[("earlier_same", "h2", "h1")],
        judgement=["T039 the 1 March deposit's notification day is the first withdrawal (5 March 2025); the 8 March "
                   "deposit's is the withdrawal after its receipt (10 March 2025)."]),
    hdcase("T040", R, extra=["entered_agreement"], ints={"taday_hd": "2025-03-30"}),
]

UNSUPPORTED = {  # in-scope questions the translation cannot carry: case id -> (reason, [qids])
}
PROBES = {  # out-of-scope cases: case id -> reason
    "T041": "out of scope: a letting agent's own requirement (s. 2) is not written in the translation",
    "T042": "out of scope: a letting agent acting for the tenant only (s. 2, letting agent definition)",
    "T043": "out of scope: rent (Sch. 1 para. 1) is not an in-scope paragraph",
    "T044": "out of scope: rent and differential rent (Sch. 1 paras. 1, 1A) are not in-scope paragraphs",
    "T045": "out of scope: a termination payment (Sch. 1 para. 7) is not an in-scope paragraph",
    "T046": "out of scope: communication services (Sch. 1 para. 11) is not an in-scope paragraph",
    "T047": "out of scope: housing in Wales",
    "T048": "out of scope: a tenancy entered into before commencement (transitional provision)",
    "T049": "out of scope: a holiday let is not a tenancy within the Act",
    "T050": "out of scope: the reasonable costs of the variation are not given",
}
PROBE_QIDS = {  # case id -> [its qids]
    "T041": ["T041-1"], "T042": ["T042-1"], "T043": ["T043-1", "T043-2"], "T044": ["T044-1", "T044-2"],
    "T045": ["T045-1", "T045-2"], "T046": ["T046-1", "T046-2"], "T047": ["T047-1", "T047-2"],
    "T048": ["T048-1", "T048-2"], "T049": ["T049-1", "T049-2"], "T050": ["T050-1", "T050-2"],
}
