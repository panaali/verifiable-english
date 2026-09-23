# `ve assist` evaluation (runner, smoke test, commands)

Design: [PREREG-ASSIST.md](PREREG-ASSIST.md). Code: `ve_experiments/assist_eval/`:

| Module | Purpose |
|---|---|
| `items.py` | DEV items and seeded HELD-OUT selection; checks the materials' hashes |
| `prompts.py` | Author prompts (task, VE guide, per-arm interface, Claude text protocol) and auditor prompts |
| `authors.py` | Claude CLI text-protocol author and Gemini Vertex function-calling author; per-call cost and ceiling |
| `loop.py` | `SessionRun`: the budgeted loop for arms A2/A3/A4, A2 whole-document evaluation, persistence |
| `dossier.py` | The waiver allowlist W(item), reference formalisations of given sentences, dossier graph checks |
| `scoring.py` | Evaluation success and the faithful-complete gap route |
| `audit.py` | Blind packets, cross-family audit (Codex all, Opus also Gemini), endpoints, report, spot-check list |
| `pricing.py` | List prices used for budget matching |
| `cli.py` | Commands, registered `CONFIG`, PREREG hash manifest, held-out gate, proposer smoke |

Each session writes `runs/<run-id>/<split>/<author>/<arm>/<item>/`:

- `prompt.json`: system prompt, opening materials and tools.
- `transcript.jsonl`: per turn, the reply, parsed calls, usage, cost and harness response.
- `session.json`: the `ve assist` ledger. It replays and is verified on audit export.
- `attempt-NNN.json`: A2 only, one ledger per attempt.
- `author-calls.jsonl` or the run's `gemini-ledger.jsonl`: audited raw calls.
- `proposer-calls.jsonl`: A4 only.
- `result.json`.

A session with `result.json` is skipped on rerun. An interrupted session is rerun from scratch, and completed model
calls replay from the ledgers at no cost. An infrastructure-aborted session keeps `result.aborted-N.json`; its rerun
starts with every earlier attempt's spend charged to the item's $2 budget and stops when that budget is exhausted.

## Commands

Set `UV_CACHE_DIR=/private/tmp/ve-uv-cache-assist`. Run sessions serially: one command at a time, since the Claude
ledgers are per session and the Gemini ledger is per run. Claude calls use the main account (the default Claude
configuration directory); the saeedi.danial token is revoked and no longer a default.

```sh
M="uv run python -m ve_experiments.assist_eval"
# 0. Proposer smoke on DEV (<= 2 proposer calls; done 2026-09-23, runs/proposer-smoke-2026-09-23/)
$M proposer-smoke --run-id proposer-smoke-2026-09-23
# 1. Freeze
#    edit PREREG-ASSIST.md line 1 -> "Status: FROZEN 2026-..", then:
$M waivers --write          # the preregistered allowlist W (waivers.json)
$M hashes --write           # PREREG text, tool, prompts, W, items, CONFIG
git add experiments/assist-eval ve_experiments/assist_eval && git commit -m "PREREG-ASSIST: freeze"
uvx --from opentimestamps-client ots stamp experiments/assist-eval/PREREG-HASHES.txt
# 2. HELD-OUT (refuses unless FROZEN, hashes (whole ve/ package included) and W match, no setting flag differs
#    from CONFIG, the author/arm set is the FULL registered one, no other held-out run id exists, and no
#    account-override environment variable is set). Rerun the same command to resume after an abort.
$M run --split heldout --run-id heldout-1        # opus,gemini x A2,A3,A4; Gemini run ledger capped at $40
$M audit-export --run-id heldout-1
$M audit-run    --run-id heldout-1   # Codex (pinned gpt-6-astra) audits every packet; Opus also audits Gemini's
$M report       --run-id heldout-1   # report.json (primary: Opus A3 vs A2 paired) + audit-spotcheck.jsonl
```

On DEV, `--budget`, `--max-tool-calls`, `--proposer-model`, `--account`, `--gemini-cap-usd` (at most $40) and
`--items` remain available for tuning; on held-out they are rejected unless equal to CONFIG (`--items` always).

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

## Review fixes (2026-09-23, after dev-tune-2; prompts v4, scoring v2)

Two xhigh reviews (Astra, Opus; `manage-agents/reviews/assist-heldout-review-*.md`) returned FIX FIRST. Changes:

- **Waivers (Astra A1, Opus A2).** A preregistered allowlist W(item) computed from the public dossier text
  (`dossier.py`, hashed as `waivers.json`): declared-rule lists, "remain unassumed" metadata, lot/sample
  statements (waive-only), unused facts, and dead rules that no claimed sentence relies on. Waivers must lie in W;
  no node may anchor to a waive-only sentence; a given-anchored assumption must be entailed by its anchors'
  reference content (closes the anchoring smuggle in full, not only the conditional-to-fact case); no assumption
  may entail a "remain unassumed" check. Authors see the rule in words, not the list (dead rules mark underivable
  conditions). Opus's point (c): "Lot U supplied sample U." is formalisable (`supplied`) and is NOT waive-only; it
  is in W as an `unused-fact` because no rule and no claimed sentence uses it (decision 1 puts unused facts in W),
  and anchoring anything but its content to it fails the content check.
- **Faithful-complete (Astra A2, Opus A1).** `scoring.gap_route`: every claimed sentence has an anchored step,
  verified ledger, every non-gap step certified, every gap step refuted by a checker countermodel (unchecked or
  unknown steps never count) and not entailed by the whole dossier, no violations, and `gap_located` required. A
  hard dependency-alignment gate was tried and rejected: faithful "would imply" steps legitimately use earlier
  results that are not the paragraph's P5 parents (e.g. `s_n18b <- s_n01`, 12 faithful dev sessions). Alignment is
  audited instead (packets list each step's "reasons").
- **Audit (Astra A5, Opus A3).** Codex audits every packet; Opus also audits Gemini packets; a packet passes only if
  both pass. Waiver units show W codes and fixed descriptions, never the author's reason. Author-declared glosses
  are listed apart and marked AUTHOR-WRITTEN. Omitted sentences are units. The auditor prompt drops "a fact never
  used" and is frozen in the manifest.
- **Endpoint and claim (Astra A3/A4, Opus A4).** Primary: Opus A3 vs A2, paired by item at the same total budget
  (exact sign test). Gemini secondary, Haiku dropped, A4 exploratory ("proposer offered, uptake n"). The ">= 6/12"
  threshold is removed; the claim is the Opus review's minimum claim (PREREG "Claim scope").
- **Freeze (Astra A6, Opus B1-B3).** The manifest hashes the PREREG text, W and every executable setting; held-out
  runs reject any deviating flag. Default account = main. Gemini cap $40. Stale README/CONFIG/PREREG text updated.
- **Restarts (Astra B7).** Every attempt counts toward the item budget and the reports: restarts start with the
  aborted attempts' spend, budget exhaustion stops the item, Claude prior attempts and failed calls are charged,
  and a Gemini 5xx/timeout charges the paid ledger's unknown-billing hold. `report` sums all attempts and
  reconciles Gemini against its paid ledger.
- **Proposer restored.** `proposer-smoke` on DEV, main account: 1 Haiku call, one valid candidate, $0.0051.

### dev-tune-2 replayed under the new scoring ($0, `runs/dev-tune-2/replay-v4/report.json`)

Deterministic parts (W, graph checks, gap route, all-attempt spend) are recomputed from the committed ledgers. The
audit part is a **legacy proxy**: the packets were audited once under the old layout (Codex for Claude authors, Opus
for Gemini) and that single verdict stands in for every required auditor; the new packets (W codes, omitted units,
reasons) and the second (Codex) audit of Gemini packets were not run (no model calls).

| Author | Arm | Tool success | Faithful-complete | Gap located | Sessions with violations | Alarms | Spend, all attempts | Items over $2 |
|---|---|---|---|---|---|---|---|---|
| Opus 5.5 | A2 | 4 -> 4 | 9 -> **9** | 5 | 0 | 0 | $1.31 -> $1.31 | 0 |
| Opus 5.5 | A3 | 4 -> 4 | 12 -> **12** | 8 | 0 | 0 | $8.29 -> $8.29 | 0 |
| Opus 5.5 | A4 | 4 -> 4 | 12 -> **12** | 8 | 0 | 0 | $8.78 -> $8.78 | 0 |
| Gemini 3.1 Pro | A2 | 3 -> 3 | 5 -> **4** | 5 | 7 | 0 | $0.86 -> $0.86 | 0 |
| Gemini 3.1 Pro | A3 | 4 -> 4 | 4 -> **4** | 5 | 2 | 0 | $3.51 -> $4.35 | 0 |
| Gemini 3.1 Pro | A4 | 0 -> 0 | 0 -> **0** | 6 | 5 | 0 | $6.07 -> $10.33 | 2 |
| Haiku 4.5 | A2 | 1 -> 1 | 1 -> **1** | 1 | 5 | 0 | $0.99 -> $0.99 | 0 |
| Haiku 4.5 | A3 | 0 -> 0 | 0 -> **0** | 0 | 8 | 0 | $10.73 -> $10.73 | 0 |
| Haiku 4.5 | A4 | 0 -> 0 | 0 -> **0** | 0 | 2 | 0 | $14.12 -> $14.12 | 0 |

The one change is Gemini A2 `i0e03b71` (the Opus-review A1 instance): claimed `n18.2` has no step and three live
rules (`r15.1`, `r15.2`, `r15.4`) were waived. No dev node anchors to a waive-only sentence and no dev assumption
fails the content check. Spend rises only for Gemini A3/A4 (aborted attempts and 504 holds now counted); two
Gemini A4 items exceed $2 over all attempts (`i910d7c5`: $2.01 recorded, $4.46 with holds; `i248c407`: $2.05
with holds), which the new restart accounting prevents. Primary endpoint on dev (tuning, not evidence): Opus A3
12/12 vs A2 9/12, 3 discordant pairs all favouring A3, sign test p = 0.25; A3 12/12 has an exact lower bound of
0.779; alarms 0/8 (upper bound 0.312). A4: proposer offered, uptake 0/12 for every author.

## Re-review fixes (2026-09-23, prompts v5, scoring v3)

Both re-reviews (`manage-agents/reviews/assist-heldout-review2-{astra.final,opus}.md`) returned FIX FIRST. Changes:

- **Complete graph in every packet (Astra A1).** Packets carry every node under neutral ids (N1, N2, ...: kind,
  statement, anchors, derived-from edges), unanchored helpers included, and each unit's "reasons" follow helpers
  down to anchored nodes. Astra's two certified graphs (stated reason vs an unstated alternative behind a helper) now
  give different packets (`test_packet_exports_the_complete_graph_so_a_helper_cannot_hide_the_reasoning`). No
  check result, status or certification is exported; author node names are replaced.
- **Anchors both ways (Astra A2, Opus A1/A2).** Per anchor: each anchor sentence ALONE must entail the assumption
  (Q anchored to "P" and "if P then Q" is a violation; split it). Coverage: the nodes anchored to a formalised
  given sentence, steps included, must together entail its reference formalisation. Claim steps: a step anchored to
  a claimed sentence must be decided non-valid and may use only the (unit, term) atoms its sentence mentions, so
  Opus's tautology construction no longer reaches the gap route. The `scoring.py` docstring that claimed
  certification alone blocked it is corrected. **Dev replay:** 0 of the 108 dev-tune-2 sessions gain a violation;
  all 42 faithful-complete sessions (718 claim-anchored steps) pass (`test_no_faithful_dev_session_is_rejected_by_the_new_checks`;
  `runs/dev-tune-2/replay-v5/`).
- **Freeze (Opus A3, Astra A3).** The manifest hashes every file of `ve/` (checker, entailment, parser, English
  layer, lexicon data) besides the harness. The held-out gate requires the full registered author and arm set and
  refuses a second held-out run id. `VE_CLAUDE_ACCOUNT_CONFIG_DIR` / `CLAUDE_CODE_OAUTH_TOKEN` (which could reroute
  "main") make every real Claude backend refuse to start. Codex runs with `-m gpt-6-astra`; a reported model other
  than that (or none) voids the call; the Opus auditor rejects any served model but `claude-opus-5-5`.
- **Budget (Astra B, Opus B1).** `PaidClient` calls a `before_attempt` gate before EVERY backend attempt (its
  internal 5xx retries included) and the Claude endpoint a `before_retry` gate; both check the item budget with what
  the call was already charged. Every Gemini turn charges the paid ledger's completions and holds for its identity
  (a recovered 504's holds included; a billed reply that fails validation is charged), and every exit reconciles the
  session with the ledger. Astra's cases are tests: after $1.70, 504s stop the item at $1.90 (was $2.31 committed,
  $1.70 reported); four failed attempts after $1.40 stop at $1.80 (was $2.52). An item over budget over all attempts
  scores as a failure. The Claude ceiling now prices input at the cache-write rate (dearer than uncached).
- **Blinding (Opus C2).** Each Codex call runs in a fresh temporary directory holding only `packet.json`; `--json`
  events are kept in the ledger (`stdout`), and any tool use (command, file read, MCP, web) voids the call.
- **No real calls from tests (Opus C3).** `tests/conftest.py` fails any test that starts `claude`, `codex`, `gemini`
  or `security`, or connects to a non-loopback address, even when the code under test swallows the error.
- **Auditor spend cap.** `audit-run --max-usd X` gates each priced (Opus) auditor call on its ceiling (output capped
  at 6,000 tokens, retries off; failed calls charged).

### W and the held-out text (disclosure, Opus C1)

`dossier.py` (W and the reference reading) was written on 2026-09-23 AFTER the held-out dossier text had been read
(the W document covers both splits). Two parsing branches fired only on held-out text and are REMOVED: the "lot
tail" split of a given "If A, then B. unitX is a sample of lot unitY." sentence (with the second `LOT` form), and
the "would yield" verb of the "would imply ..., respectively" pattern. Removing "yield" changes no W entry (those
sentences' mentions already mark the rules as relied on). The five held-out "rule + lot" givens (`i91ead25` r12.2,
`i0458325` r01.2, `ibdc20cc` r00.2, `i31ec957` r12.2, `iacc3cf` r05.2) now fall to the generic `unparsed` kind:
never in W (they were `dead-rule` waivers before), no reference, so no deterministic anchor or coverage check;
the auditor judges them, and its prompt now says that stating every expressible part of a partly inexpressible
sentence is faithful. No dev sentence is `unparsed`.

Branches the held-out items trigger (every one also fires on dev, apart from `unparsed`): given kinds `declared`
60, `unassumed` 12, `lot` 4 ("The sample from lot ..." form), `supplied` 3, `facts` 12, `rule` 259, `unparsed` 5;
W codes `declared` 60, `unassumed` 12, `lot-sample` 4, `unused-fact` 3 (the `supplied` facts), `dead-rule` 31;
claimed-sentence readings "the immediately preceding TERM result" (48 sentences) and "would imply/establish ...,
respectively" (9; "yield" 3 no longer matched); 88 dead rules relied on. Dev: `declared` 60, `unassumed` 12, `lot`
9, `supplied` 3, `facts` 12, `rule` 264; W `dead-rule` 36, `lot-sample` 9, `unused-fact` 3; 76 relied on.

### New dual audit on a dev-tune-2 copy (2026-09-23, LABELLED DEV PROXY; `runs/dev-tune-2/audit-v5-proxy/`)

One `audit-run` with the new packets (complete graph) and auditor prompt v5 on a copy of dev-tune-2's sessions
(`--max-usd 0.40`; the copy's session directories stayed outside the repo, so packet ids differ from the legacy
ones and are matched by session directory). Codex (`gpt-6-astra`, reported model confirmed on all 91 calls, no tool
use) audited all 91 non-empty packets (17 empty packets fail without a call). Opus audited 2 Gemini packets for
$0.258721 before the cap stopped it; the other 33 Gemini packets lack their Opus verdict and count as unaudited.
This validates the new path end to end; it is a dev proxy, not a validation of the audit.

Agreement with the old single-auditor verdicts (packet pass/fail): Codex 57/91 (Opus-authored 32/36, Gemini 12/35, Haiku 13/20),
combined decision 46/58 where complete. Every
disagreement is old PASS -> new FAIL (34 Codex, 1 Opus); none goes the other way: the full graph and helper rule
make the audit stricter. Opus faithful-complete under the new audit: A2 9/12 (unchanged), A3 11/12 (was 12), A4
12/12; primary dev pairing 9 both / 2 A3-only / 0 A2-only / 1 neither, sign p = 0.5. Gemini rows are not
interpretable (33/36 packets missing the Opus verdict).

## Tuning log

- v1 (`ve-assist-eval-prompts@1`): initial prompts; smoke only.
- v2 (`ve-assist-eval-prompts@2`, before any tuning run): added the one-step-per-claimed-sentence rule and the multi-anchor audit wording, in response to the smoke's collapsed graph.
- v3 (`ve-assist-eval-prompts@3`, before dev-tune-2): coverage text for the fixed tool (claimed sentences derived and
  never waived; given meta-sentences waived; the waiver status line alone is acceptable); `finish` "complete" is
  refused by the harness otherwise; the auditor may accept a waiver of a "remain unassumed" sentence.
- v4 (`ve-assist-eval-prompts@4`, after the dev-tune-2 reviews): the coverage text states the allowlist rule and the
  anchor content check; the gap text states the gap-route conditions; the auditor prompt audits W codes, omitted
  units and step reasons and drops "a fact never used". Not run on dev with authors (replay only).
- v5 (`ve-assist-eval-prompts@5`, after the re-reviews): author text states the per-anchor rule (one assumption per
  sentence), full coverage of given sentences and the claim-step rules; the auditor prompt describes the complete
  node graph and helper nodes and says how to judge partly inexpressible sentences. Not run on dev with authors;
  the auditor prompt was run once on a dev-tune-2 copy (above).
