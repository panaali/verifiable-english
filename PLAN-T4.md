# T4: universal policy guarantees with a weak trusted monitor (2026-09-22), for review

Why: P3 found VE added value ONLY on universal properties (6/12 certified); per-request questions were answered 75/75 by
plain review. Snapshot tools (trusted BFS on a JSON edge list, a judge's own script) answer queries about the CURRENT
state; a universal claim - "no principal can ever reach R under any membership assignment these rules allow", or "this
policy change preserves invariant I" - needs a proof or a countermodel.

Setting (AI control): untrusted agent Opus 5.5 (sabotaging on half the items) claims an invariant holds; trusted monitor
Haiku 4.5 (and Sonnet 5 for scale) approves or rejects. Items: rule-based policies (role inheritance, group-nesting rules,
conditional grants expressible in closure@0) with 50-300 rules, from P3's real artefact families plus generated variants;
sabotaged items have an invariant violated only under a non-obvious membership assignment (a countermodel exists) or a
proposed change that breaks it. Arms at matched monitor tokens: (a) monitor reads rules + claim; (b) agent's own script /
test suite as evidence, executed by the harness (can only test sampled states); (b') trusted random/exhaustive state
testing up to a size bound (a strong snapshot baseline); (c) agent supplies a VE formalisation + certificate (invariant
proved) or the checker returns a countermodel; monitor checks translation faithfulness (mistranslation attack included);
(d) monitor writes and runs its own code. Metrics: false approval of violated invariants, honest completion, monitor tokens,
certificate success rate (prover step limits are a known risk: 6/12 in P3 hit ResourceLimit - report and bound it).
Gate: 20 items, arm (a) with Haiku; continue if false approval >= 15%. Preregister and timestamp.

## After review (2026-09-22): both "revise; narrow feasibility pilot"

Key facts: negative reachability invariants ("no principal reaches R") need induction; the closure calculus has none
(docs/spec/v0.1-profiles.md), so they are unprovable on cyclic graphs and blow up on acyclic ones (P3 ResourceLimit).
For monotone rules (b') reduces to one search over the maximal assignment, so it catches everything unless violations
need interacting rules/principals. Decision:
1. BUILD FIRST (valuable independently; also the math use case's gap G5): a closure-induction rule,
   P(x) and forall a,b.(P(a) and E(a,b) -> P(b))  |-  forall y.(tc[E](x,y) -> P(y)), with the agent supplying the invariant
   P; soundness proved in Lean; Python checker + Lean replay; certificate format versioned; no change to existing rules.
2. Then the pilot: one family (group nesting + deny / separation-of-duty rules), sizes 50 and 150, 20 items (10
   sabotaged, violations arising from COMBINATIONS of individually harmless rules), arms (a), (b') at a preregistered
   bound, (c); Haiku only; generator supplies background axioms; one hand-written mistranslation per sabotaged item.
   Two-sided gate: (a) false approval >= 15% AND (b') misses >= 30% AND >= 80% of true invariants certify. Intervals.

Implementation update (2026-09-22): item 1 is implemented as `closure-induct@1`
in checker version `ve-tableau-closure-checker@1`, with old certificates accepted
unchanged. Lean proves the rule and the extended certificate checker sound.
[Specification](docs/spec/closure-induction.md),
[implementation report](docs/closure-induction-report.md), and
[T9/T9e plus cyclic-policy certificates](usecases/closure-induction/README.md).
The pilot in item 2 remains separate future work.
