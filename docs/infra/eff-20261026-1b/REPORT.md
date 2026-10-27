No DRI signature is reserved, and nothing stops this item. It changes Python tooling only, and trust is +0. There is no user-visible delta, so there is no DELTA.md.

# eff-20261026-1b: `tools/trust_mutants.py --classes`, built

The DRI decided to build this despite eff-20261026-1's stop rule (manage-agents `reviews/dri-decisions-20261027-eff-20261026-1.md`, item 1, narrowed). The flag is opt-in. With no flag, the plan, the verdict rules and `--rescore` work as on main. The tool stays builder and reviewer evidence only: no gate, merge train or nightly reads it.

## What was built

Only `tools/trust_mutants.py` (one owner) and its tests changed. The change is eff-20261026-1's `prototype.patch`, merged by hand into speed-tmchecks' tool (d06e9a2cd, 85fdcbf1d):

1. **`--classes LIST`**, comma-separated. `trusted` is the default and is today's plan. A name may be one of trust_map's own class names. Those are `SELECTABLE`, read from `trust_map.CLASSES` minus the classes `trust_map.KIND_CLASSES` gives to theorems and checks, so there is no second copy. `all` picks every class but P and T, plus every trusted declaration. `chosen` is the one rule. A theorem, a proof helper (P) or a check (T) is never selected. An unknown or empty name exits 2 and quotes the list. `all,X` is written as `all`.
2. **`inputs`**: the list is one more key in `options`. The `inputs` structure and `carry()` are unchanged. `previous()` already treats `options` as fixed, so a different list is a full run in both modes ("its inputs differ (options)"). This holds even when the two lists select the very same mutants.
3. **Each mutant records** `trust_class` (trust_map's class, with " tied" added for a tied one) and `trusted`. SURVIVOR, UNKNOWN and NOT RUN lines show `(<class>)`, with ", trusted" added when R16 counts the declaration. One summary line per class counts its verdicts, and the JSON gains `classes` and `class_counts`.
4. **Docs.** The tool's docstring is the one statement of what `--classes` selects and why. The new section of `docs/TESTING.md` summarises it and points back to the docstring.

Note: the output lines and the JSON rows now carry the class even with no flag, since item 3 asks for it. One pre-existing test pinned the old line text and was updated (`test_a_guard_over_the_empty_list_leaves_survivors`). No other reader parses those lines: I searched `tests/`, `tools/`, `docs/speed` and me-12a's tools.

## Evidence

**The default plan is today's.** For the in-process check, `plan()` from main's tool and the new default `plan()` were run on this tree. The rows were equal field for field, ignoring the two new fields, over two bases:
- `HEAD~40`: 2,839 mutants;
- `7855620f3`: 2,482 mutants.

Under `all` the same bases give 6,331 and 5,022 mutants. In both, the trusted part equals the default as a multiset.

**Real-tree check** (df-1ad `b8f32f8f`, base `7855620f3`, `--jobs 6 --max-mutants 1000`, detached scratch worktree, since removed). `python3 docs/infra/eff-20261026-1b/compare.py` exits 0. It pins the HEAD, base, options and counts itself, and prints:
"default 80 and all 114 mutants equal the saved sweeps; all's 80 trusted ones equal the default's; times 3229 s and 3270 s; 0 problems".
- The default sweep matches eff-20261026-1's `cost/df-1ad-default.json` exactly: the same ids, mutants and verdicts (55 KILLED, 4 SURVIVOR, 21 UNKNOWN).
- The `--classes all` sweep also matches the prototype's saved `cost/df-1ad-all.json` exactly (114 mutants). Its trusted mutants and their verdicts equal the default sweep's.
- By class: C has 14 KILLED, 1 SURVIVOR and 4 UNKNOWN. G[R] has 3 KILLED. Tied G[V] has 10 KILLED and 2 SURVIVOR. D[V] (trusted) and G[V] (trusted) match the default.

**Times.** Default 3,229 s, `--classes all` 3,270 s. These are the tool's own `seconds`. Both runs went through `mac-pytest.sh --trustmut`, but both Mac pytest slots were busy for the full 600-s wait. The script then fell back to the VM, by its own rule, at VM load 22–45 of 32. The scratch tree had no `lean/.lake` and no shared build (`lean-prep.sh` restored none), so each sweep's control build compiled the whole tree. That dominates both times, so they are not comparable with the Mac's 341 s and 510 s. The logs are in `cost/`. There are only these 2 sweeps, one after the other, and only one whole-tree Lean build ran at a time. No test asserts a time.

**`mac-pytest.sh --trustmut` passes `--classes` through unchanged.** `--classes all` falls into neither of the script's argument cases. `--classes=all` is split into `--classes all`. The log line "trust_mutants … --classes all --json ../tm-out.json" and the JSON's `"classes": ["all"]` show it arriving.

## Tests (tests/test_trust_mutants.py; hermetic: tmp_path and a tiny Lean package `CLASSED`)

The package has one D[R] limit (`small`), one C definition (`evens`), one P helper (`double`), a theorem, and one unclassified (trusted) definition (`twice`).

- `test_with_no_flag_the_plan_selects_exactly_the_trusted_definitions`: the default plan equals the plan for `trusted`. Its declarations are exactly the ones `trust_map.walk` counts as trusted.
- `test_classes_all_adds_the_untrusted_definitions_and_keeps_the_default`: `all` adds `small` and `evens`, and its trusted mutants equal the default's. A class name picks that class alone.
- `test_a_theorem_proof_helper_or_check_is_never_selected`: covers `all`, every selectable name, and `trusted` with them.
- `test_an_unknown_class_name_is_refused[...]`: P, T, unknown and empty names give exit 2 and no JSON.
- `test_classes_names_are_read_from_trust_map`.
- `test_classes_all_mutates_a_reject_only_definition_and_names_each_class`: a real run in which `small`'s mutants are KILLED. `(C)` appears on the survivors' lines, and the JSON holds `classes`, `trust_class`, `trusted` and `class_counts`.
- `test_a_default_run_records_its_selection`.
- `test_rescore_carries_only_across_the_same_classes`: under the same list, mode is "identical" and every verdict is reused. A different list that selects the same mutants is a full run.
- `test_any_changed_input_but_checks_gives_a_full_run[classes]`: speed-tmchecks' table, with a check-only change beside it. speed-tmchecks' own rescore and carry tests pass unchanged.

The DRI's condition is that the tests pinning the no-flag plan, keeping theorems and checks out, and refusing a carry across `--classes` stay selected. They do: `select_tests.py --paths tools/trust_mutants.py` selects the whole of `tests/test_trust_mutants.py` (the tool is imported, named and read).

Selected tests: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` at `add79102e` ran on ve-mac-1 and gave 343 passed, 1 failed. The failure was `test_a_guard_over_the_empty_list_leaves_survivors`, which pinned the line text without the class. It was fixed in `3915a730e`, and that test plus `test_max_mutants_lists_the_rest_as_not_run` then passed (3 passed). No test from `main-known-red.txt` came up. As directed, I did not run the full gate myself.

## Seeded bugs

Python is the only language changed. The bugs are committed as `docs/infra/eff-20261026-1b/mutants.json` and run by `tools/mutants.py`. Its baseline passes, and the results are in `mutants-evidence.json`: 7 of 7 killed. Each one is in `tools/trust_mutants.py`:

| Id | Bug | Killed by |
| --- | --- | --- |
| C1 | the default selection widened (`"trusted"` also picks every selectable class) | `test_with_no_flag_the_plan_selects_exactly_the_trusted_definitions` |
| C2 | P and T selectable, so a theorem or proof helper is selected under `--classes all` | `test_a_theorem_proof_helper_or_check_is_never_selected` |
| C3 | `--classes` missing from `inputs` | `test_any_changed_input_but_checks_gives_a_full_run[classes]`, `test_rescore_carries_only_across_the_same_classes` |
| C4 | the carry ignores the classes (`options` not fixed in `previous`, so a check-only change carries across another list) | the same two |
| C5 | SURVIVOR and UNKNOWN lines without the class | `test_classes_all_mutates_a_reject_only_definition_and_names_each_class` |
| C6 | an unknown class name accepted | `test_an_unknown_class_name_is_refused[P]`, `[X]` |
| C7 | every mutant recorded as trusted | `test_classes_all_adds_the_untrusted_definitions_and_keeps_the_default`, `…names_each_class` |

The evidence check `docs/infra/eff-20261026-1b/compare.py` was seeded too. One trusted mutant's `raw_status` in `cost/df-1ad-all.json` was changed from KILLED to SURVIVOR. The check then exits 1 with "the mutants or verdicts differ" and "its trusted mutants and verdicts are not the default sweep's". The file was then restored.

## Orchestrator lines (for the .new procedure; I did not edit manage-agents)

- **prompts/build-checklist.txt 13a**, appended: "An item that adds or changes Lean decoders, admission checks or limits (trust_map classes other than trusted, P and T) also runs the sweep with `--classes all` on its own changes (its own `--json docs/<batch>/trust-mutants-all.json`). Every SURVIVOR there gets a killing check or fixture, or an `--allow` reason (one reason may cover equivalent mutants). UNKNOWN there is reported, not required (a `mutual` block gives no kill; pytest-only fixtures are L93's class)." The `--json` clause is my addition: without it the second sweep overwrites the first sweep's evidence file.
- **BUILDER-CHECKLIST.md item 3**, appended to the trust_mutants bullet: "An item that adds or changes Lean decoders, admission checks or limits also runs it with `--classes all --json docs/<batch>/trust-mutants-all.json`: every SURVIVOR there gets a killing check or fixture, or an `--allow` reason (one may cover equivalent mutants); UNKNOWN there is reported, not required (2026-10-27 DRI, eff-20261026-1b)."
- **Review prompt**: "Rerun trust_mutants with `--classes all` before planting hand mutants; plant only forms it does not write."

## Follow-ups (not built)

1. L102's next step would carry verdicts across a `tools/trust-classes.json` edit when the mutant list is unchanged. That is now no longer enough: under `--classes`, the table decides both the selection and each mutant's `trust_class` and `trusted`. That carry would also have to compare those two fields per mutant.
2. eff-20261026-1's follow-ups 2 (mutual blocks give no kill), 3 (forms beyond OPERATORS) and 4 (pytest-only fixtures, L93) stand.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean route, response or schema changed.
2. PASS: items 1–4 and the tests are built. The real-tree check stayed within 2 sweeps. No product code changed in Lean, Rust or `ve/`, and no generated file changed (`regen_generated.py --check` reports 33 entries, all current).
3. PASS: seeded bugs C1–C7 are each killed (`mutants-evidence.json`), and `compare.py`'s seeded check exits 1. 13a's trusted-growth sweep is N.A., since no Lean changed.
4. N.A.: no Python, Lean or Rust checker path changed.
5. N.A.: no relayed field.
6. N.A.: the chain runs the gate on the final HEAD.
7. PASS: no DELTA row, no reserved signature, trust +0.
8. PASS: no user-visible change. This is a developer tool's opt-in flag, plus a class label on its evidence lines.
9. PASS: `select_tests.py --paths tools/trust_mutants.py` selects `tests/test_trust_mutants.py` whole.
10. N.A.: no Lean statement.
11. PASS: an unknown `--classes` name fails closed (exit 2, `test_an_unknown_class_name_is_refused`). A different list never reuses a verdict (`test_rescore_carries_only_across_the_same_classes`).
12. PASS: with no flag the plan is the same list, and `chosen` adds one membership test per declaration. The real-tree times above are evidence only.
13. PASS: no test was removed or renamed. One assertion's expected line text gained the class.
