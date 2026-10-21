STOP RULE (both rules fire, measured): only 2 of the 34 corpus mutants are SURVIVOR at their reviewed tree and KILLED at their fixed tree with the proposed operators and pytest kill mode (8 needed); and on me-6b's reviewed HEAD with its own fixture file, the pytest phase alone takes 569 s against the 55 s Lean-only sweep, 10.35× (3× allowed). No implementation of `--pytest` or new operators is retained.

# eff-20261021-1: measured stop

The first review (FIX) found that the stop rested on an invalid timing run (F1) and that the corpus was never replayed (F2). Both measurements are now taken and checked from raw tool output. `python3 docs/infra/eff-20261021-1/verify_evidence.py` exits 0: "pairs 2 (stop below 8); pytest phase 10.35x the Lean-only sweep (stop above 3x); fired: ['pairs', 'time']; 0 problems".

## Rule 2: the pytest phase on me-6b's reviewed HEAD (review F1)

The tool measured is [prototype.patch](prototype.patch): `tools/trust_mutants.py` at the merge base `7855620f3`, plus the tier-4 operators and a `--pytest` phase. That phase runs after the Lean phase, over its SURVIVORs only, and is timed on its own (`phases` in the JSON). It builds `ve_service` in an unmutated scratch and runs the named tests there as the control. Then, in clones of that scratch, it builds each mutant's `ve_service` and runs the same tests with `VE_LEAN_SERVICE` pointing at it. Both sweeps ran on the VM (ve-mac-1 offline) at `82c0e6ad8`, base `c5197da7`, with `--jobs 4`, `--max-mutants 40` and `VE_LEAN_SHARE=off` (no shared build of this tree exists). Every scratch copied the checkout's `lean/.lake`. Before both runs, `lake build VE.Calc.Units` (124 s) built what the fixture file's `lake env lean` reads.

| Sweep | Time | Verdicts |
| --- | ---: | --- |
| [Lean only](lean-only.json) | 55 s | 30 SURVIVOR, 9 UNKNOWN, 1 INVALID |
| [`--pytest tests/test_calc_units.py`](pytest-attempt.json): Lean phase | 38 s | the same 40 verdicts |
| the same run's pytest phase | **569 s** | control PASS (70 tests) in 391 s; all 30 SURVIVORs built and tested in 178 s; 0 KILLED-BY-PYTEST |

The pytest phase alone is 10.35× the Lean-only sweep. Even without its one-off control build, the per-mutant part is 3.2×. All 30 stay SURVIVOR. The reviewed fixtures compile an outside Lean file with `lake env lean` in the checkout, which reads the checkout's build. `VE_LEAN_SERVICE` cannot redirect them to the mutant (`tests/test_calc_units.py`, `tests/lean_build.py` at `82c0e6ad8`). The fixed tree of ap-1b confirms the cost is per mutant, not one-off: its single SURVIVOR's pytest phase took 457–509 s, against a 2–3 s Lean phase ([replay/ap-1b-fixed-proposed.json](replay/ap-1b-fixed-proposed.json)).

The superseded runs, kept in `evidence.json` `superseded`, timed 265 s and 862 s. They named `test_fixture[factor-below-one]` and `[refuse-base-identifier]`, which only the fix `db34c272d` adds. So the control errored, no mutant was built, and the ratio compared the whole sweep.

## Rule 1: the corpus replay (review F2)

[replay.py](replay.py) replays every one of the 34 rows, at its reviewed tree and its fixed tree, under two tools: today's tool (the merge base's) and the proposed one. Each run is in a detached worktree. For me-2 the fixed tree is `573a703c8`, since `fc118c879`'s `declarations.txt` is stale: the next commit only regenerates it. For each tree, the tool's own `plan` names the row's definition and its trust_map class. It also says whether the tool selects the definition and which mutants either operator set writes on the row's line. The row's `replay` mutant is the reviewer's form, or the tool mutant with its behaviour at that line. That one mutant is then run through the tool's unchanged `main`. The raw output is in [replay/](replay/), and `evidence.json` columns `measured`, `legacy_verdict`, `fixed_verdict`, `pair` and `gap` are derived from it by `replay.derive`, the one owner of that rule.

| Gap (measured) | Rows | What the replay shows |
| --- | ---: | --- |
| unselected | 19 | trust_map does not count the definition as trusted: classes C (me-5 eliminate, me-9 `fits`, all 7 me-9b rows), G[R] (me-5's limits), G[V] tied (df-1ac W9 `pairs`), D[I] and D[R] (me-2's hash parts, `supports`, span, literal and scan). The tool never mutates them, so neither new operators nor a pytest phase reaches them. |
| G1 | 9 | selected, and no operator, today's or proposed, writes the form: ap-1a slots-length and permission/obligation-canonical, me-6b base-identifier (`identifier s` → `true`), and me-2 rounds hash tags, within-bounds order, software-hash and claim-id-char |
| G1, its line's generated form already KILLED | 1 | df-1ac W10: `eq-ne` at Wire.lean:265 is KILLED at the reviewed tree. The reviewer's `match true, …` is not generated. |
| open | 1 | ap-1a form-any-role: `and-or` is SURVIVOR at both trees, because the killing check, `lean/VE/Acts/LexicalExamples.lean:195`, is outside `VE/Norms`. With `--deep`, it is KILLED at the reviewed tree already (4,430 s). |
| **pair**, today's Lean phase | 1 | me-6b factor-below-one: `lit-plus` SURVIVOR → KILLED by `lean/VE/Calc/UnitsExamples.lean` |
| **pair**, G1 and G2 | 1 | ap-1b acts-fixed-premise: the proposed `arm-wildcard` (`| false, .ok block` → `| _, .ok block`) is SURVIVOR → KILLED-BY-PYTEST by `tests/test_acts_profile.py::test_without_acts_an_invalid_block_is_not_read` |

That is 2 pairs, and 8 are needed. The proposed design reaches at most 2 of the 34 hand mutants: one through the pytest phase, and one that today's tool already finds. Corrections against the first submission, all measured:
- Its "12 rows today's operators generate" were 3. The me-5 limits, me-9b's points, df-1ac W9 and me-2's supports and span are in untrusted definitions.
- Its "13 G2" rows are 0 pure G2. The only pytest kill also needs a new operator.
- The ap-1a fixtures are in `lean/VE/Acts/LexicalExamples.lean:110,189,190,195`. `lean/VE/Norms/ActsExamples.lean` does not exist at `ce7de0760`.
- Four row lines were off by one or six; `line` now gives the reviewed tree's.

## Build outcome

The committed change is evidence only: REPORT.md, `evidence.json`, the two sweeps, `replay/`, `replay.py`, `verify_evidence.py` and `prototype.patch`. The prototype is a measurement tool, kept as a patch so the sweeps can be rerun. It is not retained: its inputs digest does not yet cover the executables' digests, and its tests were reverted. `tools/`, `tests/` and every product, Lean, Rust and generated file are byte-identical to the merge base. There is no user-visible VE delta and no trust growth, so there is no DELTA table and no DRI signature.

Regression checks: `verify_evidence.py`, the saved-evidence check (architecture decision D4: no new permanent report test). It now recomputes both rules from the raw JSONs, from git and from `replay.derive`, never from constants copied from `evidence.json` (review F3). It checks four things. Every `--pytest` argument must be a test of the swept tree, the control must pass, and the set of mutants the pytest phase built must equal the Lean-only SURVIVORs (PROBE F1). Every row must be replayed in both trees under both tools, and `evidence.json` must state what the replay gives (PROBE F2).

Seeded bugs, each planted, `verify_evidence.py` run (exit 1 each), then restored:
1. `evidence.json`: me-6b factor-below-one `fixed_verdict` set to UNMEASURED. Fails: "does not state the replay".
2. `pytest-attempt.json`: `--pytest` set to the superseded `test_fixture[factor-below-one]`. Fails: "no such parameter at 82c0e6ad8f46".
3. `pytest-attempt.json`: one SURVIVOR's `pytest_executables` emptied. Fails: "built and tested 29 mutants, not the 30 Lean SURVIVORs".
4. `verify_evidence.py`: the ratio taken over the whole sweep (the original F1 error). Fails: ratio 10.35 recorded, 11.31 measured.
5. `replay.py` `derive`: a mutant KILLED at the reviewed tree counted as a pair. Fails: df-1ac/W10 pair, "pairs 2, measured 3".
6. `replay.py` `status`: the NOT SELECTED case removed. Fails: 19 rows "does not state the replay".

No full release gate was run, as directed. The selected tests are reported in the build final.

## Follow-ups (not built here)

- Half the corpus (19 of 34) is in definitions R16's sweep never selects: reject-only, identity, checked and tied code. Those are the decoder and limit checks that reviewers mutate by hand. Whether `trust_mutants` should also sweep D[R], D[I], G[R] and C definitions, as evidence only, is a separate decision, and the lever this measurement points at.
- The 9 G1 rows need forms beyond the prototype's tier 4: a guard replaced by `true`, a string tag changed, list elements swapped, a function replaced by another namespace's. None alone reaches 8 pairs.
- A pytest phase pays off only for fixtures that go through `ve_service`. Those that run `lake env lean` in the checkout (me-6b, me-9, me-9b) would need a test-helper change to read a scratch tree, which needs a DRI decision.
- Orchestrator lines: none proposed. BUILDER-CHECKLIST 3 and build-checklist.txt 13a stay as installed. Reviewers keep planting the forms listed in the G1 row and, for ap-1a-like layouts, run `--deep`.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean response route or schema changed.
2. PASS: the stop decision, corpus replay and both sweeps are saved evidence, checked by `verify_evidence.py`.
3. N.A.: no trusted Lean change. `tools/trust_mutants.py` was the instrument, run on the corpus trees.
4. N.A.: no product behaviour changed.
5. N.A.: no relayed field changed.
6. N.A.: the chain runs the final-HEAD gate.
7. PASS: no DELTA row and no trust growth; `git diff main...HEAD` holds only `docs/infra/eff-20261021-1/`.
8. PASS: no VE output changed.
9. PASS: the selected tests for this diff were run (build final).
10. N.A.: no Lean statement or theorem changed.
11. N.A.: no public budget, limit or deadline changed.
12. N.A.: no runtime product path changed; the times above are the task's measurement.
13. PASS: no test removed or renamed.
