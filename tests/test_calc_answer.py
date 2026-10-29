"""The relay never takes a Lean `calc` answer that is not an answer to the request it sent (R8; math-evidence ME-3,
spec 3.4). Genuine answers of the service are mutated one and two faults at a time (each member dropped, emptied,
retyped, duplicated or reordered, a row past the request's last claim): through the service's schema check and
`ve.calc.read_answer`, the path `ve calc check` takes, every mutant is `CheckerUnavailable` or changes nothing
`ve.calc.lines` shows, apart from the evidence's semantic values covered by Lean's encoder theorem. Every binding fault (a claim id, kind or reproduction rebound, two claim ids swapped, rows
dropped, added or reordered) is refused by the relay's own binding alone. Then the follows row's `certificate` and
`counterexample` (DRI decision 2026-10-27 me-5d item 1): each check on both sides."""
from __future__ import annotations

import copy
import json
from itertools import combinations

import pytest

from tests.lean_build import lean_build
from tests.lean_service_corpus import calc_cases
from tests.subprocesses import HANG_TIMEOUT
from ve import calc
from ve.backends.lean_service import LeanService, _decode_json, case_digest, case_texts
from ve.backends.service_schema import Invalid, check_response
from ve.errors import CheckerUnavailable

DEEP: list = []
for _ in range(10_000):
    DEEP = [DEEP]
RETYPED = (7, 1.5, True, None, [], {}, "x", "\ud800", DEEP)
# Members whose value Lean may leave null (a line beyond 11.2's nesting rule; a side, display or tie without a known
# value), with the type a null of theirs may become: making one null, or a null a line's text or a tie's flag, is a
# change of Lean's value, which a relay cannot bind (it never re-evaluates), not a type fault. Every other retype of
# them is applied ("x" is no exact value and no display).
NULLABLE = {"line": str, "sides": None, "display": None, "tie": bool}
# Lists of Lean's exact values in order: reordering them changes a value, as replacing one does (not a binding).
VALUES = frozenset({"sides"})
# The route cases mutated: R-1, R-2 (an unknown and an undefined row), V-2 (three rows), V-9 (a software convention),
# R-3 and R-4 (follows), and the mixed case (claim and follows rows under a software convention).
GENUINE = {"R-1": 0, "R-2": 1, "V-2": 2, "V-9": 4, "R-3": 20, "R-4": 21, "mixed": 28}


@pytest.fixture(scope="module")
def service():
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as running:
        yield running


_ANSWERS: dict = {}


def _genuine(service, name):
    """The case, the service's response to it and the request it is checked against (as `LeanService` checks it)."""
    if name not in _ANSWERS:
        case = calc_cases()[GENUINE[name]]
        text = json.dumps([case], ensure_ascii=False)
        _, response = service.exchange("calc", text, 1, timeout=HANG_TIMEOUT)
        request = {"id": response["id"], "mode": "calc", "cases": [case],
                   "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
        _ANSWERS[name] = (case, response, request)
    return copy.deepcopy(_ANSWERS[name])


def _shown(case, response, request, result):
    """What `ve calc check` shows of `result`, or None when the transport (`LeanService` decodes each line with
    `_decode_json`: no lone surrogate, no nesting past the runtime's limit), the schema or the relay refuses it."""
    try:
        result = _decode_json(json.dumps(result))
        check_response("calc", {**response, "results": [{**response["results"][0], "result": result}]}, request)
        return [line for line in calc.lines(calc.read_answer(result, case))
                if not line.startswith(("  certificate ", "  counterexample "))]
    except (ValueError, RecursionError, Invalid, CheckerUnavailable):
        return None


def _nodes(value, path=()):
    yield path, value
    children = value.items() if type(value) is dict else enumerate(value) if type(value) is list else ()
    for key, child in children:
        yield from _nodes(child, (*path, key))


def _set(row, path, value):
    out = copy.deepcopy(row)
    parent = out
    for step in path[:-1]:
        parent = parent[step]
    if value is _set:
        del parent[path[-1]]
    else:
        parent[path[-1]] = value
    return out


def _faults(result):
    """One-fault mutants as (path, value) edits, `_set` dropping the member: each member dropped, each value emptied or
    retyped, each list's first or last element duplicated and the list reversed, a row past the last claim."""
    for path, value in _nodes(result):
        if not path:
            continue
        member = next((step for step in reversed(path) if type(step) is str), None)
        if type(path[-1]) is str:
            yield path, _set
        for other in RETYPED:
            if type(other) is not type(value) or other == "\ud800":
                if member in NULLABLE and (other is None or (
                        value is None and type(other) is NULLABLE[member] and other != "\ud800")):
                    continue
                yield path, other
        if type(value) in (str, list, dict) and value:
            yield path, type(value)()
        if type(value) is list and value:
            for other in ([value[0], *value], [*value, value[-1]], *(() if member in VALUES else (value[::-1],))):
                if other != value:
                    yield path, other
    rows = result["rows"]
    yield ("rows",), [*rows, {**rows[-1], "claim": f"{rows[-1]['claim']}-past"}]


@pytest.mark.parametrize("name", GENUINE)
def test_mutants_never_pass_as_answers(service, name):
    case, response, request = _genuine(service, name)
    genuine = response["results"][0]["result"]
    shown = _shown(case, response, request, genuine)
    assert shown is not None
    faults = list(_faults(genuine))
    shallow = [fault for fault in faults if fault[1] is not DEEP]  # a 10k-deep list is one fault only
    accepted = []
    for depth, edits in [(1, [(f,) for f in faults]), (2, combinations(shallow, 2))]:
        for edit in edits:
            try:
                mutant = genuine
                for path, value in edit:
                    mutant = _set(mutant, path, value)
            except (KeyError, IndexError, TypeError):
                continue  # the second fault's path is gone after the first
            if mutant != genuine and (seen := _shown(case, response, request, mutant)) is not None and seen != shown:
                accepted.append((depth, edit))
    assert not accepted, accepted[:5]


def _binding_faults(case, result):
    """Faults of what the relay binds: each row's claim id and kind rebound to each other one the request names, its
    reproduction set where the case has no software convention and unset where it has one, two claim ids swapped,
    and the rows dropped, duplicated or reordered."""
    rows = result["rows"]
    ids = [c["id"] for c in case["claims"]] + ["c-unasked"]
    for i, row in enumerate(rows):
        for other in ids:
            if other != row["claim"]:
                yield f"row {i} names {other}", _set(result, ("rows", i, "claim"), other)
        yield f"row {i} of the other kind", _set(result, ("rows", i, "kind"),
                                                  "claim" if row["kind"] == "follows" else "follows")
        yield f"row {i} reproduction", _set(result, ("rows", i, "reproduction"),
                                            None if row["reproduction"] else "unknown")
    for i, j in combinations(range(len(rows)), 2):
        swapped = _set(result, ("rows", i, "claim"), rows[j]["claim"])
        yield f"claim ids {i} and {j} swapped", _set(swapped, ("rows", j, "claim"), rows[i]["claim"])
        yield f"rows {i} and {j} swapped", _set(_set(result, ("rows", i), rows[j]), ("rows", j), rows[i])
    for i in range(len(rows)):
        yield f"row {i} dropped", {**result, "rows": rows[:i] + rows[i + 1:]}
        yield f"row {i} duplicated", {**result, "rows": rows[:i + 1] + rows[i:]}


@pytest.mark.parametrize("name", GENUINE)
def test_the_relay_alone_refuses_every_binding_fault(service, name):
    """The plan's seeded bug (the binding skips claim ids: two swapped claim ids are accepted) fails here."""
    case, response, _ = _genuine(service, name)
    genuine = response["results"][0]["result"]
    assert calc.answer_problem(genuine, case) is None
    accepted = [label for label, mutant in _binding_faults(case, genuine) if calc.answer_problem(mutant, case) is None]
    assert not accepted


# -- A follows row's certificate and counterexample (spec 3.4's table, 13.6's R-3 and R-4;
#    pinned by `lean/VE/Calc/RunExamples.lean`'s certificate and counterexample guards).

R3_CERTIFICATE = [{"farkas": {"goal": {"const": "1/20", "coeffs": [["s", "-1"]], "strict": True},
                              "weights": ["1", "0", "1", "2/5"]}},
                  {"square": {"square": "s", "root": "r", "a": "1/20", "b": "1/4"}}]
R4_COUNTEREXAMPLE = [["r", "1/5"], ["s", "1/25"], ["d", "2/125"]]


def _shown_row(service, name, certificate, counterexample, row=0):
    """A genuine route answer with row `row`'s evidence changed for the binding probe."""
    case, response, _ = _genuine(service, name)
    result = response["results"][0]["result"]
    result["rows"][row] = {**result["rows"][row], "certificate": certificate, "counterexample": counterexample}
    return case, result


def _refused(case, result, why):
    assert calc.answer_problem(result, case) == why
    with pytest.raises(CheckerUnavailable, match="not bound to its request"):
        calc.read_answer(result, case)


def test_the_true_certificate_and_counterexample_are_bound(service):
    for name, certificate, counterexample in [("R-3", R3_CERTIFICATE, None), ("R-4", None, R4_COUNTEREXAMPLE)]:
        case, response, request = _genuine(service, name)
        result = response["results"][0]["result"]
        assert result["rows"][0]["certificate"] == certificate
        assert result["rows"][0]["counterexample"] == counterexample
        assert _shown(case, response, request, result) is not None
        assert calc.read_answer(result, case) == result
    # a counterexample reading no free value, and the mixed case's two follows rows beside its claim rows
    case, result = _shown_row(service, "R-4", None, [])
    assert calc.answer_problem(result, case) is None
    case, result = _shown_row(service, "mixed", R3_CERTIFICATE, None, row=1)
    result["rows"][3] = {**result["rows"][3], "certificate": None, "counterexample": R4_COUNTEREXAMPLE}
    assert calc.answer_problem(result, case) is None


FREE = "a counterexample names a value that is not a free value of the request"
LINK = "a square step's pair is not one of the derivation's links"
COEFF = "a farkas goal names a value that is not a free value of the request"


@pytest.mark.parametrize("label, counterexample, why", [
    ("a renamed value (the decision's condition)", [["r", "1/5"], ["q", "1/25"], ["d", "2/125"]], FREE),
    ("a claim id", [["r", "1/5"], ["h6", "1/25"]], FREE),
    ("the true names, first and last only", [["r", "1/5"], ["d", "2/125"]], None),
    ("one name", [["s", "1/25"]], None),
    ("out of declaration order", [["s", "1/25"], ["r", "1/5"], ["d", "2/125"]],
     "a counterexample's names are not each once, in declaration order"),
    ("a name twice", [["r", "1/5"], ["r", "1/5"]], "a counterexample's names are not each once, in declaration order"),
    ("a value not exact", [["r", "0.2"]], "a counterexample is not a list of [name, value] pairs"),
    ("a pair of three", [["r", "1/5", "x"]], "a counterexample is not a list of [name, value] pairs"),
    ("a name not a string", [[1, "1/5"]], "a counterexample is not a list of [name, value] pairs"),
    ("an object", {"r": "1/5"}, "a counterexample is not a list of [name, value] pairs"),
])
def test_each_counterexample_name_is_a_free_value(service, label, counterexample, why):
    case, result = _shown_row(service, "R-4", None, counterexample)
    if why is None:
        assert calc.answer_problem(result, case) is None
    else:
        _refused(case, result, why)


def test_a_declared_value_that_is_not_free_is_refused(service):
    """The mixed case declares `h` stated: a counterexample or a goal naming it is refused, its free `d` accepted."""
    for name, accepted in (("h", False), ("d", True)):
        case, result = _shown_row(service, "mixed", None, [["r", "1/5"], [name, "1/8"]], row=3)
        assert (calc.answer_problem(result, case) is None) is accepted
        goal = {"const": "1/20", "coeffs": [[name, "-1"]], "strict": True}
        step = [{"farkas": {"goal": goal, "weights": ["1"]}}]
        case, result = _shown_row(service, "mixed", step, None, row=1)
        assert calc.answer_problem(result, case) == (None if accepted else COEFF)


def _square(square, root):
    return [R3_CERTIFICATE[0], {"square": {"square": square, "root": root, "a": "1/20", "b": "1/4"}}]


@pytest.mark.parametrize("label, certificate, why", [
    ("the derivation's link", _square("s", "r"), None),
    ("the link reversed (the decision's condition)", _square("r", "s"), LINK),
    ("two free values that are no link", _square("d", "r"), LINK),
    ("a renamed square", _square("q", "r"), LINK),
    ("a goal naming a renamed value", [{"farkas": {"goal": {"const": "1/20", "coeffs": [["q", "-1"]], "strict": True},
                                                   "weights": ["1"]}}], COEFF),
    ("a goal with no coefficients", [{"farkas": {"goal": {"const": "1/20", "coeffs": [], "strict": True},
                                                 "weights": ["1"]}}], None),
    ("no steps", [], "a certificate is not a list of steps"),
    ("no weights", [{"farkas": {"goal": R3_CERTIFICATE[0]["farkas"]["goal"], "weights": []}}],
     "a farkas step's weights are not exact values"),
    ("a weight not exact", [{"farkas": {"goal": R3_CERTIFICATE[0]["farkas"]["goal"], "weights": ["0.4"]}}],
     "a farkas step's weights are not exact values"),
    ("a strict flag retyped", [{"farkas": {"goal": {"const": "1/20", "coeffs": [], "strict": "true"},
                                           "weights": ["1"]}}], "a farkas goal is not a fact"),
    ("a bound not exact", [{"square": {"square": "s", "root": "r", "a": 0.05, "b": "1/4"}}],
     "a square step's bounds are not exact values"),
    ("two steps in one", [{**R3_CERTIFICATE[0], **R3_CERTIFICATE[1]}],
     "a certificate step is not one farkas or square step"),
    ("another step kind", [{"identity": {}}], "a certificate step is not one farkas or square step"),
])
def test_each_square_step_is_one_of_the_derivations_links(service, label, certificate, why):
    case, result = _shown_row(service, "R-3", certificate, None)
    if why is None:
        assert calc.answer_problem(result, case) is None
    else:
        _refused(case, result, why)


def test_a_link_of_another_derivation_is_refused(service):
    """Each step is bound to its own derivation's links: the mixed case's h6 has (s, r); a case whose follows claim
    has no link refuses the same step, and accepts the certificate without it."""
    case, result = _shown_row(service, "mixed", R3_CERTIFICATE, None, row=1)
    assert calc.answer_problem(result, case) is None
    case["claims"][1]["claim"][3] = []
    assert calc.answer_problem(result, case) == LINK
    result["rows"][1]["certificate"] = R3_CERTIFICATE[:1]
    assert calc.answer_problem(result, case) is None


@pytest.mark.parametrize("name, certificate, counterexample, why", [
    ("R-3", None, None, "a certificate is not exactly on a holds row"),
    ("R-3", R3_CERTIFICATE, R4_COUNTEREXAMPLE, "a counterexample is not exactly on a fails row"),
    ("R-4", R3_CERTIFICATE, R4_COUNTEREXAMPLE, "a certificate is not exactly on a holds row"),
    ("R-4", None, None, "a counterexample is not exactly on a fails row"),
])
def test_a_certificate_only_on_holds_and_a_counterexample_only_on_fails(service, name, certificate, counterexample,
                                                                         why):
    case, result = _shown_row(service, name, certificate, counterexample)
    _refused(case, result, why)


def test_the_two_fields_come_together_and_only_on_a_follows_row(service):
    case, response, _ = _genuine(service, "R-3")
    result = response["results"][0]["result"]
    row = result["rows"][0]
    result["rows"][0] = {k: v for k, v in row.items() if k not in {"certificate", "counterexample"}}
    _refused(case, result, "row h6 does not have the fields of a follows row")
    result["rows"][0] = {k: v for k, v in row.items() if k != "counterexample"}
    _refused(case, result, "row h6 does not have the fields of a follows row")
    case, response, _ = _genuine(service, "R-1")
    result = response["results"][0]["result"]
    result["rows"][0] = {**result["rows"][0], "certificate": None, "counterexample": None}
    _refused(case, result, "row c1 does not have the fields of a claim row")


def test_the_certificate_and_counterexample_are_rebound_nowhere(service):
    """Every name in the two fields rebound to each other string the request holds: only a free value at its place
    in declaration order, and only the derivation's link, are accepted."""
    case, result = _shown_row(service, "R-3", R3_CERTIFICATE, None)
    strings = {"r", "s", "d", "p1", "p2", "h6", "ve-calc@0", "assumption", "the velocity ratio"}
    paths = [("rows", 0, "certificate", 0, "farkas", "goal", "coeffs", 0, 0),
             ("rows", 0, "certificate", 1, "square", "square"), ("rows", 0, "certificate", 1, "square", "root")]
    accepted = {(path[-1], other) for path in paths for other in strings - {"s", "r"}
                if calc.answer_problem(_set(result, path, other), case) is None}
    assert accepted == {(0, "d")}  # a goal over another free value is still a fact over free values
    case, result = _shown_row(service, "R-4", None, R4_COUNTEREXAMPLE)
    for i in range(3):
        assert all(calc.answer_problem(_set(result, ("rows", 0, "counterexample", i, 0), other), case) is not None
                   for other in strings - {R4_COUNTEREXAMPLE[i][0]})
