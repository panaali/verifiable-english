# ap-1be build report: the norm-defaults route's wordings of plain acts

**No DRI signature is reserved; nothing stops the item.** DELTA has three rows: R16 (trust, untied V +7, K +0, S +0),
R3 (the added `wordings` member) and the DRI decision files ap-1bb's DELTA row 4 cites (the display). Part (2), the
`acts@0` wire contract, is cut to **ap-1bf** by the size rule (section 5).

Plan and spec on `main` (byte-identical to `0e7a813e8`): [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) 4 "AP-1",
2.1, 2.5, 2.8; [act-phrases.md](../../spec/act-phrases.md) 3.1-3.3, 4.4, 14.3; [ap-1bc's REPORT](../ap-1bc/REPORT.md)
section 5, [ap-1bb's REPORT](../ap-1bb/REPORT.md) (deviation 2) and [df-1ae's REPORT](../../defeasible/df-1ae/REPORT.md).

## 0. Statement gate, order and overlap

The spec's statement review converged (14.3, FIX applied in draft 2): this is the gate ap-1a, ap-1b, ap-1bb and
ap-1bc took. No approved theorem changed: `lean/statements.txt` is unchanged by this item (`gate_acts`,
`decodeRegulated_without_acts`, `canonicalActIn_without_acts`, `decodeRegulated_plain` and every other statement keep
their text). No theorem was added; `runCaseReported_fits` (Norms and NormDefaults encoders) keeps its statement and
now covers the member (two simp lists name `wordingsJson`).

**Overlap** (hand-written files against `git diff --name-only <merge-base> <branch>` for every `lean-first/*`,
`feature/*`, `infra/*` and `foundation/*` branch ahead of `main`): only `tools/trust-classes.json`, the shared side
table (ap-2b, jt-2, me-2c, q1-4, qt-a3b, me-1 edit it too; this item adds five names to two existing lists).

Not touched: `lean/VE/Service/Protocol.lean`, `ve/backends/service_schema.py`, `lean/VE/Service/Standalone.lean`,
`lean/VE/Readings/Wire.lean`, `lean/VE/Acts/*`, `ve/defaults.py`, `ve/document/`. No service mode was added.

## 1. Task rows delivered and not delivered

| Task part | Status | Where |
|---|---|---|
| (1) a `wordings` member on `norm-defaults-elaborate` (`Norms.Wire.plainWordings` of the decoded source), with its shape and encoder theorem | **done**. `runOtherCase` writes `Norms.Run.wordingsJson s.src.ne`, the one encoding the norms route's row now uses too (one owner). The `elaborate` shape requires it (`string_map`, closed row, render pinned); the layered rows are unchanged, since `acts@0` with `soft-norms@0` or `rights@0` is refused | `2085f9013`, `c34045ec3`; `lean/VE/Service/ActsExamples.lean` section "ap-1be" (8 guards); DELTA row 2 |
| (1) bound in Python by `ve/norms.py`'s `_bind_wordings` (the same R8 check, slots by `relay.slots_bound`) | **done**, on both readers of the row: `plain_wordings` and `UnspecifiedDocument` (the document's own row), as ap-1bb bound both norms readers. The refusal names the row's kind | `e967aabc0`; `tests/test_acts_profile.py::test_norm_defaults_wordings_not_bound_to_the_request_are_unavailable` (12) |
| (1) `plain_wordings` asks it for `norm-defaults@0` environments | **done**: one cached request to `norm-defaults` (`relay.decide_once`), none without a plain act. This deletes ap-1bb deviation 2's fallback for those environments | `e967aabc0`; DELTA row 3 |
| (1) new answer fields carrying Lean's text under R3, with its test | **done**: DELTA row 2; the field equals Lean's text (`test_a_norm_defaults_environment_reads_with_the_wording_lean_selected`, the guard against Lean's English selection) | — |
| (1) every answer main gives unchanged apart from the new member, base against head on the recorded route cases | **done**: 363 cases, 360 identical, 3 differ by `"wordings": {}` only ([evidence/delta.json](evidence/delta.json)) | section 4 |
| (2) `ve/wire_contract/acts@0.json` with its own `acts@0`-aware environment hook | **cut to ap-1bf** (size: section 5) | — |

## 2. Deviations

1. **One encoding, two routes.** `wordingsJson` moved the norms route's inline encoding into a definition both rows
   call; the norms row's bytes are unchanged (every `norms` record of `evidence/delta.json` is identical).
2. **The document's row is bound too** (`UnspecifiedDocument`), though it does not read `wordings`; ap-1bb bound both
   norms readers the same way.
3. **`readings-choice`'s `inner`.** The readings route relays the lower route's row whole, so a choice whose inner case
   is a plain `norm-defaults-elaborate` row carries `wordings` (`{}` until ap-1bd lets the readings route read
   `acts@0`). `ve/readings_verdicts/choice.py` does not read it; ap-1bd, which makes it non-empty, should bind it
   there.
4. **The shape pin** reads JSON, so `ResponseShape/Schemas/NormDefaults.lean` is listed under the manifest's
   `other_json` with its reason, and the map counts one line of it as V (DELTA row 1). The consolidation plan's
   measured row 7 moved from 683 to 682 removed lines (`runCase`'s member line is one line shorter).
5. **`trust_mutants`** ran first directly on the VM (28 min), then through `mac-pytest.sh --trustmut` without
   `--rescore`, which fell back to the VM (no Mac slot in 600 s); both runs gave the same verdicts.

## 3. Seeded bugs

[seed_bugs.py](seed_bugs.py) plants, runs and restores each; [mutants.json](mutants.json) records `definition`,
`file`, `test` and the first failure. **8 bugs, all killed**: Lean 4, Python 4. No Rust code changed.

| Id | File (definition) | Bug | First failure |
|---|---|---|---|
| `nd-wordings-dropped` | `lean/VE/NormDefaults/Run.lean` (`runOtherCase`) | the member not written | `ActsExamples.lean:389` |
| `nd-wordings-renamed` | `lean/VE/NormDefaults/Run.lean` (`runOtherCase`) | written as `wording` | `ResponseShape.Encoders.NormDefaults` (`runCase_fits`: the closed shape) |
| `wordingsJson-names` | `lean/VE/Norms/Run.lean` (`wordingsJson`) | each value is the predicate's name | `ActsExamples.lean:231` |
| `shape-wordings-strings` | `lean/ResponseShape/Schemas/NormDefaults.lean` (`elaborate`) | typed as a list of strings | the render pin, `Schemas/NormDefaults.lean:374` |
| `py-nd-not-asked` | `ve/norms.py` (`plain_wordings`) | the base's fallback: `norm-defaults@0` asks nothing | `test_a_norm_defaults_environment_reads_with_the_wording_lean_selected` |
| `py-nd-norms-mode` | `ve/norms.py` (`plain_wordings`) | always asks the norms route | the same test |
| `py-nd-document-unbound` | `ve/norm_defaults.py` (`UnspecifiedDocument`) | the row's wordings not bound | `test_norm_defaults_wordings_not_bound_to_the_request_are_unavailable[dropped]` |
| `py-bind-subset` | `ve/norms.py` (`_bind_wordings`) | names checked as a subset | the same test, `[dropped]` |

R16 mutants per definition (`tools/trust_mutants.py --test lean/VE/Service/ActsExamples.lean`,
[trust-mutants.json](trust-mutants.json)): 45 mutants of `wordingsJson`, `Norms.Run.runCase`, `runOtherCase` and the
`elaborate` shape: 34 KILLED, 0 SURVIVOR, 0 UNKNOWN, 8 INVALID, 3 ALLOWED (cuts that do not elaborate, one reason each
in [trust-mutants-allow.json](trust-mutants-allow.json)). The first run without `--test` killed none (the guards live
outside the mutated modules' directories), and the elaborate shape's mutants survived until the render pin was added.

## 4. Trust, size, evidence and tests

- **Trust:** `trust_map.py --check` PASS against `a557ff887`: K +0, S +0, untied V +7 (per file in DELTA row 1), two
  allowances signed by R16 (V +6, V +1). `wordingsJson` is G[V], as `reportJson` beside it; the four new fixture
  definitions are `T`. FOLLOW-UPS has the "## ap-1be" row.
- **Size** (hand-written lines added or changed, `git diff --numstat` against the merge base): product Lean 18
  (`Run` 4, `Norms/Run` 5, shape 6, encoder simp lists 3), Lean fixtures and pins 43, Python 15, tests 97, evidence
  scripts 208 (`delta.py` 110, `seed_bugs.py` 98), side tables 33, DELTA and this report about 150: about 565.
  Measured at about 165 after part (1)'s code and tests; part (2) at 500-800 (ap-1bc) could not fit.
- **Evidence:** [evidence/delta.json](evidence/delta.json): 366 records, 361 identical, 4 `wordings` (the three
  recorded plain `norm-defaults-elaborate` rows and the A1-A3 probe), 1 `display`. Both sides were recorded by their
  own checkout's client against their own `ve_service`; `--compare` exits 1 head against head and on empty input.
  [evidence/commits.txt](evidence/commits.txt) is `git log main..HEAD --no-merges`, through the commit before the
  one that adds it.
- **Generated** (`regen_generated.py --write`; `--check` passes, 33 entries): `norm-defaults.json`, the binding
  census (answers re-asked with `binding_census.py --answers`), `lean/checkers.lock`, `lean/declarations.txt`.
- **Tests:**
  - `lake build` (1,117 jobs) and `lean/audit.py` PASS.
  - Selected tests (`mac-pytest.sh --select`, ve-mac-1) at `59e9314b`: 384 units, 4 failed:
    `test_trust_budget.py::test_trust_map_check_passes_on_the_live_tree` and
    `test_trust_ratchet.py::test_committed_budget_passes_its_check` (the shape pin's line, after the first allowance),
    `test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` (the pin reads JSON) and
    `test_consolidation_tools.py::test_committed_ledger_names_real_declarations` (row 7). Fixed in `cb010be57`; the
    four files then pass (535 passed).
  - `gate_collection.py --check --prebuilt`: 14 added, 1 removed by a trailer, 0 refused, 0 stale, 0 malformed.
  - Pre-existing failures (`main-known-red.txt`): none was selected or touched.
  - The full gate is the chain's.
- **Pilot bytes expected to move:** 0 B (*estimate*). No pilot environment lists `acts@0` yet; the UDHR's 8
  act-phrase units (1,403 B, M7) need ap-1bd's typing and model path.

## 5. Next items: ap-1bf, then ap-1bd

**ap-1bf** (part (2), cut by the size rule): `ve/wire_contract/acts@0.json` as ap-1bc's REPORT section 5 lists it: a
`UNITS` row in `tools/wire_contract.py`; a registry module in `conformance/`; two examples under
`ve/wire_contract/examples/acts@0/`; `conformance/wire_contract_faults_acts.py` writing
`conformance/wire-contract/acts@0-catalogue.json`; `lean/VE/WireContract/Hooks/Acts.lean` and its row in
`WireContract/Diagnose.lean`; tests, manifest and trust-class entries. Its blocker stands: `Hooks/Norms.lean`'s
`w1Environment` and `typingEnvironment` decode without `acts := true`, so the contract needs its own `acts@0`-aware
environment hook, and its limits (400-byte act, 300-byte phrase, 128 phrases) must be read from `VE.Acts.Lexical`,
never copied. The spec names no checks or codes for the contract.

**ap-1bd** (after jt-2 merges): typing and the model path read `acts@0`, the readings route's decoder, the model
oracle's answers; with it, bind `wordings` in a `readings-choice` answer's inner rows (deviation 3).

## 6. Self-review against BUILDER-CHECKLIST

One line per item of `manage-agents/BUILDER-CHECKLIST.md`.

1. PASS: `test_a_retyped_norm_defaults_wordings_field_fails_the_schema` (14 values through `_decode_json`: retypes, `7.5`, `"\ud800"`, a 10,000-deep list, the member deleted; the genuine exchange passes); `test_route_row_schemas.py` fuzzes the recorded norm-defaults rows (passed in the selected run).
2. PASS: section 1 copies each task part with its commit and test; (2) cut by the size rule to ap-1bf; no Python wording, no new report test, no file of an in-flight branch but the shared side table (section 0).
3. PASS: [mutants.json](mutants.json) (8 killed, Lean and Python), [trust-mutants.json](trust-mutants.json) (0 SURVIVOR, 0 UNKNOWN); `delta.py --compare` exits 1 head against head and on empty input.
4. PASS: [evidence/delta.json](evidence/delta.json), base and head side by side on the 363 route cases and three probes, each with its own client and service (361 identical).
5. PASS: `test_norm_defaults_wordings_not_bound_to_the_request_are_unavailable` (undeclared, a non-plain predicate, renamed, emptied, dropped, the member dropped, six slot mutants; both readers; the genuine row accepted).
6. PASS: base is `git merge-base HEAD main` (`a557ff887`, `main`'s tip); [evidence/commits.txt](evidence/commits.txt) from `main..HEAD --no-merges`; the gate is the chain's, on the final HEAD.
7. PASS: DELTA rows cite R16, R3 and the DRI decision files ap-1bb's row 4 cites; no signature reserved.
8. PASS: every changed record of `evidence/delta.json` is a DELTA row (rows 2 and 3), counts recomputed.
9. PASS: `select_tests.py --base a557ff887` selects 385 of 466 units (Lean and `checkers.lock` changed), including `tests/test_acts_profile.py`, which every Python seeded bug fails.
10. PASS: `nd-wordings-renamed` fails `ResponseShape.Encoders.NormDefaults.runCase_fits`; `shape-wordings-strings` fails the render pin; `lean/statements.txt` unchanged.
11. N.A.: no budget, limit or deadline code changed.
12. PASS: `test_an_environment_without_a_plain_act_asks_lean_nothing_to_display` (no Lean call for an environment without a plain act, now under `norm-defaults@0` too; seeded bug `py-nd-not-asked` shows the call is made only with one); one cached call otherwise.
13. PASS: the `Test-removed` trailer for `test_norm_defaults_keeps_todays_display_without_asking` in `7b04fcd28` (replaced by `test_a_norm_defaults_environment_reads_with_the_wording_lean_selected`); `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
