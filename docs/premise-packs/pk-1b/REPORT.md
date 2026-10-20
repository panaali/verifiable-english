# pk-1b: the premise-pack kind table (build report)

**No DRI signature is reserved or needed.** The statement gate passed: `dispatch_legacy` and
`softLabelledU_labels_nodup` equal the stub (`docs/spec/premise-packs/SpecStubs_pk1.lean:352`, `:157`) token for
token after whitespace normalisation. `legacy_labels_nodup` is out of scope: it is false as approved (pk-1's F1′) and
waits for the DRI. This item does not build, restate or use it; it is pk-1c.

Branch `feature/pk-1b`, synced with `main` 20aa836fd (merge df010a1ae). Spec: `docs/spec/premise-packs.md` 2.6, 2.10
and 5 (pk-1s, reviewed). Other inputs: SYNTHESIS 2.1 and 4.2, DRI-DECISIONS-PHASE2 DF4, DF7 and JT-R2, and
`docs/premise-packs/pk-1/REPORT.md`.

## 1. What was built

| Plan row | Delivered | Where |
| --- | --- | --- |
| 2.10 `KindRow`, `dispatch` | yes; the bodies are the stub's | `lean/VE/NormDefaults/Packs.lean` |
| 2.10 `legacyKinds`, `legacyRows` | yes; the rows call `layeredCase` (see 3.1) | `lean/VE/NormDefaults/Layered.lean` |
| 2.10 today's dispatch replaced by the table | yes: `runLayered` calls `kindCase` (`Packs.dispatch legacyRows` over the source's pack ids) | `Layered.lean` |
| 2.10 `dispatch_legacy` | proved | `lean/VE/NormDefaults/PacksLegacy.lean` |
| 2.6 `softLabelledU_labels_nodup` | proved; taken from `wip/pk-1b-labels` e415f9c32 (the soft theorem and its helpers only; not the candidate repair) | `lean/VE/NormDefaults/PacksLabels.lean` (new) |
| Encoder (spec 5: "unfold `dispatch`, `legacyRows`…") | `runLayered_fits` rewrites with `kindCase_eq`; `layeredCase_fits` is unchanged | `lean/ResponseShape/Encoders/NormDefaults.lean` |
| Fixtures for each new definition | `#guard`s: `dispatch` on fixture rows in `PacksExamples.lean`; `kindCase` against `layeredCase` on a source decoded by the real `decodeSoftU` (DF-1a's γ) in `PacksLegacyExamples.lean` | both fixture files |
| Seeded bugs (spec 5: "`dispatch` running a row whose pack is absent") | M1 (that bug) to M4, plus 9 guard mutants | `mutants.json`, `tests/test_packs_guard_mutants.py` |
| `python3 lean/audit.py`, `tools/regen_generated.py --check` | both pass | — |
| `legacy_labels_nodup` | **not in this item** (out of scope; pk-1c) | — |
| df-1ab's `defaultsCase` row (DF4) | not in this item: it is df-1ab's row, and it comes after this table | — |

Helper theorems added: `layeredCase_some` and `kindCase_eq` (`PacksLegacy.lean`). `kindCase_eq` states that `kindCase`
answers every kind exactly as `layeredCase` does. `PacksLabels.lean` adds 13 `pk_*` helpers for the labels theorem,
unchanged from the wip branch.

## 2. Evidence

- **Byte identity.** Proved for every input: `runLayered` computes `kindCase`, which equals `layeredCase`
  (`kindCase_eq`), today's call.
  - Measured with `tools/lean_output_diff.py --build --recorded`. The base is main 20aa836fd's executables (the
    `ve-share-main` build of that tree), the head this branch. 445 invocations, 366 run on both builds, **0
    differences**, 0 timed out (`evidence/ab_full.txt`).
  - Coverage: every conformance corpus, plus the `ve_service` sessions recorded at head by 8 test files (the layered,
    report, soft-kinds and switch tests, readings nd/sd/s2, and alternatives fill).
  - Those sessions hold 76 `norm-defaults-elaborate`, 54 `-conflict`, 93 `-status`, 2,693 `-report` and 68
    `readings-choice` cases (`evidence/ab_recorded_kinds.txt`).
- **Statement gate.** All three compare equal to the stub after whitespace normalisation: the statements of
  `dispatch_legacy` and `softLabelledU_labels_nodup`, and the bodies of `KindRow`, `dispatch` and `legacyKinds`.
  `legacyRows` differs only in how names are qualified (`Packs.KindRow` and `layeredCase` inside
  `VE.NormDefaults.Wire`), which names the same constants. `tools/check_rd9_sc1_statements.py` and
  `tools/check_readings_defaults_statements.py` pass.
- **Tests.**
  - Selected run on the Mac runner (`mac-pytest.sh --select`, HEAD ff08c8b3c, 401 of 453 units, wide because
    `checkers.lock` and `Audit.lean` changed): 399 files passed and 1 failed.
  - The failure was `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`: the two
    fixture files now build JSON. 7c0c9cf90 classifies them, and `tests/test_assurance_manifest.py` then passes
    (137).
  - `tests/test_packs_guard_mutants.py`: 44 passed (41 mutants, 3 checks).
  - `tools/gate_collection.py --check --prebuilt`: 9 added, 0 removed, 0 refused, 0 stale and 0 malformed.
  - Not run by me: the full gate (the chain runs it on the final HEAD).
- **Pre-existing failures** (`main-known-red.txt`: the two sub-tick deadline tests and the rd8 report test) were
  not hit and not touched.

## 3. Deviations from the spec's build plan (statements unchanged)

1. **`layeredCase` keeps its name and body; the table's dispatch is the new `kindCase`.** Spec 2.10's prose renames
   today's `layeredCase` to `legacyCase` and makes `layeredCase` the dispatch. The stub's `legacyRows` and
   `dispatch_legacy` name `VE.NormDefaults.Wire.layeredCase`, meaning today's function. Under the rename, the
   unchanged text of `dispatch_legacy` would compare the table with itself; changing its text would change an
   approved statement. Keeping the name keeps both the text and the meaning, and `kindCase_eq` closes the loop. Also,
   `legacyKinds` and `legacyRows` sit after `layeredCase` (which they call), not before it.
2. **`choiceInnerX` (`Readings/UnspecifiedWire.lean`) still calls `layeredCase`.** Its text is approved RD-9 text,
   and `tools/check_rd9_sc1_statements.py` refuses an edit that the premise-packs spec does not approve. Today the two
   dispatches agree on every kind (`kindCase_eq`). The first row that needs a pack (df-1ab's, DF4) must decide
   whether a choice's inner case goes through the table, with its own statement review.
3. **`softLabelledU_labels_nodup` is in `PacksLabels.lean`, not `PacksLegacy.lean`** (the wip file, as the task
   names). It imports `VE.Readings.Labels`, so `PacksLegacy.lean` and its importers (now the encoder file) do not
   gain that import. Nothing imports `PacksLabels.lean` except `VE.lean` and `Audit.lean`.
4. **The encoder file imports `VE.NormDefaults.PacksLegacy`** for `kindCase_eq` (layer 4 imports layer 2;
   `tools/check_lean_imports.py` passes).
5. **No R6 row.** The task expected the replaced dispatch lines to be R6. The table is a layer in front of
   `layeredCase`, and no Python or Rust decision path is deleted, so all growth is R16 (DELTA T1).
6. **`PacksLegacyExamples.lean` imports `VE.Defaults.Examples`** (same layer) to reuse DF-1a's decoded fixture γ,
   rather than copying its JSON builders.

## 4. Seeded bugs

All are listed in `mutants.json`. M1 to M4 were planted in the real files and removed, and the tree was rebuilt and
repinned afterwards. Only Lean product code changed (no Python or Rust product file), so every bug is in Lean.

| Bug | Language, file | Fails |
| --- | --- | --- |
| M1 `dispatch` runs a row whose pack is absent (spec 5's bug) | Lean, `lean/VE/NormDefaults/Packs.lean` | `PacksExamples.lean:124` `#guard` (`weigh` needs the weighing pack) |
| M2 `legacyRows` needs the rights pack | Lean, `lean/VE/NormDefaults/Layered.lean` | `tests/test_norm_defaults_layered.py`: 6 failed (`UnsupportedProfile: case kind norm-defaults-elaborate needs the rights premise pack`), through the rebuilt and temporarily pinned `ve_service`; `dispatch_legacy` (`PacksLegacy.lean:286`); with the two proofs stubbed for that run, `PacksLegacyExamples.lean` guards at lines 89 and 97 |
| M3 `kindCase` over an empty table | Lean, `lean/VE/NormDefaults/Layered.lean` | `kindCase_eq` (`PacksLegacy.lean:300`); guard mutant `kindCase-40` |
| M4 `softLabelledU` repeats its first exception label | Lean, `lean/VE/NormDefaults/Layered.lean` | `softLabelledU_labels_nodup` (`PacksLabels.lean:196`); F1's nodup `#guard` evaluated on the mutated copy |

**Guard mutants per new trusted definition** (R16). `tests/test_packs_guard_mutants.py` now also copies `legacyKinds`,
`legacyRows` and `kindCase`. Each mutant runs with the theorems stripped and must fail at a `#guard` and nowhere else.
The unmutated copy passes every guard.

| Definition | Mutants (test ID suffix) |
| --- | --- |
| `dispatch` | `dispatch-32` (the pack check removed), `-33` (no row throws), `-34` (last row first), `-35` (a row without a pack gives none), `-36` (refusal text) |
| `legacyKinds` | `legacyKinds-37` (drops `norm-defaults-report`) |
| `legacyRows` | `legacyRows-38` (needs the rights pack), `legacyRows-39` (runs the elaborate kind for every row) |
| `kindCase` | `kindCase-40` (empty table) |
| `KindRow` | a type (`TYPES`) |

One mutant is equivalent on today's rows: `kindCase` given `[]` for the source's pack ids. No legacy row needs a
pack. df-1ab's first row with a pack makes it observable.

## 5. Size and trust

- **Trust** (R16, DELTA T1): V +22, K +0, S +0. `Packs.lean` +17 (`KindRow`, `dispatch`). `Layered.lean` +5
  (`legacyKinds`, plus 2 docstring lines). `kindCase` and `legacyRows` are tied, to `kindCase_eq` and
  `dispatch_legacy`. The allowance is recorded, and FOLLOW-UPS "## pk-1b" asks for the ties pass.
- **Size.** Hand-written changed lines, `git diff --numstat $(git merge-base HEAD main)`, without generated files,
  evidence or this report:

  | Kind | Lines |
  | --- | --- |
  | Lean product (`Packs.lean` 19, `Layered.lean` 24, encoder 2, `VE.lean` 1) | 46 |
  | Lean proofs (`PacksLabels.lean` 204, taken from the wip branch; `PacksLegacy.lean` 49) | 253 |
  | Lean fixtures (`PacksExamples.lean` 26, `PacksLegacyExamples.lean` 28) | 54 |
  | Python test (`tests/test_packs_guard_mutants.py`) | 27 |
  | JSON ledgers (`trust-classes.json` 21, `assurance-manifest.json` 10) | 31 |
  | DELTA and `mutants.json` (one mutant per line) | 47 |
  | This report | 171 |

  That is about 630 lines in all, at the ~600 guideline. A third of them is the labels proof that pk-1 moved here
  (204). Nothing is left for a further cut.

## 6. Pilot bytes expected to move

None. Every answer is byte-identical (section 2). Nothing is claimed before a pilot audit.

## 7. Next items

- **df-1ab's kind-table row** (DF4): the `defaults-*` kinds as rows needing the `soft` pack, calling `defaultsCase`.
  It also decides deviation 3.2 (the choice dispatch).
- **pk-1c**: `legacy_labels_nodup`, once the DRI rules (FOLLOW-UPS, "pk-1 DRI decision").
- **ties-pk-1b**: the R16 ties pass (FOLLOW-UPS "## pk-1b").

Evidence commit list (`git log --oneline main..HEAD --no-merges`, before this report's commit): 64c877586, 216093ec0,
ff08c8b3c, 7c0c9cf90.

## Self-review against BUILDER-CHECKLIST

1. **Every Lean answer typed and contained.** N.A.: no response shape, schema or relay changes. `runLayered_fits` still
   holds (rewritten through `kindCase_eq`).
2. **Every required deliverable built.** PASS: the table in section 1. Rows not built are out of scope by the task
   (pk-1c) or belong to df-1ab (DF4).
   - Rule grep: no Python copy of a Lean decision, and no permanent report test.
   - Overlap: of in-flight branches, only `lean/VE.lean` (a union) and `tools/trust-classes.json` (separate lines)
     are shared.
3. **Tests and gates can fail.** PASS: M1 to M4 (`mutants.json`) and the 9 guard mutants
   (`tests/test_packs_guard_mutants.py::test_each_mutant_fails_a_guard[dispatch-32 … kindCase-40]`), with the
   unmutated control (`::test_the_unmutated_copy_passes_every_guard`).
4. **Python, Lean and Rust agree; valid inputs pass.** PASS: `evidence/ab_full.txt` (0 differences) and
   `kindCase_eq`. Rust is untouched (the binary was rebuilt and is pinned unchanged, `6422647f…`).
5. **R8 binding.** N.A.: no new relayed field.
6. **Gate evidence matches the final HEAD.** PASS: synced with main first; the chain gates the committed final HEAD;
   the commit list comes from `main..HEAD --no-merges`.
7. **No unsigned item.** PASS: DELTA T1 cites R16 with its evidence; no other row.
8. **Every user-visible change in DELTA.** PASS: the base/head diff is empty (`evidence/ab_full.txt`), and DELTA
   says so.
9. **Test selection.** PASS: the selection (401 units) contains `tests/test_norm_defaults_layered.py` (M2's failing
   file) and `tests/test_packs_guard_mutants.py`. It is wide because `checkers.lock` and `Audit.lean` changed.
10. **Lean statements say what is claimed.** PASS: equal to the stub (section 2). M2, M3 and M4 each break the
    theorem about the returned value (`dispatch_legacy`, `kindCase_eq`, `softLabelledU_labels_nodup`).
11. **Budgets and limits fail closed.** N.A.: no budget, limit or deadline is touched.
12. **No CPU or memory regression.** N.A.: one `find?` over four rows per case, with no enumeration. The A/B ran
    both builds over the same 366 invocations, none timing out.
13. **Test-removed trailers.** PASS: `tools/gate_collection.py --check --prebuilt`: 9 added, 0 removed, 0 refused,
    0 stale and 0 malformed.
