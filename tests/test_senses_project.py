"""Senses B6: the `senses.project` mode through the service, and the identities a `senses.read` answer gives its
projection and each candidate's (docs/spec/senses-PLAN.md 2.6, 2.7; fixtures i1, i2, i6, i7)."""
from __future__ import annotations

import hashlib
from copy import deepcopy

import pytest

from test_senses_route import PACK, _paths, _retyped, pack_with, read_in, sense, world
from ve.assurance import operation
from ve.backends import senses as route
from ve.backends.service_schema import Invalid, check_row
from ve.english_grammar import actions_version, grammar_id
from ve.environment import Environment
from ve.errors import VEError
from ve.wire import canonical_json

FUNNY = "The riddle is funny."
LINE2 = "In this document, funny means strange."


@pytest.fixture(scope="module")
def joke():
    return world()


def project(joke, lines=LINE2, used=("funny",), pack=PACK):
    env, overlay = joke
    return route.project(env, [pack], lines, list(used), overlay=overlay)


def test_i1_reading_identities_are_its_projections(joke):
    env, _ = joke
    result = read_in(joke, FUNNY)
    reading, ids = result["reading"], result["reading"]["identities"]
    assert result["senses_version"] == project(joke)["senses_version"]
    assert ids["environment_id"] == Environment(reading["environment"]).environment_id
    assert ids["source_sha256"] == hashlib.sha256(FUNNY.encode()).hexdigest()
    assert (ids["grammar_id"], ids["actions_version"]) == (grammar_id(env.profiles), actions_version())
    assert "overlay_digest" not in ids and reading["used"] == ["funny"]


def test_i2_the_same_request_twice_is_byte_identical(joke):
    assert canonical_json(read_in(joke, FUNNY)) == canonical_json(read_in(joke, FUNNY))
    assert canonical_json(project(joke)) == canonical_json(project(joke))


def test_i7_candidate_projection_identities(joke):
    """Each candidate's identities are those of `senses.project` over its resolving lines, under which its sense
    is the bare one; the second candidate's are those of the document that has its line."""
    reading = read_in(joke, FUNNY)["reading"]
    [unit] = reading["units"]
    bare = {}
    for candidate in unit["candidates"]:
        projection = project(joke, candidate["lines"], reading["used"])["projection"]
        assert {k: v for k, v in projection["identities"].items() if k != "actions_version"} \
            == candidate["identities"]
        predicates = projection["environment"]["vocabulary"]["predicates"]
        bare[candidate["choice"][0][1]] = [p for p in ("sense__funny_1", "sense__funny_2")
                                           if predicates[p]["verbalisation"] == "{0} is funny"]
    assert bare == {1: ["sense__funny_1"], 2: ["sense__funny_2"]}
    resolved = read_in(joke, LINE2 + " " + FUNNY)["reading"]
    assert resolved["status"] == "one"
    assert {k: resolved["identities"][k] for k in route.PROJECTION_IDS} == unit["candidates"][1]["identities"]


@pytest.mark.parametrize("lines, used, text", [
    (FUNNY, ["funny"], "InvalidInput: sentence 1 of the lines is not a preamble line"),
    (LINE2, ["giggle"], "InvalidInput: used word giggle is not a word of the dictionary"),
    (LINE2, ["funny", "funny"], "InvalidInput: a used word is given more than once"),
])
def test_lean_refuses_a_request_with_its_text(joke, lines, used, text):
    with pytest.raises(VEError) as caught:
        project(joke, lines, used)
    assert str(caught.value) == text


def test_a_fault_of_the_lines_is_leans(joke):
    assert project(joke, "In this document, funny means purple.")["projection"] == {
        "status": "rejected", "code": "UnknownGloss", "details": {"line": 0, "word": "funny", "gloss": "purple"}}
    assert project(joke, "")["projection"]["status"] == "ok"


def test_a_large_request_is_read_once_within_the_predicate_limit(joke):
    """120 preamble lines over 120 used words of two senses each: 240 of `maxPredicates`' 256, answered; ten words
    more pass the limit, which Lean refuses by its code."""
    words = ["zq" + chr(97 + i // 26) + chr(97 + i % 26) for i in range(130)]
    big = pack_with([sense(w, k, gloss, ["joke"], "{0} is " + w) for w in words
                     for k, gloss in ((1, "amusing"), (2, "strange"))])
    lines = "\n".join(f"In this document, {w} means strange." for w in words[:120])
    projection = project(joke, lines, words[:120], big)["projection"]
    assert len(projection["environment"]["vocabulary"]["predicates"]) == 240
    assert project(joke, lines, words, big)["projection"] == {
        "status": "rejected", "code": "VocabularyLimit", "details": {"what": "predicates"}}


def _refused(env, row) -> bool:
    try:
        check_row(route.PROJECT, row, {"id": route.PROJECT}, 0)
    except Invalid:
        return True
    return route._projection_problem(row, {"id": route.PROJECT}, env, route._dictionary([PACK], [])[0]) is not None


@pytest.mark.parametrize("lines", [LINE2, "In this document, funny means purple."])
def test_projection_answer_mutations_are_rejected(joke, lines):
    """Every member of a genuine answer dropped or retyped, and every string but the version rebound, is refused;
    so is an environment whose identity is not the one the answer names."""
    env, _ = joke
    genuine = {"id": route.PROJECT, "status": "ok", "result": project(joke, lines)}
    assert not _refused(env, genuine)
    for path in _paths(genuine):
        original = genuine
        for part in path:
            original = original[part]
        # Lean's version constant is typed, not bound: its lock is sn-b6b's.
        rebound = [original + "0"] if type(original) is str and path[-1] != "senses_version" \
            and genuine["result"]["projection"]["status"] == "ok" else []
        for value in ["delete", *_retyped(original), 1.5, *rebound]:
            mutant = deepcopy(genuine)
            parent = mutant
            for part in path[:-1]:
                parent = parent[part]
            if value == "delete":
                if type(parent) is not dict:
                    continue
                del parent[path[-1]]
            else:
                parent[path[-1]] = value
            assert _refused(env, mutant), (path, value)
    if genuine["result"]["projection"]["status"] == "ok":
        mutant = deepcopy(genuine)
        mutant["result"]["projection"]["environment"]["vocabulary"]["sorts"]["joke"]["description"] = "B."
        assert _refused(env, mutant)


def test_reading_identity_rebinding_is_refused(joke):
    """The identities a reading names are bound to the request: its grammar, S2's actions version, its source, the
    returned environment and the dictionary's words."""
    env, _ = joke
    genuine = read_in(joke, FUNNY)
    binding = {"env": env, "source": FUNNY, "words": route._dictionary([PACK], [])[1]}
    def problem(result):
        return route._response_problem(result, genuine["dictionary_id"], genuine["request_id"], source=FUNNY,
                                       binding=binding)
    assert problem(genuine) is None
    edits = [("identities", key) for key in ("environment_id", "grammar_id", "source_sha256", "actions_version")]
    for key in edits:
        mutant = deepcopy(genuine)
        mutant["reading"][key[0]][key[1]] = "0" * 64
        assert problem(mutant), key
    for change in (lambda r: r["reading"].update(used=["giggle"]), lambda r: r["reading"].update(used=["funny", "giggle"]),
                   lambda r: r["reading"].update(used=["funny"] * 2),
                   lambda r: r["reading"].update(used=[]),
                   lambda r: r["reading"]["units"][0]["candidates"][0]["identities"].update(grammar_id="0" * 64),
                   lambda r: r["reading"]["units"][0]["candidates"][0]["identities"].update(extra="x")):
        mutant = deepcopy(genuine)
        change(mutant)
        assert problem(mutant)


def test_budget_zero_never_projects(joke):
    """A line read with no budget is Lean's PreambleBudget, never a projection; with no line there is no work."""
    env, overlay = joke
    assert route.project(env, [PACK], LINE2, ["funny"], overlay=overlay, budget=0)["projection"] == {
        "status": "budget", "code": "PreambleBudget", "details": {"line": 0}}
    assert route.project(env, [PACK], LINE2, ["funny"], overlay=overlay)["projection"]["status"] == "ok"


def test_the_lean_decoder_refuses_each_retyped_member(joke):
    """Each member of a genuine `senses.project` case, retyped or dropped, and an extra one, is refused: Lean's error
    row, or the service's refusal of a value its restricted reader does not take."""
    from ve.backends.relay import rows
    env, overlay = joke
    case = route.request(env, None, [PACK.decode()], overlay=overlay)
    del case["source"]
    case.update(id=route.PROJECT, lines=LINE2, used=["funny"])
    assert rows(route.PROJECT, [case])[0]["status"] == "ok"
    mutants = [dict(case, extra=True)] + [{k: v for k, v in case.items() if k != key} for key in case if key != "id"]
    mutants += [dict(case, **{key: value}) for key in case if key != "id"
                for value in _retyped(case[key]) if value is not None and not (key == "overlay" and value == {})]
    for mutant in mutants:
        try:
            [row] = rows(route.PROJECT, [mutant])
        except VEError:  # the service's restricted reader refuses the value before the decoder
            continue
        assert row["status"] == "error" and row["error"], mutant.keys()


def test_i6_both_operations_are_lean_only():
    for name in ("senses.read", "senses.project"):
        entry = operation(name)
        assert (entry["authority"], entry["target"], entry["python"]) == ("lean-only", "lean", [])
