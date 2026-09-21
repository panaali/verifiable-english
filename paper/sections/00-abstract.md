# Abstract {.unnumbered}

A proof checker establishes a formal consequence. It does not establish that the
proved statement expresses the supervisor's intended requirement. Verifiable
English (VE) addresses this statement-reading gap with a small relational
language, deterministic presentations, and explicit assumption tracking. A claim
is a closed formula of many-sorted, function-free first-order logic with equality.
Its environment records the vocabulary and intended descriptions. Five views
render the same syntax tree with a shared vocabulary legend. Finite evaluation,
countermodels, tableau replay, and claim graphs separate logical support from
interpretation and evidence. Lean proves evaluator correctness, canonical
print/parse round trips, certificate soundness, and assumption-preserving graph
composition for specified reference representations. These results do not verify
the Python or Rust implementations, the full decoding boundary, or empirical
premises. An opt-in reachability profile has a separately stated proof boundary.
An exploratory coverage audit reports substantial disagreement between model
raters, especially about policy hierarchies. Development pilots motivate a
capability gate before testing presentation effects with model supervisors.
**[RESULT-ABSTRACT: scored E1 and E5 effects and uncertainty are not yet available;
insert the audited outcomes, including null or harmful effects.]**
No human participants were studied. The implementation, experiments, reviews,
and manuscript were produced by AI workers from different model families under
an AI orchestrator and human project direction. The paper reports artifacts and
experimental designs; improved oversight and human readability remain unestablished.

<!-- src: docs/rendering-views.md (five views); lean/METATHEORY.md;
lean/CLOSURE.md; PROTOCOL.md; paper/sources/process-log-excerpts.md.
All RESULT markers deliberately remain visible. Source comments name committed
artifacts; external records were first committed under paper/sources/. -->
