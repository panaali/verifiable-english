# ap-parse-index delta: reading an act phrase within the CPU deadline at 128 frames

Base: `git merge-base HEAD main`. See [REPORT.md](REPORT.md).

**Answers: none changed.** Every definition the proofs read is unchanged; compiled code runs proved-equal forms
(`@[csimp]`: `closed`, `build`, `combine`, `readings`, `read`) and `witnessed`/`rowsOf` share one rule table. Every
step count, `#guard`, budget boundary and parse tree of the existing fixtures is the same (no charge changed: DRI
2026-11-09 ap-parse-index item 1, as the REPORT's section 3 records).

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | Trust growth (numbers in REPORT section 5): the proved-equal fast forms and the one-table readers | `uv run python tools/trust_map.py --check`; `docs/act-phrases/ap-parse-index/mutants.json` (each new trusted definition's bug killed by a proof or `#guard`); FOLLOW-UPS.md "## ap-parse-index" | R16 |

## Evidence (no row: an availability gain on a fail-closed path)

- `act-readings`, L6 (P64) with 126 frames more: `CheckerUnavailable` at the 5 s CPU deadline (305 s of CPU needed)
  before; `LISTED`, the same 64 readings as with V5 alone, after (0.42 s wall on the VM).
  `tests/test_acts_readings_lean.py::test_p64_with_126_frames_more_is_listed_within_the_cpu_deadline` replaces the test
  that pinned the gap (DRI 2026-11-09 ap-parse-index item 2; `Test-changed:` trailer).
- `norms`, a document with 128 frames and a joined act: answered with its parts (`p027__1`, `p027__2`) within the
  deadline (`tests/test_ap_parse_index.py`).
- The 400-byte phrase with 32 to 128 frames: a deterministic step-budget `LIMIT`, never `CheckerUnavailable` (before:
  `LIMIT` at 32 frames, 3.2 s of CPU; `CheckerUnavailable` at 128 frames, 21 s).
