# Content-bearing reading candidates in Lean (`lean/VE/Readings/*`, composition stage S1)

Specification: [docs/spec/composition-s1.md](../docs/spec/composition-s1.md) section 8 (the theorem statements),
through the pointer plan [docs/spec/composition-S1-PLAN.md](../docs/spec/composition-S1-PLAN.md). This file lists
every definition the statement review reads and every theorem in plain words. All statements quantify universally
over their displayed parameters. `lean/audit.py` audits every theorem: no `sorry`, only `propext`,
`Classical.choice` and `Quot.sound`. No frozen source changed: `lean/VE/{Norms,SoftNorms,Rights,Route,Discourse,
Compose}/*` and every P0 source are untouched (`python3 VE/Route/frozen.py` passes; the new modules are listed in
`VE/Route/frozen-sources.sha256`). `VE.lean` and `VE/Audit.lean` gained imports and audit entries only, and
`lakefile.toml` gained the `ve_readings_route` target (root `ReadingsMain.lean`, also in `defaultTargets`). The
audit allowlist is unchanged. The namespace is `VE.Readings` (`lean/VE/Route/Readings.lean` is `VE.Route`).

## Files

| File | Contents |
|---|---|
| `Doc.lean` | 8.2 verbatim: `Chain`, `chainOf`, `Candidate`, `ReadingSet`, `Item`, `Coupling`, `Narrowing`, `Doc`, `candidate`; the names a content uses (`uses`), `declaredBy`, `interfaceOf`, the relation `Attached` and its computation `attached` (a table per fixed unit, one level per step, stopping at a fixed point, fuel `D.items.length`); `place`, `build`, `free`, `one`; `chainWF`, `sideWF`, `reservedFree`, `distinctAcrossSets`, `interfaceClosed`, `singlyAttached`, `WellFormedDoc` |
| `Layers.lean` | Lean-first plan F5d, imported only by the readings route: the expansion table built once (`expEntries`, `expAt`), a document's layers (`Layers`, `layersOf`, `substIn`), the conflict formulas and targets from them (`conflictIn`, `outcomeBaseIn`, `pairConflictIn`, `targetsIn`), and the soft and rights validations with the layers computed once (`selectsOn`, `defaultDecidesOn`, `softPremisesIn`, `checkSoftOnce`, `softSemanticCheckOnce`, `validateSoftOnce`, `validateRightsOnce`); each is declared in the namespace of the function it replaces |
| `Separate.lean` | 8.3: `GenKey`, `genKeys`, `owned`, `ownedKeys`; `Tables`, `withTables`, `expand`, `Probe`, `selectable`, `Observes`, `authorEnv`, `Achieves`, `Separated`; the executable check (`Situation`, `tablesModel`, `tablesTyped`, `probeTyped`, `observe`, `sideValid`, `sideValue`, `cells`, `assignments`, `tablesFor`, `tablesOf`, `situationWF`, `separates`), each on a candidate's document a caller built once (`ownedKeysOf`, `sideValidOf`, `sideValueOf`, `cellsOf`, `assignmentsOf`, `tablesForOf`, `situationWFOf`, `twinDocsOf`, `decisionOnlyOf`, `actOnlyOf`; the form on `D s i` applies it to `one D s i`); `probesOf`, `observeAll`; a candidate's side computed once from its document (`Side`, `sideOfDoc`, `sideOf`, `tablesModelOn`, `tablesTypedOn`, `keyTuplesOn`, `cellsOn`, `assignmentsOn`, `backgroundValidOn`, `observeOn`, `sideValidOn`, `sideValueOn`; F5d); `strictOf`, `strictTwin`, `forceTwins`, `relaxTo`, `twinDocs`, `decisionOnly`, `AchievesQuiet`, `actOnly` |
| `Force.lean` | `decision_only_sound` and its three parts: `relaxDoc`, `Twin` and the force lemma for a whole document; `canon_relax`; the premises and probe values over one base; `TwinDocs`, `tablesRel`, `quiet_iff` |
| `Lines.lean` | DRI ruling 1: `linesOnce`, the admission text `lineOrderText` (4.4), `checkRights` in named steps (equal by `rfl`) and the facts read from it, and `genKeys_nodup` |
| `Wire.lean` | 8.4: the environment on the three chains, the document's units and active reading sets, contents, keys, tables, probes and situations; the checks of 4.1 with section 7's texts (`admissionText`, stopping at the first); the request's table of every candidate's document (`onesOf`, read by `oneOf`, `Admitted.side`); admission as specified (`admitReadingsSpec`) and as run (`admitReadings`: `candidateStage` builds each candidate's document once, validates it and keeps it in the table, stopping at the first diagnostic); a side's chain checks as specified (`chainTextSpec`) and as run (`chainText`, the layers computed once); `SeparateReplay`, `replaySeparate`, `readings_wire_separate_sound` |
| `Run.lean` | The `ve_service` mode `readings-route` (`runCaseReported`; the one-shot `ve_readings_route` and its root `../ReadingsMain.lean` were deleted in lean-first batch 1); a candidate's row, a pair's facts, a set's pairs and a set's findings as specified (`candidateJsonSpec`, `pairFactsSpec`, `setPairsSpec`, `setFindingsSpec`) and as run, every document read from the request's table, each candidate's side built from it once per set (`sideIn`, `sidesOf`, `sideAt`) and the other side scanned lazily (`pairFactsIn`, `setPairs`) |
| `Scan.lean` | The other side of a pair scanned lazily (`scanOthers`, `otherScanOn`) and a pair's facts in a monad that can count the other side's evaluations (`pairEval`) |
| `RunExamples.lean` | Build-time `#guard` counts of `pairEval`'s evaluations of the other side (batches 3b and 3d review B): one admissibility and one value on a 12-cell query, not 4,096; and which candidates' documents admission builds into the request's table (K15) |
| `Examples.lean` | Build-time `#guard` regressions on fixtures K1 to K22 of 9.2, K2b's inadmissible base as two theorems, and the two counterexamples to `genKeys_nodup` without its hypothesis (`twiceListed`, `orderOnly`) |

## Theorems

### `Doc.lean`

* `attached_iff`: the computed `attached D u` lists exactly the sets `Attached D u` relates `u` to. The proof
  reads both as walks through fixed units; a walk that repeats a unit can be cut (`pathTo_cut`), so a shortest
  walk has distinct units and at most `D.items.length` steps (`pathTo_nodup`, `attachedF_iff`); the table of each
  level holds the walks of that length (`mem_attachedLevels`), and stopping at a fixed point changes nothing
  (`attachedIter_eq`).
* `distinctAcrossSets_spec`: the Boolean check holds exactly when no name a candidate declares is declared by a
  fixed unit, a bar or a candidate of another set, and no two items declare one name.
* `interfaceClosed_spec`: the check holds exactly when every name a fixed unit uses that a set declares is an
  interface name of that set.
* `singlyAttached_spec`: the check holds exactly when no fixed unit is attached to two different sets.
* `correlate_noRights`: without rights content, the rights elaboration is the soft document and `Lim_D` is empty.
* `chain_soft`: on every chain, a well-formed side's elaboration is a well-formed soft document.
* `chain_norms_value`: on the norms chain the value is W1's (`soften_faithful` with `soften_hard_identity`).
* `one_formula_only`: when every candidate is an assertion, no fixed unit is attached and every candidate's
  document is the fixed document.
* Helpers: `mem_sets`, `mem_fixedUnits`, `mem_usesOfUnit`, `mem_directSets`, `mem_nextUnits`,
  `mem_fixedNames_of_uses`, `attachedF_path`, `pathTo_suffix`, `pathTo_cut`, `exists_dup_split`, `pathTo_head`,
  `pathTo_nodup`, `pathTo_fixed`, `attached_path_iff`, `attachedF_iff`, `usesOfUnit_nil`, `attachedF_nil`,
  `mem_attachedLevels`, `attachedIter_eq`, `build_eq`, `buildStep_set_fst`, `build_fst_assertions`,
  `not_attached_of_formula_only`.

### `Separate.lean`

* `genKeys_names`: the generated names and sorts of `genKeys X`, in order, are the soft decisions of `correlate X`
  followed by the rights-generated predicates.
* `observe_sound`: on a side valid over its elaborated base vocabulary that passes the background check, and a
  typed probe, the finite evaluation `observe` gives `some v` exactly when the probe has value `v` in the expansion
  (`conflict_canon`, `outcome_canon`, `circ_canon`, `selectsPrime_denote`).
* `separates_sound`: on a well-formed document, two candidates with content and a base valid over the author's
  vocabulary, `separates = true` proves that the witness achieves the recorded value on the shown base and shared
  tables and the other candidate does not. The witness's finite model is its completion name by name
  (`tablesModel_rel`); the base is valid over the side's elaborated base vocabulary because every layer symbol of a
  candidate's elaborated document is hidden in the author's vocabulary (`layerNames_hidden`, via
  `dependencyOrder_ok` on the frame's stratum graph, a subgraph of the elaborated one); and any completion of the
  other side with the recorded value is, restricted to the typed tuples admissibility forces, one of the enumerated
  `assignments` (`separates_other`).
* `separates_separated`: a checked separation proves `Separated`.
* `separation_conservative`: when neither candidate owns a key and the shared tables pass step 1, some probe of
  `probesOf` separates the pair in some direction exactly when the two observation lists differ.
* `force_agrees_off_exception`: a default rule alone in a document and its strict twin give the same value at
  every tuple where the rule's exception does not hold.
* `decisionOnly_spec`: when `decisionOnly` answers a key, the two candidates are force twins with the strict one
  first, the key is the default twin's exception, its sufficient conditions are empty, and every rule of the
  default reading's document on the twin's act is the twin.
* Helpers: `keyedNodes_nodes`, `typedTuple_iff`, `mem_tuplesOf`, `selectable_mem`, `catalaValue_eq`,
  `buildStep_soft`, `build_soft`, `keepsFrame_build`, `keepsFrame_one`, `names_nodup_of_order`, `lookupSym_name`,
  `nodeNames_stratum`, `lookupSym_some`, `layer_sub`, `layerNames_hidden`, `tableOf_cons`, `tableOf_nil`,
  `mem_tableOf`, `mem_tableOf_iff`, `tableOf_filter`, `tableOf_append_of_not`, `tableOf_none`,
  `tablesFor_generated`, `find_name`, `keyOfName_of_find`, `tablesModel_eq`, `observes_rel`, `genKeys_find_none`,
  `envAt_author`, `envAt_constants`, `typedTuple_domains`, `tupleTyped_tablesModel`, `valid_tablesModel`,
  `mem_uniq`, `filter_mem_subsets`, `mem_assignments_foldr`, `tableOf_map_keys`, `tableOf_append_right_not`,
  `withTables_domain`, `tupleTyped_withTables`, `backgroundValidR_of_admissible`, `probeTyped_congr`,
  `sideWF_one`, `tablesModel_rel`, `separates_witness`, `separates_other`, `probesOf_typed`, `cells_nil`,
  `assignments_nil`, `separates_noKeys`, `strictTwin_nodes`, `switch_false`, `strictDecides_alone`, `eff_alone`,
  `applies_alone`, `yields_alone`, `decides_alone`.

### `Lines.lean` (DRI ruling 1)

* `genKeys_nodup`: on a document that passes its chain's checks and whose line order lists each line of each right
  once (`linesOnce`), no two generated base predicates have one source key.
* `linesOnce_of_text`, `lineOrderText_go`: the admission check of 4.4 (`lineOrderText`, `UnknownRight: <r>` or
  `InvalidInput: line order lists a line of right <r> twice`) passes only on a document `linesOnce` accepts.
* `checkRights_steps`: `checkRights` restated in named steps, equal to it by `rfl`; `rightsNames_of_check`,
  `rightsNames_of_chainWF` read from it that rule names, limitation names, each limitation's condition names and each
  line's fan-out bearer sorts are distinct (`stepsHead_dup`, `stepsPreds_rights`, `stepsRights_lines`,
  `stepsLines_limits`, `stepsLimits_conds`, `limBody_ok`, `checkSourceLine_fan`).
* `keyedNodes_pairwise`: no two rules of the elaboration carry one source rule name and bearer
  (`keyedNodes_bearerless`, `linesAux_pairwise`, `instancesOf_fan`, `instancesOf_bearers`, `distinct_lines`).
* List lemmas: `nodup_flatMap_iff`, `pairwise_of_ne`, `sortBy_perm`, `insertBy_perm`, `dedup_nodup`, and others.

### `Wire.lean`

* `readings_wire_separate_sound`: a decoded `readings-separate` replay for which `separates` answers true proves
  the conclusion of `separates_sound` for the decoded document, pair and situation.
* `author_valid`: a base decoded over the author's base model vocabulary is valid over `authorEnv`.
* `layerNames_sub`: every layer symbol is a regulated or a defined predicate.
* `admitReadings_eq` (lean-first plan F5b): admission as run equals admission as specified. `admissionText` already
  validates `free D` and every candidate's `one D s i` (`chainText`); once it finds nothing, `WellFormedDoc` is
  `frameWF` (`wellFormedDoc_of_admissionText`, from `sideWF_of_chainText`), so admission evaluates `frameWF` instead
  of validating each document a second time. Admission as run checks the candidates with content (`activeOf`) in
  `candidateStage`, which builds each of their documents once and keeps it: its answer is the first candidate
  diagnostic or the table `onesOf D` (`stageOf_eq`, `candidateStage_eq`, `candidateStage_ok`,
  `admissionText_of_stage`). A pending candidate has no diagnostic (`candidateText`), so leaving it out leaves the
  first one (`firstSome_filter`, `firstSome_activeOf`) and its document is never built (batch 3b looprecheck B).
* `oneOf_eq`, `onesOf_holds`, `onesOf_active` (F5b): the table answers `one D s i` for every pair, holds every
  candidate with content of every set and no pending one, so `oneOf` builds a document itself only for a pending
  candidate, which only a `readings-separate` request naming it reaches, once, before refusing it.
  `Admitted.side_eq`: an admitted document's table is that table. `tests/test_readings_lean_sharing.py` walks the compiled route from `main` and finds no other path
  to `one`.

### `Run.lean` and `Scan.lean`

* `candidateJson_eq` (F5b): a candidate's row reads its document from the request's table, once, for its keys and its
  findings. `setFindings_eq`: a set's findings read the table, for pairs of candidates with content only; a pair with
  a pending candidate has neither finding (`pairFindings_pending`), so its sides are not read.
* `pairEval_id` (`Scan.lean`; F5b, F5d, batches 3b and 3d review B): with each candidate's own side and the other
  side's cells within `maxCells`, `pairEval` in `Id` is `separates` and the specified fields. Each document is read
  from its side (`tablesForOf_sideOf`, `situationWFOf_sideOf`), so none is built there. The witness's completion is
  evaluated once; the other side's completions go through `scanOthers`, each one's admissibility evaluated only when
  the scan reaches it and its value only when needed (`scanOthers_eq`, `otherScanOn_id`, `and_not_and_any`;
  `assignments_of_ownedKeys_nil` for `other_value`). `RunExamples.lean` counts those evaluations at build time: one
  admissibility and one value on a 12-cell query (4,096 completions) that its first completion decides.
* `pairFactsIn_eq` (F5d): with `side i = sideOf a.D s i` for every `i`, a pair's facts read from the sides equal
  `pairFactsSpec`. `replayPair_doc`: a replay is of the admitted document and the requested set.
* `sideIn_eq`, `sideAt_sidesOf` (F5b, F5d): a candidate's side built from the request's table (`sideIn`, the merge
  of batches 3b and 3d) is `sideOf a.D s i`, and so is the per-set cache `sidesOf` (each side a `Thunk`, built when
  first read) at every `i`. `setPairs_eq`: a set's pairs read from the cache equal `setPairsSpec`, where each pair
  builds both sides' layers. Batch 3b's `pairFacts` (the documents from the table, each formula's layers rebuilt)
  is replaced by `pairFactsIn`, which reads both.

### `Layers.lean` (lean-first plan F5d)

`expTable T i` answers a lookup by recomputing the layer order (a topological sort of the stratum DAG) at each of
the `i` levels, and `envAt` and `size` recompute it too; a validation of a UDHR candidate computed it a few hundred
times, and a pair's two conflict formulas once per level. Each function here computes it once per document and is
equal to the function it replaces:

* `expAt_expEntries`: the table of the first `i` layer symbols read from `expEntries T` (one entry per symbol,
  newest first, each symbol's base formula a `Thunk` built when first read under the entries before it) is
  `expTable T i`; from `entryTable_take` (by induction on `i`), `expStep_foldl_drop` and `expStep_foldl_length`.
  `subst_expAt` and `substIn_eq`: `subst` read from the entries.
* `layersOf_syms`, `layersOf_names`, `layersOf_entries` (`rfl`): the layers of a document are its layer symbols,
  their names and `expEntries`.
* `conflictIn_eq`, `outcomeBaseIn_eq`, `pairConflictIn_eq`, `targetsIn_eq`: the conflict formulas and the
  conflict targets from a document's layers are `conflict`, `outcomeBase`, `pairConflict` and `targets`.
* `selectsOn_soften` (`rfl`), `softPremisesIn_eq`: `selects′` and the soft premises with `soften D` and its layers
  given.
* `checkSoftOnce_eq`, `softSemanticCheckOnce_eq`, `validateSoftOnce_eq`, `validateRightsOnce_eq`: the soft and
  rights validations with the layers computed once are `checkSoft`, `softSemanticCheck`, `validateSoft` and
  `validateRights`.

In `Separate.lean`: `ownedKeysOn_sideOf`, `cellsOn_sideOf`, `assignmentsOn_sideOf`, `tablesModelOn_sideOf` (`rfl`),
`sideValidOn_sideOf` and `sideValueOn_sideOf`: a candidate's completions read from `sideOf D s i` are `ownedKeys`,
`cells`, `assignments`, `tablesModel`, `sideValid` and `sideValue`. In `Wire.lean`: `chainText_eq`, a side's chain checks as run (each
validation by its `Once` function, the complete environment for the assertions computed once) equal
`chainTextSpec`; `sideWF_of_chainText` now reads `chainTextSpec` through it.

### `Force.lean`

* `decision_only_sound` (8.3, the approved statement): when `decisionOnly D s i j` answers `k₀`, on every base `B`,
  shared tables `F`, probe `q` and value `v`, candidate `i` achieves `v` exactly when candidate `j` achieves it with
  the table of `k₀` empty. `decisionOnly` answers only when `twinDocs` holds (`Separate.lean`): the two contents
  declare the same names, the twin's rule among them; the readings assert the same formulas and generate the same
  rights vocabulary and `Lim_D`; the default reading's elaborated rules are the strict reading's through `relaxTo`
  (the twin's name relaxed to the default twin's mode, exception and `hard`), and every rule with the twin's name
  is strict there; the generated keys differ by `k₀` only, and `k₀` is the one key named by the twin's exception
  predicate; the selectable rules correspond through `relaxTo`; and no definition takes the exception predicate's
  name. K1, K5 and K19 keep their finding and K6 and K14 stay without one (`Examples.lean`).
* The proof has four parts.
  * Force: `Twin C Nd` holds when the rules named like the twin are strict and on its predicate, the relaxed
    document is valid and the twin is the only rule on its act there. Then wherever the twin's exception
    predicate is false the document and `relaxDoc C Nd` decide every predicate alike (`Twin.decides`) and select
    alike (`Twin.selects`): no other rule's blocking, dominance or exceptions read the twin, and the relaxed twin
    is neither blocked nor dominated (`Twin.blocked_twin`, `Twin.dom_twin`).
  * Expansion: over one base on which the exception predicate is false in the relaxed expansion, every formula
    of the strict document has one truth in both canonical expansions (`canon_relax`), and so do decides, values
    and selection (`decides_canon`, `value_canon`, `selects_canon`).
  * One base: the two documents have the same colliding pairs, outweighs triples and base vocabulary off the
    exception predicate (`Twin.collidingPairs_eq`, `Twin.decisions_find`, `Twin.envAt_zero`); the relaxed
    document adds only exception premises with empty sufficient conditions, which hold where the predicate is
    empty (`Twin.excPremises`); so on such a base the two are admissible together (`Twin.baseAdmissiblePrime`)
    and every probe has one value (`observes_twin`). The exception predicate is no layer symbol of the relaxed
    elaboration (`Twin.excepted_out`), so the expansion keeps it empty (`Twin.excepted_canon`).
  * Assembly: `TwinDocs` reads `twinDocs` as propositions (`twinDocs_spec`, `decisionOnly_twin`). The default
    reading's elaborated document is `relaxDoc` of the strict one's (`TwinDocs.correlate_eq`), and its selectable
    rules are the strict one's through `relaxTo` (`TwinDocs.selectable_eq`). A base admissible over the author's
    vocabulary has no tuple on the exception predicate (`TwinDocs.excepted_empty`, by `envAt_author` and the
    freshness of decision names). On such a base a completion of the strict reading is the completion of the
    default one whose `k₀` table is empty and whose other tables are the same (`TwinDocs.tablesRel_eq`); both
    readings own the same keys and `k₀` is owned (`TwinDocs.owned_eq`, `TwinDocs.owned_excepted`). `quiet_iff`
    exchanges the two completions over abstract documents.
* Helpers: `relaxTo_name`, `relaxTo_pred`, `relaxTo_sign`, `relaxTo_over`, `relaxTo_alterable`, `relaxTo_of_ne`,
  `relaxTo_of_eq`, `mem_relaxDoc`, `relax_mem`, `fuel_relax`, `eq_of_key`, `dualPerm_act`, `dualOblig_act`,
  `act_of_incompatible`, `force_incompatible_self`, the remaining `Twin.*` lemmas, `relax_children`, `syms_mem`,
  `layerNames_mem`, `flatMap_congr_mem`, `filterMap_congr_mem`, `find_filter_of`, `find_filter_mem`, `sat_append`,
  `atom_false`, `Twin.outweighsTriples_eq`, `offDecisions_relax`, `Twin.exceptedDecisions_filter`,
  `Twin.baseAdmissible`, `Twin.cohPremises`, `excepted_mem`, `eq_relaxDoc`, `TwinDocs.find_strict`,
  `TwinDocs.find_excepted`, `TwinDocs.twin`, `TwinDocs.core`, `tablesRel`, `withTables_rel`, `withTables_none`,
  `observes_withTables`.

### `Examples.lean`

* `k2b_not_admissible`, `k2b_achieves_neither`: K2b's base, with a tuple on the default reading's generated
  exception predicate, is not admissible over the author's vocabulary, so neither candidate achieves anything on it.

## Statements of 8.3: status

* `genKeys_nodup` as first approved was false (`WellFormedRights` accepts a line order that lists one default
  fan-out line twice, `Examples.lean` `twiceListed`, or a line its right lacks, `orderOnly`). DRI ruling 1 of
  2026-10-02 adds the hypothesis `linesOnce X = true`, and the corrected statement is proved in `Lines.lean`.
* `decision_only_sound` is proved in `Force.lean` with the approved statement. The finding's wire text and English
  are unchanged: `readings-validate` still writes `SeparatedByDecisionOnly: <set>: <i>, <j> (not certified)` and
  shows E25, as DRI ruling 2 of 2026-10-02 set them while the theorem was open. Replacing them with the certified
  form (E15) is a change to the wire contract, the Python side and the specification, and is not made here.

## The wire (`ve_readings_route`)

A case is `{"id", "kind", "environment", "document", ...}`; `readings@1` must be in the environment's profiles and
`dispatch` must name the head `readings`. The document is `{"units": [{"id", "kind"?, "content"?}], "reading_sets":
[...]}`. A unit's `content` is a formula, a unit content of the chain (`{"norm", "cites"?}`, `{"right"}`,
`{"right_lines"}`, `{"limitation"}`, `{"bar"}`), or absent (the restricted JSON input has no `null`); a unit with
content carries its W2 `kind` (a string, or an array for a composite kind), and its content is in force only under
that kind (`Wire.inForce`: a formula under `asserted`, a norm under `norm`, a rights block under a rights kind or
`norm`). Reading sets are W2's with S1's `situations`; a reading's absent `content` is pending, and so is a formula
candidate of another kind than `asserted`. The active version of each unit is
the latest. A situation entry is `{"base", "fixed", "witness", "decisions", "probe", "value"}` (section 3), its
base over the author's base model vocabulary with lowercase entity identifiers (`complete` may be omitted), and its
id is `digest("ve-situation-<identity version>\n", {"environment_id", "situation"})`.

* `readings-validate` answers `content_bearing: false` for a document with no content-bearing set; otherwise
  `sets`, per content-bearing set in source order: `candidates` (per candidate `id`, `index`, `pending`, and for a
  candidate with content the chain's `document_hash` of `one D s i`, its `owned` and `shared` keys with their
  generated `name`s, its chain `findings` with ` under <set>@<v>:<i>`), `pairs` (per ordered pair, neither pending,
  the recorded situation and its facts; a situation whose witness is not one of the pair's two readings is
  `InvalidInput: invalid situation <id>`) and the `findings` of 4.6 (the decision-only finding marked
  ` (not certified)`). A failing check is the first diagnostic of 4.1.
* `readings-separate` takes `set`, `situation` and `other` and answers `pair`: `separated`, `witness`,
  `witness_admissible`, `witness_value`, `other_admissible`, and `other_value` when the other reading owns no key.
* Every other kind is run by the lower route's runner with `readings@1` stripped.

Not decoded by S1's case kinds: couplings and narrowings (4.7; their checks are rights 3.3's and Python's), and W2's
own structural validation of the sets, which Python performs first. S2a's case kinds decode couplings and
narrowings (below).

# Superposed readings in Lean (composition stage S2a)

Specification: [docs/spec/composition-s2.md](../docs/spec/composition-s2.md) section 8, draft 5 with the DRI rulings
of 2026-10-03 and findings 4 to 6 (change log). `lean/audit.py` passes with no `sorry` and only `propext`,
`Classical.choice` and `Quot.sound`. S1 definitions changed by S2a: by DRI ruling 2, `chainWF` on the soft chain
gains `namesFit` (`Doc.lean`), and `Wire.chainText` reports `ResourceLimit: decision predicate <name>` first; by DRI
ruling 4, `Wire.decodeEnvironment` decodes the frame of a `norm-defaults@0` environment with each `unspecified`
completion read as the placeholder `deny` (`placeholderFrame`, E‴'s reading), so that content beside the profile
reaches S1's abstention and a document without content is W2's, instead of a decoder text that is false of the
document. No S1 theorem statement changed. Frozen sources are untouched (`python3 VE/Route/frozen.py` passes; the new modules are
listed in `VE/Route/frozen-sources.sha256`).

## Files

| File | Contents |
|---|---|
| `Choice.lean` | 8.3: choices (`search_spec`, `choices_spec`, `exists_compatible_of_choices`, `no_compatible_of_choices`; the checked choices `checkedChoices` and `choicesSoftChecked` of DRI ruling 5), the choice vocabulary (`bitsOf`, `bitName`, `bitDecls`, `pattern`, `choiceAtom`), `choiceFresh`, `itemUnit`, `unitsDistinct`, `supReady`, `sup`, owners and `Choice_D`, `slotP`, `slotUnder`, `superposable`, `nameMap`, `pull`, `Encodes`, `ChoiceExtension`, `sharedEnv` |
| `Superpose.lean` | `sup_wellFormed`, `encodes_atoms`, `encodes_unique`, `dead_sound`, `unsat_sound`, the bit and pattern facts |
| `ChoiceFacts`, `Children`, `Live`, `Names`, `Shape`, `SoftFacts`, `Simulate`, `Faithful` | the image map `fmap`, its fields and children, liveness through the name map, and `superpose_faithful` by a simulation |
| `SupSlot.lean`, `Strings.lean` | `sup_no_sets`; string lemmas on ASCII prefixes |
| `Labels.lean` | `slot_wellLabelled` |
| `SupEnv.lean` | the vocabulary of `sup D`; `slot_wellFormed` |
| `Asserted.lean`, `Assertions.lean` | `asserted_shared` (finding 4), `superpose_assertions` (finding 5) |
| `ChoiceValid.lean`, `ChoiceTyped.lean` | `choice_valid`: W1 reads a compatible choice's softened document as `Valid` (precedence and stratum orders, typing) |
| `Situation.lean` | `canon_meaning`; Lemma K (`pull_canon`): the expansion of `sup D`, pulled, is the expansion of the choice's document over the pulled base; `superpose_situation` |
| `SupConflict.lean` | `superpose_conflict_iff` |
| `BaseDown.lean` | `base_down` (with `checkSoftRule_exception`, the typing of exception conditions read off the rule check) |
| `SupWitness.lean` | `superpose_conflict_witness`, `superpose_countermodel` |
| `BaseUp.lean`, `UpPremises.lean`, `UpSlot.lean` | the lifted base `upB` and `base_up` (finding 6) |
| `SupFree.lean` | `superpose_conflict_free` |
| `SupAll.lean` | `superpose_all`, `superpose_all_base` |
| `ChoiceWF.lean` | `choice_sideWF_of_soft`; `choice_wellFormed` with the route's soft check of every choice as its hypothesis (DRI ruling 5) |
| `Route.lean` | the route of 1.1, `supCertificateCheck`, `supModelCheck`, the refusals of 4.1 steps 3 and 5 (`routeRefusal`, `unsatText`, `superposedCheckText`, `enumeratedCheckText`), the regenerated elaboration (`elaborateFields`) |
| `SupWire.lean` | 8.5's structures and decoders: couplings and narrowings (W2's texts), `admitS2`, `replaySup`, `decodeChoice`, `supVocabulary`, `decodeSupModel`, `replayCertificate`, `replayModel` |
| `SupWireSound.lean` | `readings_wire_all_sound`, `readings_wire_model_sound`, `readings_wire_satisfiable`, `readings_wire_assumed_taken`, `readings_wire_choice_wellFormed` |
| `SupRun.lean` | the case kinds of section 3 (`Run.lean` dispatches to them) |
| `Examples.lean` | `#guard`s and theorems on M1, M16, M19 (KH, KB), M20; `MU` (two narrowings keeping no choice, review A1) and `MB` (past `maxChoiceChecks`) |

## The statements of 8.4 and 8.5

Proved as stated (draft 5): `sup_no_sets`, `sup_wellFormed`, `asserted_shared` (with `hr`, finding 4),
`slot_wellFormed`, `slot_wellLabelled`, `encodes_unique`, `encodes_atoms`, `superpose_faithful`, `base_down`,
`superpose_situation`, `base_up` (as corrected by finding 6), `superpose_conflict_iff`, `superpose_conflict_free`,
`superpose_conflict_witness`, `superpose_all`, `superpose_all_base`, `superpose_countermodel`, `dead_sound`,
`unsat_sound`, `superpose_assertions` (with `ChoiceExtension` of finding 5), `readings_wire_all_sound`,
`readings_wire_model_sound`; and, added by the review of 2026-10-03, `readings_wire_satisfiable` (a replayed
superposed case has a compatible choice), `readings_wire_assumed_taken` (its named readings are taken by one) and
`readings_wire_choice_wellFormed`. `base_down`, `base_up`, `superpose_conflict_free` and `superpose_assertions` use
`choiceFresh` (DRI ruling 1) through `hs` or `hr`; `Examples.lean` keeps the M19 counterexamples without it.

`choice_wellFormed` is proved with one more hypothesis, by DRI ruling 5: `(hw : choicesSoftChecked D = true)`, the
route's runtime check that every compatible choice's soft document passes the soft check (`WellFormedSoft`, up to
`maxChoiceChecks` = 1024 choices; past them the check is false and the superposed case kinds refuse with
`ResourceLimit: more than 1024 readings to check`). `choice_sideWF_of_soft` derives every other conjunct of `sideWF`,
and `choice_valid` the part every other theorem uses (W1 validity of the softened document). The unconditional
statement, the soft check's size limits on the generated formulas derived from `sup D`'s, is not claimed; it is a
follow-up item. `SupReplay.checked` carries the check, so `readings_wire_choice_wellFormed` concludes `sideWF` for
every compatible choice of a replayed case.

Findings (pending the DRI's confirmation; change log of the spec):

* 4: `asserted_shared` is false without distinct set and unit ids (M20); `supReady` gains `unitsDistinct`, and the
  theorem gains `(hr : supReady D = true)`.
* 5: `superpose_assertions` is false when `ChoiceExtension` may reinterpret every `ve__bit__` name; it reinterprets
  exactly `bitDecls D`'s names.
* 6: `base_up` was ill-typed (an existential `B` with an arbitrary carrier in `(pull D c B).relation p vs ↔
  B₀.relation p vs`); the extension is stated as `{ B₀ with relation := R, domain := dom, constant := k }`.

## The wire (S2a case kinds)

Every case is `{"id", "kind", "environment", "document", ...}` as for S1; the document may carry `couplings` and
`narrowings` in W2's shape (`{"id", "axis", "sets": [{"set", "version"}], "by", "reason_spans"}`,
`{"id", "set", "version", "keeps", "by", "reason_spans"}`), decoded with W2's checks and texts after S1's admission;
a unit id used twice is `InvalidInput: duplicate or invalid unit id`. A choice is `[[set, index], ...]`. A model is
the finite-model wire form (`{"complete", "domains", "constants", "relations"}`, every predicate listed when
`complete`) over `sup D`'s base vocabulary: the frame's sorts and `ve__reading`, its constants and `ve__here`, the
decision predicates of `sup D`, the bits `ve__bit__<m+1>__<j>`, and the frame's base predicates. A formula is the
AST wire form over `sharedEnv D`. A certificate is the tableau certificate wire form (the checker replays the trace;
the binding fields are not compared). `readings-conflict`, `readings-certificate` and `readings-model` refuse a
document that is not superposable with `ReadingsNotSuperposable: <sets> (<cause>); use readings-choice` (on the
rights chain `UnsupportedProfile: superposition of a rights document is S2b; use readings-choice`); before any
verdict they also refuse, as `readings-elaborate` does on the superposed and enumerated routes (4.1 steps 3 and 5,
review A1 and DRI ruling 5), a document whose couplings and narrowings in force admit no compatible choice
(`ReadingsUnsatisfiable: <ids>`, decided by Lean's own search: `no_compatible_of_choices`), and a document with a
compatible choice whose document fails the chain's check (`<chain diagnostic> under <set>@<v>:<i>, ...`; on the
superposed route the soft check of every compatible choice, on the enumerated route the chain's check of each of the
at most 64 choices it checks); past 1024 compatible choices the superposed kinds refuse with
`ResourceLimit: more than 1024 readings to check`; and `readings-certificate`, `readings-conflict` and
`readings-model` refuse named readings (`assumed`) that no compatible choice takes, whose every verdict would be
vacuous (`ReadingsUnsatisfiable: no compatible reading takes <set>@<v>:<i>, ...`; `takenBy`,
`readings_wire_assumed_taken`). `readings-elaborate` otherwise reports the route, `readings-dead`
asks `supReady`, and `readings-choice` runs on any admitted document.

* `readings-elaborate`: `route` (`w2`, `pending`, `abstention`, `superposed`, `enumerated`); for `superposed`,
  `finding` null, `narrowings_stale`, `vocabulary`, `units` (the units of `sup D` with `set`, `unit`, `version`,
  `index`, `position`), `slot` (label and AST per premise), `names` (per set and candidate, the author name and its
  name in `sup D`), `choices`, `choice_count`, `choices_checked` (how many compatible choices' documents passed
  the check, or `over 1024`), `sizes` (against the limits); for `enumerated`, `finding`
  (`{"text": "ReadingsNotSuperposable: <sets>", "cause"}`), `narrowings_stale`, `choices`, `choice_count`,
  `choices_checked` (or `over 64`).
* `readings-conflict`: `assumed` (a choice, default `[]`) and either `conflict_certificates` (an object keyed by
  conflict target, each a certificate of the target's closed negation over `Background_base′ ++ slotP ++ atoms`)
  answering `verdict` `CONFLICT-FREE` or `UNKNOWN` with `targets` and `reading_premises`, or `witness`
  (`{"model", "target", "tuple"}`) answering `CONFLICT` or `UNKNOWN` with `target` and the `choice` the model
  encodes.
* `readings-certificate`: `assumed`, `premises`, `conclusion`, `conflict_certificates`, `certificate`; answers
  `accepted` (`conflict_free && valid`), `conflict_free`, `valid`, `assumed`, `reading_premises`. `accepted: true` is
  `readings_wire_all_sound`.
* `readings-model`: `assumed`, `premises`, optional `conclusion` (default `⊥`), `model`; answers `valid`
  (`supModelCheck`), `conclusion_value`, `first_failing` (the first slot label or assumed atom the model falsifies,
  else null) and the encoded `choice`. `valid: true` with `conclusion_value: false` is
  `readings_wire_model_sound`.
* `readings-dead`: `set`, `index` and a certificate of `¬χ` from `choiceCore D` answer `accepted` and
  `DeadReading: <set>:<index>` (not for a candidate a narrowing in force drops); without `index`, a certificate of
  `⊥` answers `ReadingsUnsatisfiable: <coupling and narrowing ids>`.
* `readings-choice`: `choice` (a compatible complete choice) and `inner` (a case of the lower route without
  environment or document); Lean runs the lower route on `choiceDoc D c`'s units and answers `choice`,
  `document_hash` (the chain's hash of that document), `assertions` (how many assertions `choiceDoc D c` has in
  force) and `inner`. For the evidence kinds (the chain's `soft-certificate`, `norms-certificate` or
  `rights-certificate`, and `choice-model`) the inner `premises` are the regenerated assertions in source order
  (`choiceAssertionJsons`) followed by the case's own, so evidence cannot leave an assertion out (compose-s2
  looprecheck1 review B). `choice-model` takes `premises`, optional `conclusion` (default `⊥`) and a base `model` in
  the chain decoder's form (soft `decodeModel`, rights `decodeModelR`, norms `baseModelVocabulary`, no
  definitions), and answers `valid` (the chain's base Background, `Lim_D` included on the rights chain, and every
  premise read through the outcome substitution), `conclusion_value`, `first_failing` (the first failing premise's
  index, else null) and `assertions`. `valid: true` with `conclusion_value: false` is `soft_choice_model_sound`,
  `rights_choice_model_sound` or `norms_choice_model_sound`.
  A certificate kind also needs `conflict`, the chain's conflict packages (`packages`, and `pairs` on the soft
  chain) for the same choice: Lean runs the lower route's own conflict kind on them over the same regenerated
  document (`choiceConflictCase`, never a witness) and answers `conflict_free`, and `accepted` exactly when the
  certificate is `valid` and the conflict status is CONFLICT-FREE (14.8, as `readings-certificate` asks on `sup D`;
  compose-s2 looprecheck2 review B). A certificate case without `conflict` is refused.

# Readings under unspecified defaults in Lean (readings-defaults, batch RD-1)

Specification: [docs/spec/readings-defaults.md](../docs/spec/readings-defaults.md) section 6.2 (draft 2) and plan
[readings-defaults-PLAN.md](../docs/spec/readings-defaults-PLAN.md) RD-1. `lean/audit.py` passes with no `sorry`
and only `propext`, `Classical.choice` and `Quot.sound`. Nothing calls these files yet, so no answer changes; no
frozen file changed (the two modules are listed in `VE/Route/frozen-sources.sha256`).
`tools/check_readings_defaults_statements.py` compares each statement with the approved text.

## Files

| File | Contents |
|---|---|
| `Unspecified.lean` | `NDoc`, `asU` and the four documents as norm-defaults documents (`freeU`, `oneU`, `choiceU`, `supU`); `normsShaped`; `fillDoc` (`fillSoftNode`, `fillContent`, `fillItem`, `strictNodeOf`, `fillUnits`, `fillFrameEnv`); `fillNamesFree`; `WellFormedND`; `AchievesU`, `SeparatedU`, `fillHolds`; the statements of 6.2 |
| `UnspecifiedExamples.lean` | the fixtures of 8.1 as `#guard`: F-ND1 (rows 1.1 to 1.10), F-ND5 (5.1 to 5.3), F-ND0, and F-ND11 |

## The statements of 6.2

In plain words, each with the hypotheses it states. `normsShaped N.D` is the norms chain's shape (strict rules, no
rights content); `fillNamesFree N` says no unit id or declared name begins `unsaid--`.

* `fillDoc_one`, `fillDoc_free`, `fillDoc_choice`, `fillDoc_sup` (under `normsShaped N.D` and `fillNamesFree N`):
  taking a reading's document, the free document, a choice's document or the superposed document of the filled
  readings document gives, after `soften ∘ correlate`, exactly norm-defaults' `fill` of the same document taken from
  the author's; the assertions are unchanged. So every S1 and S2a theorem about `fillDoc N` is a theorem about the
  filled documents of norm-defaults 2.3.
* `compatible_fillDoc` (no hypothesis): the compatible choices of `fillDoc N` are those of `N.D`.
* `attached_fillDoc` (under `fillNamesFree N` and `singlyAttached N.D`, part of `WellFormedDoc`): a fixed unit is
  attached to the same list of sets in `fillDoc N` as in `N.D`. The first approved statement had `fillNamesFree`
  only; the DRI approved the added hypothesis on 2026-10-07 and spec 6.2 now states it. F-ND11 is a norms-shaped
  document with free names whose unit `u0` is attached to `[s2, s0, s1]` in `N.D` and to `[s0, s1, s2]` in
  `fillDoc N`: `attached` iterates its levels once per item, `fillDoc` adds items, and the level lists of a unit
  attached to several sets alternate in order. The members always agree (`mem_attached_fillDoc`, `fillNamesFree`
  only), and that is what the four equalities use.
* `fillDoc_conservative` (no hypothesis but `N.unspec = []`): without unspecified predicates `fillDoc N = N.D`.
* `separates_soundU`, `separates_separatedU` (under `WellFormedDoc (fillDoc N)`, both candidates with content, a
  valid base, and `fillHolds`): a situation that S1's check accepts on `fillDoc N`, whose witness's `Fill_T` holds on
  the base (`fillHolds`), shows the witness achieving the probe value under the completion and the other reading not
  achieving it; so the two readings are separated (one base, one shared filling).
* `achievesU_iff` (under `normsShaped N.D` and `fillNamesFree N`): on the norms chain no key is generated, so
  achieving a probe value under the completion is an admissible base of the author's filled vocabulary, admissible
  for the reading's filled document (norm-defaults' `BaseAdmissibleU`, `Fill_T` included), on which the probe has
  the value.

The helper lemmas say how: building `fillDoc N` is building `N.D` and then filling (`build_fillDoc`, `sup_fillDoc`),
`soften` is the identity on strict documents (`soften_strict`, `soften_hard_identity`'s core without its unused
hypothesis), and the choice vocabulary and `E‴` override disjoint names (`choiceEnv_fill`).

## The wire under the unspecified completion: the statements of 6.3 (RD-2a)

`lean/VE/Readings/UnspecifiedWire.lean`, with the UDoc lemmas beside the 10a theorems whose cores they are. A
document is under the completion when `readings@1` and `norm-defaults@0` are on the norms chain and a set is
content-bearing; the abstention stays on the soft and rights chains (`Wire.abstention`), and `routeOf` takes the
enumerated route there with the finding `ReadingsNotSuperposable: <every open set>`, cause `the unspecified
completion`. Admission (`admitND`, spec 4.1) runs S1's and S2a's admission, then the reserved `unsaid--` names, then
norm-defaults' author checks and `WellFormedU` on the free document and on each reading's document (`ndText`), then
S1's admission of the filled document with its own request table (`admitDecoded`), then each of the at most 64
compatible choices (`choiceChainText` on the filled choice, `ndChoiceText` on `choiceU N c`). Each reading's document
is built once, in a request table.

In plain words, each with the hypotheses it states:

* `acceptanceU` (under `WellFormedU U`): a certificate that checks over `premisesU U Γ` proves `φ` in every filled
  expansion of an admissible filling that satisfies `Γ` (`EntailsU`). `normDefaults_wire_acceptance` keeps its
  statement and calls the same proof (`acceptance_of_fillTyped`).
* `modelCheckU_sound` (under `WellFormedU U` and the base model's validity): a passing model check with a separate
  filling is an admissible filled situation where every premise holds, read through `fill U`'s outcome
  substitution, and the conclusion has the value the check reports.
* `readings_wire_nd_separate_sound` (a replay of `readings-separate` under the completion, `separates` on
  `fillDoc N`, and the witness's `Fill_T` on the base): the witness achieves the probe value under the completion
  and the other reading does not. `separates_filled` says the answer's `separated` is exactly that `separates`.
* `readings_wire_nd_choice_conflict` (a replay of `readings-choice` under the completion, and certificates for every
  target of the choice's filled document): the choice is compatible and its filled document is CONFLICT-FREE under
  every admissible filling.
* `readings_wire_nd_choice_entails` (the same, and a certificate over the choice's regenerated premises): the filled
  choice document is CONFLICT-FREE and entails the conclusion from its assertions and the case's premises.

The helpers: `ndRest_of_ndText` (a passing `ndText` establishes `WellFormedND`'s norm-defaults conjuncts, so each
check runs once), `frameOf_filled` (the filled environment's frame is `fillDoc`'s), `one_links` and
`separates_links` (S1 reads no coupling or narrowing), `choiceU_E` (a choice's filled document reads the frame's
environment, so a base model of it is valid), `fillHoldsOf_eq` (the witness's `Fill_T`, read from the table, is
`fillHolds`).

## Readings with their own vocabulary: the statements of 6.6's wire part (RD-4a)

`lean/VE/Readings/Companions.lean`, its `#guard` fixtures in `CompanionsExamples.lean`. A candidate may carry
`companion: {environment, open_terms}`; a set whose readings all carry one is a companion set (`companionSets`), a set
that mixes the two is refused. Every readings kind first splits the case (`splitCase`, `Run.runCase`): `main`, the
document without its companion sets (their units stay, without content), then one case per companion set in source
order, over the companions' environments merged (`mergeCompanions`) with the set's unit, the set, the narrowings on
it and the companions' open terms merged (`mergeOpenTerms`). The split's checks run in 5's order, rows 6 to 13: a
mixed set, a coupling across components, a companion on the soft or rights chain, different language, revision or
profiles, a name declared differently, an open term declared differently, the frozen decoders on the merged frame,
then each reading's recorded `meaning_id` against `companionMeaningId` (W1's identity over the companion's own
environment). `readings-validate` and `readings-elaborate` answer per case (`components`); the other kinds run on the
case `component` names. A document without `companion` is one case, run as before.

Declarations are compared as JSON values by `jeq` (structural; `jeq_sound`, `jeq_refl`) after each companion is
brought to one normal form (`normJ`), so the request's key order decides nothing.

In plain words, each with the hypotheses it states:

* `mergeCompanions_extends` (a merge that succeeds): every sort, constant or predicate any source declares is in the
  merged environment with that same declaration.
* `mergeCompanions_identical` (the same): two sources declaring one name declare it identically.
* `mergeOpenTerms_identical` (a merge of open terms that succeeds): every source's open term is in the result, and
  two terms of the result with one name are one term.
* `split_keeps_links` (a split that succeeds): every reading set, coupling and narrowing of the document is in exactly
  one case. Its `contains` reads JSON equality as `jeq`, a local instance of the file's section: Lean's own
  `BEq Json` is compiled code a proof cannot unfold.

The helpers: `mergeCategory_spec` (each category's merge keeps names distinct and covers every source's entries),
`mergeTerms_spec` (the same for open terms), `count_one` (an item lands in `main` when its set is not a companion set,
else in its set's case alone), `splitCase_parts`, `componentsOf_docs` and `companionSets_nodup` (the cases are
`main` and one per companion set, without repeats), `mkObj_get`, `overlay_get` and `entries_mem` (lookups in the
objects the split builds).

# S2a with a carried base-premise family in Lean (readings-defaults, batch RD-6a)

Specification: [docs/spec/readings-defaults.md](../docs/spec/readings-defaults.md) section 6.7 and plan
[readings-defaults-PLAN.md](../docs/spec/readings-defaults-PLAN.md) RD-6a. Off the UDHR path: it is what RD-6b
needs to run the superposed route under the completion (more than 64 choices in one frame). `lean/audit.py` passes
with no `sorry` and only `propext`, `Classical.choice` and `Quot.sound`. Nothing calls these files yet, so no answer
changes and every S2a fixture answers as before; the S2a theorems are not restated.
`tools/check_readings_defaults_statements.py` compares each statement with the approved text.

## Files

| File | Contents |
|---|---|
| `SupExtra.lean` | `Transfers`, `supCertificateCheckExtra`, `supModelCheckExtra`; the RD-6a statements of 6.7; `sat_pull_up`; the checks at `Q = []` (`supCertificateCheckExtra_nil`, `supModelCheckExtra_nil`, `baseAdmissibleR_nil`) and three `example`s deriving S2a's `superpose_conflict_free`, `superpose_all` and `superpose_countermodel` from the `_extra` forms at `transfers_nil` |
| `SupExtraExamples.lean` | the fixtures as `#guard` on S2a's K1: X1 (rows X1.1 to X1.6, the counterexample below) and X2 (the `_extra` checks at `Q = []` are S2a's) |

## The statements of 6.7 (RD-6a)

`Q` is a list of base premises added to the slot of `sup D`, and `Q' c` the list added to the limitation premises of
choice `c`'s document. `Transfers D Q Q'` says that each `Q' c` is over the complete vocabulary of `c`'s own
document (so it names no choice symbol), and that a slot-admissible base of `sup D` encoding `c` satisfies `Q`
exactly when the pulled base satisfies `Q' c`.

* `superpose_conflict_free_extra` (under `Transfers`): `sup D` is conflict-free under the slot, the atoms of `A` and
  `Q` exactly when every compatible choice taking `A`'s candidates is conflict-free under its limitation premises and
  `Q' c`. Downward, a base pulls back (`base_down`) and `Transfers` carries `Q` to `Q' c`. Upward, a base of the
  choice's document is lifted (`upB`); the pulled lift reads `Q' c` as the base does (`sat_pull_up`, from `pull_up`),
  so `Transfers` gives `Q` on the lift.
* `superpose_all_extra` (under `Transfers` and `hQw`, below): a certificate on `sup D` with `Q` in its slot proves the
  conclusion in every situation of every compatible reading taking `A`'s candidates whose base satisfies `Q' c`.
* `superpose_countermodel_extra` (under `Transfers`): a finite model passing the model check with `Q` is a situation
  of the reading its atoms encode, whose pulled base satisfies `Q' c`, and with the conclusion false there.
* `transfers_nil`: `Q = []` and `Q' = fun _ => []` transfer, so the S2a statements are the instances.

**One statement changed, pending the statement re-review.** `superpose_all_extra` also takes
`hQw : SlotWellFormed (correlate (sup D).1) Q`: `Q` is over `sup D`'s base vocabulary, as every slot premise is
(`slot_route_acceptance`). Without it the approved statement is false (X1). On K1,
`Q = [∀agent ∀user. ¬avoid_required]` names a regulated predicate, which is a layer symbol and so outside the base
vocabulary: an admissible base gives it no tuple, so `Q` holds of every admissible base (of `sup K1` and, pulled, of
each reading's document), `Transfers` holds with `Q' c = Q`, and the slot stays CONFLICT-FREE. A one-step
certificate proves the conclusion `Q` itself, since the certificate reads `Q` on the intended structure, where
`avoid_required` is the expansion's. On a base with one agent and one user, both readings require
`avoid_required`, so the conclusion is false on their expansions. The other two `_extra` statements and
`Transfers` are as approved.
