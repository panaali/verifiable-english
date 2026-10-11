# AR-5a: the evidence toolkit

Plan: `docs/ARCHITECTURE-REVIEW-2026-10.md` (branch `design/arch-review`), section 4.3, row AR-5a, and
DRI decision D4. A batch now describes its evidence in `docs/<track>/<batch>/evidence.toml` and runs one
shared implementation of each measurement. It writes no scripts and adds no `tests/test_<batch>_*.py`.
`tools/batch_evidence.py --check <dir>` checks the toml and the evidence at the batch's gate and in the merge
train.

## What a batch runs

| Command | Owner | What it does |
|---|---|---|
| `python -m tools.evidence scope --base main --out DIR/evidence/scope.json` | `tools/evidence/__init__.py` | Saves `main..HEAD --no-merges`: the commits and the lines each path adds and deletes. Reports read this, never a live diff. |
| `python -m tools.evidence latency measure ...` / `latency check ...` | `tools/evidence/latency.py` | Paired base and head CPU samples, keyed by full path, with every run's output compared, and the 20% rule. Fails on empty, missing, duplicated or empty keys and on unavailable values. `tools/readings_batch_latency.py` and `tools/lean_service_latency.py` keep their CLIs and call this module. |
| `python -m tools.evidence ab BASE HEAD --head-commit SHA --out F` | `tools/evidence/ab.py` | Runs `tools/lean_first_diff.py compare`. Refuses empty recordings, unlisted differences, records unavailable on both sides, and a missing required corpus. |
| `python -m tools.evidence fuzz_ab --base-root B --batch DIR --out F` | `tools/evidence/fuzz_ab.py` | Runs `tools/difffuzz.py` in both checkouts and compares the reports: the sample, counts, new signatures, and each replayed baseline entry's status and answers. A difference passes only if a toml rule explains it. |
| `python -m tools.evidence mutants MUTANTS.json --evidence F` | `tools/mutants.py` (unchanged, the one harness) | Seeded mutants: the baseline passes, the named test fails, the exact bytes are restored. |
| `python -m tools.evidence report DIR [--write]` | `tools/evidence/report.py` | Renders the `[report]` lines from the evidence JSON. `--check` fails when the block in the document differs. |
| `python tools/batch_evidence.py --check DIR [--report-commit SHA]` | `tools/batch_evidence.py` | Checks the toml schema (an unknown key is an error) and every check the positional form had: `REQUIRED_STAGES`, `REQUIRED_CORPORA`, and the report commit's ancestry and changed paths. It also checks the scope, the gate's counts and failures, and the mutants, which must be at least three, each failing a named test. Where named, it checks the A/B (required when the scope touches `ve/` or `lean/`), latency, fuzz A/B, the report block, and tally claims. |

This batch is the toolkit's first user: `evidence.toml` here describes AR-5a and is checked with
`tools/batch_evidence.py --check docs/arch/AR-5a`.

## Measured outcome

All numbers below are rendered from `evidence/` by `python -m tools.evidence report docs/arch/AR-5a`.

<!-- BEGIN GENERATED AR-5A NUMBERS -->
<!-- END GENERATED AR-5A NUMBERS -->

`evidence/measure.json` lists every counted file. The pattern counts are taken on `main` as of the batch. With
this batch, a new batch writes none of these; AR-5b migrates the existing ones and deletes nothing here.

## Gate item: b16c re-checked

`recheck-b16c/evidence.toml` points the toolkit at `docs/lean-first/b16c/evidence/` without changing it. The
toolkit renders b16c's `B16C METRICS` block byte for byte from the saved evidence. It confirms that the
residue ledger agrees with `share.json` (the tally claim), that the gate at `f0c44d43` passed with consistent
counts, and that 10/10 seeded faults failed their tests. These are the checks of the four tests in
`tests/test_b16c_evidence.py`, and all pass (two row checks differ, see below). It then fails b16c on one point: the batch changes `ve/` and `lean/`
but has no corpus A/B. b16c's own report gives the same verdict: "No claim of batch 16c acceptance is made …
The nine-corpus A/B … remain[s] open" (`docs/lean-first/b16c/REPORT.md`, `DELTA.md`). The output is saved in
`evidence/b16c-recheck.json`. Two of `test_b16c_evidence.py`'s stricter row checks are not toolkit concepts:
SHA-256 length and `cause != "lean"`. The toolkit checks the row keys, uniqueness and the tallies instead.

## Merge train

For a batch it merges, the train runs this one line in the batch's worktree at the batch's own tip, before
syncing with `main`, because a sync merge changes paths outside the batch directory after the gate:

```
git diff --diff-filter=AM --name-only main...$BRANCH -- ':(glob)docs/*/*/evidence.toml' | xargs -rn1 dirname | xargs -rI{} uv run python tools/batch_evidence.py --check {} --report-commit $BRANCH
```

It exits non-zero if any batch evidence fails. It does nothing for batches made before the toolkit, whose
report tests still run in the suite until AR-5b. The strict `:(glob)` keeps `*` from matching across
directories, so a re-check fixture such as `docs/arch/AR-5a/recheck-b16c/` is not taken as a batch. Installing
the line in `manage-agents/merge-train.sh` is the DRI's (orchestration, outside the repository).

## Overlap with branches in flight

Checked with `git diff --name-only main...<branch>` for every `lean-first/*`, `readings-defaults/*`,
`question-answering/*`, `infra/*` and `english*/*` branch. Two files overlap, both shared registries:
`tools/gate-collection.json` (the generated test inventory: a conflict means taking `main`'s file and
regenerating it, DELTA row 6) and `tools/regen_generated.py`, where this batch adds one `NOT_REGENERATED` line;
`infra/arch-AR-1`, `infra/arch-AR-3` and `infra/arch-20261010-1` edit other hunks of that file. This batch does
not edit `tools/gate.py`, `ve/` or `lean/`.

## Seeded bugs

The 13 mutants are in `mutants.json`. `python -m tools.evidence mutants docs/arch/AR-5a/mutants.json --evidence
docs/arch/AR-5a/evidence/mutants.json` killed all 13, and the harness restored each file's bytes. Product code
in only one language changed (Python, under `tools/`). By file: `tools/evidence/latency.py` (M1 b1 key by
name, M6 missing key, M11 the 20% rule), `tools/evidence/fuzz_ab.py` (M2 b10a replay swap, M3 b10b known
rejection), `tools/evidence/ab.py` (M4 lf-0 empty files, M7 unavailable on both),
`tools/evidence/__init__.py` (M5 duplicated key), `tools/batch_evidence.py` (M8 report block, M9 tally, M12
gate failures), `tools/readings_batch_latency.py` (M10 two cases with one name), `tools/evidence/config.py` (M13 a toml
lowering the mutant minimum).

## Follow-ups and what was not run

- FOLLOW-UP (`tools/mutants.py`, owner eff-merge): the harness reads a failed node id with `\S+`, so a
  parametrized test whose id contains a space never counts as killing a mutant. This errs on the safe side: it
  reports a survivor, never a false kill. This batch gives its tests space-free ids. The harness also does not
  create the parent directory of `--evidence`.
- FOLLOW-UP (pre-existing on `main`, not this batch): `tools/test_layer_policy.py` fails
  `test_documented_python_layers_match_policy` for layer 4 (`ask`). A clean `main` worktree fails the same way,
  and the gate does not run that script.
- AR-5b, not in scope: migrating the report and evidence tests that `evidence/measure.json` lists to
  `evidence.toml`, deleting copied scripts, and the over-1 MB evidence branch.
- Not run: `fuzz_ab` and `latency measure` across two different checkouts. This batch changes no product
  code, so there is no base/head difference to measure. Their logic is covered by the known-answer tests. The
  `fuzz_ab` comparison and `ab` were also run on real tool output (`evidence/real-runs.json`).
