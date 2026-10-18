# pk-1: premise packs (build report)

**DRI decision needed on one approved statement, not on this item's code: the approved `legacy_labels_nodup`
(`docs/spec/premise-packs/SpecStubs_pk1.lean:163`) is false.** The mechanised counterexample is fixture F1′ in
`lean/VE/NormDefaults/PacksLegacyExamples.lean`: a document `cx` with limitations `x` and `x:p` and act keys `p:q`
and `q`. It satisfies `WellFormedRights cx` and `WellFormedU`, yet two of its labels are both
`rights:limitation:x:p:q:necessary:c`. The cause is that `WellFormedRights` checks neither limitation names nor
predicate names for `:`. Decoded documents never reach this case, because the JSON environment decoder requires
predicate names to be identifiers (`Route/Wire.lean:98`). As spec 6 requires, pk-1 adds no hypothesis. The statement
moves to pk-1b with its sibling `softLabelledU_labels_nodup` (proved). A candidate repair, proved on local branch
`wip/pk-1b-labels` (e415f9c32, file `lean/VE/NormDefaults/PacksLabels.lean`), is
`legacy_labels_nodup_of_actKeys`: the same statement plus `(hk : ∀ k ∈ VE.Rights.condKeys R, ':' ∉ k.2.1.toList)`.
F1′ also checks that `hk` fails on `cx`. Nothing in pk-1 uses either theorem: `assemble_legacy_soft/rights` take
distinctness as a hypothesis. The item has no DELTA row reserved for the DRI.

Branch `feature/pk-1`, base `main` 93131f967. Spec: `docs/spec/premise-packs.md` (pk-1s, statement review
accepted, merge 49a926ee7). DRI-DECISIONS-PHASE2 rows DF4, DF7 and JT-R2.

## 1. What was built

| Spec row | Delivered | Where |
| --- | --- | --- |
| 2.1–2.4: `PackKind`, `RequestPath`, `Pack`, `packOrder`, `reservedPrefixes`, `reserved`, `ownPrefix(In)`, `ordered`, `labelledX`, `X`, `names`, `packPremises`, `extendEnv`, `fullEnv`, `envX`, `firstRepeat`, `declaredIn`, `assembleIn`, `assemble` | yes, bodies as the stub | `lean/VE/NormDefaults/Packs.lean` |
| 2.5: `extendEnv_nil`, `envX_nil`, `assemble_order`, `assemble_fresh`, `assemble_nil` | proved | `Packs.lean` |
| 2.5: `assemble_wellFormed` | proved | `PacksLegacy.lean` (it uses `Readings.wf_sub`, see 3) |
| 2.6: `softPack`, `rightsPack`, `legacyIds`, `X_legacy`, `legacy_take`, `legacy_drop`, `packPremises_absent`, `X_soft_first` | yes, proved | `Layered.lean`, `Packs.lean` |
| 2.6: `assemble_legacy_soft`, `assemble_legacy_rights`, `packPremises_legacy` | proved | `PacksLegacy.lean` |
| 2.6: `softLabelledU_labels_nodup`, `legacy_labels_nodup` | **not in pk-1**: the first is proved and the second is false as approved; both move to pk-1b (size cut, see 5) | `wip/pk-1b-labels` |
| 2.7: `labelledJson`, `elaborateArrays`, `elaborateArrays_keys`, `elaborateArrays_legacy`; `layeredElaborate` uses `elaborateArrays` | yes, proved | `Packs.lean`, `Layered.lean` |
| 2.7: `packEntry`, `furtherEntries` | not in pk-1 (spec: with the first provider, AT-2) | — |
| 2.8: `firstFailing`, `packFault`, `firstFailing_some`; `filledX` throws `packFault` | yes, proved | `Packs.lean`, `Layered.lean` |
| 2.8: `packFault_legacy_rights`, `packFault_legacy_soft` | proved | `PacksLegacy.lean` |
| 2.9: `xWithout`, `coherenceLabels`, `xWithout_nil`, `xWithout_sub`, `filledX_whole` | yes, proved | `Packs.lean`, `PacksLegacy.lean` |
| 2.10: kind table, `dispatch_legacy` | pk-1b (spec 5) | — |
| 2.11: `transfers_append`, `transfers_X` | proved | `lean/VE/Readings/SupPacks.lean` |
| `LayeredU.packs` replaces `labelled` and `rightsCount`; `LayeredU.X := Packs.X L.packs` | yes; the old fields and every take/drop over them are deleted (one owner of X's order) | `Layered.lean`, `LayeredAdmission.lean`, `Readings/UnspecifiedWire.lean`, `Readings/VerdictsWire.lean` |
| Decoders through `assemble` (used = `checkAuthorN`'s count) | yes; the count is `Wire.authorVocab`, the one owner, which `checkAuthorN` now reads too | `Layered.lean`, `NormDefaults/Wire.lean` |
| Norms chain `[]`, soft chain `[softPack U (correlate X)]` | yes; `choiceLayeredG_norms_packs` states the empty list | `UnspecifiedWire.lean`, `PacksLegacyExamples.lean` |
| Encoder theorem unchanged in statement | `layeredCase_fits` unfolds `elaborateArrays` and `labelledJson` | `ResponseShape/Encoders/NormDefaults.lean` |
| Fixtures A1–A9 (pk-1's part), A9′, F1; corpus L1, L2 | yes (see 2) | `PacksExamples.lean`, `PacksLegacyExamples.lean`, encoder file, `evidence/` |

All 24 theorems pk-1 delivers from the stub (10 of the 13 `sorry` statements, plus the 14 the stub already proved)
match the stub's statements token for token, after whitespace normalisation. The three not delivered are
`softLabelledU_labels_nodup` (proved, moved to pk-1b), `legacy_labels_nodup` (false) and `dispatch_legacy` (pk-1b). Helper theorems added: `assembleIn_ok`,
`filterMap_find_ids`, `mem_filterMap_find`, `filterMap_congr`, `filterMap_find_perm`, `firstRepeat_none`,
`packPremises_sub`, `X_single` (Packs.lean); `lookup_mem`, `lookup_flatMap_mem`, `lookup_flatMap_none`,
`names_unique`, `firstRepeat_none_of`, `assembleIn_constraint`, `firstFailing_one`, `firstFailing_two`
(PacksLegacy.lean).

## 2. Evidence

- **L1/L2 (byte identity)**, using `tools/lean_output_diff.py`. The baseline is `main` 93131f967's executables, built
  in a separate worktree. The head `ve_service` digest is `1a239a2f…`, the final HEAD's (commits after c7932eeac
  change no executable).
  - The full differential covered every conformance corpus plus the Lean sessions recorded at head from 17 test
    files (the layered, transport, soft-kinds, report and switch tests, rd9 chain/split, readings sd/nd/sup-verdicts,
    readings-defaults English, agent-policy unspecified).
  - Result: 452 invocations, 378 run on both builds, **0 differences** (`evidence/ab_full.txt`). The recorded
    sessions carry 279 elaborate, 715 conflict, 219 status, 2,705 report and 55 certificate `norm-defaults` cases,
    plus about 900 readings cases (`evidence/ab_recorded_kinds.txt`). They include both `InvalidModel(rights)` and
    `InvalidModel(soft)` cases.
  - The 33 `norm-defaults` cases of `tests/data/route-cases.jsonl`, one session each: 0 differences
    (`evidence/ab_route_cases.txt`).
- **A1–A9, A9′, F1, F1′**: `#guard`s in `PacksExamples.lean`, which imports `Packs.lean` alone, and in
  `PacksLegacyExamples.lean`, which covers today's rights documents in both list orders, `envX`/`fullEnv` on a real
  tree, F1 and F1′. The A9′ guards read `layered_elaborate`'s closed keys and sit beside `layeredCase_fits`.
- **Tests**:
  - Selected run on the Mac runner (`mac-pytest.sh --select`, HEAD 5cde0da3, 347 units, the whole suite because
    `checkers.lock` and `Audit.lean` changed): every unit passed except `test_trust_budget` and `test_trust_ratchet`,
    which were failing because the allowance was not yet recorded.
  - After recording the allowance (573e19f50) and the size cut (d21c1c3c7), 26 trust/statement/audit test files plus
    `tests/test_rd9_statements.py` and `tests/test_norm_defaults_layered.py`: 1,602 passed.
  - `tools/regen_generated.py --check`: 31 entries checked, no failure.
  - `tools/gate_collection.py --check --prebuilt`: 3 tests added, 0 removed.
  - Not run by me: the full gate (the chain runs it on the final HEAD).
- **Pre-existing failures** (`main-known-red.txt`): the two sub-tick deadline tests and the rd8 report test. They
  were not hit and not touched.

## 3. Deviations from the spec's build plan (statements unchanged)

1. **`PacksLegacy.lean`** imports `VE.NormDefaults.Layered` and `VE.Readings.SupWitness` (for `wf_sub`, used by
   `assemble_wellFormed`, which is placed here rather than in the core so that no weakening lemma is copied). Neither
   `LayeredAdmission.lean` nor `UnspecifiedWire.lean` imports it. `decodeSoftU_source` gets `L.packs = [softPack …]`
   from `assemble_order` (the order of a one-pack list), so it does not need `assemble_legacy_soft`.
2. **`NormDefaults/Wire.lean`** gains `authorVocab`, the vocabulary `checkAuthorN` charges. Both `checkAuthorN` and
   the two `assemble` calls read it, so the count has one owner. This file was not in the spec's hunk table. No
   in-flight branch edits it.
3. **`Readings/VerdictsWire.lean`**: `xEvidenceOf` reads `Packs.labelledX L.packs` where it read `L.labelled`. This
   one-line hunk was missing from the spec's table. It is byte-identical (A/B above).
4. **A9′** lives in `ResponseShape/Encoders/NormDefaults.lean`, not in `PacksExamples.lean`, because
   `tools/layer_policy.py` puts `ResponseShape` at layer 4 and `VE.NormDefaults` at layer 2. A9's
   `furtherEntries` rows are AT-2's.
5. **The fixtures are in two files**, so that a mutant of the core rebuilds two files instead of the Readings
   tree.
6. **`choiceLayeredG_norms_packs`** (PacksLegacyExamples.lean) states that the norms chain's source has the empty
   pack list. Without it, the spec's seeded bug "the soft pack on the norms chain" changes no output, since that
   pack's premises are `[]`, so nothing would catch it.
7. **`tools/check_rd9_sc1_statements.py`** gains `SUPERSEDED`: `SoftLeafX`'s approved RD-9 text with PK-1's one
   quoted edit (spec 5, LayeredAdmission row). The checker reports it as "APPROVED by a later statement spec",
   never as DRI-signed. Tests: `tests/test_rd9_statements.py::test_soft_leaf_reads_the_soft_pack_as_the_premise_packs_spec_approves`
   and `::test_a_soft_leaf_other_than_the_approved_edit_fails`.
8. **`ve/assurance-manifest.json`**: the five edited decoder files are repinned whole, and `Packs.lean` is listed
   under `other_json` as encoder only (it reads no request JSON).

## 4. Seeded bugs

All are in `mutants.json` (file, edit, test, the first errors). M1–M6 are also run against the guards with
`Packs.lean`'s theorems stripped. An unmutated control passes every guard.

| Bug | Language, file | Fails |
| --- | --- | --- |
| M1 `packOrder` with rights first | Lean, `Packs.lean` | A1 guard; `X_soft_first` |
| M2 `firstRepeat` without the seen list | Lean, `Packs.lean` | A3 guards (and A4 "declared twice"); `firstRepeat_none` |
| M3 `declaredIn` ignoring constants | Lean, `Packs.lean` | A4 guard (author constant `date__d`); `assemble_fresh` |
| M4 `packFault`'s legacy branch removed | Lean, `Packs.lean` | A7 guards; `packFault_legacy_*` |
| M5 `elaborateArrays` writing a further pack's entry | Lean, `Packs.lean` | `elaborateArrays_keys`; A9 guard |
| M6 vocabulary limit `> 257` | Lean, `Packs.lean` | A6 guards (255 + 2 names); `assembleIn_ok` |
| M7 the soft pack on the norms chain (proofs adjusted so it compiles) | Lean, `Readings/UnspecifiedWire.lean` | `choiceLayeredG_norms_packs` |
| M8 the rights route dropping its rights pack | Lean, `NormDefaults/Layered.lean` | `tests/test_norm_defaults_layered.py`: 3 failed (rights premises bind fillings, fixtures agree, packages bound), through a rebuilt and temporarily pinned `ve_service`; restored |
| M9 `SoftLeafX`'s approved edit naming the rights pack | Python, `tools/check_rd9_sc1_statements.py` | `tests/test_rd9_statements.py`: 4 failed; restored |

No Rust or Python product file changed. M9 is in tooling.

## 5. Size and trust

- **Trust** (R16, DELTA T1): V +78. `Packs.lean` +73 and `Layered.lean` +5; K +0, S +0. Five definitions are
  tied to their theorems. The allowance is recorded; FOLLOW-UPS "## pk-1" asks for the ties pass.
- **Size.** Changed lines outside generated files, `git diff --numstat main...HEAD`:

  | Kind | Lines |
  | --- | --- |
  | Lean, total | about 1,050 |
  | of which `Packs.lean` | 435 (about 150 definitions and 285 proofs) |
  | of which `PacksLegacy.lean` | 266 (proofs) |
  | of which the fixture files | 209 |
  | of which `SupPacks.lean` | 35 |
  | of which the edits to existing files | about 100 |
  | Python (tooling and test) | 51 |
  | JSON ledgers and pins | about 130 |
  | Evidence | 285 |

  This is over the ~600 guideline. Moving the two label theorems (207 lines) to pk-1b is the cut I made. What
  remains cannot be cut further without dropping spec theorems that the core's ties rely on.

## 6. Pilot bytes expected to move

None: every output on today's routes is byte-identical (section 2). Nothing is claimed before a pilot audit.

## 7. Next items

- **pk-1b**:
  - the kind table (spec 2.10: `KindRow`, `dispatch`, `legacyKinds`, `legacyRows`, `dispatch_legacy`);
  - `softLabelledU_labels_nodup` (proved, on `wip/pk-1b-labels`);
  - `legacy_labels_nodup` in whatever form the DRI approves.
- **Providers, in SYNTHESIS 4.2's order**: AT-2/AT-3a (the first provider, with `packEntry`, `furtherEntries` and
  their shape row, `ExpandsOn` and `OriginsExact`), then WG-3, ET-4 and QT-B2.

Evidence commit list (`git log --oneline main..HEAD --no-merges`, before this report's commit): b30b12f74,
df50d5b7c, c7932eeac, 5cde0da38, 573e19f50, d21c1c3c7.

## Self-review against BUILDER-CHECKLIST

1. **Every Lean answer typed and contained.** N.A.: no response shape, schema or relay changes. The elaborate keys
   do not depend on the packs: `elaborateArrays_keys`, `layeredCase_fits`, and the A9′ guard.
2. **Every required deliverable built.** PASS: table in 1. The rows not built are moved by the spec (pk-1b, AT-2)
   or are the false statement. Rule grep: no Python copy of a Lean decision, and no permanent report test.
   Overlap: only `lean/VE.lean` (union-merged) and the generated trust ledger are shared with in-flight branches.
3. **Tests and gates can fail.** PASS: M1–M9 in `mutants.json`, with the guard-only control.
4. **Python, Lean and Rust agree; valid inputs pass.** PASS: `evidence/ab_full.txt` and
   `evidence/ab_route_cases.txt` (0 differences). Rust is untouched (`rust/target/release/ve` repinned unchanged,
   `6422647f…`).
5. **R8 binding.** N.A.: no new relayed field. Origins and their binding land with AT-2.
6. **Gate evidence matches the final HEAD.** PASS: the chain gates the committed final HEAD. The evidence commit
   list above comes from `main..HEAD --no-merges`. `ve_service`'s digest is unchanged since the A/B run.
7. **No unsigned item.** PASS: DELTA T1 cites R16 with its evidence. The false statement is a theorem-statement
   decision, listed in this report's first line, and is not a DELTA row.
8. **Every user-visible change in DELTA.** PASS: the base/head diff is empty (`evidence/ab_full.txt`), and DELTA
   says so. The new `assemble` texts are unreachable from today's decoders (DELTA prose).
9. **Test selection.** PASS, with a note: `select_tests` picks all 347 units because `checkers.lock` and
   `Audit.lean` changed (known; see the merge recipe). M8's failing file, `tests/test_norm_defaults_layered.py`, is
   in that selection.
10. **Lean statements say what is claimed.** PASS:
    - token-for-token comparison with the stub (24 same, 0 different);
    - `tools/check_rd9_sc1_statements.py` and `tools/check_readings_defaults_statements.py` pass;
    - every mutant M1–M7 breaks a theorem or guard about the returned value.
11. **Budgets and limits fail closed.** PASS: A6 guards at 254+2, 255+2, 256 and 257; `assemble_fresh` states
    `used + names ≤ 256`. There are no deadlines.
12. **No CPU or memory regression.** N.A.: `assemble` walks a list of at most two packs once per check, with no
    eager enumeration. No pilot was timed, because whole-UDHR runs are forbidden (L70). The A/B ran both builds over
    the same 378 invocations with none timing out.
13. **Test-removed trailers.** PASS: `tools/gate_collection.py --check --prebuilt` reports 17,321 collected, 3 added,
    0 removed, 0 refused, 0 stale and 0 malformed.
