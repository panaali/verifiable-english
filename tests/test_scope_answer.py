"""The explain route (scope SC-1c): `ve scope explain` relays Lean's rows (service mode `scope`) and never shows an
answer that is not one about the document it asked about. Genuine answers are mutated one and two faults at a time
(each member dropped, emptied, retyped, duplicated or reordered, an index pushed out of range, an id rebound, each
with `governed` made consistent again as its second fault): every mutant is `CheckerUnavailable` or changes nothing
the relay shows (R8). Deleting any one binding check of the relay lets some mutant through (review F1)."""
from __future__ import annotations

import copy
import json
import re

import pytest

from tests.test_document_lean_switch import _structural_mutants
from tests.test_scope_document import EFFECTS, F1, OWN, _governed_text, _split, _text
from tests.test_scope_readings_document import _doc as readings_doc
from ve import document as D
from ve import scope
from ve.backends import relay
from ve.backends.service_schema import ROWS, Context, Invalid
from ve.errors import CheckerUnavailable, VEError

ANSWER = relay.answer
LEAD = "The start of this rule comes from the line above the list, \"The rules:\"."
RULE_A = "\"- **Rule a:** Unit a.\""


def multi_text() -> str:
    """The list u1–u3 under the lead-in u0 (frame g1), a carve-out of rule b from u0 (g2) and rule a yielding to c (g3)."""
    meta, body = _split(_governed_text("norms", "frame"))
    meta["scope"]["governors"] += [
        {"id": "g2", "unit": "u0", "reach": {"rules": ["b"]}, "units": ["u2"], "effect": {"carve_out": OWN}},
        {"id": "g3", "unit": "u1", "reach": {"rules": ["c"]}, "units": ["u3"], "effect": "yields"}]
    return _text(meta, body)


def sets_text(n03: int = 2, n05: int = 0, sign: bool = False, lead: bool = False) -> str:
    """F1 with u0165.s03's set (sc-5rb's `_doc`): `wide` and `narrow` when `n03` is 2, else `n03` readings `r<i>`;
    with `n05`, a second set coupled to it on u0165.s05 (its part as the readings, the unit without content); with
    `sign`, the narrow reading writes `sign` as the frame does (11.6 SR-c, a fault under one choice); with `lead`, a
    set on the lead-in u0164.s02 too, the governor's own unit, which 11.1 does not cover (SR-g)."""
    def edit(meta, rs):
        if lead:
            meta["reading_sets"].append({**rs, "id": "scope-u0164-s02", "unit": "u0164.s02"})
        if n03 != 2:
            rs["readings"] = [{**rs["readings"][0], "id": f"r{i}", "meaning_id": f"m-r{i}"} for i in range(n03)]
        if sign:
            rs["readings"][1]["content"]["part"]["sign"] = False
        if n05:
            [unit] = [u for u in meta["units"] if u["id"] == "u0165.s05"]
            part, unit["content"] = unit.pop("content"), None
            meta["reading_sets"].append({**rs, "id": "scope-u0165-s05", "unit": "u0165.s05", "readings": [
                {**rs["readings"][0], "id": f"s{i}", "meaning_id": f"m-s{i}", "content": part} for i in range(n05)]})
    return readings_doc(edit)


def _write(tmp_path, text):
    path = tmp_path / "s.ve.md"
    path.write_text(text)
    return path


def _shown(path, capsys, row=None, monkeypatch=None):
    """Both views `ve scope explain` prints, with Lean answering `row` when given."""
    if row is not None:
        monkeypatch.setattr(relay, "answer", lambda mode, case: (copy.deepcopy(row), None))
    out = []
    for ids in ([], ["--ids"]):
        assert scope.main(["explain", str(path), *ids]) == 0
        out.append(capsys.readouterr().out)
    return out


@pytest.mark.parametrize("effect, rows", [
    ("frame", [(u, [("g1", LEAD)]) for u in ("u1", "u2", "u3")]),
    ("reguard", [("u2", [("g1", f"Its condition comes from an earlier sentence, {RULE_A}, which covers 1 rule.")])]),
    ("carve_out", [("u2", [("g1", f"Its exception comes from an earlier sentence, {RULE_A}, which covers 1 rule.")])]),
    ("precedes", [("u1", [("g1", f"It takes precedence over b; this comes from {RULE_A}.")])]),
    ("yields", [("u2", [("g1", f"a takes precedence over it; this comes from an earlier sentence, {RULE_A}.")])]),
    ("title", [])])
def test_each_effect_is_explained_by_its_governor_and_sentence(tmp_path, effect, rows):
    path = _write(tmp_path, _governed_text("norms", effect))
    found, meta, _ = scope.explain(path.read_bytes())
    assert [(r["unit"], [(x["id"], x["provenance"]) for x in r["governors"]]) for r in found] == rows
    assert {x["effect"] for r in found for x in r["governors"]} <= {effect.replace("_", "-")}


def test_the_reader_sees_each_units_text_and_its_sentences_and_the_ids_only_in_the_provenance_view(tmp_path, capsys):
    plain, ids = _shown(_write(tmp_path, multi_text()), capsys)
    assert plain.splitlines()[2:4] == ["- **Rule b:** Unit b.", "  Where the parts come from: " + LEAD +
                                       " Its exception comes from an earlier sentence, \"The rules:\", which covers 1 rule."]
    assert "u2" not in plain and "g2" not in plain
    assert "[u2] - **Rule b:** Unit b." in ids and "    g2 (carve-out, u0 -> u2)" in ids


def test_the_pilot_list_is_explained_with_its_lead_in(tmp_path):
    found, meta, _ = scope.explain(F1.read_bytes())
    assert found and all([x["id"] for x in r["governors"]] == ["g1"] for r in found)
    assert {r["unit"] for r in found} <= set(meta["scope"]["governors"][0]["units"])


def test_a_document_must_list_scope_and_a_refusal_of_govern_is_lean_s(tmp_path, capsys):
    meta, body = _split(_governed_text("norms", "frame"))
    listed = _write(tmp_path, _text(meta, body))
    assert scope.main(["explain", str(listed)]) == 0
    capsys.readouterr()
    meta["environment"]["profiles"].remove("scope@0")
    del meta["scope"]
    with pytest.raises(VEError, match="the scope mode explains a document that lists scope@0"):
        scope.explain(_text(meta, body).encode())
    meta, body = _split(_governed_text("norms", "frame"))
    meta["scope"]["governors"][0]["units"] = ["u1", "u2"]
    assert scope.main(["explain", str(_write(tmp_path, _text(meta, body)))]) == 2
    assert "ManifestMismatch: scope.governors.g1.units" in capsys.readouterr().out


def _repeated(effect: str, copies: int, with_id: bool, index: int = 3) -> str:
    """`_governed_text`'s document with `copies` more copies of unit `index`, keeping its id or without one."""
    meta, body = _split(_governed_text("norms", effect))
    for _ in range(copies):
        unit = copy.deepcopy(meta["units"][index])
        if not with_id:
            del unit["id"]
        meta["units"].append(unit)
    return _text(meta, body)


def _refused_on_both_routes(tmp_path, capsys, text: str, path: str) -> None:
    """The scope mode and the document mode both give Lean's one refusal of a repeated unit id at `path`."""
    refusal = f"InvalidInput: scope@0 {path} must be a unit id no other unit has"
    repeated = _write(tmp_path, text)
    assert scope.main(["explain", str(repeated)]) == 2
    assert refusal in capsys.readouterr().out
    with pytest.raises(VEError, match=f"^{re.escape(refusal)}$"):
        D.check_document(repeated)


@pytest.mark.parametrize("effect", sorted(EFFECTS))
@pytest.mark.parametrize("copies, with_id, path", [(1, True, "units.u3"), (2, False, "units")])
def test_sc5rdb_both_routes_that_decode_the_scope_block_refuse_a_repeated_unit_id(tmp_path, capsys, effect, copies,
                                                                                 with_id, path):
    """sc-5rdb review F1: `decodeBlock`'s repeated-id check reaches the scope mode as well as the document mode. The
    scope mode used to answer `ok` here (frame: ManifestMismatch), the document mode to refuse it later in the chain;
    both now give Lean's one refusal. The document without the copies is answered on both routes."""
    _refused_on_both_routes(tmp_path, capsys, _repeated(effect, copies, with_id), path)
    plain = _write(tmp_path, _governed_text("norms", effect))
    assert scope.main(["explain", str(plain)]) == 0
    capsys.readouterr()
    D.check_document(plain)


def test_sc5rdb_frame_with_another_unit_repeated_is_refused(tmp_path, capsys):
    """sc-5rdb recheck F9: `frame` went from `ok` to refused too. With u3 repeated it was refused before (ManifestMismatch:
    DELTA row 4); these three documents it answered `ok`, and `read_answer` accepted the answer (row 3)."""
    _refused_on_both_routes(tmp_path, capsys, _repeated("frame", 1, True, index=0), "units.u0")
    _refused_on_both_routes(tmp_path, capsys, _repeated("frame", 2, False, index=0), "units")
    meta, body = _split(_governed_text("norms", "frame"))
    meta["units"] += [{}, {}]
    _refused_on_both_routes(tmp_path, capsys, _text(meta, body), "units")


@pytest.mark.parametrize("effect", sorted(EFFECTS))
def test_sc5rdb_every_unit_of_every_effect_repeated_is_refused(tmp_path, capsys, effect):
    """sc-5rdb recheck F9: which old answer a document got depends on which id repeats and where (REPORT.md's table), so
    each unit of the document is repeated, at the end and beside itself, and copied twice without its id; two empty
    units and two of its own units without their ids are the same fault."""
    meta, body = _split(_governed_text("norms", effect))
    for index, unit in enumerate(meta["units"]):
        beside = copy.deepcopy(meta)
        beside["units"].insert(index + 1, copy.deepcopy(unit))
        _refused_on_both_routes(tmp_path, capsys, _repeated(effect, 1, True, index), f"units.{unit['id']}")
        _refused_on_both_routes(tmp_path, capsys, _text(beside, body), f"units.{unit['id']}")
        _refused_on_both_routes(tmp_path, capsys, _repeated(effect, 2, False, index), "units")
    empty, own = copy.deepcopy(meta), copy.deepcopy(meta)
    empty["units"] += [{}, {}]
    del own["units"][1]["id"], own["units"][2]["id"]
    _refused_on_both_routes(tmp_path, capsys, _text(empty, body), "units")
    _refused_on_both_routes(tmp_path, capsys, _text(own, body), "units")


def test_sc5rdb_one_unit_without_an_id_passes_the_scope_boundary(tmp_path):
    """A lone unit without an id repeats no id: the scope mode answers it; the chain refuses it for its own reason."""
    single = _write(tmp_path, _repeated("title", 1, False))
    scope.explain(single.read_bytes())
    with pytest.raises(VEError, match="^invalid unit schema$"):
        D.check_document(single)


def _rebound(row):
    """Mutants that keep the shape: reorders, out-of-range and rebound ids, and two-fault versions of a drop; for choice
    groups (sc-1cb) each group's, and each label's picks reordered, out of range, rebound, copied, swapped."""
    if "rows" in row:
        yield from _rebound_rows(row, lambda r: r)
        return
    groups = row["choices"]
    yield "choices reversed", lambda r: r["choices"].reverse()
    for c, group in enumerate(groups):
        for where, mutate in _rebound_rows(group, lambda r, c=c: r["choices"][c]):
            yield f"choices[{c}] {where}", mutate
        label = lambda r, c=c: r["choices"][c]["choice"]
        yield f"choices[{c}] picks reversed", lambda r, label=label: label(r).reverse()
        yield f"choices[{c}] relabelled as the next", lambda r, c=c: r["choices"][c].update(
            choice=copy.deepcopy(r["choices"][(c + 1) % len(r["choices"])]["choice"]))
        for k in range(len(group["choice"])):
            p = lambda r, label=label, k=k: label(r)[k]
            yield f"choices[{c}] pick {k} reading out of range", lambda r, p=p: p(r).update(reading="r9999")
            yield f"choices[{c}] pick {k} set out of range", lambda r, p=p: p(r).update(set="scope-x")
            yield f"choices[{c}] pick {k} version moved", lambda r, p=p: p(r).update(version=p(r)["version"] + 1)
            yield f"choices[{c}] pick {k} unit rebound", lambda r, p=p: p(r).update(unit="u0164.s02")
            yield f"choices[{c}] pick {k} over every pick", \
                lambda r, label=label, k=k: label(r).__setitem__(slice(None), [copy.deepcopy(label(r)[k])] * len(label(r)))
    if len(groups) > 1:
        def swap(r):
            first, second = r["choices"][:2]
            first["choice"], second["choice"] = second["choice"], first["choice"]
        yield "choices[0] and [1] labels swapped", swap


def _rebound_rows(row, get):
    """`_rebound`'s mutants of one answer's rows and their index, which `get` finds in a mutant."""
    rows = row["rows"]
    yield "rows reversed", lambda r: get(r)["rows"].reverse()
    yield "governed reversed", lambda r: get(r)["governed"].reverse()
    for i, entry in enumerate(rows):
        yield f"rows[{i}] unit out of range", lambda r, i=i: get(r)["rows"][i].update(unit="u9999")
        yield f"rows[{i}] unit rebound", lambda r, i=i: get(r)["rows"][i].update(unit="u0")
        yield f"rows[{i}] governors reversed", lambda r, i=i: get(r)["rows"][i]["governors"].reverse()
        for k, x in enumerate(entry["governors"]):
            g = lambda r, i=i, k=k: get(r)["rows"][i]["governors"][k]
            yield f"rows[{i}][{k}] reach reversed", lambda r, g=g: g(r)["reach"].reverse()
            yield f"rows[{i}][{k}] reach out of range", lambda r, g=g: g(r)["reach"].append("u9999")
            yield f"rows[{i}][{k}] id rebound", lambda r, g=g: g(r).update(id="g9" if g(r)["id"] != "g9" else "g1")
            yield f"rows[{i}][{k}] unit rebound", lambda r, g=g: g(r).update(unit="u3")
            for word in ("frame", "reguard", "carve-out", "precedes", "yields", "title"):
                yield f"rows[{i}][{k}] effect {word}", lambda r, g=g, word=word: g(r).update(effect=word)
            yield f"rows[{i}][{k}] dropped, governed kept", lambda r, i=i, k=k: get(r)["rows"][i]["governors"].pop(k)
            yield f"rows[{i}][{k}] dropped with its row", \
                lambda r, i=i, k=k: get(r)["rows"].pop(i) if len(get(r)["rows"][i]["governors"]) == 1 else None
    for i, entry in enumerate(row["governed"]):
        yield f"governed[{i}] units reversed", lambda r, i=i: get(r)["governed"][i]["units"].reverse()
        yield f"governed[{i}] unit out of range", lambda r, i=i: get(r)["governed"][i]["units"].append("u9999")


def _regoverned(mutant):
    """The mutant with `governed` made consistent again with its rows (each governor with the units of the rows that
    name it, in their order, repeats kept): the second fault of a forged row, so the row's own check must refuse it.
    In an answer of choice groups, each group's."""
    if type(mutant) is dict and type(mutant.get("choices")) is list:
        return {**mutant, "choices": [_regoverned(g) for g in mutant["choices"]]}
    try:
        units = {}
        for entry in mutant["rows"]:
            for x in entry["governors"]:
                units.setdefault(x["id"], []).append(entry["unit"])
        governed = [{"id": g["id"], "units": units.get(g["id"], [])} for g in mutant["governed"]]
    except (TypeError, KeyError, AttributeError):
        return mutant
    return {**mutant, "governed": governed}


def _omits(where) -> bool:
    """Whether the fault only leaves out rows or a row's governor. With `governed` made consistent again such an answer
    omits a contribution: which units are governed and by whom is Lean's (`explain_rows_iff`, R8), not the binding's."""
    if type(where) is str:
        return "dropped" in where
    shape = tuple(type(step) if type(step) is int else step for step in where)
    shape = shape[2:] if shape[:2] == ("choices", int) else shape
    return shape in {("rows", "=empty"), ("rows", int, "-"), ("rows", int, "governors", "=empty"),
                     ("rows", int, "governors", int, "-")}


def _accepted(text, path, capsys, monkeypatch):
    """The one- and two-fault mutants of Lean's genuine answer about `text` that pass the service's schema and the
    relay's binding and change what `ve scope explain` shows, and how many mutants were tried."""
    [genuine] = relay.rows("scope", [scope.request(text)])
    monkeypatch.setattr(relay, "answer", ANSWER)
    shown = _shown(path, capsys)
    assert _shown(path, capsys, genuine, monkeypatch) == shown  # the stub replays the genuine answer
    case = scope.request(text)
    accepted, count = [], 0
    for where, mutate in [*_structural_mutants(genuine), *_rebound(genuine)]:
        once = copy.deepcopy(genuine)
        mutate(once)
        twice = [] if _omits(where) else [(_regoverned(once), (where, "governed kept"))]
        for mutant, fault in [(once, where), *twice]:
            if mutant == genuine:
                continue
            count += 1
            try:
                ROWS["scope"][0](mutant, Context(case), {})
            except Invalid:
                continue
            try:
                if _shown(path, capsys, mutant, monkeypatch) != shown:
                    accepted.append(fault)
            except CheckerUnavailable:
                pass
    return accepted, count


DOCUMENTS = {"multi": multi_text, "precedes": lambda: _governed_text("norms", "precedes"),
             "frame": lambda: _governed_text("norms", "frame"), "sets": sets_text, "coupled": lambda: sets_text(2, 2)}


@pytest.mark.parametrize("name", DOCUMENTS)
def test_every_mutant_of_a_genuine_answer_is_refused_or_changes_nothing_shown(tmp_path, capsys, monkeypatch, name):
    text = DOCUMENTS[name]()
    accepted, count = _accepted(text, _write(tmp_path, text), capsys, monkeypatch)
    assert count > 100 and not accepted, accepted


def _checks():
    """Each binding check of the relay (`answer_problem`, `choices_problem`, `rows_problem`) with the relay that lacks
    it: every disjunct of a refusing `if` (one at a time), or the whole condition when it is not a disjunction (review
    F1: no test failed when the empty-sentence, reach, repeat or order check was deleted). The mutated module is run
    whole, so a check deleted in a helper is missing from the `answer_problem` that calls it."""
    import ast
    import inspect
    source = inspect.getsource(scope)

    def sites(tree):
        return [node for f in tree.body if type(f) is ast.FunctionDef and f.name.endswith("_problem")
                for node in ast.walk(f) if type(node) is ast.If and type(node.body[0]) is ast.Return
                and node.body[0].value is not None]
    for n, site in enumerate(sites(ast.parse(source))):
        parts = site.test.values if type(site.test) is ast.BoolOp and type(site.test.op) is ast.Or else [site.test]
        for k, part in enumerate(parts):
            mutated = ast.parse(source)
            target = sites(mutated)[n]
            if len(parts) == 1:
                target.test = ast.Constant(False)
            else:
                target.test.values[k] = ast.Constant(False)
            namespace = {"__name__": "ve._scope_weakened", "__package__": "ve"}
            exec(compile(ast.fix_missing_locations(mutated), scope.__file__, "exec"), namespace)
            yield ast.unparse(part), namespace["answer_problem"]


# The checks the service's schema (`scope.json`, applied by `run_bound` before the relay reads a row) decides first: a
# mutant they would refuse never reaches the binding. Each is kept as the relay's own type guard.
SCHEMA_FIRST = {
    "type(row) is not dict", "set(row) not in ({'id', 'status', 'rows', 'governed'}, {'id', 'status', 'choices'})",
    "row['id'] != case_id", "row['status'] != 'ok'", "type(rows) is not list", "type(governed) is not list",
    "type(entry) is not dict", "set(entry) != {'unit', 'governors'}", "type(entry['governors']) is not list",
    "type(unit) is not str", "not entry['governors']", "set(x) != {'id', 'unit', 'effect', 'reach', 'provenance'}",
    "type(x['effect']) is not str", "type(x['provenance']) is not str", "type(group) is not dict",
    "set(group) != {'choice', 'rows', 'governed'}", "type(group['choice']) is not list",
    "set(pick) != {'unit', 'set', 'version', 'reading'}", "type(pick['reading']) is not str", "not labels"}


def test_every_binding_check_has_a_mutant_only_it_refuses(tmp_path, capsys, monkeypatch):
    """Deleting any binding check of the relay lets some mutant of a genuine answer change what is shown (or crash the
    relay), unless the schema refuses that mutant first (`SCHEMA_FIRST`, kept exact so it cannot go stale)."""
    texts = []
    for name, make in DOCUMENTS.items():
        (tmp_path / name).mkdir()
        texts.append((make(), _write(tmp_path / name, make())))
    survivors = set()
    for check, weakened in _checks():
        monkeypatch.setattr(scope, "answer_problem", weakened)
        killed = False
        for text, path in texts:
            try:
                killed = bool(_accepted(text, path, capsys, monkeypatch)[0])
            except (TypeError, KeyError, AttributeError, IndexError, ValueError):
                killed = True  # the weakened relay crashes on a mutant instead of refusing it
            if killed:
                break
        if not killed:
            survivors.add(check)
        monkeypatch.undo()
    assert survivors == SCHEMA_FIRST, (survivors - SCHEMA_FIRST, SCHEMA_FIRST - survivors)


def test_a_row_lean_did_not_bind_to_the_case_is_no_answer(tmp_path, monkeypatch):
    text = _governed_text("norms", "frame")
    [genuine] = relay.rows("scope", [scope.request(text)])
    meta, _ = _split(text)
    assert scope.answer_problem(genuine, meta) is None
    for forged in ({**genuine, "id": "other"}, {**genuine, "status": "error"}, {**genuine, "extra": 1},
                   {k: v for k, v in genuine.items() if k != "governed"}):
        assert scope.answer_problem(forged, meta) is not None
    monkeypatch.setattr(relay, "answer", lambda mode, case: ({**genuine, "governed": []}, None))
    with pytest.raises(CheckerUnavailable, match="governed is not the document's governors"):
        scope.explain(text.encode())


def test_route_cases_answer_their_rows():
    """The recorded `scope` route cases: every genuine document is answered and bound, every hostile one refused."""
    from tests.lean_service_corpus import recorded
    cases = recorded("scope")
    answers = relay.rows("scope", cases)
    assert len(cases) >= 8
    for case, row in zip(cases, answers):
        if case["id"].startswith("refused-"):
            assert row["status"] == "error", case["id"]
        else:
            assert scope.answer_problem(row, _split(case["document"])[0], case["id"]) is None, (case["id"], row)



# sc-1cb's route cases: the number of choice groups answered, or the refusal
PER_CHOICE = {"sets-u0165-s03": 2, "sets-two-coupled": 4, "sets-64": 64,
              "refused-sets-choice-fault": "ScopeChoice: u0165.s03 scope-u0165-s03@1:narrow: ScopeConflict: u0165.s03: sign",
              "refused-sets-65": "ResourceLimit: scope choices", "refused-sets-uncovered": "ScopeReadings: u0164.s02"}


def test_a_set_governed_per_choice_is_explained_per_choice_and_every_other_answer_is_mains():
    """DRI decision 2026-11-01 sc-1cb item 1, conditions (a)-(d): u0165.s03's set (refused on main with
    `ScopeReadings`) answers two groups, two coupled sets four and 64 choices 64, each bound; a fault under one choice
    is 11.5's `ScopeChoice`, 65 choices UNKNOWN and a set 11.1 does not cover `ScopeReadings`; every other case is
    answered as main answered it (`explain-main-answers.jsonl`, recorded from main's Lean at 3148e87c4), byte for byte."""
    from pathlib import Path
    from tests.lean_service_corpus import recorded
    cases = recorded("scope")
    main = {row["id"]: row for row in map(json.loads, (Path(__file__).parent / "data/scope/explain-main-answers.jsonl")
                                          .read_text().splitlines())}
    assert main["sets-u0165-s03"]["error"] == "ScopeReadings: u0165.s03"
    assert {c["id"] for c in cases} == set(main) | set(PER_CHOICE)
    for case, row in zip(cases, relay.rows("scope", cases)):
        expected = PER_CHOICE.get(case["id"])
        if type(expected) is int:
            assert len(row["choices"]) == expected, case["id"]
            assert scope.answer_problem(row, _split(case["document"])[0], case["id"]) is None
        elif expected is not None:
            assert row["error"] == expected
        else:
            assert json.dumps(row) == json.dumps(main[case["id"]]), case["id"]


def test_each_choices_rows_are_shown_under_its_label(tmp_path, capsys):
    plain, ids = _shown(_write(tmp_path, sets_text()), capsys)
    groups = [line for line in plain.splitlines() if not line.startswith("  ")]
    assert groups == ["Under the choice u0165.s03 scope-u0165-s03@1:wide:",
                      "Under the choice u0165.s03 scope-u0165-s03@1:narrow:"]
    assert len(plain.splitlines()) == 2 + 2 * 7 * 2 and "  [u0165.s01] " in ids


def test_the_proved_statements_are_spec_5_3s_text():
    """The statement gate: `explain_bound` and `explain_rows_iff` are the reviewed text (scope.md 5.3), whitespace aside."""
    from pathlib import Path

    from tests.test_scope_5_4_statements import statement
    root = Path(__file__).resolve().parents[1]
    spec, lean = (root / "docs/spec/scope.md").read_text(), (root / "lean/VE/Scope/Run.lean").read_text()
    for name in ("explain_bound", "explain_rows_iff"):
        assert statement(spec, name) is not None, name
        assert statement(lean, name) == statement(spec, name), name
