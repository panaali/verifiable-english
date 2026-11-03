# ap-3db build report: AP-3's switch-on (the hook, the entry points, D-33), with frames and each act read once

**Status:** deliverables (1) to (5) are built: the hook, every `acts@0` entry point classified, `readings_lexical_only`,
the block's `frames`/`adverbs` (E5j) and each joined act read once. **No DRI signature is reserved.** The DELTA rows
cite the item's ruling (`reviews/dri-decisions-20261102-ap-3db.md` items 1, 3, 4), jt-3p's item 3 (the English
`actions_version` raise), R1 and R16. Trust: K +0, S +15, untied V +107 (trusted +122), under R16. Size: about 1,970
hand-written lines, over the ~600 guideline (section 6). Pilot bytes: 0 until ap-3dc (*estimate*).

Plan: section "AP-3. Joined acts" of the edited plan at `80f056f9e` (the hook, D-33, the relay, the theorem list,
E5j). Spec on main: act-phrases.md 3.1, 3.2, 6.3, 6.4, 10 (D-15 to D-18, D-24, D-28, D-31, D-33) and 11.3 (E5j, A6,
A7, A14). ap-3d's REPORT sections 2, 6, 7 and ap-3r's REPORT read first. Synthesis round 2
(`debates/plan-synthesis-2/edits-act-phrases.md`): this item implements none of its edits (none names the hook, the
entry points, D-33 or E5j).

## 1. Statement gate and the DRI's ruling

- `python3 docs/act-phrases/ap-3db/check_statements.py` prints 6 EQUAL: `decodeElaboratedU_source`,
  `decodeElaboratedU_wellFormed`, `decodeElaboratedU_lexical`, `readings_lexical_only`, `checkAct_lexical`,
  `checkAct_joined`. `decodeSourceU` gets no parameter: it is `decodeSourceUWith true`, and its statements are
  unchanged.
- `tools/lean_statements.py` after the final regen: every recorded statement of the base keeps its text. 72
  statements are added (the `In` forms, the twins, the new lemmas). The 11 field projections of the structures
  `StatusData` and `ReportU` leave the list, because the structures are now `StatusDataIn`/`ReportUIn`, with
  `StatusData`/`ReportU` as abbreviations of them at `decodeSourceU`.
- The DELTA question was asked at the start (msg.sh, 20:29Z) and answered at 20:33Z.
  - Item 1 signs joined acts on routes that run on `e.U'`.
  - Item 2 keeps every path Python reaches on `Lexical.check` until ap-3dc.
  - Items 3 and 4 sign the refusal texts and `frames`/`adverbs`.
  - Item 2 shaped the design: the hook admits a joined act only when asked (`joined`), and only the elaborating
    entry points ask.

## 2. Deliverables (task order)

| Deliverable | Status | Where |
|---|---|---|
| (1) the hook calls `checkAct` under `acts@0`; without the profile byte-identical | **done** | `Norms/Wire.lean`: `canonicalShape` in the hook (conditions 1 to 5 of 1.3), then `actsOf` runs `Acts.Wire.checkAct` once per act (`joinedActs`); without `acts@0` both are `canonicalAct`'s path. The act check and the grammar move to layer 2 (`tools/layer_policy.py`), below the norms decoder. `LexicalProofs`'s `forIn_ok` moves to `Lexical.lean` so that `Grammar` imports no `Readings` module (the cycle `Acts.Grammar → LexicalProofs → Readings.Strings → … → Norms.Wire`) |
| (2) every `acts@0` entry point classified and on `decodeElaboratedU`, twins | **done** | section 3: each runs on `e.U'`, refuses, or is shown not to read the act. Twins: `lean/VE/Acts/DecodeTwins.lean` (section 3.2) |
| (3) `readings_lexical_only`, D-33's text | **done** | `Readings/Wire.lean`: `decodeFrame` (the base's decoder, lexical hook), then `decodeEnvironment` refuses any act `lexicalAct` does not read back (D-33); the theorem is proved from it |
| (4) `frames`, `adverbs` by `decodeVocab` (`checkVocab`, D-31); E5j both sides | **done** | `Acts/Wire.lean` `decodeFrame`, `decodeVocab`; `Norms/Wire.lean` `actsVocab`, `actsFixed` (block fields); `DecodeExamples.lean` E5j |
| (5) review F4 of ap-3d: `checkAct`'s tree carried to `actsOf`, each joined act's readings run once | **done** | `NormsEnvironment.joined` (the decoder's trees); `elaborateSource` reads them, so no grammar runs after the decoder; `canonicalEnvironmentJson` reads no act (`canonicalShape`) |

**Plan rows of AP-3 still open after this item:**
- `elaborate_faithful` is ap-3dd's, already merged.
- The `acts-elaborate` relay, `_lean_route` and the Python refusal belong to ap-3dc. Item 5 of the ruling: ap-3dc lifts
  item 2's guard in the same change.
- `test_reference_table_complete` and the Python display seeded bug also belong to ap-3dc.

## 3. Entry points (spec 6.4's list and the ruling's wider reach)

### 3.1 Classes

**E: runs on `e.U'`.** Each route is generalised over its decoder (`…In dec`). The base's name is the `In` form at the
base's decoder, with its theorem's statement unchanged; the service reaches the `In` form at the elaborating decoder.

- Norms route: `Norms/Run.lean` `runCaseRouted` (from `runCaseReported`, service mode `norms`), i.e.
  `runCaseIn (decoderOf env)`, where `decoderOf` is `Acts.Decode.flaggedSource` under `acts@0`. Each kind is covered:
  - `norms-elaborate`;
  - `norms-certificate`: `Flagged.replayEntailmentIn`;
  - `norms-conflict` with certificates: `replayConflictIn`;
  - `norms-conflict` with a witness: `replayWitnessIn`;
  - `admission`: `Admission.admitDocumentIn`, `runAdmissionIn`.

  Also generalised: `Norms/Flagged`, `FlaggedSpec`, `RunSound`, `Admission`, and the shape proof
  `ResponseShape/Encoders/Norms.lean`.
- Norm-defaults route: `NormDefaults/Run.lean` `runCaseRouted` (from `runGated`, service mode `norm-defaults`), i.e.
  `runCaseIn (decoderOf env)`, where `decoderOf` is `Acts.Decode.elaboratedU` under `acts@0`. Each kind is covered:
  - `elaborate`;
  - `conflict`: `Wire.replayConflictUIn`;
  - `certificate`: `replayEntailmentUIn`;
  - `witness`: `replayWitnessUIn`;
  - `status`: `replayStatusIn`;
  - `gaps`: `replayGapsIn`, `replayReachedIn`;
  - `report`: `reportFromIn`;
  - `admission`: `Admission.admitDocumentIn`.

  The fall-through goes to the norms route's `runCaseRouted`. The shape proof is `Encoders/NormDefaults.lean`.

**L: refuses a joined act with the base's D-4 or D-5** (item 2; `decodeNormsEnvironment`'s default is lexical):
- `Service/Standalone`: the environment row (`decodeEnvironmentU`, `validatedComposedEnvironment`), typing,
  `regulatedOf` (the model gate and Background) and `checkRegulated`;
- `EnglishGrammar/Run.validateDeclarations` (`decodeSourceLexical`) and `EnglishGrammar/Encode.modalForm`
  (`decodeRegulatedIn`);
- `Service/Document`: `decodedEnvironment`, before any admission; `checkNorms` (`joined := false`);
  `checkNormDefaults` (`decodeSourceLexical`);
- `Ask/ZeroWire` (`decodeSourceLexical`);
- `Words/Situation` and `Norms/Plain` (`decodeRegulatedIn`, `decodeRegulatedAllIn`: the plain kinds and the family
  decoder);
- `NormDefaults/Wire.decodeEnvironmentU`;
- `WireContract/Hooks/Acts` (`decoded`, as the environment row);
- the readings route: `Readings/Wire` D-33. `Readings/SupRun` decodes after `decodeEnvironment` has refused.

**G: the profile gate refuses `acts@0` before the decoder:**
- `Alternatives/Wire`, `Service/FamilyNorms` (closure and order families), `SoftNorms`, `Rights` and `SpeechActs`: AR-10's
  row, with `Compose/Examples.lean`'s guards. The soft, rights and speech-acts runners hand every case off their own
  path to `Norms.Run.runCaseReported`, which is routed. Their inner fall-through to `Norms.Run.runCase` is reached
  only on their own path.
- `Attribution/Wire.decodeNormNode` refuses `acts@0` at its envelope: guard in `Service/ActsExamples.lean`.
- `WireContract/Hooks/NormDefaults` decodes without `acts`.

**N: reads no act:** `canonicalEnvironmentJson`. Under `acts@0` it uses `canonicalShape`, which canonicalises only
and keeps the bytes `decodeSource` stored. On the readings route it uses `canonicalActIn`.

### 3.2 The twins (`lean/VE/Acts/DecodeTwins.lean`)

Each twin is the existing proof, read through the `In` form at the elaborating decoder.
- `Elaborated env norms src` is `∃ e, decodeElaboratedFlagged … = .ok e ∧ src.D = e.U'.D ∧ …`.
- `ElaboratedDoc env norms s` is `∃ e, decodeElaboratedU … = .ok e ∧ s.U = e.U'`.

The twins:
- Norms route: `norms_flagged_acceptance_elaborated`, `norms_flagged_conflict_sound_elaborated`,
  `norms_flagged_witness_sound_elaborated`, `norms_flagged_conflict_free_elaborated`,
  `norms_wire_certificate_acceptance_elaborated`, `norms_wire_conflict_free_elaborated`,
  `norms_wire_conflict_refuted_elaborated`, `norms_wire_conflict_exclusive_elaborated`,
  `norms_wire_acceptance_elaborated`, `admission_elaborated`.
- Norm-defaults route: `normDefaults_wire_conflict_sound_elaborated` and `normDefaults_wire_witness_sound_elaborated`
  (stated with `decodeElaboratedU … = .ok e` and `e.U'` directly), `normDefaults_wire_acceptance_elaborated`,
  `normDefaults_wire_status_sound_elaborated`, `normDefaults_wire_report_sound_elaborated`,
  `normDefaults_wire_admission_elaborated`.
- The `In` theorems with no decoder in their statement (`normDefaults_wire_reached_soundIn`,
  `norms_wire_report_consequenceIn`, `wire_report_consequenceIn`, `runAdmission_soundIn`) hold at either decoder as
  they are.

### 3.3 `sourceOf`

`sourceOf` turns an `ElaboratedU` into the `SourceU` the routes read, so that every route theorem over any `Source`
holds of it.
- The parts are declared in place of their sources (`splitPredicates`, with `lookup_split` proving it is `splitEnv`).
- `namesValid` and the definitions chain (`chainOk`) are checked over the new vocabulary.
- The proofs `wf`, `env` and `lits` come from `elaborateMap_ok`.
- A document whose acts are all lexical is its source, unchanged (`sourceOf_lexical`).

## 4. Fixtures (each check on both sides)

- **`DecodeExamples.lean`:**
  - E5j: `e.s.U.unspec = [p027]`, `e.U'.unspec = [p027__1, p027__2]`, both parts deny by default; the opposite side
    has no frames (refused) and `deny` (no unspecified part). `frames` is refused without `acts@0`.
  - `decodeVocab`: D-31 rows, malformed fields, absent fields, the markers, split and modifiers told apart, a two-word
    head.
  - `sourceOf`: the parts in every vocabulary, never the source; `splitJson`, `splitPredicates` and A7 (one atom,
    unsplit).
  - Data flags: `flaggedSource` keeps them, and `decodeElaboratedU` refuses them with the base's text.
  - At the limits, each act read once: 32 acts and 128 rules give 64 parts and 256 part rules; 33 acts are refused;
    the decoder's own limit holds at 65.
  - `joinedActs` on both sides.
- **`Service/ActsExamples.lean`:**
  - The routed norms and norm-defaults cases name `p027__1` and `p027__2`, while the unrouted `runCase` names `p027`.
  - A plain part's wording.
  - A lexical case answers byte for byte as the unrouted one.
  - D-16 on the route.
  - D-4 on every path of item 2: the decoder, `decodeEnvironmentU`, `decodeSourceLexical` both ways,
    `validatedComposedEnvironment`, `regulatedOf`, the model gate, `folBackground` (with the lexical side passing),
    `modalForm`, the document gate, the quoted W1 block.
  - `canonicalEnvironmentJson` and `canonicalShape` on both sides.
  - D-33 with and without frames, a lexical act admitted, and `lexicalAct` and `fixedOf` on both sides.
- **`tests/test_acts_joined_route.py`** (7 tests through `ve_service`, which nothing relays yet):
  - the norms elaborate and conflict cases and the norm-defaults case name the parts;
  - a lexical act keeps its predicate;
  - D-16 and D-31 through the service;
  - a joined act with no rule is refused (D-20).

## 5. Seeded bugs and mutants

**Lean, `docs/act-phrases/ap-3db/seed_bugs.py`:** **43 of 43 KILLED** ([mutants.json](mutants.json); each row gives
its file, definition and the failing `#guard`).
- How it works: each bug is planted in a copy of `lean/`. The proofs named beside it are stubbed with `sorry`, so a
  fixture must fail and not only a proof.
- Coverage: one or more bugs per new or changed trusted definition of `Norms/Wire.lean`, `Acts/Wire.lean`,
  `Acts/Decode.lean`, `Norms/Run.lean`, `NormDefaults/Run.lean`, `NormDefaults/Wire.lean` and `Readings/Wire.lean`.
- One row is a proof kill (`readings-guard-dropped`): the branch it cuts is reached by no input while the frame
  decoder is lexical, so `readings_lexical_only` is what fails.
- Item 1's seeded bug, "the entry point put back on the source", is `norms-entry-source` and `defaults-entry-source`.
- When it ran: at `d26ecfc67`. Since then the product definitions have changed only in `lookup_split`'s statement (a
  proof) and in the revert of the four gate-refused calls (section 7).
- Dropped row: `source-profile-lost` cannot be planted past `sourceOf`'s embedded proof. Three other `sourceOf` rows
  cover the definition.

**Python route test:** planted in the service's own entries, `ve_service` rebuilt, then
`tests/test_acts_joined_route.py` run.
- `service-norms-unrouted` (`Norms/Run.lean` `runCaseReported` back on `runCase`): 3 failed, among them
  `::test_the_norms_route_answers_a_joined_act_with_its_parts_and_never_the_source`.
- `service-defaults-unrouted` (`NormDefaults/Run.lean` `runGated` back on `runCase`): 1 failed,
  `::test_the_norm_defaults_route_answers_with_the_parts`.
- Restored: 7 passed.
- No Python or Rust product code changed, so there is no Python or Rust product bug to seed.

**trust_mutants:** TMLINE

## 6. Trust, size, tests and checks

**Trust:** `uv run python tools/trust_map.py --check` against fe252f79af28 gives K +0, S +15, D +144, G +25, tied +60,
trusted +122.
- Per file:
  - untied D[V]: `Norms/Wire.lean` +46, `Acts/Wire.lean` +18, `NormDefaults/Wire.lean` +11, `Readings/Wire.lean` +6,
    `Acts/Decode.lean` +1;
  - untied G[V]: `Norms/Run.lean` +14, `NormDefaults/Run.lean` +11;
  - S: `Acts/Decode.lean` +5, `DecodeTwins.lean` +4, the two `Admission.lean` +2 each, the two `Run.lean` +1 each.
- Ties: the first measurement was +182. Tying `sourceOf`, `splitPredicates`, `decodeElaboratedFlagged`,
  `flaggedSource`, `elaboratedU`, `fixedOf` and the readings `decodeEnvironment` to their theorems brought it to +122.
- Recorded with `--allow`, signed by R16 (DELTA row 6); FOLLOW-UPS "## ap-3db" asks for the ties pass.

**Size:** `git diff --numstat $(git merge-base HEAD main)`, hand-written lines, added plus deleted.
- Lean product 1,327:
  - `Decode.lean` 231;
  - `DecodeTwins.lean` 210 (statements of the twins);
  - the `In` generalisation of 11 route files, about 600;
  - `Norms/Wire.lean` 72, `Readings/Wire.lean` 45, `Acts/Wire.lean` 26;
  - the moved `forIn_ok`, 38;
  - the two shape proofs, 45.
- Fixtures 265 (`DecodeExamples.lean` 132, `ActsExamples.lean` 109, the senses pins 24).
- Tests 83, `tools/layer_policy.py` 8.
- Evidence 282 (the seed script 222, `check_statements.py` 41, DELTA 19), and this report.
- Side tables: `tools/trust-classes.json` 253 and `ve/assurance-manifest.json` 131, reviewed by hand.
- Total: about 1,970 without the tables. Deliverables (1) to (3) are one safety unit (the task: "even if they alone
  pass ~600 lines"), and they alone are most of it. (4) and (5) add about 60 product lines.

**Builds and checks on the final tree:**
- `regen_generated.py --write` (with `route-cases` and the Rust binary): `lean/VE/Route/examples/route-cases.json`
  unchanged, and `tests/data/route-cases.jsonl` untouched. Then `--check --skip route-cases`: every entry checked.
- `lake build`: 1,253 jobs. `python3 tools/check_lean_imports.py`: "Lean layer graph kept".
- `uv run pytest -q tests/test_assurance_manifest.py`: 139 passed.
- `tests/test_acts_joined_route.py`: 7 passed.
- `tests/test_acts_profile.py` passed unchanged, at 372 passed together with the manifest tests before the final pins.
- `uv run python tools/english_grammar_gen.py --check` passes (version 38).

**Selected tests:** SELLINE

**Not run:** the full gate (the chain runs it), any pilot, AP-7.

## 7. Deviations and choices

1. **`checkAct` runs once per act, right after the declarations, not inside each declaration's hook.** The hook stores
   the canonical act (`canonicalShape`: conditions 1 to 5 and the lexing), and `actsOf` then reads each act with
   `checkAct` and keeps its tree on `NormsEnvironment.joined` (deliverable 5). Effect: a document holding both a
   joined act refused for its reading and a later declaration's fault gives the later fault first (DELTA row 2).
2. **Admitting a joined act is opt-in** (item 2).
   - `decodeNormsEnvironment (joined := false)` is lexical by default.
   - `decodeSource (joined := true)` admits joined acts by default, which `decodeSourceU`'s and the route's statements
     need. Its callers that do not elaborate pass `false` or are refused earlier (section 3).
   - `decodeSourceLexical` is `decodeSourceUWith false`, so `decodeSourceU` keeps no parameter.
3. **`decodeElaboratedFlagged`.** The norms route admits `data@0` flags and `decodeSourceU`'s second branch does not,
   so `decodeElaboratedU` refuses a flagged document. The norms route's twins are therefore stated with
   `decodeElaboratedFlagged` (`decodeSource (flags := true)`, then `elaborateSource`), the decoder `decodeElaboratedU`
   wraps.
4. **Twins by generalisation.** Each route takes its decoder; the base's names instantiate it and keep their
   statements. A twin restates the conclusion with `Elaborated`/`ElaboratedDoc`. Nothing in the item re-proves a
   theorem.
5. **The four gate-refused calls keep the base's text** (`Alternatives/Wire`, `Service/FamilyNorms`,
   `Attribution/Wire`, `Readings/SupRun`). A first version added `(joined := false)` there. The gate refuses `acts@0`
   first, so the argument changed nothing, and trust_mutants read its flips as survivors. Section 3 shows each
   refusal.
6. **English `actions_version` 38.** `EnglishGrammar/Run.lean` calls `decodeSourceLexical`, which keeps D-4 for the
   English view (item 2). The goldens are re-recorded by their tools: the senses pins and the ask fixtures, and the S3
   comparison with only `actions_version` changed. Its two lark messages, whose "expected one of" set order varies
   between Python runs, are kept as recorded. DELTA row 5.
7. **The original `runCase` and `runAdmission`** (`Wire.decodeFlagged`, which admits a joined act) are reached by the
   service only through `runCaseRouted`. `Service/Document`'s admission follows its environment gate, which refuses a
   joined act (guard).
8. **`singleActsOnly`** (ap-1bd's text match of D-4) stays, unchanged. The new guard behind it is structural
   (`lexicalAct`).

## 8. DELTA

See [DELTA.md](DELTA.md), rows 1 to 6.
- Each Ruling cell cites the decider's file and item word for word, or R1 or R16.
- `review-ready.py --delta-dri-needed` does not apply: no row is reserved.

## 9. Pilot bytes and next items

- **Pilot bytes expected to move: 0 B** (*estimate*). Python still refuses a joined act until ap-3dc relays the
  elaboration. u079b's 76 B (A7) and the AP-3 rows of u027 and u0123.s03 wait for ap-3dc.
- **ap-3dc (next):**
  - the `acts-elaborate` relay;
  - `_lean_route` for `acts@0`, with item 2's guard lifted in the same change (item 5);
  - `test_reference_table_complete`;
  - the Python display seeded bug;
  - u0218.s18's regression document (DEC 16).
- **Then:** ap-4.

## 10. Self-review against BUILDER-CHECKLIST

SELFREVIEW

## 11. Commits (`main..HEAD --no-merges`)

COMMITS
