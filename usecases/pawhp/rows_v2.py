"""PAWHP (SSI 2024/351) formulas: pass65.py v2 lines 37-348, copied byte for byte (no edit).

Source: manage-agents reviews/spare/spare-second-statute/tools/pass65.py (sha256 0a1acb87...8662e), written by
dri-spare-second-statute-q-1123 and finished 2026-11-23 09:05Z, before the question writer started (09:03Z run, files
09:11Z). v1 graded 21 of 29 by a non-author (GRADES.md); v2 = v1 + the grader five fixes. translation.py checks the slice
hash at import. SAME-FAMILY (Opus).
"""


QW0, QW1 = "2026-09-21", "2026-09-27"      # bridge: qualifying week 2026 (week beginning the third Monday of September)
QW_MINUS_12W = "2026-06-29"                # bridge: first day of the 12 weeks immediately preceding the week (QW0 - 84)
END_MARCH = "2027-03-31"                   # bridge: 31 March in the year following the week
BENEFITS = {"pension_credit": "state pension credit", "income_based_jsa": "income-based jobseeker's allowance",
            "income_related_esa": "income-related employment and support allowance",
            "income_support": "income support", "universal_credit": "universal credit"}
DAY = {"scale": "1", "display": {"kind": "iso_date"}}
INTS = {  # name: (unit, words)
    "applicant_pa_date": ("day", "the applicant's pensionable-age date"),
    "applicant_eightieth": ("day", "the applicant's 80th birthday"),
    "applicant_scot_from": ("day", "the applicant's first day of ordinary residence in Scotland"),
    "applicant_scot_last_day": ("day", "the applicant's last day of ordinary residence in Scotland"),
    "applicant_care_from": ("day", "the first day the applicant lived in a care home or independent hospital"),
    "applicant_care_last_day": ("day", "the last day the applicant lived in a care home or independent hospital"),
    "applicant_received": ("day", "the day the Scottish Ministers received the applicant's application"),
    "applicant_application": ("day", "the day the applicant's application is treated as made"),
    "applicant_opt_in_day": ("day", "the day the applicant's opt-in request was made"),
    "amount": ("gbp_penny", "the applicant's payment amount"),
}
PERSON1 = {
    "entitled": "is entitled to Pension Age Winter Heating Payment for the qualifying week",
    "reached_pa": "has reached pensionable age before or on a day in the qualifying week (reg. 6)",
    "reached_80": "has reached the age of 80 in or before the qualifying week",
    "residence_condition": "satisfies the residence condition (reg. 8(1))",
    "meets_8_2": "meets the condition in reg. 8(2)",
    "meets_8_2a": "is treated as meeting reg. 8(2)(a) (ordinarily resident in Scotland on a day of the week, after 8(3))",
    "meets_8_2b": "meets reg. 8(2)(b)",
    "meets_8_2bi": "meets reg. 8(2)(b)(i) after reg. 8(4)",
    "meets_8_2bii": "is subject to immigration control but within a sub-head of reg. 8(2)(b)(ii) on a day of the week",
    "not_pic_some_day": "is not subject to immigration control (s.115(9) IAA 1999) on at least one day of the week",
    "pic_by_last_day": "is subject to immigration control by the last day of the week",
    "ever_resident_scot": "has been ordinarily resident in Scotland",
    "remains_resident_scot": "remains ordinarily resident in Scotland (no last day)",
    "ever_in_care": "has lived in a care home or independent hospital (temporary absences disregarded)",
    "remains_in_care": "still lives in a care home or independent hospital (no last day)",
    "in_residential_care": "is in residential care (reg. 2)",
    "own_rb_day": "is entitled in their own right to a relevant benefit on a day in the qualifying week",
    "own_rb_throughout": "on every day of the qualifying week is entitled in their own right to at least one relevant benefit (not necessarily the same one)",
    "rb_each_day_with_member": "on every day of the qualifying week the person, or another member of their couple or polygamous marriage, is entitled in their own right to at least one relevant benefit",
    "bii_possible": "the question says the person is subject to immigration control and may fall within a sub-head of reg. 8(2)(b)(ii)",
    "applied": "made an application for Pension Age Winter Heating Payment for the qualifying week",
    "eff_rb_day": "is entitled, or treated under reg. 2A as entitled, to a relevant benefit on a day in the week",
    "eff_rb_throughout": "is entitled, or treated under reg. 2A as entitled, to a relevant benefit throughout the week",
    "wfp_awarded": "has been awarded a winter fuel payment under the 2024 GB or NI Regulations for the week",
    "wfp_award_in_error": "that winter fuel payment award was made in error",
    "wfp_regarded": "is regarded as having been awarded a winter fuel payment for the week (reg. 4)",
    "excluded_9": "is not entitled by virtue of reg. 9",
    "fipt_throughout_qw": "receives free in-patient treatment throughout the qualifying week",
    "fipt_52w_before": "has received free in-patient treatment for the 52 weeks immediately preceding the week",
    "custody_throughout_qw": "is detained in legal custody under a sentence imposed by a court throughout the week",
    "paid_for_qw": "has been paid Pension Age Winter Heating Payment, or a winter fuel payment under the 2024 GB or NI "
                   "Regulations, in respect of the qualifying week",
    "opt_out_before_payment": "notified an opt-out request received before this week's payment would otherwise be made",
    "opt_in_before_payment": "notified an opt-in request received before this week's payment falls to be made",
    "opt_in_made": "made an opt-in request after the opt-out",
    "opt_in_future_only": "stated that the opt-in request is to take effect for future payments only",
    "opt_in_restores": "has an opt-in request with effect for this week's payment (reg. 9B(3))",
    "opt_out_in_effect": "has an opt-out request in effect for this week's payment (reg. 9A)",
    "para_4": "reg. 10(4) applies to the person",
    "para_5": "reg. 10(5) applies to the person",
    "para_6": "reg. 10(6) applies to the person",
    "deadline_16b2_applies": "the 31 March limit of reg. 16B(2) applies to the person",
    "application_in_time": "made the application in time under reg. 16B",
    "rb_by_later_decision": "a decision made after the week makes the person entitled, for a day in the week, to a relevant benefit",
    "s115_ceased_by_later_decision": "a decision made after the week is that s.115 IAA 1999 ceases to apply for the week",
    "married_to_several": "is for the time being married to more than one person",
}
PREDS = {
    **{p: (["person"], d) for p, d in PERSON1.items()},
    "relevant_benefit": (["benefit"], "is a relevant benefit (reg. 2)"),
    "benefit_day": (["person", "benefit"], "the person is entitled to the benefit on a day in the qualifying week"),
    "benefit_throughout": (["person", "benefit"], "the person is entitled to the benefit throughout the qualifying week"),
    "married_or_cp": (["person", "person"], "the two people are married to, or civil partners of, each other"),
    "same_household": (["person", "person"], "the two people are members of the same household"),
    "living_as_married": (["person", "person"], "the two people live together as if they were a married couple or civil partners"),
    "couple_with": (["person", "person"], "the two people are a couple (reg. 2)"),
    "polygamous_with": (["person", "person"], "the two people are different members of the same polygamous marriage"),
    "share_mutual_home": (["person", "person"], "the two people share accommodation as their mutual home on the last "
                                                "day of the week (temporary absences disregarded)"),
    "lives_with": (["person", "person"], "the first person lives with the second on the last day of the week (reg. 10(9))"),
    "polygamous_marriage": (["marriage"], "a polygamous marriage (reg. 2)"),
    "under_polygamy_law": (["marriage"], "took place under the laws of a country which permits polygamy"),
    "member_of": (["person", "marriage"], "the person is a member of the marriage"),
}


def environment():
    consts = {"applicant": {"sort": "person", "description": "The applicant.", "verbalisation": "the applicant"}}
    for n, w in BENEFITS.items():
        consts[n] = {"sort": "benefit", "description": f"The benefit {w}.", "verbalisation": w}
    for n, (u, w) in INTS.items():
        consts[n] = {"sort": "$int", "unit": u, "description": w[0].upper() + w[1:] + ".", "verbalisation": w}
    preds = {n: {"arguments": a, "description": d[0].upper() + d[1:] + "."} for n, (a, d) in PREDS.items()}
    sorts = {s: {"description": f"A {s}."} for s in ("person", "benefit", "marriage")}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": sorts, "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {"day": DAY, "gbp_penny": {"scale": "100", "display": {"kind": "money", "currency": "GBP",
                                                                             "input_symbol": "£"}}}}


def c(n): return ["const", n]
def ci(n): return ["const", INTS[n][0], n]
def day(iso): return ["date", iso]
def gbp(t): return ["decimal", "gbp_penny", t]
def t(x): return c(x) if isinstance(x, str) else x
def U(p, x): return ["unary", p, t(x)]
def B(p, x, y): return ["binary", p, t(x), t(y)]
def Not(f): return ["not", f]
def V(i): return ["var", i]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def All(sort, f): return ["forall", sort, f]
def Ex(sort, f): return ["exists", sort, f]
def Eq(a, b): return ["eq", a, b]
def amount(v): return Eq(ci("amount"), gbp(v))


def And(*fs):
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["and", f, r]
    return r


def Or(*fs):
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["or", f, r]
    return r


def P1(p, body):  # forall person p. body(V(0)) -- unary rules for every person
    return All("person", body(V(0)))


def P2(body):  # forall person p, forall person q. body(p, q) with p = V(1), q = V(0)
    return All("person", All("person", body(V(1), V(0))))


def member_or_couple(p, q):  # p, q terms at the same depth
    return Or(B("couple_with", p, q), B("polygamous_with", p, q))


A = "applicant"
some_day_scot = And(U("ever_resident_scot", A), ["date_no_later", ci("applicant_scot_from"), day(QW1)],
                    Or(U("remains_resident_scot", A), ["date_no_later", day(QW0), ci("applicant_scot_last_day")]))
gone_by_last_day = And(Not(U("remains_resident_scot", A)), ["date_before", ci("applicant_scot_last_day"), day(QW1)])
# "lives with any other entitled individual" (on the last day, 10(7)); q = V(0) inside the exists, applicant a constant
lw_ent = Ex("person", And(B("lives_with", A, V(0)), U("entitled", V(0))))
lw_ent_80 = Ex("person", And(B("lives_with", A, V(0)), U("entitled", V(0)), U("reached_80", V(0))))
lw_ent_u80 = Ex("person", And(B("lives_with", A, V(0)), U("entitled", V(0)), Not(U("reached_80", V(0)))))
amount_guard = lambda para: And(U(para, A), U("entitled", A), Not(U("opt_out_in_effect", A)))  # noqa: E731

T = {
    # ---- reg. 2 (terms used) ----
    1: ("NAME", None, "the 2018 Act: a statute named by its title"),
    2: ("NAME", None, "care home: defined by PSR(S)A 2010 sch. 12 para. 2; a fact inside ever_in_care"),
    3: ("RULE", P2(lambda p, q: Iff(B("couple_with", p, q), And(Not(Eq(p, q)),
                                    Or(And(B("married_or_cp", p, q), B("same_household", p, q)),
                                       And(Not(B("married_or_cp", p, q)), B("living_as_married", p, q)))))),
        "both limbs; 'two people' = two different people (v2: grader row 3)"),
    4: ("NAME", None, "determination: by reference to the 2018 Act s.25; used only in Part 5 (out)"),
    5: ("NAME", None, "free in-patient treatment: defined by SI 2005/3360 reg. 2(4),(5); a fact inside fipt_*"),
    6: ("NAME", None, "income support: a benefit named by its Act: a declared constant"),
    7: ("NAME", None, "income-based JSA: a benefit named by its Act: a declared constant"),
    8: ("NAME", None, "income-related ESA: a benefit named by its Act: a declared constant"),
    9: ("NAME", None, "independent hospital: defined by other Acts; a fact inside ever_in_care"),
    10: ("NAME", None, "Pension Age Winter Heating Payment: a label of this instrument with no condition (reported with "
                       "the names; if counted in the denominator, the share is given beside)"),
    11: ("NAME", None, "pensionable age: Pensions Act 1995 sch. 4 para. 1; the date is a bridge (tested script)"),
    12: ("RULE", And(All("person", B("same_household", V(0), V(0))),
                     All("marriage", Iff(["unary", "polygamous_marriage", V(0)],
                         And(["unary", "under_polygamy_law", V(0)],
                             Ex("person", And(["binary", "member_of", V(0), V(1)], U("married_to_several", V(0)))),
                             All("person", All("person", Implies(And(["binary", "member_of", V(1), V(2)],
                                                                     ["binary", "member_of", V(0), V(2)]),
                                                                 B("same_household", V(1), V(0)))))))),
                     P2(lambda p, q: Iff(B("polygamous_with", p, q),
                                         And(Not(Eq(p, q)),
                                             Ex("marriage", And(["unary", "polygamous_marriage", V(0)],
                                                                ["binary", "member_of", V(2), V(0)],
                                                                ["binary", "member_of", V(1), V(0)])))))),
         "(a) and (b) of the definition; reflexive same_household stated (challenge B4); polygamous_with links two "
         "DIFFERENT members of one polygamous marriage, so 2A, 9(d) and 10(4)(a)(ii) never pick the person themself"),
    13: ("NOT", None, "qualifying week = the week beginning on the third Monday of September: a calendar computation "
                      "with no weekday function in the language; carried as a bridge (QW0, QW1) by the tested script"),
    14: ("RULE", And(*(U("relevant_benefit", b) for b in BENEFITS),
                     All("benefit", Implies(["unary", "relevant_benefit", V(0)],
                                            Or(*(Eq(V(0), c(b)) for b in BENEFITS)))),
                     P1(None, lambda p: Iff(U("own_rb_day", p), Ex("benefit", And(["unary", "relevant_benefit", V(0)],
                                                                                   ["binary", "benefit_day", V(1), V(0)])))),
                     P1(None, lambda p: Implies(Ex("benefit", And(["unary", "relevant_benefit", V(0)],
                                                                  ["binary", "benefit_throughout", V(1), V(0)])),
                                                U("own_rb_throughout", p)))),
         "the closed list (a)-(e) ('(f)' is empty in the revised text); 'entitled to a relevant benefit throughout the "
         "week' = some relevant benefit on every day (v2: grader row 14): one benefit throughout implies it; a change of "
         "benefit inside the week is a stated fact (own_rb_throughout), no day quantifier in the vocabulary"),
    15: ("RULE", Iff(U("in_residential_care", A),
                     And(U("ever_in_care", A), ["date_no_later", ci("applicant_care_from"), day(QW_MINUS_12W)],
                         Or(U("remains_in_care", A), ["date_no_later", day(QW1), ci("applicant_care_last_day")]))),
         "throughout the week and the 12 weeks immediately before it = from 29 Jun 2026 (QW0 - 84 days, a bridge) to "
         "27 Sep 2026; one care interval, temporary absences disregarded by the facts; for other people a fact"),
    16: ("NAME", None, "state pension credit: a benefit named by its Act: a declared constant"),
    17: ("NAME", None, "universal credit: a benefit named by its Act: a declared constant"),
    # ---- reg. 2A ----
    18: ("RULE", And(P1(None, lambda p: Iff(U("eff_rb_day", p),
                                           Or(U("own_rb_day", p),
                                              Ex("person", And(member_or_couple(V(1), V(0)), U("own_rb_day", V(0))))))),
                     P1(None, lambda p: And(Implies(Or(U("own_rb_throughout", p),
                                                       Ex("person", And(member_or_couple(V(1), V(0)),
                                                                        U("own_rb_throughout", V(0))))),
                                                    U("rb_each_day_with_member", p)),
                                            Iff(U("eff_rb_throughout", p), U("rb_each_day_with_member", p))))),
         "deeming: own entitlement OR another member of the couple/polygamous marriage entitled in their own right (not "
         "deemed: no circular deeming); the deeming carries the time qualifier of the provision that uses it (a day in "
         "the week for 10(2)/(3), throughout the week for 9(c)/(d)); any number of members; v2 (grader row 18): the deeming works "
         "day by day, so 'throughout' is the stated union fact rb_each_day_with_member"),
    # ---- reg. 4 ----
    22: ("RULE", P1(None, lambda p: Implies(U("wfp_regarded", p), Not(U("entitled", p)))),
         "4(1); 'awarded ... in respect of the qualifying week' is the fact wfp_awarded"),
    23: ("RULE", P1(None, lambda p: Iff(U("wfp_regarded", p), And(U("wfp_awarded", p), Not(U("wfp_award_in_error", p))))),
         "4(2): an award made in error (induced or not) is not regarded"),
    # ---- reg. 5 ----
    24: ("RULE", P1(None, lambda p: Iff(U("entitled", p), And(U("reached_pa", p), U("residence_condition", p),
                                                             Not(U("excluded_9", p)), Not(U("wfp_regarded", p))))),
         "5 with 4(1) as the only other condition (Iff: no other route to entitlement)"),
    # ---- reg. 6 ----
    25: ("RULE", Iff(U("reached_pa", A), ["date_no_later", ci("applicant_pa_date"), day(QW1)]),
         "pensionable-age date (bridge) on or before the week's last day; for other people reached_pa is a fact"),
    # ---- reg. 8 ----
    26: ("RULE", P1(None, lambda p: Iff(U("residence_condition", p), U("meets_8_2", p))), "8(1)"),
    27: ("RULE", P1(None, lambda p: And(Iff(U("meets_8_2", p), And(U("meets_8_2a", p), U("meets_8_2b", p))),
                                       Implies(U("meets_8_2bi", p), U("meets_8_2b", p)),
                                       Implies(And(Not(U("meets_8_2bi", p)), Not(U("bii_possible", p))),
                                               Not(U("meets_8_2b", p))))),
         "8(2): (a) and (b) split; after 8(3)/(4) both (a) and (b)(i) hold on the week's last day, so the 'same day' "
         "of 8(2) is kept for (b)(i); v2 (grader row 27): where (b)(ii) may apply (out of scope: probes) nothing is derived"),
    28: ("RULE", Iff(U("meets_8_2a", A), And(some_day_scot, Not(gone_by_last_day))),
         "8(2)(a) with 8(3): resident on a day of the week and not gone by its last day; one residence interval"),
    29: ("RULE", P1(None, lambda p: Iff(U("meets_8_2bi", p), And(U("not_pic_some_day", p), Not(U("pic_by_last_day", p))))),
         "8(2)(b)(i) with 8(4)"),
    30: ("NAME", None, "immigration rules: defined by the Immigration Act 1971 s.3(2)"),
    # ---- reg. 9 ----
    31: ("RULE", P1(None, lambda p: Iff(U("excluded_9", p), Or(
                     And(U("fipt_throughout_qw", p), U("fipt_52w_before", p)),
                     U("custody_throughout_qw", p),
                     And(U("eff_rb_throughout", p), U("in_residential_care", p)),
                     And(U("eff_rb_throughout", p),
                         Ex("person", And(member_or_couple(V(1), V(0)), U("paid_for_qw", V(0)))))))),
         "(a)-(d); 2A applies to 'entitled to a relevant benefit' in (c) and (d) ('In these Regulations'); (d) any "
         "other member of the couple or marriage"),
    # ---- reg. 9A(3)-(4) ----
    34: ("RULE", Iff(U("opt_out_in_effect", A), And(U("opt_out_before_payment", A), Not(U("opt_in_restores", A)))),
         "(a) the next payment after receipt, (b) ongoing unless an opt-in under 9B; payment timing is a fact"),
    35: ("RULE", Implies(And(U("entitled", A), U("opt_out_in_effect", A)), amount("0.00")),
         "'£0 instead of' reg. 10: the reg. 10 rows carry the matching 'no opt-out' guard"),
    # ---- reg. 9B(3)(a)-(b)(i) ----
    38: ("RULE", Iff(U("opt_in_restores", A),
                     Or(U("opt_in_before_payment", A),
                        And(U("opt_in_made", A), Not(U("opt_in_future_only", A)),
                            ["date_no_later", ci("applicant_opt_in_day"), day(END_MARCH)]))),
         "(a) next payment after receipt; (b)(i) the current or preceding week's payment if not 'future only' and made "
         "no later than 31 March (read as 31 March 2027 for the 2026 week, a bridge); (b)(ii) good reason is OUT"),
    # ---- reg. 10 ----
    39: ("NOT", None, "10(1) is a signpost ('decided in accordance with this regulation'); its content is the entitled "
                      "guard carried in rows 42-44"),
    40: ("RULE", P1(None, lambda p: Implies(U("eff_rb_day", p), U("para_4", p))), "10(2) with 2A"),
    41: ("RULE", P1(None, lambda p: And(Iff(U("para_5", p), And(Not(U("eff_rb_day", p)), Not(U("reached_80", p)))),
                                       Iff(U("para_6", p), And(Not(U("eff_rb_day", p)), U("reached_80", p))))),
         "10(3); 'aged 80 or over in that week' read as reached 80 by the week's last day (as 10(4)(a)(i))"),
    42: ("RULE", And(Iff(U("reached_80", A), ["date_no_later", ci("applicant_eightieth"), day(QW1)]),
                     Implies(amount_guard("para_4"),
                             And(Implies(Or(U("reached_80", A),
                                            Ex("person", And(member_or_couple(A, V(0)), U("reached_80", V(0))))),
                                         amount("316.70")),
                                 Implies(Not(Or(U("reached_80", A),
                                                Ex("person", And(member_or_couple(A, V(0)), U("reached_80", V(0)))))),
                                         amount("211.15"))))),
         "10(4) under 10(2) and the 9A(4) guard; any other member of the couple or marriage; 80th birthday a bridge"),
    43: ("RULE", Implies(amount_guard("para_5"),
                         And(Implies(And(Not(lw_ent), Not(U("in_residential_care", A))), amount("211.15")),
                             Implies(Or(lw_ent, U("in_residential_care", A)), amount("105.55")))),
         "10(5); (a) read as not in residential care too (else (a) and (b)(ii) both apply: (b)(ii) is the specific "
         "rule; a reading choice); any number of others (10(7): on the week's last day)"),
    44: ("RULE", Implies(amount_guard("para_6"),
                         And(Implies(And(Not(lw_ent), Not(U("in_residential_care", A))), amount("316.70")),
                             Implies(And(lw_ent_u80, Not(lw_ent_80), Not(U("in_residential_care", A))), amount("211.15")),
                             Implies(And(Or(lw_ent_80, U("in_residential_care", A)), Not(lw_ent_u80)), amount("158.35")))),
         "10(6); living with entitled others both under and over 80 meets (b) and (c)(i) at once: the text gives two "
         "amounts, so no amount is derived (refuse when in doubt); (a) read as not in residential care (as 43)"),
    45: ("NOT", None, "10(7) fixes the day the facts are read (the week's last day); carried only in the descriptions of "
                      "lives_with and share_mutual_home, no formula"),
    46: ("RULE", P2(lambda p, q: Iff(B("lives_with", p, q),
                                     And(Not(Eq(p, q)), B("share_mutual_home", p, q),
                                         Not(U("in_residential_care", p)), Not(U("in_residential_care", q))))),
         "10(9): two different people sharing a mutual home, neither in residential care; temporary absence in the facts"),
    # ---- reg. 16B(1)-(3) ----
    62: ("RULE", Eq(ci("applicant_application"), ci("applicant_received")), "16B(1)"),
    63: ("RULE", Implies(And(U("applied", A), U("deadline_16b2_applies", A)),
                         Iff(U("application_in_time", A), ["date_no_later", ci("applicant_application"), day(END_MARCH)])),
         "'31 March in the year following that week' a bridge"),
    64: ("RULE", And(Iff(U("deadline_16b2_applies", A),
                         Not(Or(U("rb_by_later_decision", A),
                                Ex("person", And(member_or_couple(A, V(0)), U("rb_by_later_decision", V(0)))),
                                U("s115_ceased_by_later_decision", A)))),
                     Implies(And(U("applied", A), Not(U("deadline_16b2_applies", A))), U("application_in_time", A))),
         "16B(3): the later decision is a yes/no fact; v2 (grader row 64): no limit -> in time, and (a) through 2A "
         "('In these Regulations'): a later award to another member of the couple or marriage also lifts the limit"),
}
IN_SCOPE = sorted(T)
