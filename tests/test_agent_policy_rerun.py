"""Agent-policy use case: rerun VE on every logged action and every policy query.

The recomputed results must equal the committed `results.json`, so any change
in the policy, the log or VE's behaviour fails here. When `lake build` has
produced the route runner, Lean also replays every certificate of the rerun.
The six mutants take several minutes each; `check.py mutants` reruns them, and
`test_agent_policy.py` checks their committed results against the answer key.
"""
import json
import multiprocessing
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "agent-policy"
sys.path.insert(0, str(HERE))

import check  # noqa: E402

COMMITTED = json.loads((HERE / "results.json").read_text())


def _json(value):
    return json.loads(json.dumps(value, ensure_ascii=False, sort_keys=True))


@pytest.fixture(scope="module")
def rerun():
    evidence = check.Evidence(keep=check.LEAN_ROUTE.exists())
    with multiprocessing.get_context("fork").Pool(check.WORKERS) as pool:
        base = check.run(evidence=evidence, pool=pool)
        # Let the workers exit normally (leaving the block terminates them by a signal).
        pool.close()
        pool.join()
    return base, evidence


def test_every_action_and_policy_query_equals_the_committed_results(rerun):
    base, _ = rerun
    summary = _json(check.base_summary(base))
    for field in ("inputs", "actions", "policy", "policy_summary", "comparison", "M8"):
        assert summary[field] == COMMITTED[field], field


def test_counts_equal_the_committed_run(rerun):
    _, evidence = rerun
    for field in ("ve_prover_calls", "focused_calls", "certificates", "open_by_models", "unknown",
                  "model_witnesses"):
        assert evidence.counts[field] == COMMITTED["M10"][field], field


def test_lean_replays_every_certificate_of_the_rerun(rerun):
    _, evidence = rerun
    if not check.LEAN_ROUTE.exists():
        pytest.skip("lake build has not produced ve_conformance")
    replay = check.replay_lean(evidence.exported)
    assert replay["valid"] == replay["certificates"]
    assert sum(replay["certificates"].values()) == COMMITTED["M10"]["certificates"]
