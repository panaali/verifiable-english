# norm-defaults-cfr-1b: status rules bound under acts@0 and rights@0

Status: built. The gate is the chain's, run on the final HEAD. No DRI signature is reserved: DELTA rows 1 and 2 are R16.
Change: Lean echoes the request rule each `norm-defaults-status` rule comes from (`sources`, one `{rule, source}` per
rule), and the client binds each echo to the request under every profile, `acts@0` and `rights@0` included (ND-FC2
closes). Trust: V +31, K +0. Not bound: a generated name forged together with its echo (see "Not bound").
Next item: none (acts@0 was not cut).

## Deliverables (task file prompts/task-norm-defaults-cfr-1b.txt)

| # | Task line | Delivered by |
|---|---|---|
| 1 | Lean echoes each status rule's source under rights@0 and acts@0, through the schema and the encoder, with theorems tying the echo to what the part or fan/bar line was built from | `Wire.ruleSources`/`sourcesJson` and `statusFields` (lean/VE/NormDefaults/Explain.lean). The table each route generates: `SourceU.sources` (lean/VE/NormDefaults/Wire.lean; set by `Acts.Decode.sourceOf` from the `SplitMap`) and `LayeredU.sources` = `rightsSources` (lean/VE/NormDefaults/Layered.lean). Schema: `sources` and `.sameLength ["rules", "sources"]` (lean/ResponseShape/Schemas/NormDefaults.lean, regenerated `norm-defaults.json`). Theorems: `ruleSources_spec`; `Acts.splitMap_rules_built`, `elaborateMap_sources`, `Acts.Decode.sourceOf_sources`, `elaboratedU_sources`, `Wire.decodeSourceUWith_sources`; `instancesOf_fan`, `linesAux_mem`, `rightsSources_built`, `decodeRightsU_sources`, `decodeRightsU_echo`, `decodeSoftU_sources` |
| 2 | `_bind_norm_defaults` binds `rules` on both profiles: every echoed source is a request rule, the pair checked against Lean's echo only, a forged generated name refused | `_bind_status_rules` and `_rule_names` (ve/backends/lean_service.py). Under `rights@0` the request rules are read from the `document` (`RULE_FIELDS`, now in `ve/profiles.py`, the one table `ve/rights.py` also reads). Python keeps no copy of Lean's naming |
| 3 | Extend tests/test_norm_defaults_response_binding.py: a forged generated name refused under acts@0 and rights@0; genuine acts@0 and rights@0 rows pass; the new cases shown failing on main | `[acts-status-rules-forged_generated]`, `[rights-fan-status-rules-forged_generated]`, `[rights-bar-status-rules-forged_generated]`, the `*-sources-*` forgeries, `test_each_echo_field_deleted_retyped_or_extended_is_no_answer`, `test_a_generated_rule_needs_its_echo`; genuine rows: `test_genuine_answers_pass` (split act, rights line, fan-out, bar rule, two UNKNOWN points). On main: `evidence/new-tests-on-main.txt` |
| - | Remove the statements of the gap | `_bind_norm_defaults` docstring; docs/premise-packs/norm-defaults-cfr-1/REPORT.md (summary, row 2, "Rules" and the follow-up line); `uncounted.rules` in ve/assurance-manifest.json. The schema description had no such statement on main (`grep -n cfr-1b lean/ResponseShape` found none); the new description states the echo. cfr-1's DELTA row 1 records what that item shipped and is left as it is |

Files beyond the task's list, each needed for the echo: `lean/VE/NormDefaults/{Wire,Explain,Layered,Run}.lean`,
`lean/VE/Acts/Decode.lean`, `lean/VE/Readings/UnspecifiedWire.lean` (two `LayeredU` constructions gain `[]`),
`lean/ResponseShape/Encoders/NormDefaults.lean` (the fits proofs unfold `sourcesJson`), the guards in
`lean/VE/NormDefaults/PacksLegacyExamples.lean` and `lean/VE/Acts/DecodeExamples.lean`, `tests/test_enum_domains.py`
(the status probe row carries `sources`), `tools/trust-classes.json`, `ve/profiles.py` and `ve/rights.py` (the table
moves down a layer; self-review B3). **Tree.lean is not edited.** A fan-out `Line` already carries its `SourceLine`
(`source`), and `instancesOf` keeps it. Its `norm` is the request rule the instance was renamed from
(`instancesOf_fan`). `RightsDoc` is untouched. `lean/VE/Rights/Correlate.lean` is not edited either: `rightsSources`
reads `barNodes`.

## What is bound

For each status row (`_bind_status_rules`, with schema `x-same-length` and the typed `{rule, source}` items):
- `sources[i].rule` is `rules[i]`.
- `sources[i].source` is a rule of the request: the `name` of a `{"norm": ...}` unit of its `norms`; under `rights@0`,
  whose route reads the `document` (`Wire.decodeLayered`), instead every rule the document holds (a line's `norm`,
  `liberty`, `recognition`; a `norm` unit; a `bar`).
- A rule may differ from its source only when the profiles list contains `acts@0` or `rights@0`, and only if no request
  rule has its name.

**Not bound** (Lean's to choose, or past binding):
- Which generated name a request rule gives: a row that forges a generated name together with its echo, naming a real
  source (e.g. `rules ["r027-a7"]`, `sources [{"rule": "r027-a7", "source": "r027"}]`), passes. Only Lean's naming tells
  that one, and copying it into Python is forbidden (R8). Probe: `test_a_generated_rule_needs_its_echo` accepts
  `g1 <- r1`.
- A `bar` name is accepted as a source whatever its `reading` (only a rule reading generates a rule). This is lenient,
  and copying that rule would put a Lean decision in Python.

## Fails on main

The new test file was run against main's client, schema and `ve_service` (c94ad399b7, a detached worktree; command and
provenance in `evidence/new-tests-on-main.txt`): 24 failed, 28 passed. Six forged rows that main accepted (DID NOT
RAISE) are `[acts-status-rules-forged_generated]`, `[rights-fan-status-rules-forged_generated]`, `[*-rules-ghost]` and
`[*-rules-appended]` under each profile. The other failures are the `sources` field main does not send.

## Seeded bugs (mutants.json)

Python (ve/backends/lean_service.py), each restored after:
- S1, echo binding skipped under acts@0: `[acts-status-rules-forged_generated]` fails.
- S2, the same under rights@0: `[rights-fan-status-rules-forged_generated]` fails.
- S3, a source outside the request accepted: `[acts-status-sources-echo_own_rule_no_such_rule]` fails.
- S4, no document rules read under rights@0: `test_genuine_answers_pass` errors, refusing Lean's own rights rows.
- S5, a request rule echoed from another request rule accepted:
  `[rights-bar-status-rules-and-sources-request_rule_from_another]` fails.

Lean, each with `lake build` of the named module (command: `/tmp` script, output quoted in mutants.json):
- L1, `sourcesJson` keeps one echo: the `sourcesJson` `#guard` fails.
- L2, `ruleSources` echoes each rule as its own source: `ruleSources_spec` breaks.
- L3, `statusFields` drops the echo: the `statusFields` `#guard` fails.
- L4, `rightsSources` names a fan-out as its own source: `rightsSources_built` breaks.
- L5, `rightsSources` drops the bar rules: `rightsSources_built` breaks.
- L6, `sourceOf` echoes no part: `elaboratedU_sources` breaks.
- L7, the status shape loses `.sameLength`: the rendered-shape `#guard` fails.

The settled flag in `runOtherCaseIn` and `layeredCase`, survivors of the first sweep, were checked with `ve_service`
rebuilt. M1/M2 (`!= -> ==`) and M3/M4 (`&& -> ||`) each make `test_genuine_answers_pass` fail; M3/M4 needed the new
UNKNOWN fixtures (u12, and the rights `tried ∨ ¬tried` case).

## Trust

`uv run python tools/trust_map.py --check` on the final Lean: PASS. The new allowance is V +31, K +0, S +0
(Layered +12, Explain +11, Wire +3, Schemas/NormDefaults +3, Decode +1, Run +1), recorded in `docs/trust-baseline.json`
and signed by standing ruling R16. FOLLOW-UPS.md has `## norm-defaults-cfr-1b` (the ties pass). The new trusted
definitions `ruleSources`, `sourcesJson` and `rightsSources` are classified in `tools/trust-classes.json`.

trust_mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/NormDefaults/PacksLegacyExamples.lean
--test lean/VE/Acts/DecodeExamples.lean --allow trust-mutants-allow.json --rescore ... --json trust-mutants.json`), last on a46ac9160f (after the merge of main and the guard move below): "112 KILLED, 0 SURVIVOR, 0
UNKNOWN, 19 INVALID, 28 ALLOWED, 0 NOT RUN" (`trust-mutants.json`, head a46ac9160f, base 97b3c799).

## Tests

- `uv run pytest -q tests/test_norm_defaults_response_binding.py`: 62 passed.
- Selected run (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select`, committed tree a3c9499000): 477 files ran, 4 failed
  (/tmp log; the failures were this item's, none in main-known-red.txt):
  - `test_pk1c_fixture_assurance_claim` (2 tests): pk-1c's REPORT cites `PacksLegacyExamples.lean:131–141`, and the
    new guards had shifted those lines. Fix (a46ac9160f): the guards move to the end of the file, and
    `import VE.NormDefaults.Examples` replaces the redundant `import VE.Defaults.Examples` (PacksExamples imports it).
    Lines 1–162 are main's again; every citation of this file in docs/ and tests/ lies there.
  - `test_sc9_migrate.py::test_c9_point_status_is_measured_on_every_choice_and_condition`: the sc-9 pilot's saved C9
    answers predate `sources`. All 160 were re-asked of the current build (`evidence/resave_c9_sources.py`), which
    asserts that each live answer equals the saved one apart from the added `sources`, and that the echo names `rules`
    in order.
  - `test_shape_binding_mutants.py[norm-defaults]`: the recorded answers (`tests/data/binding-answers.jsonl.gz`)
    lacked `sources`. They were re-asked (`binding_census.py --answers`), and only the three norm-defaults rows were
    kept. The other six modes' rows differ only by `actions_version` 46 -> 47, which is already stale on main, and were
    left as they are.
  - `test_trust_mutants_probe_scope.py`: exit 143, killed when the run stopped at `--maxfail 5`.
- Reruns on f14e263fbe (`mac-pytest.sh -- <files>`, ve-mac-1): the four files, 148 passed. The other tests that read
  the changed files (`test_b16f_senses_document`, `test_binding_census`, `test_decoded_rights_labels_proof_claim`,
  `test_packs_guard_mutants`, `test_defeasible_baseline_evidence`, `test_rd9_gap_relay`, `test_readings_sd_ce4`):
  162 passed.
- `python3 lean/audit.py` on c5251726: PASS (843 source files, 9487 theorems). `tools/check_rd9_sc1_statements.py`: PASS.

## Size, pilot bytes, self-review

SIZE: 383 product (Lean 297, Python 86), 207 tests, 371 other hand-written lines (docs and evidence; the
tool-written `tools/trust-classes.json`, `docs/trust-baseline.json` and the re-asked saved answers are not counted). Command: `git diff --numstat
$(git merge-base HEAD main)` less the generated files (`regen_generated.py --list`). Pilot bytes: none expected to move. The binding refuses forged rows only, and
Lean's answers on the pilots are unchanged apart from the added `sources` field (an estimate; no pilot audit was run).
SELF-REVIEW: 0 A, 9 B, 6 C; fixed 13 (all 9 B; C10, C12, C13, C14 fixed, C11 noted above, C15 measured).

## Notes for the DRI

- The sibling review's F1 (rule names unchecked when `environment.profiles` is missing or not a list) does not apply:
  `_profiles` reads such a case as no profiles, so `_rule_names` reads its `norms` and a rule that is not its own
  source is refused. Fixture: `tests/test_norm_defaults_response_binding.py` (the `environment` parametrization at
  line 367: `None`, `{}`, `{"profiles": None}`, `{"profiles": {}}`, `[]`, `["norms@0"]`).
- main moved 59 commits after the merge in 3ce045dfa8; none of them touches this item's Lean or relay definitions
  (`git diff --name-only HEAD...main`). The shared files it does touch (`docs/trust-baseline.json`,
  `tools/trust-classes.json`, `ve/assurance-manifest.json`, `ve/profiles.py`, `lean/checkers.lock`) are left to the
  merge train's rebase-second step.
- `docs/test-architecture/binding-census.md` lists `/sources/*/rule` and `/sources/*/source` as "not probed": their
  binding is `_bind_status_rules`, a hand binder the census sees only after a live `binding_census.py --record` probe.
  That probe was not run here; the binding's own tests are listed under "What is bound".

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. `test_each_echo_field_deleted_retyped_or_extended_is_no_answer` (each `sources` field
   deleted, retyped, extended) and the schema's typed `{rule, source}` items with `x-same-length`.
2. Deliverables built, no rule broken: PASS. The deliverables table above; no Python copy of Lean's naming
   (`_bind_status_rules` compares names with the request only); no report test added (D4).
3. Tests can fail: PASS. Seeded bugs S1-S5 (Python), L1-L7 (Lean), `mutants.json`; trust_mutants 0 survivors
   (`trust-mutants.json`).
4. Lean and Python agree, valid inputs pass: PASS. `test_genuine_answers_pass` (Lean's own rows from `ve_service`:
   author norms, split act, rights line, fan-out, bar rule, UNKNOWN points).
5. R8 binding: PASS. `[*-rules-ghost]`, `[*-rules-appended]`, `[*-rules-forged_generated]`, the `*-sources-*`
   forgeries, `test_request_rules_on_each_source_shape`.
6. Gate evidence matches HEAD: PASS. Evidence is saved (`evidence/new-tests-on-main.txt`, `trust-mutants.json` on
   a46ac9160f); the gate is the chain's, on the final HEAD.
7. No unsigned item: PASS. DELTA rows 1 and 2 cite R16; no signature reserved.
8. Every user-visible change in DELTA: PASS. DELTA row 1 (refuses more, the `sources` field); `evidence/new-tests-on-main.txt`.
9. Test selection: PASS. `tools/select_tests.py --base 97b3c799` selects `tests/test_norm_defaults_response_binding.py`
   and the other norm-defaults suites, not every unit.
10. Lean statements: PASS. L2, L4, L5, L6 break `ruleSources_spec`, `rightsSources_built`, `elaboratedU_sources`;
    `tools/check_rd9_sc1_statements.py` PASS; no hypothesis added to an approved statement.
11. Budgets fail closed: N.A. no budget, limit or deadline is added; the binding walks the request already decoded.
12. CPU and memory: N.A. one linear pass over the request and the row; no Lean enumeration added (the echo is built
    with the rules it describes).
13. Test-removed trailer: PASS. 2b8b0d01e2 carries `Test-removed: ...test_rules_named_by_lean_under_acts_or_rights_are_not_yet_bound — ...`.
14. Both directions, cited evidence, spec re-read: PASS. Each forgery has a genuine row that passes
    (`test_genuine_answers_pass`, `test_a_generated_rule_needs_its_echo`). Spec re-read: "a forged generated rule name
    is refused" against prompts/task-norm-defaults-cfr-1b.txt deliverable (2): refused unless forged together with its
    echo, which only Lean's naming tells (section "Not bound", R8).
15. Overclaim, silent cut, checks can fail, limits: PASS. "Not bound" states what passes; no deliverable cut (acts@0
    kept); each new check has a seeded bug (S1-S5, L1-L7); no new limit (item 11).
