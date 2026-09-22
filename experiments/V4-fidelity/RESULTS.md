# Infrastructure verification, 2026-09-22

Built on branch `codex/v4` from `ve-integration` at `10b4495`. No bulk model run. Live spend: **A 12 calls** (five canaries, five trivial calls, two fixed-cwd canaries) and **B 3 calls** (one per smoke item). Resuming/reparsing the first saved stream did not spend a call. All 15 calls reported `claude-opus-5-5`; all init tool and MCP inventories were empty. CLI `2.1.280 (Claude Code)`, binary SHA-256 is recorded with every attempt. Every request was a fresh single turn, MAX_THINKING_TOKENS=1024, effort low, no configured SDK or harness retry, no fallback-model flag.

## A: the endpoint audit found a real limitation

| Probe | Input tokens by fresh call | Strict invariant |
|---|---|---|
| Canary, random temp cwd | 375, 374, 374, 374, 374 | Failed; 4 rejected |
| Trivial `Reply with exactly OK.`, random temp cwd | 294, 297, 296, 297, 295 | Failed; 4 rejected |
| Canary, fixed empty temp cwd, recreated per call | 334, 334 | Passed for these 2 diagnostics |

Input totals include system/user content and CLI wrapper/context. All cache-read and cache-creation counts were zero in A. The **absolute wrapper overhead is not separately measured**: the CLI does not supply an exact content-only token count. Repeated-content variation was 1 token for the original canary and 3 tokens for the original trivial prompt, then 0 for the two fixed-cwd canaries. The final backend asserts constant input count for identical content, and can assert absolute residual overhead across different prompts when supplied an independent exact `content_tokens` count. Do not label 334 as absolute overhead.

Canary output (full verbatim responses and usage are in `results/endpoint-summary.json` and the raw ledgers):

> You are a Claude agent, built on Anthropic's Claude Agent SDK.

Both fixed-cwd canaries also identified an environment block appended to the user message: `/private/tmp/ve-claude-v4-empty`, not a git repository, darwin/Darwin 25.3.0, shell unknown; an Opus 5.5/model-id/June-2026-cutoff block; `15000000 tokens left`; and the date `2026-09-22`. They reported no memory, files, attachments or tools. The first canary did not mention the environment block, demonstrating that self-report is not a complete context attestation. All five trivial outputs were exactly `OK`, including the four rejected for overhead drift.

The final implementation uses the fixed empty directory to remove random-cwd token variation. Fresh config/home directories remain isolated per call, and only the OAuth access token is copied into the child environment. Existing directories are never deleted or reused. Safe mode disables account/project customizations, but **extra provider/CLI identity and environment context remains observable**. `--bare` is incompatible with subscription OAuth in the installed CLI. These controls do not establish API equivalence or pass a no-extra-context gate. A full five-plus-five verification of the final fixed-cwd variant remains pending because A's 12-call ceiling was reached.

The first raw stream was initially rejected by an overly strict parser: built-in agent names are always in init, and thinking/text arrive as chunks with the same message ID. An offline correction revalidated that saved stream. The original error row and revalidation reason remain in the ledger. No failed endpoint call was secretly replayed.

## B: three engineering smoke items

60 items were generated locally (20 per label), passed the existing E0 mechanical fit checks plus VE type/parse roundtrips, and had labels validated by independent SAT solving with VE-evaluated witness models. No Opus call generated the gold items. The corpus and exact seed/hash are frozen in `manifest.json`; generation adaptations and upstream source are in `PROVENANCE.md`.

| Item | Answer (correct) | Exact gold translations, including query | Faithful and certified | Input | Output | Thinking |
|---|---|---:|---|---:|---:|---:|
| v4-000 | True | 28/28 | yes | 3476 | 5298 | 481 |
| v4-001 | False | 31/31 | yes | 3921 | 5697 | 373 |
| v4-002 | Uncertain | 27/27 | yes | 3521 | 5458 | 710 |

All **86/86** premise/query translations matched gold ASTs exactly. The True and False items supplied graphs whose deductions were certified and bound to the translated premises and query polarity. The Uncertain item supplied two finite models satisfying the submitted premises, one for each query polarity; both were checked by VE. Its `query_bound=false` and `premise_bound=false` fields refer to the non-certifying query graph, not the two-model uncertainty certificate. Python checker replay only; no Lean claim. These three samples are engineering smoke evidence, not a fidelity-rate estimate or frontier-benefit result.

## Offline verification

Serial regression command: `UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run pytest -q tests/test_llm.py tests/test_argument.py tests/test_argument_adversarial.py tests/test_equivalence.py tests/test_v4_infrastructure.py`. Result: **102 passed, 1 live test deselected**. The 18 new V4 cases include model fallback, truncation, ambient config isolation, cached token accounting, resume/no-retry behavior, overhead drift, SAT truth tables, all 60 gold labels, certified mistranslations, extra assumptions, quantifier/argument order, xor equivalence, and both-polarity uncertainty witnesses.

## Open issues

- Extra endpoint context remains; fixed-cwd constancy has only two diagnostic replicates. Absolute wrapper overhead, API equivalence, actual internal thinking control and provider-internal transport behavior are not independently established.
- The full ProverGen LLM language-realization stage was replaced with declared compositional English. This is a symbolic-generator adaptation with a restricted language distribution; lexical meanings are supplied by the vocabulary. Upstream licensing of redistributed rule templates needs clarification before broader redistribution.
- The preregistration is local, not externally timestamped. Human audit of 12 preselected item clusters, independent-model fidelity audit, API replication, full k=3 sampling and bulk subscription approval are pending. The smoke IDs must be excluded from confirmatory rates or a fresh study generated.
- No C/D calibration, debate, or powered comparison was built or run.

## Full B controls revision (before the main run)

Lead authorized serial subscription use. The final ten-call endpoint audit succeeded: five canaries **337/337/337/337/337** input tokens; five trivial probes **259/259/259/259/259**, all `OK`, all served `claude-opus-5-5`. These fixed reference-input baselines include supplied text; absolute wrapper-only overhead is still **unmeasured**, not 337 or 259. Full logs: `results/endpoint-controlled.jsonl`. Fixed empty cwd, shell `/bin/sh`, locale `en_US.UTF-8`, UTC; host release pinned in attempt controls. The shipped CLI reads the real date despite exposing an unused override flag, so calls are guarded before/after against the fixed UTC date `2026-09-22` and stop at rollover. There is no clock tampering or asserted unsupported override.

The SDK identity prefix **“You are a Claude agent, built on Anthropic's Claude Agent SDK.” is an uncontrolled constant**. Injected environment/model/cutoff/token-budget/date context remains observable. New model identities in C necessarily have model-specific constant context, not identical overhead across models. Equal counts and canary reports are not complete provider-context attestation.

Fresh main-study corpus: `items-b.jsonl`, seed 2026092217, 60 items, no prior smoke identities reused. Revised protocol and material hashes are in `PREREG-B.md` / `HASHES`; the earlier smoke protocol is preserved as `PREREG-B-smoke.md`. Human and independent-model fidelity audits remain deferred.
