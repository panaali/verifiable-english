"""Spec fixture admission through the Python transport and the compiled Lean reader."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
import re
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pytest

from subprocesses import HANG_TIMEOUT
from ve.environment import Environment
from ve.errors import CheckerUnavailable, VEError
from ve.senses import bundled_pack
from ve.backends import senses as route

ROOT = Path(__file__).resolve().parents[1]
PACK = bundled_pack("fixtures@1")


@pytest.fixture(scope="module")
def joke():
    env = Environment({
        "language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {name: {"description": "A sort."} for name in ("joke", "person")},
            "predicates": {},
            "constants": {"alice": {"sort": "person", "description": "A constant."},
                          "riddle": {"sort": "joke", "description": "A constant."}},
        },
    })
    overlay = {"format": "ve.english-vocabulary@1", "environment_id": env.environment_id,
               "sorts": {}, "predicates": {},
               "constants": {"riddle": {"verbalisation": "the riddle"}}}
    return env, overlay


def admit(joke, source, *, budget=route.WORK_BUDGET):
    env, overlay = joke
    return route.read(env, source, [PACK], overlay=overlay, budget=budget)["reading"]


def pack_with(extra=(), replace=None) -> bytes:
    """The fixture pack with senses added, and `replace(sense)` applied to each of its own."""
    data = json.loads(PACK)
    data["senses"] = [replace(dict(s)) if replace else s for s in data["senses"]] + list(extra)
    return json.dumps(data).encode()


def sense(word, index, gloss, kinds, wording):
    return {"word": word, "index": index, "gloss": gloss, "description": "a sense of " + word,
            "kinds": list(kinds), "wording": wording}


def world(sorts=("joke", "person"), constants=(("alice", "person"), ("riddle", "joke")), predicates=None):
    env = Environment({
        "language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {"sorts": {name: {"description": "A sort."} for name in sorts},
                       "predicates": predicates or {},
                       "constants": {name: {"sort": sort, "description": "A constant."} for name, sort in constants}},
    })
    overlay = {"format": "ve.english-vocabulary@1", "environment_id": env.environment_id,
               "sorts": {}, "predicates": {},
               "constants": {"riddle": {"verbalisation": "the riddle"}} if "riddle" in dict(constants) else {}}
    return env, overlay


def read_in(place, source, pack=PACK, *, budget=route.WORK_BUDGET):
    env, overlay = place
    return route.read(env, source, [pack], overlay=overlay, budget=budget)


NEAR = [sense("near", 1, "beside bob", ["person"], "{0} is near bob"),
        sense("near", 2, "beside", ["person", "person"], "{0} is near {1}")]
MANY_WORDS = ["zq" + chr(97 + i // 26) + chr(97 + i % 26) for i in range(30)]
WORLDS = {
    "joke": lambda: world(),
    "near": lambda: world(constants=(("alice", "person"), ("riddle", "joke"), ("bob", "person"))),
    "service": lambda: world(sorts=("joke", "person", "service"),
                             constants=(("alice", "person"), ("riddle", "joke"), ("legacy", "service"))),
    "own-funny": lambda: world(predicates={"funny": {"arguments": ["joke"], "description": "A predicate.",
                                                     "verbalisation": "{0} is funny"}}),
    # 255 predicates of its own and the two senses of `funny` pass the 256 of `maxPredicates` (j17)
    "crowded": lambda: world(predicates={
        name: {"arguments": ["joke"], "description": "A predicate.", "verbalisation": "{0} is " + name}
        for name in ("q" + chr(97 + i // 26) + chr(97 + i % 26) for i in range(255))})}
J = ("In this document, funny means amusing.\nEvery joke that is funny (meaning strange) is not funny."
     "\nAlice tells the riddle.\nThe riddle is funny (meaning strange).\nTherefore the riddle is not funny.")
JBODY = J.split("\n")[1:]
LINE = "In this document, funny means amusing."


@pytest.mark.parametrize("fixture, source, status, code", [
    ("s1", J, "none", "NoDerivation"),
    ("s4", "In this document, funny means purple. The riddle is funny.", "rejected", "UnknownGloss"),
    ("s7", "Alice tells the riddle.", "one", None),
    ("s16", "The riddle is odd.", "open", "Unresolved"),
    ("s21", "Alice tells the riddle.", "budget", "Budget"),
])
def test_spec_reading_fixtures(joke, fixture, source, status, code):
    reading = admit(joke, source, budget=1 if fixture == "s21" else route.WORK_BUDGET)
    assert (reading["status"], reading.get("code")) == (status, code), fixture
    if fixture == "s1":
        # `stopped 1 noDerivation`: the sentence index counts the preamble line (spec 4.1, reviews B1/B2)
        assert reading == {"status": "none", "code": "NoDerivation", "sentence": 1,
                           "text": "Sentence 2 has no reading with the current vocabulary."}
    if fixture == "s4":
        assert reading["details"] == {"line": 0, "word": "funny", "gloss": "purple"}
    if fixture == "s21":
        assert reading["sentence"] == 0
    if fixture == "s7":
        [unit] = reading["units"]
        assert unit["formula"] == ["binary", "sense__tells_1", ["const", "alice"], ["const", "riddle"]]
        assert (unit["referents"], unit["binder_seen"]) == (["alice", "riddle"], False)
        assert [(o["sentence"], o["symbol"]) for o in reading["sense_map"]] == [(0, "sense__tells_1")]
    if fixture == "s16":
        [unit] = reading["units"]
        assert unit["unresolved"] == ["odd"]
        assert [c["choice"] for c in unit["candidates"]] == [[['odd', 1]]]
        # the state after an open unit is its candidates' common successor (B0)
        assert (unit["referents"], unit["binder_seen"]) == (["riddle"], False)


# Every refusal of spec 4.1 with its arguments: the sense faults with `details` (or `failure`), S2's outcomes
# with S2's fields. Each row is a computed fixture of spec section 8 or of lean/VE/Senses/Examples.lean.
REFUSALS = [
    ("d3", "joke", pack_with(replace=lambda s: {**s, "gloss": "odd"} if s["word"] == "odd" and s["index"] == 1 else s),
     "Alice tells the riddle.", None,
     {"status": "rejected", "code": "InvalidDictionary", "failure": ["W2", "odd", "the gloss of odd is the word itself"]}),
    ("unknown-word", "joke", PACK, "In this document, zany means amusing. Alice tells the riddle.", None,
     {"status": "rejected", "code": "UnknownWord", "details": {"line": 0, "word": "zany"}}),
    ("s4", "joke", PACK, "In this document, funny means purple. The riddle is funny.", None,
     {"status": "rejected", "code": "UnknownGloss", "details": {"line": 0, "word": "funny", "gloss": "purple"}}),
    ("dotted-i", "joke", PACK, "İn this document, funny means amusing.\nThe riddle is funny (meaning strange).", None,
     {"status": "rejected", "code": "MalformedPreamble", "details": {"line": 0}}),
    ("preamble-budget", "joke", PACK, LINE + "\nAlice tells the riddle.", 1,
     {"status": "budget", "code": "PreambleBudget", "details": {"line": 0}}),
    ("repeated", "joke", PACK, LINE + "\nIn this document, funny means strange.\nAlice tells the riddle.", None,
     {"status": "rejected", "code": "RepeatedDefault", "details": {"line": 1, "word": "funny"}}),
    ("s5", "joke", PACK, "\n".join([JBODY[0], JBODY[1], LINE, JBODY[2], JBODY[3]]), None,
     {"status": "rejected", "code": "PreambleLate", "details": {"sentence": 2}}),
    ("s6", "own-funny", PACK, J, None,
     {"status": "rejected", "code": "Collision",
      "details": {"kind": "predicate", "name": "funny", "sense": "sense__funny_1"}}),
    ("predicates-limit", "crowded", PACK, "The riddle is funny (meaning strange).", None,
     {"status": "rejected", "code": "VocabularyLimit", "details": {"what": "predicates"}}),
    ("a1-30-words", "joke",
     pack_with([sense(w, i, g, ["joke"], "{0} is " + w) for w in MANY_WORDS
                for i, g in ((1, "plain kind"), (2, "usual kind"))]),
     "The riddle is " + ", ".join(MANY_WORDS) + ".", None,
     {"status": "rejected", "code": "TooManyCandidates", "details": {"sentence": 0, "words": MANY_WORDS}}),
    ("s17", "near", pack_with(NEAR), "Alice is near bob.", None,
     {"status": "rejected", "code": "CandidatesDiverge",
      "details": {"sentence": 0, "words": ["near"], "why": {"referent": "bob"}}}),
    ("s23", "near", pack_with(NEAR),
     "In this document, near means beside.\nAlice is near bob.\n"
     "Starting from alice, bob is reachable by one or more \"sense__near_2\" steps.", None,
     {"status": "rejected", "code": "QuotedSense", "details": {"sentence": 2, "word": "near"}}),
    ("s1", "joke", PACK, J, None,
     {"status": "none", "code": "NoDerivation", "sentence": 1,
      "text": "Sentence 2 has no reading with the current vocabulary."}),
    ("s21", "joke", PACK, "Alice tells the riddle.", 1,
     {"status": "budget", "code": "Budget", "sentence": 0,
      "text": "Sentence 1 needs more work than the limit allows. No verdict was reached."}),
    ("s3", "service", PACK, LINE + "\nLegacy is funny.", None,
     {"status": "rejected", "code": "IllTyped",
      "text": "The text was read, and its formulas do not pass the type check."}),
    ("empty", "joke", PACK, LINE, None,
     {"status": "rejected", "code": "EmptyDocument", "text": "Write at least one statement ending with a period."}),
]


@pytest.mark.parametrize("fixture, place, pack, source, budget, expected", REFUSALS, ids=[r[0] for r in REFUSALS])
def test_every_refusal_carries_its_arguments(fixture, place, pack, source, budget, expected):
    """Reviews (Astra B1, Fable B2): a refusal names its sentence and its fault's arguments."""
    result = read_in(WORLDS[place](), source, pack, budget=route.WORK_BUDGET if budget is None else budget)
    assert result["reading"] == expected, fixture


def test_every_sense_fault_code_has_a_refusal_fixture():
    """The table of fault arguments and the fixtures above cover the same codes."""
    codes = {row[-1]["code"] for row in REFUSALS}
    assert set(route.FAULT_DETAILS) | {"InvalidDictionary"} <= codes


MINI = json.dumps({"format": "ve.sense-pack@1", "name": "mini@1",
                   "sorts": [{"name": "thing", "noun": "thing", "plural": "things", "description": "A thing.",
                              "letter": "T"}],
                   "senses": [sense("zany", 1, "silly", ["thing"], "{0} is zany")]}).encode()
ADJECTIVE = {"arguments": ["service"], "description": "A predicate."}


def S2_WORLD():
    """english-lean-s2 fixture FD: a sort whose noun is `deployed service` makes `Every deployed service is
    reviewed.` ambiguous."""
    env, overlay = world(sorts=("service",), constants=(("legacy", "service"), ("beta", "service")),
                         predicates={"deployed": {**ADJECTIVE, "verbalisation": "{0} is deployed"},
                                     "reviewed": {**ADJECTIVE, "verbalisation": "{0} is reviewed"}})
    data = env.to_dict()
    data["vocabulary"]["sorts"]["dservice"] = {"description": "A sort.", "verbalisation": {
        "singular": "deployed service", "plural": "deployed services"}}
    env = Environment(data)
    return env, {**overlay, "environment_id": env.environment_id}


@pytest.mark.parametrize("source", [
    "Every deployed service is reviewed.", "Legacy is beta.", "It is deployed.", "Legacy is deployed",
    "Legacy is deployed. Beta is reviewed. Legacy is gamma.", "Legacy, legacy and beta are deployed.",
])
def test_s2_outcomes_match_the_english_route(source):
    """With no dictionary word in the text, S2's outcome reaches the senses answer with exactly the fields,
    texts, sentence and witness trees of S2's own authoring answer (ve_english_route): Run.lean's copy of
    S2's two inline texts cannot drift."""
    from ve.backends.english_lean import EXECUTABLE as ENGLISH, request
    from ve.backends.lean import run_english_cases
    from ve.english import EnglishVocabulary
    env, overlay = S2_WORLD()
    reading = read_in((env, overlay), source, MINI)["reading"]
    case = request(env, source, EnglishVocabulary(env, vocabulary=overlay), {"vocabulary": overlay})
    [row] = run_english_cases(ENGLISH, "english.read", [case], timeout=HANG_TIMEOUT)
    english = {k: v for k, v in row["result"].items() if k != "identities"}
    assert english["status"] != "one", english
    assert reading == english


def test_gloss_words_are_not_occurrences():
    """Fable B3: a word inside a gloss is not an occurrence of that word (spec 2.6, R7): with `funny` 2
    glossed `odd thing`, `odd` adds no choice; nor does `tell` (a headword token of `tells`) in `tell apart`."""
    place = WORLDS["service"]()
    for gloss, extra in (("odd thing", []), ("tell apart", [sense("tells", 2, "reveals", ["person", "joke"],
                                                                   "{0} tells {1}")])):
        pack = pack_with(extra, lambda s, g=gloss: {**s, "gloss": g} if (s["word"], s["index"]) == ("funny", 2) else s)
        reading = read_in(place, f"Both legacy is reviewed and the riddle is funny (meaning {gloss}).", pack)["reading"]
        assert reading["status"] == "open", gloss
        [unit] = reading["units"]
        assert unit["unresolved"] == ["reviewed"], gloss
        assert [c["choice"] for c in unit["candidates"]] == [[["reviewed", 1]], [["reviewed", 2]]], gloss


@pytest.mark.parametrize("mark", [" (meaning odd thing reviewed)", ", in the sense of odd thing reviewed"])
def test_prefix_gloss_does_not_project_its_remaining_words(mark):
    """A shorter valid comma gloss cannot expose the tail of a longer gloss as a body word.
    At 253 document predicates, incorrectly projecting `reviewed` would exceed the 256 cap.
    """
    names = ("q" + chr(97 + i // 26) + chr(97 + i % 26) for i in range(253))
    place = world(predicates={name: {"arguments": ["joke"], "description": "A predicate.",
                                     "verbalisation": "{0} is " + name} for name in names})
    pack = pack_with(replace=lambda s: {**s, "gloss": "odd thing" if s["index"] == 1 else
                      "odd thing reviewed"} if s["word"] == "funny" else s)
    reading = read_in(place, "The riddle is funny" + mark + ".", pack)["reading"]
    assert reading["status"] == "one", reading
    assert reading["sense_map"][0]["symbol"] == "sense__funny_2"


def test_name_collision_with_empty_sense_is_a_valid_refusal():
    """Lean preCheck reports a name clash with an empty `sense`; Python relays it."""
    place = world(predicates={"sense__funny_1": {"arguments": ["joke"],
                                                    "description": "A predicate.",
                                                    "verbalisation": "{0} is amusing"}})
    result = read_in(place, "The riddle is funny.")
    assert result["reading"] == {"status": "rejected", "code": "Collision",
                                 "details": {"kind": "name", "name": "sense__funny_1", "sense": ""}}
    for field in ("kind", "name", "sense"):
        bad = deepcopy(result)
        bad["reading"]["details"][field] = None
        assert route._response_problem(bad, result["dictionary_id"], result["request_id"])


@pytest.fixture(scope="module")
def lean_guards():
    """VE.Senses.Examples compiled once: its `#guard`s are the Lean side of the fixture comparison."""
    result = subprocess.run(["lake", "build", "VE.Senses.Examples"], cwd=ROOT / "lean",
                            capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("fixture, source, status, formula, unresolved, candidates", [
    ("s8", "In this document, funny means amusing. The riddle is funny (meaning amusing).",
     "one", ["unary", "sense__funny_1", ["const", "riddle"]], [], []),
    ("s9", "In this document, funny means amusing. In this document, odd means strange. "
     "Every funny joke is odd.", "one",
     ["forall", "joke", ["implies", ["unary", "sense__funny_1", ["var", 0]],
                          ["unary", "sense__odd_1", ["var", 0]]]], [], []),
    ("s22", "Both the riddle is odd and the riddle is funny (meaning strange).",
     "open", None, ["odd"],
     [{"choice": [["odd", 1]], "lines": "In this document, odd means strange.", "mark": False,
       "formula": ["and", ["unary", "sense__odd_1", ["const", "riddle"]],
                   ["unary", "sense__funny_2", ["const", "riddle"]]]}]),
    ("n1", "In this document, funny means amusing. The riddle is not funny.",
     "one", ["not", ["unary", "sense__funny_1", ["const", "riddle"]]], [], []),
    ("n2", "The riddle is not funny (meaning strange).",
     "one", ["not", ["unary", "sense__funny_2", ["const", "riddle"]]], [], []),
    ("n3", "Alice does not tell the riddle.",
     "one", ["not", ["binary", "sense__tells_1", ["const", "alice"],
                          ["const", "riddle"]]], [], []),
])
def test_spec_fixtures_through_the_route_against_lean(lean_guards, joke, fixture, source, status, formula,
                                                      unresolved, candidates):
    """Spec against Lean, not three-way: Rust has no senses code and Python only relays the Lean reader.
    The route's answer is compared with the spec row that VE.Senses.Examples also guards."""
    reading = admit(joke, source)
    assert reading["status"] == status, fixture
    [unit] = reading["units"]
    assert unit.get("formula") == formula, fixture
    assert unit["unresolved"] == unresolved, fixture
    assert unit["candidates"] == candidates, fixture


def test_spec_pack_python_file_and_lean_fixture_agree(tmp_path):
    """The spec's JSON, the shipped file, and Lean's fixture pack describe one dictionary."""
    text = (ROOT / "docs/spec/senses.md").read_text()
    block = re.search(r'```json\n(\{"format": "ve.sense-pack@1".*?\})\n```', text, re.S)
    assert block
    specified = json.loads(block[1])
    specified["sorts"] += [
        {"name": "principal", "noun": "principal", "plural": "principals", "description": "A principal.",
         "letter": "R"},
        {"name": "resource", "noun": "resource", "plural": "resources", "description": "A resource.",
         "letter": "Q"},
    ]
    lake = shutil.which("lake")
    assert lake, "lake is required for three-way fixture conformance"
    probe = tmp_path / "SensesPackProbe.lean"
    probe.write_text('import VE.Senses.Fixtures\n'
                     '#eval IO.println VE.Senses.Fixtures.packF.toJson.compress\n'
                     '#eval IO.println (VE.Senses.dictionaryId VE.Senses.Fixtures.F)\n'
                     '#eval IO.println VE.EnglishGrammar.workBudget\n')
    run = subprocess.run([lake, "env", "lean", str(probe)], cwd=ROOT / "lean",
                         capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout + run.stderr
    pack_json, dictionary_id, budget = run.stdout.splitlines()
    shipped = json.loads(PACK)
    assert specified == shipped == json.loads(pack_json)
    assert dictionary_id == read_in(world(), "Alice tells the riddle.")["dictionary_id"]
    assert int(budget) == route.WORK_BUDGET


@pytest.mark.parametrize("mutant", [b"null", b"7", b"true", b"[]", b"{}", b'{"format":true}'])
def test_malformed_pack_is_rejected_by_lean(joke, mutant):
    with pytest.raises(VEError):
        route.read(joke[0], "Alice tells the riddle.", [mutant], overlay=joke[1])


@pytest.mark.parametrize("field, message", [("dictionary_id", "dictionary identity"),
                                           ("request_id", "request identity")])
def test_response_identity_and_type_mutations_fail_closed(joke, monkeypatch, field, message):
    real = subprocess.run
    def changed(*args, **kwargs):
        answer = real(*args, **kwargs)
        rows = json.loads(answer.stdout)
        rows[0]["result"][field] = "wrong"
        answer.stdout = json.dumps(rows).encode()
        return answer
    monkeypatch.setattr(subprocess, "run", changed)
    with pytest.raises(CheckerUnavailable, match=message):
        admit(joke, "Alice tells the riddle.")


def test_the_route_goes_through_the_manifest_binding(joke, monkeypatch):
    """Fable B1: the transport is `ve.backends.lean.run` under the `senses.read` binding and call site."""
    from ve import assurance
    calls = []
    real = assurance.require_lean_binding
    def spy(op_id, executable, mode, kinds=()):
        calls.append((op_id, executable, mode, set(kinds)))
        return real(op_id, executable, mode, kinds)
    monkeypatch.setattr("ve.backends.lean.require_lean_binding", spy)
    admit(joke, "Alice tells the riddle.")
    assert calls == [("senses.read", "ve_senses_route", "", set())]
    assert assurance.operation("senses.read")["lean_call_sites"] == ["ve.backends.senses:read"]


def test_only_senses_check_reads_with_senses(joke, tmp_path):
    """Fable B1: `ve check` keeps its record contract, so it has no `--senses`; `ve senses check` prints Lean's
    reading with the honesty fields of its manifest operation."""
    env = tmp_path / "environment.json"
    env.write_text(json.dumps(joke[0].to_dict()))
    pack = tmp_path / "pack.json"
    pack.write_bytes(PACK)
    source = tmp_path / "source.txt"
    source.write_text("Alice tells the riddle.")
    refused = subprocess.run([sys.executable, "-m", "ve", "check", "--surface", "english", "--env", str(env),
                              "--senses", str(pack), str(source)], cwd=ROOT, capture_output=True, text=True,
                             timeout=HANG_TIMEOUT)
    assert refused.returncode == 2 and "--senses" in refused.stderr
    run = subprocess.run([sys.executable, "-m", "ve", "senses", "check", "--env", str(env), "--pack", str(pack),
                          str(source)], cwd=ROOT, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout + run.stderr
    answer = json.loads(run.stdout)
    assert {k: answer[k] for k in ("operation", "assurance", "intent", "proof", "conclusions")} == {
        "operation": "senses.read", "assurance": "experimental", "intent": "unconfirmed", "proof": "not_checked",
        "conclusions": "not_checked"}
    assert answer["reading"]["status"] == "one"
    assert answer["reading"]["units"][0]["formula"] == [
        "binary", "sense__tells_1", ["const", "alice"], ["const", "riddle"]]


def test_zero_budget_never_admits(joke):
    reading = admit(joke, "Alice tells the riddle.", budget=0)
    assert (reading["status"], reading["code"], reading["sentence"]) == ("budget", "Budget", 0)
    assert "units" not in reading


def test_deadline_covers_pack_preparation(joke, monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(route, "time", SimpleNamespace(monotonic=lambda: clock[0]))
    original = route._text
    def delayed(raw):
        clock[0] = 1_000_000_000
        return original(raw)
    monkeypatch.setattr(route, "_text", delayed)
    def must_not_run(*_args, **_kwargs):
        pytest.fail("the runner started after the deadline")
    monkeypatch.setattr(subprocess, "run", must_not_run)
    with pytest.raises(CheckerUnavailable, match="deadline"):
        admit(joke, "Alice tells the riddle.")


def _paths(value, prefix=()):
    """Every path to a field or element of a response, outside the projected environment (which
    `Environment` validates as a whole)."""
    if prefix[-1:] == ("environment",):
        return
    items = value.items() if type(value) is dict else enumerate(value) if type(value) is list else ()
    for key, item in items:
        yield prefix + (key,)
        yield from _paths(item, prefix + (key,))


def _retyped(value):
    """Values of other JSON types than `value`: never a Boolean for a number or a number for a Boolean."""
    return [other for other in (None, True, 7, -1, "x", [], {}) if type(other) is not type(value)
            and not (type(value) is int and type(other) is bool)]


W = route.WORK_BUDGET
GENUINE = [("open", "joke", PACK, "The riddle is odd.", W),
           ("one", "joke", PACK, "In this document, funny means amusing. In this document, odd means strange. "
                                 "Every funny joke is odd.", W),
           ("none", "joke", PACK, J, W),
           ("budget", "joke", PACK, "Alice tells the riddle.", 1),
           ("many", "s2", MINI, "Every deployed service is reviewed.", W),
           ("diverge", "near", pack_with(NEAR), "Alice is near bob.", W),
           ("dictionary", "joke", REFUSALS[0][2], "Alice tells the riddle.", W)]


@pytest.mark.parametrize("name, place, pack, source, budget", GENUINE, ids=[g[0] for g in GENUINE])
def test_genuine_response_field_mutations_are_rejected(name, place, pack, source, budget):
    """Checklist 4: every field of a genuine answer, dropped, nulled or given another type, is refused;
    and so is a duplicated candidate or a referent the projection does not declare."""
    genuine = read_in(S2_WORLD() if place == "s2" else WORLDS[place](), source, pack, budget=budget)
    def problem(mutant):
        return route._response_problem(mutant, genuine["dictionary_id"], genuine["request_id"])
    assert problem(genuine) is None
    paths = list(_paths(genuine))
    assert len(paths) > 4, name
    for path in paths:
        original = genuine
        for part in path:
            original = original[part]
        for mutate in ["delete", *_retyped(original)]:
            mutant = deepcopy(genuine)
            parent = mutant
            for part in path[:-1]:
                parent = parent[part]
            if mutate == "delete":
                if type(parent) is not dict:
                    continue
                del parent[path[-1]]
            else:
                parent[path[-1]] = mutate
            assert problem(mutant), (name, path, mutate)
    if name == "open":
        duplicated = deepcopy(genuine)
        candidates = duplicated["reading"]["units"][0]["candidates"]
        candidates.append(deepcopy(candidates[0]))
        assert problem(duplicated) == "candidate choices are duplicated"
        stranger = deepcopy(genuine)
        stranger["reading"]["units"][0]["referents"] = ["nobody"]
        assert problem(stranger) == "the state after a unit is malformed"


def test_senses_check_is_admission_only(joke, tmp_path):
    """Astra (added) A: an unsupported marked conclusion is admitted, and the answer says the conclusion was
    not checked; `ve check` (which checks conclusions) cannot be given packs."""
    env = tmp_path / "environment.json"
    env.write_text(json.dumps(joke[0].to_dict()))
    pack = tmp_path / "pack.json"
    pack.write_bytes(PACK)
    source = tmp_path / "source.txt"
    source.write_text(LINE + " The riddle is funny. Therefore the riddle is not funny.")
    run = subprocess.run([sys.executable, "-m", "ve", "senses", "check", "--env", str(env), "--pack", str(pack),
                          str(source)], cwd=ROOT, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    answer = json.loads(run.stdout)
    assert answer["conclusions"] == "not_checked"
    assert [unit["mark"] for unit in answer["reading"]["units"]] == [False, True]
    help_text = subprocess.run([sys.executable, "-m", "ve", "senses", "check", "--help"], cwd=ROOT,
                               capture_output=True, text=True, timeout=HANG_TIMEOUT).stdout
    assert "Admission only" in " ".join(help_text.split())


@pytest.mark.parametrize("own, status", [
    ([sense("funny", 1, "amusing", ["joke"], "{0} is funny")], "one"),
    ([], "none"),
])
def test_own_senses_need_no_pack(joke, own, status):
    """Astra (added) B: a dictionary of own senses alone goes to Lean, which decides it; Python adds no rule.
    The own sense's kind is a kind of the document (W4)."""
    env, overlay = joke
    result = route.read(env, "The riddle is funny.", [], own=own, overlay=overlay)
    assert result["reading"]["status"] == status


# The status of every code (Lean `SensesOutcome.statusCode`): the sense faults' are `FAULT_DETAILS`',
# S2's are english_lean's.
def _status_of(code):
    from ve.backends import english_lean
    if code is None:
        return "one"
    if code == "Unresolved":
        return "open"
    if code == "PreambleBudget":
        return "budget"
    if code in route.FAULT_DETAILS or code == "InvalidDictionary" or code in english_lean.CLASSES:
        return "rejected"
    return {v: k for k, v in english_lean.STATUS_CODES.items()}.get(code)


@pytest.mark.parametrize("name, place, pack, source, budget", GENUINE, ids=[g[0] for g in GENUINE])
def test_impossible_status_code_pairs_are_rejected(name, place, pack, source, budget):
    """Astra (added) B: a genuine answer given any status and code that `statusCode` never pairs is refused."""
    from ve.backends import english_lean
    genuine = read_in(S2_WORLD() if place == "s2" else WORLDS[place](), source, pack, budget=budget)
    codes = [None, "Unresolved", "InvalidDictionary", "DefinitelyNotARealCode", *route.FAULT_DETAILS,
             *english_lean.CLASSES, *english_lean.STATUS_CODES.values()]
    for status in sorted(route.STATUSES):
        for code in codes:
            if _status_of(code) == status:
                continue
            mutant = deepcopy(genuine)
            mutant["reading"]["status"] = status
            mutant["reading"].pop("code", None)
            if code is not None:
                mutant["reading"]["code"] = code
            assert route._response_problem(mutant, genuine["dictionary_id"], genuine["request_id"]), \
                (name, status, code)
