"""RD-8 (readings-defaults plan, section 6): senses in `ve document`.

A document with `senses` in its front matter has its English fences read by Lean's `senses.read`, in one
request, one sentence per fence; the front matter's defaults are rendered by Lean as preamble lines. The
fixtures are the senses spec's s1, s9, s16 and s22 as fences, compared with `ve senses check` on the same
text (both paths call the one compiled reader). The document environment has no English overlay, so the
constant `riddle` reads as `Riddle` where the spec writes `the riddle`.
"""
from __future__ import annotations

import json
import shutil
from copy import deepcopy

import pytest

from ve.ast import formula_from_data
from ve.backends import senses as route
from ve.document import check_document, load_document
from ve.environment import Environment
from ve.errors import CheckerUnavailable, VEError
from ve.identity import meaning_id
from ve.senses import bundled_pack

PACK = bundled_pack("fixtures@1")
LINE_FUNNY = "In this document, funny means amusing."
LINE_ODD = "In this document, odd means strange."
S1 = [LINE_FUNNY, "Every joke that is funny (meaning strange) is not funny.", "Alice tells riddle.",
      "Riddle is funny (meaning strange).", "Therefore riddle is not funny."]
S9 = [LINE_FUNNY, LINE_ODD, "Every funny joke is odd."]
S16 = ["Riddle is odd."]
S22 = ["Both riddle is odd and riddle is funny (meaning strange)."]


def environment(profiles=None):
    data = {"language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
            "vocabulary": {"sorts": {name: {"description": "A sort."} for name in ("joke", "person")},
                           "predicates": {},
                           "constants": {"alice": {"sort": "person", "description": "A constant."},
                                         "riddle": {"sort": "joke", "description": "A constant."}}}}
    if profiles is not None:
        data["profiles"] = profiles
    return data


def line(text):
    return text.startswith("In this document,")


def write(tmp_path, texts, senses=None, *, reading_sets=None, extra=None, name="doc.ve.md"):
    """A document with one English fence per text, unit `u<i>` each; a preamble line is a definition."""
    body, units, cursor = b"", [], 0
    for i, text in enumerate(texts, 1):
        prose = f"Sentence {i}.\n".encode()
        body += prose + f"```ve u{i}\n{text}\n```\n".encode()
        units.append({"id": f"u{i}", "span": [cursor, cursor + len(prose)],
                      "kind": "definition" if line(text) else "asserted", "meaning": "specified",
                      "support": "assumption", "surface": "english", "content": {"fence": f"u{i}"}})
        cursor += len(prose)
    front = {"format": "ve-document@1", "environment": environment(), "units": units,
             **({"senses": senses} if senses is not None else {}),
             **({"reading_sets": reading_sets} if reading_sets is not None else {}), **(extra or {})}
    path = tmp_path / name
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + body)
    return path


def check(texts):
    """`ve senses check`'s reading of the same text: the fences joined by line breaks."""
    return route.read(Environment(environment()), "\n".join(texts), [PACK])["reading"]


def units_of(doc):
    return {u["id"]: u for u in doc["units"]}


# --- the spec fixtures as fences -------------------------------------------------------------------------

def test_s1_refused_as_senses_check_refuses_it(tmp_path):
    reading = check(S1)
    assert (reading["status"], reading["code"]) == ("none", "NoDerivation")
    with pytest.raises(VEError) as info:
        load_document(write(tmp_path, S1, {"packs": ["fixtures@1"]}))
    assert info.value.message == reading["text"] == "Sentence 2 has no reading with the current vocabulary."
    assert info.value.diagnostic == reading


def test_s9_formula_and_meaning_id_are_leans(tmp_path):
    reading = check(S9)
    [lean_unit] = reading["units"]
    doc = load_document(write(tmp_path, S9, {"packs": ["fixtures@1"]}))
    units = units_of(doc)
    projected = Environment(reading["environment"])
    assert units["u3"]["content"] == lean_unit["formula"] == [
        "forall", "joke", ["implies", ["unary", "sense__funny_1", ["var", 0]], ["unary", "sense__odd_1", ["var", 0]]]]
    assert units["u3"]["meaning_id"] == meaning_id(projected, formula_from_data(projected, lean_unit["formula"]))
    assert units["u3"]["status"] == "CHECKED"
    # the preamble lines are no claims
    assert (units["u1"]["content"], units["u2"]["content"]) == (None, None)
    assert doc["senses"].lines == {"u1", "u2"}
    assert doc["senses"].environment.environment_id == projected.environment_id
    assert doc["environment"].environment_id != projected.environment_id


@pytest.mark.parametrize("texts", [S16, S22], ids=["s16", "s22"])
def test_open_fence_refused_with_leans_unresolved_text(tmp_path, texts):
    reading = check(texts)
    assert (reading["status"], reading["code"]) == ("open", "Unresolved")
    [lean_unit] = reading["units"]
    assert lean_unit["text"] == ("Sentence 1 uses odd, which has two senses here, and only strange gives a reading "
                                 'of this sentence. Add the line "In this document, odd means strange." to say so.')
    with pytest.raises(VEError) as info:
        load_document(write(tmp_path, texts, {"packs": ["fixtures@1"]}))
    assert info.value.message == lean_unit["text"]
    assert info.value.diagnostic == {"unit": "u1", "code": "Unresolved"}


def test_open_fence_with_a_reading_set_loads(tmp_path):
    [candidate] = check(S16)["units"][0]["candidates"]
    projected = Environment(check(S16)["environment"])
    reading_set = {"id": "r1", "unit": "u1", "version": 1, "status": "authored", "signature": "alice",
                   "readings": [{"id": "strange", "kind": "asserted", "content": candidate["formula"],
                                 "meaning_id": meaning_id(projected, formula_from_data(projected, candidate["formula"])),
                                 "admission": {"who": "alice", "why": "the author chose strange",
                                               "distinguishing_models": {}}}]}
    doc = load_document(write(tmp_path, S16, {"packs": ["fixtures@1"]}, reading_sets=[reading_set]))
    assert units_of(doc)["u1"]["content"] is None
    assert units_of(doc)["u1"]["status"] == "CHECKED"


# --- front-matter defaults ----------------------------------------------------------------------------------

def test_defaults_read_as_the_same_text_with_the_lines_written(tmp_path):
    written = load_document(write(tmp_path, S9, {"packs": ["fixtures@1"]}, name="written.ve.md"))
    given = load_document(write(tmp_path, S9[2:], {"packs": ["fixtures@1"], "defaults": {"funny": 1, "odd": 1}},
                                name="given.ve.md"))
    assert units_of(given)["u1"]["content"] == units_of(written)["u3"]["content"] == check(S9)["units"][0]["formula"]
    assert units_of(given)["u1"]["meaning_id"] == units_of(written)["u3"]["meaning_id"]
    assert given["senses"].environment.environment_id == written["senses"].environment.environment_id
    # the defaults resolve s16's open unit, as the written line does
    resolved = load_document(write(tmp_path, S16, {"packs": ["fixtures@1"], "defaults": {"odd": 1}}, name="s16.ve.md"))
    assert units_of(resolved)["u1"]["content"] == check([LINE_ODD, *S16])["units"][0]["formula"]


def test_defaults_and_written_lines_are_refused(tmp_path):
    path = write(tmp_path, S9, {"packs": ["fixtures@1"], "defaults": {"funny": 1}})
    with pytest.raises(VEError, match="^InvalidInput: defaults are given both in the front matter and as lines$"):
        load_document(path)


@pytest.mark.parametrize("defaults, text", [
    ({"funny": 3}, "InvalidInput: the front matter gives funny the default 3, which is not one of its senses"),
    ({"zany": 1}, "InvalidInput: the front matter gives zany the default 1, which is not one of its senses"),
])
def test_a_default_that_names_no_sense_is_refused(tmp_path, defaults, text):
    with pytest.raises(VEError) as info:
        load_document(write(tmp_path, S16, {"packs": ["fixtures@1"], "defaults": defaults}))
    assert info.value.message == text


@pytest.mark.parametrize("defaults", [{"odd": True}, {"odd": "1"}, {"odd": -1}, {"odd": 1.5}, [], "odd", 7])
def test_malformed_defaults_are_refused_by_lean(tmp_path, defaults):
    with pytest.raises(VEError):
        load_document(write(tmp_path, S16, {"packs": ["fixtures@1"], "defaults": defaults}))


# --- one sentence per fence -------------------------------------------------------------------------------

@pytest.mark.parametrize("texts, message", [
    (["Alice tells riddle. Riddle is odd."],
     "InvalidInput: English fence 1 holds 2 sentences; each VE fence must contain exactly one sentence"),
    (["Riddle is odd.", "Alice tells riddle. Riddle is odd. Alice tells riddle."],
     "InvalidInput: English fence 2 holds 3 sentences; each VE fence must contain exactly one sentence"),
])
def test_a_fence_of_several_sentences_is_refused(tmp_path, texts, message):
    with pytest.raises(VEError) as info:
        load_document(write(tmp_path, texts, {"packs": ["fixtures@1"], "defaults": {"odd": 1}}))
    assert info.value.message == message


# --- the path never reads English in Python -----------------------------------------------------------------

def test_parse_english_is_not_called_for_a_senses_document(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("parse_english called on the senses path")
    monkeypatch.setattr("ve.english.parse_english", forbidden)
    assert units_of(load_document(write(tmp_path, S9, {"packs": ["fixtures@1"]})))["u3"]["content"]
    # the patch is live: the same document without senses reads its fences with parse_english
    plain = write(tmp_path, ["Alice tells riddle."], name="plain.ve.md")
    with pytest.raises(AssertionError, match="parse_english called"):
        load_document(plain)


def test_check_document_checks_in_the_projected_environment(tmp_path):
    result = check_document(write(tmp_path, S9, {"packs": ["fixtures@1"]}))
    assert result["premises"]["status"] == "model"


def test_pack_by_path_relative_to_the_document(tmp_path):
    (tmp_path / "packs").mkdir()
    (tmp_path / "packs" / "mine.json").write_bytes(PACK)
    by_path = load_document(write(tmp_path, S9, {"packs": ["packs/mine.json"]}, name="a.ve.md"))
    by_name = load_document(write(tmp_path, S9, {"packs": ["fixtures@1"]}, name="b.ve.md"))
    assert units_of(by_path)["u3"]["meaning_id"] == units_of(by_name)["u3"]["meaning_id"]
    with pytest.raises(VEError, match="Cannot read sense pack"):
        load_document(write(tmp_path, S9, {"packs": ["packs/missing.json"]}, name="c.ve.md"))


@pytest.mark.parametrize("profiles", [["soft-norms@0"], ["readings@1"], ["norm-defaults@0", "norms@0"]])
def test_other_routes_are_not_read_with_senses(tmp_path, profiles):
    path = write(tmp_path, S9, {"packs": ["fixtures@1"]})
    raw = path.read_bytes()
    front, body = raw[4:].split(b"\n---\n", 1)
    meta = json.loads(front)
    meta["environment"] = environment(profiles)
    path.write_bytes(b"---\n" + json.dumps(meta).encode() + b"\n---\n" + body)
    with pytest.raises(VEError):
        load_document(path)


@pytest.mark.parametrize("senses", [7, True, None, [], "fixtures@1", {"packs": "fixtures@1"},
                                    {"packs": [7]}, {"packs": ["fixtures@1"], "extra": 1},
                                    {"packs": ["../x"]}, {"packs": ["fixtures@1"], "own": 7},
                                    {"packs": ["fixtures@1"], "own": [{}]}, {"packs": [{"deep": [[[[[]]]]]}]}])
def test_malformed_senses_raise_only_veerror(tmp_path, senses):
    with pytest.raises(VEError):
        load_document(write(tmp_path, S9, senses))


# --- entry points agree: one fence read by the document and by `ve senses check` ----------------------------

VARIANTS = ["Riddle is odd.", "Riddle is odd.", "Riddle  is odd.", "Riddle\tis odd.", "Riddle is odd.\r",
            "Riddle is “odd”.", "Riddle is Kodd.", "İn this document, odd means strange.",
            "Riddle is odd\u0007.", "Riddle is odd", "Every funny joke is odd.", "Alice tells riddle."]


@pytest.mark.parametrize("text", VARIANTS)
def test_one_fence_gets_the_answer_senses_check_gives(tmp_path, text):
    """Lean lexes both: a text is admitted with the same formula, or refused with the same text, on both paths."""
    try:
        reading = check([text])
    except VEError as exc:
        expected = ("error", exc.message)
    else:
        if reading["status"] == "one":
            expected = ("formula", reading["units"][0]["formula"])
        elif reading["status"] == "open":
            expected = ("error", reading["units"][0]["text"])
        else:
            expected = ("error", reading.get("text", reading.get("code")))
    try:
        doc = load_document(write(tmp_path, [text], {"packs": ["fixtures@1"]}))
    except VEError as exc:
        got = ("error", exc.message)
    else:
        got = ("formula", units_of(doc)["u1"]["content"]) if "u1" not in doc["senses"].lines else ("line", None)
    if expected[0] == "formula" or got[0] != "line":
        assert got == expected, text


# --- the relay validates Lean's new fields -------------------------------------------------------------------

def _genuine(texts, defaults=None):
    env = Environment(environment())
    result = route.read_fences(env, texts, [PACK], defaults=defaults)
    return result


@pytest.mark.parametrize("mutate", [
    lambda r: r["reading"].pop("fences"),
    lambda r: r["reading"]["fences"].pop(),
    lambda r: r["reading"]["fences"].append(0),
    lambda r: r["reading"]["fences"].__setitem__(2, True),
    lambda r: r["reading"]["fences"].__setitem__(2, 1),
    lambda r: r["reading"]["fences"].__setitem__(2, "line"),
    lambda r: r["reading"]["fences"].__setitem__(0, 0),
    lambda r: r["reading"].__setitem__("fences", {}),
    lambda r: r["reading"]["units"][0].__setitem__("text", "Sentence 3 uses nothing."),
])
def test_genuine_fence_answer_mutations_are_rejected(mutate):
    result = _genuine(S9)
    assert route._response_problem(result, result["dictionary_id"], result["request_id"], 3) is None
    bad = deepcopy(result)
    mutate(bad)
    assert route._response_problem(bad, bad["dictionary_id"], bad["request_id"], 3)


@pytest.mark.parametrize("mutate", [
    lambda u: u.pop("text"),
    lambda u: u.__setitem__("text", ""),
    lambda u: u.__setitem__("text", 7),
])
def test_genuine_open_unit_text_mutations_are_rejected(mutate):
    result = _genuine(S16)
    assert route._response_problem(result, result["dictionary_id"], result["request_id"], 1) is None
    bad = deepcopy(result)
    mutate(bad["reading"]["units"][0])
    assert route._response_problem(bad, bad["dictionary_id"], bad["request_id"], 1)


def test_a_source_answer_carries_no_fence_map():
    env = Environment(environment())
    result = route.read(env, "Riddle is odd.", [PACK])
    assert "fences" not in result["reading"]
    assert route._response_problem(result, result["dictionary_id"], result["request_id"]) is None
    bad = deepcopy(result)
    bad["reading"]["fences"] = [0]
    assert route._response_problem(bad, bad["dictionary_id"], bad["request_id"])


def test_a_malformed_fence_answer_is_checker_unavailable(monkeypatch):
    real = route.lean_backend.run

    def drop(*args, **kwargs):
        rows = real(*args, **kwargs)
        rows[0]["result"]["reading"]["fences"] = rows[0]["result"]["reading"]["fences"][:-1]
        return rows
    monkeypatch.setattr(route.lean_backend, "run", drop)
    with pytest.raises(CheckerUnavailable, match="fence map"):
        _genuine(S9)
