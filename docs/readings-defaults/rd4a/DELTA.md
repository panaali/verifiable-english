# RD-4a: readings with their own vocabulary (Lean wire)

Batch RD-4a of [readings-defaults-PLAN.md](../../spec/readings-defaults-PLAN.md) (its RD-4a section, table row and
gate), statements of [readings-defaults.md](../../spec/readings-defaults.md) 6.6 (the wire part, `section
Companions`), on branch `readings-defaults/rd4a` from `main` at `51853586`. Built by one Lean worker session on
2026-10-08; no model was called. Every number below is in [evidence/gate.json](evidence/gate.json), the A/B files and
[evidence/seeded-bugs.json](evidence/seeded-bugs.json), and `tests/test_readings_defaults_rd4a_report.py` checks it
against them (saved evidence only: no live git, build or dump).

## What changed

- `lean/VE/Readings/Companions.lean` (new): `companionSets`, `mergeCompanions`, `mergeOpenTerms`, `splitCase`,
  `companionMeaningId` and `arr` as 6.6 states them, and the four 6.6 theorems, each proved with no `sorry`:
  `mergeCompanions_extends`, `mergeCompanions_identical`, `mergeOpenTerms_identical`, `split_keeps_links`. The split
  runs 5's rows 6 to 13 in order: a set mixing readings with and without a companion; a coupling naming a companion
  set beside another set; a companion on the soft or rights chain; different language, revision or profiles; a name
  declared differently; an open term declared differently; the frozen decoders on the merged frame (with every open
  term's conditions typed there by `openTermNames`, E4); each recorded `meaning_id` against `companionMeaningId` (W1's
  identity, `encodeNode` over the companion's own `environment_id`). Declarations are compared as JSON values
  (`jeq`, `jeq_sound`, `jeq_refl`) after each companion is brought to one normal form (`normJ`).
- `lean/VE/Readings/Run.lean`: every readings kind first splits the case (`runCase`). A document without `companion`
  is one case, `main`, run as before through `runOne` (the former body of `runCase`). With companion sets,
  `readings-validate` and `readings-elaborate` answer per case (`runComponents`: `{"components": [{"component",
  "answer"}]}`, `main` first, then each companion set in source order), and every other kind runs on the case its
  `component` names (`main` when absent).
- `lean/VE/Readings/CompanionsExamples.lean` (new): `#guard` fixtures of the merge and the split, each claim both ways.
- Response shapes: `validate_components` and `elaborate_components` (`ResponseShape/Schemas/ReadingsRoute.lean`,
  regenerated `readings-route.json`) with their `*_fits` theorems; `runCase_fits` proved for the new dispatch.
- Python: none outside tests and tools. W2's structural validation still refuses a reading with `companion`
  (`ve/readings.py`, RD-4b's change), so `ve document` cannot reach any of this yet; Lean computes every companion
  meaning id and merges everything (3.10).
- Manifests: `VE/Audit.lean`, `ResponseShape/Audit.lean`, `axioms.txt`, `statements.txt` (additions only),
  `predicates.txt`, `declarations.txt`, `VE/Route/frozen-sources.sha256`, `tools/trust-classes.json`,
  `ve/assurance-manifest.json` with `docs/spec/assurance-manifest.md` (Companions.lean pinned whole),
  `lean/checkers.lock` (the new `ve_service`), `tools/gate-collection.json`, `tools/consolidation-ledger.json` (step 7
  names `runOne`, so the dispatch lines `runCase` now delegates stay counted: 645 to 659, the plan's row updated);
  `tools/check_readings_defaults_statements.py` compares 6.6's wire part too; `lean/READINGS.md`.
- Tests: `tests/test_readings_companions_lean.py` (F-C1 to F-C12 through the service, the split contract, malformed
  companions), `tests/data/readings_companions/udhr-20261006T1800Z.json` (the three UDHR companions of F-C7 and their
  recorded ids, copied from `bd6c7ab2`), RD-4a's statement-check tests, and the admission-once IR walk of RD-2a
  updated to name `runOne`, `validateOne` and `elaborateOne`.

## Fixtures (spec 8.4)

| # | Where | Result |
|---|---|---|
| F-C1 | `test_fc1_three_components_each_answered_as_a_document_of_its_own` | three components; each answer equals Lean's answer on that component written as a document of its own (F-ND1's twice) |
| F-C2 | `test_fc2_a_name_declared_differently`, `#guard` | `InvalidInput: readings rs_a@1:0 and rs_a@1:1 declare avoid_life_required differently` |
| F-C3 | `test_fc3_a_set_mixing_readings_with_and_without_their_own_vocabulary`, `#guard` | 5 row 6's text |
| F-C4 | `test_fc4_language_revision_and_profiles_must_agree`, `#guard` | 5 row 9's text for each of the three keys |
| F-C5 | `test_fc5_identical_declarations_unite_whatever_their_key_order`, `#guard` | one sort in the merged frame, whatever the key order the request writes |
| F-C6 | `test_fc6_a_main_rule_over_a_companion_readings_rule` | `UnknownRule: rule must-help` |
| F-C7 | `test_fc7_meaning_ids_of_the_udhr_companions` | the recorded ids (the companion unit's for u074) are accepted and each companion set is admitted; any tampered id is `reading meaning id does not match content` |
| F-C8 | `test_fc8_a_companion_on_the_soft_or_rights_chain` | 5 row 8's text for both profiles |
| F-C9 | `test_fc9_a_coupling_across_components_is_refused_one_within_main_is_kept`, `#guard` | refused across components, both orders; kept and checked in `main` |
| F-C10 | `test_fc10_open_terms_merge_by_name_and_are_typed_in_the_merged_frame`, `#guard` | refused when different; merged when identical; a condition over another frame's predicate refused |
| F-C11 | `test_fc11_a_narrowing_travels_with_its_companion_set`, `#guard` | the narrowing narrows its component's choices only |
| F-C12 | `test_fc12_an_unseparated_set_stays_in_main_as_w2` | the set stays in `main` (route `w2`), never a component |

## Deviations from the spec, each for the statement re-review or the planner (EXTERNAL)

1. **`split_keeps_links` reads `contains` with a local instance.** Its text is the approved text (10 of 10
   declarations exact), but Lean's own `BEq Json` is compiled code with no definition a proof can unfold, so no
   statement about `contains` under it can be proved. In `Companions.lean`'s section the statement elaborates with
   `jeq`, structural equality (sound and reflexive, both proved). Owner: statement re-review.
2. **Byte-identical canonical declarations are decided as equal JSON trees after a normal form** (`normJ` rebuilds
   every object in key order). Two declarations whose canonical bytes agree are equal there; a number written in two
   JSON forms of one value (`1` and `1.0`) is refused as different, failing closed.
3. **A component's document also holds the units its narrowings cite, by id and without content**, beside the set's
   unit, so that W2's citation check of a narrowing reads them; they add nothing to any reading's document.
4. **Every environment key agrees, not only language, revision and profiles**: another key written differently is
   `InvalidInput: the readings of <set> declare different <key>` (row 9's form). A companion whose `open_terms` is not
   a list is `open_terms must be a list` (`openTermNames`' text); found by seeded bug M10, which showed it was read as
   none.
5. **`component`.** Every kind of one case (`readings-separate`, `readings-choice`, `readings-dead` and the superposed
   kinds) takes it, and `readings-validate` or `readings-elaborate` answer one case when it is given. A name that is not
   `main` or a companion set is `InvalidInput: component <c> is not main or a reading set with its own vocabulary` (a
   new text, not in 5). Kinds outside the readings route (the lower routes) are not split.
6. **Companion sets are found per set id over every version written**: a set id whose versions mix readings with and
   without a companion is 5 row 6.
7. **F-C11's `restrictions` and F-C12's W2 UNKNOWN are RD-3's and RD-4b's answers**, not on `main` yet; the fixtures
   show the narrowing in its component's choices and the unseparated set on `main`'s `w2` route.

## Availability

None. `ve document` refuses a reading with `companion` in W2's structural validation, as before; only the Lean
service reads it, and RD-4b makes it reachable.

## Gate (HEAD before this report, `18319355`, this worktree with a clean status)

| Check | Result |
|---|---|
| `lake build` | 840 jobs, success |
| `python3 lean/audit.py` | PASS: 454 source files, 4852 theorems (base 4801), standard axioms only |
| `python3 VE/Route/frozen.py` | PASS |
| `tools/lean_statements.py --check` | PASS: 4467 statements (base 4422), 0 changed, 0 removed |
| `tools/check_readings_defaults_statements.py` | RD-1: 31 exact, 0 pending; RD-2a: 16 exact, 0 pending; RD-4a: 10 exact, 0 pending (RD-6a: 7 exact, 1 amended) |
| service fixtures `tests/test_readings_companions_lean.py` | 19 passed, 0.62 s serially |
| full suite in 8 chunks (`-n 16`, the gate's plugins, `VE_*_PREBUILT=1`) | 2675, 1388, 1387, 1386, 1387, 1386, 1388 and 1387 passed; 0, 0, 0, 2, 1, 2, 0 and 1 skipped; 0 failed |
| corpus A/B (`tools/lean_first_diff.py`, base `51853586`) | 54504 records, 54500 the same, 4 unavailable on both sides with the same answer, 0 different |
| `tools/trust_map.py` | 0 unclassified; `--check` still fails on growth that predates RD-4a (RD-1's and RD-2a's DELTA); RD-4a's own trusted growth is `Companions.lean`'s readers (`D[V]`) and `Run.lean`'s dispatch |

Chunks 3 and 4 ran at `f99c84e4`, whose tree differs from `18319355` only in `tests/test_readings_lean_sharing.py`
(chunk 5). The 4 records unavailable on both sides are pilot documents of the constitution pilot's `readings/s1.ve.md`
whose English check answers `CheckerUnavailable` (the lexicon) on both commits; every recorded file of the base and
the head is byte-identical (the SHA-256 prefixes in `gate.json`).

Not run: the corpus A/B under the Lean authority for `probe`, `conformance` and `quantity` (on this host, loaded by
other sessions to an average of 35, each Rust `ve jsonl` call of that path idled for seconds and the base recording
did not finish in an hour; the Python authority of the same corpora is in the A/B above, and those routes' Lean
sources are unchanged by this batch: the frozen inventory changed only for `Audit.lean`, `Readings/Run.lean` and the
two new files); `tools/gate.py` in a fresh worktree (it does not fit one 60-minute foreground call; the chunks are its
suite); latency (the split reads the document once more, in Lean, only for a document with `companion`).
`tests/test_assurance_manifest.py::test_bundle_separates_rejection_from_unavailability` fails when run without the
gate's plugins on this commit and on the base alike, and passes in the chunked suite.

## Seeded bugs (each planted, the service rebuilt and the tests run, then removed; the binary rebuilt and its pinned hash restored)

| # | Bug | What failed |
|---|---|---|
| M1 | a name declared differently is merged | `test_fc2_a_name_declared_differently`; `#guard`s at lines 30 and 58; the proof of `addDecl_spec` |
| M2 | a set mixing readings with and without a companion is not refused | `test_fc3_a_set_mixing_readings_with_and_without_their_own_vocabulary`; `#guard` at line 126 |
| M3 | a coupling across components is kept | `test_fc9_a_coupling_across_components_is_refused_one_within_main_is_kept`; `#guard` at line 120 |
| M4 | a recorded meaning id is not compared with `companionMeaningId` | `test_fc7_meaning_ids_of_the_udhr_companions` |
| M5 | a narrowing on a companion set does not travel with it | `test_fc11_a_narrowing_travels_with_its_companion_set`; `#guard` at line 107; the proofs of `componentDoc_arr` and `split_keeps_links` |
| M6 | a kind naming one component runs on `main` whatever it names | `test_kinds_naming_one_component`, `test_without_companions_the_answer_is_todays` |
| M7 | a companion on the soft or rights chain is admitted | `test_fc8_a_companion_on_the_soft_or_rights_chain` |
| M8 | companions merged in the request's key order (no normal form) | `test_fc5_identical_declarations_unite_whatever_their_key_order` |
| M9 | open terms not typed in the merged frame | `test_fc10_open_terms_merge_by_name_and_are_typed_in_the_merged_frame`; `#guard` at line 79; the proofs of `mergeOpenTerms_ok` and `mergeOpenTerms_identical` |
| M10 | validate and elaborate answer `main` only | 7 tests, among them `test_fc1_three_components_each_answered_as_a_document_of_its_own` (it also showed `open_terms` of another type read as none: fixed, deviation 4) |
| M11 | `runCase` admits the document itself before the split | `test_the_route_admits_the_case_document_once` |

A bug whose mutant broke a proof was built with that proof replaced by `sorry` (listed), so the tests could run; the
proof failing is itself a failed check. The statement checker's tests also fail on every changed 6.6 declaration, a
dropped hypothesis and a missing declaration; this report's test fails on a wrong A/B total in this file and on a
seeded bug naming a test that does not exist (each tried once, then restored).

## Build checklist

| # | Status |
|---|---|
| 1 one contract | partly: every new text is Lean's and nothing relays it yet; readings@1 has no generated diagnostic table (none existed before) |
| 2 differential fuzz | not done: no Python or Rust implementation of the split exists (Lean only, 3.10) |
| 3 normalization | done for what the split compares: declarations in any key order merge (`normJ`, F-C5, M8); no text input |
| 4 untrusted output | partly: the per-component answer has a schema and `*_fits` theorems; no client reads it yet (RD-4b) |
| 5 malformed input | partly: `companion`, its `environment` and its `open_terms` replaced by 7, true, [], {} and a string are refused by the split (`test_malformed_companions_are_refused_by_name`); no 10k-deep sweep |
| 6 three-valued verdicts | not applicable: the split gives no verdict; an error of any case is the case's answer |
| 7 deadlines | not applicable: the service's per-case CPU deadline wraps the split; no new loop has its own budget |
| 8 exhaustive folds | not applicable: no kind or owner fold |
| 9 English | not applicable: no sentence (E30 to E32 are RD-4b's) |
| 10 one admit() | done: every readings kind splits first and each case is admitted once (`test_the_route_admits_the_case_document_once`, M11) |
| 11 no regex of a real language | partly: the statement checker reads Lean text by regex, as RD-1's |
| 12 state machines | not applicable |
| 13 tests can fail | done: M1 to M11 |
| 14 hermetic | done: the new tests write nothing, read no environment variable, no sleep |
| 15 identity | done: each companion reading's `meaning_id` is checked against Lean's own identity over its environment (F-C7, M4); no identity of a document without `companion` changes (A/B) |
| 16 lists | done: audit manifests, frozen inventory, statement, predicate and declaration dumps, trust classes, assurance manifest, gate collection, ledger |
| 17 statement diff | done: 10 of 10 exact; deviation 1 for the re-review |
| 18 both directions | done: F-C2/F-C5, F-C9 (refused and kept), F-C10 (refused and merged), conservativity without `companion` |
| 19 use-case formalisation | not applicable |
| 20 reports | done: `tests/test_readings_defaults_rd4a_report.py` checks this file against `evidence/` |
| 21 AGENT/HUMAN/EXTERNAL | done: deviations EXTERNAL (statement re-review, planner); the rest AGENT; nothing for the DRI to sign (no availability change) |
| 22 hand-off | partly: all committed, chunked suite on HEAD with a clean status, 83 GB free; `tools/gate.py` in a fresh worktree and the Lean-authority A/B not run |
