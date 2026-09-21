# Post-v0 supplied run log

- 05:31 PAPER DRAFT v0 exists: Codex drafted all non-result sections (paper/, 21 pages, 8.7k words; `make html pdf` works;
  PDF at ~/code/ve-claude-paper/paper/build/paper.pdf; merged into ve-integration). I read the abstract: conservative and
  accurate. Placeholders: RESULT-ABSTRACT, -CONTRIBUTIONS, -E1-FREEZE, -E1, -E1B, -E5-FREEZE, -E5, -E2, -E4, -T-GATE,
  -T-TRAINING. TODO: update Assurance for closure-cert (200 theorems, Lean-checked closure certificates); Claude claim audit
  once results exist. Codex E5 export running (log codex-e5-export); I submit the dev job to Colab when ready.
- 07:00 WORKER C2 REPORT (claude/e1 @ fea1b55): Colab backend, scored materials (874 candidates: 280 good, 594 oracle-VALID bad;
  explanations all by astra, 59.9 vs 59.5 words), dev run of all 10 cells. FINDING: with the final prompt (4,000-char JSON
  legend) NO judge passes the gate: fol_symbols|none FA 7B .96, 14B .77, 32B .15 (earlier ladder used an older prompt with a
  plain vocab listing: 7B .57, 14B .39). Diagnostic with plain listing: 7B .75, 14B .46. Dev signal (not a result): 14B
  ve_strict vs fol_symbols FA .59 vs .77 (no explanation), .78 vs .86 (attacker explanation), contrast -0.08 [-0.17,+0.02].
  E1b comprehension fol/ve_strict: 7B .59/.55, 14B .66/.67, 32B .78/.85. DECISION: compact legend (codex/legend-compact,
  log codex-legend), keep band [0.30,0.60] for primary, (0.60,0.85] permissive-secondary, [0.10,0.30) near-floor-secondary.
  C2 ignored my queued SendMessage as possible injection (it arrived inside tool output): re-sent as task message; C2 resumed
  to do the 6 Codex review items + rerun dev with compact legend + final PREREG, then STOP for Codex PREREG review.
  Scored run plan: A100, <= 25 units, 32B last. E4/E5 dev jobs queued on the L4.
- 07:14 MERGED codex/legend-compact (773 tests; tag ve-green-0725); told C2 (expects the notice). My Colab dev jobs e4-dev-a and
  e5-dev-medium-neutral-a/b FAILED (missing ninja after runtime restart; 30 E5 prompts > 8k context): resubmitted as
  e4-dev-c and e5-dev-medium-neutral-c with ninja install + max_model_len 10240. Score with
  ~/code/ve-codex/experiments/E5/colab/score.py and experiments/E2E4/colab/ (labels are in the parent of each gpu/ dir).
  LESSON: when grepping remote logs, filter tightly (one log dump cost a lot of context).
- 07:34 E4 DEV (Qwen 7B/14B, 16 items per cell, sanity only): checked countermodel 0/8 FA and 8/8 HA for both; dishonest critic:
  7B HA 3/8, 14B 7/8; prose critique: 14B HA 4/8. Table: colab/results/e4-dev-c/out/score-table.md (DON'T cat it: huge; read
  score-summary.json selectively). E2 dev submitted (e2-dev-c, 24k ctx). E5 dev queued (e5-dev-medium-neutral-c).
  CONTEXT HYGIENE: never print unknown JSON/markdown tables; use `python -c` to pull specific fields or `head -c`.
- 08:05 QUOTAS (user-reported): Claude session 31% used (resets 09:49), Claude week 31%, **Fable week 54% used**; **Codex week
  52% used** (resets Sep 26 21:34). RATIONING: Claude subagents on opus/sonnet (Agent tool `model` param), Fable only for
  orchestrator + final judgement; Codex default effort now `high` (run-codex.sh arg 4; `medium` or a cheaper model via arg 5
  for mechanical tasks; `xhigh` only for Lean proofs / science reviews). SCOPE FREEZE: finish E1, E5, E4/E2 scored runs +
  paper with results + claim audit; then Phase T gate on Colab. DEFERRED until the user says otherwise: order@0 profile,
  Phase U use-case corpus, further Lean/Rust extensions (all in FUTURE.md).
- 08:34 C2 REPORT 2 (claude/e1 @ 9cdbc7a): all 6 Codex review items done (judge isolation flags `--safe-mode --setting-sources ""
  --disable-slash-commands`; E1b via runner; FROZEN gate; cluster-t primary; balance gate). Balance gate FAILED on free-form
  explanations (SMD -0.22, style AUC 0.78) -> recipe e2 fixed-form + length matching passes (AUC 0.525). DEV with compact
  legend, FA (HA): fol_symbols|none 7B .855(.85) 14B .66(.90) 32B .31(.96); ve_strict|none .91/.46/.24; fol|attacker
  .82/.33/.05; ve_strict|attacker .82/.36/.10. ROLES: 32B primary (34/110, by one candidate), 14B secondary-permissive, 7B
  not scored, luna 5/110 reference. KEY OBSERVATION: e2 explanations LOWER false approval (they honestly describe the
  formula) = not adversarial. MY DECISION: recipe e3 = ONE explanation per base item written from the requirement/faithful
  AST, asserted verbatim for every candidate (true for good, the adversary's lie for bad; zero label info by construction).
  C2 resumed: e3, dev rerun of the 5 attacker cells (14B, 32B), PREREG v4 draft, switch Colab to A100 (<= 30 units today),
  then STOP for Codex PREREG review -> freeze -> scored (14B then 32B). Design detects ~0.09 reduction at 80% power.
- 08:44 E2 DEV NOT RUN: preflight refused (72 of 432 prompts exceed 24k tokens; the largest, direct review of a 256-step
  derivation with growing workload, is ~40k tokens, above Qwen2.5's native 32k window; the checker arms at that size are
  ~25k). DECISION (time + quota): E2 is deferred and reported in the paper as 'not run', with the token counts as a
  descriptive observation; to run it later use sizes 4/32/128 or a long-context judge. E5 dev (medium, neutral) running
  on the L4. Colab still L4 (C2 has not switched to A100 yet).
- 10:57 LOST ~2h (09:15-10:56): C2 stalled waiting on the Colab queue (stream watchdog) and I was not woken. C2 resumed (its
  e1-dev-e3 job is done) to score e3 cells + PREREG v4. E5 DEV on Qwen (medium, neutral): 7B approves EVERYTHING (64/64 FA and
  HA in all 5 cells); 14B job incomplete (98/128 outputs missing per cell; worst-case scoring meaningless); 32B not run.
  DECISION: E5 scored run NOT executed (no affordable judge in the gate: haiku ~40% FA would need thousands of long Claude
  calls); paper reports E5 as materials + pilots. E2 deferred (context). Remaining: E1 scored (14B, 32B) + E4 scored (tiny)
  + paper results + claim audit. Noon target for scored results will be missed; keep going.
- 10:59 C2 REPORT 3 (claude/e1 @ a6b6503, PREREG DRAFT v4): recipe e3 done (96/96 scored base items; balance gate passes: SMD
  +0.005, AUC 0.469). DEV e3, FA none -> attacker: 32B fol_symbols .32->.10, fol_keywords .31->.13, ve_strict .24->.11,
  ve_natural .19->.08, ve_fluent .17->.12; 14B .66->.55, .60->.48, .48->.40, .53->.46, .55->.45. The asserted-faithful
  explanation LOWERS false approval in every view (judges seem to use the restated requirement as a second reference).
  Dev contrasts ve_strict - fol_symbols: attacker cells 32B +0.01 [-.14,+.16], 14B -0.14 [-.28,.00]; no-explanation 32B
  -0.08, 14B -0.18. MY DECISION (dev only, pre-freeze): two CO-PRIMARY contrasts for 32B (attacker cells; no-explanation
  cells), Bonferroni 97.5% cluster-t; C2 writing PREREG v5 + switching Colab to A100; then Codex review -> freeze -> score.
- 11:03 Codex reviewed E1 PREREG v5 (claude/e1 @ 6acdf63): FIX-THEN-FREEZE, six one-line edits (truncated/tool replies must be
  invalidated before parsing; 97.5% only for primary judge; add promised bootstrap + E1b intervals; three wording fixes).
  Text: codex-prereg-e1.final.md. Sent to C2 with authority to fix, FREEZE, export, run scored on A100 (14B then 32B),
  analyse once, write experiments/E1/RESULTS.md. NOTE: message was queued mid-run; if C2 treats it as injection again,
  re-send when it goes idle. E4 FROZEN (codex/e5 @ cbc6a80), scored job e4-scored-a submitted (360 prompts, 7B+14B);
  score with experiments/E2E4/colab/score.py against .../out/scored/E4/labels.jsonl.
- 11:13 **E1 FROZEN and SCORED RUN STARTED.** claude/e1: PREREG line 1 `Status: FROZEN 2026-09-21 (v5 with the six cross-review
  edits...)`, head 56424da. Colab runtime is now an **A100-80GB (7.5 units/h, not the 40GB at 5.4)**; job e1-scored-0921
  running (14B then 32B); e4-scored-a queued behind it. Budget watch: ~2-2.5 h = 15-19 units.

[Access-configuration tail omitted; no experimental outcomes omitted.]
