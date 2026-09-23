Status: DRAFT v4 (post-dev-tune-2 review fixes, prompts v4, scoring v2; the manifest stamped on 2026-09-22 records the pre-tuning state). Freeze: set this line to "Status: FROZEN <date>", run `waivers --write` and `hashes --write`, commit, OpenTimestamps-stamp PREREG-HASHES.txt, then run held-out.

# PREREG-ASSIST: budgeted evaluation of `ve assist` on P5 dossiers

Plan: [PLAN-ASSIST.md](../../PLAN-ASSIST.md). The final "After review" section is binding. Runner:
`ve_experiments/assist_eval/` (`python -m ve_experiments.assist_eval`). Hash manifest:
[PREREG-HASHES.txt](PREREG-HASHES.txt). It covers this PREREG text, the tool version, every tool and runner source
file, each author system prompt (arm x protocol), the frozen auditor prompt, the waiver allowlist W
([waivers.json](waivers.json)), both item-id lists and the registered configuration (`CONFIG` in `cli.py`: every
executable setting: budget and its scope, limits, proposer model, Claude account, Gemini cap, authors, arms, items,
auditors, success rule, endpoints and claim). The manifest's OpenTimestamps proof is `PREREG-HASHES.txt.ots`. The
held-out command refuses to run unless line 1 says FROZEN, the manifest recomputes byte for byte, `waivers.json`
equals the recomputed W, and no command-line setting (`--budget`, `--max-tool-calls`, `--proposer-model`,
`--account`, `--gemini-cap-usd`, `--items`, an unregistered author or arm) differs from CONFIG. `audit-run` on a
held-out run applies the same gate and the registered auditor account.

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
| A4 | Full tool: A3 plus the Haiku 4.5 proposer (`propose`/`accept`). Premise suggestions are off. **Exploratory**: A4 measures proposer *availability*, not efficacy (no dev session used the proposer); it is reported as "proposer offered, uptake n". |

Authors: **Opus 5.5** (primary; effort medium, the audited claude CLI on the main account, i.e. the default Claude
configuration directory, with `CLAUDE_CODE_NO_MODEL_FALLBACK=1`) and **Gemini 3.1 Pro** (secondary; Vertex through
`ve_experiments.paid`, native function calling, thinking LOW). Haiku 4.5 was an author in dev-tune-2 only and is
dropped (disclosed dev selection: 1/36 dev sessions faithful-complete). The proposer (Haiku 4.5, main account) was
restored after the saeedi.danial token was revoked and smoke-tested on DEV on 2026-09-23 with one call
(`runs/proposer-smoke-2026-09-23/`: one valid candidate, $0.0051 at list price).

**Claude tool-call protocol.** The controlled claude CLI endpoint runs with tools disabled and is single-turn. Each
author turn is therefore one fresh CLI call. The system prompt holds the task, the VE guide and the tool list as
JSON schemas. The user message holds the item materials and every earlier turn: the author's reply and the harness
response. The author acts by ending its reply with one fenced JSON block, `{"calls": [{"tool", "arguments"}]}`,
holding 1 to 10 calls that run in order. A reply without a valid block is a protocol error: it is charged, reported
back, and the loop continues. Gemini uses native function calls with the same tool schemas and the same 10-calls-per-turn
cap. Both get the same `[budget]` line after every turn.

## Budget (matched TOTAL per item, identical across arms and authors)

- A hard cap of **$2.00 per item** on author plus proposer spend over **every attempt** at the item, costed at
  list price. A session restarted after an infrastructure abort starts with the aborted attempts' spend charged
  (`prior_attempts_spent_usd`); an exhausted budget stops the item and is never reset. Charged too: the tokens of
  earlier attempts of a Claude call (infrastructure retries), the tokens of a Claude call that failed, and the
  paid ledger's unknown-billing hold for a Gemini 5xx/timeout (fail closed). Reports show spend over all attempts,
  and for Gemini reconcile it with the run's paid ledger (billed plus holds). Claude uses Anthropic API list
  price with the CLI cache breakdown: Opus 5.5 $4 in / $20 out / $5 cache write / $0.20 cache read; Haiku 4.5
  $1 / $5 / $1.25 / $0.10. Haiku subscription calls are costed at API list price (orchestrator decision c). Gemini
  3.1 Pro costs $2 in / $12 out, with thoughts billed as output and cached input at the full rate
  (`ve_experiments.paid`).
- Before every author call the harness computes that call's worst case: all input uncached, 16,000 output tokens
  including thinking. It stops if the spent amount plus this ceiling would exceed the cap. Proposer calls are gated
  the same way. Spend therefore never exceeds the cap.
- Secondary limits: 60 turns, 250 tool calls, 10 calls per turn, and 8,000 characters per tool result (larger
  results are truncated and flagged). Gemini input is capped at 190k tokens, below the long-context price tier.
- Auditor spend is evaluation cost and is not charged to the item. The Gemini run ledger is capped at **$40** per
  run (`gemini_cap_usd`; PLAN-FRONTIER section 7).

## Endpoints

Per session the tool's `status` reports **tool success**: every target is certified by graph replay, every step is
certified, every asserting sentence is covered or waived, no unanchored assumption is load-bearing, no declared
vocabulary carries a target, and the assumptions are consistent.

**Waiver allowlist W(item)** (`dossier.py`, preregistered and content-hashed as `waivers.json`). The tool counts any
waiver as a failure, and every P5 dossier has given sentences no VE statement can state. W is computed by a
deterministic rule from the public dossier text only (no labels): sentences that only list declared rules
(`declared`), "... remain unassumed" metadata (`unassumed`), lot/sample statements (`lot-sample`); facts that no live
rule, relied-on rule or claimed sentence uses (`unused-fact`); and rules whose antecedents cannot be derived from
the given facts (`dead-rule`) **only if** no claimed sentence relies on them (mentions, sense-free, one of the
underivable antecedents together with the consequent, including "would imply ..., respectively" pairs and "the
immediately preceding X result"); a relied-on dead rule must be formalised. The first three kinds are
**waive-only**. On the 12 dev items W has the same code profile on benign and flawed items. Authors see the rule in
words, not the list (W marks underivable rules, which could hint at a flaw); a waiver outside W is reported to the
author only once it is the sole remaining obstacle.

**Evaluation tool success** (`scoring.eval_success`) = status success, or the waiver line is its only failure with
every waived sentence in W, AND no dossier graph violation:
- no node is anchored to a waive-only sentence;
- **anchor content**: an assumption whose anchors are all given must be entailed by the reference formalisation of
  those sentences (the template reading of the given text). Citing a sentence is not enough: the Opus-review smuggle
  (a lot/sample bridge anchored to "The sample from lot unit0 is unit2.") fails twice (waive-only anchor; content);
- "remain unassumed" keeps its restriction: no assumption node may entail a listed check (decided "no" required);
- and the ledger verifies.

**Fidelity audit.** A separate step, blind to proof status, by a model from a different family. `audit-export`
writes one packet per session: the sentences, the dossier glossary (author-declared predicates listed apart and
marked "AUTHOR-WRITTEN"), and one unit per asserting sentence: `formalised` (deterministic paraphrases of its
anchored nodes, the frozen conclusion for the target sentence, and the sentence ids of each step's parents as
"reasons", so dependency alignment is audited without certification status), `waiver` (the W code and its fixed
description; never the author's free-text reason) or `omitted` (with its W code, if any). Packets never contain
check results, status, arm, author or item id; packet ids are salted hashes, order shuffled with seed 20260923.
**GPT-6 Astra** (`codex exec`, read-only, reasoning high) audits every packet; **Opus 5.5** (main account)
additionally audits every Gemini-authored packet, and such a packet passes only if both pass (disagreements are
reported). The auditor prompt is frozen in the manifest. An auditor passes a packet iff every formalised unit is
`faithful` and every waiver/omitted unit `acceptable`; a waiver or omission outside W fails deterministically; a
missing, unparseable or `unclear` verdict fails; a packet with nothing formalised or waived fails without a call.
Calibration: the human spot-check list (`audit-spotcheck.jsonl`: every unit of every tool-successful session plus
2 seeded random units per other packet) is adjudicated by the lead before the report is final; auditor
disagreements on Gemini packets are listed.

- **Certified and faithful** = evaluation tool success AND audit pass. Reported overall and on benign items.
- **Headline:** certified but unfaithful = tool success AND NOT audit pass.
- **Faithful-complete.** Benign items: certified and faithful. Flawed (shift, smuggle) items, ALL of: audit pass;
  finished with verdict `gap` naming at least one gap step; **every claimed sentence has an anchored step**; every
  step not named as a gap is certified; every gap step was checked and refuted by a **checker countermodel**
  (unchecked or unknown steps never count as gaps) and its statement is not entailed by the whole dossier (every
  given sentence's reference formalisation; so a missing premise cannot manufacture a gap); a step states the
  frozen target; no uncovered given sentence, no waived claimed sentence, no load-bearing unanchored assumption, no
  renamed conclusion, no dossier graph violation; **verified ledger**; and **`gap_located`**: the claimed paragraphs
  of the gap steps equal one of the item's P5 `acceptable_locations`. When the root paragraph is an acceptable
  location, "freeze the target, add one step that states it, finish gap" still fails: every other claimed
  sentence needs its own step and every non-gap step must be certified (regression test
  `test_opus_a1_construction_state_target_and_finish_gap_cannot_score`).
- **Alarms:** tool success on a flawed item. Each case is examined.

**Primary endpoint.** Opus 5.5 **A3 vs A2** faithful-complete, paired by held-out item at the same $2 total
budget; reported as the 2x2 paired table with an exact two-sided sign test on the discordant pairs. (Power note:
with 12 pairs, p < 0.05 needs at least 6 discordant pairs, all in one direction; dev-tune-2 had 3.)

**Secondary / exploratory.** Gemini 3.1 Pro (secondary author) on the same endpoints; A4 for both authors
(exploratory; "proposer offered, uptake n": sessions with a successful `propose`, and accepted candidates); gap
localisation; spend over all attempts; turns; tool calls; protocol errors; node provenance.

**Claim scope (replaces the ">= 6/12" threshold).** Twelve items support narrow feasibility only: 12/12 gives an
exact one-sided 95% lower bound of 77.9% (4/4 benign: 47.3%), so no result here shows claim B's 80% fidelity gate
or a 10-point non-inferiority margin. The minimum claim, reported whatever the outcome: "Opus 5.5 with checker
feedback at <= $2/item on 12 held-out same-generator P5 items: k/12 faithful-complete (exact one-sided 95% lower
bound), alarms a/8 (exact upper bound; 0/8 gives 31.2%). The proposer is untested (A4 is availability only) and the
80% gate is not shown." Superiority of A3 over A2 is claimed only if the primary sign test is significant;
transfer to T1e needs separate evidence. The next step (a cost-charged P5 VE-arm DEV run with the tool) is decided
by the lead from this report, not by a count threshold.

## Procedure

1. Smoke (done 2026-09-22, see README): one DEV item, A3, Opus, at most 30 tool calls. The session was tool-certified but the audit found it unfaithful (a collapsed chain), so prompts v2 were adopted before tuning.
2. DEV tuning pass (dev-tune-2, done 2026-09-23): authors x A2/A3/A4 x 12 DEV items, audit and report; two xhigh
   reviews (Astra, Opus) then required the scoring, audit, freeze and accounting fixes above (prompts v4, scoring
   v2). dev-tune-2 was replayed under the new scoring at $0 (`runs/dev-tune-2/replay-v4/`; the audit component is a
   legacy single-auditor proxy, see README). Each change bumps `PROMPT_VERSION` and is recorded in README "Tuning
   log".
3. Freeze: set line 1 FROZEN, run `waivers --write` and `hashes --write`, commit, run `ots stamp`.
4. HELD-OUT: `run --split heldout` with no setting flags (one author x arm per command is allowed), then
   audit-export, audit-run, report. No changes after the freeze. An infrastructure-aborted session is rerun with the
   same command; its earlier attempts stay charged to the item. Aborts are reported.
