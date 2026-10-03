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
| `Separate.lean` | 8.3: `GenKey`, `genKeys`, `owned`, `ownedKeys`; `Tables`, `withTables`, `expand`, `Probe`, `selectable`, `Observes`, `authorEnv`, `Achieves`, `Separated`; the executable check (`Situation`, `tablesModel`, `tablesTyped`, `probeTyped`, `observe`, `sideValid`, `sideValue`, `cells`, `assignments`, `tablesFor`, `tablesOf`, `situationWF`, `separates`); `probesOf`, `observeAll`; `strictOf`, `strictTwin`, `forceTwins`, `decisionOnly`, `AchievesQuiet`, `actOnly` |
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

### `Examples.lean`

* `k2b_not_admissible`, `k2b_achieves_neither`: K2b's base, with a tuple on the default reading's generated
  exception predicate, is not admissible over the author's vocabulary, so neither candidate achieves anything on it.

## Statements of 8.3 not proved here

* `genKeys_nodup` as first approved was false (`WellFormedRights` accepts a line order that lists one default
  fan-out line twice, `Examples.lean` `twiceListed`, or a line its right lacks, `orderOnly`). DRI ruling 1 of
  2026-10-02 adds the hypothesis `linesOnce X = true`, and the corrected statement is proved in `Lines.lean`.
* `decision_only_sound` is not proved (see the work-item report). `decisionOnly` and `decisionOnly_spec` are
  in place, so the criterion is computed; the theorem that backs it is open. Until it is proved the finding is
  **not certified** (DRI ruling 2 of 2026-10-02): `readings-validate` writes it as
  `SeparatedByDecisionOnly: <set>: <i>, <j> (not certified)`, its English is E25 ("It is not certified that ..."),
  not E15, and nothing downstream reads it as a checked result.

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
| `SupWireSound.lean` | `readings_wire_all_sound`, `readings_wire_model_sound`, `readings_wire_satisfiable`, `readings_wire_choice_wellFormed` |
| `SupRun.lean` | the case kinds of section 3 (`Run.lean` dispatches to them) |
| `Examples.lean` | `#guard`s and theorems on M1, M16, M19 (KH, KB), M20; `MU` (two narrowings keeping no choice, review A1) and `MB` (past `maxChoiceChecks`) |

## The statements of 8.4 and 8.5

Proved as stated (draft 5): `sup_no_sets`, `sup_wellFormed`, `asserted_shared` (with `hr`, finding 4),
`slot_wellFormed`, `slot_wellLabelled`, `encodes_unique`, `encodes_atoms`, `superpose_faithful`, `base_down`,
`superpose_situation`, `base_up` (as corrected by finding 6), `superpose_conflict_iff`, `superpose_conflict_free`,
`superpose_conflict_witness`, `superpose_all`, `superpose_all_base`, `superpose_countermodel`, `dead_sound`,
`unsat_sound`, `superpose_assertions` (with `ChoiceExtension` of finding 5), `readings_wire_all_sound`,
`readings_wire_model_sound`; and, added by the review of 2026-10-03, `readings_wire_satisfiable` (a replayed
superposed case has a compatible choice) and `readings_wire_choice_wellFormed`. `base_down`, `base_up`, `superpose_conflict_free` and `superpose_assertions` use
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
`ResourceLimit: more than 1024 readings to check`. `readings-elaborate` otherwise reports the route, `readings-dead`
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
  `document_hash` (the chain's hash of that document) and `inner`.
