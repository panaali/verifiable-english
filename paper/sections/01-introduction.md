# Introduction

Scalable oversight asks how a limited supervisor can assess a more capable
agent's work. Formal verification can remove the need to inspect each step of a
proof. It leaves a separate responsibility: deciding whether the statement and
its assumptions say what the supervisor intended. We call this the
*statement-reading gap*: proofs are checked by machines; statements are signed
off by supervisors.

Recent vendor reports of AI-produced mathematics make this distinction concrete.
[Anthropic's Fermat formalization report](https://www.anthropic.com/research/formalizing-fermats-last-theorem)
describes Lean checking and a separate comparison with Mathlib's theorem
statement. [OpenAI's mathematics report](https://openai.com/index/ten-advances-in-mathematics/)
describes AI-generated arguments subsequently formalized as Lean certificates.
We checked these announcements, not their proof repositories or mathematical
novelty. They motivate the problem and are not evidence about VE. Lean's own
[proof-validation guidance](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)
separates proof validity from statement interpretation and retains misleading
presentation as a trust assumption.
<!-- src: paper/sources/capability-brief.md, motivating reports;
docs/architecture-and-design.md, statement-reading argument; paper/references.md. -->

An agent can submit a provable but inadequate requirement. It can omit a
condition, change a quantifier dependency, or attach persuasive prose to a
weakened formula. A correct proof then certifies the wrong target. A different
failure arises when one formal predicate is supported with evidence using
incompatible meanings. Logical composition remains valid, but the premises have
not been established under a common interpretation. Neither failure is repaired
by a longer proof.

VE proposes *sign-off on precise claims plus checked composition of those
claims*. A supervisor inspects an environment and an exact claim. Deterministic
views expose its operators, binders, and vocabulary. Deduction certificates are
checked against those same claims. Composition retains the premises on which the
root depends. A critic may submit a finite countermodel rather than an
unsupported assertion that an inference is invalid.

The scaling argument is conditional. If the specification and remaining premises
stay manageable while proofs grow, supervision can focus on them. This does not
bound the difficulty of reading specifications, validating evidence, constructing
proofs, or checking large submissions. The formal machinery is available to
non-English interfaces too. VE's surface must therefore be compared with
structured logic using the same checker and evidence. Model judges test a model
oversight hypothesis; they cannot establish human readability.

The evidence supports the checked components more than the English surface.
Strict English showed no benefit for the capable primary judge; a useful
reduction is excluded without explanation and remains inconclusive with it.
Fluent rendering for a weaker judge is an exploratory hypothesis. The two hosted reference judges (one measured only under the earlier JSON
legend) were at ceiling on these development items, so these items do not
saturate capable readers.
In contrast, the checked-countermodel intervention cut false approval for 14B
and rescued honest acceptance for 7B. Real policy text also exposes a separate
bottleneck: much of its meaning and justification lies outside current VE.
<!-- src: paper/sources/e1-results.md; paper/sources/e1-prereg-frozen.md;
paper/sources/e4-score-summary.json; paper/sources/debate-coverage.md;
paper/sources/amendment-coverage.md. -->

The contributions available for inspection are:

- A relational language, five deterministic presentations, finite evaluation,
  countermodel validation, data-only certificates, and assumption-preserving
  claim graphs, with Python, Lean, and Rust boundaries documented separately.
  Lean establishes named reference properties, including an opt-in sound
  closure certificate checker; it does not establish production refinement.
- A frozen sign-off experiment with a negative primary conclusion: VE strict
  has no demonstrated benefit over symbolic FOL for Qwen2.5-32B-Instruct-AWQ.
  P1 is inconclusive; P2 refutes a 0.05 reduction without establishing harm.
  The combined claim is inconclusive and not supported. Fluent rendering for
  14B remains an exploratory hypothesis for replication.
- A countermodel-display mechanism demonstration: checked feedback cuts 14B
  false approval and recovers 7B honest acceptance. Fabricated countermodels
  fail replay by construction. These results concern machine checking and
  its display, with per-judge limits, not an English-specific advantage.
- A model-rater coverage audit with preserved disagreements and a qualitative
  policy use case showing low coverage without extensions: five of nine
  debate claims fall outside formalization, and three of four amendment
  clauses are OPAQUE. One Sonnet agent produced the new use case without
  cross-review; this is not a representative coverage estimate.
- A process record of caught defects, failed calibration, and runner-estimated
  compute costs. E5 remains materials and pilots only; E2 was not run.
  Human evaluation, multi-family scored replication, external-baseline
  comparisons, long-context and compaction settings, and training remain open.

<!-- src: docs/rendering-views.md; docs/spec/closure-implementation.md;
lean/METATHEORY.md; lean/CLOSURE.md; paper/sources/e1-results.md;
paper/sources/e4-score-summary.json; paper/sources/e4-prereg-frozen.md;
paper/sources/e0-second-rater.md; paper/sources/debate-coverage.md;
paper/sources/amendment-coverage.md; paper/sources/process-log-results.md;
paper/sources/manifest.json pins the implementation base and branch documents. -->
