"""The `calc` service mode (math-evidence ME-2, me-2b): Lean's answers to the mode's route cases in
`tests/data/route-cases.jsonl` through `ve_service`, and the mode's case decoder (`VE.Service.calcCases`):
negative integers are read with their signs, while duplicate keys and the fraction and exponent spellings
of an integer are refused, as the restricted decoder refuses them in every mode."""
from __future__ import annotations

import json

import pytest

from tests.lean_build import lean_build
from tests.lean_service_corpus import calc_cases as route_cases
from tests.subprocesses import HANG_TIMEOUT
from ve.backends.lean_service import LeanService, case_digest, case_texts
from ve.backends.service_schema import Invalid, check_response

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
    "VerbalisationCollision(x, x)",  # me-2d: the same words, so W6a's check before DuplicateName
    "DuplicateClaimId: c1",
    "NoClaims: a calculation needs at least one claim",
    ["h6 holds"],  # R-3 (H-6): a derivation that follows
    ["h6 fails"],  # R-4 (H-6n): one that does not
    ["t1 holds", "t2 holds", "t3 holds", f"t4 unknown ({DIGITS})", "t5 undefined", "t6 holds", "t7 holds"],  # me-2c
    "DuplicateName: x",  # me-2d: the words checks, each refused, and the nearest accepted words
    'ValueWordsForm: the words of x must begin with "the" and not with "baseline"',
    'ReservedWord: "and" in the words of x',
    "VerbalisationCollision(x, y)",
    ["c1 holds", "c2 fails"],
    # me-3: claim and follows rows (both outcomes) under a software convention, beside a stated value
    ["w1 holds reproduction unknown", "h6 holds reproduction unknown", "u1 holds reproduction unknown",
     "h7 fails reproduction unknown"],
    # me-2nb (spec 3.2 (a), (b)): each value computed once, so F1-28, past the deadline before, holds; G-1's power
    # is known beyond the digit limit from its base and never computed
    ["f1 holds"],
    [f"g1 unknown ({DIGITS})"],
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


def test_route_cases_answer_their_rows(service):
    """Each row is its own claim's (the plan's seeded bug, claim i + 1's verdict for claim i, fails here)."""
    cases = route_cases()
    response = ask(service, json.dumps(cases, ensure_ascii=False), len(cases))
    assert [says(bound["result"]) for bound in response["results"]] == EXPECTED


NINES = "9" * 40
WORK = "ResourceLimit: the work of the calculation exceeds 8589934592"


def free(name: str) -> dict:
    return {"name": name, "words": f"the {name}", "free": True}


def defined(name: str, expr: list) -> dict:
    return {"name": name, "words": f"the {name}", "defined": expr}


def bounded_case(values: list, side: list, premises: int, claims: list) -> str:
    """A case of `premises` premises `side < i`, one plain claim first (spec 13.3's P-2 and N-1)."""
    return json.dumps({"format": "ve-calc@0", "values": values, "premises": [
        {"id": f"p{i}", "claim": ["lt", side, ["lit", str(i)]], "support": "assumption"} for i in range(premises)],
        "claims": [{"id": "c", "claim": ["lt", ["lit", "0"], ["lit", "1"]]}, *claims]})


def p2_case(premises: int) -> str:
    """P-2: a doubling of a sum of 16 free values with 800-digit coefficients, and a derivation from premise 0, whose
    conclusion is small: a side over `a8` would be one more lowering at that side's price."""
    names = [f"u{i}" for i in range(16)]
    total = ["val", "u0"]
    for name in names[1:]:
        total = ["add", total, ["val", name]]
    values = [free(name) for name in names] + [
        defined("big", ["pow", ["lit", NINES], 20]), defined("a0", ["mul", ["val", "big"], total]),
        *(defined(f"a{i + 1}", ["add", ["val", f"a{i}"], ["val", f"a{i}"]]) for i in range(8))]
    return bounded_case(values, ["val", "a8"], premises,
                        [{"id": "d", "claim": ["follows", ["lt", ["val", "u0"], ["lit", "1"]], ["p0"], []]}])


def balanced(parts: list) -> list:
    while len(parts) > 1:
        pairs = [["add", a, b] for a, b in zip(parts[::2], parts[1::2])]
        parts = pairs + parts[len(pairs) * 2:]
    return parts[0]


def n1_case(premises: int) -> str:
    """N-1: a balanced sum of 400 free values, 8 mentions balanced in each premise, no derivation."""
    names = [f"v{i}" for i in range(400)]
    values = [free(name) for name in names] + [defined("s", balanced([["val", name] for name in names]))]
    return bounded_case(values, balanced([["val", "s"]] * 8), premises, [])


@pytest.mark.parametrize("case, want", [
    (p2_case(72), ["c holds", "d fails"]),
    (p2_case(73), WORK),
    (n1_case(121), ["c holds"]),
    (n1_case(122), WORK),
], ids=["P-2 at 72", "P-2 at 73", "N-1 at 121", "N-1 at 122"])
def test_limit_10_on_the_lowering(service, case, want):
    """me-2nc (spec 3.2, DRI item 3): the premises' lowering is charged; under the limit the rows are today's, past it
    the whole case is refused with `Wire.limit`'s text."""
    assert says(ask(service, f"[{case}]", 1)["results"][0]["result"]) == want


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


def _row_mutants(rows):
    """(label, rows) of R-1's two rows rebound or re-paired: each claim id rebound, a row dropped, added or the
    two swapped, a decided outcome given a reason and an unknown one none, a reproduction retyped."""
    first, second = rows
    yield "claim rebound", [{**first, "claim": "c2"}, second]
    yield "claim not the request's", [first, {**second, "claim": "c3"}]
    yield "row dropped", [first]
    yield "row added", [first, second, second]
    yield "rows swapped", [second, first]
    yield "no rows", []
    yield "reason on a decided row", [{**first, "reason": DIGITS}, second]
    yield "unknown without a reason", [{**first, "outcome": "unknown"}, second]
    yield "unknown with another text", [{**first, "outcome": "unknown", "reason": "unknown"}, second]
    yield "reproduction retyped", [{**first, "reproduction": "yes"}, second]
    yield "kind retyped", [{**first, "kind": "follows"}, second]
    yield "meaning id not a digest", None
    # me-2c's row fields: one side per expression of the request's claim, each an exact value or null; a display only
    # for a rounding claim; a tie flag; a line or null; no finding; a follows row has none of a claim row's members.
    yield "a side added", [{**first, "sides": ["8/27", "1"]}, second]
    yield "no side", [{**first, "sides": []}, second]
    yield "a side not exact", [{**first, "sides": ["0.296"]}, second]
    yield "a side a number", [{**first, "sides": [1]}, second]
    yield "a side zero-padded", [{**first, "sides": ["08/27"]}, second]
    yield "display retyped", [{**first, "display": 0.296}, second]
    yield "display not a decimal", [{**first, "display": "about 0.3"}, second]
    yield "tie retyped", [{**first, "tie": "false"}, second]
    yield "line retyped", [{**first, "line": 7}, second]
    yield "line empty", [{**first, "line": ""}, second]
    yield "a finding", [{**first, "finding": {"kind": "source", "text": "x"}}, second]
    for member in ("sides", "display", "tie", "line", "finding"):
        yield f"{member} dropped", [{k: v for k, v in first.items() if k != member}, second]
    yield "an extra member", [{**first, "rests_on": []}, second]


def _bound_request(service, case):
    text = json.dumps([case], ensure_ascii=False)
    response = ask(service, text, 1)
    request = {"id": response["id"], "mode": "calc", "cases": [case],
               "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
    check_response("calc", response, request)
    return request, response


def _refused(response, request, result):
    with pytest.raises(Invalid):
        check_response("calc", {**response, "results": [{**response["results"][0], "result": result}]}, request)


def test_answers_are_bound_to_their_request(service):
    """R8: a row per request claim, in order, naming the request's claim; an outcome with its reason only."""
    request, response = _bound_request(service, route_cases()[0])
    result = response["results"][0]["result"]
    for label, rows in _row_mutants(result["rows"]):
        _refused(response, request, {**result, "rows": rows} if rows is not None else {**result, "meaning_id": "x"})


# Spec 13.6's R-1 and R-2 rows, every member me-2c delivers (`rests_on` is not delivered: REPORT, spec gap); the
# lines are Lean's own (11.1), R-2's second `null` where 11.2's nesting rule refuses `1 divided by (x minus x)`.
R1_R2 = [
    [{"claim": "c1", "outcome": "holds", "sides": ["8/27"], "display": "0.29629\u2026", "tie": False,
      "line": "The scored baseline rate is 0.296 when rounded to three decimal places, with exact ties going up."},
     {"claim": "c2", "outcome": "fails", "sides": ["8/27"], "display": "0.29629\u2026", "tie": False,
      "line": "The scored baseline rate is 0.297 when rounded to three decimal places, with exact ties going up."}],
    [{"claim": "v1", "outcome": "unknown", "sides": [None, "1"], "display": None, "tie": False,
      "line": "The largest number is less than 1."},
     {"claim": "v2", "outcome": "undefined", "sides": [None, "1"], "display": None, "tie": False, "line": None}]]
R3_LINE = ("Assume the following. 1. The displacement equals the product of 0.4 and the squared velocity ratio. "
           "2. The displacement is less than 0.02. 3. The squared velocity ratio equals the square of the velocity "
           "ratio. 4. The velocity ratio is at least 0. From these, it follows that the velocity ratio is less than "
           "1 divided by 4.")


def test_rows_carry_leans_sides_display_tie_and_line(service):
    """R3: each new member is Lean's text, as spec 13.6 writes R-1, R-2 and R-3; no row has a finding (a standalone
    case), and a follows row has no sides, display or tie."""
    cases = route_cases()
    response = ask(service, json.dumps([cases[0], cases[1], cases[20]], ensure_ascii=False), 3)
    results = [bound["result"] for bound in response["results"]]
    for result, want in zip(results, R1_R2):
        assert [{k: row[k] for k in want[0]} for row in result["rows"]] == want
        assert {row["finding"] for row in result["rows"]} == {None}
    (h6,) = results[2]["rows"]
    assert h6["line"] == R3_LINE and h6["finding"] is None and not {"sides", "display", "tie"} & h6.keys()


# The last route case's rows (me-2c): a tie under either rule and none for a printed bound, two places beyond the
# printed ones, no display or tie flag without a value, one side per expression of a range; a negative numeral has
# no English (11.2), so its line is null.
ROW_FIELDS = [
    (["1/8"], "0.1250", True, "The eighth is 0.13 when rounded to two decimal places, with exact ties going up."),
    (["1/8"], "0.1250", True,
     "The eighth is 0.12 when rounded to two decimal places, with exact ties going to the even digit."),
    (["1/8"], "0.1250", False, "The eighth is 0.12 when rounded down to two decimal places."),
    ([None], None, None, "The largest number is 1 when rounded to a whole number, with exact ties going up."),
    ([None], None, False, None),
    (["1/8", "0", "1/3"], None, False, "The eighth is from 0 through 1 divided by 3."),
    (["1/8", "-1"], None, False, None)]


def test_row_fields_at_their_boundaries(service):
    """R3: each member is Lean's text on both sides of its boundary (the RunExamples row-field guards pin more)."""
    case = route_cases()[22]
    result = ask(service, json.dumps([case], ensure_ascii=False), 1)["results"][0]["result"]
    assert [(r["sides"], r["display"], r["tie"], r["line"]) for r in result["rows"]] == ROW_FIELDS


def test_a_follows_row_has_no_claim_members(service):
    """R8: a derivation's row given a claim row's sides, display or tie is refused."""
    request, response = _bound_request(service, route_cases()[20])
    result = response["results"][0]["result"]
    (row,) = result["rows"]
    for member, value in (("sides", ["1"]), ("display", None), ("tie", False)):
        _refused(response, request, {**result, "rows": [{**row, member: value}]})


@pytest.mark.parametrize("claim, sides, display, tie", [
    (["eq", ["val", "x"], ["lit", "1"]], ["1"], None, False),  # two expressions, one side
    (["eq", ["val", "x"], ["lit", "1"]], ["1", "1"], "1.00", False),  # no display beside a comparison
    (["eq", ["val", "x"], ["lit", "1"]], ["1", "1"], None, None),  # a comparison's tie is false
    (["within", ["val", "x"], ["lit", "0"], ["lit", "2"]], ["1", "0"], None, False),  # three expressions
    (["rounds-down", ["val", "x"], "1"], ["1"], "1.00", True),  # a printed bound is never a tie
])
def test_sides_display_and_tie_are_bound_to_the_claims_form(service, claim, sides, display, tie):
    """R8: the number of sides is the request claim's number of expressions; a display only beside a rounding claim;
    a tie flag only for a `rounds` claim; anything else is refused."""
    case = json.loads(CASE % ('"1"', "1", ""))
    case["claims"][0]["claim"] = claim
    request, response = _bound_request(service, case)
    result = response["results"][0]["result"]
    (row,) = result["rows"]
    _refused(response, request, {**result, "rows": [{**row, "sides": sides, "display": display, "tie": tie}]})


def test_a_reproduction_is_unknown_exactly_under_a_software_convention(service):
    """The rows of a case without `software` have no reproduction (R-1); those of a case with one, `unknown` (V-9)."""
    for case, other in ((route_cases()[0], "unknown"), (route_cases()[4], None)):
        request, response = _bound_request(service, case)
        result = response["results"][0]["result"]
        assert {row["reproduction"] for row in result["rows"]} == {"unknown" if other is None else None}
        _refused(response, request, {**result, "rows": [{**row, "reproduction": other} for row in result["rows"]]})
