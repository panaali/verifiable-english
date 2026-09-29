# Discourse and cross-reference in Lean (`ve.discourse@1`, sequence 3)

Implements [docs/spec/discourse.md](../docs/spec/discourse.md) draft 4, section 9, in `lean/VE/Discourse/*`,
with the executable `ve_discourse_route` (`DiscourseMain.lean`, its own `[[lean_exe]]`). No frozen file changed:
`Route/*`, `Definitions/*`, `Norms/*`, `English/*`, P0 sources and `Main.lean` are untouched; `VE.lean`,
`VE/Audit.lean` and `lakefile.toml` gain imports, audit lines and the new target only, and the discourse modules
are registered in `VE/Route/frozen-sources.sha256`. Every theorem is audited (`python lean/audit.py`): no `sorry`,
no added axiom, only `propext`, `Classical.choice`, `Quot.sound`.

Tests: `tests/test_discourse_lean.py` (the route on the section 10 fixtures, one regression per review finding),
`tests/test_discourse.py` (the Python adapter) and `tests/test_discourse_three_way.py` (one shared document text
through Python, Lean and Rust: identities, report ids, statuses, diagnostics, and the Rust `elaborated-document`
verdict on the formulas Python admitted, over α and every sub-case of α′).

## Files

| File | Contents |
|---|---|
| `Manifest.lean` | 9.1 data: target kinds, forms, targets, anchors, names, content names, mentions, slots, documents, imports, groups, constraints, validity bindings, the manifest, `DDoc`; lawful `BEq` for P0 terms and formulas |
| `Loader.lean` | the `ve-document` text (front matter, source, fences, as `ve/document.py`), the front matter's checks and its translation to W2's admission object, `source_id`, `document_id`, distinguishing-model identities |
| `Access.lean` | the lexer (trust boundary), target shapes, the inputs of `Acc`, `Acc`/`accB`, `candidates`, `accessible`, `AliasEq` |
| `Grammar.lean` | the discourse sentence grammar with slot productions, `Derives`, the enumerator `derivs`, reference surfaces |
| `Elaborate.lean` | `elaborateD`, `SlotMeaning`, capture and alias congruence |
| `Resolve.lean` | `Accepted`, `validate`, `Supported`, the culprit slot of an ill-typed elaboration |
| `WellFormed.lean` | `wellFormed` (4.1 in order), `WellFormedDiscourse`, the typing judgment `TreeTyped`, `Intended`, `symbolsOf` |
| `Descriptions.lean`, `Fusion.lean`, `Joint.lean`, `Documents.lean` | 4.5, 4.6, 4.8, 4.7 logic |
| `Wire.lean` | strict decoder of the 3.1 `discourse` block, byte-to-token spans, discourse wording |
| `Admission.lean` | the profile adapter, integrity of stored documents, `admitCore`, `admitDiscourse`, `checkImport`, `statusOf` |
| `Theorems.lean` | the admission theorems of 9.3, 9.4, 9.6 |
| `English.lean` | 9.5: presentation, round trip, and the source surface's derivation obligations |
| `Run.lean` | `ve_discourse_route` (`admission`, `discourse-resolve`, `discourse-validity`, `discourse-joint`) |
| `Examples.lean` | fixture models μ, ξ, η checked by `decide` |

## The theorems, in plain words

**Accessibility and resolution (9.2).** `accessible_iff`: the executable list and the relation agree.
`acc_no_heuristic`: two documents that agree on the registrations, content names, anchors, documents,
definitions version, environment and its sorts' nouns, unit table, lemma names, innermost anchor and the texts
(tokens and bytes) inside it agree on
`Acc`. `acc_ignores_manifest_choices`: recorded targets and reading choices are not inputs of `Acc`.
`no_witness_escape`, `name_scope`, `kind_fit`, `mem_derivs` (the all-derivations gate). `validate_sound`:
whatever the validator returns is the unique accepted resolution. `validate_slots_recorded`.
`ill_typed_target`: an ill-typed recorded elaboration is `IllTypedTarget: <mention>: <target>` naming a recorded
mention of the unit (the slot whose target does not fit its position's sort); `ill_typed_target_single`: with
one recorded slot, it names exactly that slot. `accepted_no_pruning`, `validate_complete`, `accepted_unique`,
`validate_closed`, `validate_total`, `validate_budget`, `elaborateD_capture`.

**Elaboration, descriptions, fusion (9.3).** `elaborate_faithful`: on every admissible structure the validated
formula holds iff `Intended`, which sorts the derivation directly (`TreeTyped`) and never mentions the
elaboration; `elaborate_typed` shows `TreeTyped` is exactly the type check of the elaboration.
`elaborate_no_new_symbols`, `description_definedness`, `assertive_denote`, `presupposition_retained`,
`presupposition_carried`, `no_discourse_label`, `group_single_assertion`, `fused_implies_split`,
`split_not_fused_model`, `sharedWitness_spec`, `xi_models`, `eta_models`.

**Joint choices (9.4).** `compatible_sound`, `compatible_empty_error`, `compatible_budget`, `compatible_no_sets`,
`conj_nil`, `joint_no_sets`, `joint_denote`, `joint_all_iff`, `unconstrained_product`, `joint_none_sound`,
`joint_some_sound`, `independent_shortcut`, `citation_choices_retained`, `manifest_choices_are_labels`,
`citation_extends_joint`, `report_extends_joint`, `extension_rejected`, `extension_unknown` (an unfinished
enumeration is never a compatibility rejection, and the answer reports `admitted: UNKNOWN` with the
reading-dependent verdicts `readingVerdicts`).

**English (9.5).** `presentation_expands`, `discourse_parseRender`, `discourse_renderInjective` on the
presentation surface; `discourse_uniqueDerivation`, `discourse_parseSound`, `discourse_oneReading` on the source
surface (`discourseSourceSurface`).

**Documents and the wire (9.6).** `format1_unchanged`, `format1_profile_requires_format2`,
`profile_adapter_base`, `admission_projects`, `discourse_report_sound`, `validity_stripped`,
`validity_independent`, `validity_self` (with `validity_self_outcome`, `validity_self_unknown`), `validity_import`,
`outcome_unknown_of_joint`, `validity_unknown_never_checked`,
`stale_import_rejected`, `validity_never_premise`, `self_truth_never_content`, `document_sort_conservative`,
`import_acyclic`, `discourse_wire_binding`, `stale_target_rejected`, `Run.discourse_wire_acceptance`.

## What the route checks, beyond the statement's letter

- **Slots are discovered from the source** (3.4, 4.1(6)): before any unit is resolved, every unit with content or
  an active reading set (its readings are its meaning) must record every reference surface of its own bytes
  (`coverageOk`, `UnrecordedSlot: <unit>: [a, b)` in prose bytes, Python's text), and a unit whose text has a
  derivation with a slot or a surface is validated. Discovery (`textSurfaces`, Python's `reference_surfaces`) reads
  each unit alone, as its segments: maximal runs of characters with a fold (ASCII letters and digits, and `İ`, `ı`,
  `ſ`, the Kelvin sign, which `re.I` equates with ASCII letters), folded. So a reference word joined to anything
  else (`It's`, `It’s`, `They're`, `It-is`, `It_`, `Itʼs`, `İt`, `ſuch`) is still a slot, and a unit boundary with
  no space after its full stop (`reviewed.It`) still ends a word. Surfaces are taken longest first (a document
  display `It is safe` is one surface, not the pronoun inside it) and are recorded only by a formula-producing
  mention with exactly their byte range (`Mention.bytes`); overlapping or containing one is not enough. The lexer
  also reads each unit alone and folds its words, so `İt` is the pronoun `it` and `ſome` a competing quantifier,
  as in Python. Fail closed: a non-ASCII letter splits segments, so a word such as `Itália` has the surface `it`.
- **`Acc` reads the same segments** (4.2): the competing binders (`bindsSort`: a quantifier word followed later in
  the sentence by a word of the sort, its name or declared singular noun), the coordinations of an ordinal or
  plural and the restrictive properties of `such` are read from the segments of the earlier sentences of the
  innermost anchor and of the slot's sentence before it (`scopeSegments`), so `A service's owner` and
  `A service’s owner` bind a service and `Alice and Bob's manager` coordinates, in Lean as in Python. A recorded
  surface is read as the lexer's words (`surfaceOk`), and a mention's byte range
  that does not start and end on its unit's tokens is `InvalidInput: mention <m> span` in both checkers, before
  any other check of the block.
  A bound unit's content and every reading of its active set must be its elaboration
  (`ManifestMismatch: bound.<unit>`); an open set of candidate readings for an unresolved reference (2.4) is
  therefore not admitted by the route (fail closed).
- **Discourse wording** (4.1(4)): with its span, the unit of every formula-producing mention must be printable
  ASCII with canonical spacing once the layout around it is removed (`canonicalWording` in `toTokenSpans`: one
  space between words, none before `.,;:!?)`, none after `(`); otherwise `InvalidInput: discourse wording of
  <unit>`, Python's text, before any sentence is parsed. So `It is safe .`, `The\u00a0former`, a tab or newline
  inside a sentence and `İt` in a recorded unit reject alike in both checkers; Python parses the expansions
  without the surrounding layout and with the parser's spelling of each constant, never a display.
- **Group readings are regenerated** from the spans' English (`a|an|some [ADJ] SORT is P.` then `PRONOUN is Q.`)
  and compared with the recorded reading (`ManifestMismatch: groups.<set>@<version>:<reading>`); other span shapes
  fail closed. A group span carrying another reading set is `IndependentFragment`.
- **Pending presuppositions** (4.5) reach W2 without content and without their reading sets: a pending unit is
  never a premise, and a label naming its set is W2's rejection.
- **Validity bindings are regenerated** from the unit's wording (`<document name> is [not] a valid VE document.`):
  another wording is `InvalidInput`, a different document or polarity `ManifestMismatch: validity.<unit>.*`.
- **Stored documents** (4.1(10)) are document texts, embedded or supplied as sibling files: their bytes must
  re-fingerprint to the pinned `source_id`, the declaration's pins must equal the import table's, each must decode
  (text, envelope and, for `@2`, its whole discourse block, strictly, as the importing document's own block) with its
  recomputed `document_id` equal to its pin, and the chain must be
  acyclic by source id and at most four deep. A stored document is checked under its own environment and profiles.
- **Certificates are bound** explicitly (3.3): every deduction's environment id is the base pair's, and a deduction
  formalising a bound unit carries the meaning id of that unit's elaboration.
- **Recorded reading choices** (the block's `choices`) must be the lemmas' concrete labels.

## Deviations from the approved statements

Each item is a point where the implementation differs from the text of draft 4; items marked **(renewal)**
need renewed statement approval (the approved statement is false or unprovable as written).

1. **Sentences are identified by their unit.** `Derives`, `Accepted`, `Intended` and `Supported` take the unit id.
2. **Token spans.** `Mention.span` and `Slot.span` are token ranges of the unit; the decoder maps prose byte ranges
   through the lexer, reading each unit's bytes alone, and keeps the byte range (`Mention.bytes`). Diagnostics that
   print a span (`UnrecordedSlot`) print the prose byte range, the text Python prints.
3. **The discourse grammar.** `DTree.tree` is a discourse tree (`STree`), not `VE.English.Tree`; words are symbol
   names (sort noun = sort, adjective and unary noun = unary predicate, relational noun `p` for the binary `p_of`,
   verb = binary predicate), lowercased by the lexer.
4. **`acc_no_heuristic`** compares the unit table (id, span, kind) and lemma names, not unit ids only.
5. **(renewal) `ill_typed_target`.** The approved conclusion `e.startsWith ("IllTypedTarget: " ++ mentionIdAt D m)`
   for every slot `m` cannot hold for a two-slot derivation (η has `Her manager` and `Her`). Proved instead: the
   error names a recorded mention of the unit, the slot whose target does not fit its position's sort
   (`ill_typed_target`), and exactly `m` when the unit has one recorded slot (`ill_typed_target_single`). Both add
   the mention-budget hypothesis, without which `validate_budget` contradicts the statement, and state
   `startsWith p` as `∃ rest, e = p ++ rest` (the toolchain has no `String.startsWith` lemmas).
6. **(renewal) Plural candidates and `AliasEq`.** 4.2 makes every list of accessible constants a candidate of a
   distributive `they`, so `[alice, bob]` and `[bob, alice]` both type-check in θ. The route takes a plural's
   candidates from the coordinations `c₁ and c₂` of the earlier text, in their order, as for ordinal pairs (θ:
   "‘They’ with no listed constants in scope: `UnresolvedReference`"), and `AliasEq` is equality, since targets
   name constants. The earlier set-comparison of members is withdrawn.
7. **Acc refinements.** A `definition_ref` candidate is the predicate its surface word names; a `document_name`
   candidate is the document whose display its surface spells. The only in-sentence binder a slot targets is a
   definite description's own entity, `binder:0`.
8. **Readings of definites** come from the recorded mention (a fixed input).
9. **`elaborate_no_new_symbols`** states `DeclaredSymbol D.E q` (the environment has no symbol list).
10. **(renewal) The wire and fixture ι.** The route reads the 3.1 wire from the document text: reading ids decode to `original_index`, an
    import's `bytes` names a sibling file whose text the case supplies (`files`), and a target's `version` pin is
    carried as the mention's `pin`, reported, and checked (`pinOk`, in Python too): only a `definition_ref` to a
    predicate may carry one (`InvalidInput: mention <m> target` otherwise), and it must equal the regenerated
    definition version (`StaleTarget: <mention>: <target>@<version>`). No environment the admission accepts declares
    a W3 definition version (W2 defers definitions; `definitionVersion` is `none`), so every pin is stale and fixture
    ι's pinned reference is `StaleTarget: m1: eligible@2` where the fixture (10) expects CHECKED at version 2, rather
    than admitted with an unchecked pin; an unpinned `definition_ref` resolves (CHECKED). Beyond 3.1 the
    block may carry `validity`, `self_truth` and `choices` (the Manifest fields of 9.1); Python does not evaluate
    them and relays this route's verdicts on them (the Lean authority below).
11. **The loader.** JSON `null` (which the restricted parser does not read), fenced English or strict content, norm
    content, `MIXED` units and a document without a claim graph (W2 admission needs one; Python loads such a
    document without admitting it) are `NotImplemented: <feature>`. A `@2` input is the document text; a W2 admission
    object with a `format` field is the unchanged `@1` path.
12. **(renewal) Outcomes, `validity_self` and `validity_import`.** `outcomeOf` also treats `NotImplemented` as
    `unknown` (a check the route cannot complete is never a rejection), and a successful admission whose joint set hit
    the budget (`admitted: UNKNOWN`, 4.1(8)) as `unknown` (`outcome_unknown_of_joint`): "ResourceLimit (any)" of 4.7.
    The same holds for `self`: this document's outcome is `unknown` when its own joint set hit the budget, so the
    approved `validity_self` (always `checked`/`refuted`) is proved under `jointUnknown res.joint = none`, and
    `validity_self_unknown` gives `unconfirmed` otherwise. The approved `validity_import` checks an import under the
    *importing* document's profiles (`checkImport profiles b fuel`); an import is checked under its own environment
    and profiles instead (`checkImport files b fuel`, through `outcomeWith`), which the spec needs to adopt.
13. **(renewal) `validity_independent`.** The approved equation over `stripValidityJson j` is false: fixture υ makes
    a malformed binding (a self-truth wording bound as a validity claim) `InvalidInput`, a rejection the stripped
    document does not have. The admission therefore keeps the bindings out of the admitted document (`res.claims`,
    `res.doc.K.validity = []`) and reads them only in the second phase; proved: `validity_stripped` (the W2 result
    is `admitCore`'s on the validity-free document) and `validity_independent` (two admissions with the same
    admitted document and front matter have the same W2 result). Theorems about validity claims range over
    `res.claims`. A JSON-level statement also needs `Json`/`RBNode` lemmas the toolchain lacks.
14. **`discourse_wire_binding`.** The manifest is the decoded block mapped to token spans with its validity bindings
    kept apart (`res.doc.K = {K with validity := []}`, `res.claims = K.validity`); `boundMeaningId` is the meaning id
    of a bound unit's elaboration under the base pair; the wrapper identity is `wrapperReportId`.
15. **`stale_target_rejected`** drops the unused hypotheses on the retargeted mention: the conclusion follows from the
    distinct meaning ids alone. `acceptedCertificates res u` are the certificates of deductions formalising `u`.
16. **`manifest_choices_are_labels`** and **`extension_rejected`** are stated over W2 lemmas (`Admission.Lemma`; the
    Lean W2 document carries no W3 bundle); `choicesAsLabels` keeps a lemma's `v:all` and replaces a concrete label
    by the recorded choice. `extension_rejected` spells the statement's `w3Passes` out: every stage before the gate
    passed and every earlier lemma extends.
17. **(renewal) 9.5.** On the approved surface `parse` reads the presentation (core English) while a derivation
    yields the source (discourse English), so `ParseSound` and `OneReading` fail there. `discourse_parseRender`
    and `discourse_renderInjective` are stated on the presentation surface; `discourse_uniqueDerivation`,
    `discourse_parseSound` and `discourse_oneReading` on the source surface, whose derivations are the
    type-checking competitors of an admitted unit (`Accepted`'s uniqueness clause).
18. **Statuses.** A pending unit is OPEN (no `PENDING`, 13.12); units keep the loader's W2 status (OPEN,
    UNFORMALISED, LABELLED); a group span has its owning set's status, so an open set's group is OPEN (μ).
19. **The admission result** also carries the front matter, the original profiles, the environment id, the inner
    report id, the bound meaning ids, the reference lines and the validity bindings; `DDoc` also carries the active
    reading sets, the loader's statuses, the source and the sibling files. `Admitted.projected` is the projected W2
    object; `admission_projects`, `stale_import_rejected` and `format1_profile_requires_format2` take
    `formatOf j = some "ve-document@…"` instead of the top-level `format` field (the input is a loaded text, whose
    format is in its front matter; `stale_import_rejected` also takes that the input is a loaded text).
20. **(renewal) Authored sets in the composition gate (4.8).** The joint set ranges over the active open sets only,
    so the approved `citation_extends_joint`/`report_extends_joint` (`∃ c ∈ cs, ExtendsTo ch c`) cannot hold for a
    label naming an authored set, which `@1` admits (the gate would turn a W2-accepted label into
    `InvalidCompatibility`). The gate reads each compatible choice with the active authored sets fixed at their one
    signed reading (`gateChoices`, `authoredChoice`), and both theorems conclude `ExtendsTo ch (c ++ authoredChoice
    res.doc)`; with no authored set this is the approved statement. Python's `check_joint_extensions` is the same.
21. **Checks not implemented in `wellFormed`:** 4.1(9) (the definition/proof dependency DAG; the Lean W2 document has
    no citation graph); `exports` is checked as "a `definition` unit lies inside the anchor".

## Renewal requests

The (renewal) items above cannot be closed by the implementation: each approved statement is false as written,
and the reviewers' own findings require the behaviour that falsifies it. They are ready for the spec reviewers as a
mechanical approval. `test_renewal_items_are_counterexamples_to_the_approved_statements` (and the named tests)
exhibit, on route outputs, the approved statement's hypotheses holding with its conclusion failing; the replacement
is the proved Lean statement.

| Item | Approved (draft 4) | Counterexample on the route | Replacement to approve |
|---|---|---|---|
| 5 | `ill_typed_target`, 9.2: the error starts with `IllTypedTarget: <m>` for **every** slot `m` | η with `Her` → `api`: both slots recorded and accessible, one diagnostic `IllTypedTarget: m1: api` (R1) | `ill_typed_target` (a recorded mention of the unit, the misfitting slot) and `ill_typed_target_single` |
| 6 | 4.2: every list of accessible constants is a `plural` candidate | θ: `[alice, bob]` and `[bob, alice]` both type-check, so "They are ready." is ambiguous, contradicting the fixture's expected resolution | 4.2 amended: candidates are the earlier coordinations, in order (as ordinal pairs); `AliasEq` is equality |
| 10 | fixture ι (10): m1 → `predicate eligible` version 2, `∀x:service (eligible(x) → reviewed(x))` CHECKED | `sec2` exports `eligible`, its definition unit lies in `sec2`, m1 pins 2, and the result is `StaleTarget: m1: eligible@2`: no environment W2 admits declares a definition version (`definitionVersion` is `none`), so no pin can be confirmed (R7) | ι amended: a pinned `definition_ref` is `StaleTarget` until W3 definition versions reach the admitted environment; the CHECKED case is the unpinned reference |
| 12 | `validity_import`, 9.6: an import is checked under the importing document's profiles | a valid `@1` import is `UnsupportedProfile` under the importer's `ve.discourse@1` profiles, refuting a true claim (R2) | `validity_import` over `checkImport files b fuel` / `outcomeWith` (the import's own environment and profiles) |
| 12 | `validity_self`, 9.6: always `checked`/`refuted` | an admission answering `admitted: UNKNOWN` would certify its own validity (R3, `test_unknown_admission_is_an_unknown_outcome`) | `validity_self` under `jointUnknown res.joint = none`, `validity_self_unknown`, `outcome_unknown_of_joint` |
| 13 | `validity_independent`, 9.6: the W2 result equals the one of `stripValidityJson j` | υ: a self-truth wording bound as a validity claim is `InvalidInput`; the stripped document is admitted (R4) | `validity_stripped` and the relational `validity_independent` |
| 17 | 9.5 `ParseSound`/`OneReading` on `discourseSurface` | "It is safe." is derived (→ `safe(api)`) but the core parser rejects it: it reads presentations (R5) | the 9.5 theorems on the presentation and source surfaces as listed in item 17 |
| 20 | `citation_extends_joint`/`report_extends_joint`, 9.4: `∃ c ∈ cs, ExtendsTo ch c` | an authored singleton's label with no open set: `cs = [[]]`, which extends no label, yet `@1` and W2 admit it (R6, `test_authored_reading_labels_extend`) | both theorems with `ExtendsTo ch (c ++ authoredChoice res.doc)` |

## Not done

- **Unverifiable readings fail closed:** an open set of candidate readings for an unresolved reference (2.4) and a
  pinned `definition_ref` (no environment declares definition versions; renewal item 10) are rejected, not admitted.
- **Fixtures not covered by tests:** parts of κ (renumbering, `DependencyCycle`), λ lemma-level citations over W3
  bundles, χ quotation, ψ W1 rule references, ω corpus, the proved-carrier case of η (it needs a certificate), and
  the 1,000-manifest Python/Lean differential. `discourse-joint` reports the joint set and the disjunction, not
  ALL/NONE/SOME verdicts.
- **The Lean authority** (`manage-agents/discourse-authority-directive.md`, spec 3.4): Python's admission of a
  `ve-document@2` document is this route's `admission` answer on the same bytes (`ve/discourse.py`
  `lean_admission`, `validate_discourse`), with the sibling files its imports name: the verdict, every unit's
  status, the references, the validity verdicts and the report id. Python's own check (`python_discourse`), which
  elaborates pronouns, demonstratives and ordinal pairs only and evaluates no validity claim, self-truth label or
  recorded choice, gives editor hints (`discourse_hints`, the reviewed presentations) and the diagnostic text of a
  document this route rejects too. A route that is missing, fails or answers anything but one well-formed answer to
  the case is `CheckerUnavailable`; `NotImplemented` is Python's `UnsupportedProfile`; neither is a verdict.
