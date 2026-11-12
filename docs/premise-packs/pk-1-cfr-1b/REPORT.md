# pk-1-cfr-1b: a valid route-case differential for pk-1 (build report)

Evidence only. pk-1's route-case differential (`docs/premise-packs/pk-1/evidence/ab_route_cases.txt`) is INVALID
and exited 1. It is replaced here by a differential that rebuilt pk-1's base and head and ran every rebuilt
executable. No product file, generated file or pk-1 file changed. No DELTA row; trust +0. No DRI signature is
reserved.

## 1. Measure (step 1)

- **pk-1's base and head.** pk-1 merged into main as `cb033316a7` ("Merge feature/pk-1 (pk-1)", 2026-10-18 19:25Z;
  found with `git log --merges --grep pk-1`). Its parents are:
  - `3cc70f557e`: main just before pk-1, which is also the branch's merge base with main;
  - `6f6bbfc27e`: pk-1's branch head.

  The **base** is `3cc70f557e` and the **head** is `cb033316a7`, so the diff between them is exactly pk-1's merge.
  The INVALID record's baseline `22c4b9154284` (Merge tarch-manifest-ops, 10:36Z) is an ancestor of `3cc70f557e`,
  119 commits earlier, with 4,768 added lines under `lean/` from other items. A differential against it would
  mix in their changes, so it is not used as the base.
- **Why the 33-case run never invoked `ve_speech_acts_route`.** `tools/lean_output_diff.py` gives that executable
  inputs from only two places:
  - `CASE_MODES` over the case corpora (`static_invocations`: one run per `conformance/*.json` and
    `lean/VE/*/examples/*.json` list);
  - `--recorded`.

  `harness_invocations` has none for it. The INVALID record's counts line lists no `ve_conformance` and no
  `ve_speech_acts_route` at all, so its invocation list had no corpus runs. Its 48 invocations are the 33
  route-case `ve_service` sessions plus the 15 harness invocations (`ve_service` 2, `ve_english_run` 6,
  `ve_english_route` 2, `ve_response_decode` 2, and one each of `ve_english_lean_bench`, `ve_metered` and
  `ve_senses_route`): 33 + 15 = 48.

  `ve_speech_acts_route` was rebuilt, but nothing invoked it, so the coverage rule (`compare`'s `uncovered`
  check) marked the run INVALID and it exited 1.

## 2. Delivered

1. **The differential**, saved in `evidence/`:
   - `ab_route_cases_valid.txt`: the full output, with both commits, the commands and the exit status;
   - `route_cases_norm_defaults.jsonl`: the 33 cases;
   - `route_case_sessions.py` and `run_differential.zsh`: the scripts that wrote them.

   How it was run:
   - Each tree was built in its own detached worktree, one after the other. Each ran a full `lake build` and then
     a `lake build` of every `lean_exe`, through `iso.sh pk-1-cfr-1b 24G`. Base built in 16 min.
   - `--save-baseline` ran in the base worktree, on a clean `lean/` with `ve_service` pinned.
   - The comparison used head's own `tools/lean_output_diff.py`, so the lakefile, corpora and session encoder
     match the executables:
     - the static invocations (every corpus through `CASE_MODES` and the `ve_service` modes, and the harness);
     - plus `--recorded`, with the 33 `norm-defaults` cases of head's `tests/data/route-cases.jsonl`, one
       `ve_service` session each.
   - The 33 lines are byte-identical at base and head (sha256 `df47679e…`), and no two are the same.

   The same seven executables were rebuilt as in pk-1's record, `ve_speech_acts_route` included. Result: **456
   invocations, 382 run on both builds, 0 differences, 0 timed out, no INVALID line, exit 0**
   (`evidence/ab_route_cases_valid.txt`). `ve_speech_acts_route` ran 17 times, once per corpus. The record's
   invocation plan line counts the 33 recorded sessions as distinct, and `ve_service`'s 358 runs are 323
   static, 33 route-case and 2 harness.
2. **Test** `tests/test_pk1_route_case_differential.py::test_pk1_required_route_case_differential_is_valid`. It reads
   only the saved record and the saved case file, never git or a build. It requires:
   - the pinned base, head and baseline-manifest commits;
   - the case file's pinned sha256, with 33 rows;
   - one `route-case nd-NN id=… kind=… sha256=…` line per case;
   - `ve_service` among the rebuilt executables, and every rebuilt executable with at least one invocation;
   - a summary with no difference and no timeout;
   - no INVALID line, and a last line of `exit 0`.

   `test_differential_check_refuses_invalid_records` keeps the seeded records below as permanent fixtures,
   together with `exit 1` and a rebuilt executable with 0 invocations.

**The pk-1 claims the valid record supports** (for norm-defaults-text-1 to cite; pk-1's files are not edited here):

- the spec's fixtures L1/L2 for the route cases (`docs/spec/premise-packs.md:260-261`: every `norm-defaults-*`
  case in `tests/data/route-cases.jsonl`, byte-identical base vs head, with saved A/B evidence);
- `docs/premise-packs/pk-1/REPORT.md:62-65`: the sentence "these cases have no valid differential" can now say
  the 33 cases are byte-identical, citing `docs/premise-packs/pk-1-cfr-1b/evidence/ab_route_cases_valid.txt`;
- `docs/premise-packs/pk-1/DELTA.md:17-19` (the same bullet);
- `REPORT.md:161`, "every output on today's routes is byte-identical (section 2)", as far as the route cases go.
  Together with `ab_full.txt`, it now covers the corpora, the 17 recorded test files and the 33 route cases.

## 3. Seeded bugs

Each was run against the condition test and then restored (`cmp` against the saved copy). They are also the
permanent fixtures of `test_differential_check_refuses_invalid_records`.

| # | File | Seeded bug | Failing test, fault |
|---|---|---|---|
| S1 | `tests/test_pk1_route_case_differential.py` | `RECORD` points at pk-1's INVALID record | `test_pk1_required_route_case_differential_is_valid`: "INVALID line: …", "ends 'exit 1'", no base commit, 33 "case not run" (41 faults) |
| S2 | `docs/premise-packs/pk-1-cfr-1b/evidence/ab_route_cases_valid.txt` | the line of case `nd-05` (`id=x`) dropped | same test: "case not run: route-case nd-05 id=x kind=no-such-kind sha256=452aa1dd375c" |
| S3 | same record | the summary's difference count changed from 0 to 1 | same test: "summary: 456 invocations, … 1 differences, 0 timed out" |

No product code changed in any language, so no product-language seeded bug applies.

## 4. Size, trust, delta

- SIZE: 0 product, 73 tests, 72 other hand-written lines: the two evidence scripts, 39 + 33. This REPORT and the
  saved outputs are not counted.
- Trust: +0. `tools/trust_map.py --check` reports K +0, S +0, trusted +0 and PASS. No `lean/`, `ve/` or `rust/`
  file changed.
- No trust_mutants sweep, because nothing here could be mutated. `light-lane.py check` prints NOT, but only
  because it counts the saved evidence and this REPORT (344 lines, no trusted-core file). The build checklist's
  sweep (13a) applies only to trusted Lean growth, and this item has none.
- DELTA: none (evidence only, no user-visible change).
- Pilot bytes expected to move: none.

## 5. Tests run

- `uv run pytest -q tests/test_pk1_route_case_differential.py tests/test_pk1_route_case_evidence_validity.py`: 5
  passed. The pk-1-cfr-1 scan accepts this REPORT: its one byte-identity claim cites only the valid record.
- `select_tests --paths` selects the new test for the new test file, the record and this REPORT.
- Generators fed by tests: `code_map --check` was already stale on main, for other items' files. That check is
  advisory on branches, and main regenerates the codemap on every merge, so it is not regenerated here.
  `heavy_tests`, `history_tests`, `platform_contract` and `binding_census` checks pass.
- The final selected run is recorded in the build reply. Pre-existing reds (`main-known-red.txt`) are not touched.

## Notes for the DRI

- The base is pk-1's merge parent `3cc70f557e`, not the INVALID record's `22c4b9154284`. The task named both as
  hints. Using the merge's own first parent is the narrower reading: it isolates pk-1's change from 119 other
  main commits.
- pk-1's full differential (`ab_full.txt`, base `93131f967`, head pk-1's branch before main merges) and this one
  (base `3cc70f557e`, head the merge) use different commit pairs. Both exited 0 and found no difference.

- Spec re-read: L1/L2 against `docs/spec/premise-packs.md:260-261`. L1 names two sources:
  - every `norm-defaults-*` case of `tests/data/route-cases.jsonl`. This record covers all 33 lines that the
    `norm-defaults` mode sends, a superset that also includes the `admission` cases and the `no-such-kind`
    refusal;
  - the layered tests (`test_norm_defaults_layered.py`, `test_route_transport.py`). pk-1's `ab_full.txt`
    recorded those, and they are not re-run here.

Next item: none in this stream.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A., no relayed answer or Lean code changed.
2. Every deliverable built: PASS. The differential is `evidence/ab_route_cases_valid.txt`, and the test is
   `test_pk1_required_route_case_differential_is_valid`.
3. Tests can fail: PASS. S1-S3 above, and `test_differential_check_refuses_invalid_records`.
4. Python, Lean and Rust agree: PASS for the claim made here. Base and head Lean outputs agree on 382
   invocations (`evidence/ab_route_cases_valid.txt`). No Python or Rust code changed.
5. R8 binding: N.A., no relay changed.
6. Gate evidence matches HEAD: PASS. The record names its commits, and the test reads only the saved record
   (D4).
7. No unsigned item: PASS. No DELTA and no reserved signature.
8. DELTA: N.A., no user-visible change. `git diff --stat main...HEAD` shows only `tests/` and
   `docs/premise-packs/pk-1-cfr-1b/`.
9. Selection: PASS. `select_tests --paths` selects `tests/test_pk1_route_case_differential.py` for the record and
   this REPORT.
10. Lean statements: N.A., none changed.
11. Budgets fail closed: N.A., no evaluator. The record's `0 timed out` is checked by the summary rule in
    `differential_faults`.
12. CPU and memory: N.A., no product code.
13. Test-removed trailer: N.A., no test removed.
14. Both directions, cited evidence, spec: PASS. The test accepts the valid record and refuses S1-S3, `exit 1`
    and a rebuilt executable with no invocation. Each count in this REPORT cites its record line. The spec
    re-read is above.
15. Overclaim, silent cut, new check can fail, limits:
    - Overclaim: PASS. This REPORT claims identity only for the 33 cases and the corpora this run covers.
    - Silent cut: PASS, nothing was cut.
    - New check can fail: PASS, S1-S3.
    - Limits: N.A., no evaluator.
