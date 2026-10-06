"""Every checker transport sends only values `json` writes as themselves (lf-9 review, B).

The W6 relays (environment, typing, meaning ids, certificates, countermodels, document admission)
sent the caller's data to Lean with no wire check, which the Python decoders they replaced ran
first: a lone surrogate escaped as `UnicodeEncodeError`, a set or bytes as `TypeError`, and `json`
sent a tuple formula as a list, so it was admitted. `ve.environment_wire.wire_checked` is the one
check, in `relay.decide`, `relay.rows` and `rust_jsonl.run`, and only a `VEError` may escape any
entry point. JSON that is off the restricted subset (null, a float, a negative or huge integer, a
depth past 256) is still sent, and Lean decides it in Lean's words (R9, signed row W9.3)."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ve.admission import admit_document
from ve.backends import relay, rust_jsonl
from ve.document import check_document
from ve.environment import Environment
from ve.environment_wire import TRANSPORT_DEPTH, EncodedEnvironment, wire_checked
from ve.errors import ResourceLimit, VEError
from ve.units import (check_quantity_certificate, elaborate_quantity, quantity_countermodel,
                      quantity_meaning_id)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "usecases" / "news-article" / "w6a-quantity-fixtures.json"
DOCUMENT = ROOT / "usecases" / "news-article" / "news-w6a.ve.md"
SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
needs_service = pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")


def _cycle():
    value = ["not"]
    value.append(value)
    return value


def _nested(depth):
    value = ["top"]
    for _ in range(depth):
        value = ["not", value]
    return value


# Python values `json` cannot send as themselves: it raises on a surrogate, a set, bytes, an
# object or a cycle, writes `NaN` for a non-finite float and sends a tuple as a list.
UNSENDABLE = {"surrogate": lambda: "\ud800", "set": lambda: {"a"}, "bytes": lambda: b"a",
              "tuple": lambda: ("top",), "object": object, "nan": lambda: float("nan"),
              "infinity": lambda: float("inf"), "cycle": _cycle,
              "past-transport-depth": lambda: _nested(TRANSPORT_DEPTH + 1)}
WIRE_TEXT = {name: "Unsupported JSON value" for name in UNSENDABLE} | {
    "surrogate": "lone UTF-16 surrogates", "cycle": "runtime limit", "past-transport-depth": "runtime limit"}
# JSON values that are off the subset or the wrong shape (build checklist 5): Lean decides them.
SENDABLE = {"seven": lambda: 7, "true": lambda: True, "null": lambda: None, "empty-list": list,
            "empty-object": dict, "float": lambda: 1.5, "negative": lambda: -1,
            "too-large": lambda: 2**53, "deep": lambda: _nested(300)}


@pytest.fixture(scope="module")
def news():
    fixture = json.loads(FIXTURE.read_text())
    return fixture, Environment(fixture["environment"])


def _payload(fixture):
    return {"format": "ve-quantity@1", "formula": copy.deepcopy(fixture["cases"][0]["formula"])}


def _entry_points(fixture, env):
    """Each W6 relay, as a function of the one caller value it is given."""
    p = _payload(fixture)

    def environment(value):
        raw = copy.deepcopy(fixture["environment"])
        raw["vocabulary"]["constants"]["decision_date"]["description"] = value
        return Environment(raw)

    return {
        "environment": environment,
        "elaborate": lambda v: elaborate_quantity(env, {"format": "ve-quantity@1", "formula": ["eq", v, v]}),
        "meaning-id": lambda v: quantity_meaning_id(env, {"format": "ve-quantity@1", "formula": v}),
        "certificate": lambda v: check_quantity_certificate(env, [p], p, {"format": v}),
        "countermodel": lambda v: quantity_countermodel(env, [p], p, {"complete": v}),
        "admission": lambda v: admit_document(env, {"format": v, "units": []}),
    }


ENTRY_POINTS = ["environment", "elaborate", "meaning-id", "certificate", "countermodel", "admission"]


@needs_service
@pytest.mark.parametrize("entry", ENTRY_POINTS)
@pytest.mark.parametrize("name", list(UNSENDABLE))
def test_unsendable_caller_data_is_the_wires_veerror(news, monkeypatch, entry, name):
    fixture, env = news
    pool = _Pool()
    monkeypatch.setattr(relay, "_pool_for", lambda executable: pool)
    with pytest.raises(VEError, match=WIRE_TEXT[name]):
        _entry_points(fixture, env)[entry](UNSENDABLE[name]())
    assert pool.calls == []  # nothing reached Lean


@needs_service
@pytest.mark.parametrize("entry", ENTRY_POINTS)
@pytest.mark.parametrize("name", list(SENDABLE))
def test_sendable_caller_data_raises_only_veerror(news, entry, name):
    """Checklist 5: 7/true/null/[]/{}/deep and off-subset numbers at each entry point; Lean answers
    and only `VEError` escapes."""
    fixture, env = news
    with pytest.raises(VEError):
        _entry_points(fixture, env)[entry](SENDABLE[name]())


@needs_service
def test_a_tuple_formula_is_not_admitted_as_a_list(news):
    fixture, env = news
    payload = _payload(fixture)
    elaborate_quantity(env, payload)
    payload["formula"] = tuple(payload["formula"])
    with pytest.raises(VEError, match="Unsupported JSON value"):
        elaborate_quantity(env, payload)


@needs_service
def test_an_integer_key_is_not_sent_as_a_string(news):
    fixture, env = news
    with pytest.raises(VEError, match="keys must be strings"):
        elaborate_quantity(env, {**_payload(fixture), 1: "x"})
    raw = copy.deepcopy(fixture["environment"])
    raw["units"][1] = raw["units"].pop(next(iter(raw["units"])))
    with pytest.raises(VEError, match="keys must be strings"):
        Environment(raw)


@needs_service
def test_every_node_of_a_formula_replaced_by_an_unsendable_value_is_the_wires_veerror(news):
    """Each node of a genuine annotated formula, at any depth, replaced by each unsendable value."""
    fixture, env = news

    def paths(value, prefix=()):
        yield prefix
        if type(value) is list:
            for i, item in enumerate(value):
                yield from paths(item, (*prefix, i))

    formula = fixture["cases"][0]["formula"]
    for path in list(paths(formula))[1:]:
        for name, bad in UNSENDABLE.items():
            mutated = copy.deepcopy(formula)
            node = mutated
            for i in path[:-1]:
                node = node[i]
            node[path[-1]] = bad()
            with pytest.raises(VEError, match=WIRE_TEXT[name]):
                elaborate_quantity(env, {"format": "ve-quantity@1", "formula": mutated})


@needs_service
def test_depth_past_256_is_still_leans_to_answer(news):
    """Signed row W9.3: the transport does not preempt Lean's depth limit."""
    _, env = news
    for depth in (300, TRANSPORT_DEPTH // 2):
        with pytest.raises(ResourceLimit, match="^ResourceLimit: JSON depth exceeds 256$"):
            elaborate_quantity(env, {"format": "ve-quantity@1", "formula": _nested(depth)})


@needs_service
def test_document_check_of_a_file_with_a_lone_surrogate_is_the_wires_veerror(tmp_path):
    """The review's reproduction: stdlib `json.loads` reads `"\\ud800"` in the front matter."""
    text = DOCUMENT.read_text()
    assert '"description": "' in text
    path = tmp_path / DOCUMENT.name
    path.write_text(text.replace('"description": "', '"description": "\\ud800', 1))
    with pytest.raises(VEError, match="lone UTF-16 surrogates"):
        check_document(path)


class _Pool:
    def __init__(self):
        self.calls = []

    def run_bound(self, mode, cases, *, timeout=None):
        self.calls.append(cases)
        return [{"index": i, "digest": "0" * 64, "result": {"status": "ok"}} for i, _ in enumerate(cases)]


@pytest.mark.parametrize("call", [relay.decide, relay.rows])
@pytest.mark.parametrize("name", list(UNSENDABLE))
def test_the_relay_sends_nothing_unsendable(monkeypatch, call, name):
    pool = _Pool()
    monkeypatch.setattr(relay, "_pool_for", lambda executable: pool)
    with pytest.raises(VEError, match=WIRE_TEXT[name]):
        call("check", [{"id": "a"}, {"id": "b", "quantity": {"formula": UNSENDABLE[name]()}}])
    assert pool.calls == []
    assert call("check", [{"id": "a"}]) == [{"status": "ok"}]


@pytest.mark.parametrize("cases", [({"id": "a"},), {"id": "a"}, None])
def test_a_batch_is_a_list(cases):
    with pytest.raises(VEError):
        wire_checked(cases)


def test_shared_values_and_cached_environments_pass():
    environment = EncodedEnvironment({"language": "ve.core@0.2", "profiles": ["time@0"]})
    shared = ["top"]
    cases = [{"id": "a", "environment": environment, "f": ["and", shared, shared]},
             {"id": "b", "environment": environment, "n": None, "x": 1.5, "i": -(2**80)}]
    assert wire_checked(cases) is cases and cases[0]["environment"] is environment
    # The case is level 0 and `_nested(d)` has d + 1 levels: the innermost list here is at
    # level TRANSPORT_DEPTH - 1, the last level sent.
    wire_checked([{"deep": _nested(TRANSPORT_DEPTH - 2)}])
    with pytest.raises(ResourceLimit, match="runtime limit"):
        wire_checked([{"deep": _nested(TRANSPORT_DEPTH - 1)}])


@pytest.mark.parametrize("name", list(UNSENDABLE))
def test_the_rust_transport_sends_nothing_unsendable(tmp_path, name):
    """The check comes before any process or build-lock check: a missing binary is never
    reached."""
    with pytest.raises(VEError, match=WIRE_TEXT[name]):
        rust_jsonl.run({"id": "a", "ast": UNSENDABLE[name]()}, executable=tmp_path / "absent")
