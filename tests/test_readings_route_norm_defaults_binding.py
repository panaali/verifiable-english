"""The readings route binds its norm-defaults rows as the norm-defaults mode does (ndc1b-F6).

`readings-route` answers a case of no readings kind on the lower route (`Readings.Run.runLower`), so its row for a
`norm-defaults-status` or `norm-defaults-certificate` case is the norm-defaults runner's (`readings-route.json`'s
`norm-defaults.json#/row`). The schema types that row but cannot state two bindings: a status rule's echoed source is a
rule of the request, and a certificate row's `premises` is the count of the regenerated premises its certificate is
bound to. `MODE_BINDINGS["readings-route"]` applies the one owner of both, `_bind_norm_defaults`; every other
readings-route row binds as before. The rows are built by hand to the row schema (no service), and the client path is
the scripted fake of tests/test_lean_service.py.
"""
from __future__ import annotations

import json

import pytest

from tests.test_lean_service import fake
from ve.backends.lean_service import Invalid, LeanService, bind_answers
from ve.backends.service_schema import check_row
from ve.errors import CheckerUnavailable

MODE = "readings-route"
PROFILES = ["norm-defaults@0", "norms@0", "readings@1"]
RULE = {"norm": {"name": "r1", "predicate": "p", "sign": True, "guard": ["top"], "unless": [], "over": []}}
# Three premise meaning ids, one the case's own premise: the certificate is bound to two regenerated premises.
CERTIFICATE_CASE = {"id": "certificate", "kind": "norm-defaults-certificate", "environment": {"profiles": PROFILES},
                    "norms": [RULE], "premises": [["top"]], "conclusion": ["top"],
                    "certificate": {"premise_meaning_ids": ["m1", "m2", "m3"]}}
CERTIFICATE_ROW = {"id": "certificate", "status": "ok", "valid": True, "premises": 2}
STATUS_CASE = {"id": "status", "kind": "norm-defaults-status", "environment": {"profiles": PROFILES},
               "norms": [RULE], "predicate": "p", "tuple": ["a"], "method": "table3"}
STATUS_ROW = {"id": "status", "status": "ok", "point_status": "SETTLED yes", "predicate": "p", "tuple": ["a"],
              "rules": ["r1"], "sources": [{"rule": "r1", "source": "r1"}], "differs": []}


def _relayed(case: dict, row: dict) -> None:
    """The client's two checks of one `ok` row: its schema (`check_row`), then its request binding (`bind_answers`)."""
    check_row(MODE, row, case, 0)
    bind_answers(MODE, {"status": "ok", "results": [{"index": 0, "result": row}]}, {"cases": [case]})


def _scripted(tmp_path, case, row):
    """The client's answer when the service sends `row` for `case` under readings-route."""
    answer = {"id": "__nonce__", "status": "ok", "mode": MODE, "results": [row],
              "counts": {"cases": 1, "bytes": "__bytes__", "errors": 0}}
    (tmp_path / "marker").write_text(json.dumps(answer))
    with LeanService(fake(tmp_path, "scripted"), allow_unlisted_build=True) as service:
        return service.run(MODE, [case])


def test_readings_route_binds_norm_defaults_certificate_count(tmp_path):
    """Astra's probe: a schema-valid certificate row with a forged `premises` count is refused under readings-route,
    as under norm-defaults (it passed on main); the genuine count still passes; and the status-rule binding
    (`_bind_status_rules`) applies under readings-route too."""
    for count in (999, 3, 1, 0):  # forged, every id, one fewer, none
        forged = {**CERTIFICATE_ROW, "premises": count}
        check_row(MODE, forged, CERTIFICATE_CASE, 0)  # schema-valid: only the binding refuses it
        with pytest.raises(Invalid, match="premises is not the count its certificate is bound to"):
            _relayed(CERTIFICATE_CASE, forged)
    _relayed(CERTIFICATE_CASE, CERTIFICATE_ROW)
    # Status rules: a rule the request does not hold, or one echoed from another source, is no answer.
    for rule, source in (("ghost", "ghost"), ("ghost", "r1"), ("r1", "ghost")):
        with pytest.raises(Invalid, match="no rule of the request"):
            _relayed(STATUS_CASE, {**STATUS_ROW, "rules": [rule], "sources": [{"rule": rule, "source": source}]})
    _relayed(STATUS_CASE, STATUS_ROW)
    # Through the client: the forged row is no answer, the genuine one is relayed.
    with pytest.raises(CheckerUnavailable, match="malformed response"):
        _scripted(tmp_path, CERTIFICATE_CASE, {**CERTIFICATE_ROW, "premises": 999})
    [relayed] = _scripted(tmp_path, CERTIFICATE_CASE, CERTIFICATE_ROW)
    assert relayed["premises"] == 2


DEEP: list = [[]]
for _ in range(10_000):
    DEEP = [DEEP]
RETYPED = [7, True, None, [], {}, 1.5, "\ud800", "", "2", [7], [None], -1, DEEP]


@pytest.mark.parametrize("case, row, field", [
    (CERTIFICATE_CASE, CERTIFICATE_ROW, "id"), (STATUS_CASE, STATUS_ROW, "id"),
    (CERTIFICATE_CASE, CERTIFICATE_ROW, "premises"), (CERTIFICATE_CASE, CERTIFICATE_ROW, "valid"),
    (STATUS_CASE, STATUS_ROW, "rules"), (STATUS_CASE, STATUS_ROW, "sources"), (STATUS_CASE, STATUS_ROW, "tuple")])
def test_readings_route_norm_defaults_field_deleted_or_retyped(case, row, field):
    """Each typed and bound field deleted or retyped: the schema or the binding refuses the row under readings-route."""
    mutants = [{k: v for k, v in row.items() if k != field}]
    # No rule deciding is an answer Lean gives (UNKNOWN): `rules: []` with no echo is no forgery, so it is not here;
    # nor is the genuine value itself (`valid: True`).
    mutants += [{**row, field: value} for value in RETYPED if not (field == "rules" and value == [])
                and not (type(value) is type(row[field]) and value == row[field])]
    for mutant in mutants:
        with pytest.raises(Invalid):
            _relayed(case, mutant)


@pytest.mark.parametrize("rules, sources", [
    (["r1", "r1"], [{"rule": "r1", "source": "r1"}] * 2),  # a duplicated row
    (["r1", "absent"], [{"rule": "r1", "source": "r1"}, {"rule": "absent", "source": "absent"}]),  # an extra row
    (["r1"], []),  # an empty echo list
    (["r1"], [{"rule": "r1", "source": "r1"}] * 2),  # one echo too many
    (["absent"], [{"rule": "absent", "source": "r1"}])])  # a generated name outside acts@0 and rights@0
def test_readings_route_status_rows_extra_duplicated_or_empty(rules, sources):
    """A status row under readings-route with a duplicated, extra or undeclared rule, or an echo list that is not one
    echo per rule, is refused by the schema or by `_bind_status_rules`; the genuine row passes (the test above)."""
    with pytest.raises(Invalid):
        _relayed(STATUS_CASE, {**STATUS_ROW, "rules": rules, "sources": sources})


@pytest.mark.parametrize("missing", ["certificate", "premises"])
def test_readings_route_certificate_case_without_its_certificate_has_no_count(missing):
    """No certificate (or no premise list) in the request: no premise count binds, so no `ok` row is an answer."""
    case = {k: v for k, v in CERTIFICATE_CASE.items() if k != missing}
    with pytest.raises(Invalid, match="premises is not the count"):
        _relayed(case, CERTIFICATE_ROW)


def test_other_readings_route_rows_bind_as_before():
    """Only the two norm-defaults kinds gain a binding: a readings kind, a norms kind, a norm-defaults kind the
    norm-defaults mode does not bind, and an error row of a certificate case are relayed as before."""
    others = [({"kind": "readings-elaborate"}, {"status": "ok", "premises": 999}),
              ({"kind": "readings-verdicts"}, {"status": "ok", "rules": ["ghost"]}),
              ({"kind": "norms-certificate", "premises": []}, {"status": "ok", "premises": 999}),
              ({"kind": "norm-defaults-elaborate"}, {"status": "ok", "rules": ["ghost"]}),
              (CERTIFICATE_CASE, {"status": "error", "error": "UnsupportedProfile: no"})]
    for case, row in others:
        bind_answers(MODE, {"status": "ok", "results": [{"index": 0, "result": row}]}, {"cases": [case]})
