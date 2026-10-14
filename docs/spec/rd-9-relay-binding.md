# RD-9 elaboration relay binding

The response shapes are owned by `ResponseShape/Schemas/SoftNorms.lean` and
`ResponseShape/Schemas/Rights.lean`. Their encoder theorems cover the values Lean
derives. Python checks the generated schema, then binds every identity or count
that a displayed row names to the submitted source. `CheckerUnavailable` is the
only result of a failed relay check. The following inventory is the complete
`soft-elaborate` and `rights-elaborate` response field set at this revision.

| Field | Request binding or Lean-derived value | Regression |
| --- | --- | --- |
| `id`, `status` | Service request id and success discriminator; common response binder | `test_route_row_schemas` |
| `environment_prime.profiles`, `.vocabulary.predicates` | Profiles equal the request. Predicate keys equal request keys plus exactly the decision and rights-generated names; original declarations are unchanged and generated argument sorts match their source acts. | `test_binding_audit_soft_fields_reject_forgery`, `test_binding_audit_rights_fields_reject_forgery` |
| `document_hash` (soft) | Lean document identity; schema and encoder theorem | `test_every_decision_carries_leans_key` |
| `decisions[].key`, `.name`, `.arguments` | Every key corresponds to exactly one submitted default, switch, or colliding pair; name encodes that key; arguments equal the rule or act's declared sorts; no duplicate or missing row. | `test_a_mutated_decision_key_is_unavailable`, `test_binding_audit_soft_fields_reject_forgery` |
| `derived` | Exactly one rule row per submitted rule | `test_f14_each_soft_identity_field_is_bound` |
| `order`, `premises` | Layer names are exactly the request's regulated predicates; each premise has the matching `layer:norms:` label. Lean owns their order and ASTs. | `test_binding_audit_soft_fields_reject_forgery` |
| `background` | Every `soft:` label is exactly a submitted default's condition or an elaborated colliding pair, once; formulas and other generators are Lean-derived | `test_f14_each_soft_identity_field_is_bound` |
| `colliding_pairs[].pair`, `.act`, `.comparable`, `.label`, `.outweighs` | Exactly the submitted incompatible default pairs, ordered by rule name; each act is the pair's declared act, comparability follows the submitted rank relation, and a holistic comparable pair has its matching named decision. AST is Lean-derived. | `test_f11_unbound_or_missing_decision_rows_are_unavailable`, `test_f14_each_soft_identity_field_is_bound` |
| `conflict_targets` | Exactly the regulated predicates and declared obligation and permission pairs, once; formulas are Lean-derived. | `test_binding_audit_soft_fields_reject_forgery` |
| `conditional_on` | Exactly the labels of colliding pairs Lean reports as incomparable. | `test_f12_public_soft_route_rejects_unbound_output`, `test_rights_elaboration_premise_identities_are_bound` |
| `fragment`, `warnings` | Lean-derived Boolean and diagnostics; schema and encoder theorem | `test_route_row_schemas` |
| `ranks_above` (soft) | Exact transitive closure of the request's rank declarations. | `test_f14_each_soft_identity_field_is_bound` |
| `rule_acts` (soft) | Exact act key of each submitted rule predicate. | `test_binding_audit_soft_fields_reject_forgery` |
| `incompatible_pairs` (soft) | Exact submitted rule pairs with opposite effects on one declared act. | `test_f14_each_soft_identity_field_is_bound` |
| `soft_residual`, `default_exceptions_by_decider` (soft) | Exact counts implied by submitted defaults, switches, holistic decisions, open pairs and decider declarations. | `test_binding_audit_soft_fields_reject_forgery`, `test_f12_decider_counts_are_bound_per_decider` |
| `soft_status` (soft) | Lean-derived status; schema and encoder theorem | `test_route_row_schemas` |
| `overlaps`, `override_cycles` (soft, optional) | Submitted witness results, typed by schema; their validity and message are Lean-derived | `test_route_row_schemas` |
| `lines[].right`, `.kind`, `.instance`, `.rule`, `.predicate`, `.node.sign`, `.node.hard`, `.node.over` (rights) | Each instance maps to its authored line, kind and field; node fields match the authored rule. Derived guards and limitation packs remain Lean-owned. | `test_binding_audit_rights_fields_reject_forgery` |
| `generated[].kind`, `.limitation`, `.act`, `.condition`, `.predicate`, `.name` (rights) | Exactly the in-scope limitation/act/condition keys and bar predicates, with key-ordered generated names; each generated declaration has the act's sorts. | `test_binding_audit_rights_fields_reject_forgery` |
| `bars[].predicate`, `.name`, `.over` (rights) | Bar nodes occur only for an authored rule reading and their over rules are positive lines on the same predicate. | `test_rights_bar_nodes_are_bound_to_generated_aimed_predicates` |
| `limitations`, `rights_background` (rights) | Every in-scope limitation/act/condition key has one label; the background rows match those labels and formulas exactly. | `test_binding_audit_rights_fields_reject_forgery` |
| `narrowings[].mechanisms[].mechanism`, `.target` (rights) | Each reference names an authored rule, switch party or carve-out index; the target is exactly `rule:mechanism`. Request-implied carve-outs, switches, exceptions and limitation packs are present. | `test_f18_narrowing_mechanism_and_target_bind_to_authored_line` |
| `findings`, `unit_open` (rights) | ProtectedInCone text is tied to the distinction hits; each open flag is typed and positioned for a submitted unit. | `test_binding_audit_rights_fields_reject_forgery`, `test_route_row_schemas` |
| `distinction`, `wordings` (rights) | One distinction row per right-derived predicate; each hit names an elaborated right/rule and protected predicate. Wording keys equal generated names, and placeholders are positional within the declaration's arity. | `test_binding_audit_rights_fields_reject_forgery`, `test_f17_distinction_rows_and_hits_are_bound` |

The displayed `rights-scope` response binds every line and mechanism identity
to the checked elaboration of the same source. Its scope flags equal the
elaboration; each licence has a fixed form or names its blocking rule, and each
finding names an in-scope mechanism with no licence. The displayed `rights-bar`
response has exactly the elaborated aimed predicate rows under the authored
reading; each reported barred, blocked or composition rule has the required
line, sign and mode.
`test_f16_scope_rows_are_bound_to_elaboration` and
`test_f16_bar_rows_are_bound_to_elaboration` mutate the displayed identities,
missing rows and extra rows.

The displayed `rights-conflict` response also binds `targets` to the complete
`conflict_targets` list of the same elaboration and `conditional_on` to its
coherence and limitation labels. A conflict-free status line states the exact
two counts; its verdict and optional detail are Lean-derived. `test_f15_rights_conflict_identities_are_bound`
mutates each displayed identity, including an extra row and an empty list.
