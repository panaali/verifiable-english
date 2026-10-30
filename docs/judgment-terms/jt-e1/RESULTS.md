# JT-E1 results: proxy readability

**Status: INVALID for the JT-3 gate.** The recorded scores below describe the original calls; they cannot establish the pre-registered comparison. The identifier answer lines were invented rather than captured from main's renderer, and seven conditional controls omitted a named decider. The English arm supplied independent wording to all 20 constitution items whose template was rejected, contrary to the required identifier fallback. No model calls were repeated. A corrected measurement requires fresh items under [`jt-e1b/PROTOCOL.md`](../jt-e1b/PROTOCOL.md). The 40-item frozen frame and both arms are in [`PRE-REGISTRATION.md`](PRE-REGISTRATION.md) and [`items.tsv`](items.tsv); 80 separate raw call records remain in [`raw/`](raw/). Each record contains the exact prompt, full CLI result, model usage and answer.

| Arm | Fully correct / 40 | Rate | Critical misreadings |
|---|---:|---:|---:|
| Today's identifier/fallback wording | 16 / 40 | 40.0% | 0 |
| Plan 2.4 English | 37 / 40 | 92.5% | 0 |

English minus identifier in the invalid study: **21/40 = 52.5 percentage points**. The arithmetic clears the numerical thresholds, but **neither gate bar is validly measured** because the arms violated the protocol. A critical misreading means an answer whose key is `turns` or `conditional` was called SETTLED/CHECKED; class and decider errors count toward accuracy separately.

English errors: U04 was read as CONDITIONAL rather than TURNS; U18 and U19 were read as having no decider for the conditional conflict-freedom statement, though the frozen key names tribunal and court. None treated the dependent answer as settled or checked. Identifier errors: C01, C04, C07, C08, C10, C13, C14, C15, C16, C18, C20, U02, U04, U05, U06, U07, U08, U09, U10, U13, U14, U17, U18, U19. The raw explanations are retained for review.

All 80 CLI calls returned success with model `claude-sonnet-5-5`. The picker chose `claude-panaali2` for 75 and `claude-saeedi-danial` for 5, each checked as a Claude subscription; every result reported `fallback_credit: null`. Total charged CW by the frozen runner's usage sum was **205,437**, below 3M; 80 calls are below 100. The picker briefly withheld all accounts when the five-hour cap was reached, then resumed after eligibility returned. The three calls before that wait were reused, not repeated.

The frame has **20/40** judgments without a supplied template accepted by today's wording lint, all in the synthetic constitution subset. Their English arm used wording the specified renderer must not supply. The identifier arm used synthetic answer lines for future zone and criterion answers; JT-4 has not implemented those display routes. These violations invalidate the comparison.

**Next plan step:** Withdraw the JT-3 go-ahead. Run a corrected `jt-e1b` study on fresh items after the real display routes are available; decide the gate from that study only.
