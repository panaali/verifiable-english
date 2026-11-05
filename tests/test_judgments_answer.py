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


def deep(n=10_000):
    value = []
    for _ in range(n):
        value = [value]
    return value


RETYPES = (None, True, 7, 7.5, "7", "\ud800", [], {}, deep())


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
    """The mutants that stay bound: a unit dropped from a `units` list of two or more, when another term still lists
    it (`judgment_lines` has its status row, jt-3b). Which units use a term is Lean's decision (R8: the relay binds and
    never recomputes it), and no display shows the map yet (jt-2c)."""
    listed = [unit for r in usage["used"] for unit in r["units"]]
    return {f"drop {('used', i, 'units', j)}" for i, r in enumerate(usage["used"]) if len(r["units"]) > 1
            for j, unit in enumerate(r["units"]) if listed.count(unit) > 1}


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


def rebind_lines(lines, unit_ids):
    """Each term or unit of `judgment_lines` pushed out of the request, or to a place the request gives it no right to."""
    def changed(fn):
        m = deepcopy(lines)
        fn(m)
        return m
    for i, r in enumerate(lines["legend"]):
        for fresh in ("undeclared", "arrest", ""):
            yield f"legend {i} -> {fresh!r}", changed(lambda m: m["legend"][i].update(term=fresh))
        yield f"legend {i} repeated", changed(lambda m: m["legend"].append(deepcopy(r)))
        yield f"legend {i} without a line", changed(lambda m: m["legend"][i].update(lines=[]))
        yield f"legend {i} with an empty line", changed(lambda m: m["legend"][i]["lines"].append(""))
        yield f"legend {i} with an extra member", changed(lambda m: m["legend"][i].update(extra=1))
    for i, r in enumerate(lines["status"]):
        for fresh in ("u999", "u0", "U1", ""):
            yield f"status {i} -> {fresh!r}", changed(lambda m: m["status"][i].update(unit=fresh))
        yield f"status {i} repeated", changed(lambda m: m["status"].append(deepcopy(r)))
        yield f"status {i} with an empty line", changed(lambda m: m["status"][i].update(line=""))
        yield f"status {i} with an extra member", changed(lambda m: m["status"][i].update(extra=1))
    used = {r["unit"] for r in lines["status"]}
    for fresh in unit_ids:
        if fresh not in used:
            # A unit of the request that uses no judgment: a row Lean did not write.
            yield f"status for unused {fresh}", changed(lambda m: m["status"].append({"unit": fresh, "line": "Open."}))
    yield "extra member", changed(lambda m: m.update(extra=[]))


def lean_s_lines(lines):
    """The mutants that stay bound: the text is Lean's and only typed (R8), so another string in its place is relayed
    (`RETYPES`' "7"), and a row of two or more lines may lose one or be reordered; a row keeps at least one."""
    out = {f"retype {('status', i, 'line')} '7'" for i in range(len(lines["status"]))}
    for i, r in enumerate(lines["legend"]):
        out |= {f"retype {('legend', i, 'lines', j)} '7'" for j in range(len(r["lines"]))}
        if len(r["lines"]) > 1:
            out |= {f"drop {('legend', i, 'lines', j)}" for j in range(len(r["lines"]))}
            out |= {f"reorder {('legend', i, 'lines')}", f"rotate {('legend', i, 'lines')}"}
    return out


LINES_GENUINE = {**GENUINE, "decider": (((
    record("arbitrary", decided_by="governance_function", factors=["the source", "the budget"]),),
    STATUS["J-alpha"][1]), ([("arbitrary", ["u1"])], []))}


@pytest.mark.parametrize("name", LINES_GENUINE)
def test_every_mutant_of_the_lines_is_refused(service, name):
    """R8: drop, empty, retype, duplicate and reorder each member of `judgment_lines`, and rebind each term and unit.
    The text itself is only typed: a changed word is relayed, as `test_a_changed_word_of_the_text_is_lean_s` states."""
    (records, units), _ = LINES_GENUINE[name]
    case = {"id": "d", "document": document(service, units, records), "admit": False}
    row = service.run("document", [case])[0]
    lines = row["judgment_lines"]
    assert relayed(case, row) and lines["legend"] and {r["term"] for r in lines["legend"]} == {r["name"] for r in records}
    unit_ids = [x["id"] for x in units]
    accepted, count = set(), 0
    for label, mutated in [*mutants(lines), *rebind_lines(lines, unit_ids)]:
        if json.dumps(mutated, sort_keys=True) == json.dumps(lines, sort_keys=True):
            continue
        count += 1
        if relayed(case, {**row, "judgment_lines": mutated}):
            accepted.add(label)
    assert count > 15 and accepted == lean_s_lines(lines)


def test_a_changed_word_of_the_text_is_lean_s(service):
    """The relay holds no word list and decides nothing about the text (R8, plan JT-3): only its type is checked."""
    (records, units), _ = GENUINE["J-alpha"]
    case = {"id": "d", "document": document(service, units, records), "admit": False}
    row = service.run("document", [case])[0]
    changed = deepcopy(row["judgment_lines"])
    changed["status"][0]["line"] = "Another line."
    assert relayed(case, {**row, "judgment_lines": changed})


def test_the_lines_are_there_exactly_under_the_profile(service, genuine):
    case, row = genuine["J-alpha"]
    assert not relayed(case, {k: v for k, v in row.items() if k != "judgment_lines"})
    plain = [p for p in PROFILES if p != "judgments@0"]
    case = {"id": "d", "document": document(service, STATUS["J-alpha"][1], J1, profiles=plain), "admit": False}
    row = service.run("document", [case])[0]
    assert "judgment_lines" not in row and relayed(case, row)
    assert not relayed(case, {**row, "judgment_lines": {"legend": [], "status": []}})


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
    # The status rows stand for the units this map lists, so that only the map's own binding is at stake.
    using = sorted({unit for r in usage["used"] for unit in r["units"]})
    lines = {**row["judgment_lines"], "status": [{"unit": unit, "line": "Open."} for unit in using]}
    assert relayed(case, {**row, "judgments": usage, "judgment_lines": lines}) == accepted


# `ve/openterms.py` off the live document path (JT-2, Python): a rights document Lean's `document` mode answers takes
# its open terms from the names Lean's W2 check accepted, and a malformed record is Lean's diagnostic.
OPEN_TERM = {"name": "z_open", "arguments": [], "decided_by": "court", "necessary": [], "sufficient": [],
             "factors": [], "precedents": [], "jurisdiction": "x", "version": 1}
RIGHTS_OPEN_TERMS = {
    "declared": ([OPEN_TERM], False, None),
    "an open unit": ([OPEN_TERM], True, None),
    "schema": ([{"name": "z_open"}], False, "invalid open-term schema"),
    "version": ([{**OPEN_TERM, "version": 0}], False, "invalid open-term version"),
    "repeated": ([OPEN_TERM, OPEN_TERM], False, "duplicate or invalid open term"),
    "undeclared": ([], True, "invalid meaning status"),
}


@pytest.mark.parametrize("name", RIGHTS_OPEN_TERMS)
def test_a_rights_document_reads_lean_s_open_terms(tmp_path, name):
    from tests.test_b16e_rights_document import _both, _join, _split, _text
    terms, opened, refusal = RIGHTS_OPEN_TERMS[name]
    meta, body = _split(_text(0))
    meta["open_terms"] = terms
    if opened:
        meta["units"][0]["meaning"] = {"open": ["z_open"]}
    path = tmp_path / "rights.ve.md"
    path.write_text(_join(meta, body))
    decided, new, old = _both(path)
    assert decided and new == old
    assert [o.get("raised", {}).get("message") for o in new] == [refusal, refusal]


def test_openterms_is_imported_only_where_the_layer_policy_retains_it():
    import ast
    from pathlib import Path
    from tools.layer_policy import RETAINED
    root = Path(__file__).resolve().parents[1]
    importers = set()
    for path in root.glob("**/*.py"):
        relative = path.relative_to(root).as_posix()
        if relative.startswith((".venv/", "lean/.lake/", ".git/")):
            continue
        package = ".".join(path.relative_to(root).with_suffix("").parts[:-1])
        for node in ast.walk(ast.parse(path.read_bytes())):
            names = []
            if isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:
                    base = ".".join([*package.split(".")[:len(package.split(".")) - node.level + 1], base]).strip(".")
                names = [base, *(f"{base}.{a.name}" for a in node.names)]
            elif isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            if "ve.openterms" in names:
                importers.add(relative)
    assert importers == set(RETAINED["ve.openterms"])
