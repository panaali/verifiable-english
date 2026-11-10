# arch-20261109-2: a module declares its own layer (PIPELINE-LIMITS L184, backlog arch-layer-policy-rows)

**Status:** built; the final selected run passed (215 of 568 test units, exit 0) on 809a9df2d. The full gate is left to the chain.
**What changed:** a Lean module (`-- ve-layer: <1-5> (<reason>)`) or a Python module or package
(`# ve-layer: <1-5> (<reason>)`) may declare its layer on its own first line. `tools/layer_policy.py` reads that
declaration before its name rules. Every check that reads layers reads it too. Every module's layer is unchanged.
**Open:** none. No DRI signature is needed (DELTA.md: none user-visible). Follow-ups: arch-layer-legacy-move
(181 names) and L185 (FOLLOW-UPS.md).

## Why

Every new family module used to get its layer by hand. Its name went into a set literal in `lean_layer`, or its
package name went into a `PYTHON` string, in `tools/layer_policy.py`. So every family branch edited the same few
lines. The architecture pass of 2026-11-09 counted the cost (`reviews/architecture-pass-20261109.md`; the batch
reuses its figures and did not re-measure them):

- Since Nov 5, 13 of 50 publications needed an agent sync.
- `tools/layer_policy.py` was a conflicting file in 6 of those 13.
- It changed in 7 of 49 merges.
- 4 of the 13 live branches edit it now: en-e3a, ci-3b, ap-5 and et-5.

**Hand rows at the base (de7fb946).** I counted them with `ast` on `git show main:tools/layer_policy.py`
(command in the build log; it reproduces with the same `ast` walk):
- `lean_layer` had 22 `if` rules, 16 set literals naming 90 modules (7 of them aggregation targets), and 16 name
  prefixes.
- `PYTHON` held 97 names in 5 strings: 8, 19, 19, 50 and 1 for layers 1 to 5.

## What was built (task items, each with its commit and test)

| Item | Delivered by | Test or evidence |
|---|---|---|
| 1. A Lean module declares its layer in its source, in one fixed, greppable form that the plain-layout header rule accepts; `lean_layer` reads it first and falls back to the name rules; no build, no service | 3f97ebe81, 596d83f63 (`layer_declaration`, `lean_declared`, `lean_layer`; the role rules split into `lean_fixed`, and the rest kept as `lean_name_layer`) | `LayerDeclarationTests::test_the_plain_layout_header_accepts_the_declaration`, `::test_a_lean_declaration_places_the_module_both_ways` |
| 2. The same for Python, read by `python_layer` before `PYTHON` | 3f97ebe81 (`python_row_declared`, `python_declared_rows`, `python_layer`, `python_rows`) | `::test_a_python_declaration_places_its_module_or_package`, `::test_a_declared_module_in_a_placed_package_splits_it` |
| 3. As strict as a set entry; the same answers on the current tree; malformed, unknown layer and no reason fail with the file named; a test for each | 3f97ebe81, 596d83f63 | `::test_a_malformed_declaration_is_refused`, `::test_an_unknown_layer_is_refused`, `::test_a_declaration_without_a_reason_is_refused`, `::test_a_declaration_off_the_first_line_is_refused`, `::test_a_declaration_cannot_override_a_role_rule`, `::test_a_lean_module_named_by_the_policy_cannot_also_declare`, `::test_python_check_refuses_each_bad_declaration_by_file`; same answers: `layers-before.txt` = `layers-after.txt`, `checks-before-after.txt` |
| End-to-end on a scratch tree: an upward import fails, then passes once the module declares the higher layer | a01d442a3 | `::test_a_new_lean_module_with_an_upward_import_passes_once_it_declares_its_layer`, `::test_a_new_python_module_with_an_upward_import_passes_once_it_declares_its_layer`, `::test_an_unmapped_lean_module_names_the_declaration` |
| 4. One reviewers' view | 3f97ebe81: `uv run python tools/layer_declarations.py` (one line per declaration: language, module, layer, reason, file; exits 1 on a refused one) | `::test_a_python_declaration_places_its_module_or_package` (listing and exit 1), `::test_the_repository_declarations_are_all_accepted` |
| 5. The violation messages name the declaration; ARCHITECTURE-LAYERS.md lines 23-27 updated; ROUTE-RECIPE.md if it names layer_policy.py; AGENTS.md not grown | 3f97ebe81, 596d83f63 (the messages "unmapped Lean module", "new outward Lean import", "unmapped Python module", the split-package outward import, the import-linter hint and the hook's three messages); a01d442a3 and 596d83f63 (docs) | the message asserts in the tests above, `test_split_package_init_import_is_checked`, `tests/test_precommit_hook.py::test_staged_python_layer_declaration_classifies_the_module`, `::test_staged_lean_layer_declaration_classifies_the_module`. `docs/ROUTE-RECIPE.md` does not name `layer_policy.py` (grep: only "operational policy" at line 17), so it is unchanged. AGENTS.md is unchanged. |
| Do not move the legacy names; set literals and `PYTHON` strings byte-identical | No set literal and no `PYTHON` string changed (`git diff main...HEAD -- tools/layer_policy.py`) | the four live branches merge with HEAD: `git merge-tree --write-tree HEAD <branch>` exits 0 for ap-5, ci-3b and et-5. en-e3a conflicts on `tools/layer_policy.py` exactly as it already does with main (main's `Rights.Run` comment line against en-e3a's insert); none of this batch's lines are in the hunk |
| FOLLOW-UPS note with the count of names that would move | 809a9df2d, `FOLLOW-UPS.md` | 84 Lean names (`layer_policy.lean_named()`) + 97 `PYTHON` names = 181 |
| Never weaken a check; no layer changes; `tools/lean-layer-exceptions.json` keeps its entries | `tools/lean-layer-exceptions.json` and `tools/layer-exceptions.json` are not in the diff | `layers-before.txt` = `layers-after.txt` (1001 modules, sha256 c664d34c…); `.importlinter` sha256 unchanged (0acb98b0…); `check_lean_imports.py` "Lean layer graph kept (812 modules, 18 reviewed legacy edges)" before and after |
| No in-module declaration added to a product module (a worked example was optional) | none added: `tools/layer_declarations.py` prints "0 in-module layer declarations" (`checks-before-after.txt`) | the worked examples live in the docs and in the scratch-tree tests, so no Lean file changed and no build, audit or trust sweep was needed |

### Two design choices

- **Where the declaration goes: the first line only.** A Lean `-- ...` comment is a full-line comment, which the
  plain-layout header allows (PLAIN_LAYOUT). A Python `# ...` line sits before the module docstring. Keeping it to
  the first line means the reader parses no Lean or Python syntax (build checklist 11). Any comment or doc line
  elsewhere that looks like a declaration is refused, naming the file and line. That includes the docstring form
  the task gave as an example, `ve-layer: 4 (...)` inside `/-! -/`. Code such as `VE_LAYER = 4` is not read as a
  declaration (`test_valid_declarations_are_read`).
- **What a declaration may not override.** It is refused when a role rule fixes the module's layer, even at the same
  layer:
  - Lean (`lean_fixed`): aggregation and audit targets are layer 5. Entry points, `*.Run`, `VE.Route.MeteredRun`,
    `VE.Service.*`, `ResponseShape` and `ResponseShape.*` are layer 4.
  - Python: the app areas are layer 5, and a root package has no layer.

  It is also refused when the policy already names the module one by one (one owner): a Lean set entry or `==` rule,
  or a `PYTHON` row.

  A declaration may override the prefix rules (for example `VE.Commands.*` at 3) in either direction, as the set
  entries do today.

### Readers of the layers

I found the readers by searching for `lean_layer`, `python_layer` and `PYTHON_MODULES`:

- `tools/check_lean_imports.py`: computes each module's layer once from the tree it checks.
- `tools/check_python_layers.py`: the rows, the split packages and the generated contract include the declared rows.
- `tools/hooks/precommit.py`: reads declarations from the staged index, not the snapshot.
- `tools/select_tests.py`: a change to the declaration line alone now adds the Python layer check. Before, a
  comment-only edit skipped it.
- `layer_policy.source_layer`: a refused declaration counts as an unknown path, so the full run is selected.

`tests/test_trust_mutants.py::test_the_plan_only_argument_still_holds` now derives `derived` from the names that
`check_lean_imports` imports. `tools/trust_mutants.py`'s PLAN_ONLY argument quotes the new import line.

## Coordination

Files I touched: tools/layer_policy.py, tools/check_lean_imports.py, tools/check_python_layers.py,
tools/hooks/precommit.py, tools/hooks/README.md, tools/select_tests.py, tools/layer_declarations.py (new),
tools/test_layer_policy.py, tools/trust_mutants.py (comment only), tests/test_precommit_hook.py,
tests/test_trust_mutants.py, docs/ARCHITECTURE-LAYERS.md, docs/codemap/** (generated) and this folder.

I compared them with `git diff --name-only main...<branch>` for every `feature/*`, `infra/*`, `lean-first/*` and
`foundation/*` branch:

- **tools/layer_policy.py:** ap-5, ci-3b, en-e3a and et-5. This overlap was expected; see the merge-tree row above.
- **docs/ARCHITECTURE-LAYERS.md:** et-5 edits table line 19. This batch edits lines 26-27 and the new section, so
  line 22 stays unchanged between the two edits and the merge is clean.
- **tools/select_tests.py and tests/test_select_tests.py:** foundation/me-1 and infra/eff-20261020-1-impl. Neither
  is in flight (6004 and 4572 commits behind main, last commits Oct 15 and Oct 20).
- **tools/trust_mutants.py:** infra/tm-orphans edits other hunks. `git merge-tree HEAD infra/tm-orphans` exits 0.

## Evidence (saved; D4)

- `layers-before.txt` and `layers-after.txt`: every Lean and Python module of the final tree with its layer.
  - The before list uses the base policy (`layer_list.py --policy-at de7fb946`).
  - The after list uses the head policy.
  - The two are byte-identical: `cmp` exits 0; sha256 c664d34c99890d01382da410bf5437401f9f4546ef8951541ccbf658a26832c7.
  - 812 Lean modules (42, 460, 105, 198 and 7 in layers 1 to 5); 189 Python modules (19, 19, 31, 84 and 35, plus
    `ve` with no layer).
- `checks-before-after.txt`: the output of `check_lean_imports.py` and `check_python_layers.py` on the base code and
  on the final code (identical), the `.importlinter` hash and the `layer_declarations.py` listing.
- `mutants.json` and `mutants-result.json`: the seeded bugs below
  (`uv run python tools/mutants.py docs/infra/arch-20261109-2/mutants.json --evidence …`, 12/12 killed, exit 0).
- No `evidence.toml`. `tools/batch_evidence.py` asks for `[ab]` only when `lean/` or `ve/` changes, and neither
  did. Its `[gate]` file would be the chain's gate, which runs after this report.
- Commits (`git log --no-merges main..HEAD` at 809a9df2d, before this report): d48d3e863, 3f97ebe81, a01d442a3,
  596d83f63, f6082aace, 926671dfd, 809a9df2d.

## Seeded bugs (Python, the only product language changed)

`tools/mutants.py` applied each seeded bug, ran its tests (the tests passed on the unmutated file first), required
a named test to FAIL, and restored the file byte for byte (`mutants-result.json`). "Tests" below are in
`tools/test_layer_policy.py::LayerDeclarationTests` unless named otherwise.

| Id | File | Bug | Failing test |
|---|---|---|---|
| Sa1 | tools/layer_policy.py | (a) `lean_layer` ignores the declaration | `test_a_lean_declaration_places_the_module_both_ways`, `test_a_new_lean_module_with_an_upward_import_passes_once_it_declares_its_layer` |
| Sa2 | tools/layer_policy.py | (a) `python_layer` ignores the declared rows | `test_a_python_declaration_places_its_module_or_package` |
| Sb | tools/layer_policy.py | (b) a declaration with no reason is accepted | `test_a_declaration_without_a_reason_is_refused` |
| Sc1 | tools/layer_policy.py | (c) a Lean declaration overrides a role rule | `test_a_declaration_cannot_override_a_role_rule` |
| Sc2 | tools/layer_policy.py | (c) a Python declaration in an app area is ignored instead of refused | `test_a_declaration_cannot_override_a_role_rule` |
| Sd | tools/layer_policy.py | a Lean module the policy names may also declare (two owners) | `test_a_lean_module_named_by_the_policy_cannot_also_declare` |
| Se | tools/layer_policy.py | a declaration off the first line is ignored | `test_a_declaration_off_the_first_line_is_refused` |
| Sf | tools/layer_policy.py | code starting with `ve_layer` is read as a declaration | `test_valid_declarations_are_read` |
| Sg | tools/check_lean_imports.py | the Lean check reads declarations from this checkout, not the tree it checks | `test_a_new_lean_module_with_an_upward_import_passes_once_it_declares_its_layer`, `test_an_unmapped_lean_module_names_the_declaration` |
| Sh | tools/check_python_layers.py | the contract leaves declared rows out of their layer | `test_a_new_python_module_with_an_upward_import_passes_once_it_declares_its_layer` |
| Si | tools/hooks/precommit.py | the hook ignores a staged module's declaration | `tests/test_precommit_hook.py::test_staged_python_layer_declaration_classifies_the_module` |
| Sj | tools/select_tests.py | a declaration-only change skips the Python layer check | `test_a_declaration_change_runs_the_python_layer_check` |

## Checks run, and what was not run

| Check | Result |
|---|---|
| Iterating | Ran only the touched tests: `tools/test_layer_policy.py` (all of it), `tests/test_precommit_hook.py` (all 62 before my two were added, then the layer subset), `tests/test_hang_guards.py`, `tests/test_trust_mutants.py::test_the_plan_only_argument_still_holds`, and both layer checks. All passed. |
| `uv run python tools/regen_generated.py --write` (once) | Rewrote only the advisory code map; the other 37 entries were up to date (`--check` before it). |
| Final selected run | `MAC_PYTEST_NO_DEFER=1 zsh …/mac-pytest.sh --select -- --base de7fb946 --run` on the clean, committed 809a9df2d: 215/568 units in 5 cloud shards, exit 0, 2268 s. It included `check_python_layers.py`, `check_lean_imports.py`, `check_rust_deps.py` and `tools/test_layer_policy.py`. |
| Lean build, `lean/audit.py`, trust_mutants | Not run: no Lean file changed. light-lane.py printed NOT only because of the 2002 lines of saved layer lists; there is no trusted Lean to mutate. |
| Full gate | Not run by me; the chain runs it on this HEAD. |

Pre-existing red tests on main (`main-known-red.txt`): two in `tests/test_lean_service.py` and one in
`tests/test_readings_defaults_rd8_report.py`. Neither file was touched or selected here.

Spec re-read:
- The task file's items 1-5 and its "Do NOT move", "Never weaken" and "Tests" paragraphs, against
  `/home/seyran/code/manage-agents/prompts/arch-20261109-2-task.txt`.
- PLAIN_LAYOUT, against `tools/check_lean_imports.py:19-21`.

## Self-review against BUILDER-CHECKLIST

| Item | Result | Evidence |
|---|---|---|
| 1. Lean answer typed and contained | N.A. | No Lean answer is read; tooling only. |
| 2. Deliverables built, no rule broken | PASS | The task-item table above. No set literal or `PYTHON` string moved; no new permanent report test (the layer lists are saved evidence, not a test). |
| 3. Tests can fail | PASS | 12 seeded bugs, 12 killed (`mutants-result.json`). |
| 4. Same answers on valid input | PASS | `layers-before.txt` = `layers-after.txt`; `checks-before-after.txt`. |
| 5. R8 binding | N.A. | No relayed answer. |
| 6. Gate evidence matches HEAD | PASS for the selected run | 809a9df2d, clean tree. Only this report (a docs `.md`) follows it. The full gate is the chain's. |
| 7. No unsigned item | PASS | DELTA.md has no rows; none user-visible. |
| 8. Every user-visible change in DELTA | PASS | No product output changed (DELTA.md); the developer-facing check messages are listed there. |
| 9. Selection finds the tests | PASS | `test_a_declaration_change_runs_the_python_layer_check`; seeded bug Sj. |
| 10. Lean statements | N.A. | No Lean changed. |
| 11. Budgets and limits | N.A. | No budgeted operation. |
| 12. CPU and memory | PASS | `check_lean_imports.py` reads each module's layer once (one file read per module); it ran in 2.4 s before, and its output after is identical. The test suite has no timing assertions. |
| 13. Test-removed trailers | N.A. | No test removed or renamed; I only added assertions to `test_split_package_init_import_is_checked` and `test_ledger_edges_must_exist_and_point_outward`. |
| 14. Both directions, cited claims, spec re-read | PASS | Each refusal test has its accepting counterpart (for example `test_valid_declarations_are_read` and `test_a_lean_module_named_by_the_policy_cannot_also_declare`, whose last assertion accepts an unnamed module). Claims cite the files above. |
| 15. Overclaim, silent cut, new checks can fail, limits | PASS | Universal claims ("every layer unchanged", "byte-identical") cite `cmp` and the sha256 values. No deliverable was cut; the worked example was optional. Each new check has a seeded bug. N.A. for limits. |

SELF-REVIEW: 0 A, 5 B, 9 C; fixed 14

- All 5 B findings fixed in 596d83f63: Lean one owner; look-alikes only in comment and doc lines; the split-package
  message names the declaration; the trust_mutants guard derived from the real imports; evidence computed on one
  tree.
- All 9 C findings fixed or documented: strict UTF-8 in the hook; refusals deduplicated by message; app-area
  selection prefixes; the hint only on a broken contract; docstring names; the role list in the docs and the
  audit-word note; balanced parentheses in a reason; the shebang limit documented; Python end-to-end refusals
  through `problems`.
