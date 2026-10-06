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


@pytest.mark.parametrize("fixture, source, status, code", [
    ("s1", "In this document, funny means amusing.\nEvery joke that is funny (meaning strange) is not funny."
     "\nAlice tells the riddle.\nThe riddle is funny (meaning strange).\nTherefore the riddle is not funny.",
     "none", "NoDerivation"),
    ("s4", "In this document, funny means purple. The riddle is funny.", "rejected", "UnknownGloss"),
    ("s7", "Alice tells the riddle.", "one", None),
    ("s16", "The riddle is odd.", "open", "Unresolved"),
    ("s21", "Alice tells the riddle.", "budget", "Budget"),
])
def test_spec_reading_fixtures(joke, fixture, source, status, code):
    reading = admit(joke, source, budget=1 if fixture == "s21" else route.WORK_BUDGET)
    assert (reading["status"], reading.get("code")) == (status, code), fixture
    if fixture == "s7":
        assert reading["units"][0]["formula"] == ["binary", "sense__tells_1", ["const", "alice"],
                                                     ["const", "riddle"]]
        assert [(o["sentence"], o["symbol"]) for o in reading["sense_map"]] == [(0, "sense__tells_1")]
    if fixture == "s16":
        assert reading["units"][0]["unresolved"] == ["odd"]
        assert [c["choice"] for c in reading["units"][0]["candidates"]] == [[['odd', 1]]]


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
    assert dictionary_id == route.read(joke_env(), "Alice tells the riddle.", [PACK])["dictionary_id"]
    assert int(budget) == route.WORK_BUDGET


def joke_env():
    """Small no-overlay environment for a dictionary identity probe."""
    return Environment({"language": "ve.core@0", "profile": "relational-fol@0",
                        "spec_revision": "ve-v0-draft-2026-09-20",
                        "vocabulary": {"sorts": {"person": {"description": "A sort."},
                                                 "joke": {"description": "A sort."}},
                                       "predicates": {},
                                       "constants": {"alice": {"sort": "person", "description": "A constant."},
                                                     "riddle": {"sort": "joke", "description": "A constant."}}}})


@pytest.mark.parametrize("mutant", [b"null", b"7", b"true", b"[]", b"{}", b'{"format":true}'])
def test_malformed_pack_is_rejected_by_lean(joke, mutant):
    with pytest.raises(VEError):
        route.read(joke[0], "Alice tells the riddle.", [mutant], overlay=joke[1])


@pytest.mark.parametrize("field, message", [("dictionary_id", "dictionary identity"),
                                           ("request_id", "request identity")])
def test_response_identity_and_type_mutations_fail_closed(joke, monkeypatch, field, message):
    real = route.subprocess.run
    def changed(*args, **kwargs):
        answer = real(*args, **kwargs)
        rows = json.loads(answer.stdout)
        rows[0]["result"][field] = "wrong"
        answer.stdout = json.dumps(rows).encode()
        return answer
    monkeypatch.setattr(route.subprocess, "run", changed)
    with pytest.raises(CheckerUnavailable, match=message):
        admit(joke, "Alice tells the riddle.")


def test_two_cli_admission_paths_agree(joke, tmp_path):
    env = tmp_path / "environment.json"
    env.write_text(json.dumps(joke[0].to_dict()))
    pack = tmp_path / "pack.json"
    pack.write_bytes(PACK)
    source = tmp_path / "source.txt"
    source.write_text("Alice tells riddle.")
    commands = [
        ["senses", "check", "--env", str(env), "--pack", str(pack), str(source)],
        ["check", "--surface", "english", "--env", str(env), "--senses", str(pack), str(source)],
    ]
    answers = []
    for args in commands:
        run = subprocess.run([sys.executable, "-m", "ve", *args], cwd=ROOT, capture_output=True,
                             text=True, timeout=HANG_TIMEOUT)
        assert run.returncode == 0, run.stdout + run.stderr
        answers.append(json.loads(run.stdout))
    assert answers[0] == answers[1]


def test_zero_budget_never_admits(joke):
    reading = admit(joke, "Alice tells the riddle.", budget=0)
    assert reading == {"status": "budget", "code": "Budget"}


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
    monkeypatch.setattr(route.subprocess, "run", must_not_run)
    with pytest.raises(CheckerUnavailable, match="deadline"):
        admit(joke, "Alice tells the riddle.")


def test_genuine_open_response_field_mutations_are_rejected(joke):
    genuine = route.read(joke[0], "The riddle is odd.", [PACK], overlay=joke[1])
    def problem(mutant):
        return route._response_problem(mutant, genuine["dictionary_id"], genuine["request_id"])
    assert problem(genuine) is None
    paths = [
        ("request_id",), ("dictionary_id",), ("reading", "status"), ("reading", "code"),
        ("reading", "units"), ("reading", "sense_map"), ("reading", "mixed"),
        ("reading", "unused"), ("reading", "environment"),
        ("reading", "units", 0, "candidates", 0, "choice"),
        ("reading", "units", 0, "candidates", 0, "lines"),
        ("reading", "units", 0, "candidates", 0, "formula"),
        ("reading", "units", 0, "candidates", 0, "mark"),
        ("reading", "sense_map", 0, "token_start"),
        ("reading", "sense_map", 0, "symbol"),
        ("reading", "sense_map", 0, "is_default"),
    ]
    for path in paths:
        mutant = deepcopy(genuine)
        parent = mutant
        for part in path[:-1]:
            parent = parent[part]
        parent[path[-1]] = None
        assert problem(mutant), path
        mutant = deepcopy(genuine)
        parent = mutant
        for part in path[:-1]:
            parent = parent[part]
        del parent[path[-1]]
        assert problem(mutant), path
    duplicated = deepcopy(genuine)
    candidates = duplicated["reading"]["units"][0]["candidates"]
    candidates.append(deepcopy(candidates[0]))
    assert problem(duplicated) == "candidate choices are duplicated"
    typed = deepcopy(genuine)
    typed["reading"]["sense_map"][0]["token_start"] = True
    assert problem(typed) == "a sense-map occurrence is malformed"
