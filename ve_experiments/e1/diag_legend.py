"""DEV-ONLY diagnostic, not a cell of E1: does the long JSON legend explain why the open-weight judges approve far
more often under the current prompt than on the ladder (which used a plain vocabulary listing)?

  uv run python -m ve_experiments.e1.diag_legend export|score <job id>

Variant: the E1 judge prompt with the legend block replaced by `views.vocabulary_text` (sorts and predicates with
their descriptions, about 700 characters instead of about 4,000). Everything else is unchanged. Cells: fol_symbols
and ve_strict, with and without the explanation; judges: the 7B and 14B rungs. Scoring uses the project's strict
verdict parser with the worst case for failures.
"""

from __future__ import annotations

import json
import sys

from ..colab import KeyedRequest, export_job, slug
from ..llm import DEFAULT_SYSTEM, Request, VerdictParseError, parse_verdict
from .colab_run import usable
from .pilot import E1
from .prompts import MAX_NEW_TOKENS, judge_prompt
from .views import legend, vocabulary_text

MODELS = ["Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen2.5-14B-Instruct-AWQ"]
CELLS = [(v, e) for v in ("fol_symbols", "ve_strict") for e in ("none", "attacker")]


def variant_prompt(c: dict, view: str, explanation: str) -> str:
    full = judge_prompt(c, view, explanation)
    old = legend(c["environment"])
    assert full.count(old) == 1
    return full.replace(old, vocabulary_text(c["environment"]) + "\n")


def main() -> None:
    what, job_id = sys.argv[1:3]
    root = E1 / "colab" / job_id
    cands = usable("dev")
    if what == "export":
        reqs = [KeyedRequest(f"E1diag|dev|{c['id']}|{v}|{e}|0", Request(f"vllm:{m}", variant_prompt(c, v, e), system=DEFAULT_SYSTEM))
                for c in cands for v, e in CELLS for m in MODELS]  # fmt: skip
        print(export_job(root / "job", job_id, reqs, [{"id": m, "max_model_len": 4096} for m in MODELS], MAX_NEW_TOKENS))
    else:
        label = {c["id"]: c["label"] for c in cands}
        lines = ["| model | cell | false approval | honest acceptance | failures |", "|---|---|---|---|---|"]
        for m in MODELS:
            rows = [json.loads(x) for x in (root / "results" / "out" / slug(m) / "outputs.jsonl").read_text().splitlines()]
            for v, e in CELLS:
                fa = ha = nb = ng = fail = 0
                for r in rows:
                    _, _, cid, rv, re_, _ = r["key"].split("|")
                    if (rv, re_) != (v, e):
                        continue
                    try:
                        approved = parse_verdict(r["text"]).value == "approve"
                    except VerdictParseError:
                        approved, fail = label[cid] == "bad", fail + 1
                    nb, ng = nb + (label[cid] == "bad"), ng + (label[cid] == "good")
                    fa, ha = fa + (approved and label[cid] == "bad"), ha + (approved and label[cid] == "good")
                lines.append(f"| {m} | {v}|{e} (plain vocabulary) | {fa / nb:.3f} ({fa}/{nb}) | {ha / ng:.3f} ({ha}/{ng}) | {fail} |")
        print("\n".join(lines))


if __name__ == "__main__":
    main()
