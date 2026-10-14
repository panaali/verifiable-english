# RD-9 elaboration relay binding

The response shapes are owned by `ResponseShape/Schemas/SoftNorms.lean` and
`ResponseShape/Schemas/Rights.lean`. Their encoder theorems cover the values Lean
derives. Python checks the generated schema, then binds every identity or count
that a displayed row names to the submitted source. `CheckerUnavailable` is the
only result of a failed relay check.

The complete, machine-checked inventory is `INVENTORY` in
`tests/test_relay_binding_inventory.py`. Its field list is walked from the
generated schemas of every relayed RD-9 answer: `soft-elaborate`, `soft-pairs`,
`soft-conflict` (packages and witness), the soft and rights `admission`,
`rights-elaborate`, `rights-scope`, `rights-bar` and `rights-conflict`. A field
the Lean shape adds fails `test_every_schema_field_is_classified` until it is
classified as bound or as Lean-derived, with a reason. Every bound field is
fuzzed on genuine answers of fifteen sources: renamed, shifted, flipped,
dropped, duplicated, extended and, when ordered, reversed. Each mutant that still
fits the schema must be `CheckerUnavailable`
(`test_every_bound_field_mutant_is_unavailable`). The table below explains the
relations; the inventory is what is checked.

| Field | Request binding or Lean-derived value | Regression |
| --- | --- | --- |
| `id`, `status` | Service request id and success discriminator; common response binder | `test_route_row_schemas` |
| `environment_prime` (every field) | One binder for both routes (`softnorms.bind_prime_environment`): every field other than `vocabulary.predicates` equals the request. Predicate keys equal request keys plus exactly the decision and rights-generated names, disjointly; original declarations are unchanged; each decision is declared exactly with its key's argument sorts; generated argument sorts match their source acts. | `test_f19_rights_prime_environment_is_the_request_plus_bound_declarations`, `test_f19_soft_prime_environment_is_the_request_plus_bound_declarations`, `test_binding_audit_soft_fields_reject_forgery`, `test_binding_audit_rights_fields_reject_forgery` |
| `document_hash` (soft) | Lean document identity; schema and encoder theorem | `test_every_decision_carries_leans_key` |
| `decisions[].key`, `.name`, `.arguments` | Every key corresponds to exactly one submitted default, switch, or colliding pair; name encodes that key; arguments equal the rule or act's declared sorts; no duplicate or missing row. | `test_a_mutated_decision_key_is_unavailable`, `test_binding_audit_soft_fields_reject_forgery` |
| `derived` | Exactly one rule row per submitted rule | `test_f14_each_soft_identity_field_is_bound` |
| `order`, `premises` | Layer names are exactly the request's regulated predicates; each premise has the matching `layer:norms:` label. Lean owns their order and ASTs. | `test_binding_audit_soft_fields_reject_forgery` |
| `background` | Every `soft:` label is exactly a submitted default's condition or an elaborated colliding pair, once; formulas and other generators are Lean-derived | `test_f14_each_soft_identity_field_is_bound` |
| `colliding_pairs[].pair`, `.act`, `.comparable`, `.label`, `.outweighs` | Exactly the submitted incompatible default pairs, ordered by rule name; each act is the pair's declared act, comparability follows the submitted rank relation, and a holistic comparable pair has its matching named decision. AST is Lean-derived. | `test_f11_unbound_or_missing_decision_rows_are_unavailable`, `test_f14_each_soft_identity_field_is_bound` |
| `conflict_targets` | Exactly the regulated predicates and declared obligation and permission pairs, once. Each target's `sorts` are the layer's declared argument sorts, or the obligation's for a `req->perm` pair (Norms/Replay.lean `targets`). Formulas are Lean-derived. | `test_binding_audit_soft_fields_reject_forgery`, `test_f22_conflict_target_sorts_are_the_declared_argument_sorts` |
| `conditional_on` | Exactly the labels of colliding pairs Lean reports as incomparable. | `test_f12_public_soft_route_rejects_unbound_output`, `test_rights_elaboration_premise_identities_are_bound` |
| `fragment`, `warnings` | Lean-derived Boolean and diagnostics; schema and encoder theorem | `test_route_row_schemas` |
| `ranks_above` (soft) | Exact transitive closure of the request's rank declarations. | `test_f14_each_soft_identity_field_is_bound` |
| `rule_acts` (soft) | Exact act key of each submitted rule predicate. | `test_binding_audit_soft_fields_reject_forgery` |
| `incompatible_pairs` (soft) | Exact submitted rule pairs with opposite effects on one declared act. | `test_f14_each_soft_identity_field_is_bound` |
| `soft_residual`, `default_exceptions_by_decider` (soft) | Exact counts implied by submitted defaults, switches, holistic decisions, open pairs and decider declarations. | `test_binding_audit_soft_fields_reject_forgery`, `test_f12_decider_counts_are_bound_per_decider` |
| `soft_status` (soft) | Lean-derived status; schema and encoder theorem | `test_route_row_schemas` |
| `overlaps`, `override_cycles` (soft, optional) | Rows that answer submitted witnesses. No relay submits a witness, so any such row is extra. | `test_unrequested_witness_rows_are_unavailable` |
| `lines[].right`, `.kind`, `.instance`, `.rule`, `.predicate`, `.holder_slot`, `.node.sign`, `.node.hard`, `.node.over`, `.node.unless` (rights) | Each instance maps to its authored line, kind and field, and its node fields match the authored rule. The rule id is the authored name, or `rights-fan-<k>` for the k-th fan-out instance in document order (Tree.lean `instancesOf`). The holder slot is Tree.lean `holderSlot`: 0 for a liberty half, else the authored `holder_slot`, else the first object slot of the right's holder sort. `node.unless` holds the authored carve-outs, then one limitation pack exactly when a limitation is in scope (Correlate.lean `nodeOf`). Derived guards and the pack's formula remain Lean-owned. | `test_binding_audit_rights_fields_reject_forgery`, `test_f21_generated_rule_ids_follow_leans_naming`, `test_f23_an_authored_holder_slot_stays_the_lines_slot` |
| `generated[].kind`, `.limitation`, `.act`, `.condition`, `.predicate`, `.name` (rights) | Exactly the in-scope limitation/act/condition keys and bar predicates, with key-ordered generated names; each generated declaration has the act's sorts. | `test_binding_audit_rights_fields_reject_forgery` |
| `bars[].predicate`, `.name`, `.over`, `.sign`, `.hard`, `.mode`, `.unless` (rights) | Bar nodes occur only for an authored rule reading. Each is named `rights-bar-<i>` for its aimed predicate's index, and its over rules are the positive lines on the same predicate. Each is strict, hard and negative, with no carve-out (Correlate.lean `barNode`). | `test_rights_bar_nodes_are_bound_to_generated_aimed_predicates`, `test_f21_generated_rule_ids_follow_leans_naming` |
| `limitations`, `rights_background` (rights) | Every in-scope limitation/act/condition key has one label; the background rows match those labels and formulas exactly. | `test_binding_audit_rights_fields_reject_forgery` |
| `narrowings[].in_scope`, `.mechanisms[].licence` (rights) | `in_scope` is whether an authored limitation covers the line's right and kind (Tree.lean `inScope`). A licence has the form Run.lean `licence` gives its mechanism, and the elaboration sends no certificates, so it never says `certified`. | `test_every_bound_field_mutant_is_unavailable[rights-elaborate]` |
| `narrowings[].mechanisms[].mechanism`, `.target` (rights) | The texts are exactly the slots of Correlate.lean `narrowings`, in its order: each authored carve-out `carve-out <i>` (canonical decimal); `exception <M>`; `limitation` iff a limitation is in scope; `exception` iff the rule is default; each authored switch; `blockedBy <M>` (strict `M`) and `dominatedBy <M>` (default `M`) only on a default line; `bar` iff a rule-reading bar reaches the line. Each `M` is another line instance or norm unit. The target is exactly `rule:mechanism`. | `test_f18_narrowing_mechanism_and_target_bind_to_authored_line`, `test_f20_mechanisms_are_exactly_the_request_implied_slots` |
| `findings`, `unit_open` (rights) | ProtectedInCone text is tied to the distinction hits; each open flag is typed and positioned for a submitted unit. | `test_binding_audit_rights_fields_reject_forgery`, `test_route_row_schemas` |
| `distinction`, `wordings` (rights) | One distinction row per right-derived predicate. Each hit names an elaborated right/rule and a protected predicate, and is `cited` exactly when its line cites a guard source (Distinction.lean `distinctionHits`). Wording keys equal generated names, and placeholders are positional within the declaration's arity. | `test_binding_audit_rights_fields_reject_forgery`, `test_f17_distinction_rows_and_hits_are_bound` |

The displayed `rights-scope` response binds every line and mechanism identity
to the checked elaboration of the same source. Its scope flags equal the
elaboration. Each licence has the form its mechanism allows (one shared
`rights_route._licence_bound`); `certified` is allowed only when certificates were sent. Each
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
two counts; its verdict and optional detail are Lean-derived. A witness answer
(on either route) names the submitted witness's target. The `soft-conflict`
answer's `conditional_on` is a subset of the open (incomparable) coherence
labels, and its `budget` is the one sent.

Every admission relay (`admission.bound_admission`, soft and rights) binds the
report with one binder, `admission.bind_report`. The root is the graph's root
claim, and the assumptions are exactly the ordered unfolding of the request
graph (ClaimGraph.lean `Unfolds`), with a shared premise listed once per use.
`test_a_report_is_the_ordered_unfolding_of_the_request_graph` drops, repeats,
reorders and replaces assumptions and changes the root. `test_f15_rights_conflict_identities_are_bound`
mutates each displayed identity, including an extra row and an empty list.
