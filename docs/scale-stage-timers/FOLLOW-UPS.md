# Follow-ups: scale-stage-timers

| Owner | Request | Reason |
|---|---|---|
| Lean service maintainers | Add a ties pass binding `Serve.lean`'s `main` (its two stage-stream lines) to the existing service theorems, or reclassify them with the `VE.Service.StageTimes` diagnostics once a theorem states that the stream changes no stdout byte. | R16 signs the +2 trusted lines now and asks for this ties pass. |
| Scale program (DRI) | Re-measure the whole-request cases of `docs/perf/measure_admission.py` with `VE_READINGS_STAGE_TIMES=1` to read the per-stage split, if item 2 goes the linear-admission route. | Out of scope here (the row asks for the timer and its count test only); the timer is what that reading needs. |
