# rsp-b-repair-1115: what the RSP translation still does not carry

This file lists the current limits of the units the B repairs touched. The repairs, their tests, the evidence and the
workflow notes are in `HISTORY.md` next to this file. The record for every other block is
`usecases/anthropic-rsp/accounting.d1.txt` and its saved report `docs/usecases/safetyfw/anthropic-rsp/accounting.json`.

## The D2 and D3 documents (`D2D3`)

- 3.1's coverage-date sentence opens "A Risk Report will cover the risks of Anthropic's models and actions as of a
  given coverage date". D3 carries the coverage date and its limit, "no more than 30 days prior to the publication of
  the report". What the sentence says a Risk Report covers, the risks of the company's models and actions, is in
  neither D2 nor D3: the accounting line of `D2D3` records it as a loss of class 1.
- Footnote 1 says "Catastrophic risk" "refers generally to risks of the most severe potential harms from advanced
  AI". D2 has one severity class, "catastrophic", with no definition and no ranking: the accounting line of `D2D3`
  records the definition as a loss of class 1. The footnote's two instances, "existential threats or fundamental
  destabilization of global systems", are carried in the words of the one harm constant `existential_threats`.
- "Scope.", the run-in heading of that 3.1 sentence, is recorded as exposition.

## F6 (`f6-strive-default`)

- Whether a Roadmap goal is revised "simply because we are unable to achieve them" is a fact each case states
  (`revised_because_unable`). VE does not decide the cause. A case that states the revision without this cause gets
  no duty from F6.

## F14 (`f14-full-review`)

- "(described below)" stays an exposition entry. The act's legend quotes it with the rest of F14's sentence; the
  process it points to (3.6.1 and 3.6.2) is carried by the F15 and F16 rules, not by this rule.

SIZE: 32 product, 190 tests, 1 other hand-written lines (added lines, `git diff --numstat` against the merge base; this item's docs not counted)
