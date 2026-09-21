# Abstract {.unnumbered}

A proof checker establishes a formal consequence, not that the statement
expresses the supervisor's intended requirement. Verifiable English (VE)
addresses this statement-reading gap with a small relational language, five
deterministic views of one syntax tree, and checked composition with explicit
assumptions. Lean proves specified reference evaluator, printer/parser round-trip,
certificate, and graph properties; it does not verify production implementations
or empirical premises. The scored evidence separates surface presentation from
machine checking. For the primary Qwen2.5-32B-Instruct-AWQ judge, strict English
showed no benefit over symbolic FOL: the false-approval contrast with an
asserted-faithful explanation was +0.027 [-0.065, +0.120] (inconclusive), and
without explanation +0.003 [-0.043, +0.049] (a 0.05 reduction refuted, not
harmful), using 97.5% intervals. The combined claim is not supported. Fluent
rendering for the weaker 14B judge is an exploratory replication hypothesis.
The two hosted reference judges (one measured only under the earlier JSON
legend) were at ceiling on these development items, so these items do not
saturate capable readers. Machine-checked
components did help in a separate, pilot-sized countermodel-display demonstration whose
two Qwen2.5 judges both failed its own calibration gate: for 14B,
checked feedback reduced false approval (preregistered -0.267 [-0.392, -0.142],
satisfying the frozen protection rule; -0.117 [-0.231, -0.002] under lenient
parsing in a post hoc sensitivity analysis, not preregistered); for 7B, it rescued honest acceptance by
+0.80 [0.56, 1.04] (unbounded cluster-t; the upper endpoint exceeds the feasible
maximum) from near-universal rejection (95% intervals). Replay rejects
fabricated countermodels by construction. A qualitative, single-agent policy
exercise exposes a disputed predicate but leaves much of the argument outside
VE: five of nine debate claims are unformalized, and amendment clauses receive
one REIFIED and three OPAQUE labels. Coverage of this policy text is low without extensions.
Humans, other judge families in scored comparisons, external baselines,
long-context and compaction settings, and training remain untested. AI workers
produced the artifacts and manuscript under human direction; improved human
readability and general oversight remain unestablished.

<!-- src: paper/sources/e1-results.md (cb2b7ff), E1 and E1b;
paper/sources/e1-prereg-frozen.md (555b3ae), decisions and hosted calibration;
paper/sources/e4-score-summary.json and paper/sources/e4-prereg-frozen.md
(cbc6a80), per-judge effects and decision rule;
paper/sources/debate-coverage.md; paper/sources/amendment-coverage.md;
lean/METATHEORY.md; lean/CLOSURE.md; PROTOCOL.md. -->
