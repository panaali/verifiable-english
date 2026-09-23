Status: DRAFT (pre-tuning, prompts v2; the manifest stamped on 2026-09-22 records this pre-tuning state). Freeze after the DEV tuning pass: set this line to "Status: FROZEN <date>", run `hashes --write`, commit, OpenTimestamps-stamp PREREG-HASHES.txt, then run held-out.

# PREREG-ASSIST: budgeted evaluation of `ve assist` on P5 dossiers

Plan: [PLAN-ASSIST.md](../../PLAN-ASSIST.md). The final "After review" section is binding. Runner:
`ve_experiments/assist_eval/` (`python -m ve_experiments.assist_eval`). Hash manifest:
[PREREG-HASHES.txt](PREREG-HASHES.txt). It covers the tool version, every tool and runner source file, each author
system prompt (arm x protocol), the auditor prompt, both item-id lists and the registered configuration
(`CONFIG` in `cli.py`: budget, limits, success rule and threshold). The manifest's OpenTimestamps proof is
`PREREG-HASHES.txt.ots`. The held-out command refuses to run unless line 1 says FROZEN and the manifest recomputes
byte-for-byte.

## Question

Can tool-using agents author faithful, checker-certified VE formalisations of P5 dossiers when they get an
interactive sentence-level tool and a fixed total budget? Which part of the tool matters: checker feedback,
interactivity, or the proposer?

## Items

- **Tuning (DEV):** the 12 P5 DEV items (`materials/dev.jsonl.gz`; 4 families x benign/shift/smuggle). Prompts,
  budget and limits may change during this pass only. DEV results are reported as tuning results, never as
  evaluation results.
- **Evaluation (HELD-OUT):** 12 P5 *scored* items chosen by seeded sampling (`items.py`, seed 20260922). The
  selection shuffles the 24 families, keeps 12 and assigns 4 benign / 4 shift / 4 smuggle through a seeded shuffle.
  It takes one item per family. Reports label these items "held-out P5 scored items". The ids are in the manifest.
  Labels are used only for this stratification and for post-hoc scoring. No author or auditor prompt contains
  label content.
- The materials are byte copies of ve-codex `experiments/P5-shifting-definitions` (commit afa11f4). Their sha256
  values equal that directory's MATERIALS-HASHES.txt, and the loader checks them.

The harness supplies the target SENTENCE (the root paragraph's conclusion). The author must formalise that sentence
and freeze its formal statement before adding any node (orchestrator decision a). The frozen target is audited for
fidelity like every other node.

## Arms (same task text and item materials in every arm)

| Arm | Interface |
|---|---|
| A1 | Existing P5 one-shot results, cited only: Gemini 3.1 Pro, DEV, surface VE 0/12 and schema-JSON 0/12 replay after one repair. No fidelity assessment. |
| A2 | Checker-feedback-only retries. Each turn the author writes the whole graph as one JSON document. The harness freezes the targets from the first freezing document, builds a fresh session, checks every step and returns diagnostics (parse errors, follows/countermodel/unknown with models, unanchored and uncovered). This repeats until success, `finish`, or budget. |
| A3 | Interactive `ve assist` tools, no proposer, premise suggestions off. |
| A4 | Full tool: A3 plus the Haiku 4.5 proposer (`propose`/`accept`). Premise suggestions are off. |

Authors: Gemini 3.1 Pro (Vertex through `ve_experiments.paid`, native function calling, thinking LOW); Opus 5.5
(effort medium) and Haiku 4.5, both through the audited claude CLI on account saeedi.danial with
`CLAUDE_CODE_NO_MODEL_FALLBACK=1`.

**Claude tool-call protocol.** The controlled claude CLI endpoint runs with tools disabled and is single-turn. Each
author turn is therefore one fresh CLI call. The system prompt holds the task, the VE guide and the tool list as
JSON schemas. The user message holds the item materials and every earlier turn: the author's reply and the harness
response. The author acts by ending its reply with one fenced JSON block, `{"calls": [{"tool", "arguments"}]}`,
holding 1 to 10 calls that run in order. A reply without a valid block is a protocol error: it is charged, reported
back, and the loop continues. Gemini uses native function calls with the same tool schemas and the same 10-calls-per-turn
cap. Both get the same `[budget]` line after every turn.

## Budget (matched TOTAL per item, identical across arms and authors)

- A hard cap of **$2.00 per item** on author plus proposer spend, costed at list price. Claude uses Anthropic API list
  price with the CLI cache breakdown: Opus 5.5 $4 in / $20 out / $5 cache write / $0.20 cache read; Haiku 4.5
  $1 / $5 / $1.25 / $0.10. Haiku subscription calls are costed at API list price (orchestrator decision c). Gemini
  3.1 Pro costs $2 in / $12 out, with thoughts billed as output and cached input at the full rate
  (`ve_experiments.paid`).
- Before every author call the harness computes that call's worst case: all input uncached, 16,000 output tokens
  including thinking. It stops if the spent amount plus this ceiling would exceed the cap. Proposer calls are gated
  the same way. Spend therefore never exceeds the cap.
- Secondary limits: 60 turns, 250 tool calls, 10 calls per turn, and 8,000 characters per tool result (larger
  results are truncated and flagged). Gemini input is capped at 190k tokens, below the long-context price tier.
- Auditor spend is evaluation cost and is not charged to the item.

## Endpoints

Per session the tool's `status` reports **tool success**: every target is certified by graph replay, every step is
certified, every asserting sentence is covered or waived, no unanchored assumption is load-bearing, no declared
vocabulary carries a target, and the assumptions are consistent.

**Fidelity audit.** This is a separate step, blind to proof status, and done by a model from a different family.
`audit-export` writes one packet per session. A packet holds the sentences, the predicate glosses, and per asserting
sentence either the deterministic paraphrases of its anchored nodes (plus the frozen conclusion for the target
sentence) or its waiver reason. Packets never contain parents, checks, status, arm, author or item id. Packet ids
are salted hashes, and the order is shuffled with seed 20260923. Gemini 3.1 Pro audits Claude authors; Opus 5.5
audits Gemini. A packet passes iff every formalised unit is `faithful` and every waiver is `acceptable`. A missing,
unparseable or `unclear` verdict fails the packet. The human spot-check list (`audit-spotcheck.jsonl`) contains
every unit of every tool-successful session plus 2 seeded random units from each other packet.

- **Primary (orchestrator):** certified and faithful = tool success AND audit pass. Reported overall and on
  benign items.
- **Headline:** certified but unfaithful = tool success AND NOT audit pass.
- **Faithful-complete (decision endpoint).** Shift and smuggle items are flawed by construction: a faithful graph
  cannot certify the flawed step without an unanchored bridge, which fails tool success. The primary endpoint
  therefore has a ceiling of 4/12. Faithful-complete counts benign items as certified and faithful. It counts
  flawed items as follows: audit pass, the author finished with verdict `gap`, every unproved step is named in
  `gap_steps`, a step states the frozen target, nothing is uncovered, and there is no load-bearing unanchored
  assumption and no renamed conclusion.
- **Alarms:** tool success on a flawed item. Each case is examined; it means either an audit miss or a hidden bridge.
- **Secondary (exploratory):** gap localisation against the P5 `acceptable_locations`; spend; turns; tool calls;
  protocol errors; node provenance (hand-written, proposer-verbatim, proposer-edited); Haiku+tool vs Opus+tool as
  the "the proposer does the work" check.

**Decision threshold:** proceed to a cost-charged P5 VE-arm DEV run with the tool iff, for at least one author, A3 or
A4 reaches faithful-complete >= 6/12 on the HELD-OUT items. Otherwise report infeasibility at this budget.

## Procedure

1. Smoke (done 2026-09-22, see README): one DEV item, A3, Opus, at most 30 tool calls. The session was tool-certified but the audit found it unfaithful (a collapsed chain), so prompts v2 were adopted before tuning.
2. DEV tuning pass: all authors x A2/A3/A4 x 12 DEV items, then audit and report. Prompt, budget and limit changes
   are allowed. Each change bumps `PROMPT_VERSION` and is recorded in README "Tuning log".
3. Freeze: set line 1 FROZEN, run `hashes --write`, commit, run `ots stamp`.
4. HELD-OUT: the same commands with `--split heldout`, then audit-export, audit-run, report. No changes after the
   freeze. An infrastructure-aborted session is rerun with the same command: completed calls replay from the ledgers
   at no cost. Aborts are reported.
