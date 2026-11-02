"""Senses B6: the `senses.project` mode through the service, and the identities a `senses.read` answer gives its
projection and each candidate's (docs/spec/senses-PLAN.md 2.6, 2.7; fixtures i1, i2, i6, i7)."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy

import pytest

from test_senses_route import PACK, _paths, _retyped, pack_with, read_in, sense, world
from ve.assurance import operation
from ve.backends import lean_service, senses as route
from ve.backends.lean import ROUTE_TIMEOUT
from ve.backends.service_schema import Invalid, check_row
from ve.english_grammar import actions_version, grammar_id
from ve.environment import Environment
from ve.errors import CheckerUnavailable, VEError
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


def test_the_large_request_is_answered_within_half_its_deadline(joke, monkeypatch):
    """The large request leaves its deadline a 2x margin: its pack of 260 senses costs the shared dictionary decode
    and checks most of it, and under load the core modes' 6.4 s failed it (review F1)."""
    monkeypatch.setitem(lean_service.DEADLINES, route.PROJECT,
                        tuple(share / 2 for share in lean_service.DEADLINES[route.PROJECT]))
    test_a_large_request_is_read_once_within_the_predicate_limit(joke)


def test_a_projection_is_as_available_as_the_reading_it_serves():
    """`senses.project` decodes the packs the reading decodes: its CPU deadline is the document mode's, which reads
    senses, and never below `senses.read`'s route timeout, at any request size (review F1)."""
    for size in (0, 46_000, 1 << 20, 8 << 20):
        assert lean_service.deadline(route.PROJECT, size) == lean_service.deadline("document", size)
        assert lean_service.deadline(route.PROJECT, size) >= ROUTE_TIMEOUT


def project_case(joke, lines=LINE2, used=("funny",)):
    """The `senses.project` case `project` sends, which the schema's bindings read."""
    env, overlay = joke
    case = route.request(env, None, [PACK.decode()], overlay=overlay)
    del case["source"]
    case.update(id=route.PROJECT, lines=lines, used=list(used))
    return case


def _refused(env, row, case) -> bool:
    try:
        check_row(route.PROJECT, row, case, 0)
    except Invalid:
        return True
    return route._projection_problem(row, case, env, route._dictionary([PACK], [])[0]) is not None


def _every_path(value, prefix=()):
    """Every path to a member or element, the projected environment's included (typed in senses.project.json)."""
    items = value.items() if type(value) is dict else enumerate(value) if type(value) is list else ()
    for key, item in items:
        yield prefix + (key,)
        yield from _every_path(item, prefix + (key,))


@pytest.mark.parametrize("lines", [LINE2, "In this document, funny means purple."])
def test_projection_answer_mutations_are_rejected(joke, lines):
    """Every member of a genuine answer, the projected environment's included, dropped or retyped, and every string
    but the version rebound, is refused: by the schema or by the relay's binding of the environment's identity."""
    env, _ = joke
    case = project_case(joke, lines)
    genuine = {"id": route.PROJECT, "status": "ok", "result": project(joke, lines)}
    assert not _refused(env, genuine, case)
    paths = list(_every_path(genuine))
    assert genuine["result"]["projection"]["status"] != "ok" or \
        ("result", "projection", "environment", "vocabulary", "sorts", "joke", "description") in paths
    for path in paths:
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
            assert _refused(env, mutant, case), (path, value)


def test_the_typed_environment_is_bound_to_the_request(joke):
    """The schema refuses a projected environment whose language, revision or constants are not the request's, an
    unknown member, and a sort with an unknown member; the relay refuses one whose identity is not the answer's."""
    env, _ = joke
    case = project_case(joke)
    genuine = {"id": route.PROJECT, "status": "ok", "result": project(joke)}
    def schema_refuses(change):
        mutant = deepcopy(genuine)
        change(mutant["result"]["projection"]["environment"])
        try:
            check_row(route.PROJECT, mutant, case, 0)
        except Invalid:
            return True
        return False
    assert not schema_refuses(lambda e: None)
    assert schema_refuses(lambda e: e.update(language="ve.closure@0"))
    assert schema_refuses(lambda e: e.update(spec_revision="other"))
    assert schema_refuses(lambda e: e["vocabulary"]["constants"].pop("alice"))
    assert schema_refuses(lambda e: e.update(extra={}))
    assert schema_refuses(lambda e: e["vocabulary"].update(extra={}))
    assert schema_refuses(lambda e: e["vocabulary"]["sorts"]["joke"].update(extra="x"))
    assert schema_refuses(lambda e: e["vocabulary"]["predicates"]["sense__funny_1"].pop("arguments"))
    # within the schema, an environment other than the one the identities name: the relay's binding
    mutant = deepcopy(genuine)
    mutant["result"]["projection"]["environment"]["vocabulary"]["sorts"]["joke"]["description"] = "B."
    assert not schema_refuses(lambda e: e["vocabulary"]["sorts"]["joke"].update(description="B."))
    assert route._projection_problem(mutant, case, env, route._dictionary([PACK], [])[0]) \
        == "the projected lexicon does not name the projected environment"


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


# sn-b6b (a): the preamble lines of a source answer, Lean's `writtenLines`, bound to the request's source.
ODD = "In this document, odd means strange."


def test_the_preamble_lines_are_the_sources_leading_sentences(joke):
    """Each line is a sentence of the source as written, in order, and there are as many as the sentences before the
    body; a source without a preamble has none."""
    source = LINE2 + "\n\n" + ODD + "  " + FUNNY
    reading = read_in(joke, source)["reading"]
    assert reading["preamble"] == [LINE2, ODD] and reading["units"][0]["sentence"] == 2
    assert read_in(joke, FUNNY)["reading"]["preamble"] == []


@pytest.mark.parametrize("change", [
    lambda lines: lines.__setitem__(0, "In this document, funny means amusing."),  # a line not in the source
    lambda lines: lines.pop(),                                                       # a line dropped
    lambda lines: lines.append(FUNNY),                                               # an extra line, the body's
    lambda lines: lines.append(lines[0]),                                            # a line repeated
    lambda lines: lines.reverse(),                                                   # out of order
    lambda lines: lines.__setitem__(1, ODD[:-1]),                                    # shifted: not a whole sentence
    lambda lines: lines.__setitem__(0, ""),                                          # emptied
    lambda lines: lines.clear(),                                                     # emptied list
], ids=["absent", "dropped", "extra", "repeated", "reordered", "shifted", "empty-line", "empty"])
def test_preamble_rebinding_is_refused(joke, change):
    source = LINE2 + "\n" + ODD + " " + FUNNY
    genuine = read_in(joke, source)
    def problem(result):
        return route._response_problem(result, genuine["dictionary_id"], genuine["request_id"], source=source)
    assert problem(genuine) is None
    mutant = deepcopy(genuine)
    change(mutant["reading"]["preamble"])
    assert problem(mutant) and "preamble" in problem(mutant)


def test_a_preamble_line_lean_did_not_read_is_unavailable(joke, monkeypatch):
    """Through the route: an answer whose preamble line is not in the request's source is CheckerUnavailable."""
    from ve.backends import lean as lean_backend
    real = lean_backend.run_limited
    def changed(*args, **kwargs):
        answer = real(*args, **kwargs)
        rows = json.loads(answer.stdout)
        rows[0]["result"]["reading"]["preamble"] = ["In this document, funny means amusing."]
        answer.stdout = json.dumps(rows).encode()
        return answer
    monkeypatch.setattr(lean_backend, "run_limited", changed)
    with pytest.raises(CheckerUnavailable, match="preamble line"):
        read_in(joke, LINE2 + " " + FUNNY)


# sn-b6b (d): the flip models of each open unit (VE.Senses.flipsOf; plan 2.6 step 7, spec 2.6).
def flip(sentence, first, second, status, true=None, values=None):
    row = {"sentence": sentence, "first": first, "second": second, "status": status}
    return row if true is None else {**row, "true": true, "values": values}


@pytest.mark.parametrize("source, flips", [
    (FUNNY, [flip(0, 0, 1, "distinguished", ["sense__funny_1"], [True, False])]),
    ("The riddle is not funny.", [flip(0, 0, 1, "distinguished", ["sense__funny_1"], [False, True])]),
    ("Every joke is funny.", [flip(0, 0, 1, "distinguished", ["sense__funny_1"], [True, False])]),
    # the two senses only under a conjunct both make false: no valuation of the rule separates them
    ("Both the riddle is funny and the riddle is odd.", [flip(0, 0, 1, "undistinguished")]),
    (LINE2 + " " + FUNNY, []),         # resolved by its line: no pair
    ("The riddle is odd.", []),        # one candidate: no pair
    (FUNNY + " " + FUNNY, [flip(0, 0, 1, "distinguished", ["sense__funny_1"], [True, False]),
                           flip(1, 0, 1, "distinguished", ["sense__funny_1"], [True, False])]),
], ids=["positive", "negated", "universal", "undistinguished", "resolved", "one-candidate", "two-units"])
def test_flip_models_are_leans(joke, source, flips):
    assert read_in(joke, source)["reading"]["flips"] == flips


@pytest.mark.parametrize("change", [
    lambda flips: flips.pop(),                                         # a pair without its row
    lambda flips: flips.append(deepcopy(flips[0])),                    # a row repeated
    lambda flips: flips[1].update(sentence=flips[1]["sentence"] + 1),  # shifted to another unit
    lambda flips: flips[0].update(first=1, second=0),                  # the pair reversed
    lambda flips: flips[0].update(second=2),                           # a candidate the unit does not have
    lambda flips: flips[0].update(first=False),                        # a Boolean for a number
    lambda flips: flips[0].update(true=["absent"]),                    # a predicate the projection lacks
    lambda flips: flips[0].update(true=[]),                            # no sense made true
    lambda flips: flips[0].update(values=[True, False, True]),         # a third value
    lambda flips: flips[0].update(values=[1, 0]),                      # numbers for Booleans
    lambda flips: flips[0].update(status="BOGUS"),                     # an unknown status
    lambda flips: flips[0].update(status="unknown"),                   # a status without its members' shape
    lambda flips: flips[0].pop("values"),                              # a member dropped
    lambda flips: flips.clear(),                                       # emptied
], ids=["dropped", "repeated", "shifted", "reversed", "absent-candidate", "bool", "absent-predicate", "no-true",
        "three-values", "int-values", "bogus-status", "status-shape", "no-values", "empty"])
def test_flip_rebinding_is_refused(joke, change):
    source = FUNNY + " " + FUNNY
    genuine = read_in(joke, source)
    def problem(result):
        return route._response_problem(result, genuine["dictionary_id"], genuine["request_id"], source=source)
    assert problem(genuine) is None
    mutant = deepcopy(genuine)
    change(mutant["reading"]["flips"])
    assert problem(mutant) and "flip model" in problem(mutant)
