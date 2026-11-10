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
--test lean/VE/Acts/DecodeExamples.lean --allow trust-mutants-allow.json --rescore ...`): SWEEP_RESULT.

## Tests

- `uv run pytest -q tests/test_norm_defaults_response_binding.py`: 62 passed.
- Final selected run (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select`, committed tree): SELECTED_RESULT.
- `python3 lean/audit.py`: PASS (824 files, 9300 theorems). `tools/check_rd9_sc1_statements.py`: PASS.

## Size, pilot bytes, self-review

Hand-written lines: SIZE_LINE. Pilot bytes: none expected to move. The binding refuses forged rows only, and
Lean's answers on the pilots are unchanged apart from the added `sources` field (an estimate; no pilot audit was run).
SELF-REVIEW: 0 A, 9 B, 6 C; fixed 13 (all 9 B; C10, C12, C13, C14 fixed, C11 noted above, C15 measured).
