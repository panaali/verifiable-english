"""Council tax, LGFA 1992 (usecases/council_tax): the latent departures the fidelity sweep found, as named unit tests run
with the text's own runner (rows statute-latent-council-tax-I11, -I12, -I33; manage-agents
reviews/spare/statute-corpus/fidelity-check/sweep/council-tax.md FL01, FL02, FL05; record: sweep/council-tax/FIX.md).

Each test is the check seat's own case, encoded in cases.py's record shape and answered by usecases/council_tax/run.py
run_case (the staged prover over translation.py and encode.py; the question-set run also replays every certificate in
Lean). The check seats never saw run.py, so each row test was first run on the frozen rules (2572735f63) and on the
merge with after-release.

* I11 FL01 (s. 10(1), A / D): with A = 1,500.00 and D = 365 no whole-penny day's amount exists. The check seat said
  the premises then have no model and any amount could be proved. The runner's sentinel step (a value no consistent
  premise set proves) already marks such premises inconsistent and refuses the amount, so this row closes harmless if
  the test passes on the frozen rules.
* I12 FL02 (s. 11(5), Sch. 1): Or(dis1, dis2, dis3, dis4, dis6, dis7) decided "not disregarded" for everyone else, so a
  person disregarded only under para. 8, 9, 10 or 11 (or an order) got a definite discount. Now the paragraphs written
  only imply "disregarded"; "not disregarded" also needs the stated fact that no other Sch. 1 paragraph and no order
  applies to the person on the day (sch1_closed). Unstated: refused.
* I33 FL05 (Sch. 1 para. 7(2), "independent hospital", England): the exclusion is "a health service hospital as defined
  by that section" (s. 275 NHS Act 2006 only), not the three-Act fact of para. 6(2)(a). New fact inst_s275_hs; unstated
  where it matters: refused.
* The fidelity step on the changed units (sweep/council-tax/fix/FIDELITY.md) flagged two more of the same kind, on
  frozen behaviour: step FL01 on I12 (s. 10(1) "subject to sections 11 to 13A": the amount payable was fixed as if no
  premium or reduction could apply) and step FL02 on I15 (s. 11(2) "subject to sections 11A, 11B and 11C"). Both now
  need the stated open fact adj_none (no provision of ss. 11A-13A and nothing else changes the amount on the day).
  Unstated: the amount, and a s. 11(2) discount, are refused. Its one re-read flagged FL03 (I12) and FL04 (I15): s. 11(1)
  and (2) are about "any chargeable dwelling in England", which no rule checked. Both now need the stated open fact
  eng_chargeable (unstated: the discount is refused).

On the frozen code the vocabulary the fix adds (sch1_closed, inst_s275_hs, adj_none, the record key "open") does not
exist; the helper drops what the vocabulary in use lacks, so a frozen run of a row test fails by behaviour, not by a missing
name (the mutant tests fail there with KeyError: M8-M11 do not exist on the frozen code).
M8-M11 restore the frozen rules and are killed here: each gives the frozen answer again. Guard tests pass on both.

Set COUNCIL_FIDFIX_UC to run these tests against another copy of usecases/council_tax (the frozen one).
"""
import os
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(os.environ.get("COUNCIL_FIDFIX_UC") or Path(__file__).resolve().parents[1] / "usecases" / "council_tax")
RES = ["resident"]


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import encode as E
        import run as RUN
        import translation as T
        yield T, E, RUN


def case(cid, persons, pd, *, band="C", amt=None, amtd=None, day="2025-06-10", closed=True, adj=True,
         eng=True, open_facts=None):
    """One dwelling, one day d1 in 2025-26 (365 days); questions Q2 (discount) and Q3 (amount) for d1."""
    ints = {"days_y1": "365", "date_d1": day}
    if amt:
        ints["amt_y1"] = amt
    if amtd:
        ints["amtd_y1"] = amtd
    rec = {"id": cid, "dwelling": "w", "days": ["d1"], "persons": persons, "years": ["y1"], "in_year": [("d1", "y1")],
           "facts": {"w": [f"list_{band.lower()}"]}, "pd": {f"{p}@d1": list(fs) for p, fs in pd.items()},
           "ints": ints, "questions": [{"qid": "Q2", "item": "d1", "form": "discount"},
                                       {"qid": "Q3", "item": "d1", "form": "amount"}], "judgement": []}
    if closed:
        rec["sch1_closed"] = True
    if adj:
        rec["adj_none"] = True
    if eng:
        rec["eng_chargeable"] = True
    if open_facts:
        rec["open"] = open_facts
    return rec


def known(T, c):
    """The record with only the vocabulary the rules in use have (the frozen rules lack the fix's names)."""
    binary = set(T.BINARY)
    return dict(c, pd={k: [f for f in v if f in binary] for k, v in c["pd"].items()})


def answers(uc, c, mutant=None):
    T, _E, RUN = uc
    got = RUN.run_case(known(T, c), mutant)[0]
    return {q: (a["answer"] if a["answer"] != "AMOUNT" else a["gbp"]) for q, a in got.items()}


# --- I11 FL01: s. 10(1) A / D with no whole-penny day's amount --------------------------------------------------
def test_i11_fl01_amount_not_divisible_by_days_no_wrong_amount(uc):
    # Band C; A = 1,500.00 for band C for 2025-26 (365 days); one resident, not disregarded; Q3 for 10 June 2025.
    # Source: 1500 / 365 x 0.75 = 3.0821..., GBP 3.08 under the case's stated "nearest penny, half up". The translation
    # has no rounding rule, so it refuses (lost coverage, not a wrong answer): no whole-penny base candidate exists.
    got = answers(uc, case("T-FL01", ["ann"], {"ann": RES}, amt="1500.00"))
    assert got["Q2"] == "25", got
    assert got["Q3"] == "OPEN", got   # refused: the runner proves no amount from premises with no whole-penny model


def test_i11_fl01_spurious_candidate_from_other_year_length_refused(uc):
    # A = 1,464.00 with D = 365: the D = 366 branch offers 4.00 as a base candidate, which the stated D = 365 must
    # refuse (1464 / 365 is not a whole number of pence); the sentinel step marks such premises inconsistent.
    got = answers(uc, case("T-FL01-b", ["ann"], {"ann": RES}, amt="1464.00"))
    assert got["Q3"] == "OPEN", got


def test_guard_fl01_amount_divisible_by_days(uc):
    got = answers(uc, case("T-FL01-g", ["ann"], {"ann": RES}, amt="1460.00"))
    assert got == {"Q2": "25", "Q3": "3.00"}, got


# --- I12 FL02: s. 11(5) closes over every Sch. 1 paragraph, not only 1-4, 6, 7 -------------------------------------
def test_i12_fl02_night_shelter_resident_not_stated_closed_refused(uc):
    # Ann is the only resident; her sole or main residence is the dwelling, a night shelter meeting para. 10(2). The
    # facts do not say that no paragraph other than 1-4, 6, 7 applies (para. 10 does). Source: Ann disregarded under
    # para. 10, so 50 (s. 11(2)(b)); the brief expects NOT SUPPORTED. Frozen: 25 (s. 11(1)(a)).
    got = answers(uc, case("T-FL02", ["ann"], {"ann": RES}, amt="1460.00", closed=False))
    assert got == {"Q2": "OPEN", "Q3": "OPEN"}, got


def test_i12_fl02_two_residents_one_not_stated_closed_refused(uc):
    # Ann and Ben resident; Ben a student meeting para. 4 (disregarded); nothing stated about Ann's other paragraphs.
    got = answers(uc, case("T-FL02-b", ["ann", "ben"], {"ann": RES, "ben": RES + ["student", "cond4b"]},
                           amt="1460.00", closed=False))
    assert got["Q2"] == "OPEN", got   # frozen: 25 (s. 11(1)(b))


def test_guard_fl02_closed_world_stated_one_resident(uc):
    got = answers(uc, case("T-FL02-g", ["ann"], {"ann": RES}, amt="1460.00"))
    assert got == {"Q2": "25", "Q3": "3.00"}, got


def test_guard_fl02_disregarded_paragraph_written_needs_no_closure(uc):
    # Ben a student meeting para. 4 is disregarded whatever else applies; he is the only resident: 50 (s. 11(2)(b)).
    got = answers(uc, case("T-FL02-g2", ["ben"], {"ben": RES + ["student", "cond4b"]}, amt="1460.00", closed=False))
    assert got == {"Q2": "50", "Q3": "2.00"}, got


# --- I33 FL05: para. 7(2) independent hospital, England: "not a health service hospital as defined by that section" -
DEE = RES + ["smr_inst", "receiving_care", "inst_england", "inst_s275_hospital", "inst_hs_hospital"]


def test_i33_fl05_s275_hospital_hs_only_under_welsh_act_disregarded(uc):
    # Dee is the sole resident; her sole or main residence is a hospital in England, a hospital as defined by s. 275
    # NHS Act 2006 and a health service hospital within the NHS (Wales) Act 2006 but not as defined by s. 275; she
    # receives care there and is not a patient. Source: independent hospital, para. 7 disregards her: 50. Frozen: 25.
    got = answers(uc, case("T-FL05", ["dee"], {"dee": DEE}, band="D", amtd="1971.00", open_facts={"dee@d1": {"inst_s275_hs": False}}))
    assert got == {"Q2": "50", "Q3": "2.70"}, got


def test_i33_fl05_s275_hs_unstated_refused(uc):
    got = answers(uc, case("T-FL05-u", ["dee"], {"dee": DEE}, band="D", amtd="1971.00"))
    assert got["Q2"] == "OPEN", got   # frozen: 25


def test_guard_fl05_s275_health_service_hospital_not_independent(uc):
    got = answers(uc, case("T-FL05-g", ["dee"], {"dee": DEE}, band="D", amtd="1971.00", open_facts={"dee@d1": {"inst_s275_hs": True}}))
    assert got == {"Q2": "25", "Q3": "4.05"}, got


# --- mutants restoring the frozen rules -----------------------------------------------------------------------------
def test_m8_frozen_disregarded_biconditional_killed(uc):
    got = answers(uc, case("T-FL02", ["ann"], {"ann": RES}, amt="1460.00", closed=False), mutant="M8")
    assert got == {"Q2": "25", "Q3": "3.00"}, got


def test_m9_frozen_independent_hospital_exclusion_killed(uc):
    got = answers(uc, case("T-FL05", ["dee"], {"dee": DEE}, band="D", amtd="1971.00", open_facts={"dee@d1": {"inst_s275_hs": False}}),
                  mutant="M9")
    assert got == {"Q2": "25", "Q3": "4.05"}, got


# --- fidelity step on the changed units: FL01 (I12, s. 10(1) "subject to ss. 11 to 13A"), FL02 (I15, s. 11(2)) ------
def test_i12_step_fl01_no_adjustment_unstated_amount_refused(uc):
    # One resident, not disregarded (closure stated); nothing said about premiums, reductions or local schemes.
    got = answers(uc, case("T-SFL01", ["ann"], {"ann": RES}, amt="1460.00", adj=False))
    assert got == {"Q2": "25", "Q3": "OPEN"}, got   # frozen: Q3 3.00


def test_i15_step_fl02_s11_2_qualifier_unstated_refused(uc):
    # Nobody is a resident on the day; nothing said about ss. 11A-11C.
    got = answers(uc, case("T-SFL02", ["ann"], {}, amt="1460.00", adj=False))
    assert got == {"Q2": "OPEN", "Q3": "OPEN"}, got   # frozen: 50, 2.00


def test_guard_step_fl02_no_resident_adjustment_none_stated(uc):
    got = answers(uc, case("T-SFL02-g", ["ann"], {}, amt="1460.00"))
    assert got == {"Q2": "50", "Q3": "2.00"}, got


def test_m10_frozen_amount_without_qualifier_killed(uc):
    got = answers(uc, case("T-SFL01", ["ann"], {"ann": RES}, amt="1460.00", adj=False), mutant="M10")
    assert got == {"Q2": "25", "Q3": "3.00"}, got


def test_m11_frozen_s11_2_without_qualifier_killed(uc):
    got = answers(uc, case("T-SFL02", ["ann"], {}, amt="1460.00", adj=False), mutant="M11")
    assert got["Q2"] == "50", got


def test_open_fact_stated_both_ways_is_an_encoding_error(uc):
    c = case("T-ENC1", ["ann"], {"ann": RES}, amt="1460.00", open_facts={"ann@d1": {"sch1_closed": False}})
    with pytest.raises(ValueError, match="both true and false"):
        answers(uc, c)


def test_s275_health_service_hospital_needs_three_act_fact_listed(uc):
    c = case("T-ENC2", ["dee"], {"dee": DEE[:-1]}, band="D", amtd="1971.00", open_facts={"dee@d1": {"inst_s275_hs": True}})
    with pytest.raises(ValueError, match="without inst_hs_hospital"):
        answers(uc, c)


# --- the step's re-read: FL03 (I12, s. 11(1)), FL04 (I15, s. 11(2)): "any chargeable dwelling in England" -----------
def test_i12_reread_fl03_dwelling_england_unstated_refused(uc):
    got = answers(uc, case("T-RFL03", ["ann"], {"ann": RES}, amt="1460.00", eng=False))
    assert got == {"Q2": "OPEN", "Q3": "OPEN"}, got   # frozen: 25, 3.00


def test_i15_reread_fl04_dwelling_england_unstated_refused(uc):
    got = answers(uc, case("T-RFL04", ["ann"], {}, amt="1460.00", eng=False))
    assert got == {"Q2": "OPEN", "Q3": "OPEN"}, got   # frozen: 50, 2.00


def test_m11_frozen_unit_13_without_england_killed(uc):
    # M11 (unit 13 as frozen) gives the frozen 50 back; M10 (unit 12 as frozen) is killed by test_m10 above (with
    # eng_chargeable unstated, unit 13's own gate still leaves Q2 open under M10).
    got = answers(uc, case("T-RFL04", ["ann"], {}, amt="1460.00", eng=False), mutant="M11")
    assert got["Q2"] == "50", got
