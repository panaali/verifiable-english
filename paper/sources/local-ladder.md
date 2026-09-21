# Ladder of open-weight judges: E1 dev pilot (NOT a result)

Dev split only (157 candidates: 109 attacked, 48 faithful; 16 base items from 4 templates), view `fol_symbols`, no
explanation, the exact E1 judge prompt (`ve_experiments/e1/prompts.py`), default system prompt, greedy decoding,
`max_new=400`. Local inference: Apple M1 Pro 16 GB, `mlx-lm` 0.31.3, 4-bit `mlx-community` quantizations, batch 8.
Intervals are 95% bootstraps over base items and are rough. Unparseable replies are scored as the worst case
(a false approval for an attacked item, a rejection for a faithful one), so "false approval" includes parse failures.
The run was stopped by the orchestrator before the ladder was complete (machine overloaded; 7B+ rungs moved to a
Colab L4). Everything below is a dev pilot used to pick judges, not evidence about VE.

## Why

Hosted "weak" judges are at floor on raw FOL (`experiments/E1/PILOT-dev.md`: Haiku 4.5 false approval 1/109,
gpt-5.6-luna 5/109). The Plan v2 gate needs raw-FOL false approval in 30-60% with honest acceptance high enough to
mean something. This ladder looks for the model size where that happens.

## Table

Modes: plain name = free-form reply (reasoning, then final JSON, strict parser). `@verdict=forced` = no reasoning,
verdict chosen by comparing the log-probabilities of `approve"}` and `reject"}` after the assistant prefix
`{"verdict": "`. A judge is "usable" only if parse failures <= 10%, honest acceptance >= 70%, and it does not
approve attacked and faithful statements at (nearly) the same rate.

| judge | cell | parse failures | accuracy | false approval | honest acceptance | approve rate | wall s/call (batch 8) | mean out tokens | usable |
|---|---|---|---|---|---|---|---|---|---|
| Llama-3.2-1B-Instruct-4bit | fol_symbols|none | 24/157 (15%) | 0.26 (41/157) | 0.98 [0.95, 1.00] (107/109) | 0.81 [0.71, 0.90] (39/48) | 131/157 | 0.9 | 166 | NO: parse failures > 10% |
| Llama-3.2-1B-Instruct-4bit@verdict=forced | fol_symbols|none | 0/157 (0%) | 0.31 (48/157) | 1.00 [1.00, 1.00] (109/109) | 1.00 [1.00, 1.00] (48/48) | 157/157 | 0.9 | 0 | NO: approves bad and good alike |
| Qwen2.5-0.5B-Instruct-4bit | fol_symbols|none | 19/157 (12%) | 0.28 (44/157) | 0.98 [0.94, 1.00] (107/109) | 0.88 [0.71, 0.98] (42/48) | 136/157 | 0.4 | 89 | NO: parse failures > 10% |
| Qwen2.5-0.5B-Instruct-4bit@verdict=forced | fol_symbols|none | 0/157 (0%) | 0.31 (48/157) | 1.00 [1.00, 1.00] (109/109) | 1.00 [1.00, 1.00] (48/48) | 157/157 | 0.6 | 0 | NO: approves bad and good alike |
| Qwen2.5-1.5B-Instruct-4bit | fol_symbols|none | 20/157 (13%) | 0.29 (45/157) | 1.00 [1.00, 1.00] (109/109) | 0.94 [0.85, 1.00] (45/48) | 137/157 | 1.6 | 295 | NO: parse failures > 10% |
| Qwen2.5-1.5B-Instruct-4bit@verdict=forced | fol_symbols|none | 0/157 (0%) | 0.31 (48/157) | 1.00 [1.00, 1.00] (109/109) | 1.00 [1.00, 1.00] (48/48) | 157/157 | 1.4 | 0 | NO: approves bad and good alike |
| Qwen2.5-3B-Instruct-4bit | fol_symbols|none | 16/157 (10%) | 0.32 (51/157) | 0.91 [0.83, 0.97] (99/109) | 0.85 [0.73, 0.96] (41/48) | 128/157 | 1.7 | 119 | NO: parse failures > 10% |
| Qwen2.5-7B-Instruct-4bit | fol_symbols|none | 0/157 (0%) | 0.57 (90/157) | 0.52 [0.44, 0.59] (57/109) | 0.79 [0.71, 0.88] (38/48) | 95/157 | 3.1 | 90 | yes |
| gemma-2-2b-it-4bit@verdict=forced | fol_symbols|none | 0/157 (0%) | 0.31 (48/157) | 1.00 [1.00, 1.00] (109/109) | 1.00 [1.00, 1.00] (48/48) | 157/157 | 1.9 | 0 | NO: approves bad and good alike |

| judge | cell | and_or_swap | argument_reversal | dropped_conjunct | implication_reversal | model:claude-fable-5-1 | model:gpt-6-astra | quantifier_swap | vacuous_domain | weakened_exception |
|---|---|---|---|---|---|---|---|---|---|---|
| Llama-3.2-1B-Instruct-4bit | fol_symbols|none | 1.00 (16/16) | 1.00 (4/4) | 1.00 (4/4) | 1.00 (16/16) | 1.00 (32/32) | 0.95 (20/21) | 1.00 (4/4) | 1.00 (8/8) | 0.75 (3/4) |
| Llama-3.2-1B-Instruct-4bit@verdict=forced | fol_symbols|none | 1.00 (16/16) | 1.00 (4/4) | 1.00 (4/4) | 1.00 (16/16) | 1.00 (32/32) | 1.00 (21/21) | 1.00 (4/4) | 1.00 (8/8) | 1.00 (4/4) |
| Qwen2.5-0.5B-Instruct-4bit | fol_symbols|none | 1.00 (16/16) | 1.00 (4/4) | 1.00 (4/4) | 1.00 (16/16) | 0.97 (31/32) | 1.00 (21/21) | 1.00 (4/4) | 0.88 (7/8) | 1.00 (4/4) |
| Qwen2.5-0.5B-Instruct-4bit@verdict=forced | fol_symbols|none | 1.00 (16/16) | 1.00 (4/4) | 1.00 (4/4) | 1.00 (16/16) | 1.00 (32/32) | 1.00 (21/21) | 1.00 (4/4) | 1.00 (8/8) | 1.00 (4/4) |
| Qwen2.5-1.5B-Instruct-4bit | fol_symbols|none | 1.00 (16/16) | 1.00 (4/4) | 1.00 (4/4) | 1.00 (16/16) | 1.00 (32/32) | 1.00 (21/21) | 1.00 (4/4) | 1.00 (8/8) | 1.00 (4/4) |
| Qwen2.5-1.5B-Instruct-4bit@verdict=forced | fol_symbols|none | 1.00 (16/16) | 1.00 (4/4) | 1.00 (4/4) | 1.00 (16/16) | 1.00 (32/32) | 1.00 (21/21) | 1.00 (4/4) | 1.00 (8/8) | 1.00 (4/4) |
| Qwen2.5-3B-Instruct-4bit | fol_symbols|none | 0.88 (14/16) | 1.00 (4/4) | 1.00 (4/4) | 0.75 (12/16) | 0.91 (29/32) | 0.95 (20/21) | 1.00 (4/4) | 1.00 (8/8) | 1.00 (4/4) |
| Qwen2.5-7B-Instruct-4bit | fol_symbols|none | 0.31 (5/16) | 1.00 (4/4) | 0.25 (1/4) | 0.44 (7/16) | 0.59 (19/32) | 0.48 (10/21) | 0.25 (1/4) | 0.75 (6/8) | 1.00 (4/4) |
| gemma-2-2b-it-4bit@verdict=forced | fol_symbols|none | 1.00 (16/16) | 1.00 (4/4) | 1.00 (4/4) | 1.00 (16/16) | 1.00 (32/32) | 1.00 (21/21) | 1.00 (4/4) | 1.00 (8/8) | 1.00 (4/4) |


All models verified ungated on the Hugging Face API before download. Reference (hosted, same items): Haiku 4.5
0.01, gpt-5.6-luna 0.05 false approval.

## Findings

1. **0.5B to 3B are not judges.** Qwen2.5 0.5B/1.5B/3B, Llama-3.2-1B and gemma-2-2b approve 91-100% of attacked
   statements. In forced-verdict mode every one of them approves 157/157: they have no signal at all, so their
   "honest acceptance" is approval bias, and "false approval" is meaningless for them.
2. **Verdict format is a secondary problem, not the bottleneck.** Free-form parse failures are 10-15% at <= 3B (the
   reply ends in prose without the JSON object; a few hit `max_new`). The forced mode removes parse failures
   (0/157) and changes nothing else: the models still approve everything.
3. **The informative band lies above 3B.** The one 7B rung that finished before the stop, Qwen2.5-7B-Instruct
   4-bit, is inside the gate: false approval 0.52 (57/109), honest acceptance 0.79 (38/48), 0 parse failures,
   accuracy 0.57 against 0.99 for hosted judges. Its errors are structured (and/or swap 5/16, dropped conjunct 1/4,
   quantifier swap 1/4, but argument reversal 4/4, weakened exception 4/4, vacuous domain 6/8), i.e. it reads some
   of the formula. One model, one quantization, 16 base items: treat as a pointer, to be confirmed on the L4.
4. Step 4 (other views on the best rungs) was **not run**: the stop came first. No view effect has been measured
   for any open-weight judge.

Not run or incomplete: Llama-3.2-3B, Phi-4-mini, Llama-3.1-8B (stopped at 96/157 while swapping; discarded),
Qwen2.5-3B forced, Qwen2.5-7B forced, gemma-2-2b free-form (first attempt hit an `mlx-lm` batching bug with Gemma 2's
sliding-window attention; the worker now falls back to one-by-one generation; the invalid run was deleted and the
rerun was not started), `reason_forced` mode on any rung, temperature sampling on any rung.

## Recommendation

- Do not use any model <= 3B as a weak judge in scored E1/E5.
- Candidate weak judges are the 7-8B class (Qwen2.5-7B-Instruct first; Llama-3.1-8B as the second family) and the
  rungs between 8B and the hosted judges (14B, 32B), which the Colab agent covers. Pick rungs whose dev raw-FOL false
  approval is 30-60% with honest acceptance >= 70% and parse failures <= 10%, from two families, and name them in
  PREREG before scoring. Quantization differs (MLX 4-bit here, bf16/AWQ under vLLM): re-measure the gate on the
  serving stack that will score; do not carry the 0.52 over.
- Honest acceptance of 0.79 is close to the 0.70 floor: the PREREG honest-acceptance constraint will bind.

## Throughput

Measured wall time per call over a whole dev run (157 prompts, about 450 input tokens, model load included,
batch 8), on the M1 Pro **while other agents kept the machine at load average ~160 and 11 GB of swap**; an idle
machine would be faster.

| rung | s/call | calls/hour |
|---|---|---|
| Qwen2.5-0.5B | 0.4 | ~9,000 |
| Llama-3.2-1B | 0.9 | ~4,000 |
| Qwen2.5-1.5B | 1.6 (295 output tokens/call) | ~2,250 |
| Qwen2.5-3B | 1.7 | ~2,100 |
| Qwen2.5-7B | 3.1 (90 output tokens/call) | ~1,150 |
| Llama-3.1-8B | not usable locally: 8-40 s/call under memory pressure | - |

A scored set of 3-6k prompts on Qwen2.5-7B would take about 2.5-5 hours per model locally, and the 8B rung does
not fit beside the other workloads in 16 GB. **Colab is needed for 7B and above.** Estimate, not measured: vLLM on
an L4 (24 GB) with bf16 7-8B weights and continuous batching typically sustains on the order of 1-2k output
tokens/s; at about 450 input and 100-300 output tokens per prompt that is roughly 10-30 minutes for 6k prompts per
7-8B model, and 14B/32B need AWQ/GPTQ 4-bit to fit and would take roughly 2-4 times longer.

## Using the backend

```
uv venv --python 3.12 ~/code/ve-judges-env/.venv && uv pip install --python ~/code/ve-judges-env/.venv/bin/python mlx-lm
HF_TOKEN=... python -c "from huggingface_hub import snapshot_download; snapshot_download('mlx-community/Qwen2.5-7B-Instruct-4bit')"
export VE_OPEN_PYTHON=~/code/ve-judges-env/.venv/bin/python   # interpreter that has mlx-lm; VE_OPEN_BATCH=8
uv run python -m ve_experiments.e1.ladder run "open:mlx-community/Qwen2.5-7B-Instruct-4bit" fol_symbols ve_strict
uv run python -m ve_experiments.e1.ladder table
```

Judge names are `open:<hf repo>[@max_new=400,temp=0,verdict=free|forced|reason_forced]` and work anywhere a judge
name is accepted (`LLMClient.call`, `Experiment.judges`). Settings are part of the name, so of the cache key and of
every trial row. `temp=0` is greedy; `temp>0` samples with the trial's seed as a real seed, unbatched, so
(prompt, seed) replays. The worker (`ve_experiments/open_worker.py`) is a separate process holding one model at a
time, runs offline (`HF_HUB_OFFLINE=1`, no token) from an empty directory, and has no tools. The client cache, retries
and `calls.jsonl` apply as for hosted judges; `.llm_cache/open_calls.jsonl` adds batch size, batch wall time, token
counts, `hit_max_new` and forced-verdict log-probabilities. Caveat: greedy replies are generated in batches of
whatever requests arrive together, and padding can change low-order numerics, so a rerun without the cache is not
guaranteed to be bit-identical; the disk cache is what makes reruns replay exactly. The vLLM runs on Colab do not
go through this backend.
