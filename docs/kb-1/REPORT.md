# KB-1 build report

Trust budget K +34 (DELTA row 2; R16 does not cover K growth): SIGNED by the DRI 2026-11-12 (reviews/dri-decisions-20261112-kb-1.md item 1), allowance recorded in `docs/trust-baseline.json` (3350e57cdf).
Status: deliverables (0) to (8) built and committed on `infra/kb-1`; trust_mutants exit 0; selected run: 2 failures (this branch's), fixed, rerun green.
What changed: `lean/VE/Kernel/Carry.lean` (verbatim), the kernel check in the gate and in regen, `--check` also ratchets verdict writers outside the kernel, `--out` refuses a total above the signed one, the per-kind table, the experimental import boundary, the CHECKED wording, AGENTS.md's exception.
Open: 14 untied kinds for the architect (listed below); `usecases/openai-preparedness/run.py --check` already fails on main (stale `results.json`, not this branch).
Kernel: 9,504 lines (= baseline), verdict writers outside the kernel 56 (= baseline).

SIZE: 291 product, 338 tests, 211 other hand-written lines (`git diff --numstat 35a9ba135f...HEAD`, generated files left out; tests include `lean/VE/Kernel/CarryChecks.lean`).

## Deliverables

| # | Task line | Where | Test or command |
|---|---|---|---|
| 0 | cherry-pick `d664812fec` | commit `6523b586f0` | `grep -c "What each token claims" docs/spec/kernel-boundary.md` = 1, `grep -c "were proved"` = 0; `uv run pytest -q tests/test_kernel_closure.py`: 35 passed |
| 1 | `lean/VE/Kernel/Carry.lean` = architect's file minus its last line; layer 1 (`"VE.Kernel."` in `tools/layer_policy.py`); `lean/VE.lean` import; audit entries (regen); K classes for Path, Row, Path.row, Path.Ran, shell, carry | `lean/VE/Kernel/Carry.lean`, `tools/trust-classes.json` | `diff <(head -n -1 …/architect/Carry.lean) lean/VE/Kernel/Carry.lean` empty; `lean/axioms.txt`: `shell_sound` depends on `[propext, Quot.sound]`; `python3 tools/check_lean_imports.py`: "Lean layer graph kept (865 modules …)" |
| 1+ | checks for the K definitions (trust_mutants kills only by a check) | `lean/VE/Kernel/CarryChecks.lean` (T classes) | `docs/kb-1/trust-mutants.json` |
| 2 | gate: `kernel_closure.py --check docs/kernel/closure-baseline.json` in the trust stage after the Lean build; registry `imports` built first; `--check` fails on a rise of writers outside the kernel with the asked message | `tools/gate.py` (stage "Kernel check"), `tools/kernel_closure.py` (`check_writers`, `build_imports`) | `tests/test_gate_trust.py::test_every_gate_runs_the_kernel_check_after_the_lean_build`, `tests/test_kernel_closure.py::test_the_check_fails_when_verdict_writers_outside_the_kernel_rise`, `::test_the_check_command_fails_on_kernel_growth_and_on_a_new_writer_outside`, `::test_measure_builds_the_registry_imports_before_the_lean_half` |
| 3 | `closure-baseline.json` generated: write `--out`, check `--check`, note on ALLOWANCES.md; the write refuses a total above "signed total:" | `tools/regen_generated.py` entry `kernel-closure` (fresh: `gate:Kernel check`), `tools/kernel_closure.py` (`signed_total`, `check_signed`) | `tests/test_kernel_closure.py::test_the_write_refuses_a_kernel_total_above_the_signed_one`; `uv run python tools/regen_generated.py --check --only kernel-closure`: "PASS: kernel 9504 <= 9504", "PASS: verdict writers outside the kernel 56 <= 56" |
| 4 | per-kind table: `kinds` on every kernel path, `untied_kinds` | `tools/kernel-paths.json`, `tools/kernel_closure.py` (`kind_problems`) | `tests/test_kernel_closure.py::test_every_case_kind_of_a_kernel_runner_has_an_entry_and_every_entry_a_kind`, `::test_each_kind_theorem_fixes_its_kind_and_no_theorem_states_an_untied_kind`, `::test_the_kind_table_problems_are_found_before_any_lean_runs` |
| 5 | experimental boundary: service-reachable imports of `VE.Experimental.*`; `Expires: YYYY-MM-DD` in the first docstring, not passed | `tools/check_lean_imports.py` (`experimental_imports`, `expiry_problems`, `lean_modules(root)`) | `tests/test_lean_experimental_boundary.py` (8 tests, tmp_path trees, injected date) |
| 6 | ALLOWANCES.md: unchanged (kernel_lines did not rise) | — | regen log: "kernel (distinct lines of every path of tier kernel): 9504" |
| 7 | CHECKED wording | `ve/document/cli.py` (`CHECKED_MEANS`, the `check` help), README.md (quotes it) | `uv run python -m ve document check --help`; `tests/test_kernel_closure.py::test_the_readme_quotes_what_checked_means` |
| 8 | AGENTS.md exception after "Python never recomputes it." | AGENTS.md, 5,972 bytes (was 5,978), 90 lines | `uv run pytest -q tests/test_repo_map.py` (in the 300-test run below) |

Deliverable (2), a choice: the registry's `imports` are built by `tools/kernel_closure.py` itself (`build_imports`,
before `lake env lean`), not by a separate gate command, so the gate, regen's write and check, and a hand run all
build them from the one registry (one owner). The gate's stage runs that tool.

Deliverable (4), what the regular expression reads (`tests/test_kernel_closure.py` `KIND_SOURCES`): the four files the
task names and the runners the kernel paths' subjects dispatch through, where the kinds are actually compared:
`lean/VE/Route/Wire.lean`, `lean/VE/Core/Wire.lean`, `lean/VE/Core/Layers.lean` (route), `lean/VE/Norms/Plain.lean`
(norms), `lean/VE/Route/MeteredRun.lean` (metered). `lean/VE/CertificateWire.lean` compares no kind literal and its
path is a candidate; the test asserts both, so a promotion makes its table required.

### Untied kinds (`untied_kinds`, the architect's next input)

Verdict-bearing kinds of kernel paths that no theorem in `lean/statements.txt` states on the path's subjects
(checked by `test_each_kind_theorem_fixes_its_kind_and_no_theorem_states_an_untied_kind`):

- route `admission` (`admitted`, VE.Route.Run.runAdmit), route `bundle` (`checked`, VE.Definitions.Bundle.runBundle);
- route `certificate`, `countermodel`, `evaluate` on the closureNary family (VE.Core.Wire.run, VE.Core.Layers.run):
  the listed theorems fix the fol, closure and order families only; `VE.Core.Wire.run_certificate_acceptance` is
  about Core.Wire.run, not about a subject (`near`);
- norms `certificate`, `countermodel`, `evaluate` (Norms.Plain.run, already `uncovered`);
- softNorms `soft-rule`, `soft-rules` (well-formedness admissions), `soft-pairs`, `soft-certificate` (near:
  VE.SoftNorms.Wire.soft_wire_acceptance), `soft-conflict` (near: soft_wire_conflict_sound, soft_wire_conflict_witness_sound);
- metered `non-vacuity` (already `uncovered`).

Mapped to a theorem: route evaluate/countermodel/certificate (route_fol_*), norms admission, norms-certificate,
norms-conflict, softNorms admission, soft-elaborate (`soft_wire_elaborate` fixes the kind and states its
`background` and `premises` only; its `residualStatus` CHECKED stays `uncovered` through runSoftKind), metered
evaluate-budgeted. Nonverdict: route background, dependency-order, label; norms norms-elaborate (its `fragment` is
a syntactic class), background.

### CHECKED wording (7): places and pinned strings

`grep -rn "CHECKED" README.md docs/*.md ve/*.py | grep -iv test` finds status logic and constants only
(`ve/discourse.py:91`, `ve/readings_*`, `ve/readings_s2_english.py` CHECKED_ALONE and the UNCHECKED texts); none
says what a unit's CHECKED status means, and neither do docs/README.md, docs/natural-view.md or the `ve document
check` help. So the wording was added where a reader of the check meets it (its help) and quoted in README.md; no
existing string changed. Pinned strings for kb-2a: none touched. `ve/document/render.py:183` "Checked reading: " is
a display prefix, not a meaning statement, and was left as it is.

## Seeded bugs (each restored; tree clean after each)

| # | File | Bug | Caught by |
|---|---|---|---|
| a | `lean/VE/Route/MeteredWire.lean` | a 3-line helper `seededId` that `EvaluationAnswer` (the `metered` spec) mentions | `uv run python tools/kernel_closure.py --check docs/kernel/closure-baseline.json` (the gate's stage): exit 1, "FAIL: the kernel grew from 9504 to 9507 lines" |
| b | `lean/VE/Service/DocumentView.lean` | `def leak : String := "CHECKED"` | same run: "FAIL: verdict writers outside the kernel rose from 56 to 57: VE.Service.Document.leak" |
| c | `tools/kernel_closure.py` | `covered()` counts overlaps twice | `tests/test_kernel_closure.py::test_overlapping_ranges_are_counted_once` |
| d1 | `tools/check_lean_imports.py` | no transitive walk | `tests/test_lean_experimental_boundary.py::test_a_module_the_service_reaches_may_not_import_an_experimental_one` |
| d2 | `tools/check_lean_imports.py` | an expired date passes (`< date.min`) | `tests/test_lean_experimental_boundary.py::test_an_experimental_module_carries_an_expiry_date_not_yet_passed` |
| d3 | `tools/check_lean_imports.py` | two `Expires:` lines accepted | same test |
| e | `tools/kernel_closure.py` | writer ratchet allows +1 | `::test_the_check_fails_when_verdict_writers_outside_the_kernel_rise` |
| f | `tools/kernel_closure.py` | signed-total refusal allows +1 | `::test_the_write_refuses_a_kernel_total_above_the_signed_one` |
| g | `tools/kernel_closure.py` | a `kinds` theorem not of the path accepted | `::test_the_kind_table_problems_are_found_before_any_lean_runs` |
| h | `tools/kernel-paths.json` | softNorms `admission` entry dropped | `::test_every_case_kind_of_a_kernel_runner_has_an_entry_and_every_entry_a_kind` |
| i | `tools/gate.py` | the kernel check not run | `tests/test_gate_trust.py::test_every_gate_runs_the_kernel_check_after_the_lean_build` |
| j | `ve/document/cli.py` | the help's wording drifts from README's | `::test_the_readme_quotes_what_checked_means` |
| k (Lean) | `lean/VE/Kernel/Carry.lean` | `Path.row` answers `.ok case` | `lake build VE.Kernel.Carry`: "Carry.lean:49:6: Tactic `rfl` failed" (shell_provenance) |
| l | `tools/kernel_closure.py` | review F2: `--out` skips the writer ratchet | `::test_the_write_refuses_more_verdict_writers_outside_than_the_file_it_replaces` |
| m | `tools/check_lean_imports.py` | review F3: `first_docstring` does not skip string literals | `tests/test_lean_experimental_boundary.py::test_the_expiry_rule_reads_the_first_actual_doc_comment_not_text_inside_strings_or_comments` |
| n | `tools/check_lean_imports.py` | review F3: comments do not nest (replanted after F4 in `_block_end`, which closes the docstring) | `tests/test_lean_experimental_boundary.py::test_a_plain_header_before_the_docstring_is_read_and_its_date_decides` |
| o | `tools/check_lean_imports.py` | review F4: `first_docstring` put back to the lexing reader of b65639b0bd | `::test_the_review_f4_layouts_with_an_expired_docstring_are_refused` (and 2 more of the file's tests) |
| p | `tools/check_lean_imports.py` | review F4: `first_docstring` searches past code for a doc comment | `::test_a_module_passes_only_on_a_docstring_with_no_code_in_front_of_it` (and 2 more) |

Bugs a and b were planted together and checked in one run (each message names its own cause). Bugs c to j were run
one at a time, each with its one test (`1 failed` each); so were l to n (fix round) and o, p and n again (F4 round:
o and p each fail 3 of the file's 8 tests, n 1). Rust: no product code changed.
The same list, with file and test keys, is committed as `docs/kb-1/seeded-bugs.json` (pre-review [mutants] reads it).

## Fix rounds (reviews of 123405eeb6, d01672d8e7 and the recheck of b65639b0bd)

- **F1 (A)**: fixed in eeee089f5a and d01672d8e7 (DELTA row 2 reads exactly the decision's wording; REPORT no longer says the signature is needed). PROBE F1 exits 0.
- **F2 (B)**: `tools/kernel_closure.py --out` now also runs the writer ratchet against the file it replaces and refuses (`REFUSED: verdict writers outside the kernel rose from A to B: <names>`, file left as it was) before writing; a first write (no file) has no bound. The regen entry `kernel-closure` writes through the same command, so it inherits the refusal; the gate stage runs `--check`, which already ratcheted. Regression test `test_the_write_refuses_more_verdict_writers_outside_than_the_file_it_replaces` (also pins the regen entry's command). PROBE F2 passes.
- **F3 (B)**: at b65639b0bd, `tools/check_lean_imports.py::first_docstring` lexed the source by hand to skip string literals (raw ones too), character literals, `--` comments, `«…»` names and nested plain `/- -/` comments, failing closed on an unclosed string or comment. The recheck's F4 showed that claim was too strong (interpolations and `⟨'"'` defeated it); the lexer is gone since, see F4. Regression test `test_the_expiry_rule_reads_the_first_actual_doc_comment_not_text_inside_strings_or_comments` sweeps `/--` and `/-!`, each with the real docstring expired and missing, behind six hiding places. On the 866 Lean files of the tree it finds the same first docstring as before. PROBE F3 passes.
- **F4 (B)** (recheck of b65639b0bd): the class is a hand-written lexer of Lean code (FINDING-CLASSES row 7). Fixed by removing the lexer: `first_docstring` now takes the docstring only as the first command after the import header, read by `header` (split out of `imports`, the one header reader, already checked against the pinned `lean --deps` by `main`); any code before it (a string, a character literal, an interpolation, a definition) or a header outside the plain layout yields no docstring, so the module is refused. It never guesses where a string ends. On the 866 Lean files of the tree it agrees with the b65639b0bd reader on 810; the other 56 (`Serve.lean`, `VE/ParserContracts.lean`, ...) have code before their first doc comment, none is experimental. The refusal now reads "first docstring, before any code but `import` lines and comments, needs one line `Expires: YYYY-MM-DD`". Regression tests: `test_the_review_f4_layouts_with_an_expired_docstring_are_refused` (the probe's two layouts), the F3 test widened to eleven code hiding places (both F4 layouts among them) refused whatever the docstring says, a seeded 3,000-prefix fuzzer `test_a_module_passes_only_on_a_docstring_with_no_code_in_front_of_it` (a pass only when a plain header alone precedes the docstring), and `test_a_plain_header_before_the_docstring_is_read_and_its_date_decides` (no over-refusal; nested comments inside the docstring). PROBE F4 exits 1 before, 0 after.
- **[mutants] pre-review FAIL**: the Python seeds were only in this file; now also in `docs/kb-1/seeded-bugs.json`.

## Trust mutants

`zsh manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/kb-1/trust-mutants.json --test
lean/VE/Kernel/CarryChecks.lean` (ran on ve-cloud-2): 24 KILLED, 3 SURVIVOR, 5 UNKNOWN, 14 INVALID. The 8 left are
allowed in `docs/kb-1/trust-mutants-allow.json` (Path.Ran is a Prop over Json, which has no decidable equality: its
mutants break shell_provenance and ran_meaning; the other five are texts Lean refuses: no LE on Except, `[]` for an
Except, `[].map`). Rescored with `--allow … --rescore docs/kb-1/trust-mutants.json` (ve-cloud-3): exit 0, "24
KILLED, 0 SURVIVOR, 0 UNKNOWN, 14 INVALID, 8 ALLOWED, 0 NOT RUN". Light lane: NOT (`tools-local/light-lane.py
check`: trusted-core files changed).

## Acceptance: the five frozen keys

Run on this branch (log /tmp/kb1-keys.log, wait-bg):

- `usecases/anthropic-rsp/run.py --check`: rc 0, "110 / 126";
- `usecases/openai-preparedness/run.py --check`: rc 1, "results.json is out of date". Pre-existing on main: the
  harness's `metrics` read `coverage.json`, which main's 989862dbe1 (11-11 04:28) changed after `results.json` was
  last written (c5ca07a749, 11-11 02:50). Rewriting it here changes only `metrics` (CHECKED 344 -> 170, asserted
  222 -> 48) and keeps "230 / 239", the saved score; the file was restored, not committed (another item's);
- `usecases/safety-framework/run.py --check`: rc 0; `usecases/agent-policy/check.py base`: rc 0;
  `usecases/eligibility/run.py --no-write`: rc 0.

Kernel check: `regen_generated.py --check --only kernel-closure`: kernel 9,504 <= 9,504, writers outside 56 <= 56.

## Tests run

- While iterating: `tests/test_kernel_closure.py` (35 passed), `tests/test_lean_experimental_boundary.py` (4),
  `tests/test_gate_trust.py -k kernel_check` (1); `python3 tools/test_layer_policy.py` rc 0.
- Touched files' suites: `uv run pytest -q tests/test_regen_generated.py tests/test_document_split.py
  tests/test_repo_map.py tests/test_lean_default_build.py tests/test_gate_trust.py tests/test_gate_rerun.py
  tests/test_gate_integrity.py tests/test_lean_import_reader.py tests/test_kernel_closure.py
  tests/test_lean_experimental_boundary.py`: 300 passed.
- `uv run python tools/gate_collection.py --check --prebuilt`: 13 added, 0 refused, 0 stale, 0 malformed.
- Selected run on the committed HEAD `3932802d5b` (`MAC_PYTEST_NO_DEFER=1 zsh manage-agents/mac-pytest.sh --select -- --base
  $(git merge-base HEAD main) --run`, ran on ve-cloud-3, log /tmp/kb1-sel-run.log): exit 1, 540 units, 2 failed, both
  from this branch's additions: `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`
  (the two new Lean files read or build JSON: reasons added under `other_json` in `ve/assurance-manifest.json`, layout
  regenerated) and `tests/test_merge_tooling_evidence.py::test_the_generated_file_table_names_every_entry` (the
  `kernel-closure` row added to `docs/merge-tooling.md`). Rerun of those two ids (`mac-pytest.sh -- <ids>`): 2 passed;
  their two files in full: 162 passed. The fix is committed after the selected run, so the chain gate runs the tests.
- Not run: the full gate (the chain runs it on the final HEAD).

## Notes for the DRI

- The spec's candidate rows moved with main's code since kb-0 measured them (normDefaults, readingsRoute,
  discourse, document); the kernel rows did not. The spec's table now quotes the regenerated baseline, and says so.
- The route path counts the closureNary family's runners (Core.Wire.run, Core.Layers.run) as body inside the kernel,
  though no listed theorem covers that family; recorded as `untied_kinds` with `family`. Whether those runners
  should be `uncovered` is the architect's call (a tier/registry change, out of this item's scope).
- The CHECKED sentence says the translation "is shown with them"; today's `ve document check` shows each unit's
  reading, and the carried core cases arrive with KB-2a.
- `check_lean_imports.py`: a tree without `lean/lakefile.toml` (the layer tests' trees) does not require the two
  service roots, as its unbuilt-module rule already does; the repository's tree requires them
  (`test_the_repository_service_reaches_no_experimental_module`).

## Spec re-read

- `kernel_closure.py --check … runs where the trust budget check runs (same stage of tools/gate.py, after lake build)` against `tools/gate.py` (trust stage, after "Lean build").
- "FAIL: verdict writers outside the kernel rose from A to B: <the new names>" against `check_writers`' message.
- "the write refuses to raise kernel_lines above the 'signed total:' figure" against `check_signed` (`>`: equal passes).
- "every case kind its runner dispatches on … mapped to either {theorem} or {nonverdict: reason, at least 20 characters}" against `kind_problems` (`< 20` refused).
- "imports, directly or transitively … starts with VE.Experimental." and "`Expires: YYYY-MM-DD` in its first docstring or that date has passed" against `experimental_imports` (`is_experimental`: the name itself or with a dot) and `expiry_problems` (`expires < today`).
- Section 3 "Trust classes … = K; the theorems are P by kind" against `tools/trust-classes.json` and `trust_map.py --check` (theorems not listed).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer or schema changed (no service mode touched).
2. PASS: deliverables table above, each with its commit or test; `grep` of the diff: no Python copy of a Lean decision (the kinds test reads Lean literals as a cross-check only), no report test.
3. PASS: seeded bugs a to n (`docs/kb-1/seeded-bugs.json`); trust mutants exit 0 (`docs/kb-1/trust-mutants.json`).
4. N.A.: no Python/Lean/Rust answer path changed.
5. N.A.: no new field read from a Lean answer.
6. PASS (pending the chain): selected run on the committed HEAD, its 2 failures fixed and rerun (Tests run); the chain gates the final HEAD.
7. PASS: DELTA row 1 cites R1 with its test; row 2's K growth cites the DRI's signature (reviews/dri-decisions-20261112-kb-1.md item 1), as this report's first line does.
8. PASS: DELTA.md lists the help text and the trust delta; no service answer changes (no runner touched).
9. PASS: `uv run python tools/select_tests.py --base $(git merge-base HEAD main)` selects `tests/test_kernel_closure.py`, `tests/test_lean_experimental_boundary.py`, `tests/test_gate_trust.py`.
10. PASS: seeded bug k breaks `shell_provenance`; Carry.lean's statements are the architect's, verbatim.
11. PASS: `test_an_experimental_module_carries_an_expiry_date_not_yet_passed` injects the date; no sleeps or literal timeouts in the new tests.
12. N.A.: no product path runs more work (one extra gate stage; the tool already ran by hand).
13. PASS: no test removed or renamed; `tools/gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
14. PASS: opposite directions tested (writers fall/rise, signed at/above, kinds accepted/refused, boundary clean/violated, expiry today/passed).
15. PASS: universal words checked ("no service answer changes": no runner or schema file in the diff; "every kernel path": `test_every_case_kind_…`); every new check has a mutant (bugs c to j, trust mutants for the `#guard`s).
