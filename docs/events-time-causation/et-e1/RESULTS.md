# ET-E1 results: comprehension of the explicit wordings

**Early evidence from a model proxy (Sonnet 5.5), not proof about human readers.** Pre-registration
`PREREGISTRATION.md` committed in `4158614c2` at 2026-10-28T13:12:51Z; the 150 calls ran from 13:13:10Z to
13:16:17Z on the subscription account `claude-panaali2` (OAuth, no API key), model `claude-sonnet-5-5` in every
answer, with no transport errors or retries. Raw answers: `raw/<item>__s<k>.json`; scores: `results.json`
(`python3 run.py score` reproduces them).

**Summary: 13 of the 16 groups pass, including all 13 wordings of 2.7, U2 and the date candidate. `until-U1` is
below the bar (13/25), and so is "until" told apart (8/20).** For "must" and "must not", the reader reads the
silent candidate U1 as if it said U2.

## Per wording

| Group | Wording | Correct / total | Verdict |
|---|---|---|---|
| happens-on | `<event> <vp> on <day>` | 5/5 | PASS |
| begins-ends-on | `begins on` / `ends on` | 10/10 | PASS |
| is-before | `<day> is before <day>` | 10/10 | PASS |
| is-after | `<day> is after <day>` | 5/5 | PASS |
| no-later-than | `<day> is no later than <day>` | 10/10 | PASS |
| on-or-after | `<day> is on or after <day>` | 5/5 | PASS |
| from-through | `each day from <day> through <day>` | 5/5 | PASS |
| event-vs-day | `<event> <vp> before / no later than <day>` | 10/10 | PASS |
| event-vs-event | `<event> <vp> before / on the same day as <event>` | 10/10 | PASS |
| in-progress | `<state> is in progress on <day>` | 10/10 | PASS |
| contributed-to | `<cause> contributed to <effect>` | 5/5 | PASS |
| necessary-for | `<cause> was necessary for <effect>` | 5/5 | PASS |
| named-dates | `2026-10-12`, `the date of this document` | 10/10 | PASS |
| until-U1 | rule guarded by "if it is not the case that <E> happens no later than that day" | 13/25 | **BELOW BAR** |
| until-U2 | U1 plus the opposite modality from E's day | 20/20 | PASS |
| until-date | "on each day before 31 December 2026", asked on 31 December | 5/5 | PASS |
| **"until" told apart** | U1 and U2 both correct, paired sample by sample | 8/20 | **BELOW BAR** |

## "until": where U1 fails

| Item | Expected | Answers (5 samples) | Correct |
|---|---|---|---|
| `t11-may-u1-before-e` (4 January, before E) | D permitted | D D D D D | 5 |
| `t11-may-u1-e-day` (5 January, E's day) | E says nothing | C C C C E | 1 |
| `t11b-must-u1-later` (7 January) | E says nothing | C C C C C | 0 |
| `mustnot-u1-later` (7 January) | E says nothing | D D E E D | 2 |
| `neednot-u1-later` (7 January) | E says nothing | E E E E E | 5 |

The told-apart pairs were: "may" 1/5, "must" 0/5, "must not" 2/5 and "need not" 5/5. Every U2 answer was correct.
The day comparisons are not the problem. In every reply the reader found the guard false on E's day and later
(the "no later than" reading of E's own day is right in every sample). What goes wrong is the next step: once the
rule does not apply, the reader fills in a default. If an obligation does not apply, the act is "not required"
(C, which is U2's "need not"). If a prohibition does not apply, the act is "permitted" (D, which is U2's "may"). If
a permission does not apply, the act is "not permitted", and the reader then picked C. One reply says this outright
(`raw/t11b-must-u1-later__s0.json`): "the condition for the requirement is not met on 7 January, and the text
imposes no requirement that day". This is the allow-style completion that D9 notes can make U1 and U2 coincide.
Under `norm-defaults@0` with the predicate unspecified, VE answers UNDECIDED here, and readers do not. "Need not"
passes because a lifted "need not" suggests no default.

A confound to settle in the rerun: options C and D read "It is not required ..." and "It is permitted ...". A reader
can take them as "no requirement is stated" and not as "the text says it is not required". The pattern shows up only
for the modalities that have a natural default, and every U2 item passes, so the options probably do not explain the
whole effect. They may explain part of it.

## Proposed rewording for ET-5 (not applied)

**until-U1.** State the silence in the text instead of leaving it implied. After each U1 rule, add a sentence
that says the document is silent on the days the guard excludes. For T11:

> Every person may be presumed innocent on each day, if it is not the case that there is a conviction such that
> that conviction is of that person and that conviction happens no later than that day. **This document does not
> say whether a person may be presumed innocent on a day on which a conviction of that person happens no later than
> that day.**

Use the same pattern for every modality ("does not say whether <x> must / must not / need not <act> on a day on
which ..."). The block's legend should also get the line: "A rule says nothing about the days its condition
excludes: on those days the document does not say whether the act is required, permitted or forbidden." Whether
the silence sentence is a profile wording (Lean-checked, like 2.7's) or a generated display line is ET-5's and
english-lean's to decide (2.7, X9).

**"until" told apart.** This needs no separate wording. The failures come only from U1, so the U1 rewording above is
the fix. The `until` advice row in 2.7 already tells authors to add the U2 rule when the rule stops.

**For the ET-6 rerun** (changed wordings only, i.e. the five U1 items and the four pairs), reword options C and D
to "The text says it is not required ..." and "The text says it is permitted ...". Then a miss can only come from
the wording.
