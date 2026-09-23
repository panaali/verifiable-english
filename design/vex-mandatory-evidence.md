# VEX: mandatory evidence against obfuscation (2026-09-22)

Status: idea from the project lead, analysed; not a plan (needs the usual two frontier reviews before any build).
Builds on `design/positioning-vs-debate-theory.md` correction 2 and `~/code/manage-agents/reviews/obfuscation-recheck.md`.

## Idea

Mandatory proof removes obfuscation for claims with affordable formal proofs but leaves heuristic, statistical and
approximate claims as unproved leaves, where obfuscation returns. Extend VE (VEX) so those claims are also checkable
objects, and require every accepted claim to be either proved from reviewed foundations or supported by checkable
evidence with propagated uncertainty.

- Statistical claims carry data + the test; the checker recomputes data -> result. Residual: data provenance and the
  test's stated assumptions.
- Physical approximations become theorems with explicit error bounds ("under model M the answer is within eps"),
  via validated numerics. Residual: applicability of M (an accepted law or stated checkable condition).
- Heuristic arguments become explicit defeasible estimates (cf. ARC, "Formalizing the presumption of independence",
  Christiano, Neyman, Xu 2022).

## Consequence: deception becomes abstention

A Barnes-Christiano argument chains many 96-99%-plausible leaves. In VEX each leaf carries evidence and a probability
that the checker propagates (worst-case Frechet bounds unless independence is itself supported), so the certified
confidence of a long merely-plausible chain collapses. What is propagated is a *lower* bound on each claim; leaves never
give an upper bound, and evidence within a leaf combines multiplicatively only under a supported conditional-independence
claim (`design/evidence-layer-design.md` §§2.2-2.4, 2.9). Hence the dishonest claim comes out "not established" instead of
fooling the judge. Sound but incomplete: a true claim with equally long, uncertain support is also unestablished.
Acceptable for control (refuse uncertified actions), costly for open science.

## Where obfuscation can still enter

1. Cherry-picked considerations (heuristic estimates depend on what is included). Counter: robustness to added
   considerations; the opponent may add considerations and the certified estimate must survive them (ARC's core open
   problem; PE's stability condition).
2. Hidden dependence assumptions. Counter: independence is a stated claim with its own support; default to worst-case
   bounds.
3. False accepted foundations (laws, trusted data, model applicability): irreducible but explicit, shared, auditable.
4. Unfaithful formalisation of a test or model: author approval plus translator/sample audits.
5. Cost as an attack (flooding with expensive-to-certify claims): charge certification cost to the claimant.

## Test

Barnes-Christiano-style arguments (long chains of plausible leaves, one false, including statistical/approximate
leaves). Arms: judge alone; debate; VEX with mandatory evidence and propagated bounds. Metrics: false certifications
(predicted near zero for VEX) and honest claims left unestablished (the completeness cost).
