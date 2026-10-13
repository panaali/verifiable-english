# ME-0 summary: pinned targets and baseline partition (2026-10-13)

Today's VE is `main` at `406736a4`. It was run from its built checkout `ve-pilot-20261013T0600Z`, whose `lean/`,
`rust/` and `ve/` trees equal `406736a4` (each `run.json` records this). Every `ve` run was under
`prlimit --as=6442450944`. No model was called and no product code was changed. Every number below comes from
`summary.json`, which `research/math-evidence/summarise.py` builds from the saved evidence. Results and their
consequences are in [docs/research/math-evidence-phase1.md](../../math-evidence-phase1.md).

## Sources (SOURCE)

| Row | Target | Pinned bytes | Fetched from (plain HTTP, no model) | Licence evidence |
|---|---|---:|---|---|
| H | Michelson and Morley 1887, *Am. J. Sci.* 34: 333-345 | 24,368 (`physics-michelson-morley/source.txt`) | Wikisource, 13 proofread `Page:` wikitexts (`raw/`, kept), derived by `extract_sources.py` | Published 1887; Michelson d. 1931, Morley d. 1923; Wikisource `{{PD/US|1931}}` |
| M | Ramanujan 1919, "A proof of Bertrand's postulate" (*Collected Papers* 1927, 208-209) | 2,651 (`math-ramanujan-bertrand/source.txt`) | archive.org `pli.kerala.rare.28155`, OCR text, bytes 313,130-315,781 of the fetched file | Published 1919; Ramanujan d. 1920 |
| DL | Jumper et al. 2021, AlphaFold, *Nature* 596: 583-589 | 66,858 (`dl-alphafold/source.txt`) | Europe PMC JATS of PMC8371605 (`raw/europepmc-fulltext.xml`, kept) | CC BY 4.0: the Nature page's `license` field and the JATS licence (`dl-licence-check/licence-evidence.json`) |
| V | VE paper, `paper/sections/04-e1.md` and the appendix section "Per-template differences …" | 8,883 + 1,054 | repository at this branch (paper bytes equal `main` and `49de179e`) | the repository |

URLs, retrieval times, HTTP status, sizes and SHA-256 of every fetched file are in each `raw/fetch-log.json`. The
third-party pages (the Nature HTML, the Hardy-item OCR text, the arXiv pages) are not committed. Their digests are
in those logs, and `fetch_sources.py` re-fetches them, keeping a page only if it matches. The Kerala OCR text that M is
sliced from is committed (the 1927 edition is public domain). Each source's own SHA-256 is in its `*.units.json`.
These logs and this table stand in for the per-target `SOURCE.md` that the plan's ME-0 names.

## Partition by status (Lean's `ve document coverage`; every ledger accounts for 100% of its bytes)

| Row | Bytes | CHECKED | of which in units taking part in Lean-certified relations | LABELLED | UNFORMALISED | CHECKED % |
|---|---:|---:|---:|---:|---:|---:|
| H | 24,368 | 1,858 | 1,582 | 11,560 | 10,950 | 7.62 |
| M | 2,651 | 0 | 0 | 265 | 2,386 | 0.00 |
| V (E1 slice) | 9,937 | 1,199 | 382 | 4,088 | 4,650 | 12.07 |
| DL | 66,858 | 4,453 | 2,548 | 49,707 | 12,698 | 6.66 |

CHECKED means Lean admitted the unit's W6a statement (support: testimony). Where noted, the statement is also a
premise of a consequence whose certificate Lean replayed. It never means the source's numbers are true. The premise
set of the H, V and DL documents is UNKNOWN to `ve document check` (no model or contradiction within budget, domain
size 2), so every certificate is replayed but its non-vacuity is undecided; only M's premises have a checked model.
Certified relations:

- H: each printed Mean is the tenths-rounding of its three sessions (34 values); the unlabelled row repeats marks
  8-16 (18); each Final mean averages marks k and k + 8 (18).
- V: 280 + 594 = 874; 8,740 = 874 × 5 × 2; 9 + 3 = 12 templates.
- DL: AlphaFold's medians are below the alternatives'; each printed point estimate lies in its interval; the BFD
  cluster counts are ordered as described; 75% + 25% = 100%; batch 128 = 128 cores × 1; the test-set date limit
  equals the training cut-off; and the Data-availability dates equal the Methods dates.

Negative controls: one printed number changed while the certificate for the true number is kept (H: noon Mean at mark
1, 41.6 → 41.9; V: 594 → 595; DL: 2019-08-28 → 2019-08-29). Lean refuses each with "graph rejected: … invalid
certificate", raised from the Lean admission relay (`*.control.check.txt`).

Rust accelerator limit: at its default 5 s wall-clock limit, the untrusted Rust checker stops the H document
(216 constants), which is then CheckerUnavailable (`source.check.default-limit.json`). With `VE_RUST_TIMEOUT=1800` it
is admitted in about 47 s. The V document hit the same limit on one of three runs
(`source-04-e1.check.default-limit.earlier-run.json`), so the limit depends on machine load.

## UNFORMALISED bytes by missing feature

| Row | This plan's features | Siblings' tags | Largest |
|---|---:|---:|---|
| H | 6,166 | 4,784 | approximation 2,731; attitudes 2,633; calc 2,216; attribution 1,093; calc-algebra 752; events 679; quantities 379; calc-derive 222; calc-data 153; calc-dimension 92 |
| M | 2,386 | 0 | arith-import 2,114; arith 220; calc-derive 52 |
| V | 4,215 | 435 | calc-stats 2,858; calc-data 512; calc 469; attitudes 435; approximation 376 |
| DL | 6,560 | 6,138 | quantities 3,802; calc-data 3,355; approximation 1,730; calc-stats 1,329; attitudes 1,303; attribution 553; events 480; calc 146 |

## Sentence kinds (units; a MIXED unit counts once, by its largest part)

| Kind | H | M | V | DL |
|---|---:|---:|---:|---:|
| exposition | 65 | 1 | 21 | 109 |
| equation | 20 | 19 | 0 | 0 |
| table (rows) | 16 | 0 | 14 | 0 |
| hedge | 13 | 0 | 5 | 6 |
| caption | 12 | 0 | 1 | 41 |
| quantity | 11 | 0 | 11 | 37 |
| empirical claim | 9 | 0 | 6 | 25 |
| definition | 7 | 3 | 13 | 9 |
| citation | 7 | 2 | 0 | 381 (reference-list sentences) |
| comparison | 6 | 0 | 6 | 17 |
| meta | 7 | 4 | 19 | 96 |
| proof step | 0 | 15 | 0 | 0 |
| theorem | 0 | 5 | 0 | 0 |
| exposition share of bytes | 39.4% | 1.5% | 19.4% | 29.3% |

## Other measurements

- Constitution and UDHR pilots (`run-20261012T1800Z`): 0 units and 0 bytes are blocked by this topic
  (`pilots-zero.json`).
- An 1887 W6a date is refused with `DateRange(1887-07-08)`, and the 1970-01-01 control is admitted
  (`date-floor.json`).
- Fixture anchors, over the 32 fixtures in P4's pre-registered scope: 14 ANCHORED, 9 RE-WORDED, 3 CHANGED (H-4,
  H-5, H-9), 0 ABSENT, 6 NOT A QUOTE. V-9 to V-12 lie outside the scope (1 RE-WORDED, 3 NOT A QUOTE)
  (`fixture-anchors.json`, with exact-fraction pre-checks for ME-S that are not VE verdicts).
