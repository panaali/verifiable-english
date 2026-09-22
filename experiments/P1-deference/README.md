# P1 execution

The approved replacement probe is complete (10 valid responses), selecting
`full_256`. Original attempts remain in `results/probe-attempt{1,2}.json` and
`runs/probe-attempt{1,2}/`. No dev or scored inference has run. See `freeze.json`
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
continue after failure. Exit 0 means these six gates passed, not provider/dev
readiness. `freeze.json.dev_blockers` also includes pending provider preflight.

The Vertex gate covers all 200 dev+scored items in all arms: 1,336 initial
prompts, 200 replay continuations, and 280 maximal joint pushback histories.
The latter count the full attacker/judge wire including replay results and
six role wrappers, reserving six times 256 generated tokens plus the initial
response and (for R) replay-call output. Future native response signatures
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
Weak control routes in order through DeepInfra, Novita and Groq only; Qwen
remains pinned to DeepInfra. Provider evidence is stored in `checks/provider-preflight.json`;
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
run analysis. An exhausted infrastructure run is marked incomplete without
scoring its missing observations as model failures.

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
queries, 200 semantic pairs, 1,345 tests (two optional-backend skips), pending
calendar timestamp inspection, and **1,816/1,816 fresh Vertex counts**. There
were zero token errors or overflows; the maximum including generated reserves
was 6,175. The separate local native-counter receipts passed **1,536/1,536**
fixtures for each of Qwen (maximum 4,548) and Llama (maximum 4,085). These are
local counts, not OpenRouter usage confirmations. No judge/OpenRouter calls
were made; worker inference spend was $0.

See `checks/` and `freeze.json` for the receipts and current blockers.
The pre-amendment Vertex gate had 118 overflows among 1,816 real counts, all in
A/R. Amendment 3 applies the smallest hundred-token ceiling admitting its
6,175-token maximum with a 10% margin: 6,800. Other arms, all items, prompts,
replay text, and output bounds are unchanged. The selected full_256 schedule
fits the amended $36 budget and awaits the current OpenRouter provider gate.
