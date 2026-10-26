# ap-1bb build report: Lean's environment identity in Python, and Lean's wordings of plain acts relayed

**No DRI signature is reserved; nothing stops the item.** DELTA rows: R16 (trust, untied V +18, K +0), R3 (the
added `wordings`), and the DRI's SYNTHESIS 2.2/4.2 decision ap-1b's DELTA row 2 cites (the A19 load, the display).
Parts (3)-(5) of the task are cut to the next item, **ap-1bc** (section 6): size, and (3) needs files jt-2 edits.

Plan and spec on `main` (byte-identical to `c5197da78`): [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) 4 "AP-1",
2.1, 2.5, 2.8; [act-phrases.md](../../spec/act-phrases.md) 3.1-3.3, 4.4, 14.3; [ap-1b's REPORT](../ap-1b/REPORT.md)
sections 2, 3 (deviations 3 and 4) and 6.

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
| (1) Python's environment identity from Lean's canonical environment, Python's own computation deleted, U+2019 fixture | **done**: `validated_environment` builds the container with Lean's `environment_id` and no longer hashes `to_dict()` to compare it (deviation 4) | `ve/backends/validation.py`, `ve/environment.py`; DELTA row 2 |
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
3. **Projections still hash.** Soft-norms and reports projections (`_validated_projection`, `_generated_reports`)
   bind their identity against their own Lean answers by hashing `to_dict()`; both profiles refuse `acts@0`.

## 4. Seeded bugs

[seed_bugs.py](seed_bugs.py) plants, runs and restores each; [mutants.json](mutants.json) has `file`, `test` and the
first failure. **13 bugs, all killed** (Lean 7, Python 6).

| Definition (file) | Bug: what fails |
|---|---|
| `plainWording` (`Norms/Wire.lean`) | form ignored; role ignored: `ActsExamples` guards |
| `plainWordings` (`Norms/Wire.lean`) | first predicate only; the declaration read instead of its `regulated`: `ActsExamples` guards |
| `Norms.Run.runCase` (`Norms/Run.lean`) | wordings emptied: guards; wordings written as an array: `ResponseShape.Encoders.Norms` (encoder theorem) |
| `modalForm` (`EnglishGrammar/Encode.lean`) | plain wording dropped: `ActsExamples` wordings guard |
| `validated_environment` (`ve/backends/validation.py`) | Python's hash back: `test_an_act_with_a_curly_apostrophe_has_leans_identity` |
| `EnglishVocabulary` (`ve/english.py`) | wordings not installed: `test_a_plain_act_reads_with_the_wording_lean_selected` |
| `_bind_wordings`, `_lean_regenerated`, `plain_wordings` (`ve/norms.py`) | binding off; document binding off; `norm-defaults@0` asked; asked without a plain act: `test_wordings_not_bound_to_the_request_are_unavailable`, `test_norm_defaults_keeps_todays_display_without_asking`, `test_an_environment_without_a_plain_act_asks_lean_nothing_to_display` |

No Rust code changed.

## 5. Trust, size, evidence and tests

- **Trust:** `trust_map.py --check` PASS against `ba2532a22`: K +0, S +0, untied V +18 (per file in DELTA row 1),
  allowance signed by R16; FOLLOW-UPS has "## ap-1bb". `trust_mutants` ([trust-mutants.json](trust-mutants.json), full run at `adcdf78a5`): 79 mutants of 4 definitions, 52 KILLED, 0 SURVIVOR, 0 UNKNOWN, 16 INVALID, 11 ALLOWED (equivalent or not elaborating, one reason each in [trust-mutants-allow.json](trust-mutants-allow.json)); `plainWording` and `modalForm` by the seeded bugs.
- **Size** (hand-written lines added, `git diff --numstat` against the merge base): product Lean 33, Python 55, Lean
  fixtures 21, tests 151, evidence scripts 210, side tables 19, DELTA and this report about 115: about 605.
- **Evidence:** [evidence/delta.json](evidence/delta.json) (332 records, 327 identical; base and head each recorded
  with its own checkout); [evidence/commits.txt](evidence/commits.txt) (`git log main..HEAD --no-merges`, through the commit before the one that adds it).
- **Generated** (`regen_generated.py --write`): `norms.json`, inventories, `checkers.lock`, the English grammar lock
  (`actions_version` 34: `Encode.lean` changed); the binding census with its answers re-asked
  (`binding_census.py --answers`, then `--write`).
- **Tests:** `lake build` (1,064 jobs), `lean/audit.py`, `tests/test_acts_profile.py` (42), `tests/test_stage2_validation.py`;
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

1. PASS: `test_a_retyped_wordings_field_fails_the_schema` (14 values through `_decode_json`: retypes, `"\ud800"`, a 10,000-deep list, the member deleted; the genuine answer passes the same path).
2. PASS: section 2 copies each task part with its commit and test; (3)-(5) cut by the size rule to ap-1bc; no Python wording, no report test (`git diff main...HEAD`).
3. PASS: [mutants.json](mutants.json) (13 killed), [trust-mutants.json](trust-mutants.json) (0 SURVIVOR, 0 UNKNOWN); `delta.py --compare` exits 1 head against head and on empty input.
4. PASS: [evidence/delta.json](evidence/delta.json) (327 of 332 identical, each checkout with its own client); `test_rust_refuses_an_acts_environment` unchanged.
5. PASS: `test_wordings_not_bound_to_the_request_are_unavailable` (undeclared, a non-plain predicate, renamed, emptied, dropped; both readers); a duplicated name is refused by `_decode_json`.
6. PASS: `git merge-tree --write-tree HEAD main` is clean; [evidence/commits.txt](evidence/commits.txt) from `main..HEAD --no-merges`, base `git merge-base`; the gate is the chain's, on the final HEAD.
7. PASS: DELTA rows cite R16, R3 and the DRI decision files ap-1b's DELTA row 2 cites; no signature reserved.
8. PASS: every changed record of `evidence/delta.json` is a DELTA row (rows 2-4), counts recomputed.
9. PASS: `select_tests` picks 377 of 461 units (Lean and `checkers.lock` changed), including `tests/test_acts_profile.py`, which every Python seeded bug fails.
10. PASS: `runCase-wordings-renamed` fails `ResponseShape.Encoders.Norms.runCaseReported_fits`; `lean/statements.txt` unchanged.
11. N.A.: no budget, limit or deadline code changed.
12. PASS: `test_an_environment_without_a_plain_act_asks_lean_nothing_to_display` (no Lean call to display an environment without a plain act; seeded bug `py-asked-without-acts`); one cached call otherwise.
13. PASS: three `Test-removed` trailers in `9524e3792`; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
