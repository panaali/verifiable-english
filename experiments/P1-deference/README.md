# P1 execution

## Final status — 2026-09-22

The initial stage is complete: **1,128/1,128** Qwen judgments. Pushback remains
infrastructure-incomplete: all **120** trajectories ended, with **84** exhausted
attacker truncation retries, **28** concessions and **8** two-turn completions.
Amendment 9 prohibits another attempt on those exhausted trajectories; an
ordinary resume cannot fill the gaps. No paid calls were made for finalization.

See [RESULTS.md](RESULTS.md) for separate E4/E5 contrasts, Wilson rates, Gemini
dev ceilings, pushback coverage, amendments and spending. Recorded realised
cost is **$3.45987693870** in the study ledger and **$3.49623306220** across all
retained billing ledgers. Historical Amendment 14 instructions below describe
the pre-resume state and do not request another scored run.

## Historical pre-resume status — Amendment 14

The scored Qwen run retains **1,010/1,128 initial trials** (E4 751/840,
E5 259/288), 20 pushback judgments and 208 Gemini attacker calls.
**Initial stage incomplete; pushback incomplete.** The supplied initial-stage
completion claim does not match the frozen assignments. All completed calls
are reused from the ledger; no samples are re-bought.

The Gemini attacker keeps provider `max_output_tokens=256`, with a **1,024
billed-output cap** including thinking. The 304-token halted reply is retained
and narrowly recovered; its existing truncation policy still applies.
See [Amendment 14](PROPOSED-AMENDMENT.md#amendment-14) and
[the audit receipt](checks/amendment14.json).

Selected **`replication_2turn`**: Qwen E4+E5, all initial arms, two pushback
turns in V/W/A/F/R; Gemini remains attacker. Weak control is **not run**.
Both Gemini judge panels remain dev ceilings. Qwen contrasts are
**exploratory-primary (judge substitution due to ceiling)**, never pooled.
[Current initial analysis](runs/scored/analysis.json) includes provisional
available-pair, label-balanced family contrasts and descriptive Wilson arm
rates. It identifies missing observations and does not score infrastructure
gaps as model failures. Complete panels use the original preregistered method.

Strict pushback ceiling **$15.17346528000**; all scored calls
**$17.95921624320**; cumulative API cap **$19.90026000260**;
all-in ceiling with $0.25 local **$20.15026000260**, within $40.
Completed scored charges consume the same envelope, not a second budget.
Worker paid calls/spend: **0 / $0**.

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex
uv run python experiments/P1-deference/run_p1.py preflight --offline
uv run python experiments/P1-deference/run_p1.py preflight-openrouter --cap-usd 0.50 --cached-only
uv run python experiments/P1-deference/run_p1.py refresh-dev
uv run python experiments/P1-deference/run_p1.py reconcile
uv run python experiments/P1-deference/run_p1.py analyze experiments/P1-deference/runs/scored/trials.jsonl --schedule replication_2turn
# Orchestrator; not dispatched by this worker:
uv run python experiments/P1-deference/run_p1.py scored --cap-usd 19.90026000260
```

`refresh-dev` validates the identical retained Qwen dev subset locally.
`reconcile` appends audited recovery and reopens the existing scored block,
subtracting completed costs and retaining unresolved holds.

The remaining sections describe execution history; the current contract,
bounds, accounting and replacement rules above supersede them.

The approved replacement probe is complete (10 valid responses), originally
selecting `full_256`; Amendment 11 records the budget-authorized replacement
`primary_1024` without altering the samples. Original attempts remain in `results/probe-attempt{1,2}.json` and
`runs/probe-attempt{1,2}/`. Dev halted after 19 completed calls; scored inference has not run. See `freeze.json`
for current gate outcomes and `PROPOSED-AMENDMENT.md` for the dated amendments.

## Preflight

Run from the repository root:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex
uv run python experiments/P1-deference/run_p1.py preflight
```

This exports prompts, regenerates the manifest from current code/materials,
and actually runs known-answer integration, Lean executable replay (building
Lean once if missing), semantic pairs, the entire non-live pytest suite,
external timestamp inspection, and Vertex countTokens under ADC. It performs
no model generations. Each gate records its own outcome and freeze digest;
exceptions produce failed receipts, never recycled passes. Independent gates
continue after failure. Exit 0 means these six gates and the schedule budget passed, not provider/dev
readiness. Exit 3 means the schedule exceeds the study cap. `freeze.json.dev_blockers` also includes pending provider preflight.

The Vertex gate covers all 200 dev+scored items in all arms: 1,336 initial
prompts, 200 replay continuations, and 280 maximal joint pushback histories.
The latter count the full attacker/judge wire including replay results and
six role wrappers, reserving three times (1,024 judge + 256 attacker) generated tokens plus the initial
1,024-token response and (for R) 1,024-token replay-call output. Future native response signatures
cannot be known offline; every actual transcript is counted again before
runtime dispatch with no truncation. These counts are only for Gemini.

The timestamp gate requires the current PREREG SHA-256 in
`experiments/PREREG-HASHES.txt`, successful `uvx --from opentimestamps-client
ots info`, and the proof's embedded hash matching that hash file. Pending
calendar attestation suffices for this pilot as explicitly authorized by the
orchestrator. The receipt distinguishes pending calendars from an included
Bitcoin attestation; `ots info` is not blockchain confirmation. It does not
claim the new aggregate freeze has been externally timestamped.

## Orchestrator-only OpenRouter preflight

With the key already in the process environment, the orchestrator runs:

```sh
uv run python experiments/P1-deference/run_p1.py preflight-openrouter --cap-usd 0.50
```

`--counter-command` defaults to the bundled executable `native_counter.py`.
Its interface is full OpenRouter wire JSON on stdin and one integer on stdout.
The bundled counter is loaded in-process by preflight so tokenizer loading is
amortized across all fixtures; custom executables retain the subprocess interface.
It uses `tokenizers` to encode the entire rendered chat once, with no truncation,
padding, approximate fallback, or duplicate special tokens. The native
Jinja chat templates include system messages, tool schemas, assistant tool calls,
replay results, and the assistant generation prefix. Amendment 6 omits the
HF-injected date header for Llama requests without tool definitions: the retained
DeepInfra smoke counts 21, exactly matching this rendering, versus 41 with the
dates. BOS and the assistant header remain; Qwen stays at 19. Tool-bearing Llama
requests retain the upstream template. See `checks/smoke-tokenizer-diagnosis.json`
for the rendered variants. Strict smoke equality remains required for both judges.
OpenAI JSON argument strings
are decoded to objects before rendering. Unsupported models/content fail closed.

Tokenizer provenance is pinned in `tokenizers/sources.json`, with Git blob hashes
checked against every downloaded tokenizer and the bundled configurations:

- Qwen uses [Qwen/Qwen2.5-72B-Instruct](https://huggingface.co/Qwen/Qwen2.5-72B-Instruct/tree/495f39366efef23836d0cfae4fbe635880d2be31).
- Llama uses the public [NousResearch tokenizer](https://huggingface.co/NousResearch/Meta-Llama-3.1-8B-Instruct/blob/d10aef7999a2b5ba950ab3974312feeedbfe0b77/tokenizer.json)
  and [hugging-quants configuration/template](https://huggingface.co/hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4/blob/db1f81ad4b8c7e39777509fac66c652eb0a52f91/tokenizer_config.json).
  On 2026-09-21, their Git blob IDs matched the [official Meta repository metadata](https://huggingface.co/api/models/meta-llama/Llama-3.1-8B-Instruct/revision/0e9e39f249a16976918f6564b8830bc894c89659?blobs=true)
  exactly: `5cc5f00a5b203e90a27a3bd60d1ec393b07971e8` for tokenizer bytes and
  `db88166e2bc4c799fd5d1ae643b75e84d03ee70e` for configuration bytes. Using the
  AWQ repository's configuration does not substitute the inference model.
  Unsloth's current assets did not match and were not selected.

The first local invocation downloads vocabulary assets from Hugging Face into
`.cache/p1-tokenizers`; subsequent invocations need no network. The freeze pins
counter code, source metadata, configurations, and dependency lockfile. Native
asset identity does not establish served-provider template agreement; that
remains a separate preflight check. The script calls no OpenRouter API.

The command checks served model IDs and endpoint metadata, then dispatches at
most one output token per planned OpenRouter judge, serially, through the
existing durable budget ledger. It checks native usage reconciliation and
counter agreement on the smoke prompt, and counts all initial/replay fixtures
for both judges. Amendment 5 preserves successful smoke results and reruns only
failed judges. It recovers successful usage from the durable ledger if an older
run overwrote the report; a changed freeze revalidates cached usage locally.
Weak control routes in order through DeepInfra, Novita and Groq only, except
R: Amendment 7 removes provider and quantization restrictions for weak R while
requiring parameter support. Qwen remains pinned to tool-capable DeepInfra. Provider evidence is stored in `checks/provider-preflight.json`;
paid reservations/responses go to `runs/provider-preflight/costs.jsonl`.
Local fixture counting must pass before the smoke generation for that judge.
Missing or mismatched native assets block the panel without guessing. The worker
only downloaded public tokenizer assets and ran local counts; no OpenRouter API
or key lookup was performed.

Provider metadata API: [models](https://openrouter.ai/docs/api/api-reference/models/get-models)
and [endpoints](https://openrouter.ai/docs/api/api-reference/endpoints/list-endpoints).

## After all preflight gates pass

Only the orchestrator should advance the experiment. The full schedule's
cumulative API ceilings now reserve the replacement probe's $1 envelope,
$0.056900 for attempt 1 (including its unresolved dispatch), and a $0.50
provider-preflight envelope. Attempt 2's completed calls are already included
in the completed replacement probe, not counted twice. Amendment 3 raises A/R
input bounds to 6,800. The resulting full_256 all-in
ceiling is **$35.71826352**, within Amendment 4's approved **$36** study cap.
The current provider gate must pass before dev can start. Amendment 5 permits
three infrastructure retries with 1/2/4-second backoff for 429/5xx/timeouts;
these attempts are logged separately from samples. Unknown timeout/5xx billing
keeps a full-ceiling infrastructure hold against the same cap. Output failures
are scored as preregistered and cannot buy replacement dev/scored samples.
Served providers appear per call in the ledger and trials, with counts in the
run analysis. An exhausted infrastructure panel is marked incomplete without
scoring its missing observations as model failures; the other judges continue.
An explicit no-tool-endpoint 404 for unrestricted weak R excludes that whole
arm from analysis and gates, with a durable infrastructure-unavailable receipt.
Dev gate files retain observed numerators and denominators for every judge.
Both dev and scored automatically resume from the ledger: completed calls and
transcripts are reused, trial rows are deduplicated, and the original 19 dev
completions are never repurchased. Do not delete the existing run directories.
Refresh preflight and provider receipts for amended code before resuming.

```sh
uv run python experiments/P1-deference/run_p1.py dev --cap-usd 6.7108092992
```

The dev runner now requires current test-suite and external-timestamp receipts
as well as the known-answer, tokenizer, Lean, semantic-pair and provider gates.
All schedules and exact cumulative commands are recorded in `freeze.json`.
Budget failure exits 3; gate failure exits 2. Never delete ledgers or substitute
approximate counts to bypass a failure.

## Latest executed gates

The amended preflight passed all six gates: known-answer, 500 Lean replay
queries, 200 semantic pairs, 1,356 tests (two optional-backend skips), pending
calendar timestamp inspection, and **1,816/1,816 fresh Vertex counts**. There
were zero token errors or overflows; the maximum including generated reserves
was 6,175. The separate local native-counter receipts passed **1,536/1,536**
fixtures for each of Qwen (maximum 4,548) and Llama (maximum 4,085). These are
local counts, not OpenRouter usage confirmations. No new model generations
were made; worker inference spend was $0. Provider revalidation reused both
retained smoke replies. Amendment 7 tests also reconstruct the original dev
ledger prefix, preserving its 19 completions and 17 trial rows without dispatch.

See `checks/` and `freeze.json` for the receipts and current blockers.
The pre-amendment Vertex gate had 118 overflows among 1,816 real counts, all in
A/R. Amendment 3 applies the smallest hundred-token ceiling admitting its
6,175-token maximum with a 10% margin: 6,800. Other arms, all items, prompts,
replay text, and output bounds are unchanged. The selected full_256 schedule
fits the amended $36 budget; all gate receipts must match the execution freeze.
