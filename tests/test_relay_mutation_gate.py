"""tools/relay_mutation_gate.py: every relayed Lean answer refuses every mutant of a genuine answer.

* The mutation classes: every field of an answer is dropped, emptied, duplicated (an array element, and a key
  written twice in the line) and retyped to each other JSON type; a string the request names, the result's
  position, its digest, the nonce and the envelope's counts are rebound to values the request does not hold.
* The routes are complete: the one-shot readers are exactly the `ve` call sites of one-shot runners (manifest
  bindings with call sites, and calls of the route reader), every service mode and one-shot route has
  fixtures, and a route without an `ok` fixture fails the gate.
* Through the client's own reader (`LeanService.exchange` with the line replaced): a genuine answer is
  accepted and a mutant of its binding is CheckerUnavailable.
* On sample routes against the built Lean executables the gate passes with the committed allow-list, and fails
  on an accepted mutant the allow-list does not list, on an allow-list entry that matches nothing, and on a
  route whose fixtures are gone.
* The speech-source reader refuses a unit whose class or status is a list or an object (it raised TypeError).
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

from tests.lean_build import lean_build

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import relay_mutation_gate as G  # noqa: E402
from ve.backends.service_schema import MODES  # noqa: E402


# Mutation classes


def _kinds(found):
    return {(m.kind, m.pattern(), m.value) for m, _ in found}


def test_every_field_gets_every_mutation_class():
    answer = {"id": "case-1", "status": "ok", "names": ["p", "q"], "count": 2, "flag": True, "inner": {"k": "v"}}
    found = G.mutants(answer, named={"case-1", "p"}, rebind_ints={("count",): 3})
    kinds = _kinds(found)
    for field in ("id", "status", "names", "count", "flag", "inner"):
        assert ("drop", field, None) in kinds
        retypes = {value for kind, pattern, value in kinds if kind == "retype" and pattern == field}
        assert len(retypes) >= len(G.RETYPES) - 1, (field, retypes)
    assert ("retype", "count", "number") in kinds          # 7.5 for an integer
    assert ("empty", "status", None) in kinds and ("empty", "names", None) in kinds
    assert ("duplicate", "names", None) in kinds and ("duplicate", "inner", None) in kinds
    # Rebinding: a name the request gives (emptying one is a rebind too), and a bound integer.
    assert ("rebind", "id", None) in kinds and ("rebind", "id", "") in kinds and ("rebind", "names/*", None) in kinds
    assert ("rebind", "count", None) in kinds
    assert not any(kind == "rebind" and pattern in ("status", "inner/k") for kind, pattern, _ in kinds)
    rebound = dict((m.path, value) for m, value in found if m.kind == "rebind" and m.value is None)
    assert rebound[("id",)]["id"] == G.FRESH and rebound[("count",)]["count"] == 3


def test_a_duplicated_key_is_written_twice_in_the_line():
    found = [(m, value) for m, value in G.mutants({"a": {"x": 1, "y": 2}}, set(), {})
             if m.kind == "duplicate" and m.duplicate_key]
    [(mutant, value)] = found
    assert G._text(mutant, value) == '{"a":{"x":1,"x":1,"y":2}}'


# Routes


def test_one_shot_readers_are_exactly_the_one_shot_call_sites():
    inventory = G.one_shot_inventory()
    assert set(inventory) == set(G.ONE_SHOT)
    assert "call:ve.backends.speech_source:decide_source" in inventory
    assert "ve_senses_route::senses.read" in inventory


def test_every_route_has_fixtures():
    cases = G.load_cases()
    service = {row[1] for row in cases if row[0] == "service"}
    assert service == set(MODES)
    one_shot = {G._one_shot_route(row[1], row[2], row[3]) for row in cases if row[0] == "one-shot"}
    assert one_shot == set(G.ONE_SHOT)


@pytest.fixture(scope="module")
def built():
    lean_build("ve_service", "ve_speech_acts_route", "ve_metered")


def _genuine(mode):
    case = next(row[2] for row in G.load_cases() if row[0] == "service" and row[1] == mode)
    text = json.dumps(case, separators=(",", ":"))
    [answer] = G._service_answers(G.DEFAULT_EXECUTABLE, mode, [text])
    return text, answer


def test_the_client_reader_accepts_a_genuine_answer_and_refuses_a_rebound_one(built):
    text, answer = _genuine("identity")
    replay = G._Replay()
    replay.answer, replay.mutant = answer, None
    assert G._exchange_outcome(replay, "identity", "[" + text + "]") == ("accepted", "")
    for path, value in ((("results", 0, "digest"), "0" * 64), (("results", 0, "index"), 1)):
        mutant = G.Mutant("rebind", path)
        replay.answer, replay.mutant = G._replace(answer, path, value), mutant
        outcome, detail = G._exchange_outcome(replay, "identity", "[" + text + "]")
        assert outcome == "refused" and "CheckerUnavailable" in detail
    replay.answer, replay.mutant = answer, G.Mutant("rebind", ("id",))
    replay.answer = {**answer, "id": G.FRESH}
    assert G._exchange_outcome(replay, "identity", "[" + text + "]")[0] == "refused"


SAMPLE = ("service:identity", "service:check", "ve_metered::countermodel.search")


def test_the_gate_passes_on_sample_routes_with_the_committed_allow_list(built):
    report = G.run_gate(set(SAMPLE))
    assert report["failures"] == []
    assert set(report["routes"]) == set(SAMPLE)
    for route in SAMPLE:
        stats = report["routes"][route]
        assert stats["ok_fixtures"] >= 1 and stats["mutants"] == stats["refused"] + stats.get("allowed", 0)
    # service:check's untyped unsat core is listed as a follow-up, so some mutants were allowed.
    assert report["routes"]["service:check"]["allowed"] > 0


def test_the_gate_fails_on_an_unlisted_accepted_mutant_and_on_a_stale_entry(built, tmp_path):
    allow = json.loads(G.ALLOW.read_text())
    kept = [entry for entry in allow["entries"] if entry["route"] != "service:check"]
    stale = {"route": "service:identity", "mutation": "drop", "path": ["results/*/result/no_such_field"],
             "kind": "follow-up", "id": "X", "reason": "test"}
    path = tmp_path / "allow.json"
    path.write_text(json.dumps({"entries": kept + [stale]}))
    report = G.run_gate({"service:check", "service:identity"}, allow_path=path)
    failures = "\n".join(report["failures"])
    assert "accepted service:check retype results/*/result/core/*" in failures
    assert "untyped service:check untyped results/*/result/core/*" in failures
    assert "allow-list path matches nothing: X service:identity drop results/*/result/no_such_field" in failures


def test_a_route_without_fixtures_fails_the_gate(built, tmp_path):
    path = tmp_path / "cases.jsonl"
    path.write_text("".join(json.dumps(row) + "\n" for row in G.load_cases()
                            if row[:2] != ["service", "identity"]))
    report = G.run_gate({"service:identity"}, cases_path=path)
    assert "route service:identity has no fixture with an ok answer" in report["failures"]


def test_the_speech_source_reader_refuses_an_unhashable_unit_class(built, tmp_path):
    case = next(row[3] for row in G.load_cases() if row[0] == "one-shot" and row[1] == "ve_speech_acts_route")
    status, stdout = G._run_runner("ve_speech_acts_route", "-", case)
    stand_in = G._StandIn(tmp_path)
    stand_in.set(stdout, status)
    assert G._call_outcome(G._speech_source, case, stand_in.path) == ("accepted", "")
    [row] = json.loads(stdout)
    for field in ("class", "status"):
        for value in ([], {}):
            stand_in.set(json.dumps([G._replace(row, ("units", 0, field), value)]).encode(), status)
            outcome, detail = G._call_outcome(G._speech_source, case, stand_in.path)
            assert outcome == "refused", (field, value, detail)
