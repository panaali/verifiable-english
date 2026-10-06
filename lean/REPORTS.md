# `reports@0` in Lean (attribution plan item 2)

Statement spec: [docs/spec/attribution.md](../docs/spec/attribution.md), draft 10, section 9; plan:
[docs/spec/attribution-PLAN.md](../docs/spec/attribution-PLAN.md), revision 9. Sources are in
`lean/VE/Attribution/` (the work item's directory; the spec proposes `lean/VE/Reports/`), namespace `VE.Reports`,
so every theorem has the spec's name. The executable is `lean/.lake/build/bin/ve_reports_route`, root
`ReportsMain.lean`, its own Lake target. Frozen `Route/*`, `Norms/*`, `Definitions/*`, P0 sources and `Main.lean`
are untouched (`python3 lean/VE/Route/frozen.py` passes); `VE/Audit.lean` and `lakefile.toml` gain imports, audit
lines and the target only. No theorem uses anything beyond `propext`, `Classical.choice` and `Quot.sound`
(`python3 lean/audit.py`).

| File | Contents |
|---|---|
| `Content.lean` | 9.1: acts, judgments, contexts, assessment records, `Content`, keys, units, paths, `ReportDoc`, canonical objects (`CJson`), ids, `document_id`, keys and generated names, `envReports`, `elab`, `premises`, `neqs`, paths (`contentAt`, `envAt`, `holderAt`, …), `payloadFormulas`, the reports gate and `reports_gate_sound`, `WellFormedReports` |
| `Semantics.lean` | 4.2/4.3: `Source`, `Sat`, `IntendedReports`, `interp`, `restrictJ`, `AgreeOn`, `Expandable`, `reportsRoute`, `checkedList`, `beliefsIn` |
| `Facts.lean` | the conjuncts of `WellFormedReports`; keys, names, `keyOf`, `E_reports` predicates; the four shapes of a top-level premise |
| `Elaborate.lean` | 9.2 vocabulary theorems, `no_collision(_complement)`, faithfulness in both directions, correspondence, finite witness decoding |
| `Conservative.lean` | `neqs`, model existence, expansion, conservativity, `reports_no_leak` |
| `Structure.lean` | the 4.5 structure theorems, nested contents, identity theorems, truth combinations |
| `Route.lean`, `Scoped.lean`, `Assess.lean`, `Bridge.lean` | 9.3 |
| `Wire.lean`, `Admission.lean`, `Run.lean` | the decoder, W2 admission under the profile, the executable |

## Theorems, in plain words

Every theorem is stated for `VE.Structure.{u}` at every universe `u`; `h : WellFormedReports D = true` is a
hypothesis of all but the parser and gate facts.

Vocabulary (1.5, 3.4, 4.1).
- `envReports_extends`: every formula over `E` is one over `E_reports`.
- `names_fresh`: generated names are undeclared in `E`, at most 64 bytes, pairwise distinct.
- `names_injective_on_keys`: two keys of `D` with one name are one key (report and assessment keys alike).
- `hide_envReports`: hiding the generated names from `E_reports` gives back `E`.
- `premises_wellFormed`, `premises_signed`: every report premise is a well-formed signed generated atom over
  `E_reports`.
- `premises_all`: one premise per top-level unit (`elab` is total on statements).
- `keys_finite`: report and assessment keys together are at most the number of content nodes.
- `content_depth_bounded`: every unit's content depth is at most 16.
- `no_collision`, `no_collision_complement`: for two objects the document digests (occurring nodes; complements
  of occurring report nodes), one digest means one canonical object. Nothing is claimed of an object the document
  does not digest, and no theorem asserts SHA-256 injectivity.

Faithfulness and correspondence (4.3).
- `reports_elaboration_faithful`: the interpretation of an admissible source model is admissible over
  `E_reports`, and it satisfies the report premises exactly when the document's intended meaning holds.
- `reports_elaboration_faithful_out`: an admissible `E_reports` structure satisfies the report premises exactly
  when its restriction satisfies the intended meaning.
- `restrict_interp`: restricting the interpretation gives back the source model on every key (`AgreeOn`).
- `interp_restrict`: interpreting the restriction gives back every relation (and `interp_restrict_eq`, the whole
  structure).
- `old_formula_invariant`: old-language formulas keep their truth value across `interp`.
- `restrictJ_admissible`: the restriction is admissible over `E`.
- `finite_witness_decodes`: a valid finite model over `E_reports` is the interpretation of a source model.

Model existence, expansion, conservativity (4.4).
- `positive_uniform`, `uniform_neqs`, `positive_expandable`: a positive document forces no disequality, so every
  structure is `Expandable`.
- `neqs_wellFormed`: the forced disequalities are old-language formulas.
- `source_over_any_structure(_iff)`: an admissible old-language structure underlies a source model of `D` exactly
  when it satisfies the forced disequalities.
- `unreported_key_free`: … and then with any key that no top-level unit asserts or denies empty.
- `expansion_exists(_iff)`: the same, as existence (not uniqueness) of an admissible `E_reports` expansion
  satisfying the report premises.
- `reports_old_language_conservative`: over old-language premises and conclusion, consequence at `E_reports` is
  consequence at `E`.
- `reports_no_leak`, `reports_no_leak_uniform`: adding well-formed signed generated atoms changes old-language
  consequence by exactly the disequalities they force (by nothing when their polarity is uniform).

Structure (4.5).
- `attitude_not_factive`: a report of a formula content false in an `Expandable` structure has a source model
  over that structure in which the content is false.
- `no_closure_under_consequence`: beliefs in `P` and `P → Q` leave the belief-in-`Q` key free when no top-level
  unit asserts or denies it.
- `nested_independent`: a nested belief with an unreported key is free, and its formula content can be false.
- `nested_positive_entailed`, `nested_positive_refuted`, `nested_negated_entailed`, `nested_negated_refuted`: a
  top-level unit carrying the nested node (or its negation) entails (or refutes) its holder-applied atom.
- `holder_atom_free`: the atom of a key at a holder is free when no positive premise carries it at a co-denoting
  holder.
- `negation_scopes_distinct`, `probably_not_scopes_distinct`, `literal_paraphrase_distinct`: distinct canonical
  objects; distinct digests and names when both compared objects occur.
- `tense_keys_distinct`: keys in contexts of different tenses have different names.
- `content_structural`: formula contents have one canonical object exactly when their normal forms are equal;
  when both occur, the same for their ids.
- `all_truth_combinations`, `all_truth_combinations_assess`: any truth assignment to unasserted keys, uniformly
  on the key's sort.

Route, scoped checks, assessments, bridges, wire (9.3).
- `reports_route_acceptance`: an accepted certificate over `literals ++ Γ_reports ++ Γ` at `E_reports` proves the
  conclusion there, over string-admissible structures, over those whose restriction meets the intended meaning,
  and over every source model's interpretation.
- `reports_route_acceptance_base(_positive)`: for old-language `Γ` and `φ`, the same certificate proves `φ` at `E`
  from the literals, the forced disequalities and `Γ` (from the literals and `Γ` alone for a positive document or
  when `Γ` already entails the disequalities).
- `reports_route_countermodel`: a checked finite countermodel over `E_reports` refutes the route statement and
  decodes to a source model in which `Γ` holds and the conclusion fails.
- `scoped_consequence_sound`, `scoped_witness_sound`: a scoped check's certificate (model) proves (refutes) the
  conclusion at the payloads' own environment under its own Background.
- `scoped_not_premise`: dropping every scoped check changes neither `Γ_reports` nor `E_reports`.
- `scoped_background_local`: a quoted package's definition premises are in the checked list only if the author
  wrote them into `Γ`.
- `quoted_inconsistency_local`: an inconsistent payload set has no model under its Background, while the outer
  document keeps every source model.
- `assessment_open_term`: an assessment unit's generated name is an open term on the evidence sort, with a record
  whose decider is present.
- `assessment_not_factive`, `may_probably_independent`: as the attitude case; `may` and `probably` have different
  names and independent truth values on unasserted keys.
- `bridge_root_is_legacy`, `bridge_root_parse_frozen`, `bridge_nested_label_new`: root bridge labels are the
  frozen parser's and are admitted exactly by W2's `QuotedUnit` on the W2 view; the nested label is parsed only
  where the frozen parser rejects.
- `bridge_formula_exact`, `bridge_kind_rejected`, `bridge_nested_needs_record`, `bridge_assessment_any_agent`,
  `bridge_payload_not_belief`, `bridge_through_negation`: an admitted bridge assumes exactly the elaborated formula
  at its path over `E`; norm and definition nodes and nodes under a pinned environment are never targets; nested
  targets need a record; assessment targets accept any agent; the payload bridge assumes the payload, not the
  belief; a root path passes through a negation.
- `reports_gate_sound`: a list the gate accepts is, minus `reports@0`, one the frozen classifier classifies as
  FOL, and has no `norms@0`, `definitions@0` or `data@0`.
- `reports_admission_sound`, `reports_labels_decoded`: an admitted document is well-formed and decoded from the
  input, its envelope is recomputed, every node of the input graph that carries a certificate carries exactly that
  envelope (3.4's outer binding: a graph node with a `certificate` has an `envelope` field
  `{"environment_id", "document_id"}`, removed before the frozen W2 node decoder reads the node), and its report is a `SoundReport` at `E_reports` whose assumptions are
  decoded leaves admitted by `ReportsLeafAdmitted`, with closed citations and compatible choices.
- `Run.scopedCertified_sound`: a scoped certificate (FOLLOWS, or PAYLOADS INCONSISTENT with `⊥`) counts only
  with both bindings of 3.4: its envelope is the recomputed one and it replays under the inner binding at the
  check's pinned scope. A `reports-scoped` case's `certificates` and `inconsistency` are bound by the case's
  `envelope`; a certificate a scoped check carries in the document is bound by that check's own `envelope` field
  (not part of `document_id`; an envelope without a certificate is `InvalidInput`). A check whose only
  certificates are unbound is UNKNOWN with detail `envelope`; one whose bound certificate does not replay is
  UNKNOWN with detail `certificate does not replay`; one with no evidence at all, `no evidence`.
- `foldStatus_le`, `foldStatus_checked`, `unitStatus_le`, `documentStatus_le` (`Status.lean`, section 6): one
  status order, UNFORMALISED, OPEN and UNKNOWN below LABELLED below CHECKED (the three lowest ranked in that
  order), and one meet. A unit's status is the meet of its meaning's (`meaningStatus`, W2's inference) and every
  result nested in it: each assessment node at any depth OPEN, each act outside the slice at any depth of its
  kind LABELLED, each `unformalised` node at any depth of its kind UNFORMALISED with its reason
  (`Run.nestedResults`); a document's is the meet of its units' and every scoped check's replayed
  status (`verdictStatus`: FOLLOWS, DOES NOT FOLLOW and PAYLOADS INCONSISTENT are decided, anything else
  UNKNOWN). The document's is at most every unit's, every nested result's and every verdict's, and CHECKED only
  when every folded result is. `ve/reports.py` (`fold_status`, `unit_status`, `statuses`) computes the same, and
  `check_document` compares it with the `reports-status` case, then reports the meet as the document's status
  once the premise-set line has a model.
- `Run.reports_wire_acceptance`: a successful `admission` answer is exactly the encoding of such an admission of
  the case's own environment and document.
- `Run.decodeReportsModel_valid`, `Run.reports_countermodel_decoded`, `Run.runCountermodel_sound`: the model
  vocabulary the executable regenerates has exactly the constants and predicate signatures of `E_reports`
  (`reportsModel_constants`, `reportsModel_predicates`), so a model it decodes is `Mo.Valid (envReports D)` and
  meets the literals, and a `reports-countermodel` answer's `refutes` is the check of such a model, which then
  refutes the route statement and decodes to a source model (`reports_route_countermodel`).

## Conventions and deviations from the spec's Lean blocks

- **Canonical objects** are values of `CJson` (JSON with formula ASTs and W1 rule nodes as leaves, arrays and
  objects as cons chains, derived decidable equality), not Lean `Json`: the collision check must decide equality
  of objects, and Lean's `Json` objects are red-black trees with no lawful equality. `CJson.toJson` gives the JSON
  that is hashed with the frozen canonical serialiser. Optional absent fields are absent keys (never `null`).
- **`canonical`** (P5) is the identity on ASTs: ASTs are de Bruijn terms and P5 normalisation only renames binders
  and prints.
- **Pinned environments**: `Content.norm` and `Content.definition` take a `Pinned` record (decoded environment, its
  `environment_id`, the Background of its own route, its profile list), which coerces to `VE.Environment`, in
  place of a bare `VE.Environment`: `object(norm)` and `object(definition)` need `E_q`'s id, and `background Eq`
  of a definitions package needs its definitions, neither of which a `VE.Environment` holds. So
  `payloadFormulas` returns a `Pinned`, `background` takes one, and `scoped_background_local` binds
  `(Eq : Pinned)`.
- **`ReportDoc`** gains `profiles` and `environmentId` (the identity domain and `environment_id(E)`, inputs of
  every formula's canonical object and of `document_id`) and `w2` (the rest of the W2 document: its other units,
  lemmas, open terms, reading sets and narrowings). `w2Doc D` is `D.w2` plus the report units with their 3.3
  kinds and root-complement formulas, and the generated open terms. `WellFormedReports` additionally requires
  unit ids unique across both parts and no content on the rest's quoted units, so that
  `bridge_root_is_legacy` holds on the whole W2 view.
- **`WellFormedReports`** checks, besides 4.1, the facts about generated names that 4.1 step 7 calls validity of
  `E_reports` (fresh in `E`, at most 64 bytes, pairwise distinct, and with the author's predicates at most
  `MAX_PREDICATES`, for which `ReportDoc` carries `authorPredicates`), that every declared literal is a constant of
  sort `$string`, that bridge and scoped ids are distinct (section 8's `DuplicateDeclaration`), and every unit's W2
  metadata (`metaOk`): W2's support values, open meanings naming declared or generated open terms, and a report
  unit `specified` exactly when its tree has no assessment node, otherwise `open` listing every generated
  assessment name of its tree (3.3).
- **`ReportDoc.unitMeta`** holds every unit's span, meaning and support in document order, and `document_id`
  hashes it (`"metadata"`), so a changed span, meaning or support changes the envelope.
- `elab` and `scoped` are Lean keywords: the definition and the field are `«elab»` and `«scoped»`.
- `envReports_extends` annotates `∀ a : VE.Formula` (the binder's type is not inferable).
- `finite_witness_decodes` concludes `interp D M = Mo.asStructure`: the spec's relation-wise conclusion compares
  relations over `(interp D M).Carrier` and `α`, which are not definitionally equal for an existential `M`; the
  structure equality gives it by transport.
- `holder_atom_free` concludes over `M.S.constant hd`: the spec's `S₀.constant hd = some v` does not typecheck
  against `M.J … v` for an existential `M` (it is the same constant, `M.S = S₀`).
- `reports_admission_sound` states the envelope as `VE.Route.Wire.environmentId profiles environment = .ok
  res.envelope.1 ∧ res.envelope.2 = documentId res.D` (the spec compares an `Except` with a string and names a
  `VE.Route.Wire.canonicalEnvironmentJson` that does not exist; the reports family has no regulated predicates to
  canonicalise, so the raw environment is hashed, as P0 does), adds that the document is the one the raw input
  decodes to, and uses `VE.Graph.ClaimGraph VE.Tableau.Certificate` for the spec's `VE.Graph.Graph`.
- `Run.ReportsAdmissionAnswer` is the encoding of an `admissionReports` result for the case's environment and
  document, with the envelope and report id recomputed; `reports_admission_sound` supplies the rest.
- A bridge record may name a root target (3.2); the spec's Lean comment `target.depth ≥ 1` is not enforced.
- Section 6's `unreviewed_acts` ("units whose act is outside the slice, by act") counts every attributed node
  whose act is outside the slice, at any depth of a unit's kind (under attributed, hedged and causal wrappers),
  and `reports-elaborate` warns once per node, with its kind path when it is not the root. The Python residual
  also lists the open terms by name (declared, then generated), so each assessment node, at any depth, is named
  in it; their count is W2's `open_terms` line, unchanged.
- An `unformalised` node nested in a unit's kind (under attributed, hedged or causal wrappers) leaves that part of
  the unit unformalised whatever its meaning and content (6's MIXED row, in one unit), so it is an UNFORMALISED
  nested result, not a rejection: W2 admits such kinds. A root unformalised kind requires an unformalised meaning
  with the same reason (`InvalidInput` otherwise). The residual gains a line beside 6's, `unformalised_kinds` (every
  unformalised node of a unit's kind at any depth, root included, by reason), and the coverage's
  `unformalised_reasons` counts each nested one's reason beside each unformalised meaning's (a matching root kind
  and meaning count once). A plain W2 document applies the same root reason agreement rule.

## Spec defects found

- 10.1's `E₀` declares a sort `service` and a constant `service`; P0's vocabulary decoder rejects the pair
  (`duplicate declaration`). The fixtures rename the sort `system`.
- 3.1's constants `the_article` and `e1` have no `description`, which P0's decoder requires.
- 3.2's `"reference_time": null`, 3.3's `"literal": null` and 3.3's `"content": null` are rejected by the frozen
  restricted JSON parser; the Lean wire omits absent keys.
- The ill-typed statements listed above (`finite_witness_decodes`, `holder_atom_free`, the envelope conjunct).
- The Lean `Bridge` comment (`target.depth ≥ 1`) contradicts 3.2 (a root target may have a record).

## The executable

`ve_reports_route <cases.json|->` with case kinds `reports-elaborate`, `reports-certificate`,
`reports-countermodel`, `reports-scoped`, `reports-status` and `admission` (documented at the top of `Run.lean`); P0 cases without
a reports construct delegate unchanged to `VE.Route.Run.runCase`. `tests/test_reports_lean.py` runs 22 fixtures of
10.2/10.3 (α to ω, a selection, and B₁₃, B₁₄); the Python prover is used only as an untrusted certificate search,
every certificate is replayed by Lean.

## Not done

- The Python production layer (`ve/reports.py`) and the English (`ve/report_english.py`) exist and are compared
  with this route by `tests/test_reports_lean.py` (elaborations) and `tests/test_reports_agreement.py` (what is
  admitted, with section 8's diagnostic kind); the reports parse-uniqueness theorem (`reports_parse_unique`) is
  item 4's and is not stated here. Rust is an untrusted witness search only.
- `{"fence": …}` content is rejected; reading-set choices are not part of canonical objects.
- The local W1 conflict check of a quoted norm block (fixture κ's "CONFLICT among the quoted rules") is not run:
  the block is only validated by the frozen W1 decoder.
- `reports-scoped` replays witness models only over the author's `E`; a witness for a quoted package's scope is
  reported UNKNOWN (certificates are replayed at either scope).
- Admission reports section 8's `BridgeHolder` and `MissingBridgeRecord` diagnostics before the generic graph
  rejection. `reports-status` supplies the nested statuses, section 6 residual lines and section 7.2 report,
  assessment, scoped and bridge display lines. The P0 premise-set line is produced after the separate premise
  check. Coverage requests statuses without replay; a carried bound certificate remains UNKNOWN with detail
  `not replayed` until the checked document call asks Lean to replay it.
- Fixtures not exercised: κ, ν (parser part), ξ, ρ, υ, χ, ψ (a, c) and most of B₁ to B₁₆.
