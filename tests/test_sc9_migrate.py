"""SC-9's migration of the constitution pilot's translation to the soft form (docs/spec/rd-9-soft-chain-PLAN.md SC-9;
`usecases/claude-constitution-pilot/run-20261104T0716Z/migrate_soft.py`): one fixture per rewrite rule, the
u0073.s05 probe's shape (C9), and the committed probe translation and changed units as the script writes them.

The translation is the pinned copy of `tests/ce4.py` (run 20261010T1800Z at 76922d6c, checked against its blob id);
no service, git or network call is made. The measured answers are read from the run's saved evidence.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from tests import ce4

RUN = Path(__file__).resolve().parents[1] / "usecases/claude-constitution-pilot/run-20261104T0716Z"
_spec = importlib.util.spec_from_file_location("sc9_migrate_soft", RUN / "migrate_soft.py")
migrate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migrate)
_status_spec = importlib.util.spec_from_file_location("sc9_status", RUN / "c9_status.py")
c9_status = importlib.util.module_from_spec(_status_spec)
_status_spec.loader.exec_module(c9_status)
DROPPED = (*migrate.EXCEPTIONS, migrate.GENERAL)


@pytest.fixture(scope="module")
def pinned():
    _, front, source = ce4.pinned_bytes().split(b"---\n", 2)
    return json.loads(front), source


@pytest.fixture(scope="module")
def migrated(pinned):
    return migrate.rewrite(pinned[0])


def unit(meta, uid):
    [found] = [u for u in migrate.pilot._flat(meta["units"]) if u["id"] == uid]
    return found


def test_rule1_soft_norms_is_added_once(pinned, migrated):
    before = pinned[0]["environment"]["profiles"]
    after = migrated[0]["environment"]["profiles"]
    assert migrate.SOFT not in before and after == sorted({*before, migrate.SOFT})
    assert migrate.with_soft(migrated[0]["environment"])["profiles"] == after


def test_rule2_each_default_candidate_is_rewritten_as_in_5_2(pinned, migrated):
    """The `default` candidate is the strict rule with `mode: default`, an unstated exception and no `unless`; the
    `strict` candidate and every other field are as written; the situations are left for the search."""
    for old, new in zip(pinned[0]["reading_sets"], migrated[0]["reading_sets"], strict=True):
        assert "situations" in old and "situations" not in new
        strict, default = new["readings"]
        assert strict["content"] == old["readings"][0]["content"]
        rule = default["content"]["norm"]
        assert rule == {**old["readings"][1]["content"]["norm"], "unless": [], "mode": "default",
                        "exception": ce4.UNSTATED}
        assert [r["admission"]["distinguishing_models"] for r in new["readings"]] == [
            {"default": "pending"}, {"strict": "pending"}]
        assert {k: v for k, v in new.items() if k != "readings"} == {
            k: v for k, v in old.items() if k not in ("readings", "situations")}


def test_rule3_u0073_s05_is_one_default_rule_with_three_sufficient_conditions(pinned, migrated):
    """C9: the first three `unless` formulas become the exception's sufficient conditions, in order; the general
    open term is gone; the rule's name, predicate, sign and guard are as written."""
    old = unit(pinned[0], migrate.CONDITIONED)["content"]["norm"]
    new = unit(migrated[0], migrate.CONDITIONED)["content"]["norm"]
    assert old["unless"][3] == ["unary", migrate.GENERAL, ["var", 0]]
    assert new == {**old, "unless": [], "mode": "default",
                   "exception": {"decided_by": "unstated", "sufficient": old["unless"][:3], "necessary": [],
                                 "factors": []}}
    assert [c[1] for c in new["exception"]["sufficient"]] == [
        "compliance_unsafe", "compliance_unethical", "compliance_against_guidelines"]


@pytest.mark.parametrize("edit", ["no general term", "only the general term", "already default"])
def test_rule3_refuses_a_rule_of_another_shape(pinned, edit):
    content = copy.deepcopy(unit(pinned[0], migrate.CONDITIONED)["content"])
    rule = content["norm"]
    if edit == "no general term":
        rule["unless"] = rule["unless"][:3]
    elif edit == "only the general term":
        rule["unless"] = rule["unless"][3:]
    else:
        rule["mode"] = "default"
    with pytest.raises(ValueError):
        migrate.conditioned(content)


def test_rule4_the_five_open_terms_are_dropped_everywhere(pinned, migrated):
    before, after = pinned[0], migrated[0]
    assert {t["name"] for t in before["open_terms"]} - {t["name"] for t in after["open_terms"]} == set(DROPPED)
    assert len(before["open_terms"]) == 33 and len(after["open_terms"]) == 28
    assert not set(DROPPED) & set(after["environment"]["vocabulary"]["predicates"])
    assert not [u["id"] for u in migrate.pilot._flat(after["units"])
                if set(DROPPED) & set((u.get("meaning") or {}).get("open", []) if type(u.get("meaning")) is dict
                                      else [])]
    assert unit(after, migrate.CONDITIONED)["meaning"]["open"] == [
        "compliance_unsafe", "compliance_unethical", "compliance_against_guidelines"]


def test_rule4_refuses_a_term_some_content_still_names(migrated):
    with pytest.raises(ValueError, match="compliance_unsafe"):
        migrate.drop_open_terms(migrated[0], ("compliance_unsafe",))


def test_units_spans_and_source_words_are_unchanged(pinned, migrated):
    migrate.unchanged(pinned[0], migrated[0], pinned[1], pinned[1])
    moved = copy.deepcopy(migrated[0])
    moved["reading_sets"][0]["source_word"] = [w + 1 for w in moved["reading_sets"][0]["source_word"]]
    with pytest.raises(AssertionError):
        migrate.unchanged(pinned[0], moved, pinned[1], pinned[1])


def test_the_committed_probe_is_the_rewrite_with_searched_situations(pinned, migrated):
    """The probe translation is the rewrite, plus what the search and the identities add: one recorded situation
    per set, named by both readings, and a meaning id per candidate; its body is the translation's."""
    probe, body = migrate.pilot.read(migrate.PROBE)
    assert body == pinned[1]
    found = copy.deepcopy(probe)
    for R in found["reading_sets"]:
        [sid] = R.pop("situations")
        for r in R["readings"]:
            assert r.pop("meaning_id") and set(r["admission"]["distinguishing_models"].values()) == {sid}
            r["admission"]["distinguishing_models"] = {o: "pending" for o in r["admission"]["distinguishing_models"]}
    written = copy.deepcopy(migrated[0])
    for R in written["reading_sets"]:
        for r in R["readings"]:
            r.pop("meaning_id")
    assert found == written
    saved = json.loads((RUN / "changed_units.json").read_text())
    assert saved["changed_units"] == migrated[1] == sorted(
        [R["unit"] for R in pinned[0]["reading_sets"]] + [migrate.CONDITIONED])


def test_the_c9_probe_has_three_sufficient_premises_on_every_choice():
    """C9's shape as Lean answered the probe's load (saved): X ≠ [] on every candidate of every set, the three
    `soft:exception:comply-operator-prompt:sufficient:<i>` premises in order; the unit stays OPEN."""
    load = json.loads((RUN / "answers/after/load.out").read_text())
    assert load["route"] == "enumerated" and load["choices"] == 16
    labels = [f"soft:exception:comply-operator-prompt:sufficient:{i}" for i in range(3)]
    assert sorted((e["set"], e["index"]) for e in load["soft_premises"]) == [(s, i) for s in ce4.SETS for i in (0, 1)]
    assert all([p["label"] for p in e["premises"]] == labels for e in load["soft_premises"])
    assert load["units"][migrate.CONDITIONED][0] == "OPEN"


def test_c9_point_status_is_measured_on_every_choice_and_condition(tmp_path):
    """F1: universal entailment UNKNOWN is not a point status. Both readings must save Lean's status on every
    choice, under each sufficient condition and with none, including the two old unsafe query phrasings."""
    from ve.readings_route import run_lean

    probe = migrate.PROBE
    meta, source = migrate.pilot.read(probe)
    strict = tmp_path / "strict.ve.md"
    migrate.pilot.write(strict, c9_status.strict_twin(meta), source)
    scenarios = ["c9-unsafe-required", "c9-unsafe-not-required", "c9-compliance_unethical",
                 "c9-compliance_against_guidelines", "c9-none-required"]
    for document, path in (("after", probe), ("strict", strict)):
        cases, labels = c9_status.point_status_cases(path)
        saved = json.loads((RUN / "answers" / document / "point-status-c9.out").read_text())["cases"]
        assert len(cases) == len(labels) == len(saved) == 16 * len(scenarios)
        assert labels == scenarios * 16
        assert len({tuple(map(tuple, case["choice"])) for case in cases}) == 16
        for i, (case, label, record) in enumerate(zip(cases, labels, saved, strict=True)):
            assert record["scenario"] == label
            assert record["choice"] == case["choice"]
            assert record["inner_request"] == case["inner"]
            answer = record["answer"]
            assert answer["id"] == case["id"] and answer["status"] == "ok"
            assert answer["inner"]["status"] == "ok"
            expected = ("UNDECIDED" if document == "after" and label != "c9-none-required"
                        else "SETTLED yes")
            assert answer["inner"]["point_status"] == expected, (document, i, answer)
            relations = case["inner"]["model"]["relations"]
            condition = next((p for p in ("compliance_unsafe", "compliance_unethical",
                                           "compliance_against_guidelines") if relations[p]), None)
            assert condition == (["compliance_unsafe", "compliance_unsafe", "compliance_unethical",
                                  "compliance_against_guidelines", None][i % len(scenarios)])
            c9_table = relations.get("soft__excepted__comply_operator_prompt")
            expected_table = ([] if condition is None else [["c", "s"]]) if document == "after" else None
            assert c9_table == expected_table
        assert run_lean(cases[:len(scenarios)]) == [record["answer"] for record in saved[:len(scenarios)]]


def test_each_candidate_id_is_the_loaders_binding_of_its_content():
    """DRI decision sc-9 item 2 (deviation D1): every candidate's `meaning_id` in the probe is
    `s1_content_meaning_id` of its content, and the saved record holds that id and Lean's unit id for all eight."""
    from ve.document import _environment
    from ve.readings import s1_content_meaning_id
    probe, _ = migrate.pilot.read(migrate.PROBE)
    env = _environment(probe["environment"])
    saved = json.loads((RUN / "answers/meaning-ids.json").read_text())
    ids = {f"{R['id']}:{r['id']}": r["meaning_id"] for R in probe["reading_sets"] for r in R["readings"]}
    assert len(ids) == 8 and set(saved) == set(ids)
    for R in probe["reading_sets"]:
        for r in R["readings"]:
            assert r["meaning_id"] == s1_content_meaning_id(env, R["id"], r) == saved[f"{R['id']}:{r['id']}"]["candidate"]
    assert all(type(v["lean_unit"]) is str and len(v["lean_unit"]) == 64 for v in saved.values())


def test_the_comprehension_lines_are_the_renderers(tmp_path):
    """DRI decision sc-9 item 1: C10 is NOT RUN; its four lines are the probe's rendered lines byte for byte, as this
    branch's renderer produces them, each with spec 2.6's question and no answer."""
    from tests import lean_routes
    from ve.document import render_document
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    saved = json.loads((RUN / "comprehension/questions.json").read_text())
    assert saved["status"].startswith("NOT RUN") and all(row["answer"] is None for row in saved["rows"])
    assert [(row["case"], row["kind"]) for row in saved["rows"]] == [
        ("C1", "permission"), ("C2", "obligation"), ("C3", "permission"), ("C4", "obligation")]
    lines = render_document(migrate.PROBE).splitlines()
    for row in saved["rows"]:
        assert lines[row["line"] - 1] == row["rendered"], row["case"]
        assert row["question"].startswith("Does the text say that " +
                                          ("c may " if row["kind"] == "permission" else "c need not "))
