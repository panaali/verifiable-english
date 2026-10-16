# Test architecture rank 9 (part): shared Lean builds with platform provenance, and obsolete executables

**DRI decision needed (one, about wiring, not about code in this branch):** whether the merge train's candidate verify (R2)
may call `restore` (section "Wiring" below). The tool works either way; my recommendation is: R2 may, R3 never.

Plan: `test-architecture-2026-10-14.md` draft 2, section 3.8 ("Shared builds", "Obsolete executables") and rank 9 of
section 4, with Astra's re-check (ADOPT WITH CHANGES) points 7 and 8. Branch `infra/tarch-leanshare`, from `dae12d5ff`,
synced with main `21029b86e`. Files: `tools/lean_share.py` (new), `tools/lake_outputs.py`, `tests/test_lean_share.py`
(new), `tests/test_lake_outputs.py`, and this directory. It does not touch `tools/select_tests.py`, `tests/conftest.py`,
the import-time modules, `lean/VE/Audit.lean`, `tools/gate.py` or manage-agents. Out of scope (DRI trust-boundary
sign-off): splitting `VE.Audit`, the audit evidence contract, collection without Lean.

## Delivery

| Plan or directive line | Delivered | Test |
|---|---|---|
| 3.8: shared builds "keyed by the `lean/` tree hash, the toolchain, the architecture and the lake manifest" | `lean_share.key`: `lean_tree` (SHA-256 of `git ls-tree -r HEAD` under `lean/`, without `lean/checkers.lock`, which no build reads; `lean/` must equal HEAD), `toolchain` (`lean --version`, `lake --version`, and the 10 variables Lake 4.24 reads to choose its compiler, archiver and toolchain), `platform` (OS and `uname -m`), `lake_manifest` (SHA-256), `pins` | `test_a_build_of_another_tree_is_never_offered`, `test_a_build_of_another_architecture_is_never_offered`, `test_a_build_of_another_toolchain_is_never_offered[lean,lake,env]`, `test_a_build_lake_finds_out_of_date_or_a_dirty_tree_is_never_stored_or_restored` |
| 3.8: "immutable once their pins are written" | `publish` fills a scratch directory, writes the pins (for a runner-local authority, the runner's pins file), then the seal `pins.json` (key, SHA-256, size and mode of every file, checker digests), makes the entry read-only and renames it into place; a sealed entry is never rewritten, a second publish keeps the first | `test_runner_local_pins_are_their_runners_alone`, `test_a_tampered_entry_is_refused_and_withdrawn` |
| 3.8: "checked by `tools/lake_outputs.py` and the pins before use" | `restore`: (1) the seal's key is the worktree's; (2) the entry holds exactly the sealed files with their SHA-256 (a failing entry moves to `refused/`); (3) every pinned checker (`ve_service`) is pinned by the key's authority; (4) in the worktree, `lake_outputs.stale` and `lake_outputs.obsolete` are empty and `lake build --no-build` passes; otherwise the previous `lean/.lake` is put back. The copy is staged under `lean/.cache/` (ignored by git), so a restore killed midway never leaves the worktree dirty for the gate's clean-tree check | `test_a_tampered_entry_is_refused_and_withdrawn[5 victims]`, `test_a_checker_the_authority_does_not_pin_is_refused`, `test_a_forged_seal_for_another_tree_is_refused_by_lake_and_the_worktree_restored`, `test_a_restore_killed_while_it_copies_leaves_nothing_git_sees`, `test_a_restore_that_died_midway_leaves_the_worktree_clean_and_is_cleared` |
| Task: x86 pins are `lean/checkers.lock`; Mac pins are runner-local; "the key and the check must say which runner's pins"; aarch64 never offered to x86 or the reverse (Astra 7; Astra 8: key on actual digests, not "pinned" ones) | `pins` is `lean/checkers.lock` (default on x86_64) or `runner-local:<runner>` (default elsewhere: the host name; pins in `<store>/pins/<runner>.json`). The checker digests are the files' actual SHA-256, re-hashed at every restore. Platform and toolchain (whose version line names the target triple) are both in the key | `test_the_default_authority_is_the_lock_on_x86_and_the_runners_own_pins_elsewhere`, `test_runner_local_pins_are_their_runners_alone`, the architecture test (both directions) |
| Task: "A build whose key or check does not match is never used (fall back to building)" | Any refusal is exit 3 and leaves the worktree as it was; the caller's `lake build` then builds as before | the other-tree, tamper, pins and forged-seal tests assert the worktree's `lean/.lake` is as before; `test_the_command_line_off_switch_and_prune` (exit 3) |
| Task: "Provide the restore command" | see Wiring | `test_the_command_line_off_switch_and_prune` |
| 3.8: obsolete executables, "a new rule ... separate from `drop_stale`'s trace check" | `lake_outputs.executables` (Lake's file name per `lean_exe`, `exeName` honoured; a `lakefile.lean` or a name it cannot tell is an error, so nothing is removed on a guess), `obsolete`, `drop_obsolete`, `--obsolete`, `--drop-obsolete`. A file is live only as `<exe>`, `<exe>.trace`, `<exe>.hash` or `<exe>.sha256-cache` | `test_a_removed_targets_binary_is_obsolete_and_a_live_ones_files_are_kept`, `test_targets_it_cannot_name_remove_nothing[5]`, `test_a_lakefile_only_lake_can_evaluate_removes_nothing`, `test_the_repositorys_executables_are_its_lakefiles_targets` |
| Measure: Lean build of a fresh worktree with and without the share, and disk saved | below; raw numbers in `evidence/measurements.json` | – |

**Sharing on disk.** `.olean` files and executables are shared as read-only hard links when the store is on the same file
system; everything else is copied. This rests on a measured fact about the pinned toolchain (strace, Lean 4.24): Lean
writes an `.olean` to `<file>.tmp.<pid>` and renames it, and the linker unlinks the executable and renames a temporary
file over it, so a later build in the worktree replaces its links. Lake writes `.c`, traces, `.ilean` and
`.setup.json` in place: a first experiment that hard-linked the whole build corrupted the source's `Tiny.c` and traces,
so those files are copied. A read-only link turns any in-place write into an error instead of a silent change, and
every restore re-hashes the whole entry. On the real tree, the publishing worktree then rebuilt for lf-14c, replacing
its links, and `verify` still passed on the store. `--copy` never links.

## R2 and R3 stay complete, live and without reuse

- `tools/gate.py` is not changed and never reads the store. It still runs `drop_stale`, its own `lake build` (which
  rebuilds whatever Lake's traces do not match), the stale check, the binaries check, the audit, and the Rust pins.
- The nightly (R3) must not restore: `VE_LEAN_SHARE=off`, or simply no `restore` call, so that it compiles every module
  from its sources each night. That run also catches a bad entry or a build that is not reproducible.
- Every check that exists today still runs where it can fail. The obsolete rule removes only files that no lakefile
  target names; `drop_stale` is unchanged.

## Wiring (exact commands; the orchestrator wires them, nothing in manage-agents was edited)

In a worktree, or the train's candidate worktree, before its Lean build:

```
python3 tools/lake_outputs.py --drop-obsolete      # files no lakefile target names (2.0 GiB in each worktree that has them)
python3 tools/lean_share.py restore || true        # exit 0: restored and checked; exit 3: nothing usable (reason on stderr)
(cd lean && lake build)                            # unchanged: a no-op after a restore, the usual build otherwise
python3 tools/lean_share.py publish || true        # after a successful build: offer it to the next worktree of this tree
```

- On the Mac runner the same commands default to `--pins runner-local:<host name>`. Their store is `~/.cache/ve-lean-share`;
  set `VE_LEAN_SHARE=<dir>` to put it on the same file system as `~/pyt` and `~/jobs`, so links work.
- The runner's own `regen_generated.py --only checker-pins` step stays as it is.
- Pruning: `python3 tools/lean_share.py prune --keep 8` (for example daily). A worktree that restored an entry keeps its
  files, because they are its own links.
- **Decision for the DRI:** R2 restoring means the candidate's Lean modules were compiled by an earlier `lake build` of
  the identical tree on the same runner, not in the candidate's checkout. The entry is bound to that tree by its hashes,
  by the pins and by Lake's own traces.
  - Today's runners already seed R2 from a neighbour's build with no check: the Mac copies a gate job's `lean/.lake` by
    reflink. On the VM, `ve-integration`'s build turned out to be out of date for its own tree (`VE.Surface`).
  - So restoring is no weaker than today's seeding and is checked. It is still reuse, which R2's rule forbids.
  - Recommendation: allow it in R2 and keep R3 a full build. Otherwise call `restore` only in R0/R1 worktrees and
    builders.

## Measured effect

| | Mac (ve-mac-1, aarch64, 18 cores, load 42 → 24) | VM (x86_64, 32 cores, load 68–79) |
|---|---|---|
| Fresh worktree, no share: cold `lake build` | **492 s** (931 jobs) | **1,589 s** (26.5 min; user 5,996 s) |
| Fresh worktree, share hit: `restore` + `lake build` | **2.0 s + 0.4 s** (links); 3.1 s + 0.4 s (`--copy`) | **7.3 s + 0.5 s** (links) |
| `publish` (once per tree and runner) | 3.8 s | 36 s |
| A neighbour's build copied, then `lake build` (today's seeding) | 491 s (mac-pytest setup: reflink seed from another tree, build, pins) | 1,834 s (458 targets: the neighbour's build was out of date) |
| `lean/.lake` of one worktree | 2.24 GB | 2.2 GB |
| Disk a restored worktree adds (links) | **185 MB** (`du` of publisher, store and restored worktree together: 2,425,432 → 2,610,296 KiB) | **178 MB** |
| Disk the store adds beyond the publishing worktree | 185 MB | 179 MB |
| Disk a `--copy` restore adds | 2.24 GB | – |

- **Disk saved:** about 2.05 GB for each worktree that restores instead of building (VM 2.2 GB → 178 MB; Mac
  2.24 GB → 185 MB).
- **Duplicate builds now on the VM:** 23 worktrees with a build hold 8 distinct `lean/` trees, and 32.3 GiB of live
  build is held more than once. Est. ~29 GiB of that would be links if those worktrees had restored.
- **Obsolete executables on the VM:** 9 of 23 worktrees hold the same 12 obsolete executables, 2.0 GiB each, 18.0 GiB in
  all. That disk comes back on the first `--drop-obsolete`. The VM disk was at 91% when measured.
- None on the Mac runner's persistent checkouts.
- Caveats: single runs; elapsed time depends on the runner's load (Mac load fell from 42 to 24 during the cold build).
  The Mac run used the test's `tmp_path`, which is tmpfs there. Durations here are scheduling data, and no test asserts
  one.

## Seeded bugs (Python: the only language this branch changes)

Each was planted in a changed file, the named test ran on the VM and failed at the assertion shown, and the file was
restored byte for byte (`git status` clean afterwards). Committed as `mutants.json`.

| Bug | File | Fault | Test that failed |
|---|---|---|---|
| S1 | `tools/lean_share.py` | the `lean/` tree left out of the key | `test_a_build_of_another_tree_is_never_offered` (the other tree's build was offered; Lake then refused it) |
| S2 | `tools/lean_share.py` | the platform left out of the key | `test_a_build_of_another_architecture_is_never_offered` (DID NOT RAISE) |
| S3 | `tools/lean_share.py` | the toolchain left out of the key | `test_a_build_of_another_toolchain_is_never_offered` (DID NOT RAISE) |
| S4 | `tools/lean_share.py` | entries checked by size, not SHA-256 | `test_a_tampered_entry_is_refused_and_withdrawn` |
| S5 | `tools/lean_share.py` | the pins not checked | `test_a_checker_the_authority_does_not_pin_is_refused`, `test_runner_local_pins_are_their_runners_alone` |
| S6 | `tools/lean_share.py` | Lake's up-to-date check skipped | `test_a_forged_seal_for_another_tree_is_refused_by_lake_and_the_worktree_restored`, `test_a_build_lake_finds_out_of_date_or_a_dirty_tree_is_never_stored_or_restored` |
| S7 | `tools/lean_share.py` | a refused restore does not put the worktree's build back | `test_a_forged_seal_for_another_tree_is_refused_by_lake_and_the_worktree_restored` |
| S8 | `tools/lake_outputs.py` | a file that starts with a live target's name counts as live | `test_a_removed_targets_binary_is_obsolete_and_a_live_ones_files_are_kept` |
| S9 | `tools/lake_outputs.py` | a live executable's `.hash` counts as obsolete | `test_a_removed_targets_binary_is_obsolete_and_a_live_ones_files_are_kept` |
| S10 | `tools/lean_share.py` | traces and `.ilean` shared as links | `test_a_stored_build_restores_up_to_date_and_never_shares_a_file_lake_rewrites` |
| S11 | `tools/lean_share.py` | a restore stages its copy beside `lean/.lake`, where git sees it | `test_a_restore_killed_while_it_copies_leaves_nothing_git_sees` |

A first S2/S3 variant mutated `machine()` and `toolchain()` themselves. The tests replace those functions, so it only
broke the test's setup. Both were re-seeded where those values enter the key, and both fail at the refusal assertion.

## Tests and runs

- New and changed files: `tests/test_lean_share.py` 20 tests and `tests/test_lake_outputs.py` 19 tests, all passing on
  the VM. `test_lean_share.py` builds a real one-module Lake project with the pinned toolchain in a private git
  repository under `tmp_path`, so it needs no network and no cache.
- `mac-pytest.sh --select` on `1c0fbe57e` (54/395 units) had 2 failures, both caused by this branch and fixed in
  `0143f7e62`:
  - `test_a_checker_the_authority_does_not_pin_is_refused` assumed x86's default authority; on aarch64 the default is
    the runner's own pins. The test now names the lock.
  - `tools/test_layer_policy.py::test_non_default_lean_executables_are_built_by_name` failed because my known-answer
    test named `ve_english_lean_bench` literally. The selector's static graph read that as a use of the binary and
    added it to the plan's named build. The test now compares with `layer_policy.lean_executables()`. The same test
    passes on main in a clean clone, and it passed again here after the fix.
- After the sync with main (lf-14c), `select_tests --base <merge base>` picks all 396 units: the coverage map is
  92 files behind (the plan's cause B), not this change. That run outran my 58-minute limit (exit 124, no
  result). Since the 54-unit run only this branch's own files changed, so I ran the units they can reach:
  `test_lean_share`, `test_lake_outputs`, `test_hang_guards`, `test_select_tests`, `test_repo_map`,
  `test_inventory_lint`, `test_nested_pytest`, `test_single_owner`, `test_regen_generated` and `test_gate`.
  **488 passed** (mac-pytest fell back to the VM: no Mac slot within 30 min). `tools/test_layer_policy.py` passed
  on the VM.
- `tools/check_python_layers.py`, `tools/regen_generated.py --check` and `tools/gate_collection.py --check --prebuilt`
  all pass: 26 added, 0 removed, 0 refused, 0 stale, 0 malformed. No test was removed or renamed against main.
- `main-known-red.txt`: none of its three tests is touched here.
- Not run by me: `tools/gate.py` (the chain runs it on the final HEAD). The relay mutation gate does not apply: no file
  under `ve/` or `lean/` changed.

## AGENT, HUMAN, EXTERNAL

- AGENT: everything above.
- EXTERNAL:
  - the chain's full gate on the final HEAD;
  - wiring the commands into the runners and the train;
  - the one-time `--drop-obsolete` in the 9 VM worktrees (not mine to edit);
  - the DRI decision on R2.
- HUMAN: none.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer is read or changed.
2. PASS: every plan row and directive line is in the Delivery table with its test. No permanent report test was added
   (D4): the evidence is saved in `evidence/measurements.json` and checked by no test. The diff decides nothing Lean
   owns. No other `infra/tarch-*` branch changes any of this branch's files (checked against each branch's merge base).
3. PASS: S1–S11 (`mutants.json`), each failing at its assertion. The refusal tests cover a changed value (tree,
   platform, toolchain, pins), a missing record (missing file, no stored build) and an extra one (planted file).
4. N.A.: no checker semantics changed. A valid build still restores and stays up to date
   (`test_a_stored_build_restores_up_to_date_and_never_shares_a_file_lake_rewrites`; the real tree on the VM and the Mac).
5. N.A.: no Lean answer fields. The analogous binding here is the seal to its entry name and to the worktree's key:
   `test_a_build_of_another_tree_is_never_offered` (an entry moved under another key is refused).
6. PASS: synced with main `21029b86e` (ts-B3) last; after it the Lean build and `tools/regen_generated.py --check` (25 entries) passed, and my two test files passed again (39). The gate runs on the final HEAD in the chain, and the
   evidence is saved, never computed against a live diff.
7. PASS: no unsigned DELTA row (`DELTA.md`: no user-visible change in VE's output). The one open item is the R2 wiring
   decision, named in this report's first line. The exit code on every refusal is tested
   (`test_the_command_line_off_switch_and_prune`; `main` returns 3 on Refused, OSError and RuntimeError).
8. PASS: `DELTA.md` lists the tooling additions; VE's outputs, codes, texts and verdicts are unchanged.
9. PASS: `select_tests --base` picks 54/395 units and includes `test_lean_share.py` and `test_lake_outputs.py` for these
   files. Its failure on a literal executable name was traced and fixed (above).
10. N.A.: no Lean statement or proof.
11. PASS (where it applies): no sleep or wall-clock assertion. Every wait in the tests is `HANG_TIMEOUT`, and the tool's
    waits follow `VE_LEAN_TIMEOUT`.
12. N.A.: no checker CPU path. The restore costs 2–7 s against a 492–1,589 s build (measured above).
13. PASS: no test removed or renamed against main. `tools/gate_collection.py --check --prebuilt` reports 0 refused,
    0 stale and 0 malformed.
