Faithful: **18/20 sampled + 0/0 changed**. `changed_units` is empty.

Sampling: Python `random.Random("20261013T0600Z")`; five draws from each id-sorted pool, in CHECKED/LABELLED/OPEN/READINGS order. Source hash and all sampled span bindings match. No model calls.

```text
VERDICTS:
u022c FAITHFUL
u025 FAITHFUL
u026 FAITHFUL
u028 FAITHFUL
u029 FAITHFUL
u035 FAITHFUL
u044 FAITHFUL
u045a FAITHFUL
u046 FAITHFUL
u049 UNFAITHFUL
u052 FAITHFUL
u061 FAITHFUL
u066 FAITHFUL
u070 FAITHFUL
u077 UNFAITHFUL
u084a FAITHFUL
u100a FAITHFUL
u109 FAITHFUL
u113 FAITHFUL
u114 FAITHFUL
```

**Unfaithful units:** u049 and u077 have incomplete reading sets. Both restrict “his country” to nationality or residence and explicitly claim these exhaust its meanings. Ordinary English also permits a country of origin or homeland that remains “his country” after emigration and a nationality change. Neither encoded alternative preserves that possibility. Retain an open person–country relationship instead of asserting that these two specifications exhaust the phrase.

The remaining sampled units preserve their source content and qualifications; the headings are correctly labelled. I found no invented duty bearer in the sampled candidates.

Three highest-value missing features:

1. **Compositional act phrases:** preserve coordinated objects, embedded clauses and qualifications structurally; act-phrase grammar blocks 11 units.
2. **Composable rights and norms:** express right inclusion, equality and conditions across readings without introducing unstated duty bearers; seven norm and four right-inclusion units remain blocked.
3. **Open relational references:** represent phrases such as “his country” without prematurely fixing their relationship to nationality or residence; this addresses both audit failures.

`AUDIT.md` was not written: the requested directory is outside the sandbox’s writable roots.