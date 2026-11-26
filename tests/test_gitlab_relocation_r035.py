"""GitLab relocation (usecases/gitlab_relocation): written VP/PBP pre-approval and the encoder's no-predicate rule
(row statute-corpus-gitlab-relocation-wrong-r035; decide wake 20261125T2021Z, reviews/dri-decisions-20261125-relocation-r035.md).

The frozen build (1847cd06dc, translation 8b113741bd) left unit 4 ("If your manager is supportive, discuss and obtain
pre-approval in writing from your functional Vice President and People Business Partner") unwritten, and its acceptance
rule R10 answered YES from conditions (a)-(h); its encoder dropped R035's stated lack of that pre-approval ("not entered").
Cross-family R035-2 (Ines: every condition, business approval, no written VP/PBP pre-approval) was answered yes; the
sealed answer and both graders say no. These tests pin the fix:
* condition (i) of R10 (translation R17): no written pre-approval -> acceptance NO, never YES; not stated -> never YES;
* encoder rule E5 (encode.py, narrowed after the review): a stated fact with no predicate on a clause the translation
  writes, which the answer reads for the fact's item -> REFUSED, unless the answer still follows without those rules;
  a fact on a clause the translation does not write refuses nothing and is reported;
* the planted error M17 (the frozen R10) flips R035-2 back to YES.
Each answer is derived by the use case's own staged prover (run.run_sub); the run replays every certificate in Lean.
On 1847cd06dc (tests-on-1847cd06dc.txt in the fix's RESULT folder) every test fails, but only two by BEHAVIOUR
(test_preapproval_not_stated_never_yes and test_r035_2_encoded_from_the_case_is_not_yes: the frozen code answers yes);
the others fail because the frozen vocabulary cannot state wpre or a no-predicate fact (no E5, no M17): they are
regression tests of the new rule, not evidence of the frozen behaviour.
"""
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(__file__).resolve().parents[1] / "usecases" / "gitlab_relocation"
PRE = "written pre-approval from the functional Vice President and People Business Partner"


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import cases as K
        import encode as E
        import run as R
        import translation as T
        yield K, E, R, T


def request(uc, wpre=True, biz=True, cap=False, nopred=()):
    """Every R10 condition (a)-(g) holds (Spain-like destination, entity open, tenure met); biz and wpre as given."""
    _, E, _, _ = uc
    s = E.Sub().fact("fed", "p", False)
    s.place("d", None, False)
    for f, v in (("ent", True), ("open", True), ("restr", False), ("cap", cap), ("newposs", False)):
        s.fact(f, "d", v)
    s.item("r", "req", "d").fact("tcc", "r", False).fact("elig", "r", True).fact("rtw", "r", True).fact("biz", "r", biz)
    s.val("rd", "r", "2027-01-02").start("2025-01-01")
    if wpre is not None:
        s.fact("wpre", "r", wpre)
    for unit, text in nopred:
        s.nopred(unit, text)
    return s


def ask(uc, spec, forms, mutant=None):
    _, _, R, _ = uc
    sub = {"spec": spec, "questions": [{"qid": k, "form": f} for k, f in forms.items()]}
    return R.run_sub(sub, mutant)[0]


ACC, WHICH, ELIG = ("yn", "acc", "r"), ("which", "r"), ("yn", "eligrel", "r")


def test_all_conditions_and_business_approval_no_written_vp_pbp_preapproval_not_yes(uc):
    """The named test (a): all conditions + business approval, no written VP/PBP pre-approval -> not YES (NO, (i) fails)."""
    got = ask(uc, request(uc, wpre=False), {"acc": ACC, "which": WHICH, "elig": ELIG})
    assert got["acc"]["answer"] == "no"
    assert got["which"] == {"answer": "CONDITIONS", "value": PRE}
    assert got["elig"]["answer"] == "yes"      # (i) is acceptance's, not eligibility's (R12)


def test_written_preapproval_given_accepts(uc):
    got = ask(uc, request(uc, wpre=True), {"acc": ACC, "which": WHICH})
    assert got["acc"]["answer"] == "yes"
    assert got["which"] == {"answer": "CONDITIONS", "value": "none"}


def test_preapproval_not_stated_never_yes(uc):
    """Where the facts leave the pre-approval unknown, acceptance is refused (OPEN), never YES; NO still follows from
    another condition that fails."""
    got = ask(uc, request(uc, wpre=None), {"acc": ACC, "which": WHICH})
    assert got["acc"]["answer"] == "OPEN"
    assert got["which"]["answer"] == "OPEN"
    got = ask(uc, request(uc, wpre=None, cap=True), {"acc": ACC, "which": WHICH})
    assert got["acc"]["answer"] == "no"
    assert got["which"]["answer"] == "OPEN"     # (i) unknown: the list of failing conditions is not complete


def test_stated_fact_with_no_predicate_on_a_covered_unit_refused(uc):
    """The named test (b): stated fact with no predicate on a covered unit -> REFUSED (unit 26: eligibility to work,
    which acceptance turns on)."""
    got = ask(uc, request(uc, nopred=[(26, "the work permit is under appeal")]), {"acc": ACC, "fam": ("yn", "famcost", "r")})
    assert got["acc"]["answer"] == "OPEN"
    assert "encoder rule E5" in got["acc"]["refused"] and "unit 26" in got["acc"]["refused"]
    assert got["fam"]["answer"] == "no"          # unit 32's answer does not turn on unit 26


def test_no_predicate_fact_does_not_refuse_an_answer_that_follows_without_it(uc):
    """E5 (4): the cap fails (condition (a)), so acceptance is NO whatever unit 26's fact is: the NO stands."""
    got = ask(uc, request(uc, cap=True, nopred=[(26, "the work permit is under appeal")]), {"acc": ACC})
    assert got["acc"]["answer"] == "no"


def test_no_predicate_fact_on_a_clause_not_written_refuses_nothing(uc):
    """A turns_on fact on a clause the translation's ledger records as a duty with no outcome (unit 6's 'contact the
    People Operations Team immediately') is reported, not used."""
    _, _, R, _ = uc
    s = request(uc)
    s.nopred(6, "has not contacted the People Operations Team", True,
             "If you believe you may exceed (or has already exceeded) the 183 days limit (or a lower threshold in certain "
             "countries), contact the People Operations Team immediately", "team member")
    sub = {"spec": s, "questions": [{"qid": "acc", "form": ACC}]}
    answers, _, staged, *_ = R.run_sub(sub)
    assert answers["acc"]["answer"] == "yes"
    assert [x[1] for x in staged.e5["unwritten"]] == [6]


def test_no_predicate_fact_is_scoped_to_its_item(uc):
    """R016's six stays: a fact about the France stay on unit 7's manager-approval clause refuses the France question,
    not the Spain one."""
    K, _, R, _ = uc
    s = K.stays_sub("2027", K.R016, person={"tzrole": True}, need={"work"})
    s.nopred(7, "the manager was never asked about France", True,
             "All Team members are required to obtain manager approval to work outside of their primary location "
             "regardless of the length of time at that location", "France")
    got = ask(uc, s, {"es": ("yn", "workok", "s1"), "fr": ("yn", "workok", "s3")})
    assert got["es"]["answer"] == "yes"
    assert got["fr"]["answer"] == "OPEN" and "encoder rule E5" in got["fr"]["refused"]


def test_stated_fact_with_no_predicate_on_a_unit_not_covered_answers(uc):
    got = ask(uc, request(uc, nopred=[(30, "has not reviewed benefit changes")]), {"acc": ACC})
    assert got["acc"]["answer"] == "yes"


def test_no_predicate_fact_marked_not_turning_on_is_recorded_not_used(uc):
    s = request(uc)
    s.nopred(16, "takes a company-owned laptop", turns_on=False)
    assert ask(uc, s, {"acc": ACC})["acc"]["answer"] == "yes"


def test_covered_units_of_acceptance(uc):
    _, E, R, T = uc
    s = request(uc)
    ctx, _, _ = E.build(s)
    units = E.covered_units(T.ground_by_unit(ctx), [T.A("acc", "r")])
    assert {3, 4, 22, 24, 25, 26, 29, 31, 33} <= units
    assert not units & {1, 2, 12, 14, 21, 27, 28, 30}     # units the translation does not write


def test_r035_2_encoded_from_the_case_is_not_yes(uc):
    """The cross-family case itself (cases.py, the fresh seat's wpre = false): R035-2 -> no; R035-1 names (i)."""
    K, _, R, _ = uc
    case = [c for c in K.CASES if c["id"] == "R035"][0]
    got = R.run_case(case)
    assert got["R035-2"]["answer"] == "no"
    assert got["R035-1"] == {"answer": "CONDITIONS", "value": PRE}


def test_mutant_m17_changes_only_acceptance_and_unit_4(uc):
    """M17 rebuilds unit 33's entry by hand: its ground rules must differ from the fix's only in acceptance (acc) and in
    unit 4's condition (i) (fpre)."""
    K, E, R, T = uc
    ctx, _, _ = E.build(request(uc))
    key = lambda rs: {T.key([r["formula"], r["defines"]]) for r in rs}  # noqa: E731
    fix, m17 = T.rules(ctx), T.rules(ctx, "M17")
    diff = [r for r in fix if T.key([r["formula"], r["defines"]]) not in key(m17)] + \
           [r for r in m17 if T.key([r["formula"], r["defines"]]) not in key(fix)]
    assert diff and all(r["defines"] in ([T.A("acc", "r")], [T.A("fpre", "r")]) for r in diff)


def test_mutant_m17_restores_the_frozen_r10_and_flips_r035_2_to_yes(uc):
    """The planted error M17 (translation.MUTANTS, run.py --mutants): acceptance from (a)-(h), unit 4 unwritten."""
    K, _, R, T = uc
    assert "M17" in T.MUTANTS
    case = [c for c in K.CASES if c["id"] == "R035"][0]
    got = R.run_case(case, "M17")
    assert got["R035-2"]["answer"] == "yes"
    assert got["R035-1"]["answer"] == "OPEN"     # (i) unwritten under M17: the Q3 list does not settle
    assert ask(uc, request(uc, wpre=False), {"acc": ACC}, "M17")["acc"]["answer"] == "yes"


def test_about_a_place_the_sub_case_lacks_widens_to_every_item(uc):
    """A place name this sub-case has no place for (a destination named by country, an origin, two names) scopes the
    fact to every item, never to fewer."""
    _, E, _, _ = uc
    s = request(uc, nopred=[])
    s.nopred(26, "the work permit is under appeal", True, None, "Germany")
    assert ask(uc, s, {"acc": ACC})["acc"]["answer"] == "OPEN"


def test_no_predicate_fact_on_an_unwritten_unit_refuses_under_m17(uc):
    """E5 (5): with unit 4's rules removed by M17 while WRITTEN still lists its clause, R035's fact entered the old way (a
    no-predicate fact on unit 4) refuses acceptance. This is only that table/WRITTEN mismatch; it is NOT the frozen
    build's state (there WRITTEN would not list unit 4: the R035 class stays a stated limit of E5)."""
    _, E, _, _ = uc
    s = request(uc, wpre=None)
    s.nopred(4, "Neither the functional Vice President nor the People Business Partner gave written pre-approval.", True,
             "If your manager is supportive, discuss and obtain pre-approval in writing from your functional Vice "
             "President and People Business Partner.", "request")
    got = ask(uc, s, {"acc": ACC}, "M17")
    assert got["acc"]["answer"] == "OPEN" and "encoder rule E5" in got["acc"]["refused"]
    assert ask(uc, request(uc, wpre=None), {"acc": ACC}, "M17")["acc"]["answer"] == "yes"   # the frozen behaviour
