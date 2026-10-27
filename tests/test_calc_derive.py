"""Derivations over rational unknowns in the `calc` mode (math-evidence ME-5, me-5c): spec 13.6's R-3 and R-4 and
the plan's physics fixtures H-6, H-6p, H-6n and H-6a through `ve_service`, the refusals of spec 3.1, and the
binding of a derivation row's `kind` to its request. Lean decides every row (`Check.run_sound`); the forged
certificate with a negative weight and H-6a's assignment s = 0, r = 1 are refused at the level of facts by the
`#guard`s of `lean/VE/Calc/DeriveExamples.lean`, which the service never takes from a request."""
from __future__ import annotations

import json

import pytest

from tests.lean_service_corpus import calc_cases
from tests.test_calc_service import _bound_request, _refused, ask, says, service  # noqa: F401 (the fixture)

R3 = next(case for case in calc_cases() if [c["id"] for c in case["claims"]] == ["h6"])


def h6(bound: str, n: str, links=(("s", "r"),), conclusion: str = "lt") -> dict:
    """H-6's case: p1, d = 0.4 s, and p2, d < `bound`; the derivation of "r is less than 1 divided by `n`"."""
    case = json.loads(json.dumps(R3))
    case["premises"][1]["claim"][2] = ["lit", bound]
    case["claims"][0]["claim"][1] = [conclusion, ["val", "r"], ["div", ["lit", "1"], ["lit", n]]]
    case["claims"][0]["claim"][3] = [list(link) for link in links]
    return case


def answer(service, case: dict):
    return says(ask(service, json.dumps([case]), 1)["results"][0]["result"])


@pytest.mark.parametrize("case, want", [
    (h6("0.02", "4"), ["h6 holds"]),  # H-6, R-3: "certainly less than one-fourth"
    (h6("0.01", "6"), ["h6 holds"]),  # H-6p: "probably less than one sixth"
    (h6("0.02", "5"), ["h6 fails"]),  # H-6n, R-4: "less than one fifth" does not follow
    (h6("0.02", "4", links=()), ["h6 fails"]),  # H-6a: without the link, r = 1 and s = 0 refute it
    (h6("0.02", "4", conclusion="le"), ["h6 holds"]),
])
def test_each_derivation_has_its_row(service, case, want):
    assert answer(service, case) == want


@pytest.mark.parametrize("edit, want", [
    (lambda c: c["claims"][0]["claim"][2].append("p3"), "UnknownPremise: p3"),
    (lambda c: c["claims"][0]["claim"][3].append(["s", "q"]), "UnknownLink: q"),
    (lambda c: c["premises"].append({"id": "p3", "claim": ["eq", ["val", "s"], ["mul", ["val", "r"], ["val", "r"]]],
                                     "support": "assumption"}),
     "NonlinearPremise: premises.2.claim.2 (declare a square link or name the product)"),
    (lambda c: c["claims"][0]["claim"].__setitem__(1, ["eq", ["val", "r"], ["lit", "1"]]),
     "InvalidInput: claims.0.claim.1 must be an lt, le, gt or ge claim"),
    (lambda c: c["premises"][0].pop("support"), "InvalidInput: premises.0.support is missing"),
    (lambda c: c["premises"].append({**c["premises"][0], "id": "h6"}), "DuplicateClaimId: h6"),
])
def test_refusals(service, edit, want):
    case = json.loads(json.dumps(R3))
    edit(case)
    assert answer(service, case) == want


def test_a_rows_kind_is_its_requests(service):
    """R8: a derivation's row says `follows` and a claim's says `claim`, each bound to the request's form."""
    request, response = _bound_request(service, R3)
    result = response["results"][0]["result"]
    assert [row["kind"] for row in result["rows"]] == ["follows"]
    _refused(response, request, {**result, "rows": [{**result["rows"][0], "kind": "claim"}]})
    _refused(response, request, {**result, "rows": [{**result["rows"][0], "kind": "identity"}]})
