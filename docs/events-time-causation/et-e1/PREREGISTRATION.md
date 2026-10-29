# ET-E1 pre-registration: comprehension of the explicit wordings

Committed before the first model call (DRI decision 2026-10-27, `reviews/dri-decisions-20261027-featureplan-gates.md`
item 7). Nothing listed here is edited after the first call; a change after it would be a new, separately
registered run.

## What is tested

Plan: `docs/spec/events-time-causation-PLAN.md`, ET-E1 (section 5, "Experiments and triggers"), at main `0ca50f5d5`.
30 items in `items.json`, each with its expected answer:

- 20 items on the 13 wordings of 2.7 (one group per row of the table), each item a situation chosen at the
  boundary where a misreading shows: the same day for "before", "after", "no later than", "on or after"; the last day
  of "from ... through" and of "ends on"; a state with no stated end (persistence never assumed, F); "contributed to"
  against the but-for reading of "was necessary for"; `2026-10-12` (year-month-day, not 10 December) and "the date
  of this document".
- 10 items on the "until" reading sets of D9 written as their explicit candidates: U1 (the rule guarded by "if it is
  not the case that <E> happens no later than that day", silent from E's day) and U2 (U1 plus the opposite of the
  modality from E's day) for each modality: "may" (the T11 reading set: presumed innocent until a conviction, with
  the day before E and E's own day), "must" (T11b: the opposite is "need not"), "must not" (opposite "may") and
  "need not" (opposite "must"), on the later day 7 January 2027 of the distinguishing situation; and T11c's exclusive
  date candidate "on each day before 31 December 2026", asked about 31 December 2026 (the text does not say).

The texts carry no generated legend: a wording that is read correctly without the legend is read correctly with it.

## Prompt

`prompt.txt` holds the system prompt and the user-message template; `python3 run.py render <item-id>` prints the
exact prompt of an item. Options are lettered; the reply ends with `ANSWER: <letter>`. The scorer takes the letter
of the last `ANSWER` line; a reply with no such line, or a letter that is not an option, is scored incorrect.

## Reader and calls

Sonnet 5.5 (`claude-sonnet-5-5`, CLI default thinking) as the human proxy, through the `claude` CLI on the account
`pick-claude-account.sh` picks (an OAuth subscription login; no API key, no paid credits). Each item is asked
**5 times** (`samples_per_item`), each call a fresh session in an empty temporary directory with no tools and no
settings, 150 calls in all. Only transport errors (no JSON, CLI error, timeout) are retried, up to 3 attempts; a call
that still fails is saved with its errors and scored incorrect.

## Bar (from the plan)

- **Per wording**: at least 90% of the answers in the wording's group correct (`correct >= 0.9 * total`; with 5 or
  10 answers per group this means 5/5 or 9/10). Groups: the 13 rows of 2.7, `until-U1`, `until-U2` and
  `until-date` (`items.json` `wordings`).
- **"until" told apart**: for each modality the U1 and U2 items of `until_pairs` are paired sample by sample (sample
  k of U1 with sample k of U2); a pair is told apart when both answers are correct. Bar: at least 90% of the 20 pairs
  (18/20).

A wording below the bar gets a proposed rewording for ET-5 in RESULTS.md (not applied); ET-6 reruns only changed
wordings. The results are early evidence from a model proxy, not proof about human readers.
