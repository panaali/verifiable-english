# Scores of the three stand-in newcomers against the fixed key

The key: tour/NEWCOMER-QUESTIONS.md as last changed in commit 8648d5fb50 (28 November 2026, 02:29 UTC), sha256
f60c3a7361a93964c3c9807768c89b9dc3716745d14bcec3114996a8621458d2. A question is right when the answer contains the
key's point; wording is free. The stand-ins never saw the key (it was removed from their copies).

**Result: run 1, run 2 and run 3 each answered 5 of 5 right; none reported an error** (each report's part B says
"None"). The pass rule set before the runs (at least 2 of 3 answer all five right, none hits an error) is met.

**Who graded**: an AI, not a person. The session that ran the stand-ins (Claude Opus 5.5) graded them on 27 November
2026 (5 of 5 each); a second Claude Opus 5.5 session graded them again from these files on 28 November 2026, with
the same result. A third Claude Opus 5.5 session checked the fifteen grades against the fourth version of the key
(below) on 28 November 2026, with the same result. All graders are made by the same company as the stand-ins
(Anthropic). No person has graded them.

## Each answer

The last column quotes the answer's own words that carry the key's point (fragments separated by " / ", each
copied from that run's report).

| run | question | grade | the answer's words |
|---|---|---|---|
| 1 | 1 | right | VE gives the exact sentences the answer rests on, quoted by number / VE's own checker, written in Lean, has already replayed the proof from those sentences |
| 1 | 2 | right | means the text rules the answer out / means the rules neither give the conclusion nor rule it out / VE shows a concrete situation where every rule holds but the conclusion fails |
| 1 | 3 | right | VE refuses and does not guess / names the unknown phrase, and suggests nearby known wordings / it offers one clearer question per reading / it keeps all readings and answers under each one |
| 1 | 4 | right | Lean only checks that answers follow from the rules it is given. It does not check that the rules say what the policy says / a separate AI reader that compares the translation with the policy / a set of answers written in advance from the policy alone |
| 1 | 5 | right | It cannot multiply amounts or take percentages / On long real texts it cannot answer questions in your own words, only the ones written with each case |
| 2 | 1 | right | VE names the sentences the answer rests on, and only those / The proof behind it is replayed by VE's checker, a program written in Lean |
| 2 | 2 | right | means the text doesn't settle the question, and nothing rules the answer out / a concrete counter-example: a situation where every sentence holds but the answer fails / is for when the text rules the answer out |
| 2 | 3 | right | VE refuses. It says there is no reading, names the unknown phrase and suggests nearest known wordings / VE won't pick one. It offers one question per reading / VE keeps all of them and answers under each reading separately |
| 2 | 4 | right | Lean checks that answers follow from the rules it is given, not that the rules say what the policy says / an AI reader that compares the translation with the policy part by part / answers written in advance from the policy alone |
| 2 | 5 | right | It can't multiply amounts or take percentages / On long real texts it can't answer your own question in your own words |
| 3 | 1 | right | VE gives the sentences the answer rests on (stop 1: sentences 1 and 3, quoted word for word) / The reasoning is checked by VE's own checker, written in Lean |
| 3 | 2 | right | means the text rules the thing out / means the text doesn't settle it: it neither forces the thing nor excludes it / VE shows a concrete counter-example situation where every rule holds and the thing fails |
| 3 | 3 | right | VE won't pick a reading. It offers one rewritten question per reading / it refuses and says why. It names the unknown phrase and suggests the nearest known wordings / it keeps all the readings and answers under each one |
| 3 | 4 | right | Lean only checks that answers follow from the rules it is given. It does not check that the rules say what the policy says / A separate AI reader compares the translation with the policy / Answers written in advance from the policy alone |
| 3 | 5 | right | It cannot multiply amounts or take percentages / it answers only the questions written with each case, word for word. You cannot ask your own questions in your own words |

Two notes on the grading:
- Question 1: the key says "Lean (the proof checker) checks the steps"; the page the stand-ins read says the checker
  is VE's own program written in Lean, not Lean's small proof kernel. All three answers say the finer thing; each is
  graded right.
- Question 4: the first three versions of the key called the reader "independent", a word the page no longer uses
  (the reader is an AI of the translators' own model family); the fourth calls it "separate", as the page does. All
  three answers describe the reader as the page does.

## How the key changed (git log -p tour/NEWCOMER-QUESTIONS.md)

The key has four commits; nothing has changed it since the fourth.

1. **4454de2d3f, 26 November 2026, 08:33 UTC**: the five questions and the first key, "fixed before the first
   newcomer run". Round 1 started at 09:48 UTC and round 2 at 09:55 UTC, both on the first version of the page.
2. **0d184debe9, 26 November 2026, 12:58 UTC**: written after rounds 1 and 2 had been read, in the same commit that
   revised the page, and before round 3 (13:02 UTC). The five questions did not change; the title changed ("the
   stand-in newcomers" became "the test readers"), and so did key points 3, 4 and 5:
   - point 3 added the case the revised stop 3 shows: a question with several readings gets one question per
     reading (every / some), not an answer;
   - point 4 added a second accepted answer: the reader that compares the translation with the policy, beside the
     answers written in advance ("Either one is right"). This widened what counts as right;
   - point 5's list changed: "multiply amounts" became "multiply amounts or take percentages"; "follow duties
     through time" and "list clauses and assumptions on the company-policy route" were dropped; "give checked
     answers to must/may questions on main" and "print the sentences an answer rests on in the company-policy route"
     were added.
3. **86972ff1eb, 28 November 2026, 02:13 UTC**, after round 5 had been graded: point 4's parenthesis "it flags the
   planted part" became the counted reader figures of stop 9 (in five runs the reader raised the day-count problem
   every time and named the planted part in three).
4. **8648d5fb50, 28 November 2026, 02:29 UTC**, a review fix to the third: point 4 calls the reader "separate", not
   "independent", and its parenthesis gives the figures like for like (same prompt, no mistake list; the right rule
   named in three of five, two at high confidence; none of five on the translation as written).

   Neither the third nor the fourth changed what counts as right: point 4 still accepts either the reader that
   compares the translation with the policy or the answers written in advance, and the parenthesis reports what that
   reader did, which no answer is asked to repeat.

Rounds 3, 4 (void) and 5 were graded against the second version, and round 5 again against the fourth, with the
same fifteen grades. The three runs kept here are round 5 (README.md in this folder). All fifteen answers would also be right under the first key: each answer to question 3
names the refusal of an unknown word and the keeping of all readings of a sentence, each answer to question 4 names
the answers written in advance from the policy alone, and each answer to question 5 names multiplying amounts and
free-form questions on long real texts.
