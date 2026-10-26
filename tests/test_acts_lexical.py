"""act-phrases AP-1, first part (ap-1a): `VE.Acts.Lexical` and the profile-aware regulated decoder.

Without `acts@0` every document decodes with today's act check (`decodeRegulated_without_acts`); with it (its
row landed in ap-1b, `tests/test_acts_profile.py`) the norms route reads the act with `Lexical.check`. These cases go
through the Lean service's norms mode and read Lean's text only; the fixtures of the new check are `#guard`s in
`lean/VE/Acts/LexicalExamples.lean`, which `lake build` elaborates.
"""
from __future__ import annotations

import copy

import pytest

from tests import lean_routes

pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="ve_service is not built")

A1 = "{0} in full equality to a fair and public hearing by an independent and impartial tribunal in {1}"

BASE = {
    "id": "w1", "kind": "norms-elaborate",
    "environment": {
        "language": "ve.core@0.2", "profiles": ["norms@0", "relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {
            "sorts": {"person": {"description": "person"}, "case": {"description": "case"}},
            "predicates": {
                "heard": {"arguments": ["person", "case"], "description": "permission",
                          "regulated": {"role": "permission", "default": "allow", "act": "{0} be heard in {1}"}},
            },
            "constants": {},
        },
    },
    "norms": [{"norm": {"name": "m", "predicate": "heard", "sign": True, "guard": ["top"], "unless": [],
                        "over": []}}],
}


def answer(regulated=None, profiles=None):
    case = copy.deepcopy(BASE)
    env = case["environment"]
    if regulated is not None:
        env["vocabulary"]["predicates"]["heard"]["regulated"] = regulated
    if profiles is not None:
        env["profiles"] = profiles
    status, rows, stderr = lean_routes.run("norms", [case])
    assert rows is not None and len(rows) == 1, (status, stderr)
    return rows[0]


def message(row) -> str:
    assert row.get("status") == "error", row
    return row["error"]


def test_todays_document_is_answered():
    assert answer().get("status") != "error"


def test_under_the_acts_profile_the_norms_route_reads_the_act_with_the_lexical_check():
    # ap-1b: the row landed; A1 (97 B) needs its fixed phrase for its "and"
    regulated = {"role": "permission", "default": "allow", "act": A1}
    profiles = ["acts@0", "norms@0", "relational-fol@0"]
    assert message(answer(regulated, profiles)) == (
        "InvalidInput: act phrase for heard joins acts with 'and' outside a fixed phrase")
    case = copy.deepcopy(BASE)
    case["environment"]["profiles"] = profiles
    case["environment"]["vocabulary"]["predicates"]["heard"]["regulated"] = regulated
    case["environment"]["vocabulary"]["acts"] = {
        "fixed": ["a fair and public hearing by an independent and impartial tribunal"]}
    status, rows, stderr = lean_routes.run("norms", [case])
    assert rows is not None and rows[0].get("status") != "error", (status, rows, stderr)


@pytest.mark.parametrize("regulated", [
    {"role": "plain", "default": "deny", "act": "{0} to seek asylum", "form": "has the right"},
    {"role": "plain", "default": "deny", "form": "is entitled"},
    {"role": "permission", "default": "allow", "act": "{0} be heard in {1}", "form": "has the right"},
], ids=["plain-act-and-form", "plain-form", "permission-form"])
def test_without_acts_a_plain_act_or_a_form_is_refused_as_today(regulated):
    assert message(answer(regulated)) == "InvalidInput: invalid regulated fields for heard"


@pytest.mark.parametrize("act", [
    A1,  # A1: 97 bytes, over today's 80 characters
    "{0} be heard and answered in {1}",  # a join word: today's reserved word
    "{0} be heard, then answered in {1}",  # a comma
    "{0} comply with the operator’s instructions in {1}",  # A19: today's check does not fold U+2019
])
def test_without_acts_an_act_is_checked_by_todays_check(act):
    regulated = {"role": "permission", "default": "allow", "act": act}
    assert message(answer(regulated)) == "InvalidInput: invalid act phrase for heard"


def test_without_acts_nor_stays_one_unanalysed_act():
    # A24: today's check accepts "nor"; acts@0 will refuse it (D-4), today's documents keep it
    regulated = {"role": "permission", "default": "allow", "act": "{0} neither seek nor dodge {1}"}
    assert answer(regulated).get("status") != "error"
