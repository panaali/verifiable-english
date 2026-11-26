"""Universal Credit award (usecases/uc_award): reg. 3(6) read from both sides of a pair, and at most one partner per
claimant (row statute-xfam-wrong-uc-award-1; DRI decide wake 20261124T0212Z).

The frozen build (9517f4dcd2) ended a couple under UC Regs 2013 reg. 3(6) only when the award anchor's PARTNER was the
absent member, so with the absent member himself as anchor his couple stood (cross-family U035-5 / U035-6: Bob, absent
over six months from Ann's household, kept Ann as a joint partner beside Cara). These tests pin the rule:
* the pair (x, y) ceases to be a couple when EITHER member is the one temporarily absent over six months from the
  other's household, whichever of them anchors the award (the pair has one status in every award);
* a member of two couples needs the household the absence is from (absent_from); without it the award is refused;
* a claimant holds at most one partner: when reg. 3(4)-(6) leave two couple links standing, VE refuses rather than
  answer on two joint partners;
* planted errors M7 (one-sided reg. 3(6)) and M8 (the 9517f4dcd2 reading: one-sided and no partner refusal) change
  these answers.
Each award is derived by the use case's own staged prover (usecases/uc_award/run.py run_case); the cross-family and
same-family runs replay every certificate in Lean.
"""
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(__file__).resolve().parents[1] / "usecases" / "uc_award"


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import cases as K
        import run as R
        import translation as T
        yield K, R, T


def go(uc, case, mutant=None):
    K, R, T = uc
    answers, _, staged, _, _, _ = R.run_case(case, mutant)
    return answers, staged


def truth(uc, staged, pred, x, y):
    return staged.truth(uc[2].B(pred, x, y))


def couple_absent(uc, anchor, absent="bob", links=()):
    """Ann and Bob, a couple, both 30; the absent member temporarily absent over six months."""
    K = uc[0]
    return K.award(f"T36{anchor}", "T36", anchor, {"ann": ("30", "500.00", "0.00"), "bob": ("30", "300.00", "0.00")},
                   facts={absent: ["temp_absent", "abs_over6"]}, links=[("couple", "ann", "bob"), *links])


POLY = [("couple", "ann", "bob"), ("couple", "bob", "cara"), ("married", "bob", "ann"), ("married", "bob", "cara"),
        ("poly_law", "bob", "ann"), ("poly_law", "bob", "cara"), ("earlier", "bob", "ann")]


def poly(uc, anchor, scoped=True):
    """Bob married to Ann (earlier) and Cara under a law permitting polygamy; Ann lives apart; Bob temporarily absent
    over six months from ANN's household (absent_from when scoped); Ann has limited capability for work."""
    K = uc[0]
    links = POLY + ([("absent_from", "bob", "ann")] if scoped else [])
    return K.award(f"T37{anchor}", "T37", anchor, {"ann": ("35", "900.00", "0.00"), "bob": ("40", "400.00", "0.00"),
                                                   "cara": ("28", "0.00", "0.00")},
                   facts={"ann": ["lcw"], "bob": ["temp_absent", "abs_over6"]}, links=links,
                   qids=(4, 5, 6) if anchor == "bob" else (1, 2, 3))


def test_reg36_anchor_is_the_absent_member_pair_status_same_from_both_sides(uc):
    """Bob absent over six months: Ann's award and Bob's own award both treat the pair as no couple (old code: Bob's
    award kept Ann as his joint partner)."""
    ann, s_ann = go(uc, couple_absent(uc, "ann"))
    bob, s_bob = go(uc, couple_absent(uc, "bob"))
    assert truth(uc, s_ann, "tcp", "ann", "bob") is False
    assert truth(uc, s_bob, "tcp", "bob", "ann") is False
    assert ann["T36-3"]["answer"] == bob["T36-3"]["answer"] == "SINGLE"
    assert bob["T36-1"] == {"answer": "AMOUNT", "gbp": "424.90"}  # single 25 or over; Ann's income not counted
    assert bob["T36-2"] == {"answer": "AMOUNT", "gbp": "259.90"}  # 424.90 - 55% x 300.00


def test_reg36_absent_from_decides_which_of_two_couples_ends(uc):
    """A member of two couples absent from ONE household: that couple ends from both sides, the other stands; one
    joint partner only."""
    bob, s_bob = go(uc, poly(uc, "bob"))
    ann, s_ann = go(uc, poly(uc, "ann"))
    assert truth(uc, s_bob, "tcp", "bob", "ann") is False
    assert truth(uc, s_ann, "tcp", "ann", "bob") is False
    assert truth(uc, s_bob, "jointp", "bob", "cara") is True
    assert truth(uc, s_bob, "jointp", "bob", "ann") is False
    assert bob["T37-6"] == {"answer": "JOINT", "row": "NONE"}  # neither Bob nor Cara has LCW or a child
    assert bob["T37-4"] == {"answer": "AMOUNT", "gbp": "666.97"}
    assert bob["T37-5"] == {"answer": "AMOUNT", "gbp": "446.97"}  # 666.97 - 55% x 400.00 (Ann's 900.00 not counted)
    assert ann["T37-3"] == {"answer": "SINGLE", "row": "HIGHER SINGLE"}


@pytest.mark.parametrize("anchor", ["ann", "bob"])
def test_unscoped_absence_of_a_member_of_two_couples_is_refused(uc, anchor):
    """The 9517f4dcd2 facts shape (absence on Bob, two couple links, no household named): refused in each award (old
    code: Ann's award answered single, Bob's award answered on two joint partners)."""
    answers, _ = go(uc, poly(uc, anchor, scoped=False))
    assert {a["answer"] for a in answers.values()} == {"UNSUPPORTED"}
    assert all("reg. 3(6)" in a["refused"] for a in answers.values())


def test_reg36_the_other_couple_of_the_absent_member_stands_from_both_sides(uc):
    """U035 shape, Cara's award: Bob's absence is from Ann's household, so Bob and Cara stay a couple (joint), as in
    Bob's own award; Bob-Ann (ended) gives Bob no second partner."""
    case = poly(uc, "cara")
    answers, staged = go(uc, case)
    assert truth(uc, staged, "tcp", "cara", "bob") is True
    assert truth(uc, staged, "tcp", "bob", "ann") is False
    assert answers["T37-3"] == {"answer": "JOINT", "row": "NONE"}


def two_couples(uc, anchor, facts=None):
    """Bob a stated couple with Ann and with Cara, nothing in reg. 3(4)-(6) ending either."""
    K = uc[0]
    return K.award(f"T38{anchor}", "T38", anchor, {"ann": ("35", "100.00", "0.00"), "bob": ("40", "400.00", "0.00"),
                                                   "cara": ("28", "0.00", "0.00")},
                   facts=facts, links=[("couple", "ann", "bob"), ("couple", "bob", "cara")])


def test_two_couple_links_at_most_one_joint_partner_two_jointp_refused(uc):
    """Bob's award: the rules prove jointp for both partners, and VE refuses instead of answering on two joint
    partners (old code: answered JOINT)."""
    answers, staged = go(uc, two_couples(uc, "bob"))
    assert truth(uc, staged, "jointp", "bob", "ann") is True
    assert truth(uc, staged, "jointp", "bob", "cara") is True
    assert {a["answer"] for a in answers.values()} == {"UNSUPPORTED"}
    assert all("at most one partner" in a["refused"] for a in answers.values())


@pytest.mark.parametrize("anchor", ["ann", "cara"])
def test_partner_with_a_second_standing_couple_is_refused_in_the_other_awards(uc, anchor):
    """The same facts, Ann's or Cara's award: her partner Bob stays treated as a couple with the other woman, so the
    pair has no single status and VE refuses (it never makes Bob a joint claimant with Ann in one award and with Cara
    in another; old code: answered JOINT)."""
    answers, staged = go(uc, two_couples(uc, anchor))
    other = "cara" if anchor == "ann" else "ann"
    assert truth(uc, staged, "tcp", anchor, "bob") is True
    assert truth(uc, staged, "tcp", "bob", other) is True
    assert {a["answer"] for a in answers.values()} == {"UNSUPPORTED"}
    assert all("at most one partner" in a["refused"] for a in answers.values())


def test_two_treated_couples_with_one_joint_partner_still_refused(uc):
    """Cara a prisoner (reg. 3(3)(c)): Bob and Cara are a couple but not joint claimants; with Ann also his couple, Bob
    has two treated partners and one jointp, and the award is still refused (two tcp)."""
    answers, staged = go(uc, two_couples(uc, "bob", facts={"cara": ["prisoner"]}))
    assert truth(uc, staged, "jointp", "bob", "ann") is True
    assert truth(uc, staged, "jointp", "bob", "cara") is False
    assert truth(uc, staged, "tcp", "bob", "cara") is True
    assert {a["answer"] for a in answers.values()} == {"UNSUPPORTED"}


def test_reg34_polygamy_leaving_one_partner_is_still_answered(uc):
    """reg. 3(4) disregards the later marriage when the earlier wife lives in the household: one partner remains, so
    the partner refusal does not fire (the same-family U023 shape)."""
    K = uc[0]
    case = K.award("T39", "T39", "hamid", {"hamid": ("50", "400.00", "0.00"), "wafa": ("48", "0.00", "0.00"),
                                           "zara": ("32", "200.00", "0.00")},
                   facts={"wafa": ["same_household"], "zara": ["same_household"]},
                   links=[("couple", "hamid", "wafa"), ("couple", "hamid", "zara"), ("married", "hamid", "wafa"),
                          ("married", "hamid", "zara"), ("poly_law", "hamid", "wafa"), ("poly_law", "hamid", "zara"),
                          ("earlier", "hamid", "wafa")])
    answers, staged = go(uc, case)
    assert truth(uc, staged, "tcp", "hamid", "zara") is False
    assert answers["T39-3"] == {"answer": "JOINT", "row": "NONE"}


T39_PERSONS = {"hamid": ("50", "400.00", "0.00"), "wafa": ("48", "0.00", "0.00"), "zara": ("32", "200.00", "0.00")}
T39_LINKS = [("couple", "hamid", "wafa"), ("couple", "hamid", "zara"), ("married", "hamid", "wafa"),
             ("married", "hamid", "zara"), ("poly_law", "hamid", "wafa"), ("poly_law", "hamid", "zara"),
             ("earlier", "hamid", "wafa")]


def test_reg34_earlier_spouse_award_is_answered_joint(uc):
    """The same household seen from Wafa (the earlier wife, anchor): reg. 3(4) disregards Hamid-Zara, so Hamid has one
    partner and Wafa and Hamid are joint claimants. The household judgement is anchor-relative (Hamid and Zara live in
    Wafa's household); the outer pair reads it from her side (AUDIT-reg36.md finding 1: 593a9b6265 refused, reading
    same_household of the anchor herself)."""
    K = uc[0]
    case = K.award("T39w", "T39", "wafa", T39_PERSONS, facts={"hamid": ["same_household"], "zara": ["same_household"]},
                   links=T39_LINKS)
    answers, staged = go(uc, case)
    assert truth(uc, staged, "tcp", "wafa", "hamid") is True
    assert truth(uc, staged, "tcp", "hamid", "zara") is False
    assert answers["T39-3"] == {"answer": "JOINT", "row": "NONE"}


def test_reg34_later_spouse_award_is_single(uc):
    """Zara's award (the later wife): 3(4) disregards her marriage to Hamid, so she claims as a single person (the
    text's "the person who is not a party to the earlier marriage may make a claim ... as a single person")."""
    K = uc[0]
    case = K.award("T39z", "T39", "zara", T39_PERSONS, facts={"hamid": ["same_household"], "wafa": ["same_household"]},
                   links=T39_LINKS)
    answers, staged = go(uc, case)
    assert truth(uc, staged, "tcp", "zara", "hamid") is False
    assert answers["T39-3"]["answer"] == "SINGLE"


def test_reg34_outer_pair_household_not_established_is_refused(uc):
    """Wafa's award with no household facts: reg. 3(4)(b) is not established for Hamid-Zara from her side, so Hamid
    stays a couple with Zara and the award is refused (never answered on two partners)."""
    K = uc[0]
    answers, _ = go(uc, K.award("T39n", "T39", "wafa", T39_PERSONS, links=T39_LINKS))
    assert {a["answer"] for a in answers.values()} == {"UNSUPPORTED"}
    assert all("at most one partner" in a["refused"] for a in answers.values())


def test_absent_from_the_only_partner_equals_the_unstated_default(uc):
    """For a member of one couple, absent_from(bob, ann) states what the unary absence already means."""
    plain, _ = go(uc, couple_absent(uc, "bob"))
    scoped, _ = go(uc, couple_absent(uc, "bob", links=[("absent_from", "bob", "ann")]))
    assert plain == scoped


def test_absence_from_another_household_does_not_end_the_couple(uc):
    """Bob absent from a third person's household (not Ann's): the pair Ann-Bob stands (reg. 3(6) reads the absence
    from the claimant's household)."""
    K = uc[0]
    case = K.award("T40", "T40", "ann", {"ann": ("30", "500.00", "0.00"), "bob": ("30", "300.00", "0.00"),
                                         "dee": ("60", "0.00", "0.00")},
                   facts={"bob": ["temp_absent", "abs_over6"]},
                   links=[("couple", "ann", "bob"), ("absent_from", "bob", "dee")])
    answers, staged = go(uc, case)
    assert truth(uc, staged, "tcp", "ann", "bob") is True
    assert answers["T40-3"]["answer"] == "JOINT"


def test_mutants_m7_m8_restore_the_one_sided_reading(uc):
    """M7 (one-sided reg. 3(6), partner refusal kept): Bob's own award with the anchor absent turns JOINT, and the
    two-couple award is refused. M8 (the 9517f4dcd2 reading): the two-couple award is answered with Ann as a second
    joint partner (her income and limited capability counted)."""
    m7, _ = go(uc, couple_absent(uc, "bob"), "M7")
    assert m7["T36-3"]["answer"] == "JOINT"
    m7p, _ = go(uc, poly(uc, "bob"), "M7")
    assert {a["answer"] for a in m7p.values()} == {"UNSUPPORTED"}
    assert all("at most one partner" in a["refused"] for a in m7p.values())
    m8, s8 = go(uc, poly(uc, "bob"), "M8")
    assert truth(uc, s8, "jointp", "bob", "ann") is True and truth(uc, s8, "jointp", "bob", "cara") is True
    assert m8["T37-6"] == {"answer": "JOINT", "row": "HIGHER JOINT"}
    assert m8["T37-5"] == {"answer": "AMOUNT", "gbp": "342.47"}  # 666.97 - 55% x (1300.00 - 710.00)


def test_overlay_refuses_a_household_outside_the_record():
    """reg36_overlay: an absence from the household of someone the award record does not name is an error, never
    skipped (the absent6 default would read it as the record's own couple)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("reg36_overlay_t", UC / "xfam" / "reg36_overlay.py")
    ov = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ov)
    import json
    import tempfile
    rec = {"id": "Xc", "case": "X", "persons": ["bob", "cara"], "links": [["couple", "bob", "cara"]]}
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "a.jsonl"
        f.write_text(json.dumps({"id": "X", "person": "Bob", "absent_from": ["Ann"]}) + "\n", encoding="utf-8")
        with pytest.raises(ValueError, match="not a person of the record"):
            ov.apply([rec], f)
        f.write_text(json.dumps({"id": "X", "person": "Bob", "absent_from": ["Cara"]}) + "\n", encoding="utf-8")
        assert ov.apply([rec], f) == {"Xc": [("absent_from", "bob", "cara")]}
