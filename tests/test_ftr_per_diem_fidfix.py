"""FTR per diem (usecases/ftr_per_diem/translation.py): the fidelity sweep's six fix rows, one named test each (rows
statute-latent-ftr-per-diem-U8, -U20, -U24, -U27, -U33, -T013; manage-agents
reviews/spare/statute-corpus/fidelity-check/sweep/ftr-per-diem.md flags FL01, FL03, FL05, FL06, FL07, FL10).

Each row test is the check seat's test, answered by the text's own runner (run.py run_sub: the staged prover; the
question-set run replays every certificate in Lean). Each FAILS on the frozen commit 24d490f718 and on after-release
merged into it (the frozen answer is in the test's docstring), and passes on the fix. Each fix has a planted error
(translation.MUTANTS M27-M32) restoring the frozen rule; the mutant tests show the row test's answer goes back to the
frozen one under it. The guards pin the answers the fix must keep.
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

def rv_night(uc, rows):
    _, _, kit, _, _ = uc
    s = kit.night(frame(uc), "n1", "2027-02-01", ltype="rv", tax="0.00", arrive=("2027-02-01", "16:00"))
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


def test_u24_longterm_cap_is_full_daily_per_diem(uc):
    """T014's facts: lodging $120, M&IE $80, furnished rent $2400 for 10 entitled days: 240 capped at the $200 daily
    per diem rate -> $200.00; T013's $2000 / 10 = 200 -> $200.00. Frozen: $120.00 both (lodging rate only)."""
    assert ask(uc, longterm(uc, [("ka", "2400.00", lx(frent=True))]), ("amt", "dlr", "lt")) == "200.00"
    assert ask(uc, longterm(uc, [("ka", "2000.00", lx(frent=True))]), ("amt", "dlr", "lt")) == "200.00"


def test_u24_guard_under_lodging_rate(uc):
    """$1200 / 10 = 120 at a $140 lodging rate: $120.00 (T012's shape; frozen and fix)."""
    assert ask(uc, longterm(uc, [("ka", "1200.00", lx(frent=True))], lr="140.00", mr="68.00"),
               ("amt", "dlr", "lt")) == "120.00"


def test_m29_frozen_lodging_rate_cap_killed(uc):
    assert ask(uc, longterm(uc, [("ka", "2400.00", lx(frent=True))]), ("amt", "dlr", "lt"), "M29") == "120.00"


# --- U27 (FL06): "(b) Costs of connecting, disconnecting, and using utilities;" -----------------------------------------

UTIL_INST = [("ka", "1000.00", lx(frent=True)), ("kb", "50.00", lx(util=True, inst=True))]


def test_u27_utility_installation_not_excluded(uc):
    """A $50 charge for connecting electricity that the case calls the utility's installation fee (util and inst):
    unit 27 includes connecting utilities with no installation carve-out (that carve-out is units 29-30's, for the
    telephone and internet fees), so no definite 'not part of the lodging cost': refused. Frozen: no."""
    assert ask(uc, longterm(uc, UTIL_INST), ("yn", "allow", "kb")) == "OPEN"


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

def dateline(uc, idl=True):
    _, _, kit, _, _ = uc
    s = frame(uc, dep=("2027-02-03", "22:00"), ret=("2027-02-05", "02:00"), zoned=(540, 540), idl=idl, mr="80.00")
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


def test_u33_guard_same_trip_without_dateline(uc):
    """The same clock times with idl stated false keep the calendar-day shares: 100 percent / $80.00 for 4 Feb."""
    s = dateline(uc, idl=False)
    assert ask(uc, s, ("share", "d2")) == "100"
    assert ask(uc, s, ("amt", "mie", "d2")) == "80.00"
    assert ask(uc, s, ("yn", "ge24", "t")) == "yes"


def test_m31_frozen_calendar_days_on_dateline_killed(uc):
    assert ask(uc, dateline(uc), ("share", "d2"), "M31") == "100"


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


def test_t013_guard_stated_entitled_night(uc):
    """The same night stated to be one of the entitled days: min(daily rate $200, lodging rate $120) = $120.00."""
    s = t013_3(uc)
    s.fact("ltent", "n2", True)
    assert ask(uc, s, ("amt", "lo", "n2")) == "120.00"


def test_m32_frozen_night_entitlement_default_killed(uc):
    assert ask(uc, t013_3(uc), ("amt", "lo", "n2"), "M32") == "120.00"
