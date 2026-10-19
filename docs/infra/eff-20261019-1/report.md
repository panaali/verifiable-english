# eff-20261019-1: regen_generated builds and pins ve_service before the entries that start it

No DRI signature is needed. There are no DELTA rows: this is Python tooling only (`tools/regen_generated.py`,
`tools/source_graph.py`, their tests and docs). There is no Lean, Rust or product-code change and no user-visible
product change (trust +0). The full gate is the chain's, on the final HEAD.

Sources read first: PIPELINE-LIMITS.md rows L58 (its open "cure in the repo") and L82, and
reviews/efficiency-daily-20261019.md.

## Stop rule: not met

The defect reproduces on main's tool. I used a scratch worktree of main (`a34ea95ac`, never ve-integration). I added
one definition to `lean/VE/Service/Protocol.lean`, which is inside the service's import closure, and ran
`lake build` (591 s). That changed the ve_service digest:

- before (D0): `5ea6e1f2…4099`, pinned;
- after (D1): `496a16a3…8e11`, not pinned.

Then `regen_generated.py --write` with main's tool stopped after 2 s at `english-lexicon-fixtures`, with
"CheckerUnavailable: … has unlisted build 496a16a3…" (`main-write.log`). `lake-build` and `checker-pins` never ran.

This is the agents' case: they built after a Lean edit, and then the regeneration refused the build. An edit without
a build would not stop main's tool, because the old binary is still pinned. But the users then read a stale build, and
a protocol change gives "unexpected handshake" instead. The new tool also builds first in that case, because Lake
says the build is not current.

## Which entries need the service, and when

I measured this with main's `--check` on the reproduction (`main-check.excerpt.log`: 492 s, 983 KB, 6 tracebacks,
16 "unlisted build" lines) and cross-checked it against the import graph:

| entry | starts the service in | mark |
|---|---|---|
| wire-contract | its check only (the writer runs `--generated-only`) | `check` |
| english-lexicon-fixtures | its writer (and so its check by rewriting) | `write` |
| question-fixtures | its writer and its check (through `tests/question_fixtures.py` → `ve/ask.py`) | `write` |
| route-cases | its writer (and so its check by rewriting) | `write` |
| english-codes | its writer and its check | `write` |
| question-codes | its writer and its check | `write` |
| binding-census | never in --write/--check: it imports `LeanService` inside `record_answers` (only `--record`/`--refresh`) | none (`IMPORTS_ONLY` in the test) |
| history-tests | never: it reaches the client through `test_map → select_tests → answer_replay`, which it does not call | none (`IMPORTS_ONLY`) |
| checker-pins | never: it imports the client only to hash the build (`executable_sha256`) | the bootstrap entry itself |

`binding-census` is in merge-train's candidate-regen list (`cand-regen-entries.txt`: "no Lean build, seconds").
Marking it would have made each candidate regen ask Lake, and possibly build, under its 300 s timeout. That is why
the two import-only entries are left unmarked, and why a test verifies them (below).

The static graph missed `question-fixtures`. `tools/question_fixtures.py` puts `tests/` first on its path and
imports `question_fixtures`, but `source_graph.Graph.resolve` resolved that name to the importer itself. Now
`resolve` never returns the importer. Across the whole repository this adds exactly one edge
(`tools/question_fixtures.py → tests/question_fixtures.py`) and removes none. I compared the full edge maps before
and after.

## What was built

- **`Generated.service`** ("write" | "check" | ""): the one list of the entries that start the Lean service. Its
  place in GENERATED is the order. `--list` prints it.
- **`_Service`** (tools/regen_generated.py) holds the service state for one run:
  - `problem()` asks Lake whether ve_service is current. The query is the lake-build entry's own command plus
    `--no-build ve_service`; Lake exits 3 when the target is missing or out of date, and I measured 0.4–0.6 s. It
    then checks the digest against `lean/checkers.lock`. If Lake cannot be run (`OSError`), only the pin decides,
    as the service client itself does. That keeps a Lake-less `--check --only <user>` working as before.
  - `ready()` runs the `lake-build` and `checker-pins` entries' own steps through `_run(entry, entry.write)`. No
    command is copied. Then it asks again and fails closed if the service still cannot start. The bootstrap's pin
    step runs with `VE_REGEN_NO_RUST=1`, so the Rust pin stays with the ordinary `checker-pins` entry, as today.
  - `ran()`: after a writer changed one of its own files under `lean/` (the lock excepted), Lake is asked again
    before the next user. After the ordinary `lake-build` succeeded, the service counts as current: its step builds
    the default targets, which include ve_service (`test_the_build_entry_builds_the_service`). A pinned and current
    service therefore costs one Lake query per `--write`.
  - `prune()` runs at the end of `write`, in a `finally`. It removes the ve_service pins that `ready` added (the lock
    after the bootstrap minus the lock before it) and that are not the final build. A pin the lock had before is
    never removed.
- **`write`** calls `ready()` before every entry marked `write`, including `--write --only X` when X is marked, even
  though lake-build and checker-pins are not selected then. `--resolve` uses the same `write`, then `check`.
- **`check`** writes nothing. Before the first marked entry it calls `problem()` once. If the service cannot start,
  it prints one line to stderr:
  `regen_generated: the built ve_service <digest> is not pinned in lean/checkers.lock: the entries that start it are not checked; fix: uv run python tools/regen_generated.py --write --only lake-build --only checker-pins (or --write)`.
  The other causes are "not current for the Lean sources" and "not built". It then fails `checker-pins` (not
  pinned) or `lake-build` (not built or not current), and prints `<entry>: not checked: needs the pinned service`
  for each marked entry instead of running it. The final line lists the failed and the not-checked entries, and
  the exit code is 1. The other entries run as before, including `lake-build`'s check (`lake build`), which only
  writes the untracked build. `checker-pins`' check semantics are unchanged; `_service_digest()` now returns None
  for a missing build, and both pin functions report that instead of raising.
- docs/merge-tooling.md section 1 describes the mark, the bootstrap, the pruning and the `--check` behaviour.

## Pins (item 2)

The final lock is the lock at the start (after `--resolve`'s merge, both sides' pins) plus the final build, and the
Rust pin as today. Evidence:

- `test_write_with_an_unpinned_service_bootstraps_once_then_runs_every_entry`: the final pins are `{old, final}`.
- `test_a_bootstrap_pin_the_final_build_supersedes_is_removed`: the first bootstrap pin is removed after a Lean
  writer changed the tree.
- `test_a_pin_the_lock_had_before_the_run_is_never_removed`: a pre-existing pin that equals the bootstrap's own build
  stays.
- `test_resolve_of_two_pinned_sides_builds_and_pins_the_merged_service_in_one_run`: L58/L82 end to end.
- On the scratch reproduction, the lock gained exactly D1 and lost nothing. This held after one `--write`, and after
  the train's two passes.

## Evidence (docs/infra/eff-20261019-1/, numbers in evidence.json)

All runs were on the VM with 32 CPUs and `VE_REGEN_NO_RUST=1`, for both tools alike. The load was 33–72, from other
jobs.

| run | tool | rc | time | 1-min load (start → end) |
|---|---|---|---|---|
| `--write`, D1 unpinned | main | 1, stops at english-lexicon-fixtures | 2 s | 70.7 → 70.7 |
| `--check`, D1 unpinned | main | 1, 11 failed, 6 tracebacks, 983 KB | 492 s | 72.3 → 33.5 |
| `--write`, D1 unpinned (cold dump caches) | branch | 0, 1 bootstrap, 31 entries | 575 s | 67.3 → 46.9 |
| same start state again (warm caches) | branch | 0, 1 bootstrap | 51 s | 46.5 → 67.1 |
| `--check` after that `--write` | branch | 1: trust-tables only* | 69 s | 47.9 → 55.9 |
| `--check --skip trust-tables` after it | branch | 0, 30 entries | 58 s | 59.0 → 55.7 |
| `--check`, D1 unpinned | branch | 1, one cause line, 6 not checked, 0 "unlisted build", 2.4 KB stderr | 52 s | 54.6 → 42.3 |
| `--write --only lake-build --only checker-pins`, then `--write` | branch | 0, 0 | 1 s, 45 s (no bootstrap) | 38.3 → 43.9 |

\* The scratch edit adds 2 unclassified trusted lines to `VE/Service/Protocol.lean`, so the trust ratchet refuses
it, as it should. That has nothing to do with the service. The one traceback in the unpinned `--check` is
`lean-statements` reporting that `declarations.txt` is stale from the edit, which is a correct failure, as on main.

**Merge-train / presync first pass (item 4).** I ran
`VE_REGEN_NO_RUST=1 uv run python tools/regen_generated.py --write --only lake-build --only checker-pins` and then
`--write` on the scratch start state. The first pass succeeds (1 s) exactly as before, because neither selected entry
is marked, so there is no bootstrap and no Lake query. The second run then needs no bootstrap. The lock ends with
the same single added pin as the one-run flow (`check-and-train.log`). So the first pass is redundant now, but still
works. `--resolve` runs the same `write` and `check` functions, as covered by the resolve test above.

Branch HEAD on the real tree, synced with main a671d23b9: a full `--check` asked Lake once, ran every service user
(no "not checked", no bootstrap), and found only `tests/history-dependent.json` stale from this branch's test file. I
regenerated it with `--write --only history-tests` (its own commit).

## Tests (tests/test_regen_generated.py, hermetic)

The fake trees use a fake Lake (`lake.py`: builds `bin/ve_service` from `lean/Source.lean` and answers
`--no-build` like Lake) and a fake service user, which refuses an unpinned or stale build the way the client and the
handshake do. Everything they write is under `tmp_path`, and there are no sleeps or timing asserts.

- `test_write_with_an_unpinned_service_bootstraps_once_then_runs_every_entry`
- `test_a_bootstrap_pin_the_final_build_supersedes_is_removed`
- `test_a_pin_the_lock_had_before_the_run_is_never_removed`
- `test_a_pinned_and_current_service_runs_no_bootstrap`: Lake log = one query plus the run's own build.
- `test_write_only_a_service_user_bootstraps_without_selecting_the_build`
- `test_a_failed_bootstrap_build_stops_the_run_and_names_the_build`
- `test_resolve_of_two_pinned_sides_builds_and_pins_the_merged_service_in_one_run`
- `test_check_with_a_service_that_cannot_start_names_the_cause_once_and_checks_no_user`, for not pinned, not current
  and not built: it writes nothing, prints one cause line with the fix, marks every user "not checked", reports the
  cause entry once, exits 1, and prints no traceback.
- `test_check_with_a_ready_service_checks_every_user_and_asks_lake_once`
- `test_without_lake_the_pin_alone_decides_as_before`
- `test_every_entry_whose_commands_import_the_service_client_is_marked`: the source graph's import closure of each
  entry's scripts, plus the imports of its function steps and the module functions they call. Every importer
  carries the mark, except the two bootstrap entries and the `IMPORTS_ONLY` entries, each with its reason. Removing
  any entry's mark fails the test, which checks this for every marked entry.
- `test_the_entries_that_import_the_client_only_never_start_the_service`: runs the `IMPORTS_ONLY` entries' checks
  with a `LeanService._spawn` that records any start (2 s and 12 s). The positive control is english-codes, whose
  start the trap does record.
- `test_the_build_entry_builds_the_service`: lakefile `defaultTargets` includes ve_service, and the lake-build step is
  plain `lake build`.

The selected tests on the Mac runner (`mac-pytest.sh --select`, HEAD cdc539c34) ran 111 of 448 units in 1994 s, with
0 failed. After that I added the Lake-less test and its fallback, then ran `tests/test_regen_generated.py`: 55
passed. `gate_collection.py --check --prebuilt`: 18226 collected, 14 added, 0 removed, 0 refused, 0 stale,
0 malformed.

## Seeded bugs (docs/infra/eff-20261019-1/seeded-bugs.json; all Python, the only language changed)

Each bug was planted, made its test fail, and was restored:

1. Bootstrap skipped (`tools/regen_generated.py`, `cause = None`):
   `test_write_with_an_unpinned_service_bootstraps_once_then_runs_every_entry` FAILS.
2. Prune removes a pre-existing pin (`tools/regen_generated.py`, `added` without `- before`):
   `test_a_pin_the_lock_had_before_the_run_is_never_removed` FAILS.
3. Prune left out (`tools/regen_generated.py`): `test_a_bootstrap_pin_the_final_build_supersedes_is_removed` FAILS.
4. `--check` runs the dependent entries anyway (`tools/regen_generated.py`, `continue` removed):
   `test_check_with_a_service_that_cannot_start_names_the_cause_once_and_checks_no_user` FAILS.
5. Lake asked again after the run's own lake-build (`tools/regen_generated.py`):
   `test_a_pinned_and_current_service_runs_no_bootstrap` FAILS.
6. english-codes loses its mark (`tools/regen_generated.py`):
   `test_every_entry_whose_commands_import_the_service_client_is_marked` FAILS.
7. `source_graph.resolve` returns the importer again (`tools/source_graph.py`): the same mark test FAILS
   (question-fixtures is no longer seen as an importer).
8. The Lake-less preflight raises (`tools/regen_generated.py`, `raise` in `except OSError`):
   `test_without_lake_the_pin_alone_decides_as_before` FAILS.

## Choices and limits

- **Lake is asked again after a Lean change, not only before the first user.** If a writer (english-lexicon-fixtures
  writes `LexiconFixtures.lean`) changes the service's closure, the next user gets a build of the tree as it is then.
  The superseded bootstrap pin is then pruned. Without a Lean change this costs nothing extra.
- **The bootstrap runs even with `--skip lake-build`**, because the build is a precondition of the selected users,
  not the entry being run. Without it those users fail exactly as before.
- **`--check` does not build in its preflight.** It reports the cause once. The `lake-build` entry's own check still
  runs `lake build` in its place, as before.
- **The eff-20261018-1 dump cache (`tools/lean_dump_cache.py`) is unchanged.** Editing `tools/source_graph.py`
  changes the selector's `CODE_VERSION`, so the shared parse caches rebuild once after the merge. The mark test's
  graph load took about 46 s on a cold cache under load 56.
- **Not run:** the full gate (the chain runs it on the final HEAD) and Rust pinning in the reproduction
  (`VE_REGEN_NO_RUST=1` for both tools).
- **Pre-existing failures:** none hit (main-known-red.txt not involved).

## Build checklist (prompts/build-checklist.txt)

1 N.A. (no diagnostics or limits). 2–9 N.A. (no relayed answer, parser, verdict or English surface).
10 N.A. (one entry point: `main`, and `--resolve` shares `write`/`check`).
11: Lake decides currency (`--no-build`), and the source graph decides imports; neither is re-implemented.
12 N.A. 13: seeded bugs above. 14: hermetic, tmp_path only, HANG_TIMEOUT on the trap's subprocesses, no sleeps.
15 N.A. 16: the mark is generated data covered by the importer test. 17–19 N.A.
20: every number here is in evidence.json with the run it came from. 21: all items are AGENT.
22: the selected tests were run; the full gate is the chain's. 23: no delta.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed or changed. The tool only decides when to build and pin.
2. PASS: each task item is delivered by a test or by the evidence. Item 1: `test_every_entry_whose_commands_import_the_service_client_is_marked`,
   `test_write_with_an_unpinned_service_bootstraps_once_then_runs_every_entry` and
   `test_write_only_a_service_user_bootstraps_without_selecting_the_build`. Item 2:
   `test_a_bootstrap_pin_the_final_build_supersedes_is_removed` and
   `test_a_pin_the_lock_had_before_the_run_is_never_removed`. Item 3:
   `test_check_with_a_service_that_cannot_start_names_the_cause_once_and_checks_no_user`. Item 4: check-and-train.log.
   Evidence: evidence.json. There are no new permanent report tests (D4): the evidence is saved, not tested.
3. PASS: 8 seeded bugs, each failing a named test (seeded-bugs.json).
4. PASS: base and head were run side by side on the same scratch state (the evidence table). On the ready path, a
   full `--check` on the real tree ran every user.
5. N.A.: there is no relayed field to bind.
6. PASS: synced with main a671d23b9 before the final checks. The full gate runs on the final HEAD (chain).
7. PASS: no DELTA rows, no trust growth (tooling only), and no signature reserved.
8. PASS: no user-visible product delta. The tool's own output change is documented in docs/merge-tooling.md.
9. PASS: the selector chose `tests/test_regen_generated.py` for `tools/regen_generated.py` (select.log: 111 units).
   That test fails on every seeded bug above.
10. N.A.: no Lean statement or proof changed.
11. PASS: `test_a_failed_bootstrap_build_stops_the_run_and_names_the_build` (fails closed), with no fixed wall
    deadlines (`HANG_TIMEOUT` only).
12. PASS: a pinned and current service costs one `lake build --no-build ve_service` (0.4–0.6 s) per run
    (`test_a_pinned_and_current_service_runs_no_bootstrap` counts the Lake calls). The timings are in the
    evidence table.
13. PASS: no test removed or renamed. `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
