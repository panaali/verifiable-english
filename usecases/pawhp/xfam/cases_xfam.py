"""PAWHP (SSI 2024/351): the ENCODER's file for the CROSS-FAMILY question set (/work/questions-enc.jsonl). TEMPLATE: the
frozen build's own cases.py with its case records and per-case texts removed. The build's description:

Bridges (pensionable-age date, 80th birthday, reached-by-the-week flags of other people) come only from /work/bridges.jsonl (computed for THIS set by the frozen bridge script)
(the tested bridge script output); `b` below is the index of the person's birth in that record,
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

S2000 = "2000-01-01"  # "ordinarily resident in Scotland continuously since 1 January 2000"
ALL3 = ("same_household", "share_mutual_home")


def A(b=0, sex=None, received=None, scot_from=S2000, **kw):
    """The applicant. Defaults are the facts' closing sentences: no care, in-patient treatment, custody, relevant
    benefit, winter fuel payment, payment or request; not subject to immigration control; no later decision."""
    return {"c": "applicant", "b": b, "sex": sex, "scot_from": scot_from, "received": received, **kw}


def O(c, b, sex=None, **kw):
    """Another person the case names (resident in Scotland, not subject to immigration control, as stated for all)."""
    return {"c": c, "b": b, "sex": sex, **kw}


def case(cid, people, pairs=(), judgement=(), marriages=()):
    r = {"id": cid, "people": list(people), "pairs": [list(p) for p in pairs], "judgement": list(judgement)}
    if marriages:
        r["marriages"] = list(marriages)
    return r


CASES = [
    # one dict per in-scope id: {"id": ..., "people": [...], "pairs": [...], "judgement": [...]} (fields: see encode.py)
    # ---- one person living alone; age, residence, application date ----
    case("P001", [A(sex="M", received="2027-03-31")]),
    case("P002", [A(sex="F", received="2027-03-30")]),
    case("P003", [A(sex="F", received="2027-03-31"), O("other1", 1, "M")],
         pairs=[("applicant", "other1", ["share_mutual_home"])]),
    case("P004", [A(received="2027-03-31", wfp=True, wfp_award_in_error=True)]),
    case("P005", [A(received="2027-04-01")]),
    case("P006", [A(received="2027-03-31")]),
    case("P007", [A(received="2027-03-31")]),
    case("P008", [A(received="2027-03-31")]),
    case("P009", [A(received="2027-03-31")]),
    case("P010", [A(received="2027-03-31")]),
    case("P011", [A(received="2027-03-31")]),
    case("P012", [A(received="2027-03-31")]),
    case("P013", [A(received="2027-03-31")]),
    # ---- residence and immigration ----
    case("P014", [A(received="2027-03-31", scot_from="2026-09-27")]),
    case("P015", [A(received="2027-03-31", scot_last_day="2026-09-26")]),
    case("P016", [A(received="2027-03-31", not_pic_some_day=True, pic_by_last_day=True, bii_possible=False)]),
    # ---- winter fuel payment awards ----
    case("P017", [A(received="2027-03-31", wfp=True, wfp_award_in_error=False)]),
    case("P018", [A(received="2027-03-31", wfp=True, wfp_award_in_error=False)]),
    # ---- free in-patient treatment, custody ----
    case("P019", [A(received="2027-03-31", fipt=["2025-09-21", "2026-09-27"])],
         judgement=["free in-patient stay dates only (re-encoded by a fresh encoder seat, ../fipt-enc/stays-xfam.jsonl; "
                    "the 52-week and whole-week facts are derived in the checker, translation.fipt_rules)"]),
    case("P020", [A(received="2027-03-31", fipt=["2025-09-22", None])],
         judgement=["free in-patient stay dates only (re-encoded by a fresh encoder seat, ../fipt-enc/stays-xfam.jsonl; "
                    "'remained there continuously through 28 September 2026': not left; the 52-week and whole-week "
                    "facts are derived in the checker, translation.fipt_rules)"]),
    case("P021", [A(received="2027-03-31", custody_throughout_qw=True)]),
    case("P022", [A(sex="M", received="2027-03-31", custody_throughout_qw=False)]),
    # ---- care home / independent hospital ----
    case("P023", [A(received="2027-03-31", care=("2026-06-29", None), rb={"pension_credit": "throughout"})],
         judgement=["care home from 2026-06-29 with no last day: the absence 10-20 Aug 2026 is a temporary absence, disregarded"]),
    case("P024", [A(received="2027-03-31", care=("2026-06-30", None), rb={"income_support": "throughout"})]),
    case("P025", [A(sex="F", received="2027-03-31", care=("2026-06-29", None), rb={"pension_credit": "day"})]),
    case("P026", [A(received="2027-03-31", care=("2026-06-29", None))]),
    case("P027", [A(sex="F", received="2027-03-31", care=("2026-06-29", None))]),
    # ---- couples and polygamous marriages (2A deeming, reg. 9(d)) ----
    case("P028", [A(received="2027-03-31", each_day=True),
                  O("other1", 1, "F", rb={"universal_credit": "throughout"})],
         pairs=[("applicant", "other1", ["married_or_cp", *ALL3])]),
    case("P029", [A(received="2027-03-31", each_day=True),
                  O("other1", 1, rb={"income_related_esa": "throughout"}, paid=True)],
         pairs=[("applicant", "other1", ["married_or_cp", *ALL3])]),
    case("P030", [A(received="2027-03-31", each_day=True),
                  O("other1", 1, rb={"income_support": "throughout"}, wfp=True, wfp_award_in_error=False, paid=True)],
         pairs=[("applicant", "other1", ["living_as_married", *ALL3])]),
    case("P031", [A(received="2027-03-31", each_day=True, married_to_several=True),
                  O("other1", 1, rb={"income_based_jsa": "throughout"}),
                  O("other2", 2, each_day=True, wfp=True, wfp_award_in_error=False, paid=True)],
         pairs=[("applicant", "other1", ["married_or_cp", *ALL3]),
                ("applicant", "other2", ["married_or_cp", *ALL3]),
                ("other1", "other2", list(ALL3))],
         marriages=[{"c": "marriage1", "polygamy_law": True, "members": ["applicant", "other1", "other2"]}]),
    case("P032", [A(received="2027-03-31", each_day=True),
                  O("other1", 1, "M", each_day=True, married_to_several=True),
                  O("other2", 2, rb={"pension_credit": "throughout"})],
         pairs=[("applicant", "other1", ["married_or_cp", *ALL3]),
                ("other1", "other2", ["married_or_cp", *ALL3]),
                ("applicant", "other2", list(ALL3))],
         marriages=[{"c": "marriage1", "polygamy_law": True, "members": ["applicant", "other1", "other2"]}]),
    # ---- age 80, living with others (reg. 10(5)-(9)) ----
    case("P033", [A(sex="M", received="2027-03-31")]),
    case("P034", [A(sex="F", received="2027-03-31"), O("other1", 1)],
         pairs=[("applicant", "other1", ["share_mutual_home"])],
         judgement=["Robert's holiday 20-28 Sep 2026 is a temporary absence: the mutual home is shared on the week's last day"]),
    case("P035", [A(sex="F", received="2027-03-31"), O("other1", 1, "M"), O("other2", 2)],
         pairs=[("applicant", "other1", ["share_mutual_home"]), ("applicant", "other2", ["share_mutual_home"]),
                ("other1", "other2", ["share_mutual_home"])]),
    case("P036", [A(received="2027-03-31"), O("other1", 1), O("other2", 2)],
         pairs=[("applicant", "other2", ["share_mutual_home"])],
         judgement=["share_mutual_home is read on the week's last day (27 Sep 2026): Wallace had moved out that day, so he shares with neither"]),
    # ---- opt-out / opt-in, later decisions ----
    case("P037", [A(received="2027-03-31", opt_out_before_payment=True, opt_in_before_payment=False,
                    opt_in_made=True, opt_in_future_only=True, opt_in_day="2027-03-31")],
         judgement=["opt_in_before_payment false: the opt-in (31 Mar 2027) came after this week's payment fell to be made (1 Dec 2026)"]),
    case("P038", [A(received="2027-04-03", opt_out_before_payment=True, opt_in_before_payment=False,
                    opt_in_made=True, opt_in_future_only=False, opt_in_day="2027-03-31",
                    rb={"pension_credit": "day"}, rb_by_later_decision=True)],
         judgement=["opt_in_before_payment false: the opt-in (31 Mar 2027) came after this week's payment fell to be made (1 Dec 2026)",
                    "the 2 Apr 2027 award makes Colin entitled to state pension credit on 22 Sep 2026 (a day in the week, not throughout)"]),
    case("P039", [A(received="2026-09-25", opt_out_before_payment=True, opt_in_before_payment=True,
                    opt_in_made=True, opt_in_future_only=False, opt_in_day="2026-09-24")],
         judgement=["opt_in_before_payment true: the opt-in (24 Sep 2026) came before this week's payment fell to be made (1 Dec 2026)"]),
    case("P040", [A(sex="M", received="2027-04-16", not_pic_some_day=True, pic_by_last_day=False,
                    s115_ceased_by_later_decision=True, paid=True, opt_out_before_payment=False,
                    unknown=["rb_by_later_decision"])],
         judgement=["opt_out_before_payment false: the opt-out (1 Feb 2027) came after this week's payment was made (1 Dec 2026)",
                    "rb_by_later_decision left unknown: these facts omit the usual 'no later benefit decision' sentence"]),
]

# Ids the vocabulary cannot state (UNSUPPORTED; the encoder's reason)
PROBES = {
    "P041": "scope out: a different qualifying week (beginning 20 Sep 2027); the build's week is fixed at 21-27 Sep 2026",
    "P042": "scope out: reg. 8(2)(b)(ii) sub-heads (subject to immigration control) are not translated",
    "P043": "scope out: determination without application (Part 5) is not translated",
    "P044": "scope out: official error, re-determination and overpayment recovery are not translated",
    "P045": "scope out: re-determination requests are not translated",
    "P046": "scope out: opt-in after 31 March on good reason (reg. 9B(3)(b)(ii)) is not translated",
    "P047": "scope out: form of payment and payment to a third party are not translated",
    "P048": "scope out: ordinary residence is a status fact (C6), not decided from circumstances",
    "P049": "scope out: winter fuel payment under the GB Regulations, not this instrument",
    "P050": "scope out: supplementary award after a later benefit decision is not translated",
}
