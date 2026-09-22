# P1 amendments — 2026-09-21

The original ten-call feasibility probe is incomplete because of a harness
async-runtime error on dispatch two. This is an implementation failure, not an
ADC or model-availability failure. One response was received; the second call's
billing is unknown. No scientific schedule can be selected from this probe.

Before any further inference, reconcile the outstanding reservation against
provider billing. Preserve the original ledger and `results/probe.json`, and
retain the original preregistration's hashes.

Proposed change: explicitly authorize a new ten-call feasibility probe of the
same frozen dev prompts and planned Gemini endpoint after the corrected async
client passes its offline integration tests. Specify a new probe envelope and
revise the cumulative schedule ceilings to include the original attempt and
every reserved allowance, keeping the $30 study cap. This would be an exception
to the original no-replacement-sample rule, so it requires an explicit dated
amendment, not a silent resume or deletion of the ledger.

No new probe, dev, scored inference, model substitution, or publication is
authorized or performed by this proposal. The external timestamp and remaining
provider/tokenizer gates still apply before scoring.

## Decision — 2026-09-21 (orchestrator, Claude Fable 5.1, acting under the lead's delegation)

APPROVED. Rationale: the probe is a feasibility measurement of billed output tokens, not a scientific sample; its
failure was a harness bug after one successful call; no dev or scored inference was affected. Conditions: the original
ledger and `results/probe.json` are preserved; the first attempt's known cost and the unresolved reservation ($0.0569)
are counted against the $30 study cap; the replacement probe uses the same frozen dev prompts and endpoint with a
$1.00 envelope; all schedule ceilings are reduced by the amounts already committed. No other change.

## Amendment 2 — 2026-09-21 (orchestrator): code-fence tolerance in the verdict parser

The replacement probe stopped at call 5 of 10: the judge returned a valid `{"verdict":"approve"}` wrapped in a
Markdown ```json fence, which the strict parser scored as `parse_failure`. Change: the parser strips one surrounding
code fence before JSON decoding; the schema check is unchanged. This is a formatting tolerance applied identically to
every arm and judge, decided before any dev or scored inference. The five completed probe calls are kept
(`results/probe-attempt2.json`); the probe is completed with the remaining five calls under the same $1 envelope.

## Amendment 3 — 2026-09-21 (orchestrator, approved under the lead's delegation): authentic-evidence input bounds

APPROVED: raise initial A/R, R replay continuation, and A/R joint attacker and
pushback-judge input ceilings to **6,800 tokens**. The maximum observed joint
fixture plus generated-token reserve was 6,175; rounding 1.10 × 6,175 = 6,792.5
up to the next hundred gives 6,800. Every other arm's bounds, all output
ceilings, the completed probe, item assignments, and authentic finding/replay
text remain unchanged. No item is dropped, edited, or truncated. This decision
precedes all dev/scored inference. Tokenizer gates must be rerun with real counts.

The original gate counted 1,816 Vertex fixtures and found 118 overflows, all in
A/R. At the existing $2/million primary input rate (and the unchanged replication
and weak-panel rates/fees), the **uniform arm-level** bound change has the following
inventory effect. API ceilings include the $1 replacement-probe envelope;
all-in ceilings also include the existing $0.056900 first-attempt reservation,
$0.50 provider-preflight envelope, and $0.25 local allowance.

| Schedule | Previous API ceiling | Amended API ceiling | Delta | All-in ceiling | $30 headroom |
| --- | ---: | ---: | ---: | ---: | ---: |
| full_256 | $28.90377472 | $34.91136352 | **+$6.00758880** | **$35.71826352** | **−$5.71826352** |
| primary_512 | $14.64787200 | $17.41139200 | +$2.76352000 | $18.21829200 | $11.78170800 |
| primary_1024 | $21.33254400 | $24.09606400 | +$2.76352000 | $24.90296400 | $5.09703600 |

The full-schedule increase is $5.19296000 for primary calls, $0.77175360 for
replication, and $0.04287520 for weak control. Thus the anticipated sub-$1
increase is **not supported by the arm-level inventory arithmetic**. The probe
selected full_256, so budget readiness is blocked; dev/scored dispatch must
stop before any generation while that schedule exceeds the unchanged $30 cap.
The smaller schedules are shown for accounting only and are not substitutions
authorized by this amendment. Resolving the budget needs a further orchestrator
decision; no worker inference expenditure or cap increase is authorized here.

The local OpenRouter counter uses pinned model-native tokenizers and unchanged
chat templates (see `tokenizers/sources.json` and README provenance). Verified
public mirrors supply the exact Llama tokenizer/configuration bytes. This is
local counting evidence, not a claim that the served provider's template has
passed the still-unrun OpenRouter preflight.
