"""E1 on the open-weight judges: `uv run python -m ve_experiments.e1.colab_run export|submit|fetch|score <split> <job id>`.

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

from ..colab import ColabJobRunner, KeyedRequest, export_job, experiment_requests, import_outputs, is_batch_judge, model_id
from ..llm import LLMClient, Request, VerdictParseError, parse_verdict
from ..runner import allocate_run_dir, run
from .pilot import E1, experiment, load_candidates
from .prompts import E1B_ANSWERS, EXPLANATIONS, MAX_NEW_TOKENS, e1b_prompt
from .views import VIEWS

JUDGES_FILE = E1 / "judges.json"


def batch_judges() -> list[dict]:
    return [j for j in json.loads(JUDGES_FILE.read_text(encoding="utf-8"))["judges"] if is_batch_judge(j["judge"])]


def usable(split: str) -> list[dict]:
    return [c for c in load_candidates(name=split) if c["split"] == split and c.get("explanation")]


def e1b_requests(split: str, judges: list[str]) -> list[tuple[dict, str, KeyedRequest]]:
    out = []
    for c in usable(split):
        for view in VIEWS:
            for j in judges:
                key = f"E1b|{split}|{c['id']}|{view}|0"
                out.append((c, view, KeyedRequest(key, Request(j, e1b_prompt(c, view), identity=f"E1b|{split}|{c['id']}|{view}|{j}|0"))))
    return out


def all_requests(split: str, client: LLMClient):
    judges = [j["judge"] for j in batch_judges()]
    exp = experiment(load_candidates(name=split), VIEWS, EXPLANATIONS, judges)
    e1 = experiment_requests(exp, split, client)  # raises for "scored" unless the PREREG is committed
    return exp, e1, e1b_requests(split, judges)


def score_e1b(client: LLMClient, split: str, judges: list[str], out_dir: Path) -> Path:
    run_dir = allocate_run_dir(out_dir, E1 / "runs", split)
    triples = e1b_requests(split, judges)
    results = client.map([kr.request for _, _, kr in triples])
    with open(run_dir / "trials.jsonl", "x", encoding="utf-8") as fh:
        for (c, view, kr), res in zip(triples, results):
            truth = "".join("T" if t else "F" for t in c["e1b_truth"])
            try:
                answer = None if res.tool_events else parse_verdict(res.text, allowed=E1B_ANSWERS).value
            except VerdictParseError:
                answer = None
            correct = 0 if answer is None else sum(a == t for a, t in zip(answer, truth))  # failures score 0 of 2
            fh.write(json.dumps({"item_id": c["id"], "group": c["group"], "template": c["template"], "label": c["label"],
                                 "view": view, "judge": kr.request.model, "truth": truth, "answer": answer,
                                 "correct_of_2": correct, "ok": res.ok, "truncated": res.truncated, "reply": res.text}) + "\n")  # fmt: skip
    return run_dir


def main() -> None:
    what, split, job_id = sys.argv[1:4]
    client = LLMClient()
    job_dir, results_dir = E1 / "colab" / job_id / "job", E1 / "colab" / job_id / "results"
    if what == "export":
        _, e1, e1b = all_requests(split, client)
        specs = [{"id": model_id(j["judge"]), **j.get("vllm_spec", {})} for j in batch_judges()]
        print(export_job(job_dir, job_id, e1 + [kr for _, _, kr in e1b], specs, MAX_NEW_TOKENS))
    elif what == "submit":
        print(ColabJobRunner().submit(job_dir))
    elif what == "fetch":
        print(ColabJobRunner().wait_fetch(job_id, results_dir))
    elif what == "score":
        exp, e1, e1b = all_requests(split, client)
        print(json.dumps(import_outputs(client, e1 + [kr for _, _, kr in e1b], results_dir), indent=1))
        print(run(exp, client, split, out_dir=E1 / "runs" / job_id))
        print(score_e1b(client, split, list(exp.judges), E1 / "runs" / f"{job_id}-e1b"))


if __name__ == "__main__":
    main()
