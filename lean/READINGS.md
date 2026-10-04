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
| `Separate.lean` | 8.3: `GenKey`, `genKeys`, `owned`, `ownedKeys`; `Tables`, `withTables`, `expand`, `Probe`, `selectable`, `Observes`, `authorEnv`, `Achieves`, `Separated`; the executable check (`Situation`, `tablesModel`, `tablesTyped`, `probeTyped`, `observe`, `sideValid`, `sideValue`, `cells`, `assignments`, `tablesFor`, `tablesOf`, `situationWF`, `separates`); `probesOf`, `observeAll`; `strictOf`, `strictTwin`, `forceTwins`, `relaxTo`, `twinDocs`, `decisionOnly`, `AchievesQuiet`, `actOnly` |
| `Force.lean` | `decision_only_sound` and its three parts: `relaxDoc`, `Twin` and the force lemma for a whole document; `canon_relax`; the premises and probe values over one base; `TwinDocs`, `tablesRel`, `quiet_iff` |
| `Lines.lean` | DRI ruling 1: `linesOnce`, the admission text `lineOrderText` (4.4), `checkRights` in named steps (equal by `rfl`) and the facts read from it, and `genKeys_nodup` |
| `Wire.lean` | 8.4: the environment on the three chains, the document's units and active reading sets, contents, keys, tables, probes and situations; the checks of 4.1 with section 7's texts (`admissionText`); `SeparateReplay`, `replaySeparate`, `readings_wire_separate_sound` |
| `Run.lean`, `../ReadingsMain.lean` | The `ve_readings_route` executable |
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
  `act_of_incompatible`, `incompatible_self`, the remaining `Twin.*` lemmas, `relax_children`, `syms_mem`,
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

Not decoded by Lean: couplings and narrowings (4.7; their checks are rights 3.3's and Python's), and W2's own
structural validation of the sets, which Python performs first.
