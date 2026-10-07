# Lean-first batch 10b: norm defaults, switch

Base `7345e3ed`, head `lean-first/b10b`. Plan `docs/LEAN-FIRST-PLAN.md` (draft 3, branch `design/lean-first`),
section 5.2 row 10b: switch the norm-defaults callers to the Lean route and delete `ve/norm_defaults.py`'s
semantics (~1,000 lines) and the Python admission (~105). Lead directive: one owner per piece of logic.

## First: the batch 10a trace-fuzzer gap

The 10a recheck found that the fuzzer trace did not hash the baseline replay. Two commits fix it before any switch
evidence uses it:

- `c564a163` hashes every replayed entry's input and full answer (`docs/lean-first/b10a/trace_fuzzer.py`).
- `3754cfe3` fixes a second fault the first fix introduced. `difffuzz.replay` answers surface by surface, but the
  committed baseline interleaves surfaces (requests, environment, wire, requests, environment), so the positional
  check raised on every full run; only the one-entry unit test had run it. Answers are now matched to their entry
  and hashed in baseline order.
  `tests/test_lean_first_b10a_report.py::test_baseline_replay_trace_follows_baseline_order_across_interleaved_surfaces`
  uses the real `replay` and fails on the old code.

## What changed

**Lean** (+39, -10 lines in `.lean` files):

- `NormDefaults.Run`: the `norm-defaults-elaborate` row now also carries `environment_id`, `filled_environment_id`,
  `document_hash`, `fill_hash` and `fill_labels`. Python reads these identities and no longer computes them.
- `Route.Wire.decodeVocabulary`, `Norms.Wire.decodeNormsEnvironment` and `decodeSource` take `displayConstants`
  (default `false`). `NormDefaults.Wire.decodeSourceU` alone passes `true`, so the norm-defaults decoder accepts a
  constant's `verbalisation` where Python's `Environment` does (DF-19), checked in the constant loop as Python
  checks it. Every other route keeps its base answer: the `norms@0` DF-19 baseline entries still reproduce.
  - An earlier version of this branch widened the general decoder and Rust's. That made eight baseline entries on
    other routes disappear, and the Rust change panicked on vocabularies with no `reports` block (it changed a
    recorded answer). Both were reverted: Rust is byte-identical to the base build (`d255808c…`, already pinned).
- `NormDefaults.Wire.placeholderJson` refuses a repeated `norm-defaults@0` with the envelope's text. Setting the
  profile aside used to drop every copy, so the Lean route accepted a repeated profile. DF-19 hid this until the
  fuzzer exposed it, and the base already had the bug (30 sampled inputs below). Python validates the environment
  first on every product path, so no public result changes.

**Python switched to the Lean owner and deleted** (`ve/`: 1,163 lines deleted, 272 added):

| Deleted Python decision | Lean owner now |
|---|---|
| `norm_defaults.py`: fill, unspecified-predicate selection, guards, generated layers, statuses, conflict, reached, report and residual (1,089 → 324 lines) | `VE.NormDefaults.Wire` and `VE.NormDefaults.Report` through the `norm-defaults` service mode |
| `norm_defaults.py`: environment, fill and document identities | the `norm-defaults-elaborate` row; `UnspecifiedDocument` refuses a mismatch as `CheckerUnavailable` |
| `norm_defaults_route.py`: the regeneration comparison and the W1 admission checks (230 → 95 lines) | `NormDefaults.Run` and `NormDefaults.Admission`; `admit_norm_defaults_document` relays the Lean row |
| `document.py`: gaps and grounding folds | the Lean `norm-defaults-report` row (`residual`, `findings`) |

What remains in `norm_defaults.py` is containers built from Lean's accepted row, a W1 English display view whose
generated layer premises must equal Lean's row, an untrusted evidence proposer (models and certificates that Lean
replays, rule 3), the audit composition of Lean's rows, and CLI file reading.
`tools/relay_lint.py` now lists `ve/norm_defaults.py` and `ve/norm_defaults_route.py` and passes. The audit-file
shape check is marked file I/O, and an exhausted certificate generator raises `CheckerUnavailable` (rule 3), not a
`VEError`. `tools/inventory_lint.py` passes.

Fixed while switching: `search_reached` fell back to the frozen oracle for old document types. That fallback hid
that its own path built the situation over the source environment (`InvalidModel`). The authoring-question test now
uses the relayed container, and the situation is over E‴'s base without the unsaid tables, as on the base.

The frozen pre-deletion Python (`conformance/frozen_norm_defaults.py`, loaded from `9160d326` and checked by
SHA-256, DRI answer 7) is a test oracle only. One non-test module reads it: `ve/norm_defaults_contract.py`, the
wire-contract diagnostic hooks that `tools/wire_contract.py` and the contract tests load. No product entry point
reaches that module. It goes with the wire-contract engine (plan 6.1).

## Fix 4: Lean owns the English of its norm-defaults rows

Directive `lf-10b-fix4` and recheck `lf-10bc-looprecheck1` (two B findings). The latent-conflict renderer still
enumerated every yes/no answer of the unspecified rows (18 acts: 148 s and 950 MiB, doubling per act), and the
gap renderer evaluated the default itself through `document.value` and its 1,000,000-step limit (60 acts: the
private `_Exhausted`). Both were Python re-deriving answers Lean owns. The class is removed, not the example:

- **Lean answers carry what the English states** (`VE/NormDefaults/Explain.lean`, 229 lines). A CONFLICT
  witness row carries its `tuple`, its `kind` (spec 3.1: `settled` when the target is Kleene-true with no unsaid
  atom known, `settled_every_filling`; else `latent`), the deciding assignment `under` and the deciding author
  `rules`. `under` is one evaluation that records the unsaid atoms supporting the value, shrunk one atom at a
  time while the Kleene check passes; it is used only when that check passes (`underOf_sufficient`: the target
  holds in every structure that agrees with the witness on `under` and on the base). The work is polynomial: no
  filling is enumerated, and the 40-act fixture answers at once. A status row carries the deciding `rules`
  (`selectedRules_sound`) and, when UNDECIDED, the atoms the two fillings `differs` on. A reachable report line
  carries the completed `value` (`value3_gap`: where no author rule decides, the value is the completion's). The
  soft and rights branches emit the same fields, and `norm-defaults.json` requires them exactly where the runner
  emits them (`ResponseShape/Encoders/NormDefaults.lean` proves every row fits).
- **The renderers only format those fields** (`ve/norm_defaults_english.py`: the model enumeration, the
  evaluator, `document.value`, the conflict replay and the authoring question's search are gone). A missing or
  unknown field is `CheckerUnavailable`, never a recomputation.
- **Regressions.** The 13-, 16-, 18- and 40-act `latent` fixtures render in under 2 s. The 60-act repro renders
  from Lean's line at a0 (`tests/test_relay_english_scale.py`). `test_renderers_reach_no_evaluation_search_or_limit`
  walks the AST call graph from every public function and allows only display helpers; seeded recomputations
  fail it. `test_rendered_text_follows_leans_fields_not_a_recomputation` changes Lean's fields and checks the
  sentence follows them. The u13 tests now render Lean's rows for the frozen oracle's fixtures.
- **Corpus.** The 60-act source (`link` with ∃y∃z∃w) is not in this batch's frozen norm-defaults differential
  corpus, which the fourteen-seed fuzzer evidence compares with the base, so its test is outside wire-contract-s5
  7.1's recorded globs and is listed below for the next corpus refresh. Every other new test reuses a corpus
  source (the settled case is u5d). The fuzzer's request surface has no norm-defaults route kind, so the new
  fields change no sampled answer.
- **Public outputs unchanged.** The four A/B corpora recorded at `864f8a7e` reproduce the base recordings'
  hashes (`evidence/ab-recordings.json`, `also_recorded_at`).

## Gate (section 5.1)

<!-- generated by verify_report.py: begin -->
| Evidence | Result |
|---|---|
| A/B probe and conformance | 58,482 records same |
| A/B norm-defaults profile corpus | 2,020 records same |
| A/B readings, discourse, rights, quantity | 35,713 records same |
| A/B historical pilots | 294 records same |
| Fuzzer date seeds, base and head on the base baseline | 14, none unexplained |
| Explained: DF-19 masked inputs now decoded | 331 |
| Explained: repeated `norm-defaults@0` now refused with Python's text | 30 |
| Explained: retired baseline entry fixed on the head | 14 |
| Listed: head-only diagnostic finding unmasked from DF-19 | 1 |
| Mean norm-defaults corpus wall, base / head (s) | 87.88 / 90.86 |
| Mean norm-defaults corpus user CPU, base / head (s) | 332.93 / 321.66 |
| Python under `ve/`: lines deleted / added | 1237 / 357 |
| Lean: lines added / deleted | 359 / 35 |
<!-- generated by verify_report.py: end -->

`tests/test_lean_first_b10b_report.py` regenerates this table from `evidence/` and the Git diff, and checks every
evidence file.

1. **Suite.** The full gate (`tools/gate.py`) runs on the final commit in a clean worktree. Its JSON names that
   commit, so it lives outside the tree: `verify_report.py --gate FILE` checks it, and the hand-off report gives
   the result.
2. **Corpus A/B.** `tools/lean_first_diff.py` record and compare, base and head. The recordings are byte-identical
   on every corpus (`evidence/ab-recordings.json`), so this batch has no `wording`, `order`, `verdict` or
   `availability` change on a public entry point.
3. **Differential fuzzer.** The committed baseline shrinks from 357 to 356 entries: the norm-defaults
   `environment` DF-19 entry is fixed and retired (`conformance/DIFFFUZZ.md`). `tests/test_difffuzz.py` passes.
   For the fourteen date seeds, `docs/lean-first/b10b/fuzzer_gate.py` runs base and head against the base's
   baseline and records every sampled input and replayed entry (`trace_items.py`). It accepts a changed answer
   only in these cases:
   - **DF-19:** the base Lean answer is the DF-19 rejection, and Python's and Rust's answers are unchanged.
   - **Repeated profile:** the head Lean text is Python's own `profiles must be sorted and unique`.
   - **Retired entry:** the retired baseline entry.
   - **Head-only finding:** allowed only if DF-19 masked its input and the class is `diagnostic`.

   Any other change fails the gate. All fourteen seeds pass, and on ten seeds the head no longer makes 16 findings
   the base made. The one head-only finding is a DF-3 fault-order instance, now visible on the norm-defaults
   profile; DF-3 already baselines it for the risk, alternatives and speech profiles:

   | Seed | Input | Python | Lean |
   |---|---|---|---|
   | 20260923 | `regulated: []` and a constant with `sort: []` | `InvalidInput: regulated declaration csam_generation_permitted needs role and default` | `InvalidInput: String expected` |

   This is a Lean answer on a two-fault fuzz input, not a public result: Python's `Environment` rejects first on
   every product path. It is an `order` item (HUMAN, below).
4. **Deletion ledger.** Above. `relay_lint` and `inventory_lint` pass.
5. **Latency.** The same corpus run four times, alternating base and head (`evidence/timing.json`): head user CPU
   is 3% lower, wall is 3% higher on a shared host. Both are inside the 20% budget, and a document check is about
   0.3 s of CPU.

## Theorem statements

`tools/lean_statements.py` reports 0 added, 0 removed and 17 changed. The printed text of all 17 is unchanged. Only
the structural hash of the elaborated type moved, because the terms now carry the new decoder argument at its
default `false`, whose branch is the base body (`decodeVocabulary_flag_not_defined`, the norms acceptance and
conflict theorems, `decodeSourceU_plain` and `decode_conservative`). `lean/statements.txt` and
`declarations.txt` are regenerated. No new theorem.

Fix 4 adds 5 theorems and changes none: `kept_sound`, `settled_every_filling`, `underOf_sufficient`,
`selectedRules_sound` and `value3_gap` (`VE.NormDefaults.Wire`, `lean/VE/NormDefaults/Explain.lean`).

## Acceptance items

| Item | Owner | Status |
|---|---|---|
| Suite, A/B, fuzzer, ledger, latency | AGENT | done above; the final gate in the hand-off report |
| The listed `order` item (DF-3 instance on the norm-defaults profile, fuzz-only) | HUMAN (DRI) | deferred: sign with the wording/order block |
| 17 statement hashes moved with unchanged text (default argument) | HUMAN (DRI) | deferred: acknowledge as no statement change, or ask for approval |
| Trust map: +29 trusted Lean lines (D +10, G +19: `NormDefaults/Run.lean` +15 for the identities Lean now owns, `Route/Wire.lean` +5, the response schema +4, `NormDefaults/Wire.lean` +3). `tools/trust_map.py --check` already fails at the base (V +346 with no signed allowance); the consolidation ledger's 8b figure is regenerated (3,456 to 3,458) | HUMAN (DRI) | deferred: sign the allowance with the other batches' growth |
| Fix 4: five new theorems (above) | HUMAN (DRI) | deferred: approve the statements |
| Fix 4: trust map +102 untied [V] Lean lines (`NormDefaults/Explain.lean` +59, the response schema +31, `NormDefaults/Run.lean` +6, `NormDefaults/Layered.lean` +6; `trust_map.py --since f0756983`); the support search is C, and `keptV`, `settledConflict`, `underOf`, `selectedRules` and `completedLabel` are tied | HUMAN (DRI) | deferred: sign with the allowance above |
| Fix 4: record the 60-act repro's source (`tests/test_relay_english_scale.py`) in the norm-defaults corpus | HUMAN (DRI) | deferred: at the next fuzzer-gate corpus refresh |
| External check | EXTERNAL | none in this batch |

DRI rulings used:
- [x] Answer 7, the pinned frozen oracle: `tests/test_norm_defaults_differential.py`.
- [x] Answer 9, batch order: `tests/test_norm_defaults_switch.py`.
- [x] The throughput rule that the difffuzz baseline must not grow:
  - `tests/test_difffuzz.py::test_ci_run`;
  - `tests/test_lean_first_b10b_report.py::test_any_other_difference_fails_the_gate`.

## Build checklist

| Lines | Owner | Check or scope |
|---|---|---|
| 1-2 | AGENT | Generated wire and route schemas; difffuzz CI and fourteen seeds through the 10b gate. |
| 3 | AGENT | Existing text-normalisation fixtures in the full gate; no normaliser changed. |
| 4-5 | AGENT | Response schema `norm-defaults.json` for the new row fields; route decoder and malformed-input suites. |
| 6-7 | AGENT | Lean statuses; budget and deadline tests in the full gate. Generator exhaustion is `CheckerUnavailable`. |
| 8-9 | AGENT | No kind fold or English parser changed; English tests in the full gate. |
| 10 | AGENT | Document, admission and audit paths all call the one Lean route; A/B compares public entry points. |
| 11 | AGENT | No regex over a real language added. |
| 12 | AGENT | No state-machine or ledger code changed. |
| 13 | AGENT | Twelve seeded bugs, below. |
| 14-16 | AGENT | Hermetic gate; identities from Lean; `relay_lint`'s list extended; assurance manifest re-pinned. |
| 17-18 | AGENT / HUMAN | Statement diff above; no spec-stage theorem. |
| 19 | AGENT | No use-case rule or answer key changed; agent-policy `unspecified` harness in the suite. |
| 20 | AGENT | The gate table is regenerated from `evidence/` by a test. |
| 21 | AGENT / HUMAN / EXTERNAL | Tagged above. |
| 22 | AGENT | Final clean-worktree gate, disk check, local commits, hand-off report. |

## Seeded bugs (`evidence/seeded-bugs.json`)

Each mutant was applied alone (the two Lean mutants in one build, each test attributable to its own), its test
failed, and the file was restored and the test passed again:

1. Trace: the baseline replay answers left unhashed. `test_fuzzer_gate_detects_changed_baseline_replay_answer`
   fails.
2. Trace: the positional replay check restored.
   `test_baseline_replay_trace_follows_baseline_order_across_interleaved_surfaces` fails.
3. Admission relay forced to `admitted: false`. `test_document_graph_admits_the_layer_of_fill_u` fails.
4. Report relay forced to `translation: false`. `test_document_reports_the_leans_grounding_and_gap` fails.
5. The 10b gate accepts a changed Python answer. `test_any_other_difference_fails_the_gate` fails.
6. Situation built over the source environment. `test_latent_conflict_finding_and_the_authoring_question` fails.
7. Lean: the repeated-profile check removed.
   `test_lean_accepts_constant_wording_and_refuses_a_repeated_profile` fails (did not raise).
8. Lean: constant wording accepted on every route. `tests/test_difffuzz.py::test_ci_run` fails: the DF-19 envelope
   entry changes and five `norms@0` wire entries are fixed. The restored build reproduces the pinned hash.
9. Fix 4: `gap_sentence` derives the completed value from the completion instead of Lean's `value`.
   `test_rendered_text_follows_leans_fields_not_a_recomputation` fails.
10. Fix 4: `gap_sentence` evaluates the value with `document.value`.
    `test_renderers_reach_no_evaluation_search_or_limit` fails.
11. Fix 4, Lean: the `under` value negated, so Lean's field differs from the English the fixtures state. The four
    `test_latent_fixture_renders_in_under_two_seconds` cases and the one-act latent test fail; the restored build
    reproduces the pinned hash.
12. Fix 4, Lean: `completedLabel` completes `deny` as yes. The build fails: `value3_gap` no longer proves.
