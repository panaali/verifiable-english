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
$M run --split dev --run-id dev-tune-1 --authors opus,haiku,gemini --arms A2,A3,A4 --gemini-cap-usd 80
$M audit-export --run-id dev-tune-1
$M audit-run    --run-id dev-tune-1 --gemini-cap-usd 90   # same run ledger, raise the cap to cover audits
$M report       --run-id dev-tune-1
# (optional prompt/budget changes: bump PROMPT_VERSION, log them below, rerun with a new --run-id)
# 2. Freeze
#    edit PREREG-ASSIST.md line 1 -> "Status: FROZEN 2026-..", then:
$M hashes --write
git add experiments/assist-eval ve_experiments/assist_eval && git commit -m "PREREG-ASSIST: freeze"
uvx --from opentimestamps-client ots stamp experiments/assist-eval/PREREG-HASHES.txt
# 3. HELD-OUT evaluation (refuses unless FROZEN and hashes match)
$M run --split heldout --run-id heldout-1 --authors opus,haiku,gemini --arms A2,A3,A4 --gemini-cap-usd 80
$M audit-export --run-id heldout-1
$M audit-run    --run-id heldout-1 --gemini-cap-usd 90
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

## Tuning log

- v1 (`ve-assist-eval-prompts@1`): initial prompts; smoke only.
- v2 (`ve-assist-eval-prompts@2`, before any tuning run): added the one-step-per-claimed-sentence rule and the multi-anchor audit wording, in response to the smoke's collapsed graph.
