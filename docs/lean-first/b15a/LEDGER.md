# Batch 15a owner and deletion ledger

| Decision | Owner after 15a | Caller in this batch | Duplicate deleted |
|---|---|---|---:|
| Bounded finite-model evaluation, shared document charging, value, `ResourceLimit` | Lean `VE.Route.Metered` over the existing proved family evaluators | Lean `ve_metered` (`evaluate-budgeted`) | 0 |
| Evaluation explanation display | Lean `VE.Route.MeteredTrace`, called only after the metered result | Lean `ve_metered` | 0 |
| Non-vacuity of a proposed witness, including domain and semantic guards | Lean `VE.Route.NonVacuity` | Lean `ve_metered` (`non-vacuity`) | 0 |
| Layered core model: defined tables computed over the FOL projection (review B3) | Lean `VE.Core.Layers.completeModel`; `decodeLayered` for the layered environment's two decodings | `Core.Layers.run`, `Route.Run` labels, `Service.Standalone.modelCase`, `Service.Family.coreEnv`, `ve_metered` | 3 Lean copies (`MeteredRun.coreLayers`, `Standalone.modelCase`, `Family.coreEnv`) |
| Evaluable environment, frozen `ve.core@0`/`ve.core@0.1` envelopes included (review B1) | Lean `VE.Service.Standalone.evaluable` over `decodeLegacy` (frozen) and `validated` (`ve.core@0.2`) | `ve_metered`; `Standalone.legacyTyped` now dispatches on `decodeLegacy` | 2 Lean copies (`ve_metered`'s own envelope gate, `legacyTyped`'s inline frozen-envelope dispatch) |
| One family decoding per metered case | Lean `VE.Route.MeteredRun.run` building a `Session` | both `ve_metered` case kinds | 1 Lean copy (`runNonVacuity`'s second per-family decoding) |

The draft-3 plan (`git show design/lean-first:docs/LEAN-FIRST-PLAN.md`, section 5.2) specifies `—` in its deletion column for 15a. The old Python and Rust evaluator consumers continue to run as before. Batch 15b owns the switch of those callers and deletion of their generator-internal copies, subject to the rule-3 decision. The batch-2 [record](../b2/rule3.json) found that the Rust enumerator missed its deadline, so 15a does not add the conditional candidate-batch path.
