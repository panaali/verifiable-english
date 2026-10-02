"""Agent-policy under norm-defaults@0 (docs/spec/norm-defaults.md fixture u4).

The expected sets are copied from the frozen answer key and README, never
regenerated. Each action's base situation is the closed-world model of its
record (check.py `record_model`), for the 39 records that the committed
results mark finite-model complete (M8); a40 to a42 leave facts open, so their
situation is not one finite model and they are outside this check.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "agent-policy"
sys.path.insert(0, str(HERE))

import check  # noqa: E402
import environments  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve import norm_defaults as nd  # noqa: E402

KEY = json.loads((HERE / "answer-key.json").read_text())
RESULTS = json.loads((HERE / "results.json").read_text())
COMPLETE = RESULTS["M8"]["finite_model_complete_records"]
# README.md:151-152: approved, unreported actions that are breaches only under "must be reported".
APPROVED_UNREPORTED = ["a01", "a02", "a04", "a07", "a15", "a17", "a19", "a21", "a23", "a25", "a29", "a35", "a42"]


def test_unspecified_environment_is_generated_and_differs_only_in_profile_and_defaults():
    ((name, text),) = environments.unspecified_file().items()
    assert (HERE / name).read_text() == text
    data = json.loads(text)
    base = json.loads((HERE / "environment.deny-neednot.json").read_text())
    assert data["profiles"] == ["data@0", "norm-defaults@0", "norms@0", "relational-fol@0"]
    for predicate in ("permitted", "report_required"):
        assert data["vocabulary"]["predicates"][predicate]["regulated"]["default"] == "unspecified"
        data["vocabulary"]["predicates"][predicate]["regulated"]["default"] = "deny"
    data["profiles"] = base["profiles"]
    assert data == base


def _statuses():
    rules = check.policy().rules
    inventory, records = check.parse_log((HERE / "log.ve").read_text())
    raw = json.loads((HERE / "environment.unspecified.json").read_text())
    out = {}
    for action in COMPLETE:
        env = check.environment(action=action, data=raw)
        document = nd.UnspecifiedDocument(env, rules)
        situation = check.record_model(document.situation_environment(), (*inventory, *records[action]))
        out[action] = (document, situation,
                       {p: document.status(situation, p, (action,)) for p in ("permitted", "report_required")})
    return out


STATUSES = None


def statuses():
    global STATUSES
    if STATUSES is None:
        STATUSES = _statuses()
    return STATUSES


def test_u4_permitted_is_undecided_exactly_on_the_forced_default_cases():
    undecided = sorted(a for a, (_, _, s) in statuses().items() if s["permitted"].status == "UNDECIDED")
    assert undecided == KEY["forced_default_sensitive"] == ["a27", "a36", "a37", "a38"]
    for action, (document, situation, status) in statuses().items():
        entry = KEY["actions"][action]
        if action in KEY["forced_default_sensitive"]:
            first, second = status["permitted"].fillings
            assert nd.check_undecided(document, situation, "permitted", (action,), first, second)
            continue
        permitted = status["permitted"]
        assert permitted.status == "SETTLED", action
        # The completed outcome is the same in all four shipped environments.
        assert entry["deny"] == entry["allow"], action
        if entry["verdict"] != "CONFLICT":
            assert permitted.value is (entry["deny"] == "P"), action


def test_u4_a10_is_still_a_conflict_between_rules_3_and_14():
    document, situation, _ = statuses()["a10"]
    report = nd.check_conflict(document, model=situation.to_dict())
    assert (report.status, report.target, report.kind) == ("CONFLICT", "permitted", "settled")
    numbers = check.numbers(document.author.rules)
    filled = document.with_filling(situation, report.filling)
    selected = document.filled.selected_rules("permitted", filled, ("a10",))
    assert sorted(numbers[r.name] for r in selected) == [3, 14]


def test_u4_reporting_breaches_settled_and_undecided():
    covered = KEY["obligation"]["covered"]
    for action, (_, situation, status) in statuses().items():
        report = status["report_required"]
        if action in covered:
            assert (report.status, report.value) == ("SETTLED", True), action
        else:
            assert report.status == "UNDECIDED", action
    breaches = {"settled": [], "undecided": []}
    for action, (document, situation, status) in statuses().items():
        permitted, report = status["permitted"], status["report_required"]
        reported = (action,) in situation.relations["reported"]
        if permitted.status != "SETTLED" or not permitted.value or reported:
            continue
        if nd.check_conflict(document, model=situation.to_dict()).status == "CONFLICT":
            continue  # a10: not approved, a contradiction
        if report.status == "SETTLED" and report.value:
            breaches["settled"].append(action)
        elif report.status == "UNDECIDED":
            breaches["undecided"].append(action)
    assert breaches["settled"] == KEY["obligation"]["breach_neednot"] == ["a13"]
    # a42's record is not finite-model complete, so it is checked by the key alone.
    assert breaches["undecided"] == [a for a in APPROVED_UNREPORTED if a in COMPLETE]
    assert sorted(set(KEY["obligation"]["breach_must"]) - {"a13"}) == APPROVED_UNREPORTED


UNSPECIFIED = RESULTS["unspecified"]


def test_flag_free_lean_copy_is_generated_and_differs_only_in_the_tool_flags():
    ((name, text),) = environments.unspecified_lean_file().items()
    assert (HERE / name).read_text() == text
    data = json.loads(text)
    assert "functional" not in data["vocabulary"]["predicates"]["tool"]
    data["vocabulary"]["predicates"]["tool"].update(functional=True, total=True)
    assert data == json.loads((HERE / "environment.unspecified.json").read_text())


def test_committed_unspecified_results_are_this_environment_and_these_statuses():
    raw = json.loads((HERE / "environment.unspecified.json").read_text())
    assert UNSPECIFIED["environment_id"] == Environment(raw).environment_id
    assert UNSPECIFIED["records"] == COMPLETE
    assert UNSPECIFIED["not_one_finite_model"] == ["a40", "a41", "a42"]
    for action, (_, _, status) in statuses().items():
        entry = UNSPECIFIED["actions"][action]
        for predicate in ("permitted", "report_required"):
            s = status[predicate]
            text = s.status if s.status != "SETTLED" else "SETTLED " + ("yes" if s.value else "no")
            assert entry[predicate] == text, (action, predicate)


def test_every_changed_verdict_is_a_default_the_policy_does_not_state():
    """Each change against the four shipped environments: `permitted` exactly on the
    key's forced-default actions, `report_required` exactly on the actions rules 25
    and 26 do not cover; nothing a rule decides changes."""
    covered = set(KEY["obligation"]["covered"])
    changed = {(c["action"], c["predicate"]): c for c in UNSPECIFIED["changes"]}
    expected = {(a, "permitted") for a in KEY["forced_default_sensitive"]}
    expected |= {(a, "report_required") for a in COMPLETE if a not in covered}
    assert set(changed) == expected
    for (action, predicate), change in changed.items():
        assert change["after"] == "UNDECIDED" and change["reason"], (action, predicate)
        if action == "a10":
            assert change["before"] == {"need not": "⊥", "must": "⊥"}
        elif predicate == "permitted":
            assert change["before"] == {"deny": "F", "allow": "P"}
        else:
            assert change["before"] == {"need not": "F", "must": "P"}
    assert UNSPECIFIED["undecided"]["permitted"] == KEY["forced_default_sensitive"]
    assert UNSPECIFIED["actions"]["a10"]["conflict"] == "CONFLICT"
    assert UNSPECIFIED["conflict"] == {"action": "a10", "target": "permitted", "kind": "settled", "rules": [3, 14]}


def test_gaps_breaches_and_lean_replay():
    for predicate in ("permitted", "report_required"):
        assert UNSPECIFIED["gaps"][predicate] == {"lines": ["completion: unspecified", "gaps: reachable"],
                                                  "witness": "a27"}
        assert UNSPECIFIED["inherits_from"][predicate] == []
    assert UNSPECIFIED["reporting_breaches"]["settled"] == KEY["obligation"]["breach_neednot"]
    assert UNSPECIFIED["reporting_breaches"]["undecided"] == [a for a in APPROVED_UNREPORTED if a in COMPLETE]
    lean = UNSPECIFIED["lean"]
    # 39 records x 2 points, the a10 conflict witness and the two gap witnesses.
    assert lean == {"elaborate": "regenerated", "cases": 81, "agree": 81, "mismatches": []}
