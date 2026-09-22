# Statement-faithfulness pilot (2026-09-22), for review

Evidence (~/code/manage-agents/reviews/lit-proof-grading.md): with Lean + Comparator, proof validity is mechanical; the
remaining frontier gap is whether a FORMAL STATEMENT faithfully captures the informal problem. A 2026 audit of ~10k Lean
statements (arXiv 2606.29493) reports LLM auditors with F1 0.15-0.18 on formalisation errors (missing hypotheses, N vs Z,
truncated subtraction, division by zero); miniF2F-v2 finds mismatches in more than half of miniF2F.

Question: does VE's protocol move - challenge a claim with a concrete DISTINGUISHING EXAMPLE (the analogue of VE's
countermodel/`find_distinguishing_model`) - raise frontier detection of unfaithful formal statements?

Items: faithful vs unfaithful (informal problem, Lean statement) pairs from the audit's released data if public, else
miniF2F-v2's corrected pairs, plus seeded unfaithful variants (hypothesis dropped, N vs Z, truncated subtraction, off-by-
one bound, quantifier swap), balanced, 60-100 pairs, recent problems where possible. Arms (Opus 5.5 and Haiku 4.5 judges,
CLI, one account): (a) judge reads problem + Lean statement; (b) + judge may write and run small Lean `#eval`/`decide`
checks itself (tool); (c) + a trusted harness tool that searches small instances (bounded enumeration over the statement's
free variables via Lean evaluation) and reports any instance where the formal statement's truth value differs from a
reference predicate computed from the informal problem by an INDEPENDENT formaliser model (distinguishing example); (d)
(c) without the independent formaliser (harness only reports small instances where the statement is true/false, no
reference). Metrics: detection F1/false alarms vs the published 0.15-0.18 anchor; cost. Requires a separate Lean+Mathlib
project (not the repo's trusted Lean). VE-language contribution is NOT claimed; this tests the protocol idea.
