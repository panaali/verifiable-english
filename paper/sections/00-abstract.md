---
abstract: |
  AI systems now produce long formal proofs that a proof checker verifies. The checker does not verify that the
  *statement* proved is the one a supervisor meant. That step is still a person, or a weaker model, reading a formal
  statement and signing it off. Verifiable English (VE) is a small controlled language aimed at that step. A VE claim is a
  closed formula of many-sorted, function-free first-order logic with equality. It has one canonical text, a
  content-addressed identity, and five deterministic renderings, from symbolic logic to contracted controlled English, all
  produced from the same syntax tree together with one shared vocabulary legend. A checker evaluates claims in finite
  models, validates countermodels, replays data-only tableau certificates, and composes certified deductions while keeping
  every undischarged assumption visible. A Lean 4 development proves, for a reference implementation, that finite
  evaluation equals Tarski denotation, that accepted countermodels refute entailment, that canonical printing and parsing
  round-trip, and that an accepted certificate implies entailment over all admissible structures. The Python and Rust
  implementations are tested against the Lean executable; they are not verified. A coverage audit by two raters from
  different model families finds that v0 fits most sampled items from two logic benchmarks (strict fit 73% and 87%) and
  almost none from two policy sets (0% and 3%), and ranks the missing constructs.
  <!-- src: codex/e0-rater@46be9e1:experiments/E0/SECOND_RATER.md, table "Coverage estimates" -->
  We preregister four experiments on whether a deterministic rendering helps a weak model judge to reject adversarially
  weakened specifications, and whether a "proof checked" label makes grounding errors easier to miss. A development pilot
  shows that small hosted models are at floor on the task in raw logic and that open-weight models up to 3B parameters
  approve nearly everything, so the scored runs need judges chosen from a measured capability ladder.
  <!-- src: claude/open-judges@fcd378c:experiments/judges/LADDER.md; claude/e1@db51da3:experiments/E1/PILOT-dev.md -->
  **Results: [RESULT-ABSTRACT: scored experiments not yet run; this sentence will state the primary contrasts of E1
  and E5 with intervals, including null or negative outcomes].**
  No human took part as a subject, rater or reviewer. All code, proofs, experiments and text were produced by two AI
  workers from different model families under an AI orchestrator, with cross-family review before every merge. We report
  what that process caught and what it cannot catch.
---

<!-- Conventions for auditors.
  * Every number in this paper is followed by an HTML comment `src:` naming the committed file (and branch or commit
    where the file is not on ve-integration) or, in a few marked cases, the orchestrator's run log outside the repository.
  * A missing experimental result is written as [RESULT-<ID>: not yet run]. `make placeholders` lists them all.
  * Body text is ASCII so that the LaTeX build has no missing glyphs; build.py enforces this.
-->

