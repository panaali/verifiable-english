# bs-sel-defer-broad: `select_tests.py --defer-broad` (build bottleneck fix F1)

Ruling: acting DRI dri-build-speed 2026-11-09, reviews/build-speed-20261109.md section "Ruling", fix F1 (guarded
trial to 2026-11-16T16:00Z). DELTA: none (DELTA.md). No Lean or trust change.

## What changed

- `tools/select_tests.py`: the new option **`--defer-broad`**. It is valid only with `--defer-heavy` and refuses
  the same `--full`, `--tier` and `--impacted`. Without `--defer-heavy` it exits 2:
  `--defer-broad widens --defer-heavy; it takes --defer-heavy`.
  With it, `defer_heavy()` also defers a heavy unit (map seconds > `DEFER_SECONDS` = 120) when all of these hold:
  - every reason that selected it is weak or a Lean reason (`lean_reason`: `reads lean/...` including the
    declarations, statements and predicates inventories, `runs Lean via lean/...` or
    `runs service mode via lean/...`; a `.py` under lean/ is Python, and a `(static)` reason is weak);
  - the unit is a broad Lean consumer: `lean_shares` >= `BROAD_LEAN_SHARE` = 0.25;
  - its own source does not name a changed Lean module or that module's directory (`names_changed_lean`).

  These still stay: a changed test, SMOKE, HISTORY_TEST, `run_order.last_failed`, and any unit with a non-Lean
  strong reason.
- Lean reach (`lean_shares`). For each unit the map records the files it read and the programs it ran. It does not
  record the Lean modules a program runs. So the reach of a unit is built from three parts, out of the lean/VE
  `.lean` files the map records as read by some unit:
  - the files it read;
  - for each Lean executable it ran, the modules in that executable's import closure from the source graph (all
    modules when a header is unreadable, as in `executables_using`);
  - every module when it ran `lake` or `lean`.

  This is the set of modules whose change selects the unit through `file_impact`'s Lean reasons.
- Threshold 0.25, measured on map 223babd3d0 (559 units) with `lean_shares`:
  - 125 units reach at most 0.1201;
  - 352 reach 0.661 to 0.99;
  - 82 reach at least 0.99;
  - no unit falls in between.

  0.25 sits in that empty gap. Command: `uv run python -c "...lean_shares(test_map.load(find_map('HEAD')), source_graph.load(ROOT))..."`.
  Output: `max<0.25: 0.1201 min>=0.25: 0.661`, `Counter({'0.25-0.99': 352, '<0.25': 125, '>=0.99': 82})`.
- Plan and printed line. Each `deferred` row is `{"seconds", "reasons", "class"}`. `class` is `"weak"` or
  `"broad"`, and a broad row also has `"lean_share"`. `deferred_seconds` works as before. The printed line now
  reads `deferred to the chain gate: N test files over 120 s selected only for weak reasons or as broad Lean
  consumers (K) (S s): a (broad), b, ...`.
- Who passes the option: only builder feedback runs pass `--defer-heavy` and `--defer-broad`. These never pass
  them, so they still run every deferred unit, and the merge train's full suite runs every unit:
  - the chain's own selected run (`MAC_PYTEST_NO_DEFER=1`);
  - the GATE_REUSE_SAME_TREE final run;
  - `tools/gate.py`;
  - `--full`.

  This is stated in `defer_heavy`'s docstring and in docs/TESTING.md.

## For the hook row bs-sel-defer-broad-hook (manage-agents, not this item)

- Option name: `--defer-broad`, passed after `--defer-heavy`. Detect it with
  `grep -qF -- '"--defer-broad"' $w/tools/select_tests.py`, the same check `defer-heavy.zsh` uses for
  `"--defer-heavy"`.
- Plan fields the ledger (`tools-local/buildfix-sel.py`) should read from `select_tests.py ... --json`:
  - `deferred` (unit -> `{seconds, reasons, class, lean_share?}`); sum `seconds` where `class == "broad"` for F1's
    share, and where `class == "weak"` for the earlier `--defer-heavy`;
  - `deferred_seconds` (all deferred);
  - `selected` and `selected_count` (after deferral);
  - `map.commit`.

  From a text run, read the `deferred to the chain gate:` line, where broad units are marked ` (broad)`.
- For the guard ("a broad-deferred unit failing in the same item's chain run or train"): the broad units are the
  `deferred` keys with `class == "broad"`.

## Before and after (recorded plans, map seconds)

The plans were recorded at each item's tip with that tip's own `tools/select_tests.py --base <base> --json`, in a
temporary worktree. They are trimmed in `tests/data/select_defer/<item>.json`. The numbers below are asserted by
`tests/test_select_defer.py::test_the_recorded_plans_before_and_after`:

| item | base | selected units | selected s | after --defer-heavy | after + --defer-broad | change |
|---|---|---|---|---|---|---|
| cmp-s3a-cfr-2 | 6db6ee16dd | 116 | 19915 | 19915 | 5835 (30 broad) | -71% |
| sc-7 | da5303b787 | 120 | 24080 | 24080 | 12641 (21 broad) | -48% |
| ps-2a | 223babd3d0 | 486 | 50868 | 50712 | 47814 (6 broad, 1 weak) | -6% |
| sn-b6d | 223babd3d0 | 454 | 50047 | 50047 | 22076 (60 broad) | -56% |

- The one-family Lean changes (cfr-2, sc-7, sn-b6d) lose about half or more of their selected seconds.
- ps-2a also changed Python (`tools/lean_statements.py`, `lean/audit.py`) and `.gitattributes`. Its heavy units
  carry those strong non-Lean reasons, so they correctly stay.
- Recomputed at the tips, the cfr-2 and sc-7 plans do not select `test_readings_rd6b_differential.py` and
  `test_speech_polar_lean.py`: they are ve_service users, and the RightClauses and Scope changes reach no
  ve_service user. The tests check the three that those plans select, and all five on sn-b6d (one Senses family).
- sc-7 keeps four heavy Lean tests that name `lean/VE/Audit.lean`, which sc-7 changed, for example
  `test_lean_audit_record.py`.

## Tests (tests/test_select_defer.py, no Lean build, no test run)

- `test_lean_reasons_are_the_lean_trees_files_never_python_or_static`
- `test_a_units_lean_reach_is_what_it_reads_and_the_closures_of_what_it_runs` (synthetic map and graph, plus the unreadable case)
- `test_a_unit_names_a_changed_module_or_its_directory_never_a_sibling`: both directions, including `tests/test_scope_lean.py` for a Scope change
- `test_with_shares_a_broad_lean_consumer_is_deferred_and_the_rest_stays`: broad deferred; Python reason, narrow share and own-source stay; nothing broad without shares
- `test_the_share_threshold_is_inclusive`
- `test_the_heavy_lean_wide_files_are_deferred_for_a_one_family_lean_change[cmp-s3a-cfr-2|sc-7|sn-b6d]`: also not deferred without `--defer-broad`
- `test_each_heavy_lean_wide_file_stays_when_it_changed_or_failed[...]`
- `test_a_familys_own_lean_test_and_a_python_reader_stay_in_the_recorded_sc_7_plan`
- `test_the_recorded_plans_before_and_after`
- `test_the_option_passes_the_maps_shares_and_marks_broad_files`: JSON and text output, opt-in
- `test_defer_broad_takes_defer_heavy_and_its_exclusions`: exit 2 without `--defer-heavy`, and with `--full`, `--impacted` or `--tier`

Run: `uv run pytest -q tests/test_select_defer.py` -> `38 passed`.

## Seeded bugs (Python; docs/infra/bs-sel-defer-broad/seeded-bugs.json)

Each bug was planted alone in `tools/select_tests.py`, and the named test was run alone. All 9 were caught (rc 1),
then the file was restored:

- B1: share `>=` changed to `>`.
- B2: `all(weak or Lean)` changed to `any`.
- B3: the own-source rule dropped.
- B4: every executable reaches every module.
- B5: the directory pattern matches a sibling.
- B6: a `.py` under lean/ counted as a Lean reason.
- B7: `keep` ignored.
- B8: `--defer-broad` accepted alone.
- B9: the `(broad)` mark dropped.
