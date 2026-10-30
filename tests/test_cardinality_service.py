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
    "document-fa1": "ok", "document-leaf-dropped": STALE,
    "document-unproved": "graph rejected: cycle, duplicate name, dangling premise or invalid certificate",
    "document-no-profile": "UnsupportedProfile: cardinality documents require documents@1",
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
    stale certificate refused, and one case per diagnostic class of the hostile set, in spec 4.2's order; FA1 as a
    claim graph, with a leaf dropped, unproved and without `documents@1`."""
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


# Values every typed member refuses (BUILDER-CHECKLIST 1).
BAD = (7, True, None, [], {}, 1.5, "\ud800", [[[]]])


def test_document_rows_are_typed_and_bound(service):
    """qt-a3d, R8: the report names the request's root and its nodes only; each retyped or rebound member is
    refused."""
    case = next(case for case in route_cases() if case["id"] == "document-fa1")
    request, response = exchange(service, [case])
    row = response["results"][0]["result"]
    report, leaves = row["report"], row["report"]["leaves"]
    assert [leaf["name"] for leaf in leaves] == ["total", "increase", "stay", "exclusive"]
    for mutant in ({**row, "report": {**report, "root": {**report["root"], "name": "total"}}},
                   {**row, "report": {**report, "leaves": [{**leaves[0], "name": "unknown"}, *leaves[1:]]}},
                   {**row, "report": {**report, "leaves": [{**leaves[0], "meaning_id": 3}, *leaves[1:]]}},
                   {**row, "report": {**report, "leaves": [{**leaves[0], "formula": ["most"]}, *leaves[1:]]}},
                   {**row, "report": {**report, "extra": []}},
                   {k: v for k, v in row.items() if k != "report"}, {**row, "premises": []}, {**row, "valid": True},
                   {k: v for k, v in row.items() if k != "report_id"},
                   *({**row, key: bad} for key in row for bad in BAD),
                   *({**row, "report": {**report, "root": {**report["root"], key: bad}}}
                     for key in report["root"] for bad in BAD),
                   *({**row, "report": {**report, "leaves": [{**leaves[0], key: bad}, *leaves[1:]]}}
                     for key in leaves[0] for bad in BAD)):
        mutated = deepcopy(response)
        mutated["results"][0]["result"] = mutant
        with pytest.raises(Invalid):
            check_response("cardinality", mutated, request)


def _report_mutants(report):
    """(label, report) of FA1's document report with one fault each (review F1 of qt-a3d)."""
    root, leaves = report["root"], report["leaves"]
    yield "leaves emptied", {**report, "leaves": []}
    yield "a leaf dropped", {**report, "leaves": leaves[1:]}
    yield "a leaf duplicated", {**report, "leaves": [*leaves, leaves[0]]}
    yield "leaves reordered", {**report, "leaves": leaves[::-1]}
    yield "meaning ids swapped", {**report, "leaves": [{**leaves[0], "meaning_id": leaves[1]["meaning_id"]},
                                                       {**leaves[1], "meaning_id": leaves[0]["meaning_id"]}, *leaves[2:]]}
    yield "formulas swapped", {**report, "leaves": [{**leaves[0], "formula": leaves[1]["formula"]},
                                                    {**leaves[1], "formula": leaves[0]["formula"]}, *leaves[2:]]}
    yield "a leaf as the root", {**report, "root": {**leaves[0], "name": root["name"]}}


def test_document_report_id_binds_both_identities_the_document_and_the_report(service):
    """Review F1 of qt-a3d (spec 4.1: reports carry both identities and bind both): `report_id` is the `ve-report`
    digest, in the environment's identity version, of the cardinality and both W6a identities, the document as sent
    and the report, as `VE.Time.Document.runDocument`'s; so a report with its leaves emptied, dropped, duplicated or
    reordered, its meaning ids or formulas swapped, or a leaf as its root, is not the report `report_id` names, and
    neither is the same report beside another document or other identities. QT-A4's relay checks this digest."""
    from ve.wire import digest
    case = next(case for case in route_cases() if case["id"] == "document-fa1")
    _, response = exchange(service, [case])
    row = response["results"][0]["result"]
    profiles = case["environment"]["profiles"]
    assert profiles == sorted(profiles) and profiles[0] == "cardinality@0"

    def identity(report, document=case["document"], **ids):
        identities = {key: row[key] for key in ("environment_id", "w6_environment_id", "w6_target_environment_id")}
        return digest(f"ve-report-v0.2:{','.join(profiles)}\n",
                      {**identities, **ids, "document": document, "report": report})
    assert row["report_id"] == identity(row["report"])
    labels = []
    for label, report in _report_mutants(row["report"]):
        assert report != row["report"] and identity(report) != row["report_id"], label
        labels.append(label)
    assert len(labels) == 7
    other = {**case["document"], "nodes": [*case["document"]["nodes"], {"name": "unused", "statement": case[
        "document"]["nodes"][0]["statement"]}]}
    assert identity(row["report"], other) != row["report_id"]
    for key in ("environment_id", "w6_environment_id", "w6_target_environment_id"):
        assert identity(row["report"], **{key: row["w6_environment_id" if key == "environment_id" else
                                              "environment_id"]}) != row["report_id"], key
    # The same report beside another document is answered under that document's identity.
    _, other_response = exchange(service, [{**case, "document": other}])
    other_row = other_response["results"][0]["result"]
    assert other_row["report"] == row["report"] and other_row["report_id"] == identity(row["report"], other)


def universal(i: int, depth: int = 6, bits: int = 4) -> dict:
    """F5 of the qt-a3c loop recheck: a universal statement over the counted sort whose first `depth` conjuncts every
    statement shares; only the last `bits` connectives (the bits of `i`) tell two statements apart."""
    def unary(p):
        return ["unary", p, ["var", 0]]

    def common(d):
        return unary("expects_further_increase") if d == 0 else ["and", common(d - 1), unary("expects_rates_to_stay")]

    def tail(b):
        if b == 0:
            return unary("expects_further_increase")
        return ["and" if (i >> (b - 1)) & 1 else "or", tail(b - 1), unary("expects_rates_to_stay")]
    return {"format": "ve-cardinality@1",
            "formula": ["quantity", ["forall", "fomc_policymaker", ["and", common(depth), tail(bits)]]]}


def test_universals_are_bridged_once_in_first_use_order(service):
    """F5 of the qt-a3c loop recheck: the counted universal statements are deduplicated in near-linear time (a hash
    set, `firstUseH_eq` and the `@[csimp]` lemmas of `VE/Cardinality/Regions.lean`). Sixteen statements that differ
    only at the end, then each again in reverse order: the erased problem bridges each once, in first-use order, so
    its region premises and bridges are the sixteen-statement request's, and the erased premises follow them."""
    base = next(case for case in route_cases() if case["id"] == "p3-charged")
    count = {"format": "ve-cardinality@1", "formula": ["count", "fomc_policymaker", [["1", ["any"]]], "eq", "18"]}
    top = {"format": "ve-cardinality@1", "formula": ["quantity", ["top"]]}
    distinct = [universal(i) for i in range(16)]
    once, twice = ({**base, "id": name, "premises": [count, *premises], "conclusion": top}
                   for name, premises in (("once", distinct), ("twice", distinct + distinct[::-1])))
    first, second = (bound["result"] for bound in exchange(service, [once, twice])[1]["results"])
    assert first["status"] == second["status"] == "ok", (first, second)
    assert first["regions"] == second["regions"]
    assert first["regions"]["predicates"] == {"fomc_policymaker": ["expects_further_increase", "expects_rates_to_stay"]}
    regions, shared = len(first["regions"]["constants"]), len(first["regions"]["constants"]) + len(distinct)
    assert len({json.dumps(bridge) for bridge in first["erased"]["premises"][regions:shared]}) == len(distinct)
    assert len(first["erased"]["premises"]) == shared + 1 + len(distinct)
    assert len(second["erased"]["premises"]) == shared + 1 + 2 * len(distinct)
    assert second["erased"]["premises"][:shared] == first["erased"]["premises"][:shared]
