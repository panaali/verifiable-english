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
