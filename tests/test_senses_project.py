"""Senses B6: the `senses.project` mode through the service, and the identities a `senses.read` answer gives its
projection and each candidate's (docs/spec/senses-PLAN.md 2.6, 2.7; fixtures i1, i2, i6, i7)."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy

import pytest

import test_english_e2_boundary as boundary
from test_senses_route import PACK, ROOT, _paths, _retyped, pack_with, read_in, sense, world
from ve.assurance import operation
from ve.backends import lean_service, senses as route
from ve.backends.lean import ROUTE_TIMEOUT
from ve.backends.service_schema import Invalid, check_row
from ve.english_grammar import actions_version, grammar_id, lexicon_id
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.environment import Environment
from ve.errors import CheckerUnavailable, VEError
from ve.senses import bundled_pack
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
        # Lean's version constant is typed, not bound: its lock is sn-b6bb's.
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
    # the environment and lexicon kept, the identity another digest: refused by the environment_id binding
    mutant = deepcopy(genuine)
    mutant["result"]["projection"]["identities"]["environment_id"] = "0" * 64
    assert not _refused(env, genuine, case) and _refused(env, mutant, case)
    assert route._projection_problem(mutant, case, env, route._dictionary([PACK], [])[0]) \
        == "the projection's environment identity is not the returned environment's"


def _core(profiles=("relational-fol@0",)):
    return {"language": LANGUAGE, "spec_revision": SPEC_REVISION, "profiles": list(profiles),
            "vocabulary": {"sorts": {"joke": {"description": "A sort."}}, "predicates": {},
                           "constants": {"riddle": {"sort": "joke", "description": "A constant."}}}}


def _data(path, *keys):
    value = json.loads((ROOT / path).read_text())
    for key in keys:
        value = value[key]
    return value


# One request environment per member a profile adds (`profileMembers`, lean/ResponseShape/Schemas/SensesProject.lean),
# and a document layer's profile list: the corpus families of the review's sweep. rights@0 is refused by
# english.read itself (UnsupportedProfile), before any projection.
FAMILIES = {
    "v0": lambda: world()[0].to_dict(),
    "core": _core,
    "judgments": lambda: _core(["documents@1", "judgments@0", "relational-fol@0"]),
    "acts": lambda: _data("tests/data/acts/environment.json"),
    "reports": lambda: boundary.reports(),
    "speech": lambda: boundary.speech(),
    "readings": lambda: boundary.readings(),
    "soft": lambda: _data("conformance/soft_norms_rust.json", 9, "source", "environment"),
    "alternatives": lambda: _data("tests/data/et7/et1-component.json", "environment"),
    "risk": lambda: _data("usecases/asimov-extended/environment.json"),
    "units": lambda: _data("usecases/news-article/w6a-quantity-fixtures.json", "environment"),
}


def _changed(value):
    return value + "x" if type(value) is str else [*value, "documents@1"] if type(value) is list else \
        {**value, "x": {}} if type(value) is dict else [value]


@pytest.mark.parametrize("family", FAMILIES)
def test_every_member_a_request_environment_carries_is_copied_and_bound(family):
    """F1, F2 (sn-b6b review): whatever member its profiles add, a request environment projects (an answer, not
    CheckerUnavailable); the projection keeps every member but the sorts and predicates as the request's, the
    profile list as written (`judgments@0` kept); and the schema refuses each copied member dropped or changed."""
    env = Environment(FAMILIES[family]())
    result = route.project(env, [], "", [])
    projection = result["projection"]
    assert projection["status"] == "ok", projection
    sent, returned = env.to_dict(), projection["environment"]
    own = {"vocabulary"}, {"sorts", "predicates"}
    assert {k: v for k, v in returned.items() if k not in own[0]} == {k: v for k, v in sent.items() if k not in own[0]}
    assert {k: v for k, v in returned["vocabulary"].items() if k not in own[1]} == \
        {k: v for k, v in sent["vocabulary"].items() if k not in own[1]}
    case = route.request(env, None, [])
    del case["source"]
    case.update(id=route.PROJECT, lines="", used=[])
    row = {"id": route.PROJECT, "status": "ok", "result": result}
    check_row(route.PROJECT, row, case, 0)
    copied = [(k,) for k in returned if k not in own[0]] + [("vocabulary", k) for k in returned["vocabulary"]
                                                             if k not in own[1]]
    for path in copied:
        for change in ("drop", "change"):
            mutant = deepcopy(row)
            parent = mutant["result"]["projection"]["environment"]
            for part in path[:-1]:
                parent = parent[part]
            if change == "drop":
                del parent[path[-1]]
            else:
                parent[path[-1]] = _changed(parent[path[-1]])
            with pytest.raises(Invalid):
                check_row(route.PROJECT, mutant, case, 0)


def test_a_forged_profile_list_with_recomputed_identities_is_refused():
    """F2 (sn-b6b review): a projected environment naming profiles the request does not, its identities recomputed
    so the relay's identity binding holds, is refused by the schema's binding of `profiles` to the request's."""
    env = Environment(_core())
    result = route.project(env, [], "", [])
    case = route.request(env, None, [])
    del case["source"]
    case.update(id=route.PROJECT, lines="", used=[])
    forged = deepcopy(result)
    projection = forged["projection"]
    projection["environment"]["profiles"] = ["documents@1", "relational-fol@0"]
    environment_id = Environment(projection["environment"]).environment_id
    projection["lexicon"]["environment_id"] = projection["identities"]["environment_id"] = environment_id
    projection["identities"]["lexicon_id"] = lexicon_id(projection["lexicon"])
    row = {"id": route.PROJECT, "status": "ok", "result": forged}
    assert route._projection_problem(row, case, env, route._dictionary([], [])[0]) is None  # self-consistent
    with pytest.raises(Invalid, match="profiles"):
        check_row(route.PROJECT, row, case, 0)


@pytest.mark.parametrize("change", [
    lambda e: e.update(language="ve.closure@0"),
    lambda e: e.update(profile="relational-fol@1"),
    lambda e: e.pop("spec_revision"),
    lambda e: e.update(extra={}),
    lambda e: e["vocabulary"]["constants"].pop("alice"),
    lambda e: e["vocabulary"].update(acts={"fixed": []}),
], ids=["language", "profile", "revision-dropped", "extra", "constant-dropped", "block-added"])
def test_a_readings_environment_is_bound_to_the_request(joke, change):
    """F1, F2 for `senses.read`: its reading carries the same projected environment, checked by the same generated
    schema (`check_projected_environment`); a copied member changed, dropped or added is refused before anything
    reads it."""
    env, overlay = joke
    genuine = read_in(joke, FUNNY)
    binding = {"env": env, "source": FUNNY, "words": route._dictionary([PACK], [])[1],
               "case": route.request(env, FUNNY, [PACK.decode()], overlay=overlay)}
    def problem(result):
        return route._response_problem(result, genuine["dictionary_id"], genuine["request_id"], source=FUNNY,
                                       binding=binding)
    assert problem(genuine) is None
    mutant = deepcopy(genuine)
    change(mutant["reading"]["environment"])
    assert problem(mutant).startswith("the projected environment is not the request's")


# The base's texts (3b4e471f8, ve/backends/senses.py:150-154), each read after a possessive: "the reading's the
# grammar identities ...".
BASE_IDENTITY_PROBLEMS = {"grammar_id": "the grammar identities do not match the request",
                          "source_sha256": "the source identity does not match the request",
                          "environment_id": "the environment identity is not the returned environment's"}


@pytest.mark.parametrize("key", BASE_IDENTITY_PROBLEMS)
def test_an_identity_problem_names_its_identity_once(joke, key):
    """F8 (sn-b6b review), R1: an identity problem reads after its possessive with one article, and keeps the
    base text's words: the base's text, its leading `the` dropped."""
    env, overlay = joke
    genuine = read_in(joke, FUNNY)
    binding = {"env": env, "source": FUNNY, "words": route._dictionary([PACK], [])[1],
               "case": route.request(env, FUNNY, [PACK.decode()], overlay=overlay)}
    mutant = deepcopy(genuine)
    mutant["reading"]["identities"][key] = "0" * 64
    assert route._response_problem(mutant, genuine["dictionary_id"], genuine["request_id"], source=FUNNY,
                                   binding=binding) == "the reading's " + BASE_IDENTITY_PROBLEMS[key][len("the "):]


def test_reading_identity_rebinding_is_refused(joke):
    """The identities a reading names are bound to the request: its grammar, S2's actions version, its source, the
    returned environment and the dictionary's words."""
    env, _ = joke
    genuine = read_in(joke, FUNNY)
    binding = {"env": env, "source": FUNNY, "words": route._dictionary([PACK], [])[1],
               "case": route.request(env, FUNNY, [PACK.decode()], overlay=joke[1])}
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



# sn-b6b: `ve senses project` relays Lean's answer verbatim; i4: the review status of a one-pack request.
def cli(tmp_path, capsys, command, env, pack: bytes, *extra):
    from ve.__main__ import main
    (tmp_path / "env.json").write_text(json.dumps(env.to_dict()))
    (tmp_path / "pack.json").write_bytes(pack)
    code = main(["senses", command, "--env", str(tmp_path / "env.json"), "--pack", str(tmp_path / "pack.json"),
                 *extra])
    return code, json.loads(capsys.readouterr().out)


def test_senses_project_cli_relays_leans_answer(tmp_path, capsys):
    """The CLI's answer is the relay's, member for member, with the operation and its assurance; a fault of the
    lines is exit 3 with Lean's fault, a refused request exit 2 with Lean's text."""
    env, _ = world()
    (tmp_path / "lines.txt").write_text(LINE2)
    code, out = cli(tmp_path, capsys, "project", env, PACK, "--used", "funny", "--lines", str(tmp_path / "lines.txt"))
    assert code == 0 and out == {"operation": "senses.project", "assurance": operation("senses.project")["assurance"][
        "current"], **route.project(env, [PACK], LINE2, ["funny"]), "review_status": {"fixtures@1": "unreviewed"}}
    assert out["projection"]["environment"]["vocabulary"]["predicates"]["sense__funny_2"]["verbalisation"] \
        == "{0} is funny"
    (tmp_path / "lines.txt").write_text("In this document, funny means purple.")
    code, out = cli(tmp_path, capsys, "project", env, PACK, "--used", "funny", "--lines", str(tmp_path / "lines.txt"))
    assert code == 3 and out["projection"]["code"] == "UnknownGloss"
    code, out = cli(tmp_path, capsys, "project", env, PACK, "--used", "giggle")
    assert code == 2 and out == {"status": "InvalidInput",
                                 "error": "InvalidInput: used word giggle is not a word of the dictionary"}


def test_i4_a_changed_pack_is_unreviewed_and_reads_the_same(tmp_path, capsys):
    """i4: a reviewed pack shows `reviewed` (Lean's dictionary_id is its pin); one changed byte of a description
    gives `unreviewed` from `ve.senses.review_status`, and the reading's status and formulas are unchanged."""
    from test_senses_packs import PACKS, senses_env
    usecase, source, _ = PACKS["policies@1"]
    env, _ = senses_env(usecase)
    pack = bundled_pack("policies@1")
    changed = pack.replace(b'"description": "', b'"description": "A', 1)
    (tmp_path / "text.txt").write_text(source)
    seen = []
    for bytes_, status in ((pack, "reviewed"), (changed, "unreviewed")):
        code, out = cli(tmp_path, capsys, "check", env, bytes_, str(tmp_path / "text.txt"))
        assert out["review_status"] == {"policies@1": status}
        seen.append((code, out["reading"]["status"], [u.get("formula") for u in out["reading"]["units"]]))
        code, out = cli(tmp_path, capsys, "project", env, bytes_, "--used", "resides")
        assert code == 0 and out["review_status"] == {"policies@1": status}
    assert seen[0] == seen[1] and seen[0][1] == "one"


def test_i5_a_service_killed_mid_request_is_unavailable(joke, monkeypatch):
    """i5: the `ve_service` process killed during every attempt at a `senses.project` request is CheckerUnavailable
    from the relay after its one retry, never an answer; so is the `ve_senses_route` runner killed mid-answer."""
    import os
    kills = []
    write = lean_service.LeanService._write_all
    def kill_then_write(service, line, deadline):
        kills.append(service.pid)
        os.kill(service.pid, 9)
        return write(service, line, deadline)
    with monkeypatch.context() as patch:
        patch.setattr(lean_service.LeanService, "_write_all", kill_then_write)
        with pytest.raises(CheckerUnavailable):
            project(joke)
    assert len(kills) == 2 and kills[0] != kills[1]
    assert project(joke)["projection"]["status"] == "ok"
    from ve.backends import lean as lean_backend
    real = lean_backend.run_limited
    def killed(*args, **kwargs):
        answer = real(*args, **kwargs)
        answer.returncode, answer.stdout = -9, answer.stdout[: len(answer.stdout) // 2]
        return answer
    monkeypatch.setattr(lean_backend, "run_limited", killed)
    with pytest.raises(CheckerUnavailable):
        read_in(joke, FUNNY)
