"""fid-mech-b5: the batch runner (plan 7, 2e, 10) on the B2 fixture case with an injected evaluator, host and clock.

No test needs Lean or a real document: the kernel run is a fake evaluator returning projections, the host's load and
memory are fakes, and every wait advances an injected clock (no sleep, no short timeout).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import threading
from pathlib import Path

import pytest

from tools.fidmech import __main__ as CLI
from tools.fidmech import adapters
from tools.fidmech import manifests
from tools.fidmech import mutants as M
from tools.fidmech import runner as RUN
from tools.fidmech import worker as W

ROOT = Path(__file__).resolve().parents[1]
B2 = ROOT / "tests/data/fidmech/b2"
DOC = "anthropic-rsp"
DIGEST = "a" * 64
RULE = "Rule 1. Every situation must share the final report with the Board."


class Clock:
    def __init__(self):
        self.now, self.lock = 0.0, threading.Lock()

    def __call__(self):
        return self.now

    def advance(self, seconds):
        with self.lock:
            self.now += seconds


class FakeHost:
    """1-min loads given in order (the last repeats); the 5-min load fixed."""

    def __init__(self, load1=(1.0,), load5=1.0):
        self.load1, self.load5, self.reads = list(load1), load5, 0

    def loadavg(self):
        self.reads += 1
        value = self.load1.pop(0) if len(self.load1) > 1 else self.load1[0]
        return (value, self.load5, self.load5)

    def mem_available(self):
        return 100 * 10**9

    def cgroup_room(self):
        return None


def projection(answer):
    return adapters.Projection({"Q1": (("ve", answer),)}, {"Q1": ("r-share",)}, {"Q1": ()}, {"Q1": True})


@pytest.fixture
def tree(tmp_path):
    """A worktree whose only use case is the B2 fixture case, named as RSP."""
    root = tmp_path / "tree"
    shutil.copytree(B2, root / "usecases" / DOC)
    return root


def record(tree, mid, new_rule, op="drop-conjunct", unit="r-share", parse="ok", equivalent=None):
    files = M.case_files(tree / "usecases" / DOC)
    edits = M.line_edits("rules.d1.ve", files["rules.d1.ve"], files["rules.d1.ve"].replace(RULE, new_rule))
    return {"id": mid, "document": DOC, "unit": unit, "class": "structural", "op": op, "where": "rule",
            "edits": edits, "equivalent": equivalent, "parse": parse, "seed": None, "generator": "fidmech/1",
            "inputs_sha256": DIGEST}


def deps(tree, records, answers, *, host=None, clock=None, digest=DIGEST, calls=None, step=0.0, leak=None):
    """Deps with a fake prepare (the records), a fake evaluator ({mutant id: answer}, baseline "ALL") and no text
    checks unless the test passes them."""
    clock = clock or Clock()
    calls = [] if calls is None else calls
    state = {"leaked": False}

    def evaluate(mutant, limit):
        calls.append(mutant.id)
        clock.advance(step)
        if leak and mutant.id == leak:
            state["leaked"] = True
        if mutant.id == "baseline":
            return projection("NONE" if state["leaked"] else "ALL")
        return projection(answers[mutant.id])

    def slot(name, document, scratch):
        return W.Worker(document, tree, scratch, name=name, evaluate=evaluate, clock=clock,
                        cpu_clock=lambda: 0.0, reset=lambda: None)
    return RUN.Deps(host=host or FakeHost(), prepare=lambda *a: RUN.Prepared(records, digest),
                    slot=slot, text=lambda document: None, lean_start=None, clock=clock, sleep=clock.advance,
                    log=lambda *a: None, worktree=tree)


def lines(out):
    return {x["record"]["id"]: x for x in map(json.loads, (out / "results.jsonl").read_text().splitlines())}


def test_the_admission_limits_are_the_plans():
    assert (RUN.MAX_WORKERS, RUN.MAX_LOAD1, RUN.REFUSE_LOAD5, RUN.EXIT_REFUSED) == (16, 24, 44, 75)
    assert RUN.MIN_MEM_AVAILABLE == 4 * 10**9


def test_a_five_minute_load_of_50_exits_75_and_runs_nothing(tmp_path, monkeypatch):
    """Plan 10 'admission': fake loadavg 50 -> exit 75, nothing generated, written or run."""
    monkeypatch.setattr(RUN.Host, "loadavg", lambda self: (50.0, 50.0, 50.0))
    monkeypatch.setattr(RUN, "prepare", lambda *a: pytest.fail("mutants were generated"))
    out = tmp_path / "out"
    assert CLI.main(["batch", "--doc", "RSP", "--jobs", "auto", "--out", str(out)]) == 75
    assert not out.exists()


def test_admission_waits_at_load_30_logs_the_wait_and_dispatches_at_10(tree, tmp_path):
    clock, logged = Clock(), []
    host = FakeHost(load1=(30.0, 30.0, 30.0, 10.0), load5=10.0)
    d = deps(tree, [record(tree, "m1", RULE.replace(" with the Board", ""))], {"m1": "NONE"}, host=host, clock=clock)
    d.log = logged.append
    summary = RUN.run(DOC, tmp_path / "out", jobs=1, deps=d)
    assert summary["measurements"]["admission_wait_s"] == 2 * RUN.POLL_S
    assert any(m.startswith("admission wait: 1-min load 30.0 >= 24") for m in logged)
    assert any(m.startswith("admitted after 30.0 s") for m in logged)
    assert lines(tmp_path / "out")["m1"]["record"]["verdict"]["K"] == "killed"


def test_the_budget_stops_dispatch_and_the_rest_is_not_run(tree, tmp_path, capsys):
    recs = [record(tree, f"m{i}", RULE.replace("final ", "x" * i + " ")) for i in range(1, 4)]
    calls = []
    d = deps(tree, recs, {"m1": "NONE", "m2": "NONE", "m3": "NONE"}, calls=calls, step=60.0)
    summary = RUN.run(DOC, tmp_path / "out", jobs=1, budget=100, deps=d)
    got = {k: v["record"]["verdict"]["K"] for k, v in lines(tmp_path / "out").items()}
    assert got == {"m1": "killed", "m2": "not-run", "m3": "not-run"}
    assert summary["not_run"] == 2 and "m2" not in calls and "m3" not in calls


def test_resume_on_a_matching_inputs_sha256_continues_and_a_mismatch_refuses(tree, tmp_path):
    recs = [record(tree, f"m{i}", RULE.replace("final ", "x" * i + " ")) for i in range(1, 4)]
    answers = {"m1": "NONE", "m2": "ALL", "m3": "NONE"}
    RUN.run(DOC, tmp_path / "first", jobs=1, budget=100, deps=deps(tree, recs, answers, step=60.0))
    calls = []
    summary = RUN.run(DOC, tmp_path / "second", jobs=1, resume=tmp_path / "first/results.jsonl",
                      deps=deps(tree, recs, answers, calls=calls))
    got = {k: v["record"]["verdict"]["K"] for k, v in lines(tmp_path / "second").items()}
    assert got == {"m1": "killed", "m2": "survived", "m3": "killed"}
    assert "m1" not in calls and {"m2", "m3"} <= set(calls) and summary["kept"] == 1
    calls = []
    with pytest.raises(RUN.Refused) as refused:
        RUN.run(DOC, tmp_path / "third", jobs=1, resume=tmp_path / "first/results.jsonl",
                deps=deps(tree, recs, answers, digest="b" * 64, calls=calls))
    assert refused.value.code == RUN.EXIT_MISMATCH and calls == [] and not (tmp_path / "third").exists()


def test_an_inputs_file_whose_sha256_differs_is_refused_before_anything_runs(tree, tmp_path):
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    for name in manifests.SHA256:
        (inputs / name).write_text("[]\n")
    pins = {name: hashlib.sha256(b"[]\n").hexdigest() for name in manifests.SHA256}
    assert manifests.load(inputs, pins)["plants"] == []
    with pytest.raises(manifests.InputsError, match="is not the pinned"):
        manifests.load(inputs)
    calls = []
    d = deps(tree, [], {}, calls=calls)
    d.prepare = lambda *a: pytest.fail("mutants were generated")
    with pytest.raises(RUN.Refused) as refused:
        RUN.run(DOC, tmp_path / "out", jobs=1, inputs=inputs, deps=d)
    assert refused.value.code == RUN.EXIT_MISMATCH and calls == [] and not (tmp_path / "out").exists()


def test_an_answer_turning_undecided_is_inconclusive_and_a_decided_change_kills(tree, tmp_path):
    recs = [record(tree, "m-und", RULE.replace("final ", "")), record(tree, "m-kill", RULE.replace("Board", "CEO")),
            record(tree, "m-same", RULE.replace("the final", "a final"))]
    d = deps(tree, recs, {"m-und": "UNDECIDED (resource limit)", "m-kill": "NONE", "m-same": "ALL"})
    RUN.run(DOC, tmp_path / "out", jobs=2, deps=d)
    got = {k: (v["record"]["verdict"]["K"], v["record"]["kernel"]["inconclusive"])
           for k, v in lines(tmp_path / "out").items()}
    assert got == {"m-und": ("inconclusive", ["Q1"]), "m-kill": ("killed", []), "m-same": ("survived", [])}


def test_a_worker_with_a_leaked_module_global_makes_the_batch_invalid(tree, tmp_path):
    """Plan 10 'sentinel': after the leaking mutant every baseline differs, so its slot's sentinel fails, the
    mutant is re-queued once, and the slot's last sentinel makes the batch INVALID."""
    recs = [record(tree, "m-leak", RULE.replace("final ", ""))]
    calls = []
    summary = RUN.run(DOC, tmp_path / "out", jobs=1, deps=deps(tree, recs, {"m-leak": "ALL"}, calls=calls,
                                                                 leak="m-leak"))
    assert summary["status"] == "INVALID" and summary["sentinels"]["failed"] >= 1
    assert calls.count("m-leak") == 2
    assert lines(tmp_path / "out")["m-leak"]["record"]["sentinel_ok"] is False


def test_a_clean_parallel_batch_is_ok_and_runs_a_sentinel_per_slot(tree, tmp_path):
    recs = [record(tree, f"m{i}", RULE.replace("final ", "x" * i + " ")) for i in range(1, 6)]
    calls = []
    summary = RUN.run(DOC, tmp_path / "out", jobs=3,
                      deps=deps(tree, recs, {f"m{i}": "NONE" for i in range(1, 6)}, calls=calls))
    assert summary["status"] == "ok" and summary["sentinels"]["failed"] == 0
    assert 1 <= summary["measurements"]["peak_concurrency"] <= 3
    assert sorted(c for c in calls if c != "baseline") == [f"m{i}" for i in range(1, 6)]


def test_a_stillborn_mutant_is_listed_never_run_and_never_scored(tree, tmp_path):
    recs = [record(tree, "m-ok", RULE.replace("final ", "")),
            record(tree, "m-dead", RULE.replace("must", "mustnt"), parse="stillborn")]
    calls = []
    summary = RUN.run(DOC, tmp_path / "out", jobs=1, deps=deps(tree, recs, {"m-ok": "NONE"}, calls=calls))
    assert summary["stillborn"] == 1 and "m-dead" not in calls
    assert set(lines(tmp_path / "out")) == {"m-ok"}
    listed = [json.loads(x)["id"] for x in (tmp_path / "out/mutants.jsonl").read_text().splitlines()]
    assert "m-dead" in listed


# ---- text-check kills (plan 2e) ---------------------------------------------------------------------------------

def text_case(tmp_path, bare=False):
    case = tmp_path / DOC
    shutil.copytree(B2, case)
    if bare:
        legend(case, "report_shared", description="section 3 at {0}")
    return case


def legend(case, name, description=None, act=None):
    env = json.loads((case / "environment.d1.json").read_text())
    entry = env["vocabulary"]["predicates"][name]
    if description is not None:
        entry["description"] = description
    if act is not None:
        entry["regulated"]["act"] = act
    (case / "environment.d1.json").write_text(json.dumps(env))


def env_record(case, change, unit="r-share"):
    files = M.case_files(case)
    env = json.loads(files["environment.d1.json"])
    change(env["vocabulary"]["predicates"])
    edits = M.line_edits("environment.d1.json", files["environment.d1.json"], json.dumps(env))
    return {"id": "m", "unit": unit, "edits": edits}


def checks(case):
    return RUN.TextChecks(case, (case / "source.txt").read_bytes(), case / "fidmech/boundaries.json")


def test_a_mutant_on_a_unit_whose_legend_is_bare_at_baseline_does_not_kill_by_l2(tmp_path):
    """Plan 10 'text-check kill': the baseline already has L2b on report_shared, so the mutant's L2b is the same
    standing hit and kills nothing; on a clean baseline the same edit that bares the legend kills."""
    def act(preds):
        preds["report_shared"]["regulated"]["act"] = "{0} share the report with the Board"
    tc = checks(text_case(tmp_path / "bare", bare=True))
    assert ("L2b", "report_shared", None) in tc.keys
    verdicts, new, error = tc.verdicts(env_record(tc.case, act))
    assert verdicts["L2"] == "survived" and not [h for h in new if h["class"] == "L2b"] and error is None

    def bare(preds):
        preds["report_shared"]["description"] = "section 3 at {0}"
    tc = checks(text_case(tmp_path / "clean"))
    verdicts, new, _ = tc.verdicts(env_record(tc.case, bare))
    assert verdicts["L2"] == "killed" and [h["class"] for h in new] == ["L2b"]


def test_a_new_hit_away_from_the_mutated_unit_kills_nothing(tmp_path):
    tc = checks(text_case(tmp_path))
    files = M.case_files(tc.case)
    old = 'section 1 "We will keep records of every review."'
    edits = M.line_edits("rules.d1.ve", files["rules.d1.ve"], files["rules.d1.ve"].replace(old, 'section 1 "We will keep records"'))
    near, _, _ = tc.verdicts({"id": "m", "unit": "r-records", "edits": edits})
    far, _, _ = tc.verdicts({"id": "m", "unit": "r-share", "edits": edits})
    assert near["L1"] == "killed" and far["L1"] == "survived"


def test_the_batch_writes_each_mutants_text_verdicts_run_beside_its_kernel_run(tree, tmp_path):
    case = tree / "usecases" / DOC
    files = M.case_files(case)
    old = '"We will share the final report with the Board."'
    edits = M.line_edits("rules.d1.ve", files["rules.d1.ve"], files["rules.d1.ve"].replace(old, '"We will share the"'))
    rec = {**record(tree, "m-cut", RULE), "edits": edits}
    d = deps(tree, [rec, record(tree, "m-k", RULE.replace("final ", ""))], {"m-cut": "ALL", "m-k": "NONE"})
    d.text = lambda document: checks(case)
    RUN.run(DOC, tmp_path / "out", jobs=2, budget=None, deps=d)
    got = lines(tmp_path / "out")
    assert got["m-cut"]["record"]["verdict"]["L1"] == "killed" and got["m-cut"]["record"]["verdict"]["K"] == "survived"
    assert got["m-cut"]["text"]["new_hits"][0]["block"] == "r-share"
    assert got["m-k"]["record"]["verdict"]["K"] == "killed"
    assert (tmp_path / "out/textcheck.json").exists()


TOY = ROOT / "tests/data/fidmech/worker"


def test_a_fresh_run_is_reaped_with_its_own_cpu_and_peak_rss_and_its_stderr_names_a_failure(tmp_path):
    """The runner's per-run measurements: evaluate_fresh reaps its process with os.wait4 (one entry per run in
    Worker.usage, CPU and peak RSS of that process alone), and a failing process's error carries its stderr."""
    from subprocesses import HANG_TIMEOUT
    root = tmp_path / "toy"
    shutil.copytree(TOY, root)
    run_py = root / "usecases" / DOC / "run.py"
    (root / "usecases" / DOC / "run.py.txt").rename(run_py)
    worker = W.Worker(DOC, root, tmp_path / "scratch", fresh=True)
    ok = worker.run(W.BASELINE, HANG_TIMEOUT)
    broken = worker.run(W.Mutant("m-raise", {f"{DOC}/run.py": run_py.read_text() + "\nraise RuntimeError('planted')\n"}),
                        HANG_TIMEOUT)
    assert ok.status == "ok" and broken.status == "error" and "planted" in broken.error
    assert len(worker.usage) == 2 and all(rss > 2**20 for _, rss in worker.usage)  # the peak RSS of each run


def _args(out, **kw):
    import argparse
    base = {"doc": DOC, "out": str(out), "jobs": "1", "budget": None, "resume": None, "inputs": None}
    return argparse.Namespace(**{**base, **kw})


def test_the_exit_code_is_0_for_an_ok_batch_1_for_an_invalid_one_and_2_when_the_out_dir_holds_results(tree,
                                                                                                          tmp_path):
    recs = [record(tree, "m1", RULE.replace("final ", ""))]
    assert RUN.main(_args(tmp_path / "ok"), deps(tree, recs, {"m1": "NONE"})) == 0
    assert RUN.main(_args(tmp_path / "bad"), deps(tree, recs, {"m1": "ALL"}, leak="m1")) == 1
    assert RUN.main(_args(tmp_path / "ok"), deps(tree, recs, {"m1": "NONE"})) == 2


def test_a_budget_of_zero_runs_no_mutant_and_reads_not_run_never_a_verdict(tree, tmp_path):
    recs = [record(tree, f"m{i}", RULE.replace("final ", "x" * i + " ")) for i in range(1, 3)]
    calls = []
    summary = RUN.run(DOC, tmp_path / "out", jobs=2, budget=0, deps=deps(tree, recs, {}, calls=calls))
    assert calls == ["baseline"] and summary["not_run"] == 2 and summary["ran"] == 0
    assert {v["record"]["verdict"]["K"] for v in lines(tmp_path / "out").values()} == {"not-run"}
    assert summary["measurements"]["cpu_h_per_100"] is None


def test_a_batch_that_dies_leaves_its_confirmed_results_and_resumes_from_them(tree, tmp_path, monkeypatch):
    """results.partial.jsonl holds each result a good sentinel confirmed; a batch killed after that resumes from
    it and runs only the rest."""
    monkeypatch.setattr(W, "SENTINEL_EVERY", 1)
    recs = [record(tree, f"m{i}", RULE.replace("final ", "x" * i + " ")) for i in range(1, 4)]
    answers = {"m1": "NONE", "m2": "ALL", "m3": "NONE"}
    d = deps(tree, recs, answers)
    real = d.slot

    def dying(name, document, scratch):
        worker = real(name, document, scratch)
        evaluate = worker.evaluate

        def run(mutant, limit):
            if mutant.id == "m3":
                raise KeyboardInterrupt  # the batch process dies (Worker.run does not catch it)
            return evaluate(mutant, limit)
        worker.evaluate = run
        return worker
    d.slot = dying
    with pytest.raises(KeyboardInterrupt):
        RUN.run(DOC, tmp_path / "dead", jobs=1, deps=d)
    partial = tmp_path / "dead/results.partial.jsonl"
    assert not (tmp_path / "dead/results.jsonl").exists()
    assert {k: v["record"]["verdict"]["K"] for k, v in lines_of(partial).items()} == {"m1": "killed", "m2": "survived"}
    calls = []
    RUN.run(DOC, tmp_path / "again", jobs=1, resume=partial, deps=deps(tree, recs, answers, calls=calls))
    assert [c for c in calls if c != "baseline"] == ["m3"]
    assert {k: v["record"]["verdict"]["K"] for k, v in lines(tmp_path / "again").items()} == {
        "m1": "killed", "m2": "survived", "m3": "killed"}
    with pytest.raises(RUN.Refused):  # a dead batch's out dir is not silently reused
        RUN.run(DOC, tmp_path / "dead", jobs=1, deps=deps(tree, recs, answers))


def lines_of(path):
    return {x["record"]["id"]: x for x in map(json.loads, path.read_text().splitlines())}


# ---- a result no good sentinel confirmed (fid-mech-b5 review F1) ------------------------------------------------

def test_resume_runs_again_a_result_its_sentinel_marked_invalid(tree, tmp_path):
    """F1 probe: the first batch is INVALID (m-leak's sentinels fail); a resume from it keeps no INVALID line and
    runs m-leak again, so the resumed batch is ok only on a confirmed result."""
    recs = [record(tree, "m-leak", RULE.replace("final ", ""))]
    first = RUN.run(DOC, tmp_path / "a", jobs=1, deps=deps(tree, recs, {"m-leak": "ALL"}, leak="m-leak"))
    assert first["status"] == "INVALID" and first["invalid"] == 1
    assert RUN.read_resume(tmp_path / "a/results.jsonl", DIGEST) == {}
    calls = []
    second = RUN.run(DOC, tmp_path / "b", jobs=1, resume=tmp_path / "a/results.jsonl",
                     deps=deps(tree, recs, {"m-leak": "ALL"}, calls=calls))
    assert "m-leak" in calls and second["kept"] == 0 and second["status"] == "ok" and second["invalid"] == 0
    assert lines(tmp_path / "b")["m-leak"]["record"]["sentinel_ok"] is True


def test_a_requeued_mutant_the_budget_cuts_is_not_run_and_never_counted_as_ran(tree, tmp_path):
    """F1 sweep: m-leak runs (killed), its sentinel fails, it is re-queued, then the budget cuts it: its line is
    not-run (no INVALID decided K) and it is counted once, as not run."""
    recs = [record(tree, "m-leak", RULE.replace("final ", ""))]
    summary = RUN.run(DOC, tmp_path / "out", jobs=1, budget=100,
                      deps=deps(tree, recs, {"m-leak": "NONE"}, leak="m-leak", step=60.0))
    got = lines(tmp_path / "out")["m-leak"]["record"]
    assert (got["verdict"]["K"], got["sentinel_ok"]) == ("not-run", False)
    assert (summary["ran"], summary["not_run"], summary["invalid"]) == (0, 1, 0)
    assert summary["measurements"]["per_mutant_s"] is None


def scripted(tree, sentinels, calls):
    """A slot whose sentinels (every baseline after the first) give the scripted results (True: the baseline)."""
    clock, script, seen = Clock(), list(sentinels), {"baselines": 0}

    def evaluate(mutant, limit):
        calls.append(mutant.id)
        if mutant.id != "baseline":
            return projection("NONE")
        seen["baselines"] += 1
        return projection("ALL" if seen["baselines"] == 1 or script.pop(0) else "NONE")

    def slot(name, document, scratch):
        return W.Worker(document, tree, scratch, name=name, evaluate=evaluate, clock=clock,
                        cpu_clock=lambda: 0.0, reset=lambda: None)
    return slot


def test_a_result_invalid_twice_makes_the_batch_invalid_though_every_last_sentinel_holds(tree, tmp_path,
                                                                                        monkeypatch):
    """F1 sweep (worker.run_batch's rule): m1's sentinel fails, it is re-queued and its sentinel fails again; the
    slot's last sentinel holds. The batch is INVALID, m1 reads INVALID and stays out of results.partial.jsonl, and a
    resume runs m1 alone."""
    from tools.fidmech import records as R
    monkeypatch.setattr(W, "SENTINEL_EVERY", 1)
    recs = [record(tree, f"m{i}", RULE.replace("final ", "x" * i + " ")) for i in range(1, 4)]
    calls = []
    d = deps(tree, recs, {})
    d.slot = scripted(tree, [False, False, True, False, True], calls)
    summary = RUN.run(DOC, tmp_path / "out", jobs=1, deps=d)
    assert [c for c in calls if c != "baseline"] == ["m1", "m2", "m3", "m1", "m2"]
    assert summary["status"] == "INVALID" and summary["invalid"] == 1 and summary["ran"] == 3
    got = lines(tmp_path / "out")
    assert {k: R.k_reading(v["record"]) for k, v in got.items()} == {"m1": R.INVALID, "m2": "killed", "m3": "killed"}
    assert set(lines_of(tmp_path / "out/results.partial.jsonl")) == {"m2", "m3"}
    calls = []
    again = RUN.run(DOC, tmp_path / "again", jobs=1, resume=tmp_path / "out/results.jsonl",
                    deps=deps(tree, recs, {"m1": "NONE"}, calls=calls))
    assert [c for c in calls if c != "baseline"] == ["m1"] and again["status"] == "ok" and again["kept"] == 2
