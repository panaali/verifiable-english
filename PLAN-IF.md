> SUPERSEDED on 2026-09-22 by ROADMAP.md (stopped; see section 6) - kept for history; do not edit.

# Independent-formaliser pilot (2026-09-22), for review

Motivation: P2 (experiments/P2-flaw-taxonomy/report.md, single rater) found ~35% of natural flaws are invalid steps, and
that misencoded GIVEN premises (S-premise) are a large share on puzzle/maths corpora (42% on BIG-Bench Mistake). If the
premises are formalised by a party INDEPENDENT of the prover, VE's checker also catches misencodings: estimated coverage
~80% on ProcessBench, ~78% on BIG-Bench Mistake.

Design: take real flawed chains from BIG-Bench Mistake (logical deduction subset; VE-expressible after an order-free
filter, or with order@0 only if its Python stage is ready - else restrict) and a VE-expressible subset of ProcessBench-like
logic items (no arithmetic), plus matched correct chains. Roles: prover = the original chain (human/LLM-written, fixed);
formaliser F = a model that sees ONLY the problem statement (not the chain) and writes the premises in VE; chain
formaliser C = a model that formalises the chain's steps; checker verifies each step against F's premises. Arms at matched
tokens: (a) frontier judge reads the chain and flags the first wrong step (published protocol of BIG-Bench Mistake);
(b) C formalises premises+steps together (prover-side formalisation, no independence); (c) F independent + C steps +
checker; (d) judge with code (writes its own solver). Metric: first-mistake localisation accuracy (BIG-Bench Mistake's
published metric) and false alarms on correct chains, per flaw class (D vs S-premise vs other). Judges/formalisers: Opus
5.5 and Haiku 4.5 via CLI (one account). Anchor: BIG-Bench Mistake published mistake-finding accuracies. Success: (c)
beats (a), (b) and (d) on S-premise + D flaws without more false alarms. Risks: F's own misformalisation (measure vs gold);
contamination (public set) - add freshly generated chains of the same type.

## After review (2026-09-22): both reviewers "do not run as designed"

Common ground: BBM logical deduction is all ORDERING puzzles with a unique solution, so (i) an order-free filter leaves
zero items and VE needs order@0's Python stage (not built); (ii) "entailed by correct premises" = "true in the solution",
so the checker reduces to answer-key comparison and a 20-line solver (arm d) does the same; (iii) the ~80% is an
optimistic category tally (BBM ceiling ~70% vs published gold, ProcessBench has no logic items); (iv) independence is not
the lever - exposure to the chain is. Decision: run ONLY the day-1 headroom check (no VE): published BBM prompts
(direct-trace, direct-step, CoT-step) on Opus 5.5 and Haiku 4.5; (d) model writes its own solver; gold-answer oracle;
ablation judge + independently re-read premises in English; 100 flawed + 100 correct traces across 3/5/7 objects; BBM
metrics. If (d) ~ oracle, formalise-then-check has no headroom beyond a solver on BBM and VE's specific value must be
sought elsewhere (T1-style oversight of untrusted work, real artefacts). Queued after P3 on the saeedi.danial account.
