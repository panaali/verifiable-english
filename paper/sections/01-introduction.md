# Introduction

## The statement-reading gap

Scalable oversight asks how a limited supervisor can check the work of a more capable agent. Formal proof is one
answer for the part of the work that can be stated formally. The agent supplies a proof, a small trusted checker
verifies it, and the supervisor does not read the proof. The cost of review then depends on the statement, not on the
length of the proof or on the capability of the agent that found it.

Recent reports suggest this is no longer hypothetical. Vendors report AI systems that formalized Fermat's Last Theorem
in Lean and that produced Lean-checked solutions to long-open problems.[^brief] In these reports the proof is
machine-checked. What remains for people is to confirm that the formal statement says what is claimed. The report on
the Fermat formalization, for example, describes a separate comparison of the proved statement with the statement in
Lean's mathematical library. Lean's own guidance on validating proofs lists a misleading presentation of the theorem
statement among the things a checked proof does not rule out (Lean reference manual, "Validating a Lean proof").

[^brief]: These reports are vendor announcements and press summaries collected by the orchestrator of this project
(file `model-capability-brief.md`, kept outside the repository). We did not verify them and we use them only as
motivation. URLs are in the references under "Motivating reports".

We call this the *statement-reading gap*: proofs are checked by machines, statements are signed off by supervisors.
An agent that is rewarded for an approved proof has a reason to weaken the statement in a way that still looks right:
swap two quantifiers, drop a conjunct, reverse the arguments of a relation, make a domain vacuous, or reuse one vague
predicate with two meanings. Work on reinforcement learning with formal verifiers has already observed policies that
weaken the specification they are asked to prove (Yan et al. 2025; Tan 2026). Explanations do not close the gap in an
oversight setting, because the natural author of the explanation is the agent being overseen.

## What VE proposes

VE separates four things that are often blurred: whether a claim holds in a supplied finite model, whether a conclusion
follows from stated premises in all structures, whether a supervisor has confirmed what a claim means, and whether the
premises are true of the world. It gives machinery for the first two, a presentation for the third, and nothing for
the fourth except keeping it visible.

The core is *sign-off on precise claims plus checked composition of those claims*. A claim has one typed syntax tree.
Every presentation of it is computed from that tree by a deterministic renderer, never written by the agent.
Deductions carry data-only certificates that a small checker replays. Composition keeps every undischarged premise in
view. A critic can object to an inference with a finite countermodel that the supervisor's tools can evaluate without
trusting the critic. Debate is the first protocol intended to use this core, but the core does not depend on debate.

This is a design argument, not a result. The checked parts would be available with any exact formal language. The
English surface matters only at sign-off and only if it helps the reader. Whether it helps is an empirical question,
and with model judges it may well not: the judges in our pilot read symbolic logic almost perfectly.

## Contributions

Each item names the artifact that a reader can check.

1. **A language with a specification and three implementations.** VE v0 is many-sorted, function-free first-order
   logic with equality, with a strict surface grammar, a canonical form and content-addressed identities
   (`docs/spec/v0-language.md`). There is a Python reference package (`ve/`), a Lean 4 reference (`lean/`) and a Rust
   core (`rust/`). An opt-in profile, `closure@0`, adds transitive and reflexive-transitive closure.
2. **Five deterministic views of one syntax tree**, from symbolic logic to contracted controlled English, each with an
   independently written inverse parser used in tests, and one vocabulary legend shown identically with every view
   (`docs/rendering-views.md`).
3. **A checker**: finite evaluation, countermodel validation, tableau certificates with a replay checker, claim graphs
   with assumption-preserving composition, and a three-valued equivalence oracle used to validate attack items
   (`docs/implementation.md`, `docs/oracle.md`).
4. **Machine-checked assurance with a stated boundary.** A Lean development with 141 audited named theorems and no
   `sorry` proves evaluator correctness, countermodel soundness, print/parse round trip and certificate-checker
   soundness for the Lean reference (`lean/README.md`, `lean/METATHEORY.md`, `lean/CLOSURE.md`). We state what is not
   proved.
   <!-- src: docs/closure-merge-report.md line "33 source files, 141 named theorems"; lean/axioms.txt has 141 entries -->
5. **A coverage audit (E0)** of 210 items from seven public datasets by two raters from different model families, with
   agreement statistics and a ranked list of missing constructs.
   <!-- src: codex/e0-rater@46be9e1:experiments/E0/SECOND_RATER.md -->
6. **Preregistered designs for four experiments (E1, E1b, E5, E2/E4) and a training study (Phase T)**, with a measured
   capability gate. The pilot finding that commonly used "weak" judges are not weak on this task is reported as a
   finding. **Scored results: [RESULT-CONTRIB: not yet run].**
7. **A disclosed production process.** The work was produced without human participants by AI workers from two model
   families with cross-family review. Section 10 lists concrete defects that the reviews found.
