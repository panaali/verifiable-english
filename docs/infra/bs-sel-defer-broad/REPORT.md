# bs-sel-defer-broad: `select_tests.py --defer-broad` (build bottleneck fix F1)

- **Status:** built. HEAD is the branch tip; the commits are listed under "Task lines". No DRI signature is needed. DELTA: none (DELTA.md).
- **What changed:** `tools/select_tests.py` has a new opt-in option, `--defer-broad`, used only with `--defer-heavy`. With it, a builder run defers the heavy broad Lean consumers that only weak and Lean reasons select.
- **Effect:** on the recorded plans, the map seconds drop by 71% (cmp-s3a-cfr-2), 44% (sc-7), 56% (sn-b6d) and 6% (ps-2a, which changed Python).
- **Open (HUMAN/EXTERNAL):** the manage-agents hook row bs-sel-defer-broad-hook, owned by its delegate, is not this item. The full gate is run by the chain.

Ruling: acting DRI dri-build-speed 2026-11-09, reviews/build-speed-20261109.md section "Ruling", fix F1 (guarded
trial to 2026-11-16T16:00Z). There is no Lean change and no trust change.

## What changed

- **The option.** `--defer-broad` is valid only with `--defer-heavy`. It refuses `--full`, `--tier` and `--impacted`, the same as `--defer-heavy`. Without `--defer-heavy` it exits 2 with the message `--defer-broad widens --defer-heavy; it takes --defer-heavy`.
- **What it defers.** `defer_heavy(..., shares=)` (`deferral`) also defers a heavy unit (map seconds > `DEFER_SECONDS` = 120) when all of these hold:
  - every reason that selects it is weak or a Lean reason;
  - its reach (`lean_shares`) is at least `BROAD_LEAN_SHARE` = 0.25;
  - its own source names no changed Lean module and no directory of one (`names_changed_lean`);
  - its file name does not make it a test of a changed module's family (`family_test`, e.g. `test_scope_*.py` for lean/VE/Scope).

  These still stay, as before: a changed test, SMOKE, HISTORY_TEST, `run_order.last_failed`, a unit with no recorded seconds, and a unit that `shares` does not hold.
- **Lean reasons** (`lean_reason`). A reason is a Lean reason when it says `reads`, `runs Lean via` or `runs service mode via`, and the file it names is either:
  - a Lean input (`is_lean_input`: a `.lean` module or a Lean project file), or
  - one of `LEAN_INVENTORIES`: `lean/declarations.txt`, `statements.txt`, `predicates.txt`, `axioms.txt`, `checkers.lock`.

  `checkers.lock` is in the list because it is the checker-pins generated file, which every rebuilt checker rewrites.

  Any other file under lean/ is Python or data, and a unit selected by it stays: `lean/audit.py`, `route-cases.json`, `frozen-sources.sha256`, `*.md`.
- **Lean reach** (`lean_shares`). The map records, per unit, the files it read and the programs it ran. It does not record which Lean modules a program runs. So a unit's reach is counted against the lean/VE `.lean` files that the map records some unit reading, and is the union of:
  - the modules the unit read;
  - the import closure (from the source graph) of each Lean executable it ran, or every module when a header is unreadable;
  - every module, when it ran `lake` or `lean`.

  This is the set of modules whose change selects the unit through `file_impact`'s Lean reasons.
- **The threshold.** On map 223babd3d0 (559 units), `lean_shares` gives 125 units at <= 0.1201, 352 units at 0.661-0.99 and 82 units at >= 0.99. No unit falls in between, so 0.25 sits in that gap. The command and its output:
  `uv run python -c "import sys,collections; sys.path.insert(0,'tools'); import select_tests as st, test_map, source_graph; from pathlib import Path; d=test_map.load(Path.home()/'.cache/ve-testmap/223babd3d047fbd14cf5ddd01fdd5dd2ba9ba9a6.json.gz'); s=st.lean_shares(d, source_graph.load(st.ROOT)); v=[s.get(t,0.0) for t in d['tests']]; print(max(x for x in v if x<0.25), min(x for x in v if x>=0.25)); print(collections.Counter('<0.25' if x<0.25 else ('>=0.99' if x>=0.99 else '0.25-0.99') for x in v))"`
  gives `0.1201 0.661` and `Counter({'0.25-0.99': 352, '<0.25': 125, '>=0.99': 82})`.
- **The plan.** Each `deferred` row is `{"seconds", "reasons", "class"}`. `class` is `"weak"` or `"broad"`, and a broad row also has `"lean_share"`. `deferred_seconds` is the same as before. The printed line now reads:
  `deferred to the chain gate: N test files over 120 s selected only for weak reasons or as broad Lean consumers (K) (S s): a (broad), b, ...`
- **Runs that never pass the option.** Only builder feedback runs pass `--defer-heavy` and `--defer-broad`. These runs never pass them, so they still run every deferred unit:
  - the chain's own selected run (`MAC_PYTEST_NO_DEFER=1`);
  - the GATE_REUSE_SAME_TREE final run;
  - `tools/gate.py`;
  - `--full`.

  The merge train's full suite also still runs every unit. This is stated in `defer_heavy`'s docstring and in docs/TESTING.md.

## For the hook row bs-sel-defer-broad-hook (manage-agents, not this item)

- **The option** is `--defer-broad`, passed after `--defer-heavy`. To detect whether a worktree's selector has it, use `grep -qF -- '"--defer-broad"' $w/tools/select_tests.py`. This mirrors the existing `"--defer-heavy"` check in defer-heavy.zsh.
- **What the ledger (`tools-local/buildfix-sel.py`) should read** from `select_tests.py ... --json`:
  - `deferred` (unit -> `{seconds, reasons, class, lean_share?}`). Summing `seconds` where `class == "broad"` gives F1's share; where `class == "weak"`, it gives what `--defer-heavy` already deferred.
  - `deferred_seconds`;
  - `selected` and `selected_count` (after deferral);
  - `map.commit`.

  In a text run, the broad units are marked ` (broad)` on the `deferred to the chain gate:` line.
- **The guard's "broad-deferred unit":** the `deferred` keys whose `class == "broad"`.

## Before and after (recorded plans, map seconds)

Each plan was recorded at the item's tip, using that tip's own `tools/select_tests.py --base <base> --json`, in a temporary worktree. The trimmed plans are in `tests/data/select_defer/<item>.json`. `tests/test_select_defer.py::test_each_recorded_plan_keeps_these_map_seconds` asserts these numbers:

| item | base | selected units | selected s | after --defer-heavy | after + --defer-broad | change |
|---|---|---|---|---|---|---|
| cmp-s3a-cfr-2 | 6db6ee16dd | 116 | 19915 | 19915 | 5835 (30 broad) | -71% |
| sc-7 | da5303b787 | 120 | 24080 | 24080 | 13407 (19 broad) | -44% |
| ps-2a | 223babd3d0 | 486 | 50868 | 50712 | 47814 (6 broad, 1 weak) | -6% |
| sn-b6d | 223babd3d0 | 454 | 50047 | 50047 | 22076 (60 broad) | -56% |

- **Mostly-Lean changes** (cfr-2: RightClauses; sc-7: Scope and VE/Audit; sn-b6d: Senses, plus `ve/backends/senses.py` and a relay test) lose about half or more of their selected seconds.
- **ps-2a.** It also changed Python (`tools/lean_statements.py`, `lean/audit.py`) and `.gitattributes`. Its heavy units carry those non-Lean reasons, so they correctly stay.
- **The 450-486 units in the review** match ps-2a (486) and sn-b6d (454).
- **Why cfr-2 and sc-7 select only 116 and 120 units at their tips.** Their changed Lean modules are in no Lean executable's import closure: `executables_using` returns nothing for `VE.RightClauses.Plain`, `VE.Scope.Authoring`, `VE.Audit` and `VE.Service.ScopeExamples` at those tips. So no executable runner is selected through them, including the ve_service users `test_readings_rd6b_differential.py` and `test_speech_polar_lean.py`. The tests therefore check the three heavy files those plans select, and all five on sn-b6d.
- **What sc-7 keeps:**
  - the units whose source names `lean/VE/Audit.lean`, e.g. `test_question_reading.py`;
  - the family tests by name: `test_scope_answer.py` (`test_lean_audit_record.py` is kept by both rules);
  - units with non-Lean reasons.

## Task lines

| task line | commit | test | tag |
|---|---|---|---|
| 1. `--defer-broad`, only with `--defer-heavy`; weak or broad; broad = Lean reason + share >= 0.25 from the map | 4a904f190, 1baa360f3 | `test_with_shares_a_broad_lean_consumer_is_deferred_and_the_rest_stays`, `test_the_share_threshold_is_inclusive`, `test_lean_reasons_are_the_lean_trees_files_never_python_or_static`, `test_a_units_lean_reach_is_what_it_reads_and_the_closures_of_what_it_runs`, `test_defer_broad_takes_defer_heavy_and_its_exclusions` | AGENT |
| 2. never deferred: changed test, SMOKE, HISTORY_TEST, last failed, non-Lean strong reason, own source names a changed module or its directory | 4a904f190, 1baa360f3 | `test_each_heavy_lean_wide_file_stays_when_it_changed_or_failed`, `test_a_familys_own_lean_test_and_a_python_reader_stay_in_the_recorded_sc_7_plan`, `test_a_unit_names_a_changed_module_or_its_directory_never_a_sibling`, `test_a_test_of_a_changed_modules_family_is_named_for_it`, `test_these_heavy_weak_units_always_stay` | AGENT |
| 3. deferred rows give the class; printed line marks broad | 4a904f190 | `test_the_option_passes_the_maps_shares_and_marks_broad_files`, `test_a_heavy_file_selected_only_for_weak_reasons_is_deferred` | AGENT |
| 4. the chain's runs, gate and `--full` never pass it (docstring) | 4a904f190 | `defer_heavy` docstring and docs/TESTING.md; `test_the_option_refuses_full_impacted_and_tier_runs` | AGENT |
| Tests: five files deferred on cfr-2/sc-7-like plans, stay when changed, failed, or without the option; family test stays | 4a904f190, 1baa360f3 | `test_the_heavy_lean_wide_files_are_deferred_for_a_one_family_lean_change[cmp-s3a-cfr-2,sc-7,sn-b6d]` | AGENT |
| Before/after seconds for cfr-2, sc-7, ps-2a, sn-b6d | 1baa360f3 | `test_each_recorded_plan_keeps_these_map_seconds` | AGENT |
| Hook in manage-agents (defer-heavy.zsh, ledger) | n/a | n/a | EXTERNAL (row bs-sel-defer-broad-hook) |

## Spec re-read

- "valid only with --defer-heavy (same exclusions)" against the task's FIX 1: the option exits 2 alone, and with `--full`, `--impacted` or `--tier`.
- "EVERY reason that selected it is weak OR broad" against FIX 1: `all(weak_reason or lean_reason)`.
- "a Lean reason ('reads lean/...', 'runs Lean via lean/...', or the declarations/statements inventories)" against FIX 1. It is narrowed to Lean inputs and the named inventories, because FIX 2 says "a changed data file it reads" stays.
- "reads or runs at least BROAD_LEAN_SHARE ... of the lean/VE modules the map knows" against FIX 1: see `lean_shares`.
- The never-deferred list against FIX 2:
  - changed test: `stay`;
  - SMOKE and HISTORY_TEST: `stay`;
  - last failed: `keep`;
  - non-Lean strong reason: `deferral`;
  - own source: `names_changed_lean`, with `family_test` added.
- "deferred rows say which reason class" against FIX 3: `class`.
- "the printed line marks broad ones" against FIX 3: `(broad)`.
- The statement about who never passes the option against FIX 4: the `defer_heavy` docstring.

## Seeded bugs (Python; docs/infra/bs-sel-defer-broad/seeded-bugs.json)

14 seeded bugs, each planted alone in `tools/select_tests.py`. The named test was run alone each time. All 14 were caught (rc 1), then the file was restored. The bugs:

- B1: share `>=` changed to `>`.
- B2: `all(weak or Lean)` changed to `any`.
- B3 and B14: the own-source rule dropped (synthetic plan and recorded sc-7).
- B4: every executable reaches every module.
- B5: the directory pattern matches a sibling.
- B6: the inventories are not Lean.
- B7: `keep` ignored.
- B8: `--defer-broad` accepted alone.
- B9: the `(broad)` mark dropped.
- B10: a missing share counts as 1.0.
- B11: the family-name rule dropped.
- B12: any file under lean/ is Lean.
- B13: the family name matches inside a word.

## Checks run

- `uv run pytest -q tests/test_select_defer.py` -> `39 passed`.
- `uv run python tools/regen_generated.py --write` (once) rewrote docs/codemap. Besides this branch's docstring, it also fixed entries that were already stale on main: a removed `runmut.py` and a missing `test_speech_acts_acts0.py`.
- The final selected run: see the section below.
- There was no Lean change, so no lake build, `lean/audit.py` or trust_mutants (checklist 13a covers trusted Lean growth only). The full gate is run by the chain.
