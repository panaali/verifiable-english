"""norm-defaults@0 report in Lean (lean-first batch 10a; docs/spec/norm-defaults.md 3.2 and 5).

Lean's `norm-defaults-report` (`lean/VE/NormDefaults/Report.lean`) decides the gap and
default-reached lines, `UngroundedDefault`, `inherits_from` and the residual `gaps` line.
No caller uses it yet (batch 10b switches them); these tests hold it to Python's
`norm_defaults.report`, line for line, and check that it fails closed on bad input.
"""
from __future__ import annotations

from copy import deepcopy

import pytest

from conformance.norm_defaults_report import compare, python_rows, report_case, search_evidence
from conformance.norm_defaults import _norm
from conformance.norm_defaults_three_way import fixtures
from tests.test_norm_defaults_three_way import lean_executable  # noqa: F401  (the route fixture)
from ve import norm_defaults as nd
from ve import norm_defaults_route as route
from ve.environment import Environment
from ve.errors import VEError
from ve.norms import NormDocument

CSAM = "csam_generation_permitted"
GOOD = {"cites": ["u1"], "reason": "the source states the completion"}


def _document(name):
    for fixture, env, units, situations in fixtures():
        if fixture == name:
            return nd.UnspecifiedDocument(Environment(env), [NormDocument._decode(u) for u in units]), situations
    raise KeyError(name)


def _run(cases, executable):
    return route.run_cases(cases, executable)


def test_report_with_a_situation_is_pythons_line_for_line(lean_executable):
    """Every fixture and situation: Lean's own witness search gives Python's lines, tuple,
    filling and residual, as an authored and as a translation document."""
    cases, expected = [], []
    for name, env, units, situations in fixtures():
        doc = nd.UnspecifiedDocument(Environment(env), [NormDocument._decode(u) for u in units])
        for raw in situations:
            for translation in (False, True):
                cases.append(report_case(doc, model=raw, translation=translation))
                expected.append((name, nd.report(doc, model=raw, translation=translation)))
    rows = _run(cases, lean_executable)
    problems = [(name, compare(lines, row)) for (name, lines), row in zip(expected, rows)]
    assert [p for p in problems if p[1]] == []
    reached = {line.reached for _, lines in expected for line in lines}
    assert reached == {"reachable", "unknown"}  # a situation alone never proves `none`
    assert any(line.inherits_from for _, lines in expected for line in lines)
    assert any(line.grounding.startswith("UngroundedDefault") for _, lines in expected for line in lines)
    assert len(cases) == 2 * sum(len(s) for _, _, _, s in fixtures())


def test_report_replays_pythons_search_evidence(lean_executable):
    """Without a situation (the document path, `coverage_defaults`): Python's small-model
    witnesses and proved certificates replay in Lean to Python's lines."""
    cases, expected = [], []
    for name, env, units, _ in fixtures():
        doc = nd.UnspecifiedDocument(Environment(env), [NormDocument._decode(u) for u in units])
        lines, evidence = search_evidence(doc, translation=True)
        cases.append(report_case(doc, evidence=evidence, translation=True))
        expected.append((name, lines))
    rows = _run(cases, lean_executable)
    assert [(name, p) for (name, lines), row in zip(expected, rows) if (p := compare(lines, row))] == []
    reached = {line.reached for _, lines in expected for line in lines}
    assert reached == {"reachable", "none"}
    by_name = dict(zip((n for n, _ in expected), rows))
    assert by_name["u1-allow"]["findings"] == [f"UngroundedDefault: {CSAM}"]
    assert by_name["u1"]["residual"] == {"gaps": [CSAM], "ungrounded_defaults": 0}


def test_without_evidence_every_line_is_unknown(lean_executable):
    doc, _ = _document("u1-allow")
    (row,) = _run([report_case(doc, translation=True)], lean_executable)
    assert [r["reached"] for r in row["report"]] == ["unknown"]
    # no witness, so no finding: "One without a witness is not flagged" (spec 5)
    assert row["findings"] == [] and row["residual"] == {"gaps": [], "ungrounded_defaults": 0}


def test_grounding_lines_follow_the_completions_block(lean_executable):
    """u1: a reached allow or deny completion of a translation document is
    `UngroundedDefault` unless the block cites it; an authored document has no finding; an
    unspecified completion never has one."""
    situation = _document("u1")[1][0]
    cases, wanted = [], []
    for name in ("u1-allow", "u1-deny", "u1"):
        doc, _ = _document(name)
        for translation, block in ((True, None), (False, None), (True, {CSAM: GOOD})):
            if name == "u1" and block:
                continue
            fields = {"translation": translation}
            if block:
                fields.update(completions=block, unit_ids=["u1", "u2"])
            cases.append(report_case(doc, model=situation, **fields))
            completions = nd.validate_completions(doc, block, {"u1", "u2"}) if block else None
            wanted.append(python_rows(nd.report(doc, model=situation, translation=translation,
                                                completions=completions)))
    rows = _run(cases, lean_executable)
    assert [r["report"] for r in rows] == wanted
    lines = [r["report"][0]["lines"] for r in rows]
    assert lines[0][-1] == f"UngroundedDefault: {CSAM}" and lines[2][-1] == "grounded: u1"
    assert len(lines[1]) == 2 and lines[-1] == ["completion: unspecified", "gaps: reachable"]
    assert [r["residual"]["ungrounded_defaults"] for r in rows] == [1, 0, 0, 1, 0, 0, 0, 0]


def _completions_fault(doc, block, unit_ids=("u1",)):
    try:
        nd.validate_completions(doc, block, set(unit_ids))
    except VEError as exc:
        return str(exc)
    return None


@pytest.mark.parametrize("block", [
    [], 7, "x", True,
    {"nothing": GOOD},
    {CSAM: {"cites": [], "reason": "x"}},
    {CSAM: {"cites": ["u1"]}},
    {CSAM: {"cites": ["u1"], "reason": "x", "extra": 1}},
    {CSAM: {"cites": ["u1", "u1"], "reason": "x"}},
    {CSAM: {"cites": [7], "reason": "x"}},
    {CSAM: {"cites": [True], "reason": "x"}},
    {CSAM: {"cites": "u1", "reason": "x"}},
    {CSAM: {"cites": ["u1"], "reason": 7}},
    {CSAM: {"cites": ["u1"], "reason": "  \t"}},
    {CSAM: {"cites": ["u1"], "reason": "  　"}},
    {CSAM: {"cites": ["u1"], "reason": "\x1c\x85"}},
    {CSAM: {"cites": ["u9"], "reason": "x"}},
    {CSAM: []}, {CSAM: 7}, {CSAM: {}},
])
def test_completions_faults_have_pythons_text(lean_executable, block):
    """Each malformed `completions` block: Lean refuses it with Python's text (types
    swapped, absent fields, a duplicate, a blank reason in Python's `str.isspace` sense)."""
    doc, situations = _document("u1-deny")
    expected = _completions_fault(doc, block)
    assert expected is not None
    (row,) = _run([report_case(doc, model=situations[0], translation=True, completions=block,
                               unit_ids=["u1"])], lean_executable)
    assert (row["status"], row["error"]) == ("error", expected)


def test_completions_of_an_unspecified_predicate_cite_nothing(lean_executable):
    doc, situations = _document("u1")
    expected = _completions_fault(doc, {CSAM: GOOD})
    (row,) = _run([report_case(doc, completions={CSAM: GOOD}, unit_ids=["u1"])], lean_executable)
    assert row["error"] == expected == f"InvalidInput: completion of {CSAM} is unspecified and cites nothing"


def test_completions_are_read_in_key_order(lean_executable):
    """Two faulty entries: Lean reports the first in key order (its JSON objects are keyed
    maps). Python reads the block in insertion order; batch 10b lists this as an order change."""
    doc, _ = _document("u5a")
    block = {"x_required": GOOD, "x_permitted": {"cites": [], "reason": "x"}}
    (row,) = _run([report_case(doc, completions=block, unit_ids=["u1"])], lean_executable)
    assert row["error"] == "InvalidInput: invalid completion grounding for x_permitted"
    assert _completions_fault(doc, block) == "InvalidInput: completion of x_required is unspecified and cites nothing"


@pytest.mark.parametrize("field,value,message", [
    ("translation", "yes", "InvalidInput: translation must be a boolean"),
    ("translation", 1, "InvalidInput: translation must be a boolean"),
    ("unit_ids", "u1", "InvalidInput: unit_ids must be a list of strings"),
    ("unit_ids", [1], "InvalidInput: unit_ids must be a list of strings"),
    ("predicates", [True], "InvalidInput: predicates must be a list of strings"),
    ("witnesses", [], "InvalidInput: witnesses must be an object"),
    ("packages", 7, "InvalidInput: packages must be an object"),
])
def test_case_fields_are_typed(lean_executable, field, value, message):
    doc, _ = _document("u1")
    (row,) = _run([report_case(doc, **{field: value})], lean_executable)
    assert (row["status"], row["error"]) == ("error", message)


def test_a_situation_table_named_unsaid_is_a_filling(lean_executable):
    doc, situations = _document("u1")
    model = deepcopy(situations[0])
    model["relations"]["unsaid__" + CSAM] = [["sol0"]]
    with pytest.raises(VEError, match="is a filling"):
        doc.situation(model)
    (row,) = _run([report_case(doc, model=model)], lean_executable)
    assert row["error"] == (f"InvalidModel(norm-defaults): unsaid__{CSAM} is a filling; "
                            "supply it as a filling, not a table")


def test_tampered_evidence_never_becomes_a_line(lean_executable):
    """Supplied evidence is checked: a witness at a tuple where a rule decides, a witness
    for another predicate's entry, a witness whose filling breaks `Fill_T`, and a
    certificate of another document give `unknown` or the decoder's diagnostic, never
    `reachable` or `none`."""
    doc, _ = _document("u1")
    _, (witnesses, packages) = search_evidence(doc)
    good = witnesses[CSAM]
    model = good["model"]
    claude = model["constants"]["claude"]
    decided = {**good, "tuple": [claude]}
    rows = _run([report_case(doc, evidence=({CSAM: good}, {})),
                 report_case(doc, evidence=({CSAM: decided}, {})),
                 report_case(doc, evidence=({}, {}))], lean_executable)
    assert [r["report"][0]["reached"] for r in rows] == ["reachable", "unknown", "unknown"]

    # u5c: both members unspecified; the filling (required yes, permitted no) fails Fill_T
    pair, situations = _document("u5c")
    lines, (witnesses, _) = search_evidence(pair)
    assert witnesses, lines
    predicate, witness = next(iter(witnesses.items()))
    bad = deepcopy(witness)
    bad["model"]["relations"]["unsaid__x_required"] = [[e] for e in bad["model"]["domains"]["act"]]
    bad["model"]["relations"]["unsaid__x_permitted"] = []
    (row,) = _run([report_case(pair, evidence=({predicate: bad}, {}))], lean_executable)
    assert (row["status"], row["error"]) == ("error", "InvalidModel(unsaid): the model violates a background premise")

    # a certificate proved for one document does not replay on another
    never, _ = _document("u15-deny")
    _, (_, packages) = search_evidence(never)
    other, _ = _document("u15-unspecified")
    rows = _run([report_case(never, evidence=({}, packages)),
                 report_case(other, evidence=({}, packages))], lean_executable)
    assert [r["report"][0]["reached"] for r in rows] == ["none", "unknown"]


def test_the_atom_budget_bounds_lean_like_python(lean_executable):
    """b2-wide: each point's cone is one atom of 13; a guard reading every unsaid atom puts
    13 in one cone, past `MAX_UNSAID_ATOMS`, so neither side searches it."""
    doc, situations = _document("b2-wide")
    lines = nd.report(doc, model=situations[0])
    (row,) = _run([report_case(doc, model=situations[0])], lean_executable)
    assert compare(lines, row) == []
    env = deepcopy(doc.env.to_dict())
    wide = NormDocument._decode(_norm("r", "x_permitted", True, ["forall", "act", ["unary", "y_permitted", ["var", 0]]]))
    tight = nd.UnspecifiedDocument(Environment(env), [wide])
    lines = nd.report(tight, model=situations[0])
    (row,) = _run([report_case(tight, model=situations[0])], lean_executable)
    assert compare(lines, row) == []
    assert row["report"][[r["predicate"] for r in row["report"]].index("x_permitted")]["reached"] == "unknown"


def test_predicates_restrict_the_report(lean_executable):
    doc, situations = _document("a1-switch-deny")
    lines = nd.report(doc, model=situations[0], predicates=("p_permitted",))
    (row,) = _run([report_case(doc, model=situations[0], predicates=["p_permitted"])], lean_executable)
    assert compare(lines, row) == [] and len(row["report"]) == 1


def test_report_on_generated_trees(lean_executable):
    """Spec 8's generated trees (1,000 with their situations, 200 through Python's search
    evidence), as authored and translation documents, some with a `completions` block:
    every report is Python's, line for line."""
    from conformance.norm_defaults_report import generated
    result = generated(lean_executable)
    assert result["mismatches"] == []
    assert result["cases"] == 1200
    counts = result["counts"]
    for key in ("situation:reachable", "situation:unknown", "situation:UngroundedDefault", "situation:grounded",
                "searched:reachable", "searched:none", "searched:UngroundedDefault"):
        assert counts.get(key, 0) >= 20, (key, counts)


MALFORMED = [7, True, [], {}, "x", [7], {"a": 7}, [[]]]


def test_malformed_fields_are_refused_or_inert(lean_executable):
    """Every report field, every entry of `witnesses`, `packages` and `completions`, and
    every part of a situation replaced by a value of another shape: Lean answers each case
    with a row, no malformed evidence ever becomes a `reachable` or `none` line, and a
    replaced situation part is refused exactly when Python refuses the situation (otherwise
    the report is Python's)."""
    doc, situations = _document("u1-allow")
    cases = [report_case(doc, **{field: value}) for field in
             ("completions", "unit_ids", "translation", "witnesses", "packages", "predicates")
             for value in MALFORMED]
    for value in MALFORMED:
        cases += [report_case(doc, witnesses={CSAM: value}), report_case(doc, packages={f"reached:{CSAM}": value}),
                  report_case(doc, completions={CSAM: value}, unit_ids=["u1"])]
    models = [{**situations[0], part: value} for part in ("complete", "domains", "constants", "relations")
              for value in MALFORMED] + [value for value in MALFORMED]
    rows = _run(cases + [report_case(doc, model=m) for m in models], lean_executable)
    assert len(rows) == len(cases) + len(models)
    evidence, situated = rows[:len(cases)], rows[len(cases):]
    errors = [r for r in evidence if r["status"] == "error"]
    assert all(type(r["error"]) is str and r["error"] for r in errors)
    answered = [r for r in evidence if r["status"] == "ok"]
    assert answered and len(errors) > 3 * len(answered)
    assert {line["reached"] for r in answered for line in r["report"]} == {"unknown"}
    refused = 0
    for model, row in zip(models, situated):
        try:
            lines = nd.report(doc, model=model)
        except (VEError, AttributeError, KeyError, TypeError, ValueError):
            # Python's situation decoder refuses it (not always as a VEError: batch 10b relays Lean's)
            assert row["status"] == "error", model
            refused += 1
        else:
            assert compare(lines, row) == [], model
    assert refused > len(models) // 2
