# eff-20261108-1: lazy, scoped control probes in trust_mutants

Status: done; lazy is the default (the STOP RULE did not trigger: 0 of 1,245 compared rows differ; 18 of them are owned rows that ran).
DRI signature needed: none. Tools layer only (`tools/trust_mutants.py` and its two test files); no Lean, no Rust, no
VE output, no DELTA row, trust +0. Final gate: run by the chain on the committed final HEAD.
Every number below cites a file in `evidence/`; `evidence/checks.txt` copies the outputs of the commands named.

## Cost (eff pass 2026-11-08, read-only; from the task, not regenerated here)

From `steps.wall.control_probes` vs `seconds` in `manage-agents/cloud-jobs/*/part-*.json`:

- Last 24 live hours (113 parts, 23 sweeps): control probes 23.5 of 57.5 part-h (41%); 12.8 h of it repeated in
  other shards of the same sweep. 7 calendar days (459 parts, 100 sweeps): 52.3 of 244 part-h (21%), 34.3 h repeated.
- Heavy sweeps spend about half of each part on controls: pc-1gtm-53fdabfd 1,315-1,484 s of 2,581-2,813 s per part;
  jt-3b-ab084a64 1,163-2,016 s of 2,538-3,875 s; ap-3dc-5aeccc44 up to 1,856 s of 3,971 s; et-4b-a97072e6 part-6
  1,030 s of 1,222 s for 21 mutants.
- Resumed parts pay the whole control again: qt-a4b-34d3afcf part-4 (--resume) 4,423 s of controls, then 1,939 s for
  its 2 mutants.
- Light sweeps (pe-1, at-1c) spend 3-40 s on controls.

## Diff summary

`tools/trust_mutants.py` (+67/-23 lines against main):

- `ControlProbes`: the shared control cache. `get((file, span), scope)` probes, under the file's own lock, only the
  spans of `scope` (what `Probes.scope` handed over for the file, `probes.given[file]`) not yet attempted, with
  `probe(..., only=<spans>)`. If any span of that set that `named` can probe has no `complete` entry, the whole file
  is probed (the `Probes.__call__` fallback). Entries are never recomputed. Different files have different locks.
- `run.reading`: reads the control from the `ControlProbes` (lazy) or from the dict (eager) and passes it to `refusal`
  as before. `refusal`, `complete`, `settle`, the cuts and the stage `controls` are unchanged.
- `sweep`: `first` (the unmutated control build) is no longer put in the mutant pool; `min(jobs, len(todo))` pooled
  scratches are made from it, and the controls probe in `first` only. `control_build`, the `outside` failing check
  and `probe_install` still run up front. `--control-probes lazy|eager` (default `lazy`): `eager` is the old
  up-front `ThreadPoolExecutor` pass over every check file (each probed whole), still under the `control_probes` phase.
- Records: `control_probes` is written next to `jobs`. `unread` accepts `lazy`, `eager` or no field (old records
  read as eager). `--merge` writes the common mode, or `mixed`. The mode is not in `inputs.options`, so --rescore,
  --resume, --merge and the shards' AGREED checks treat it as not changing a verdict. The module docstring and
  the docstrings of `probe`, `Probes`, `ControlProbes` and `run` say so.
- Time: a lazy control runs under `STEPS.step("control_probes")` (Lake step); the wall phase `control_probes` is
  near 0 in lazy mode. DEADLINE is unchanged: a lazy control runs inside a mutant's `run` with its timeout, and
  `Abandoned` there makes that mutant NOT RUN. The cache records nothing then, so a later reader tries again.

Tests: `tests/test_trust_mutants_probe_scope.py` and `tests/test_trust_mutants.py`: 8 new tests; none removed,
renamed or skipped. One existing test keeps its name and takes a shared fixture
(`test_the_scoped_probe_classifies_the_seeds_as_the_whole_file_probe(seed_package, ...)`). One existing assertion
was changed for lazy mode: `test_a_run_records_where_its_time_goes` required the wall phase `control_probes` > 0.
That phase is now 0.0 by design (task item 4), and the selected run failed it (`evidence/checks.txt`). It now
requires `control_probes == "lazy"`, the Lake step `control_probes` > 0 (lazy controls still counted) and the wall
phase below the mutants' phase. Its other assertions are unchanged.

| Claim (task proof list) | Test |
| --- | --- |
| a file no kill reads is never control-probed; entries are reused | `test_lazy_controls_only_probe_read_checks_and_reuse_entries` (counts `probing` calls) |
| a later mutant that reads a new span probes only that span | same test (`calls == [{(1,1)}, {(2,2)}]`) |
| one computation for two readers, including concurrent ones | `test_concurrent_lazy_control_of_one_file_is_computed_once` (events and an instrumented lock, no timing) |
| different files compute concurrently | `test_lazy_controls_of_different_files_can_probe_together` (barrier) |
| incomplete scoped entry falls back to the whole file; a control timeout gives today's UNKNOWN reason | `test_lazy_control_incomplete_scope_falls_back_and_timeout_stays_unknown` |
| the control is the unmutated entry (a drifted const is refused) | `test_run_reads_the_unmutated_control_for_a_drifted_constant` |
| control scratch is never given to a mutant | `test_control_scratch_is_never_given_to_a_mutant` |
| eager == lazy (id, definition, operator, status, raw_status, detail) on the seeded package (30 mutants, real Lean); `--control-probes eager` makes today's calls: one whole-file control per check file, all before the first mutant | `test_eager_and_lazy_controls_agree_on_seeded_package` |
| an old record without the mode is accepted by --resume, --rescore (mode `identical`) and --merge (`mixed`) | `test_control_probe_mode_is_recorded_but_not_a_verdict_input` |

## Why verdicts cannot change

A control entry is read only by `refusal(probes(key), control)` in `run.reading`, which `settle` calls only on the way
to a KILLED verdict, so a control can only change whether a candidate kill is refused. The lazy control is the
same `probe` of the same unmutated build (`first`: no mutant edit and no cut is ever written there, and
`test_control_scratch_is_never_given_to_a_mutant` checks this), without `TM_TRUST_MUTATED`. It is scoped by the same
`Probes.scope` set as the mutant's side and falls back to the whole file under the same `complete` rule.
eff-tm-probe-scope showed that a check's scoped entry equals its whole-file entry (jt-2c 73e809748, qt-a3d 493da762,
51 seeded mutants); the merged mutant-side scoping already rests on this. So every lazy control entry equals the eager
one, except where the eager whole-file probe has no entry because it timed out (design F1/F2). There the scoped probe
can finish, and UNKNOWN can become KILLED, against a finished control. No such case occurred in the A/B below.
Checks: the seeded-package agreement test, and the 1,245 rows (18 owned) compared between eager and lazy runs on real Lean (0 differ).

## Paired A/B on real Lean

Command: `zsh manage-agents/mac-pytest.sh --trustmut -- --base b5a80d5e4584d3b8f462e5a9904deb580c0bee02 --test
lean/VE/Judgments/ChainExamples.lean --allow docs/profile-composition/pc-1g/trust-mutants-allow.json --max-mutants 60
--shard K/N --control-probes MODE --json docs/infra/eff-20261108-1/evidence/MODE-KofN.json`. The base is the first
parent of pc-1gtm's merge. Runs were one at a time. The mode is the only difference within a pair (same head,
same host class). The 1/8 pair ran at `03ade26e1`, which has the same tool code as HEAD before the merge of main
apart from one docstring line. The 2/8 pair ran at `fb40d6659`, the item's HEAD before the merge of main. The
supplementary 1/32 pair ran on a dispatch snapshot (`5febd940f`) of the same tool code. Sweep exit 1 means
survivors/UNKNOWN exist (a measurement, not the trust gate), and it is the same in both modes.

| Shard | Mode | jobs | control Lake s | control wall s | mutants wall s | total s | K/S/U/I/A | rows equal |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1/8 | eager | 6 | 625.9 | 417.0 | 47.3 | 476 | 5/2/1/0/0 | baseline |
| 1/8 | lazy | 6 | 18.7 | 0.0 | 67.4 | 80 | 5/2/1/0/0 | 415/415 (8 owned) |
| 2/8 | eager | 8 | 1,250.8 | 1,194.8 | 104.0 | 1,346 | 4/3/1/0/0 | baseline |
| 2/8 | lazy | 8 | 24.2 | 0.0 | 184.9 | 238 | 4/3/1/0/0 | 415/415 (8 owned) |
| 1/32 | eager | 2 | 496.3 | 471.9 | 31.1 | 520 | 2/0/0/0/0 | baseline |
| 1/32 | lazy | 2 | 5.0 | 0.0 | 50.3 | 67 | 2/0/0/0/0 | 415/415 (2 owned) |

Source: `evidence/{eager,lazy}-{1of8,2of8,1of32}.json` (`steps`, `seconds`, `counts`). The row comparison of every
row (status, raw_status, detail) is in `evidence/checks.txt` ("differing []" for all three pairs). A part's total drops
by 83% (1/8), 82% (2/8) and 87% (1/32). The mutants' wall grows by 20-81 s, because the few controls that kills read
now run inside it. The 1/8 and 2/8 UNKNOWN is the same row with the same detail in both modes, so no
UNKNOWN -> KILLED case occurred.

## Seeded bugs (Python, `tools/trust_mutants.py`; each restored after the named test failed)

1. `run.reading` returned the mutant's own probe entry as the control: FAILED
   `tests/test_trust_mutants_probe_scope.py::test_run_reads_the_unmutated_control_for_a_drifted_constant`
   (`/tmp/eff-seed-drift.log`, copied to `evidence/checks.txt`).
2. `ControlProbes.get` skipped the whole-file fallback for an incomplete scoped entry: FAILED
   `tests/test_trust_mutants_probe_scope.py::test_lazy_control_incomplete_scope_falls_back_and_timeout_stays_unknown`
   (`/tmp/eff-seed-fallback.log`).
3. The control scratch `first` was put back in the mutant pool, so a control could probe a scratch with another
   mutant's edit in place: FAILED `tests/test_trust_mutants.py::test_control_scratch_is_never_given_to_a_mutant`
   (`/tmp/eff-seed-scratch.log`).
4. The per-file lock dropped (`with threading.Lock():` for `with self.locks[f]:`): FAILED
   `tests/test_trust_mutants_probe_scope.py::test_concurrent_lazy_control_of_one_file_is_computed_once`
   (`/tmp/eff-seed-lock.log`; again this session after the test was made deterministic: `calls` had two entries).

## Test runs

- Changed tests: `uv run pytest -q tests/test_trust_mutants_probe_scope.py -k 'concurrent or eager_and_lazy'`:
  2 passed. Earlier focused runs are in `evidence/checks.txt`.
- `uv run python tools/regen_generated.py --check` after the merge of main: "checked 37 entries" (`evidence/checks.txt`).
- Selected tests (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, at `11be24c14`): shards
  1, 3 and 4 passed. Shard 2 had 1 failure, `test_a_run_records_where_its_time_goes`, fixed as described above; the
  failed id then passed alone (`1 passed`). No pre-existing main-known-red test was involved.

## Acceptance

AGENT: the implementation, record compatibility, tests and the A/B (done). EXTERNAL: the 48 h production measure
(FOLLOW-UPS). HUMAN: none.

FOLLOW-UPS (eff pass): 48 h after the merge, sum `steps.wall.control_probes` and `steps.lake.control_probes`
against `seconds` in cloud-jobs part JSONs of sweeps whose tool has this change (`control_probes` in the record).
Expected: control under 10% of part-h (from 41% on Nov 8), and heavy parts' wall down by about their old control
share (A/B: 82-87%).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer or response schema changed (`git diff --stat main...HEAD`: tools/tests/docs only).
2. PASS: deliverables 1-5 built: lazy cache, dedicated scratch, `--control-probes eager`, the mode in the record
   and its compatibility, step accounting, and the docstrings. A/B 2 shards × 2 modes plus a supplementary pair.
   `test_control_probe_mode_is_recorded_but_not_a_verdict_input`; `uv run python tools/regen_generated.py --check`.
3. PASS: 4 seeded bugs, each failing its named test (above).
4. PASS: eager and lazy agree: `test_eager_and_lazy_controls_agree_on_seeded_package`; real-Lean rows in `evidence/checks.txt`.
5. N.A.: no relayed answer or R8 binding.
6. PASS: A/B evidence records its heads; the chain runs the gate on the final HEAD.
7. PASS: no unsigned item: no DELTA row (no VE output changes), trust +0.
8. N.A.: no user-visible VE change (tools layer only).
9. PASS: the selection picked both changed test files and the chunks of `tests/test_trust_mutants.py` (`evidence/checks.txt`).
10. N.A.: no Lean statement or proof.
11. PASS: deadline/timeout stays UNKNOWN / NOT RUN:
    `test_lazy_control_incomplete_scope_falls_back_and_timeout_stays_unknown`; DEADLINE code path unchanged.
12. PASS: no CPU regression: A/B totals down 82-87%; light sweeps pay at most what eager paid, since lazy probes only a subset of the files.
    `test_lazy_controls_only_probe_read_checks_and_reuse_entries`.
13. N.A.: no test removed or renamed (the `-def`/`+def` pair in the diff is the same name with a new fixture).
14. PASS: both directions: the fallback taken (incomplete) and not taken (`test_lazy_controls_only_probe_read_checks_and_reuse_entries`); a
    drifted const refused and an equal one kept (`test_run_reads_the_unmutated_control_for_a_drifted_constant`);
    one file serialized and two files concurrent. Every claim here cites a file or log. Spec re-read: task items 1-5
    against the item text.
15. PASS: no overclaim: the universal words ("never recomputed", "0 differ", "none removed") are backed by the
    reuse test, `evidence/checks.txt` and `git diff main...HEAD | grep -E '^[-+]def test_'`. No silent cut. Every new
    check can fail (seeded bugs 1-4). Limits: DEADLINE/timeouts unchanged (`test_lazy_control_incomplete_scope_falls_back_and_timeout_stays_unknown`).
