"""RD-7: the superposed service owns verdicts, dependency replay and the complete English plan."""
from copy import deepcopy
import json

import pytest

from ve.errors import CheckerUnavailable
from ve.readings_verdicts import BUDGET, _check_sup_answer


def example(tmp_path):
    from tests.test_readings_s2_document import DF, HELP_X, S, s2_document, _wording
    return _wording(s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X)]))


def test_sup_service_all_some_none_and_english(tmp_path):
    from tests.test_readings_s2_document import every
    doc, route, wording = example(tmp_path)
    assert route.route == "superposed"
    all_result = route.entailment(every("help_required"))
    assert all_result["verdict"] == "ALL" and all_result["evidence"] == "certificate"
    with pytest.raises(CheckerUnavailable, match="displayed conclusion"):
        wording.query(every("help_required", negated=True), all_result)
    some = route.entailment(every("avoid_required"))
    assert some["verdict"] == "SOME"
    assert some["proof"]["choice"] == [["rs1", 0]]
    assert some["countermodel"]["choice"] == [["rs1", 1]]
    none = route.entailment(every("help_required", negated=True))
    assert none["verdict"] == "NONE" and len(none["countermodels"]) == 2
    for phi in (every("help_required"), every("avoid_required"), every("help_required", negated=True)):
        answer = route.query_answer(phi)
        assert answer["route"] == "superposed"
        assert len(wording.plan(answer, wording.conclusion(phi))) == len(answer["english"])
        _check_sup_answer(answer, route.requests[id(answer)], route)


def test_public_conflict_keeps_service_envelope_private(tmp_path):
    _, route, _ = example(tmp_path)
    conflict = route.conflict()
    assert conflict["status"] == "CONFLICT-FREE"
    assert "status_text" in conflict and "route" not in conflict
    report = route.report_fields()
    assert "route" not in report["conflict"]


def test_superposed_scopes_need_only_the_two_answer_roundtrips(tmp_path, monkeypatch):
    from ve import readings_route

    _, route, _ = example(tmp_path)
    original = readings_route.run_lean
    questions = []

    def counted(cases):
        if cases[0]["kind"] == "readings-verdicts":
            questions.append(cases[0]["question"])
        return original(cases)

    monkeypatch.setattr(readings_route, "run_lean", counted)
    answer = route.conflict_answer()
    assert len(answer["scopes"]) > 1
    assert questions == ["conflict", "conflict"]


def test_premise_model_short_circuits_proof_search(tmp_path, monkeypatch):
    _, route, _ = example(tmp_path)
    modelled, proved = set(), set()
    original_model, original_proof = route.model, route._generate_certificate

    def model(A=(), gamma=(), conclusion=None):
        result = original_model(A, gamma, conclusion)
        if result is not None:
            modelled.add(tuple(tuple(x) for x in A))
        return result

    def proof(A=(), gamma=(), conclusion=None):
        proved.add(tuple(tuple(x) for x in A))
        return original_proof(A, gamma, conclusion)

    monkeypatch.setattr(route, "model", model)
    monkeypatch.setattr(route, "_generate_certificate", proof)
    route.premises_answer()
    assert modelled and not modelled & proved


def test_premise_scopes_reuse_lean_proposals_without_extra_verdicts(tmp_path, monkeypatch):
    from ve import readings_route

    _, route, _ = example(tmp_path)
    original = readings_route.run_lean
    questions = []

    def counted(cases):
        if cases[0]["kind"] == "readings-verdicts":
            questions.append(cases[0]["question"])
        return original(cases)

    monkeypatch.setattr(readings_route, "run_lean", counted)
    answer = route.premises_answer()
    assert len(answer["scopes"]) > 1
    assert questions == ["premises", "premises", "premises"]


def test_sup_zero_budget_is_unknown(tmp_path, monkeypatch):
    from tests.test_readings_s2_document import every
    _, route, _ = example(tmp_path)
    monkeypatch.setitem(BUDGET, "max_steps", 0)
    monkeypatch.setitem(BUDGET, "max_models", 0)
    assert route.entailment(every("help_required"))["verdict"] == "UNKNOWN"
    assert route.premises()["status"] == "UNKNOWN"
    assert route.conflict()["status"] == "UNKNOWN"


def paths(value, prefix=()):
    yield prefix, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from paths(child, prefix + (key,))
    elif isinstance(value, list):
        for key, child in enumerate(value):
            yield from paths(child, prefix + (key,))


def changed(value, path, replacement):
    out = deepcopy(value)
    if not path:
        return replacement
    parent = out
    for key in path[:-1]:
        parent = parent[key]
    parent[path[-1]] = replacement
    return out


def test_sup_response_retypes_every_field_and_rebinds_references(tmp_path):
    from tests.test_readings_s2_document import every
    _, route, wording = example(tmp_path)
    route.entailment(every("avoid_required"))
    answer = route.query_answer(every("avoid_required"))
    request = route.requests[id(answer)]
    _check_sup_answer(answer, request, route)
    # Every leaf and container gets every other JSON type, including bool for int.
    mutations = []
    for path, value in paths(answer):
        for replacement in (None, True, 7, 7.5, "unknown-id", [], {}):
            if type(value) is type(replacement):
                continue
            mutations.append((path, replacement))
            out = changed(answer, path, replacement)
            try:
                _check_sup_answer(out, request, route)
            except CheckerUnavailable:
                pass
            else:
                slot = wording.conclusion(every("avoid_required"))
                if path == ("dead_readings",) and value is None and replacement == []:
                    # R8: this typed union is unused by a query; it changes no displayed line.
                    assert wording.plan(out, slot) == wording.plan(answer, slot)
                elif len(path) == 3 and path[0] == "english" and path[-1] in {"result", "model", "label"} and replacement is None:
                    # A typed nullable slot cannot be shown in a frame that needs a result.
                    with pytest.raises(CheckerUnavailable):
                        wording.plan(out, slot)
                elif path[-1:] == ("status_text",) and type(replacement) is str:
                    # A well-typed Lean diagnostic unused by this English plan is not a request identity.
                    assert wording.plan(out, slot) == wording.plan(answer, slot)
                else:
                    pytest.fail(f"accepted retype {path}: {replacement!r}")
    # Two independent leaf faults, retaining both changes in the forged answer.
    leaves = [(path, replacement) for path, replacement in mutations
              if path and path != ("dead_readings",) and not (len(path) == 3 and path[0] == "english" and path[-1] in {"result", "model", "label"}) and not isinstance(dict(paths(answer))[path], (dict, list))]
    unique = list(dict(leaves).items())
    for left, right in zip(unique[::2], unique[1::2]):
        out = changed(changed(answer, *left), *right)
        with pytest.raises(CheckerUnavailable):
            _check_sup_answer(out, request, route)
    for path, value in paths(answer):
        if path and (path[-1] in ("choice", "readings") or path[-1] == "model" and isinstance(value, str)):
            out = changed(answer, path, [["unknown-set", 0]] if isinstance(value, list) else "model@999999")
            with pytest.raises(CheckerUnavailable):
                _check_sup_answer(out, request, route)
    for path, value in paths(answer):
        if path and isinstance(value, str) and value in {R.id for R in route.sets}:
            with pytest.raises(CheckerUnavailable):
                _check_sup_answer(changed(answer, path, "unknown-set"), request, route)
        if path and isinstance(value, str) and value in {l for l, _ in route.labelled}:
            with pytest.raises(CheckerUnavailable):
                _check_sup_answer(changed(answer, path, "unknown-label"), request, route)
    for out in (changed(answer, ("model_proposals",), []),
                changed(answer, ("model_proposals",), answer["model_proposals"] + [answer["model_proposals"][0]]),
                changed(answer, ("scopes", 0, "model_proposals"), []),
                changed(answer, ("scopes", 0, "model_proposals"),
                        answer["scopes"][0]["model_proposals"] + [answer["scopes"][0]["model_proposals"][0]]),
                changed(answer, ("scopes",), []),
                changed(answer, ("scopes",), answer["scopes"] + [answer["scopes"][0]]),
                changed(answer, ("scopes",), answer["scopes"][1:]),
                changed(answer, ("scopes",), answer["scopes"][:1] + answer["scopes"][2:]),
                changed(answer, ("scopes",), list(reversed(answer["scopes"])) )):
        with pytest.raises(CheckerUnavailable):
            _check_sup_answer(out, request, route)


def test_sup_relay_leaves_status_consistency_to_lean(tmp_path):
    from tests.test_readings_s2_document import every
    _, route, _ = example(tmp_path)
    answer = route.query_answer(every("avoid_required"))
    request = route.requests[id(answer)]
    changed_answer = deepcopy(answer)
    proved = next(scope for scope in changed_answer["scopes"] if scope["row"]["query"] == "proved")
    proved["row"]["query"] = "UNKNOWN"
    proved["row"]["evidence"]["certificate"] = False
    # These are well-typed, request-bound semantic claims. The encoder theorem and Lean own their consistency.
    _check_sup_answer(changed_answer, request, route)


def test_python_sup_has_no_fold_or_dependency_replay():
    import ast
    from pathlib import Path
    tree = ast.parse(Path("ve/readings_verdicts.py").read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Superposed")
    names = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
    assert not names & {"_fold", "_dependencies", "_mentions", "_choice_conflicts", "_gated_choice"}
    assert not any(isinstance(n, ast.FunctionDef) and n.name == "_replays" for n in tree.body)


def test_budget_free_nd_verdict_request_keeps_the_enumerated_contract():
    from pathlib import Path
    from ve.backends.lean_service import LeanService

    fixture = Path(__file__).resolve().parents[1] / "tests/data/route-cases.jsonl"
    for line in fixture.read_text().splitlines():
        mode, case = json.loads(line)
        if (mode == "readings-route" and case.get("kind") == "readings-verdicts"
                and "norm-defaults@0" in case["environment"]["profiles"] and "budget" not in case):
            break
    else:
        pytest.fail("the saved enumerated request is missing")
    with LeanService(allow_unlisted_build=True) as lean:
        [answer] = lean.run(mode, [case])
    assert answer["status"] == "ok" and answer["route"] == "enumerated"


def test_superposed_answer_is_stable_when_document_keys_are_reordered(tmp_path):
    from pathlib import Path
    from tests.test_readings_nd_document import fnd1
    from ve.document import load_document
    from ve.readings_verdicts import context

    path = fnd1(tmp_path)
    original = Path(path).read_bytes()
    end = original.index(b"\n---\n", 4)
    meta = json.loads(original[4:end])

    def reversed_keys(value):
        if isinstance(value, dict):
            return {key: reversed_keys(value[key]) for key in reversed(value)}
        if isinstance(value, list):
            return [reversed_keys(item) for item in value]
        return value

    reordered = tmp_path / "reordered.ve.md"
    reordered.write_bytes(b"---\n" + json.dumps(reversed_keys(meta), ensure_ascii=False).encode()
                          + original[end:])
    assert reordered.read_bytes() != original
    left = context(load_document(path))
    right = context(load_document(reordered))
    assert left.route == right.route == "superposed"
    assert left.conflict() == right.conflict()


def test_superposed_scope_count_stays_bounded_above_64_choices():
    from tests.test_readings_nd_lean import case, run
    from tests.test_readings_verdicts_lean import QUERY, fnd3

    raw, document = fnd3()
    [row] = run("ve_readings_route", [case("readings-verdicts", raw, document, question="query",
                                           evidence=[], premises=[], conclusion=QUERY, budget=dict(BUDGET))])
    assert row["status"] == "ok" and row["route"] == "superposed"
    # The 128 compatible choices do not become 128 evidence scopes or model proposals.
    assert len(row["scopes"]) == 1
    assert len(row["model_proposals"]) == 16
    assert row["result"]["verdict"] == "UNKNOWN"


def test_scoped_proposals_reach_checked_choices_after_the_64_choice_prefix():
    from tests.test_readings_nd_lean import case
    from tests.test_readings_verdicts_lean import QUERY, fnd3
    from ve.backends.lean_service import LeanService

    raw, document = fnd3()
    assumed = [["rs_1", 1], ["rs_2", 1]]
    request = case("readings-verdicts", raw, document, question="query", assumed=assumed,
                   evidence=[], premises=[], conclusion=QUERY, budget=dict(BUDGET))
    # The unlisted-build test path lets a seeded Lean mutant reach the assertion.
    with LeanService(allow_unlisted_build=True) as lean:
        [row] = lean.run("readings-route", [request])
    assert row["status"] == "ok" and row["route"] == "superposed"
    assert len(row["model_proposals"]) == 16
    assert all(all(candidate in choice for candidate in assumed) for choice in row["model_proposals"])
    assert row["model_proposals"][0] == assumed + [[f"rs_{k}", 0] for k in range(3, 8)]


def test_superposed_verdicts_keep_the_1024_choice_budget():
    from tests.test_readings_nd_lean import case, run
    from tests.test_readings_verdicts_lean import QUERY
    from tests.test_readings_nd_lean import doc1, env1
    from ve.readings_verdicts import _public_sup_conflict

    raw = env1()
    for n in (10, 11):
        sets, units = [], []
        for k in range(n):
            document, _ = doc1(raw, set_id=f"rs_{k + 1}", unit=f"u{k + 1}", rule=f"must-help-{k + 1}")
            sets.extend(document["reading_sets"])
            units.extend(document["units"])
        document = {"units": units, "reading_sets": sets}
        for question, extra in (("conflict", {}), ("premises", {}),
                                ("query", {"premises": [], "conclusion": QUERY})):
            [row] = run("ve_readings_route", [case("readings-verdicts", raw, document, question=question,
                                                   evidence=[], budget=dict(BUDGET), **extra)])
            assert row["status"] == "ok" and row["route"] == "superposed"
            if n == 11:
                assert row["result"]["reason"] == "ResourceLimit: more than 1024 readings to check"
                if question == "conflict":
                    assert _public_sup_conflict(row["result"]) == {
                        "status": "UNKNOWN", "reason": "ResourceLimit: more than 1024 readings to check"}
            else:
                assert row["result"].get("reason") != "ResourceLimit: more than 1024 readings to check"
            assert row["result"]["verdict" if question == "query" else "status"] == "UNKNOWN"


def test_a_canonical_base_with_a_local_collision_is_not_a_premise_model(tmp_path):
    from tests.test_readings_s2_document import DF, NEVER_AVOID, S, s2_document, _wording
    _, route, _ = _wording(s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]),
                                                ("fixed", "u0", NEVER_AVOID)]))
    witness = route.conflict_answer()
    assert witness["result"]["status"] == "CONFLICT"
    request = route.requests[id(witness)]
    for member, replacement in (("sorts", ["unknown-sort"]), ("target", "unknown-target"),
                                ("tuple", ["unknown-entity"]),
                                ("selected", [["unknown-rule", "selects"]])):
        with pytest.raises(CheckerUnavailable):
            _check_sup_answer(changed(witness, ("result", member), replacement), request, route)
    found = route.model([("rs1", 1)])
    assert found is not None
    bad = deepcopy(found["model"])
    # M3's strict reading: all base and decision tables empty, bit 0, so both strict rules apply.
    bad["relations"] = {name: [] for name in bad["relations"]}
    bad["domains"]["agent"] = ["a"]
    bad["domains"]["user"] = ["u"]
    lower = route.lean("readings-model", assumed=[["rs1", 0]], premises=[], conclusion=None, model=bad)
    assert lower["valid"] is True
    route._pieces([["rs1", 0]])["model"] = {"model": bad}
    answer = route._ask("premises", [["rs1", 0]])
    assert answer["result"]["status"] == "UNKNOWN"
    scope = next(s for s in answer["scopes"] if s["row"]["choice"] == [["rs1", 0]])
    assert scope["row"]["evidence"]["model"] is False


def test_missing_proof_scope_cannot_hide_behind_a_reindexed_model(tmp_path):
    from tests.test_readings_s2_document import every
    _, route, _ = example(tmp_path)
    route.entailment(every("avoid_required"))
    answer = route.query_answer(every("avoid_required"))
    request = route.requests[id(answer)]
    out = deepcopy(answer)
    assert out["scopes"][1]["row"]["query"] == "proved"
    out["scopes"].pop(1)
    for line in out["english"]:
        if line["model"] is not None:
            piece, _, index = line["model"].partition("@")
            assert int(index) > 1
            line["model"] = f"{piece}@{int(index) - 1}"
    with pytest.raises(CheckerUnavailable):
        _check_sup_answer(out, request, route)
