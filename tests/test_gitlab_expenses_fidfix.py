"""GitLab travel and expense policy (usecases/gitlab_expenses/translation.py, run.py): twelve latent departures found by the
fidelity sweep, fixed in the rule (rows statute-latent-gitlab-expenses-U4, -U7, -U16, -U21, -U33, -U34, -U36, -U39, -U41,
-U67, -U74, -U76; manage-agents reviews/spare/statute-corpus/fidelity-check/sweep/gitlab-expenses.md, flags FL01-FL18).

Each test is the check seat's own test case, encoded with this use case's encoder (encode.Sub) and answered by its own
staged prover (run.run_sub; the question-set run replays every certificate in Lean). Each states the answer the source
gives (or no answer where the source leaves it open) and FAILS on the frozen commit 24ed6a6481 and on after-release with
the frozen rules. Each planted error M25-M38 (translation.MUTANTS) restores one frozen rule and is killed here.

Two encodings depend on the vocabulary in force, so that the same case is stated in each version's own words:
* unit 74's guard: the fixed rules apply only where the travel is stated not to be to an internal event (fact ievt);
  the frozen vocabulary has no such fact, so the cases state it only where it exists;
* FL01: the frozen fact appr meant 'approved AND attached'; the fixed appr is the approval alone (att = attached). A case
  with the approval given but not attached is appr false in the frozen vocabulary, appr true + att false in the fixed one.
"""
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(__file__).resolve().parents[1] / "usecases" / "gitlab_expenses"


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import encode as E
        import run as R
        import translation as T
        yield E, R, T


def ask(uc, sub, questions, mutant=None):
    """{qid: answer or value} for one made-up sub-case; questions [(qid, form)]."""
    _, R, _ = uc
    got = R.run_sub({"spec": sub, "questions": [{"qid": q, "form": f} for q, f in questions]}, mutant)[0]
    return {q: a.get("value", a["answer"]) for q, a in got.items()}


def base(uc, ievt=False):
    """A sub-case; ievt False = the travel is stated not to be to an internal GitLab event (None: not stated)."""
    E, _, T = uc
    s = E.Sub()
    if "ievt" in T.FACTS and ievt is not None:
        s.fact("ievt", val=ievt)
    return s


def approval(uc, s, f, approved, attached):
    T = uc[2]
    if "att" in T.FACTS:
        return s.fact("appr", f, approved).fact("att", f, attached)
    return s.fact("appr", f, approved and attached)


def flight(uc, s, f, *, intl, sel, bus=3, segs=((5, 1),), price="500.00", dp="500.00", ch="480.00", bu="50.00",
           bk="2028-03-01", dep="2028-03-21", navan=True, approved=False, attached=False, reason=None):
    s.item(f, "flight").fact("intl", f, intl).fact("navan", f, navan).fact("biz", f)
    approval(uc, s, f, approved, attached)
    s.val("pr", f, price).val("dp", f, dp).val("ch", f, ch).val("bu", f, bu).val("bk", f, bk).val("dep", f, dep)
    s.val("rsel", f, sel).val("rstd", f, 1).val("rbus", f, bus)
    for i, (h, m) in enumerate(segs):
        s.seg(f"{f}s{i + 1}", f, h, m)
    if reason is not None:
        for r in ("rcus", "rspk", "rcnf"):
            s.fact(r, f, r == reason)
    return s


# --- U4 (FL01): the height upgrade needs the manager's approval, not its attachment ---------------------------------------

def fl01(uc):
    s = base(uc).fact("incm").val("cm", "p", "201")
    return flight(uc, s, "f", intl=False, sel=2, segs=((3, 0),), approved=True, attached=False)


def test_u4_fl01_height_upgrade_with_approval_not_attached_is_in_policy(uc):
    assert ask(uc, fl01(uc), [("ph", ("yn", "ph", "f")), ("c", ("yn", "clsok", "f"))]) == {"ph": "yes", "c": "yes"}


def test_m25_frozen_u4_attachment_killed(uc):
    assert ask(uc, fl01(uc), [("c", ("yn", "clsok", "f"))], "M25") == {"c": "no"}


# --- U4 (FL02): a permission whose facts are not stated is not a failed permission ----------------------------------------

def fl02(uc):
    s = base(uc).fact("incm").val("cm", "p", "180")
    return flight(uc, s, "f", intl=True, sel=3, segs=((9, 0),), reason="rcus")


def test_u4_fl02_business_with_no_trip_list_has_no_answer(uc):
    assert ask(uc, fl02(uc), [("c", ("yn", "clsok", "f"))]) == {"c": "OPEN"}


def test_m26_frozen_u4_dropped_route_killed(uc):
    assert ask(uc, fl02(uc), [("c", ("yn", "clsok", "f"))], "M26") == {"c": "no"}


# --- U7 (FL03): only international trips' 8-hour segments count -----------------------------------------------------------

def fl03(uc):
    s = base(uc).fact("incm").val("cm", "p", "180")
    for i in (1, 2, 3):
        s.item(f"t{i}", "trip").fact("intl", f"t{i}").seg(f"t{i}s1", f"t{i}", 9, 0)
    s.item("t4", "trip").fact("intl", "t4", False)
    for j in (1, 2, 3):
        s.seg(f"t4s{j}", "t4", 9, 0)
    return flight(uc, s, "f", intl=True, sel=3, segs=((9, 0),), reason="rcus")


def test_u7_fl03_domestic_long_segments_do_not_make_a_frequent_traveller(uc):
    assert ask(uc, fl03(uc), [("pf", ("yn", "pfreq", "f")), ("c", ("yn", "clsok", "f"))]) == {"pf": "no", "c": "no"}


def test_m27_frozen_u7_counts_killed(uc):
    assert ask(uc, fl03(uc), [("pf", ("yn", "pfreq", "f"))], "M27") == {"pf": "yes"}


# --- U16 (FL04, FL05): automatic acceptance follows unit 15's email for a flight booked in Navan --------------------------

def chk(s, noact=True):
    s.item("c", "chk").clock("bd", "bm", "c", "2028-03-01", "10:00").clock("td", "tm", "c", "2028-03-02", "10:00")
    return s.fact("noact", "c", noact).fact("apv", "c", False).fact("den", "c", False)


def fl04(uc, navan=False, price="500.00"):
    s = base(uc).fact("incm").val("cm", "p", "170")
    return chk(flight(uc, s, "f", intl=False, sel=1, segs=((3, 0),), price=price, navan=navan))


def test_u16_fl04_booking_outside_navan_is_not_accepted_by_silence(uc):
    assert ask(uc, fl04(uc), [("a", ("yn", "acc", "c"))]) == {"a": "OPEN"}


def test_u16_emailed_navan_booking_still_accepted_after_24_hours(uc):
    """Guard: a Navan booking over the cheapest option + buffer (unit 14) is emailed and accepted after 24 hours."""
    assert ask(uc, fl04(uc, navan=True, price="600.00"), [("a", ("yn", "acc", "c"))]) == {"a": "yes"}


def test_m28_frozen_u16_any_flag_killed(uc):
    assert ask(uc, fl04(uc), [("a", ("yn", "acc", "c"))], "M28") == {"a": "yes"}


def fl05(uc):
    s = base(uc).item("h", "stay").fact("navan", "h").fact("std", "h").val("amt", "h", "250.00").val("dp", "h", "300.00")
    return chk(s)


def test_u16_fl05_no_flight_no_automatic_acceptance(uc):
    assert ask(uc, fl05(uc), [("a", ("yn", "acc", "c"))]) == {"a": "OPEN"}


def test_m29_frozen_u16_no_flight_killed(uc):
    assert ask(uc, fl05(uc), [("a", ("yn", "acc", "c"))], "M29") == {"a": "yes"}


# --- U21 (FL07): fuel $300 limit per DAY ---------------------------------------------------------------------------------

def fuel_day(uc, amounts):
    s = base(uc).item("d", "fday")
    for i, a in enumerate(amounts):
        s.item(f"u{i + 1}", "fuelx", "d").fact("renting", f"u{i + 1}").fact("fuel", f"u{i + 1}").val("amt", f"u{i + 1}", a)
    return s


FUEL_Q = [("u1", ("amt", "rmb", "u1")), ("u2", ("amt", "rmb", "u2"))]


def test_u21_fl07_two_fuel_purchases_over_300_in_a_day_not_both_in_full(uc):
    got = ask(uc, fuel_day(uc, ["200.00", "150.00"]), FUEL_Q)
    assert got != {"u1": "200.00", "u2": "150.00"}
    assert got == {"u1": "OPEN", "u2": "OPEN"}


def test_u21_single_fuel_purchase_at_the_limit_in_full(uc):
    assert ask(uc, fuel_day(uc, ["300.00"]), FUEL_Q[:1]) == {"u1": "300.00"}


def test_m30_frozen_u21_per_item_killed(uc):
    assert ask(uc, fuel_day(uc, ["200.00", "150.00"]), FUEL_Q, "M30") == {"u1": "200.00", "u2": "150.00"}


# --- U32/U33/U36 (FL09, FL11): the $300 hotel cap ---------------------------------------------------------------------------

def room(uc, amt, *, notappl=None, block=False, excg=None, exc=None, alt=None, corp=None, only=False, refund=True):
    s = base(uc).item("h", "stay").fact("navan", "h").fact("std", "h").val("amt", "h", amt).val("dp", "h", "320.00")
    s.val("ci", "h", "2028-03-08").val("co", "h", "2028-03-09").val("bk", "h", "2028-03-01").fact("block", "h", block)
    s.fact("only", "h", only).fact("refund", "h", refund).fact("airbnb", "h", False)
    if notappl is not None:
        s.fact("notappl", "h", notappl)
    if excg is not None:
        s.fact("excg", "h", excg)
    if exc is not None:
        s.val("exc", "h", exc)
    if alt is not None:
        s.val("alt", "h", alt)
    if corp is not None:
        s.fact("corp", "h", corp)
    return s


RMB = [("r", ("amt", "rmb", "h"))]


def test_u33_fl09_limit_not_applicable_no_300_cap(uc):
    assert ask(uc, room(uc, "340.00", notappl=True), RMB) == {"r": "OPEN"}


def test_u32_limit_applicable_still_capped(uc):
    assert ask(uc, room(uc, "300.01", notappl=False), RMB) == {"r": "300.00"}


def test_m31_frozen_u33_cap_killed(uc):
    assert ask(uc, room(uc, "340.00", notappl=True), RMB, "M31") == {"r": "300.00"}


def fl11(uc):
    return room(uc, "320.00", notappl=False, block=True, corp=False, alt="360.00", excg=True, exc="320.00")


def test_u36_fl11_block_room_with_ap_exception_reimbursed_at_its_rate(uc):
    assert ask(uc, fl11(uc), RMB) == {"r": "320.00"}


def test_m33_frozen_u36_cap_killed(uc):
    assert ask(uc, fl11(uc), RMB, "M33") == {"r": "300.00"}


# --- U34 (FL10): unit 35's block exception needs a Corporate Events block or better pricing --------------------------------

def fl10(uc):
    return room(uc, "280.00", block=True, corp=False, alt="250.00", refund=False)


def test_u34_fl10_conference_block_not_better_than_navan_must_be_refundable(uc):
    assert ask(uc, fl10(uc), [("n", ("yn", "nrok", "h"))]) == {"n": "no"}


def test_m32_frozen_u34_any_block_killed(uc):
    assert ask(uc, fl10(uc), [("n", ("yn", "nrok", "h"))], "M32") == {"n": "yes"}


# --- U39 (FL13), U41 (FL14): room service and hotel parking within the DAY's limits -----------------------------------------

def rs_day(uc, amt, others):
    s = base(uc).item("h", "stay").item("i1", "inc", "h").fact("rsv", "i1").fact("mtag", "i1").fact("report", "i1")
    s.val("amt", "i1", amt).item("d1", "rsday", "i1")
    for j, a in enumerate(others):
        s.item(f"e{j + 1}", "meal", "d1").val("amt", f"e{j + 1}", a)
    return s


def test_u39_fl13_room_service_over_the_days_meal_limit_not_yes(uc):
    assert ask(uc, rs_day(uc, "60.00", ["30.00", "50.00"]), [("i", ("yn", "iok", "i1"))]) == {"i": "OPEN"}


def test_u39_room_service_within_the_days_meal_limit_yes(uc):
    assert ask(uc, rs_day(uc, "40.00", []), [("i", ("yn", "iok", "i1"))]) == {"i": "yes"}


def test_m34_frozen_u39_per_item_killed(uc):
    assert ask(uc, rs_day(uc, "60.00", ["30.00", "50.00"]), [("i", ("yn", "iok", "i1"))], "M34") == {"i": "yes"}


def pk_day(uc, amt, others):
    s = base(uc).item("h", "stay").item("i2", "inc", "h").fact("park", "i2").fact("ptag", "i2").fact("client", "i2")
    s.fact("desc", "i2").fact("report", "i2").val("amt", "i2", amt).item("d2", "pkday", "i2")
    for j, a in enumerate(others):
        s.item(f"g{j + 1}", "ground", "d2").val("amt", f"g{j + 1}", a)
    return s


def test_u41_fl14_hotel_parking_over_the_days_parking_and_tolls_limit_not_yes(uc):
    assert ask(uc, pk_day(uc, "100.00", ["80.00"]), [("i", ("yn", "iok", "i2"))]) == {"i": "OPEN"}


def test_u41_hotel_parking_within_the_days_limit_yes(uc):
    assert ask(uc, pk_day(uc, "20.00", []), [("i", ("yn", "iok", "i2"))]) == {"i": "yes"}


def test_m35_frozen_u41_per_item_killed(uc):
    assert ask(uc, pk_day(uc, "100.00", ["80.00"]), [("i", ("yn", "iok", "i2"))], "M35") == {"i": "yes"}


# --- U67 (FL15): standard class may always be booked -----------------------------------------------------------------------

def fl15(uc):
    s = base(uc)
    for i in (1, 2):
        s.item(f"t{i}", "ttrip").seg(f"t{i}s1", f"t{i}", 5, 1).seg(f"t{i}s2", f"t{i}", 5, 1)
    s.item("r", "train").fact("navan", "r").val("pr", "r", "100.00").val("dp", "r", "100.00").val("bk", "r", "2028-03-01")
    return s.val("dep", "r", "2028-03-15").val("rsel", "r", 1).val("rstd", "r", 1)


def test_u67_fl15_standard_class_may_be_booked_by_a_non_frequent_traveller(uc):
    assert ask(uc, fl15(uc), [("t", ("yn", "tup", "r"))]) == {"t": "yes"}


def test_m36_frozen_u67_killed(uc):
    assert ask(uc, fl15(uc), [("t", ("yn", "tup", "r"))], "M36") == {"t": "no"}


# --- U74 (FL17): internal events follow their own guidelines ---------------------------------------------------------------

def fl17(uc, ievt=True):
    s = base(uc, ievt=ievt).fact("incm").val("cm", "p", "180")
    s = flight(uc, s, "f", intl=True, sel=2, segs=((9, 0),))
    return s.fact("intev", "f", True) if ievt else s


def test_u74_fl17_internal_event_travel_gets_no_general_policy_answer(uc):
    assert ask(uc, fl17(uc), [("c", ("yn", "clsok", "f"))]) == {"c": "OPEN"}


def test_u74_event_not_stated_gets_no_answer(uc):
    assert ask(uc, fl17(uc, ievt=None), [("c", ("yn", "clsok", "f"))]) == {"c": "OPEN"}


def test_u74_not_an_internal_event_answers(uc):
    assert ask(uc, fl17(uc, ievt=False), [("c", ("yn", "clsok", "f"))]) == {"c": "yes"}


def test_m37_frozen_u74_killed(uc):
    assert ask(uc, fl17(uc), [("c", ("yn", "clsok", "f"))], "M37") == {"c": "yes"}


# --- U76 (FL18): internet $50 per DAY -----------------------------------------------------------------------------------

def net_day(uc, amounts):
    s = base(uc).item("nd", "nday")
    for i, a in enumerate(amounts):
        s.item(f"n{i + 1}", "net", "nd").fact("trav", f"n{i + 1}").fact("desc", f"n{i + 1}").val("amt", f"n{i + 1}", a)
    return s


NET_Q = [("n1", ("amt", "rmb", "n1")), ("n2", ("amt", "rmb", "n2")), ("d", ("amt", "rmb", "nd"))]


def test_u76_fl18_two_internet_charges_capped_per_day(uc):
    got = ask(uc, net_day(uc, ["40.00", "30.00"]), NET_Q)
    assert (got["n1"], got["n2"]) != ("40.00", "30.00")
    assert got == {"n1": "OPEN", "n2": "OPEN", "d": "50.00"}


def test_u76_single_charge_over_50_capped(uc):
    assert ask(uc, net_day(uc, ["50.01"]), NET_Q[:1]) == {"n1": "50.00"}


def test_m38_frozen_u76_per_charge_killed(uc):
    got = ask(uc, net_day(uc, ["40.00", "30.00"]), NET_Q[:2], "M38")
    assert got == {"n1": "40.00", "n2": "30.00"}


# --- fidelity step on the changed units (reader flags of the fix's own step: R25-R27) ----------------------------------------

def frequent(uc, *, intl, sel, bus=3):
    """3 international trips of two 9h00 segments each (a frequent traveller); the asked flight one 9h00 segment."""
    s = base(uc).fact("incm").val("cm", "p", "180")
    for i in (1, 2, 3):
        s.item(f"t{i}", "trip").fact("intl", f"t{i}").seg(f"t{i}s1", f"t{i}", 9, 0).seg(f"t{i}s2", f"t{i}", 9, 0)
    return flight(uc, s, "f", intl=intl, sel=sel, bus=bus, segs=((9, 0),), reason="rcus")


def test_u7_step_domestic_8h_flight_of_a_frequent_traveller_has_no_answer(uc):
    assert ask(uc, frequent(uc, intl=False, sel=3), [("pf", ("yn", "pfreq", "f"))]) == {"pf": "OPEN"}


def test_u7_international_business_of_a_frequent_traveller_permitted(uc):
    assert ask(uc, frequent(uc, intl=True, sel=3), [("pf", ("yn", "pfreq", "f"))]) == {"pf": "yes"}


def test_m39_earlier_u7_domestic_killed(uc):
    assert ask(uc, frequent(uc, intl=False, sel=3), [("pf", ("yn", "pfreq", "f"))], "M39") == {"pf": "no"}


def test_u7_step_premium_two_above_standard_for_a_frequent_traveller_has_no_answer(uc):
    """Classes standard, economy plus, premium, business, first: premium (3) is below business (4), not the next class."""
    assert ask(uc, frequent(uc, intl=True, sel=3, bus=4), [("c", ("yn", "clsok", "f"))]) == {"c": "OPEN"}


def test_m40_earlier_u7_business_only_killed(uc):
    assert ask(uc, frequent(uc, intl=True, sel=3, bus=4), [("c", ("yn", "clsok", "f"))], "M40") == {"c": "no"}


def test_u32_step_room_booked_two_days_ahead_has_no_amount(uc):
    s = room(uc, "250.00", notappl=False)
    late = base(uc).item("h", "stay").fact("navan", "h").fact("std", "h").val("amt", "h", "250.00")
    late.val("dp", "h", "320.00").val("ci", "h", "2028-03-08").val("co", "h", "2028-03-09").val("bk", "h", "2028-03-06")
    late.fact("block", "h", False).fact("notappl", "h", False)
    assert ask(uc, late, RMB) == {"r": "OPEN"}
    assert ask(uc, s, RMB) == {"r": "250.00"}
    assert ask(uc, late, RMB, "M41") == {"r": "250.00"}


def trains(uc, n, h, m, sel=2):
    s = base(uc)
    for i in range(1, n + 1):
        s.item(f"t{i}", "ttrip").seg(f"t{i}s1", f"t{i}", h, m).seg(f"t{i}s2", f"t{i}", h, m)
    s.item("r", "train").fact("navan", "r").val("pr", "r", "100.00").val("dp", "r", "100.00").val("bk", "r", "2028-03-01")
    return s.val("dep", "r", "2028-03-15").val("rsel", "r", sel).val("rstd", "r", 1)


def test_u67_step_trips_over_5_hours_together_have_no_answer(uc):
    """5 round trips of two 4h00 journeys: no journey over 5 hours, every trip over 5 hours together."""
    assert ask(uc, trains(uc, 5, 4, 0), [("t", ("yn", "tup", "r"))]) == {"t": "OPEN"}


def test_u67_short_trips_not_frequent(uc):
    assert ask(uc, trains(uc, 5, 2, 0), [("t", ("yn", "tup", "r"))]) == {"t": "no"}


def test_m42_earlier_u67_journey_reading_killed(uc):
    assert ask(uc, trains(uc, 5, 4, 0), [("t", ("yn", "tup", "r"))], "M42") == {"t": "no"}


# --- flags of the step's one re-read (R28, R29; not read a third time, STEP.md s.4) ------------------------------------------

def test_u7_trip_with_no_segments_is_not_counted(uc):
    """R28: a listed trip with no stated segments grounds no count (the frozen empty conjunction counted it surely)."""
    E, _, T = uc
    s = base(uc).item("t1", "trip").fact("intl", "t1")
    rules = T.rules(T.Ctx(s.items, s.parent))
    assert not [r for r in rules if r["defines"] and r["defines"][0] in ("tl_t1", "th_t1")]
    assert [r for r in T.rules(T.Ctx(s.items, s.parent), "M43") if r["defines"] and r["defines"][0] == "tl_t1"]


def empty_train_trip(uc):
    """3 train trips of three 5h01 journeys and a 4th trip listed with no journeys; first class (one up)."""
    s = base(uc)
    for i in (1, 2, 3):
        s.item(f"t{i}", "ttrip")
        for j in (1, 2, 3):
            s.seg(f"t{i}s{j}", f"t{i}", 5, 1)
    s.item("t4", "ttrip")
    s.item("r", "train").fact("navan", "r").val("pr", "r", "100.00").val("dp", "r", "100.00").val("bk", "r", "2028-03-01")
    return s.val("dep", "r", "2028-03-15").val("rsel", "r", 2).val("rstd", "r", 1)


def test_u67_train_trip_with_no_journeys_does_not_make_more_than_3(uc):
    assert ask(uc, empty_train_trip(uc), [("t", ("yn", "tup", "r"))]) == {"t": "OPEN"}


def test_m44_earlier_u67_empty_trip_killed(uc):
    assert ask(uc, empty_train_trip(uc), [("t", ("yn", "tup", "r"))], "M44") == {"t": "yes"}


def outside(uc, apadm):
    s = room(uc, "250.00", notappl=False)
    s.facts = [f for f in s.facts if f["formula"] != ["unary", "navan", ["const", "h"]]]
    return s.fact("navan", "h", False).fact("mgr", "h").fact("apadm", "h", apadm)


def test_u32_outside_navan_without_ap_admin_has_no_amount(uc):
    assert ask(uc, outside(uc, False), RMB) == {"r": "OPEN"}


def test_u32_outside_navan_with_both_approvals_reimbursed(uc):
    assert ask(uc, outside(uc, True), RMB) == {"r": "250.00"}


def test_m45_earlier_u32_outside_killed(uc):
    assert ask(uc, outside(uc, False), RMB, "M45") == {"r": "250.00"}


def test_planted_errors_restoring_each_frozen_rule_exist(uc):
    T = uc[2]
    assert {f"M{i}" for i in range(25, 46)} <= set(T.MUTANTS)
