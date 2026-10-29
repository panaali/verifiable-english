# gha-gate-shard loop recheck 1 fix, 2026-10-29

Status: F9 and F10 (both B) fixed; earlier A/B fixes remain in `FIX-20261029.md`.
Code HEAD: `f12aeca50`; this report is committed separately.
Changed: shared pytest selector coverage and contract evidence for every listed selector.
Open: F3 is a C follow-up (`{"lean": null}` shard identity), outside this A/B fix request.
DRI signature: none needed; no VE language, checker, wire, verdict, or trust-budget delta.

## Findings

| Finding | Fix | Regression test ID | Commit |
|---|---|---|---|
| F9 | Recognize a parameter suffix before any `::` inside its ID, and use the shared coverage rule for gate filtering, contract coverage, reduction, and estimates | `test_selector_coverage_is_shared_by_gate_and_contract`, `test_native_pytest_parameter_selector_matches_the_gate_rule` | `f12aeca50` |
| F10 | Check every original contract selector against the selected pytest IDs, even when a broader selector subsumes it for execution | `test_covered_but_missing_contract_selector_fails_the_run` | `f12aeca50` |

The exact F9 and F10 review probes failed before the change and passed afterward. Two temporary Python mutants restored the old selector boundary and the old reduced-list coverage check. Each made its named regression fail; both mutants were restored before commit. The F9 native pytest fixture confirms that `a::b` selects only that parameter ID, even beside `a::b[c]`.

## Validation

- Focused contract test file: 59 passed before the final native fixture expansion; both new targeted regressions passed afterward. The selected run includes the final file.
- Selected run: 102 mapped units, zero failures, on the VM for code commit `f12aeca50` (tree `b0b0ea0cc4`). The Mac slots were busy for 600 seconds; the first VM fallback was blocked by read-only caches. The successful run used writable `/tmp` caches and exited 0 after 4,631 seconds.
- `PATH=~/.elan/bin:$PATH lake build`: passed, 1,135 jobs. `python3 lean/audit.py`: passed, 653 source files and 7,286 named theorem declarations.
- No full suite or release gate was run, as this fix request directs. The three IDs in `main-known-red.txt` are pre-existing main failures; their tests and product paths were not edited here.

There are no DELTA Ruling cells for this gate-only correction. The prior fix report's F3 closure was superseded by the recheck's C follow-up; no F3 code was changed in this round.
