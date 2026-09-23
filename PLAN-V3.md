# VE plan v3: gated pilots (supersedes PLAN-V2.md)

PLAN-V2 was reviewed before any spend by GPT-6 Astra (xhigh) and Claude Fable 5.1 (xhigh):
`~/code/manage-agents/reviews/plan-review-astra.md`, `plan-review-fable.md`. Both said **proceed with changes, and the
changes are large**, and they agree on almost all of them. This plan adopts their common ground.

## What the reviewers changed

1. **Thesis, corrected.** Not "a verified checker has none of these failures" (true of the checker, false of the
   pipeline: an LLM still writes the formalisation, a judge still decides premises and vocabulary, claim text is an
   injection channel, and our experiments replay certificates in Python, not Lean). The defensible thesis is about
   FACTORING: an oversight decision can be split so that the trusted part is mechanical and the remaining LLM part is
   local, short-context and measurably easier, with the untrusted party paying for formalisation at a tolerable
   usefulness tax. Three things to measure: how hard the residual decision is, how large the tax is, and whether a
   "checked" label causes harm through deference.
2. **The obfuscated-arguments benchmark must not lead**, and must not be called that: its deduction cell is a
   tautology, its premise cell is set by a generator parameter (leaves per step), its formalisation cell exists only in
   the VE arm, uniform planted flaws flatter VE (an adaptive adversary never plants a deduction flaw against a checker),
   ten items per cell cannot support a slope, and prose rendered from VE makes VE's authoring cost zero by construction.
   It survives as a smaller "long-argument flaw localisation" study with the fixes below.
3. **Context-invariance as designed is a strawman** (the checker never sees the 800K tokens; whoever extracted the
   certificate did) and is unaffordable at frontier tier (about $3 per uncached 800K-token call).
4. **The evidence-layer design has errors**: P(conclusion) <= min P(leaf) is false (that bounds the conjunction, not
   its consequence); the worked example's doubt budget is inconsistent; multiplying likelihood ratios needs conditional
   independence, which different originators do not give; coherence checking that drops UNKNOWN constraints is not
   "exact". Fix the mathematics before building anything. It is also the largest build and its key quantities are LLM
   judgments, so it cannot be filed under "not a language model".
5. **Budget and effort were not realistic**: packages 1-4 summed to $340-535 against $293 available, and to about 30
   engineer-days against depleted agent quotas. Engineering, not dollars, is the scarce resource.
6. **Do not economise on scientific review**, and have a person read the primary sources behind the survey's numbers
   (they came through a summarising tool; three are flagged unverified; several papers postdate the reviewers'
   knowledge).

## Work packages (each is a pilot with a cap, a primary contrast and a refutation condition fixed in advance and
externally timestamped)

| # | Deliverable | Decisive experiment | Refuted if | Cap |
|---|---|---|---|---|
| 1 | **Deference and persuasion**, on the existing E4 harness (also closes the paper's round-2 controls) | E4 ablation with frontier and weak judges: verdict only; countermodel without verdict; authentic checker finding delivered through a trusted channel; FORGED checker line in the proposer's channel; a replay tool the judge may call; plus adversarial pushback on checker-decided vs judge-decided items. Known-answer harness tests first (an oracle judge scores 1.0, a random judge scores chance) | the forged line works as well as the authentic finding, or judges flip on checker-decided items under pushback. If a "checked" label raises false approval on bad premises, publish it as harm | $20-30 |
| 2 | **Natural flaw taxonomy** and primary-source check | In human-annotated corpora of real flawed arguments or proofs or code reviews, classify where the flaw sits: invalid step, false or unjustified premise, wrong statement. Two model families; the project lead hand-checks a sample. This is the base rate that says how much any proofs-plus-debate hybrid can buy, and it is what the prover-estimator paper asks for | fewer than about 20% of real flaws are invalid steps: then the checker buys little and we say so | $15 |
| 3 | **Formalisation tax on real artefacts** | 30-50 items in a domain the language fits (reachability, role-based access control, Alloy-style relational specs, where the closure profile does real work), VE written by a model, differential-tested against the source engine; full authoring cost against structured review | faithful formalisation below about 30%, or authoring costs more than the review it saves: the thesis is then confined to synthetic items | $25 |
| 4 | **Long-argument flaw localisation (small)** and the merged-predicate duel on one generator | N in {50, 500}; leaves K crossed with N; at least 60 paired items per cell; every arm gets the declared leaf list, the graph and the same retrieval; flaw types include a smuggled premise; arms: cross-examination with glossary, structured review without certificates, a per-edge LLM verifier at equal dollars, VE with checker; primary metric is each arm's WORST flaw type; scored certificates replayed in Lean | VE's worst-cell accuracy does not beat cross-examination's by a preregistered margin at matched dollars, or benign completion gets worse. A win on deduction flaws alone does not count | $80-100 |
| 5 | **Length and re-authoring drift**, and a **minimal evidence pilot** | the pipelines of package 4 at growing length (cheap tier, one frontier spot-check); VE vs pinned JSON when an agent re-authors requirements; tiny enumerable evidence worlds with one challenge round against equal-cost direct estimation (no general LP, no live retrieval) | the strongest baseline matches within a preregistered margin; evidence bounds are usually vacuous or no Brier/robustness gain | $50 |

Total about $190-230 of the $293 available; the rest is reserve. Everything larger waits for the grant.

## Frozen until the grant or a positive pilot

New language profiles (obligation and priority; the Python stage of numbers), the Lean proof for the English surface,
the training study, the full evidence layer, the 5,000-step sizes, the post-cutoff forecasting study. In flight and
allowed to finish because it was requested separately: the regular-English surface pass and the math mini-paper use case.

## Claims we stop making

Flat TOTAL cost in N; pipeline-wide immunity to prompt injection; that the checker "cannot be fooled" when the scored
path is Python replay; anything about human readability; any number from the survey that nobody has read in the
primary source; the name "obfuscated-arguments benchmark".

## Housekeeping the reviewers asked for

External timestamps for every preregistration (hash published somewhere dated before scoring); replay E4's scored
certificates through the Lean executable; fix the evidence-layer mathematics in `design/evidence-layer-design.md`;
"E0 by execution" is folded into package 3.

## Queue update (2026-09-22, after the obfuscation re-check, commit 627a989)
Order: (1) pushback study; (2) T1c separating certificates; (3) OBFUSCATION STUDY (new): Barnes-Christiano-style chains
of plausible leaves with one false (including statistical/approximate leaves); arms judge alone, debate, and
mandatory-proof / mandatory-evidence VE (VEX, design/vex-mandatory-evidence.md); metrics false certifications and honest
claims left unestablished; seeded with the iceberg Lean pilot and the train and wrapping-ball trees. Plan review by Astra
xhigh + Opus xhigh before any spend (Astra available after Sep 26 21:34).
