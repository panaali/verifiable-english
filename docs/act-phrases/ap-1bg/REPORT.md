# ap-1bg build report: reading sets over `acts@0`, Lean's model view for Rust

**No DRI signature is reserved; nothing stops the item.** (c) `readings_lexical_only` did not fit the size line and
is ap-1bh (section 1). DELTA: [DELTA.md](DELTA.md) (R16; ap-1bd's row 2 decision files, continued). Row 2 (ii), Rust's
search, is confirmed by the DRI (reviews/dri-decisions-20261102-ap-1bg.md item 1).

Plan and spec on `main`: [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) 2.8, 2.9, AP-1 (lines 860-888);
[act-phrases.md](../../spec/act-phrases.md) 6.4. Synthesis round 2 edits (edits-act-phrases.md): none implemented;
edit 2 (the wire contract as a shadow step) is untouched, as no combination is added to `ve/wire_contract/acts@0.json`.

## 0. Statement gate and overlap

The statement review accepted AP-1 and 6.4 (ap-1bd built on them). `readings_lexical_only` is not on `main` yet, so
it is not false as written; it is not built here (ap-1bh). Overlap: of the in-flight branches, `feature/ap-3r` edits
`lean/VE/Acts/{Table,TableExamples,ElaborateExamples,ReadingsExamples}.lean` and `feature/pc-1`
`Service/Document.lean` and `Compose/Dispatch.lean`; this item touches none of them (nor `lean/VE/Compose/`).

## 1. Task rows

| Task part | Status | Where |
|---|---|---|
| (a) the superposed and enumerated readings routes read `acts@0` by relaying Lean's decoder | **done**. Python's soft frame (`readings_s1.soft_frame`) is asked of Lean's `soft-elaborate`, whose decoder now reads the soft view of an `acts@0` norms frame (`SoftNorms.Phases.actsFrame`: `acts@0` listed and exactly the empty strict block; any other block as before). Lean's model mode checks a witness over that view as its frame (`Phases.frameView` in `Standalone.actsRead`, `modelCase`, `reportedModel`). The view's plain acts are worded by the norms route on the frame (`wording_frame`, `norms.plain_wordings`). Two Python base projections that kept `acts@0` call `norms.base_data` (one owner) | `Phases.lean`, `Standalone.lean`, `readings_s1.py`, `softnorms.py`, `norms.py`; deviation 1 |
| (a) lift `decodeDocument`'s refusal; type and bind the filled `form` and `acts`, fuzz one and two faults | **done**: the refusal is gone; `filledPredicate.form` is one of Lean's two forms, `filledEnvironment.acts` closed with `fixed`; the common prime environment's `acts` equals the request's; `_bind_completion` binds the block, acts and forms | `ReadingsRoute.lean`, `Common.lean`, `readings_route.py`; `test_a_retyped_filled_act_field_fails_the_schema` (29 cases), `test_a_filled_act_not_bound_to_the_request_is_unavailable` (14), `test_a_soft_views_prime_acts_block_not_bound_to_the_request_is_unavailable` |
| (b) a Lean-owned model view for Rust's search of an `acts@0` environment with a permission or obligation act | **done**. The environment row's `model_acts` (`Standalone.modelActs`): one placeholder `{0} act<letters> {1} …` per distinct act, which `canonicalAct` accepts. `profiles.model_view` (replacing ap-1bd's `without_wording_acts`) drops the profile, the block and the plain wording and takes Lean's acts; `bound_model_acts` binds names and equal acts on every environment row. Rust is unchanged | `Standalone.lean`, `Environment.lean`, `validation.py`, `profiles.py`; `test_rust_searches_leans_model_view_of_an_acts_environment`, `test_model_acts_not_bound_to_the_request_are_unavailable` (21), `test_a_retyped_model_acts_field_fails_the_schema` |
| (c) spec 6.4's `readings_lexical_only` | **not done: ap-1bh** (size line, section 4). Measured plan: define `VE.Acts.Wire.fixedOf`, gate `decodeEnvironment`'s result on `Lexical.check (fixedOf environment)` of every act under `acts@0` (D-33), and prove the theorem from the gate | — |
| Evaluators and runners | N.A.: no evaluator or runner added; `modelActs` reads at most 64 regulated declarations once | — |

## 2. Deviations

1. **Lean's soft decoder, not a Python projection.** The soft frame is Python's container over a Lean answer; making
   it read `acts@0` needed Lean's soft decoder (and model mode) to accept the frame's soft view, restricted to the
   empty strict block so a soft document with `acts@0` stays refused. Wording through the readings route's
   `runLower` was tried and reverted: `runLower_fits` (encoder theorem) breaks on it.
2. **Guards beside the trusted modules.** The trust mutants build only the checks of the mutated module's directory, so
   the soft view's guards are also in `lean/VE/SoftNorms/ActsFrameExamples.lean` (new, imported by `VE.lean`).
3. **Field tables.** `tests/test_difffuzz.py` and `tests/test_relay_binding_inventory.py` list `model_acts` and the
   prime's `acts`; `tests/data/binding-answers.jsonl.gz` re-asked (`tools/binding_census.py --answers`).

## 3. Evidence

- Seeded bugs: [mutants.json](mutants.json), 11 killed (Lean 6, Python 5), each with its one check; `emptyBlock`'s
  11 trust mutants are all killed.
- Trust: `trust_map.py --check` K +0, S +2, V +63 (R16 allowance). Trust mutants (`mac-pytest.sh --trustmut`, final
  run at `747ab468`, exit 0): 350 killed, 0 survivors, 0 unknown, 20 invalid, 62 allowed
  ([trust-mutants.json](trust-mutants.json), [trust-mutants-allow.json](trust-mutants-allow.json): each allowed
  mutant is equivalent, does not elaborate, or is UNKNOWN only because `VE/Defaults/Examples.lean:175` cannot be
  re-elaborated by the probe while `VE.SoftNorms.ActsFrameExamples` refutes it, three of them re-planted by hand).
  The first run's 38 survivors were killed by checks beside the mutated modules: the schema shapes pinned by their
  rendered digests, `VE.SoftNorms.ActsFrameExamples` (new) and a third distinct model act.
- Oracle: `uv run python -I tests/b15b_model_cases.py record tests/data/b15b-model-oracle.json.gz --profile acts@0`;
  48 answers changed, every one on a `ve.core@0.2:acts@0,…` environment (a comparison of the old and new archives).
- `lake build` (1,228 jobs) and `python3 lean/audit.py` (PASS, 721 files) after the last Lean change;
  `regen_generated.py --check`: 35 entries.
- Selected tests (`mac-pytest.sh --select`, 433 units at `40cbf7b3`): 4 failed, all field tables of the new members;
  fixed in `3d892ae73` and rerun by id (section 6).

## 4. Size and bytes

`git diff --numstat $(git merge-base HEAD main)`, generated files excluded: about 520 lines of code, tests and side
tables before these docs. Bytes: the UDHR's act-phrase units with reading sets (M7) can now be checked; no pilot byte
is claimed (estimate only, not measured).

## 5. Next items

- ap-1bh: spec 6.4's `readings_lexical_only` (section 1 row (c)).
- ap-4 (readings from derivations; after SC-1c in the protocol queue), for u092.

## 6. Self-review against BUILDER-CHECKLIST

1. PASS: `test_a_retyped_filled_act_field_fails_the_schema`, `test_a_retyped_model_acts_field_fails_the_schema`.
2. PASS: section 1 (each row with its tests); (c) named ap-1bh; no Python copy of a Lean decision (two projections now call `base_data`).
3. PASS: [mutants.json](mutants.json); [trust-mutants.json](trust-mutants.json).
4. PASS: `test_a_reading_set_over_acts_takes_the_superposed_and_enumerated_routes` (with and without `acts@0`).
5. PASS: `test_a_filled_act_not_bound_to_the_request_is_unavailable`, `test_model_acts_not_bound_to_the_request_are_unavailable` (undeclared, dropped, emptied).
6. PASS: base is `git merge-base`; the gate is the chain's, on the final HEAD.
7. PASS: DELTA rows cite R16 and ap-1bd row 2's decision files; none reserved.
8. PASS: DELTA's "everything else" paragraph; the oracle diff (48 `acts@0` answers only).
9. PASS: `mac-pytest.sh --select` picked `tests/test_acts_profile.py` and the field-table tests that failed.
10. PASS: `lean/statements.txt` unchanged; `environment_fits` rebuilt over the new member.
11. N.A.: no budget, limit or deadline changed.
12. PASS: `model_acts` costs nothing without `acts@0`; the view relays once per environment (`cached_rust_environment`).
13. PASS: `Test-removed:` trailer in `ca4316cab`; `gate_collection.py --check --prebuilt`: 1 removed by a trailer, 0 refused, 0 stale, 0 malformed.
14. PASS: both sides: `test_the_readings_route_reads_single_acts_and_refuses_a_joined_act`, the "another soft block" guards.
