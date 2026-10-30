# pipeline-death-alert (2026-10-30): a dead design pipeline alerts; no pipeline under 16G; stage 1 names DRI-CROSSPLAN.md

Status: built and installed in manage-agents (not a git repository); this branch carries only this report. 16 new stub-harness tests pass; 10 seeded bugs are each caught.
Signature: none needed. There is no VE product code, no DELTA row and no Ruling cell.
For the DRI: en-e3-norm and imprecise-dates sit in the late-synthesis hold inside 10G scopes. They still run the old feature-pipeline.sh, which their zsh holds open, so the new guard does not cover them. Before `rm <n>-pipeline-state/hold`, raise their caps (`systemctl --user set-property ve-research-en-e3-norm-1793270108.scope MemoryMax=32G`, and the same for ve-research-imprecise-dates-1793272546.scope) or relaunch them. If they die in stage 1 anyway, the new alert reports it. This item did not touch either running job.

Order: reviews/dri-decisions-20261030-fp-apol-draw.md items 2-3; task prompts/task-pipeline-death-alert.txt; backlog pipeline-death-alert.

## Changes (all in /home/seyran/code/manage-agents)

Every edited file went through `.new`, then `zsh -n` or `py_compile` and a line-count check, then a backup `.bak-20261030-pda` and `mv`. Before the swap, `systemctl --user list-units --type=scope` and `pgrep -af feature-pipeline.sh` showed two live readers of feature-pipeline.sh: en-e3-norm (pid 719879) and imprecise-dates (pid 4145008), both in the late-synthesis hold. After the `mv`, `/proc/<pid>/fd` showed both still reading the old inode (`(deleted)`). None of the launchers below was running.

1. **Alert: tools-local/pipeline-death-alert.py (new).** It lists `ve-*.scope` units with `systemctl --user list-units --type=scope --all`. A unit counts as a pipeline scope when its command runs research-wave.sh, research-refresh.sh, feature-pipeline.sh, design-item.sh, pipeline-stage1-resume.sh, a `*-revise.sh` or a `*-leanrun.sh`, or when the unit is named `ve-research*-<n>`. It reports a pipeline scope that is `failed` when all of these hold:
   - none of the pipeline's ending finals is newer than the scope's start: `<n>-design-ready`, `<n>-pipeline-stop`, `<n>-pipeline-done`, `research-<n>-stop`, `<n>-refresh-done`, `research-<n>-refresh-stop`, any `*.md`, so handled renames count;
   - no later scope of that pipeline exists, in any state, and no live process runs it (so it was not restarted);
   - the unit is not already in `pipeline-death-alert.state`.

   With `--write`, it writes `<n>-pipeline-stop.final.md`, which states the unit, the systemd result (oom-kill) and time, the stage files, the command, "this needs the DRI" and how to restart. It then records the unit, so a final that has been handled and renamed is not raised again.
   - **Caller: checkin-scan.py.** Each scan, but not `--mark`, runs the detector with `--write` before it collects finals. A death between two check-ins therefore becomes a new `*-pipeline-stop.final.md` that the same scan reports (verdict RUN), and NOW.md lists it under "Waiting on the DRI" (`*-stop.final.md`, < 3 d). The text "needs the DRI" also matches dri-decider.sh's wake grep. `--mark` never writes: a final written after the scan would get an mtime before the mark and would be lost.
   - **Live check after install (one scan, which wrote nothing):** no pipeline is reported. The 7 failed pipeline scopes (action-preferences, apol-flow, apol-assent, hedges-generics, attitudes refresh, risk refresh, commands-imperatives) each have an ending final newer than the scope's start. The two active ones are not failed. ve-exp-elanbin-mac and ve-svc-freeze-mover are not pipelines.
2. **Memory: both approaches.**
   - **feature-pipeline.sh refuses a cap under 16G** (`FP_MIN_MEM`, default 17179869184). The check runs before the pause gate, the state dir and any stage. It reads `memory.max` on its own cgroup and each parent, and takes the lowest numeric value, because iso.sh sets MemoryMax on the scope. Under 16G it writes `<n>-pipeline-stop.final.md` (the cap, the minimum, "this needs the DRI", relaunch with 16G or more) and exits 1. Why the guard: every launch passes through feature-pipeline.sh, including ad hoc DRI launches, one-off relaunch scripts and old usage lines, so this one check covers launchers that a list of scripts would miss. It fails loudly with a final instead of an OOM kill that leaves no trace.
   - **The reusable launchers are raised from 4G to 32G**, so a normal wave does not hit the guard at the handoff to feature-pipeline.sh. 32G is the size of the DRI's 09:22Z restart and of pipeline-stage1-resume.sh. The files: research-wave-launch.sh, research-wave2-launch.sh, research-gap-run.sh (the research-wave line; its research-refresh.sh line stays 2G because research-refresh.sh does not call feature-pipeline.sh), research2-run.sh (2 lines), tools-local/const-replan-launch.sh, and the usage lines of apol-assent-revise.sh, commands-imperatives-revise.sh and ap-v2-key-design-revise.sh.
   - **The dated one-off scripts are left as their records:** recover-20261014.sh (4G) and tools-local/relaunch-waves-20261029*.sh (10G). The guard refuses them if they are re-run.
   - No `.md`/`.txt` instruction launches a pipeline under 16G (grep).
3. **Stage 1 prompt (feature-pipeline.sh).** When `$D/DRI-CROSSPLAN.md` exists, the prompt begins "Your orders are $D/DRI-CROSSPLAN.md ...: read it whole first". It says the file sets what to apply and in what order, and that it overrides the converged edits where they differ. The orders are checked when stage 1 starts, after the late-synthesis hold, so orders written during the hold count. In both branches the plan is applied "as edits, not a rewrite: change only what they ask for and keep every other line of the plan as it is, word for word (no summary, no shortening)". Without the file, the prompt is the old one plus that sentence. I added it in both branches because a rewrite is wrong with or without cross-plan orders.
4. **tools-local/test_pipeline_death_alert.py (new, 16 tests, `python3 -I tools-local/test_pipeline_death_alert.py`).** Each test runs in a temp sandbox with a fake systemctl, a process-list file, and, for feature-pipeline.sh, `HOME=<sandbox>` with stub helpers and `FP_CGROUP`.

## Evidence

`python3 -I tools-local/test_pipeline_death_alert.py`: `Ran 16 tests ... OK` on the installed files. The first 15 also passed against the `.new` copies before the swap.

| Claim | Test |
|---|---|
| A failed research scope with no final gets one stop final with the unit, oom-kill, stage files, command and 16G; recorded; a handled final is not raised again | test_oom_killed_design_pipeline_gets_a_stop_final_once |
| Opposite direction: without the state record the same unit is raised again (the record is what silences it) | test_without_the_state_file_the_same_unit_is_raised_again |
| Without --write: printed, nothing written | test_without_write_it_prints_and_writes_nothing |
| hedges-generics, attitudes, risk, commands-imperatives, apol-assent, action-assurance, each finished since: silent | test_old_failures_that_finished_since_stay_silent |
| apol-assent 01:24Z replay: a stop final older than the scope does not silence it | test_a_final_older_than_the_scope_does_not_count |
| A later scope (active resume, or a later failed run) or a live process: silent | test_a_restarted_pipeline_stays_silent |
| Two dead runs: the newest alerted once | test_two_dead_runs_alert_the_newest_once |
| elanbin, freeze-mover, design-hold-end, an active research scope: ignored | test_other_scopes_are_ignored |
| Names from revise, refresh (env prefix), stage1-resume, design-item, leanrun, research2 scope name | test_pipeline_names_from_each_launcher |
| checkin-scan reports the new final and says RUN; --mark writes none; a CS_M sandbox without CS_PDA never runs it | test_checkin_scan_reports_the_new_stop_final_and_mark_writes_none |
| A detector crash is reported by the scan as an anomaly (rc and last stderr line), not as silence | test_checkin_scan_reports_a_detector_crash |
| 4G: exit 1, stop final, no prompt, no state dir, pause gate not reached | test_a_4g_scope_is_refused_before_anything_runs |
| A 10G cap on the parent slice with an uncapped scope: refused | test_a_cap_on_a_parent_slice_is_refused |
| Opposite direction: 16G (boundary), 32G, max, no cgroup run stage 1 | test_16g_32g_and_no_cap_run_stage_1 |
| With DRI-CROSSPLAN.md: named as the orders, read whole, overrides, edits not rewrite | test_stage_1_names_dri_crossplan_as_the_orders |
| Without: converged edits as edits; no DRI-CROSSPLAN mention | test_stage_1_without_crossplan_applies_the_converged_edits_as_edits |

## Seeded bugs

Each bug was planted in a temp copy and run against the one test below; each run failed. The live files were never seeded.

| # | file | seed | failing test |
|---|---|---|---|
| S1 | tools-local/pipeline-death-alert.py | any ending final counts, whatever its age | test_a_final_older_than_the_scope_does_not_count |
| S2 | tools-local/pipeline-death-alert.py | alerted unit not recorded | test_oom_killed_design_pipeline_gets_a_stop_final_once |
| S3 | tools-local/pipeline-death-alert.py | restart check off | test_a_restarted_pipeline_stays_silent |
| S4 | feature-pipeline.sh | cap read on its own cgroup only (no walk up) | test_a_cap_on_a_parent_slice_is_refused |
| S5 | feature-pipeline.sh | `-lt` -> `-le` (16G refused) | test_16g_32g_and_no_cap_run_stage_1 |
| S6 | feature-pipeline.sh | DRI-CROSSPLAN.md test never true | test_stage_1_names_dri_crossplan_as_the_orders |
| S7 | feature-pipeline.sh | "as edits, not a rewrite" dropped | test_stage_1_without_crossplan_applies_the_converged_edits_as_edits |
| S8 | checkin-scan.py | detector also run with --mark | test_checkin_scan_reports_the_new_stop_final_and_mark_writes_none |
| S9 | tools-local/pipeline-death-alert.py | state file not read | test_oom_killed_design_pipeline_gets_a_stop_final_once |
| S10 | checkin-scan.py | detector's exit code ignored | test_checkin_scan_reports_a_detector_crash |

Languages: the changed code is Python (pipeline-death-alert.py, checkin-scan.py) and zsh (feature-pipeline.sh, launchers). There is no Lean or Rust.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed: N.A., no relayed answer.
2. Deliverables: PASS. Items 1-3, the install rule, the CURRENT-STATE line and the backlog status are covered by the tests above.
3. Tests can fail: PASS, S1-S10; test_a_4g_scope_is_refused_before_anything_runs.
4. Python/Lean/Rust agree: N.A., no VE path. Old and new prompt are compared by test_stage_1_without_crossplan_applies_the_converged_edits_as_edits.
5. R8 binding: PASS for the tool's own input: unknown scopes are ignored (test_other_scopes_are_ignored).
6. Gate evidence: N.A. for the builder; the chain gates the final HEAD.
7. Nothing unsigned: PASS. No DELTA row; the branch diff is this report only.
8. User-visible change: PASS. The new stop final and the 16G refusal are listed here; there is no VE behaviour change. Tests: test_oom_killed_design_pipeline_gets_a_stop_final_once, test_a_4g_scope_is_refused_before_anything_runs.
9. Test selection: PASS. The selection ran once on 5635e8883 (mac-pytest.sh --select: GitHub Actions, 4 shards, exit 0).
10. Lean statements: N.A., no Lean.
11. Budgets fail closed: PASS. A cap under 16G stops with a final; an unreadable cgroup does not refuse (test_16g_32g_and_no_cap_run_stage_1). A detector crash is reported by the scan as an anomaly, never as silence (test_checkin_scan_reports_a_detector_crash).
12. CPU/memory: N.A. One systemctl call per check-in; the 16 tests take about 3 s.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. test_without_the_state_file_the_same_unit_is_raised_again, test_16g_32g_and_no_cap_run_stage_1; task and decision re-read before finishing.
