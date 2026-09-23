"""Invariants of ``ve assist`` over random small sessions.

For every random session (seeded, reproducible):

* success is a function of the graph: identical under every node insertion order, step check order
  and PARENT order within a node, and monotone in the proof budget (with and without countermodel
  search);
* ``verify_session`` accepts the untampered ledgers of a session whose proposer calls go through the
  audited claude CLI endpoint with random outcomes (success, model mismatch, timeout, malformed
  stream, infrastructure failure with and without retries, a CLI that breaks before a retry);
* no persisted or returned string contains the fake access token under any decoding, although every
  backend reply echoes it in a random encoding (checked by an independent brute-force decoder).
"""
import base64
import json
import random
import subprocess
from urllib.parse import quote

import pytest

from secret_decode import exposes_secret
from ve.assist import AssistSession, source_from_text, verify_session
from ve.environment import LANGUAGE, PROFILE, SPEC_REVISION

FAKE_TOKEN = "oauth-fake-9f8e7d6c5b4a"
ENV = {"language": LANGUAGE, "profile": PROFILE, "spec_revision": SPEC_REVISION, "vocabulary": {
    "sorts": {"service": {"description": "A service in the inventory."}},
    "predicates": {
        "deployed": {"arguments": ["service"], "description": "Recorded as deployed."},
        "reviewed": {"arguments": ["service"], "description": "Recorded as reviewed."},
        "safe": {"arguments": ["service"], "description": "Recorded as safe."}},
    "constants": {"api": {"sort": "service", "description": "The public API."},
                  "web": {"sort": "service", "description": "The web front end."}}}}
TEXT = """[given] Every reviewed service is safe. The API is reviewed. The web front end is reviewed.

[claimed] So the API is safe. So the web front end is safe.

[context] This paragraph is commentary."""

ASSUMPTIONS = ["@api is reviewed.", "@web is reviewed.", "@web is deployed.",
               "if (@api is reviewed), then (@api is safe).", "if (@web is reviewed), then (@web is safe).",
               "for every service s, (if (s is reviewed), then (s is safe)).",
               "if (@api is reviewed), then (@web is deployed).", "(@api is reviewed) or (@web is deployed).",
               "(@api is deployed) or ((@web is safe) and (@web is deployed))."]
CONCLUSIONS = [("@api is safe.", ["p2.1"]), ("@web is safe.", ["p2.2"]), ("@web is deployed.", ["p1.3"]),
               ("(@api is safe) and (@api is reviewed).", ["p2.1"]), ("@web is safe.", [])]
EXTRA_STEPS = [("@api is safe.", ["p2.1"], ["rule", "fact"]),
               ("(@api is safe) and (@api is reviewed).", ["p2.1"], ["goal", "fact"]),
               ("@web is safe.", ["p2.2"], ["rule", "webfact"]),
               ("@web is safe.", [], ["rule", "webfact"])]
ANCHORS = [["p1.1"], ["p1.2"], ["p1.3"], ["p1.1"], ["p1.2"], [], ["p2.1"]]
BUDGETS = (0, 2, 3, 4, 8, 10_000)
SPECS = range(16)


def random_spec(seed):
    """A small graph: a legitimate derivation of both claims, then 0-3 random mutations (extra assumptions
    and parents, re-anchoring, replaced formulas, extra steps), so outcomes mix successes and failures."""
    rng = random.Random(seed)
    rule = rng.choice(["for every service s, (if (s is reviewed), then (s is safe)).",
                       "(if (@api is reviewed), then (@api is safe)) and (if (@web is reviewed), then (@web is safe))."])
    nodes = [["rule", rule, ["p1.1"], []], ["fact", "@api is reviewed.", ["p1.2"], []],
             ["webfact", "@web is reviewed.", ["p1.3"], []],
             ["goal", "@api is safe.", ["p2.1"], ["rule", "fact"]],
             ["web_goal", "@web is safe.", ["p2.2"], ["rule", "webfact"]]]
    for i in range(rng.choice([0, 1, 1, 1, 2, 2, 3])):
        kind = rng.choice(["extra_parent", "anchor", "replace", "extra_step"])
        assumptions = [n for n in nodes if not n[3]]
        steps = [n for n in nodes if n[3]]
        if kind == "extra_parent":
            nodes.insert(0, [f"x{i}", rng.choice(ASSUMPTIONS), rng.choice(ANCHORS), []])
            target = rng.choice(steps)
            target[3] = target[3] + [f"x{i}"]
        elif kind == "anchor":
            rng.choice(assumptions)[2] = rng.choice(ANCHORS)
        elif kind == "replace":
            rng.choice(assumptions)[1] = rng.choice(ASSUMPTIONS)
        elif rng.random() < 0.75:  # a derivable extra step (a competing or chained witness)
            text, anchors, parents = rng.choice(EXTRA_STEPS)
            more = [q for q in rng.sample(["fact", "webfact"], rng.randint(0, 1)) if q not in parents]
            nodes.append([f"s{i}", text, anchors, parents + more])
        else:  # an arbitrary extra step (usually unprovable)
            text, anchors = rng.choice(CONCLUSIONS)
            pool = [n[0] for n in assumptions]
            nodes.append([f"s{i}", text, anchors, rng.sample(pool, rng.randint(1, min(3, len(pool))))])
    return [tuple(n) for n in nodes]


def build(nodes, budget, order_seed=None, proposer=None, plan=(), **options):
    """Insert the nodes in a random topological order with shuffled parents, check steps in random order.
    ``plan`` interleaves proposer calls (returned results are collected on ``session.returned``)."""
    rng = random.Random(order_seed)
    s = AssistSession.create(ENV, source_from_text(TEXT), [{"id": "t_main", "sentence": "p2.1"}],
                             options={"max_proof_steps": budget, **options})
    s.returned = []
    s.proposer = proposer
    assert s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})["ok"]
    plan = list(plan)
    pending = list(nodes)
    while pending:
        ready = [row for row in pending if all(p in s.nodes for p in row[3])]
        row = rng.choice(ready) if order_seed is not None else ready[0]
        pending.remove(row)
        name, text, anchors, parents = row
        parents = list(parents)
        if order_seed is not None:
            rng.shuffle(parents)
        result = s.apply("add_node", {"name": name, "text": text, "anchors": anchors, "parents": parents})
        assert result["ok"], result
        if plan:
            s.returned.append(plan.pop(0)(s))
    steps = [n for n in s.nodes if s.nodes[n].kind == "step"]
    if order_seed is not None:
        rng.shuffle(steps)
    for n in steps:
        s.returned.append(s.apply("check_step", {"name": n}))
    while plan:
        s.returned.append(plan.pop(0)(s))
    return s


@pytest.mark.parametrize("seed", SPECS)
def test_success_is_a_function_of_the_graph_and_monotone_in_budget(seed):
    nodes = random_spec(seed)
    for extra in ({}, {"max_evaluations": 0}):
        row = []
        for budget in BUDGETS:
            outcomes = {}
            for order in (None, 1, 2):
                s = build(nodes, budget, order, **extra)
                status = s.apply("status")
                outcomes[order] = status["success"]
                if order is None:
                    replayed = AssistSession.from_ledger(json.loads(json.dumps(s.to_ledger())))
                    assert replayed.apply("status")["success"] is status["success"]
            assert len(set(outcomes.values())) == 1, (seed, extra, budget, outcomes, nodes)
            row.append(outcomes[None])
        first = row.index(True) if True in row else len(row)
        assert all(row[first:]), (seed, extra, dict(zip(BUDGETS, row)), nodes)


# ---------------------------------------------------------------- the audited endpoint, faked

def encodings(secret):
    esc = "\\u%04x" % ord(secret[0]) + secret[1:]
    return [secret, esc, json.dumps({"inner": json.dumps({"t": esc})}),
            base64.b64encode(("key=" + secret).encode()).decode(),
            base64.urlsafe_b64encode(secret.encode()).decode().rstrip("="),
            "".join("%%%02X" % b for b in secret.encode()), secret.encode().hex(),
            quote(base64.b64encode(esc.encode()).decode(), safe=""), secret.upper()]


def stream(model, served, text, usage=(900, 7)):
    return [{"type": "system", "subtype": "init", "model": model, "tools": [], "mcp_servers": [], "agents": [],
             "session_id": text[-40:]},
            {"type": "assistant", "message": {"id": "m1", "model": served, "content": [{"type": "text", "text": text}],
                                              "usage": {"input_tokens": usage[0], "output_tokens": 1}}},
            {"type": "result", "subtype": "success", "is_error": False, "num_turns": 1, "result": text,
             "stop_reason": "end_turn", "modelUsage": {served: {}},
             "usage": {"input_tokens": usage[0], "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
                       "output_tokens": usage[1]}}]


def infra(model):
    return [{"type": "system", "subtype": "init", "model": model, "tools": [], "mcp_servers": [], "agents": []},
            {"type": "result", "subtype": "error_during_execution", "is_error": True, "num_turns": 1,
             "result": "API Error: Connection error.", "modelUsage": {model: {}},
             "usage": {"input_tokens": 700, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
                       "output_tokens": 0}}]


def raw(records):
    return "\n".join(json.dumps(r) for r in records)


@pytest.fixture
def endpoint(tmp_path, monkeypatch):
    """A ClaudeProposer over a fake CLI: ``state["queue"]`` holds the next process outcomes."""
    import ve_experiments.claude_cli as cc
    from ve_experiments.assist_haiku import ClaudeProposer
    fake = tmp_path / "claude"
    fake.write_text("#!/bin/sh\n")
    state = {"queue": [], "missing": False}
    monkeypatch.setattr(cc.shutil, "which", lambda name: None if state["missing"] else str(fake))
    monkeypatch.setattr(cc.subprocess, "check_output", lambda *a, **k: cc.Controls().cli_version)
    monkeypatch.setattr(cc, "oauth_token", lambda config=None: FAKE_TOKEN)
    monkeypatch.setattr(cc, "check_context_date", lambda controls: None)
    monkeypatch.setattr(cc.time, "sleep", lambda seconds: None)

    def run(*a, **k):
        outcome = state["queue"].pop(0)
        if state["queue"] and state["queue"][0] == "break":  # the CLI disappears after this attempt
            state["queue"].pop(0)
            state["missing"] = True
        if isinstance(outcome, BaseException):
            raise outcome
        return subprocess.CompletedProcess(a, outcome[1], outcome[0], "")
    monkeypatch.setattr(cc.subprocess, "run", run)
    proposer = ClaudeProposer(tmp_path / "calls.jsonl", model="sonnet", working_directory=str(tmp_path / "empty"))
    return proposer, state, cc.MODELS["sonnet"], tmp_path / "calls.jsonl"


def random_plan(seed, proposer, state, model):
    rng = random.Random(1000 + seed)
    kinds = ["ok", "mismatch", "timeout", "malformed", "infra", "infra_then_ok", "infra_then_missing"]

    def step(kind, echo):
        reply = json.dumps({"candidates": [{"ve": "@api is reviewed.", "reading": "echo " + echo}]})
        good = raw(stream(model, model, reply))

        def act(s):
            state["missing"] = False
            proposer.client.infrastructure_retries = kind in ("infra_then_ok", "infra_then_missing")
            state["queue"] = {
                "ok": [(good, 0)],
                "mismatch": [(raw(stream(model, "claude-" + echo, reply)), 0)],
                "timeout": [subprocess.TimeoutExpired(["claude"], 180, output="\n".join(good.splitlines()[:2]).encode())],
                "malformed": [(raw(stream(model, model, reply) + [dict(stream(model, model, reply, (0, 0))[2])]), 0)],
                "infra": [(raw(infra(model)), 1)],
                "infra_then_ok": [(raw(infra(model)), 1), (good, 0)],
                "infra_then_missing": [(raw(infra(model)), 1), "break"],
            }[kind]
            if kind == "infra_then_missing":
                state["queue"].append((good, 0))  # never reached: the CLI is gone
            result = s.apply("propose", {"sentence": "p1.2", "k": 1})
            assert result["ok"] is (kind in ("ok", "infra_then_ok")), (kind, result)
            state["missing"] = False
            return result
        return act
    echoes = encodings(FAKE_TOKEN)
    return [step(rng.choice(kinds), rng.choice(echoes)) for _ in range(rng.randint(2, 4))]


@pytest.mark.parametrize("seed", SPECS)
def test_untampered_ledgers_verify_and_no_string_carries_the_token(seed, endpoint):
    proposer, state, model, calls = endpoint
    nodes = random_spec(seed)
    s = build(nodes, 10_000, seed, proposer=proposer, plan=random_plan(seed, proposer, state, model))
    status = s.apply("status")
    # Proposer calls never change the outcome.
    assert status["success"] is build(nodes, 10_000, seed).apply("status")["success"]
    ledger = json.loads(json.dumps(s.to_ledger()))
    rows = [json.loads(line) for line in calls.read_text().splitlines()]
    result = verify_session(ledger, calls=rows)
    assert result["ok"], (seed, result["problems"])
    assert AssistSession.from_ledger(ledger).usage()["tokens"] == s.usage()["tokens"]
    # The endpoint's tokens equal the calls ledger's, attempt for attempt.
    assert s.usage()["tokens"]["proposer"]["input_tokens"] == result["calls"]["ledger_input_tokens"]
    for value in (calls.read_text(), rows, ledger, s.returned, status):
        assert not exposes_secret(value, FAKE_TOKEN), seed
