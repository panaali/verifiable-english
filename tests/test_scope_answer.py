"""The explain route (scope SC-1c): `ve scope explain` relays Lean's rows (service mode `scope`) and never shows an
answer that is not one about the document it asked about. Genuine answers are mutated one and two faults at a time
(each member dropped, emptied, retyped, duplicated or reordered, an index pushed out of range, an id rebound, each
with `governed` made consistent again as its second fault): every mutant is `CheckerUnavailable` or changes nothing
the relay shows (R8). Deleting any one binding check of the relay lets some mutant through (review F1)."""
from __future__ import annotations

import copy
import json

import pytest

from tests.test_document_lean_switch import _structural_mutants
from tests.test_scope_document import F1, OWN, _governed_text, _split, _text
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


def _rebound(row):
    """Mutants that keep the shape: reorders, out-of-range and rebound ids, and two-fault versions of a drop."""
    def at(path):
        def mutate(r):
            *head, last = path
            for key in head:
                r = r[key]
            return r, last
        return mutate
    rows = row["rows"]
    yield "rows reversed", lambda r: r["rows"].reverse()
    yield "governed reversed", lambda r: r["governed"].reverse()
    for i, entry in enumerate(rows):
        yield f"rows[{i}] unit out of range", lambda r, i=i: r["rows"][i].update(unit="u9999")
        yield f"rows[{i}] unit rebound", lambda r, i=i: r["rows"][i].update(unit="u0")
        yield f"rows[{i}] governors reversed", lambda r, i=i: r["rows"][i]["governors"].reverse()
        for k, x in enumerate(entry["governors"]):
            g = lambda r, i=i, k=k: r["rows"][i]["governors"][k]
            yield f"rows[{i}][{k}] reach reversed", lambda r, g=g: g(r)["reach"].reverse()
            yield f"rows[{i}][{k}] reach out of range", lambda r, g=g: g(r)["reach"].append("u9999")
            yield f"rows[{i}][{k}] id rebound", lambda r, g=g: g(r).update(id="g9" if g(r)["id"] != "g9" else "g1")
            yield f"rows[{i}][{k}] unit rebound", lambda r, g=g: g(r).update(unit="u3")
            for word in ("frame", "reguard", "carve-out", "precedes", "yields", "title"):
                yield f"rows[{i}][{k}] effect {word}", lambda r, g=g, word=word: g(r).update(effect=word)
            yield f"rows[{i}][{k}] dropped, governed kept", lambda r, i=i, k=k: r["rows"][i]["governors"].pop(k)
            yield f"rows[{i}][{k}] dropped with its row", \
                lambda r, i=i, k=k: r["rows"].pop(i) if len(r["rows"][i]["governors"]) == 1 else None
    for i, entry in enumerate(row["governed"]):
        yield f"governed[{i}] units reversed", lambda r, i=i: r["governed"][i]["units"].reverse()
        yield f"governed[{i}] unit out of range", lambda r, i=i: r["governed"][i]["units"].append("u9999")


def _regoverned(mutant):
    """The mutant with `governed` made consistent again with its rows (each governor with the units of the rows that
    name it, in their order, repeats kept): the second fault of a forged row, so the row's own check must refuse it."""
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
             "frame": lambda: _governed_text("norms", "frame")}


@pytest.mark.parametrize("name", DOCUMENTS)
def test_every_mutant_of_a_genuine_answer_is_refused_or_changes_nothing_shown(tmp_path, capsys, monkeypatch, name):
    text = DOCUMENTS[name]()
    accepted, count = _accepted(text, _write(tmp_path, text), capsys, monkeypatch)
    assert count > 100 and not accepted, accepted


def _checks():
    """Each binding check of `scope.answer_problem` with the function that lacks it: every disjunct of a refusing
    `if` (one at a time), or the whole condition when it is not a disjunction (review F1: no test failed when the
    empty-sentence, reach, repeat or order check was deleted)."""
    import ast
    import inspect
    import textwrap
    tree = ast.parse(textwrap.dedent(inspect.getsource(scope.answer_problem)))
    sites = [node for node in ast.walk(tree) if type(node) is ast.If and type(node.body[0]) is ast.Return
             and node.body[0].value is not None]
    for n, site in enumerate(sites):
        parts = site.test.values if type(site.test) is ast.BoolOp and type(site.test.op) is ast.Or else [site.test]
        for k, part in enumerate(parts):
            mutated = copy.deepcopy(tree)
            target = [node for node in ast.walk(mutated) if type(node) is ast.If
                      and type(node.body[0]) is ast.Return and node.body[0].value is not None][n]
            if len(parts) == 1:
                target.test = ast.Constant(False)
            else:
                target.test.values[k] = ast.Constant(False)
            namespace = dict(vars(scope))
            exec(compile(ast.fix_missing_locations(mutated), scope.__file__, "exec"), namespace)
            yield ast.unparse(part), namespace["answer_problem"]


# The checks the service's schema (`scope.json`, applied by `run_bound` before the relay reads a row) decides first: a
# mutant they would refuse never reaches the binding. Each is kept as the relay's own type guard.
SCHEMA_FIRST = {
    "type(row) is not dict", "set(row) != {'id', 'status', 'rows', 'governed'}", "row['id'] != case_id",
    "row['status'] != 'ok'", "type(row['rows']) is not list", "type(row['governed']) is not list",
    "type(entry) is not dict", "set(entry) != {'unit', 'governors'}", "type(entry['governors']) is not list",
    "type(unit) is not str", "not entry['governors']", "set(x) != {'id', 'unit', 'effect', 'reach', 'provenance'}",
    "type(x['effect']) is not str", "type(x['provenance']) is not str"}


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
            except (TypeError, KeyError, AttributeError, IndexError):
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



def test_the_proved_statements_are_spec_5_3s_text():
    """The statement gate: `explain_bound` and `explain_rows_iff` are the reviewed text (scope.md 5.3), whitespace aside."""
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    spec, lean = (root / "docs/spec/scope.md").read_text(), (root / "lean/VE/Scope/Run.lean").read_text()

    def statement(text, name):
        rest = text[text.index(f"theorem {name} "):]
        return " ".join(rest[:min(i for i in (rest.find(":="), rest.find("\n\n")) if i >= 0)].split())
    for name in ("explain_bound", "explain_rows_iff"):
        assert statement(lean, name) == statement(spec, name), name
