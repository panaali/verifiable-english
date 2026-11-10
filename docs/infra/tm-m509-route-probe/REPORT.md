# tm-m509-route-probe: report

**STOPPED at DO (3): only a tools/trust_mutants.py change can judge M509 reliably.** No test file can do it. One DRI
condition is not met: there is no `m509.json` from a branch fix. KILLED depends on the host's speed (see (1)). Nothing
is committed to the tool or to any Lean file. The DRI was told through msg.sh.

## The mutant

The nightly's M509 (test-skip/nightly/20261109T1849Z.json, head 1531891aa, base 039d3dd51) is et-4b-tm's M217:
`VE/Events/Wire.lean:180`, `VE.Events.decodeThroughLinks`, list-empty, `(← arrAt b "" "events")` -> `[]`. That record
is not on this host (`manage-agents/test-skip/` is absent here). On this head, `--only M509` with the default base
names nothing, because the branch has no trusted lines. The same mutant is `M1952` under `--base a270588eb^` (the
parent of et-4b's Wire commit), with the same file, line, definition, operator, before and after. Every run below is
`trust_mutants.py --base 'a270588eb^' --only M1952 --test lean/VE/Events/WireExamples.lean --test
lean/VE/Events/RouteExamples.lean --jobs 2`, on main 65e6e4b0e (this branch had no commits). The first run used the
bare command and gave KILLED. The saved runs used `evidence/drv.py.txt`: the tool's own `main`, unchanged, with
`probe` and `settle` wrapped so that each probe's scope, return code, seconds and entries are logged
(`evidence/probe-log-*.jsonl`).

`lean/VE/Events/` is byte-identical at et-4b-tm's record head (6be3f873f), the nightly head (1531891aa) and main
(`git diff --stat` empty). Their import cone is not: 27 files under lean/VE changed from 6be3f873f to 1531891aa.
The task's premise is wrong: pk-1-conditions-b's last RouteExamples commit (a95fa911e) is an ancestor of
6be3f873f. RouteExamples.lean has not changed since et-4b-tm judged this mutant KILLED.

## (1) On main: the verdict depends on the probe's time limit

Default `--build-timeout 1800` (`m509-main.json`):

    trust_mutants: 1 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 0 ALLOWED, 0 NOT RUN in 2019 s
    (M1952 detail: lean/VE/Events/WireExamples.lean:55: Expression)

`--build-timeout 500`, same command otherwise (`m509-main-timeout500.json`). The nightly's detail, word for word:

    UNKNOWN lean/VE/Events/Wire.lean:180 VE.Events.decodeThroughLinks (D[V], trusted) list-empty: (← arrAt b "" "events") -> [] (lean/VE/Events/RouteExamples.lean:62: Expression (Lean could not elaborate it in the probe))

The probe outputs. The tool's `probe` and `settle` were wrapped by a driver script in /tmp; the tool file was not
changed. The mutant's build has 131 refuted checks: 91 in WireExamples and 40 in RouteExamples (lines 62 to 350),
and `settle` probes all of them.

| run | side | file, checks walked | lake rc | seconds | entry for RouteExamples:62 |
|---|---|---|---|---|---|
| default | mutant | WireExamples, 91 | 0 | 27.6 | - |
| default | mutant | RouteExamples, 40 (scoped) | 0 | 669.8 | `done`, hash 18276708281300643823, 5068 consts |
| default | control | RouteExamples, 40 (scoped) | 0 | 633.3 | `done`, same hash, 5070 consts |
| timeout 500 | mutant | RouteExamples, 40 (scoped) | TIMED_OUT | 500.2 | absent |
| timeout 500 | mutant | RouteExamples, all (whole-file fallback) | TIMED_OUT | 500.3 | absent |
| timeout 500 | control | RouteExamples, 40 (scoped) | 0 | 640.6 | `done`, same hash, 5070 consts |

**Why the probe entry is incomplete.** The control elaborates fine. Guard :62 elaborates in both builds and has the
same hash. The mutant's probe of RouteExamples is a single `lake lean` run, and it is killed at `--build-timeout`.
That limit applies to a mutant's probes (`run`'s `lake`), but not to the control's (`first.lake`, no limit). When the
scoped probe times out, the whole-file fallback walks all 92 guards and times out too. Every RouteExamples entry is
then absent. `refusal` gives "Lean could not elaborate it in the probe", and `settle` reports it on the first
refuted row, line 62. Here the probe needs 630–670 s at `--jobs 2`. The nightly ran 24 jobs on ve-cloud-3
(manage-agents CURRENT-STATE.md, 2026-11-09 01:30Z L5: load 46.1/31.6/23.5; reviews/nightly-tm-triage-20261109.md:55)
under the 1800 s default, so it only had to run about 2.7 times slower than this machine to time out.

This cause is inferred, not observed: the nightly's own run log is not on this host. One alternative fits the same
evidence: the probe's `lake lean` crashed or was killed for memory under that load. `probe` keeps only lake's output
(`tools/trust_mutants.py:685`, `[1]`) and drops its return code, so any run that never prints `done` reads as "could
not elaborate" (the docstring's F2/F4). The deadline path is ruled out: it raises `Abandoned` and gives NOT RUN
(`trust_mutants.py:1235-1247`). The nightly run's log (`test-skip/nightly-run-<stamp>.log`, its stderr), or the
pool's memory and load during the run, would tell the two apart.

The masking itself is a defect worth naming. A probe that times out reaches the record as "Lean could not elaborate
it in the probe", not as "did not finish in N s (--build-timeout)". So tm-nightly.py `build_timeout()` (line 345)
never counts it as an infra timeout, and the disposition filed M509 as a test-file fault ("9 build timeouts +
M509").

## Why no test-file fix exists (DO 2, 3)

- **Each walk is slow because of the guard's closure.** One walk of guard :62 (`elaborated envOf`, which reaches
  `runCaseReported`) prints 5,070 `const` entries (outside core, not theorems) and takes 16.3 s in a probe of
  RouteExamples cut at line 63 (commands and outputs: `evidence/variants.md`). The same
  file with `#guard (1 : Nat) == 1` at line 62 takes 2.3 s. Dropping `import VE.Service.DocumentChain` changes
  nothing (15.9 s). The time grows with the closure, not with the environment, and the closure is the claim.
- **About half of that is the walk's own algorithm.** `READS` appends to the end of its worklist with
  `todo := todo ++ …`, which copies the whole list for each constant it visits. A copy of READS changed in memory
  only, with those two lines prepending (`… ++ todo`), gives the same entry (`done`, 5,070 consts) in 8.1–8.2 s
  instead of 16.3 s.
- **The test file cannot cut the number of walks.** The mutant refutes 40 RouteExamples guards, so `settle` walks
  all 40. Fewer walks would mean merging guards, which changes what they check. Moving guards to a new file would
  go outside this item's paths and its 80-line limit. Neither would change the claim at :62, which already
  elaborates.
- **The fix belongs in the tool.** These are the options, for the DRI:
  - (a) a linear worklist in READS, which halves the walk;
  - (b) a probe time limit kept apart from `--build-timeout` (the control has none);
  - (c) carrying a probe's TIMED_OUT (or a crash's return code) into the detail, so that `build_timeout()` counts
    it and a resume reruns it. This is needed under either cause.

  Each is a tools/trust_mutants.py change, so DO (3) applies. Neither (a) nor (b) helps if the cause was memory.

  There is also an operational option, with no code change: give tm-nightly-restart-run a larger
  `--build-timeout`, or run M509 alone. Warning: the restart run (DRI amendment 04:23Z) sweeps on the same loaded
  pools, and it may give this same UNKNOWN again and leave its record incomplete.

## TESTS as asked, and what stands in for them

- The task's "rerun on the branch shows KILLED" and the seeded bug ("revert the fix -> UNKNOWN") need a test-file
  fix, and there is none. Instead, the same command flips with the probe's time limit alone, on unchanged code:
  KILLED at 1800 s, UNKNOWN with the nightly's detail at 500 s. Both records are saved here. No `m509.json` (the
  branch rerun) exists, because no branch fix exists.
- `lake build VE.Events.RouteExamples VE.Events.WireExamples` (no Lean file changed): `Build completed
  successfully (395 jobs).`
- Trust +0: `uv run python tools/trust_map.py --check` prints PASS.
- Seeded bugs: none. No product code changed in any language: the diff is this directory only.

## Delta

DELTA.md: no rows (docs only).

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 0 A, 5 B, 4 C; fixed 9. The fixes: crash/OOM named as an alternative cause, the driver and its logs
saved, the per-walk figures sourced, the TIMED_OUT masking and the operational option added, this section added,
the m509.json condition flagged, the named lake build run, the wording on `const` entries and the import cone.

1. N.A.: no relayed answer, schema or relay changed.
2. PASS. DO (1): the control and mutant probe outputs and the cause are in this report, `m509-main*.json` and
   `evidence/probe-log-*.jsonl`. DO (3): STOP, the DRI message (inbox/dri/20261110T071629Z-tm-m509-route-probe-*.md).
   DO (2) and `m509.json` are not built, because DO (3) applies; this is stated in the first lines. Nothing is
   committed to the tool.
3. PASS: the verdict can go either way on unchanged code. `m509-main.json` is KILLED and
   `m509-main-timeout500.json` is UNKNOWN with the nightly's detail. No product code changed, so no seeded bug is due.
4. N.A.: no Python, Lean or Rust behaviour changed.
5. N.A.: no binding changed.
6. PASS: the final selected run is on the committed HEAD (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select`), and
   only docs are committed after it.
7. PASS: DELTA.md has no rows. `review-ready.py --delta-dri-needed` reserves nothing.
8. N.A.: no user-visible change (DELTA.md).
9. N.A.: no code or test changed. Selection is unaffected.
10. N.A.: no Lean statement or proof changed.
11. N.A.: no budget, limit or deadline changed. The probe's own limit is reported as the tool's issue.
12. N.A.: no product code changed.
13. N.A.: no test removed or renamed.
14. PASS. Both directions: KILLED at 1800 s and UNKNOWN at 500 s. Every number points to a saved file:
    `m509-main*.json`, `evidence/probe-log-*.jsonl`, `evidence/variants.md`, and the lake build line above. The
    spec was re-read: the task file's DO (1)-(3) and TESTS against prompts/task-tm-m509-route-probe.txt.
15. PASS. Overclaim: "no test-file fix" is limited to the item's paths and its rule that the guards' claims stay
    unchanged. "Byte-identical" is limited to `lean/VE/Events/` (`git diff --stat` empty). The cause is marked
    "inferred, not observed". No silent cut: DO (2) is cut by the task's own DO (3). New checks: none. Limits: N.A.
