# RD-9 Lean progress report

Status: **in progress; not an RD-9 acceptance report**. This increment builds a part of SC-1. No soft-completion route is enabled by it. No model calls were made.

## Implemented

- `LayeredEntail.lean`: the exact SC-1 `premisesX`, `EntailsX`, conflict-certificate and finite-model statements, their soundness proofs, nil conservativity, and the shared `bindCertX` binder.
- `SoftDefaults.lean`: the soft document shape and per-document `X` definitions, the strict and norms-shaped nil theorems, `filledAuthorEnv`, and `WellFormedSD`.
- `Verdicts.lean`: `ChoiceSem`, `HoldsG`, `CoversG`, `RowsHoldG`, seven generic fold soundness proofs, `CounterX`, `ConsistentX`, `ndSem`, and `xSem`. RD-3's seven fold theorems retain their statements and now apply the generic proofs.
- The norms choice and verdict certificate callers use `bindCertX` with `X = []`. This does not alter their regenerated premise list or wire output.
- `UnspecifiedWire.lean` now states `fillRest`, `ndRest_eq_fillRest`, and `wellFormedSD_eq` with the spec's exact expressions.
- Generated axiom, statement, declaration, predicate, frozen-source and checker-pin inventories were refreshed. The assurance manifest's whole-file decoder pins and its generated document were updated for the two edited wire files. The source files under `VE/Norms`, `VE/SoftNorms`, and `VE/Route` were not edited.

## Outstanding work

- SC-1 still needs `softX_wellFormed`, the approved fixture module, and exact-statement checks for the later RD-9 batches. `check_rd9_sc1_statements.py` checks the 48 SC-1 declarations already built and reports the missing theorem explicitly.
- SC-A, SC-2, SC-3, SC-4, SC-5, and SC-6 are not implemented here; SC-8 and SC-9 are also not done. The plan's SC-0 bounded re-check and the item-specific DRI signature for the SC-6 theorem amendment are not recorded in this worktree.
- `tools/trust_map.py --check` classifies every new declaration and reports `S +56` and untied verdict-bearing `V +13`, for 69 added trusted lines. **Needs a DRI signature.** Standing ruling R6 does not cover this change because no Python or Rust decision path was deleted. No allowance was added to `docs/trust-baseline.json`.
- No user-visible wording, field, fault-order, verdict, or availability delta is enabled by this increment. Thus no standing ruling signs a user-visible delta yet. Future batches must record each delta and its ruling/test in this file.

## DRI signatures (2026-10-15)

Recorded as decided in `manage-agents/reviews/rd-9-dri-signatures-20261015.md` (not re-decided here); review F27 of
`manage-agents/reviews/rd-9-conditions-gap-20261015.md`.

| Item | Signature | Evidence |
| --- | --- | --- |
| Trust growth (B8, B9) | **SIGNED WITH CONDITION** by the DRI (item 1). Re-measured with `tools/trust_map.py` on the final tree of the DRI-conditions round: K 997, S 9,959, V 37,526, against the signed baseline K +0, S +171, V +372 (V +363 at 67d0cb31, plus F25's V +9: `Readings.Chain.text` and `filled.chain`). S by file: `VE/NormDefaults/LayeredAdmission.lean` +54, `VE/Readings/Verdicts.lean` +52, `VE/NormDefaults/Run.lean` +24, `VE/Readings/SoftSeparate.lean` +20, `VE/NormDefaults/Admission.lean` +17, `VE/NormDefaults/LayeredEntail.lean` +4. V by file: `VE/Readings/Run.lean` +146, `VE/Readings/VerdictsWire.lean` +69, `VE/Readings/SoftWire.lean` +44, `ResponseShape/Schemas/ReadingsRoute.lean` +31, `VE/NormDefaults/Run.lean` +30, `VE/Readings/SoftVerdicts.lean` +24, `ResponseShape/Schemas/NormDefaults.lean` +14, `VE/Readings/UnspecifiedWire.lean` +14, `VE/NormDefaults/LayeredEntail.lean` +11, `VE/Readings/SoftDefaults.lean` +10, `VE/Readings/Doc.lean` +5, `ResponseShape/Schemas/SoftNorms.lean` +2, `VE/NormDefaults/Layered.lean` +1, `VE/Readings/ComponentsWire.lean` -29. FOLLOW-UP: a ties pass binding these lines to the existing render, wire and encoder theorems | the signed entry in `docs/trust-baseline.json` (`history`, absorbed by `trust_map.py --write`); `trust_map.py --check` PASS; `tests/test_rd9_dri_signatures.py` |
| D1 exception: `ve/rights_route.py:23-89` `_narrowings` | **GRANTED, time-boxed to 2026-10-22** (item 2). `_narrowings` mirrors Lean's derivation of each line's mechanisms (Correlate.lean `narrowings`) and, since F24, their licences (Run.lean `licence`: `own_cites` line 45, `narrows`, `collides` and `licence` lines 56-63, the licensed pairs lines 67-88), called by the elaboration binder at lines 313-317. The exception expires when the FOLLOW-UP infra item **rights-licence-relay** merges: Lean returns the licences and Python relays them | `_narrowings`' docstring; `tests/test_rd9_dri_signatures.py::test_the_d1_exception_cites_narrowings_lines` |
| B4: `choiceLayeredG` gains `hN`; `ndTextWith` builds `free N.D` once | **SIGNED** (item 3; bounded statement re-check PASS, `manage-agents/reviews/rd-9-b4-recheck.md`). `tools/check_rd9_sc1_statements.py` lists both under `SIGNED`, each the approved text with exactly its one edit; any other difference still fails | `tests/test_rd9_statements.py::test_probe_f27_the_signed_declarations_are_no_longer_pending`, `::test_a_signed_declaration_still_fails_on_any_other_difference[*]`, `::test_a_signed_edit_that_no_longer_applies_fails` |
| B1: soft-completion availability | **SIGNED once the full gate passes on the final HEAD** (item 3). Conditions: (a) F11 fixed (met earlier); (b) the full gate on the final HEAD: due from the merge train's branch verify, not run in this round (task instruction); (c) R14 (F26, below); (d) the `soft_chain` copy removed: Lean relays the chain (F25) | `tests/test_rd9_chain_relay.py`, `tests/test_rd9_r14_candidates.py` |
| B8: gap selection | **SIGNED** (item 3): "not claimed sound" is stated (FIX-REPORT B6 row, spec 8) with the flip tests | `tests/test_rd9_gap_relay.py` (the unlisted-gap flip tests) |
| SC-9 external and comprehension checks | FOLLOW-UP (DRI), not blocking | — |
| Trust ties (item 1's FOLLOW-UP row; infra item trust-ties-rd9, 2026-10-16) | Done as far as existing theorems reach: six of rd-9's [V] declarations are tied in `tools/trust-classes.json` to existing theorems that constrain their meaning, and untied V falls by their 30 lines (V 39,600 to 39,570 on this tree; rd-9's V +372 to +342). No allowance is raised or added and no signature is written: the change only lowers V. The declarations no existing theorem ties are listed with the theorem that would, below ("Trust ties pass") | `trust_map.py --check` PASS before and after; the per-file counts below; the seeded ties below |
| F33: F32's wording for a soft-chain document with content beside a companion set | **SIGNED by the DRI note** `manage-agents/reviews/rd-9-dri-note-20261015e.md` (F32: "This needs no new ruling: the spec already decides it"; rd-9-soft-chain.md 5 row 7). R1 does not cover it (row 7 does not quote `readings@1` or `norm-defaults@0`); the item-specific note takes precedence. Before rd-9, `abstention` (`Wire.lean`) refused such a document on the soft chain with row 6's `UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented`; rd-9 narrowed that abstention to the rights chain, and F32's `splitAdmissible` (`ComponentsWire.lean`) now refuses it in every admission of the split with row 7's `UnsupportedProfile: readings with their own vocabulary on the soft or rights chain are not implemented`. The code (`UnsupportedProfile`) and the refusal are unchanged; only the text changed. Such a document without a companion set is answered under the soft completion (B1) | `tests/test_rd9_soft_split.py::test_f32_every_kind_of_a_soft_split_is_refused_with_row_7[*]` (33 requests), `::test_f32_probe_validate_and_elaborate_through_the_relay`, `::test_fsd1_alone_stays_under_the_soft_completion` |

## R14 (DRI condition B1(c), review F26)

Any conflict the readings route reports about the constitution (`CE4`, SC-8 and SC-9) is a result about the pilot's
translation: a CANDIDATE (R14 source check pending: SC-9 external check, FOLLOW-UP) until SC-9's independent source check has run. No report of this batch presents one as a
conflict in the source; `CE4`'s conflict question (C5) answers CONFLICT-FREE on all 16 choices.
`tests/test_rd9_r14_candidates.py` fails if an rd-9 report, spec, docstring or `CE4` golden states a constitution
conflict without this label.

## Trust ties pass (FOLLOW-UP of the trust signature, infra item trust-ties-rd9, 2026-10-16)

Method. `tools/trust_map.py` was run against rd-9's base (`ee4ae48ad`, main's first parent before the rd-9 merge) and
on the merged tree; every untied D[V] or G[V] declaration whose lines rd-9 added or grew (V +372 in all) was checked
against `lean/statements.txt` for a theorem whose `-- uses` line names it and another anchor. The tool accepts any such
theorem; a tie was added only where the statement fixes the declaration's meaning, either outright (an equation with
existing meaning) or in the direction a verdict relies on (a soundness statement, so that what is left unconstrained only
refuses). The encoder theorems of `lean/ResponseShape/Encoders` cannot tie anything: the statement dump reads
`lean/VE/Audit.lean` only, and their statements (`Fits`, `OkP`) constrain an answer's form, not its meaning.

### Ties added

| File | Declaration (lines) | Tying theorem | What the statement fixes |
| --- | --- | --- | --- |
| `VE/NormDefaults/LayeredEntail.lean` | `VE.NormDefaults.Wire.premisesX` (3) | `VE.NormDefaults.acceptanceX`, `VE.NormDefaults.Wire.premisesX_nil` | A certificate checked over `premisesX U X Γ` gives `EntailsX U X Γ φ` (S, the semantic consequence over `BaseAdmissibleX`), so no premise outside the layered semantics can be in the list; at `X = []` the list is `premisesU`'s exactly |
| `VE/NormDefaults/Run.lean` | `VE.NormDefaults.Admission.runAdmissionX` (10) | `VE.NormDefaults.Admission.runAdmissionX_sound` | Every answer is `AdmissionAnswerX` (S): `encodeAdmittedX` of the admitted result with the report id digested from the canonical environment, and on every admissible structure the report's root follows from the background, `X`, `Fill_T`, the layer premises and the report's other assumptions; only refusals are left |
| `VE/Readings/SoftDefaults.lean` | `VE.Readings.softX` (1) | `VE.Readings.softPremisesIn_fill` | An equation: `softX N X` is soft-norms' own `softPremisesIn (correlate X)` on `fill (asU N X)` |
| `VE/Readings/SoftDefaults.lean` | `VE.Readings.filledAuthorEnv` (3) | `VE.Readings.filledAuthorEnv_eq` | An equation: it is `authorEnv (fillDoc N)`, two declarations that existed before rd-9 |
| `VE/Readings/UnspecifiedWire.lean` | `VE.Readings.Wire.ndDocTextG` (6) | `VE.Readings.Wire.wellFormedU_of_ndDocTextG` | A document it passes is `WellFormedU`; what is left (the author checks, the `generated` count for the vocabulary limit) only refuses. `ndDocText_eq_G` was not used: `ndDocText` is defined from it |
| `VE/Readings/VerdictsWire.lean` | `VE.Readings.Wire.probeFormulaOn` (7) | `VE.Readings.Wire.probeFormulaOn_eval` | Wherever the probe's observation is defined (`observeOn P M q = some v`), the formula evaluates to that value |

Rejected candidates (the tool accepts them; the statement does not constrain the declaration): `bindCertX` by
`VE.Ask.ndBoundCert_eq` (it defines Ask's binder by `bindCertX`); `PairFacts` and `pairFactsSpec` by `pairFactsIn_eq`
(the first appears only as a type; the second is the specification side of an equation with the faster `pairFactsIn`,
so a tie would only move the trust to the less readable side); `AdmittedSD` by its own fields and by
`authorEnv_unsaid` and `candidate_unsaid` (a type only); `choiceX` and `oneX` by the `readings_wire_sd_*` theorems,
`SDVerdicts.hX`, `ChoiceReplayS.hX` and `otherShowsS` (arguments only), and `choiceX` by `choiceX_normsShaped` (one
case); `xInfos` by `xInfos_rows` (it fixes each row's choice, conflict, query and premise but not `notes`, the
`conditional_on` the answer shows); `NormDefaults.Run.runCase` by `normDefaults_wire_admission` and `...X` (the
`admission` kind only).

### Per-file counts (untied V lines, `trust_map.py`; before = `d7ea7228b` (main with rd-9 merged), after = `d92a55e1f` (the ties commit))

| File | rd-9's V (signed) | V before | V after | Ties | rd-9's V after the ties |
| --- | --- | --- | --- | --- | --- |
| `ResponseShape/Schemas/NormDefaults.lean` | +14 | 243 | 243 | 0 | +14 |
| `ResponseShape/Schemas/ReadingsRoute.lean` | +31 | 849 | 849 | 0 | +31 |
| `ResponseShape/Schemas/SoftNorms.lean` | +2 | 319 | 319 | 0 | +2 |
| `VE/NormDefaults/Layered.lean` | +1 | 192 | 192 | 0 | +1 |
| `VE/NormDefaults/LayeredEntail.lean` | +11 | 11 | 8 | -3 | +8 |
| `VE/NormDefaults/Run.lean` | +30 | 123 | 113 | -10 | +20 |
| `VE/Readings/ComponentsWire.lean` | -29 | 271 | 271 | 0 | -29 |
| `VE/Readings/Doc.lean` | +5 | 18 | 18 | 0 | +5 |
| `VE/Readings/Run.lean` | +146 | 569 | 569 | 0 | +146 |
| `VE/Readings/SoftDefaults.lean` | +10 | 10 | 6 | -4 | +6 |
| `VE/Readings/SoftVerdicts.lean` | +24 | 24 | 24 | 0 | +24 |
| `VE/Readings/SoftWire.lean` | +44 | 44 | 44 | 0 | +44 |
| `VE/Readings/UnspecifiedWire.lean` | +14 | 179 | 173 | -6 | +8 |
| `VE/Readings/VerdictsWire.lean` | +69 | 763 | 756 | -7 | +62 |
| **All files** | **+372** | **39,600** | **39,570** | **-30** | **+342** |

K (997) and S (10,138) are unchanged; tied lines 190 to 220. `trust_map.py --check` passes before and after (against
`ee4ae48ad` and the allowances introduced since).

### Declarations no existing theorem ties

Each row names the rd-9 lines (added, or grown from n) and the theorem that would tie it. None was written here: the
task allows ties to existing theorems only, and no trusted code was added to make up for one.

| File | Declaration (rd-9 lines) | Why no existing theorem ties it | A theorem that would |
| --- | --- | --- | --- |
| `ResponseShape/Schemas/NormDefaults.lean` | `file` (+1 of 20), `soft_admission` (+13) | Response shapes: no dumped theorem names them; the encoder theorems read the generated JSON through `skel%`, not these declarations, and are outside the dump | A dumped theorem that the encoder's `skel%` shape is this declaration's render, with the encoder theorem; even then it fixes the answer's form only |
| `ResponseShape/Schemas/ReadingsRoute.lean` | `soft_premises` (+18), `filledFieldsS` (+5), `elaborate` (+2), `validate` (+2), `file`, `filled`, `pair`, `verdictsFor` (+1 each) | As above | As above |
| `ResponseShape/Schemas/SoftNorms.lean` | `elaborated`, `file` (+1 each) | As above | As above |
| `VE/NormDefaults/Layered.lean` | `layeredCase` (+1 of 33) | `layered_conflict_sound` and `layered_report_sound` are about the replayed cases, not the dispatch | A wire theorem per kind on `layeredCase`'s answer, as `normDefaults_wire_admission` is on `runCase`'s |
| `VE/NormDefaults/LayeredEntail.lean` | `bindCertX` (+8) | Only `VE.Ask.ndBoundCert_eq` names it, and it defines Ask's binder by it | A binding theorem: `bindCertX … = .ok cert` implies the certificate's premise meaning ids are those of `(premisesX U X A).map enc ++ own`, its conclusion's and its environment id the canonical environment's |
| `VE/NormDefaults/Run.lean` | `softCase` (+12), `runCase` (+5 of 14) | The admission theorems fix `runCase`'s `admission` kind (and so `softCase`'s admission branch); the soft `norm-defaults-certificate` branch and the fall-through are named by no theorem | `runCase j = .ok a`, kind `norm-defaults-certificate` on the soft route, implies `a` is the replayed entailment's `valid` (with `LayeredEntailment.hvalid` and `acceptanceX`); and every other kind's answer is `runOtherCase`'s |
| `VE/NormDefaults/Run.lean` | `softAdmissionWitness` (+3) | A private fixture read only by `#guard`s; no theorem can tie test data | None; it is test data classed G[V] (a classification change for the DRI, not a tie) |
| `VE/Readings/ComponentsWire.lean` | `PartRun.answer` (+2 of 4) | No theorem names it | A theorem that a component's answer is `ndVerdictsAnswer` of the component's rows (as for the document) |
| `VE/Readings/Doc.lean` | `Chain.text` (+5) | `chainText_fits` (an encoder theorem, outside the dump) fixes only that the text is one of three | A round trip with the client's chain names (`Chain.text` injective onto `norms`, `soft`, `rights`) in the dump |
| `VE/Readings/Run.lean` | `PairFacts` (+1 of 11), `pairFactsSpec` (+1 of 13) | See the rejected candidates | A field-wise statement that each fact is S1's check on the replayed pair (`separated` is `separates …`, `witnessValid` is `sideValid …`, and so on) |
| `VE/Readings/Run.lean` | `pairFactsS` (+20), `ndPairFacts` (+13 of 21), `setPairsBy` (+24), `setPairsS` (+5), `sideAtS` (+5), `sidesOfS` (+4), `sideInS` (+3) | The docstrings cite `readings_wire_sd_separate_sound` and `readings_wire_nd_separate_sound`, but those are about the replays (`replaySeparateS`), and no theorem states that the runner's `separated` is `separatesS` | `pairFactsS r fa side s sid other = .ok p`, with `side` the filled sides, implies `p.separated = separatesS …` and the witness facts are its completion's (as `pairFactsIn_eq` is for S1); for the set, every emitted pair is a pair of the set with those facts, in index order |
| `VE/Readings/Run.lean` | `runChoiceSD` (+22), `runElaborateSD` (+12), `runSeparateSD` (+8), `runValidateSD` (+6), `validateResultBy` (+15), `sdRefusal` (+5), `runOne`, `runS2ND`, `validateOne` (+3 each) | The soft-chain wire theorems (`readings_wire_sd_*`) are stated on the replays (`ChoiceReplayS`, `SDVerdicts`), not on the runners' answers; `validateBy_rows` is an encoder theorem (form only, outside the dump) | Runner-level wire theorems, as `normDefaults_wire_admissionX` is for `runCase`: e.g. `runChoiceSD id r j = .ok a` with `accepted` true implies `EntailsX (choiceU r.N c) (choiceX r.N c) …` |
| `VE/Readings/Run.lean` | `filledFieldsS` (+5), `filledJsonS` (+9), `softPremisesJson` (+7) | Wire encoders; no theorem relates the JSON to the values it encodes | A decoder round trip: decoding `soft_premises` gives `softXL` of each reading's side, and `filled` gives the filled environment and units |
| `VE/Readings/SoftDefaults.lean` | `choiceX` (+2), `freeX`, `oneX` (+1 each) | Named by theorems only as arguments, or (`choiceX_normsShaped`) for one case; with `softX` tied it is no longer an anchor for them | An equation with soft-norms' premises, as `softPremisesIn_fill` is for `softX` (e.g. `choiceX N c = softPremisesIn (correlate (choiceDoc N.D c).1) …`) |
| `VE/Readings/SoftDefaults.lean` | `softXL` (+2) | `softPremisesIn_fill` fixes its formulas through `softX`, not its labels | An equation of the labelled list with soft-norms' labelled premises |
| `VE/Readings/SoftVerdicts.lean` | `runVerdictsSD` (+24) | The `readings_wire_sd_verdicts_*` theorems are about the replay `SDVerdicts` | A runner-level statement that its answer's rows are the replay's (as `xInfos_rows` is for the rows of `XVerdicts`) |
| `VE/Readings/SoftWire.lean` | `admitSDOf` (+22), `admitSD` (+6), `AdmittedSD` (+7) | `AdmittedSD`'s fields carry its invariants (`hN`, `wf`, `side`), but a structure's own text cannot tie it, and no theorem names the admission functions | `admitSDOf b = .ok r` implies `r.N = ⟨b.D, unspecOf b.a.re b.D⟩` (the invariants come with the type); and a document it refuses is not `softShaped` or fails `WellFormedSD` |
| `VE/Readings/SoftWire.lean` | `sdChoiceText` (+6), `underSoftCompletion` (+3) | No theorem names them; `underSoftCompletion` is spec 3's condition itself | `sdChoiceText re N c = none` implies `WellFormedU (choiceU N c)` (as for `ndDocTextG`); for `underSoftCompletion` none: it is the spec's condition, so a classification question for the DRI, not a tie |
| `VE/Readings/UnspecifiedWire.lean` | `choiceCertificateX` (+20), `choiceModelX` (+13), `choiceInnerX` (+11), `runChoiceND` (+1 of 25) | The choice theorems are on the replay (`ChoiceReplayS`), not on these runners | A runner-level acceptance theorem: `choiceCertificateX re L A inner = .ok fields` with `valid` true implies `EntailsX L.U L.X (A ++ Γ) φ`; `choiceModelX` that a returned model is `BaseAdmissibleX` with its filling |
| `VE/Readings/UnspecifiedWire.lean` | `unitsJsonOf` (+9), `filledJson` (+2 of 10), `decisionCount` (+2) | Wire encoders and a count for a limit; `unitsJsonOf_fits` and `filledUnits_fits` fix form only and are outside the dump | A decoder round trip for the units; `decisionCount` is a limit's input (it only refuses) and needs none |
| `VE/Readings/VerdictsWire.lean` | `xEvidenceOf` (+70, generalising `ndEvidenceOf`, 71 to 11), `xFilled` (+8) | Evidence decoding: the `XVerdicts` theorems take the decoded evidence as given, as the earlier `ndEvidenceOf` was untied | A decoder theorem: each piece in the evidence is bound by `bindCertX`, decoded by `situationX L` and `decodeFilling`, and each refused piece is absent with its refusal noted |
| `VE/Readings/VerdictsWire.lean` | `verdictsRequest` (+16), `VerdictsRequest` (+12), `ndVerdictsAnswer` (+8), `overInfos` (+6), `rowInfoOf` (+6), `xInfos` (+4) | Request reading and answer assembly; `xInfos_rows` leaves `notes` free (see the rejected candidates) | `xInfos_rows` extended with `(xInfos x).map (·.notes) = x.notes` padded with `[]`; a round trip for the request's members |
| `VE/Readings/VerdictsWire.lean` | `partDecided`, `readingPremise` (+12 each), `documentOrder` (+7) | Moved from `ComponentsWire.lean` (its -29); no theorem named them there either | A theorem that a decided unit is one whose rows are all decided (`fixedDecided` over `foldConflict` and `foldPremises`) |
| `VE/Readings/VerdictsWire.lean` | `pairGapsOn` (+6) | The gaps are a diagnostic over unsaid atoms; no theorem names it | A gaps soundness theorem: each listed atom is an `unsaid` atom the probe formula reads, with its value in the model |

### Seeded ties (each restored; `trust_map.py --check` exit 1)

| Seed | Temporary change | Failure |
| --- | --- | --- |
| T1 | `premisesX` tied to an unrelated theorem (`VE.Readings.softX_strict`) | "the statement of VE.Readings.softX_strict does not mention VE.NormDefaults.Wire.premisesX"; with it, `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check` fails |
| T2 | `softPremisesIn_fill`'s `-- uses` line without `VE.Readings.softX` (`lean/statements.txt`) | "the statement of VE.Readings.softPremisesIn_fill does not mention VE.Readings.softX" |
| T3 | `runAdmissionX_sound`'s `-- uses` line without its anchor `AdmissionAnswerX` | "mentions no K, S or untied [V] declaration of the tree, validly classified, to tie it to" |
| T4 | `probeFormulaOn` tied to an encoder theorem (`ResponseShape.Encoders.ReadingsRoute.setPairsBy_entries`) | "tying theorem … is not in statements.txt" |

## Verification to date

- `PATH=~/.elan/bin:$PATH lake build`: PASS, 890 jobs.
- `PATH=~/.elan/bin:$PATH python3 lean/audit.py --write` and the plain `python3 lean/audit.py`: PASS, 483 source files, 5,281 named theorems, standard axioms only.
- `tools/lean_statements.py` through `regen_generated.py`: 29 added theorem statements, 0 removed, 0 changed; 4,831 statements total. `tools/check_readings_defaults_statements.py`: existing RD-1, RD-2a, RD-3, RD-4a/b, RD-6a/b statements pass unchanged.
- `tools/check_rd9_sc1_statements.py`: 48 implemented SC-1 declarations match the approved text; `softX_wellFormed` remains unbuilt.
- `VE/Route/frozen.py`: PASS after regeneration; frozen source files unchanged.
- `tools/assurance_manifest.py --check` and the selected `tests/test_assurance_manifest.py`: PASS after reviewing and updating the two whole-file decoder pins.
- Selected tests (`select_tests.py --base $(git merge-base HEAD main) --run`): the first run selected 81 units and failed while generated inventories and `ve_service` pin were stale. It also could not write the test-map cache under the sandbox's read-only home cache. The pin and inventories have since been regenerated. A targeted rerun of selected norm-defaults and consolidation cases produced 23 pass and one classification failure; the classification failure passed after adding the new declarations to `tools/trust-classes.json`. A later pre-commit selection of 81 units found two stale assurance decoder pins; both were corrected. On commit `ed42c25d` the selector ran all 358 units: 357 passed, and `tests/test_readings_defaults_rd6b_report.py::test_trust_growth_is_rd6b_entry_and_listed_for_signature` failed because `docs/trust-baseline.json` still pins the approved base. This is intentionally left unsigned pending DRI review. The wire-gate corpus unit passed.
- Full release gate: **not run**. It is reserved for the committed final RD-9 HEAD, which this is not.

### Seeded bugs removed

Each temporary mutation was made in `LayeredEntail.lean`, `lake build VE.NormDefaults.LayeredEntail` exited 1, and the file was restored. The restored target builds successfully. The mutation logs were saved under `/tmp/rd9-mutant-*.log` during this run.

| Seed | Temporary bug | Failing Lean check |
|---|---|---|
| M1 | Omit `X` from `premisesX` | `acceptanceX` proof, line 38 |
| M2 | Omit `X` from the conflict certificate premises | `conflictFreeCheckX_sound` proof, line 83 |
| M3 | Replace `extraValid U X M F` with `true` | `modelCheckX_sound` proof, line 113 |

## Build checklist (current increment)

1. Not applicable yet: no diagnostic, limit, or decoder contract changed.
2. Not applicable yet: no three-language contract surface changed.
3. Not applicable: no text normalization changed.
4. Not applicable yet: the existing certificate decoder and binder are reused; no response schema changed.
5. Not applicable: no new JSON decoder or referenced-id lookup.
6. Not applicable yet: no public verdict route enabled.
7. Not applicable: no new public operation or deadline.
8. Not applicable: no kind or owner fold changed.
9. Not applicable: no English rendered or parsed.
10. Not applicable: no entry point changed.
11. Done: Lean compiler is the oracle for the new declarations; no language regex was added.
12. Not applicable: no ledger or state machine changed.
13. Done for this increment: three seeded mutations each failed a Lean proof check; all were removed.
14. Done for the new checker: it reads the spec and Lean source only. Selected tests use cache paths under `/tmp` in this sandbox. The first attempt without those paths failed before running tests.
15. Done for the binder change: existing full-envelope certificate binding is preserved with `X = []`; no identity field was added.
16. Done for the current declarations: audit, statement, declaration, predicate, frozen-source and checker-pin inventories regenerated, and both affected assurance decoder pins reviewed and updated.
17. Done for the implemented SC-1 declarations: the new checker compares all 48 against the approved text and lists the one unbuilt theorem. The later batches remain not done.
18. Not done: SC-1 acceptance fixtures have not been added, although SC-0's scratch stub contains computed fixture values.
19. Not applicable yet: no use-case formalisation changed.
20. Not done: this progress report's measurements are not backed by a saved-evidence report test.
21. Done for this report: implemented proofs/build are AGENT; SC-0 review and SC-6 amendment are HUMAN/DRI, deferred to the DRI; SC-9 source audit is EXTERNAL, deferred to SC-9.
22. Not done: final clean-HEAD gate awaits completion of RD-9; this increment has an open trust-budget failure. Disk space was checked (65 GB available).
23. Not done: no user-visible delta is enabled; the new trusted-line allowance needs a DRI signature before acceptance.
