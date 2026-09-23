# `ve assist` evaluation (runner, smoke test, commands)

Design: [PREREG-ASSIST.md](PREREG-ASSIST.md). Code: `ve_experiments/assist_eval/`:

| Module | Purpose |
|---|---|
| `items.py` | DEV items and seeded HELD-OUT selection; checks the materials' hashes |
| `prompts.py` | Author prompts (task, VE guide, per-arm interface, Claude text protocol) and auditor prompts |
| `authors.py` | Claude CLI text-protocol author and Gemini Vertex function-calling author; per-call cost and ceiling |
| `loop.py` | `SessionRun`: the budgeted loop for arms A2/A3/A4, A2 whole-document evaluation, persistence |
| `audit.py` | Blind packets, cross-family audit, endpoints, report and human spot-check list |
| `pricing.py` | List prices used for budget matching |
| `cli.py` | Commands, registered `CONFIG`, PREREG hash manifest and held-out gate |

Each session writes `runs/<run-id>/<split>/<author>/<arm>/<item>/`:

- `prompt.json`: system prompt, opening materials and tools.
- `transcript.jsonl`: per turn, the reply, parsed calls, usage, cost and harness response.
- `session.json`: the `ve assist` ledger. It replays and is verified on audit export.
- `attempt-NNN.json`: A2 only, one ledger per attempt.
- `author-calls.jsonl` or the run's `gemini-ledger.jsonl`: audited raw calls.
- `proposer-calls.jsonl`: A4 only.
- `result.json`.

A session with `result.json` is skipped on rerun. An interrupted session is rerun from scratch, and completed model
calls replay from the ledgers at no cost.

## Commands

Set `UV_CACHE_DIR=/private/tmp/ve-uv-cache-assist`. Run sessions serially: one command at a time, since the Claude
ledgers are per session and the Gemini ledger is per run.

```sh
M="uv run python -m ve_experiments.assist_eval"
# 1. DEV tuning pass (all authors x arms x 12 DEV items; Gemini spend hard-capped by the run ledger)
# one author x arm per command, so that one Claude account serves the whole arm
$M run --split dev --run-id dev-tune-2 --authors opus --arms A2 --account saeedi.danial   # ... each author x arm
$M run --split dev --run-id dev-tune-2 --authors gemini --arms A2,A3,A4 --gemini-cap-usd 40
$M audit-export --run-id dev-tune-2
$M audit-run    --run-id dev-tune-2 --account saeedi.danial   # Codex audits Claude authors, Opus audits Gemini
$M report       --run-id dev-tune-2
# (optional prompt/budget changes: bump PROMPT_VERSION, log them below, rerun with a new --run-id)
# 2. Freeze
#    edit PREREG-ASSIST.md line 1 -> "Status: FROZEN 2026-..", then:
$M hashes --write
git add experiments/assist-eval ve_experiments/assist_eval && git commit -m "PREREG-ASSIST: freeze"
uvx --from opentimestamps-client ots stamp experiments/assist-eval/PREREG-HASHES.txt
# 3. HELD-OUT evaluation (refuses unless FROZEN and hashes match)
$M run --split heldout --run-id heldout-1 --authors opus,haiku,gemini --arms A2,A3,A4 --gemini-cap-usd 80
$M audit-export --run-id heldout-1
$M audit-run    --run-id heldout-1
$M report       --run-id heldout-1
```

Run a single author or arm with `--authors opus --arms A3`, and a subset of items with `--items 0,3` (index or id).

## Smoke test (2026-09-22)

`$M smoke --run-id smoke-2026-09-22`: one DEV item, arm A3, Opus 5.5 author, at most 30 tool calls. The summary
follows.

Run directory: `runs/smoke-2026-09-22/`. The item is DEV `i11e21a96aa6260b7bafaaec82c8810b9` (benign). The author run used
prompts v1; the audit below used the v2 audit wording.

| Turn | Calls | What happened | Cost |
|---|---|---|---|
| 1 | 10 | `freeze_target` (`@unit5 is calibrated.`) succeeded, then 9 `add_node`. One node, the n09 fact conjunction, had a parenthesis error, which the harness returned as `SyntaxError` with a span. | $0.0694 |
| 2 | 10 | The author re-added the facts and rule conjunctions, then added steps s_a to s_c, with 3 `check_step` results of FOLLOWS. | $0.1149 |
| 3 | 10 | 2 more `check_step` results of FOLLOWS, 6 `waive` (rule-declaration sentences and "remain unassumed"), then `finish(complete)`. | $0.0889 |

The session used 3 turns and 30 tool calls (the cap), with 0 protocol errors. Opus 5.5 spent **$0.2732** at list
price (cache reads in use), over 61.5 s. The tool reported **success**: the target was certified by replay, all 5
steps were certified, and there were 41 covered and 6 waived sentences.

The audit pipeline was then run end to end: `audit-export`, `audit-run` (one Gemini 3.1 Pro Vertex call, $0.0740),
and `report`. The audit **failed** the packet. Opus had collapsed the 16 claimed paragraphs into 4 steps: s_a states
only "unit5 is weighed_in" but is anchored to n18.1, n07.1, n03.1 and n08.1. Gemini flagged 12 claimed sentences as
unfaithful ("the formalisation states that unit5 is weighed-in, but the sentence concludes that unit3 is ready").
The report therefore shows `certified_unfaithful = 1`, the exact failure mode the plan's headline number exists
for. It also skips the intermediate sense commitments where P5 flaws live.

Change made before any tuning run (prompts v2): the task now requires one step per claimed sentence that states
exactly that sentence's conclusion. Audit packets now show "also anchored to" for multi-anchored nodes. The v1 smoke
artifacts are kept unchanged.

## dev-tune-1 (2026-09-23): DISCARDED

`runs/dev-tune-1/` is kept unchanged but is **not evidence**: it ran the unfixed tool (before the `ve-green-assist`
fixes merged from `ve-integration`), and the branch was switched during the run. Its report's "0 audits passed" is
an artefact. Diagnosis:

- The first Gemini A3 call was counted at ~3.5k input tokens by Vertex `countTokens` (the reservation allowed
  3,846 with the old 2% + 256 margin) but billed 4,004: `countTokens` under-counts the function declarations. The
  paid ledger recorded `panel_validation_halt` ("provider exceeded per-call token cap"), which is sticky for model
  `pro`. Every later Gemini session (11 A2, 12 A3, 12 A4) aborted at $0, and so did every Gemini audit call.
- `audit-run` therefore audited exactly one packet (a Gemini A4 packet with no units, which Opus answered with
  `{"units": []}`), then raised on the first Claude-author packet (Gemini auditor, halted ledger) and exited 1.
  96 of 97 packets had no verdict, and `report` counted every unaudited tool success as "certified unfaithful".

Fixes: the Gemini margin is now 5% + 2,048 tokens; `audit-run` logs auditor errors to `audit/errors.jsonl`,
continues, and exits 1 while any packet lacks a verdict; an empty packet fails without an auditor call; `report`
counts certified-unfaithful only for audited sessions; a Claude infrastructure abort (e.g. a session limit) or a
halted Gemini ledger stops the run instead of recording failures.

## dev-tune-2 changes (fixed tool, prompts v3)

- Tool: `ve assist` from `ve-integration` (tag `ve-green-assist`). Every session's final ledger, and every A2
  attempt ledger, is checked with `ve.assist.verify_session` (dossier, arm options, the session's dedicated
  `proposer-calls.jsonl`); an unverified ledger is never a success (`result.json` `verification`).
- Proposer: `--proposer-model haiku|sonnet|opus` (default haiku), recorded per session; proposer calls are priced
  at that model's list price, including failed calls and retried attempts.
- Success rule: the fixed tool reports any waiver of an asserting sentence as "never success". Every P5 dossier has
  given meta-sentences that no VE statement states ("Rules r00, r14 are declared.", "The checks that ... remain
  unassumed."), so strict tool success is structurally unreachable. `tool_success` here = status success, or the
  waiver line is the only failure and every waived sentence is given; the waivers are audited and must be
  "acceptable". `tool_success_strict` keeps the tool's own verdict.
- Auditors (lead decision 2026-09-23): GPT-6 Astra via `codex exec -s read-only -c model_reasoning_effort=high`
  audits Claude authors; Opus 5.5 audits Gemini. Gemini is an author only. Each verdict records `auditor` and
  `auditor_model`.
- Harness: `finish` with verdict "complete" is refused unless the evaluation success rule holds (Haiku finished
  "complete" after a failed `freeze_target` in a probe).
- Accounts: `--account LABEL|main`; one account per author x arm.
- Report: per-session failure attribution (`attribution`, `failing_units` with node provenance): proposer
  candidate accepted unchanged / author-written / audit disagreement (unclear or missing verdicts) / tool refusal /
  budget / infrastructure / ledger verification.

## dev-tune-2 results (2026-09-23, fixed tool, prompts v3)

`runs/dev-tune-2/`: 12 DEV items (4 benign, 4 shift, 4 smuggle) x 3 authors x 3 arms = 108 sessions, all ledgers
verified by `verify_session` (108/108), all 108 packets with a verdict (56 GPT-6 Astra, 35 Opus 5.5, 17 empty packets
failed without a call). Budget $2.00/item. Claude authors ran on account saeedi.danial; that account's OAuth token
was revoked during the audit, so the last 7 Opus audit calls ran on the main account
(`audit/opus-audit-calls.main.jsonl`; no author arm mixes accounts).

| Author | Arm | Tool success | Audit pass | Certified-faithful (benign) | Certified-unfaithful | Faithful-complete | Spend (list) |
|---|---|---|---|---|---|---|---|
| Opus 5.5 | A2 | 4 | 12 | 4/4 | 0 | 9 | $1.31 |
| Opus 5.5 | A3 | 4 | 12 | 4/4 | 0 | **12** | $8.29 |
| Opus 5.5 | A4 | 4 | 12 | 4/4 | 0 | **12** | $8.78 |
| Haiku 4.5 | A2 | 1 | 2 | 1/4 | 0 | 1 | $0.99 |
| Haiku 4.5 | A3 | 0 | 1 | 0/4 | 0 | 0 | $10.73 |
| Haiku 4.5 | A4 | 0 | 5 | 0/4 | 0 | 0 | $14.12 |
| Gemini 3.1 Pro | A2 | 3 | 8 | 3/4 | 0 | 5 | $0.86 |
| Gemini 3.1 Pro | A3 | 4 | 11 | 4/4 | 0 | 4 | $3.51 |
| Gemini 3.1 Pro | A4 | 0 | 12 | 0/4 | 0 | 0 | $6.07 |

Tool success = the evaluation rule above; strict tool success is 0/108 (every session waives the given
meta-sentences). No flawed item was certified (0 alarms).

Failure attribution (`report.json` `attribution`), over 108 sessions: proposer candidate accepted unchanged 0;
author-written audit failures 16 (Haiku 12, Gemini 4); author formalised nothing (empty packet) 17 (Haiku 16,
Gemini 1); audit disagreement 0; tool refusal 29 (Gemini 21, Opus A2 3, Haiku 5); budget 3; infrastructure 0 in the
final records. Tool refusals are graph failures the author did not fix: claimed sentences waived (Gemini A4
benign: it finished "gap" with the waiver line as the only failure plus waived claimed sentences), the target not
stated by a step, uncovered given sentences, or a gap route with more unproved steps than it named.

The proposer played no part: Opus and Haiku never called `propose`; Gemini called it twice (one A4 session), and
both calls failed with the revoked saeedi.danial token (recorded in the ledger, $0). The `--proposer-model sonnet`
rerun (`dev-tune-2s`) was therefore not triggered: no audit failure involves an accepted candidate.

Spend: Claude authors $44.2 at list price (subscription); Gemini authors $12.88 real (Vertex, including aborted attempts; $0.95 of it on the
first ledger, halted by an under-counted call, `gemini-ledger.halted-1.jsonl`); Opus audits $3.25 at list price;
Codex audits 566k tokens (subscription). Gemini infrastructure: 429 and 504 errors caused 13 aborted session
attempts (kept as `result.aborted-N.json`); each was restarted with fresh call ids.

## Tuning log

- v1 (`ve-assist-eval-prompts@1`): initial prompts; smoke only.
- v2 (`ve-assist-eval-prompts@2`, before any tuning run): added the one-step-per-claimed-sentence rule and the multi-anchor audit wording, in response to the smoke's collapsed graph.
- v3 (`ve-assist-eval-prompts@3`, before dev-tune-2): coverage text for the fixed tool (claimed sentences derived and
  never waived; given meta-sentences waived; the waiver status line alone is acceptable); `finish` "complete" is
  refused by the harness otherwise; the auditor may accept a waiver of a "remain unassumed" sentence.
