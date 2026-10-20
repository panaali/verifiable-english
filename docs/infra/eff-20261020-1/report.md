# eff-20261020-1: the drift check's binary cutoff (stopped by the stop rule)

**The stop rule is met: the item stops, and this branch delivers only the measurement.** No DRI signature is
needed or reserved. There are no DELTA rows. This branch changes no code: it adds this report, `evidence.json`,
the two replay scripts and `impl-seeded-bugs.json`, all under `docs/infra/eff-20261020-1/`. The full gate is
the chain's, on the final HEAD.

The implementation that the measurement replayed is kept, unmerged, on the local branch
`infra/eff-20261020-1-impl` (commit `073cea86a`, one commit on main `c5197da78`). It is there so the item can
resume if the DRI changes the rule (see "If the item resumes").

Sources: PIPELINE-LIMITS.md row L83. Row L89 and reviews/efficiency-daily-20261020.md do not exist yet. I worked
from the task's own numbers and the eff scripts it names.

## What was measured

I replayed `select_tests.py --commit <c> --json` for main's last 30 first-parent commits (`c5197da78` back to
`3cc70f557`), on the VM:

- **old**: main's tool, from a scratch worktree of main (`/tmp/ve-eff-old`);
- **new**: the drift cutoff from the implementation branch.

`replay.py` holds the commands. `evidence.json` `replay` has one row per commit: map, drift files, drift Lean
files, uncertain old/new, selected old/new, dropped units, both cutoff states, and what the drift rebuilt.

**Records.** I replayed twice. The first time, I used the VM's record store as it was. There the drift cutoff
applied to only 3 of the 12 commits whose drift holds a Lean change. The other 9 had no record of the base's
`lean/` tree. The base is the replayed commit's first parent, and those are often main commits that no one built
on the VM.

So, to measure the rule itself rather than how sparse the records are, I added the 7 missing base records. I
used only `tools/test_map.py build-record`, in the scratch worktree of main, after `lean-prep.sh` and
`lake build` (plus `ve_english_lean_bench`), at `dc10bdfb6`, `673c1ea57`, `e14d56df9`, `bb205adae`,
`9a6ba67ae`, `a34ea95ac` and `208d00af6`. Two of them were restores; five were builds of 9 to 20 minutes.
`evidence.json` `records_added` lists their trees.

The scratch builds do not depend on their path: the builds of `208d00af6`, `a34ea95ac` and `e14d56df9` equal
the VM's records of `b7613541c`, `e010fb6aa` and `d15066d04` (the same programs) in all 9 digests. Then I
replayed both tools again with the same store. Both the old and the new runs use it, so the change-side cutoff
is the same on both sides.

## Stop rule: met

Over the 12 replayed commits whose drift holds a Lean change:

| | old | new |
|---|---|---|
| median selected | 391.5 | 391.5 (fall 0.0%) |
| median uncertain | 370.5 | 227 |
| total selected | 4116 | 3724 (-9.5%) |
| median selected, the store as it was | 391.5 | 391.5 |

Per commit (map → base, `uncertain old→new`, `selected old→new`, what the drift rebuilt):

| commit | map | uncertain | selected | drift rebuilt |
|---|---|---|---|---|
| c5197da78 | 2296317a9 | 68→68 | 82→82 | none |
| 2296317a9 | 75a9bcef9 | 371→81 | 370→84 | none |
| fd68f174a | 75a9bcef9 | 364→71 | 164→58 | none |
| 75a9bcef9 | d15066d04 | 79→79 | 459→459 | none |
| b1f7ca7ad | e2ab87cf6 | 402→402 | 403→403 | response_decode, service, speech_acts_route |
| bfec7f9ef | e2ab87cf6 | 370→370 | 402→402 | response_decode, service, speech_acts_route |
| 88b4626b0 | a671d23b9 | 459→459 | 437→437 | all 9 |
| 630d2e136 | a671d23b9 | 459→459 | 149→149 | all 9 |
| beb5c4630 | a671d23b9 | 459→459 | 438→438 | all 9 |
| 6b1d1b817 | a671d23b9 | 372→372 | 459→459 | 7 (all but conformance, english_run) |
| a671d23b9 | e010fb6aa | 84→84 | 372→372 | none |
| e010fb6aa | b7613541c | 366→79 | 381→381 | none |

The new rule never selected a unit the old one did not; `evidence.json` checks this for every row. It drops
286 units at `2296317a9` and 106 at `fd68f174a`, and none elsewhere.

There are three reasons the median does not move:

1. **In 6 of the 12, the drift really rebuilt `ve_service`** (and others), so the cutoff cannot help. In the
   three `a671d23b9` rows, the drift also edits `ve/assurance-manifest.json` with no safe map, which makes all
   459 units uncertain whatever the build.
2. **In 3 more (`c5197da78`, `75a9bcef9`, `a671d23b9`), the drift built the same programs, but its uncertain
   units came from other files.** The cutoff removes nothing there.
3. **Where the cutoff removes about 290 uncertain units** (`2296317a9`, `fd68f174a`, `e010fb6aa`), the commit's
   own change still selects most of the suite at `e010fb6aa` (a Lean merge: 381). It drops a lot only at the
   two commits whose own change is small.

## Which executables really change, and is Protocol/Registry the cause?

`evidence.json` `transitions` compares every pair of consecutive main commits whose two trees are both recorded.
There are 30 pairs, 25 of them with Lean file changes:

- **15 of the 25 Lean merges changed no compiled program.** df-1ab, et-3c, qt-a1c, me-9, sc-1ab, qt-b1b, jt-1b,
  me-5, et-3b, me-6, df-1a, qt-a2, qt-b1, ap-2 and qt-a1b all built byte-identical executables.
- **10 rebuilt something.** How many of the 10 rebuilt each executable: ve_response_decode 10, ve_service 9,
  ve_speech_acts_route 9; ve_english_route, ve_senses_route and ve_english_lean_bench 6 each; ve_metered 5;
  ve_conformance and ve_english_run 1 each.
- **Protocol/Registry mode additions are not the main cause.** Only 2 of the 10 (ar-10b, lf-18) touched
  `lean/VE/Service/Protocol.lean`, `Registry.lean` or `Serve.lean`. The other 8 changed modules inside
  `ve_service`'s closure. So the service-wide rule is not the reason the rule falls short here: those merges
  changed the program itself.

The task's premise holds (most Lean merges change no program, and the 75a9bcef9 → 2296317a9 range is identical).
But over this window, the drift between a map and the next main commit crossed a merge that changed the
program in half the cases, and the replay metric also counts each merge's own large selection.

## A builder-shaped check (context only, not the stop rule)

A builder's change is usually small and not Lean. `builder_shape.py` plans one small edit at the base of each of
the 12 commits, with the old and the new tool (`evidence.json` `builder_shape`):

| edit | median selected old | new | fall |
|---|---|---|---|
| a line appended to docs/TESTING.md | 101.5 | 74.5 | 26.6% |
| a comment appended to ve/discourse.py | 124.5 | 104.5 | 16.1% |

Where the drift built the same programs, the fall is large (TESTING.md: 104→48, 99→41, 99→41). Over the 12, it
is still below 30%.

## What was not done (the stop rule's "build nothing more")

- **Soundness spot check: not run.** The stop rule stopped the item first. The two candidate commits would have
  been `2296317a9` (286 dropped units) and `fd68f174a` (106).
- Nothing is delivered: the drift cutoff, the gate's record, the TESTING.md paragraph and the tests stay on
  `infra/eff-20261020-1-impl`.
- That branch has no test yet of `tools/gate.py`'s record: the record written after a faked Lean build, and the
  verdict unchanged when the write fails.

## If the item resumes

The implementation on `infra/eff-20261020-1-impl`:

- **`tools/select_tests.py`.** `drift_cutoff` is `lean_cutoff` of the map's commit and the base (sides
  `map`/`base`). `uncertain_since(..., cutoff)` passes its `rebuilt` to `uncertain_units` and then
  `file_impact`, the same code the plan uses. `changed_programs` is the one place where the plan and the drift
  narrow the executables. The uncertain cache is keyed by the executables built differently and by
  `SELECTOR_VERSION`. `--json` has `map_lean_cutoff`, and the plain output prints a "map lean cutoff" line.
- **`tools/test_map.py`.** `record_build(root, names, env)`: a record of some executables keeps what a record of
  the same tree holds for the others. `update` keeps the old behaviour (no cutoff).
- **`tools/gate.py`.** `record_lean_build(env)` runs right after the Lean build stage, for the default-target
  executables, in the gate's own environment. A failure is a warning line, and the gate's result JSON is
  unchanged.
- **Measured but not delivered:** the 58 selector tests pass, including the 7 new drift and record tests (9 cases).

Seeded bugs on that branch (`impl-seeded-bugs.json`). Each one made its test fail, and each was then removed:

- **drift cutoff ignores a differing digest** (tools/select_tests.py):
  `test_a_drift_digest_that_differs_makes_its_runners_uncertain` failed.
- **drift cutoff applied with one record missing** (tools/select_tests.py):
  `test_without_both_drift_records_the_drift_check_is_as_before` failed in 3 cases.
- **the source-reader exception dropped** (tools/select_tests.py):
  `test_a_drift_lean_change_built_the_same_leaves_its_runners_certain` failed.
- **a partial record drops the others of its tree** (tools/test_map.py):
  `test_a_record_of_some_executables_keeps_the_others_of_its_tree` failed.

The fourth seeded bug the task asks for (gate.py's record failure fails the gate) is not planted, because the
gate test is not written.

The records are what limits the rule in practice. On the VM, 9 of the 12 base trees had no record. The gate's
record addresses this; the replay above shows how much it would add once records exist.

**Orchestrator lines** (only if the item resumes): after its Lean build, x86-essentials.py would add one call,
`uv run python tools/test_map.py build-record`.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is read or relayed.
2. PASS: every directive line is answered above. The measurement is in `evidence.json`. Items 1–3 are not
   delivered, by the stop rule (stated as the reason). The diff holds no Python copy of a Lean decision and no
   permanent report test.
3. PASS (implementation branch): 4 seeded bugs, each caught (`impl-seeded-bugs.json`). This branch changes no code.
4. N.A.: no Python, Lean or Rust behaviour changes.
5. N.A.: no relayed field.
6. PASS: the chain runs the gate on the final HEAD. The batch numbers are saved in `evidence.json`, not checked
   by a test.
7. PASS: no DELTA rows and no trust growth; no signature needed.
8. N.A.: no user-visible change (docs only).
9. N.A.: the selection for a docs-only diff is unchanged. The new rule never selected more than the old one in
   the replay (`evidence.json` `replay`, `dropped_units`; no row added a unit).
10. N.A.: no Lean.
11. N.A.: no budget or deadline code.
12. N.A.: no product code. The selector's own cost is unchanged: the median replay row took 3.8 s (old) and 3.0 s (new), with warm caches.
13. N.A.: no test removed or renamed.
