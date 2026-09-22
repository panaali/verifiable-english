# P1 execution

The approved replacement probe is complete (10 valid responses), selecting
`full_256`. Original attempts remain in `results/probe-attempt{1,2}.json` and
`runs/probe-attempt{1,2}/`. No dev or scored inference has run. See `freeze.json`
for current gate outcomes and `PROPOSED-AMENDMENT.md` for the two approvals.

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
uv run python experiments/P1-deference/run_p1.py preflight-openrouter --cap-usd 0.50 --counter-command "$P1_NATIVE_COUNTER"
```

`P1_NATIVE_COUNTER` must identify an executable provider-native joint chat
counter: full OpenRouter wire JSON on stdin, one nonnegative integer on stdout.
It must implement the served provider's chat template and tool serialization,
not a text-length approximation. Its executable hash is pinned and checked
again by the study adapter. No such counter is bundled here.

The command checks served model IDs and endpoint metadata, then dispatches at
most one output token per planned OpenRouter judge, serially, through the
existing durable budget ledger. It checks native usage reconciliation and
counter agreement on the smoke prompt, and counts all initial/replay fixtures
for both judges. It never substitutes an endpoint/model or retries an assigned
smoke call. Provider evidence is stored in `checks/provider-preflight.json`;
paid reservations/responses go to `runs/provider-preflight/costs.jsonl`.
Without `--counter-command`, endpoint/usage smoke checks can still execute but
the provider gate fails explicitly for missing native joint counts. Do not
use that diagnostic invocation before supplying the counter if a complete
provider pass is wanted: smoke calls cannot be repeated. No OpenRouter
preflight or key lookup was performed by the implementation worker.

Provider metadata API: [models](https://openrouter.ai/docs/api/api-reference/models/get-models)
and [endpoints](https://openrouter.ai/docs/api/api-reference/endpoints/list-endpoints).

## After all preflight gates pass

Only the orchestrator should advance the experiment. The full schedule's
cumulative API ceilings now reserve the replacement probe's $1 envelope,
$0.056900 for attempt 1 (including its unresolved dispatch), and a $0.50
provider-preflight envelope. Attempt 2's completed calls are already included
in the completed replacement probe, not counted twice. The separate $0.25
local allowance leaves total maximum spending below $30.

```sh
uv run python experiments/P1-deference/run_p1.py dev --cap-usd 5.7689486912
# Only after dev capability passes and the orchestrator authorizes scoring:
uv run python experiments/P1-deference/run_p1.py scored --cap-usd 29.4606747200
```

The dev runner now requires current test-suite and external-timestamp receipts
as well as the known-answer, tokenizer, Lean, semantic-pair and provider gates.
All schedules and exact cumulative commands are recorded in `freeze.json`.
Budget failure exits 3; gate failure exits 2. Never delete ledgers or substitute
approximate counts to bypass a failure.

## Latest executed gates

The current `preflight` exited 2: known-answer, all 500 Lean queries, 200
semantic pairs, 1,310 tests (two optional-backend skips), and the pending-calendar
timestamp gate passed. Vertex returned real counts for all 1,816 fixtures;
118 exceeded their bounds. Maximum totals including generated reserves were
4,118 initial / 4,400 replay / 6,126 attacker / 6,175 pushback judge tokens.
The full schedule therefore remains blocked by token limits as well as the
unrun OpenRouter gate. The orchestrator must resolve the token overflows through
an approved amendment before dev; this worker did not change prompt limits,
truncate evidence, run dev/scored, or spend on generation.
