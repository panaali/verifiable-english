# P2 natural flaw taxonomy: report (single rater, indicative only)

Five corpora with human error annotations (flawed text mostly LLM-generated), 50 items each, seed 20260922: ProcessBench
(expert earliest wrong step), BIG-Bench Mistake logical deduction (crowd first-mistake step), MathArena USAMO+IMO 2025
(judge comments), Open Proof Corpus (feedback on 0-score proofs), LogicClimate (fallacy labels). REVEAL gated (skipped);
PRM800K downloaded, not labelled. Codes: D invalid step; P false/unjustified premise; S wrong statement (S-premise
misencoded given premise; S-goal wrong question); O other; D* annotated jump that follows from the full premise set;
N no flaw; U flaw not located (N, U excluded). One rater; about 30% of labels marked unsure.

| Corpus | n (U, N) | D | P | S | O | D + equivocation | + case/circularity/arithmetic |
|---|---|---|---|---|---|---|---|
| ProcessBench | 50 (0,0) | 38% [26-52] | 14% | 22% | 26% (arith 24%) | 38% | 62% |
| BIG-Bench Mistake | 45 (0,5) | 33% [21-48] | 0% | 42% (all S-premise) | 4% | 33% | 36% |
| MathArena proofs | 37 (13,0) | 32% [20-49] | 27% | 5% | 35% | 32% | 46% |
| Open Proof Corpus | 46 (4,0) | 26% [16-40] | 30% | 2% | 41% | 26% | 37% |
| LogicClimate | 50 (0,0) | 42% [29-56] | 30% | 6% | 22% | 46% | 46% |
| Pooled (unweighted) | 228 | 35% [29-41] | 20% | 16% | 25% | 36% | 46% |

Implications: a deduction checker alone addresses about one third of natural flaws (26-42%); with arithmetic, missing-case
and circularity checks about half; false/ungrounded premises (~20%) and wrong statements (~16%) need grounding or debate.
Equivocation is rare (2/228), so identity-bound predicates are not a headline benefit on natural data. The largest lever
is who formalises the given premises: if done independently of the prover, VE also catches misencoded premises (coverage
~80% on ProcessBench, ~78% on BIG-Bench Mistake). PLAN-V3 refutation threshold (<20% D) is NOT met: D is ~35%.
