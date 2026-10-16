# fix/relay-mutation-gate: the relay mutation gate passes on main again

No DRI signature needed: the one user-visible delta is signed R8 (DELTA.md).

## Problem

`tools/relay_mutation_gate.py` exited 1 on main. Only review-ready's `[relay]` check ran it, and only when relay
code changed, so every relay-touching item saw a `[relay] FAIL` that was not its own, and items merged on top of
it. Reproduced on main 2a4fbf708 (all 42 routes, 21 min): 39 failures in route, parse, graph, norm-defaults and
readings-route. After tarch-b8 (dae12d5ff) merged: 13. After lf-14c, premise-scale and ts-B3 merged (21029b86e,
this branch's merge base): 10 on the merged tree.

## Bisect

Each point gates the five failing routes with that commit's own tree (gate, fixtures, allow-list, built Lean),
over main's first-parent merges since 2026-10-13 (`/tmp/rmg-bisect/run.sh`, one detached worktree).

| Main merge | Failures | What changed |
|---|---|---|
| 2d964d5dc fix-main-relay (10-13) | 98 | already red: 93 stale readings-route/route/norm-defaults paths, 5 accepted readings-route mutants |
| 4667e8de6 lf-14d (10-14) | 124 | lf-14d re-recorded `tests/data/relay-gate-cases.jsonl`; the new route `background`, graph `background` and parse error fixtures expose untyped fields (route/graph/parse accepted mutants first appear) |
| 9f40783b8 english-run-root (10-14) | 26 | bad2756f2 pruned 181 stale lines and filed readings-route `fill` and `units/*/content/norm/over` under B0 |
| b96f04a5a lf-14b (10-14) | 29 | lf-14b (branched before english-run-root) filed the same three paths under F10; B0, first in file order at equal specificity, takes every finding, so F10's three match nothing |
| b98d87947 qa-q2 (10-15) | 30 | qa-q2 added `unsaid[].description` to the norm-defaults row typed bare `str`: an emptied description is accepted |
| 1cbd5ed1e tarch-b1 (10-15) | 30 | none |
| 16a02693a lf-14a (10-15) | 39 | lf-14a typed parse `ast` (generated formula) and gave readings-route labels and conflict targets `minLength 1`: nine allow-list paths (parse B0/F3/F7/F11, readings-route F11) match nothing |
| dae12d5ff tarch-b8 (10-16) | 13 | tarch-b8 typed graph background and parse `error`, filed route Background lists: the lf-14d findings are gone |
| 21029b86e (lf-14c, premise-scale, ts-B3) | 10 on the merged tree | lf-14c (8cbb3049f) bound route background/premises/generators (`x-same-length`, `x-equal-fields`, core formulas) after tarch-b8 had listed them: 8 B0/F4 paths match nothing. main pruned F10's `fill` while this branch had pruned B0's, so the merge listed it nowhere (2 accepted) |

Not gated separately: f98183bf5 (AR-3: no change to gate inputs), dccd9cf5a (runner-portability: 4 lines in
`LeanService._write_all`/`_read_line`, which the gate's `_Replay` overrides), 8594f1d05, f187e4e9a, 4ce477e18
(between gated points with unchanged results, or no gate-input change).

## Cause and fix

The gate's mutations are right; the inputs went stale as schemas were tightened on parallel branches, and no
test ran the gate on all routes, so nothing stopped a merge.

1. **norm-defaults `description` (qa-q2).** Typed in the Lean shape: `("description", n [str, .minLength 1])`
   in `lean/ResponseShape/Schemas/NormDefaults.lean`; `norm-defaults.json` regenerated with
   `tools/response_schemas.py --write`, `lean/declarations.txt` with `tools/lean_statements.py`. This is F11's
   own remedy ("give each a non-empty type"). The skeleton erases `minLength`, so `runCaseReported_fits` is
   unchanged and still builds. Not allow-listed: Lean always writes `unsaidDescription p`, never empty.
2. **Stale paths (lf-14a, lf-14c).** Removed: parse B0 duplicate `ast/*`, F3 retype `ast`, `ast/*`, `ast/*/*`,
   F7 untyped `ast/*/*`, F11 empty `ast/*/*` (lf-14a); route B0 duplicate/empty `background`, `generators`,
   `premises`, F4 rebind `background/*/*/*/*`, `premises/*/*/*/*` (lf-14c). Each is a mutant the gate now
   refuses; the gate itself fails an entry that matches nothing. The readings-route F11 label/target paths
   were stale too; main (lf-14c) pruned them independently.
3. **readings-route `fill` listed twice (english-run-root vs lf-14b).** One copy is kept, under B0 as on main:
   `fill` is the premise list Lean computes, B0's class. (Before the main sync this branch kept F10's copy; main
   meanwhile pruned F10's, and premise-scale/lf-14c made a repeated `over` refused, so B0 is the minimal state.)

The allow-list was not widened: 14 paths (and the 3 entries they emptied) are removed relative to main (`git diff main --
tools/relay-gate-allow.json`), no path or entry is added. premise-scale and tarch-b8 are both merged now, so
this change is on top of both.

## Regression test

`tests/test_relay_mutation_gate.py`:

- `test_the_gate_passes_on_every_route[<route>]`, one case per service mode and one-shot route (43): `run_gate({route})`
  on the committed schemas, fixtures and allow-list has no failure, an `ok` fixture, and every mutant is refused or
  listed. It replaces `test_the_gate_passes_on_sample_routes_with_the_committed_allow_list` (three of these cases;
  `Test-removed` trailer in f614070cc). Per route, so xdist spreads the ~12 CPU-minutes.
- `test_every_allow_list_entry_and_untyped_manifest_field_names_a_gated_route`: a one-route run checks only its
  route's entries, so the cases together cover the whole allow-list only if every entry names a gated route.

## Evidence (saved)

- `docs/fix-relay-mutation-gate/relay-gate-report.json`: `tools/relay_mutation_gate.py --json` on e11d781a3 (the
  merged tree; the later commits only add docs): 43 routes, 502 fixtures, 117799 mutants, 110445 refused, 7354
  listed, **0 failures**; its `inputs` hashes are those of the committed fixtures and allow-list.
- Selected tests (`mac-pytest.sh --select -- --base 21029b86e --run`, tree 463d6a82b of d5c9e5a02; no Mac slot
  within 600 s, so it ran on the VM): 400/400 units, 0 failed, exit 0, 5534 s. It includes
  `tests/test_relay_mutation_gate.py` (exit 0, all 43 route cases).

## Seeded bugs

All in `docs/fix-relay-mutation-gate/seeded-bugs.json`; each was planted, its test failed, and it was restored.

1. Lean, `lean/ResponseShape/Schemas/NormDefaults.lean`: `description` back to `str` (rebuilt, regenerated) →
   `test_the_gate_passes_on_every_route[service:norm-defaults]` fails: accepted empty description.
2. `tools/relay-gate-allow.json`: F3 parse retype `ast` put back → `[service:parse]` fails: matches nothing.
3. `tools/relay-gate-allow.json`: readings-route `fill` in B0 and F10 → `[service:readings-route]` fails.
4. `tools/relay-gate-allow.json`: an entry for `service:no-such-mode` →
   `test_every_allow_list_entry_and_untyped_manifest_field_names_a_gated_route` fails.
5. The whole fix undone (four files at 5f0089e29^, decoder rebuilt) → `[service:parse]`, `[service:norm-defaults]`,
   `[service:readings-route]` fail.

Changed product code by language: Lean (`NormDefaults.lean`) only; no Python or Rust product code changed.

## Pre-existing

Tests in `main-known-red.txt` (lf-14d's sub-tick deadline tests and the rd8 report test) are not touched here.

## Not run

The full release gate (fast lane: the chain runs the selected tests, the merge train the full suite). The Rust
release binary is not built in this worktree, so `regen_generated.py --check --only checker-pins` was run with
`VE_REGEN_NO_RUST=1` (the ve_service pin holds).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: PASS. norm-defaults `description` typed non-empty; the whole gate (every field dropped, emptied, duplicated, retyped incl. 10k-deep, rebound) on all 43 routes: `relay-gate-report.json`, 0 failures; `test_the_gate_passes_on_every_route[*]`.
2. Deliverables built, no rule broken: PASS. Reproduce on main (2a4fbf708, 39 failures), bisect (table above), cause fixed (shape + regenerated schema; stale paths removed, none added), suite test, seeded undo-the-fix (seeded bug 5). No Python copy of a Lean decision, no permanent report test (D4), no generated file hand-edited; `tools/relay-gate-allow.json` change kept minimal (14 removals) and made after premise-scale and tarch-b8 merged.
3. Tests and gates can fail: PASS. Seeded bugs 1-5 (`seeded-bugs.json`), each a failing test; the allow-list names exact paths.
4. Py/Lean/Rust agree, valid inputs pass: PASS. Every genuine fixture answer is accepted (`run_gate` fails on a refused genuine answer); `tests/test_route_row_schemas.py` and the norm-defaults tests in the selected run pass.
5. R8 binding: PASS. No new field read; the empty-description mutant is refused (`[service:norm-defaults]`); binding mutants unchanged across the gate.
6. Gate evidence matches final HEAD: PASS. Synced with main (21029b86e); `relay-gate-report.json` from e11d781a3, whose later commits add only docs; selected run on the tree of d5c9e5a02; scope base from `git merge-base`.
7. No unsigned item: PASS. One DELTA row, signed R8 (DELTA.md); no trust-budget growth.
8. Every user-visible change in DELTA: PASS. Only a tampered answer changes outcome (DELTA row 1); genuine answers unchanged (all fixtures accepted).
9. Test selection finds the tests: PASS. `select_tests.py --base 21029b86e` selects `tests/test_relay_mutation_gate.py` for the schema and allow-list change (seeded bugs 1 and 5 fail there).
10. Lean statements: N.A. for new theorems (none). The shape change leaves `runCaseReported_fits` unchanged (the skeleton erases `minLength`); `lake build` and `lean_statements.py --check` pass.
11. Budgets and deadlines: N.A. No budget, limit or deadline code changed.
12. CPU/memory regression: N.A. for product code (a schema `minLength`); the suite gains ~12 CPU-minutes of gate cases, spread per route over xdist.
13. Test-removed trailer: PASS. f614070cc; `tools/gate_collection.py --check --prebuilt`: 1 removed by a trailer, 0 refused, 0 stale, 0 malformed.
