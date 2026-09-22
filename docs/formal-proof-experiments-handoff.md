# Handoff: experiments on mandatory proofs and VE review

For the coordinating agent. These suggestions supplement the existing
[work plan](plan.md) and [human-review study](research-review.md); they do not
supersede their preliminary feasibility gates.

## Claim to test

Requiring a complete, affordable proof from accepted foundations can remove the
critic's need to locate a hidden deduction error. VE's additional hypothesis is
that its presentation helps people approve the **right specification, physical
model, and assumptions**. Test these benefits separately. Neither settles the
general obfuscated-arguments problem.

## Starting evidence

We recovered and read the three original physics argument trees. The
[feasibility report](../experiments/obfuscated-arguments/README.md) records their
sources, modeling issues, and remaining work. The
[Lean probe](../experiments/obfuscated-arguments/Feasibility.lean) contains 11
checked algebraic lemmas/counterexamples; the
[verification record](../experiments/obfuscated-arguments/verification.json)
records one 3.115-second invocation. This establishes only small rational-algebra
checks, not complete physics formalizations, VE integration, or affordable
end-to-end development.

## Suggested experiments, in priority order

1. **Complete one original example and measure the actual cost.** Start with the
   iceberg problem; attempt the wrapping ball next if the first is manageable.
   Independently review the intended question, idealizations, and approximation
   tolerance before proving the result. Supply a short direct proof of the root
   claim; translating every misleading debate branch is unnecessary. Distinguish
   accepted physical laws from derived claims, and prohibit assuming disputed
   conclusions. Record model review, formalization, proof repair, checking, and
   compute separately. Deliver a checked artifact plus an assumption checklist
   and measured cost ledger. This tests affordable certification, not VE's surface.

2. **Test whether VE helps humans catch a valid proof of the wrong model.** Prepare
   matched faithful and misleading specifications: point-particle versus finite
   train, massless versus positive-mass air, exact versus approximate equality,
   and gravity-free versus gravity-including ball motion. Have experts adjudicate
   each variant. Compare VE with a structured formal interface using the same
   claims, checker, evidence, examples, and assistance. Measure wrong approvals,
   correct approvals, repairs, unresolved decisions, review time, and comprehension
   of remaining assumptions. This is the direct test of VE's additional benefit.

3. **Test mandatory proofs against adversarial debate.** On the reviewed tasks,
   compare ordinary debate with cross-examination, mandatory proofs with the
   structured interface, and mandatory proofs with VE. Include honest submissions,
   invalid deductions, and wrong-but-provable specifications. Give all conditions
   equivalent task information and clarification; charge proof generation and
   extra tools to their condition. Retain direct-checker and single-critique
   baselines where applicable. Evaluate false approvals together with successful
   completion and total cost: rejecting everything is not useful oversight.

4. **Check whether any benefit survives increased size and new tasks.** After the
   pilot, vary deduction depth while holding the assumptions fixed; separately
   increase assumption-review difficulty. Add a predefined PrOntoQA subset for
   relational deductions, then arithmetic word problems only after the required
   semantics exist. Use held-out variants and disclose exclusions. These are
   transfer tests, not evidence that a benchmark reproduces computationally
   intractable localisation.

## Coordination decisions

- Integrate with the [roadmap's matched comparisons](roadmap.md#comparison-conditions)
  rather than launching a duplicate study. Calibrate and freeze success thresholds
  before held-out evaluation; retain timeouts and unsupported cases in reporting.
- VE v0 lacks arithmetic and calculus. Scope a minimal extension or an audited
  read-only view of Lean statements; do not hide calculations in opaque predicates.
  Label experimental displays accurately and check their correspondence.
- If proof requirements help but VE does not outperform the matched interface,
  credit formal verification and reconsider the English surface. If model errors
  dominate, prioritize specification review. Revise broad “VE does not help with
  obfuscation” wording to distinguish checked deductions from unresolved premises,
  without claiming the general problem is solved.
