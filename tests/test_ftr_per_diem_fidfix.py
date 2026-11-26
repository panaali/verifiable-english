"""FTR per diem (usecases/ftr_per_diem/translation.py): the fidelity sweep's six fix rows, one named test each (rows
statute-latent-ftr-per-diem-U8, -U20, -U24, -U27, -U33, -T013; manage-agents
reviews/spare/statute-corpus/fidelity-check/sweep/ftr-per-diem.md flags FL01, FL03, FL05, FL06, FL07, FL10).

Each row test is the check seat's test, answered by the text's own runner (run.py run_sub: the staged prover; the
question-set run replays every certificate in Lean). Each FAILS on the frozen commit 24d490f718 and on after-release
merged into it (the frozen answer is in the test's docstring), and passes on the fix. Each fix has a planted error
(translation.MUTANTS M27-M34; M11 and M29 for U24) restoring the frozen rule; the mutant tests show the row test's answer goes back to the
frozen one under it. The guards pin the answers the fix must keep. The audit seat's HIGH findings (fix-review.md) added
the rented-RV test (U20/U23, M33) and the ship-across-the-dateline test (U33); the fidelity step's flags on the fix
changed U24 to a refusal above the lodging rate and added the ship-day meal test (U56, M34).
"""
import copy
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(__file__).resolve().parents[1] / "usecases" / "ftr_per_diem"


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import cases as K
        import encode as E
        import kit
        import run as R
        import translation as T
        yield K, E, kit, R, T


def ask(uc, spec, form, mutant=None):
    R = uc[3]
    answers = R.run_sub({"spec": spec, "questions": [{"qid": "q", "form": form}]}, mutant)[0]
    a = answers["q"]
    return a.get("value", a["answer"])


def frame(uc, dep=("2027-02-01", "08:00"), ret=("2027-02-03", "18:00"), lr="140.00", mr="68.00", **kw):
    _, E, kit, _, _ = uc
    s = kit.trip(E.Sub(), dep=dep, ret=ret, **kw)
    return kit.loc(s, "ls", lr=lr, mr=mr)


# --- U8 (FL01): unit 8 "Agencies may allow a different method to be used each calendar day." -------------------------

def day_method_atom(T):
    """The atom that carries unit 8's per-day-method permission: daymeth after the fix; on the frozen translation the
    permission exists only inside mayalt (its wording: '... in advance and a different method each calendar day')."""
    return "daymeth" if "daymeth" in T.DERIVED else "mayalt"


def not_advantageous(uc):
    s = frame(uc, altauth=True)
    s.fact("adv", "t", False)
    return s


def test_u8_daily_method_permission_without_advantage(uc):
    """Kira lodges outside the TDY location, the agency judges it not advantageous (adv false); may the agency allow a
    different reimbursement method each calendar day? Source: yes. Frozen: no (Not mayalt <- Not adv)."""
    T = uc[4]
    assert ask(uc, not_advantageous(uc), ("yn", day_method_atom(T), "t")) == "yes"


def test_u8_guard_alternate_rate_and_methods(uc):
    """T025-7's conjunction (advantageous, authorized): mayalt yes; not advantageous: mayalt no (frozen and fix)."""
    s = frame(uc, altauth=True)
    s.fact("adv", "t", True)
    assert ask(uc, s, ("yn", "mayalt", "t")) == "yes"
    assert ask(uc, not_advantageous(uc), ("yn", "mayalt", "t")) == "no"


def test_m27_frozen_daily_method_killed(uc):
    assert ask(uc, not_advantageous(uc), ("yn", "daymeth", "t"), "M27") == "no"


# --- U20 (FL03): RV lodging "Reimbursable for expenses such as parking fees, ..." --------------------------------------

def rv_night(uc, rows, owned=True):
    """owned: the RV stated personally owned (fact rvown, added by the fix; the frozen translation has no such fact)."""
    _, _, kit, _, T = uc
    s = kit.night(frame(uc), "n1", "2027-02-01", ltype="rv", tax="0.00", arrive=("2027-02-01", "16:00"))
    if "rvown" in T.FACTS:
        s.fact("rvown", "n1", owned)
    return kit.items(s, "n1", "rvx", rows)


PROPANE = [("va", "20.00", dict(rvl=True, rvbuy=False)), ("vb", "15.00", dict(rvl=False, rvbuy=False))]


def test_u20_unlisted_rv_expense_refused(uc):
    """RV night, Springfield lodging rate $140: parking $20 (listed) and a $15 propane refill (not listed, not a
    purchase). Source: 'such as' does not exclude the $15: no definite $20. Frozen: $20.00."""
    assert ask(uc, rv_night(uc, PROPANE), ("amt", "lo", "n1")) == "OPEN"


def test_u20_guard_listed_and_purchase(uc):
    """Listed fees count, a purchase payment counts 0 (T010's shape): $20 + $4 = $24.00 (frozen and fix)."""
    rows = [("va", "20.00", dict(rvl=True, rvbuy=False)), ("vb", "4.00", dict(rvl=True, rvbuy=False)),
            ("vk", "90.00", dict(rvl=False, rvbuy=True))]
    assert ask(uc, rv_night(uc, rows), ("amt", "lo", "n1")) == "24.00"


def test_m28_frozen_rv_list_exhaustive_killed(uc):
    assert ask(uc, rv_night(uc, PROPANE), ("amt", "lo", "n1"), "M28") == "20.00"


RENTED = [("va", "20.00", dict(rvl=True, rvbuy=False)), ("vr", "60.00", dict(rvl=False, rvbuy=True))]


def test_u20_u23_payment_for_rv_not_stated_owned_refused(uc):
    """(Audit HIGH, FL04's path once unit 20's list is not exhaustive.) A night in an RV stated NOT personally owned: parking
    $20 and a $60 payment for the vehicle. Unit 23 bars paying for the vehicle only for a 'Personally-owned recreational
    vehicle' and unit 20's 'such as' leaves it open: refused. Frozen: $20.00 (the payment zeroed)."""
    assert ask(uc, rv_night(uc, RENTED, owned=False), ("amt", "lo", "n1")) == "OPEN"


def test_m33_frozen_rv_payment_bar_without_ownership_killed(uc):
    assert ask(uc, rv_night(uc, RENTED, owned=False), ("amt", "lo", "n1"), "M33") == "20.00"


# --- U24 (FL05): "The daily rate may not exceed the daily per diem rate for the TDY location." -------------------------

LX0 = dict(frent=False, urent=False, furn=False, necf=False, util=False, maid=False, reasm=False, phone=False, net=False,
           typ=False, inst=False, ldist=False)


def lx(**kw):
    return {**LX0, **kw}


def longterm(uc, rows, n=10, lr="120.00", mr="80.00", ret=("2027-02-11", "18:00"), asked=()):
    _, _, kit, _, _ = uc
    s = frame(uc, ret=ret, lr=lr, mr=mr)
    s.item("lt", "lt", "t")
    s.n["lt"] = n
    kit.items(s, "lt", "lx", rows)
    for x in asked:
        s.link[(x, "asked")] = True
    return s


def test_u24_longterm_cap_above_lodging_rate_refused(uc):
    """T014's facts: lodging $120, M&IE $80, furnished rent $2400 for 10 entitled days (240); T013's $2000 / 10 (200).
    The check seat read 'the daily per diem rate' as lodging plus M&IE ($200.00 both); the fix's fidelity reader read it
    as the lodging rate; the question writer marked both ambiguous. Above the lodging rate the cap is open: refused.
    Frozen: $120.00 both (the lodging-rate reading, definite)."""
    assert ask(uc, longterm(uc, [("ka", "2400.00", lx(frent=True))]), ("amt", "dlr", "lt")) == "OPEN"
    assert ask(uc, longterm(uc, [("ka", "2000.00", lx(frent=True))]), ("amt", "dlr", "lt")) == "OPEN"


def test_u24_guard_under_lodging_rate(uc):
    """$1200 / 10 = 120 at a $140 lodging rate: $120.00 (T012's shape; frozen and fix)."""
    assert ask(uc, longterm(uc, [("ka", "1200.00", lx(frent=True))], lr="140.00", mr="68.00"),
               ("amt", "dlr", "lt")) == "120.00"


def test_m29_frozen_lodging_rate_cap_killed(uc):
    assert ask(uc, longterm(uc, [("ka", "2400.00", lx(frent=True))]), ("amt", "dlr", "lt"), "M29") == "120.00"


def test_m11_cap_dropped_killed(uc):
    assert ask(uc, longterm(uc, [("ka", "2400.00", lx(frent=True))]), ("amt", "dlr", "lt"), "M11") == "240.00"


# --- U27 (FL06): "(b) Costs of connecting, disconnecting, and using utilities;" -----------------------------------------

UTIL_INST = [("ka", "1000.00", lx(frent=True)), ("kb", "50.00", lx(util=True, inst=True))]


def test_u27_utility_installation_not_excluded(uc):
    """A $50 charge for connecting electricity that the case calls the utility's installation fee (util and inst):
    unit 27 includes connecting utilities with no installation carve-out (that carve-out is units 29-30's, for the
    telephone and internet fees), so no definite 'not part of the lodging cost': refused. Frozen: no."""
    assert ask(uc, longterm(uc, UTIL_INST), ("yn", "allow", "kb")) == "OPEN"
    mixed = [("ka", "1000.00", lx(frent=True)), ("kc", "30.00", lx(phone=True, util=True, inst=True))]
    assert ask(uc, longterm(uc, mixed), ("yn", "allow", "kc")) == "OPEN"     # audit MEDIUM: also of another listed kind


def test_u27_guard_phone_internet_installation_excluded(uc):
    """T012's separate charges (installation, long-distance; no other kind) and a telephone fee stated as installation
    stay excluded; utilities alone and rent stay included (frozen and fix)."""
    rows = [("ka", "800.00", lx(urent=True)), ("kd", "20.00", lx(util=True)), ("kl", "25.00", lx(inst=True)),
            ("km", "15.00", lx(ldist=True)), ("ki", "20.00", lx(phone=True, inst=True)),
            ("kj", "20.00", lx(net=True, inst=True)), ("kp", "10.00", lx(phone=True, ldist=True))]
    s = longterm(uc, rows, asked=("kl", "km"))
    assert ask(uc, s, ("yn", "anyinc", "p")) == "no"
    for x, want in (("ka", "yes"), ("kd", "yes"), ("kl", "no"), ("km", "no"), ("ki", "no"), ("kj", "no"), ("kp", "no")):
        assert ask(uc, longterm(uc, rows), ("yn", "allow", x)) == want, x


def test_m30_frozen_installation_everywhere_killed(uc):
    assert ask(uc, longterm(uc, UTIL_INST), ("yn", "allow", "kb"), "M30") == "no"


# --- U33 (FL07): "When crossing the IDL, actual elapsed travel time will be used ... rather than calendar days." -------

def dateline(uc, idl=True, **trip_facts):
    _, _, kit, _, _ = uc
    s = frame(uc, dep=("2027-02-03", "22:00"), ret=("2027-02-05", "02:00"), zoned=(540, 540), idl=idl, mr="80.00",
              **trip_facts)
    for x, dy in (("d1", "2027-02-03"), ("d2", "2027-02-04"), ("d3", "2027-02-05")):
        kit.day(s, x, dy)
    return s


def test_u33_dateline_shares_not_by_calendar_days(uc):
    """Depart 22:00 3 Feb, return 02:00 5 Feb (both UTC+09), crossing the dateline, M&IE $80, days 3-5 Feb: the source
    counts elapsed time (28 hours), not calendar days, so no calendar-day share or amount: refused. Frozen: 100 percent
    and $80.00 for 4 Feb, $200.00 for the trip."""
    s = dateline(uc)
    assert ask(uc, s, ("share", "d2")) == "OPEN"
    assert ask(uc, s, ("amt", "mie", "d2")) == "OPEN"
    assert ask(uc, s, ("amt", "pdt", "t")) == "OPEN"


def ship_dateline(uc, idl=True):
    return dateline(uc, idl=idl, ship=True).val("shr", "t", "50.00")


def test_u33_ship_rate_not_by_calendar_days_across_dateline(uc):
    """(Audit HIGH.) The same trip by ship at the agency's $50 rate for each calendar day, crossing the dateline: no
    per-calendar-day amount (refused). Frozen: $50.00 for 4 Feb."""
    assert ask(uc, ship_dateline(uc), ("amt", "mie", "d2")) == "OPEN"


def ship_day(uc, provider):
    _, _, kit, _, _ = uc
    s = frame(uc, dep=("2027-02-01", "08:00"), ret=("2027-02-03", "18:00"), ship=True, mr="80.00")
    s.val("shr", "t", "50.00")
    return kit.day(s, "d2", "2027-02-02", meals=[("m1", "din", provider)])


def test_u56_ship_day_with_meal_to_deduct_refused(uc):
    """(Fidelity step flag on unit 56.) A ship day at the agency's $50 rate with a Government-provided dinner: unit 57
    deducts provided meals 'when M&IE per diem is authorized' and units 56-57 do not say how that applies to the agency's
    rate: refused. Frozen: $50.00 (no deduction)."""
    assert ask(uc, ship_day(uc, "gov"), ("amt", "mie", "d2")) == "OPEN"


def test_u56_guard_ship_day_carrier_meal(uc):
    """A common-carrier meal is not deducted (unit 59): $50.00 everywhere."""
    assert ask(uc, ship_day(uc, "carrier"), ("amt", "mie", "d2")) == "50.00"


def test_m34_frozen_ship_rate_without_deduction_killed(uc):
    assert ask(uc, ship_day(uc, "gov"), ("amt", "mie", "d2"), "M34") == "50.00"


def test_u33_guard_ship_without_dateline(uc):
    assert ask(uc, ship_dateline(uc, idl=False), ("amt", "mie", "d2")) == "50.00"


def test_u33_guard_same_trip_without_dateline(uc):
    """The same clock times with idl stated false keep the calendar-day shares: 100 percent / $80.00 for 4 Feb."""
    s = dateline(uc, idl=False)
    assert ask(uc, s, ("share", "d2")) == "100"
    assert ask(uc, s, ("amt", "mie", "d2")) == "80.00"
    assert ask(uc, s, ("yn", "ge24", "t")) == "yes"


def test_m31_frozen_calendar_days_on_dateline_killed(uc):
    assert ask(uc, dateline(uc), ("share", "d2"), "M31") == "100"
    assert ask(uc, ship_dateline(uc), ("amt", "mie", "d2"), "M31") == "50.00"


# --- T013 (FL10): 10 of 14 occupancy days entitled, which ones not stated -------------------------------------------

def t013_3(uc):
    K = uc[0]
    case = [c for c in K.CASES if c["id"] == "T013"][0]
    sub = [s for s in case["subs"] if s["questions"][0]["qid"] == "T013-3"][0]
    return copy.deepcopy(sub["spec"])   # the guard adds a fact: never to the module's own spec


def test_t013_unstated_entitled_night_refused(uc):
    """T013-3 as encoded (cases.py): lodging for the night of 2 February when 10 of 14 occupancy days carried lodging
    entitlement and which ones is not stated: refused. Frozen: $120.00 (the night taken as entitled)."""
    assert ask(uc, t013_3(uc), ("amt", "lo", "n2")) == "OPEN"


def entitled_t013_3(uc):
    """T013-3's night stated to be an entitled day (fact ltent, added by the fix; frozen: the night is taken as entitled)."""
    s = t013_3(uc)
    if "ltent" in uc[4].FACTS:
        s.fact("ltent", "n2", True)
    return s


def test_t013_guard_stated_entitled_night(uc):
    """The same night stated to be one of the entitled days: min(daily rate $200, lodging rate $120) = $120.00."""
    assert ask(uc, entitled_t013_3(uc), ("amt", "lo", "n2")) == "120.00"


def test_m10_lodging_cap_killed_on_entitled_long_term_night(uc):
    """M10 (the lodging-rate cap dropped) changes no question-set answer once T013-3 is refused; here it gives $200.00."""
    assert ask(uc, entitled_t013_3(uc), ("amt", "lo", "n2"), "M10") == "200.00"


def test_m32_frozen_night_entitlement_default_killed(uc):
    assert ask(uc, t013_3(uc), ("amt", "lo", "n2"), "M32") == "120.00"
