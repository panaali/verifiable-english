# sc-1bb report: B1, the layout and `governFast` on the full pinned constitution

No DRI signature is needed and nothing stops the item: there is no user-visible delta ([DELTA.md](DELTA.md)) and
trusted Lean lines grow by 0.

Base `ab010c3f0` (`git merge-base HEAD main`). Plan and spec: [scope-PLAN.md](../../spec/scope-PLAN.md) and
[scope.md](../../spec/scope.md) on main (the same text as at `0e7a813e8`).

**Statement gate.** The scope statement review closed with PASS (`manage-agents/scope-p3ver1.final.md`, then
`scope-p3ver2.final.md`). This item proves no statement and changes no definition: `lean/VE/` is untouched (and so
are `lean/VE/Scope/`, `lean/VE/Service/Document.lean` and `ve/document/`, which df-1b is editing).

## Plan rows

| Plan line | Delivered | Commit, test |
|---|---|---|
| B1: "a `tools/bench` row: F1-doc's document, the full pinned constitution pilot (184,893 B, 1,132 units), through the layout and the run path `governFast`", "a benchmark row with its baseline; never a timing assertion in the suite" | `tools/bench/test_perf.py::test_scope_b1`, two measures, `layout` and `layout and governFast`, each the CPU of one `ve_scope_bench` process, with baselines in `tools/bench/baselines.json`. The suite has no timing assertion (`tests/test_scope_b1_input.py` checks the input and the check only) | `0d08f429d`, `19d7a62dc` |
| B1 / C11: "The input's layout is the one SC-M0 regenerated (C11)" | before it records anything, the row checks that Lean's layout of B1's input has C11's hash (`scope_b1.LAYOUT_SHA256`, the hash of SC-M0's own transcription of `ofSource` on the same text and spans), that the list run of u0164.s02 is C11's F1 run, and that `governFast` answers `ok` with F1's six item parts composed. Anything else fails with "B1 is not timed: …" and records nothing | `scope_b1.problems`; `tests/test_scope_b1_input.py::test_a_run_that_is_not_b1_is_reported`, `test_every_layout_field_is_in_the_hash`; [layout-evidence.json](layout-evidence.json) |
| "`tools/bench/test_perf.py` and its baselines: the B1 row" | as above | `0d08f429d` |
| the command that refreshes the baseline | `PATH="$HOME/.elan/bin:$PATH" uv run --frozen python -m pytest tools/bench/test_perf.py -k scope_b1 --update-baselines` (in the row's docstring) | `0d08f429d` |
| the row runs the layout and `governFast` only (L70) | `ve_scope_bench` calls `VE.Scope.decodeScope` and `VE.Scope.governFast` and nothing else; it never runs `ve document check`, `ve jsonl` or any chain | `lean/ScopeBenchMain.lean` |

**The full layout fits.** On the VM (x86_64, load about 16 to 18): `layout` 0.151 CPU s, `layout and governFast`
0.539 CPU s, at most 112 MB resident. That is far below 4 GB and 10 minutes, so no part document is needed.

## How B1 is built (`tools/bench/scope_b1.py`)

- **The pilot.** Run 20261012T1800Z's `translation.ve.md` at pilot commit `ecfd1ace7` is kept byte for byte as
  `tools/bench/data/translation-ecfd1ace.ve.md.gz` (82 KB). It is checked against its git blob id and SHA-256, as
  `tests/ce4.py` does for run 20261010T1800Z. B1's text is the translation's first 184,893 body bytes: the pinned
  constitution, with SHA-256 `fa10ed48…d50dd`, SC-M0's recorded input. The 37-byte English fence after it is left
  out, because the plan's row counts 184,893 B.
- **F1-doc.** The pilot's 1,132 units are kept in order. The ten units of F1's block (u0164.s01 to u0166.s01, from
  `tests/data/scope/hard-constraints.scope.md`) replace the pilot's at the same spans (offset 101,233; checked).
  F1's `scope` block, `scope@0`, and F1's vocabulary and open terms are added to the pilot's front matter. Where F1
  and the pilot share a name, F1's entry wins, because the fixture's guards are AT-0p's. The other front matter
  members (reading sets, graph) are the pilot's.
- **Deviation, for the reviewer to judge.** The plan's F1-doc is "the pilot's hard-constraint block rewritten".
  sc-1b's fixture holds that block with an environment that differs from the pilot's in 19 predicates, so B1
  merges the two environments as described above. `decodeScope` checks the environment (`environmentOf`), and the
  merged one passes.
- **What `layout` measures.** It is the whole `ve_scope_bench` process with stage `layout`: start-up, reading the
  430 KB case, then `decodeScope` (split, environment check, block decode and `layoutOf`, i.e. `ofSource`). The
  `layout and governFast` measure adds `governFast` and the output.

## C11 (input check, `layout-evidence.json`)

SC-M0's transcription (`research/scope/sc_m0_tally.py` at `9a98c33f1`, read only from its research branch) and
Lean's layout give the same hash on B1's input: `a6519806…eb60a`. That hash covers every field of every unit
(id, span, item, midLine, lead, label, para). The input has 182 items, the spec's count (1.2), and the F1 run of
u0164.s02 is the seven u0165 items. The bench compares Lean's hash with this pinned value on every run. A changed
pilot copy, F1 fixture or layout function is therefore reported as "the layout is not C11's", with both hashes.
Such a change needs C11 rerun on the new layout before a new baseline.

## Limits found (not fixed here)

- **Sensitivity.** `baselines.json` has one tolerance for every row (100% + 0.5 s). B1 therefore flags a slowdown of
  the whole row beyond about 2.9 times. Swapping in `govern` for `governFast` (a temporary, uncommitted swap) cost
  0.721 s against 0.539 s. That is inside the tolerance on this document, which has a single frame governor. A
  per-row tolerance, or a B1 variant with several graph governors, would make B1 catch that swap. Either is a
  possible follow-up and is not in this item's plan row.
- **Where the bench runs.** The row builds `ve_scope_bench` itself (`lake build ve_scope_bench`, a non-default
  target, as `ve_english_lean_bench` is). Its baseline was recorded on the VM, and the Mac's numbers differ.

## Trust, DELTA, size

- **Trust.** `tools/trust_map.py --check` on the final tree reports PASS. Against the base, this item adds +0
  trusted lines (K +0, S +0, untied V +0). The only growth it lists, `VE/Calc/Run.lean` +50, is main's me-2c, which
  has its own allowance. The four declarations of `lean/ScopeBenchMain.lean` (`ScopeBench.row`, `.changed`,
  `.report`, `main`) are class `T` in `tools/trust-classes.json`. The reason: they are a measurement executable,
  outside the default build, that no admission path, service mode or record reads. This follows
  `EnglishLeanBench.leastNanos` and `.policyMain`. If a reviewer prefers them as untied G[V], they are 34 lines
  under R16, with no K growth. No R16 allowance or FOLLOW-UPS row is needed as classified.
- **DELTA.** There is no user-visible delta ([DELTA.md](DELTA.md)).
- **Registries the new executable needed:**
  - `ve/assurance-manifest.json` `other_json` (`test_every_json_handling_lean_file_is_classified`);
  - `tools/lean_output_diff.py`'s harness: B1's case under `govern`, whose output has no times
    (`test_output_diff_every_executable_has_inputs`);
  - the consolidation ledger's step 7 list of top-level mains (`test_the_skeleton_step_names_every_top_level_executable_main`);
  - the regenerated `lean/declarations.txt` and `lean/predicates.txt`.
- **Size.** `git diff --numstat` against the base counts 274 hand-written lines (Lean 53 + lakefile 5, Python
  `scope_b1.py` 107 + `test_perf.py` 29 + `lean_output_diff.py` 9, test 62, side tables 10). The docs add about 130
  lines. The generated files (`declarations.txt`, `predicates.txt`, and `baselines.json`, written by
  `--update-baselines`) and the verbatim gzip copy are excluded. This is well under 600.
- **In-flight overlap.** No branch in `lean-first/*`, `feature/*`, `infra/*` or `foundation/*` touches
  `lean/lakefile.toml`, `tools/bench/` or the new files.

## Seeded bugs ([mutants.json](mutants.json))

Each bug was planted, its failing test was observed, and the source was restored.

**Lean, `lean/ScopeBenchMain.lean`.** Every definition has a mutant, and each fails
`tools/bench/test_perf.py::test_scope_b1` with "B1 is not timed: …":
- `row`: `para + 1` gives "the layout is not C11's".
- `changed`: `out` compared with itself gives "governFast answered {'ok': []}".
- `report`: the lead is the governor's id, which gives "the list run of g1 is ScopeUnknownUnit".
- `main`: the `govern` stage skips `governFast`, which gives "governFast answered None".
- One mutant survived and is recorded as equivalent: `listRun` on `layout.tail` gives the same run of u0164.s02.

**Python, `tools/bench/scope_b1.py`.** All seven are killed by `tests/test_scope_b1_input.py`:
- F1's spans off by one;
- the pilot's vocabulary wins over F1's;
- F1's open terms dropped;
- the trailing fence kept in the text;
- no layout-hash check;
- `governFast`'s answer ignored;
- `label` left out of the hash.

## Tests

- **Selected tests.** I ran `mac-pytest.sh --select -- --base ab010c3f0 --run` at `19d7a62dc`. It selected 376 of
  467 units, mostly because of the Lean root. The checks passed: `check_lean_imports`, `lake build` (with
  `ve_scope_bench`), `audit.py`, the Rust build and `test_layer_policy`. Of 375 test files, 371 passed with exit 0
  before my foreground limit stopped the run.
- **The two failures** were `test_assurance_manifest.py` and `test_consolidation_tools.py`: the registries above.
  Both are fixed in `cb6075768` and `ce9c4b12e`.
- **The remaining files**, with the two fixed files in full and `test_scope_b1_input.py`, ran on the Mac at
  `ce9c4b12e`: 1,172 passed, exit 0.
- **Other checks:** `regen_generated.py --check`, `trust_map.py --check`, `repo_map.py --check`, `lean/audit.py`
  and `gate_collection.py --check --prebuilt` (9 added, 0 refused, 0 stale, 0 malformed) all pass.
- **Known red.** None of `main-known-red.txt` was hit.
- **Full gate.** The chain runs it on the final HEAD.
- **Bench row.** `test_scope_b1` passes on the final Lean source. A changed input fails it, shown by the four Lean
  mutants above.

**Pilot bytes.** 0: the item changes no answer.

**Commits** (`main..HEAD --no-merges`, before this report): `0d08f429d`, `19d7a62dc`, `cb6075768`, `ce9c4b12e`.

## Next items

- **SC-1c** (explain route and relay; protocol queue after qt-a3c) and **SC-2**. Each runs B1 after it lands.
  B1's input is fixed, so a slowdown shows against the baseline, and a change to the layout functions shows as
  "not C11's layout".
- **sc-1ae**, after the DRI's decision.
- **Possible follow-up**, not planned: a per-row tolerance in `tools/bench/baselines.json`, or a B1 variant with
  graph governors, so a regression from `governFast` back to `govern` shows on B1 (see "Sensitivity").

## Self-review against BUILDER-CHECKLIST

1. **N.A.** No Lean answer is relayed. The bench reads its own executable's output, and `scope_b1.problems` refuses
   anything but B1's (`test_a_run_that_is_not_b1_is_reported`).
2. **PASS.** Every plan row is in the table above with its commit and test. The grep of the diff finds no Python
   copy of a Lean decision (the expected run and answer are pinned constants, not recomputed), no permanent report
   test, no authority switch, and no overlapping files.
3. **PASS.** There are 11 killed seeded bugs, Lean and Python ([mutants.json](mutants.json)), with every definition
   of the new Lean file mutated (`test_scope_b1`, `tests/test_scope_b1_input.py`). Trust mutants are N.A., since
   there is no trusted growth.
4. **N.A.** No checker behaviour changed, and Python, Lean and Rust answers are unchanged.
5. **N.A.** No relayed field. The bench input's unit ids and spans are checked against the pinned pilot
   (`test_b1_is_f1s_block_over_the_pinned_constitution`).
6. **PASS.** Evidence is pinned to commits ([layout-evidence.json](layout-evidence.json)). The full gate is the
   chain's, on the final HEAD.
7. **PASS.** There are no DELTA rows and no unsigned growth (`trust_map.py --check` PASS, +0 for this item).
8. **PASS.** No user-visible output changed: `lean/VE/` and `ve/` code are untouched, and `regen_generated.py
   --check` shows no schema change ([DELTA.md](DELTA.md)).
9. **PASS.** `select_tests.py --paths tools/bench/scope_b1.py` selects `tests/test_scope_b1_input.py` and
   `tests/test_consolidation_tools.py`. The branch selection is 376 of 467 units, not all.
10. **N.A.** There are no new theorems or statements.
11. **PASS.** There are no new budgets. The bench waits use `HANG_TIMEOUT`, and the suite test has no timing
    (`tests/test_hang_guards.py` is in the selected run).
12. **PASS.** This item is the constitution measurement: B1 at 0.539 CPU s, with the `govern` swap at 0.721 s
    ([layout-evidence.json](layout-evidence.json)). The suite has no timing assertion, by the plan's rule.
13. **PASS.** No test was removed. `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0
    malformed.
