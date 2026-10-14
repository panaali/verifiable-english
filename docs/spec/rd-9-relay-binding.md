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
| `environment_prime` | Lean-generated environment; schema and encoder theorem, then constructed as a checked `SoftEnvironment` | `test_f11_public_soft_route_binds_lean_row` |
| `document_hash` (soft) | Lean document identity; schema and encoder theorem | `test_every_decision_carries_leans_key` |
| `decisions` | Every key corresponds to exactly one submitted default, switch, or colliding pair; no duplicate or missing rows; names and argument sorts are Lean-derived | `test_a_mutated_decision_key_is_unavailable`, `test_f11_unbound_or_missing_decision_rows_are_unavailable` |
| `derived` | Exactly one rule row per submitted rule | `test_f14_each_soft_identity_field_is_bound` |
| `order`, `premises` | Layer names are distinct declared predicates; each premise has the matching `layer:norms:` label | `test_f14_each_soft_identity_field_is_bound` |
| `background` | Every `soft:` label is exactly a submitted default's condition or an elaborated colliding pair, once; formulas and other generators are Lean-derived | `test_f14_each_soft_identity_field_is_bound` |
| `colliding_pairs` | Pair members are submitted rules, their act is declared, and their label names the pair in Lean's order; no duplicate | `test_f11_unbound_or_missing_decision_rows_are_unavailable`, `test_f14_each_soft_identity_field_is_bound` |
| `conflict_targets` | Every target names a declared act or its declared obligation and permission pair, once; formulas are Lean-derived | `test_f14_each_soft_identity_field_is_bound` |
| `conditional_on` | Distinct labels among the elaborated coherence pairs | `test_f12_public_soft_route_rejects_unbound_output`, `test_rights_elaboration_premise_identities_are_bound` |
| `fragment`, `warnings` | Lean-derived Boolean and diagnostics; schema and encoder theorem | `test_route_row_schemas` |
| `ranks_above` (soft) | Every key and value names a submitted rank, with no duplicate | `test_f14_each_soft_identity_field_is_bound` |
| `rule_acts` (soft) | Exactly submitted rule keys and declared acts | `test_f11_unbound_or_missing_decision_rows_are_unavailable` |
| `incompatible_pairs` (soft) | Distinct submitted rule pairs | `test_f14_each_soft_identity_field_is_bound` |
| `soft_residual`, `default_exceptions_by_decider` (soft) | Counts are bounded by submitted defaults, switches, pair and decider declarations; exact semantic residual is Lean-derived | `test_f12_public_soft_route_rejects_unbound_output`, `test_f12_decider_counts_are_bound_per_decider` |
| `soft_status` (soft) | Lean-derived status; schema and encoder theorem | `test_route_row_schemas` |
| `overlaps`, `override_cycles` (soft, optional) | Submitted witness results, typed by schema; their validity and message are Lean-derived | `test_route_row_schemas` |
| `lines`, `generated`, `bars` (rights) | Each line's right, kind, source rule, bearer and predicate match the corresponding authored line; bar nodes match generated aimed predicates under a submitted rule reading and their over rules are elaborated lines; every generated source key names a submitted limitation, condition, act or bar, and its generated declaration exists once | `test_f11_public_rights_route_binds_lean_row`, `test_rights_elaboration_premise_identities_are_bound`, `test_rights_bar_nodes_are_bound_to_generated_aimed_predicates` |
| `limitations`, `rights_background` (rights) | Every limitation label names a submitted limitation, condition, role and declared act, once; the background rows match those labels and formulas exactly | `test_rights_elaboration_premise_identities_are_bound` |
| `narrowings` (rights) | Right and rule pairs equal the elaborated lines; each distinct mechanism target names its rule; scope, conclusion and licence are Lean-derived | `test_rights_elaboration_premise_identities_are_bound` |
| `findings`, `unit_open` (rights) | Lean-derived diagnostics and one open flag per submitted unit, typed by schema and covered by encoder theorem | `test_route_row_schemas` |
| `distinction`, `wordings` (rights) | Distinction predicates and hit right/rule pairs refer to submitted acts and elaborated lines; wording keys equal generated names; text and flags are Lean-derived | `test_rights_elaboration_premise_identities_are_bound` |

The displayed `rights-conflict` response also binds `targets` to the complete
`conflict_targets` list of the same elaboration and `conditional_on` to its
coherence and limitation labels. Its `verdict`, `status_text` and optional
`detail` are Lean-derived. `test_f15_rights_conflict_identities_are_bound`
mutates each displayed identity, including an extra row and an empty list.
