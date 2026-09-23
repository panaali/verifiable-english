"""D gate offline tests: answer parsing, ledger reconciliation, statistics, the runner's stop rules,
resume and UTC-midnight handling, and the freeze checks. No model calls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from ve_experiments.claude_cli import MODELS, SYSTEM, EndpointError

D = Path(__file__).resolve().parent.parent / "experiments" / "D-gate"
sys.path.insert(0, str(D))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, D / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = _load("analyze")
R = _load("run_raw")
RP = _load("render_prompts")

MODEL = MODELS["opus"]


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


# ------------------------------------------------------------------------------------------------
# fixtures: a small synthetic study (the real items are used where the statistic depends on them)
# ------------------------------------------------------------------------------------------------

@pytest.fixture
def study():
    ids = [f"X{i}" for i in range(6)]
    texts = {i: f"prompt {i}" for i in ids}
    prompts = {i: sha(t) for i, t in texts.items()}
    frozen = dict(k=3, account_label="acct", system_sha256=sha(SYSTEM), model=MODEL, claude_binary_sha256="bin",
                  arms={"high": dict(model=MODEL, effort="high", timeout_s=900, output_tokens=32000)},
                  endpoint_controls=dict(backend_revision=4, host_system="Darwin", host_release="25.3.0",
                                         shell="/bin/sh", locale="en_US.UTF-8", timezone="UTC"))
    return ids, texts, prompts, frozen


REJECTED = {"type": "rate_limit_event", "rate_limit_info": {"status": "rejected"}}
OPUS_MSG = {"type": "assistant", "message": {"model": MODEL, "id": "m1", "content": [{"type": "text", "text": "Let"}]}}
SYNTH_MAX = {"type": "assistant", "message": {"model": "<synthetic>", "id": "m2", "content": [
    {"type": "text", "text": "API Error: Claude's response exceeded the 32000 output token maximum. To configure "
                             "this behavior, set the CLAUDE_CODE_MAX_OUTPUT_TOKENS environment variable."}]}}
ERROR_ROWS = {
    "error": ("CLI exit 1", dict(stream_records=[], reported_models=[])),
    # the pinned CLI's truncation: real Opus output then a <synthetic> max-output-tokens message (rejected by
    # claude_cli as a served-model mismatch, not as "Truncated ...")
    "truncated": ("Served model mismatch: ['<synthetic>', 'claude-opus-5-5']",
                  dict(stream_records=[OPUS_MSG, SYNTH_MAX], served_model=MODEL, reported_models=[MODEL],
                       output_tokens=32000)),
    "quota": ("CLI exit 1", dict(stream_records=[REJECTED], served_model=None, reported_models=[])),
    "quota_after_output": ("CLI exit 1", dict(stream_records=[OPUS_MSG, REJECTED], served_model=MODEL,
                                              reported_models=[MODEL], output_tokens=40)),
    "mixed": ("Served model mismatch", dict(stream_records=[OPUS_MSG], served_model=None,
                                            reported_models=[MODEL, "claude-sonnet-5"])),
}


class FakeClient:
    """Writes claude_cli-shaped ledger rows and replies or raises like ClaudeCLI.sample."""

    def __init__(self, ledger, day, frozen, behaviour, clock, tick=lambda: None):
        self.ledger, self.day, self.frozen, self.behaviour, self.clock = Path(ledger), day, frozen, behaviour, clock
        self.tick = tick  # advances the fake clock after each call
        self.calls = []

    input_tokens = staticmethod(lambda item: 100)

    def _row(self, item, s, prompt, system, status, **extra):
        return dict(key=f"{item}#{s}", item_id=item, sample_index=s, system=system, prompt=prompt,
                    account_label=self.frozen["account_label"], status=status,
                    timestamp=self.clock().isoformat(),
                    controls=dict(self.frozen["arms"]["high"], **self.frozen["endpoint_controls"],
                                  context_date=self.day, binary_sha256=self.frozen["claude_binary_sha256"]),
                    **extra)

    def _write(self, row):
        with open(self.ledger, "a") as f:
            f.write(json.dumps(row) + "\n")

    def sample(self, item, system, prompt, s):
        try:
            return self._sample(item, system, prompt, s)
        finally:
            self.tick()

    def _sample(self, item, system, prompt, s):
        self.calls.append((item, s))
        kind = self.behaviour(item, s)
        if kind == "global":
            exc = EndpointError("Call budget exhausted")
            exc.usage = {"not_started": True, "call_key": None}
            raise exc
        self._write(self._row(item, s, prompt, system, "started"))
        if kind in ERROR_ROWS:
            msg, extra = ERROR_ROWS[kind]
            self._write(self._row(item, s, prompt, system, "error", error=msg, **extra))
            exc = EndpointError(msg)
            exc.usage = {"call_key": f"{item}#{s}"}
            raise exc
        init = {"type": "system", "subtype": "init", "model": MODEL,
                "apiKeySource": "none" if kind != "paid" else "ANTHROPIC_API_KEY"}
        served = MODEL if kind != "othermodel" else "claude-sonnet-5"
        text = {"yes": "ok\nANSWER: YES", "no": "ANSWER: NO\n", "junk": "I think so."}.get(kind, "ANSWER: YES")
        row = self._row(item, s, prompt, system, "ok", text=text, served_model=served, stop_reason="end_turn",
                        stream_records=[init], input_tokens=self.input_tokens(item))
        self._write(row)
        return row


def make_runner(tmp_path, study, behaviour, start=datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc)):
    ids, texts, prompts, frozen = study
    clock = {"t": start}
    clients = {}

    def tick():
        clock["t"] += timedelta(seconds=30)

    def client_for_day(day, ledger):  # one client per ledger segment, as in run_raw.main
        clients.setdefault(Path(ledger).name, FakeClient(ledger, day, frozen, behaviour, lambda: clock["t"], tick))
        return clients[Path(ledger).name]

    def sleep(s):
        clock["t"] += timedelta(seconds=s)

    runner = R.Runner("high", tmp_path / "high", prompts, frozen, client_for_day, now=lambda: clock["t"],
                      sleep=sleep, log=lambda *_: None)
    return runner, clients, clock


def calls(clients):
    return [c for cl in clients.values() for c in cl.calls]


# ------------------------------------------------------------------------------------------------
# parsing
# ------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("reasoning\nANSWER: YES", "YES"),
    ("reasoning\nANSWER: NO\n\n  \n", "NO"),
    ("  ANSWER:  NO  ", "NO"),
    ("ANSWER: YES\nOn reflection the answer is no.", "UNPARSED"),   # an earlier answer line never counts
    ("ANSWER: YES\nANSWER: NO", "NO"),
    ("**ANSWER: YES**", "YES"),                                      # markdown emphasis tolerated
    ("reasoning\n**ANSWER:** NO", "NO"),
    ("_ANSWER: NO_", "NO"),
    ("`ANSWER: YES`", "YES"),
    ("ANSWER: YES.", "YES"),                                          # trailing punctuation tolerated
    ("**ANSWER: NO.**", "NO"),
    ("ANSWER: NO!", "NO"),
    ("**ANSWER: YES**\nThough I am not sure.", "UNPARSED"),          # still the final line only
    ("answer: yes", "UNPARSED"),
    ("ANSWER: YES, probably", "UNPARSED"),
    ("ANSWER: YESNO", "UNPARSED"),
    ("ANSWER: MAYBE", "UNPARSED"),
    ("", "UNPARSED"),
    (None, "UNPARSED"),
])
def test_parse_final_nonempty_line_only(text, expected):
    assert A.parse(text) == expected


CTRL = {"model": MODEL, "output_tokens": 32000}


def err(error="CLI exit 1", **kw):
    return dict(status="error", error=error, controls=CTRL, **kw)


def test_ledger_classification_separates_truncation_from_infrastructure():
    assert A.classify_ledger_final({"status": "ok", "text": "x\nANSWER: NO"}) == "NO"
    assert A.classify_ledger_final({"status": "ok", "text": "no answer"}) == "UNPARSED"
    assert A.classify_ledger_final(err()) == "ENDPOINT_ERROR"
    assert A.classify_ledger_final(dict(err(), status="infrastructure_error")) == "ENDPOINT_ERROR"


def test_truncation_is_classified_from_stream_evidence_not_error_text():
    opus = dict(reported_models=[MODEL], served_model=MODEL)
    # the error text alone is not evidence
    assert A.classify_ledger_final(err("Truncated or non-final response")) == "ENDPOINT_ERROR"
    # the pinned CLI's synthetic max-output-tokens message after real Opus output (a served-model mismatch)
    row = err("Served model mismatch: ['<synthetic>', 'claude-opus-5-5']", stream_records=[OPUS_MSG, SYNTH_MAX], **opus)
    assert A.classify_ledger_final(row) == "TRUNCATED"
    assert A.truncation_evidence(row) == ["synthetic max-output-tokens message"]
    # stop_reason max_tokens on the result or on an assistant message
    res = {"type": "result", "subtype": "success", "stop_reason": "max_tokens", "modelUsage": {MODEL: {}}}
    assert A.classify_ledger_final(err("Truncated or non-final response", stream_records=[OPUS_MSG, res], **opus)) == "TRUNCATED"
    msg = {"type": "assistant", "message": dict(OPUS_MSG["message"], stop_reason="max_tokens")}
    assert A.classify_ledger_final(err("Not a single-turn response", stream_records=[msg], **opus)) == "TRUNCATED"
    # output tokens at the cap
    row = err("Not a single-turn response", stream_records=[OPUS_MSG], output_tokens=32000, **opus)
    assert A.truncation_evidence(row) == ["output tokens 32000 at the cap 32000"]
    assert A.classify_ledger_final(dict(row, output_tokens=31999)) == "ENDPOINT_ERROR"
    # no output from the frozen model, or another model involved: never a model outcome
    assert A.classify_ledger_final(err(stream_records=[SYNTH_MAX])) == "ENDPOINT_ERROR"
    other = {"type": "assistant", "message": dict(OPUS_MSG["message"], model="claude-sonnet-5")}
    row = err(stream_records=[other, SYNTH_MAX], served_model=None, reported_models=["claude-sonnet-5"])
    assert A.classify_ledger_final(row) == "ENDPOINT_ERROR"


def test_quota_rejection_without_output_is_excluded_not_an_endpoint_error():
    assert A.classify_ledger_final(err(stream_records=[REJECTED])) == "QUOTA_EXCLUDED"
    assert A.classify_ledger_final(err("You've hit your limit")) == "QUOTA_EXCLUDED"
    after = err(stream_records=[OPUS_MSG, REJECTED], served_model=MODEL, reported_models=[MODEL], output_tokens=40)
    assert A.classify_ledger_final(after) == "ENDPOINT_ERROR"


def test_model_identity_rejects_none_with_mixed_or_foreign_reported_models():
    assert A.model_problems(err(served_model=None, reported_models=[]), MODEL) == []
    assert A.model_problems(err(served_model=None, reported_models=[MODEL]), MODEL) == []
    assert A.model_problems(err(served_model=None, reported_models=[MODEL, "claude-sonnet-5"]), MODEL)
    assert A.model_problems(err(served_model=None, reported_models=["claude-sonnet-5"]), MODEL)
    foreign = {"type": "assistant", "message": {"model": "claude-haiku-4-5-20251001", "content": []}}
    assert A.model_problems(err(served_model=None, reported_models=[], stream_records=[foreign]), MODEL)
    assert A.model_problems({"status": "ok", "served_model": None}, MODEL)


# ------------------------------------------------------------------------------------------------
# reconciliation
# ------------------------------------------------------------------------------------------------

def complete_run(tmp_path, study, behaviour=lambda i, s: "yes"):
    runner, clients, _ = make_runner(tmp_path, study, behaviour)
    runner.run(study[1], SYSTEM)
    return A.load_arm(tmp_path / "high")


def test_reconcile_accepts_a_complete_consistent_run(tmp_path, study):
    answers, ledgers, stop = complete_run(tmp_path, study)
    records, orphans = A.reconcile(answers, ledgers, study[2], study[3], "high")
    assert len(records) == 18 and not orphans and stop is None


def test_reconcile_refuses_incomplete_data(tmp_path, study):
    answers, ledgers, _ = complete_run(tmp_path, study)
    with pytest.raises(A.DataError, match="started in the ledger but no answers row"):
        A.reconcile(answers[:-1], ledgers, study[2], study[3], "high")
    # the review's case: a single UNPARSED record with no ledger must not pass
    one = [dict(id="X0", sample=0, arm="high", status="UNPARSED", answer=None, key="k", ledger="ledger-2026-09-23.jsonl")]
    with pytest.raises(A.DataError, match="incomplete|without a ledger start"):
        A.reconcile(one, {}, study[2], study[3], "high")


def test_reconcile_refuses_duplicates_replays_and_mismatches(tmp_path, study):
    answers, ledgers, _ = complete_run(tmp_path, study)
    prompts, frozen = study[2], study[3]
    with pytest.raises(A.DataError, match="duplicate"):
        A.reconcile(answers + [answers[0]], ledgers, prompts, frozen, "high")
    (name, rows), = ledgers.items()
    replay = {name: rows, "ledger-2026-09-24.jsonl": [dict(rows[0], controls=dict(rows[0]["controls"], context_date="2026-09-24"),
                                                           timestamp="2026-09-24T00:05:00+00:00")]}
    with pytest.raises(A.DataError, match="replay"):
        A.reconcile(answers, replay, prompts, frozen, "high")
    flipped = [dict(answers[0], status="NO", answer="NO")] + answers[1:]
    with pytest.raises(A.DataError, match="ledger implies YES"):
        A.reconcile(flipped, ledgers, prompts, frozen, "high")
    other = {name: [dict(r, account_label="other") for r in rows]}
    with pytest.raises(A.DataError, match="not the frozen account"):
        A.reconcile(answers, other, prompts, frozen, "high")
    wrong_prompt = {name: [dict(rows[0], prompt="tampered")] + rows[1:]}
    with pytest.raises(A.DataError, match="prompt differs"):
        A.reconcile(answers, wrong_prompt, prompts, frozen, "high")
    wrong_date = {name: [dict(r, controls=dict(r["controls"], context_date="2026-09-22")) for r in rows]}
    with pytest.raises(A.DataError, match="segment date"):
        A.reconcile(answers, wrong_date, prompts, frozen, "high")
    ghost = [dict(answers[0], id="X9")] + answers[1:]
    with pytest.raises(A.DataError, match="not a scheduled sample"):
        A.reconcile(ghost, ledgers, prompts, frozen, "high")


# ------------------------------------------------------------------------------------------------
# statistics on the real items
# ------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real():
    return A.load_inputs()


def records_from(statuses):
    """statuses: {(id, s): status}."""
    return {k: {"status": v} for k, v in statuses.items()}


def all_correct(items, gt):
    return {(i, s): gt[i] for i in items for s in range(3)}


def test_items_edges_and_directions(real):
    items, gt, prompts = real
    assert len(items) == 43 and sum(gt[i] == "YES" for i in gt) == 20
    assert sorted(i for i in items if "edge" in items[i]["tags"]) == ["D26", "D42"]
    assert {items[i]["direction"] for i in items} == {"restriction", "guarantee"}
    assert items["D37"]["direction"] == "guarantee" and items["D09"]["direction"] == "guarantee"
    primary = [i for i in items if "edge" not in items[i]["tags"]]
    assert sum(items[i]["direction"] == "restriction" and gt[i] == "NO" for i in primary) == 16
    assert "local time is defined" in items["D26"]["question"]
    assert "Every referenced entity exists in the entity store" in items["D01"]["domain"]


def test_gate_fail_when_all_correct_and_no_gate_for_low(real):
    items, gt, _ = real
    rec = records_from(all_correct(items, gt))
    out = A.analyse_arm(rec, items, gt, "high", 129)
    assert out["primary"]["error"] == 0 and out["gate"].startswith("FAIL")
    assert out["primary"]["items"] == 41 and out["primary"]["artefacts"] == 28
    low = A.analyse_arm(rec, items, gt, "low", 129)
    assert low["gate"].startswith("not applicable")


def flip(gt, i):
    return "NO" if gt[i] == "YES" else "YES"


def test_gate_pass_weak_pass_and_robustness(real):
    items, gt, _ = real
    primary = [i for i in items if "edge" not in items[i]["tags"]]
    # wrong on every sample of 12 original items spread over many artefacts: 12/41 = 29%
    spread, seen = [], set()
    for i in primary:
        if items[i]["variant"] == "original" and items[i]["cluster"] not in seen:
            spread.append(i)
            seen.add(items[i]["cluster"])
    spread = spread[:12]
    st = all_correct(items, gt)
    st.update({(i, s): flip(gt, i) for i in spread for s in range(3)})
    out = A.analyse_arm(records_from(st), items, gt, "high", 129)
    assert out["primary"]["error"] == round(12 / 41, 4)
    assert all(v["holds"] for v in out["robustness"].values())
    assert out["gate"] == "PASS" and out["primary"]["ci95_cluster_bootstrap"][0] >= 0.15
    # 7 wrong items: 17% point estimate, but the bootstrap lower bound is below 15% -> weak pass
    st = all_correct(items, gt)
    st.update({(i, s): flip(gt, i) for i in spread[:7] for s in range(3)})
    out = A.analyse_arm(records_from(st), items, gt, "high", 129)
    assert out["primary"]["ci95_cluster_bootstrap"][0] < 0.15 <= out["primary"]["error"]
    assert out["gate"].startswith("WEAK PASS")
    # errors concentrated on fewer than 5 artefacts cannot pass
    few = [i for i in primary if items[i]["cluster"] in ("c02_cit_2a", "c06_cit_3b", "c19_streaming", "k05_crontab_default_roles")]
    st = all_correct(items, gt)
    st.update({(i, s): flip(gt, i) for i in few for s in range(3)})
    out = A.analyse_arm(records_from(st), items, gt, "high", 129)
    assert out["primary"]["error"] >= 0.15
    assert not out["robustness"]["artefacts_with_errors"]["holds"] and out["gate"].startswith("FAIL: the point")
    # errors only on planted edits cannot pass
    edits = [i for i in primary if items[i]["variant"] == "planted-edit"]
    st = all_correct(items, gt)
    st.update({(i, s): flip(gt, i) for i in edits for s in range(3)})
    out = A.analyse_arm(records_from(st), items, gt, "high", 129)
    assert out["primary"]["error"] < 0.15 or not out["robustness"]["planted_edits_excluded"]["holds"]
    assert not out["gate"].startswith(("PASS", "WEAK"))


def test_invalid_counts_as_error_but_never_as_direction(real):
    items, gt, _ = real
    st = all_correct(items, gt)
    no_restr = [i for i in items if gt[i] == "NO" and items[i]["direction"] == "restriction" and "edge" not in items[i]["tags"]]
    st.update({(no_restr[0], s): "UNPARSED" for s in range(3)})
    st[(no_restr[1], 0)] = "TRUNCATED"
    st[(no_restr[1], 1)] = "YES"  # an actual false approval
    out = A.analyse_arm(records_from(st), items, gt, "high", 129)
    fa = out["key_secondary_false_approval_restriction_NO"]
    assert fa["items"] == len(no_restr)
    assert fa["rate"] == round((1 / 3) / len(no_restr), 4)            # only the actual YES
    # the sensitivity drops invalid samples, so the all-UNPARSED item has no data and leaves the mean
    assert fa["rate_invalid_excluded"] == round((1 / 2) / (len(no_restr) - 1), 4)
    assert out["per_item"][no_restr[0]]["error"] == 1.0 and out["per_item"][no_restr[0]]["wrong_direction"] == 0
    assert out["invalid_samples"] == 4
    assert out["primary"]["invalid_excluded_sensitivity"] < out["primary"]["error"]


def test_item_without_samples_is_reported_and_counts_zero(real):
    items, gt, _ = real
    st = all_correct(items, gt)
    wrong = [i for i in items if "edge" not in items[i]["tags"]][:10]
    st.update({(i, s): flip(gt, i) for i in wrong for s in range(3)})
    for s in range(3):
        st[(wrong[0], s)] = "ENDPOINT_ERROR"
    out = A.analyse_arm(records_from(st), items, gt, "high", 129)
    assert out["items_without_model_outcome"] == [wrong[0]]
    assert out["per_item"][wrong[0]]["error"] is None
    assert out["primary"]["error"] == round(9 / 41, 4)   # kept in the denominator as 0


def originals_on_distinct_artefacts(items, n):
    out, seen = [], set()
    for i in items:
        if "edge" not in items[i]["tags"] and items[i]["variant"] == "original" and items[i]["cluster"] not in seen:
            out.append(i)
            seen.add(items[i]["cluster"])
    assert len(out) >= n
    return out[:n]


def only_failing(out):
    return sorted(k for k, v in out["robustness"].items() if not v["holds"])


def test_opus_review_case_twelve_endpoint_errors_now_fail(real):
    """Opus re-review B1: 12 endpoint errors (within the stop threshold) turned a 9.8% FAIL into 19.5%."""
    items, gt, _ = real
    pick = originals_on_distinct_artefacts(items, 12)
    st = all_correct(items, gt)
    for i in pick[:6]:   # 2 endpoint errors and 1 wrong answer each
        st.update({(i, 0): flip(gt, i), (i, 1): "ENDPOINT_ERROR", (i, 2): "ENDPOINT_ERROR"})
    for i in pick[6:]:   # 1 wrong answer in 3
        st[(i, 0)] = flip(gt, i)
    out = A.analyse_arm(records_from(st), items, gt, "high", 129)
    assert out["endpoint_errors"]["n"] == 12 <= out["endpoint_errors"]["stop_threshold"]
    assert out["primary"]["error"] == round(8 / 41, 4)                       # 0.1951 as run
    assert out["primary"]["endpoint_errors_imputed_correct"] == round(4 / 41, 4)
    assert only_failing(out) == ["endpoint_errors_imputed_correct"]           # every other condition holds
    assert out["gate"].startswith("FAIL: the point estimate") and "endpoint_errors_imputed_correct" in out["gate"]


def test_astra_review_case_14_63_to_19_51_now_fails(real):
    """Astra re-review B2: replacing 12 correct responses with endpoint errors moved 14.63% FAIL to 19.51%."""
    items, gt, _ = real
    pick = originals_on_distinct_artefacts(items, 14)
    st = all_correct(items, gt)
    for i in pick[:12]:
        st[(i, 0)] = flip(gt, i)
    for i in pick[12:]:
        st.update({(i, s): flip(gt, i) for s in range(3)})
    before = A.analyse_arm(records_from(st), items, gt, "high", 129)
    assert before["primary"]["error"] == round(6 / 41, 4) == 0.1463 and before["gate"].startswith("FAIL (closes")
    for i in pick[:12]:
        st[(i, 1)] = "ENDPOINT_ERROR"                                         # a correct response lost
    out = A.analyse_arm(records_from(st), items, gt, "high", 129)
    assert out["primary"]["error"] == round(8 / 41, 4) == 0.1951
    assert out["primary"]["endpoint_errors_imputed_correct"] == 0.1463
    assert only_failing(out) == ["endpoint_errors_imputed_correct"]
    assert out["gate"].startswith("FAIL") and "WEAK" not in out["gate"] and out["gate"] != "PASS"


def test_formatting_alone_cannot_create_a_pass(real):
    """Opus re-review B2: a pass that vanishes when INVALID samples are excluded is a FAIL, not a note."""
    items, gt, _ = real
    pick = originals_on_distinct_artefacts(items, 12)
    st = all_correct(items, gt)
    st.update({(i, s): "UNPARSED" for i in pick[:9] for s in range(3)})      # formatting failures
    st.update({(i, s): flip(gt, i) for i in pick[9:] for s in range(3)})       # real errors
    out = A.analyse_arm(records_from(st), items, gt, "high", 129)
    assert out["primary"]["error"] == round(12 / 41, 4) and out["primary"]["ci95_cluster_bootstrap"][0] >= 0.15
    assert out["primary"]["invalid_excluded_sensitivity"] == round(3 / 41, 4)
    assert only_failing(out) == ["invalid_excluded"]
    assert out["gate"].startswith("FAIL") and "invalid_excluded" in out["gate"]
    # the same errors as real wrong answers pass
    st.update({(i, s): flip(gt, i) for i in pick[:9] for s in range(3)})
    assert A.analyse_arm(records_from(st), items, gt, "high", 129)["gate"] == "PASS"


def test_t_quantile_and_interval():
    assert abs(A.t_quantile(0.975, 27) - 2.0518) < 1e-3
    assert abs(A.t_quantile(0.975, 10) - 2.2281) < 1e-3
    assert abs(A.t_quantile(0.975, 1) - 12.706) < 1e-2
    m, (lo, hi) = A.t_interval([0.0, 0.5, 1.0])
    assert m == 0.5 and abs((hi - m) - 4.3027 * 0.5 / 3 ** 0.5) < 1e-3


# ------------------------------------------------------------------------------------------------
# runner: stop rules, resume, midnight
# ------------------------------------------------------------------------------------------------

def test_runner_endpoint_error_stop_rule(tmp_path, study):
    runner, clients, _ = make_runner(tmp_path, study, lambda i, s: "error")
    assert runner.max_errors == 1  # floor(10% of 18)
    with pytest.raises(R.Stop):
        runner.run(study[1], SYSTEM)
    stop = json.loads((tmp_path / "high" / "STOP.json").read_text())
    assert stop["endpoint_errors"] == 2 and len(calls(clients)) == 2
    runner2, clients2, _ = make_runner(tmp_path, study, lambda i, s: "yes")
    with pytest.raises(R.Stop, match="never resumed"):
        runner2.run(study[1], SYSTEM)
    assert not calls(clients2)


def test_runner_global_error_aborts_without_rows(tmp_path, study):
    runner, clients, _ = make_runner(tmp_path, study, lambda i, s: "global" if (i, s) == ("X1", 0) else "yes")
    with pytest.raises(R.Abort):
        runner.run(study[1], SYSTEM)
    answers, _, _ = A.load_arm(tmp_path / "high")
    assert [(a["id"], a["sample"]) for a in answers] == [("X0", 0), ("X0", 1), ("X0", 2)]
    assert not (tmp_path / "high" / "STOP.json").exists()


def test_runner_resume_never_duplicates_or_replays(tmp_path, study):
    beh = lambda i, s: "error" if (i, s) == ("X0", 1) else ("global" if i == "X2" else "yes")
    runner, clients, _ = make_runner(tmp_path, study, beh)
    with pytest.raises(R.Abort):
        runner.run(study[1], SYSTEM)
    # simulate a crash after the ledger logged X1#2 but before its answers row was written
    path = tmp_path / "high" / "answers.jsonl"
    lines = path.read_text().splitlines()
    assert json.loads(lines[-1])["id"] == "X1"
    path.write_text("\n".join(lines[:-1]) + "\n")
    runner2, clients2, _ = make_runner(tmp_path, study, lambda i, s: "yes")
    runner2.run(study[1], SYSTEM)
    made = calls(clients2)
    assert ("X0", 1) not in made and ("X1", 2) not in made and len(made) == 12
    answers, ledgers, _ = A.load_arm(tmp_path / "high")
    records, _ = A.reconcile(answers, ledgers, study[2], study[3], "high")
    assert records[("X0", 1)]["status"] == "ENDPOINT_ERROR"
    assert records[("X1", 2)]["status"] == "YES" and records[("X1", 2)]["recovered_from_ledger"]
    assert len(answers) == 18


def test_runner_interrupted_call_is_final(tmp_path, study):
    runner, clients, _ = make_runner(tmp_path, study, lambda i, s: "yes")
    ledger = tmp_path / "high" / "ledger-2026-09-23.jsonl"
    ledger.parent.mkdir(parents=True)
    fc = FakeClient(ledger, "2026-09-23", study[3], None, lambda: datetime(2026, 9, 23, 11, tzinfo=timezone.utc))
    fc._write(fc._row("X3", 0, study[1]["X3"], SYSTEM, "started"))  # started, never finished
    runner.run(study[1], SYSTEM)
    assert ("X3", 0) not in calls(clients)
    answers, ledgers, _ = A.load_arm(tmp_path / "high")
    records, _ = A.reconcile(answers, ledgers, study[2], study[3], "high")
    assert records[("X3", 0)]["status"] == "ENDPOINT_ERROR"


@pytest.mark.parametrize("kind,reason", [("paid", "billing"), ("othermodel", "served model")])
def test_runner_billing_and_served_model_stop(tmp_path, study, kind, reason):
    runner, clients, _ = make_runner(tmp_path, study, lambda i, s: kind if (i, s) == ("X1", 1) else "yes")
    with pytest.raises(R.Stop, match=reason):
        runner.run(study[1], SYSTEM)
    assert len(calls(clients)) == 5


def test_runner_truncation_is_a_model_outcome_and_quota_aborts(tmp_path, study):
    runner, clients, _ = make_runner(tmp_path, study, lambda i, s: {"X0": "truncated", "X1": "junk"}.get(i, "yes"))
    runner.run(study[1], SYSTEM)
    answers, ledgers, _ = A.load_arm(tmp_path / "high")
    records, _ = A.reconcile(answers, ledgers, study[2], study[3], "high")
    assert {records[("X0", s)]["status"] for s in range(3)} == {"TRUNCATED"}
    assert {records[("X1", s)]["status"] for s in range(3)} == {"UNPARSED"}


def test_runner_quota_rejection_without_output_is_excluded_and_retried(tmp_path, study):
    runner, clients, _ = make_runner(tmp_path, study, lambda i, s: "quota" if (i, s) == ("X1", 0) else "yes")
    with pytest.raises(R.Abort, match="usage limit"):
        runner.run(study[1], SYSTEM)
    answers, ledgers, _ = A.load_arm(tmp_path / "high")
    assert len(answers) == 3                                      # no row for the rejected sample
    records, orphans = A.reconcile(answers, ledgers, study[2], study[3], "high", allow_incomplete=True)
    assert ("X1", 0) not in records and not orphans
    with pytest.raises(A.DataError, match="incomplete"):        # the analysis refuses until it is retried
        A.reconcile(answers, ledgers, study[2], study[3], "high")
    # after the reset: the same sample is retried (same account) in a fresh segment; not an endpoint error
    runner2, clients2, _ = make_runner(tmp_path, study, lambda i, s: "yes")
    runner2.run(study[1], SYSTEM)
    assert calls(clients2)[0] == ("X1", 0) and sorted(clients2) == ["ledger-2026-09-23-q1.jsonl"]
    answers, ledgers, _ = A.load_arm(tmp_path / "high")
    records, _ = A.reconcile(answers, ledgers, study[2], study[3], "high")
    assert records[("X1", 0)]["status"] == "YES" and records[("X1", 0)]["ledger"] == "ledger-2026-09-23-q1.jsonl"
    assert not any(r["status"] == "ENDPOINT_ERROR" for r in records.values())
    assert A.quota_excluded_attempts(ledgers) == 1


def test_runner_quota_rejection_after_output_is_recorded_and_aborts(tmp_path, study):
    runner, clients, _ = make_runner(tmp_path, study, lambda i, s: "quota_after_output" if i == "X1" else "yes")
    with pytest.raises(R.Abort, match="usage limit"):
        runner.run(study[1], SYSTEM)
    answers, _, _ = A.load_arm(tmp_path / "high")
    assert len(answers) == 4 and answers[-1]["status"] == "ENDPOINT_ERROR"


def test_a_replay_that_is_not_an_excluded_quota_rejection_is_refused(tmp_path, study):
    runner, clients, _ = make_runner(tmp_path, study, lambda i, s: "error" if (i, s) == ("X1", 0) else "yes")
    runner.run(study[1], SYSTEM)
    answers, ledgers, _ = A.load_arm(tmp_path / "high")
    (name, rows), = ledgers.items()
    again = [r for r in rows if (r["item_id"], r["sample_index"]) == ("X1", 0)]
    with pytest.raises(A.DataError, match="replay"):
        A.reconcile(answers, {name: rows, "ledger-2026-09-23-q1.jsonl": again}, study[2], study[3], "high")


@pytest.mark.parametrize("kind", ["paid", "othermodel", "mixed"])
def test_recovery_rechecks_billing_and_model_before_any_call(tmp_path, study, kind):
    """A crash after a bad call's ledger outcome but before its stop: the resumed run must stop, not call."""
    runner, clients, _ = make_runner(tmp_path, study, lambda i, s: kind if (i, s) == ("X1", 1) else "yes")
    with pytest.raises(R.Stop):
        runner.run(study[1], SYSTEM)
    (tmp_path / "high" / "STOP.json").unlink()                  # the stop was never written (crash)
    path = tmp_path / "high" / "answers.jsonl"
    path.write_text("".join(line + "\n" for line in path.read_text().splitlines()[:-1]))
    runner2, clients2, _ = make_runner(tmp_path, study, lambda i, s: "yes")
    with pytest.raises(R.Stop, match="billing" if kind == "paid" else "served model"):
        runner2.run(study[1], SYSTEM)
    assert not calls(clients2) and (tmp_path / "high" / "STOP.json").exists()


def test_mixed_reported_models_with_served_none_stop_the_run_and_the_analysis(tmp_path, study):
    runner, clients, _ = make_runner(tmp_path, study, lambda i, s: "mixed" if (i, s) == ("X2", 0) else "yes")
    with pytest.raises(R.Stop, match="served model"):
        runner.run(study[1], SYSTEM)
    assert len(calls(clients)) == 7
    answers, ledgers, _ = A.load_arm(tmp_path / "high")
    with pytest.raises(A.DataError, match="served model differs"):
        A.reconcile(answers, ledgers, study[2], study[3], "high", allow_incomplete=True)


def test_drift_is_checked_against_the_baseline_across_daily_ledgers(tmp_path, study):
    """Input tokens and endpoint controls are compared with the first segment, not reset each UTC day."""
    start = datetime(2026, 9, 23, 23, 40, tzinfo=timezone.utc)
    runner, clients, _ = make_runner(tmp_path, study, lambda i, s: "yes", start=start)
    runner.run(study[1], SYSTEM)
    answers, ledgers, _ = A.load_arm(tmp_path / "high")
    A.reconcile(answers, ledgers, study[2], study[3], "high")
    day1, day2 = "ledger-2026-09-23.jsonl", "ledger-2026-09-24.jsonl"
    # X0#0 moved to day 2 with a 1-token overhead shift: consistent within day 2, but not with X0's baseline
    # (its first successful call, X0#1 on day 1). A per-day check would never compare the two.
    rows1 = ledgers[day1]
    x0 = [r for r in rows1 if (r["item_id"], r["sample_index"]) == ("X0", 0)]
    moved = [dict(r, controls=dict(r["controls"], context_date="2026-09-24"),
                  timestamp="2026-09-24T00:30:00+00:00", input_tokens=101 if r["status"] == "ok" else None) for r in x0]
    bad = {day1: [r for r in rows1 if r not in x0], day2: moved + ledgers[day2]}
    answers2 = [dict(a, ledger=day2) if (a["id"], a["sample"]) == ("X0", 0) else a for a in answers]
    with pytest.raises(A.DataError, match="input tokens 101 drift from the baseline 100"):
        A.reconcile(answers2, bad, study[2], study[3], "high")
    same = {day1: bad[day1], day2: [dict(r, input_tokens=100) if r["status"] == "ok" else r for r in bad[day2]]}
    A.reconcile(answers2, same, study[2], study[3], "high")
    # a host update between days changes the endpoint controls: drift from the frozen baseline
    host = dict(ledgers, **{day2: [dict(r, controls=dict(r["controls"], host_release="26.0.0")) for r in ledgers[day2]]})
    with pytest.raises(A.DataError, match="control drift from the frozen baseline"):
        A.reconcile(answers, host, study[2], study[3], "high")


def test_runner_stops_on_cross_day_input_drift(tmp_path, study):
    start = datetime(2026, 9, 23, 23, 40, tzinfo=timezone.utc)
    runner, clients, _ = make_runner(tmp_path, study, lambda i, s: "yes", start=start)
    orig = FakeClient._row
    try:

        def row(self, item, s, prompt, system, status, **extra):
            if status == "ok" and self.day == "2026-09-24":
                extra["input_tokens"] = 101
            return orig(self, item, s, prompt, system, status, **extra)
        FakeClient._row = row
        with pytest.raises(R.Stop, match="drift"):
            runner.run(study[1], SYSTEM)
    finally:
        FakeClient._row = orig
    stop = json.loads((tmp_path / "high" / "STOP.json").read_text())
    assert any("drift from the baseline" in p for p in stop["problems"])


def test_runner_waits_for_utc_midnight_and_starts_a_new_segment(tmp_path, study):
    start = datetime(2026, 9, 23, 23, 40, tzinfo=timezone.utc)   # 20 min left; timeout 900 s + 120 s margin
    runner, clients, clock = make_runner(tmp_path, study, lambda i, s: "yes", start=start)
    runner.run(study[1], SYSTEM)
    assert sorted(clients) == ["ledger-2026-09-23.jsonl", "ledger-2026-09-24.jsonl"]
    answers, ledgers, _ = A.load_arm(tmp_path / "high")
    assert sorted(ledgers) == ["ledger-2026-09-23.jsonl", "ledger-2026-09-24.jsonl"]
    A.reconcile(answers, ledgers, study[2], study[3], "high")
    for name, rows in ledgers.items():   # no call started within timeout + margin of midnight
        for r in rows:
            t = datetime.fromisoformat(r["timestamp"])
            assert R.seconds_to_utc_midnight(t) >= 900 + R.MIDNIGHT_MARGIN_S


def test_billing_signal_detection():
    assert R.billing_signals([{"type": "system", "subtype": "init", "apiKeySource": "none"}]) == []
    assert R.billing_signals([{"type": "system", "subtype": "init", "apiKeySource": "/login managed key"}])
    assert R.billing_signals([{"type": "rate_limit_event", "rate_limit_info": {"isUsingOverage": True}}])
    assert not R.billing_signals([{"type": "rate_limit_event", "rate_limit_info": {"status": "allowed_warning",
                                                                                   "isUsingOverage": False}}])


# ------------------------------------------------------------------------------------------------
# freeze checks (in a throwaway git repository)
# ------------------------------------------------------------------------------------------------

def _git(root, *args):
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    for f in R.FROZEN_FILES:
        p = root / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"content of {f}\n")
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "inputs")
    monkeypatch.setattr(R, "ROOT", root)
    monkeypatch.setattr(R, "HERE", root / R.REL)
    monkeypatch.setattr(R, "claude_binary", lambda: ("claude", "binsha", R.frozen_arm("high")["cli_version"]))
    import ve_experiments.claude_cli as cc
    (tmp_path / "acct").mkdir()
    (tmp_path / "acct" / ".claude.json").write_text(json.dumps({"oauthAccount": {"accountUuid": ACCOUNT_UUID}}))
    monkeypatch.setattr(cc, "account_dir_for_label", lambda label: tmp_path / label)
    R.freeze("acct")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "freeze")
    R.stamp(run=fake_ots)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "timestamp the freeze")
    return root


ACCOUNT_UUID = "0b7d3c1e-1111-4222-8333-444455556666"


def fake_ots(cmd, **_):
    """Stands in for `ots stamp FILE`: writes FILE.ots with a real OpenTimestamps header for FILE's SHA-256."""
    assert tuple(cmd[:-1]) == R.OTS_CMD
    f = Path(cmd[-1])
    Path(f"{f}.ots").write_bytes(R.OTS_MAGIC + b"\x01\x08" + hashlib.sha256(f.read_bytes()).digest() + b"\xf0\x10pending")
    return subprocess.CompletedProcess(cmd, 0, "", "")


def test_ots_header_parser_matches_an_earlier_ve_receipt():
    root = Path(__file__).resolve().parent.parent / "experiments" / "T1c"
    assert R.ots_binds((root / "HASHES.ots").read_bytes(), (root / "HASHES").read_bytes())
    assert not R.ots_binds((root / "HASHES.ots").read_bytes(), b"other")


def test_freeze_record(repo):
    fr = json.loads((repo / R.REL / "FREEZE.json").read_text())
    assert fr["account_label"] == "acct" and fr["model"] == MODEL and fr["system_sha256"] == sha(SYSTEM)
    assert "ve_experiments/claude_cli.py" in fr["files"] and "ve/stream_audit.py" in fr["files"]
    assert len(fr["frozen_commit"]) == 40 and fr["claude_binary_sha256"] == "binsha"
    assert fr["arms"]["high"]["effort"] == "high" and "context_date" not in fr["arms"]["high"]
    assert R.check_freeze("acct", "high")["account_label"] == "acct"
    assert fr["account_uuid_sha256"] == sha(f"claude-oauth-account:{ACCOUNT_UUID}")
    assert ACCOUNT_UUID not in (repo / R.REL / "FREEZE.json").read_text()      # only the hash is kept
    assert fr["endpoint_controls"] == R.endpoint_controls()


def test_freeze_checks_the_oauth_account_uuid(repo, tmp_path):
    (tmp_path / "acct" / ".claude.json").write_text(json.dumps({"oauthAccount": {"accountUuid": "other-uuid"}}))
    with pytest.raises(SystemExit, match="OAuth account UUID") as e:
        R.check_freeze("acct", "high")
    assert "other-uuid" not in str(e.value)
    (tmp_path / "acct" / ".claude.json").unlink()
    with pytest.raises(SystemExit, match="OAuth account UUID"):
        R.check_freeze("acct", "high")


def test_freeze_refuses_without_account_uuid(repo, tmp_path, monkeypatch):
    import ve_experiments.claude_cli as cc
    (tmp_path / "bare").mkdir()
    monkeypatch.setattr(cc, "account_dir_for_label", lambda label: tmp_path / label)
    with pytest.raises(SystemExit, match="no OAuth account UUID"):
        R.freeze("bare")


def test_run_requires_the_committed_opentimestamps_stamp(repo):
    stamp_file, ots = repo / R.STAMP, repo / R.OTS
    text = stamp_file.read_text()
    assert text.splitlines()[0].split()[0] == R.sha_file(repo / R.REL / "FREEZE.json")
    assert text.splitlines()[1].split()[0] == R.freeze_commit()
    # a tampered receipt
    ots.write_bytes(ots.read_bytes()[:40] + b"\x00" * 24 + ots.read_bytes()[64:])
    _git(repo, "commit", "-q", "-am", "tamper")
    with pytest.raises(SystemExit, match="does not bind"):
        R.check_freeze("acct", "high")
    # no receipt at all
    _git(repo, "rm", "-q", R.OTS)
    _git(repo, "commit", "-q", "-m", "drop receipt")
    with pytest.raises(SystemExit, match="missing or not committed"):
        R.check_freeze("acct", "high")


def test_stamp_must_name_the_current_freeze(repo):
    fz = repo / R.REL / "FREEZE.json"
    fz.write_text(fz.read_text().replace('"k": 3', '"k": 4'))
    _git(repo, "commit", "-q", "-am", "edit the freeze after stamping")
    with pytest.raises(SystemExit, match="does not name the current FREEZE.json"):
        R.check_freeze("acct", "high")


def test_stamp_refuses_an_uncommitted_freeze(repo):
    (repo / R.REL / "FREEZE.json").write_text("{}\n")
    with pytest.raises(SystemExit, match="clean committed tree"):
        R.stamp(run=fake_ots)


def test_freeze_rejects_wrong_account(repo):
    with pytest.raises(SystemExit, match="not the frozen account"):
        R.check_freeze("someone-else", "high")


def test_freeze_rejects_dirty_tree_and_changed_inputs(repo):
    p = repo / "ve_experiments" / "claude_cli.py"
    p.write_text("SYSTEM = 'changed'\n")
    with pytest.raises(SystemExit, match="not clean"):
        R.check_freeze("acct", "high")
    _git(repo, "commit", "-q", "-am", "change endpoint")
    with pytest.raises(SystemExit, match="changed since the frozen commit"):
        R.check_freeze("acct", "high")


def test_freeze_rejects_new_file_under_covered_paths(repo):
    (repo / "ve" / "extra.py").write_text("x = 1\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "new dep")
    with pytest.raises(SystemExit, match="changed since the frozen commit"):
        R.check_freeze("acct", "high")


def test_freeze_ignores_run_outputs_and_rejects_binary_change(repo, monkeypatch):
    runs = repo / R.REL / "runs" / "high"
    runs.mkdir(parents=True)
    (runs / "answers.jsonl").write_text("{}\n")
    R.check_freeze("acct", "high")
    monkeypatch.setattr(R, "claude_binary", lambda: ("claude", "other", "9.9.9 (Claude Code)"))
    with pytest.raises(SystemExit, match="claude binary"):
        R.check_freeze("acct", "high")


def test_freeze_refuses_dirty_tree_at_freeze_time(repo):
    (repo / "stray.txt").write_text("x")
    with pytest.raises(SystemExit, match="clean committed tree"):
        R.freeze("acct")


# ------------------------------------------------------------------------------------------------
# prompt rendering
# ------------------------------------------------------------------------------------------------

def test_cedar_comment_stripping_respects_strings():
    src = ('// header\npermit (principal, action, resource)\n'
           'when { resource.url == "http://x//y" && principal.n == "a\\"//b" }; // trailing\n\n\n// end\n')
    out = RP.strip_cedar_comments(src)
    assert out == ('permit (principal, action, resource)\n'
                   'when { resource.url == "http://x//y" && principal.n == "a\\"//b" };')


def test_rendered_prompts_have_no_comments_and_match_hashes():
    rows = [json.loads(line) for line in (D / "prompts.jsonl").read_text().splitlines()]
    assert len(rows) == 43
    for r in rows:
        assert hashlib.sha256(r["prompt"].encode()).hexdigest() == r["sha256"]
        art = r["prompt"].split("Domain of the question")[0]
        assert "//" not in art and "\n#" not in art and " # " not in art, r["id"]
    d39 = next(r["prompt"] for r in rows if r["id"] == "D39")
    assert "resources: [\"secrets\"]" in d39 and "'true'" not in d39
