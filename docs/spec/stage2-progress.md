# Semantics migration Stage 2 progress

This checkpoint follows [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md), revision 3. Stage 0 and Stage 1 are merged on `mig/stage2`. The Stage 0 `python.json` behaviour baseline remains the oracle; only its generator-commit metadata was updated after the replay-script commit. `VE_AUTHORITY` still defaults to `python`.

| Plan item | Status | Evidence and remaining work |
|---|---|---|
| 2a Python adapters | Partial | `ve/backends/` selects authority, translates diagnostics, records shadow differences, checks binary hashes and Rust response framing. Public adapters exist for Background, dependency order, labels, evaluation, countermodel checks, bounded countermodel search and distinguishing search. Search witnesses are checked by Lean before return. Other class-A functions still need adapters. Batching, provenance fields, complete fault injection and exact full-matrix parity remain. |
| 2b Lean glue modes | Open | The merged Stage 1 service exposes its original six modes. Standalone `parse`, `normalize`, `check`, `environment`, `model`, `graph`, `readings` and `identity`, plus route evaluation source binding, are not implemented. |
| 2c Lean coverage closure | Open | The plan's norms with definitions/data flags and closure bundle gaps remain. The existing route does not generate Background for `closure@0+nary@0`. |
| 2d readings checker | Open | No Lean readings checker or soundness theorems are merged. |
| 2e Rust extensions | Partial | Budgeted evaluation now emits Python-shaped traces with the legacy charging rule. Search supports `min_domain_size`, `nonempty_domains` and distinguishing models, including n-ary relation atoms. `nonvacuous_for`, `semantic_nonvacuity`, order-family search/evaluation and Rust parse diagnostics remain. |

The Python-default Stage 0 probe replay and inventory lint pass. Focused Python tests and `cargo test -p ve-core` pass. A direct comparison of positive and budget probes on six profile families found agreement for implemented FOL, data, definitions, closure and n-ary evaluation/search operations, with the n-ary Background and order-family differences listed above. Gate 2 is **not passed**: the full Lean-authority suite, matrix regression comparison, graph mode and readings checker are outstanding. Shadow mode records differences while returning Python's result; the Stage 3 soak has not started.
