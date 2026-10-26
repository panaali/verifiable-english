# ap-1bb build report: Lean's environment identity in Python, and Lean's wordings of plain acts relayed

**No DRI signature is reserved; nothing stops the item.** DELTA rows: R16 (trust, untied V +35, K +0), R3 (the
added `wordings` and the environment row's `acts`), and the DRI's SYNTHESIS 2.2/4.2 decision ap-1b's DELTA row 2 cites
(the A19 load, the display).
Parts (3)-(5) of the task are cut to the next item, **ap-1bc** (section 6): size, and (3) needs files jt-2 edits.

Plan and spec on `main` (byte-identical to `c5197da78`): [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) 4 "AP-1",
2.1, 2.5, 2.8; [act-phrases.md](../../spec/act-phrases.md) 3.1-3.3, 4.4, 14.3; [ap-1b's REPORT](../ap-1b/REPORT.md)
sections 2, 3 (deviations 3 and 4) and 6.

## 0. Fix round 1 (`manage-agents/ap-1bb-review.final.md`)

Both B findings fixed as classes; each review probe failed before its fix and passes after, and is a regression test.

| Finding | Fix (the class) | Regression tests | Commits |
|---|---|---|---|
| F1 (B) one `environment_id`, two `to_dict()` (U+2019 and U+0027) | **One identity, one environment.** Lean's environment row gives each regulated act in the canonical form its identity hashes (`Norms.Wire.canonicalActs`, the row's `acts`, typed by its shape, `environment_fits`; `{}` for ve.core@0.1); Python stores that act, hashes `to_dict()` again and `validated_environment` checks it against Lean's `environment_id` (R8), so every cache keyed by the identity (lexicon, encoded requests, definitions, English, accepted rows: the review's sweep) holds one environment per key; the acts' names are bound to the request | `tests/test_acts_profile.py::test_one_identity_is_one_environment_whichever_loads_first` (the probe, both orders: `to_dict`, lexicon, legend, request bytes), `::test_acts_not_bound_to_the_request_are_unavailable` (8), `::test_a_retyped_acts_field_fails_the_schema` (13), `::test_an_act_with_a_curly_apostrophe_has_leans_identity`; `tests/test_stage2_validation.py::test_a_row_naming_another_identity_is_unavailable`, `::test_a_mismatched_identity_is_unavailable_and_an_accepted_row_is_cached`; `environmentRow` guards in `ActsExamples.lean`; `tests/test_difffuzz.py` (the row's `acts` retyped and dropped) | `caf80f1b1`, `bcf0eb544`, `021def33f`, `9448778` |
| F2 (B) a wording's `{i}` slots not bound to the arity | **One slot check for every relayed wording template**: `relay.slots_bound` (every brace a canonical `{i}`, the slots exactly `0 … arity-1`), used by both norms readers (`_bind_wordings`) and by the rights relay, whose own `Formatter` check it replaces | `tests/test_acts_profile.py::test_wordings_not_bound_to_the_request_are_unavailable` (6 slot mutants added: past the arity, left out, `{01}`, a format spec, a stray brace, `{1}` in a unary wording; both readers), `::test_slots_bound_is_the_one_slot_binding_of_every_relayed_wording` (17), `tests/test_rights.py::test_a_generated_wording_whose_slots_are_not_its_predicates_arguments_is_unavailable` (5) | `ed70a5715`, `caf80f1b1` |
| F3 (C) | not fixed (C): the words route's plain-act refusal is a FOLLOW-UPS row ("## ap-1bb") | — | — |
| F4 (C) | the U+2019 environment now reads and has a legend (Python's modal wording reads Lean's canonical act: DELTA row 2, `probe:read/A19`, `probe:legend/A19`); relaying the modal wordings is a FOLLOW-UPS row | — | — |

Pre-existing failures (`manage-agents/main-known-red.txt`): none was selected or touched.

## 1. Statement gate, order and overlap

The spec's statement review converged (14.3, FIX applied), the gate of ap-1a and ap-1b. No approved theorem changed:
`lean/statements.txt` is unchanged by this item (`gate_acts`, `decodeRegulated_without_acts`,
`canonicalActIn_without_acts` and every other statement keep their text), and no theorem was added.
**Overlap** (hand-written files of branches in flight): `feature/jt-2` edits `lean/VE/Service/Standalone.lean` and
`lean/VE/Readings/Wire.lean`, which (3) and the typing of an `acts@0` document need: not touched here (section 6).
`foundation/me-1` edits `ve/english.py` (its comparison rows, 480 lines above this item's hunk). Not touched:
`lean/VE/Service/Protocol.lean`, `ve/backends/service_schema.py`, `lean/VE/Acts/LexicalProofs.lean`.

## 2. Task rows delivered and not delivered

| Task part | Status | Where |
|---|---|---|
| (1) Python's environment identity from Lean's canonical environment, U+2019 fixture | **done** (fix round 1): Python stores the canonical acts Lean's environment row gives, so `to_dict()` is the environment Lean's identity hashes, and checks Lean's `environment_id` against it; Python's own act canonicalisation is gone from the Lean-built path (deviation 4) | `ve/backends/validation.py`, `ve/environment.py`, `Service/Standalone.lean`; DELTA rows 2, 5 |
| (2) Lean's selected wordings relayed (typed, bound), as a field of a norms-route answer, no new mode | **done**: `norms-elaborate`'s `wordings` (`Norms.Wire.plainWordings`; `modalForm` reads the same `plainWording`), typed by its shape and the encoder theorem, bound by `ve/norms.py` (`_bind_wordings`, both readers) | DELTA row 3 |
| (2) `ve/printer.py` renders a plain act with Lean's wording (A1 109 B, A21 414 B); Python computes none | **partly**: `EnglishVocabulary` (the vocabulary of `printer.render`'s `ve_natural` and `ve_english` views) installs Lean's wording (A1, A21 tested); a whole `acts@0` document cannot be rendered yet, because typing (`check` mode, `Standalone.typingReduced`) refuses `acts@0` before any view runs. `norm-defaults@0` environments keep the base display (the norms route does not read them) | `ve/english.py`, `ve/norms.py`; DELTA row 4; ap-1bc |
| (3) the readings route's decoder and Lean's model path read `acts@0`; the model oracle re-recorded | **ap-1bc**: `Readings/Wire.lean` and `Standalone.lean` are jt-2's in flight | — |
| (4) `Words/Situation.lean`'s regulated decode | **ap-1bc** (size) | — |
| (5) `ve/wire_contract/acts@0.json`, registry entry, examples, catalogue | **ap-1bc** (size) | — |

## 3. Deviations

1. **The display path reads one route.** `plain_wordings` asks the norms route's `norms-elaborate` over the
   environment alone (cached per request by `relay.decide_once`), so a vocabulary built without a document still
   shows Lean's wording; the document's own row is bound the same way.
2. **`norm-defaults@0`** with a plain act keeps the base's fallback display: its route gives no wordings yet.
3. **Projections keep the act as written.** Soft-norms and reports projections (`_validated_projection`,
   `_generated_reports`) are not built from an environment row: they keep each act as written (whitespace folded, as
   before) and bind their identity against their own Lean answers; both profiles refuse `acts@0`.

## 4. Seeded bugs

[seed_bugs.py](seed_bugs.py) plants, runs and restores each; [mutants.json](mutants.json) has `file`, `test` and the
first failure. **26 bugs, all killed** (Lean 13, Python 13; 14 added and one re-planted at fix round 1).

| Definition (file) | Bug: what fails |
|---|---|
| `plainWording` (`Norms/Wire.lean`) | form ignored; role ignored: `ActsExamples` guards |
| `plainWordings` (`Norms/Wire.lean`) | first predicate only; the declaration read instead of its `regulated`: `ActsExamples` guards |
| `Norms.Run.runCase` (`Norms/Run.lean`) | wordings emptied: guards; wordings written as an array: `ResponseShape.Encoders.Norms` (encoder theorem) |
| `modalForm` (`EnglishGrammar/Encode.lean`) | plain wording dropped: `ActsExamples` wordings guard |
| `canonicalActs` (`Norms/Wire.lean`) | no act listed; every act under one name: `ActsExamples` guards |
| `Standalone.environmentCase` (`Service/Standalone.lean`) | acts of the source, not the canonical environment; acts emptied: `ActsExamples` guards; `acts` renamed, dropped from the ve.core@0.1 row: `ResponseShape.Encoders.Standalone.environment_fits` |
| `validated_environment` (`ve/backends/validation.py`) | identity unchecked: `test_acts_not_bound_to_the_request_are_unavailable[changed]` |
| `Environment._decode` (`ve/environment.py`) | the act as written; the acts' names unbound: `test_one_identity_is_one_environment_whichever_loads_first[curly]`, `test_acts_not_bound_to_the_request_are_unavailable[undeclared]` |
| `slots_bound` (`ve/backends/relay.py`), its callers (`ve/norms.py`, `ve/rights_route.py`) | names only; a subset of the slots; a slot past the arity; braces unchecked; the rights check off: `test_wordings_not_bound_to_the_request_are_unavailable[slot-past-arity]`, `test_slots_bound_is_the_one_slot_binding_of_every_relayed_wording`, `test_a_generated_wording_whose_slots_are_not_its_predicates_arguments_is_unavailable[past-arity]` |
| `EnglishVocabulary` (`ve/english.py`) | wordings not installed: `test_a_plain_act_reads_with_the_wording_lean_selected` |
| `_bind_wordings`, `_lean_regenerated`, `plain_wordings` (`ve/norms.py`) | binding off; document binding off; `norm-defaults@0` asked; asked without a plain act: `test_wordings_not_bound_to_the_request_are_unavailable`, `test_norm_defaults_keeps_todays_display_without_asking`, `test_an_environment_without_a_plain_act_asks_lean_nothing_to_display` |

No Rust code changed.

## 5. Trust, size, evidence and tests

- **Trust:** `trust_map.py --check` PASS against `ba2532a22`: K +0, S +0, untied V +35 (per file in DELTA row 1),
  two allowances signed by R16 (V +18, V +17); FOLLOW-UPS has the "## ap-1bb" rows. `trust_mutants`
  ([trust-mutants.json](trust-mutants.json): full run at `bcf0eb544`, then `--rescore` after the allow-only edit):
  138 mutants of 6 definitions, 104 KILLED, 0 SURVIVOR, 0 UNKNOWN, 20 INVALID, 14 ALLOWED (equivalent or not
  elaborating, one reason each in [trust-mutants-allow.json](trust-mutants-allow.json)); `plainWording`,
  `canonicalActs` and `modalForm` by the seeded bugs too.
- **Size** (hand-written lines added, `git diff --numstat` against the merge base): product Lean 60 (with the two shape
  pins), Python 83, Lean fixtures 64, tests 293, evidence scripts 275, side tables about 30, DELTA and this report
  about 150: about 955.
- **Evidence:** [evidence/delta.json](evidence/delta.json) (335 records, 327 identical; base and head each recorded
  with its own checkout, at fix round 1); [evidence/commits.txt](evidence/commits.txt) (`git log main..HEAD --no-merges`, through the commit before the one that adds it).
- **Generated** (`regen_generated.py --write`; `--check` passes, 33 entries): `norms.json`, `environment.json`,
  the assurance manifest's `Norms/Wire.lean` pin (ranges reviewed: one declaration added), consolidation row 8b, inventories, `checkers.lock`, the English grammar lock
  (`actions_version` 34: `Encode.lean` changed); the binding census with its answers re-asked
  (`binding_census.py --answers`, then `--write`).
- **Tests (fix round 1):** `lake build` (1,064 jobs), `lean/audit.py` PASS; selected tests (`mac-pytest.sh --select`,
  377 units) at `94487786`: all pass (the first run at `60fa1bd6` failed `test_route_tables_are_the_genuine_rows_fields`,
  the environment row's new member, and `test_committed_ledger_names_real_declarations`, row 8b: both fixed in
  `94487786`); `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
- **Tests (first round):** `lake build` (1,064 jobs), `lean/audit.py`, `tests/test_acts_profile.py` (42), `tests/test_stage2_validation.py`;
  selected tests (`mac-pytest.sh --select`, 377 of 461 units: Lean and `checkers.lock` changed) at `9d9c8ccba`: all pass but
  one (`test_regen_generated`: `delta.py`'s `--record` flag; renamed `--answers` in `5a42ff396`, the file passes).
  `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed. The full gate is the chain's.
- **Pilot bytes expected to move:** 0 B (*estimate*): the display of entitlement lines needs ap-1bc's typing.

## 6. Next item: ap-1bc

Typing and the model path reading `acts@0` (`Standalone.typingReduced` and `modelEnvironment`, after jt-2 merges),
so `printer.render` shows a whole `acts@0` document; the readings route's decoder (`Readings/Wire.lean`) and the
model oracle's `acts@0` answers re-recorded by its tool (deviation 3); the norm-defaults route's wordings;
`Words/Situation.lean`'s regulated decode; `ve/wire_contract/acts@0.json` with its registry, examples and catalogue.
Then AP-3.

## 7. Self-review against BUILDER-CHECKLIST

One line per item of `manage-agents/BUILDER-CHECKLIST.md`.

1. PASS: `test_a_retyped_wordings_field_fails_the_schema` and `test_a_retyped_acts_field_fails_the_schema` (14 and 13 values through `_decode_json`: retypes, `"\ud800"`, a 10,000-deep list, the member deleted; the genuine answer passes the same path).
2. PASS: section 2 copies each task part with its commit and test; (3)-(5) cut by the size rule to ap-1bc; no Python wording, no report test (`git diff main...HEAD`).
3. PASS: [mutants.json](mutants.json) (26 killed), [trust-mutants.json](trust-mutants.json) (0 SURVIVOR, 0 UNKNOWN); `delta.py --compare` exits 1 head against head and on empty input.
4. PASS: [evidence/delta.json](evidence/delta.json) (327 of 335 identical, each checkout with its own client); `test_rust_refuses_an_acts_environment` unchanged.
5. PASS: `test_wordings_not_bound_to_the_request_are_unavailable` (undeclared, a non-plain predicate, renamed, emptied, dropped, and six slot mutants; both readers), `test_acts_not_bound_to_the_request_are_unavailable` (8); a duplicated name is refused by `_decode_json`.
6. PASS: `git merge-tree --write-tree HEAD main` is clean; [evidence/commits.txt](evidence/commits.txt) from `main..HEAD --no-merges`, base `git merge-base`; the gate is the chain's, on the final HEAD.
7. PASS: DELTA rows cite R16, R3 (rows 3, 5) and the DRI decision files ap-1b's DELTA row 2 cites; no signature reserved.
8. PASS: every changed record of `evidence/delta.json` is a DELTA row (rows 2-5), counts recomputed.
9. PASS: `select_tests` picks 377 of 461 units (Lean and `checkers.lock` changed), including `tests/test_acts_profile.py`, which every Python seeded bug fails.
10. PASS: `runCase-wordings-renamed` fails `ResponseShape.Encoders.Norms.runCaseReported_fits`; `lean/statements.txt` unchanged.
11. N.A.: no budget, limit or deadline code changed.
12. PASS: `test_an_environment_without_a_plain_act_asks_lean_nothing_to_display` (no Lean call to display an environment without a plain act; seeded bug `py-asked-without-acts`); one cached call otherwise.
13. PASS: three `Test-removed` trailers in `9524e3792`, two more naming the restored identity tests' renames in `9448778`; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
