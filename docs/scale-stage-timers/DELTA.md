# User-visible deltas: scale-stage-timers

Base: the merge base with `main` (`ea269e96c`). No answer changes: stdout is byte-identical with the variable unset,
`0`, `1` or `markers` on every truth-table cell (`tests/test_readings_stage_trace.py::test_stage_times_count_the_production_markers`).

| Delta | Before | After | Test or evidence | Ruling |
|---|---|---|---|---|
| `VE_READINGS_STAGE_TIMES=1` makes `ve_service` write one JSON line per production call of `admitS2`, `admitS2Of`, `admitSDOf`, `admitNDFull` and each set's distinguishing models (`stage`, `part`, `status`, `nanos`, `cpu_ticks`) on stderr; `=markers` writes the raw production markers instead; unset or any other value stays silent | no stage lines (the profiler of scale-admission-profile was withdrawn) | the lines; every other stderr write passes through unchanged | `test_stage_times_count_the_production_markers` (each timed line equals a production marker, per stage, component and status; every `part` is `main` or a reading set of the request), `test_stage_times_are_silent_by_default_and_pass_other_stderr_through`, F1-F9 regression tests in the same file | R3 (DRI-RULINGS.md): information is added and nothing is removed or renamed; the lines are Lean's own markers and each component name is bound to the request |
| Trusted Lean growth against `ea269e96c`: K +0, S +0, V +2 (`Serve.lean` +2: `main` installs the stage stream). `VE/Readings/Stage.lean` and `VE/Service/StageTimes.lean` are G[R] (diagnostic: `stage_eq`, `part_eq` prove by `rfl` that a wrapped stage's value is its work's own); the five stage functions and the part loops wrap on their existing lines (+0) | V at base | V +2, allowance in `docs/trust-baseline.json` | `uv run python tools/trust_map.py --check` (`Serve.lean: trusted +2`); `test_stage_times_are_silent_by_default_and_pass_other_stderr_through` fails if `main` stops installing the stream (the markers would then reach stderr raw; the seeded `.off` leak in `seeded-bugs.json` shows the test catches leaked markers); `docs/scale-stage-timers/trust-mutants.json` (8 KILLED, 2 ALLOWED, exit 0); ties follow-up in `FOLLOW-UPS.md` | R16 (DRI-RULINGS.md): within 150 lines and no K growth |

Not a product output, so not a row: `lake build` now prints, as `info` messages that Lake replays on cached builds,
the markers of the build-time `#guard`s that run a readings stage (2,384 lines on a full build, from
`VE/Readings/ActsExamples.lean`, `VE/Service/MemoExamples.lean` and `VE/Service/ScopeExamples.lean`). No `#guard_msgs`
reads them (the full build passes).
