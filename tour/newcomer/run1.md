# Stand-in newcomer, run 1

A stand-in, not a person: a fresh claude-sonnet-5-5 session that knew nothing of the project (see README.md in this folder for how it was run and what was removed from the record). It made 5 tool calls in 103 seconds. Every call and its output follow in order, then its report.

## Call 1: Read

```json
{
 "file_path": "<newcomer>/verifiable-english/tour/README.md"
}
```

Output: the tour page, 798 lines, not repeated here (sha256 of its text without the line numbers: c1350a65a9fc2a4f01e28ef5fd7d1a180469fc3fc4def308fec059839fdad01a; README.md in this folder says which version it is).

## Call 2: Bash

```sh
cd <newcomer>/verifiable-english && time sh tour/install.sh 2>&1 | tail -30
```

Output:

```
rustup 1.29.3 (edbc831ce 2026-11-02)
==> rustup (Rust): done in 0 s
==> rust toolchain (rust-toolchain.toml)
==> rust toolchain (rust-toolchain.toml): done in 1 s
==> uv sync --locked
Resolved 59 packages in 2ms
Checked 58 packages in 1ms
==> uv sync --locked: done in 0 s
==> lake build (Lean; the first build is the long one)
The first Lean build takes 20 to 40 minutes (a line every minute while it runs); a later run takes seconds.
Build completed successfully (1478 jobs).
==> lake build (Lean; the first build is the long one): done in 2 s
==> rust build
5aeecbc57d8c24a7d18e1bf2602c15258ddfebf65c3cfc66f53e6c73ed8da8f2  <newcomer>/verifiable-english/rust/target/release/ve: pinned in <newcomer>/verifiable-english/lean/checkers.lock
==> rust build: done in 1 s
==> all steps done in 4 s
Next (DEMO.md step 4): uv run python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json
If uv is not found in a new shell, run first: export PATH="$HOME/.local/bin:$PATH"
==> the after-release checkout (.tour-after-release/)
after-release checkout at a5dde317c4 (2026-11-26)
==> the after-release checkout (.tour-after-release/): done in 0 s
==> after-release builds
Build completed successfully (1480 jobs).
==> after-release builds: done in 2 s
==> uv sync --locked (after-release)
Resolved 59 packages in 2ms
Checked 58 packages in 1ms
==> uv sync --locked (after-release): done in 0 s
==> tour install: all done in 7 s
Next: sh tour/stops/01-yes.sh

real	0m6.843s
user	0m2.366s
sys	0m1.377s
```

## Call 3: Bash

```sh
for s in 01-yes 02-not-necessarily 03-every-or-some 04-date 05-sum; do echo "##### $s"; sh tour/stops/$s.sh 2>&1; echo "[script exit $?]"; done
```

Output:

```
##### 01-yes
$ uv run --frozen python -m ve ask tour/texts/club.ve.md "Is Ann eligible?"
You asked whether Ann is eligible.
Yes.
Sentence 1 says: "Every member who is active is eligible."
Sentence 3 says: "Ann is active."
[script exit 0]
##### 02-not-necessarily
$ uv run --frozen python -m ve ask tour/texts/club.ve.md "Is Bo eligible?"
You asked whether Bo is eligible.
Not necessarily.
Here is a situation the document allows where it fails: ann is a member; bo is a member; ann is active; ann is eligible; bo is junior; bo is supervised.
[script exit 0]
##### 03-every-or-some
$ uv run --frozen python -m ve ask tour/texts/club.ve.md "Is a member eligible?"
VE cannot tell whether "a" here means every or some. Ask one of these instead:
Is every member eligible?
Is some member eligible?
[exit code 2]
[script exit 0]
##### 04-date
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python ../tour/stops/dates.py
Rule 1: If the return date is after the last day of the period of 21 days beginning with the borrowing date, then the person is late.
Rule 2: If the return date is on or before the last day of the period of 21 days beginning with the borrowing date, then the person is on time.
Borrowed on Tuesday 3 November 2026.
Lean works out the last day of the loan: Monday 23 November 2026.
Ann returned it on Tuesday 24 November 2026. Is Ann late? Yes: Lean checked it.
Bo returned it on Monday 23 November 2026. Is Bo on time? Yes: Lean checked it.
Ann returned it on Tuesday 24 November 2026. Is Ann on time? VE has no proof that Lean accepts, so it does not say Ann is on time.
[script exit 0]
##### 05-sum
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python ../tour/stops/sums.py
The rule: The bill equals the sum, over each pizza that is charged, of the price of the pizza.
The order:
  p1: margherita, £9.50, arrived 22 minutes after the order, charged
  p2: pepperoni, £11.00, arrived 22 minutes after the order, charged
  p3: four cheese, £10.50, arrived 41 minutes after the order, not charged (free: the 30-minute promise)
VE's reading of the rule for this order:
  The pizzas of this case are exactly p1, p2 and p3.
  If "p1" is charged, then the amount counted for the pizza (p1) equals the price of the pizza (p1).
  If it is not the case that "p1" is charged, then the amount counted for the pizza (p1) equals GBP 0.00.
  If "p2" is charged, then the amount counted for the pizza (p2) equals the price of the pizza (p2).
  If it is not the case that "p2" is charged, then the amount counted for the pizza (p2) equals GBP 0.00.
  If "p3" is charged, then the amount counted for the pizza (p3) equals the price of the pizza (p3).
  If it is not the case that "p3" is charged, then the amount counted for the pizza (p3) equals GBP 0.00.
  The bill equals the sum of the amount counted for the pizza (p1), the amount counted for the pizza (p2) and the amount counted for the pizza (p3).
Is the bill £20.50? Yes: Lean checked the addition.
Is the bill £31.00? VE has no proof that Lean accepts, so it does not say so.
[script exit 0]
```

## Call 4: Bash

```sh
for s in 06-checker 07-company-policy 08-outside-the-text 09-planted-mistake 10-not-yet 11-longer-example 12-write-your-own; do echo "##### $s"; if [ $s = 06-checker ]; then sh tour/stops/$s.sh > /tmp/06.out 2>&1; echo "[exit $?]"; wc -l /tmp/06.out; else sh tour/stops/$s.sh 2>&1; echo "[script exit $?]"; fi; done
```

Output:

```
##### 06-checker
[exit 0]
374 /tmp/06.out
##### 07-company-policy
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python -m ve ask usecases/gitlab_relocation "Does Ivo meet the policy’s requirement to reside in their primary location in 2028?" --case R009
no
$ uv run --frozen python -m ve ask usecases/gitlab_relocation "May Ivo live and work outside their primary location for the stays described in 2028?" --case R009
no
[script exit 0]
##### 08-outside-the-text
$ uv run --frozen python -m ve ask tour/texts/club.ve.md "Is Ann retired?"
The question has no reading with the current vocabulary. Closest sentence tried: "Ann is retired.". Unknown English phrase 'is retired'. Nearest declared wordings: 'is active'; 'member'; 'is junior'.
[exit code 2]
[script exit 0]
##### 09-planted-mistake
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python ../tour/stops/planted.py
The planted mistake: a stay's days are counted without its last day, so Ivo's 184 days in Spain count as 183.
The reader read exactly this planted file: yes (same SHA-256)

1. The reader's check: an AI model of the translators' own model family (recorded 2026-11-26; running it again needs an AI model account).
  It flags part 6 of the policy (the 183-day rule), with high confidence:
  The policy says:      U6: 'must reside in their primary location for at least 183 days ... may live or work
                        outside their permanent location ... for a maximum total of 183 days'
  The translation says: _days: Eq(sn_s, sg_s) with sg_s = elapsed_days(sf_s, sl_s), i.e. a stay's days = last day
                        minus first day (R1)
  Why it matters:       A stay from 1 Jan to 1 Jan, which is one day away, counts as 0 days, so every stay is
                        undercounted by one day. That pushes 'out' down and 'inn' up and can give a definite
                        resok/outok/workok YES (and ltr/comp NO) when the person has actually gone over 183 days
                        outside. The separate sg/sn bases and R3's '-1' both fit inclusive counting (sn = sg + 1),
                        so the rule is also inconsistent with the rest of the translation.
  It raised 3 other flags: part 6 (low), part 15 (high), part 16 (low). It raised 3 of them (same part, kind and confidence) on the translation as written too.

2. The answers, compared with answers written from the policy alone before the translation ran:
  Does Ivo meet the policy’s requirement to reside in their primary location in 2028?
    policy alone: no; translation as written: no; with the mistake: yes (caught)
  May Ivo live and work outside their primary location for the stays described in 2028?
    policy alone: no; translation as written: no; with the mistake: yes (caught)
[script exit 0]
##### 10-not-yet
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python ../tour/stops/not_yet.py
The rule: The late fee equals the daily fee plus the daily fee.
  VE reads it (one reading).
The rule: The late fee equals the daily fee times the number of days late.
  VE refuses to read it (SyntaxError): it has no reading of this sentence.
The rule: The late fee equals 10 percent of the price of the book.
  VE refuses to read it (SyntaxError): it has no reading of this sentence.
[script exit 0]
##### 11-longer-example
$ uv run --frozen python -m ve ask usecases/question-answering/udhr-part07.ve.md "May every person form as well as join trade unions to protect their interests?"
You asked whether every person may form as well as join trade unions to protect their interests.
If sentence 1 means "Every person is classified as "has_the_right_to_form_and_join_trade_unions"", the text does not settle this.
Here is a situation where the answer depends on what the text leaves unsaid: e0 is a person; e0 is classified as "has_the_right_to_education"; e0 is classified as "has_the_right_to_form_and_join_trade_unions", reading sentence 1 as "Every person is classified as "has_the_right_to_form_and_join_trade_unions"" and sentence 10 as "Every person is classified as "has_the_right_to_education"".
The text does not say whether e0 may form as well as join trade unions to protect their interests.
If sentence 1 means "Every person must be left free to form as well as join trade unions to protect their interests" (VE has not checked this wording), the text does not settle this.
Here is a situation where the answer depends on what the text leaves unsaid: e0 is a person; e0 is classified as "has_the_right_to_education", reading sentence 1 as "Every person must be left free to form as well as join trade unions to protect their interests" (VE has not checked this wording) and sentence 10 as "Every person is classified as "has_the_right_to_education"".
The text does not say whether e0 may form as well as join trade unions to protect their interests.
If sentence 1 means "Every person may form as well as join trade unions to protect their interests" (VE has not checked this wording), yes.
Sentence 1 says: "4. Everyone has the right to form and to join trade unions for the protection of his interests."
VE did not use 9 sentences of this document that it could not read formally: sentences 3, 5, 6, 7, 8, 11, 17, 18 and 19.
[script exit 0]
##### 12-write-your-own
$ uv run --frozen python -m ve read tour/texts/own-rules.txt
I read these words as:
  member: a kind of thing (noun; 5 senses in the list)
  active: a property of members (adjective; 14 senses in the list: this text reads it with ONE meaning throughout, check every use means the same)
  allowed: a property of members (participle of allow; 10 senses in the list: this text reads it with ONE meaning throughout, check every use means the same)
  paid: a property of members (adjective or participle of pay; 14 senses in the list: this text reads it with ONE meaning throughout, check every use means the same)
  suspended: a property of members (adjective or participle of suspend; 7 senses in the list: this text reads it with ONE meaning throughout, check every use means the same)
  Ann: a member (line 4)
Lean read every sentence: 5 of 5 CHECKED (177 of 177 bytes, 100%).
  Sentence 1 (line 1): "Every member who is paid is active." CHECKED
  Sentence 2 (line 2): "Every member who is active and is not suspended is allowed." CHECKED
  Sentence 3 (line 3): "Every member who is suspended is not allowed." CHECKED
  Sentence 4 (line 5): "Ann is paid." CHECKED
  Sentence 5 (line 6): "Ann is not suspended." CHECKED
Question (line 7): Is Ann allowed?
  You asked whether Ann is allowed.
  Yes.
  Sentence 1 says: "Every member who is paid is active."
  Sentence 2 says: "Every member who is active and is not suspended is allowed."
  Sentence 4 says: "Ann is paid."
  Sentence 5 says: "Ann is not suspended."
$ uv run --frozen python -m ve read tour/texts/own-rules-new-word.txt
Not read: 1 problem; nothing is answered.
- line 1: 'overlimit' is not in the word list (oewn-2025); after 'is' VE reads an adjective or a past participle.
  Fix (add this line): Words: overlimit (property of member)
[exit code 2]
$ uv run --frozen python -m ve read tour/texts/own-rules-new-word-fixed.txt
I read these words as:
  member: a kind of thing (noun; 5 senses in the list)
  allowed: a property of members (participle of allow; 10 senses in the list: this text reads it with ONE meaning throughout, check every use means the same)
  overlimit: a property of members (declared in the text, line 1)
  paid: a property of members (adjective or participle of pay; 14 senses in the list: this text reads it with ONE meaning throughout, check every use means the same)
  Ben: a member (line 4)
Lean read every sentence: 4 of 4 CHECKED (135 of 135 bytes, 100%).
  Sentence 1 (line 2): "Every member who is paid and is not overlimit is allowed." CHECKED
  Sentence 2 (line 3): "Every member who is overlimit is not allowed." CHECKED
  Sentence 3 (line 5): "Ben is paid." CHECKED
  Sentence 4 (line 6): "Ben is overlimit." CHECKED
Question (line 7): Is Ben allowed?
  You asked whether Ben is allowed.
  No. The document rules this out.
  Sentence 1 says: "Every member who is paid and is not overlimit is allowed."
  Sentence 2 says: "Every member who is overlimit is not allowed."
  Sentence 4 says: "Ben is overlimit."
[script exit 0]
```

## Call 5: Bash

```sh
sleep 1; grep -n -E "^(Entitled|Payment|Taken|Kept|Question|Answer|Lean check|Assumptions)" /tmp/06.out; sed -n 1,12p /tmp/06.out
```

Output:

```
2:Entitled: YES
3:Payment: £200.00
4:Taken back by HMRC: NO
5:Kept: £200.00
10:Question 1. Is the applicant entitled to a Winter Fuel Payment for winter 2026 to 2027?
11:Answer: YES
173:Assumptions (taken as given, not checked):
228:Lean check: this answer rests on 15 proof steps; 15 of 15 proof steps accepted by Lean; the answer was checked by Lean and accepted.
231:Question 2. How much is the payment?
232:Answer: £200.00
314:Assumptions: those listed above, plus:
330:Lean check: this answer rests on 18 proof steps; 18 of 18 proof steps accepted by Lean; the answer was checked by Lean and accepted.
333:Question 3. Does HMRC take the payment back because the applicant's total income is over £35,000?
334:Answer: NO
338:Assumptions: those listed above, plus:
357:Lean check: this answer rests on 19 proof steps; 19 of 19 proof steps accepted by Lean; the answer was checked by Lean and accepted.
360:Question 4. How much does the applicant keep after that?
361:Answer: £200.00
365:Assumptions: those listed above, plus:
374:Lean check: this answer rests on 21 proof steps; 21 of 21 proof steps accepted by Lean; the answer was checked by Lean and accepted.
$ uv run --frozen python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json
Entitled: YES
Payment: £200.00
Taken back by HMRC: NO
Kept: £200.00

Winter Fuel Payment, winter 2026 to 2027: the answers for one applicant, with the clauses
and assumptions each answer rests on.

Question 1. Is the applicant entitled to a Winter Fuel Payment for winter 2026 to 2027?
Answer: YES
```

## Report (the session's final reply)

**A. Where I stumbled**

- **Opening section.** This was the heaviest part. These phrases were unexplained or confusing:
  - "Lean's small proof kernel".
  - "`checkCertificate_sound`".
  - "the trusted base". It is only a link, and I was told not to follow it.
  - "per-text program".
  - "replayed proof".
  - The four meanings of "Lean checked", which are listed before I had seen any stop.
- **Stop 1.** The text shown has no line saying "Ann is a member". Stop 2's counter-example, though, lists "ann is a member; bo is a member". I had to guess that membership is implied or hidden.
- **Stop 2.** The page says "Lean checked that this situation obeys every sentence". It is not clear how Lean "checks" a counter-example, or what "replayed" means here. The lower-case names are explained, but only in brackets.
- **Stop 4.** The page says the reading of the date words is "tested but not checked by Lean". I could not tell what that means for how much to trust the result. The last line, "VE has no proof that Lean accepts, so it does not say…", reads awkwardly.
- **Stop 5.** The "£20.50 or £31.00" setup is explained clearly. "Its search for a proof has a limit" is vague.
- **Stop 6.**
  - The page shows an abridged output, so I could only partly compare it. I counted 374 lines, which matches.
  - "the checker's dates start in 1970" is unexplained.
  - "Read as" lines are said to be unchecked, which seems odd next to "Lean checked".
- **Stop 7.** The answers print as bare lowercase "no", unlike "No." elsewhere. "encoder", "runner" and "`--case R009`" are jargon. The page asks me to accept that I cannot ask my own question.
- **Stop 9.**
  - This was the hardest stop to follow: two checks, two AI families, and the "(caught)" labels.
  - The page says "Lean checked nothing", yet the summary says "Lean would accept the planted rules anyway". I had to work out that both are true.
  - The recorded AI output includes unexplained shorthand such as `sg_s`, `R1`, "resok/outok/workok" and "ltr/comp".
- **Stop 12.**
  - "5 of 5 CHECKED" counts rules and facts but not the "Ann is a member" line. Sentence 4 is on line 5, so the numbers look off until the later explanation.
  - "CHECKED" sounds like "true", and the page has to say it does not mean that.
- **Install.** The output ended with a leftover "Next (DEMO.md step 4): uv run python usecases/eligibility/ask.py …", then a different "Next: sh tour/stops/01-yes.sh" at the very end. The first one points away from the page. The install took 7 seconds, not the page's 17. That is expected, since it was already done.

I found no differences from "What you should see" in stops 1–5 or 7–12. For stop 6 I only checked the lines the page shows, and they match.

**B. Errors**

None. Every command finished with exit code 0. The only non-zero codes were the expected "[exit code 2]" lines in stops 3, 8 and 12.

**C. Answers**

1. **A "Yes".** VE gives the exact sentences the answer rests on, quoted by number. In stop 1 those were sentences 1 and 3. Sentences that aren't needed are left out. VE's own checker, written in Lean, has already replayed the proof from those sentences, so no separate "checked" line appears. This checker is VE's program, not Lean's small kernel. Trusting it means trusting that program and the code that turns the English into its input.

2. **"Not necessarily" and "No".**
   - "Not necessarily" means the rules neither give the conclusion nor rule it out. For example, nothing says Bo is active.
   - "No" means the text rules the answer out. In stop 12 it said "The document rules this out" and named the sentences.
   - To back up "Not necessarily", VE shows a concrete situation where every rule holds but the conclusion fails. In stop 2, Bo is junior and supervised but not active, so Bo is not eligible.

3. **Undefined words or ambiguity.** VE refuses and does not guess. For an ambiguous reading ("Is a member eligible?"), it offers one clearer question per reading and exits with code 2. For an unknown word ("Is Ann retired?"), it says there is no reading, names the unknown phrase, and suggests nearby known wordings. These are different questions, not restatements. In stop 12 it refuses the whole text and offers the line that declares the new word. For a real sentence with several readings, as in the longer example, it keeps all readings and answers under each one.

4. **The planted mistake.** The planted mistake was counting a stay's days without its last day. Lean only checks that answers follow from the rules it is given. It does not check that the rules say what the policy says, so it accepts the wrong rules. Two other checks catch it. One is a separate AI reader that compares the translation with the policy. It flagged the 183-day part, along with three other flags that also appear on the unmodified translation. The other is a set of answers written in advance from the policy alone by an AI from a different model family. The planted copy answered "yes" twice where those answers said "no".

5. **Two things VE cannot do yet.** It cannot multiply amounts or take percentages. On long real texts it cannot answer questions in your own words, only the ones written with each case. It also handles "must/may" only partly.
