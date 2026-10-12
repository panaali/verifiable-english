"""Replay every pre-closure v0 certificate against its frozen original verdict."""
from dataclasses import asdict
import json
from pathlib import Path

from ve import Environment
from ve.ast import document_from_data
from ve.entailment import check_entailment_certificate


def test_whole_v0_certificate_corpus_has_identical_replay_verdicts():
    path = Path(__file__).resolve().parents[1] / "conformance/v0-replay-baseline.json"
    baseline = json.loads(path.read_text())
    assert baseline["baseline_commit"] == "6798e034c4aa7082dafacbb7b130879cd4eec4f6"
    assert (baseline["positive"], baseline["forged"]) == (732, 150)
    assert len(baseline["rows"]) == 882
    assert len({row["case"]["id"] for row in baseline["rows"]}) == 882
    verdicts = []
    for row in baseline["rows"]:
        case = row["case"]
        env = Environment(case["environment"])
        assert not env.closure  # Type checking excludes Reach at every depth.
        fs = document_from_data(env, case["premises"] + [case["conclusion"]]).formulas
        after = asdict(check_entailment_certificate(env, fs[:-1], fs[-1], case["certificate"]))
        before = row["before"]
        if before["status"] == after["status"] == "InvalidCertificate":
            # Documented wording: Lean, which replays under every authority since
            # lean-first batch 13b, names its own decode or replay failure
            # ("certificate does not replay"), not the node Python rejected first.
            before = {**before, "detail": after["detail"]}
        assert after == before, case["id"]
        verdicts.append(after["valid"])
    assert sum(verdicts) == 732
