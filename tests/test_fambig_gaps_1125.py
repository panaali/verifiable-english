"""Source-fidelity gaps of feature C's reading tables, found by the gate-3 source check of the feature-ambig build
(manage-agents reviews/spare/statute-corpus/feature-ambig/build/seats/src-*-out.txt, finding 1 of each law).

* PAWHP (row fambig-pawhp-16b4): SSI 2024/351 reg. 16B(4) "the Scottish Ministers may treat an application received after
  the date in paragraph (2) as made by that date where they consider that the individual has a good reason" was not
  encoded: row 63 wrote 16B(2) alone. Under the table's reading B of block B1 row 63 also decides entitlement.
* UC award (row fambig-uc-b2-party): reading B of block B2 gave the reg. 3(4) single-claim route to either member of
  the disregarded pair, though reg. 3(4) gives it to "the person who is not a party to the earlier marriage".
* Tenant Fees (row fambig-tf-b2-breach): the law is on its own branch (fambig-gaps-tf-1125, usecases/tenant_fees,
  test_default_breach.py runs the law); here only the table's edit is pinned.

Each answer is derived by the use case's own staged prover (the same prover its run.py uses before the Lean replay).
Fails on after-release 9babe6639e (no 16B(4) fact or rule; no not_earlier_party atom; the old table edits).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope
from usecases import reading_runs as rr

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "usecases" / "reading_tables"


def reading_edits(law, block, reading):
    cfg, blocks = rr.load_table(TABLES / f"{law}.tsv")
    edits = blocks[block][reading]["edits"]
    return cfg, json.loads(edits) if isinstance(edits, str) else edits


def under(T, cfg, edits, label="~test-reading"):
    """Register a reading's edits as the law's MUTANTS key (as reading_runs.Law does); returns the key."""
    T.MUTANTS[label] = ("reading table edits", rr.transform(edits, cfg["slot"]))
    return label


# ---- PAWHP reg. 16B(4) ------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def pawhp():
    with usecase_scope(ROOT / "usecases" / "pawhp"):
        import cases as K
        import run as RUN
        import translation as T
        from ve.environment import Environment
        yield K, RUN, T, RUN.Prover(Environment(T.environment()))
        T.MUTANTS.pop("~test-reading", None)


def late_p004(K, treated):
    """P004 (block B1's case): Callum's application received 2 April 2027, after the 31 March limit; the Ministers'
    16B(4) decision as given (P004 itself states none)."""
    case = copy.deepcopy(next(c for c in K.CASES if c["id"] == "P004"))
    assert case["people"][0]["received"] == "2027-04-02"
    if treated:
        case["people"][0]["late_treated_in_time"] = True
    return case


def test_pawhp_16b4_a_late_application_treated_as_in_time_is_in_time(pawhp):
    K, RUN, T, prover = pawhp
    assert RUN.run_case(prover, late_p004(K, False))[0]["Q3"] == "NO"
    assert RUN.run_case(prover, late_p004(K, True))[0]["Q3"] == "YES"


def test_pawhp_16b4_reaches_entitlement_under_reading_b_of_b1(pawhp):
    """Reading B (the 31 March limit is a condition of entitlement): a late application the Ministers treat as made in
    time no longer defeats entitlement; without that decision it still does."""
    K, RUN, T, prover = pawhp
    cfg, edits = reading_edits("pawhp", "B1", "B")
    key = under(T, cfg, edits)
    assert RUN.run_case(prover, late_p004(K, False))[0]["Q1"] == "YES"  # reading A: the limit adds no condition
    assert RUN.run_case(prover, late_p004(K, False), key)[0]["Q1"] == "NO"
    assert RUN.run_case(prover, late_p004(K, True), key)[0]["Q1"] == "YES"


def test_pawhp_16b4_is_written_in_row_63_and_the_planted_error_m3_still_applies(pawhp):
    K, RUN, T, prover = pawhp
    r63 = [r for r in T.rules(["applicant"]) if r["row"] == 63]
    assert len(r63) == 1 and '"late_treated_in_time"' in json.dumps(r63[0]["formula"])
    m3 = [r for r in T.rules(["applicant"], (), "M3") if r["row"] == 63]
    assert '"date_before"' in json.dumps(m3[0]["formula"]) and '"late_treated_in_time"' in json.dumps(m3[0]["formula"])
    assert "late_treated_in_time" in T.environment()["vocabulary"]["predicates"]


# ---- UC award reg. 3(4) "the person who is not a party to the earlier marriage" ---------------------------------------

@pytest.fixture(scope="module")
def uc():
    with usecase_scope(ROOT / "usecases" / "uc_award"):
        import cases as K
        import run as R
        import translation as T
        yield K, R, T
        T.MUTANTS.pop("~test-reading", None)
        T.MUTANTS.pop("~test-old", None)


def hamid_single(K):
    """U023h (Hamid married to Wafa, earlier, and to Zara under a law permitting polygamy, all in one household) with
    s. 115 applying to Wafa: Hamid, a member of the couple with Wafa, claims as a single person (reg. 3(3)(e)), and
    Hamid IS the party to the earlier marriage, so reg. 3(4) gives him no single-claim route with Zara."""
    case = copy.deepcopy(next(c for c in K.CASES if c["id"] == "U023h"))
    case["facts"]["wafa"] = case["facts"].get("wafa", []) + ["s115"]
    return case


OLD_B2_ROUTE = ["and", ["binary", "poly_dis", "?a", "?b"], ["unary", "single_claim", "?a"]]


def test_uc_reading_b_single_claim_route_is_only_for_the_non_party(uc):
    K, R, T = uc
    cfg, edits = reading_edits("uc-award", "B2", "B")
    old = copy.deepcopy(edits)
    for e in old:  # the edits of table b0781531de (source-checked 2026-11-24): no not_earlier_party condition
        e["new"][2] = OLD_B2_ROUTE
    case = hamid_single(K)
    a, _, sa, *_ = R.run_case(case)
    b, _, sb, *_ = R.run_case(case, under(T, cfg, edits))
    o, _, so, *_ = R.run_case(case, under(T, cfg, old, "~test-old"))
    zara = T.U("inc_counted", "zara")
    assert sa.truth(T.B("poly_dis", "hamid", "zara")) is True
    assert sb.truth(T.B("not_earlier_party", "hamid", "zara")) is False
    assert sa.truth(zara) is False and sb.truth(zara) is False
    assert so.truth(zara) is True  # the gap: Zara's income joined to Hamid's single claim
    assert b == a and o != a


def test_uc_not_earlier_party_for_the_anchor_pairs_of_u023(uc):
    K, R, T = uc
    z = next(c for c in K.CASES if c["id"] == "U023z")
    cfg, edits = reading_edits("uc-award", "B2", "B")
    _, _, s, *_ = R.run_case(z, under(T, cfg, edits))
    assert s.truth(T.B("not_earlier_party", "zara", "hamid")) is True
    assert s.truth(T.U("inc_counted", "hamid")) is True  # U023-5 reading B (94.90): unchanged by the fix
    assert "not_earlier_party" in T.environment(R.make_ctx(z))["vocabulary"]["predicates"]


# ---- Tenant Fees para. 5 "for breach of a tenancy agreement" (the law runs on branch fambig-gaps-tf-1125) --------------

def test_tenant_fees_reading_b_para5_route_needs_a_breach():
    """The exact edit: para. 5's route for a sum the agreement fixes on a default is a CONJUNCTION with default_breach
    (an extra disjunct would let a default that breaches nothing through again). The same route is run on the law in
    usecases/tenant_fees/test_default_breach.py (branch fambig-gaps-tf-1125)."""
    _, edits = reading_edits("tenant-fees", "B2", "B")
    U = lambda p: ["unary", p, "?x"]  # noqa: E731
    route = ["and", U("default_payment"), ["and", U("ta_requires"), ["and", U("default_breach"),
                                                                      ["not", U("relevant_default")]]]]
    assert edits == [{"op": "replace", "row": 30, "old": U("damages"), "new": ["or", U("damages"), route]}]
