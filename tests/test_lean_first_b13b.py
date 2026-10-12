"""Lean-first batch 13b: the core operations default to Lean (docs/lean-first/b13b/DELTA.md).

Every switched relay reads a Lean row that the service schema types (`service_schema.ROWS`, applied by
`run_bound`) and that the relay binds to its request. These tests take each relay's genuine row and every
one-fault structural mutant of it (each member dropped, a member added, each list element dropped or
duplicated, each value retyped, a boolean for a count included), plus an empty and an extra row: none may
reach a caller as an answer (build checklist line 4).
"""
from __future__ import annotations

from copy import deepcopy
import json
import re

import pytest

from ve.backends import dispatch, relay
from ve.backends.service_schema import ROWS, Context, Invalid
from ve.errors import CheckerUnavailable, VEError

from tests.probe_matrix import raw_environment

RETYPES = (7, True, None, [], {}, "x")


def _structural_mutants(node, at=()):
    """(path, mutate) for every one-fault structural mutant of `node` (as in test_document_lean_switch)."""
    def at_path(root, path):
        for key in path:
            root = root[key]
        return root
    if type(node) is dict:
        yield at + ("+forged",), lambda r: at_path(r, at).update(forged_line=7)
        for key in node:
            yield at + (key, "-"), lambda r, key=key: at_path(r, at).pop(key)
    if type(node) is list:
        for i in range(len(node)):
            yield at + (i, "-"), lambda r, i=i: at_path(r, at).pop(i)
            yield at + (i, "x2"), lambda r, i=i: at_path(r, at).insert(i, deepcopy(at_path(r, at)[i]))
    children = node.items() if type(node) is dict else enumerate(node) if type(node) is list else ()
    for key, child in children:
        for value in RETYPES:
            if type(value) is not type(child):
                yield at + (key, f"={value!r}"), lambda r, key=key, value=value: \
                    at_path(r, at).__setitem__(key, deepcopy(value))
        yield from _structural_mutants(child, at + (key,))


def _env(profiles=(), **predicates):
    from ve.environment import Environment
    raw = raw_environment(profiles)
    raw["vocabulary"]["predicates"].update(predicates)
    return Environment(raw)


def _admission_call():
    from ve.admission import admit_document
    from ve.ast import Const, Unary, formula_to_data
    env = _env()
    claim = formula_to_data(env, Unary("base", Const("x")))
    document = {"units": [{"id": "u", "span": [0, 1], "kind": "asserted", "content": claim}],
                "graph": {"root": "a", "nodes": [{"name": "a", "ast": claim, "unit": "u"}]}}
    return lambda: admit_document(env, document)


def _norms_admission_call():
    from ve.norm_admission import admit_norm_document
    from tests.test_norm_admission import source
    env, document = source()
    return lambda: admit_norm_document(env, document)


def _background_call():
    from ve.background import background
    env = _env(("data@0",), linked={"arguments": ["item", "item"], "description": "linked",
                                    "functional": True, "total": True})
    return lambda: background(env)


def _definitions_call():
    from ve.definitions import compile_definitions
    raw = raw_environment(("definitions@0",))
    raw["vocabulary"]["predicates"]["derived"] = {"arguments": ["item"], "description": "derived",
                                                  "defined": {"arguments": ["item"],
                                                              "body": ["unary", "base", ["var", 0]]}}
    from ve.environment import Environment
    env = Environment(raw)
    return lambda: compile_definitions(env, env.definition_entries, version=env.environment_id)


def _label_call():
    from ve.admission import validate_label
    return lambda: validate_label("readings:u@0:1")


def _dependency_call():
    from ve.background import dependency_order
    return lambda: dependency_order({"b": {"a"}, "a": set(), "c": {"a", "b"}})


# (name, the public call, the service mode its row comes from)
RELAYS = {"admission": (_admission_call, "route"), "norms_admission": (_norms_admission_call, "norms"),
          "background": (_background_call, "route"), "definitions": (_definitions_call, "route"),
          "label": (_label_call, "route"), "dependency_order": (_dependency_call, "route")}


def _fresh(monkeypatch):
    """No relay answer is reused across a mutant: Lean's per-request answers and the accepted caches."""
    from ve.backends import validation
    from ve import ast as formula_ast, definitions
    monkeypatch.setattr(relay, "_answers", {})
    monkeypatch.setattr(validation, "_ACCEPTED", {})
    monkeypatch.setattr(formula_ast, "_LEAN_TYPED", {})
    monkeypatch.setattr(definitions, "_COMPILED", {})


def _genuine(monkeypatch, name):
    """The relay's public answer, and the (mode, case, row) of its one Lean call in `RELAYS[name]`'s mode."""
    make, mode = RELAYS[name]
    call = make()
    seen, original = [], relay.decide

    def spy(asked, cases, **kwargs):
        rows = original(asked, cases, **kwargs)
        seen.extend((asked, case, row) for case, row in zip(cases, rows))
        return rows
    _fresh(monkeypatch)
    monkeypatch.setattr(relay, "decide", spy)
    answer = call()
    monkeypatch.setattr(relay, "decide", original)
    mine = [entry for entry in seen if entry[0] == mode]
    assert mine, (name, [entry[0] for entry in seen])
    return call, answer, mine[-1]


def _fed(monkeypatch, call, mode, case, rows):
    """`call()` with Lean answering its `mode` request about `case` with `rows` (other requests are real)."""
    original = relay.decide

    def feed(asked, cases, **kwargs):
        if asked == mode and cases == [case]:
            return deepcopy(rows)
        return original(asked, cases, **kwargs)
    _fresh(monkeypatch)
    monkeypatch.setattr(relay, "decide", feed)
    try:
        return call()
    finally:
        monkeypatch.setattr(relay, "decide", original)


def _same(left, right):
    return json.dumps(left, sort_keys=True, default=repr) == json.dumps(right, sort_keys=True, default=repr)


@pytest.mark.parametrize("name", sorted(RELAYS))
def test_every_structural_mutant_of_a_relayed_row_is_refused(monkeypatch, name):
    """Each mutant is refused by the service's row schema (as `run_bound` applies it) or, if the schema admits
    it, by the relay's own binding; none is returned as an answer different from the genuine one, and a
    mutant the relay returns must be the genuine answer (a field the relay does not read, which the schema
    types)."""
    call, genuine, (mode, case, row) = _genuine(monkeypatch, name)
    accepted, count, schema_refused = [], 0, 0
    for where, mutate in _structural_mutants(row):
        mutant = deepcopy(row)
        mutate(mutant)
        if _same(mutant, row):
            continue
        count += 1
        try:
            ROWS[mode][0](mutant, Context(case), {})
        except Invalid:
            schema_refused += 1
            continue
        try:
            answer = _fed(monkeypatch, call, mode, case, [mutant])
        except (CheckerUnavailable, VEError):
            continue
        if not _same(answer, genuine):
            accepted.append(where)
    assert count >= 8 and schema_refused > 0 and not accepted, (count, accepted)


@pytest.mark.parametrize("name", sorted(RELAYS))
@pytest.mark.parametrize("rows", ["empty", "extra"])
def test_an_empty_or_extra_row_is_refused(monkeypatch, name, rows):
    """The service binds one row to each case (`check_response`): a response line answering the relay's request
    with no row, or with a second row, is a failed exchange, never an answer."""
    from ve.backends.lean_service import LeanService
    call, _, _ = _genuine(monkeypatch, name)
    original = LeanService._read_line

    def read(self, deadline):
        raw = original(self, deadline)
        response = json.loads(raw)
        if type(response.get("results")) is list and response["results"]:
            response["results"] = [] if rows == "empty" else response["results"] + response["results"][-1:]
            return (json.dumps(response) + "\n").encode()
        return raw
    _fresh(monkeypatch)
    monkeypatch.setattr(LeanService, "_read_line", read)
    try:
        with pytest.raises(CheckerUnavailable, match="malformed response"):
            call()
    finally:
        monkeypatch.setattr(LeanService, "_read_line", original)
        relay._close()


@pytest.mark.parametrize("name", sorted(RELAYS))
@pytest.mark.parametrize("selected", ["python", "shadow", "lean", "rust-experimental"])
def test_the_switched_relay_asks_lean_under_every_selection(monkeypatch, name, selected):
    """The default is Lean: under every selection the relay sends its request to Lean and observers see Lean."""
    monkeypatch.setenv("VE_AUTHORITY", selected)
    seen = []
    monkeypatch.setattr(dispatch, "observers", [lambda op, authority: seen.append((op, authority))])
    _, _, (mode, _, _) = _genuine(monkeypatch, name)
    assert mode == RELAYS[name][1]
    assert seen and all(authority == "lean" for op, authority in seen if op in dispatch.LEAN_OWNED)


# ---------------------------------------------------------------- saved evidence (build checklist line 20)

def _report():
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "docs/lean-first/b13b/report.py"
    spec = importlib.util.spec_from_file_location("b13b_report", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_report_numbers_are_regenerated_from_saved_evidence():
    """Every number of REPORT.md's generated block comes from the saved evidence of `docs/lean-first/b13b/evidence`
    (the A/B, the fuzz pairs, the seeded faults, the latency pairs, the gate when recorded, and the branch's own
    commits as `main..HEAD --no-merges` saved at its last source commit); no live git is read, so the check holds
    after a sync with main and after the merge."""
    report = _report()
    assert report.problems() == []
    scope = report.load("scope.json")
    assert scope["commits"] and all(len(c["sha"]) == 40 for c in scope["commits"])
    ab = report.load("corpus-ab.json")
    assert ab["unlisted"] == 0 and not ab["totals"].get("verdict") and not ab["totals"].get("availability")
    assert sum(ab["totals"].values()) == sum(ab["records"].values()) > 90_000  # records per side


def test_the_delta_lists_exactly_the_recorded_differences():
    """DELTA.json is the comparison's own list: each order record is a recorded difference with both outcomes,
    and each wording pair occurs in a recorded wording difference."""
    import json
    from pathlib import Path
    from tools.lean_first_diff import text_pairs
    here = Path(__file__).resolve().parents[1] / "docs/lean-first/b13b"
    delta = json.loads((here / "DELTA.json").read_text())
    differences = _report().load("corpus-ab.json")["differences"]
    order = [{k: d[k] for k in ("corpus", "authority", "case", "op", "base", "head")}
             for d in differences if d["class"] == "order"]
    assert sorted(map(json.dumps, order)) == sorted(map(json.dumps, delta["order"]))
    used = {(a, b) for d in differences if d["class"] == "wording" for a, b in text_pairs(d["base"], d["head"])}
    assert {(p["base"], p["head"]) for p in delta["wording"]} == used


def test_no_consumer_of_a_deleted_decision_site():
    """The deletion ledger: no module of `ve/`, `tools/`, `conformance/` or the tests names a deleted body."""
    from pathlib import Path
    import ve.admission as admission, ve.background as background, ve.norm_admission as norm_admission
    from ve.backends import validation
    deleted = {admission: ("_admit_document_python", "_validate_label_python", "_check_graph", "_decode_doc",
                           "_node_admitted"),
               norm_admission: ("_admit_norm_document_python",),
               background: ("_background_python", "_dependency_order_python", "_flag_premises",
                            "_profile_premises"),
               validation: ("decided",)}
    for module, names in deleted.items():
        assert not [name for name in names if hasattr(module, name)], module.__name__
    root = Path(__file__).resolve().parents[1]
    names = [n for group in deleted.values() for n in group if n.startswith("_")]
    for folder in ("ve", "tools", "conformance"):
        for path in (root / folder).rglob("*.py"):
            used = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", path.read_text()))
            assert not used & set(names), path
