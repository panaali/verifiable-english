# cmp-s4: documents and cases, the composed admission, the identity cases (discourse 14.4 to 14.6)

- **Status:** done as cut below; no DRI signature needed (DELTA has no row: reviews/dri-decisions-20261102-cmp-s4.md item 1).
  Review of `4cd3844d4` (FIX): F1 and F-ready1 fixed ("Review fix"). Loop recheck of `622b05893` (FIX) and the DRI note
  of 2026-11-02: F7 (an unbound fence went unread) and F8 (values evaluated twice) fixed ("Review fix 2"). F2 to F6,
  f9 and f10's FOLLOW-UPS row stay the reviews' FOLLOW-UPs.
- **What changed:** `lean/VE/Discourse/Compose.lean` (new) holds 14.4, 14.5 and 14.6's identity theorems, all proved
  (no `sorry`, no new axiom). `lean/VE/Discourse/Run.lean` gains `encodeComposed`, `ComposedAdmissionAnswer` and the
  restated `discourse_wire_acceptance`; `fuelBudget` moved unchanged to `Admission.lean` as `VE.Discourse.fuelBudget`.
  Fixtures: `lean/VE/Discourse/ComposeExamples.lean` (each step on its own input) and
  `lean/VE/Service/ComposedAdmissionExamples.lean` (the admission end to end); `lean/VE/Discourse/ComposeKeys.lean`
  holds eight key-order facts `conditions_retained`'s proof reads.
- **Cut to cmp-s4c (FOLLOW-UP):** the route entry (`runCase` on the composed path, the three `NotImplemented: <kind> on
  the chain` kinds), its relay, schema and fuzz tests, the route cases, the chain decoders that let the soft, rights
  and norm-defaults lists through step 1, and the fixtures that need them (S4-1 on the constitution part, S4-16 and
  S4-17 through the route, S4-18, S4-27, S4-28's route test, the saved byte-identity comparison). Reason: size (below).
- **Depends on cmp-s4ab (not merged):** 14.3 steps 1 and 3 to 7 and the fence slots. Until it merges, the composed path
  refuses a fenced unit and a prose unit with a recorded formula-producing mention by name (below). S4-4, S4-5, S4-22
  with its fence and S4-24 as a route case wait for it.
- **Trust:** S +134, V +16, K +0 (trusted +150 of R16's 150). SIGNED by standing ruling R16. Trust mutants exit 0.
- **DELTA:** no row (docs/composition/cmp-s4/DELTA.md). No route, wire, Python or English answer changes.

## Review fix (review of `4cd3844d4`, `manage-agents/cmp-s4-review.final.md`)

| Finding | Fix | Regression test | Commit |
|---|---|---|---|
| F1 (B): the composed path skipped 14.5 step 4, the manifest checks of 4.1; class: every check today's admission runs before W2 and the composed path did not (unit checks, anchors, tables, mentions and their limit, coverage, labels, the document sort; `caseManifest`; `chainDocument`'s narrowings) | `chainChecks` runs today's functions, no copy: the document mode's load of the `@1` part (4.1(1)) and `wellFormed` on `chainDDoc` (4.1(2) to (8)); a chain content's unit is a unit with meaning (`DDoc.chain`, read by `coveredOk` and `slotUnit`); `documentSortOk` shared with `admitCore`; `caseManifest` runs the same checks; `chainDocument`'s empty narrowings are now exact (the load refuses a narrowing with no reading set). Theorems `composed_wellFormed`, `chainChecks_wellFormed`, `caseManifest_wellFormed` | PROBE F1 as `ComposedAdmissionExamples.lean:107-108`; the differential table `mutations` (`:136`, guards `:161-177`): 14 mutations (byte gap, support, `meaning_id`, narrowing, unknown unit, anchor tree, unknown name, 4097 mentions, overlapping mentions, `It` in a norm unit and in an `ast` unit, a pronoun naming a unit in a norm unit, `self_truth`, document sort), each today's text on the twin without a chain construct and the same text on the composed path and from `caseManifest`; unit guards `ComposeExamples.lean:131-173` | `06a97292d`, `6e376756d` |
| F1's records | the module docstring, `admitChain`'s docstring, this report's step list (step 4), deliverables row and trust figures | | `06a97292d`, this commit |
| F-ready1 (B): no seeded bug named the changed Python file | `tools/layer_policy.py`'s rule for `VE.Discourse.Compose` dropped: `python3 tools/check_lean_imports.py` exits 1 ("new outward Lean import: VE.Discourse.Compose -> VE.Service.Document"); restored. `review-ready.py`: "PASS [mutants] Python: seeded bug in changed file tools/layer_policy.py" | `mutants.json` (last entry) | `0e70487a2` |
| F2 to F6 (C) | not changed here: the review's FOLLOW-UPs cmp-s4-f2 to cmp-s4-f5 (F6 is disclosed size) | | |

No answer of today's route changes: `DDoc.chain` defaults to `[]`, so `coveredOk` and `slotUnit` read as before off
the composed path, and `documentSortOk` is `admitCore`'s former line; the twin guards pin today's texts. DELTA stays
without a row.

## Review fix 2 (loop recheck of `622b05893`, `manage-agents/cmp-s4-looprecheck1.final.md`; DRI note 2026-11-02)

| Finding | Fix | Regression test | Commit |
|---|---|---|---|
| F7 (A): the composed path loaded `Loader.sourceOf j`, which has no fences, so a body fence no unit binds was never read and `admitComposed` answered `"admitted":true` (`caseManifest` answered ok); class: a part of the payload the composed path does not read and does not refuse, on any entry | `Loader.fencesOk` is the one refusal of a body fence, `loadFront`'s former line, now also run by `resolveWith` after `contentOk` (so a bound fence keeps its unit's `NotImplemented: fenced content on the chain`, as `compileUnits` runs before the fence check in `loadFront`). Every entry reaches it: `admitComposed` and `caseManifest` through `chainChecks`, `resolveCase` through `resolveDocument`. Theorems `resolveWith_fenceless` and `composed_fenceless`: no admitted payload has a body fence, so the source `Document.check` reads is the whole body. The docstrings of `chainChecks` and of the module no longer say the `@1` part is loaded "as the document mode loads it" | PROBE F7 verbatim as `ComposedAdmissionExamples.lean:102`; today's exact text on the composed path `:103`, `caseManifest` `:104`, `resolveCase` `:106`, `Loader.fencesOk` `:108`; a bound fence `:111` | `d254fabe9`, `c910d249f` |
| F8 (B): the base environment was decoded twice (`chainBase` and `chainDDoc`) and `contentOk` ran twice (`chainChecks` and `resolveWith`); class: a value the composed path computes more than once (also `tablesOf` in `admitChain`) | `chainBase` returns the decoded route vocabulary and `chainDDoc` takes it; `chainChecks` runs `resolveWith` once and returns the resolved payload, which `admitChain` uses; `admitChain` binds `tablesOf` and `baseEnvironment` once | PROBE F8 (exit 0) and, read from the compiler rather than the source, `tests/test_cmp_s4_evaluate_once.py::test_the_composed_path_computes_each_value_once` (it elaborates a `run_cmd` check under `tmp_path` with `lake env lean`, since the tree may run no code while it elaborates, `tools/lean_dump_cache.py`): over the composed path's definitions and their auxiliaries, `decodeNormsEnvironment` 1 (in `chainBase`), `contentOk` 1 (in `resolveWith`), `resolveWith` 1 in `chainChecks` and 0 in `admitChain`, `chainBase`, `chainChecks` and `tablesOf` once each in `admitChain`, `chainBase` and `chainChecks` once in `caseManifest`; the `large` fixture still ends within its limit (`ComposedAdmissionExamples.lean:50`) | `d254fabe9`, `f45619184` |
| f10 (optional) | this report's line references re-measured; the FOLLOW-UPS row lives in `manage-agents/FOLLOW-UPS.md`, outside this tree: left as filed | | this commit |

The trust budget is unchanged: trusted +150, K +0 (`tools/trust_map.py --check` on `c910d249f`); `Loader.fencesOk` is
D[R] and the new fixture `fenceBody` is T, so neither counts as trusted.

## Deliverables (task cmp-s4)

| Task row | Delivered | Evidence |
|---|---|---|
| (1) 14.4 `resolveDocument`, `caseManifest`, `resolveCase`, `contentFree`, `caseShape`; `resolveDocument_keeps`, `resolveCase_keeps`, `resolveCase_off` | yes, statements verbatim | `Compose.lean:90-275`; statement check below |
| (1) 14.5 `dispatchAdmission`, `chainDocument`, `ChainAdmitted`, `Composed`, `admitComposed`, `conditionalOnOf`, `composedJson`; `composed_admission`, `composed_path`, `conditions_retained` | yes, statements verbatim; step 4 (the manifest checks of 4.1) since the review fix: `chainChecks`, `composed_wellFormed` | `Compose.lean` |
| (2) 14.6 `composed_unchanged`, `composed_base_unchanged`, `composed_unchanged_error` (DRI condition: the `"ve.discourse@1" ∉ profiles ∨` disjunct) | yes, verbatim, in `lean/statements.txt` | `Compose.lean:486-509` |
| (2) `encodeComposed`, `ComposedAdmissionAnswer`, restated `discourse_wire_acceptance` (namespace `VE.Discourse.Run`) | yes, verbatim | `Run.lean:177-202`; `runCase` unchanged, so the proof takes the left disjunct |
| (2) `fuelBudget` moved to `Admission.lean` | yes | `Admission.lean:715` |
| (3) route entry and relay | **cut to cmp-s4c** | widening row pre-signed there (DRI decision item 2) |
| (4) fixtures as `#guard`s | S4-2 (α), S4-3, S4-20, S4-21, S4-22 and S4-23 (without a fence), S4-25, S4-28; S4-16 and S4-17 at `dispatchAdmission`; a synthetic S4-1 on the norms route | the two fixture modules |
| (4) S4-1 on the constitution part, S4-14, S4-18, S4-27, route cases, saved byte-identity comparison | **cut to cmp-s4c** (S4-14 keeps today's answer: no code path changed) | |
| (5) seeded bugs: the four the task names, plus one per new trusted definition | yes, 29 of 29 killed | `mutants.json`, table below |
| evaluate once, charge against a stated limit, a large fixture | yes since review fix 2 (F8: the environment was decoded twice and `contentOk` ran twice before it) | "Evaluation cost"; `tests/test_cmp_s4_evaluate_once.py` |
| `lean/statements.txt`, generated tables | regenerated | `tools/regen_generated.py --write` |

Plan rows (composition-PLAN.md S4, `docs/spec/composition-PLAN.md:824`): "the discourse loader's three abstentions
become implementations" is cmp-s4c's (route) after cmp-s4ab (fences); "`ve/profiles.py` and the Lean gate admit
`ve.discourse@1` beside the chain" is cmp-s4c's (three-way agreement, 14.6); question 7 stays OPEN 1 (DRI 2026-10-31
item 2).

## The composed path in this item (14.5 steps 1 to 7)

`admitComposed` takes the composed path iff `"norms@0" ∈ profiles ∧ "ve.discourse@1" ∈ profiles ∧ chainConstructs
environment j = true`; otherwise it is `.today` of `admitDiscourse … (baseVocabulary environment) … fuelBudget`, or
`baseVocabulary`'s error. On the path, `admitChain` runs, in the spec's order:

1. `wrapperOk` (today's texts and today's frozen FOL-family gate on `baseEnvironment`), then `chainAbstentions`:
   non-empty `groups`, `constraints`, `validity` or `reading_sets` are `NotImplemented: <groups | constraints | validity
   claims | reading sets> on the chain`;
2. `integrityOk` (document table and integrity, as today);
3. `chainBase`: the norms decoder's environment of the base pair, the chain route's environment id
   (`environmentId` of `Norms.Wire.canonicalEnvironmentJson`, the id the norms route's certificates bind) and the
   manifest; `definitions_version` must equal that id (`StaleTarget: definitions@<v>`);
4. `chainChecks` (review F1), the manifest checks of 4.1 with step 5: `resolveWith` (step 5, below) first; 4.1(1),
   the `@1` part under the document mode's `Document.check` without the claim graph, on `writtenText` under the base
   pair (its front matter and the fence-free source, which is the whole body once `resolveWith` has refused every
   fence, `resolveWith_fenceless`: the byte partition, `support`, `meaning_id`, narrowings, the norm contents, with
   today's texts); then today's document sort (`documentSortOk`, now shared with `admitCore`) and
   `wellFormed` (4.1(2) to (8): anchors, tables, mentions with `ResourceLimit: mentions`, coverage, bound units,
   labels with `self_truth`) on `chainDDoc`, the document `prepare` builds: mentions on tokens, W2's units with their
   `ast` formulas, and each chain content's unit a unit with meaning (`DDoc.chain`: its reference surfaces must be
   recorded, `UnrecordedSlot` as S4-14 says, and it is a slot position). `composed_wellFormed`: a `.chain` answer
   implies `wellFormed` of that document; `caseManifest` runs the same checks (`caseManifest_wellFormed`);
5. `resolveWith` (= `resolveDocument` over `chainBase`'s manifest; run once, inside `chainChecks`, whose answer is
   its payload): 14.3 step 6 (`MentionNotSlot: <m>` for a recorded formula-producing mention on a JSON content) and
   three named abstentions while cmp-s4ab is out: `NotImplemented: fenced content on the chain`, `NotImplemented: a
   bound prose unit on the chain`, then a body fence no unit binds, with the loader's own refusal
   (`Loader.fencesOk`: `NotImplemented: fenced English or strict content`, review fix 2). Every other content's
   `resolveContent` answer is the content as written (`resolve_identity`: no slot), so the answer is the payload itself;
6. `dispatch (baseProfiles profiles)`, `chainDocument` (units and `MIXED` parts with id, span, kind and content in the
   chain route's wire form: an `ast` content its formula, any other content as written, the form `Norms.Admission`
   `splitUnit` reads; graph, lemmas, open term names; no graph is today's `NotImplemented: a document without a claim
   graph`), the byte charge, `dispatchAdmission`;
7. `Loader.documentId`, the reference lines (7.1, `referencesJson`; refused if one carries a `conditional_on` list),
   `wrapperReportId` over `inner`'s `report_id`.

Readings (each a point the spec leaves to the implementation):
- **The FOL-family check of step 1** is today's gate (`Gate.decodeEnvelope` on `baseEnvironment`), which knows only
  the frozen profiles: `soft-norms@0`, `rights@0`, `norm-defaults@0`, `readings@1` and `speech-acts@0` lists stop
  there with today's text, the same answer as off the path (`ComposedAdmissionExamples.lean:55-62`). So only the
  norms route is reached in this item; the chain decoders are cmp-s4c's. `dispatchAdmission`'s own refusals are
  pinned directly (`ComposedAdmissionExamples.lean:63-67`).
- **`composedJson`** has the keys `document_id`, `inner`, `inner_report_id`, `references`, `report_id`;
  `encodeComposed` adds `id` and `status: ok`, as `Route.Wire.ok` does for today's answer.
- **`caseShape`** is `{"id": <id>, "document": [<source>, <the front matter's shape as canonical text>]}`; `resolveCase`
  checks its own result against it (regenerated, never trusted) and `resolveCase_keeps` follows from that check.
  Lean's `Json` has no decidable equality, so the check compares strings (as `VE.Ask.Same` does).
- **`conditionalOnOf`** recurses through objects and arrays in its `where`-clauses `tree` and `list` (structural
  recursion through `Json`'s nested tree map); its signature is the spec's.
- **Layer:** `Compose` and its step fixtures are layer 4 in `tools/layer_policy.py` (it states theorems on
  `Service.Document.profilesOf` and runs the chain routes), as `VE.Compose.Contract` is; the end-to-end fixtures are
  under `VE/Service/`.
- **cmp-s4a review F1** (a definite's sort by `restrictionSort`) concerns resolution of slots, which no input reaches
  before cmp-s4ab; it stays with cmp-s4ab's route wiring.

Statement check: every declaration and docstring of 14.4 to 14.6's Lean blocks (`docs/spec/discourse.md:2313-2513`)
compared with `Compose.lean`, `Run.lean` and `Admission.lean`, whitespace-normalised (a one-off script, not
committed): "42 spec declarations and docstrings (discourse.md lines 2313-2513); 0 not verbatim".

## Size

`git diff --numstat $(git merge-base HEAD main)`, hand-written: `Compose.lean` 401, `ComposeExamples.lean` 177,
`ComposedAdmissionExamples.lean` 140, `ComposeKeys.lean` 16, `Run.lean` +14/-7, `Admission.lean` 3, `lean/VE.lean` 4,
`tools/layer_policy.py` 3, `tools/trust-classes.json` +112/-3, `ve/assurance-manifest.json` 3, the allow file 79,
this report and DELTA.md. About 950 lines before the report, above the ~600 guide. The spec-verbatim declarations
with their docstrings and the proofs of the nine theorems take about 230 of `Compose.lean`'s lines and cannot leave
without leaving the statement gate's theorems unproved; the fixtures grew so that every new trusted definition has a
check the trust mutants can read (below). I cut at the route entry (task row (3)), the fallback the task names. The review fix
adds (`git diff --numstat 4cd3844d4`): `Compose.lean` +103/-16 (`chainChecks`, `chainDDoc`, `formulaUnit`, three
theorems), `ComposedAdmissionExamples.lean` +78, `ComposeExamples.lean` +49/-2, `WellFormed.lean` +5/-5,
`Admission.lean` +6/-2, `Manifest.lean` +1, `tools/trust-classes.json` +36/-2, the allow file +5.

## Seeded bugs (Lean, and Python for `tools/layer_policy.py`; no Rust code changed)

Each was planted alone, built with `lake build VE.Discourse.ComposeExamples VE.Service.ComposedAdmissionExamples`,
and restored. All 45 are in `docs/composition/cmp-s4/mutants.json` with the first failing check: the 29 of the build,
the 7 of review fix 2 (table below) and the 9 of the review fix (eight Lean, in `admitChain`, `chainChecks`, `chainDDoc` twice, `coveredOk`, `slotUnit`,
`caseManifest` and `formulaUnit`, and one Python, `tools/layer_policy.py`'s layer-4 rule for `VE.Discourse.Compose`
dropped: `python3 tools/check_lean_imports.py`, the selection's and the gate's import check, exits 1 with "new outward
Lean import: VE.Discourse.Compose -> VE.Service.Document").

| Behaviour | Mutant | Fails |
|---|---|---|
| an unbound fence is refused (F7) | `resolveWith`: `Loader.fencesOk []` | `resolveWith_fenceless` (unsolved goal, case `cons`) |
| the same, past the theorem (F7) | as above, `resolveWith_fenceless`'s proof `sorry` | `ComposedAdmissionExamples.lean:102` (PROBE F7), `:103`, `:104`, `:106` |
| the refusal is the loader's text (F7) | `Loader.fencesOk`: `"fenced content"` | `ComposedAdmissionExamples.lean:103`, `:104`, `:106`, `:108` |
| a bound fence keeps its unit's abstention (F7) | `resolveWith`: the fence refusal before `contentOk` (proof `sorry`) | `ComposedAdmissionExamples.lean:111` |
| the environment is decoded once (F8) | `chainDDoc` decodes it again | `test_the_composed_path_computes_each_value_once`: `decodeNormsEnvironment` on the path 2, not 1 |
| `contentOk` runs once (F8) | `chainDDoc` runs it again | the same test: `contentOk` on the path 2, not 1 |
| `tablesOf` is read once (F8) | `admitChain`: `integrityOk j (tablesOf j).1 (tablesOf j).2` | the same test: `tablesOf` in `admitChain` 2, not 1 |
| the composed path needs `ve.discourse@1` (S4-28) | `admitComposed`: `"ve.discourse@1" ∈ profiles ∧` dropped | `composed_path` (`Compose.lean:431`, via `admitChain_of`) |
| `readings@1` beside `norms@0` is refused (S4-16) | `dispatchAdmission`: `.readings` runs the norms route | `ComposedAdmissionExamples.lean:64` |
| no coherence premise dropped from `conditional_on` (S4-18) | `composedJson`: `inner` with its `conditional_on` emptied | `conditions_retained` (`Compose.lean:467`) |
| `resolveCase` removes the `discourse` key (S4-22) | `writtenText`: `discourse` kept | `ComposedAdmissionExamples.lean:219` |
| `definitions_version` is checked (step 3) | `admitChain`: `req (true || …)` | `ComposedAdmissionExamples.lean:91` |
| the payload is kept (`resolveDocument_keeps`) | `resolveWith`: the source rewritten | `resolveDocument_keeps` (`Compose.lean:250`) |
| a case without `ve.discourse@1` is unchanged | `resolveCase`: always `resolveOn` | `resolveCase_keeps` (`Compose.lean:257`) |

The other 22 (one per remaining new definition: `chainKeys`, `contentKey`, `unitsAndParts`, `chainConstructs`,
`contentOk`, `chainAbstentions`, `editObj`, `editArr`, `unitFree`, `frontShape`, `textShape`, `caseParts`,
`contentFree`, `caseShape`, `chainUnit`, `conditionalOnOf` and its `tree` and `list`, `chainBase`, `caseManifest`,
`chainDocument`, `encodeComposed`) each fail a named `#guard` (`mutants.json`).

## Trust (R16)

`uv run python tools/trust_map.py --check`: "PASS: K, S and untied [V] within 3b4e471f8c29 and the allowances
introduced since"; against the merge base, re-measured on the review fix (`162a1f2b1`): K +0, S +134 (`Compose.lean`
+133: the build's 125 and `formulaUnit` +8; `Manifest.lean` +1: `DDoc.chain`), V +16 (`Compose.lean` +11: `chainBase`;
`Admission.lean` +4: `documentSortOk`; `Run.lean` +1: `encodeComposed`), trusted +150 (per file: `Compose.lean` +144,
`Admission.lean` +4, `Manifest.lean` +1, `Run.lean` +1). Recorded with `--signed "SIGNED by standing ruling R16
(DRI-RULINGS.md), cmp-s4, 2026-10-18"` (S +125, V +19) and, for the review fix's S +9, `--signed "SIGNED by standing
ruling R16 (DRI-RULINGS.md), cmp-s4, 2026-11-02"` (`docs/trust-baseline.json`). No line replaces a deleted Python
path (no R6).

Classes (`tools/trust-classes.json`): S for the meaning the theorems are stated over or that decides acceptance
(`chainConstructs` and its helpers, `contentOk`, `chainAbstentions`, `contentFree`, `caseShape` and their helpers,
`chainUnit`, `conditionalOnOf`, `ChainAdmitted`, `Composed`), as cmp-s4a's review F2 asks; C for the checked
executables (`resolveWith`, `resolveDocument`, `resolveOn`, `resolveCase`, `writtenText`, `admitChain`,
`admitComposed`); tied: `composedJson` (`conditions_retained`), `chainDocument` and `dispatchAdmission`
(`composed_admission`), `fuelBudget` (`composed_unchanged`), `ComposedAdmissionAnswer` (`discourse_wire_acceptance`);
`chainReferences` G[R]; fixtures T. Review fix: `formulaUnit` S (as `chainUnit`); `documentSortOk` G[V] (as
`admitCore`'s other checks); `chainChecks` and `chainDDoc` G[V] tied by `chainChecks_wellFormed`, `caseManifest` D[V]
tied by `caseManifest_wellFormed` (each states `wellFormed`, an S anchor, of `chainDDoc`'s document).

Re-measured on review fix 2 (`f45619184`): the same figures, per file the same (`Loader.fencesOk` D[R]; `fenceBody` T).

R16's conditions: 150 ≤ 150, K +0; every new trusted definition has a check that can fail (the 45 hand mutants; the
trust mutants); the FOLLOW-UPS row is under "## cmp-s4" in `manage-agents/FOLLOW-UPS.md` (ties pass).

Trust mutants: `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/composition/cmp-s4/trust-mutants-allow.json
--json docs/composition/cmp-s4/trust-mutants.json` on `f45619184` (review fix 2's final Lean tree, `35dae588e652`; a
full run, no `--rescore`; cloud pool, 4 parts, 1215 s): exit 0, "KILLED 173, SURVIVOR 0, UNKNOWN 0, INVALID 32,
ALLOWED 26", the counts of the runs on `6e376756d` (the review fix's tree) and `c910d249f` (before the check moved out). A first run on
`06a97292d` left 36 survivors in `slotUnit`, `coveredOk`, `documentSortOk` and `formulaUnit`, whose kills were only in
`VE/Service/` (outside the directory the tool builds); `6e376756d` adds their unit guards to `ComposeExamples.lean`
(`chainDDoc`'s four-unit document, a group span in either position, documents in either order). The 16 allow entries are type errors the tool reads as UNKNOWN
(`list-empty` on lists and maps of another type), `Composed`'s constructor drops (each constructor has a `#guard`), and
equivalent mutants (`take 1` and `reverse.take 1` on lists of at most one element or under `isEmpty`, `chainKeys.dropLast`
past the `fence` arm), each with its one-line reason; the review fix adds one, `documentSortOk`'s `K.documents` ->
`[]` (a type error). Two tool constraints shaped the fixtures, recorded for the next
item: the tool's source scan does not read Lean raw strings (`r#"…"#`), and it probes a definition's own module when
that module holds `rfl` checks, so the key-order facts live in `ComposeKeys.lean` and the end-to-end fixtures (whose
probe walks the whole chain route, about 11 minutes) are outside `Compose`'s directory.

## Evaluation cost (feature feed, evaluators and runners)

Since review fix 2 (F8), `admitComposed`'s own code computes each value it reads once: `chainConstructs` once (the
path test); on the path `tablesOf` once, the base environment decoded once and the manifest once (`chainBase`, whose
route vocabulary `chainDDoc` takes), `resolveWith` (and so `contentOk`) once, inside `chainChecks`, whose answer is the
resolved payload, `chainDocument` once, the chain route once, the reference lines once
(`tests/test_cmp_s4_evaluate_once.py` counts the calls in the elaborated bodies). The functions it reuses read their own inputs as they do today:
`Document.check` decodes the written-out text's front matter, the chain route its environment, and `decodeManifest`
its tables (once more after `tablesOf`, in today's order of `integrityOk` before the manifest). The chain
document is charged against `Loader.maxDocumentBytes` (4,000,000 bytes, the loader's limit on a document text) before
the chain route reads it: `ResourceLimit: chain document bytes`. No slot is resolved in this item, so nothing fans out;
the norms route keeps its own limit of 256 rules. Fixture: a 200-norm-unit document ends within both
(`ComposedAdmissionExamples.lean:45-50`, `large`; still `chain` after review fix 2).

## Tests

- `lake build VE.Discourse.ComposeExamples VE.Service.ComposedAdmissionExamples`: every `#guard` passes.
  `cd lean && lake build`: "Build completed successfully". `python3 lean/audit.py`: "PASS: 727 source files; 8029 named
  theorem declarations audited … only the declared standard axiom allowlist".
- `uv run python tools/regen_generated.py --check --skip route-cases`: "checked 34 entries" (route-cases needs the Rust
  release binary; its inputs did not change: `runCase` is as on main). `tools/check_lean_imports.py`: "Lean layer
  graph kept".
- Selected tests: `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on `eac6e76b1`: 436 of 437
  units passed in 6 shards; the one failure, `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`
  (the new files unclassified), was fixed in `edd6810d0`. After the fixture split, a second selected run on `161d199ea`
  (fast stage, 306 of 423 units: "1 failed, 10460 passed") failed only that test again, for `ComposeKeys.lean`'s
  docstring; fixed in `83ae4691e` and rerun: `uv run pytest -q tests/test_assurance_manifest.py`: "139 passed".
- Review fix: `cd lean && lake build`: "Build completed successfully (1237 jobs)"; `python3 lean/audit.py`: "PASS: 727
  source files; 8032 named theorem declarations audited"; `tools/regen_generated.py --check`: "checked 35 entries";
  `tools/trust_map.py --check`: PASS; PROBE F1: exit 0. Selected tests (`zsh mac-pytest.sh --select -- --base
  $(git merge-base HEAD main) --run` on `0e70487a2`): 424 units, 1 failed,
  `tests/test_trust_mutants.py::test_a_guard_over_the_empty_list_leaves_survivors` (20 printed SURVIVOR lines against
  21 in its JSON, on the tool's own Demo tree; no file it reads changed); rerun alone on the same commit: "1 passed"
  (load-sensitive: FOLLOW-UP). The selection for the report-only commit `3f6eb8234` (`--base 0e70487a2`: 5 units,
  `tests/test_trust_mutants.py` whole, "564 passed"): exit 0.
- Review fix 2: `cd lean && lake build`: "Build completed successfully (1237 jobs)"; `python3 lean/audit.py`: "PASS: 727
  source files; 8034 named theorem declarations audited"; `tools/regen_generated.py --check`: "checked 35 entries";
  `tools/trust_map.py --check`: exit 0, trusted +150, K +0; PROBE F7 and PROBE F8: exit 1 on `622b05893`, exit 0 after.
  Selected tests on `234f97d14` (6 shards, 439 units): 438 passed; `tests/test_lean_dump_cache.py` failed 3 tests
  (`test_the_real_tree_runs_no_code_while_it_elaborates` and two that follow from it: the `run_cmd` then in
  `ComposeExamples.lean` is code run while elaborating). Fixed in `f45619184` (the check moved to
  `tests/test_cmp_s4_evaluate_once.py`); those three and the new file rerun alone: "6 passed".
  Selected tests on `8dab6ee04` (the final code and evidence; `zsh mac-pytest.sh --select -- --base $(git merge-base
  HEAD main) --run`, 6 shards, 445 units, among them `tests/test_cmp_s4_evaluate_once.py` and
  `tests/test_lean_dump_cache.py`): exit 0, 445 passed. This commit changes only this report.
- No test in `main-known-red.txt` was hit. Not run: the full gate (the chain runs it on the final HEAD).

## Pilot bytes

0 (*estimate*): no route reaches the composed path before cmp-s4c.

## Commits (`git log --oneline --no-merges main..HEAD`, saved at `6a718d882`, plus this report's commit)

```
6a718d882 cmp-s4: trust mutants on f45619184 (full run): exit 0 (KILLED 173, SURVIVOR 0, UNKNOWN 0, INVALID 32, ALLOWED 26)
f45619184 cmp-s4 review F8: the evaluate-once check moves out of the tree into tests/test_cmp_s4_evaluate_once.py
234f97d14 cmp-s4 review fix 2 (F7, F8): mutants.json (45: seven seeded bugs), REPORT (review-fix 2 table, steps 4 and 5, evaluation cost, trust re-measured, line references) and DELTA (still no row)
5bfc4c424 cmp-s4: trust mutants on c910d249f (full run): exit 0 (KILLED 173, SURVIVOR 0, UNKNOWN 0, INVALID 32, ALLOWED 26)
c910d249f cmp-s4 review F7: Compose's module docstring names the unbound-fence abstention and no longer says the @1 part is loaded as the document mode loads it
d254fabe9 cmp-s4 review F7, F8: refuse an unbound body fence by the loader's own refusal; decode the base environment and run contentOk once
622b05893 cmp-s4 review fix: REPORT records the report-only commit's selected run
3f6eb8234 cmp-s4 review fix: REPORT (review-fix table, tests, trust, size) and DELTA (still no row)
0e70487a2 cmp-s4 review F1, F-ready1: mutants.json (38: the fix's eight Lean and one Python seeded bugs), REPORT step 4 and trust re-measured
162a1f2b1 cmp-s4: trust mutants on 6e376756d (full run): exit 0 (KILLED 173, SURVIVOR 0, UNKNOWN 0, INVALID 32, ALLOWED 26)
6e376756d cmp-s4 review F1: unit guards for slotUnit, coveredOk, documentSortOk and formulaUnit in the Discourse directory
06a97292d cmp-s4 review F1: the composed path runs 14.5 step 4, the manifest checks of 4.1
4cd3844d4 cmp-s4: REPORT (final)
cb5edf9e1 cmp-s4: trust mutants on 83ae4691e (rescore): exit 0 (KILLED 129, SURVIVOR 0, UNKNOWN 0, INVALID 32, ALLOWED 25)
83ae4691e cmp-s4: ComposeKeys' docstring reads no JSON API name (assurance manifest's JSON-use scan); inventories
161d199ea cmp-s4: trust mutants on 2f6fcc6ab: exit 0 (KILLED 129, SURVIVOR 0, UNKNOWN 0, INVALID 32, ALLOWED 25)
2f6fcc6ab cmp-s4: S +125 again (no helper docstrings in conditionalOnOf's where-clauses); twoMentions classified T; inventories
1028d3c6b cmp-s4: conditionalOnOf's helpers as where-clauses (one declaration); two more guards; trust-mutant allow file
bf0f12d72 cmp-s4: the key-order lemmas in their own module (ComposeKeys); inventories, pins
36cf6c26a cmp-s4: fixtures split: each step on its own input and the admission end to end; mutants rerun
edd6810d0 cmp-s4: classify Compose.lean and its fixtures in the assurance manifest's other_json
eac6e76b1 cmp-s4: DELTA (no row) and REPORT draft
3afd13161 cmp-s4: R16 allowance S +125
97452b9e5 cmp-s4: conditionalOnOf's signature as the spec writes it; inventories regenerated
c16972559 cmp-s4: classify the fixture helper envCase (T)
3539f48df cmp-s4: fixtures without raw strings, stronger guards; layer 4 for Compose; pins and inventories regenerated
cfcf7604d cmp-s4: R16 allowance recorded (S +124, V +19, K +0)
508ed932b cmp-s4: seeded mutants (29 of 29 killed), regenerated inventories
66fd81dd0 cmp-s4: trust classes (R16), regenerated tables and inventories; guards at dispatchAdmission, caseManifest and encodeComposed
ae3827aad cmp-s4: the composed admission's fixtures (14.8) as #guards; chainBase on the norms decoder
26dcaaf71 cmp-s4: Compose.lean, 14.4 to 14.6 with their theorems; the wire entry restated; fuelBudget moved to Admission.lean
```

## Next items

- FOLLOW-UP: cmp-s4c, the discourse route entry on the composed path, its relay, schema, fuzz tests and route cases,
  the chain decoders in step 1, and S4-1, S4-14, S4-16, S4-17, S4-18, S4-27, S4-28 as route fixtures with the saved
  byte-identity comparison (DRI decision 2026-11-02 item 2 signs its widening row and lists its conditions).
- cmp-s4ab (14.3 steps 1, 3 to 7; fences), cmp-s4b (OPEN 4), pc-s4-positions, then pc-7b.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A., no relayed answer changes (`runCase` and the relay unchanged; cmp-s4c).
2. Every deliverable built or ruled: PASS, the deliverables table; the cut to cmp-s4c is the task's own fallback and the DRI's decision item 1; no Python copy of a Lean decision, no report test, no in-flight overlap (`tools/layer_policy.py` edited away from feature/pc-1's hunk).
3. Tests can fail: PASS, `mutants.json` (45 of 45 killed, each planted alone) and `trust-mutants.json` (exit 0, allow file with one reason per entry).
4. Python, Lean and Rust agree: N.A., no Python or Rust product change and no answer change; the composed path and today's admission agree on every mutation of the differential table (review F1).
5. R8 binding: N.A., no relay field added (cmp-s4c).
6. Gate evidence on the final HEAD: PASS, the chain runs the gate on the final HEAD; the trust mutants ran on `f45619184`, whose Lean tree is the final one.
7. No unsigned item: PASS, R16 growth signed (`docs/trust-baseline.json`); DELTA has no row (DRI decision item 1).
8. Every user-visible change in DELTA: PASS, none: `runCase` unchanged; outside `lean/` and `tools/` the diff is `ve/assurance-manifest.json`'s three classification lines (`git diff --stat $(git merge-base HEAD main) -- ve rust tests`); DELTA.md.
9. Test selection: PASS, the selected runs above chose 437 and 423 units, not every unit.
10. Statements say what is claimed: PASS, the statement check (0 not verbatim) and the proof-killing mutants `admitComposed`, `composedJson`, `resolveWith`, `resolveCase`.
11. Budgets fail closed: PASS, `ResourceLimit: chain document bytes` before the chain route; the `large` fixture ends within it (`ComposedAdmissionExamples.lean:45-50`).
12. No CPU or memory regression: N.A., no route reaches the new code before cmp-s4c.
13. `Test-removed` trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS, accepting and refusing guards for each check (e.g. `contentOk` refuses at `ComposeExamples.lean:75-83` and accepts at :84-85; `chainAbstentions` refuses at :88-93 and accepts empty or absent lists at :94-96); spec re-read: 14.4 against `docs/spec/discourse.md:2313-2352`, 14.5 against :2354-2441, 14.6 against :2443-2512, 14.8's rows against :2521-2561.
