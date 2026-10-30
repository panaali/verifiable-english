<!-- Record of infra item fp-fulltext. The change itself lives in manage-agents tools-local (outside this
repository); this file is the branch's copy of the build report (manage-agents reviews/fp-fulltext-20261030.md).
DRI decision: manage-agents reviews/dri-decisions-20261030-fp-fulltext.md (item 1: slack 4 B SIGNED). -->

# fp-fulltext (2026-10-30): constitution unit text drawn in full

Order: reviews/dri-decisions-20261030-fp-apol.md item 3; task prompts/task-fp-fulltext.txt; backlog fp-fulltext.
Tooling only (manage-agents tools-local); no VE product code changed, nothing committed on infra/fp-fulltext.

**Deviation from the task (needs no DELTA row: no VE behaviour changes; flagged for the DRI to see):** the runner
refuses a row whose UTF-8 text is more than **4** B short of `bytes`, not 2. The census's own whitespace normalisation
drops up to 4 B: 38 of 1133 units are indented `  + ` bullets that lose 3 or 4 B (u0073.*, u0159.*, u0218.*, u0249).
With a slack of 2 the runner would refuse full texts, including 6 of the 10 units in
reviews/fidelity-pilot-20261029/action-assurance/units.tsv, and the u0218-heavy AA pool of any action-assurance re-pilot.
The cost: one of the 87 census cuts is only 3 B short, so the 4 B backstop alone would miss it. The generator does not
rely on the backstop: it checks every constitution text exactly (below).

## Changes

- tools-local/fidelity-pilot-units.py (backup .bak-20261030-fpfulltext):
  - `cunit` takes each census unit's span from the census run (pilots/claude-constitution/run-20261028T0600Z/units.json)
    of the pinned pilots/claude-constitution/source/claude-constitution.md (sha256 fa10ed48…50dd, asserted). The text is
    whitespace-collapsed, which is the census's own `norm`.
  - New `const_text` exits 2 unless all of these hold: the source is pinned; the unit has a span; the span is exactly
    `bytes` long; the census text equals the span text cut at 300 characters; the span loses only 0..4 B to whitespace.
    It never falls back to the census text.
  - `loc` in draw.json now gives the span.
  - New optional `<out root>` argument (default reviews/fidelity-pilot-20261029).
  - A units.tsv that exists with other bytes is never overwritten (exit 4, as fidelity-pilot-units-fresh.py does).
  - New `--check <units.tsv>` mode: exit 2 and one line per cut row. `SLACK` and the check have one owner, this module.
- tools-local/fidelity-pilot.sh (backup .bak-20261030-fpfulltext): before anything else, it runs
  `fidelity-pilot-units.py --check $P/units.tsv`. On failure it prints "units.tsv has cut unit text; not starting" and
  exits 2.
- tools-local/test_fidelity_pilot_units.py (new, 9 tests; `python3 -I tools-local/test_fidelity_pilot_units.py`).

## Evidence

- All 1133 census units: the span of the run gives `bytes` exactly, and the census text equals its first 300 characters
  (0 mismatches). 87 are longer than 300 characters (test_every_census_unit_is_exact_and_within_slack).
- The apol draw was regenerated with seed 20261029 in a temp root (test_apol_redraw_carries_full_spans). Ids, order and
  every other column are byte-identical to reviews/fidelity-pilot-20261029/apol/units.tsv. Only these two texts changed:

  | unit | bytes | text before | text now |
  |---|---|---|---|
  | u0115.s02 | 368 | 302 B | 366 B, the whole span with whitespace collapsed |
  | u0123.s02.p1 | 348 | 302 B | 348 B |

  The pilot dir's sha256 was unchanged before and after.
- The other four 2026-10-29 draws (profile-composition, commands-imperatives, commitments, action-assurance) were
  regenerated in scratch roots. They are byte-identical to the saved ones, and each passes `--check`.
- `--check` on the old apol units.tsv: exit 2, naming both units.

## Seeded bugs

Each was planted in a temp copy and run with the one test below. The live files were never seeded.

| # | file | seed | failing test |
|---|---|---|---|
| S1 | tools-local/fidelity-pilot-units.py | cunit text back to census `r["text"]` | test_apol_redraw_carries_full_spans |
| S2 | tools-local/fidelity-pilot-units.py | SLACK = 2 | test_check_passes_full_draws |
| S3 | tools-local/fidelity-pilot-units.py | const_text drops the span == bytes check | test_const_text_refuses_a_mismatch |
| S4 | tools-local/fidelity-pilot-units.py | overwrite guard off | test_never_overwrites_a_drawn_units_tsv |
| S5 | tools-local/fidelity-pilot.sh | refusal exits 1, not 2 | test_runner_refuses_cut_text |
| S6 | tools-local/fidelity-pilot-units.py | --check counts characters, not UTF-8 bytes | test_check_counts_utf8_bytes |

## Observation for fp-apol (not changed here)

`fidelity-pilot-units-fresh.py apol reviews/fidelity-pilot-20261029 <tmp> N` exits 3 on the flow stratum ("pool
differs from the seen draw": now 12 ids, then 18). The fresh script adds the whole assent pool to its seen keys, but
`main`'s draw excludes only the assent units it drew. Pool ids do not depend on unit text, so this change does not cause
it. fp-apol's preparer (fresh draw: assent 33 left, flow 13 left) will meet it.

Other pilots: reviews/const-paper-pilot-20261029/units.tsv (another runner, const-paper-pilot.py) also carries 3 cut
census texts (u0089, u0020.s01, u0258.s02). That runner is not in this task's scope.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no Lean, no relay).
2. Every deliverable built, no rule broken: PASS (items 1-3 of the task; .new + py_compile/zsh -n + .bak + mv; no
   pilot scope was running; CURRENT-STATE line; backlog done). Slack deviation SIGNED by the DRI (decision item 1).
3. Tests and gates can fail: PASS (S1-S6 above, each with its failing test).
4. Python, Lean and Rust agree: N.A. (tooling only).
5. R8 binding: N.A.
6. Gate evidence matches final HEAD: PASS (this commit is docs only; the chain gates it).
7. No unsigned item: PASS (the one deviation is SIGNED in the DRI decision file).
8. Every user-visible change in DELTA: N.A. (no VE behaviour changes; no DELTA row).
9. Test selection: N.A. (no VE product code changed).
10. Lean statements and proofs: N.A.
11. Budgets fail closed: PASS (const_text exits 2, runner exits 2, never a fallback to the cut text:
    test_const_text_refuses_a_mismatch, test_runner_refuses_cut_text).
12. No CPU or memory regression: N.A.
13. Test-removed trailers: N.A. (no test removed).
14. Both directions, cited evidence: PASS (full texts pass test_check_passes_full_draws; cut texts refused
    test_runner_refuses_cut_text; redraw byte-identical except the two units, test_apol_redraw_carries_full_spans).
