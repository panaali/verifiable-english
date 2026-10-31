# scale-stage-timers: readings admission stages timed at their production call sites

Status: built, synced with main (`09fca5013`); selected tests pass (below); the chain runs the full gate on the final HEAD.
What changed: the five admission stages time themselves (no mirror); `VE_READINGS_STAGE_TIMES=1` writes one JSON line per production call.
Truth table: 144 request shapes, each run with the timer, with the raw markers and silent; timed lines equal the production markers, answers unchanged; F1-F9 kept as regression tests.
Trust: K +0, S +0, V +2 (`Serve.lean`), R16; trust mutants 8 KILLED, 2 ALLOWED, exit 0.
Open: no DRI signature needed. Follow-ups: the R16 ties pass, and the per-stage re-measurement if scale item 2 needs it (`FOLLOW-UPS.md`).

## Design

Row: reviews/dri-decisions-20261029-scale-admission-profile.md item 2 (backlog `scale-stage-timers`): "one env-gated IO
timer or trace that every production caller of admitS2, admitS2Of, admitSDOf, admitNDFull and distinguishingModels
goes through, with no mirror".

- `lean/VE/Readings/Stage.lean`: `stage name work` and `part name work` write a `dbgTrace` marker before and after
  `work ()`. The closing marker reads the result (`ok` or `error`), so the work runs between the two markers. Their value is
  `work ()` (`stage_eq`, `part_eq`, both `rfl`), so no answer or theorem changes. Every encoder proof that unfolds a
  wrapped runner still builds unchanged.
- The wrapper is inside each stage function, so every caller goes through it, in `Run.lean` and in the wires it
  calls (`VerdictsWire.runVerdicts`'s second `admitNDFull`, `SupVerdictsWire`, `DefaultVerdicts`, `SoftVerdicts`,
  `ComponentsWire.admitPart`). `admitS2`/`admitS2Of` (`SupWire.lean`), `admitSDOf` (`SoftWire.lean`) and `admitNDFull`
  (`UnspecifiedWire.lean`) each wrap their own bodies. Distinguishing models are wrapped where `validateResultBy` computes each
  content-bearing set's pairs: the one place both `setPairsWith` and `setPairsS` are called. The component context
  (`part`) wraps each part in `admitComponents`, `runAdmittedComponents`, the named-component `runAdmitted` calls of
  `runCase` and `runCaseReportedMemo`, the unsplit `runOne`, and the product's `admitPart`.
- `lean/VE/Service/StageTimes.lean`: `ve_service`'s stderr stream (installed by `Serve.lean`'s `main`). Markers are timed
  (`IO.monoNanosNow`, `/proc/self/stat` CPU ticks) into `{"stage","part","status","nanos","cpu_ticks"}` under `=1`,
  passed through under `=markers`, dropped otherwise. All other writes pass through. The pairing (`step`) is pure
  and has `#guard`s.

## Tests

`tests/test_readings_stage_trace.py` (162 tests; `uv run pytest -q -n 8 tests/test_readings_stage_trace.py`: "162 passed in 26.34s"):

- Truth table, one test per cell: kind (`readings-elaborate`, `readings-choice`, `readings-verdicts`) × shape (split
  with a W2 main: fc1; split with a non-W2 main: prefix-50; unsplit: env1/doc1) × component (product, named `main`,
  named companion; unsplit has no companion) × handle (fresh, registered, reused) × admission (ok, failing: a
  duplicate unit). Each cell asserts:
  - the stdout of the silent, timed and `markers` runs is identical;
  - the per-(stage, part, status) counts of the timed lines equal the production-side counter (the `end` markers, each in its
    innermost `enter`);
  - every `part` is a component of the request;
  - a failing cell records an error stage, and an ok cell records none.
  The W2 axis exists in production only for a split main (`admitChecked`, `admitPart`), so unsplit is one shape.
- F1-F9 regressions (scale-admission-profile probes, now read from production lines): F1 split-W2 main admits twice and
  completes; F2 normal client, registered then reused handle; F3 split non-W2 main `admitS2` ×2; F4 named main and
  unsplit enumerated verdicts `admitNDFull` ×2; F5 S1-only validation records nothing, soft validation records
  `admitS2Of`, `admitSDOf`, `distinguishingModels`; F6 a failed main admission records no companion stage; F7 budgeted
  superposed verdicts `admitNDFull` ×2; F8 soft kinds record `admitSDOf`; F9 elaborate records no distinguishing models.
- `lean/VE/Service/MemoExamples.lean`: a new `#guard` checks that `admitComponents` admits `main`, `rs_a` and `rs_b` in order,
  and that `runProduct` answers all three. It kills the trust mutants of the two loops this change wraps.

Seeded bugs (Lean, the only product language changed): `seeded-bugs.json`, four mutants, each 4 failing tests.
A fifth, an off-by-one in `step`'s name parsing, fails the build at `StageTimes.lean`'s `#guard`s and is not counted.

## Probe (not evidence)

`uv run python /tmp/sst-save/cpu.py` (the 185,033-byte constitution as `readings-elaborate`, 3 runs each, 1-min load 58):
process CPU unset 0.931/1.035/1.012 s, `=1` 1.053/1.077/1.071 s; rows `admitS2` 1 (11 ticks) and `admitNDFull` 1 (73 ticks).
No base-versus-head timing was run (no base `ve_service` build on this machine). When the variable is unset, the
added work is two marker writes per stage call and per component (4 on this case).

## Selected tests

`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on `392f6680a` (the synced tree):
- shards 2 and 3 passed (125 and 129 units);
- shard 4 passed 128 of 129 units; the one failure was `tests/test_hang_guards.py::test_no_short_wait_outside_the_reviewed_allowlist`
  (a `nanos >= 0` bound in the new test);
- shard 1 stopped early (`--maxfail 5`) after 2 failing files, with 100 units not run:
  - `tests/test_assurance_manifest.py`: the four wrapped wire files needed new pins, and `StageTimes.lean` needed an
    `other_json` reason;
  - `tests/test_readings_lean_sharing.py`: the IR call graph now shows the stage closures `admitS2._lam_0` and
    `admitNDFull._lam_1`.

`288aebbb3` fixes the three. `zsh mac-pytest.sh -- <the 4 fixed or new files> <the 100 units not run>` then ran on `288aebbb3`
(the Mac had no free slot, so it ran on the VM): "3683 passed, 2 warnings in 3643.11s". No failure of
`main-known-red.txt` was hit.

After the main merge, `tools/trust-classes.json` and `docs/trust-baseline.json` are back in main's text order with
only this item's entries added: the merge driver had reordered them, with the same content. `lean/checkers.lock` keeps
only the final build's pin. `tools/regen_generated.py --check`: "checked 34 entries", exit 0.
`tests/test_trust_budget.py tests/test_trust_ratchet.py`: "112 passed".

