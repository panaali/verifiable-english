# ap-1bd build report: typing, the model path and the readings route read `acts@0`

**No DRI signature is reserved; nothing stops the item.** Status: review FIX applied (F1, the one B; section 7):
selected tests (417 units) pass at `875f93c60`, `lake build`, `lean/audit.py`, regen and `trust_map --check` pass; trust
mutants (26 killed, 10 allowed) are from `501f211b`, not rerun after the fix (section 7). What changed: Lean types, models
and reads `acts@0` single acts on the readings route (D-33); u076 is CHECKED, also with `readings@1`, whose wordings now
come from the readings route. Open: ap-1bg (section 5), review C findings F2-F7 (section 7). Size: section 4 and 7.

Plan and spec on `main`: [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) 4 "AP-1";
[act-phrases.md](../../spec/act-phrases.md) 4.1-4.4, 6.4 (`Readings/Wire.lean`), 10 (D-33); `DRI-DECISIONS-PHASE2.md`
AP1; [ap-1bb](../ap-1bb/REPORT.md) section 6, [ap-1bc](../ap-1bc/REPORT.md) section 5, [ap-1be](../ap-1be/REPORT.md)
section 5 and deviation 3. DELTA: [DELTA.md](DELTA.md) (rows: R16; the `acts@0` row's DRI decision files; R1).

## 0. Statement gate, order and overlap

The spec's statement review converged on FIX, draft 2 applied it and act-phrases-p3ver1 verified it (PASS): the gate of
ap-1a to ap-1be. No approved statement changed: `lean/statements.txt` is byte-identical to the base (a first draft of
`singleActsOnly` used a `match` whose matcher Lean then shared with `candidateStage_eq`'s statement, changing its
recorded expression; it is written with `Option.elim` instead). jt-2 merged (`6b5d6cbb6`) before this item started.
**Overlap** (hand-written files against every `lean-first/*`, `feature/*`, `infra/*`, `foundation/*` branch ahead of
`main`): none in flight. `feature/sc-5rb` edits `ve/document/`, which this item does not touch;
`lean-first/b14b-evidence` (last commit 2026-10-12) edits `SoftNorms/Soften.lean`. Not touched: `lean/VE/Acts/`,
`lean/VE/NormDefaults/Run.lean`, `ve/document/`, `Service/Protocol.lean`, `ve/backends/service_schema.py`.

## 1. Task rows delivered and not delivered

| Task part | Status | Where |
|---|---|---|
| (1) `Standalone` typing and `modelEnvironment` read `acts@0`; an `acts@0` document types and Lean checks its models | **done**. One reader for both modes: `validated` decodes the envelope through `actsRead` (the base rows' gate on the list as written, then `Norms.Wire.actsView`, as the norms decoder reads it) and checks each `regulated` declaration with `regulatedOf` (`decodeRegulatedAllIn` with the environment's `actsProfiles` and `actsFixed`). `modelCase`'s profile check and `folBackground` use `regulatedOf` too. `typingReduced` and `modelEnvironment` pass `acts@0` through to `validated` unchanged | `Standalone.lean`; guards "ap-1bd" in `Service/ActsExamples.lean`; DELTA row 2 |
| (2) the readings route's frame decoder reads `acts@0` single acts; D-33 for a joined act | **done**. `decodeEnvironment` decodes the norms frame with `acts := true`; `singleActsOnly` gives D-33 where the norms decoder gives D-4. The norms chain's `Soften.checkW1` drops its refusal of a plain act, as `Tree.check` did in AP-1 (deviation 2). A document with a reading set over `acts@0` keeps the base's refusal (deviation 5, ap-1bg) | `Readings/Wire.lean`, `SoftNorms/Soften.lean`; `Readings/ActsExamples.lean`; DELTA rows 2, 3 |
| (3) the model oracle's `acts@0` answers re-recorded by its tool | **done**. `tests/b15b_model_cases.py record PATH --profile acts@0` answers again only the environments that list the profile and keeps every other saved row (a full re-record from the head changes 106 unrelated answers: fixture drift). The `acts@0` environment of the saved oracle is no longer among the fixtures, so its two environments are now fixtures (`tests/data/acts/`): A1-A3's (a permission act) is still refused by Rust, as recorded; the all-plain one is answered | `tests/data/b15b-model-oracle.json.gz`; `tests/test_model_environment.py` |
| (4) a part document with one UDHR act-phrase unit through `ve document check` | **done**. u076 (the pilot's probe, 123 B): CHECKED 123 B, premises `model`, rendered "Every person has the right to take part in the government of his country directly or through freely chosen representatives." Base: `UnsupportedProfile: Unsupported profile acts@0` | `test_a_udhr_act_phrase_unit_is_checked_end_to_end`; `evidence/delta.json` `probe:document/u076` |
| Python relays only (R8); a Python copy of a Lean decision this replaces is deleted (R6) | **done**: no Python decision added. `norm_defaults._Filled.base_environment` was a second copy of `NormDocument.base_environment`'s projection that lacked `acts@0`; both now call `norms.base_data` (one owner) | `ve/norms.py`, `ve/norm_defaults.py` |
| bind `wordings` in a `readings-choice` answer's inner rows (ap-1be deviation 3) | **nothing to bind**, measured: on the readings route the inner `norm-defaults-elaborate` row is the layered branch's and carries no `wordings` member | section 2 |

## 2. Deviations

1. **`validated` reads `acts@0`, not `typingReduced`.** Typing and the model check both reach `validated`, so one
   reader serves both (`actsRead`, `regulatedOf`); `typingReduced` and `modelEnvironment` are unchanged.
2. **`SoftNorms/Soften.lean`** (not in spec 4.1's hunk list): `checkW1` is the readings route's norms chain check and
   kept the refusal of `.plain, some _` that AP-1 dropped from `Tree.check` (SR4). A plain act still comes only from
   `acts@0` (`decodeRegulated_plain`), and `acts@0` with `soft-norms@0` is refused by its row.
3. **Rust's search view.** Rust refuses every `acts@0` environment (spec 12). Its model environment
   (`rust_jsonl.rust_environment`) drops a wording-only acts layer: when every regulated declaration is plain, the
   profile, the block and each plain `act`/`form` (`profiles.without_wording_acts`), which no model reads, as the
   `norm-defaults@0` row reads `unspecified` as `deny`. Lean checks every witness over the whole environment. Any
   other `acts@0` environment is passed unchanged and refused by Rust (ap-1bg).
4. **The readings-choice inner `wordings`**: see section 1's last row.
5. **A reading set over `acts@0` keeps the base's refusal.** With reading sets, the document check runs Python's
   superposed route, whose soft frame (`readings_s1.soft_frame`) adds `soft-norms@0`, which `acts@0` refuses. Measured
   on an F-ND1 variant: load passed and the check was `CheckerUnavailable: ReadingsConstruction` where the base
   refused at load. `decodeDocument` therefore refuses such a document with the base's own text (identical records);
   the filled environment's typed `form`/`acts`, its binding and fuzz tests, built for that path, were reverted with it
   (ap-1bg).

## 3. Seeded bugs

[mutants.json](mutants.json) records each bug's `file`, `definition`, the one check run and its first failure:
**17 killed** (Lean 11, Python 6; no Rust changed), and one recorded equivalent first plant (`folBackground`'s
`.drop 1` dropped the permission, whose dual the obligation still names; re-planted as the loss of every pair).

| Bug (file) | Killed by |
|---|---|
| `regulatedOf` without `acts@0`; without the fixed phrases (`Standalone.lean`) | `Service/ActsExamples.lean` typing guards |
| `actsRead` without the gate; returning the environment (`Standalone.lean`) | typing guards (the closure row; A1-A3) |
| `modelCase` without the profile pairs; `folBackground` without them (`Standalone.lean`) | the model and Background guards |
| `singleActsOnly` the identity; on any refusal (`Readings/Wire.lean`) | `Readings/ActsExamples.lean` D-33 and comma guards |
| `decodeEnvironment` with `acts := false`; `decodeDocument` admitting a reading set (`Readings/Wire.lean`) | `Readings/ActsExamples.lean` |
| `checkW1` refusing a plain act again (`SoftNorms/Soften.lean`) | the `validateOne` guard |
| `without_wording_acts` returning its input; keeping the act; for any role (`ve/profiles.py`) | `test_rust_searches_a_wording_only_acts_layer_and_refuses_any_other` |
| `rust_environment` unreduced (`ve/backends/rust_jsonl.py`) | the same test |
| `base_data` keeping `acts@0` (`ve/norms.py`) | `test_a_udhr_act_phrase_unit_is_checked_end_to_end` |
| `plain_wordings` asking the lower route of a `readings@1` environment (`ve/norms.py`; review F1) | `test_a_readings_environment_has_leans_wordings` and the two other F1 tests (section 7) |

## 4. Trust, size, evidence and tests

- **Trust** (`tools/trust_map.py --check`, final tree): K +0, S +0, untied V +31 (`Standalone.lean` +19,
  `Readings/Wire.lean` +12), one R16 allowance; new names classified in `tools/trust-classes.json`; FOLLOW-UPS
  "## ap-1bd" asks for the ties pass and for spec 6.4's `readings_lexical_only` (not proved here).
- **Trust mutants** (`mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/act-phrases/ap-1bd/trust-mutants-allow.json --json docs/act-phrases/ap-1bd/trust-mutants.json`):
  exit 0 at `501f211b`: 36 mutants in 5 definitions, 26 KILLED, 10 ALLOWED, 0 SURVIVOR, 0 UNKNOWN (rescored after the
  last Lean change, which re-ran every mutant of `Readings/Wire.lean`). The allow file names six equivalent mutants
  (`isEmpty` of a list's first or last element; a sorted profile list starts with `acts@0`) and four that do not
  elaborate (`[]` without an element type). An earlier run sent to the cloud was refused by its verifier and abandoned.
- **Size** (`git diff --numstat` against the merge base; generated files, evidence JSON, mutants JSON and the oracle
  excluded): 634 added and 40 changed hand-written lines: Lean 161 (guards 120), Python 31, tests and fixtures 107, the
  oracle tool 15, the delta script 114, side tables 40, DELTA and this report 166. That is about 35 over the ~600
  rule; deviation 5's revert (the filled environment's shape, binding and fuzz tests, about 90 lines) and the
  compacted fixtures kept it there, and the rest is named ap-1bg.
- **Evidence:** [evidence/delta.json](evidence/delta.json) (369 records, 364 identical, DELTA rows 2-3);
  [evidence/commits.txt](evidence/commits.txt) (`git log main..HEAD --no-merges`).
- **Tests:** `lake build` (1,126 jobs) and `lean/audit.py` PASS; `regen_generated.py --check`: 33 checked; selected tests
  (`mac-pytest.sh --select`, 418 units) all pass at `ae9714ae`; after the last Lean change `tests/test_acts_profile.py`
  and `tests/test_response_schemas.py` (116) and `tests/test_assurance_manifest.py` (137) pass;
  `gate_collection.py --check --prebuilt`: 20 added, 0 refused, 0 stale, 0 malformed. Pre-existing failures
  (`main-known-red.txt`): none selected or touched. The full gate is the chain's.
- **Pilot bytes expected to move** (*estimate*; nothing is claimed before a pilot audit): the UDHR's 8 act-phrase units
  (1,403 B, M7) need the pilot's environment to list `acts@0`. Those whose regulated declarations are all plain
  (entitlement units, like u076's 123 B) can move now; a unit with a permission or obligation act that needs `acts@0`
  has no Rust search yet, and one with a reading set keeps the refusal (ap-1bg).

## 5. Next items: the UDHR pilot lists `acts@0`, then ap-1bg

**ap-1bg** (what did not fit): (a) Python's superposed and enumerated readings routes read `acts@0`
(`readings_s1.soft_frame`), then lift `decodeDocument`'s refusal and type and bind the filled environment's `form` and
`acts` (the reverted shape and binding, with their fuzz tests); (b) a Lean-owned model view for Rust's search of an
`acts@0` environment with a permission or obligation act; (c) spec 6.4's `readings_lexical_only`. Then ap-4 (after
ap-2c) for u092.

## 6. Self-review against BUILDER-CHECKLIST

1. PASS: no relayed field added (the reverted filled-environment members are not relayed); D-33 is Lean's text, relayed (`test_the_readings_route_reads_single_acts_and_refuses_a_joined_act`).
2. PASS: section 1 copies each task part with its test; ap-1bg is named; no Python copy of a Lean decision (one projection replaces two), no report test, no in-flight file.
3. PASS: [mutants.json](mutants.json) (17 killed), [trust-mutants.json](trust-mutants.json); `delta.py --compare` exits 1 head against head and on empty input.
4. PASS: [evidence/delta.json](evidence/delta.json), base and head each with its own client and service (364 of 369 identical); `test_rust_refuses_an_acts_environment` unchanged.
5. PASS: no new field read from a Lean answer; the oracle's search witnesses are checked by Lean (`test_search_status_and_comparison_answer_as_the_base_did`).
6. PASS: base is `git merge-base`; evidence commits from `main..HEAD --no-merges`; the gate is the chain's, on the final HEAD.
7. PASS: DELTA rows cite R16, R1 and the DRI decision files ap-1b's row 2 cites; `review-ready.py --delta-dri-needed`: none reserved.
8. PASS: every changed record of `evidence/delta.json` is a DELTA row (rows 2, 3); the reading-set document measured identical.
9. PASS: `select_tests` picked 418 units, among them `tests/test_acts_profile.py` and `tests/test_model_environment.py`.
10. PASS: `lean/statements.txt` unchanged (section 0); no new theorem.
11. N.A.: no budget, limit or deadline changed.
12. PASS: no new Lean call per item: typing and models read the environment once (`regulatedOf`); the u076 check runs in about a second.
13. PASS: no test removed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.

## 7. Review fix (ap-1bd-review.final.md)

**F1 (B), fixed** (`875f93c60`). An `acts@0` environment that lists `readings@1` loads, but `ve.norms.plain_wordings`
asked `norms-elaborate` or `norm-defaults-elaborate` of it, and both routes refuse `readings@1`; every English entry point
builds `EnglishVocabulary`, so rendering and English parsing of any such environment with a plain act failed with
`UnsupportedProfile: Unsupported profile readings@1`. The class is every reader of `plain_wordings`, and the fix is in
that one function: a `readings@1` environment is asked of the `readings-route` mode, whose runner strips the head
profile and runs the same elaborate case on the lower route (`Readings.Run.runLower`, unchanged). Python drops no
profile, and the row is typed by `readings-route.json` (any lower route's row) and bound by the same `_bind_wordings`.
The probe printed the refusal before the fix and `{'paid': '{0} has the right to equal pay …'}` after it. Regression
tests (`tests/test_acts_profile.py`): `::test_a_readings_environment_has_leans_wordings` (the probe),
`::test_every_acts_list_the_environment_mode_accepts_has_leans_wordings` (the class: before the fix 6 of the 21 accepted
lists failed, every one listing `readings@1`; after it, none), `::test_a_udhr_act_phrase_unit_with_readings_is_checked_and_rendered`
(u076 with `readings@1` and `norm-defaults@0`, as the UDHR pilot lists them: CHECKED 123 B and rendered),
`::test_readings_wordings_not_bound_to_the_request_are_unavailable` (12 rebind mutants of the genuine readings-route
row) and `::test_a_retyped_readings_wordings_field_fails_the_schema` (14 retypes, with and without `norm-defaults@0`).
Lean mirror: `lean/VE/Readings/ActsExamples.lean` guards that `runLower`'s `wordings` equal the norms and norm-defaults
routes' on the same environment without `readings@1`. Seeded bug: `plain_wordings` asking the lower route again
(`ve/norms.py`) fails all three of the first tests ([mutants.json](mutants.json) `py-plain-wordings-lower-route`). No Rust
or trusted Lean changed (trust `--check`: still V +31; the two new example helpers are classified T). DELTA row 2 lists the tests.

Tests of the fix: the five F1 tests (43 cases) pass locally; `mac-pytest.sh --select` (417 units, among them
`tests/test_acts_profile.py` and `tests/test_trust_mutants.py`) exits 0 with 0 failed at `875f93c60`; `lake build`
(1,126 jobs), `lean/audit.py`, `regen_generated.py --check` (33) and `trust_map.py --check` (V +31) pass. **Not run:** the
trust mutants after the fix. The Mac runner dropped mid-run, the VM fallback (1 job) passed the 2-hour limit and was
stopped without an answer. The fix changes no mutated definition and no trusted Lean (only `T` guards), a guard can
only add kills, and the 10 ALLOWED mutants are equivalent or do not elaborate, so the committed verdicts at `501f211b`
stand; the reviewer's full run on the HEAD checks this. Size of the fix (`git diff --numstat 777c5fd42`, generated
`declarations.txt` excluded): Python 6 added and 4 removed, tests 92, Lean guards 16, side table 2, DELTA, report and
mutants JSON 48.

**C findings, recorded:** F2: DELTA's sentence on reading sets now says the base's refusal is the readings route
decoder's, and that a document the enumerated route answers is read with `acts@0` (no evidence probe records it;
follow-up). F3: DELTA row 4 states the fault order (R2). F4 (`typingReduced` docstring), F5 (`ve/profiles.py:50`
comment, move with ap-1bg (b)), F6 (record the `Soften.lean` hunk in the plan's AP-1 change list) and F7 (size) are
follow-ups, as the review sets them.

## FIXMAP
- `lean/VE/Service/Standalone.lean`: Lean's standalone modes. `regulatedOf` :30 (acts-aware `regulated` read),
  `checkRegulated` :38, `actsRead` :46 (base rows' gate + `actsView`), `validated` :206 (uses both), `modelCase` :549
  (profile pairs via `regulatedOf`), `folBackground` :699. `typingReduced` :149 and `modelEnvironment` :329 unchanged.
- `lean/VE/Readings/Wire.lean`: readings route decoder. `singleActsOnly` :73 (D-33 over D-4), `decodeEnvironment`'s
  `acts := true` :105, `decodeDocument`'s reading-set refusal :279.
- `lean/VE/SoftNorms/Soften.lean` :480: `checkW1` admits a plain act.
- `lean/VE/Service/ActsExamples.lean` section "ap-1bd": typing, model, Background guards; `lean/VE/Readings/ActsExamples.lean`:
  readings route guards (single acts, reading sets, D-33, constants, the text map).
- `ve/profiles.py` `without_wording_acts` :116 and `ve/backends/rust_jsonl.py` :328: Rust's search view.
- `ve/norms.py` `base_data` :488 (one base projection; `ve/norm_defaults.py` :74 calls it); `plain_wordings` :204
  (review F1: a `readings@1` environment asked of `readings-route`).
- `tests/b15b_model_cases.py` `record --profile` :184; fixtures `tests/data/acts/*.json`; oracle `tests/data/b15b-model-oracle.json.gz`.
- `tests/test_acts_profile.py` :617-715 (ap-1bd tests); `docs/act-phrases/ap-1bd/delta.py` (base/head delta).
- Side tables: `tools/trust-classes.json`, `tools/layer_policy.py` (`VE.Readings.ActsExamples` layer 4),
  `ve/assurance-manifest.json` (`Readings/Wire.lean` pin reviewed: lines, sha256, `singleActsOnly`; `other_json`).
- Regression tests: `uv run pytest -q tests/test_acts_profile.py tests/test_model_environment.py -k 'acts or reaches_every'`;
  `cd lean && PATH=~/.elan/bin:$PATH lake build VE.Service.ActsExamples VE.Readings.ActsExamples`.
- Delta: `(cd <base worktree> && uv run python <this>/docs/act-phrases/ap-1bd/delta.py --answers B.json)` (with the
  head's `tests/test_acts_profile.py` copied in), the same at the head, then `--compare B.json H.json --out evidence/delta.json`.
- Oracle: `uv run python -I tests/b15b_model_cases.py record tests/data/b15b-model-oracle.json.gz --profile acts@0`.
- Regen: `uv run python tools/regen_generated.py --write` (schemas, inventories, pins, manifest tables, ledgers).
- Trust mutants: `zsh manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/act-phrases/ap-1bd/trust-mutants-allow.json --json docs/act-phrases/ap-1bd/trust-mutants.json` (add `--rescore <that JSON>` after a later edit).
## END FIXMAP
