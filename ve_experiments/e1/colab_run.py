"""E1 on the open-weight judges: `uv run python -m ve_experiments.e1.colab_run export|submit|fetch|score|hosted <split> <job id>`.

export  writes experiments/E1/colab/<job id>/ : every E1 cell (5 views x {none, attacker}) and every E1b prompt
        of the split, once, for all vllm judges of experiments/E1/judges.json (one job per split).
submit  sends the job to the Colab queue.          fetch  waits for it and downloads the outputs.
score   imports the outputs into the cache and replays them through `runner.run` (E1) and the E1b scorer,
        writing experiments/E1/runs/<job id>/ and experiments/E1/runs/<job id>-e1b/.

The scored split is refused by `experiment_requests` and `runner.run` until PREREG.md is committed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ..colab import ColabJobRunner, exported_keys, export_job, uncached, experiment_requests, import_outputs, is_batch_judge, model_id
from ..llm import LLMClient
from ..runner import run
from .balance import check as check_balance
from .pilot import E1, e1b_experiment, experiment, load_candidates
from .prompts import EXPLANATIONS, MAX_NEW_TOKENS
from .views import VIEWS

JUDGES_FILE = E1 / "judges.json"


def batch_judges() -> list[dict]:
    return [j for j in json.loads(JUDGES_FILE.read_text(encoding="utf-8"))["judges"] if is_batch_judge(j["judge"])]


def usable(split: str) -> list[dict]:  # used by the dev diagnostic
    return [c for c in load_candidates(name=split) if c["split"] == split and c.get("explanation")]


def hosted_judges() -> list[str]:
    return [j["judge"] for j in json.loads(JUDGES_FILE.read_text(encoding="utf-8"))["judges"] if not is_batch_judge(j["judge"])]


def experiments(split: str, judges: list[str] | None = None) -> tuple:
    if split == "scored":
        check_balance(split)  # raises BalanceError: explanations must not reveal the label through style
    judges = judges or [j["judge"] for j in batch_judges()]
    cands = load_candidates(name=split)
    return experiment(cands, VIEWS, EXPLANATIONS, judges), e1b_experiment(cands, judges)


def main() -> None:
    what, split, job_id = sys.argv[1:4]
    client = LLMClient()
    job_dir, results_dir = E1 / "colab" / job_id / "job", E1 / "colab" / job_id / "results"
    if what == "export":
        exp, exp_b = experiments(split)  # experiment_requests raises for "scored" unless the PREREG is frozen
        specs = [{"id": model_id(j["judge"]), **j.get("vllm_spec", {})} for j in batch_judges()]  # order = run order
        if "--a100" in sys.argv:  # engine arguments that only exist to fit the L4 (judges.json, "budget" note)
            specs = [{k: v for k, v in sp.items() if k not in ("enforce_eager", "max_num_seqs", "gpu_memory_utilization")} for sp in specs]
        reqs = experiment_requests(exp, split, client) + experiment_requests(exp_b, split, client)
        if "--only-uncached" in sys.argv:  # dev reruns: cells whose prompts did not change are replayed from the cache
            reqs = uncached(client, reqs)
        print(export_job(job_dir, job_id, reqs, specs, MAX_NEW_TOKENS))
    elif what == "submit":
        print(ColabJobRunner().submit(job_dir))
    elif what == "fetch":
        print(ColabJobRunner().wait_fetch(job_id, results_dir))
    elif what == "hosted":  # the hosted judges of judges.json, live, through the same runner (E1 then E1b)
        exp, exp_b = experiments(split, hosted_judges())
        live = LLMClient(timeout_s=600)
        print(run(exp, live, split, out_dir=E1 / "runs" / job_id))
        print(run(exp_b, live, split, out_dir=E1 / "runs" / f"{job_id}-e1b"))
    elif what == "score":
        exp, exp_b = experiments(split)
        reqs = experiment_requests(exp, split, client) + experiment_requests(exp_b, split, client)
        keys = exported_keys(job_dir)
        reqs = [kr for kr in reqs if kr.key in keys]
        print(json.dumps(import_outputs(client, reqs, results_dir), indent=1))
        print(run(exp, client, split, out_dir=E1 / "runs" / job_id))
        print(run(exp_b, client, split, out_dir=E1 / "runs" / f"{job_id}-e1b"))


if __name__ == "__main__":
    main()
