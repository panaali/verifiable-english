"""Vehicle excise duty, VERA 1994 Sch 1 Part 1AA (usecases/ved_first_year): the 1GA(1A) motor-caravan exclusion
(row statute-latent-ved-first-year-I1, covering latent departures I1 and I2; manage-agents
reviews/spare/statute-corpus/fidelity-check/LATENT-DEPARTURES.md sections 8-9; branch latent-ved-1125).

Source, 1GA(1A): "But this Part of this Schedule does not apply to a motor caravan which is first registered, under this
Act or under the law of a country or territory outside the United Kingdom, on or after 12 March 2020." (2A): a vehicle is a
"motor caravan" if the certificate mentioned in (1)(b) identifies it as one. 1GA(1B)(c) ("this Part would apply ... if the
condition in (1)(b)(ii) were met") is read with (1A).

The frozen build (3c170c4048, translation 29e5829ae3) did not write (1A) (reading R2) and had no motor-caravan fact, so a
motor caravan registered after 12 March 2020 whose certificate also identifies it as a light passenger vehicle got a Part
1AA rate (I1), and a zero-emission one with no figure on its certificate was deemed to 0 g/km and rated (I2). These tests
pin the fix (translation R7, unit 42; encode.py C6):
* a stated motor caravan first registered on or after 12 March 2020 -> "this Part does not apply", no rate (Q1, Q2) and
  1GE(2) does not apply (Q3);
* the same vehicle with the motor-caravan fact UNKNOWN -> refused (OPEN), never a rate;
* a motor caravan first registered before 12 March 2020 (and from 1 April 2017) is still rated: (1A) does not reach it;
* planted error M14 (the frozen 1GA(1) / 1GA(1B) rules, unit 42 removed) gives the frozen rates again (killed here);
* the frozen encoder sets' motor-caravan fact comes only from the fresh encoder record (latent-enc/mcaravan.json): every
  frozen case is found there, and an edited frozen case falls out (unknown).
On the frozen vocabulary the fact cannot be stated (translation.V_FACTS has no "mcaravan"): `veh` then leaves it out, which
is how the frozen encoder had to encode such a vehicle, so the behaviour tests fail on 3c170c4048 by BEHAVIOUR (a rate);
the M14 and record tests fail there because M14 and the record do not exist. Each answer comes from the use case's own
staged prover (run.run_case; the Lean checker proves each step); the full run replays every certificate in Lean.
"""
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(__file__).resolve().parents[1] / "usecases" / "ved_first_year"


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import encode as E
        import run as R
        import translation as T
        yield E, R, T


def veh(T, facts, dreg, co2=None, lp="30000.00", mc=True, unknown=False, licences=()):
    """One vehicle v1; mc: the certificate identifies it as a motor caravan; unknown: that fact left unknown (C6)."""
    facts = list(facts)
    can = "mcaravan" in T.V_FACTS  # False on the frozen vocabulary: the fact is then simply not stated
    if mc and can and not unknown:
        facts.append("mcaravan")
    ints = {"dreg": dreg, "lp": lp}
    if co2 is not None:
        ints["co2"] = co2
    v = {"id": "v1", "facts": facts + ["has_lp"], "ints": ints, "accessories": [],
         "licences": [{"id": f"v1l{i}", "date": d} for i, d in enumerate(licences, 1)]}
    if unknown and can:
        v["unknown"] = ["mcaravan"]
    return v


def ask(uc, vehicle, cid="T1", mutant=None):
    _, R, _ = uc
    qs = [{"qid": f"{cid}-1", "item": "v1", "vehicle": "v1", "form": "rate1"}]
    for lic in vehicle["licences"]:
        qs += [{"qid": f"{cid}-{lic['id']}-rate2", "item": lic["id"], "vehicle": "v1", "form": "rate2"},
               {"qid": f"{cid}-{lic['id']}-ge2", "item": lic["id"], "vehicle": "v1", "form": "ge2"}]
    case = {"id": cid, "vehicles": [vehicle], "questions": qs, "judgement": []}
    return R.run_case(case, mutant)[0]


M1_COC = ["basis_coc", "cert_lpv", "cert_co2"]  # EU certificate of conformity, identifies it as a light passenger vehicle
ZERO_UKAC = ["basis_ukac", "cert_lpv", "zero_rate"]  # UK approval certificate, no CO2 figure, zero emissions


def test_m1_certificate_motor_caravan_registered_2025_04_01_at_100_gkm_gets_no_rate(uc):
    """I1: the row's test. Frozen: GBP 365 (Table 1 row 5)."""
    _, _, T = uc
    a = ask(uc, veh(T, M1_COC, "2025-04-01", co2="100"))
    assert a["T1-1"] == {"answer": "NOT_APPLY"}


def test_zero_emission_motor_caravan_with_no_figure_is_not_deemed_and_gets_no_rate(uc):
    """I2: 1GA(1B)(c) read with (1A): no 1GA(1C) deeming, no rate. Frozen: GBP 10 (deemed 0 g/km, Table 1 row 1)."""
    _, _, T = uc
    a = ask(uc, veh(T, ZERO_UKAC, "2025-04-01", lp="60000.00"))
    assert a["T1-1"] == {"answer": "NOT_APPLY"}


def test_motor_caravan_other_licence_no_rate_and_1ge2_does_not_apply(uc, monkeypatch):
    """Q2 / Q3 for the I1 vehicle at GBP 45,000 (over GBP 40,000), licence one year on (the bridge's whole years given
    here as 1 year 0 days): no GBP 640 / 200 and 1GE(2) does not apply. Frozen: GBP 640 and yes."""
    E, _, T = uc
    monkeypatch.setattr(E, "bridges", lambda: {("T1", "v1l1"): (1, 0)})
    a = ask(uc, veh(T, M1_COC, "2025-04-01", co2="100", lp="45000.00", licences=["2026-04-01"]))
    assert a["T1-v1l1-rate2"] == {"answer": "NOT_APPLY"}
    assert a["T1-v1l1-ge2"] == {"answer": "no"}


def test_motor_caravan_fact_unknown_registered_after_12_march_2020_is_refused(uc):
    """C6: the facts leave the motor-caravan fact unknown -> refused (OPEN), never a rate. Frozen: GBP 365 / GBP 10."""
    _, _, T = uc
    assert ask(uc, veh(T, M1_COC, "2025-04-01", co2="100", unknown=True))["T1-1"] == {"answer": "OPEN"}
    assert ask(uc, veh(T, ZERO_UKAC, "2025-04-01", unknown=True))["T1-1"] == {"answer": "OPEN"}


def test_motor_caravan_registered_before_12_march_2020_is_still_rated(uc):
    """(1A) reaches only first registration on or after 12 March 2020: 11 March 2020 -> GBP 365, known or unknown."""
    _, _, T = uc
    assert ask(uc, veh(T, M1_COC, "2020-03-11", co2="100"))["T1-1"] == {"answer": "AMOUNT", "gbp": "365.00"}
    assert ask(uc, veh(T, M1_COC, "2020-03-11", co2="100", unknown=True))["T1-1"] == {"answer": "AMOUNT",
                                                                                       "gbp": "365.00"}
    assert ask(uc, veh(T, M1_COC, "2020-03-12", co2="100"))["T1-1"] == {"answer": "NOT_APPLY"}


def test_not_a_motor_caravan_is_rated_as_before(uc):
    _, _, T = uc
    assert ask(uc, veh(T, M1_COC, "2025-04-01", co2="100", mc=False))["T1-1"] == {"answer": "AMOUNT", "gbp": "365.00"}
    assert ask(uc, veh(T, ZERO_UKAC, "2025-04-01", lp="60000.00", mc=False))["T1-1"] == {"answer": "AMOUNT",
                                                                                         "gbp": "10.00"}


def test_planted_error_m14_restores_the_frozen_rule_and_is_killed(uc):
    """M14 = the frozen 1GA(1), 1GA(1B) (3c170c4048): the motor caravans get the frozen rates again."""
    _, _, T = uc
    assert "M14" in T.MUTANTS
    assert ask(uc, veh(T, M1_COC, "2025-04-01", co2="100"), mutant="M14")["T1-1"] == {"answer": "AMOUNT",
                                                                                     "gbp": "365.00"}
    assert ask(uc, veh(T, ZERO_UKAC, "2025-04-01", lp="60000.00"), mutant="M14")["T1-1"] == {"answer": "AMOUNT",
                                                                                            "gbp": "10.00"}


def test_m14_rules_equal_the_frozen_rules_for_units_1_and_2(uc):
    """M14's units 1 and 2 are the frozen formulas exactly (no Not(mc_excl)); unit 42 is gone."""
    _, _, T = uc
    ctx = T.Ctx([{"id": "v1", "accessories": [], "licences": []}])
    got = {(r["unit"], T.key(r["formula"])) for r in T.rules(ctx, "M14") if r["unit"] in (1, 2, 42)}
    x = "v1"
    frozen = [(1, T.Iff(T.U("reg17", x), T.Le(T.date("2017-04-01"), T.k("dreg", x)))),
              (1, T.Iff(T.U("basis", x), T.Or(T.U("basis_coc", x), T.U("basis_ukac", x)))),
              (1, T.Iff(T.U("applies", x), T.And(T.U("reg17", x), T.U("basis", x), T.U("cert_lpv", x),
                                                 T.U("spec_co2", x)))),
              (2, T.Iff(T.U("would_apply", x), T.And(T.U("reg17", x), T.U("basis", x), T.U("cert_lpv", x)))),
              (2, T.Iff(T.U("deem1c", x), T.And(T.U("zero_rate", x), T.Not(T.U("cert_co2", x)),
                                                T.U("would_apply", x))))]
    assert got == {(n, T.key(f)) for n, f in frozen}
    fixed = {r["unit"] for r in T.rules(ctx)}
    assert 42 in fixed


def test_frozen_encoder_cases_take_the_motor_caravan_fact_from_the_record_only(uc):
    """Every case of both frozen encoder files is in latent-enc/mcaravan.json (here: all stated false, none unknown);
    an edited frozen case is not, so its motor-caravan fact is unknown (no fact either way)."""
    E, _, _ = uc
    import importlib
    import sys
    sys.path.insert(0, str(UC / "xfam"))
    try:
        ka = importlib.import_module("cases")
        kb = importlib.import_module("cases_xfam")
        cases = ka.CASES + kb.CASES
    finally:
        sys.path.remove(str(UC / "xfam"))
        sys.modules.pop("cases_xfam", None)
    n = 0
    for case in cases:
        assert E.frozen_case(case)
        facts = {f["id"]: f["formula"] for f in E.facts(case)}
        for v in case["vehicles"]:
            assert facts[f"{v['id']}.mcaravan"] == ["not", ["unary", "mcaravan", ["const", v["id"]]]]
            n += 1
    assert n == 108
    edited = {**ka.CASES[0], "vehicles": [{**ka.CASES[0]["vehicles"][0], "ints": {**ka.CASES[0]["vehicles"][0]["ints"],
                                                                                 "dreg": "2025-04-02"}}]}
    assert not any(f["id"] == "v1.mcaravan" for f in E.facts(edited))
    with pytest.raises(ValueError):
        E.facts({**ka.CASES[0], "vehicles": [{**ka.CASES[0]["vehicles"][0],
                                              "facts": ka.CASES[0]["vehicles"][0]["facts"] + ["mcaravan"]}]})
