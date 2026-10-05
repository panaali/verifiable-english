# Lean-first batch 3: DELTA

Base `776a64d7` (`lean-first/b0` with the DRI's signatures), head `lean-first/b3`. Gate item 2 of
`docs/LEAN-FIRST-PLAN.md` 5.1: every public result of the corpora below, base against head, by
`tools/lean_first_diff.py` (each side recorded from its own checkout and builds; the base from a clean worktree of
`776a64d7`), then `compare --delta docs/lean-first/b3/delta.json`.

## Result

| Corpus | Records per side | Same | Wording | Order | Verdict | Availability |
|---|---:|---:|---:|---:|---:|---:|
| probe, `python` | 9,435 | 9,435 | 0 | 0 | 0 | 0 |
| probe, `lean` | 9,435 | 9,435 | 0 | 0 | 0 | 0 |
| conformance, `python` | 19,806 | 19,806 | 0 | 0 | 0 | 0 |
| conformance, `lean` | 19,806 | 19,806 | 0 | 0 | 0 | 0 |
| pilots (`ve document check`, default authority) | 237 | 234 | 3 | 0 | 0 | 0 |
| readings (`readings_route.validate`, new in this batch) | 1,137 | 1,086 | 0 | 0 | 0 | 51 |
| **All** | 59,856 | 59,802 | 3 | 0 | 0 | 51 |

`compare` exits 0 with `"unlisted": 0`. The head's probe and conformance records are of the head's final `ve/`
and `lean/`; the readings and pilot records were taken again after the last code change, on both sides for the
pilots (a new pilot branch, `pilot/cc-20261004T1800Z`, appeared during the batch, so the corpus is 237 documents,
23 more than batch 0's).

The **readings corpus** is new (`tools/lean_first_diff.py --corpus readings`): batch 0's corpora did not reach the
readings route except through the constitution pilot's S1 documents. It is the 1,000 documents of the readings
differential (`tests/test_readings_s1_differential.py`: twins, renamed twins, mixed kinds, two acts, rights
candidates, eleven kinds of fault, the search's situations recorded) and the 137 environment-null cases of
`tests/test_readings_s1_lean.py`, generated once by the head and read by both sides from one file (SHA-256
`4f18eaa2…`). All 1,000 differential documents get the same answer on both sides; 621 of the 1,137 are admitted
on both. Batch 3 changes no answer on any document that had one.

## W3: the report's `checked_by` no longer names a Python regeneration or a Rust replay (`wording`, one block)

The readings report (`readings_route.CHECKED_BY`, composition-s1.md 6) said which checker covered what. Its
`python` entry claimed "Python's regeneration of Lean's answer, byte for byte" and its `rust` entry "untrusted
evaluation of every recorded situation (10)"; both are deleted, so the entry is shortened and the `rust` member
removed. The three constitution-pilot S1 documents (`pilot/cc-20261003T0600Z`, `cc-20261004T0600Z`,
`cc-20261004T1800Z`, each `readings/s1.ve.md`) are the records; nothing else in their reports changed.
`tools/lean_first_diff.py` now records a JSON report parsed and compares a `checked_by` member as one text pair
(`test_a_reports_description_is_one_wording_pair`).

| Id | Base | Head | Records |
|---|---|---|---:|
| W3.1 | `"python": "W2 structure of the reading sets, couplings and narrowings (S1 limitation, DRI ruling 3: Lean does not decode them); Python's regeneration of Lean's answer, byte for byte"`, `"rust": "untrusted evaluation of every recorded situation (10)"` | `"python": "W2 structure of the reading sets, couplings and narrowings (S1 limitation, DRI ruling 3: Lean does not decode them)"`, no `rust` | 3 |

**Signature:** DRI, wording block W3 — signed 2026-10-04 (Lean's texts are canonical).

## A3: the readings route answers Lean's diagnostic where Python's regeneration disagreed (`availability`)

Before this batch `ve/readings_route.validate` raised `CheckerUnavailable` ("ReadingsConformance: Python and Lean
differ on readings-validate") whenever Python's regenerated answer differed from Lean's row. The regeneration is
deleted, so the route raises Lean's diagnostic instead. Every one of the 51 inputs is a **rejection** at the head:
none becomes an admission, so no document is accepted that the base refused to answer for. They are the
environment-null cases of `tests/test_readings_s1_lean.py` whose environment, without the field, Lean and Python's
decoders refused with different texts (`_known_text_difference`, pinned at the base as `CheckerUnavailable`):

| Lean's diagnostic at the head | Records |
|---|---:|
| `fields do not match: expected [arguments, description], got [description]` | 12 |
| `fields do not match: expected [arguments, description], got [arguments]` | 12 |
| `fields do not match: expected [description], got []` | 8 |
| `invalid signature: asks` | 6 |
| `UnknownSymbol: regulated predicate avoid_required` | 4 |
| `invalid signature: arbitrary_arrest` | 2 |
| `fields do not match: expected [language, profiles, spec_revision, vocabulary], got […]` (one per missing field) | 3 |
| `fields do not match: expected [sorts, predicates, constants], got […]` | 2 |
| `property not found: predicates`, `property not found: vocabulary` | 2 |

The 51 records, each with both outcomes, are `availability` in [`delta.json`](delta.json). The head raises
Lean's text verbatim as a `VEError` (code `InvalidInput`): the readings route is still a one-shot runner whose rows
carry no `code`, so the class of a coded text (`UnknownSymbol: …`) is not yet the code's; batch 1 moves the route
into the service, whose rows carry Lean's code. The test that pinned the base's answer now pins Lean's
(`test_explicit_null_is_absent_in_the_environment`, `routed == row` on every case, and Lean refuses each of the 51).

This is the class plan section 5.2 names for batch 3 ("a readings disagreement is `CheckerUnavailable` today, and
relaying turns it into whatever Lean says"). Batch 0's triage put readings disagreements in group R1 (class ii,
`docs/lean-first/b0/TRIAGE.md`): the contract is silent and Lean's answer is sound.

**Signature:** DRI, availability A3 (51 records) — signed 2026-10-04: where Python's regeneration disagreed with Lean, Lean's diagnostic is the answer (one owner).

## Rest of the gate (5.1)

- **Suite (item 1).** The full suite at `ffeddcc3` (the head's code; later commits change this file only), 16
  chunks and the English merge smoke, `VE_NATIVE_PREBUILT=1`, `-n 3` per chunk: **8,774 passed, 6 skipped** (the
  usual optional dependencies), merge smoke 1 passed, no failure. An earlier run at `64a3bf25` had 51 failures in
  `tests/test_environment_field_types.py`: `S1Environment` was still listed there as a validating entry, and it no
  longer validates (rule 2). The test now lists the entries that validate, and the nested-value test keeps
  `S1Environment`, so a caller before Lean (the search, `document._s1_attached`) still never crashes
  (`71a1f547`: `S1Environment` reads the profiles of the environment it built). Test changes are the ones this batch's deletions require: Python's
  regeneration is no longer compared (`test_readings_s1_lean.py` `agreed` now checks the relay;
  `test_readings_s1_differential.py` checks the search against Lean and the relay against Lean's row), and the
  new `tests/test_readings_route_relay.py`. `tools/gate_collection.py --write`: 46 IDs added, 1 removed
  (`test_generated_sets_agree_with_lean`, renamed `test_generated_sets_lean_answers`). Gate stages outside pytest
  on the head: `tools/wire_contract.py --check`, `tools/relay_lint.py` (2 relayed modules),
  `tools/check_python_layers.py`, `tools/check_rust_deps.py`, `lint-imports` and `lean/audit.py` (287 files,
  3,045 theorems, standard axioms only) pass; `lake build` replays clean (no Lean change).
- **Differential fuzzer (item 2).** `infra/difffuzz` (`7c34a1a8`) merged onto `b3844521` (`f81f36e6`, a scratch
  worktree; the only later code change is `71a1f547`'s one line of `ve/readings_s1.py`, which no fuzzer surface
  reaches). The base side is batch 0's head-side run (`ve-lf-0/.lf0`: `df-head2.json` and `seeds-head/`), whose
  `ve/`, `lean/`, `rust/` and fuzzer equal this batch's base but for one line of `ve/assurance-manifest.json` (a
  reviewed handler's name). CI sample: 23 new signatures on each side, the same ones, 329 baseline entries seen and
  80 not reproduced on each side. The 13 date seeds 20260921 to 20261003 (`--deep 1` each): per seed the same
  counts on both sides (new 66–77, seen 255–269, not reproduced 80), no head-only signature, no baseline entry
  reproduced on one side only. 14 seeds in all; the baseline does not grow. The fuzzer does not reach the readings
  route (`conformance/DIFFFUZZ.md`: no fixture environment takes it), so the readings corpus above is this batch's
  differential evidence for it.
- **Deletion ledger (item 3).** [`LEDGER.md`](LEDGER.md): 12 deleted decision sites mapped to their Lean owner,
  4 retained duplicates named with the batch that removes them; `tools/relay_lint.py` covers the readings route.
- **Latency (item 4).** [`timing.py`](timing.py), base and head on the same host, which other workers were loading
  (load 8 to 46); CPU is the comparison, wall is noisy:

  | Run | Load | Base wall / Python CPU / Lean+Rust CPU (s) | Head wall / Python CPU / Lean CPU (s) | CPU change |
  |---|---|---|---|---|
  | readings corpus (1,137 validates), 1 | 8 → 38 | 151.6 / 33.3 / 118.3 | 232.9 / 1.9 / 106.4 | −29% |
  | readings corpus, 2 | 43 | 484.9 / 46.9 / 163.9 | 317.4 / 2.0 / 110.3 | −47% |
  | readings corpus, 3 | 46 → 34 | 219.4 / 33.3 / 119.1 | 109.8 / 1.5 / 74.6 | −50% |

  Python's own CPU on the route falls by 94–96% (the regeneration and its rights calls); what remains is Lean's
  one-shot process per document and the transport. Constitution pilot, `ve document check` of each S1 document
  (two runs each, children CPU): `cc-20261003T0600Z` 6.5 and 8.0 s → 4.3 and 4.3 s; `cc-20261004T0600Z` 6.2 and
  5.5 s → 3.1 and 3.0 s; `cc-20261004T1800Z` 5.8 and 6.4 s → 2.8 and 3.0 s (mean 6.4 s → 3.4 s, −47%), 3 to
  9.5 s of wall each, inside the pilot budget of section 4 (120 s). No measured operation is slower.
  The UDHR pilot (`pilot/udhr-20261003T0600Z` translation) is `CheckerUnavailable` on both sides, the same record:
  its one Lean readings call needs about 1,161 s of CPU against the route's 120 s limit, and the Lean call comes
  first, so the base never reached the Python regeneration this batch deletes (plan F5a: about 938 s of CPU,
  918 s of it the rights calls). The UDHR load is not measured end to end here; batches 3b to 3e carry it.

## Seeded bugs (build checklist 13)

Each was applied alone, its test run, then the file restored (`git status` clean after):

| Mutant | Behaviour it breaks | Failing test |
|---|---|---|
| M1 `validate` raises `CheckerUnavailable` for a Lean error row | Lean's rejection is relayed with its text | `test_an_error_row_is_raised_with_leans_text` |
| M2 `_bound` accepts any row | a row not bound to the request is operational | `test_a_row_not_bound_to_the_request_is_unavailable` |
| M3 the E25 sentence is always added | the English reads Lean's `SeparatedByDecisionOnly` | `test_the_decision_only_sentence_follows_leans_finding` |
| M4 `_built` converts nothing | a construction failure after admission is `CheckerUnavailable` | `test_a_construction_failure_after_lean_admitted_is_unavailable` |
| M5 the search's outcome evaluation negated | the rule-3 duplicate stays in step with Lean | `test_generated_sets_lean_answers` |
| M6 the A/B tool treats `checked_by` as a verdict | a report's description is one wording pair | `test_a_reports_description_is_one_wording_pair` |
| M7 `separated` may be false | Lean answers only separated pairs | `test_every_mutant_of_a_genuine_answer_is_unavailable` |
| M8 the containment does not catch `TypeError` | a failure of the check itself is operational | `test_a_failure_of_the_check_itself_is_contained` |
| M9 pairs not bound | every ordered pair of non-pending candidates, in order, with its situation and witness | `test_a_row_not_bound_to_the_request_is_unavailable` |
| M10 `sets` may be empty | `content_bearing: true` has a set | `test_the_schema_alone_refuses_every_type_fault` |
| M11 `document_hash` any string | a hash is 64 lowercase hex digits | `test_every_mutant_of_a_genuine_answer_is_unavailable` |
| M12 `witness_value` unbound | the witness shows the recorded value | `test_a_row_not_bound_to_the_request_is_unavailable` |
| M13 finding order unchecked | findings in `setFindings`' order, once each | `test_a_row_not_bound_to_the_request_is_unavailable` |
| M14 repeated keys allowed | a candidate's keys are deduplicated | `test_a_row_not_bound_to_the_request_is_unavailable` |
| M15 a key any object | keys are `keyJson`'s constructors (`KEY_FIELDS`) | `test_the_schema_alone_refuses_every_type_fault` |
| M16 `content_bearing` unbound | `content_bearing` is bound to the request's sets | `test_the_binding_alone_refuses_every_well_typed_mutant` |

| M17 an error row skips its identity check | an error row names its case (`id` or `case_index`) | `test_a_replayed_error_not_naming_the_request_is_unavailable` |
| M18 the transport decodes in `subprocess.run` (`text=True`) | bytes that are not UTF-8 are no answer | `test_no_answer_to_the_case_is_unavailable_on_every_transport` |
| M19 the reader guesses the encoding (`json.loads` on bytes) | an answer is UTF-8 | `test_no_answer_to_the_case_is_unavailable_on_every_transport` |
| M20 an error row may carry any member | error rows are Lean's encoder shapes (`ERROR_EXTRAS`) | `test_no_answer_to_the_case_is_unavailable_on_every_transport` |
| M21 a Rust error record is not checked | a Rust error is ve-core's `Error` | `test_a_rust_record_that_is_no_answer_is_unavailable` |

M7 to M16 were added for review lf-3 and M17 to M21 for its recheck (below); each was applied alone, the route
test files run, and the file restored.

## Review lf-3: the answer's schema and binding (B1, B2)

The relay's first binding check (`_bound`) failed open: a genuine row with `sets` or `pairs` emptied, a pair
duplicated, a key of no constructor, an empty hash or `separated: false` was accepted (and `separated: false`
reached the English as "They differ here"), and a set id retyped to `[]` or a situation id to `{}` escaped as
`TypeError`. `ve/readings_route.py` `_check` replaces it: the schema `ROW`, written from `Run.lean`'s encoders,
is checked over the whole row before anything is compared or hashed; `_bind` then checks what the request fixes
(the content-bearing sets in source order, candidates and pending states, every ordered pair of non-pending
candidates with its situation and witness) and the producer's invariants (`separated` and `witness_admissible`
true, `witness_value` the recorded value, `other_value` present exactly when the other side owns no key, decisions
owned by the witness and fixed tables by neither, findings in `setFindings`' text and order); any failure of the
check is `CheckerUnavailable`. Keys are read through one table (`readings_s1.KEY_FIELDS`) for `key_json`,
`decode_key` and the schema; the English reads findings with the check's parser; the transport reads with the
Lean service's strict JSON reader (a repeated member, deep nesting); the unused, unchecked `separate_many` is
deleted. `tests/test_readings_route_fuzz.py` mutates every node of 12 genuine rows (over 5,000 mutants, and
two-fault mutants): only `CheckerUnavailable` escapes, and an accepted mutant changed only what Lean alone decides.
The readings and pilot corpora recorded again at the fix (1,374 records) are the same as the head's records above,
record for record (`compare`: 1,374 same, 0 unlisted).

## Recheck lf-3 looprecheck1: error rows and decoding (B1, B2)

Error rows were not bound: a genuine Lean error replayed against valid K1 with its `id` changed, `[]` or omitted
rejected the document. Decoding was outside the guard: a checker writing the byte 0xff made `validate` raise
`UnicodeDecodeError` (`text=True` decoded in `subprocess.run`). Both came from one class: each one-shot route
transport checked its own answer, some in fewer ways than others. `ve/backends/lean.py` `route_rows` is now the one
transport of the soft, rights, alternatives, risk, reports, discourse, norm-defaults and readings routes. It reads
bytes through `_decode_json`, the one reader of Lean and Rust answers: strict UTF-8, no repeated member, no non-JSON
number, and nesting past the limit is a `ValueError`. It checks every row with `row_problem`, the manifest runner's
check. An error row names its case by exactly one of `id` and `case_index` and carries no member outside
`ERROR_EXTRAS`, written from Lean's encoders. The soft route's operational failures are `CheckerUnavailable`, no
longer `VEError`. The Rust JSONL transport checks error records against ve-core's `Error`.
`tests/test_route_transport.py` runs every transport against 38 outputs that are no answer, using real temporary
checkers, and every built route binary against its own genuine error shapes. 171 of its 295 tests fail at the head.

## Not done here

- The UDHR load end to end (above); batches 3b to 3e.
- The retained duplicates of the ledger (attachment, generated keys, twins and acts for the English, the search's
  evaluation): no Lean work was in this batch's row.
- Coded classes on the readings route (a Lean text's code is not yet its Python class): batch 1.
- Statement review: no theorem changed.
