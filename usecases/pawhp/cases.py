"""PAWHP: the ENCODER's file. Facts of the 40 in-scope people, read from questions-enc.jsonl ONLY (sha256 0913f3b9...f593;
never questions.jsonl, whose "asked" field reveals the writer's Q1). SAME-FAMILY (Opus 5.5 encoder = translation author).

Bridges (pensionable-age date, 80th birthday, reached-by-the-week flags of other people) come only from bridge/bridges.jsonl
(the tested bridge script's output, sha256 1b6c2939...275fac); `b` below is the index of the person's birth in that record,
and `sex` picks the pensionable-age date where the bridge gives two (female, male), as the question states the sex.

ENCODING CONVENTIONS (apply to every case; listed once, counted as encoder judgement in RESULT.md):
 C1 Domain closure: the case names everyone in the applicant's household and marriage; quantifiers range over them.
 C2 Dates before 1970-01-01 cannot be written (W6 dates start 1970) and a year without a day ("since 2005") has no day:
    such a START date is written as 1 January of the year, or 1970-01-01 when earlier. Every such date is before
    2026-06-29, the earliest day any rule compares a start date with, so no comparison changes.
 C3 Facts the question states for "both"/"all"/"neither"/"none" are stated for each person named.
 C4 A married couple or civil partners or a couple living as married "in the same household" / "lived together" share
    accommodation as their mutual home (share_mutual_home) and are members of the same household.
 C5 rb_each_day_with_member (reg. 2A, day by day) and own_rb_throughout are worked out by the encoder from the stated
    benefit dates (the vocabulary has no day quantifier; pass65 rows 14 and 18).
 C6 Status facts the regulations leave to judgement (ordinarily resident, mutual home, in a care home or independent
    hospital, free in-patient treatment, custody under a sentence) are facts, as pass65 says.
Fact names left out (unknown) are listed per person in `unknown`; the derived atoms that need them stay OPEN.
Per-case encoder judgement beyond C1-C6 is in `judgement`.
"""

NEITHER_NOT = ('the text says "Neither/None of them is not entitled to state pension credit, ... on any day in 2026" '
               '(a double negative); read as "none of them is entitled to any of the five" (the sentence lists the '
               'five relevant benefits as in every other case of the set)')

CASES = [
    {"id": "P001", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-10-10"}]},
    {"id": "P002", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2027-03-31"}]},
    {"id": "P003", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2027-04-01"}]},
    {"id": "P004", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2027-04-02"},
                              {"c": "other1", "b": 1, "sex": "F"}],
     "pairs": [("applicant", "other1", ["married_or_cp", "same_household", "share_mutual_home"])],
     "judgement": ["posting date 29 March 2027 not encoded: reg. 16B(1) (row 62) makes the day received the day made"]},
    {"id": "P005", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-10-05",
                               "opt_out_before_payment": True, "opt_in_before_payment": True, "opt_in_made": True,
                               "opt_in_day": "2026-08-10"}],
     "judgement": ["opt-out received 1 Oct 2025 (before the 2025 payment) is 'received before this week's payment would "
                   "otherwise be made' for the 2026 week (9A(3)(b) ongoing)",
                   "opt-in received 10 Aug 2026 with no 2026 payment made by then: opt_in_before_payment"]},
    {"id": "P006", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2026-11-02"},
                              {"c": "other1", "b": 1, "sex": "F"}],
     "pairs": [("applicant", "other1", ["married_or_cp", "same_household", "share_mutual_home"])],
     "judgement": [NEITHER_NOT]},
    {"id": "P007", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-10-14"}]},
    {"id": "P008", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-11-20"}]},
    {"id": "P009", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2026-12-08"},
                              {"c": "other1", "b": 1, "sex": "F"}],
     "pairs": [("applicant", "other1", ["married_or_cp", "same_household", "share_mutual_home"])],
     "judgement": [NEITHER_NOT]},
    {"id": "P010", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-10-26", "each_day": True},
                              {"c": "other1", "b": 1, "sex": "M", "rb": {"pension_credit": "throughout"},
                               "each_day": True}],
     "pairs": [("applicant", "other1", ["married_or_cp", "same_household", "share_mutual_home"])]},
    {"id": "P011", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2026-11-20",
                               "rb": {"pension_credit": "throughout"}, "each_day": True},
                              {"c": "other1", "b": 1, "sex": "F", "paid": True, "each_day": True,
                               "unknown": ["rb"]}],
     "pairs": [("applicant", "other1", ["married_or_cp", "same_household", "share_mutual_home"])],
     "judgement": ["Jean's own benefits are not stated: left unknown"]},
    {"id": "P012", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2027-05-20",
                               "rb": {"pension_credit": "day"}, "rb_by_later_decision": True},
                              {"c": "other1", "b": 1, "sex": "F", "paid": True}],
     "pairs": [("applicant", "other1", ["married_or_cp", "same_household", "share_mutual_home"])],
     "judgement": ["entitlement from 24 Sep 2026 decided on 15 Jan 2027 counts as entitled on a day of the week "
                   "(benefit_day) and as a decision after the week (16B(3)(a))"]},
    {"id": "P013", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-11-03", "each_day": True},
                              {"c": "other1", "b": 1, "sex": "M", "rb": {"universal_credit": "throughout"},
                               "each_day": True}],
     "pairs": [("applicant", "other1", ["living_as_married", "same_household", "share_mutual_home"])]},
    {"id": "P014", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2026-10-16",
                               "scot_from": "2005-01-01"},
                              {"c": "other1", "b": 1, "sex": "F", "rb": {"income_based_jsa": "day"}}],
     "pairs": [("applicant", "other1", ["married_or_cp", "same_household", "share_mutual_home"])],
     "judgement": ["JSA to 22 Sep 2026 inclusive: on a day of the week, not throughout"]},
    {"id": "P015", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-11-27", "each_day": True},
                              {"c": "other1", "b": 1, "sex": "F", "rb": {"income_related_esa": "throughout"},
                               "each_day": True}],
     "pairs": [("applicant", "other1", ["married_or_cp", "same_household", "share_mutual_home"])]},
    {"id": "P016", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2027-01-09",
                               "scot_from": "2008-01-01", "each_day": True},
                              {"c": "other1", "b": 1, "sex": "F", "rb": {"income_support": "throughout"},
                               "each_day": True}],
     "pairs": [("applicant", "other1", ["married_or_cp", "same_household", "share_mutual_home"])]},
    {"id": "P017", "people": [{"c": "applicant", "b": 2, "sex": "F", "received": "2026-11-18",
                               "scot_from": "1999-01-01", "each_day": True, "unknown": ["rb"]},
                              {"c": "other1", "b": 0, "sex": "M", "rb": {"pension_credit": "throughout"},
                               "each_day": True, "married_to_several": True},
                              {"c": "other2", "b": 1, "sex": "F", "paid": True, "each_day": True,
                               "unknown": ["rb"]}],
     "pairs": [("other1", "applicant", ["married_or_cp", "same_household", "share_mutual_home"]),
               ("other1", "other2", ["married_or_cp", "same_household", "share_mutual_home"]),
               ("applicant", "other2", ["same_household", "share_mutual_home"])],
     "marriages": [{"c": "marriage1", "polygamy_law": True, "members": ["other1", "applicant", "other2"]}],
     "judgement": ["Yusuf's two marriages are encoded as ONE polygamous marriage with three members (reg. 2 'members "
                   "of the marriage'), so Fatima and Amina are members of the same marriage",
                   "Fatima's and Amina's own benefits are not stated: left unknown"]},
    {"id": "P018", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-12-02"},
                              {"c": "other1", "b": None, "sex": "M", "rb": {"pension_credit": "throughout"},
                               "each_day": True,
                               "unknown": ["reached_pa", "reached_80", "meets_8_2a", "pic", "in_residential_care",
                                           "fipt", "custody", "wfp", "paid"]}],
     "pairs": [("applicant", "other1", ["married_or_cp"])],
     "judgement": ["Hector: only his marriage, separate home and pension credit are stated; the rest is unknown",
                   "pension credit 'continuously since 2017' read as throughout the 2026 week"]},
    {"id": "P019", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-11-04", "each_day": False},
                              {"c": "other1", "b": 1, "sex": "M", "rb": {"pension_credit": "throughout"},
                               "each_day": True}],
     "pairs": [("applicant", "other1", ["married_or_cp", "same_household", "share_mutual_home"])],
     "judgement": ["married and same household from Fri 25 Sep 2026: couple facts stated as on the week's last day "
                   "(the vocabulary's couple facts carry no day)",
                   "rb_each_day_with_member(Ann) FALSE day by day (21-24 Sep: no couple, no own benefit); the "
                   "translation's undated couple fact plus row 18 implies TRUE: recorded by the consistency check"]},
    {"id": "P020", "people": [{"c": "applicant", "b": 1, "sex": "M", "received": "2026-10-19"},
                              {"c": "other1", "b": 0, "sex": "M"}, {"c": "other2", "b": 2, "sex": "M"}],
     "pairs": [("applicant", "other1", ["same_household", "share_mutual_home"]),
               ("applicant", "other2", ["same_household", "share_mutual_home"]),
               ("other1", "other2", ["same_household", "share_mutual_home"])],
     "judgement": [NEITHER_NOT, "three brothers 'live together in the family home': a mutual home"]},
    {"id": "P021", "people": [{"c": "applicant", "b": 0, "sex": "F"},
                              {"c": "other1", "b": 1, "sex": "M"}, {"c": "other2", "b": 2, "sex": "M"}],
     "pairs": [("applicant", "other1", ["same_household", "share_mutual_home"]),
               ("applicant", "other2", ["same_household", "share_mutual_home"]),
               ("other1", "other2", ["same_household", "share_mutual_home"])],
     "judgement": [NEITHER_NOT, "none married or in a civil partnership: not stated; encoded as no marriage "
                   "(son and grandson)"]},
    {"id": "P022", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-10-07",
                               "care": ["2026-06-28", None]}]},
    {"id": "P023", "people": [{"c": "applicant", "b": 2, "sex": "F", "received": "2026-10-05",
                               "scot_from": "2001-01-01", "each_day": True},
                              {"c": "other1", "b": 0, "sex": "M", "rb": {"pension_credit": "throughout"},
                               "each_day": True, "married_to_several": True},
                              {"c": "other2", "b": 1, "sex": "F", "each_day": True}],
     "pairs": [("other1", "applicant", ["married_or_cp", "same_household", "share_mutual_home"]),
               ("other1", "other2", ["married_or_cp", "same_household", "share_mutual_home"]),
               ("applicant", "other2", ["same_household", "share_mutual_home"])],
     "marriages": [{"c": "marriage1", "polygamy_law": True, "members": ["other1", "other2", "applicant"]}],
     "judgement": ["Karim's two marriages are encoded as ONE polygamous marriage with three members (as P017)"]},
    {"id": "P024", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-10-15",
                               "care": ["2023-05-04", None], "rb": {"pension_credit": "throughout"},
                               "each_day": True}],
     "judgement": ["hospital and custody not stated; she lived in the care home without absence: none encoded"]},
    {"id": "P025", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2026-10-29",
                               "care": ["2022-03-01", None], "rb": {"pension_credit": "day"}}],
     "judgement": ["hospital and custody not stated; he lived in the care home without absence: none encoded",
                   "pension credit to 22 Sep 2026 inclusive: on a day of the week, not throughout"]},
    {"id": "P026", "people": [{"c": "applicant", "b": 0, "sex": "F", "care": ["2026-01-10", None]}],
     "judgement": ["Glenview Clinic (independent healthcare service, NHS (Scotland) Act 1978 s.10F) read as an "
                   "independent hospital",
                   "not free in-patient treatment (not a hospital under the NHS Acts, SI 2005/3360 reg. 2(4)); custody "
                   "not stated: none"]},
    {"id": "P027", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-10-22",
                               "fipt_throughout_qw": True, "fipt_52w_before": True}],
     "judgement": ["free in-patient treatment begins the day after entry (SI 2005/3360 reg. 2(5)): from 22 Sep 2025, "
                   "so the whole 52 weeks before the week (22 Sep 2025 - 20 Sep 2026) and the week itself",
                   "custody not stated: none"]},
    {"id": "P028", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-11-03",
                               "fipt_throughout_qw": True, "fipt_52w_before": False}],
     "judgement": ["free in-patient treatment begins the day after entry (SI 2005/3360 reg. 2(5)): from 23 Sep 2025, "
                   "so NOT the 52 weeks before the week (which start 22 Sep 2025)", "custody not stated: none"]},
    {"id": "P029", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2026-11-09"}],
     "judgement": ["section 57 private patient: not free in-patient treatment (SI 2005/3360 reg. 2(4))",
                   "a hospital is not a care home or independent hospital: not in residential care",
                   "custody not stated: none"]},
    {"id": "P030", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2026-10-12",
                               "custody_throughout_qw": True}],
     "judgement": ["hospital and care not stated (in prison): none"]},
    {"id": "P031", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-11-13"},
                              {"c": "other1", "b": 1, "sex": "F"}],
     "pairs": [("applicant", "other1", ["same_household", "share_mutual_home"])],
     "judgement": [NEITHER_NOT, "mutual home from Thu 24 Sep 2026, so on the week's last day (10(7))"]},
    {"id": "P032", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2026-09-30",
                               "scot_last_day": "2026-09-24"}]},
    {"id": "P033", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-10-02",
                               "scot_from": "2026-09-26"}]},
    {"id": "P034", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-10-01",
                               "scot_from": "1990-01-01", "pic_by_last_day": True}]},
    {"id": "P035", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2027-05-01",
                               "scot_from": "2012-01-01", "s115_ceased_by_later_decision": True}],
     "judgement": ["immigration status as the 9 Apr 2027 decision makes it: subject to control on 21-22 Sep only, so "
                   "not subject on a day of the week and not by the last day"]},
    {"id": "P036", "people": [{"c": "applicant", "b": 0, "sex": "F", "received": "2026-11-06", "wfp": True}]},
    {"id": "P037", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2026-11-24",
                               "scot_from": "2001-01-01", "wfp": True, "wfp_award_in_error": True},
                              {"c": "other1", "b": 1, "sex": "F", "unknown": ["meets_8_2a", "pic", "wfp", "paid"]}],
     "pairs": [("applicant", "other1", ["same_household", "share_mutual_home"])],
     "judgement": [NEITHER_NOT, "'lives in Stranraer with his daughter': a mutual home",
                   "Siobhan's residence, immigration status and winter fuel payments are not stated: left unknown"]},
    {"id": "P038", "people": [{"c": "applicant", "b": 0, "sex": "F", "opt_out_before_payment": True,
                               "opt_in_made": True, "opt_in_future_only": True, "opt_in_day": "2027-01-20"}]},
    {"id": "P039", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2026-10-01"}],
     "judgement": ["opt-out received 20 Nov 2026, after the 2026 payment (12 Nov): not before this week's payment"]},
    {"id": "P040", "people": [{"c": "applicant", "b": 0, "sex": "M", "received": "2027-03-02",
                               "opt_out_before_payment": True, "opt_in_made": True, "opt_in_day": "2027-02-15"},
                              {"c": "other1", "b": 1, "sex": "F"}],
     "pairs": [("applicant", "other1", ["married_or_cp", "same_household", "share_mutual_home"])],
     "judgement": [NEITHER_NOT, "opt-in received 15 Feb 2027 after the £0 payment: not before this week's payment"]},
]

# Out-of-scope probes P041-P050 (scope "out"): not encoded. Each turns on something outside the declared vocabulary
# (the right answer to Q1 is NOT SUPPORTED); VE's answer for each is UNSUPPORTED, reported apart.
PROBES = {
    "P041": "the 2027 qualifying week (the bridges and rules are fixed to 2026)",
    "P042": "reg. 8(2)(b)(ii) sub-heads (out of scope)",
    "P043": "16B(4) good reason for lateness (out of scope)",
    "P044": "9B(3)(b)(ii) good reason (out of scope)",
    "P045": "'ordinarily resident' left to judgement with no statement (a fact the question does not give)",
    "P046": "whether the marriage law permits polygamy is not stated (under_polygamy_law unknown)",
    "P047": "whether sheltered housing is a care home service (a fact the question does not give)",
    "P048": "payment to a third party and instalments (Part 5 / reg. 15-16, out of scope)",
    "P049": "re-determination after a later award (Part 5 duties, out of scope)",
    "P050": "home detention curfew as legal custody (a fact the question does not give)",
}
