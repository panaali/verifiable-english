# Sol vs Claude builders, 12 merges each (row sol-vs-claude-12; DRI adv0847 item 4, ADV-4, lever I4)

**Verdict: WORSE on the rule fixed in advance (first-review FIX 8/12 vs 4/12; fix rounds 1.00 vs 0.50 per merge; the gap is 4 items, more than 1). It is not a Sol result: item size alone explains the whole gap, and the first reviewer differs by arm. Sol is not shown NO WORSE, so the default stays: SOL_BUILDER_CAP "concurrent: 3" is untouched. Cost check: ~1.8 Sol builder sessions per Codex point were measured, not ~8.**

## Method (read-only; evidence in reviews/sol-vs-claude-20261103-evidence/: items.json, cw.json, scripts)
- Merges: `git log --first-parent main --merges` (verifiable-english main f1c306460). The builder comes only from `<item>-build.log`. If the first line is `[run-codex …] Opus` or a fallback line, the builder is Claude. A Codex log (`model: gpt-6-sol`, with no such line) means Sol. When no -build.log exists (only -build.err/.final.md), the build ran on the direct `claude --model opus` path (infra-item.sh:30), so it counts as Claude. No item's -build-ready/-fast1 builder switched family.
- Sol arm: the logs show 21 Sol-built merges (Oct 29 04:50Z to Oct 30 11:40Z) and none after that (Codex week 90%, SOL_BUILDER_CAP). I used the 12 newest.
- Claude arm: the 12 newest Claude-built merges inside the Sol arm's span (first Sol-arm build start Oct 28 22:56Z to last Sol-arm merge Oct 30 11:40Z). 15 Claude merges fall in that span; 8 were built direct and 4 through run-codex Opus.
- First review: the first `review-overlap-end` note in stage-events.jsonl, with `review-fix-early` counted as FIX. Fix rounds: the highest `fix-start round n` before the merge.

## Items (first review / fix rounds / code lines .lean+.py+.rs / first reviewer)
Sol: scale-lean-memo FIX/1/505/sol6.1, df-1bbb FIX/1/265/sol6.1, usecase-safetyfw-b FIX/2/2456/sol6.1, rd9-docroute FIX/2/615/sol6.1,
  sc-5rc FIX/1/470/astra, eff-codemap MERGE/0/305/astra, scale-admission-profile FIX/2/334/sol6.1, sc-2 MERGE/0/115/sol6.1,
  df-e1r MERGE/0/120/astra, usecase-rsp-run FIX/2/1187/sol6.1, en-sw FIX/1/307/opus, sc-3ac MERGE/0/595/astra
Claude: me-6cc MERGE/0/45/opus, gen-inv-design-c MERGE/0/42/opus, me-12ac MERGE/0/252/opus, fp-fresh-seen MERGE/0/0/opus,
  fp-fulltext MERGE/0/0/opus, sc-1af MERGE/0/248/opus, jt-e1r FIX/1/689/sol6.1, gate-shard-order MERGE/0/202/opus,
  sc-1aeb MERGE/0/142/opus, sc-1ae FIX/2/1024/opus, et-4 FIX/1/810/opus, me-4 FIX/2/617/sol6.1

| arm | first-review FIX | fix rounds/merge | Claude CW/merge (measured) | Codex input tokens/merge | ≈ Codex week points/merge |
|---|---|---|---|---|---|
| Sol | 8/12 (67%) | 12/12 = 1.00 | mean 0.59M, median 0.28M | mean 149M, median 121M | 2.6 |
| Claude (Opus) | 4/12 (33%) | 6/12 = 0.50 | mean 1.28M, median 0.84M | mean 17M, median 0 | 0.28 |

- Claude CW is measured per item: token-ledger.py `scan()` at plan weights, counting only sessions attributed to the item. Shared work is not allocated. I imported `scan()` directly so the run would not trigger the ledger's `trial-guards --apply` side effect. For Sol items, the CW is the Opus fix rounds and rechecks; 3 items used 0 CW.
- Codex input tokens: Codex rollouts (`~/.agent-accounts/codex/sessions`), matched by worktree or review-checkout cwd, cached input included. The Claude arm's Codex tokens are fix rounds and reviews that ran on Sol.

## How alike the arms are (a difference the mix explains is not a Sol result)
- Size: median code lines are 402 for Sol and 225 for Claude. 8 Sol items and 4 Claude items are above the pooled median (305). 3 Claude items are docs-only pilots or designs (fp-fresh-seen, fp-fulltext, gen-inv-design-c); the Sol arm has none.
- Kind: Lean-dominant 5 Sol vs 7 Claude; Python-dominant 7 Sol vs 2 Claude. Totals: .lean 1601 vs 2557 lines, .py (tests included) 4974 vs 1514, .rs 699 vs 0.
- By size: large items are Sol 7/8 FIX at 1.38 rounds vs Claude 4/4 at 1.50. Small items are Sol 1/4 at 0.25 vs Claude 0/8 at 0.
  - Claude's per-size rates applied to the Sol arm's mix give exactly 8/12 FIX and 1.00 rounds, which matches Sol's actual numbers.
  - Sol's rates applied to Claude's mix give 5.5/12 and 0.63, a gap of 1.5 items, which 12 items cannot resolve.
  - The cut was chosen after looking (pooled median).
- First reviewer: the Sol arm had 7 Sol-6.1, 4 Astra and 1 Opus first reviews; the Claude arm had 10 Opus and 2 Sol-6.1. Across both arms, the FIX rate by reviewer is Sol-6.1 8/9, Astra 1/4, Opus 3/11. Reviewer, period and size all move with the arm, so builder quality cannot be separated from them here.
- Sensitivity: taking only the 9 Claude merges between the first and last Sol-arm merges gives FIX 1/9 and 0.11 rounds. The raw rule result is still WORSE.

## Cost column (decides nothing; checks I4's "~8 Sol builder sessions per Codex point")
- The Codex weekly meter went from 0% to 90% between Oct 28 08:32Z and Oct 30 04:38Z. I regressed the hourly meter rise on hourly input tokens per model (41 bins). The fit gives gpt-6-sol 0.0162 pt/M (~62M tokens per point; lp0800's ~56M holds), gpt-6.1-sol 0.0184 pt/M and Astra 0.43 pt/M (~2.4M per point).
- Sol-arm builder sessions have a median of 34M input tokens, which is ~0.55 points per session, i.e. **~1.8 Sol builder sessions per Codex point** (all 121 gpt-6-sol sessions: 2.8). Even if Sol took all 89 points, it would be 0.9 per point. The ~8 figure came from a 6.4M session; the measured median is 9.5M across all Sol sessions and 34M across builder sessions.
- Per Sol merge: ~2.6 points, including its Codex reviews. So 60 points buys roughly 23 Sol merges, not ~120 builds. The Claude CW saved is 1.28M - 0.59M ≈ 0.7M per merge, or about 0.3M CW per Codex point. That is below the 1.5-7M CW per point lp0800 gives for overlap reviews, and it is mix-confounded like everything above.

## For the DRI
- Keep the cap at 3. A fair test after the reset would build size-matched rows on both arms with the same first reviewer (Opus for both).
- Re-base I4's capacity on ~2.6 points per Sol merge.
