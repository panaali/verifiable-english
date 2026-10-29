# JT-E1 results: proxy readability

**Status: PASS on both pre-registered bars.** This is Sonnet 5.5 proxy readability, not human comprehension. The 40-item frozen frame and both arms are in [`PRE-REGISTRATION.md`](PRE-REGISTRATION.md) and [`items.tsv`](items.tsv); 80 separate raw call records are in [`raw/`](raw/). Each record contains the exact prompt, full CLI result, model usage and answer. No answer key was sent to the reader.

| Arm | Fully correct / 40 | Rate | Critical misreadings |
|---|---:|---:|---:|
| Today's identifier/fallback wording | 16 / 40 | 40.0% | 0 |
| Plan 2.4 English | 37 / 40 | 92.5% | 0 |

English minus identifier: **21/40 = 52.5 percentage points**. Bar (a), “At least 90% correct with 2.4's English, and at least 15 points above the identifier arm,” **PASS** (37 ≥ 36 and 21 ≥ 6). Bar (b), “No critical misreading in 40: an answer that turns on a judgment read as settled or checked,” **PASS** (0/40 English; also 0/40 identifier). A critical misreading means an answer whose key is `turns` or `conditional` was called SETTLED/CHECKED; class and decider errors count toward accuracy separately.

English errors: U04 was read as CONDITIONAL rather than TURNS; U18 and U19 were read as having no decider for the conditional conflict-freedom statement, though the frozen key names tribunal and court. None treated the dependent answer as settled or checked. Identifier errors: C01, C04, C07, C08, C10, C13, C14, C15, C16, C18, C20, U02, U04, U05, U06, U07, U08, U09, U10, U13, U14, U17, U18, U19. The raw explanations are retained for review.

All 80 CLI calls returned success with model `claude-sonnet-5-5`. The picker chose `claude-panaali2` for 75 and `claude-saeedi-danial` for 5, each checked as a Claude subscription; every result reported `fallback_credit: null`. Total charged CW by the frozen runner's usage sum was **205,437**, below 3M; 80 calls are below 100. The picker briefly withheld all accounts when the five-hour cap was reached, then resumed after eligibility returned. The three calls before that wait were reused, not repeated.

The frame has **20/40** judgments without a supplied template accepted by today's wording lint, all in the synthetic constitution subset. Their English arm is an experimental filling of plan 2.4; it is not a claim that JT-3 can currently display those lines. The identifier arm uses today's fallback identifier wording and a synthetic identifier-shaped answer for the future zone/criterion answers; JT-4 has not implemented those answer routes. These limits matter when using the result to write JT-3, but do not change the frozen bars.

**Next plan step:** JT-3 may use 2.4's wording. No wording revision is triggered by these bars. A fresh-item `jt-e1b` rerun is required only if a later review invalidates a bar or the wording is revised.
