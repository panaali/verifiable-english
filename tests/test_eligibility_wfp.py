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
KEY_DIGEST = "a994884704126935b51fb63178e6516922ef738981e24e0c3eafdcc2ff89e8b6"
REVIEW_PROFILES = {"B15", "B16", "B17", "B18", "B19"}  # added by the eligibility review
RECHECK_PROFILES = {"B20", "B21", "B22", "B23", "C25", "C26", "C27"}  # added by the eligibility recheck


def _digest(keys):
    return sha256(json.dumps(keys, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def keyed_cases():
    return json.loads((HERE / "cases.json").read_text(encoding="utf-8"))


def recorded():
    return json.loads((HERE / "results.json").read_text(encoding="utf-8"))


def test_key_is_frozen():
    keys = [[c["id"], c["key"]] for c in keyed_cases()["cases"]]
    assert _digest(keys) == KEY_DIGEST
    assert len(keys) == 69 and sum(k["entitled"] for _, k in keys) == 54
    # The recheck added B20 to B23 and C25 to C27 only; the other 62 keep the review's pin,
    # and the review added B15 to B19 only, so the first 57 keep the first run's pin.
    before_recheck = [k for k in keys if k[0] not in RECHECK_PROFILES]
    assert _digest(before_recheck) == "fd00bc1c3d03989750dc411c4a7b916372bc2e41a6ca49c744e28e78099ba857"
    before = [k for k in before_recheck if k[0] not in REVIEW_PROFILES]
    assert _digest(before) == "90626e32dda2b34a96a87a0399e6fa6b69bf057614346b07649f050f9cb66197"


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
    assert len(rows) == 69


def test_independent_reference_agrees_with_the_key():
    data = keyed_cases()
    for case in data["cases"]:
        assert reference.answer(case, data["defaults"]) == case["key"], case["id"]


def _unordered_move(p):
    """The first run's reading of reg. 4(4), without the order "having been ... becomes"."""
    return (reference.resident_in_qw(p) and p["scot_ni_from"] is not None
            and p["scot_ni_from"] <= reference.QW_END)


def _move_without_week_bound(p):
    """Reg. 4(4) ordered after the start of E&W residence but not after a day of the week."""
    return (reference.resident_in_qw(p) and p["scot_ni_from"] is not None
            and p["ew_from"] <= p["scot_ni_from"] <= reference.QW_END)


def _move_without_residence_bound(p):
    """Reg. 4(4) ordered after the start of the week but not after the start of E&W residence."""
    return (reference.resident_in_qw(p) and p["scot_ni_from"] is not None
            and reference.QW_START <= p["scot_ni_from"] <= reference.QW_END)


def _both_out_of_care(p, other):
    """The first run's reading of reg. 1(4)(b), with the care condition on both persons."""
    return other is not None and not reference.in_residential_care(p) and not reference.in_residential_care(other)


def _care_without_end(p):
    """The translation's reading before the recheck: a care stay's end date is ignored."""
    return p["care"] is not None and (reference.QW_START - p["care"]["from"]).days >= 84


def _care_end_strict(p):
    """R5 with the end bound strict: a stay whose last day is QW1 would not count."""
    until = p["care"] and p["care"].get("until")
    return _care_without_end(p) and (until is None or until > reference.QW_END)


@pytest.mark.parametrize("name, old, profiles", [
    ("excluded_move", _unordered_move, {"B15", "B16", "B19"}),
    ("excluded_move", _move_without_week_bound, {"B16"}),
    ("excluded_move", _move_without_residence_bound, {"B19"}),
    ("lives_with", _both_out_of_care, {"B17", "B18"}),
    ("in_residential_care", _care_without_end, {"B20", "B21", "B22", "B23", "C25", "C27"}),
    ("in_residential_care", _care_end_strict, {"C26"}),
])
def test_review_profiles_decide_the_corrected_readings(name, old, profiles, monkeypatch):
    """Eligibility review findings A (R11 order, AR6) and B (R6 condition on the subject
    only), and the recheck's care end date (R5 "throughout the qualifying week"): each
    old or partial reading changes exactly the profiles added for it, and no earlier
    profile, which is why the earlier runs missed them."""
    monkeypatch.setattr(reference, name, old)
    data = keyed_cases()
    changed = {c["id"] for c in data["cases"] if reference.answer(c, data["defaults"]) != c["key"]}
    assert changed == profiles


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


def test_review_examples_get_the_source_answer(staged_runs):
    """Eligibility review: A, resident in Scotland from 2026-09-20 and in England from
    2026-09-22 was a certified NO; B, the shared-care profile was 200 instead of 100."""
    assert staged_runs["B15"][0]["staged"] == {"Q1": "YES", "Q2": "200.00", "Q3": "NO", "Q4": "200.00"}
    assert staged_runs["B17"][0]["staged"] == {"Q1": "YES", "Q2": "100.00", "Q3": "NO", "Q4": "100.00"}
    assert staged_runs["B18"][0]["staged"]["Q1"] == "NO"
    for role in T.ROLES:  # R6 conditions only its subject; R11 orders the move after an E&W day
        r6, r11 = (next(r for r in T.rules() if r["id"] == f"{rid}.{role}") for rid in ("R6", "R11"))
        assert T.key(T.U("in_residential_care", T.OTHER[role])) not in T.key(r6["formula"])
        for bound in (T.num(role, "ew_from"), T.day(T.QW0)):
            assert T.key(["date_no_later", bound, T.num(role, "scot_ni_from")]) in T.key(r11["formula"])


@pytest.mark.skipif(not LEAN.exists(), reason="build the Lean ve_quantity runner first")
def test_lean_admits_every_answer_and_replays_every_step(staged_runs):
    raw = T.environment()
    cases = []
    for pid, (result, staged) in staged_runs.items():
        for question, target in run.answer_targets(result["staged"]).items():
            cases.append({"id": f"{pid}/{question}", "kind": "document", "environment": raw,
                          "document": staged.document(target)})
    got = run.lean(cases)
    assert len(got) == 206
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
    assert s["strict"] == 62 and s["total"] == "206/206" and s["answered"] == 206
    assert s["per_question"] == {"Q1": "62/62", "Q2": "48/48", "Q3": "48/48", "Q4": "48/48"}
    assert s["disagreements"] == [] and s["open"] == []
    assert s["single_shot"] == {"answered": 0, "profiles": 62}
    assert s["mutants_killed"] == "23/23"
    lean = s["lean"]
    assert lean["certificates"] == lean["certificates_accepted"] > 0
    assert lean["documents"] == lean["documents_admitted"] == 206
    assert lean["model_premises"] == lean["model_premises_true"] > 0
    assert results["b1_certified"] is True
    assert results["environment_id"] == Environment(T.environment()).environment_id
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    assert "206/206" in readme and "62/62" in readme
    assert (HERE / "RESULTS.md").read_text(encoding="utf-8") == run.results_markdown(
        results, {c["id"]: c for c in keyed_cases()["cases"]})
