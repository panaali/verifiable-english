"""The `cardinality` service mode (quantities QT-A3, qt-a3c): Lean's answers to the mode's route cases in
`tests/data/route-cases.jsonl` through `ve_service`, each checked against `cardinality.json` and bound to its
request: one statement per request premise, each region constant of a request finite sort, and the case's kind."""
from __future__ import annotations

from copy import deepcopy
import json

import pytest

from tests.lean_build import lean_build
from tests.lean_service_corpus import cardinality_cases as route_cases
from tests.subprocesses import HANG_TIMEOUT
from ve.backends.lean_service import LeanService, case_digest, case_texts
from ve.backends.service_schema import MODES, Invalid, check_response

STALE = "cardinality certificate is stale or bound to different statements"
# Each route case's answer, in the file's order: `ok` with its certificate verdict, or the refusal.
EXPECTED = {
    "fa1": "ok", "fa1-certificate": "ok valid", "fa1b": "ok", "fa1b-certificate": "ok invalid", "fa1-claimed": "ok",
    "forged-regions": "region table differs from the regenerated one",
    "forged-erased": "erased problem differs from the regenerated one",
    "fa11-stale": STALE,
    "certificate-malformed": "Invalid cardinality certificate: fields do not match: expected [format, "
                             "environment_id, premise_meaning_ids, conclusion_meaning_id, w6], got []",
    "kind-countermodel": "unknown case kind countermodel",
    "e2-profiles": "UnsupportedProfile: cardinality@0 requires order@0, relational-fol@0 and time@0, optionally "
                   "with documents@1",
    "s1-format": "Unsupported cardinality format",
    "s5-not-finite": "CardinalityNotFinite(user)",  # the plan's seeded bug
    "s7-terms": "ResourceLimit: At most 64 terms in a count",
    "s8-range": "ProportionRange(3 in 2)",
    "s10-rule": "UnsupportedRounding(down)",
    "p1-sorts": "ResourceLimit: At most 8 counted sorts",
    "p2-predicates": "ResourceLimit: At most 6 predicates on counted sort fomc_policymaker (64 regions)",
    "p3-charged": "ResourceLimit: premises and conclusion exceed aggregate 10000-node limit",
}


@pytest.fixture(scope="module")
def service():
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as running:
        yield running


def exchange(service, cases):
    text = json.dumps(cases, ensure_ascii=False)
    _, response = service.exchange("cardinality", text, len(cases), timeout=HANG_TIMEOUT)
    request = {"id": response["id"], "mode": "cardinality", "cases": cases,
               "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
    check_response("cardinality", response, request)
    return request, response


def says(result: dict) -> str:
    if result["status"] != "ok":
        return result["error"]
    return "ok" + {None: "", True: " valid", False: " invalid"}[result.get("valid")]


def test_route_cases_answer_as_recorded(service):
    """FA1 and FA1b admitted and certified (FA1b's trace does not close its problem), forged claims and FA11's
    stale certificate refused, and one case per diagnostic class of the hostile set, in spec 4.2's order."""
    cases = route_cases()
    assert "cardinality" in MODES and [case["id"] for case in cases] == list(EXPECTED)
    answers = [says(bound["result"]) for bound in exchange(service, cases)[1]["results"]]
    assert dict(zip(EXPECTED, answers)) == EXPECTED


def _mutants(row):
    """(label, row) of FA1's admission rebound or retyped, one fault each."""
    constants = row["regions"]["constants"]
    yield "a premise dropped", {**row, "premises": row["premises"][1:]}
    yield "a premise added", {**row, "premises": [*row["premises"], row["conclusion"]]}
    yield "a constant of another sort", {**row, "regions": {**row["regions"], "constants": [
        {**constants[0], "sort": "user"}, *constants[1:]]}}
    yield "bits not a region", {**row, "regions": {**row["regions"], "constants": [
        {**constants[0], "bits": "2"}, *constants[1:]]}}
    yield "id rebound", {**row, "id": "other"}
    yield "identity retyped", {**row, "w6_environment_id": 7}
    yield "identity not a digest", {**row, "environment_id": "x"}
    yield "a formula retyped", {**row, "conclusion": {**row["conclusion"], "formula": "x"}}
    yield "an unknown operator", {**row, "conclusion": {**row["conclusion"], "formula": ["most", "x"]}}
    for member in ("regions", "erased", "premises", "w6_target_environment_id"):
        yield f"{member} dropped", {k: v for k, v in row.items() if k != member}
    yield "an admission's valid", {**row, "valid": True}
    yield "an extra member", {**row, "bridges": []}


def test_answers_are_typed_and_bound_to_their_request(service):
    """R8: every mutant of a genuine answer is refused by the schema; a certificate row needs its verdict."""
    cases = route_cases()
    request, response = exchange(service, cases[:2])

    def refused(index, result):
        mutated = deepcopy(response)
        mutated["results"][index]["result"] = result
        with pytest.raises(Invalid):
            check_response("cardinality", mutated, request)
    admission, certificate = (bound["result"] for bound in response["results"])
    for label, row in _mutants(admission):
        refused(0, row)
    refused(1, {k: v for k, v in certificate.items() if k != "valid"})
    refused(1, {**certificate, "valid": "true"})
    refused(1, {**certificate, "regions": admission["regions"]})
