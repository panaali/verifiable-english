"""Winter Fuel Payment use case (usecases/eligibility): VE against a frozen answer key.

The test fails on any mismatch with the key, and on any change to the key, the
translation's generated files, or the answers recorded in results.json.
"""
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "usecases" / "eligibility"
LEAN = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_quantity"
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import run  # noqa: E402
import translation as T  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.entailment import prove_entailment  # noqa: E402
from ve.units import _core_problem  # noqa: E402

# sha256 of the canonical JSON of [[id, key], ...] in cases.json. A key change must
# be its own commit that says why (PLAN.md status note); update this pin there.
KEY_DIGEST = "90626e32dda2b34a96a87a0399e6fa6b69bf057614346b07649f050f9cb66197"


def keyed_cases():
    return json.loads((HERE / "cases.json").read_text(encoding="utf-8"))


def recorded():
    return json.loads((HERE / "results.json").read_text(encoding="utf-8"))


def test_key_is_frozen():
    keys = [[c["id"], c["key"]] for c in keyed_cases()["cases"]]
    assert sha256(json.dumps(keys, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == KEY_DIGEST
    assert len(keys) == 57 and sum(k["entitled"] for _, k in keys) == 44


def test_plan_table_matches_cases_json():
    """PLAN.md section 5 and cases.json state the same key."""
    rows = {}
    for line in (HERE / "PLAN.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and re.fullmatch(r"[A-D][0-9]{2}", cells[0]):
            rows[cells[0]] = cells[2:6]
    money = lambda cell: cell if cell == "—" else f"{int(cell.lstrip('£'))}.00"
    for case in keyed_cases()["cases"]:
        key = case["key"]
        expected = (["YES", key["amount"], "YES" if key["recovered"] else "NO", key["kept"]]
                    if key["entitled"] else ["NO", "—", "—", "—"])
        q1, q2, q3, q4 = rows[case["id"]]
        assert [q1, money(q2), q3, money(q4)] == expected, case["id"]
    assert len(rows) == 57


def test_independent_reference_agrees_with_the_key():
    data = keyed_cases()
    for case in data["cases"]:
        assert reference.answer(case, data["defaults"]) == case["key"], case["id"]


@pytest.mark.parametrize("benefit", sorted(reference.RELEVANT_BENEFITS))
def test_each_relevant_benefit_decides_some_key(benefit, monkeypatch):
    """Plan review finding C: deleting any benefit from the list changes a key."""
    monkeypatch.setattr(reference, "RELEVANT_BENEFITS", reference.RELEVANT_BENEFITS - {benefit})
    data = keyed_cases()
    assert any(reference.answer(c, data["defaults"]) != c["key"] for c in data["cases"])


def test_the_builder_never_reads_a_key():
    stripped = T.load_cases()
    assert all("key" not in c for c in stripped["cases"])
    for case in keyed_cases()["cases"]:
        poisoned = {**case, "key": {"entitled": not case["key"]["entitled"]}}
        assert T.profile_facts(poisoned, stripped["defaults"]) == T.profile_facts(
            {k: v for k, v in case.items() if k != "key"}, stripped["defaults"])
    source = (HERE / "translation.py").read_text(encoding="utf-8")
    assert '["key"]' not in source and "import reference" not in source


def test_generated_files_match_the_translation():
    assert json.loads((HERE / "environment.json").read_text()) == T.environment()
    assert json.loads((HERE / "rules.json").read_text())["rules"] == T.rules()
    Environment(T.environment())  # admitted by the Python early checker


@pytest.fixture(scope="module")
def staged_runs():
    env = Environment(T.environment())
    data = T.load_cases()
    prover = run.Prover(env)
    return {case["id"]: run.run_profile(prover, env, case, data["defaults"]) for case in data["cases"]}


def test_staged_answers_match_the_key_and_the_recorded_results(staged_runs):
    keys = {c["id"]: c["key"] for c in keyed_cases()["cases"]}
    results = {p["id"]: p for p in recorded()["profiles"]}
    for pid, (result, _) in staged_runs.items():
        assert result["staged"] == results[pid]["staged"] == results[pid]["answers"], pid
        scored, _ = run.score(result["staged"], keys[pid])
        assert all(scored.values()), (pid, result["staged"], keys[pid])


@pytest.mark.skipif(not LEAN.exists(), reason="build the Lean ve_quantity runner first")
def test_lean_admits_every_answer_and_replays_every_step(staged_runs):
    raw = T.environment()
    cases = []
    for pid, (result, staged) in staged_runs.items():
        for question, target in run.answer_targets(result["staged"]).items():
            cases.append({"id": f"{pid}/{question}", "kind": "document", "environment": raw,
                          "document": staged.document(target)})
    got = run.lean(cases)
    assert len(got) == 189
    assert all(r["status"] == "ok" and r["assurance"] == "lean-admitted" for r in got), \
        [r for r in got if r.get("status") != "ok"][:3]


@pytest.mark.parametrize("mutant", sorted(T.MUTANTS, key=lambda m: int(m[1:])))
def test_each_mutant_changes_its_profiles(mutant, staged_runs):
    env = Environment(T.environment())
    data = T.load_cases()
    prover = run.Prover(env)
    by_id = {c["id"]: c for c in data["cases"]}
    for pid in run.MUTANT_TARGETS[mutant]:
        result, _ = run.run_profile(prover, env, by_id[pid], data["defaults"], mutant=mutant)
        assert result["staged"] != staged_runs[pid][0]["staged"], (mutant, pid)


def test_single_shot_stops_at_the_tableau_depth_cap():
    """The recorded single-shot OPEN is structural: the search reaches the depth
    cap (MAX_TABLEAU_DEPTH = 124) before any branch closes."""
    env = Environment(T.environment())
    data = T.load_cases()
    case = next(c for c in data["cases"] if c["id"] == "A01")
    premises = [T.q(f["formula"]) for f in T.profile_facts(case, data["defaults"])]
    premises += [T.q(r["formula"]) for r in T.rules()]
    target, _, cores = _core_problem(env, premises, T.q(T.entitled_goal()))
    result = prove_entailment(target, cores[:-1], cores[-1], max_steps=10_000)
    assert result.certificate is None and result.status == "NotFound" and result.steps == 124


def test_recorded_summary():
    results = recorded()
    s = results["summary"]
    assert s["strict"] == 57 and s["total"] == "189/189" and s["answered"] == 189
    assert s["per_question"] == {"Q1": "57/57", "Q2": "44/44", "Q3": "44/44", "Q4": "44/44"}
    assert s["disagreements"] == [] and s["open"] == []
    assert s["single_shot"] == {"answered": 0, "profiles": 57}
    assert s["mutants_killed"] == "19/19"
    lean = s["lean"]
    assert lean["certificates"] == lean["certificates_accepted"] > 0
    assert lean["documents"] == lean["documents_admitted"] == 189
    assert lean["model_premises"] == lean["model_premises_true"] > 0
    assert results["b1_certified"] is True
    assert results["environment_id"] == Environment(T.environment()).environment_id
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    assert "189/189" in readme and "57/57" in readme
    assert (HERE / "RESULTS.md").read_text(encoding="utf-8") == run.results_markdown(
        results, {c["id"]: c for c in keyed_cases()["cases"]})
