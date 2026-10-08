"""The Rust JSONL checker's records are checked against `ve/backends/rust_schema/jsonl.json` before
any field is read (lf-0 fix3, build checklist line 4): a record `ve jsonl` cannot write is
`CheckerUnavailable`, never a rejection, a verdict or a Python crash.

Genuine records come from the built checker through the public adapters that call it; each is then
fed back with every field dropped, emptied, nulled and retyped."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from tests.probe_matrix import model_wire, raw_environment
from ve import Environment, FiniteModel
from ve.ast import Bottom, Const, Exists, Not, Top, Unary, Var, formula_to_data
from ve.backends import rust_jsonl
from ve.backends.service_schema import same_json
from ve.errors import CheckerUnavailable, UnknownSymbol, VEError

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not rust_jsonl.DEFAULT_EXECUTABLE.is_file(),
                                reason="the Rust checker has not been built")

ENV = Environment(raw_environment(()))
MODEL = FiniteModel.from_dict(ENV, model_wire(ENV))
ATOM = Unary("base", Const("x"))


def _superposed_case():
    """A readings-superposed-evaluate case as `readings_verdicts` `_shadow` sends it: four groups of formulas."""
    return {"id": "readings-s2-shadow", "kind": "readings-superposed-evaluate", "untrusted": True,
            "environment": ENV.to_dict(), "model": MODEL.to_dict(), "slot": [["top"]], "assertions": [["bottom"]],
            "conflict_targets": [], "conclusions": [["top"], ["bottom"]]}


def _calls():
    """Every public adapter that runs Rust, on inputs giving each record shape it can answer with."""
    from ve.ast import check_document, check_formula, Document
    from ve.evaluate import evaluate
    from ve.search import check_countermodel, find_countermodel, find_distinguishing_model
    other = FiniteModel.from_dict(ENV, {**model_wire(ENV), "relations": {"base": []}})
    return {
        "typing": lambda: check_formula(ENV, ATOM),
        "typing-document": lambda: check_document(ENV, Document((ATOM, Top()))),
        "evaluate-satisfied": lambda: evaluate(ENV, ATOM, MODEL, trace=False),
        "evaluate-violated": lambda: evaluate(ENV, ATOM, other, trace=False),
        "evaluate-trace": lambda: evaluate(ENV, Exists("item", Unary("base", Var(0))), MODEL, trace=True),
        "evaluate-budget": lambda: evaluate(ENV, Exists("item", Unary("base", Var(0))), MODEL, trace=True,
                                            max_evaluations=1),
        "countermodel-valid": lambda: check_countermodel(ENV, (ATOM,), Bottom(), MODEL),
        "countermodel-premise-false": lambda: check_countermodel(ENV, (ATOM, Top()), Bottom(), other),
        "countermodel-conclusion-true": lambda: check_countermodel(ENV, (Top(),), ATOM, MODEL),
        "countermodel-budget": lambda: check_countermodel(ENV, (ATOM, Top()), Bottom(), MODEL, max_evaluations=1),
        "search-found": lambda: find_countermodel(ENV, (Top(),), ATOM, max_domain_size=1),
        "search-not-found": lambda: find_countermodel(ENV, (ATOM,), ATOM, max_domain_size=1),
        "distinguishing-found": lambda: find_distinguishing_model(ENV, ATOM, Not(ATOM), max_domain_size=1),
        "readings-superposed": lambda: rust_jsonl.run(_superposed_case()),
        # Rejections: an undeclared predicate and a model of another vocabulary.
        "rejected-symbol": lambda: rust_jsonl.run({"id": "typing", "kind": "check", "environment": ENV.to_dict(),
                                                   "ast": ["unary", "absent", ["const", "x"]]}),
        "rejected-model": lambda: rust_jsonl.run({"id": "evaluate", "kind": "evaluate-budgeted",
                                                  "environment": ENV.to_dict(), "ast": [["top"]],
                                                  "model": {**model_wire(ENV), "constants": {}},
                                                  "max_evaluations": 10, "trace": False}),
    }


@pytest.fixture(scope="module")
def genuine():
    """{name: (case, record, exit status)}: what the built checker answered each adapter."""
    seen, original = [], rust_jsonl._run_checker

    def spy(argv, *, input, timeout):
        completed = original(argv, input=input, timeout=timeout)
        seen.append((json.loads(input), json.loads(completed.stdout), completed.returncode))
        return completed

    out = {}
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("VE_AUTHORITY", "rust-experimental")
        patch.setattr(rust_jsonl, "_run_checker", spy)
        for name, call in _calls().items():
            seen.clear()
            try:
                call()
            except VEError:
                pass
            assert seen, name
            # The adapter's own call is the last; the typing calls before it are records too.
            out[name] = seen[-1]
            out |= {f"{name}/{i}": entry for i, entry in enumerate(seen[:-1])}
    return out


def _feed(monkeypatch, case, record, status):
    """`rust_jsonl.run(case)` over a checker that answers `record` with exit status `status`."""
    line = record if isinstance(record, bytes) else json.dumps(record, ensure_ascii=False).encode()

    def answer(argv, *, input, timeout):
        return subprocess.CompletedProcess(argv, status, line + b"\n", b"")
    monkeypatch.setattr(rust_jsonl, "_run_checker", answer)
    return rust_jsonl.run(case)


@pytest.mark.parametrize("bad_record", [b"not-json", b'{"id":"other","status":"Satisfied","value":true,"evaluations":1}'])
def test_invalid_record_discards_process_before_next_case(monkeypatch, bad_record):
    """A poisoned process cannot answer a later bottom case with a stale Satisfied record."""
    rust_jsonl._close_all()
    case = {"id": "bottom", "kind": "evaluate-budgeted", "environment": ENV.to_dict(),
            "ast": [["bottom"]], "model": MODEL.to_dict(), "max_evaluations": 10, "trace": False}
    original = rust_jsonl._Checker.exchange
    first = []

    def poisoned(self, data, timeout):
        if not first:
            first.append(self)
            return bad_record
        if self is first[0]:
            return b'{"id":"bottom","status":"Satisfied","value":true,"evaluations":1}'
        return original(self, data, timeout)

    monkeypatch.setattr(rust_jsonl._Checker, "exchange", poisoned)
    try:
        with pytest.raises(CheckerUnavailable):
            rust_jsonl.run(case)
        assert first[0].process.poll() is not None
        answer = rust_jsonl.run(case)
        assert answer["status"] == "Violated" and answer["value"] is False
    finally:
        rust_jsonl._close_all()


def test_every_record_shape_is_exercised(genuine):
    """The genuine records cover every branch of the schema's selection and both outcomes."""
    shapes = {"error" if record["status"] == "error" else case.get("kind", "countermodel" if "model" in case
                                                                     else "search")
              for case, record, _ in genuine.values()}
    # No adapter sends `evaluate-budgeted` since lean-first batch 15b (evaluation is Lean's metered
    # evaluator's); the conformance tooling still does.
    assert shapes == {"error", "check", "countermodel", "search", "distinguishing-model",
                      "readings-superposed-evaluate"}
    statuses = {record["status"] for _, record, _ in genuine.values()}
    assert statuses >= {"ok", "error", "Satisfied", "Violated", "ResourceLimit", "Valid", "NotCountermodel",
                        "Found", "NotFound"}
    values = {(record["status"], record["conclusion_value"]) for _, record, _ in genuine.values()
              if "conclusion_value" in record}
    assert values == {("Valid", False), ("NotCountermodel", None), ("NotCountermodel", True), ("ResourceLimit", None)}


def test_genuine_records_are_answers(monkeypatch, genuine):
    for name, (case, record, status) in genuine.items():
        assert rust_jsonl.record_problem(case, record) is None, name
        if record["status"] == "error":
            with pytest.raises(VEError) as caught:
                _feed(monkeypatch, case, record, status)
            assert caught.value.code == record["error"]["code"] and caught.value.backend_rejection
            assert caught.value.message.endswith(record["error"]["message"])
        else:
            assert _feed(monkeypatch, case, record, status) == record


def _paths(value, path=()):
    """Every node of `value` with its path, to depth 4."""
    yield path, value
    if len(path) < 4:
        if isinstance(value, dict):
            for key, item in value.items():
                yield from _paths(item, path + (key,))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                yield from _paths(item, path + (index,))


def _replace(value, path, new):
    if not path:
        return new
    head, rest = path[0], path[1:]
    if isinstance(value, dict):
        out = dict(value)
        if new is DROP and not rest:
            del out[head]
        else:
            out[head] = _replace(value[head], rest, new)
        return out
    out = list(value)
    if new is DROP and not rest:
        del out[head]
    else:
        out[head] = _replace(value[head], rest, new)
    return out


DROP = object()
# Each field dropped, emptied ("" [] {}), nulled and retyped (7, true, a string).
REPLACEMENTS = {"drop": DROP, "empty-text": "", "empty-array": [], "empty-object": {}, "null": None,
                "number": 7, "true": True, "text": "x"}


# The fields whose type includes null (`Option<bool>`): null there is a value, not a retyping.
NULLABLE = {"value", "conclusion_value"}
# A witness model's maps are keyed by the environment's names: which entries it holds is checked
# against the environment by the adapter (`FiniteModel.from_dict`), as a list's length is.
WITNESS_MAPS = {("model", "domains"), ("model", "constants"), ("model", "relations")}


def _mutants(genuine):
    """(label, case, mutated record, exit status, whether the mutant is the same kind of value)."""
    for name, (case, record, status) in genuine.items():
        for path, value in _paths(record):
            if not path:
                continue
            for label, new in REPLACEMENTS.items():
                if new is not DROP and same_json(new, value):
                    continue
                if new is DROP and isinstance(path[-1], int):
                    continue  # a list's length is content, or the request's (`x-length`)
                same_kind = (type(new) is type(value) or new is None and path[-1] in NULLABLE if new is not DROP
                             else path[-3:-1] in WITNESS_MAPS)
                yield (f"{name}:{'.'.join(map(str, path))}:{label}", case, _replace(record, path, new), status,
                       same_kind)


def test_every_mutated_record_is_checker_unavailable(monkeypatch, genuine):
    """Table-driven over every field of every genuine record: a record Rust cannot write is no answer.

    A mutant of the same kind as the value it replaces (another count, text, Boolean, list or object)
    that the schema admits is another record Rust can write: its content is the adapters' to compare
    with Python's or Lean's answer. Every other mutant must be refused, on every path."""
    refused, content, wrong = 0, 0, []
    for label, case, record, status, same_kind in _mutants(genuine):
        if same_kind and rust_jsonl.record_problem(case, record) is None:
            content += 1
            continue
        try:
            _feed(monkeypatch, case, record, status)
            wrong.append(f"{label}: accepted")
        except CheckerUnavailable:
            refused += 1
        except Exception as exc:  # noqa: BLE001
            wrong.append(f"{label}: {type(exc).__name__}: {exc}")
    assert not wrong, "\n".join(wrong)
    assert refused > 10 * content > 0


# lf-0 fix3 B2: the reproducers, each with its genuine control.
CASE = {"id": "c", "kind": "check", "environment": ENV.to_dict(), "ast": ["unary", "absent", ["const", "x"]]}


@pytest.mark.parametrize("record", [
    {"id": "c", "status": "error"},
    {"id": "c", "status": "error", "error": {"code": "UnknownSymbol", "message": None}},
    {"id": "c", "status": "error", "error": {"code": "UnknownSymbol"}},
    {"id": "c", "status": "error", "error": {"code": "UnknownSymbol", "message": ""}},
    {"id": "c", "status": "error", "error": {"code": None, "message": "UnknownSymbol: x"}},
    {"id": "c", "status": "error", "error": {"code": "", "message": "UnknownSymbol: x"}},
    {"id": "c", "status": "error", "error": "UnknownSymbol: x"},
    {"id": "c", "status": "error", "error": None},
    {"id": "c", "status": "error", "error": {"code": "UnknownSymbol", "message": "x", "span": None}},
    {"id": "c", "status": "error", "error": {"code": "UnknownSymbol", "message": "x",
                                              "span": {"start": 0, "end": 1, "line": 1}}},
    {"id": "c", "status": "error", "error": {"code": "UnknownSymbol", "message": "x"}, "generator": "g"},
], ids=["no-error", "null-message", "no-message", "empty-message", "null-code", "empty-code", "text-error",
        "null-error", "null-span", "partial-span", "extra-field"])
def test_a_rejection_without_a_complete_diagnostic_is_checker_unavailable(monkeypatch, record):
    with pytest.raises(CheckerUnavailable, match="malformed Rust response") as caught:
        _feed(monkeypatch, CASE, record, 1)
    assert not isinstance(caught.value, VEError)


def test_a_complete_rust_diagnostic_is_its_rejection(monkeypatch):
    record = {"id": "c", "status": "error", "error": {"code": "UnknownSymbol", "message": "UnknownSymbol: x",
                                                      "span": {"start": 0, "end": 1, "line": 1, "column": 1}}}
    with pytest.raises(UnknownSymbol) as caught:
        _feed(monkeypatch, CASE, record, 1)
    assert caught.value.message == "UnknownSymbol: x" and caught.value.backend_rejection
    assert caught.value.span.column == 1


def test_a_case_of_a_shape_no_adapter_sends_has_no_record(monkeypatch):
    """The selection follows `case` in main.rs for the shapes Python sends; any other case is unanswerable."""
    with pytest.raises(CheckerUnavailable, match="no result is possible"):
        _feed(monkeypatch, {"id": "c", "kind": "label", "label": "x"}, {"id": "c", "status": "ok", "label": "x"}, 0)
