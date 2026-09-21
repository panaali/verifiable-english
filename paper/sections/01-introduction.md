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

The contributions available for inspection are:

- A relational language specification, canonical serialization, and Python,
  Lean, and Rust cores with distinct documented boundaries; an opt-in closure
  extension is implemented in Python, Rust, and the Lean reference
  (`docs/spec/`, `ve/`, `lean/`, `rust/`).
- Five deterministic views and a common vocabulary legend, with inverse-parser
  tests that recover indexed syntax on development cases
  (`docs/rendering-views.md`, `tests/test_fluent.py`).
- Finite evaluation, countermodel validation, data-only tableau certificates,
  claim graphs, and a three-valued semantic comparison API
  (`docs/implementation.md`, `docs/oracle.md`).
- Lean theorems for named reference operations, alongside explicit unproved
  boundaries and differential conformance evidence (`lean/METATHEORY.md`,
  `lean/CLOSURE.md`, `conformance/`).
- A cross-family model-rater coverage audit with preserved disagreements,
  checked syntax witnesses, and a profile-extension ledger
  (`paper/sources/e0-second-rater.md`, `docs/spec/v0.1-coverage.md`).
- Prompt-sensitive development calibration, frozen E1 and E4 designs, E5
  materials and pilots, and a process record of defects and operational failures.
  **[RESULT-CONTRIBUTIONS: insert scored E1 and E4 findings within their
  per-judge and mechanism-demonstration limits.]**

<!-- src: docs/rendering-views.md (five); docs/spec/closure-implementation.md;
paper/sources/manifest.json pins the implementation base and branch documents.
E1 v5 and E4 revision 2 are frozen; E5 remains a deferred draft. -->
