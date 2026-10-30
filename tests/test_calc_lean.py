"""`ve calc check FILE` (math-evidence ME-3): the `calc` route's own cases through `ve.calc`, the relay of the Lean
service's `calc` mode. What it shows is Lean's: each row's claim, kind, outcome and reason, English line and exact
values (spec 3.4, 13.6); a refused case is Lean's diagnostic; an answer not bound to its request is
`CheckerUnavailable` (exit 5), never a verdict."""
from __future__ import annotations

import json

import pytest

from tests.lean_service_corpus import calc_cases
from ve import calc
from ve.__main__ import main
from ve.backends import relay
from ve.errors import CheckerUnavailable, VEError

R3_LINE = ("Assume the following. 1. The displacement equals the product of 0.4 and the squared velocity ratio. "
           "2. The displacement is less than 0.02. 3. The squared velocity ratio equals the square of the velocity "
           "ratio. 4. The velocity ratio is at least 0. From these, it follows that the velocity ratio is less than "
           "1 divided by {}.")
DIGITS = "unknown: an exact value would have more than 4,096 digits"
R3_CERT = ('  certificate [{"farkas":{"goal":{"coeffs":[["s","-1"]],"const":"1/20",'
           '"strict":true},"weights":["1","0","1","2/5"]}},{"square":{"a":"1/20",'
           '"b":"1/4","root":"r","square":"s"}}]')
R4_POINT = '  counterexample [["r","1/5"],["s","1/25"],["d","2/125"]]'
# What `ve calc check` shows of each route case (after its meaning_id line): spec 13.6's R-1 to R-4, V-9, the mixed
# case of claim and follows rows under a software convention.
SHOWN = {
    0: ["c1 claim holds",
        "  The scored baseline rate is 0.296 when rounded to three decimal places, with exact ties going up.",
        "  sides 8/27", "  display 0.29629…", "  tie false",
        "c2 claim fails",
        "  The scored baseline rate is 0.297 when rounded to three decimal places, with exact ties going up.",
        "  sides 8/27", "  display 0.29629…", "  tie false"],
    1: [f"v1 claim unknown ({DIGITS})", "  The largest number is less than 1.", "  sides null, 1", "  tie false",
        "v2 claim undefined", "  sides null, 1", "  tie false"],
    4: ["c1 claim fails", "  The x is 2.67 when rounded to two decimal places, with exact ties going up.",
        "  sides 107/40", "  display 2.6750", "  tie true", "  reproduction unknown"],
    20: ["h6 follows holds", "  " + R3_LINE.format(4), R3_CERT],
    21: ["h6 follows fails", "  " + R3_LINE.format(5), R4_POINT],
    28: ["w1 claim holds", "  The eighth is from 0 through 1 divided by 3.", "  sides 1/8, 0, 1/3", "  tie false",
         "  reproduction unknown",
         "h6 follows holds", "  " + R3_LINE.format(4), R3_CERT, "  reproduction unknown",
         "u1 claim holds", "  The eighth is 0.13 when rounded to two decimal places, with exact ties going up.",
         "  sides 1/8", "  display 0.1250", "  tie true", "  reproduction unknown",
         "h7 follows fails", "  " + R3_LINE.format(5), R4_POINT, "  reproduction unknown"],
}


@pytest.mark.parametrize("index", SHOWN)
def test_check_shows_leans_rows(index):
    result = calc.check(calc_cases()[index])
    shown = calc.lines(result)
    assert shown[0] == f"meaning_id {result['meaning_id']}" and len(result["meaning_id"]) == 64
    assert shown[1:] == SHOWN[index]


def _run(tmp_path, capsys, case, name="case.json"):
    path = tmp_path / name
    path.write_text(case if type(case) is str else json.dumps(case, ensure_ascii=False))
    code = main(["calc", "check", str(path)])
    return code, capsys.readouterr().out


def test_the_command_prints_leans_answer(tmp_path, capsys):
    code, out = _run(tmp_path, capsys, calc_cases()[20])
    assert code == 0 and out.splitlines()[1:] == SHOWN[20]


@pytest.mark.parametrize("index, code, error", [
    (12, 2, "UnknownName: y (declare it before the value that uses it)"),
    (14, 4, "ResourceLimit: an exponent exceeds 64"),
    (19, 2, "NoClaims: a calculation needs at least one claim"),
])
def test_a_refused_case_is_leans_diagnostic(tmp_path, capsys, index, code, error):
    got, out = _run(tmp_path, capsys, calc_cases()[index])
    assert got == code and json.loads(out)["error"]["message"] == error


def test_a_file_that_is_no_json_case_is_invalid_input(tmp_path, capsys):
    for text, status in (('{"format": "ve-calc@0", "claims": [', "SyntaxError"),
                         ('{"a": 1, "a": 2}', "DuplicateDeclaration")):
        code, out = _run(tmp_path, capsys, text)
        assert code == 2 and json.loads(out)["status"] == status
    assert main(["calc", "check", str(tmp_path / "missing.json")]) == 2


def test_an_unbound_answer_is_checker_unavailable(monkeypatch, tmp_path, capsys):
    """Exit 5, never a verdict: Lean's answer with its two claim ids swapped."""
    case = calc_cases()[0]
    genuine = relay.decide("calc", [case])[0]
    c1, c2 = genuine["rows"]
    swapped = {**genuine, "rows": [{**c1, "claim": "c2"}, {**c2, "claim": "c1"}]}
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **options: [swapped])
    with pytest.raises(CheckerUnavailable):
        calc.check(case)
    code, out = _run(tmp_path, capsys, case)
    assert code == 5 and json.loads(out)["status"] == "CheckerUnavailable"
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **options: [genuine])
    assert calc.check(case) == genuine


def _nodes(value, path=()):
    yield path, value
    children = value.items() if type(value) is dict else enumerate(value) if type(value) is list else ()
    for key, child in children:
        yield from _nodes(child, (*path, key))


def test_a_malformed_case_reaches_only_leans_answer():
    """Each member of R-3's case (premises, a follows check and its links) replaced by 7, true, null, [], {}, 1.5, a
    lone surrogate or a 10,000-deep list: `calc.check` returns a bound answer or raises a `VEError` (Lean's refusal,
    or the wire's for a value JSON cannot send), never `CheckerUnavailable` or another exception."""
    deep: list = []
    for _ in range(10_000):
        deep = [deep]
    case = calc_cases()[20]
    outcomes = {"answered": 0, "refused": 0}
    for path, value in list(_nodes(case))[1:]:
        for other in (7, True, None, [], {}, 1.5, "\ud800", deep):
            if type(other) is type(value) and other != "\ud800":
                continue
            mutant = json.loads(json.dumps(case))
            parent = mutant
            for step in path[:-1]:
                parent = parent[step]
            parent[path[-1]] = other
            try:
                calc.check(mutant)
                outcomes["answered"] += 1
            except CheckerUnavailable:
                raise
            except VEError:
                outcomes["refused"] += 1
    assert outcomes["refused"] > 100
