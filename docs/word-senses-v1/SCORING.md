# Word-senses v1: scoring and bars (frozen before any build code; row word-senses-v1)

Ruling: reviews/dri-ruling-word-senses-20261127.md. Design: reviews/word-senses-design-1127.md page 2. The bars are fixed
here and are not tightened or loosened after any result. A bar missed: no tuning on the hashed sets; stop and report.

## What VE gives per question (branch word-senses-v1-1127, `ve read --json`)
- A plain answer: Yes / No / not determined / no answer.
- An answer both ways: a "same meaning" branch (Lean's answer over the merged document) and either one "different
  meanings" branch (Lean's answer over the split document) or, for a question on a raised word itself, one branch per
  statement use ("if '<word>' here means what it means in sentence N"). A branch may also be "VE cannot check that
  reading yet".
- A refusal of the whole text (including "the sentences cannot all be true together").

## Keys
- A (ordinary): yes / no / not decided, read as ordinary English. Set 1: the existing k2 keys (plain-vocab-1126
  scores2/seeded.tsv). Set 2 and the layer-1 texts: keys/ans-A.txt and keys/ans-B.txt (two fresh Opus 5.5 seats, the k2
  prompt unchanged). Tiers B and C: the current keys (plain-vocab-1126 scores2/b.tsv, b-fixes.tsv, rekey-b.tsv, c.tsv).
- ONE (one meaning per word throughout) and USES (per statement use of a marked word, every statement use of every
  marked word its own word): keys/branch-A.txt and keys/branch-B.txt (two fresh Opus 5.5 seats), sets 1 and 2.
- A key counts only where its two seats agree; a disagreement is excluded from that score and listed.
- C2 friction: keys/c2-A.txt and keys/c2-B.txt (two fresh Opus 5.5 seats): every repeated word same / different.

## Scoring a question
- PLAIN WRONG: a plain Yes or No that differs from key A (yes vs no, or Yes/No against not decided).
- BOTH WAYS is SAFE only if its "same meaning" branch matches key ONE (for tiers B and C, which have no ONE key: key A)
  AND every other branch is "not determined", "VE cannot check that reading yet", or matches its USES key. Otherwise it
  is BRANCH WRONG (a branch with a Yes/No and no agreed key counts as branch wrong).
- WRONG = PLAIN WRONG or BRANCH WRONG. A refusal or "not determined" against a yes/no key is a MISS, never a wrong.
- A text counts as wrong when any of its questions is wrong.

## Bars
(a) Set 1 (the 10 existing seeded texts): at most 1 of 10 texts wrong (0 recorded as the goal). Set 2 (20 new texts): at
    most 2 of 20 texts wrong, and at most 1 of the 10 no-giveaway texts; the one-sided 95% exact upper bound on the
    wrong rate is stated next to each count (0 of 10: 25.9%). Control questions (key A yes, the in-meaning question)
    reported per branch. Scored with the AI reader (two runs, either raises); the list-only figure is reported.
(b) Friction, C2 (20 new tier-C texts) with the AI reader: NEEDLESS = a both-ways answer (or interactive question) all of
    whose raised words both C2 keys mark "same". Bar: fewer than 4 needless items in the 20 texts. Reported only: the
    list-only figure, and the both-ways answers on the 34 texts of today (19 tier B, 15 tier C; the 5 B-fix texts are also
    reported). Also reported: C2 texts that reuse a word in two senses or on two kinds and read without rewriting.
(c) Layer 1 (10 seeded word-on-two-kinds texts, at least 3 with "is not"): all 10 read (no refusal) and 0 wrong against
    key A. Reported: how many C2 texts refused on main for a word on two kinds read on the branch.
(d) Tiers B and C (today's texts, current keys): 0 wrong, with the AI reader and with the word list alone. 0 trusted
    lines (no file under lean/ and no trusted file changes). Reported: the count of answer-affecting untrusted steps.
Reader agreement between the two runs (per raised-candidate word: same verdict in both) is reported.
