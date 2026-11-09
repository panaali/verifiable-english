# eff-20261108-1

Status: implementation and seeded checks complete; real-Lean A/B shard 2 and final selected tests pending.
HEAD for the A/B code: `03ade26e1` (tool code); final report commit pending.
Changed: lazy, scoped control probes with a dedicated unmutated scratch; eager veto remains available.
Open: complete the second A/B pair, full changed-file tests, selected tests, and final review.
DRI signature needed: none; this tool change has no user-visible VE output delta.

## Cost and change

The Nov 8 read-only eff pass counted `steps.wall.control_probes` against `seconds` in cloud-jobs part JSONs. In the last 24 live hours, 113 parts in 23 sweeps spent 23.5 of 57.5 part-hours (41%) on controls; 12.8 hours were repeated in other shards of the same sweep. In seven calendar days, 459 parts in 100 sweeps spent 52.3 of 244 part-hours (21%) on controls, with 34.3 hours repeated. Heavy parts spent roughly half their wall time on controls (pc-1gtm 1,315–1,484 of 2,581–2,813 s per part); a resumed qt-a4b part spent 4,423 s on controls before two mutants consumed 1,939 s. These source numbers are from the task's read-only eff pass; they were not regenerated in this worktree.

`tools/trust_mutants.py` now keeps the first, unmutated scratch for controls and creates all mutant scratches from it. A shared `ControlProbes` cache has one lock per file. A read probes only the missing spans passed by `Probes.scope`, with the same whole-file fallback for incomplete scoped entries. Lazy work is charged to `STEPS.step("control_probes")`; the wall phase remains near zero because controls run during mutant work. `--control-probes eager` retains the upfront whole-file path. The mode is recorded beside `jobs`; an old record reads as eager. The mode is outside the verdict input options, so rescore, resume, and merge can cross it; a mixed-mode merge records `mixed`. The change is Python tools only; Lean, Rust, relayed VE answers, stage controls, cuts, `refusal`, `complete`, `settle`, deadlines, and verdict rules are unchanged.

## Verdict argument

`run` reads a control entry only through `reading` while `settle` tests a candidate KILLED refutation. The lazy control is the same `probe` without `TM_TRUST_MUTATED`, scoped by the same `Probes.scope` set and using the same `complete` fallback. The prior eff-tm-probe-scope evidence on jt-2c `73e809748`, qt-a3d `493da762`, and 51 seeded mutants found scoped entries equal to whole-file entries. A missing whole-file entry caused by a timeout or failed later walk can become a completed scoped entry; in that case eager UNKNOWN may become lazy KILLED. No other verdict difference is allowed. The paired A/B rows below check this on the item's tool HEAD.

## Paired real-Lean A/B

Command family: `zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --base b5a80d5e4584d3b8f462e5a9904deb580c0bee02 --test lean/VE/Judgments/ChainExamples.lean --allow docs/profile-composition/pc-1g/trust-mutants-allow.json --max-mutants 60 --shard K/8 --control-probes MODE --json docs/infra/eff-20261108-1/evidence/MODE-Kof8.json`. The base is the first parent of the pc-1gtm merge. Each part owns eight of the first 60 mutants; 355 are past the cap. These are measurement runs, not the trust-growth gate (no Lean product code changed). A nonzero sweep exit due to survivors or UNKNOWN does not invalidate a row comparison.

| Shard | Mode | Control Lake s | Control wall s | Mutants wall s | Tool total s | Owned counts K/S/U/I/A | Row agreement |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 1/8 | eager | 625.9 | 417.0 | 47.3 | 476 | 5/2/1/0/0 | baseline |
| 1/8 | lazy | 18.7 | 0.0 | 67.4 | 80 | 5/2/1/0/0 | 8/8 exact |
| 2/8 | eager | pending | pending | pending | pending | pending | pending |
| 2/8 | lazy | pending | pending | pending | pending | pending | pending |

Source: `evidence/eager-1of8.json`, `evidence/lazy-1of8.json`; a Python comparison of each row's `(status, raw_status, detail)` printed no differences. The shard 1 Mac runner elapsed times included queue time (2,790 and 1,263 s), distinct from the tool's recorded totals. The first shard 2 eager attempt timed out after 3,000 s during a VM fallback without a part JSON; its retry is still running under `wait-bg.sh` at this draft.

## Tests and seeded bugs

The focused checks cover no read/no probe, a cache hit shared by two readers, a later missing span, whole-file fallback, timeout UNKNOWN, constant drift, concurrent same-file access, a dedicated control scratch, old mode-free records, and eager/lazy seeded-package agreement. The seeded-package test compared 30 mutants in both modes with real Lean (`5 passed` in the latest focused probe run; `/tmp/eff-post-seed-probe.log`). The record and scratch tests passed (`2 passed`; `/tmp/eff-post-seed-tests.log`). `uv run python tools/regen_generated.py --check` reported 37 checked entries (`/tmp/eff-regen-check.log`).

Each temporary Python product-code bug was restored after the named test failed:

1. `tools/trust_mutants.py`: `reading` used the mutant probe entry as its control. `test_run_reads_the_unmutated_control_for_a_drifted_constant` failed (`/tmp/eff-seed-drift.log`).
2. `tools/trust_mutants.py`: skipped the incomplete scoped control fallback. `test_lazy_control_incomplete_scope_falls_back_and_timeout_stays_unknown` failed (`/tmp/eff-seed-fallback.log`).
3. `tools/trust_mutants.py`: put the control scratch into the mutant pool. `test_control_scratch_is_never_given_to_a_mutant` failed (`/tmp/eff-seed-scratch.log`).
4. `tools/trust_mutants.py`: replaced the per-file lock with a new lock per call. `test_concurrent_lazy_control_of_one_file_is_computed_once` failed (`/tmp/eff-seed-lock.log`).

No VE DELTA rows apply: this tool does not produce a user-facing VE verdict, diagnostic, field, or wording. No DRI ruling is claimed for a changed VE output. Acceptance: implementation, record compatibility, test coverage and A/B are AGENT; 48-hour production measurement is EXTERNAL (merge chain owner). No HUMAN item is required.

FOLLOW-UPS: 48 hours after merge, sum `steps.wall.control_probes` and `steps.lake.control_probes` against `seconds` in cloud-jobs part JSONs for sweeps whose tool has this change. Expect control under 10% of part-hours, down from 41% on Nov 8, and heavy parts' wall time down by roughly their old control share.

## Self-review against BUILDER-CHECKLIST

1. N.A. — no Lean answer or response schema changed.
2. PASS — `git diff --stat main...HEAD` and `uv run python tools/regen_generated.py --check` check tool-only scope and generated files.
3. PASS — four seeded failures listed above; mode comparison checks exact row values.
4. N.A. — no Python, Lean, or Rust VE answer changed.
5. N.A. — no relayed answer or request binding changed.
6. PASS — `git status --short --branch` and the four saved A/B records will identify the final HEAD; the chain runs the final gate.
7. PASS — no VE DELTA or trust-budget growth; `git diff --stat main...HEAD` confirms the scope.
8. PASS — exact eager/lazy row comparison in saved A/B evidence; no user-visible VE output change.
9. PASS — selected-test command on final code pending; seeded tests are mapped by their named files.
10. N.A. — no Lean statement or proof changed.
11. PASS — `test_lazy_control_incomplete_scope_falls_back_and_timeout_stays_unknown` and the retained `Abandoned` path.
12. PASS — A/B step timings above; `test_lazy_controls_only_probe_read_checks_and_reuse_entries` guards call count.
13. PASS — no test removed or renamed; `git diff --name-status main...HEAD`.
14. PASS — A/B checks both modes and the four seeded failures prove the new branches can fail; no new spec binding.
15. PASS — no overclaim until the remaining A/B is saved; the required deliverables and mode compatibility are tested by `test_control_probe_mode_is_recorded_but_not_a_verdict_input`.
