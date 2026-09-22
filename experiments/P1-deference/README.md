# P1 execution

Status: **stopped; not scoring-ready**. The preregistration and shared design
are unchanged. No dev or scored inference has been run.

The authorized probe completed one response and failed during its second
dispatch with `RuntimeError: Event loop is closed`. The async SDK connection
pool was reused across separate `asyncio.run` event loops. The client now owns
one persistent event loop; the fix has only been tested offline. The original
append-only ledger and responses remain in `runs/probe/costs.jsonl`.

The completed response used 242 input, 6 candidate, 85 thinking, and 91 billed
output tokens, with zero cached tokens. Latency was 3.014263 seconds and
design-table cost was $0.001576. The second dispatch retains its $0.055296
reservation; billing has not been reconciled. Known cost plus that ceiling is
$0.056872, below this task's $1.50 cap. The mean and maximum over **one completed
response** are both 91; they cannot select a schedule for a ten-call probe.
The operational decision is **stop**, under the unknown-billing/incomplete-probe
rule. `results/probe.json` records this distinction.

## Commands

Run from the repository root. Commands are serial and never invoke paid retries.

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex
uv run python experiments/P1-deference/run_p1.py known-answer --lean-replay --freeze
uv run pytest -q
```

The following original probe command is recorded for reproducibility. It refuses
to run again when `results/probe.json` exists or the ledger has a previous
assignment. Do not remove those records to bypass the stop.

```sh
uv run python experiments/P1-deference/run_p1.py probe --cap-usd 1.00
```

There is currently **no authorized dev/scored schedule**. After an approved
amendment, a successful probe and all preflight gates, use only the row actually
selected by that probe. These are cumulative API ceilings including the entire
$1 probe envelope; dev and scored share `runs/study/costs.jsonl`.
The separate $0.25 local accounting allowance remains inside the $30 study cap.

| Schedule | Dev command's `--cap-usd` | Scored command's `--cap-usd` |
|---|---:|---:|
| full_256 | 5.2120486912 | 28.9037747200 |
| primary_512 | 2.605632 | 14.647872 |
| primary_1024 | 3.392064 | 21.332544 |

For example, the exact full-schedule commands would be:

```sh
uv run python experiments/P1-deference/run_p1.py dev --cap-usd 5.2120486912
uv run python experiments/P1-deference/run_p1.py scored --cap-usd 28.9037747200
uv run python experiments/P1-deference/run_p1.py analyze experiments/P1-deference/runs/scored/trials.jsonl --split scored --schedule full_256
```

For either primary-only schedule substitute that row's two caps and use its
schedule name for `analyze`. All exact variants also appear in `freeze.json`.
Budget exhaustion exits 3; feasibility/preflight failure exits 2.

## Implemented boundaries and remaining gates

`ve_experiments.llm` exports the native-role `VertexBackend`,
`OpenRouterBackend`, `PaidClient`, and `OfflineBackend`. The older CLI client's
retry/cache behavior does not apply to these APIs. Vertex uses Google ADC and
the exact planned project/global endpoint. OpenRouter reads its key exclusively
from `os.environ`; it uses DeepInfra fp8 or DeepInfra Turbo fp8 with fallbacks
disabled. A model/provider change stops dispatch.

The API ledger records exact API usage and response data, prompt/role bytes,
identity and checker hashes, served revision, timing, table-priced cost and
remaining budget. Cached input is disclosed and conservatively priced at the
table's full input rate. Vertex's usage response does not provide an invoice
amount; invoice reconciliation remains explicitly pending. Unknown usage or a
timeout leaves the call ceiling reserved and stops dispatch. The output ceiling
includes candidates plus thoughts, not candidates alone. Reservations use a
filesystem lock and fsync. Entire blocks are reserved before dispatch.

The renderer uses native system messages for A/V and proposer/user messages for
F/F-correct/U. F-correct copies the authentic finding bytes. F/U use the same
substantive assertion function. E5 has no invented conditional countermodel.
Only R has a replay declaration; only its pending native tool call receives the
bound replay result. Gemini assistant parts/signatures survive continuation.
Source records are never truncated. All returned verdicts pass the strict JSON
parser, and failures stay in denominators. Analysis separates each judge/panel,
uses template pairing and the specified bootstrap/boundary safeguard, and uses
Wilson only for one binary observation per template.

The offline gate includes oracle/random/constant/reversed-label outcomes,
shuffled joins, missing/duplicate assignments, role injection, replay use/no-use/
error, timeouts, budget reservations and repeated SDK calls on one event loop.
`checks/lean-replay.json` retains 500 exact query envelopes and Python/Lean
agreement across the 200 selected items. These are construction checks.

Unresolved execution gates are explicit, not waived:

- The interrupted probe and unknown second-dispatch billing.
- Exact tokenization of the whole selected schedule, including replay
  signatures, wrappers and joint pushback histories. The current tokenizer
  receipt covers only the ten fixed probe prompts.
- OpenRouter provides no native joint count endpoint here. Its adapter requires
  an independently validated native provider/template counter; without one it
  refuses dispatch. No approximate tokenizer is substituted. Provider role,
  immutable revision and current pricing preflight are also pending.
- Dev capability checks and the external timestamp receipt required for scoring.

`freeze.json` is a local manifest marked blocked, not an external timestamp or a
claim that the missing gates passed. The `known-answer --freeze` command exports
the local manifest; it does not publish anything.

Provider references checked during implementation:
[Google thinking/output accounting](https://ai.google.dev/gemini-api/docs/generate-content/thinking),
[Vertex thinking](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/thinking),
[Vertex function calling and signatures](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling),
[OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection),
[OpenRouter usage accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting).
