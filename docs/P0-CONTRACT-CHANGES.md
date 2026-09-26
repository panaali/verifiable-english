# W3 additive declaration extension

The `ve.core@0.2` environment accepts an optional `defined` field on a predicate declaration when `definitions@0` is present. Its value has exactly `arguments` and `body`; the arguments must match the predicate signature, and the body is a typed formula AST. The immutable environment stores canonical bytes for the field, validates dependency order and free variables, and includes the field in `environment_id`. No existing declaration or identity domain changes.

The `definitions` Background slot emits the closed biconditional for each declaration in dependency order. Finite models supply tables only for base predicates; decoding computes each defined table from its body. A supplied defined table is rejected. The existing checker consumes the generated Background before case premises. This is an additive hook: environments without `defined` produce the same serialized bytes, IDs, and empty definitions Background as before.

The Rust environment decoder explicitly returns `UnsupportedProfile` for a `defined` field. The Lean route vocabulary decoders also return `UnsupportedProfile`. Neither checker may silently interpret a defined predicate as uninterpreted. Their semantic elaborators remain a required next step before cross-language acceptance of defined documents.

The Lean `Definitions.Alias` theorems use the existing frozen `Layer` interface. Its three named theorems are included in the central axiom audit manifest. The contract change does not alter any existing theorem statement.
