# AR-5a: the evidence toolkit

Plan: `docs/ARCHITECTURE-REVIEW-2026-10.md` (branch `design/arch-review`), section 4.3, row AR-5a, and
DRI decision D4. A batch now describes its evidence in `docs/<track>/<batch>/evidence.toml` and runs one
shared implementation of each measurement. It writes no scripts and adds no `tests/test_<batch>_*.py`.
`tools/batch_evidence.py --check <dir>` checks the toml and the evidence at the batch's gate and in the merge
train.

## What a batch runs

| Command | Owner | What it does |
|---|---|---|
| `python -m tools.evidence scope --base main --out DIR/evidence/scope.json` | `tools/evidence/__init__.py` | Saves `main..HEAD --no-merges`: the commits and the sum of lines each non-merge commit adds and deletes per path. Reports read this, never a live diff. |
| `python -m tools.evidence latency measure ...` / `latency check ...` | `tools/evidence/latency.py` | Paired base and head CPU samples, keyed by full path, with every run's output compared, and the 20% rule. Both commits are read from the two checkouts, which must be clean and at different commits. Fails on empty, missing, duplicated or empty keys and on unavailable values. `tools/readings_batch_latency.py` and `tools/lean_service_latency.py` keep their CLIs and call this module. |
| `python -m tools.evidence ab BASE HEAD --base-commit SHA --head-commit SHA --out F` | `tools/evidence/ab.py` | Runs `tools/lean_first_diff.py compare`. Refuses one commit on both sides. Refuses empty recordings, unlisted differences, records unavailable on both sides, and a missing required corpus. |
| `python -m tools.evidence fuzz_ab --base-root B --batch DIR --out F` | `tools/evidence/fuzz_ab.py` | Runs `tools/difffuzz.py` in both checkouts (clean, at two different commits, both saved) and compares the reports: the sample, counts, new signatures, and each replayed baseline entry's status and answers. A difference passes only if a toml rule explains it. |
| `python -m tools.evidence mutants MUTANTS.json --evidence F` | `tools/mutants.py` (unchanged, the one harness) | Seeded mutants: the baseline passes, the named test fails, the exact bytes are restored. |
| `python -m tools.evidence report DIR` | `tools/evidence/report.py` | Renders the `[report]` lines from the evidence JSON. `--check` fails when the block in the document differs. |
| `python tools/batch_evidence.py --check DIR [--main REF] [--report-commit SHA]` | `tools/batch_evidence.py` | Checks the toml schema (an unknown key is an error) and every check the positional form had: `REQUIRED_STAGES`, `REQUIRED_CORPORA`, and the report commit's ancestry and changed paths. It also checks the scope, the gate's counts and failures, and the mutants, which must be at least three, each failing a named test. Where named, it checks the A/B (required when the scope touches `ve/` or `lean/`), latency, fuzz A/B, the report block, and tally claims. The evidence is tied to the batch: the scope holds the commits from the batch's merge base with `--main` (default `main`), each A/B compared that base with the scope's head, each mutant ran on its file at the head, and every file read is inside the repository and, with `--report-commit`, committed there. |

This batch is the toolkit's first user: `evidence.toml` here describes AR-5a and is checked with
`tools/batch_evidence.py --check docs/arch/AR-5a`.

## Verification before the release gate

The focused toolkit, legacy batch-evidence and generated-artifact tests passed (127 tests); the toolkit plus
the hang guard passed (92 tests); the gate-collection and latency tests passed (30 tests); and the layer-policy
tool passed (39 tests). `tools/lean_statements.py --check` reported 4,802 unchanged statements, with its
predicate and declaration lists unchanged. `tools/trust_map.py --since 5479466f` reported no trust growth.

An initial full-gate attempt on `811f6e3a` used `--workers auto` while host load exceeded 130; it was stopped
during the Python suite after the Lean build, Lean audit and Rust tests passed. It produced no acceptance
verdict. A full gate on `0933bfb0` passed the Lean build and audit and 36 Rust tests, then failed three cases of
`test_interrupted_gate_cannot_record_pass`. Its serial `--rerun-failed` reproduced the failure. That test
disabled toolchain setup but left Lake's trace check active, so the nested gate could not find Lean under its
isolated `HOME`; the test never reached its simulated interrupt. Commit `0341684a` mocks that trace check in
this test, leaving the interrupted-gate assertion intact. All three cases then passed directly.

The selected-test run completed 360 units with exit 0, including `tests/test_gate_integrity.py`. Its command
returned 1 only after testing because the selector attempted to write its coverage map to the read-only home
cache. The saved per-unit results were replayed into a writable `/tmp` map: 360 recorded, zero failed. The
full gate on clean `3537f55d` passed with eight workers; its completed JSON is the gate evidence below.

## Measured outcome

All numbers below are rendered from `evidence/` by `python -m tools.evidence report docs/arch/AR-5a`.

<!-- BEGIN GENERATED AR-5A NUMBERS -->
- Scope: `5479466f..3537f55d --no-merges`, 16 commits: `3537f55d`, `0341684a`, `0933bfb0`, `811f6e3a`, `bcbd87c3`, `ba0fb4d7`, `6c652a4b`, `7bc6b296`, `447bc6fc`, `68dba51e`, `b64be534`, `43ca4189`, `a07aa5ce`, `c8932f2e`, `7d4dfd1f`, `10842ddc`.
- Shared modules: 1164 lines (`tools/evidence/`: `__init__` 108, `__main__` 45, `latency` 192, `ab` 92, `fuzz_ab` 221, `report` 159, `config` 91; `tools/batch_evidence.py` 256).
- Per-batch evidence scripts and report tests on `main` (`c9b8cba6`) of the kinds a new batch no longer writes: 47 (1 `tools/*_mutants.py`, 12 `docs/<track>/<batch>/*latency*.py`, 13 `tests/test_*_evidence.py`, 21 `tests/test_*_report.py`); copies under `docs/` by name: 40 (latency 11, report 12, difffuzz_ab 6, mutants 4, fuzzer_gate 2, seed_faults 3, seed_mutants 1, trace_fuzzer 1).
- Fixtures: 9 known-answer fixtures FAIL as required, 3 complete controls PASS: ab: a record unavailable on both sides: FAIL; b1 latency: two documents named s1.ve.md in a/ and b/, a/ 50% slower on head: FAIL; b10a trace fuzzer: replay verdicts swapped, counts equal: FAIL; b10b fuzzer gate: new Lean ResourceLimit answer after the known DF-19 rejection: FAIL; control: complete A/B record: PASS; control: complete latency record: PASS; control: identical fuzz reports: PASS; latency: duplicated key: FAIL; latency: empty key: FAIL; latency: missing key: FAIL; latency: unavailable on both sides: FAIL; lf-0: empty A/B recordings: FAIL.
- Real-format runs: `ab` over 39612 conformance records (0 unlisted); `fuzz_ab` over a real `difffuzz --ci` report: 26422 inputs, 0 differences when equal, 2 unexplained after swapping two replay verdicts.
- b16c re-check: 2 error(s): scope base abc30811 is not the batch's merge base 67ae1e5a with main; the batch changes lean/ResponseShape/Schemas/Document.lean (and 9 more ve/ or lean/ paths) but its evidence.toml names no [ab].
- Seeded mutants (tools/mutants.py): 14/14 killed.
- Clean gate at `3537f55d`: passed; 14403 passed, 92 skipped, 0 failed; 36 Rust tests passed.
<!-- END GENERATED AR-5A NUMBERS -->

`evidence/measure.json` lists every counted file. The pattern counts are taken on `main` as of the batch. With
this batch, a new batch writes none of these; AR-5b migrates the existing ones and deletes nothing here.

## Gate item: b16c re-checked

`recheck-b16c/evidence.toml` points the toolkit at `docs/lean-first/b16c/evidence/` without changing it. The
toolkit renders b16c's `B16C METRICS` block byte for byte from the saved evidence. It confirms that the
residue ledger agrees with `share.json` (the tally claim), that the gate at `f0c44d43` passed with consistent
counts, and that 10/10 seeded faults failed their tests. These are the checks of the four tests in
`tests/test_b16c_evidence.py`, and all pass (two row checks differ, see below). It then fails b16c on two
points. First, the batch changes `ve/` and `lean/` but has no corpus A/B. b16c's own report gives the same
verdict: "No claim of batch 16c acceptance is made … The nine-corpus A/B … remain[s] open"
(`docs/lean-first/b16c/REPORT.md`, `DELTA.md`). Second, b16c's saved scope base `abc30811` is a later `main`
commit, not an ancestor of its head, rather than its merge base `67ae1e5a` (recheck F1 below). Its range
holds the same commits and changes, but an A/B bound to it could miss the batch's change. b16c's scope was
saved before the toolkit; AR-5b saves it again. The output is saved in `evidence/b16c-recheck.json`. Two of `test_b16c_evidence.py`'s stricter row checks are not toolkit concepts:
SHA-256 length and `cause != "lean"`. The toolkit checks the row keys, uniqueness and the tallies instead.

## Merge train

For a batch it merges, the train runs this one line in the batch's worktree at the batch's own tip, before
syncing with `main`, because a sync merge changes paths outside the batch directory after the gate:

```
git diff --diff-filter=AM --name-only main...$BRANCH -- ':(glob)docs/*/*/evidence.toml' | xargs -rn1 dirname | xargs -rI{} uv run python tools/batch_evidence.py --check {} --main main --report-commit $BRANCH
```

It exits non-zero if any batch evidence fails. It does nothing for batches made before the toolkit, whose
report tests still run in the suite until AR-5b. The strict `:(glob)` keeps `*` from matching across
directories, so a re-check fixture such as `docs/arch/AR-5a/recheck-b16c/` is not taken as a batch. Installing
the line in `manage-agents/merge-train.sh` is the DRI's (orchestration, outside the repository).

## Acceptance

| Item | Owner | Evidence |
|---|---|---|
| Toolkit checks the saved scope, gate, mutants and named measurements; known-answer fixtures fail | AGENT | `tests/test_evidence_toolkit.py`, `evidence/fixtures.json`, `evidence/mutants.json` |
| b16c fails on the open A/B its saved report names, and on its pre-toolkit scope base | AGENT | `evidence/b16c-recheck.json` and `tools/batch_evidence.py --check docs/arch/AR-5a/recheck-b16c` |
| Install the one-line check in the merge train | EXTERNAL, deferred to DRI | Command above; `manage-agents/merge-train.sh` is outside this worktree |

## Overlap with branches in flight

Checked with `git diff --name-only main...<branch>` for every `lean-first/*`, `readings-defaults/*`,
`question-answering/*`, `infra/*` and `english*/*` branch. The generated test inventory,
`tools/gate-collection.json`, overlaps several branches: a conflict means taking `main`'s file and
regenerating it (DELTA row 5, standing ruling R12). `infra/arch-AR-3` also edits
`tools/batch_evidence.py` to check a gate note in the old positional command. AR-5a must extend that same
checker, so its merge must retain both the note comparison and this batch's `--check` path.
`tools/regen_generated.py` overlapped in an earlier draft, so this batch removed its edit and kept the report
command read-only. `tests/test_gate_integrity.py` overlaps `infra/arch-AR-3`, `infra/arch-AR-4` and
`infra/oom-rootcause`; the full gate exposed a broken nested test setup, and this batch contains the same
two-line mock already in `infra/oom-rootcause`. The merge must retain one copy of that mock. This batch does
not edit `tools/gate.py`, `ve/` or `lean/`.

## Seeded bugs

The 14 mutants are in `mutants.json`. `python -m tools.evidence mutants docs/arch/AR-5a/mutants.json --evidence
docs/arch/AR-5a/evidence/mutants.json` killed all 14, and the harness restored each file's bytes. Product code
in only one language changed (Python, under `tools/`). By file: `tools/evidence/latency.py` (M1 b1 key by
name, M6 missing key, M11 the 20% rule), `tools/evidence/fuzz_ab.py` (M2 b10a replay swap, M3 b10b known
rejection), `tools/evidence/ab.py` (M4 lf-0 empty files, M7 unavailable on both),
`tools/evidence/__init__.py` (M5 duplicated key), `tools/batch_evidence.py` (M8 report block, M9 tally, M12
gate failures, M14 saved scope against Git), `tools/readings_batch_latency.py` (M10 two cases with one name), `tools/evidence/config.py` (M13 a toml
lowering the mutant minimum).

## Fix round: arch-20261010-2 review F1 to F3

The review found that `--check` passed evidence not tied to the batch. Each finding was fixed as a class:

- F1: the saved scope must hold the commits and changes of the batch's merge-base range with `--main`
  (`tools.evidence.merge_base`). After the batch merges, that base is computed from `main`'s commit before the
  merge, so a later merge does not move it. A base inside the batch (a fix round's `--base <reviewed commit>`)
  fails before and after the merge. (This round accepted a later `main` commit whose range holds the same
  commits and changes, such as b16c's; the recheck below refuses it.)
- F2: every A/B record (`ab`, `latency`, `fuzz_ab`, `tools/readings_batch_latency.py`) saves `base_commit`.
  The measuring tools read both commits from the two checkouts (`tools.evidence.checkouts`: one directory,
  one commit or a modified tracked file is refused). `--check` requires the base to be the scope's base and to
  differ from the head (`tools.evidence.base_problems`, one rule for all three). Each `tools/mutants.py` record's
  `source_sha256` must be its file at the scope's head. Records saved before the toolkit hash nothing and stay
  unbound until AR-5b migrates them.
- F3: every file the check opens goes through `tools.evidence.read_bytes`, and the check lists them
  (`recording`). Each must be inside the repository, and with `--report-commit` committed there byte for byte.
  An ignored file such as `gate-result.json` or an uncommitted edit fails. Each section's `file` is also
  resolved with `config.inside`.

Regression tests: `tests/test_evidence_toolkit.py::test_f1_*`, `test_f2_*`, `test_f3_*` and
`test_f1_f2_f3_a_committed_batch_passes_and_each_untied_piece_fails`. Seeded mutants M15 to M22 in
`mutants.json` each fail their named test. M8's anchor was moved to the new `read_bytes` line. All 22 were
killed (`tools/mutants.py`, run in this worktree). `tools/gate-collection.json` gains the 34 new test IDs.

Tests run in this round: the three probes (each exits 1 on `e9e1ccde` and 0 now), `lake build`,
`lean/audit.py` (PASS), `tools/test_layer_policy.py`, and the 367 tests of every file that imports a changed
module (`test_batch_evidence`, `test_evidence_toolkit`, `test_evidence_tools`, `test_lean_service`,
`test_readings_defaults_rd6a_report`) together with `test_gate_collection`. All passed. The merge-base
selection (`tools/select_tests.py --base`) picks all 360 units, the whole suite: the coverage map is stale.
That selection was stopped at its 50-minute limit and left to the branch verify.

The saved evidence (`evidence/scope.json`, `gate.json`, `mutants.json` and the generated block above) still
describes the gated head `3537f55d`. This round changes `tools/`, so `--check docs/arch/AR-5a --report-commit
HEAD` fails ("a commit after the gate changes tools/...") until the gate runs on the new head. After that, save
the scope, gate and mutants again and re-render the block. The release gate was not run in this round.

## Recheck F1: only the merge base names the scope

The recheck found that a later `main` commit passed as the scope's base when its range held the same commits
and changes. Every A/B record is bound to the saved base, so an A/B against a later `main` that had adopted the
batch's change would show no difference. `scope_history_problems` now requires the saved base to be the
batch's merge base (`tools.evidence.merge_base`), and compares the saved commits and changes with that range
alone. `tools.evidence.scope`, which writes the scope, takes its base from the same `merge_base`, so the
writer and the checker share one definition of the batch's base. A passing `--check` therefore binds every
A/B, latency and fuzz A/B record to the merge base. b16c's re-check gains the matching error (above).

Regression tests: `tests/test_evidence_toolkit.py::test_f1_recheck_only_the_merge_base_names_the_scope`
(a later `main`, a `main` that adopted the batch's change, and a commit inside the batch; each range is
asserted equal to the batch's where it should be) and the adopted-`main` step of
`test_f1_f2_f3_a_committed_batch_passes_and_each_untied_piece_fails`, which saves both the scope and the A/B
against that commit. The probe exits 1 on `5ea29179` and 0 now. Seeded mutant M23 removes the base rule; M14
and M15 are re-anchored on the new lines.

## Follow-ups and what was not run

- FOLLOW-UP (`tools/mutants.py`, owner eff-merge): the harness reads a failed node id with `\S+`, so a
  parametrized test whose id contains a space never counts as killing a mutant. This errs on the safe side: it
  reports a survivor, never a false kill. This batch gives its tests space-free ids. The harness also does not
  create the parent directory of `--evidence`.
- AR-5b, not in scope: migrating the report and evidence tests that `evidence/measure.json` lists to
  `evidence.toml`, deleting copied scripts, and the over-1 MB evidence branch.
- Not run: `fuzz_ab` and `latency measure` across two different checkouts. This batch changes no product
  code, so there is no base/head difference to measure. Their logic is covered by the known-answer tests. The
  `fuzz_ab` comparison and `ab` were also run on real tool output (`evidence/real-runs.json`).
