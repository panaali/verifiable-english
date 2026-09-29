"""Winter Fuel Payment use case (usecases/eligibility): VE against a frozen answer key.

The test fails on any mismatch with the key, and on any change to the key, the
translation's generated files, or the answers recorded in results.json.
"""
from datetime import date, timedelta
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "usecases" / "eligibility"
LEAN = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_quantity"
RUST = ROOT / "rust" / "target" / "release" / "ve"
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import run  # noqa: E402
import translation as T  # noqa: E402
from ve import ast  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.entailment import prove_entailment  # noqa: E402
from ve.evaluate import evaluate  # noqa: E402
from ve.model import FiniteModel  # noqa: E402
from ve.units import _core_problem, elaborate_quantity, erased_environment  # noqa: E402

# sha256 of the canonical JSON of [[id, key], ...] in cases.json. A key change must
# be its own commit that says why (PLAN.md status note); update this pin there.
KEY_DIGEST = "2397c7f792e3e29364d5a4cab46a036cef694bcb8a1dddf75460dac7dec37fec"
REVIEW_PROFILES = {"B15", "B16", "B17", "B18", "B19"}  # added by the eligibility review
RECHECK_PROFILES = {"B20", "B21", "B22", "B23", "C25", "C26", "C27"}  # added by the eligibility recheck
FINDING_C_PROFILES = {"B24", "B25", "B26", "B27", "B28", "B29", "B30"}  # review finding C, R7 "throughout"


def _digest(keys):
    return sha256(json.dumps(keys, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def keyed_cases():
    return json.loads((HERE / "cases.json").read_text(encoding="utf-8"))


def recorded():
    return json.loads((HERE / "results.json").read_text(encoding="utf-8"))


def test_key_is_frozen():
    keys = [[c["id"], c["key"]] for c in keyed_cases()["cases"]]
    assert _digest(keys) == KEY_DIGEST
    assert len(keys) == 76 and sum(k["entitled"] for _, k in keys) == 59
    # Finding C added B24 to B30 only; the other 69 keep the recheck's pin. The recheck
    # added B20 to B23 and C25 to C27 only; the other 62 keep the review's pin, and the
    # review added B15 to B19 only, so the first 57 keep the first run's pin.
    before_c = [k for k in keys if k[0] not in FINDING_C_PROFILES]
    assert _digest(before_c) == "a994884704126935b51fb63178e6516922ef738981e24e0c3eafdcc2ff89e8b6"
    before_recheck = [k for k in before_c if k[0] not in RECHECK_PROFILES]
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
    assert len(rows) == 76


def test_plan_and_readme_counts_match_cases_json():
    """Eligibility R7 recheck: PLAN.md section 3 still said 54 entitled and 15
    not-entitled after B24 to B30 were added (59 and 17). The class: a count in the
    prose that no test derives from cases.json. Each stated count is checked here."""
    cases = keyed_cases()["cases"]
    n, entitled = len(cases), sum(c["key"]["entitled"] for c in cases)
    plan = " ".join((HERE / "PLAN.md").read_text(encoding="utf-8").split())
    readme = " ".join((HERE / "README.md").read_text(encoding="utf-8").split())
    stated = lambda pattern, text=plan: [int(x) for x in re.search(pattern, text).groups()]
    assert stated(r"The profiles contain (\d+) entitled and (\d+) not-entitled cases") == [entitled, n - entitled]
    assert stated(r"That gives (\d+) \+ (\d+) \+ (\d+) \+ (\d+) = \*\*(\d+) scored questions\*\*") == \
        [n, entitled, entitled, entitled, n + 3 * entitled]
    groups = [sum(c["id"][0] == g for c in cases) for g in "ABCD"]
    assert stated(r"There are (\d+): (\d+) in group A .*?, (\d+) in group B .*?, (\d+) in group C .*? and (\d+) in group D") \
        == [n, *groups]
    flagged = sum(bool(c.get("flags")) for c in cases)
    assert stated(r"(\d+) profiles carry a flag in `cases.json`, so (\d+) are unflagged") == [flagged, n - flagged]
    basis = {}
    for line in (HERE / "PLAN.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and re.fullmatch(r"[A-D][0-9]{2}", cells[0]):
            basis[cells[-1].split()[0]] = basis.get(cells[-1].split()[0], 0) + 1  # B01: "guide (...)"
    assert stated(r"(\d+) are `guide` cases, (\d+) are `SI` cases and (\d+) are `SI≠guide` cases") == \
        [basis.get("guide", 0), basis.get("SI", 0), basis.get("SI≠guide", 0)]
    assert stated(r"published benefit rule on (\d+) applicant profiles") == [n]
    assert stated(r"Kill rate = mutants killed / (\d+); (\d+)/(\d+) is expected") == [len(T.MUTANTS)] * 3
    assert stated(r"\*\*Cases\.\*\* (\d+) applicant profiles", readme) == [n]
    assert stated(r"agrees with the key on all (\d+)\.", readme) == [n]
    assert stated(r"That makes (\d+) scored questions", readme) == [n + 3 * entitled]


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


def _partner_benefit(home=True, partnership=True, covers=reference.throughout):
    """Reg. 4(2)(a) with the whole-week test on the home or the partnership dropped, or
    with another test of a period covering the week."""
    def excluded(p, other, household):
        return (other is not None and household["partner"]
                and (not partnership or covers(household["partnership"]))
                and reference.lives_with(p, other) and (not home or covers(household["shared_home"]))
                and reference.reached_pensionable_age(other) and reference.relevant_benefit(other))
    return excluded


def _strict(first=False, last=False):
    """A period covers the week only if it began before QW0 (first) or ended after QW1 (last)."""
    def covers(period):
        period = period or {}
        start, end = period.get("from"), period.get("until")
        return ((start is None or (start < reference.QW_START if first else start <= reference.QW_START))
                and (end is None or (end > reference.QW_END if last else end >= reference.QW_END)))
    return covers


_amount = reference.amount


def _amount_throughout_3_3(p, other):
    """Reg. 3(3) read as "throughout the qualifying week" instead of "in that week"."""
    got = _amount(p, other)
    if got == Decimal("300.00") and other is not None and not reference.reached_80(p) and not (
            reference.throughout(other["shared_home"]) and reference.throughout(other["partnership"])):
        return Decimal("200.00")
    return got


@pytest.mark.parametrize("name, old, profiles", [
    ("excluded_move", _unordered_move, {"B15", "B16", "B19"}),
    ("excluded_move", _move_without_week_bound, {"B16"}),
    ("excluded_move", _move_without_residence_bound, {"B19"}),
    ("lives_with", _both_out_of_care, {"B17", "B18"}),
    ("in_residential_care", _care_without_end, {"B20", "B21", "B22", "B23", "C25", "C27"}),
    ("in_residential_care", _care_end_strict, {"C26"}),
    ("excluded_partner_benefit", _partner_benefit(home=False), {"B24", "B25"}),
    ("excluded_partner_benefit", _partner_benefit(partnership=False), {"B26", "B27"}),
    ("excluded_partner_benefit", _partner_benefit(home=False, partnership=False), {"B24", "B25", "B26", "B27"}),
    ("excluded_partner_benefit", _partner_benefit(covers=_strict(first=True)), {"B28"}),
    ("excluded_partner_benefit", _partner_benefit(covers=_strict(last=True)), {"B29"}),
    ("amount", _amount_throughout_3_3, {"B30"}),
])
def test_review_profiles_decide_the_corrected_readings(name, old, profiles, monkeypatch):
    """Eligibility review findings A (R11 order, AR6), B (R6 condition on the subject
    only) and C (R7 "throughout the qualifying week", AR7, and 3(3) "in that week"), and
    the recheck's care end date (R5 "throughout the qualifying week"): each
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


def _perturbed(value):
    """A different value of the same kind: a flipped bool, the next day, one penny more,
    or the benefit list with Pension Credit toggled."""
    if isinstance(value, bool):
        return not value
    if isinstance(value, list):
        return sorted(set(value) ^ {"pension_credit"})
    try:
        return (date.fromisoformat(value) + timedelta(days=1)).isoformat()
    except ValueError:
        return str(Decimal(value) + Decimal("0.01"))


def _field_paths(p):
    for name, value in p.items():
        if isinstance(value, dict):
            yield from ((name, sub) for sub in value)
        elif value is not None and name not in ("birth", *T.UNREAD_FIELDS):  # birth indexes the bridge tables
            yield (name,)


def test_every_profile_field_reaches_a_fact():
    """Eligibility recheck: role_facts dropped `care.until`, so a stay that ended before
    the week still counted as residential care. The class: a profile field that no fact
    carries. Changing any present field of any person must change the facts. The last
    profile is synthetic: a claim date beside an automatic payment."""
    data = T.load_cases()
    extra = {"id": "X", "applicant": {"birth": "1955-03-14", "claim": {"automatic": True, "claimed_on": "2026-10-01"}},
             "housemate": None}
    checked = set()
    for case in data["cases"] + [extra]:
        base = T.profile_facts(case, data["defaults"])
        for role in T.ROLES:
            if case[role] is None:
                continue
            p = {**data["defaults"], **case[role]}
            for path in _field_paths(p):
                changed = json.loads(json.dumps(p))
                if len(path) == 1:
                    changed[path[0]] = _perturbed(p[path[0]])
                    if path == ("partner",) and not changed["partner"]:
                        changed.pop("partnership", None)  # partnership dates need a partner
                else:
                    changed[path[0]][path[1]] = _perturbed(p[path[0]][path[1]])
                assert T.profile_facts({**case, role: changed}, data["defaults"]) != base, (case["id"], role, path)
                checked.add(path)
    assert ("care", "until") in checked and ("claim", "claimed_on") in checked and ("partner",) in checked
    assert {(name, end) for name in T.PERIODS for end in ("from", "until")} <= checked


@pytest.mark.parametrize("role, change", [
    ("applicant", {"care": {"from": "2025-01-10", "to": "2026-09-24"}}),  # misspelt end date
    ("applicant", {"care": {"until": "2026-09-24"}}),
    ("applicant", {"partner": True}),  # the couple is recorded on the housemate
    ("applicant", {"benefits": ["pension-credit"]}),
    ("applicant", {"hospital": {"admitted": "2025-01-10", "discharged": "2026-10-01", "ward": "7"}}),
    ("housemate", {"moved_in": "2026-09-22"}),
    ("applicant", {"shared_home": {"from": "2026-09-23"}}),  # the household is recorded on the housemate
    ("housemate", {"shared_home": {"since": "2026-09-23"}}),
    ("housemate", {"partnership": {"from": "2026-09-23"}}),  # partnership dates without a partner
    ("housemate", {"shared_home": {"from": "2026-09-28"}}),  # AR5: no day of the week
    ("housemate", {"shared_home": {"until": "2026-09-20"}}),
    ("housemate", {"shared_home": {"from": "2026-09-25", "until": "2026-09-23"}}),
])
def test_an_unread_profile_field_is_rejected(role, change):
    """The same class from the other side: a field or benefit name that no fact would
    carry is an error in the translation and in the independent reference, not a
    silent default. So is a household period that includes no day of the week (AR5)."""
    data = T.load_cases()
    case = {"id": "X", "applicant": {"birth": "1955-03-14"}, "housemate": {"birth": "1957-11-02", "partner": False}}
    case[role] = {**case[role], **change}
    with pytest.raises(ValueError):
        T.profile_facts(case, data["defaults"])
    with pytest.raises(ValueError):
        reference.answer(case, data["defaults"])


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


def test_recheck_examples_get_the_source_answer(staged_runs):
    """Eligibility recheck: care from 2026-06-29 to 2026-09-26 (or to 2026-09-20) was a
    Lean-certified 100.00; the source's whole-week condition gives 200.00. Ending the stay
    on QW1 itself still counts. The other four take each path residential care feeds."""
    answer = lambda amount: {"Q1": "YES", "Q2": amount, "Q3": "NO", "Q4": amount}
    expected = {"C25": answer("200.00"), "C27": answer("200.00"), "C26": answer("100.00"),
                "B20": answer("200.00"), "B21": answer("300.00"), "B22": answer("100.00"),
                "B23": {"Q1": "NO", "Q2": "N/A", "Q3": "N/A", "Q4": "N/A"}}
    assert {pid: staged_runs[pid][0]["staged"] for pid in expected} == expected
    for role in T.ROLES:  # R5 bounds the stay's end by QW1, on either role
        r5 = next(r for r in T.rules() if r["id"] == f"R5b.{role}")
        assert T.key(["date_no_later", T.day(T.QW1), T.num(role, "care_until")]) in T.key(r5["formula"])
        assert T.key(T.U("care_ended", role)) in T.key(r5["formula"])


def test_finding_c_examples_get_the_source_answer(staged_runs):
    """Review finding C: R7 dropped "throughout the qualifying week". A shared home or a
    partnership that starts or ends inside QW no longer excludes (B24 to B27); one that
    starts on QW0 or ends on QW1 still does (AR7, B28, B29). Reg. 3(3) says "in that week",
    so a partner aged 80 who moves in during QW still gives 300.00 (B30)."""
    answer = lambda amount: {"Q1": "YES", "Q2": amount, "Q3": "NO", "Q4": amount}
    no = {"Q1": "NO", "Q2": "N/A", "Q3": "N/A", "Q4": "N/A"}
    expected = {"B24": answer("100.00"), "B25": answer("100.00"), "B26": answer("100.00"),
                "B27": answer("100.00"), "B28": no, "B29": no, "B30": answer("300.00")}
    assert {pid: staged_runs[pid][0]["staged"] for pid in expected} == expected
    for role in T.ROLES:
        o = T.OTHER[role]
        by_id = {r["rule"]: r for r in T.rules() if r["role"] == role}
        r7 = T.key(by_id["R7"]["formula"])
        assert T.key(T.B("partners_throughout", role, o)) in r7 and T.key(T.B("home_throughout", role, o)) in r7
        assert T.key(T.B("partner_of", role, o)) not in r7
        for rid, (started, ended, start, end) in zip(("R7a", "R7b"), T.PERIODS.values()):
            text = T.key(by_id[rid]["formula"])
            assert T.key(["date_no_later", T.household(start), T.day(T.QW0)]) in text
            assert T.key(["date_no_later", T.day(T.QW1), T.household(end)]) in text
            assert T.key(T.B(started, role, o)) in text and T.key(T.B(ended, role, o)) in text
    r14_3 = T.key(next(r for r in T.rules() if r["id"] == "R14.3")["formula"])
    assert "throughout" not in r14_3 and T.key(T.B("partner_of", "applicant", "housemate")) in r14_3


def _python_lean_rust(cases_and_expected):
    """Evaluate each (id, quantity, model, expected) in Python, Lean and Rust; all three
    must agree with each other and with the expected value."""
    raw = T.environment()
    env = Environment(raw)
    target = erased_environment(env)
    rows, cases = [], []
    for cid, quantity, model_data, expected in cases_and_expected:
        model = FiniteModel.from_dict(target, model_data)
        _, core = elaborate_quantity(env, quantity)
        python = evaluate(target, ast.formula_from_data(target, core), model, trace=False).value
        rows.append((cid, python, expected))
        cases.append({"id": cid, "environment": raw, "quantity": quantity, "model": model_data})
    lean_values = [r.get("value") for r in run.lean(cases)]
    process = subprocess.run([str(RUST), "conformance", "-"], text=True, capture_output=True, timeout=600,
                             input=json.dumps([{**c, "kind": "quantity"} for c in cases]))
    rust_values = [r.get("value") for r in json.loads(process.stdout)]
    assert [(cid, p) for cid, p, _ in rows] == [(cid, e) for cid, _, e in rows]
    assert lean_values == rust_values == [p for _, p, _ in rows]


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="build Lean ve_quantity and Rust ve first")
def test_whole_week_household_rules_evaluate_alike_in_python_lean_and_rust():
    """R7a, R7b and R7, and the mutants M26 to M29 that drop or tighten "throughout", in
    the reference fixture models of B24 to B29 and of an undated couple (B01). The rules
    are true in every model; each mutant is false in the model of the profile it misreads."""
    data = keyed_cases()
    by_id = {c["id"]: c for c in data["cases"]}
    wrong = {"M26": ({"B24", "B25"}, {"R7"}), "M27": ({"B26", "B27"}, {"R7"}),
             "M28": ({"B28"}, {"R7a", "R7b"}), "M29": ({"B29"}, {"R7a", "R7b"})}
    items = []
    for pid in ("B01", "B24", "B25", "B26", "B27", "B28", "B29"):
        model = run.fixture_model(by_id[pid], data["defaults"])
        for mutant in (None, *wrong):
            for rule in T.role_rules("applicant", mutant):
                if rule["rule"] in ("R7a", "R7b", "R7"):
                    misread = mutant is not None and pid in wrong[mutant][0] and rule["rule"] in wrong[mutant][1]
                    items.append((f"{pid}/{mutant}/{rule['id']}", T.q(rule["formula"]), model, not misread))
    _python_lean_rust(items)


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="build Lean ve_quantity and Rust ve first")
def test_care_end_rule_evaluates_alike_in_python_lean_and_rust():
    """R5b and its mutants M24 (end date ignored) and M25 (end bound strict), evaluated
    in each recheck profile's reference fixture model. Python, Lean and Rust must give
    the same value, the rule must be true, and each mutant false where it misreads."""
    raw = T.environment()
    env = Environment(raw)
    target = erased_environment(env)
    data = keyed_cases()
    by_id = {c["id"]: c for c in data["cases"]}
    roles = {"B20": "applicant", "B21": "applicant", "B22": "housemate", "B23": "applicant",
             "C25": "applicant", "C26": "applicant", "C27": "applicant"}
    rows, cases = [], []
    for pid, role in roles.items():
        model_data = run.fixture_model(by_id[pid], data["defaults"])
        model = FiniteModel.from_dict(target, model_data)
        for mutant in (None, "M24", "M25"):
            [r5] = [r for r in T.role_rules(role, mutant) if r["rule"] == "R5b"]
            quantity = T.q(r5["formula"])
            _, core = elaborate_quantity(env, quantity)
            python = evaluate(target, ast.formula_from_data(target, core), model, trace=False).value
            expected = not (mutant == "M24" and pid != "C26" or mutant == "M25" and pid == "C26")
            rows.append((pid, mutant, python, expected))
            cases.append({"id": f"{pid}/{mutant}", "environment": raw, "quantity": quantity, "model": model_data})
    lean_values = [r.get("value") for r in run.lean(cases)]
    process = subprocess.run([str(RUST), "conformance", "-"], text=True, capture_output=True, timeout=600,
                             input=json.dumps([{**c, "kind": "quantity"} for c in cases]))
    rust_values = [r.get("value") for r in json.loads(process.stdout)]
    assert [(pid, m, p) for pid, m, p, _ in rows] == [(pid, m, e) for pid, m, _, e in rows]
    assert lean_values == rust_values == [p for _, _, p, _ in rows]


@pytest.mark.skipif(not LEAN.exists(), reason="build the Lean ve_quantity runner first")
def test_lean_admits_every_answer_and_replays_every_step(staged_runs):
    raw = T.environment()
    cases = []
    for pid, (result, staged) in staged_runs.items():
        for question, target in run.answer_targets(result["staged"]).items():
            cases.append({"id": f"{pid}/{question}", "kind": "document", "environment": raw,
                          "document": staged.document(target)})
    got = run.lean(cases)
    assert len(got) == 253
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
    assert s["strict"] == 76 and s["total"] == "253/253" and s["answered"] == 253
    assert s["per_question"] == {"Q1": "76/76", "Q2": "59/59", "Q3": "59/59", "Q4": "59/59"}
    assert s["disagreements"] == [] and s["open"] == []
    assert s["single_shot"] == {"answered": 0, "profiles": 76}
    assert s["mutants_killed"] == "30/30"
    lean = s["lean"]
    assert lean["certificates"] == lean["certificates_accepted"] > 0
    assert lean["documents"] == lean["documents_admitted"] == 253
    assert lean["model_premises"] == lean["model_premises_true"] > 0
    assert results["b1_certified"] is True
    assert results["environment_id"] == Environment(T.environment()).environment_id
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    assert "253/253" in readme and "76/76" in readme
    assert (HERE / "RESULTS.md").read_text(encoding="utf-8") == run.results_markdown(
        results, {c["id"]: c for c in keyed_cases()["cases"]})
