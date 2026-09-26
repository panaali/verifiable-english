# W3 additive declaration extension

The `ve.core@0.2` environment accepts an optional `defined` field on a predicate declaration when `definitions@0` is present. Its value has exactly `arguments` and `body`; the arguments must match the predicate signature, and the body is a typed formula AST. The immutable environment stores canonical bytes for the field, validates dependency order and free variables, and includes the field in `environment_id`. No existing declaration or identity domain changes.

The `definitions` Background slot emits the closed biconditional for each declaration in dependency order. Finite models supply tables only for base predicates; decoding computes each defined table from its body. A supplied defined table is rejected. The existing checker consumes the generated Background before case premises. This is an additive hook: environments without `defined` produce the same serialized bytes, IDs, and empty definitions Background as before.

The elaborator handles unary and binary predicates over user sorts on the FOL and closure families, in Python, Rust and the Lean route alike: each decodes the field, orders definitions by the shared dependency DAG (same cycle diagnostic), checks each body below its symbol, regenerates the definitions Background, and computes defined model tables from their bodies. Three gates are explicit and identical in all three: definitions on the order family, definition bodies with reachability, and `defined` without `definitions@0`. The `nary@0` checker family remains gated. The Lean route also gates admission of documents with definitions (`admit_string_sound` covers literal Background only) and lemma bundles on the closure family.

The Lean route gains two case kinds: `background` (the regenerated Background with generators, for the differential elaboration check) and `bundle` (a whole lemma bundle checked in one run). `RouteVocabulary` gains the checked definition list; `decodeModel` computes defined tables. `decodeModel_valid` and every other existing theorem statement are unchanged.

The Lean `Definitions` theorems use the existing frozen `Layer` interface unchanged; all are in the central axiom audit manifest.
