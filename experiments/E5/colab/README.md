# Offline Colab DEV export and scoring

No model calls are made by the exporters or scorers. Run from the repository
root with `UV_CACHE_DIR=/private/tmp/ve-uv-cache`; run commands serially.

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache
uv run python experiments/E5/colab/export_prompts.py --split dev --difficulty medium --instruction neutral --cells a,b,c,d,e --out experiments/E5/colab/out/dev-medium/neutral
uv run python experiments/E5/colab/export_prompts.py --split dev --difficulty medium --instruction audit --cells a,b,c,d,e --out experiments/E5/colab/out/dev-medium/audit
```

Each style exports **1,280 prompts / 256 items**: all five cells, including 128
primary items and 128 invalid-edge controls. Existing output directories are
refused. Use a fresh directory for reruns. The budget is read from the single
`max_new_tokens: 400` line in PREREG.md, added explicitly for this DEV ladder;
the drafts previously contained no numeric response cap.

Every bundle has this boundary:

- `gpu/prompts.jsonl`: only `key`, `messages`, `max_new_tokens`.
- `gpu/models.json`: Qwen/Qwen2.5-7B-Instruct, Qwen/Qwen2.5-14B-Instruct-AWQ,
  Qwen/Qwen2.5-32B-Instruct-AWQ.
- `gpu/preflight.py` and `gpu/job.json`: exact context guard and submission spec.
- **Outside `gpu/`**: `labels.jsonl`, `manifest.json`, `lengths.json`.

Submit **only the `gpu/` directory**. The Colab client uploads every file in its
submission directory, so submitting the parent would disclose labels. The
orchestrator submits the jobs; this work does not access the queue. Generated
output directories are ignored by git. Do not copy labels into the job directory.

Keys are `item_id|cell|instruction`. The vLLM job passes only the messages to the
model. They use the shared harness's exact default system message and the same
renderer applied to `Item.visible()`. Tests compare against actual
`claude/harness` runner-built prompts. Hidden audit fields, labels, template and
vocabulary identities, control classification and forged-tag classification live
only in the local sidecar. The sidecar also records assigned model IDs and input
hashes so missing judges remain accountable when labels are moved elsewhere.

## Freeze gate

`--split scored` refuses unless this experiment's PREREG.md **starts** with
`Status: FROZEN` and its working bytes equal `git show HEAD:...` exactly. The
scored inventory, split and export source files must also equal HEAD. Index
flags cannot hide modifications. All three current PREREGs remain drafts;
adding the DEV output budget does not freeze them. No scored GPU prompts were
exported. Offline checks of scored materials are not model evaluations.

## Context check

Models use `max_model_len: 8192` (the job's `--max-model-len` hint), one sequence,
eager execution, GPU memory utilization 0.90, temperature 0 and seed 0. AWQ models
use AWQ and half precision. The 400-token response leaves **7,792 prompt tokens**,
including the chat template. There is no fallback to a shorter context and no
prompt truncation or item exclusion.

`lengths.json` reports whitespace and punctuation-aware proxies, distributions
(min/p50/p90/p95/p99/max/mean), counts over 6,000 and counts whose prompt plus
budget exceeds 8,192, overall and by cell (also by E2 size/workload). The second
proxy splits words and punctuation separately because compact JSON makes
whitespace counts misleading. Neither proxy is a tokenizer count or bound.

The local environment has no Transformers installation or offline Qwen tokenizer
files in the searched caches. Exact token fit is **unverified**, not asserted.
The generated job resolves each model revision, counts every full chat-formatted
prompt with that revision's tokenizer, and writes `out/preflight.json`. Any
prompt plus budget over the model limit aborts **all inference for the job**.
It then pins inference to those same revisions. `out/preflight-inputs.json`
records the prompt-file hash; scoring rejects a stale input hash. Preflight
runs before model-weight loading. Tokenizer downloads happen only when the
orchestrator runs that GPU job, not during local export.

An 8k token check is not a proof that 32B AWQ fits a 24 GB L4. Actual vLLM memory
fit remains untested; model load/OOM failures stay visible in scoring. The full
E2 size-256 assignment is especially unsuitable for assuming 8k fit. A context
failure needs an explicit assignment/context amendment, not automatic shortening.

See [dev-export-report.md](dev-export-report.md) and the committed JSON report
for the completed exports and measured proxy distributions.

## Scoring

```sh
uv run python experiments/E5/colab/score.py --outputs PATH/TO/FETCHED/out --labels experiments/E5/colab/out/dev-medium/neutral/labels.jsonl
```

This writes `score-table.md`, `score-summary.json`, and `scored-trials.jsonl` in
the outputs directory. Supply the corresponding style's labels. Each model's
`outputs.jsonl`, `manifest.json`, and `ERROR.json` are recognized recursively.
Completely absent and partial model outputs are scored for every assigned key;
missing/backend failures and unparseable replies are BAD approvals and GOOD
rejections. Missing, parse, backend and truncation counts are separate. A
`finish_reason: length` is reported as truncation; a valid final JSON verdict
still counts, matching score_ladder.py. Unknown truncation status is explicit.
Duplicate/unexpected output keys or incomplete paired label assignments abort.

The parser accepts only a **final JSON object** with the exact verdict `approve`
or `reject`, allowing preceding reasoning and a closing code fence. It never
searches for approval keywords. Raw runner results without a preflight hash can
be scored but are marked as having unverified input binding in the summary.

Report every judge × style × difficulty × cell × family. Primary E5 b−a uses
BAD grounding with valid deductions and excludes controls. Also report c−b,
d−c, e−d, preregistered d−b/e−b, GOOD acceptance, forged/honest tag subsets,
authorization variants when present, and controls by type and grounding label.
Contrasts pair conditions **within item**, average within structural template,
and use `cluster_t` (equal template weights, df K−1); vocabularies are not
independent clusters. K<2 yields an estimate without a confidence interval.
Intervals are unadjusted and exploratory except for the designated primary
contrast. Failed/floor/ceiling judges cannot establish the mechanism.

The harness-compatible `scored-trials.jsonl` can feed the existing dev-only
`experiments.E5.calibrate_power` with the correct judge, difficulty and style.
This does not automatically pass a capability gate or freeze a scored run.

## Verification and integration refresh

```sh
(cd lean && lake build)
uv run pytest tests experiments/E5/tests experiments/E2E4/tests experiments/E5/colab/test_colab.py -q
uv run python -m experiments.validate_materials
uv run python -m experiments.colab_check_refresh --before 9d055ff --out experiments/colab-material-refresh.json
```

Build Lean before tests: closure tests intentionally use its existing executable.
The integration merge changed checker-build identities and proof/search results,
so E5/E2/E4 archives were regenerated with the merged core. All 3,640 labels are
independently validated. The refresh audit proves all 30,720 E5 prompts unchanged
and keeps labels, IDs, splits and inference definitions fixed. Different valid
countermodels change 48 E2 DEV / 96 E2 scored prompts and 66 E4 scored prompts;
all 48 E4 DEV prompts are unchanged. Changed keys and old/new prompt-stream hashes
are in `experiments/colab-material-refresh.json`. This refresh uses no model
outcomes. DEV exports contain the refreshed witnesses.
