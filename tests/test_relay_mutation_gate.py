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
* The answer itself is mutated: a one-shot answer's row array is emptied, duplicated and retyped, so a reader
  that drops its one-row-per-case check fails the gate (review B2).
* The allow-list names one route per entry and lists its paths (no wildcard route or path), the most specific
  entry takes a finding, and no by-design entry lists an id, digest or choice: a client that drops a check of
  the length of a request-bound list fails the gate (review B1).
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path
import re
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


def test_fields_near_the_top_are_also_replaced_by_a_deep_array():
    found = G.mutants({"a": {"b": {"c": 1}}}, set(), {}, deep_depth=2)
    deep = {m.pattern() for m, _ in found if m.value == "deep"}
    assert deep == {".", "a", "a/b"}
    mutant, value = next((m, v) for m, v in found if m.value == "deep" and m.pattern() == "a/b")
    text = G._text(mutant, value)
    assert text.startswith('{"a":{"b":' + "[" * G.DEEP_LEVELS) and text.count("]") == G.DEEP_LEVELS


def test_a_duplicated_key_is_written_twice_in_the_line():
    found = [(m, value) for m, value in G.mutants({"a": {"x": 1, "y": 2}}, set(), {})
             if m.kind == "duplicate" and m.duplicate_key and m.path]
    [(mutant, value)] = found
    assert G._text(mutant, value) == '{"a":{"x":1,"x":1,"y":2}}'


def test_the_answer_itself_is_emptied_duplicated_and_retyped():
    """Review B2: the root was skipped, so a one-shot answer never lost or gained a row."""
    rows = [{"status": "ok", "id": "c"}]
    found = {(m.kind, m.pattern(), m.value): value for m, value in G.mutants(rows, {"c"}, {}, deep_depth=1)}
    assert found[("empty", ".", None)] == []
    assert found[("duplicate", ".", None)] == rows + rows
    for kind in ("null", "boolean", "integer", "string", "object"):
        assert found[("retype", ".", kind)] == G.RETYPES[kind]
    assert found[("retype", ".", "deep")] is G.DEEP
    assert not any(kind == "drop" and pattern == "." for kind, pattern, _ in found)
    [(mutant, answer)] = [(m, v) for m, v in G.mutants({"a": 1}, set(), {}) if m.kind == "duplicate"]
    assert G._text(mutant, answer) == '{"a":1,"a":1}'


# The allow-list


def test_the_committed_allow_list_names_one_route_per_entry_and_lists_its_paths():
    assert G.allow_problems(json.loads(G.ALLOW.read_text())["entries"]) == []


def test_a_wildcard_route_or_path_is_refused():
    """Review B1: B0 (route `*`, path `*`) allowed every emptied or repeated field of every route."""
    entry = {"route": "*", "mutation": "empty", "path": "*", "kind": "by-design", "id": "B0", "reason": "r"}
    problems = G.allow_problems([entry])
    assert any("names no single route" in problem for problem in problems)
    assert any("no list of paths" in problem for problem in problems)
    for path in ("*", "*/*", "*/*/?"):
        problems = G.allow_problems([{**entry, "route": "service:check", "path": [path]}])
        assert problems == [f"allow-list entry 0 (B0) lists the wildcard path {path!r}: list the fields"]
    assert G.allow_problems([{**entry, "route": "service:english.*", "path": ["results/*/result/x"]}])
    assert G.allow_problems([{k: v for k, v in entry.items() if k != "reason"}])


def test_the_most_specific_entry_takes_a_finding():
    """Review B1: the first entry in file order took a finding a narrower entry listed (B0 took F1's counts)."""
    def entry(id_, mutation, path):
        return {"route": "service:m", "mutation": mutation, "path": [path], "kind": "follow-up", "id": id_,
                "reason": "r"}
    broad, narrow = entry("F", "*", "results/*/result/*"), entry("N", "*", "results/*/result/x*")
    for order in ([broad, narrow], [narrow, broad]):
        assert G._allowed(order, "service:m", "empty", "results/*/result/xy")["id"] == "N"
        assert G._allowed(order, "service:m", "empty", "results/*/result/y")["id"] == "F"
    literal, any_mutation = entry("L", "*", "results/*/result/xy"), entry("M", "empty", "results/*/result/x*")
    assert G._allowed([narrow, any_mutation, literal], "service:m", "empty", "results/*/result/xy")["id"] == "L"
    assert G._allowed([narrow, any_mutation], "service:m", "empty", "results/*/result/xy")["id"] == "M"
    assert G._allowed([narrow], "service:other", "empty", "results/*/result/xy") is None


ID_LIKE = re.compile(r"(^id|_id|_hash|^digest|^choices?|^per_choice|^tuple|^arguments)$")


def test_no_by_design_entry_lists_an_id_digest_or_request_bound_list():
    """Review B1: B0 waived emptied `environment_id`, `document_id` and readings-route `choice`; those are
    follow-ups (F10, F11), not content Lean computes."""
    for entry in json.loads(G.ALLOW.read_text())["entries"]:
        if entry["kind"] != "by-design" or entry["mutation"] not in ("empty", "duplicate"):
            continue
        for path in entry["path"]:
            leaf = [step for step in path.split("/") if step != "*"][-1]
            assert not ID_LIKE.search(leaf), (entry["id"], entry["route"], path)


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


def test_readings_route_refuses_empty_labels_targets_and_repeated_over_names(built):
    cases = [row[2] for row in G.load_cases() if row[:2] == ["service", "readings-route"]]
    texts = [json.dumps(case, separators=(",", ":")) for case in cases]
    answers = G._service_answers(G.DEFAULT_EXECUTABLE, "readings-route", texts)
    wanted = {
        ("empty", "results/*/result/fill/*/label"),
        ("empty", "results/*/result/targets/*"),
        ("duplicate", "results/*/result/units/*/content/norm/over"),
    }
    found = set()
    replay = G._Replay()
    for case, line, answer in zip(cases, texts, answers):
        for mutant, changed in G.mutants(answer, G._strings(case), G._service_rebind_ints(answer)):
            key = (mutant.kind, mutant.pattern())
            if key not in wanted or key in found:
                continue
            replay.answer, replay.mutant = changed, mutant
            outcome, detail = G._exchange_outcome(replay, "readings-route", "[" + line + "]")
            assert outcome == "refused", (key, detail)
            found.add(key)
    assert found == wanted


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


def test_the_recorder_writes_every_relayed_case(built, tmp_path):
    """`tests/route_case_recorder.py` with VE_RELAY_CASES records service and one-shot cases as sent."""
    import os
    import subprocess
    sys.path.insert(0, str(ROOT / "tools"))
    import nested_pytest
    service = next(row[2] for row in G.load_cases() if row[:2] == ["service", "identity"])
    one_shot = next(row[3] for row in G.load_cases() if row[0] == "one-shot" and row[1] == "ve_metered"
                    and row[3].get("kind") == "non-vacuity")
    probe = tmp_path / "test_probe.py"
    probe.write_text("import json\n"
                     "from ve.backends import relay, lean_runner\n"
                     f"def test_probe():\n"
                     f"    relay.rows('identity', [json.loads({json.dumps(json.dumps(service))})])\n"
                     f"    lean_runner.metered_nonvacuity(json.loads({json.dumps(json.dumps(one_shot))}))\n")
    out = tmp_path / "recorded"
    done = subprocess.run(nested_pytest.command(["-q", "-p", "tests.route_case_recorder", "-p", "no:cacheprovider",
                                                 "--rootdir", str(ROOT), str(probe)]),
                          cwd=ROOT, env=nested_pytest.environment(os.environ, VE_RELAY_CASES=str(out)),
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout[-2000:]
    rows = [json.loads(line) for path in out.glob("relay-*.jsonl") for line in path.read_text().splitlines()]
    assert ["service", "identity", json.dumps(service, separators=(",", ":"))] in [
        [row[0], row[1], json.dumps(json.loads(row[2]), separators=(",", ":"))] for row in rows if row[0] == "service"]
    assert any(row[:3] == ["one-shot", "ve_metered", ""] and json.loads(row[3]) == one_shot for row in rows)



# The reviewer's probes: the client with one check removed in memory must fail the gate.


@pytest.fixture
def without_length_check(monkeypatch):
    """The service client with its per-request length check (`x-length`) switched off. Every validator
    the client applies, the rows (`ROWS`) and the response envelope (`check_response`), is compiled
    lazily by the module's one `_compiler`, so a fresh compiler without the check replaces it.
    (The envelope's own `x-length` on `results` repeats its `x-rows` count, so the rows' checks decide
    the outcome.) ts-B1's merge verify ran the whole suite, but on a worktree holding this fix
    uncommitted, so main got the old fixture; test selection did pick this file."""
    from ve.backends import service_schema as S
    monkeypatch.setattr(S.Compiler, "_x_length", lambda self, pointer, schema, base: None)
    monkeypatch.setattr(S, "_compiler", S.Compiler())


def test_a_client_without_its_length_check_fails_the_gate(built, without_length_check):
    """Review B1: with B0 the gate still passed; without it, evaluate `values` and rights `unit_open` fail."""
    report = G.run_gate({"service:evaluate", "service:rights"})
    failures = "\n".join(report["failures"])
    assert re.search(r"^accepted service:evaluate \w+ results/\*/result/values", failures, re.M), failures
    assert re.search(r"^accepted service:rights \w+ results/\*/result/[\w/*]*unit_open", failures, re.M), failures


FAST_ONE_SHOT = ("ve_metered::evaluate", "ve_metered::countermodel.search", "ve_conformance:route:graph.compose",
                 "ve_conformance:check-certificate:graph.compose", "ve_conformance:route:bundle.check")


@pytest.fixture
def without_row_count_check(monkeypatch):
    """`read_rows` with its one-row-per-case check removed (the reviewer's in-memory mutant)."""
    source = inspect.getsource(G.lean_backend.read_rows)
    check = " or len(rows) != len(cases)"
    assert source.count(check) == 1
    namespace = dict(vars(G.lean_backend))
    exec(compile(source.replace(check, ""), G.lean_backend.__file__, "exec"), namespace)
    monkeypatch.setattr(G.lean_backend, "read_rows", namespace["read_rows"])


def test_a_reader_without_its_row_count_check_fails_the_gate(built, without_row_count_check):
    """Review B2: the one-shot routes never saw an empty or extra row, so this mutant passed."""
    lean_build("ve_conformance")
    report = G.run_gate(set(FAST_ONE_SHOT))
    for route in FAST_ONE_SHOT:
        assert any(f["route"] == route and f["path"] == "." and f["mutation"] in ("empty", "duplicate")
                   for f in report["findings"]), (route, report["failures"])
