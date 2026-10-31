# AP-7 results: do derivations find the auditors' readings?

GATE: FAIL (recall FAIL, not a reading PASS, skipped middle PASS)

Codex was at its credit cap (resets 2026-11-04), so both listing seats are Claude Opus 5.5 in separate sessions (DRI
ruling reviews/dri-decisions-20261031-ap-7.md item 1); the 'both auditors list' readings therefore come from one model
family, which can share blind spots; cross-family review is optional (lead 2026-10-10).

Every number below is `runner.py --score` over [raw/](raw/) and [lean-readings.json](lean-readings.json), saved as
[results.json](results.json); `tests/test_ap7.py` recomputes it. Run once, after the pre-registration (`2fb97f321`) and
Lean's readings (`d8b811d49`) were committed: 144 calls (92 listing, 6 judging, 46 matching), 2,227,754 CW, no failed
call, no unbound answer.

| Bar (frozen, PRE-REGISTRATION.md) | Measured | Verdict |
|---|---|---|
| recall ≥ 90% of the readings both auditors list | 23 / 105 = 21.9% | FAIL |
| ≤ 10% of Lean's readings judged "not a reading of this English" by both | 1 / 26 = 3.8% (u0038.s06 L1) | PASS |
| no skipped-middle reading | none named | PASS |

Beside the bars, with no bar of their own:

- **Phrases with at least one reading:** 20 of 46 (43%); 10 are refused by the act check (a clause word such as *is*
  or *not*, or a word that is not letters), 16 have none, none reaches a limit.
- **Phrases D9 refuses** (they parse but have no meaning: D9 (i) or a frame misfit, which Lean's counts do not tell
  apart; only option (i) is built): u037, u045a, u059, u101, u0062.s01, u0156.s03, u0283.s04. The five registered D9
  rows (u037, u045a, u101, u0062.s01, u0156.s03) hold 13 of the 105 agreed readings, all unmatched.

Where the misses are (descriptive, no bar): 61 of the 82 unmatched readings belong to the 26 phrases with no reading,
which the bar counts as zero. On the 20 phrases Lean reads, 23 of 44 agreed readings are matched (52%); on the plan's
16 fixed phrases 15 of 36, on the 30 drawn constitution sentences 8 of 69. The builder's reading of the 21 unmatched
readings on read phrases (not scored): 3 are "together" readings the table (D3) leaves out (u051 twice, "to seek and
to enjoy" as one combined right, which the table splits because each item has its own *to*; u0038.s06, the two wishes
only together, which *must* splits); 1 is an edge reading (D4): u0038.s06's *generally* inside the second item read
over both items; the rest read words the vocabulary rule cut from the act (u0067.s07's *if* clause, u0007.s03's *while*
clause, u0141.s05's *when* clause, u0203.s03's *such as* list), a modal the rule read as *may* (u0065.s02's ability
*can*), grouping inside a fixed phrase (u027, u106), or, once, a pair the matcher left unmatched against a Lean reading
that reads alike (u0241.s01).

**FAIL: D3 or D4 is revised before AP-3 or AP-4 merges, as the plan orders; there is no second run.** The bar fails
mostly on coverage (phrases with no reading under their declared vocabularies, the five D9 units among them), not on
wrong readings: only 1 of Lean's 26 readings was judged not a reading by both seats, and none skips a middle. These
percentages are evidence about the declared vocabularies (rule V for 33 of the 46 phrases), not a one-reading
guarantee.
