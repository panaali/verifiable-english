# tm-probe-rc-detail: a probe's non-zero lake rc is named in the UNKNOWN detail

Status: built, ready for the chain gate; code commit bcfbe4b7fe (this report is committed after it).
What changed: `tools/trust_mutants.py` `probe` keeps lake's rc, and `refusal` says "the probe's lake run exited with rc <N>" in place of "Lean could not elaborate it in the probe". The verdict stays UNKNOWN.
Open items: none. No DELTA rows, no DRI signature reserved, trust +0 (LIGHT lane).
Not run: the full gate (the chain runs it), trust_mutants (LIGHT lane, the task asks for no record).

SIZE: 17 product, 40 tests, 0 other hand-written lines (`git diff --numstat main...HEAD`: tools/trust_mutants.py 11+/6-, tests/test_trust_mutants_probe_scope.py 33+/7-; this report not counted).

## Deliverables

| Task line | Delivered by | Test |
|---|---|---|
| (1) The probe keeps lake's rc. A non-zero rc that is not a timeout gives "the probe's lake run exited with rc <N>", and the verdict stays UNKNOWN | `probe`: an `rc` key on each walked check with no `done`. `refusal`: names it after `late` | `test_a_probe_whose_lake_run_exits_non_zero_names_its_rc_and_stays_unknown` |
| (2) The text does not match tm-nightly.py build_timeout()'s regex. Align the timeout text if it does not match | rc text: asserts the regex does not match it. Timeout text: already matches (`Scratch.lake` prints `did not finish in {timeout:g} s (--build-timeout)`, and `refusal` keeps it after "the probe did not "), so it is not changed | same test (`not re.search(...)`), plus `test_a_probe_past_the_build_timeout_says_so_and_stays_unknown` (`re.search(...)` on the full detail) |
| (3) Condition test: the refusal path with a non-zero rc gives the new text and UNKNOWN, shown failing on main first. A timeout still gives the timeout text | the new test above. On the old `tools/trust_mutants.py` it failed with `AssertionError: ('UNKNOWN', 'lean/A.lean:2: Expression (Lean could not elaborate it in the probe)')` (`uv run pytest -q tests/test_trust_mutants_probe_scope.py -k "build_timeout or non_zero"`: 1 failed, 1 passed) | both tests above |

Timeout alignment (2): checked by hand, and pinned by the new regex assertion. The regex `did not finish in ([0-9.]+) s \(--build-timeout\)` matches "the probe did not finish in 500 s (--build-timeout)". No change was needed.

Spec re-read: the text "the probe's lake run exited with rc <N>", UNKNOWN, not counted by build_timeout(). Checked against reviews/dri-decisions-20261110-tm-m509-route-probe-addendum.md item 1 and the task file's DO (1)-(3).

## Design notes

- Only entries without `done` carry `rc`. A scoped probe (`kept`) can leave a Lean error after the checked set, which makes lake exit 1 even though the set's walks are whole. Those whole entries must stay equal to the whole file's (F3). My first version put `rc` on every entry, and `test_a_cut_that_changes_a_parse_fails_closed_in_lean` caught it. The rerun passed: `-k "cut_that_changes_a_parse_fails_closed_in_lean or non_zero or build_timeout or elaborate or lazy"` gave 10 passed. A unit assertion in the new test (`FakeLake(..., code=1)`) also pins this.
- `late` (timeout) still goes on every walked entry, as before. `refusal` checks `late` before `rc`.
- Lake also exits 1 when Lean reports an error. So an incomplete entry from an erroring run now reads "exited with rc 1" where it used to read "could not elaborate". This is the task's wording: crash, OOM and error cannot be told apart from the rc alone. A run that exits 0 with no entry for a check keeps "Lean could not elaborate it in the probe" (asserted in the new test).
- `Probes` and `ControlProbes` still fall back to the whole file's probe when a scoped entry is not whole. The rc shown is therefore the whole-file run's (the new test checks the calls: `["tmChk_2", None]`).

## Seeded bugs (Python, the only language changed; each planted in tools/trust_mutants.py, run, reverted)

Command for each: `uv run pytest -q tests/test_trust_mutants_probe_scope.py -k "non_zero or build_timeout"`.

| # | Mutation in tools/trust_mutants.py | Failing test |
|---|---|---|
| S1 | `refusal` returns "Lean could not elaborate it in the probe" for an rc | `test_a_probe_whose_lake_run_exits_non_zero_names_its_rc_and_stays_unknown` |
| S2 | the rc text written as "did not finish in <rc> s (--build-timeout)" (counted by build_timeout) | `test_a_probe_whose_lake_run_exits_non_zero_names_its_rc_and_stays_unknown` |
| S3 | `rc` attached to whole entries too | `test_a_probe_whose_lake_run_exits_non_zero_names_its_rc_and_stays_unknown` |
| S4 | `probe` keeps the code only on `TIMED_OUT` (the old behaviour) | `test_a_probe_whose_lake_run_exits_non_zero_names_its_rc_and_stays_unknown` |
| S5 | `refusal` drops the timeout text when no `rc` | `test_a_probe_past_the_build_timeout_says_so_and_stays_unknown` |

## Tests run

- New and changed tests, plus the Lean F3 test, listed above.
- `uv run pytest -q tests/test_trust_mutants_probe_scope.py` (whole file, first version): 40 passed, 1 failed (the F3 case, fixed as described above).
- The final selected run's result is recorded by the chain (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select`) on the committed HEAD.

## Notes for the DRI

- An rc of 1 also covers an ordinary Lean error, not only a crash. If the nightly needs to tell these apart, the stderr tail would have to go into the detail too. That is wording, not filed.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer. This is a tool's internal probe entry.
2. PASS: deliverables table above. Each row cites `test_a_probe_whose_lake_run_exits_non_zero_names_its_rc_and_stays_unknown`.
3. PASS: seeded bugs S1-S5, each caught by a named test.
4. N.A.: no Py/Lean/Rust checker path changed (tools only).
5. N.A.: no binding of a Lean answer.
6. PASS: the gate runs on the committed final HEAD by the chain. No evidence numbers are saved in this item.
7. PASS: no DELTA row (tool wording, refuse-only, per the task). Trust +0 (`light-lane.py check`: LIGHT 57 lines, no trusted-core file).
8. N.A.: no user-visible VE output changed. The trust_mutants UNKNOWN detail wording is a tool text, and the task says no DELTA rows.
9. PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects tests/test_trust_mutants.py and tests/test_trust_mutants_probe_scope.py.
10. N.A.: no Lean change.
11. PASS: the verdict stays UNKNOWN on a non-zero rc and on a timeout (`test_a_probe_whose_lake_run_exits_non_zero_names_its_rc_and_stays_unknown`, `test_a_probe_past_the_build_timeout_says_so_and_stays_unknown`). No sleeps and no literal timeouts in the tests.
12. N.A.: a constant-time check per walked entry. No new Lean runs.
13. N.A.: no test removed or renamed. One assertion block moved from the timeout test into the new test.
14. PASS: both directions: rc != 0 gives the rc text, rc 0 with no entry keeps the old text, a whole entry under rc 1 stays equal, and a timeout keeps the timeout text (all in the two tests above). Claims cite commands. Spec re-read is recorded above.
15. PASS: no overclaim (each "every"/"only" above names its test). No deliverable cut. Each new check has a mutant (S1-S5). Limits N.A.
