"""The senses display (senses plan 2.8, B7; sn-b7 as cut by reviews/dri-decisions-20261101-sn-b7b8.md item 1): each
candidate of an open unit is rendered under the projection `senses.project` returns for its resolving lines and
re-read by Lean under that same projection, on fixtures that read as merged (s16, one candidate; `The riddle is
funny.`, two)."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

from ve.__main__ import main
from ve.backends import senses as route
from ve.errors import CheckerUnavailable, ResourceLimit
from ve.senses import display

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_senses_route import PACK, world  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TWO = "The riddle is funny."
S16 = "The riddle is odd."
AMUSING, STRANGE = "In this document, funny means amusing.", "In this document, funny means strange."


@pytest.fixture(scope="module")
def place():
    return world()


def reading(place, source):
    env, overlay = place
    return route.read(env, source, [PACK], overlay=overlay)["reading"]


def shown(place, source):
    env, overlay = place
    return display.candidates(env, [PACK], reading(place, source), overlay=overlay)


@pytest.fixture
def calls(monkeypatch):
    """The `senses.project` lines and the `senses.read` sources the display sends."""
    seen = {"project": [], "read": []}
    project, read = route.project, route.read

    def spy_project(env, packs, lines, used, **kw):
        seen["project"].append(lines)
        return project(env, packs, lines, used, **kw)

    def spy_read(env, source, packs, **kw):
        seen["read"].append(source)
        return read(env, source, packs, **kw)

    monkeypatch.setattr(display.route, "project", spy_project)
    monkeypatch.setattr(display.route, "read", spy_read)
    return seen


def test_two_candidates_each_reread_under_its_own_projection(place, calls):
    """Each candidate is bare under its own choice (`funny` is that projection's default) and re-read after its
    own lines; under the base projection both would carry a gloss."""
    unit = reading(place, TWO)["units"][0]
    assert [c["lines"] for c in unit["candidates"]] == [AMUSING, STRANGE]
    calls["read"].clear()
    rows = shown(place, TWO)
    assert rows == [{"sentence": 0, "candidate": 0, "lines": AMUSING, "text": TWO},
                    {"sentence": 0, "candidate": 1, "lines": STRANGE, "text": TWO}]
    assert calls["project"] == [AMUSING, STRANGE]
    assert calls["read"][1:] == [AMUSING + "\n" + TWO, STRANGE + "\n" + TWO]


def test_one_candidate_reread_under_its_own_projection(place, calls):
    line = "In this document, odd means strange."
    rows = shown(place, S16)
    assert rows == [{"sentence": 0, "candidate": 0, "lines": line, "text": S16}]
    assert calls["project"] == [line] and calls["read"][-1] == line + "\n" + S16


def test_a_resolved_reading_has_no_candidate_to_render(place, calls):
    assert shown(place, AMUSING + "\nThe riddle is funny (meaning strange).") == []
    assert calls["project"] == []


def test_a_tampered_rendering_is_checker_unavailable(place, monkeypatch):
    """A rendering Lean reads to another formula (the other sense) is never shown; the genuine one is (above)."""
    monkeypatch.setattr(display, "render", lambda *a, **k: "The riddle is funny (meaning strange).")
    with pytest.raises(CheckerUnavailable, match="does not re-read under its projection"):
        shown(place, TWO)


def test_a_rendering_that_does_not_read_is_checker_unavailable(place, monkeypatch):
    monkeypatch.setattr(display, "render", lambda *a, **k: "The riddle is purple.")
    with pytest.raises(CheckerUnavailable, match="does not re-read"):
        shown(place, S16)


def test_a_base_projection_rendering_fails(place, monkeypatch):
    """Seeded-bug check (plan B7; DRI decision sn-b7b8-reread): a candidate rendered under the base projection (the
    reading's own, with no default for `funny`) is caught by the senses.read re-read on the two-candidate fixture."""
    env, overlay = place
    base = route.project(env, [PACK], "", ["funny"], overlay=overlay)["projection"]
    assert {k: base["identities"][k] for k in route.PROJECTION_IDS} == {
        k: reading(place, TWO)["identities"][k] for k in route.PROJECTION_IDS}
    rendered = display._rendered
    monkeypatch.setattr(display, "_rendered", lambda projection, candidate, overlay: rendered(base, candidate,
                                                                                               overlay))
    with pytest.raises(CheckerUnavailable, match="does not re-read under its projection"):
        shown(place, TWO)


def test_a_base_projection_is_not_the_candidates(place, monkeypatch):
    """A candidate projected without its resolving lines has the base projection's identities, not the ones its
    reading lists: refused before anything is rendered."""
    project = route.project
    monkeypatch.setattr(display.route, "project", lambda env, packs, lines, used, **kw: project(env, packs, "", used,
                                                                                                **kw))
    with pytest.raises(CheckerUnavailable, match="not the one its reading lists"):
        shown(place, TWO)


def test_a_reread_under_another_projection_is_refused(place, calls):
    """A two-sentence document whose other sentence uses `tells`: the candidate's projection has `tells`, the re-read
    of its lines and its one sentence does not, so the projections differ and the display fails closed (a re-read
    under a given projection is sn-b6c's)."""
    source = TWO + "\nAlice tells the riddle."
    answer = reading(place, source)
    assert answer["used"] == ["funny", "tells"] and len(answer["units"][0]["candidates"]) == 2
    with pytest.raises(CheckerUnavailable, match="does not re-read under its projection"):
        shown(place, source)
    assert calls["read"][-1] == AMUSING + "\n" + TWO


def _rebound(field, value):
    def tamper(answer):
        unit = answer["reading"]["units"][0] if field != "status" and field != "units" else None
        if field == "status":
            answer["reading"]["status"] = value
        elif field == "units":
            answer["reading"]["units"].append(copy.deepcopy(answer["reading"]["units"][0]))
        elif field in route.PROJECTION_IDS:
            answer["reading"]["identities"][field] = value
        else:
            unit[field] = value
        return answer
    return tamper


@pytest.mark.parametrize("field, value", [
    ("formula", ["unary", "sense__funny_1", ["const", "riddle"]]),
    ("mark", True), ("mark", 0), ("status", "open"), ("units", None),
    ("environment_id", "0" * 64), ("lexicon_id", "0" * 64), ("grammar_id", "0" * 64),
])
def test_a_reread_bound_to_another_formula_or_projection_is_refused(place, monkeypatch, field, value):
    """Every field the display reads from the re-read (status, the one unit, its formula and mark, the projection's
    identities) is bound to the candidate: a rebound value is CheckerUnavailable."""
    read = route.read
    sources = []

    def tampered(env, source, packs, **kw):
        answer = read(env, source, packs, **kw)
        sources.append(source)
        return _rebound(field, value)(answer) if len(sources) > 1 else answer

    monkeypatch.setattr(display.route, "read", tampered)
    env, overlay = place
    with pytest.raises(CheckerUnavailable, match="does not re-read"):
        display.candidates(env, [PACK], tampered(env, TWO, [PACK], overlay=overlay)["reading"], overlay=overlay)


def test_each_lines_is_projected_once_within_the_limit(place, calls, monkeypatch):
    """Two open units with the same two choices: four candidates, two projections, four re-reads; one candidate
    over the stated limit is a ResourceLimit before any service call."""
    source = TWO + "\n" + TWO
    answer = reading(place, source)
    assert [len(u["candidates"]) for u in answer["units"]] == [2, 2]
    env, overlay = place
    monkeypatch.setattr(display, "MAX_CANDIDATES", 4)
    rows = display.candidates(env, [PACK], answer, overlay=overlay)
    assert [(r["sentence"], r["candidate"], r["text"]) for r in rows] == [(s, c, TWO) for s in (0, 1) for c in (0, 1)]
    assert calls["project"] == [AMUSING, STRANGE]
    monkeypatch.setattr(display, "MAX_CANDIDATES", 3)
    calls["project"].clear()
    calls["read"].clear()
    with pytest.raises(ResourceLimit, match="at most 3 candidates"):
        display.candidates(env, [PACK], answer, overlay=overlay)
    assert calls == {"project": [], "read": []}


def _cli(tmp_path, place, source, *extra):
    env, overlay = place
    (tmp_path / "env.json").write_text(json.dumps(env.to_dict()))
    (tmp_path / "overlay.json").write_text(json.dumps(overlay))
    (tmp_path / "text.txt").write_text(source)
    return ["render", "--env", str(tmp_path / "env.json"), "--english-vocabulary", str(tmp_path / "overlay.json"),
            *extra, "--senses", str(ROOT / "ve/senses/packs/fixtures@1.json"), str(tmp_path / "text.txt")]


def test_render_senses_cli_shows_leans_reading_and_the_checked_candidates(tmp_path, place, capsys):
    assert main(_cli(tmp_path, place, TWO, "--view", "ve_english")) == 3
    out = json.loads(capsys.readouterr().out)
    assert out["operation"] == "senses.read" and out["reading"]["status"] == "open"
    assert [(r["lines"], r["text"]) for r in out["renderings"]] == [(AMUSING, TWO), (STRANGE, TWO)]
    assert main(_cli(tmp_path, place, "Alice tells the riddle.")) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["reading"]["status"] == "one" and out["renderings"] == []


def test_render_senses_cli_refuses_another_view(tmp_path, place, capsys):
    assert main(_cli(tmp_path, place, TWO, "--view", "ve_strict")) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "InvalidInput"


def test_render_senses_cli_tampered_rendering_is_checker_unavailable(tmp_path, place, capsys, monkeypatch):
    monkeypatch.setattr(display, "render", lambda *a, **k: "The riddle is funny (meaning strange).")
    assert main(_cli(tmp_path, place, TWO)) == 5
    assert json.loads(capsys.readouterr().out)["status"] == "CheckerUnavailable"
