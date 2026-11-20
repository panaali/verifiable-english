# chain-gate-empty-ve-diff: the chain gate skips a branch with no VE change

Status: BUILT, REVIEWED (MERGE, no A or B findings: `manage-agents/chain-gate-empty-ve-diff-review-ov.final.md`)
and INSTALLED by the decider (backup `chain-gate.sh.bak-20261119cgev`). No DRI signature is reserved and no DELTA row is
needed (no Lean or trust-base change).

VE side: evidence only. The product change lives in `manage-agents`. This commit exists because the pre-review
gate's [commits] check fails on a branch with 0 commits (review finding F3). Infra items record their evidence
under `docs/infra/<item>/` the same way (for example, `vm1-gate-weight` and `tmpar-lock-align`).

## Change (manage-agents)

- `chain-gate.sh` gets one 20-line block (`chain-gate.sh.cgev.diff`). It sits after the dirty-worktree refusal and
  before the `GATE_REUSE_SAME_TREE` block, so it runs before any slot wait or gate run. The block skips only when
  all three hold:
  - `git merge-base HEAD main` succeeds;
  - `git rev-list --count <base>..HEAD` is 0;
  - the worktree is clean.

  When it skips, it writes `chain-select-<label>.json` (mode selected, rc 0, skip `no-ve-change`), emits event
  gate-skip "no VE change" and exits 0. With no merge base, a git error, any commit beyond the base or a failed
  record write, the gate runs exactly as before. No new flag, service, ledger or loop.
- New test: `tools-local/test_chain_gate_empty_ve_diff.py` (the script under test comes from `CG=`).
- Three existing tests built their toy repos on `main` with 0 commits. Each gets one empty commit on branch
  `infra/t` (`tests.cgev.diff`) and passes on both the old and the new script.

## Evidence (this directory, recorded 2026-11-20 against the installed files; checksums in `md5.txt`)

- `test-on-installed.log`: `all passed (0 failures)`, rc 0.
- `test-on-old.log` (`CG=chain-gate.sh.bak-20261119cgev`): `FAILED (6 failures)`, rc 1. All failures are in cases
  (1) and (1b), the 0-commit clean branch: no gate-skip event, no record, and gate.py ran.
- `syntax.txt`: `zsh -n` is clean on the installed script.

## Seeded bugs (from the build, in copies of the staged script under /tmp/cgev-seed/; file: manage-agents/chain-gate.sh)

1. Skip on any commit count: case (2) FAILS.
2. Treat a merge-base error as HEAD: cases (4) and (4b) FAIL.
3. Exit 1 instead of 0: cases (1) and (1b) FAIL.
4. Wrong `skip` value in the record: the record checks in (1) and (1b) FAIL.
5. Remove the extra clean-tree check: survives. The earlier dirty refusal exits 2 first (review F4: harmless
   defensive code).

The reviewer planted three more (a reversed range, a skip on any count, changed event text), and each made the test fail.
No Lean, Python or Rust product code changed in VE, so no VE seeded bug applies.

## Merge train with a 0-commit item

`merge-train.sh` `mkcand` (line 509) calls `git commit-tree $t -p $base -p $cand`. When cand is the base, git drops
the duplicate parent, so the candidate is a single-parent empty commit. The train still runs the R2 gate on it and
publishes it. That spends one full gate but does not fail the item. This branch now carries this docs-only commit,
so the train merges it normally.

SIZE: 20 product, 149 tests, 0 other hand-written lines (this report and its logs are evidence).
MEASURED: `delegate-cw.py` printed "own session not found (needs VE_STEP and CLAUDE_CONFIG_DIR from
dri-delegate.sh, or a transcript path)", so there is no figure to quote.

## Notes for the DRI

- Review-ready [commits] still FAILs any 0-commit infra item (`review-ready.py:467-468`) and sends it back for builder
  rounds. Each item then has to add an evidence commit like this one. That cost is outside this item's scope.
- The review-ready WARN reads "Mac runner unavailable (no VE change …)" for a `no-ve-change` record. The wording is off but harmless.
