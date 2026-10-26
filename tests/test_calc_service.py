"""The `calc` service mode (math-evidence ME-2, me-2b): Lean's answers to the mode's route cases in
`tests/data/route-cases.jsonl` through `ve_service`, and the mode's case decoder (`VE.Service.calcCases`):
negative integers are read with their signs, while duplicate keys and the fraction and exponent spellings
of an integer are refused, as the restricted decoder refuses them in every mode."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.lean_build import lean_build
from tests.subprocesses import HANG_TIMEOUT
from ve.backends.lean_service import LeanService

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests/data/route-cases.jsonl"
DIGITS = "unknown: an exact value would have more than 4,096 digits"

# Each calc route case's rows, in the file's order (spec 13.3 and 13.6), or its refusal.
EXPECTED = [
    ["c1 holds", "c2 fails"],  # R-1
    [f"v1 unknown ({DIGITS})", "v2 undefined"],  # R-2 (V-11)
    ["c1 holds", "c2 holds", "c3 holds"],  # V-2
    [f"r{i} holds" for i in range(20)],  # V-5
    ["c1 fails reproduction unknown"],  # V-9
    ["up fails", "even holds"],  # V-8, the rule per claim
    ["up fails", "even holds"],  # V-8, the case's rule
    ["c1 holds"],  # I-1: ["sci", "5.89", -7]
    ["c1 fails"],  # I-1 with plain spellings
    ["c1 holds", "c2 fails", "c3 fails", "c4 holds", "c5 holds"],
    ["c1 holds", "c2 holds", "c3 fails"],
    ["c1 fails"],  # a printed spelling with a sign error
    "UnknownName: y (declare it before the value that uses it)",
    "UnknownName: x (declare it before the value that uses it)",
    "ResourceLimit: an exponent exceeds 64",
    "ResourceLimit: Decimal literal exceeds 40 digits",
    "InvalidInput: case.meaning_id is unknown",
    "DuplicateName: x",
    "DuplicateClaimId: c1",
    "NoClaims: a calculation needs at least one claim",
]


@pytest.fixture(scope="module")
def service():
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as running:
        yield running


def ask(service, text: str, count: int) -> dict:
    _, response = service.exchange("calc", text, count, timeout=HANG_TIMEOUT)
    return response


def says(result: dict):
    """A result's rows as `claim outcome (reason) reproduction unknown`, or its refusal."""
    if result["status"] != "ok":
        return result["error"]
    return [f"{r['claim']} {r['outcome']}" + (f" ({r['reason']})" if r["reason"] else "") +
            (" reproduction unknown" if r["reproduction"] else "") for r in result["rows"]]


def route_cases() -> list[dict]:
    rows = (json.loads(line) for line in CASES.read_text().splitlines())
    return [case for mode, case in rows if mode == "calc"]


def test_route_cases_answer_their_rows(service):
    """Each row is its own claim's (the plan's seeded bug, claim i + 1's verdict for claim i, fails here)."""
    cases = route_cases()
    response = ask(service, json.dumps(cases, ensure_ascii=False), len(cases))
    assert [says(bound["result"]) for bound in response["results"]] == EXPECTED


CASE = ('{"format": "ve-calc@0", "values": [{"name": "x", "words": "the half-even rate - a test", '
        '"stated": %s}], "claims": [{"id": "c-1", "claim": ["eq", ["val", "x"], ["lit", "%s"]]}]%s}')


@pytest.mark.parametrize("stated, literal, want", [
    ('["sci", "-5", -1]', "-0.5", ["c-1 holds"]),
    ('["sci", "5", -1]', "-0.5", ["c-1 fails"]),
    ('"-0.5"', "-0.5", ["c-1 holds"]),
])
def test_signs_are_read_and_strings_kept(service, stated, literal, want):
    """A `-` outside strings is a number's sign; in a string (a claim id, words) it stays."""
    response = ask(service, "[" + CASE % (stated, literal, "") + "]", 1)
    assert says(response["results"][0]["result"]) == want


@pytest.mark.parametrize("more", [
    ', "software": "' + "x" * 65 + '", "software": "P"',  # me-2 round 3: the earlier member was never seen
    ', "claims": []',
    ', "rounding": "half-even", "rounding": "ties-up"',
])
def test_duplicate_keys_are_refused(service, more):
    response = ask(service, "[" + CASE % ('"1"', "1", more) + "]", 1)
    assert response["status"] == "error" and "duplicate object key" in response["error"]


@pytest.mark.parametrize("exponent", ["64", "6.4e1", "64.0", "640e-1", "-64"])
def test_an_exponent_is_an_integer_written_plainly(service, exponent):
    """Fraction and exponent spellings of an integer are refused alike (me-2 round 3, hunt 1)."""
    case = CASE % ('"1"', "1", "")
    case = case.replace('["lit", "1"]', f'["pow", ["lit", "1"], {exponent}]')
    response = ask(service, f"[{case}]", 1)
    if exponent == "64":
        assert says(response["results"][0]["result"]) == ["c-1 holds"]
    elif exponent == "-64":
        assert response["results"][0]["result"]["error"].startswith("InvalidInput")
    else:
        assert response["status"] == "error" and "error" in response
