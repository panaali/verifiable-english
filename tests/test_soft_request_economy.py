"""Batch 6 latency: soft requests that Lean answers once per document (docs/lean-first/b6/DELTA.md, Latency).

Regressions of the fix-directive finding "UDHR 38.99 s -> 150.37 s and 58.90 s -> 426.19 s": every soft-norms
request rebuilt `soften D`, its layer order and its expansion table for each formula it typed (about 1.5 s on a
70-predicate environment with no rules), and readings sent the same rules again for every candidate side and
every pair. The class is removed in two places, each tested here:

* Lean checks a soft source with its layers computed once (`VE.SoftNorms.Once`, proved equal to the checks it
  replaces), so a request on the widest environment stays within a CPU deadline the old checks overran;
* Python sends a quoted rule to Lean at most once per lower soft source (`soft_relay.check_rules`): a whole
  document check never asks Lean about a rule it has already accepted under the same source.
"""
from __future__ import annotations

from itertools import product
import json

import pytest

from tests import lean_routes
from tests.test_norms import environment, obligation, permission
from tests.test_readings_s1_document import default, s1_document, strict
from tests.test_readings_s1_lean import norm as s1_norm
from ve.backends import lean_service, relay, soft_relay
from ve.document import check_document
from ve.errors import CheckerUnavailable, VEError
from ve.softnorms import SoftEnvironment, check_rule_batch, decode_rule

DECIDER = {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []}
# W1's limit on regulated predicates (`decodeNormsEnvironment`): the widest soft environment.
MAX_REGULATED = 64


@pytest.fixture
def service():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


@pytest.fixture
def fresh(monkeypatch):
    """An empty accepted-rule memo, and the soft rule requests sent while the test runs."""
    monkeypatch.setattr(soft_relay, "_accepted", type(soft_relay._accepted)())
    sent = []
    real = soft_relay.run

    def recorded(case):
        if case.get("kind") in ("soft-rule", "soft-rules"):
            sent.append(json.loads(json.dumps(case)))
        return real(case)

    monkeypatch.setattr(soft_relay, "run", recorded)
    return sent


def wide_environment():
    """`MAX_REGULATED` regulated predicates: obligations paired with their permissions, over one sort."""
    names = ["".join(letters) for letters in product("abcdefgh", repeat=2)][:MAX_REGULATED // 2]
    predicates = {}
    for name in names:
        predicates[f"{name}_required"] = obligation("deny", f"{name}_permitted", act=f"{{0}} do {name}",
                                                    args=("assistant",))
        predicates[f"{name}_permitted"] = permission("allow", act=f"{{0}} do {name}", args=("assistant",))
    raw = environment(predicates, sorts=("assistant", "user")).to_dict()
    raw["profiles"] = sorted({"relational-fol@0", "norms@0", "soft-norms@0"})
    return raw, names


def rule(name, predicate, sign=True, **soft):
    return {"norm": {"name": name, "predicate": predicate, "sign": sign, "guard": ["top"], "unless": [],
                     "over": [], **soft}}


def should(name, predicate, sign=True):
    return rule(name, predicate, sign, mode="default", exception=dict(DECIDER))


def rules_of(case):
    return [case["norm"]] if case["kind"] == "soft-rule" else case["norms"]


def sent_pairs(sent):
    """(source, rule) for every rule a request asked Lean to check."""
    return [(json.dumps(case["environment"], sort_keys=True), json.dumps(item, sort_keys=True))
            for case in sent for item in rules_of(case)]


# -- Lean: one soft source, its layers computed once


@pytest.mark.live_service  # its CPU deadline is enforced on the process (tests/answer_store.py INVENTORY row 8)
def test_soft_requests_on_the_widest_environment_stay_within_a_cpu_deadline(service, monkeypatch):
    """Each kind on 64 regulated predicates, through the production relay on a fresh service: the old checks
    spent about 1.5 s of CPU per case on a 62-predicate UDHR source; with the layers computed once a case needs a
    small fraction of the 0.5 s of service CPU allowed here (`lean_service.DEADLINES`: the service is stopped and
    the call is CheckerUnavailable past it)."""
    raw, names = wide_environment()
    cases = [{"id": f"rule-{n}", "kind": "soft-rule", "environment": raw,
              "norm": should(f"r{n}", f"{name}_required")} for n, name in enumerate(names[:3])]
    cases.append({"id": "rules", "kind": "soft-rules", "environment": raw,
                  "norms": [should(f"s{n}", f"{name}_required") for n, name in enumerate(names)]})
    cases.append({"id": "elaborate", "kind": "soft-elaborate", "environment": raw,
                  "norms": [should("a", f"{names[0]}_required"), should("b", f"{names[0]}_permitted", False),
                            rule("c", f"{names[1]}_required")]})
    monkeypatch.setitem(lean_service.DEADLINES, "soft-norms", (0.5, 0.0))
    pool = lean_service.LeanServicePool(size=1)
    monkeypatch.setattr(relay, "_pool", pool)
    try:
        rows = relay.decide("soft-norms", cases)
    finally:
        pool.close()
    assert [row["status"] for row in rows] == ["ok"] * len(cases), rows
    assert rows[3]["results"] == [{"status": "ok"}] * len(names)
    assert {item["label"] for item in rows[4]["background"] if item["generator"] == "soft"} == {
        "soft:coherence:a,b"}
    assert len(rows[4]["conflict_targets"]) == MAX_REGULATED + len(names)


# -- Python: a quoted rule is sent at most once per source


def test_a_batch_sends_only_the_rules_not_yet_accepted(service, fresh):
    raw, names = wide_environment()
    env = SoftEnvironment(raw)
    first = [should("a", f"{names[0]}_required"), should("b", f"{names[1]}_required")]
    assert check_rule_batch(env, first) == [{"status": "ok"}] * 2
    assert [rules_of(case) for case in fresh] == [first]
    second = [*first, should("c", f"{names[2]}_required")]
    assert check_rule_batch(env, second) == [{"status": "ok"}] * 3
    assert rules_of(fresh[-1]) == [second[2]]
    count = len(fresh)
    assert check_rule_batch(env, list(reversed(second))) == [{"status": "ok"}] * 3
    assert decode_rule(env, second[1]).core.name == "b"
    assert len(fresh) == count, "an accepted rule was sent again under the same source"


def test_a_rejected_rule_is_never_kept(service, fresh):
    raw, names = wide_environment()
    env = SoftEnvironment(raw)
    bad = should("bad", "missing_required")
    for _ in range(2):
        [ok, error] = check_rule_batch(env, [should("a", f"{names[0]}_required"), bad])
        assert ok == {"status": "ok"} and error["status"] == "error"
        with pytest.raises(VEError) as raised:
            decode_rule(env, bad)
        assert raised.value.code == "SOFT_INVALID_INPUT" and "missing_required" in str(raised.value)
    assert sum(bad in rules_of(case) for case in fresh) == 4


def test_a_whole_request_rejection_is_the_full_requests(monkeypatch):
    """When Lean refuses the request for the unseen rules, the full request is sent, so the diagnostic and its
    code are those of the request without the memo."""
    monkeypatch.setattr(soft_relay, "_accepted", type(soft_relay._accepted)())
    source = {"profiles": ["soft-norms@0"]}
    seen = [{"norm": {"name": "seen"}}, {"norm": {"name": "new"}}]
    soft_relay._accepted_for(soft_relay._text(source)).add(soft_relay._text(seen[0]))
    calls = []

    def refusing(case):
        calls.append([n["norm"]["name"] for n in case["norms"]])
        error = VEError(f"InvalidInput: refused {len(calls)}")
        error.code = f"CODE_{len(case['norms'])}"
        raise error

    monkeypatch.setattr(soft_relay, "run", refusing)
    with pytest.raises(VEError, match="refused 2") as raised:
        soft_relay.check_rules(source, seen)
    assert calls == [["new"], ["seen", "new"]] and raised.value.code == "CODE_2"


@pytest.mark.parametrize("answers", [[], [{"status": "ok"}] * 2, None])
def test_an_answer_count_that_differs_from_the_request_is_unavailable(monkeypatch, answers):
    monkeypatch.setattr(soft_relay, "_accepted", type(soft_relay._accepted)())
    source = {"profiles": ["soft-norms@0"]}
    soft_relay._accepted_for(soft_relay._text(source)).add(soft_relay._text({"norm": {"name": "seen"}}))
    monkeypatch.setattr(soft_relay, "run", lambda case: {"id": "soft-rules", "status": "ok", "results": answers})
    with pytest.raises(CheckerUnavailable, match="count differs"):
        soft_relay.check_rules(source, [{"norm": {"name": "seen"}}, {"norm": {"name": "new"}}])
    assert soft_relay._accepted_for(soft_relay._text(source)) == {soft_relay._text({"norm": {"name": "seen"}})}


def test_another_pool_starts_with_no_accepted_rule(monkeypatch):
    monkeypatch.setattr(soft_relay, "_accepted", type(soft_relay._accepted)())

    class Pool:
        pass

    first, second = Pool(), Pool()
    monkeypatch.setattr(soft_relay, "_pool_for", lambda executable: first)
    soft_relay._accepted_for("{}").add("rule")
    monkeypatch.setattr(soft_relay, "_pool_for", lambda executable: second)
    assert soft_relay._accepted_for("{}") == set()


def test_a_readings_document_never_asks_about_an_accepted_rule_twice(service, fresh, tmp_path):
    """Three readings of one sentence (three pairs) and two fixed rules: each candidate side rebuilt the whole
    rule list, and each pair's reading names re-sent every candidate rule."""
    fixed = [("u0", s1_norm("never-help", "help_required", False)),
             ("u2", s1_norm("always-help", "help_required", True, "default"))]
    other = ("other", s1_norm("other", "avoid_required", False, "default"), "norm")
    path = s1_document(tmp_path, [strict(), default(), other], fixed=fixed)
    report = check_document(path)
    assert len(report["readings"]["sets"][0]["pairs"]) == 3
    pairs = sent_pairs(fresh)
    assert pairs, "the document asked Lean about no quoted rule"
    assert len(pairs) == len(set(pairs)), "a rule accepted under a source was sent again"
