"""HMO licensing England (usecases/hmo): five latent departures found by the fidelity sweep, fixed in the rules (rows
statute-latent-hmo-I11, -I14, -I30, -I32, -I42; manage-agents reviews/spare/statute-corpus/fidelity-check/sweep/hmo.md
FL01-FL07). Each row test is the check seat's own test, run with the text's own runner (usecases/hmo/run.py run_case: the
staged prover over usecases/hmo/translation.py, rows.py and encode.py; the question-set run replays every certificate in
Lean).

* I11 FL01 / I14 FL02 (one cause: s.254(2)(e), (4)(f) "rents are payable or other consideration is to be provided"):
  rent_one and rent_one_n counted rent_payable only, which leaves out a reg. 3 worker's work. They now count consid (rule
  59): rent_payable, or work for which the person's accommodation is supplied.
* I14 FL03 (s.254(4)(e)): the converted building test read "only use" for the whole premises. It now reads only_use_n,
  the non-flat units' accommodation (J9): stated, or following from only_use of the premises (rule 60), else unknown.
* I30 FL04 (reg. 3(2)(a), (b) each "person B or such a member of person B's family"): dom_worker needed works_for and
  supplied_by of the same person. Each limb may now name B or a member of B's family living with B.
* I30 FL05 / I32 FL06 (one cause: reg. 3(1)(b) "living with him", reg. 3(4) "occupying the living accommodation with
  him"): with_family joined any occupier of the family, in any unit. It now needs the same unit (cohab, rule 61); a family
  member in another unit makes the household relation intransitive, and J7 refuses.
* I42 FL07 (Sch. 14 para 5(2) against para 6(2)): para 5 was applied to a flat in a s.257 block. No para 5 answer is now
  derived for such a flat (in_s257_block): refused.

Each row test fails on the frozen rules (37886aa1bf) and on the merge with after-release (bed3d5818a; after-release has no
usecases/hmo, so the merge leaves it unchanged). On the frozen code the vocabulary the fix adds (only_use_n,
in_s257_block, the record key "false") does not exist; the helper drops what the vocabulary in use lacks, so a frozen run
fails by behaviour, not by a missing name. M6-M11 restore the frozen rules and are killed here. The guard tests pass on
both: the fix leaves those answers as they were.

Set HMO_FIDFIX_UC to run these tests against another copy of usecases/hmo (the frozen one).
"""
import os
import sys
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(os.environ.get("HMO_FIDFIX_UC") or Path(__file__).resolve().parents[1] / "usecases" / "hmo")
ALL3 = ["toilet", "washing", "cooking"]
SCF = ["separate_set", "part_of_building", "above_below"]
NONFLAT = ["within", "created_since", "part_of_building", "above_below"]


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import encode as E
        import rows as R
        import run as RUN
        import translation as T
        yield R, T, E, RUN


def house(cid, people, *, person=None, rel=(), place=()):
    """A whole building let as one dwelling, everyone living in it as main residence and sharing the facilities."""
    return {"id": cid, "people": list(people), "places": ["premises"],
            "place": {"premises": ["within", "only_use"] + list(place)},
            "amen": {"premises": {"has": ALL3, "excl": ALL3}}, "lives": {p: "premises" for p in people},
            "all": ["main_res"], "person": person or {}, "rel": list(rel),
            "shares": {p: list(ALL3) for p in people}, "unknown": [], "judgement": []}


def units(cid, lives, unit_place, *, premises=("only_use",), person=None, rel=(), sharers=(), false=()):
    """A building of units; lives: person -> unit; the premises' facilities shared by `sharers`."""
    people = list(lives)
    return {"id": cid, "people": people, "places": ["premises"] + list(unit_place),
            "place": {"premises": list(premises), **{u: list(v) for u, v in unit_place.items()}},
            "amen": {"premises": {"has": ALL3, "excl": []},
                     **{u: {"has": ALL3, "excl": ALL3 if "separate_set" in v else []} for u, v in unit_place.items()}},
            "lives": dict(lives), "all": ["main_res"], "person": person or {}, "rel": list(rel),
            "shares": {p: list(ALL3) for p in sharers}, "unknown": [], "false": list(false), "judgement": []}


def known(R, case):
    """The record with only the vocabulary the rules in use have (the frozen rules lack the fix's names)."""
    p1 = set(R.PLACE1)
    c = dict(case)
    c["place"] = {u: [x for x in v if x in p1] for u, v in case["place"].items()}
    c["false"] = [f for f in case.get("false", []) if f[1] in p1]
    return c


def answers(uc, case, mutant=None):
    R, T, E, RUN = uc
    from ve.environment import Environment
    prover = RUN.Prover(Environment(T.environment()))
    return RUN.run_case(prover, known(R, case), mutant)[0]


def fl01():
    # Ben owns the freehold, lives with his wife Clara; Anna, au pair, room supplied by Ben for her exclusively domestic
    # work, pays nothing; Dan, unrelated friend, rent-free; all share kitchen and bathroom; main residence.
    return house("T-FL01", ["ben", "clara", "anna", "dan"],
                 person={"ben": ["freehold"], "anna": ["excl_domestic", "listed_work"]},
                 rel=[("ben", "clara", "married"), ("anna", "ben", "works_for"), ("anna", "ben", "supplied_by")])


def fl02():
    # Converted house: Bob, tenant of a self-contained ground-floor flat, pays rent; Ann, Bob's nanny, non-self-contained
    # attic room supplied by Bob for her work, no rent; Carl, unrelated, non-self-contained bedsit rent-free.
    return units("T-FL02", {"bob": "unit1", "ann": "unit2", "carl": "unit3"},
                 {"unit1": ["within", "created_since"] + SCF, "unit2": NONFLAT, "unit3": NONFLAT},
                 person={"bob": ["rent_payable"], "ann": ["listed_work"]},
                 rel=[("ann", "bob", "works_for"), ("ann", "bob", "supplied_by")], sharers=["ann", "carl"])


def fl03(*, stated=True, false=()):
    # Converted house: three bedsits let to three unrelated rent-paying tenants (main residence, used for nothing else);
    # one self-contained flat used partly as its occupant's office: occupation is not the only use of the premises.
    prem = ["only_use_n"] if stated else []
    return units("T-FL03", {"t1": "unit1", "t2": "unit2", "t3": "unit3", "dee": "unit4"},
                 {"unit1": NONFLAT, "unit2": NONFLAT, "unit3": NONFLAT, "unit4": ["within", "created_since"] + SCF},
                 premises=prem, person={p: ["rent_payable"] for p in ["t1", "t2", "t3", "dee"]},
                 sharers=["t1", "t2", "t3"], false=false)


def fl04():
    # Rented house: married H and W, H pays rent; nanny N works only for W (listed work), her room supplied by H as part
    # of the consideration, no rent; all main residence, sharing kitchen and bathroom.
    return house("T-FL04", ["h", "w", "n"], person={"h": ["rent_payable"], "n": ["listed_work"]},
                 rel=[("h", "w", "married"), ("n", "w", "works_for"), ("n", "h", "supplied_by")])


def fl05():
    # House of bedsits: B in room 1; A, B's au pair, room 2, supplied by B, no rent; C, B's brother, room 3, pays rent.
    return units("T-FL05", {"b": "unit1", "a": "unit2", "c": "unit3"},
                 {u: ["within", "part_of_building", "above_below"] for u in ["unit1", "unit2", "unit3"]},
                 person={"a": ["listed_work"], "c": ["rent_payable"]},
                 rel=[("a", "b", "works_for"), ("a", "b", "supplied_by"), ("b", "c", "sibling_of")],
                 sharers=["b", "a", "c"])


def fl05_one_unit():
    # The same people in one dwelling: C lives with B.
    return house("T-FL05-same", ["b", "a", "c"], person={"a": ["listed_work"], "c": ["rent_payable"]},
                 rel=[("a", "b", "works_for"), ("a", "b", "supplied_by"), ("b", "c", "sibling_of")])


def fl06():
    # Three units: B and his wife in unit 1; nanny A in unit 2, supplied by B as consideration, no rent; A's husband H in
    # unit 3, pays rent; kitchen shared; all main residence.
    return units("T-FL06", {"b": "unit1", "wife": "unit1", "a": "unit2", "h": "unit3"},
                 {u: ["within", "part_of_building", "above_below"] for u in ["unit1", "unit2", "unit3"]},
                 person={"a": ["listed_work"], "h": ["rent_payable"]},
                 rel=[("b", "wife", "married"), ("a", "b", "works_for"), ("a", "b", "supplied_by"), ("a", "h", "married")],
                 sharers=["b", "wife", "a", "h"])


def fl07(*, in_block=True):
    # Flat 2, a self-contained flat in a converted block stated to be a s.257 block; five unrelated members of a
    # religious community whose principal occupation is prayer; they share the flat's kitchen, pay rent, main residence.
    people = ["m1", "m2", "m3", "m4", "m5"]
    c = house("T-FL07", people, person={p: ["rent_payable"] for p in people},
              place=SCF + ["is_part", "created_since", "in_block", "religious"] + (["in_s257_block"] if in_block else []))
    c["places"] = ["premises", "flat1"]
    c["place"]["flat1"] = ["in_block"] + SCF
    c["amen"]["flat1"] = {"has": ALL3, "excl": ALL3}
    return c


def a(q1, q2, tests=None, sch14=None):
    return {"Q1": q1, "Q2": q2, "Q3": "OPEN" if tests is None else {"tests": tests, "sch14": sch14}}


# ---- row tests (fail on the frozen rules) -----------------------------------------------------------------------------

def test_i11_fl01_au_pair_work_is_consideration_standard_test(uc):
    assert answers(uc, fl01()) == a("NO", "NO", ["standard test"], ["para 6"])


def test_i14_fl02_nanny_work_is_consideration_converted_test(uc):
    assert answers(uc, fl02()) == a("YES", "NO", ["converted building test"], [])


def test_i14_fl03_flat_office_use_converted_test_met(uc):
    assert answers(uc, fl03()) == a("YES", "NO", ["converted building test"], [])


def test_i14_fl03_nonflat_use_unstated_refused(uc):
    # occupation is not the only use of the premises and the non-flat units' use is not stated: unknown -> refused
    assert answers(uc, fl03(stated=False)) == a("OPEN", "NO")


def test_i30_fl04_works_for_wife_supplied_by_husband_one_household(uc):
    assert answers(uc, fl04()) == a("NO", "NO", [], [])


def test_i30_fl05_brother_in_other_bedsit_refused(uc):
    assert answers(uc, fl05()) == a("OPEN", "NO")  # fewer than five: Q2 NO either way


def test_i32_fl06_worker_husband_in_other_unit_refused(uc):
    assert answers(uc, fl06()) == a("OPEN", "NO")


def test_i42_fl07_religious_flat_in_s257_block_refused(uc):
    assert answers(uc, fl07()) == a("OPEN", "OPEN")


# ---- guards (the same answer before and after the fix) ----------------------------------------------------------------

def test_guard_fl03_nonflat_other_use_stated_converted_test_fails(uc):
    got = answers(uc, fl03(stated=False, false=[("unary", "only_use_n", "premises")]))
    assert got == a("NO", "NO", [], [])


def test_guard_fl05_brother_in_same_dwelling_one_household(uc):
    assert answers(uc, fl05_one_unit()) == a("NO", "NO", [], [])


def test_guard_fl07_flat_not_in_s257_block_para5_applies(uc):
    assert answers(uc, fl07(in_block=False)) == a("NO", "NO", ["self-contained flat test"], ["para 5"])


# ---- mutants: each restores a frozen rule and is killed by its row test -------------------------------------------------

@pytest.mark.parametrize("mutant,make,fixed", [
    ("M6", fl01, a("NO", "NO", ["standard test"], ["para 6"])),
    ("M7", fl02, a("YES", "NO", ["converted building test"], [])),
    ("M8", fl03, a("YES", "NO", ["converted building test"], [])),
    ("M9", fl04, a("NO", "NO", [], [])),
    ("M10", fl05, a("OPEN", "NO")),
    ("M10", fl06, a("OPEN", "NO")),
    ("M11", fl07, a("OPEN", "OPEN")),
])
def test_mutant_restoring_frozen_rule_killed(uc, mutant, make, fixed):
    assert answers(uc, make(), mutant) != fixed
