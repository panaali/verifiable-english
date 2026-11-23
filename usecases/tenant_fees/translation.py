"""Tenant Fees Act 2019 (statute corpus law 5): the VE translation, one pass with today's language. SAME-FAMILY.

Row statute-corpus-tenant-fees (dri-statute-corpus-tenant-fees-1123, Opus 5.5). Written from the pinned source only
(manage-agents reviews/spare/statute-corpus/tenant-fees/source.txt, sha256 484ebc24...a01766a) BEFORE the encoder's
question file was opened. Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair or a lint change.

UNITS maps each in-scope unit n of tenant-fees/units.jsonl (tools/sample5.py --units tenant-fees) to
  ("RULE", builder, note)       the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note (bridged / stated / refused boundary);
  ("NOT", None, cause, note)    not written (the ledger row's cause, CAUSES.tsv v2).
Grounding is mechanical: a rule "for every payment" is written once per item the case names; a quantifier over other
items ("an earlier holding deposit", "another requirement", "a requirement imposed before the deadline") is a
disjunction over the items the case LINKS by a stated binary fact (closed world over the case's items, an encoding
convention stated in cases.py). Vocabulary: sort item (a payment, contract or loan the case names), unary facts and
derived predicates on items, per-item integer constants (money in gbp_penny, dates in day).
"""
from __future__ import annotations

import hashlib
import json

GBP, DAY = "gbp_penny", "day"
INT_UNITS = {  # per-item integer constants: base name -> (unit, words)
    "amt": (GBP, "the amount of the item"),
    "proh": (GBP, "the amount of the item that is a prohibited payment"),
    "keycost": (GBP, "the costs reasonably incurred by the landlord or letting agent as a result of the lost key"),
    "keycap": (GBP, "the cap on a lost-key payment (Sch. 1 para. 4(3))"),
    "intcap": (GBP, "the late-rent cap (Sch. 1 para. 4(5)), from the bridge script"),
    "varcost": (GBP, "the reasonable costs of the variation, assignment or novation"),
    "cap6": (GBP, "the greater of 50 pounds and the reasonable costs (Sch. 1 para. 6(2))"),
    "applied6": (GBP, "the amount of the holding deposit applied with consent under Sch. 2 para. 6"),
    "repay": (GBP, "the amount of the holding deposit that must be repaid"),
    "received": (DAY, "the day the landlord or letting agent received the holding deposit"),
    "deadline": (DAY, "the deadline for agreement"),
    "agreedday": (DAY, "the day agreed in writing as the deadline for agreement"),
    "taday": (DAY, "the date of the tenancy agreement"),
    "decideday": (DAY, "the date on which the landlord decided not to enter into the tenancy agreement"),
    "tnotifyday": (DAY, "the day the tenant notified the decision not to enter into a tenancy agreement"),
    "noticeday": (DAY, "the day the notice in writing under Sch. 2 para. 5 was given"),
    "due": (DAY, "the due date of the rent payment"),
    "end14": (DAY, "the last day of the period of 14 days beginning with the due date"),
    "paidfull": (DAY, "the day the rent was paid in full"),
    "unpaidon": (DAY, "a day at whose end the rent remained unpaid"),
    "reqday": (DAY, "the day the requirement was imposed"),
    "repaylast": (DAY, "the last day of the period within which the holding deposit must be repaid"),
}
CASE_INTS = {"annual_rent": (GBP, "the annual rent payable in respect of the tenancy immediately after its grant, "
                                  "renewal or continuance"),
             "week_rent": (GBP, "one week's rent")}

FACTS = {  # unary facts on an item (the encoder states each true or false)
    "is_payment": "is a payment", "is_contract": "is a contract with a third party", "is_loan": "is a loan",
    "to_landlord": "is (to be) made to the landlord", "to_agent": "is (to be) made to a letting agent",
    "to_billing_authority": "is made to the billing authority (LGFA 1992 Part 1)",
    "to_bbc": "is made to the British Broadcasting Corporation",
    "payer_tenant": "is required of a tenant",
    "payer_for_tenant": "is required of a person acting on behalf of, or who has guaranteed the rent of, a tenant",
    "payer_lha": "is required of a local housing authority (Housing Act 1985)",
    "payer_gla": "is required of the Greater London Authority",
    "payer_for_authority": "is required of a person acting on behalf of a local housing authority or the GLA",
    "for_tenancy_event": "is required in consideration of the grant, renewal, continuance, variation, assignment, "
                         "novation or termination of the tenancy (s. 1(6)(a))",
    "on_act_or_default_term": "is required under a tenancy agreement term that requires it in the event of an act or "
                              "default of a relevant person (s. 1(6)(b))",
    "on_change_term": "is required under a tenancy agreement term that requires it if the tenancy is varied, assigned, "
                      "novated or terminated (s. 1(6)(c))",
    "other_agreement_term": "the landlord enters into a tenancy agreement requiring it in other circumstances (s. 1(6)(d))",
    "for_act_outside_agreement": "is required as a result of an act or default of a relevant person, otherwise than "
                                 "under or for breach of a tenancy agreement term (s. 1(6)(e))",
    "for_reference": "is required in consideration of providing a reference (s. 1(6)(f))",
    "offered_as_option": "is offered as an alternative to complying with another requirement of the landlord or agent",
    "unreasonable_other": "it would be unreasonable to expect a relevant person to comply with the other requirement "
                          "(stated judgment)",
    "contract_third_party": "is a contract with a third party",
    "contract_service": "is a contract for the provision of a service",
    "contract_insurance": "is a contract of insurance",
    "contract_utility": "is a contract for the provision of a utility to the tenant",
    "contract_communication": "is a contract for the provision of a communication service to the tenant",
    "security_for_tenant": "is money intended to be held as security for the performance of a tenant's obligations or "
                           "the discharge of a tenant's liability under or in connection with the tenancy",
    "by_or_for_tenant": "is paid by or on behalf of a tenant",
    "before_grant": "is paid before the grant of the tenancy",
    "intended_schedule2": "is paid with the intention that it be dealt with in accordance with Schedule 2",
    "default_payment": "is a payment in the event of a default by the tenant",
    "ta_requires": "the tenancy agreement requires the payment to be made",
    "lost_key": "the default is the loss of a key or other security device giving access to the housing",
    "late_rent": "the default is a failure to pay rent in full",
    "key_evidence": "the costs are supported by evidence in writing provided to the person required to pay",
    "earlier_other_charge": "before this requirement, the other of landlord and letting agent required a relevant "
                            "person to pay it for the same late-rent default",
    "damages": "is a payment of damages for breach of a tenancy agreement or of an agreement between a letting agent "
               "and a relevant person",
    "for_variation": "is in consideration of (for a letting agent: of arranging) the variation, assignment or "
                     "novation of the tenancy",
    "at_tenant_request": "the variation, assignment or novation is at the tenant's request",
    "council_tax": "is in respect of council tax",
    "utility_supply": "is for or in connection with the provision of electricity, gas or other fuel, or water or sewerage",
    "green_deal": "is towards energy efficiency improvements under a green deal plan (Energy Act 2011 s. 1)",
    "tv_licence": "is in respect of a television licence (Communications Act 2003 s. 363)",
    "agreed_deadline": "the landlord or letting agent agreed with the tenant in writing a different deadline day",
    "entered_agreement": "the landlord and the tenant entered into a tenancy agreement relating to the housing",
    "landlord_decided_not": "the landlord decided not to enter into a tenancy agreement relating to the housing",
    "applied_with_consent": "part or all of the deposit was applied, with the payer's consent, towards the first "
                            "payment of rent or the tenancy deposit",
    "ia_prohibited": "the landlord is prohibited by s. 22 Immigration Act 2014 from granting the tenancy to the tenant",
    "landlord_could_not_know": "the landlord did not know, and could not reasonably have been expected to know, the "
                               "prohibition applied before the deposit was accepted (stated judgment)",
    "agent_instructed": "the landlord instructed a letting agent in relation to the proposed tenancy",
    "agent_could_not_know": "the letting agent did not know, and could not reasonably have been expected to know, the "
                            "prohibition applied before the deposit was accepted (stated judgment)",
    "false_info": "the tenant provided false or misleading information to the landlord or letting agent",
    "reasonably_entitled": "the landlord is reasonably entitled to take that information or action into account in "
                           "deciding whether to grant a tenancy (stated judgment)",
    "tenant_notified": "the tenant notified the landlord or letting agent of a decision not to enter into a tenancy "
                       "agreement",
    "landlord_steps": "the landlord took all reasonable steps to enter into a tenancy agreement before the deadline "
                      "(stated judgment)",
    "agent_steps": "the letting agent took all reasonable steps to assist the landlord to enter into a tenancy "
                   "agreement before the deadline (stated judgment)",
    "tenant_failed_steps": "the tenant failed to take all reasonable steps to enter into a tenancy agreement before "
                           "the deadline (stated judgment)",
    "unreasonable_behaviour": "before the deadline, the landlord or an instructed agent behaved towards the tenant or a "
                              "relevant person so that it would be unreasonable to expect the tenant to enter into a "
                              "tenancy agreement with the landlord (stated judgment)",
    "believes_exception": "the person who received the deposit believes that one of Sch. 2 paras. 8 to 12 applies",
    "notice_given": "that person gave the payer a notice in writing explaining why they intend not to repay",
    "repaid_in_full": "the holding deposit has been repaid in full",
}
STATED = ("unreasonable_other", "landlord_could_not_know", "agent_could_not_know", "reasonably_entitled",
          "landlord_steps", "agent_steps", "tenant_failed_steps", "unreasonable_behaviour", "keycost", "varcost")
DERIVED = {
    "relevant": "the person required is a relevant person (s. 1(9), (10))",
    "excluded_authority": "the person is an authority, or acts for one, excluded by s. 1(10)",
    "required0": "the landlord requires it within s. 1(6) (ignoring s. 1(7))",
    "required": "the landlord requires it (s. 1(6) to (8))",
    "engaged": "the landlord requires it of a relevant person",
    "banned_contract": "is a contract s. 1(3) bars (not saved by s. 1(4))",
    "breach0": "requiring it is prohibited by s. 1, ignoring s. 1(7)",
    "breach": "the landlord's requirement of it breaches s. 1",
    "s18": "s. 1(7) does not apply (s. 1(8))",
    "permitted": "is a permitted payment by virtue of Schedule 1 (in-scope paragraphs)",
    "tenancy_deposit": "is a tenancy deposit (Sch. 1 para. 2(2))",
    "perm2": "is permitted by Sch. 1 para. 2(1)", "holding_deposit": "is a holding deposit (Sch. 1 para. 3(2))",
    "perm3": "is permitted by Sch. 1 para. 3", "not_permitted_35": "Sch. 1 para. 3(5) makes it not permitted",
    "counts_36": "was received on or after the coming into force of Schedule 2 (Sch. 1 para. 3(6))",
    "relevant_default": "the default is a relevant default (Sch. 1 para. 4(2))",
    "second_charge": "Sch. 1 para. 4(7) or (8) makes it a prohibited payment",
    "perm4": "is permitted by Sch. 1 para. 4", "perm5": "is permitted by Sch. 1 para. 5",
    "perm6": "is permitted by Sch. 1 para. 6", "perm8": "is permitted by Sch. 1 para. 8",
    "perm9": "is permitted by Sch. 1 para. 9", "perm10": "is permitted by Sch. 1 para. 10",
    "sch2": "Schedule 2 applies to it (para. 1)",
    "r3a": "Sch. 2 para. 3(a) holds", "r3b": "Sch. 2 para. 3(b) holds", "r3c": "Sch. 2 para. 3(c) holds",
    "p8": "Sch. 2 para. 8 applies", "p9": "Sch. 2 para. 9 applies", "p10": "Sch. 2 para. 10 applies",
    "p11": "Sch. 2 para. 11 applies", "p12": "Sch. 2 para. 12 applies", "p13": "Sch. 2 para. 13 applies",
    "a_eff": "para. 3(a) applies after para. 6", "b_eff": "para. 3(b) applies after paras. 8 and 9",
    "c_eff": "para. 3(c) applies after paras. 8 to 13",
    "must_repay3": "paragraph 3 applies (the deposit must be repaid under para. 3)",
    "notice_in_period": "the notice was given within the relevant period (Sch. 2 para. 5(2))",
    "p5": "Sch. 2 para. 5 requires repayment",
    "must_repay": "the holding deposit must be repaid",
    "excused": "paras. 6 to 12 of Sch. 2 have applied so as to permit the deposit not to be repaid",
}
BINARY = {"alternative_to": "the first item is offered as an alternative to the second (another requirement)",
          "earlier_same": "the second item is an earlier holding deposit received by the same landlord or agent for "
                          "the same housing as the first",
          "imposed_for": "the first item is a requirement imposed on the tenant or a relevant person in relation to "
                         "the second item's proposed tenancy"}
SCH2_IN_FORCE = "2019-06-01"  # the pinned file's Commencement Information I1 for Sch. 2 para. 1 (S.I. 2019/857 reg. 3(aa))
FIFTY_K = "50000.00"


# --- formula helpers (the ve-quantity@1 wire shapes; usecases/pawhp/rows_v2.py conventions) ---------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def B(p, x, y): return ["binary", p, c(x), c(y)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def gbp(v): return ["decimal", GBP, v]
def day(iso): return ["date", iso]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def add(tag, a, b): return ["add", tag, a, b]
def scale(tag, k, t): return ["scale", tag, str(k), t]
def minus(a, b): return add(GBP, a, scale(GBP, -1, b))


def And(*fs):
    fs = [f for f in fs if f is not None]
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["and", f, r]
    return r


def Or(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return None
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["or", f, r]
    return r


def k(base, x):
    """Per-item integer constant."""
    return ["const", INT_UNITS[base][0], f"{base}_{x}"]


def kc(name):
    return ["const", CASE_INTS[name][0], name]


def iff_atom(p, x, body):
    return Iff(U(p, x), body)


def cap_rules(x, guard, cap):
    """'if the amount ... exceeds <cap>, the amount of the excess is a prohibited payment' (and no excess otherwise)."""
    return [Implies(And(guard, Lt(cap, k("amt", x))), Eq(k("proh", x), minus(k("amt", x), cap))),
            Implies(And(guard, Le(k("amt", x), cap)), Eq(k("proh", x), gbp("0.00")))]


# --- the case context ---------------------------------------------------------------------------------------

class Ctx:
    def __init__(self, items, links=()):
        self.items = list(items)
        self.links = {(p, a, b) for (p, a, b) in links}

    def linked(self, pred, x):
        """Items y with the stated binary fact pred(x, y)."""
        return [b for (p, a, b) in sorted(self.links) if p == pred and a == x]

    def linked_to(self, pred, x):
        """Items y with the stated binary fact pred(y, x)."""
        return [a for (p, a, b) in sorted(self.links) if p == pred and b == x]


def each(fn):
    return lambda ctx: [f for x in ctx.items for f in fn(x, ctx)]


# --- the units (n = tenant-fees/units.jsonl) --------------------------------------------------------------------

def _payment_breach(x, req):
    return And(U(req, x), U("relevant", x),
               Or(And(U("is_payment", x), Lt(gbp("0.00"), k("proh", x))), U("banned_contract", x), U("is_loan", x)))


UNITS = {
    # ---- s. 1 ----
    1: ("RULE", each(lambda x, ctx: [iff_atom("breach", x, _payment_breach(x, "required"))]),
        "s. 1(1)+(2)+(3)+(5) as one classification of the requirement: payee landlord (1) or third party (2) both "
        "covered (any payee); 'make a prohibited payment' = some part of it is prohibited (proh > 0). A duty ('must "
        "not') carried as a yes/no classification of the requirement (breach), not as a norm"),
    2: ("RULE", lambda ctx: [], "carried by unit 1's rule (a payment to a third party: any payee)"),
    3: ("RULE", each(lambda x, ctx: [iff_atom("banned_contract", x, And(
        U("is_contract", x), U("contract_third_party", x), Or(U("contract_service", x), U("contract_insurance", x)),
        Not(Or(U("contract_utility", x), U("contract_communication", x)))))]),
        "s. 1(3) with (4); 'utility' per Sch. 1 para. 9(3), 'communication service' (para. 11(3), out of scope) a fact"),
    4: ("RULE", lambda ctx: [], "carried by unit 3's rule"),
    5: ("RULE", lambda ctx: [], "carried by unit 1's rule (is_loan: a loan to any person)"),
    6: ("RULE", each(lambda x, ctx: [iff_atom("required0", x, Or(
        U("for_tenancy_event", x), U("on_act_or_default_term", x), U("on_change_term", x),
        U("other_agreement_term", x), U("for_act_outside_agreement", x), U("for_reference", x)))]),
        "s. 1(6) 'if and only if' (a)-(f): each limb a stated circumstance (which limb a fact fits is encoder judgement)"),
    7: ("RULE", each(lambda x, ctx: [
        iff_atom("required", x, And(U("required0", x), Not(And(U("offered_as_option", x), Not(U("s18", x)))))),
        iff_atom("engaged", x, And(U("required", x), U("relevant", x))),
        iff_atom("breach0", x, _payment_breach(x, "required0"))]),
        "s. 1(7): an option offered as an alternative to another requirement is not 'required' unless s. 1(8)"),
    8: ("PART", each(lambda x, ctx: [iff_atom("s18", x, Or(
        *[And(B("alternative_to", x, y), U("breach0", y)) for y in ctx.linked("alternative_to", x)],
        U("unreasonable_other", x)))]),
        "other:judgment standard",
        "s. 1(8)(a) for another requirement of the landlord (s. 2 out: an agent's requirement is not carried, D4); "
        "(8)(b) 'unreasonable to expect' a stated fact (stated)"),
    9: ("RULE", each(lambda x, ctx: [iff_atom("relevant", x, Or(
        U("payer_tenant", x), And(U("payer_for_tenant", x), Not(U("excluded_authority", x)))))]),
        "s. 1(9): the person of whom the item is required"),
    10: ("PART", each(lambda x, ctx: [iff_atom("excluded_authority", x, Or(
        U("payer_lha", x), U("payer_gla", x), U("payer_for_authority", x)))]),
         "definition by reference", "s. 1(10)(a) 'local housing authority within the meaning of the Housing Act 1985' "
         "is a stated fact (the HA 1985 definition is not pinned); (b), (c) written"),
    # ---- s. 3(1) ----
    11: ("RULE", each(lambda x, ctx: [
        Implies(And(U("is_payment", x), Not(U("permitted", x))), Eq(k("proh", x), k("amt", x))),
        iff_atom("permitted", x, And(U("is_payment", x), Or(*[U(p, x) for p in (
            "perm2", "perm3", "perm4", "perm5", "perm6", "perm8", "perm9", "perm10")])))]),
         "s. 3(1) closes over the in-scope Sch. 1 paragraphs only (fixed fact: no payment falls under paras. 1, 1A, 7, "
         "11); a payment that is not permitted is prohibited in full"),
    # ---- Sch. 1 para. 2 ----
    12: ("RULE", each(lambda x, ctx: [iff_atom("perm2", x, And(U("is_payment", x), U("tenancy_deposit", x)))]),
         "para. 2(1)"),
    13: ("RULE", each(lambda x, ctx: [iff_atom("tenancy_deposit", x, U("security_for_tenant", x))]),
         "para. 2(2): 'money intended to be held as security for (a) obligations or (b) liability of a tenant' as one "
         "stated fact about the money's purpose"),
    14: ("RULE", each(lambda x, ctx: (
        cap_rules(x, And(U("perm2", x), Lt(kc("annual_rent"), gbp(FIFTY_K))), scale(GBP, 5, kc("week_rent"))) +
        cap_rules(x, And(U("perm2", x), Le(gbp(FIFTY_K), kc("annual_rent"))), scale(GBP, 6, kc("week_rent"))))),
         "para. 2(3): five or six weeks' rent at the 50,000 line; written (linear arithmetic over the week_rent constant)"),
    15: ("RULE", lambda ctx: [Eq(scale(GBP, 52, kc("week_rent")), kc("annual_rent"))],
         "para. 2(4): 'one week's rent' = annual rent / 52 written as 52 x week_rent = annual_rent on the penny grid "
         "(an annual rent not divisible by 52 to the penny has no solution: nothing derived)"),
    # ---- Sch. 1 para. 3 ----
    16: ("RULE", each(lambda x, ctx: [iff_atom("perm3", x, And(U("holding_deposit", x), Not(U("not_permitted_35", x))))]),
         "para. 3(1) subject to (3)-(6)"),
    17: ("RULE", each(lambda x, ctx: [iff_atom("holding_deposit", x, And(
        U("is_payment", x), U("by_or_for_tenant", x), Or(U("to_landlord", x), U("to_agent", x)), U("before_grant", x),
        U("intended_schedule2", x)))]),
         "para. 3(2)"),
    18: ("RULE", each(lambda x, ctx: cap_rules(x, U("perm3", x), kc("week_rent"))), "para. 3(3)"),
    19: ("RULE", lambda ctx: [Eq(scale(GBP, 52, kc("week_rent")), kc("annual_rent"))], "para. 3(4) (= unit 15)"),
    20: ("RULE", each(lambda x, ctx: [iff_atom("not_permitted_35", x, Or(
        *[And(B("earlier_same", x, y), U("holding_deposit", y), U("counts_36", y), Not(U("repaid_in_full", y)),
              Not(U("excused", y))) for y in ctx.linked("earlier_same", x)]) or ["not", ["true"]])]),
         "para. 3(5) (D2: IN): an earlier deposit is an item of the case linked by earlier_same; 'none of paras. 6 to "
         "12 have applied so as to permit not to repay' = not excused (the earlier deposit's own Sch. 2 rules)"),
    21: ("RULE", each(lambda x, ctx: [iff_atom("counts_36", x, ["date_no_later", day(SCH2_IN_FORCE), k("received", x)])]),
         "para. 3(6): Sch. 2 in force 1 June 2019 (the pinned file's commencement note)"),
    # ---- Sch. 1 para. 4 ----
    22: ("RULE", each(lambda x, ctx: [iff_atom("perm4", x, And(
        U("is_payment", x), U("default_payment", x), U("relevant_default", x), U("ta_requires", x),
        Not(U("second_charge", x))))]),
         "para. 4(1) subject to (3)-(8); (7), (8) make the second payment prohibited in full"),
    23: ("PART", each(lambda x, ctx: [
        ["shift_days", k("end14", x), k("due", x), "13"],
        Implies(U("lost_key", x), U("relevant_default", x)),
        Implies(And(U("late_rent", x), ["date_after", k("paidfull", x), k("end14", x)]), U("relevant_default", x)),
        Implies(And(U("late_rent", x), ["date_no_later", k("end14", x), k("unpaidon", x)]), U("relevant_default", x)),
        Implies(And(Not(U("lost_key", x)), U("late_rent", x), ["date_no_later", k("paidfull", x), k("end14", x)]),
                Not(U("relevant_default", x))),
        Implies(And(Not(U("lost_key", x)), Not(U("late_rent", x))), Not(U("relevant_default", x)))]),
         "deadline/time limit",
         "para. 4(2): '14 days beginning with the due date' written (shift_days 13); 'in full before the end of' = paid "
         "on or before that day; the rent's own facts (due date, day paid in full or a day it was still unpaid) stated"),
    24: ("PART", each(lambda x, ctx: [
        Implies(U("key_evidence", x), Eq(k("keycap", x), k("keycost", x))),
        Implies(Not(U("key_evidence", x)), Eq(k("keycap", x), gbp("0.00"))),
        *cap_rules(x, And(U("perm4", x), U("lost_key", x), Or(U("to_landlord", x), U("to_agent", x))), k("keycap", x))]),
         "other:judgment standard",
         "para. 4(3): 'reasonably incurred' costs a stated amount (stated); evidence in writing a fact; without it the "
         "cap is 0"),
    25: ("RULE", each(lambda x, ctx: cap_rules(
        x, And(U("perm4", x), U("late_rent", x), Or(U("to_landlord", x), U("to_agent", x))), k("intcap", x))),
         "para. 4(4): the cap is the para. 4(5) amount (unit 26, bridged)"),
    26: ("NOT", None, "amount arithmetic",
         "para. 4(5): a sum over days of rate x unpaid rent / day count: products of two quantities and a sum over "
         "days are not in the linear fragment; the amount comes from the tested bridge script (bridged), with the "
         "stated convention (simple, /365, rounded down)"),
    27: ("NOT", None, "definition by reference",
         "para. 4(6): the base rate is announced by the MPC (or the Treasury under BoEA 1998 s. 19): a stated value "
         "per day, read only by the bridge"),
    28: ("RULE", each(lambda x, ctx: [iff_atom("second_charge", x, And(
        U("late_rent", x), U("earlier_other_charge", x), Or(U("to_landlord", x), U("to_agent", x))))]),
         "para. 4(7) and (8) as one rule: the later of a landlord's and an agent's charge for the same (2)(b) default"),
    29: ("RULE", lambda ctx: [], "carried by unit 28's rule"),
    # ---- Sch. 1 para. 5 ----
    30: ("RULE", each(lambda x, ctx: [iff_atom("perm5", x, And(U("is_payment", x), U("damages", x))),
                                      Implies(U("perm5", x), Eq(k("proh", x), gbp("0.00")))]),
         "para. 5 (no cap; 'damages for breach' a stated fact)"),
    # ---- Sch. 1 para. 6 ----
    31: ("RULE", each(lambda x, ctx: [iff_atom("perm6", x, And(
        U("is_payment", x), U("for_variation", x), U("at_tenant_request", x), Or(U("to_landlord", x), U("to_agent", x))))]),
         "para. 6(1)(a) landlord (in consideration of) and (b) agent (of arranging): one fact for_variation"),
    32: ("PART", each(lambda x, ctx: [
        Implies(U("perm6", x), Le(gbp("50.00"), k("cap6", x))),
        Implies(And(U("perm6", x), Le(gbp("50.00"), k("varcost", x))), Eq(k("cap6", x), k("varcost", x))),
        Implies(And(U("perm6", x), Lt(k("varcost", x), gbp("50.00"))), Eq(k("cap6", x), gbp("50.00"))),
        *cap_rules(x, U("perm6", x), k("cap6", x))]),
         "other:judgment standard",
         "para. 6(2): the greater of 50 and 'the reasonable costs' (a stated amount, stated); 'greater of' written by "
         "cases; with no stated costs, an amount up to 50 still has no excess"),
    # ---- Sch. 1 paras. 8 to 10 ----
    33: ("RULE", each(lambda x, ctx: [iff_atom("perm8", x, And(U("is_payment", x), U("to_billing_authority", x),
                                                               U("council_tax", x))),
                                      Implies(U("perm8", x), Eq(k("proh", x), gbp("0.00")))]), "para. 8(1)"),
    34: ("NOT", None, "definition by reference",
         "para. 8(2): 'billing authority' has the LGFA 1992 Part 1 meaning: a stated fact (to_billing_authority)"),
    35: ("RULE", each(lambda x, ctx: [iff_atom("perm9", x, And(U("is_payment", x), U("ta_requires", x), Or(
        U("utility_supply", x), U("green_deal", x)))), Implies(U("perm9", x), Eq(k("proh", x), gbp("0.00")))]),
         "para. 9(1) with (2) in one rule"),
    36: ("PART", lambda ctx: [], "definition by reference",
         "para. 9(2): written in unit 35's rule; 'green deal plan (Energy Act 2011 s. 1)' a stated fact"),
    37: ("RULE", lambda ctx: [], "para. 9(3): the closed list (electricity, gas or other fuel, water or sewerage) is "
                                 "the wording of the fact utility_supply; no further formula"),
    38: ("RULE", each(lambda x, ctx: [iff_atom("perm10", x, And(U("is_payment", x), U("to_bbc", x), U("tv_licence", x),
                                                                U("ta_requires", x))),
                                      Implies(U("perm10", x), Eq(k("proh", x), gbp("0.00")))]), "para. 10(1)"),
    39: ("NOT", None, "definition by reference",
         "para. 10(2): 'television licence' = Communications Act 2003 s. 363: a stated fact"),
    # ---- Sch. 2 ----
    40: ("RULE", each(lambda x, ctx: [iff_atom("sch2", x, U("holding_deposit", x))]),
         "para. 1 (paid to a landlord or agent: inside holding_deposit; England: fixed fact)"),
    41: ("PART", each(lambda x, ctx: [Implies(And(U("sch2", x), Not(U("agreed_deadline", x))),
                                              ["shift_days", k("deadline", x), k("received", x), "14"])]),
         "deadline/time limit",
         "para. 2(1): 'the fifteenth day of the period beginning with' receipt = received + 14 days (written)"),
    42: ("RULE", each(lambda x, ctx: [Implies(And(U("sch2", x), U("agreed_deadline", x)),
                                              Eq(k("deadline", x), k("agreedday", x)))]), "para. 2(2)"),
    43: ("PART", each(lambda x, ctx: [
        iff_atom("r3a", x, And(U("sch2", x), U("entered_agreement", x))),
        Implies(And(U("sch2", x), U("landlord_decided_not", x), ["date_before", k("decideday", x), k("deadline", x)]),
                U("r3b", x)),
        Implies(Or(Not(U("sch2", x)), Not(U("landlord_decided_not", x)),
                   ["date_after", k("decideday", x), k("deadline", x)]), Not(U("r3b", x))),
        Implies(And(U("sch2", x), Not(U("entered_agreement", x))), U("r3c", x)),
        Implies(And(U("sch2", x), U("entered_agreement", x), ["date_after", k("taday", x), k("deadline", x)]),
                U("r3c", x)),
        Implies(Or(Not(U("sch2", x)), And(U("entered_agreement", x), ["date_before", k("taday", x), k("deadline", x)])),
                Not(U("r3c", x)))]),
         "deadline/time limit",
         "para. 3: 'before the deadline for agreement' when the event falls ON the deadline day: before that day, or by "
         "its end? Two readings: no rule fires (refused); before and after the day written. 'fail to enter' with no "
         "agreement at all is read as failing (the question's date is after the deadline)"),
    44: ("RULE", each(lambda x, ctx: [
        Implies(U("a_eff", x), ["shift_days", k("repaylast", x), k("taday", x), "6"]),
        Implies(U("b_eff", x), ["shift_days", k("repaylast", x), k("decideday", x), "6"]),
        Implies(U("c_eff", x), ["shift_days", k("repaylast", x), k("deadline", x), "6"]),
        iff_atom("must_repay3", x, Or(U("a_eff", x), U("b_eff", x), U("c_eff", x))),
        Implies(U("a_eff", x), Eq(k("repay", x), minus(k("amt", x), k("applied6", x)))),
        Implies(Or(U("b_eff", x), U("c_eff", x)), Eq(k("repay", x), k("amt", x)))]),
         "para. 4: '7 days beginning with' D = the last day D + 6 (written); two limbs with different days give two "
         "dates (D1: no date derived)"),
    45: ("RULE", each(lambda x, ctx: [
        iff_atom("p5", x, And(U("sch2", x), U("believes_exception", x), Not(U("notice_in_period", x)))),
        Implies(And(U("p5", x), Not(U("must_repay3", x))), Eq(k("repay", x), k("amt", x))),
        iff_atom("must_repay", x, Or(U("must_repay3", x), U("p5", x)))]),
         "para. 5(1); para. 5 sets no period (D6: date NONE when only para. 5 applies)"),
    46: ("RULE", each(lambda x, ctx: [
        Implies(And(U("r3b", x), Not(U("notice_given", x))), Not(U("notice_in_period", x))),
        Implies(And(U("r3c", x), Not(U("notice_given", x))), Not(U("notice_in_period", x))),
        Implies(And(U("r3b", x), U("notice_given", x)),
                Iff(U("notice_in_period", x), ["within_days", k("noticeday", x), k("decideday", x), "6"])),
        Implies(And(U("r3c", x), U("notice_given", x)),
                Iff(U("notice_in_period", x), ["within_days", k("noticeday", x), k("deadline", x), "6"]))]),
         "para. 5(2)(a), (b): '7 days beginning with' written (within_days 6); both periods at once and the notice in "
         "one only: two outcomes (D1)"),
    47: ("RULE", each(lambda x, ctx: [
        Implies(Not(U("applied_with_consent", x)), Eq(k("applied6", x), gbp("0.00"))),
        iff_atom("a_eff", x, And(U("r3a", x), Lt(k("applied6", x), k("amt", x))))]),
         "para. 6: 3(a) does not apply 'if or to the extent that' the deposit is applied with consent: the amount "
         "applied is a stated amount; the rest is repaid"),
    48: ("NOT", None, "other:deeming",
         "para. 7: deems the amount applied 'received by the landlord on the date of the tenancy agreement' for HA 2004 "
         "s. 213 (out of the pin; secondary cross-reference); no question kind asks it"),
    49: ("PART", each(lambda x, ctx: [iff_atom("p8", x, And(
        U("ia_prohibited", x), U("landlord_could_not_know", x),
        Or(Not(U("agent_instructed", x)), U("agent_could_not_know", x))))]),
         "cross-reference",
         "para. 8: (a) prohibition by IA 2014 s. 22 a stated fact (cross-reference); (b), (c) 'could not reasonably "
         "have been expected to know' stated facts (secondary other:judgment standard, stated)"),
    50: ("PART", each(lambda x, ctx: [iff_atom("p9", x, And(U("false_info", x), U("reasonably_entitled", x)))]),
         "other:judgment standard", "para. 9: (a) or (b) 'reasonably entitled' one stated fact (stated)"),
    51: ("PART", each(lambda x, ctx: [
        Implies(And(U("tenant_notified", x), ["date_before", k("tnotifyday", x), k("deadline", x)]), U("p10", x)),
        Implies(Or(Not(U("tenant_notified", x)), ["date_after", k("tnotifyday", x), k("deadline", x)]),
                Not(U("p10", x)))]),
         "deadline/time limit", "para. 10: 'before the deadline' ON the deadline day refused (as unit 43)"),
    52: ("PART", each(lambda x, ctx: [iff_atom("p11", x, And(
        U("to_landlord", x), U("landlord_steps", x), Or(Not(U("agent_instructed", x)), U("agent_steps", x)),
        U("tenant_failed_steps", x)))]),
         "other:judgment standard", "para. 11: 'all reasonable steps' stated facts (stated)"),
    53: ("PART", each(lambda x, ctx: [iff_atom("p12", x, And(
        U("to_agent", x), U("agent_steps", x), U("landlord_steps", x), U("tenant_failed_steps", x)))]),
         "other:judgment standard", "para. 12: 'all reasonable steps' stated facts (stated)"),
    54: ("PART", each(lambda x, ctx: [
        iff_atom("p13", x, Or(
            *[And(B("imposed_for", y, x), U("breach", y), ["date_before", k("reqday", y), k("deadline", x)])
              for y in ctx.linked_to("imposed_for", x)],
            U("unreasonable_behaviour", x))),
        iff_atom("b_eff", x, And(U("r3b", x), Not(U("p8", x)), Not(U("p9", x)))),
        iff_atom("c_eff", x, And(U("r3c", x), Not(U("p8", x)), Not(U("p9", x)),
                                 Not(And(Or(U("p10", x), U("p11", x), U("p12", x)), Not(U("p13", x)))))),
        iff_atom("excused", x, And(Or(U("r3a", x), U("r3b", x), U("r3c", x)), Not(U("must_repay3", x))))]),
         "other:judgment standard",
         "para. 13: (a) a breach of s. 1 by a requirement the case links (s. 2 out, D4); (b) 'unreasonable to expect' "
         "a stated fact (stated). Also here: the exceptions' effect on 3(b), 3(c) (paras. 8, 9 and 10-12 under 13) "
         "and 'excused' for Sch. 1 para. 3(5)(c)"),
}


def _no_true(f):
    """unit 20 with no linked earlier deposit: 'not_permitted_35' is simply false."""
    return f


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a case: [{"id", "unit", "formula", "defines"}]."""
    out = []
    for n, entry in sorted(units_table(mutant).items()):
        if entry[0] not in ("RULE", "PART") or entry[1] is None:
            continue
        for i, f in enumerate(entry[1](ctx)):
            f = _fix_empty(f)
            if f is None:
                continue
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


def _fix_empty(f):
    """An iff whose right side is the empty disjunction (no linked item) becomes 'not atom'."""
    if is_iff(f) and f[1][2] == ["not", ["true"]]:
        return ["not", f[1][1]]
    return f


# --- structure helpers (pawhp translation.py conventions) --------------------------------------------------------

def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def is_iff(f):
    return (type(f) is list and f and f[0] == "and" and type(f[1]) is list and type(f[2]) is list
            and f[1][:1] == ["implies"] and f[2][:1] == ["implies"] and f[1][1] == f[2][2] and f[1][2] == f[2][1])


def conjuncts(f):
    if is_iff(f) or type(f) is not list or f[0] != "and":
        return [f]
    return conjuncts(f[1]) + conjuncts(f[2])


def atoms_in(f, atoms, constants):
    if type(f) is not list or not f:
        return
    if f[0] in ("unary", "binary"):
        atoms.add(key(f))
        return
    if f[0] == "const" and len(f) == 3:
        constants.add(f[2])
        return
    for part in f[1:]:
        atoms_in(part, atoms, constants)


def defines(f):
    """The atoms / integer constants a ground rule fixes."""
    if is_iff(f):
        lhs = f[1][1]
        if lhs[0] in ("unary", "binary"):
            return [key(lhs)]
        raise ValueError(f"iff with a non-atom left side: {f}")
    if f[0] == "implies":
        return defines(f[2])
    if f[0] in ("unary", "binary"):
        return [key(f)]
    if f[0] == "not" and f[1][0] in ("unary", "binary"):
        return [key(f[1])]
    if f[0] in ("eq", "shift_days") and f[1][0] == "const" and len(f[1]) == 3:
        return [f[1][2]]
    if f[0] == "eq" and f[1][0] == "scale" and f[1][3][0] == "const" and len(f[1][3]) == 3:
        return [f[1][3][2]]
    if f[0] == "le" and f[2][0] == "const" and len(f[2]) == 3:
        return [f[2][2]]
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case ---------------------------------------------------------------------------------

def environment(ctx):
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's item {x}.", "verbalisation": f"item {x}"}
        for base, (u, w) in INT_UNITS.items():
            consts[f"{base}_{x}"] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                                     "verbalisation": f"{w} ({x})"}
    for name, (u, w) in CASE_INTS.items():
        consts[name] = {"sort": "$int", "unit": u, "description": w[0].upper() + w[1:] + ".", "verbalisation": w}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**FACTS, **DERIVED}.items()}
    preds.update({n: {"arguments": ["item", "item"], "description": d[0].upper() + d[1:] + "."}
                  for n, d in BINARY.items()})
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "A payment, contract or loan the case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}},
                      GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP", "input_symbol": "£"}}}}


# --- planted errors (run.py --mutants): each must change the answer of a named question ---------------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _walk_replace(old, new):
    def walk(f):
        if f == old:
            return new
        if type(f) is list:
            return [walk(x) for x in f]
        return f
    return walk


def _wrap(walker):
    return lambda builder: (lambda ctx: [walker(f) for f in builder(ctx)])


MUTANTS = {
    "M1": ("Sch. 1 para. 2(3): five weeks' rent read as four",
           _swap(14, _wrap(_walk_replace(scale(GBP, 5, kc("week_rent")), scale(GBP, 4, kc("week_rent")))))),
    "M2": ("Sch. 2 para. 2(1): the deadline read as the 14th day (received + 13)",
           _swap(41, _wrap(lambda f: json.loads(json.dumps(f).replace('"14"]', '"13"]'))))),
    "M3": ("Sch. 2 para. 4: 7 days beginning with D read as ending on D + 7",
           _swap(44, _wrap(lambda f: json.loads(json.dumps(f).replace('"6"]', '"7"]'))))),
    "M4": ("Sch. 1 para. 4(2)(b): 14 days read as ending on the due date + 14",
           _swap(23, _wrap(lambda f: json.loads(json.dumps(f).replace('"13"]', '"14"]'))))),
    "M5": ("Sch. 1 para. 6(2): the 50 pound floor read as 30",
           _swap(32, _wrap(_walk_replace(gbp("50.00"), gbp("30.00"))))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
