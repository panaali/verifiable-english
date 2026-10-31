# fsf-r2-probes-stale: fsf-r2's saved probes after df-3

Status: done (infra; backlog row fsf-r2-probes-stale). No DRI signature needed.
Base: main f23f07742. What changed: `docs/usecases/safety-framework/fsf-r2/probes.json` was regenerated with
`usecases/safety-framework/measure_r2.py` (one line), and the one sentence in `probes.md` that quotes the same text was
updated. No product code changed in Lean, Python or Rust.
Cause: df-3 (97e36e510, merged ffddf155c, approved by review) changed the refusal on DF-a's document. This is df-3's
DELTA row D2, which the DRI signed (reviews/dri-decisions-20261028-df-3.md item 2). It is not a regression.

## Finding

`tests/test_safety_framework.py::test_fsf_r2_probes_rerun_equals_saved_probes` runs `measure_r2.main(["--check"])`. It
skips when the pinned FSF 3.1 source is missing, as it is on gate runners and on Actions. On this machine the source is
present (`~/code/manage-agents/pilots/safety-framework/source/fsf-3.1.txt`, 54,373 B).

- On main f23f07742, with freshly built Rust and Lean binaries (`python3 tools/rust_build.py`, `lake build`: "Build
  completed successfully (1180 jobs)"), `uv run python usecases/safety-framework/measure_r2.py --check` printed
  `probes.json is out of date`. So the test was still red on current main.
- I wrote the probes to a scratch file (`measure_r2.probes(...)`) and diffed it against the saved file. Exactly one
  line differs, probe DF-a's diagnostic:
  - saved: `VEError: --assume-no-exception applies to a soft-norms@0 document without open reading sets`
  - rerun: `VEError: --assume-no-exception applies to readings on the enumerated route`
- Where the new text comes from: `ve/document/cli.py` `_readings_without_exception`, added by df-3 in 97e36e510
  (`git log -S'applies to readings on the enumerated route'`). Since df-3, a document with a content-bearing set goes to
  df-3's readings path, which serves the enumerated route only. Every other route is refused with this text.
- DF-a's document (RS4holistic's part document) is on Lean's superposed route. A probe that loads it with
  `load_document` printed `route superposed components False`. So the new refusal is the one df-3 designed:
  `docs/spec/defeasible.md` 7.4 says "DF-3 uses the enumerated route only (at most 64 choices; plan section 11,
  issue 6)".
- df-3's `docs/defeasible/df-3/DELTA.md` says: "Every refusal `--assume-no-exception` gave before still has its df-1b
  text, except on a document with a content-bearing set (row D2)". Row D2's Ruling cell reads "SIGNED by the DRI
  2026-10-28 (reviews/dri-decisions-20261028-df-3.md item 2)".
- The rest of DF-a is unchanged: it is still refused and the unit still stays OPEN. DF-b, DF-c, every JT and SC probe,
  `units.json` and `gaps.json` match the rerun.

## Fix

- `uv run python usecases/safety-framework/measure_r2.py` rewrote the evidence. `git diff --stat` afterwards showed
  `probes.json | 2 +-`; `units.json` and `gaps.json` were byte-identical.
- In `probes.md`, the DF-a row now quotes the new text. It cites df-3 (97e36e510, DELTA D2) and keeps the text measured
  on 6d0a10526. Its other statements still hold: the flag refuses DF-a and no byte moves.
- `docs/usecases/safetyfw/REPORT.md` is a separate, older batch report that records what main did when it was written.
  It is left as it is.
- `uv run pytest -q tests/test_safety_framework.py -k fsf_r2`: `3 passed, 15 deselected`.

## DELTA

None. This branch changes no product output. The one evidence line records an output change that df-3 made and DELTA D2
signed. No new row is needed, and none is reserved for the DRI.

## Seeded bugs

Each bug was planted on the committed fix (1c3898165), shown failing, and reverted with `git checkout`. Each was caught by
`tests/test_safety_framework.py::test_fsf_r2_probes_rerun_equals_saved_probes`, which failed with `SystemExit:
probes.json is out of date` (also recorded in `mutants.json`).

| # | File | Seeded bug | Behaviour it breaks | Result |
|---|---|---|---|---|
| S1 | `docs/usecases/safety-framework/fsf-r2/probes.json` | DF-a's saved diagnostic set back to the df-1b text | saved probes equal the rerun | 1 failed |
| S2 | `ve/document/cli.py` | the enumerated-route refusal reworded ("routes") | DF-a is refused with df-3's text | 1 failed |
| S3 | `ve/document/cli.py` | the content-bearing redirect to `_readings_without_exception` disabled (`if False and ...`) | DF-a takes df-3's readings path, not the soft-norms guard | 1 failed |

S2 and S3 are in Python product code that this branch does not change. They show that the test notices df-3's
behaviour drifting again.

## Tests

- Selected tests, run once on the finished code (b4565d4e2f tree, commit after 1c3898165):
  `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`. It reported "149/508 test units" and four
  shards, each "exit 0" (41, 38, 39 and 31 units passed). Summary: "selected tests ran on GitHub Actions (4 shards, run
  fsf-r2-probes-stale-2929049d-t437267); exit=0". Selection deferred 35 slow files to the chain gate.
- On Actions the fsf-r2 test skips, because the pinned source is missing there. The run that covers it is the local one
  above: `uv run pytest -q tests/test_safety_framework.py -k fsf_r2`, `3 passed`.
- Pre-existing: this test skips wherever the pinned source is missing (gate runners, Actions). The gate therefore does
  not cover it. That is the row's note, and this item does not change it.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer or schema changed.
2. PASS: the row asks for a rerun on current main, regeneration via measure_r2 only for an approved change with that
   change cited, and nothing more. Rerun: "Finding". Regeneration: "Fix". The approved change is df-3 (97e36e510, D2).
3. PASS: seeded bugs S1 to S3 above, each failing `test_fsf_r2_probes_rerun_equals_saved_probes`.
4. N.A.: no Python, Lean or Rust code changed.
5. N.A.: no binding changed.
6. PASS: the final-HEAD gate is run by the chain. Both the evidence and the rerun come from `measure_r2.py` on this
   tree.
7. PASS: no DELTA row and no trust growth. The cited D2 is SIGNED by the DRI in df-3's DELTA.
8. PASS: the base and head outputs were diffed (the scratch rerun against the saved file). The only changed record is
   DF-a, which df-3's D2 already covers.
9. PASS: `uv run python tools/select_tests.py --base $(git merge-base HEAD main)` selects
   `tests/test_safety_framework.py` (182/508 units).
10. N.A.: no Lean changed.
11. N.A.: no budget, limit or deadline changed.
12. N.A.: no code changed.
13. N.A.: no test was removed or renamed.
14. PASS. Opposite direction: the same test passes on the regenerated evidence and fails on the stale text (S1).
    Claims cite their commands above. Spec re-read: "DF-3 uses the enumerated route only" against
    `docs/spec/defeasible.md:988`, and the D2 row against `docs/defeasible/df-3/DELTA.md` (the row starting `| D2`).
