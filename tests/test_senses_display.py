"""The senses display (senses plan 2.8, B7; sn-b7 as cut by reviews/dri-decisions-20261101-sn-b7b8.md item 1, and
sn-b7b): each candidate of an open unit is rendered under the projection `senses.project` returns for its resolving
lines and re-read by Lean under that same projection (`senses.read`'s `reread`, sn-b6d), on fixtures that read as
merged (s16, one candidate; `The riddle is funny.`, two); a resolved body is Lean's preamble lines and its rendering,
re-read by Lean; the glossary and the hover rows are the sense map's (g2, g3)."""
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
    return display.candidates(env, [PACK], source, reading(place, source), overlay=overlay)


@pytest.fixture
def calls(monkeypatch):
    """The `senses.project` lines and the `senses.read` sources the display sends."""
    seen = {"project": [], "read": []}
    project, read = route.project, route.read

    def spy_project(env, packs, lines, used, **kw):
        seen["project"].append(lines)
        return project(env, packs, lines, used, **kw)

    def spy_read(env, source, packs, **kw):
        seen["read"].append(source if kw.get("reread") is None else kw["reread"])
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
    assert rows == [{"sentence": 0, "candidate": 0, "lines": AMUSING, "lacking": [AMUSING], "text": TWO},
                    {"sentence": 0, "candidate": 1, "lines": STRANGE, "lacking": [STRANGE], "text": TWO}]
    assert calls["project"] == [AMUSING, STRANGE]
    assert calls["read"][1:] == [(0, 0, TWO), (0, 1, TWO)]


def test_one_candidate_reread_under_its_own_projection(place, calls):
    line = "In this document, odd means strange."
    rows = shown(place, S16)
    assert rows == [{"sentence": 0, "candidate": 0, "lines": line, "lacking": [line], "text": S16}]
    assert calls["project"] == [line] and calls["read"][-1] == (0, 0, S16)


def test_the_lines_a_candidate_lacks_are_those_not_in_leans_preamble(place):
    """A document with a line for `odd`: each candidate's lines keep it (Lean's `lines`), and only the line for the
    unresolved `funny` is the one the document lacks."""
    odd = "In this document, odd means strange."
    rows = shown(place, odd + "\n" + TWO + "\n" + S16)
    assert [(r["sentence"], r["lines"], r["lacking"]) for r in rows] == [
        (1, odd + "\n" + AMUSING, [AMUSING]), (1, odd + "\n" + STRANGE, [STRANGE])]
    for written in ("In this document,  odd means strange.", "In this document,\nodd means strange."):
        answer = reading(place, written + "\n" + TWO)
        assert answer["preamble"] == [written]  # Lean's line as written, not as `lines` writes it
        assert [r["lacking"] for r in shown(place, written + "\n" + TWO)] == [[AMUSING], [STRANGE]]


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


def test_a_two_sentence_candidate_rereads_and_a_patched_projection_is_refused(place, calls, monkeypatch):
    """A two-sentence document whose other sentence uses `tells`: Lean re-reads each candidate's rendering in its
    document, under the candidate's own projection (sn-b6d), so both are shown (sn-b7 failed closed here). With the
    second candidate's projection identity patched, it is refused at its projection, before its own re-read."""
    source = TWO + "\nAlice tells the riddle."
    answer = reading(place, source)
    assert answer["used"] == ["funny", "tells"] and len(answer["units"][0]["candidates"]) == 2
    assert [r["text"] for r in shown(place, source)] == [TWO, TWO]
    assert calls["read"][-2:] == [(0, 0, TWO), (0, 1, TWO)]
    answer["units"][0]["candidates"][1]["identities"]["lexicon_id"] = "0" * 64
    env, overlay = place
    calls["read"].clear()
    with pytest.raises(CheckerUnavailable, match="not the one its reading lists"):
        display.candidates(env, [PACK], source, answer, overlay=overlay)
    assert calls["read"] == [(0, 0, TWO)]


@pytest.mark.parametrize("outcome, error", [("different", CheckerUnavailable), ("unknown", ResourceLimit),
                                            (None, CheckerUnavailable)])
def test_a_candidate_is_shown_only_when_leans_reread_is_same(place, monkeypatch, outcome, error):
    """The display reads the re-read's `outcome` only (the relay binds its unit and candidate): `different` and no
    re-read (a refused reading) are CheckerUnavailable; `unknown` (the budget ended) is a ResourceLimit."""
    read = route.read

    def tampered(env, source, packs, **kw):
        answer = read(env, source, packs, **kw)
        if kw.get("reread") is not None:
            if outcome is None:
                del answer["reading"]["reread"]
            else:
                answer["reading"]["reread"]["outcome"] = outcome
        return answer

    monkeypatch.setattr(display.route, "read", tampered)
    with pytest.raises(error, match="does not re-read|work budget"):
        shown(place, TWO)


RESOLVED = AMUSING + "\nThe riddle is funny.\nAlice tells the riddle."


def test_the_body_is_leans_preamble_then_the_rendering_reread(place, calls):
    """g1's mechanism on a fixture that reads as merged: Lean's preamble line, then the body rendered under the
    reading's projected environment with nothing on the default occurrence, and Lean's re-read of that text."""
    env, overlay = place
    answer = reading(place, RESOLVED)
    assert answer["preamble"] == [AMUSING] and [o["is_default"] for o in answer["sense_map"]] == [True, True]
    calls["read"].clear()
    assert display.body(env, [PACK], RESOLVED, answer, overlay=overlay) == {"text": RESOLVED,
                                                                           "body_status": "rendered"}
    assert calls["read"] == [RESOLVED] and calls["project"] == []
    assert display.body(env, [PACK], TWO, reading(place, TWO), overlay=overlay) == {
        "text": None, "body_status": "not-one-reading"}


def test_a_body_with_a_switched_occurrence_is_not_rendered(place, calls):
    """Python's renderer has no wording for a sense with its gloss, so a body whose sense map has a switched
    occurrence is not rendered (and nothing is re-read); its reading is still shown."""
    env, overlay = place
    source = AMUSING + "\nThe riddle is funny (meaning strange)."
    calls["read"].clear()
    assert display.body(env, [PACK], source, reading(place, source), overlay=overlay) == {
        "text": None, "body_status": "switched-occurrence-not-rendered"}
    assert calls["read"] == [source]


def test_a_body_rendered_under_another_projection_is_checker_unavailable(place, monkeypatch):
    """The body rendered under the base projection, where `funny` has no default and Python's renderer words
    neither sense (`is classified as`), is not the text Lean reads back."""
    env, overlay = place
    base = route.project(env, [PACK], "", ["funny", "tells"], overlay=overlay)["projection"]["environment"]
    render = display._render
    monkeypatch.setattr(display, "_render", lambda environment, *a: render(base, *a))
    with pytest.raises(CheckerUnavailable, match="does not re-read to the reading"):
        display.body(env, [PACK], RESOLVED, reading(place, RESOLVED), overlay=overlay)


def _rebound(tampered, value):
    field = tampered.removesuffix("-last")

    def tamper(answer):
        unit = answer["reading"]["units"][-1 if tampered.endswith("-last") else 0]
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
    ("formula", ["unary", "sense__funny_2", ["const", "riddle"]]),
    ("mark", True), ("mark", 0), ("status", "open"), ("units", None),
    ("environment_id", "0" * 64), ("lexicon_id", "0" * 64), ("grammar_id", "0" * 64),
    ("formula-last", ["binary", "sense__tells_1", ["const", "riddle"], ["const", "alice"]]), ("mark-last", True),
    ("status", "budget"),
])
def test_a_reread_bound_to_another_formula_or_projection_is_refused(place, monkeypatch, field, value):
    """Every field the display reads from the body's re-read (status, the units, each formula and mark, the
    projection's identities) is bound to the reading: a rebound value is CheckerUnavailable."""
    read = route.read
    sources = []

    def tampered(env, source, packs, **kw):
        answer = read(env, source, packs, **kw)
        sources.append(source)
        return _rebound(field, value)(answer) if len(sources) > 1 else answer

    monkeypatch.setattr(display.route, "read", tampered)
    env, overlay = place
    with pytest.raises(ResourceLimit if value == "budget" else CheckerUnavailable, match="does not re-read|budget"):
        display.body(env, [PACK], RESOLVED, tampered(env, RESOLVED, [PACK], overlay=overlay)["reading"],
                     overlay=overlay)


GLOSSED = AMUSING + "\nThe riddle is funny.\nThe riddle is funny (meaning strange).\nAlice tells the riddle."


def test_g2_the_glossary_is_the_sense_maps(place):
    """g2 on a fixture that reads as merged: one row per used sense in Lean's order, written as its first occurrence
    is (the source bytes of its span), with Lean's gloss and the projected description; then the unused defaults."""
    rows = display.glossary(GLOSSED, reading(place, GLOSSED))
    assert rows == {"senses": [
        {"symbol": "sense__funny_1", "written": "funny", "gloss": "amusing", "description": "causes laughter",
         "is_default": True, "sentences": [1]},
        {"symbol": "sense__funny_2", "written": "funny (meaning strange)", "gloss": "strange",
         "description": "odd, hard to explain", "is_default": False, "sentences": [2]},
        {"symbol": "sense__tells_1", "written": "tells", "gloss": "says aloud", "description": "says the joke to "
         "someone", "is_default": True, "sentences": [3]}], "unused": []}
    unused = "In this document, odd means strange.\nThe riddle is funny (meaning strange)."
    assert display.glossary(unused, reading(place, unused))["unused"] == ["odd"]
    assert display.glossary(TWO, reading(place, TWO)) == {"senses": [], "unused": []}


def test_the_glossary_and_hover_follow_the_reading_not_the_pack(place):
    """The rows take the gloss and default flag from the sense map and the description from the projected
    environment: changed there, the rows change with them."""
    answer = copy.deepcopy(reading(place, RESOLVED))
    answer["sense_map"][0].update(gloss="witty", is_default=False)
    answer["environment"]["vocabulary"]["predicates"]["sense__funny_1"]["description"] = "makes one smile"
    [row] = [r for r in display.glossary(RESOLVED, answer)["senses"] if r["symbol"] == "sense__funny_1"]
    assert (row["gloss"], row["is_default"], row["description"]) == ("witty", False, "makes one smile")
    assert (display.hover(RESOLVED, answer)[0]["gloss"], display.hover(RESOLVED, answer)[0]["description"]) == (
        "witty", "makes one smile")


def test_g3_hover_spans_cut_the_source_at_token_boundaries(place):
    """g3: each hover row is a sense-map entry whose bytes are exactly its written words, cut where its tokens
    start and end; a candidate's entries keep their candidate."""
    source = "Alice tells the riddle. " + GLOSSED.split("\n", 1)[1].replace("\n", " ")
    source = AMUSING + "  \u00a0" + source
    answer = reading(place, source)
    rows = display.hover(source, answer)
    data = source.encode()
    assert [data[r["byte_start"]:r["byte_stop"]].decode() for r in rows] == [
        "tells", "funny", "funny (meaning strange)", "tells"]
    assert all(data[r["byte_start"] - 1:r["byte_start"]] == b" " and data[r["byte_stop"]:r["byte_stop"] + 1] in
               (b" ", b".") for r in rows)
    assert [(r["symbol"], r["is_default"], r["gloss"]) for r in rows][1:3] == [
        ("sense__funny_1", True, "amusing"), ("sense__funny_2", False, "strange")]
    assert rows[0]["description"] == "says the joke to someone"
    assert [r.get("candidate") for r in display.hover(TWO, reading(place, TWO))] == [0, 1]


def test_each_lines_is_projected_once_within_the_limit(place, calls, monkeypatch):
    """Two open units with the same two choices: four candidates, two projections, four re-reads; one candidate, or
    one source byte re-read, over the stated limits is a ResourceLimit before any service call."""
    source = TWO + "\n" + TWO
    answer = reading(place, source)
    assert [len(u["candidates"]) for u in answer["units"]] == [2, 2]
    env, overlay = place
    monkeypatch.setattr(display, "MAX_CANDIDATES", 4)
    monkeypatch.setattr(display, "MAX_REREAD_BYTES", 4 * len(source.encode()))
    rows = display.candidates(env, [PACK], source, answer, overlay=overlay)
    assert [(r["sentence"], r["candidate"], r["text"]) for r in rows] == [(s, c, TWO) for s in (0, 1) for c in (0, 1)]
    assert calls["project"] == [AMUSING, STRANGE] and len(calls["read"]) == 1 + 4
    monkeypatch.setattr(display, "MAX_REREAD_BYTES", 4 * len(source.encode()) - 1)
    calls["project"].clear()
    calls["read"].clear()
    with pytest.raises(ResourceLimit, match="re-reads at most"):
        display.candidates(env, [PACK], source, answer, overlay=overlay)
    assert calls == {"project": [], "read": []}
    monkeypatch.setattr(display, "MAX_CANDIDATES", 3)
    calls["project"].clear()
    calls["read"].clear()
    with pytest.raises(ResourceLimit, match="at most 3 candidates"):
        display.candidates(env, [PACK], source, answer, overlay=overlay)
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
    assert [(r["lines"], r["lacking"], r["text"]) for r in out["renderings"]] == [
        (AMUSING, [AMUSING], TWO), (STRANGE, [STRANGE], TWO)]
    assert out["text"] is None and out["body_status"] == "not-one-reading" and "glossary" not in out and "hover" not in out
    assert main(_cli(tmp_path, place, RESOLVED, "--glossary", "--json")) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["reading"]["status"] == "one" and out["renderings"] == [] and out["text"] == RESOLVED
    assert out["glossary"] == display.glossary(RESOLVED, out["reading"])
    assert out["hover"] == display.hover(RESOLVED, out["reading"]) and len(out["hover"]) == 2


def test_glossary_and_json_need_senses(tmp_path, place, capsys):
    args = _cli(tmp_path, place, TWO, "--glossary")
    del args[-3:-1]
    assert main(args) == 2 and "give --senses PACK" in capsys.readouterr().out


def test_render_senses_cli_refuses_another_view(tmp_path, place, capsys):
    assert main(_cli(tmp_path, place, TWO, "--view", "ve_strict")) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "InvalidInput"


def test_render_senses_cli_tampered_rendering_is_checker_unavailable(tmp_path, place, capsys, monkeypatch):
    monkeypatch.setattr(display, "render", lambda *a, **k: "The riddle is funny (meaning strange).")
    assert main(_cli(tmp_path, place, TWO)) == 5
    assert json.loads(capsys.readouterr().out)["status"] == "CheckerUnavailable"
