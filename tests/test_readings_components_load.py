"""The answers Lean gives at load for a document with companion sets, as untrusted output (docs/spec/readings-defaults.md
1.9, 3; plan RD-4b; build checklist 4 and 5; review B2 of rd-4b).

`readings_components.load` asks Lean, in one request, for the split's elaboration (each case's environment, document,
checked part and route), its validation and the product's conflict answer without evidence. Their schema is
generated from Lean's encoders (`elaborate_components`, `validate_components`, `verdicts_components`; a case's
environment, document and checked part are objects, `Readings.Run.asObject`) and every check of them runs inside one
guard (`readings_verdicts.relayed`), so a malformed answer is `CheckerUnavailable`, never a crash nor a verdict. Each
case is bound to the request by its name (`_bind_part`): its document is the request's projection on it
(`_projection`, Lean's `mainDoc` and `componentDoc`) row for row, the main case's environment is the request's, a
companion case's environment and open terms its companions' united, and the document its answer reads is its
document or the main case's fixed part.

The fuzz takes the genuine answers of F-C1 and F-C17 and retypes, drops, empties and duplicates every field; each
mutant must be refused, except the values listed in `LEAN_OWNED` with the Lean definition that owns them. The graft
fuzz (review B2 of rd-4b looprecheck 1) puts the request's own rows where the split does not: every unit, set,
narrowing and coupling of the request, in every form a unit takes in a split, inserted into each case, and each
case's lists reordered.
"""
from __future__ import annotations

import copy

import pytest

from tests import lean_routes
from tests.test_readings_components_lean import _DROP, _paths, _set, _type
from ve.errors import CheckerUnavailable

KINDS = ["readings-elaborate", "readings-validate", "readings-verdicts"]
ROWS = ("elaborate", "validate", "product")


@pytest.fixture(scope="module", autouse=True)
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def _capture(path):
    """The genuine rows Lean answers `load`'s request with, and `load`'s arguments, for the document at `path`."""
    from ve import readings_components, readings_route
    from ve.document import load_document
    captured = {}
    real_run, real_load = readings_route.run_lean, readings_components.load

    def run(cases, **kw):
        rows = real_run(cases, **kw)
        if [c["kind"] for c in cases] == KINDS:
            captured["rows"] = copy.deepcopy(rows)
        return rows

    def load(*args, **kw):
        captured["args"] = (args, kw)
        return real_load(*args, **kw)
    readings_route.run_lean, readings_components.load = run, load
    try:
        load_document(path)
    finally:
        readings_route.run_lean, readings_components.load = real_run, real_load
    return captured


NARROWING = {"id": "n1", "set": "rs_a", "version": 1, "keeps": ["every"], "by": "w", "reason_spans": ["u0"]}


@pytest.fixture(scope="module")
def genuine(tmp_path_factory):
    from tests.test_readings_components_document import fc1, fc17
    tmp = tmp_path_factory.mktemp("rd4b-load")
    return {"F-C1": _capture(fc1(tmp)), "F-C17": _capture(fc17(tmp)),
            "F-C11": _capture(fc1(tmp_path_factory.mktemp("rd4b-load-fc11"), narrowings=[NARROWING]))}


def _load(captured, rows):
    """`load` on the captured request with Lean's rows replaced by `rows` (no service call)."""
    from ve import readings_components, readings_route
    real = readings_route.run_lean
    readings_route.run_lean = lambda cases, **kw: copy.deepcopy(rows)
    try:
        args, kw = captured["args"]
        return readings_components.load(*args, **kw)
    finally:
        readings_route.run_lean = real


def _refused(captured, rows):
    """True when `load` refuses the rows with `CheckerUnavailable`; any other exception escapes and fails the test."""
    try:
        _load(captured, rows)
    except CheckerUnavailable:
        return True
    return False


def _with(captured, k, path, new):
    rows = copy.deepcopy(captured["rows"])
    rows[k] = _set(rows[k], path, new)
    return rows


def test_the_genuine_answers_load(genuine):
    for captured in genuine.values():
        loaded = _load(captured, captured["rows"])
        assert [p["name"] for p in loaded["parts"]] == ["main", "rs_a", "rs_b"]


def test_a_case_s_frame_of_another_type_is_refused(genuine):
    """The finding's probes: `checked` or `document` set to 7 escaped as a raw TypeError, a duplicated reading set as
    a bare ValueError."""
    captured = genuine["F-C1"]
    for i in range(3):
        for field in ("environment", "document", "checked"):
            for value in (7, True, None, "x", [], {}):
                assert _refused(captured, _with(captured, 0, ("components", i, field), value)), (i, field, value)
    rows = copy.deepcopy(captured["rows"])
    sets = rows[0]["components"][1]["document"]["reading_sets"]
    sets.append(copy.deepcopy(sets[0]))
    assert _refused(captured, rows)


def test_each_case_is_bound_by_its_name(genuine):
    captured = genuine["F-C1"]
    # the companion cases' documents (and checked parts) swapped: every set still lands once, under the other name
    rows = copy.deepcopy(captured["rows"])
    a, b = rows[0]["components"][1], rows[0]["components"][2]
    for field in ("document", "checked"):
        a[field], b[field] = b[field], a[field]
    assert _refused(captured, rows)
    # a companion environment that invents a declaration, or loses one of its readings'
    rows = copy.deepcopy(captured["rows"])
    rows[0]["components"][1]["environment"]["vocabulary"]["predicates"]["zz"] = {"arguments": [], "description": "z"}
    assert _refused(captured, rows)
    rows = copy.deepcopy(captured["rows"])
    predicates = rows[0]["components"][1]["environment"]["vocabulary"]["predicates"]
    predicates.pop(next(iter(predicates)))
    assert _refused(captured, rows)
    # the main case without one of the document's units, or with the companion cases' checked part
    rows = copy.deepcopy(captured["rows"])
    rows[0]["components"][0]["document"]["units"].pop()
    assert _refused(captured, rows)
    rows = copy.deepcopy(captured["rows"])
    rows[0]["components"][1]["checked"] = {**rows[0]["components"][1]["checked"], "reading_sets": []}
    assert _refused(captured, rows)


def test_a_companion_case_holding_an_uncited_unit_is_refused(genuine):
    """Review B2 of rd-4b looprecheck 1: the main unit `u0` added to `rs_a`'s document and checked part (both, so the
    two still agree) by id alone, the form a cited unit takes, was accepted and stored as `['u0', 'u_a']`; Lean's
    `componentDoc` gives `rs_a` only `u_a`. Each form of `u0` is refused."""
    captured = genuine["F-C1"]
    u0 = _request(captured)["units"][0]
    assert u0["id"] == "u0"
    for form in _forms(u0):
        rows = copy.deepcopy(captured["rows"])
        for field in ("document", "checked"):
            rows[0]["components"][1][field]["units"].insert(0, copy.deepcopy(form))
        assert _refused(captured, rows), form


def _forms(unit):
    """A unit as the split may carry it: as written, without its content, by id alone."""
    return [unit, {k: v for k, v in unit.items() if k != "content"}, {"id": unit["id"]}]


def _request(captured):
    """The document `load` sends Lean, as its request carries it."""
    from ve import readings_route
    real, seen = readings_route.run_lean, {}

    def run(cases, **kw):
        seen["document"] = cases[0]["document"]
        return copy.deepcopy(captured["rows"])
    readings_route.run_lean = run
    try:
        args, kw = captured["args"]
        from ve import readings_components
        readings_components.load(*args, **kw)
    finally:
        readings_route.run_lean = real
    return copy.deepcopy(seen["document"])


def _grafts(captured):
    """Every well-typed misplacement of the request's rows in a case's document (and checked part with it, so the two
    still agree): each row of the request's `units` (in each of its `_forms`), `reading_sets`, `narrowings` and
    `couplings` inserted first and last into that list of every case, each unit of a case put in another of its
    forms, and each such list of two or more rows reversed. The retype, drop, empty and duplicate fuzz below cannot
    make these: every value is one the request holds."""
    document = _request(captured)
    for i, part in enumerate(captured["rows"][0]["components"]):
        for key in ("units", "reading_sets", "narrowings", "couplings"):
            rows = part["document"].get(key)
            if type(rows) is not list:
                continue
            sources = document.get(key) or []
            for row in [form for u in sources for form in _forms(u)] if key == "units" else sources:
                for at in (0, len(rows)):
                    yield f"{part['component']}: {key} gains {sorted(row.items())[:2]} at {at}", i, key, \
                        rows[:at] + [copy.deepcopy(row)] + rows[at:]
            if len(rows) > 1:
                yield f"{part['component']}: {key} reversed", i, key, rows[::-1]
        units = part["document"]["units"]
        for j, unit in enumerate(units):
            for form in _forms(next(u for u in document["units"] if u["id"] == unit["id"])):
                yield f"{part['component']}: unit {unit['id']} as {sorted(form)}", i, "units", \
                    units[:j] + [copy.deepcopy(form)] + units[j + 1:]


@pytest.mark.parametrize("name", ["F-C1", "F-C11", "F-C17"])
def test_every_graft_of_a_request_row_into_a_case_is_refused(genuine, name):
    """The class of B2 (rd-4b looprecheck 1): a case's document is the request's projection on it (`_projection`,
    Lean's `mainDoc` and `componentDoc`), row for row, so a request row added to, moved within or reshaped in any case
    is refused. F-C11 carries a narrowing on `rs_a` citing `u0`, which `rs_a` holds by id alone."""
    captured = genuine[name]
    survived = []
    for label, i, key, value in _grafts(captured):
        rows = copy.deepcopy(captured["rows"])
        part = rows[0]["components"][i]
        genuine_rows = part["document"][key]
        if value == genuine_rows:
            continue
        # the checked part with it when it carries the same rows (a companion case's, or the main case's whole)
        if part["checked"].get(key) == genuine_rows:
            part["checked"] = {**part["checked"], key: copy.deepcopy(value)}
        part["document"] = {**part["document"], key: value}
        if not _refused(captured, rows):
            survived.append(label)
    assert survived == [], survived


def test_a_cited_unit_is_carried_by_id_alone(genuine):
    """F-C11 genuine: `rs_a`'s narrowing cites `u0`, which its case holds without kind or content; the main case
    keeps `u_a` without its content (the cited unit's and the set unit's forms `_projection` binds)."""
    captured = genuine["F-C11"]
    loaded = _load(captured, captured["rows"])
    by = {p["name"]: p["document"] for p in loaded["parts"]}
    assert by["rs_a"]["units"][0] == {"id": "u0"} and [u["id"] for u in by["rs_a"]["units"]] == ["u0", "u_a"]
    assert [n["id"] for n in by["rs_a"]["narrowings"]] == ["n1"] and by["main"]["narrowings"] == []
    assert "content" not in next(u for u in by["main"]["units"] if u["id"] == "u_a")


# What Lean alone computes inside these answers (a mutant there is Lean's answer, not a binding): the generated
# declarations and Fill premises of RD-2b, the filled contents (`_bind_completion`: "What is left is Lean's alone"),
# and the product answer's plan lines (as in test_readings_components_lean.py's LEAN_OWNED).
LEAN_OWNED = {
    "generated_predicates": "Readings.Route.elaborateFields: the generated declarations (RD-2b)",
    "premises": "UnspecifiedWire.fillPremisesJson: each reading's Fill_T; its labels are bound, its formulas Lean's",
    "content": "UnspecifiedWire.filledJson: the filled contents (readings_route._bind_completion)",
    "english": "Readings.Run.productPlan / verdictsPlan (plan_cites_conditions, plan_conditions_only)",
    "readings": "a plan line's readings (Readings.PlanItem.line)",
}
# RD-6b lets a filled component elaborate on the superposed route. These values
# are derived by Lean from that route; the loader binds the set ids, candidate
# ids, unit ids, slot labels and choice lists to the component request, while
# the schema checks the shape of the remaining Lean-owned values.
SUPERPOSED_LEAN_OWNED = {
    ("fill",): "the Fill_T formulas and their number (Readings.Wire.elaborateFieldsND)",
    ("slot",): "the superposed slot formulas and their number (Readings.Route.elaborateFields)",
    ("vocabulary", "sorts"): "the superposed frame's sorts (Readings.Route.vocabulary)",
    ("vocabulary", "constants"): "the superposed frame's constants (Readings.Route.vocabulary)",
}
# Lists whose length Lean alone decides; their entries' types are still fuzzed.
LEAN_LENGTHS = {
    "findings": "Readings.Run.setFindings: a set's S1 findings (SeparatedByDecisionOnly, SeparatedByActOnly), Lean's",
}
# A depth past which every value is inside a case's environment declarations or a formula, typed by its decoder.
DEPTH = 8
OTHER = {"int": 7, "str": "x", "bool": True, "null": None, "list": [], "dict": {}}


def _mutants(row, prefix):
    for path, value in _paths(row):
        if not path or path[:len(prefix)] != prefix or len(path) > DEPTH:
            continue
        if any(type(p) is str and p in LEAN_OWNED for p in path):
            continue
        if "answer" in path:
            rest = path[path.index("answer") + 1:]
            owned = (any(rest[:len(owned_path)] == owned_path for owned_path in SUPERPOSED_LEAN_OWNED) or
                     # The candidate's qualified names and a superposed predicate's argument sorts are Lean's.
                     (len(rest) >= 5 and rest[0] == "names" and rest[2] == "candidates" and rest[4] == "names") or
                     (len(rest) >= 4 and rest[:2] == ("vocabulary", "predicates") and rest[3] == "arguments"))
            if owned:
                continue
        kind = _type(value)
        for other in ("int", "null", "dict") if kind not in ("int", "dict") else ("str", "null", "list"):
            yield "retype", path, OTHER[other]
        if type(path[-1]) is str:
            yield "drop", path, _DROP
        if type(value) is list and value and path[-1] not in LEAN_LENGTHS:
            yield "empty", path, []
            yield "duplicate", path, value + [copy.deepcopy(value[0])]


CASES = [("F-C1", k, (("components", i) if k < 2 else ())) for k in range(2) for i in range(3)] + [
    ("F-C1", 2, ()), ("F-C17", 0, ("components", 0)), ("F-C17", 1, ("components", 0)),
    ("F-C11", 0, ("components", 1))]


@pytest.mark.parametrize("name,k,prefix", CASES, ids=[f"{n}-{ROWS[k]}-{'-'.join(map(str, p))}" for n, k, p in CASES])
def test_every_mutant_of_a_load_answer_is_refused(genuine, name, k, prefix):
    captured = genuine[name]
    row = captured["rows"][k]
    survived = []
    for how, path, new in _mutants(row, prefix):
        mutant = _set(row, path, new)
        if mutant == row:
            continue
        rows = copy.deepcopy(captured["rows"])
        rows[k] = mutant
        if not _refused(captured, rows):
            survived.append((how, path, new))
    assert survived == [], survived
