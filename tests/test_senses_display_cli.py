"""The senses display through the CLI (senses plan B7, 6.8 g8-g10; sn-b7b): `ve render --senses` with Lean's texts
verbatim, `ve senses resolve` (Lean's line, then the re-check) and `ve senses propose-readings` (the reading sets of
Lean's candidates and flip models, validated by the readings validation), on fixtures that read as merged."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

from ve.__main__ import main
from ve.backends import senses as route
from ve.environment import Environment
from ve.errors import CheckerUnavailable
from ve.readings import validate_reading_sets
from ve.senses import display

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_senses_display import AMUSING, GLOSSED, S16, STRANGE, TWO  # noqa: E402
from test_senses_route import NEAR, PACK, pack_with, world  # noqa: E402

S17 = "Alice is near bob."
BESIDE = "In this document, near means beside."


def _files(tmp_path, place, source, pack):
    env, overlay = place
    (tmp_path / "env.json").write_text(json.dumps(env.to_dict()))
    (tmp_path / "overlay.json").write_text(json.dumps(overlay))
    (tmp_path / "pack.json").write_bytes(pack)
    (tmp_path / "text.txt").write_text(source)


def run(tmp_path, capsys, place, command, source, *extra, pack=PACK):
    """`ve render --senses` or `ve senses <command>` on `source`: the exit code and the printed object."""
    _files(tmp_path, place, source, pack)
    common = ["--env", str(tmp_path / "env.json"), "--english-vocabulary", str(tmp_path / "overlay.json")]
    if command == "render":
        argv = ["render", *common, "--senses", str(tmp_path / "pack.json"), *extra, str(tmp_path / "text.txt")]
    else:
        argv = ["senses", command, *common, "--pack", str(tmp_path / "pack.json"), *extra, str(tmp_path / "text.txt")]
    code = main(argv)
    return code, json.loads(capsys.readouterr().out)


@pytest.fixture(scope="module")
def place():
    return world()


@pytest.fixture(scope="module")
def near():
    return world(constants=(("alice", "person"), ("riddle", "joke"), ("bob", "person")))


def test_g8_the_mixed_warning_is_leans_printed_once(tmp_path, capsys, place):
    """g8 on an as-merged Mixed fixture (s1 reads `none` as merged): Lean's warning text once, the body not
    rendered (its switched occurrence has no wording in Python's renderer, DRI 20261110 item 2), exit code 0."""
    env, overlay = place
    lean = route.read(env, GLOSSED, [PACK], overlay=overlay)["reading"]["warnings"]
    assert [w["code"] for w in lean] == ["Mixed"]
    code, out = run(tmp_path, capsys, place, "render", GLOSSED)
    assert code == 0 and out["reading"]["warnings"] == lean
    assert out["text"] is None and out["body_status"] == "switched-occurrence-not-rendered"
    assert json.dumps(out, ensure_ascii=False).count(json.dumps(lean[0]["text"], ensure_ascii=False)) == 1


def test_g9_one_candidate_through_the_cli(tmp_path, capsys, place):
    """g9 (s16): Lean's one-candidate text and its checked rendering; propose-readings writes no set and gives the
    resolving line; resolve inserts Lean's line and the re-check resolves the unit."""
    line = "In this document, odd means strange."
    code, out = run(tmp_path, capsys, place, "render", S16)
    [unit] = out["reading"]["units"]
    assert code == 3 and unit["text"].endswith('Add the line "' + line + '" to say so.')
    assert out["renderings"] == [{"sentence": 0, "candidate": 0, "lines": line, "lacking": [line], "text": S16}]
    code, out = run(tmp_path, capsys, place, "propose-readings", S16, "--output", str(tmp_path / "sets.json"))
    assert code == 0 and out["reading_sets"] == [] and not (tmp_path / "sets.json").exists()
    assert out["resolving"] == [{"sentence": 0, "lacking": [line], "text": unit["text"]}]
    code, out = run(tmp_path, capsys, place, "resolve", S16, "--word", "odd", "--gloss", "strange")
    assert code == 0 and out["line"] == {"word": "odd", "gloss": "strange", "text": line} and out["written"]
    assert (tmp_path / "text.txt").read_text() == line + "\n" + S16
    assert out["reading"]["status"] == "one" and out["reading"]["preamble"] == [line]


def test_g10_diverging_candidates_through_the_cli(tmp_path, capsys, near):
    """g10 (s17): Lean's CandidatesDiverge text verbatim, no rendering and no reading set; resolve with `beside`
    gives s18 (one reading)."""
    env, overlay = near
    pack = pack_with(NEAR)
    lean = route.read(env, S17, [pack], overlay=overlay)["reading"]
    assert lean["code"] == "CandidatesDiverge"
    code, out = run(tmp_path, capsys, near, "render", S17, pack=pack)
    assert code == 3 and out["reading"]["text"] == lean["text"] and out["renderings"] == []
    code, out = run(tmp_path, capsys, near, "propose-readings", S17, pack=pack)
    assert code == 3 and out["reading_sets"] == [] and out["reading"]["text"] == lean["text"]
    code, out = run(tmp_path, capsys, near, "resolve", S17, "--word", "near", "--gloss", "beside", pack=pack)
    assert code == 0 and out["written"] and (tmp_path / "text.txt").read_text() == BESIDE + "\n" + S17
    assert out["reading"]["status"] == "one" and out["reading"]["units"][0]["formula"][1] == "sense__near_2"


def test_resolve_writes_nothing_lean_does_not_give_or_admit(tmp_path, capsys, place):
    """Lean's code for a gloss no sense has, and a line Lean then refuses (a second line for `odd`): the file is
    unchanged, exit 3."""
    code, out = run(tmp_path, capsys, place, "resolve", S16, "--word", "odd", "--gloss", "purple")
    assert code == 3 and out["line"] == {"word": "odd", "gloss": "purple", "code": "UnknownGloss"}
    assert not out["written"] and (tmp_path / "text.txt").read_text() == S16
    source = "In this document, odd means strange.\n" + S16
    code, out = run(tmp_path, capsys, place, "resolve", source, "--word", "odd", "--gloss", "uneven")
    assert code == 3 and not out["written"] and out["reading"]["code"] == "RepeatedDefault"
    assert (tmp_path / "text.txt").read_text() == source


def test_propose_readings_writes_a_set_the_readings_validation_accepts(tmp_path, capsys, place):
    """The as-merged two-candidate fixture: one `open` set, a reading per candidate with Lean's text as `why` and
    the flip model by id; the written file passes the readings validation; each reading's text is its candidate's
    rendering, re-read by Lean under its projection."""
    code, out = run(tmp_path, capsys, place, "propose-readings", TWO, "--output", str(tmp_path / "sets.json"))
    [unit] = out["reading"]["units"]
    [flip] = out["reading"]["flips"]
    [reading_set] = json.loads((tmp_path / "sets.json").read_text())["reading_sets"]
    assert code == 0 and reading_set == out["reading_sets"][0]
    assert (reading_set["id"], reading_set["unit"], reading_set["status"]) == ("senses-0", "0", "open")
    assert [r["content"] for r in reading_set["readings"]] == [c["formula"] for c in unit["candidates"]]
    assert all(r["admission"]["who"] == "senses" and r["admission"]["why"] == unit["text"]
               for r in reading_set["readings"])
    [model_id] = reading_set["models"]
    assert reading_set["models"][model_id] == flip["model"]
    assert [r["admission"]["distinguishing_models"] for r in reading_set["readings"]] == [
        {"candidate-1": model_id}, {"candidate-0": model_id}]
    projected = Environment(out["reading"]["environment"])
    assert validate_reading_sets(projected, [reading_set], {"0"}) == {("senses-0", 1)}
    assert [(t["reading"], t["lines"], t["text"]) for t in out["texts"]] == [
        ("candidate-0", AMUSING, TWO), ("candidate-1", STRANGE, TWO)]


def _tampered(place, mutate):
    env, overlay = place
    answer = copy.deepcopy(route.read(env, TWO, [PACK], overlay=overlay)["reading"])
    mutate(answer)
    return display.propose_readings(env, [PACK], TWO, answer, overlay=overlay)


def test_a_flip_model_that_does_not_separate_is_refused(place):
    """A distinguishing model with the true sense emptied separates nothing: the readings validation refuses the
    set, CheckerUnavailable; a pair Lean does not distinguish gets no set, with Lean's status."""
    with pytest.raises(CheckerUnavailable, match="readings validation refused"):
        _tampered(place, lambda a: a["flips"][0]["model"]["relations"].update(sense__funny_1=[]))
    out = _tampered(place, lambda a: a["flips"][0].update(status="undistinguished"))
    assert out["reading_sets"] == [] and out["undistinguished"] == [
        {"sentence": 0, "flips": [[0, 1, "undistinguished"]]}]
    assert len(_tampered(place, lambda a: None)["reading_sets"]) == 1


def test_propose_readings_has_no_set_for_a_resolved_reading(tmp_path, capsys, place):
    code, out = run(tmp_path, capsys, place, "propose-readings", "Alice tells the riddle.")
    assert code == 0 and out["reading_sets"] == [] and out["resolving"] == [] and out["texts"] == []
