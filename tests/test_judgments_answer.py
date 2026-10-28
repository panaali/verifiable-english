"""The relay of the `document` mode's `judgments` field (judgment-terms-PLAN.md JT-2, Python; docs/spec/
judgment-terms.md 8.3): schema and binding only (R8), and Lean's order.

Genuine answers come from the service for spec 11.3's documents. Each member of `judgments` is dropped, emptied,
retyped, duplicated or reordered, and a unit id or a term is pushed out of the request: every mutant is refused by
the generated schema (`check_row`) or by the binding (`_bind_document_answer`), which `_lean_document` turns into
`CheckerUnavailable`; a mutant equal to the genuine answer changes nothing shown and is skipped. Whether a unit uses
a term is Lean's; only the names, the ids and the order are bound.
"""
from __future__ import annotations

from copy import deepcopy
import json

import pytest

from tests.test_judgments_document import (ALPHA, J1, J2, PROFILES, STATUS, conj, document, norm, opened, record, u,
                                           unit)
from ve.backends.lean_service import LeanService
from ve.backends.service_schema import check_row
from ve.document import _bind_document_answer, _parts, _split

# Three units, the middle one using no judgment: a `units` list skips a unit of the request.
THREE = (J2, [unit("u1", opened("arbitrary"), ALPHA), unit("u2", content=norm(u("arrest"), name="s")),
              unit("u3", opened("arbitrary", "unreasonable"),
                   norm(conj(u("arrest"), u("arbitrary"), u("unreasonable")), name="t"))])
# Each genuine answer and its usage map as Lean answers it (used rows, unused names).
GENUINE = {
    "J-alpha": ((J1, STATUS["J-alpha"][1]), ([("arbitrary", ["u1"])], [])),
    "J-mu": ((J1, STATUS["J-mu"][1]), ([], ["arbitrary"])),
    "two-rows": ((STATUS["two-rows"][0], STATUS["two-rows"][1]),
                 ([("arbitrary", ["u2"]), ("unreasonable", ["u1", "u2"])], ["gives_serious_uplift", "court_ordered"])),
    "three": (THREE, ([("arbitrary", ["u1", "u3"]), ("unreasonable", ["u3"])], [])),
}


@pytest.fixture(scope="module")
def service():
    with LeanService() as instance:
        yield instance


@pytest.fixture(scope="module")
def genuine(service):
    """Per fixture: the case sent and Lean's row."""
    out = {}
    for name, ((records, units), _) in GENUINE.items():
        case = {"id": "d", "document": document(service, units, records), "admit": False}
        out[name] = case, service.run("document", [case])[0]
    return out


def relayed(case, row) -> bool:
    """Whether the relay accepts `row` for `case`: the generated schema, then the binding `_lean_document` runs."""
    raw = case["document"].encode("utf-8")
    meta, body, _ = _split(raw)
    try:
        check_row("document", row, case, 0)
        _bind_document_answer(body, meta, list(_parts(meta["units"])), row)
    except Exception:  # noqa: BLE001 - `_lean_document` answers any refusal `CheckerUnavailable`
        return False
    return True


@pytest.mark.parametrize("name", GENUINE)
def test_the_genuine_answer_is_relayed(genuine, name):
    case, row = genuine[name]
    usage = row["judgments"]
    assert ([(r["term"], r["units"]) for r in usage["used"]], usage["unused"]) == GENUINE[name][1]
    assert relayed(case, row)


RETYPES = (None, True, 7, 7.5, "7", [], {})


def mutants(value, path=()):
    """Each mutant of `value` (a `judgments` member) with its description: a member dropped, emptied, retyped,
    duplicated or reordered."""
    if path:
        for other in RETYPES:
            if type(other) is not type(value) or other != value:
                yield f"retype {path} {other!r}", other
    if isinstance(value, (str, list, dict)) and value:
        yield f"empty {path}", type(value)()
    if isinstance(value, dict):
        for key in value:
            yield f"drop {path + (key,)}", {k: v for k, v in value.items() if k != key}
            for label, inner in mutants(value[key], path + (key,)):
                yield label, {**value, key: inner}
    if isinstance(value, list):
        for i, item in enumerate(value):
            yield f"drop {path + (i,)}", value[:i] + value[i + 1:]
            yield f"duplicate {path + (i,)}", value[:i + 1] + [item] + value[i + 1:]
            for label, inner in mutants(item, path + (i,)):
                yield label, value[:i] + [inner] + value[i + 1:]
        if len(value) > 1:
            yield f"reorder {path}", value[::-1]
            yield f"rotate {path}", value[1:] + value[:1]


def rebinds(usage):
    """Each id or name pushed out of the request, or moved to a place the request gives it no right to."""
    for i, r in enumerate(usage["used"]):
        for j in range(len(r["units"])):
            for fresh in ("u999", "u0", "U1", ""):
                m = deepcopy(usage)
                m["used"][i]["units"][j] = fresh
                yield f"unit {i}.{j} -> {fresh!r}", m
        for fresh in ("undeclared", "arrest", ""):
            m = deepcopy(usage)
            m["used"][i]["term"] = fresh
            yield f"term {i} -> {fresh!r}", m
        m = deepcopy(usage)
        m["unused"].append(r["term"])
        yield f"term {i} also unused", m
        m = deepcopy(usage)
        m["used"].append(deepcopy(r))
        yield f"row {i} repeated", m
    for i, name in enumerate(usage["unused"]):
        for fresh in ("undeclared", "arrest", ""):
            m = deepcopy(usage)
            m["unused"][i] = fresh
            yield f"unused {i} -> {fresh!r}", m
        m = deepcopy(usage)
        m["used"].append({"term": name, "units": []})
        yield f"unused {i} as an empty row", m
    m = deepcopy(usage)
    m["extra"] = []
    yield "extra member", m


def lean_s(usage):
    """The mutants that stay bound: a unit dropped from a `units` list of two or more. Which units use a term is
    Lean's decision (R8: the relay binds and never recomputes it), and no display shows the map yet (jt-2c)."""
    return {f"drop {('used', i, 'units', j)}" for i, r in enumerate(usage["used"]) if len(r["units"]) > 1
            for j in range(len(r["units"]))}


@pytest.mark.parametrize("name", GENUINE)
def test_every_mutant_of_the_usage_map_is_refused(genuine, name):
    case, row = genuine[name]
    accepted = set()
    count = 0
    for label, mutated in [*mutants(row["judgments"]), *rebinds(row["judgments"])]:
        if json.dumps(mutated, sort_keys=True) == json.dumps(row["judgments"], sort_keys=True):
            continue  # changes nothing shown
        count += 1
        if relayed(case, {**row, "judgments": mutated}):
            accepted.add(label)
    assert count > 20 and accepted == lean_s(row["judgments"])


def test_the_field_is_there_exactly_under_the_profile(service, genuine):
    """Without the field under the profile the answer is unbound; with it, without the profile, it is extra."""
    case, row = genuine["J-alpha"]
    assert not relayed(case, {k: v for k, v in row.items() if k != "judgments"})
    plain = [p for p in PROFILES if p != "judgments@0"]
    case = {"id": "d", "document": document(service, STATUS["J-alpha"][1], J1, profiles=plain), "admit": False}
    row = service.run("document", [case])[0]
    assert "judgments" not in row and relayed(case, row)
    assert not relayed(case, {**row, "judgments": {"used": [{"term": "arbitrary", "units": ["u1"]}], "unused": []}})


# The order check at its boundaries (spec 8.3, A5): each list in the request's order is accepted, and the same
# members in any other order are refused, though every member is bound.
ORDERS = [
    ("used in declaration order", "three", {"used": [{"term": "arbitrary", "units": ["u1", "u3"]},
                                                     {"term": "unreasonable", "units": ["u3"]}], "unused": []}, True),
    ("units skipping a unit", "three", {"used": [{"term": "arbitrary", "units": ["u3"]},
                                                 {"term": "unreasonable", "units": ["u1"]}], "unused": []}, True),
    ("used terms reversed", "three", {"used": [{"term": "unreasonable", "units": ["u3"]},
                                               {"term": "arbitrary", "units": ["u1", "u3"]}], "unused": []}, False),
    ("units reversed", "three", {"used": [{"term": "arbitrary", "units": ["u3", "u1"]},
                                          {"term": "unreasonable", "units": ["u3"]}], "unused": []}, False),
    ("unused in declaration order", "two-rows", {"used": [], "unused": ["arbitrary", "unreasonable",
                                                                       "gives_serious_uplift", "court_ordered"]}, True),
    ("unused out of order", "two-rows", {"used": [], "unused": ["arbitrary", "unreasonable", "court_ordered",
                                                               "gives_serious_uplift"]}, False),
    ("a term missing", "two-rows", {"used": [], "unused": ["arbitrary", "unreasonable", "court_ordered"]}, False),
    ("one unit, the last", "J-alpha", {"used": [], "unused": ["arbitrary"]}, True),
]


@pytest.mark.parametrize("label, name, usage, accepted", ORDERS, ids=[o[0] for o in ORDERS])
def test_the_order_is_lean_s(genuine, label, name, usage, accepted):
    """Which terms a unit uses is Lean's: a bound map other than Lean's is relayed as it is (the binding decides no
    usage); only a map out of the request's order or naming is refused."""
    case, row = genuine[name]
    assert relayed(case, {**row, "judgments": usage}) == accepted
