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


@pytest.mark.parametrize("texts", [["Alice tells riddle.", "Riddle is f@nny."],
                                   ["Alice tells riddlé.", "Riddle is f@nny."], ["Alice tells riddle.", "."], S1])
def test_fence_refusals_are_senses_checks_with_e2_spans(texts):
    """E2's span and advice compose with RD-8: a fence request's refusal is `ve senses check`'s over the fences
    joined by line breaks, a lexical one at its place in that text (a document fence's closing line break
    dropped); under front-matter defaults, lines the author did not write, it has no span."""
    reading = check(texts)
    assert "span" in reading
    env = Environment(environment())
    for fences in (texts, [text + "\n" for text in texts]):
        assert route.read_fences(env, fences, [PACK])["reading"] == reading
    defaulted = route.read_fences(env, S1[1:], [PACK], defaults={"funny": 1})["reading"]
    assert defaulted["code"] == "NoDerivation" and "span" not in defaulted


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
    assert "text" not in reading["units"][0]  # the source-mode wire contract is unchanged
    refused = route.read_fences(Environment(environment()), texts, [PACK], fence_ids=["u1"],
                                reading_set_units=[])["reading"]
    assert refused["status"] == "rejected" and refused["code"] == "Unresolved"
    assert refused["text"] == ("Sentence 1 uses odd, which has two senses here, and only strange gives a reading "
                               'of this sentence. Add the line "In this document, odd means strange." to say so.')
    with pytest.raises(VEError) as info:
        load_document(write(tmp_path, texts, {"packs": ["fixtures@1"]}))
    assert info.value.message == refused["text"]
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


def test_lean_selects_the_first_open_fence_without_a_reading_set():
    assert route.read_fences(Environment(environment()), S16, [PACK])["reading"]["code"] == "Unresolved"
    result = route.read_fences(Environment(environment()), S16 * 2, [PACK],
                               fence_ids=["first", "second"], reading_set_units=["first"])
    assert result["reading"]["status"] == "rejected"
    assert result["reading"]["unit"] == "second"
    assert result["reading"]["text"].startswith("Sentence 2 uses odd")
    admitted = route.read_fences(Environment(environment()), S16 * 2, [PACK],
                                 fence_ids=["first", "second"], reading_set_units=["first", "second"])
    assert admitted["reading"]["status"] == "open"


@pytest.mark.parametrize("texts, defaults", [
    (S9, None),
    (S16, {"funny": 1}),
    (S16 * 2, None),
])
def test_shifted_genuine_sentence_numbers_are_rejected(texts, defaults):
    """A response's consecutive units and linked sense-map entries still need the request's start sentence."""
    result = _genuine(texts, defaults)
    count = len(defaults or {})
    assert route._response_problem(result, result["dictionary_id"], result["request_id"], len(texts),
                                   defaults_count=count) is None
    for shift in (1, 10):
        mutant = deepcopy(result)
        for unit in mutant["reading"]["units"]:
            unit["sentence"] += shift
        for occurrence in mutant["reading"]["sense_map"]:
            occurrence["sentence"] += shift
        assert "request's preamble" in route._response_problem(
            mutant, result["dictionary_id"], result["request_id"], len(texts), defaults_count=count)


ODD_DEFAULT = ("Sentence {n} uses odd, which has two senses here, and only strange gives a reading of this sentence. "
               'Add the default "odd": 1 to the front matter to say so.')


@pytest.mark.parametrize("texts, n", [(S16, 1), (["Alice tells riddle.", *S16], 2), (S22, 1)])
def test_open_fence_under_defaults_counts_fences_and_asks_for_a_default(tmp_path, texts, n):
    """The rendered default lines are not the author's sentences, and a written line is then refused: the text
    numbers the fence and asks for a default, and following its advice admits the document."""
    with pytest.raises(VEError) as info:
        load_document(write(tmp_path, texts, {"packs": ["fixtures@1"], "defaults": {"funny": 1}}, name="a.ve.md"))
    assert info.value.message == ODD_DEFAULT.format(n=n)
    assert info.value.diagnostic == {"unit": f"u{n}", "code": "Unresolved"}
    advised = load_document(write(tmp_path, texts, {"packs": ["fixtures@1"], "defaults": {"funny": 1, "odd": 1}},
                                  name="b.ve.md"))
    assert units_of(advised)[f"u{n}"]["status"] == "CHECKED"
    with pytest.raises(VEError, match="both in the front matter and as lines"):
        load_document(write(tmp_path, [LINE_ODD, *texts], {"packs": ["fixtures@1"], "defaults": {"funny": 1}},
                            name="c.ve.md"))


@pytest.mark.parametrize("texts, defaults", [(S16, None), (S16, {"funny": 1}), (S22, None),
                                             (["Alice tells riddle.", *S16], {"funny": 1}),
                                             (["Riddle is funny."], None),
                                             (["Riddle is funny."], {"odd": 1})])
def test_admitted_open_fence_text_is_the_refusal_text(texts, defaults):
    """The `text` of an open unit a reading set admits is the text Lean refuses the same fence with."""
    env, ids = Environment(environment()), [f"u{i}" for i in range(1, len(texts) + 1)]
    refused = route.read_fences(env, texts, [PACK], defaults=defaults, fence_ids=ids, reading_set_units=[])["reading"]
    assert (refused["status"], refused["code"], refused["unit"]) == ("rejected", "Unresolved", ids[-1])
    admitted = route.read_fences(env, texts, [PACK], defaults=defaults, fence_ids=ids,
                                 reading_set_units=[ids[-1]])["reading"]
    assert admitted["status"] == "open"
    assert admitted["units"][admitted["fences"][-1]]["text"] == refused["text"]


def test_document_relays_the_admitted_text(tmp_path):
    refused = route.read_fences(Environment(environment()), S16, [PACK], fence_ids=["u1"],
                                reading_set_units=[])["reading"]["text"]
    doc = load_document(write(tmp_path, S16, {"packs": ["fixtures@1"]}, reading_sets=[_reading_set(S16)]))
    assert doc["senses"].unresolved == {"u1": refused}


@pytest.mark.parametrize("ids, covered, text", [
    (["u1", "u1"], [], "InvalidInput: unit id u1 names more than one English fence"),
    (["u1"], [], "InvalidInput: 1 fence identities are given for 2 English fences"),
    (["u1", ""], [], "InvalidInput: an English fence has an empty unit id"),
    (["u1", "u2"], ["u2", "u2"], "InvalidInput: reading-set unit u2 is given more than once"),
    (["u1", "u2"], ["u3"], "InvalidInput: reading-set unit u3 names no English fence"),
])
def test_fence_identity_refusals_name_the_fault(ids, covered, text):
    with pytest.raises(VEError) as info:
        route.read_fences(Environment(environment()), S16 * 2, [PACK], fence_ids=ids, reading_set_units=covered)
    assert info.value.message == text


def test_a_document_whose_units_share_a_fence_id_is_refused_as_a_duplicate(tmp_path):
    path = write(tmp_path, S9, {"packs": ["fixtures@1"]})
    front, body = path.read_bytes()[4:].split(b"\n---\n", 1)
    meta = json.loads(front)
    meta["units"][1]["id"] = meta["units"][1]["content"]["fence"] = "u1"
    path.write_bytes(b"---\n" + json.dumps(meta).encode() + b"\n---\n" + body)
    with pytest.raises(VEError) as info:
        load_document(path)
    assert info.value.message == "InvalidInput: unit id u1 names more than one English fence"


def test_uncovered_open_fence_cannot_be_forged_as_admitted():
    result = route.read_fences(Environment(environment()), S16, [PACK], fence_ids=["u1"],
                               reading_set_units=["u1"])
    assert route._response_problem(result, result["dictionary_id"], result["request_id"], 1,
                                   fence_ids=["u1"], reading_set_units=["u1"]) is None
    assert "no reading set" in route._response_problem(result, result["dictionary_id"], result["request_id"], 1,
                                                       fence_ids=["u1"], reading_set_units=[])


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


CONFUSERS = [7, True, None, [], {}, ["u1"], {"u1": 1}, "u1", [[[]]]]


def _paths(value, path=()):
    yield path
    if type(value) is dict:
        for key, item in value.items():
            yield from _paths(item, path + (key,))
    elif type(value) is list:
        for n, item in enumerate(value):
            yield from _paths(item, path + (n,))


def _replaced(value, paths, new):
    value = deepcopy(value)
    for path in paths:
        if not path:
            return new
        node = value
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = new
    return value


def _reading_set(texts):
    reading = check(texts)
    [candidate] = reading["units"][0]["candidates"]
    projected = Environment(reading["environment"])
    return {"id": "r1", "unit": "u1", "version": 1, "status": "authored", "signature": "alice",
            "readings": [{"id": "strange", "kind": "asserted", "content": candidate["formula"],
                          "meaning_id": meaning_id(projected, formula_from_data(projected, candidate["formula"])),
                          "admission": {"who": "alice", "why": "w", "distinguishing_models": {}}}]}


@pytest.mark.parametrize("base", ["open fence with a reading set", "defaults"])
def test_every_front_matter_node_confused_raises_only_veerror(tmp_path, base):
    """Type confusion (build checklist 5) over a senses document's front matter outside the environment: each
    node, and every node holding the unit id at once (the fence, the unit and the reading set's unit), is
    replaced by each confuser. Loading either succeeds or raises VEError; a reading set's `unit` of the wrong
    type was a TypeError."""
    path = (write(tmp_path, S16, {"packs": ["fixtures@1"]}, reading_sets=[_reading_set(S16)])
            if base == "open fence with a reading set" else
            write(tmp_path, S9[2:], {"packs": ["fixtures@1"], "defaults": {"funny": 1, "odd": 1}}))
    load_document(path)  # the base is admitted, so each mutant reaches as far as its fault
    front, body = path.read_bytes()[4:].split(b"\n---\n", 1)
    meta = json.loads(front)
    nodes = [[p] for p in _paths(meta) if p[:1] != ("environment",)]
    nodes.append([p for p in _paths(meta) if p[:1] != ("environment",) and _get(meta, p) == "u1"])
    assert len(nodes[-1]) == (3 if base != "defaults" else 2)
    mutant = tmp_path / "mutant.ve.md"
    for paths in nodes:
        for new in CONFUSERS:
            mutant.write_bytes(b"---\n" + json.dumps(_replaced(meta, paths, new)).encode() + b"\n---\n" + body)
            try:
                load_document(mutant)
            except VEError:
                pass


def _get(value, path):
    for key in path:
        value = value[key]
    return value


def test_a_reading_set_unit_of_another_type_is_refused_not_a_crash(tmp_path):
    """The review's example: `{"unit": ["u1"]}` (or a dict) gave a TypeError traceback. It names no fence, so the
    open fence is refused with Lean's Unresolved text."""
    expected = route.read_fences(Environment(environment()), S16, [PACK], fence_ids=["u1"],
                                 reading_set_units=[])["reading"]["text"]
    for unit in (["u1"], {"u1": 1}, 7, None):
        reading_set = {**_reading_set(S16), "unit": unit}
        with pytest.raises(VEError) as info:
            load_document(write(tmp_path, S16, {"packs": ["fixtures@1"]}, reading_sets=[reading_set]))
        assert info.value.message == expected, unit


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
            refused = route.read_fences(Environment(environment()), [text], [PACK], fence_ids=["u1"],
                                        reading_set_units=[])["reading"]
            expected = ("error", refused["text"])
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
    result = route.read_fences(env, texts, [PACK], defaults=defaults,
                               reading_set_units=list(map(str, range(len(texts)))))
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


# --- budgets, deadlines and identity -------------------------------------------------------------------------

def test_budget_zero_is_never_an_admission():
    """A fence request with no budget stops on the budget (Lean's `preambleBudget` or `Budget`), never `one`."""
    env = Environment(environment())
    for texts in (S9, S16, ["Alice tells riddle."]):
        reading = route.read_fences(env, texts, [PACK], budget=0)["reading"]
        assert reading["status"] == "budget", texts


def test_deadline_covers_the_fence_request(monkeypatch):
    """An injected clock that passes the deadline while the packs are prepared stops before the runner starts."""
    from types import SimpleNamespace
    clock = [0.0]
    monkeypatch.setattr(route, "time", SimpleNamespace(monotonic=lambda: clock[0]))
    original = route._text

    def delayed(raw):
        clock[0] = 1_000_000_000
        return original(raw)
    monkeypatch.setattr(route, "_text", delayed)

    def must_not_run(*_args, **_kwargs):
        pytest.fail("the runner started after the deadline")
    monkeypatch.setattr(route.lean_backend, "run", must_not_run)
    with pytest.raises(CheckerUnavailable, match="deadline"):
        route.read_fences(Environment(environment()), S9, [PACK])


@pytest.mark.parametrize("change", [
    lambda s: {**s, "defaults": {"funny": 1, "odd": 1}},
    lambda s: {**s, "own": [{"word": "zany", "index": 1, "gloss": "wild", "description": "a sense of zany",
                             "kinds": ["joke"], "wording": "{0} is zany"}]},
    lambda s: {**s, "packs": ["fixtures@1", "fixtures@1"]},
])
def test_every_senses_field_is_bound_by_the_request_and_document_ids(tmp_path, change):
    """Each field of `senses` changes the document id (front matter) and Lean's request id (the envelope)."""
    base = {"packs": ["fixtures@1"]}
    texts = S9[2:]
    first = write(tmp_path, texts, base, name="first.ve.md")
    second = write(tmp_path, texts, change(base), name="second.ve.md")
    from ve.document import stored_identities
    assert stored_identities(first.read_bytes())[2] != stored_identities(second.read_bytes())[2]
    env = Environment(environment())
    requests = [route.request(env, None, [PACK.decode()] * len(s.get("packs", [])), own=s.get("own", []),
                              fences=texts, defaults=s.get("defaults")) for s in (base, change(base))]
    from ve.wire import digest
    assert digest("ve-senses-request-v1\n", requests[0]) != digest("ve-senses-request-v1\n", requests[1])
