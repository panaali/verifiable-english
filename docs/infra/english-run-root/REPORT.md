# Build report: infra/english-run-root

## Delivery

`ve_english_run` now has root `EnglishRunMain`; it imports the `VE.English.Run`
library module and owns the unchanged `main` body. Every other executable root
is outside the library namespaces, checked against the complete lakefile by
`test_executable_roots_are_outside_library_modules`. The Python differential
harness runs the new entry file; `test_differential_harness_uses_executable_root`
guards that link. The service's existing generated namespace copy remains
generator-owned and passes `english_copy.py --check`.

The compiled statement dump reports **zero** theorem statements added, removed,
or changed. The trust table moves `main` from `VE/English/Run.lean` to
`EnglishRunMain.lean`: seven trusted lines moved, **zero net trust growth**.
`tools/trust_map.py --check` passes. `tools/trust_map.py --write` refreshed the
per-file baseline; the measured consolidation-plan row 7 changed from 666 to
673 removed lines because its selector now counts the standalone root. The
same ledger command refreshed row 6's previously stale reclassified count.
The checker pin remained byte-identical and `regen_generated.py --check` passed
all 23 entries.

## Acceptance and evidence

| Item | Owner | Delivery | Check |
|---|---|---|---|
| Distinct executable root; no other library/executable overlap | AGENT | `8133a1886` | `test_executable_roots_are_outside_library_modules`; `lake build` (884 jobs) |
| Harness and docs use the new root | AGENT | `8133a1886` | `test_differential_harness_uses_executable_root`; `tests/test_english_lean_route.py` |
| Generated copy, frozen inventory, declarations, audit, trust table, pins | AGENT | `8133a1886` plus follow-up baseline commit | `regen_generated.py --check` (23 entries); `trust_map.py --check`; `test_committed_ledger_names_real_declarations` |
| No behavior change | AGENT | `8133a1886` | `test_english_runner_bytes_match_base` (4 cases); six corpus payloads byte-identical in `evidence/english-output-diff.json`; `tests/test_lean_service.py` |
| Full release gate on committed final HEAD | AGENT | This pre-review round runs it once after the final commit | `gate-result.json` records its result; the chain also checks the new HEAD |

`DELTA.md` records no user-visible delta. No R1–R15 signature is claimed.
The saved six-case comparison records hashes of inputs, stdout, and stderr;
there is no permanent test of moving `git diff` or report commit counts (D4).

## Checks and seeded bugs

- `PATH=~/.elan/bin:$PATH lake build`: passed on this checkout.
- `uv run python tools/regen_generated.py --check`: passed, 23 entries.
- `uv run pytest tests/test_english_runner_root.py -q`: passed; six tests after the harness guard was added.
- Mac selected run from merge base: 374 units, with three failing files. The trust baseline and plan-row failures were fixed. The known Mac-only `test_the_whole_question_is_bounded_by_the_modes_deadline` passed on a serial VM rerun; all three exact failed tests passed together (3 passed).
- Mac selection for the two fix paths: 71 units, zero failures. The chain's first full gate of `049bb55a` built Lean and Rust and audited Lean, then failed one historical report test. This pre-review round corrects that test and runs the full gate on its final commit.

Seeded failures, each restored before the final build:

| Mutant file | Seeded bug | Failing test |
|---|---|---|
| `lean/EnglishRunMain.lean` | Replace stdin read with an empty string | `test_english_runner_bytes_match_base[empty_stdin]` |
| `lean/EnglishRunMain.lean` | Replace file read with an empty string | `test_english_runner_bytes_match_base[formula_file]` |
| `lean/EnglishRunMain.lean` | Return exit 0 on a malformed request | `test_english_runner_bytes_match_base[malformed_stdin]` |
| `conformance/english_lean.py` | Point the harness at the old runner path | `test_differential_harness_uses_executable_root` |
| `lean/lakefile.toml` | Point the executable back into the `VE` library | `test_executable_roots_are_outside_library_modules` raised `AssertionError: ve_english_run` when invoked directly; pytest's lakefile preflight would otherwise stop before this test |

`seeded-bugs.json` records the changed Lean and Python source paths and their
failing tests. All seeded changes were restored before this commit.

## Pre-review repair

Git lengthened a historical commit abbreviation from eight to nine digits
after new objects arrived. The existing RD-8 report test now compares saved
eight-digit prefixes with full Git object IDs. Its exact pytest case passes.

The relay mutation gate's allow-list had 128 paths that no longer matched
current genuine fixtures: 86 in readings-route and 42 in other routes'
historical report fields. Those paths were removed. Five accepted mutations
were assigned to the existing B0 content and F11 empty string classes, with
exact paths; a stale path still fails the gate. These allow-list changes do
not affect the English binary or its `DELTA.md`.

The selected Mac run reported the known Mac-only deadline failure in
`test_the_whole_question_is_bounded_by_the_modes_deadline`; the exact test
passed on the VM. Its other 287 test files passed. The generated-file check
passed all 23 entries, including the Lean statement, audit, frozen-source,
trust, and response-schema checks.

## Build checklist applicability

Items 1–12 and 15 concern parser contracts, response schemas, semantic
decisions, budgets, ledgers, and identity binding; this change adds none.
Item 13 is covered by the five seeded failures above. Item 14 is covered by
`tmp_path` in the file-input test and the repository's `HANG_TIMEOUT`; the
new fixtures make no network or model calls. Item 16 is covered by the
lakefile-wide root test and `regen_generated.py --check`. Item 17 is covered
by the zero-change statement dump and Lean audit. Items 18–19 have no new
theorem or use-case formalisation. Item 20 uses the saved byte comparison and
names all checks above; no live commit-list test was added. Item 21 is the
owner table above. Item 22 uses selected tests while iterating and one full
gate on the final committed HEAD; disk had 36 GiB available before it. Item 23 is
`DELTA.md` and the trust measurement, with no signature needed.

## Self-review against BUILDER-CHECKLIST

1. N.A. — No Lean answer schema or decoder changed.
2. PASS — `test_executable_roots_are_outside_library_modules`, `regen_generated.py --check`, and the acceptance table cover the root, generator, and pin directives.
3. PASS — Five seeded failures in the table above; each named test failed before restoration.
4. PASS — `test_english_runner_bytes_match_base` and `evidence/english-output-diff.json` compare the base and head bytes on valid and invalid English payloads; `tests/test_lean_service.py` passed.
5. N.A. — No relayed field, request binding, or input decoder changed.
6. PASS — `gate-result.json` records the clean committed HEAD's full release gate; `regen_generated.py --check` passed locally.
7. PASS — `DELTA.md` records no changed output; `tools/trust_map.py --check` reports zero net growth.
8. PASS — `evidence/english-output-diff.json` shows six identical output triples; `test_english_runner_bytes_match_base` pins four.
9. PASS — `select_tests.py --base f98183bf5f` selected 374/374 because the lakefile is project-wide; `test_english_runner_root.py` was selected and passed.
10. PASS — `tools/lean_statements.py` reported zero theorem statement changes; `lean/audit.py` and the generated check passed.
11. N.A. — No deadline, budget, or limit changed.
12. N.A. — No runtime logic changed; byte output and the focused Lean service tests passed.
