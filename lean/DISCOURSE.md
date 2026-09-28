# Discourse and cross-reference in Lean (`ve.discourse@1`, sequence 3)

Implements [docs/spec/discourse.md](../docs/spec/discourse.md) draft 4, section 9, in `lean/VE/Discourse/*`,
with the executable `ve_discourse_route` (`DiscourseMain.lean`, its own `[[lean_exe]]`). No frozen file changed:
`Route/*`, `Definitions/*`, `Norms/*`, `English/*`, P0 sources and `Main.lean` are untouched; `VE.lean`,
`VE/Audit.lean` and `lakefile.toml` gain imports, audit lines and the new target only. Every theorem is audited
(`python lean/audit.py`): no `sorry`, no added axiom, only `propext`, `Classical.choice`, `Quot.sound`.
Fixture tests: `tests/test_discourse_lean.py` (24 tests over fixtures α to φ).

## Files

| File | Contents |
|---|---|
| `Manifest.lean` | 9.1 data: target kinds, forms, targets, anchors, names, content names, mentions, slots, documents, imports, groups, constraints, validity bindings, the manifest, `DDoc`; lawful `BEq` for P0 terms and formulas |
| `Access.lean` | the lexer (trust boundary), target shapes, the inputs of `Acc`, `Acc`/`accB`, `candidates`, `accessible`, `AliasEq` |
| `Grammar.lean` | the discourse sentence grammar with slot productions, `Derives`, the enumerator `derivs` |
| `Elaborate.lean` | `elaborateD`, `SlotMeaning`, capture and alias congruence |
| `Resolve.lean` | `Accepted`, `validate`, `Supported` |
| `WellFormed.lean` | `wellFormed` (4.1 in order), `WellFormedDiscourse`, `Intended`, `symbolsOf` |
| `Descriptions.lean`, `Fusion.lean`, `Joint.lean`, `Documents.lean` | 4.5, 4.6, 4.8, 4.7 logic |
| `Wire.lean` | strict decoder of the `discourse` block, byte-to-token spans, identities |
| `Admission.lean` | the profile adapter, `admitDiscourse`, `checkImport`, `statusOf` |
| `Theorems.lean` | the admission theorems of 9.3, 9.4, 9.6 |
| `English.lean` | 9.5: presentation and round trip |
| `Run.lean` | `ve_discourse_route` (`admission`, `discourse-resolve`, `discourse-validity`, `discourse-joint`) |
| `Examples.lean` | fixture models μ, ξ, η checked by `decide` |

## The theorems, in plain words

**Accessibility and resolution (9.2).** `accessible_iff`: the executable list and the relation agree.
`acc_no_heuristic`: two documents that agree on the registrations, content names, anchors, documents,
definitions version, environment, unit table, lemma names, innermost anchor and the texts inside it agree on
`Acc`. `acc_ignores_manifest_choices`: recorded targets and reading choices are not inputs of `Acc`.
`no_witness_escape`: a binder target is accessible only where the binder scopes. `name_scope`: a registered
constant is accessible to a pronoun or demonstrative exactly at the units of its scope with no competing binder of
its sort. `kind_fit`: kinds never coerce. `mem_derivs`: the enumerator lists exactly the derivations of a sentence
(the all-derivations gate). `validate_sound` (`validate_accepted`): whatever the validator returns is the unique
accepted resolution. `validate_slots_recorded`: the recorded mentions are exactly the accepted derivation's slots.
`ill_typed_target`: an ill-typed recorded target is `IllTypedTarget`. `accepted_no_pruning`: every type-checking
competitor elaborates to the accepted formula. `validate_complete`: on a well-formed document, within budget,
every accepted formula is what the validator returns. `accepted_unique`, `validate_closed`, `validate_total`,
`validate_budget`. `elaborateD_capture`: the elaborated formula denotes exactly the slot-by-slot meaning.

**Elaboration, descriptions, fusion (9.3).** `elaborate_faithful`: on every admissible structure the validated
formula holds iff the intended meaning does. `elaborate_no_new_symbols`: it is well formed over `E` and uses
only declared symbols. `description_definedness`, `assertive_denote`, `presupposition_retained`.
`presupposition_carried`: in an admitted document every presuppositional mention's `U(D)` is a certified
unit-less `asserted` deduction node, an explicit asserted premise unit, or the mention is pending with
`PresuppositionUnresolved` and its unit unbound. `no_discourse_label`: every report assumption carries a W2 label.
`group_single_assertion`: a group's reading is its owning set's reading, at most one leaf carries the set, no
asserted leaf names a span, and every span has no content, no bound formula, is no premise and shares the group's
status. `fused_implies_split`, `split_not_fused_model`, `sharedWitness_spec`; `xi_models`, `eta_models`.

**Joint choices (9.4).** `compatible_sound`, `compatible_empty_error`, `compatible_budget`,
`compatible_no_sets`, `conj_nil`, `joint_no_sets`, `joint_denote`, `joint_all_iff`, `unconstrained_product`,
`joint_none_sound`, `joint_some_sound`, `independent_shortcut`, `citation_choices_retained`.
`citation_extends_joint`, `report_extends_joint`: each lemma's and the report's choices extend to a validated
compatible choice. `extension_unknown`: an unfinished enumeration is never a compatibility rejection and leaves
reading-dependent verdicts UNKNOWN.

**English (9.5).** `presentation_expands`: the reviewed presentation parses, through the unchanged core parser,
to exactly the elaborated formula. `discourse_parseRender`, `discourse_renderInjective`.

**Documents and the wire (9.6).** `format1_unchanged`, `format1_profile_requires_format2`,
`profile_adapter_base`, `admission_projects`, `discourse_report_sound`, `validity_self`, `validity_import`,
`validity_unknown_never_checked`, `stale_import_rejected`, `validity_never_premise`, `self_truth_never_content`,
`document_sort_conservative`, `import_acyclic` (the stored import chain passes the shared `dependencyOrder` and is within depth 4), `Run.discourse_wire_acceptance`.

## Modelling choices and deviations from the statements

1. **Sentences are identified by their unit.** `Derives`, `Accepted`, `Intended` and `Supported` take the unit id:
   a slot names its unit, and a bare token list is ambiguous when two units share a text.
2. **Token spans.** `Mention.span` and `Slot.span` are token ranges of the unit in Lean; the decoder maps prose
   byte ranges through the lexer. Diagnostics that print a span (`UnrecordedSlot`) print the token range.
3. **The discourse grammar.** `DTree.tree` is a discourse tree (`STree`), not `VE.English.Tree`: the core grammar
   has neither slot productions nor the natural wordings of 2.1 ("every X is P", "X is P"). The supported fragment
   is listed in `Grammar.lean`; words are symbol names (sort noun = sort, adjective and unary noun = unary predicate,
   relational noun `p` for the binary `p_of`, verb = binary predicate), lowercased by the lexer.
4. **`acc_no_heuristic`** compares the unit table (id, span, kind) and lemma names (`hb`), not unit ids only:
   `within` needs spans, `rule` targets need kinds, `claim` targets need lemma names.
5. **`ill_typed_target`** adds the mention-budget hypothesis (otherwise `validate_budget` contradicts it) and
   concludes `∃ rest, validate D u = .error ("IllTypedTarget: " ++ rest)`: the statement's per-slot
   `startsWith (… ++ mentionIdAt D m)` cannot hold for every slot of a two-slot derivation.
6. **`AliasEq`.** Targets name constants, so an alias never changes a target; a distributive plural's members are
   compared in registration order. This resolves the latent θ ordering ambiguity (both `[alice, bob]` and
   `[bob, alice]` type-check and would otherwise be `AmbiguousReference`); it needs the reviewers' confirmation.
7. **Acc refinements.** A `definition_ref` candidate is the predicate its surface word names (among the named
   anchor's exports); a `document_name` candidate is the document whose display its surface spells (otherwise π
   is ambiguous between the two documents). The only in-sentence binder a slot targets is a definite
   description's own entity, `binder:0`.
8. **Readings of definites** come from the recorded mention (a fixed input); a definite slot with no recorded
   mention has no elaboration.
9. **`elaborate_no_new_symbols`** states `DeclaredSymbol D.E q` (the environment has no symbol list).
10. **Wire.** A group's and a constraint's readings are `original_index` numbers; an import's stored document is the
    inline `content` (the JSON text of `{"environment", "document"}`); `source_id` is
    `sha256("ve-source-v0.2\n" + prose)`; predicate-target version pins are not carried into Lean targets (W3
    definition versions are not in the Lean W2 document); imports are checked under the importing profile list.
11. **`Admitted.projected`** holds the projected W2 document; `admission_projects` states the W2 admission of
    `res.projected` and `documentId2 … = .ok res.documentId`.
12. **The composition gate** runs over W2 lemmas (`Admission.Lemma`, leaves as label and formula): the Lean W2
    document carries no W3 bundle lemmas. `citation_extends_joint` is stated over `L ∈ res.base.doc.lemmas`.
13. **`extension_unknown`** uses `¬ CompatibilityDiagnostic e.2` (`∃ x, e.2 = "InvalidCompatibility" ++ x`)
    instead of `startsWith`; **`stale_import_rejected`** adds the `@2` format hypothesis (a `@1` document is
    delegated by `format1_unchanged`, so the two statements conflict otherwise) and names the error as
    `"StaleTarget: " ++ x`; **`group_single_assertion`** uses `unitOfLeaf res.base`.
14. **Carriers.** Pending units are decided on the submitted graph before projection (they get no content in W2);
    the reported carriers, pending lines and bound formulas are computed from the admitted W2 result. The two
    agree by construction of the decoders; that agreement is not a theorem.
15. **Checks not implemented in `wellFormed`:** 4.1(9) (definition/proof dependency DAG; W3's, unchanged, and the
    Lean W2 document has no citation graph); an embedded document's pinned `document_id`; `exports` is checked
    as "a `definition` unit lies inside the anchor" (the Lean W2 document does not link units to predicates).
    Import cycles are detected along the stored-bytes chain by source id within depth 4.

## Not done

- **Theorems:** `validity_independent` (it needs lemmas about rewriting a JSON object, which the toolchain's
  `RBNode` lacks without Batteries), `stale_target_rejected` and `discourse_wire_binding` (certificate envelopes
  across two admissions), `manifest_choices_are_labels`,
  `extension_rejected`.
- **9.5 `discourse_uniqueDerivation`, `discourse_parseSound`, `discourse_oneReading`:** not stated. On the 9.5
  surface `parse` reads the presentation (core English) while a derivation yields the source text (discourse
  English), so a parse result is in general not the reading of a derivation of that same text. Uniqueness of the
  accepted derivation is `accepted_unique` and `Accepted`'s own clause. This is a spec point to raise.
- **Fixtures not covered by tests:** parts of κ (renumbering, `DependencyCycle`), λ lemma-level citations (W3
  bundles), σ embedded documents, χ quotation, ψ W1 rule references, ω corpus, the proved-carrier case of η (it
  needs a certificate), and the Python/Lean differential over generated manifests (sequence 2 has no Python
  validator yet). `discourse-joint` reports the joint set and the disjunction, not ALL/NONE/SOME verdicts.
