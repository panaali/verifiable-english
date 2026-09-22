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

## After review (2026-09-22): both reviewers "revise; narrow feasibility pilot only"

Corrections: the 0.15-0.18 F1 is ONLY the "Formalization Error" category on 92 curated problems (overall 0.37-0.42);
not comparable to a balanced binary task; the real gap is false alarms (recall already ~0.85). A distinguishing example
shows two formalisations differ, not which is right; seeded executable mutations make arm (c) win by construction.
Evaluation is limited to N/Z/finite statements (R and unbounded quantifiers are not decidable).
Adopted minimum pilot: (1) ~30 miniF2F-v2 pairs where v2 changed the statement (original = unfaithful, corrected =
faithful), labels human/independently checked; (2) measure WITNESS YIELD: fraction of unfaithful statements for which
Mathlib `plausible`/`decide` finds a small-instance witness; STOP if < 30%; (3) only if >= 30%: Opus judge, arms
(a) baseline vs (d) witness evidence, then reference-only vs reference+search at matched budget; report TPR/FPR with Wilson
intervals, natural errors as the headline. Separate Lean+Mathlib project pinned to miniF2F-v2's toolchain.
