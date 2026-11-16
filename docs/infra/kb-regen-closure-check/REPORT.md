# kb-regen-closure-check: the kernel-closure entry's check fails on any byte its writer would change

- Status: built. No DRI signature is reserved and there are no DELTA rows (generation tooling; no trusted line, no
  decision path, kernel total 9,966 unchanged). Trust +0. HEAD: see `git log -1`; this report is the last commit.
- Change: `tools/kernel_closure.py --fresh FILE` fails unless FILE is byte for byte what `--out` writes for the same
  measurement. The `kernel-closure` entry of `tools/regen_generated.py` now runs `--check B --fresh B`: one Lean
  measurement, the section-6 limits unchanged, plus the byte compare.
- Found on main 828449f6: its committed `docs/kernel/closure-baseline.json` was itself stale (rows `discourse`, `document`,
  +8 lines each, equal totals). Regenerated here with the entry's writer, and the spec table updated to quote it.
- Open: FOLLOW-UP below. No train step runs this entry's check after a clean merge today, so the train still does not
  rewrite the file by itself. Builders and verify-fix run `regen_generated.py --check` and now see it.

SIZE: 45 product (tools/kernel_closure.py +39/-6, tools/regen_generated.py +6/-2), 103 tests
(tests/test_regen_generated.py +69, tests/test_kernel_closure.py +34), 6 other hand-written lines
(docs/spec/kernel-boundary.md +4/-2), plus this report and its evidence. The baseline's 7/7 lines are generated.

Row: kb-regen-closure-check (infra). DRI decider 2026-11-13, reviews/dri-decisions-20261113-rebase-serial-manifest.md
item 2. Task written by dri-infra-taskwrite-1116.

## Deliverables

| # | Task line | Where | Test or evidence |
|---|---|---|---|
| 1 | The entry's check regenerates and compares bytes with the baseline; any difference = stale | `kernel_closure.render` (the one function `--out` writes with), `check_fresh`, `--fresh`; entry `kernel-closure` check argv in `tools/regen_generated.py` | `tests/test_regen_generated.py::test_a_stale_closure_row_with_equal_totals_is_stale_and_the_r12_write_rewrites_it`, `tests/test_kernel_closure.py::test_fresh_fails_on_any_byte_the_write_would_change_and_check_alone_does_not` |
| 1 | `--check`'s total/writer limits kept as they are, and both run | `main`: `--check` block unchanged except that it no longer returns before `--fresh`. Exit 1 if either fails. `tools/gate.py`'s "Kernel check" stage is unchanged (`--check` only) | `tests/test_regen_generated.py::test_an_up_to_date_closure_baseline_is_not_stale_and_a_limit_still_fails_it` ("FAIL: the kernel grew from"), seed S4 |
| 1 | So R12 rewrites the file with the entry's generator | Fixture: `R.check([entry])` fails `kernel-closure`, then `R.write` of the failed entries runs the entry's own `--out`, and the file becomes the fresh bytes. The train's own wiring is NOT done (FOLLOW-UP) | same R12 test. Train scripts: see Notes |
| 2 | Measure the cost, old vs new (MEASURED) | below | `evidence.md` (Timing tails) |
| 3 | Fails on the old check: a stale per-path row with equal totals is reported stale, and an up-to-date baseline is not | the two `test_regen_generated.py` tests above. Under the old argv the first one fails (seed S1). The test also asserts that `kernel_closure.main(["--check", stale])` returns 0 | `evidence.md`, seed1.log |
| - | Condition tests stay selected | `select_tests.py --base $(git merge-base HEAD main)` selects `tests/test_kernel_closure.py` and `tests/test_regen_generated.py` (472/634 units; `/tmp/kbrc-plan.log` line 4) | final selected run below |

How deliverable 1 regenerates: the task text says `--out <tmp>` and compare. `--fresh` measures once and renders with
`render`, the function `--out` writes with, so the compared bytes are `--out`'s by construction (seed S3: a second
layout in `--out` fails the tests). A literal `--out <tmp>` call plus a separate `--check` would run the Lean half
twice. `--out`'s own refusals (the signed total, the writer ratchet) stay in the writer that R12 runs.

## Cost (MEASURED, this host)

Host: multi-agent-lab-2 (ve-cloud-2, 32 cores), not VM1. The task names VM1, but this worktree runs here. The figures
are seconds of `uv run python tools/kernel_closure.py ...` on 75735543 after `lake build` (`/tmp/kbrc-*.log`, saved in `evidence.md`;
tails in `evidence.md` (Timing tails)):

| run | old: `--check B` | new: `--check B --fresh B` | 1-min load |
|---|---|---|---|
| first, cold (15:20Z, 15:22Z) | 122.0 s (rc 0) | 107.1 s (rc 1: main's baseline stale) | 7.0 / 7.3 |
| `regen_generated.py --check --only kernel-closure` (15:28Z) | - | 79.3 s (rc 0, after the regeneration) | 6.6 |
| warm, back to back (15:29Z) | 76.0 s | 95.7 s | 7.4 -> 14.8 |

Both commands run one measurement (one `lake build` of the registry's imports, then one `lake env lean`). The new
check adds `render` and a string compare. Timed alone over 20 runs on the real 190,663-byte baseline: 1.24 ms when
fresh and 2.28 ms when stale (it then also lists the differing rows). The run-to-run spread (76 to 122 s) is host load
and cache, not the check. Cost added to any step that already ran the old check: about 2 ms.

## Found on main: the committed baseline was stale

`--fresh` on main's tree (828449f6, this branch before the refresh) printed:
`STALE: docs/kernel/closure-baseline.json is not what --out writes now (path rows discourse, document)`
(`/tmp/kbrc-new.log`). Cause: 010c493e5 (2026-11-15 21:30Z, "Tie core routing to both Lean refusal sites") changed
`lean/VE/Service/Document.lean` (+14/-4). It was made in parallel with d1ec51130's re-measure (20:15Z; neither is an
ancestor of the other, per `git merge-base --is-ancestor`). `VE.Service.Document` is charged 8 more lines in both
candidate rows:

- discourse: spec 36,199 -> 36,207, lines 36,205 -> 36,213
- document: spec 35,282 -> 35,290, lines 36,170 -> 36,178 (`wrap_modules` too)

No top-level field changed: kernel_lines is 9,966, 56 writers are outside the kernel, and keyed is unchanged. Fixed in
75735543 by `uv run python tools/regen_generated.py --write --only kernel-closure`. Its output is byte-identical
(`cmp`) to an independent earlier `--out /tmp/kbrc-m/a.json` measurement, so the measurement is deterministic. The
spec table rows quoting these figures (docs/spec/kernel-boundary.md, section 2 table) were updated by hand to the
generated values: `test_the_records_quote_the_saved_measurement` requires that, and it passed (`/tmp/kbrc-3.log`).

## Seeded bugs (Python; no Lean or Rust product code changed)

`evidence.md` (section Seeded bugs) gives file, find/replace, failing test and log. All four were caught and restored, and git status
was clean after each.

- S1 `tools/regen_generated.py`: the entry's check back to `--check` only. This fails
  `test_a_stale_closure_row_with_equal_totals_is_stale_and_the_r12_write_rewrites_it` (`evidence.md`, seed1.log).
- S2 `tools/kernel_closure.py`: `check_fresh` compares only the path names and the kernel total. This fails the R12
  test and `test_fresh_fails_on_any_byte_the_write_would_change_and_check_alone_does_not` (`evidence.md`, seed2.log).
- S3 `tools/kernel_closure.py`: `--out` writes indent=2 instead of `render`. This fails the same two tests
  (`evidence.md`, seed3.log).
- S4 `tools/kernel_closure.py`: `--check` limits skipped when `--fresh` is given. This fails all three new tests
  (`evidence.md`, seed4.log).

Light lane / trust mutants: N.A. No Lean changed and nothing trusted changed. The task asks for no trust_mutants
record.

## Tests run

- New and condition tests while iterating: `uv run pytest -q tests/test_regen_generated.py -k closure` plus the new
  kernel test plus `test_the_saved_baseline_is_of_this_registry` and `test_the_records_quote_the_saved_measurement`.
  Result: 5 passed after the fixture fix (`/tmp/kbrc-1.log`, `/tmp/kbrc-2.log`), and the 2 condition tests passed after
  the refresh (`/tmp/kbrc-3.log`).
- Final selected run on committed 75735543 (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select`, 487 units in 6 Actions
  shards, run kb-regen-closure-check-75735543-t843180): exit 0 after 2003 s; shards 1-6 passed 84, 82, 85, 84, 86 and 66
  units (487), 0 failed (`/tmp/kbrc-select.log`, SHARD lines; rc file 0). Only docs/*.md were committed after it.
- Not run: the full gate (the chain runs it on the final HEAD), and the trust_mutants sweep (N.A., above).

## FOLLOW-UP

FOLLOW-UP: kb-regen-closure-train-wiring. The merge train runs the kernel-closure entry's check after a clean merge
and writes it when stale. This is the part of deliverable 1 ("so R12 rewrites the file") that lives in
`manage-agents/merge-train.sh`, not in this repository. Today no train step runs this check on a clean merge:
`candregen` runs only `at_merge` entries (tree-only, seconds; this entry needs the Lean build, and
`test_the_entries_refreshed_at_merge_are_tree_only_writers` keeps it out). `branchregen` writes the fixed list
`le=(lean-statements lean-audit-manifests assurance-doc)`, chosen by the trust_map probe and not by checks.
`--resolve` runs every writer only when a generated file conflicts. Proposal, cheapest form: in `branchregen`, after
its Lean writes and pins (the tree is built there), run `regen_generated.py --check --only kernel-closure`, and on
exit 1 run `--write --only kernel-closure` and commit with the other refreshed files. Measured cost is 76 to 122 s per
run on this host, against a step that already takes 15 to 36 min (merge-train.sh comment on specregen). The cheaper
registry-only comparison the task mentions would not catch the case found on main above: a Lean source change with the
registry unchanged.

## Notes for the DRI

- Until the FOLLOW-UP lands, the check catches a stale baseline where `regen_generated.py --check` runs in full.
  Builders, verify-fix and sync agents run it (tools-local/fixmap.py tells them to). kb-1's verify-fix ran it and it
  passed (verifyfix-kb-1.final.md, last paragraph). With this change it would have failed, naming the rows, before the
  requeue.
- A rewrite by R12 can still leave `docs/spec/kernel-boundary.md`'s table behind (a hand-kept record that quotes the
  baseline; `test_the_records_quote_the_saved_measurement` catches it). That happened here: main's spec and baseline
  were stale together, so the test passed on main. Once the baseline is fresh, the test names the spec rows to update.
  In the kb-1 case the spec already quoted main's figures, so a rewrite alone would have passed.
- `tools/gate.py`'s "Kernel check" stage still runs `--check` only (section 6.1, the release guard). Adding `--fresh`
  there would make the gate fail on staleness as well. I left it unchanged, the narrower reading: the task scopes the
  change to the regen entry.
  As a result, the entry's `fresh="gate:Kernel check"` field (its automatic, unmocked run) now covers the limits half
  of its check only. No automatic run covers the `--fresh` half on a branch: the two baseline tests catch registry
  drift but not a Lean-only drift like main's. Adding `--fresh` to that gate stage would close it at no measured cost
  (about 2 ms). It is a gate behaviour change, so I leave the decision to the DRI and do not file it.

## Spec re-read

- "regenerates to a temp file ... compares bytes ...; any difference = stale" against the task's DO (1):
  `check_fresh` compares `saved_text == render(result)` over the whole file, not by field. Rows and fields are only
  named in the message.
- "Keep --check's total/writer limits as they are ... if regen's check still needs them, run both" against DO (1):
  `check_total` and `check_writers` are untouched, and both run with `--fresh` (seed S4).
- Section 6.1 text against docs/spec/kernel-boundary.md:403-407: the gate's command is unchanged; the added sentence
  covers only the regen entry's check.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed answer or schema touched).
2. Deliverables: PASS. Table above; the unfinished train part is the FOLLOW-UP. Diff grep: no Lean-decision copy and no
   new report test (the new tests exercise tools, not batch evidence).
3. Tests can fail: PASS. Seeds S1 to S4 (`evidence.md` (section Seeded bugs)). Head against head and empty: `check_fresh` passes only on
   identical bytes. Stale, layout and field cases are in `test_fresh_fails_on_any_byte_the_write_would_change_and_check_alone_does_not`.
4. Py/Lean/Rust agree: N.A. (no checker output changes; the Lean half is unchanged).
5. R8 binding: N.A. (no relayed field).
6. Gate evidence on final HEAD: PASS for the selected run on committed code (above). The full gate is left to the chain.
7. Unsigned items: PASS. No DELTA rows, no trust growth (`git diff --stat main...HEAD` touches no Lean).
8. User-visible changes in DELTA: PASS, none. A new CLI flag, an extra STALE line from the regen check, and candidate
   figures in a measurement record; no verdict, code or text of the checker.
9. Test selection: PASS. `select_tests.py --base $(git merge-base HEAD main)` selects both condition files
   (`/tmp/kbrc-plan.log`). Seed S1 makes a selected test fail.
10. Lean statements: N.A. (no Lean).
11. Budgets and deadlines: N.A. (no new limit; `--timeout` is unchanged).
12. CPU regression: PASS. About 2 ms added per check (Cost section).
13. Removed tests: N.A. (none removed or renamed).
14. Both directions and cited evidence: PASS. Stale is refused and up to date passes (both R12 tests and the kernel
    test). Every figure above names its log.
15. Overclaim, silent cut, new check can fail, limits: PASS (the train wiring is stated as not done; S1 to S4) and N.A.
    (limits, none added).
