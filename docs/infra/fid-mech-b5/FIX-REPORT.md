# fid-mech-b5: fix report for the final review (one B finding, F1)

**Status:** F1 fixed as a class; no A finding was filed. **HEAD:** the branch head (`git log -1`); fix commits d76a7d184a, 7abda5f3a5, 0712232697 on 1b54e9a07d.
**What changed:** `records.k_reading` is now the only way the resume and the report read a record's K. A result that no good sentinel confirmed reads as INVALID. Resume runs it again. A budget cut makes it not-run. `worker.batch_status` makes such a batch INVALID. The report leaves it out of every K denominator and counts it beside.
**Open:** none. NOTES C1-C6 were not filed and are not addressed here. The full gate is not run (the merge train runs it).
**DRI signature:** none reserved. DELTA is none (Python tooling only; no Lean, Rust, `ve/` or use-case file changed); trust +0.

## F1 (B): a sentinel-INVALID result was scored as a real K verdict

The class: anything that read a record's `verdict["K"]` without `sentinel_ok`, or took a run's outcome without its confirmation. Each site the review swept, and the fix:

| site | before | after | regression test |
|---|---|---|---|
| `runner.read_resume` | kept every line whose K was not `not-run` | keeps `records.confirmed` lines only; INVALID and not-run lines run again | `tests/test_fidmech_runner.py::test_resume_runs_again_a_result_its_sentinel_marked_invalid` (the PROBE) |
| `runner.schedule` budget path | a re-queued mutant cut by the budget kept its INVALID outcome: counted as ran and as not run, and its line carried the decided K | its outcome and text result are dropped: the line is `not-run`, and it counts as not run only | `tests/test_fidmech_runner.py::test_a_requeued_mutant_the_budget_cuts_is_not_run_and_never_counted_as_ran` |
| batch status (`runner.schedule`, `worker.run_batch`) | `ok` when each slot's last sentinel held, even with a result INVALID twice | shared `worker.batch_status`: `ok` only if every last sentinel held and every outcome is confirmed. `batch.json` gains `invalid`. The CLI prints the resume command when anything is INVALID | `tests/test_fidmech_runner.py::test_a_result_invalid_twice_makes_the_batch_invalid_though_every_last_sentinel_holds`, `tests/test_fidmech_worker.py::test_a_result_invalid_twice_fails_the_batch_though_the_last_sentinel_holds`, `tests/test_fidmech_worker.py::test_batch_status_is_ok_only_on_every_last_sentinel_and_every_outcome_confirmed` |
| `report.verdicts` / `kill_row` | raw K | K through `records.k_reading`. INVALID is out of K decided and counted in `left_out`. A missing or non-bool `sentinel_ok` reads INVALID (fail closed) | `tests/test_fidmech_report.py::test_an_invalid_k_is_left_out_of_every_k_denominator_and_counted_beside` |
| `report.unit_status` | an INVALID kill could make a unit pass, and an INVALID survivor could fail it | an INVALID K makes the unit incomplete | `tests/test_fidmech_report.py::test_a_unit_whose_mutant_is_invalid_is_incomplete_never_passing_or_failing_on_it` |
| `report.verdicts`, declared equivalents counted as survivors | overwrote every K, including not-run, with `survived` (the docstring says "every instrument it ran") | a not-run or INVALID K stays as it is | `tests/test_fidmech_report.py::test_a_declared_equivalent_counted_as_a_survivor_keeps_an_invalid_or_not_run_k` |
| `report.plant_rows` / `plant_counts`, blind spot, unprobed rules, K errors | read `record["verdict"]` directly | read through `verdicts`. `plant_counts` gains `K_invalid` and the document gains `K_invalid` (shown in the batch line of REPORT.md) | `tests/test_fidmech_report.py::test_the_document_report_reads_an_invalid_k_in_plants_blind_spot_unprobed_and_errors` |
| the class itself | any new reader could take `verdict["K"]` directly | an AST test allows a record-verdict read only in `records.k_reading`, `report.verdicts` and `report.fill_cr` (which writes CR) | `tests/test_fidmech_report.py::test_only_records_k_reading_and_report_verdicts_read_a_records_verdicts` |

The scope of INVALID: the sentinel checks the Lean worker, so it bears on K alone. The text checks (L1-L4, D) run in the runner process outside the worker, and CR comes from the recall gate, so their verdicts stand. An INVALID line therefore stays in the any-instrument denominator, under "some instrument did not run", the same as a not-run line. It is out of every K denominator. The record vocabulary is unchanged: INVALID is a reading, never a value written into `verdict["K"]`. The line keeps its measured K with `sentinel_ok: false` for diagnosis.

**PROBE F1:** before the fix it failed with `AssertionError: resume kept an INVALID result in an ok batch`. After the fix it exits 0. It is now the first test in the table.

**Saved run:** `report` was rerun on `~/code/fidmech-b5-runs/{rsp,fsf,pf}` with the same inputs. Every figure is unchanged, because none of the 64 sentinels failed. The only differences are the new `K_invalid: 0` keys and "0 with an INVALID K" in each batch line. rows.json is byte-identical to `manage-agents/reviews/fid-mech-harness/b5-run-20261117/rows.json`. The regenerated report.json and REPORT.md are committed in 0712232697.

## Seeded bugs (Python only)

8 bugs were planted, each run against its tests and restored. All 8 were killed. Script: `docs/infra/fid-mech-b5/fix-f1/seeds.py.txt`. Evidence: `docs/infra/fid-mech-b5/fix-f1/seeded-bugs.json`.

| # | file | bug | failing test(s) |
|---|---|---|---|
| S1 | runner.py | resume keeps unconfirmed lines | `test_resume_runs_again_a_result_its_sentinel_marked_invalid`, `test_a_result_invalid_twice_makes_the_batch_invalid_though_every_last_sentinel_holds` |
| S2 | runner.py | budget cut keeps the INVALID outcome | `test_a_requeued_mutant_the_budget_cuts_is_not_run_and_never_counted_as_ran` |
| S3 | worker.py | batch status ignores the outcomes | the two worker tests above and the runner invalid-twice test |
| S4 | report.py | `verdicts` reads the raw K | the four report behaviour tests |
| S5 | report.py | a plant row reads the raw verdict | `test_the_document_report_reads_...`, `test_only_records_k_reading_...` |
| S6 | report.py | the declared-survivor override turns INVALID into survived | `test_a_declared_equivalent_counted_as_a_survivor_keeps_an_invalid_or_not_run_k` |
| S7 | records.py | a missing `sentinel_ok` fails open | `test_an_invalid_k_is_left_out_of_every_k_denominator_and_counted_beside` |
| S8 | report.py | the blind spot reads the raw K | `test_the_document_report_reads_...`, `test_only_records_k_reading_...` |

## Runs

- The four fidmech test files (runner, worker, report, records): 119 passed (/tmp/b5f1-t1.log).
- `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` at 0712232697 (tree a5be7ef93a). It ran on the VM fallback: 196 units, 0 failed, exit 0, 2060 s (/tmp/b5f1-sel.log).
- `lake build`: OK, 1478 jobs. `python3 lean/audit.py`: PASS. `tools/regen_generated.py --check`: exit 0.
- Not run: the full gate and trust mutants (no Lean change, so R16 does not apply).
- Pre-existing failures (main-known-red.txt): none of them was selected or touched.

## DELTA

None. No user-visible VE behaviour changed: this is the measurement harness under tools/fidmech. No table rows, so no Ruling cells.
