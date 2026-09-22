# Proposed amendment — 2026-09-21 — NOT APPROVED OR EXECUTED

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
