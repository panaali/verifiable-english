# tm-m509-route-probe: report

**STOPPED at DO (3): only a tools/trust_mutants.py change can judge M509 reliably.** No test file can do it. Nothing is
committed to the tool or to any Lean file. The DRI was told through msg.sh.

## The mutant

The nightly's M509 (test-skip/nightly/20261109T1849Z.json, head 1531891aa, base 039d3dd51) is et-4b-tm's M217:
`VE/Events/Wire.lean:180`, `VE.Events.decodeThroughLinks`, list-empty, `(← arrAt b "" "events")` -> `[]`. That record
is not on this host (`manage-agents/test-skip/` is absent here). On this head, `--only M509` with the default base
names nothing, because the branch has no trusted lines. The same mutant is `M1952` under `--base a270588eb^` (the
parent of et-4b's Wire commit), with the same file, line, definition, operator, before and after. Every run below is
`uv run python tools/trust_mutants.py --base 'a270588eb^' --only M1952 --test lean/VE/Events/WireExamples.lean
--test lean/VE/Events/RouteExamples.lean --jobs 2` on main 65e6e4b0e (this branch had no commits).

`lean/VE/Events/` is byte-identical at et-4b-tm's record head (6be3f873f), the nightly head (1531891aa) and main
(`git diff --stat` empty). RouteExamples.lean has not changed since et-4b-tm judged this mutant KILLED.

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
refuted row, line 62. Here the probe needs 630–670 s at `--jobs 2`. The nightly ran 24 jobs on cloud pools under
the 1800 s default, so it only had to run about 2.7 times slower than this machine to time out. This mechanism is
inferred: the nightly's own run log is not on this host. It is the only one found that gives this exact detail on
unchanged files.

## Why no test-file fix exists (DO 2, 3)

- **Each walk is slow because of the guard's closure.** One walk of guard :62 (`elaborated envOf`, which reaches
  `runCaseReported`) visits 5,070 constants and takes 16.3 s in a probe of RouteExamples cut at line 63. The same
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
- **The fix belongs in the tool.** The options are a linear worklist in READS, or a probe time limit kept apart
  from `--build-timeout` (the control has none). Either is a tools/trust_mutants.py change, so DO (3) applies.

## TESTS as asked, and what stands in for them

- The task's "rerun on the branch shows KILLED" and the seeded bug ("revert the fix -> UNKNOWN") need a test-file
  fix, and there is none. Instead, the same command flips with the probe's time limit alone, on unchanged code:
  KILLED at 1800 s, UNKNOWN with the nightly's detail at 500 s. Both records are saved here. No `m509.json` (the
  branch rerun) exists, because no branch fix exists.
- `lake build VE.Events.RouteExamples VE.Events.WireExamples`: no Lean file changed. A plain
  `lake env lean VE/Events/RouteExamples.lean` passes in 53 s.
- Trust +0: `uv run python tools/trust_map.py --check` prints PASS.
- Seeded bugs: none. No product code changed in any language: the diff is this directory only.

## Delta

DELTA.md: no rows (docs only).
