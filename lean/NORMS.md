# W1 norms in Lean (`lean/VE/Norms/*`)

Specification: [docs/spec/norms.md](../docs/spec/norms.md) sections 4 to 7 (draft 2,
READY TO BUILD). This file lists every definition the statement review reads and
every theorem in plain words. All statements quantify universally over their
displayed parameters. `lean/audit.py` audits every theorem below: no `sorry`, only
`propext`, `Classical.choice` and `Quot.sound`. No frozen P0 file and no
`lean/VE/Route/*` source changed (`python3 VE/Route/frozen.py`); `VE.lean` and
`VE/Audit.lean` gained imports and audit entries only, and `lakefile.toml` gained
the `ve_norms_route` target (root `NormsMain.lean`) without changing existing
targets.

## Files

| File | Contents |
|---|---|
| `Basic.lean` | Python-shaped connectives (`anyF`, `allF`, `iffF`), binders in argument order (`bindAll`), the situation atom, `tupleVal`, `hide`/`forget`, capture-avoiding instantiation `inst` |
| `Tree.lean` | `Regulated`, `Definition`, `Node`, `Tree`, `Doc`; rules, children, layer symbols `syms` in `dependencyOrder`, prefix environments `envAt`, declared `pairs`; the executable `check`/`validate`/`WellFormed` with the shared diagnostics |
| `Valid.lean` | `Valid`, the facts the proofs use, from `WellFormed`; prefix-environment lemmas; `precedence_acyclic` |
| `Elaborate.lean` | `applies`, `yields`, `selects`, `pos`, `neg`, `outcome`, `elabPremise` (the spec's `elab`, a Lean keyword), `elaborate`; the direct semantics `AppliesD`/`YieldsD`/`SelectsD`/`DecidesD`, `Value`, `IntendedAt`, `holdsCatala`; faithfulness |
| `Subst.lean` | outcome substitution (`substWith`, `expTable`, `subst`), `restrictAll`, typing and soundness |
| `Prefix.lean` | `Sat`, pair premises, `background`, `BaseAdmissible`, `LayerMeaning`, `PrefixAdmissible`, `PrefixPremises`; `prefix_satisfaction`, `subst_sound` |
| `Conflict.lean` | `ConflictFreeAt`, `AdmissibleOut`, `conflict`, `pairConflict`, `ConflictFree`, `DocumentExpansion`; the local and document-wide iffs; witnesses |
| `Layer.lean` | `symLayer`/`layer` (frozen `VE.Route.Layer` instances), `chain`/`route` (frozen `Layer.comp`), route acceptance and countermodel theorems |
| `SmallModel.lean` | `InFragment`; `conflict_smallModel` (proved) |
| `Cedar.lean` | `CedarShape`; `cedar_decision` |
| `Checks.lean` | executable guards: byte-identical agreement with Python `ve/norms.py` on five documents; the 10.1 regressions on finite models |
| `Examples.lean` | actual `Layer` values for 10.1(c) and (m), the composed routes of (c) and (o) |
| `Wire.lean` | the norms decoder: `regulated` declarations beside the frozen P0 vocabulary decoder, norm objects, `Source`, regenerated outputs |
| `Replay.lean` | conflict-package replay (CONFLICT-FREE), witness replay (CONFLICT), entailment-certificate replay, and their theorems from raw JSON |
| `Run.lean`, `../NormsMain.lean` | the `ve_norms_route` executable (Lake target added; existing targets unchanged) |

## Conventions (agreed with Python through the spec's wire format)

* A binary `p(s₁, s₂)` has situation context `[s₂, s₁]`: de Bruijn index 0 is the
  last argument. Relation tuples stay in argument order; `tupleVal vs = vs.reverse`
  is the valuation of a tuple (spec 6.1, Astra A2).
* Generated formulas are exactly Python's: `anyF` is a left fold from `bottom`,
  `allF` from `top`; children are sorted by name, one entry per occurrence in a
  rule's `over` (Python appends per occurrence); the positive and negative
  selection lists keep the rules' document order. `Checks.lean` compares the
  compact JSON of Lean's `elaborate`, conflict formulas and profile premises with
  Python's output string for string.
* Diagnostics follow Python's check order (environment declarations, then the
  rule count, then each rule in order: name, duplicate, predicate, carve-out
  count, typing; then `over`, the precedence DAG, depth, the stratum DAG) and
  are rendered `<code>: <message>` as 11.1 writes them; Python's `VEError`
  renders the same text as `f"{code}: {message}"` when the message does not
  already begin with a code.
* The layer order is `VE.Route.dependencyOrder` over defined ∪ regulated
  predicates. Pairs are sorted by the obligation's name (Python `sorted`).
* **Premise order on the route** (the choice the Fable recheck asked W1 and W3 to
  make once): Background in the P0 generator order, flags, then W3 definition
  biconditionals in DAG order, then literals, then profile pair premises; then the
  norm elaborations (`layer:norms:<p>`) in DAG order; then the document's own
  premises. This is `background D ++ elaborate D.T ++ Γ` and is exactly Python's
  `checked_premises` with `ve/norms.py` `premises()` as layer premises. W3
  definitions are therefore Background's `definitions` slice (W3's convention);
  on the composed route a definition's layer contributes no premise and carries
  its biconditional in its output admissibility (the W3 interface requirement
  of 6.1).
* Recursion on the precedence DAG uses fuel `T.nodes.length`; every rule's
  height in an acyclic DAG is smaller, so the formulas equal Python's unbounded
  recursion. `Value` uses the same fuel, so faithfulness does not depend on it.

## Definitions under statement review

| Name | Meaning |
|---|---|
| `AppliesD`, `YieldsD`, `SelectsD`, `DecidesD` | The direct rule recursion over propositions: a rule applies when its guard holds and no carve-out does; its subtree yields when it applies or an exception subtree yields; it selects when it applies and no exception subtree yields; a sign decides when some rule of that sign selects. |
| `Value T r S vs` | Catala's value at a tuple (read at `tupleVal vs`): `true` if only positive rules decide, `false` if only negative ones, the default if none, no value if both. |
| `IntendedAt T r S` | On every typed tuple the rules, read below `p` (`forget [p] S`), give a value, and `p` holds exactly when it is `true`. |
| `holdsCatala T S` | `IntendedAt` for every regulated predicate. |
| `LayerMeaning` | `IntendedAt` for a regulated symbol; for a definition, the relation agrees with the body on typed tuples. |
| `BaseAdmissible D B` | Structural admissibility over `E_base` plus `Background_base` (literal distinctness; flags arrive with W5). |
| `PrefixAdmissible D k S` | `k = 0`: base-admissible. `k+1`: admissible over `E_(k+1)`, prefix-admissible at `k` after forgetting the `k`-th symbol, that symbol's `LayerMeaning`, and every pair premise closing at it. |
| `ConflictFreeAt D p S₀` | On the interpreted prefix below `p`: no typed tuple where both `P_p` and `N_p` hold, and every pair closing at `p` respected with the earlier member read from `S₀`'s actual relation. |
| `ConflictFree D B` | On a base structure: no typed tuple satisfies any `conflict_p` or `conflict_(r,m)` (outcome-substituted formulas). |
| `DocumentExpansion D B S` | `S` forgets to `B`, is admissible for the complete environment and satisfies Background and every norm elaboration. |
| `InFragment D` | Every conflict formula is quantifier-free. |
| `CedarShape T p` | Unique rule names, no carve-outs, permits take precedence over nothing, every forbid takes precedence over every permit and over permits only. |

## Theorems in plain words

Names have prefix `VE.Norms.`.

| Theorem | Statement in plain words |
|---|---|
| `tupleVal_typed` | A relation tuple typed by the argument sorts gives a valuation typed by the reversed sorts. |
| `tupleTyped_of_tupleVal` | Conversely, a tuple of the right length whose valuation is typed by the reversed sorts is typed. |
| `valid_of_wellFormed` | A document accepted by the executable check has distinct layer symbols declared with their sorts and arity 1 or 2, every rule guard, carve-out and definition body typed over the prefix below its symbol, every regulated declaration placed, well-formed pairs and both DAGs accepted. |
| `precedence_acyclic` | Both the precedence DAG over rule names and the stratum DAG over defined ∪ regulated predicates of a well-formed document are acyclic. |
| `catalaValue_spec` | Catala's value exists and matches a truth value exactly when positive deciding forces it true, negative deciding forces it false, and silence forces the default. |
| `elab_iff_intended` | For any structure in which the rule formulas of `p` do not see `p`, the elaboration of `p` holds iff `IntendedAt`. |
| `elaborate_iff_at` | In a well-formed document, the elaboration of a regulated predicate holds in a structure iff the direct semantics holds for it (on every structure; admissibility is not needed). |
| `elaborate_iff` | The document's norm elaborations all hold iff `holdsCatala` holds. |
| `elab_completion` | Where no typed tuple has both opposite selections, the elaboration of `p` is equivalent to `∀x̄. p(x̄) ↔ O_p(x̄)`. |
| `applies_denote`, `yields_denote`, `selects_denote`, `decides_denote`, `outcome_denote` | Each generated formula denotes its direct-semantics counterpart. |
| `subst_sound` | For a structure admissible over `E_i` that satisfies the first `i` layer premises and closed pairs, a formula typed over `E_i` and a typed valuation, the outcome-substituted formula is true in the base restriction iff the formula is true in the structure. |
| `subst_wellFormed` | Outcome substitution turns a formula typed over `E_i` into one typed over `E_base`. |
| `prefix_satisfaction` | A structure is prefix-admissible at `i` iff it is admissible over `E_i`, its base restriction is base-admissible and it satisfies the first `i` layer premises and every pair premise closed among them. |
| `local_expands` | An admissible prefix has exactly one admissible expansion by the next layer symbol iff it passes the local test there. |
| `conflictFree_expands` | For a regulated `p` and a prefix-admissible structure below it: exactly one structure forgets to it, is admissible for `p`'s layer output and satisfies `elab_p`, iff `ConflictFreeAt p` holds. |
| `conflictFree_expands_document` | For every base-admissible structure: the document has exactly one full expansion iff the structure is conflict-free (existence alone already implies conflict-freedom). |
| `conflictFree_expands_all` | Every base-admissible structure has a unique full expansion iff every base-admissible structure is conflict-free. |
| `conflictFree_prefix` | If every base-admissible structure is conflict-free, every prefix-admissible structure below a regulated `p` passes the local test at `p` (each layer's `hc`). |
| `conflict_witness_sound`, `conflict_pair_witness_sound` | A finite base model that is valid, passes the Background check and makes a conflict formula true at a typed tuple refutes conflict-freedom there, unique expansion there and the universal document property. |
| `norms_route_acceptance` | An accepted FOL certificate for Background ++ norm elaborations ++ Γ ⊢ φ gives φ in every admissible structure satisfying the direct semantics, the definitions, the profile, literal distinctness and Γ; and, for a conflict-free document and base formulas, φ in every base-admissible structure satisfying Γ (through the composed frozen route). |
| `norms_route_countermodel` | For a conflict-free document, every base-admissible countermodel of base formulas expands to a full document expansion that is still a countermodel. |
| `norms_route_entails_iff` | For a conflict-free document and base formulas, the checked entailment over the complete environment is exactly consequence over base-admissible structures. |
| `route_backgroundSound`, `route_backgroundComplete` | On the composed norms route, Background holds in every admissible output structure satisfying the layer premises, and characterises output admissibility. |
| `conflict_smallModel`, `conflict_pair_smallModel` | In the fragment, a conflict witness in a base-admissible structure restricts to a valid finite base model passing the Background check whose every sort has at most `max 1 (constants of the sort + witness variables of the sort)` elements (empty sorts stay empty), with a typed tuple on which the conflict formula evaluates to true. The constants are given by a finite list covering every declared constant. |
| `cedar_decision` | For a deny-by-default predicate whose rules have the Cedar shape, on every structure the completed outcome is "some permit applies and no forbid applies", and the two sides never both decide. |
| `ground_conflictFree` | If every conflict formula of a document is constantly false, every base structure is conflict-free. |
| `Examples.*` | The documents of 10.1(c), (m) and (o) are well-formed (by kernel reduction); both frozen layers of (c) and of (m), and the composed routes of (c) and (o), exist as values. |
| `norms_route_intended` | The certificate half of acceptance that needs no conflict-freedom. |
| `conflictFreeCheck_sound` | If every conflict target has an accepted certificate for `Background_base ⊢ ∀x̄. ¬conflict` over the regenerated `E_base`, every base-admissible structure is conflict-free. |
| `Replay.norms_wire_conflict_sound` | A successful raw conflict-package replay whose every target certificate is accepted: the input decodes to exactly the replayed well-formed document, and every base-admissible structure is conflict-free. |
| `Replay.norms_wire_conflict_free_expands` | Then every base-admissible structure has exactly one full document expansion. |
| `Replay.norms_wire_conflict_witness_sound` | A successful raw witness replay whose regenerated target formula is true at the typed tuple of the validated base model: the input decodes to that document, and the model refutes conflict-freedom, unique expansion and the document property. |
| `Replay.target_refutes` | A valid finite base witness of any conflict target refutes the document property. |
| `Admission.admitDocument_spec` | A successful norms admission from raw JSON: the active norm objects decode to the well-formed source whose layers are regenerated; every quoted norm passes the single-rule checks; the W2 document and every graph node are decoded from the same source (each node with the source AST its claim formula decodes from); every certificate names the recomputed canonical environment id and its premise and conclusion ASTs by meaning id; the graph is sound, every node admitted (by W2 provenance, as an exact regenerated `layer:norms:<p>` leaf, or as a `background:profile` leaf equal to a regenerated pair premise) and every assumption an exact decoded leaf; citations are closed and reading choices compatible. |
| `Admission.norms_wire_report_consequence` | In every admissible structure satisfying the regenerated Background and layer premises, the report's non-layer, non-Background assumptions entail its root. |
| `Run.norms_wire_acceptance`, `Run.runAdmission_sound` | 11.4 from the public entry point: a successful norms `admission` answer is exactly `encodeAdmitted` of the checked admission for the case's id; the report id is the digest of the recomputed environment id, the complete source document and that report; and the admission and semantic facts above hold (`AdmissionAnswer`). |
| `Replay.norms_wire_acceptance` | A successful raw entailment replay with an accepted certificate (bound to the complete environment, the regenerated Background ++ layer premises, the case's premises and the conclusion): the input decodes to that document; the conclusion holds under the direct semantics; and, given conflict-freedom and base formulas, over every base-admissible structure satisfying the premises. |

The remaining theorems are helper lemmas (typing, forgetting, instantiation,
prefix positions, table lookups) audited with the same allowlist.

## Status and what is not claimed

* Proved: every section 6.2 statement, the prefix satisfaction and typed
  substitution lemmas of 6.1, the proof-gated `conflict_smallModel` of 7.2,
  `cedar_decision`, and the conflict-package, witness and entailment halves of
  the 11.4 wire theorems. `elaborate_iff_at` and `elaborate_iff` are proved
  without the admissibility hypotheses the spec lists (stronger statements);
  `conflict_smallModel` takes the environment's finite constant list `cs`.
* `conflict_complete` (enumeration completeness) is deliberately not stated.
  CONFLICT-FREE still requires a tableau certificate (binding decision 9.4); a
  Lean enumerator proved against the 7.2 bound would be the next step.
* Wire path (11.4): `ve_norms_route <cases.json|->` implements
  `norms-elaborate`, `norms-conflict` (packages or a witness),
  `norms-certificate`, and W2 FOL `admission` with active norm units and
  `layer:norms:<p>` leaves. Norm content under a kind other than `norm` or a
  quoted kind is rejected, never discarded; quoted norm content is inactive but
  passes every single-rule check (`Admission.checkQuoted`). It delegates P0 cases without norm constructs to
  `Route.Run.runCase` unchanged. `Norms.Run.norms_wire_acceptance` proves that
  a successful public admission answer is exactly the encoding of a checked
  admission whose bindings equal the recomputed digests and regenerated
  formulas, with exact admitted leaves, and whose report follows from the
  regenerated Background and layers plus its remaining assumptions. Digest
  equality is not a claim that SHA-256 is injective, and decoder faithfulness
  to the wire spec is tested, as for the P0 routes.
* W5 flags (`functional`, `total`) and adapters do not exist in this tree:
  `Background_base` is literal distinctness only, and `InFragment` needs no flag
  clause yet. 10.1(h) (the `total` regression) waits for W5.
* W3 definitions are modelled by `Definition` (the shape of `VE.Definitions.Def`
  on the W3 branch) and are proved through the same prefix machinery; W3's own
  decoder feeds them once merged.

## The `ve_norms_route` cases (for the Python harness)

Every case is `{"id", "kind", "environment", "norms", ...}` with a `ve.core@0.2`
environment including `norms@0` and Python's canonical `regulated` fields, and
`norms` the array of norm objects of 3.2. Results are
`{"id", "status": "ok", ...}` or `{"id", "status": "error", "error"}` with the
shared diagnostic text.

| Kind | Extra input | Output |
|---|---|---|
| `norms-elaborate` | none | `order`, `background` (`generator`, `ast`), `premises` (`label` `layer:norms:<p>`, `ast`), `conflict_targets` (`target` `p` or `r->m`, `sorts`, `ast`), `fragment` |
| `norms-conflict` | `packages`: target → `{"environment_id", "document_hash", "target", "certificate"}` (Python `check_conflict(prove=True)`) | `verdict` `CONFLICT-FREE` or `UNKNOWN` with `detail` `missing certificate for <t>` / `invalid certificate for <t>`; `targets` |
| `norms-conflict` | `witness`: `{"target", "model", "tuple"}` (base model, entity ids in argument order) | `verdict` `CONFLICT` or `UNKNOWN`, `target` |
| `norms-certificate` | `premises`, `conclusion`, `certificate` bound to Background ++ layer premises ++ premises | `valid`, `background`, `layers` |
| `admission` | `document` with norm units and W2 graph | `admitted`, `report`, `report_id`, `kinds` |

Ad-hoc differential runs against the Python branch (`expand/w1-norms-py` at
`e44fd27`): 9 fixed and about 1,300 generated documents (nesting, carve-outs,
multi-parent and duplicate precedence, both defaults, pairs, lower regulated
atoms and existential guards, cycles, cross-predicate precedence) gave
identical `norms-elaborate` output, including about 500 identical diagnostics,
and 1,500 deliberately malformed documents (bad names, duplicates, unknown
predicates and rules, arity, scope and sort errors, too many carve-outs) gave
identical diagnostics;
Python-proved conflict packages for four documents replay as CONFLICT-FREE and
become UNKNOWN after flipping a default, dropping a rule, dropping a package or
changing an inner binding; Python witnesses for 10.1(a) and (t) replay as
CONFLICT and the reversed (t) tuple is rejected; a Python route certificate
replays as valid and is stale after dropping a rule. These runs are not yet a
committed test (the norms conformance family and `tests/test_norms*.py` are the
Python workstream's).
