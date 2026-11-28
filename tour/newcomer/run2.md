# Stand-in newcomer, run 2

A stand-in, not a person: a fresh claude-sonnet-5-5 session that knew nothing of the project (see README.md in this folder for how it was run and what was removed from the record). It made 5 tool calls in 114 seconds. Every call and its output follow in order, then its report.

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
Resolved 59 packages in 8ms
Checked 58 packages in 1ms
==> uv sync --locked: done in 0 s
==> lake build (Lean; the first build is the long one)
The first Lean build takes 20 to 40 minutes (a line every minute while it runs); a later run takes seconds.
Build completed successfully (1478 jobs).
==> lake build (Lean; the first build is the long one): done in 3 s
==> rust build
5aeecbc57d8c24a7d18e1bf2602c15258ddfebf65c3cfc66f53e6c73ed8da8f2  <newcomer>/verifiable-english/rust/target/release/ve: pinned in <newcomer>/verifiable-english/lean/checkers.lock
==> rust build: done in 1 s
==> all steps done in 5 s
Next (DEMO.md step 4): uv run python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json
If uv is not found in a new shell, run first: export PATH="$HOME/.local/bin:$PATH"
==> the after-release checkout (.tour-after-release/)
after-release checkout at a5dde317c4 (2026-11-26)
==> the after-release checkout (.tour-after-release/): done in 0 s
==> after-release builds
Build completed successfully (1480 jobs).
==> after-release builds: done in 2 s
==> uv sync --locked (after-release)
Resolved 59 packages in 13ms
Checked 58 packages in 1ms
==> uv sync --locked (after-release): done in 0 s
==> tour install: all done in 8 s
Next: sh tour/stops/01-yes.sh

real	0m7.904s
user	0m2.261s
sys	0m1.448s
```

## Call 3: Bash

```sh
for s in 01-yes 02-not-necessarily 03-every-or-some 04-date 05-sum; do echo "######## $s"; sh tour/stops/$s.sh 2>&1; echo "[script exit $?]"; done
```

Output:

```
######## 01-yes
$ uv run --frozen python -m ve ask tour/texts/club.ve.md "Is Ann eligible?"
You asked whether Ann is eligible.
Yes.
Sentence 1 says: "Every member who is active is eligible."
Sentence 3 says: "Ann is active."
[script exit 0]
######## 02-not-necessarily
$ uv run --frozen python -m ve ask tour/texts/club.ve.md "Is Bo eligible?"
You asked whether Bo is eligible.
Not necessarily.
Here is a situation the document allows where it fails: ann is a member; bo is a member; ann is active; ann is eligible; bo is junior; bo is supervised.
[script exit 0]
######## 03-every-or-some
$ uv run --frozen python -m ve ask tour/texts/club.ve.md "Is a member eligible?"
VE cannot tell whether "a" here means every or some. Ask one of these instead:
Is every member eligible?
Is some member eligible?
[exit code 2]
[script exit 0]
######## 04-date
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
######## 05-sum
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
for s in 06-checker 07-company-policy 08-outside-the-text 09-planted-mistake 10-not-yet 11-longer-example 12-write-your-own; do echo "######## $s"; sh tour/stops/$s.sh > /tmp/out-$s.txt 2>&1; echo "[script exit $?] lines: $(wc -l < /tmp/out-$s.txt)"; done; head -12 /tmp/out-06-checker.txt; grep -n "Lean check" /tmp/out-06-checker.txt; grep -n -i "error\|traceback" /tmp/out-*.txt | head
```

Output:

```
######## 06-checker
[script exit 0] lines: 374
######## 07-company-policy
[script exit 0] lines: 5
######## 08-outside-the-text
[script exit 0] lines: 3
######## 09-planted-mistake
[script exit 0] lines: 23
######## 10-not-yet
[script exit 0] lines: 8
######## 11-longer-example
[script exit 0] lines: 11
######## 12-write-your-own
[script exit 0] lines: 44
$ uv run --frozen python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json
Entitled: YES
Payment: £200.00
Taken back by HMRC: NO
Kept: £200.00

Winter Fuel Payment, winter 2026 to 2027: the answers for one applicant, with the clauses
and assumptions each answer rests on.

Question 1. Is the applicant entitled to a Winter Fuel Payment for winter 2026 to 2027?
Answer: YES

228:Lean check: this answer rests on 15 proof steps; 15 of 15 proof steps accepted by Lean; the answer was checked by Lean and accepted.
330:Lean check: this answer rests on 18 proof steps; 18 of 18 proof steps accepted by Lean; the answer was checked by Lean and accepted.
357:Lean check: this answer rests on 19 proof steps; 19 of 19 proof steps accepted by Lean; the answer was checked by Lean and accepted.
374:Lean check: this answer rests on 21 proof steps; 21 of 21 proof steps accepted by Lean; the answer was checked by Lean and accepted.
/tmp/out-10-not-yet.txt:6:  VE refuses to read it (SyntaxError): it has no reading of this sentence.
/tmp/out-10-not-yet.txt:8:  VE refuses to read it (SyntaxError): it has no reading of this sentence.
```

## Call 5: Bash

```sh
cd /tmp && for s in 07-company-policy 08-outside-the-text 09-planted-mistake 10-not-yet 11-longer-example 12-write-your-own; do echo "######## $s"; cat out-$s.txt; done
```

Output:

```
######## 07-company-policy
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python -m ve ask usecases/gitlab_relocation "Does Ivo meet the policy’s requirement to reside in their primary location in 2028?" --case R009
no
$ uv run --frozen python -m ve ask usecases/gitlab_relocation "May Ivo live and work outside their primary location for the stays described in 2028?" --case R009
no
######## 08-outside-the-text
$ uv run --frozen python -m ve ask tour/texts/club.ve.md "Is Ann retired?"
The question has no reading with the current vocabulary. Closest sentence tried: "Ann is retired.". Unknown English phrase 'is retired'. Nearest declared wordings: 'is active'; 'member'; 'is junior'.
[exit code 2]
######## 09-planted-mistake
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
######## 10-not-yet
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python ../tour/stops/not_yet.py
The rule: The late fee equals the daily fee plus the daily fee.
  VE reads it (one reading).
The rule: The late fee equals the daily fee times the number of days late.
  VE refuses to read it (SyntaxError): it has no reading of this sentence.
The rule: The late fee equals 10 percent of the price of the book.
  VE refuses to read it (SyntaxError): it has no reading of this sentence.
######## 11-longer-example
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
######## 12-write-your-own
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
Shell cwd was reset to <newcomer>
```

## Report (the session's final reply)

Quick status: I ran the install and all twelve stops, and I'm now writing the report. Here it is.

## A. Where I stumbled

- **Introduction, before stop 1.** The page spends many paragraphs on trust before showing anything. It says "VE's checker… written in Lean", then "not Lean's small proof kernel", then "Lean checked". I couldn't tell whether "Lean" meant the language, VE's own program, or the kernel. The four meanings of "Lean checked" are also listed before I'd seen any example. I only got a feel for it around stop 6.
- **Introduction.** The page links to `../docs/ARCHITECTURE.md`, which I was told not to open. It also says "47,690 lines", which means nothing to a newcomer.
- **Introduction.** The page says "ten stops", then an "optional longer example (file 11)", then "Stop 12". The ran-order is 1–10, 11, 12, so the numbering is odd.
- **Install.** The page says 17 seconds. Mine took about 8 s, which is fine given the prior install. The script ended with "Next (DEMO.md step 4): …", which points to a file I wasn't meant to read.
- **Stop 3.** The page says "Try them" for the two suggested questions. I didn't, because I was limited to the page's commands. Their answers (yes, and not necessarily) are only described, not shown.
- **Stop 5.** "VE reads the first sentence. It does not read the promise here" took me a couple of reads.
- **Stop 6.** The page shows only fragments of a 374-line output. I checked the first lines and the four "Lean check" lines against the page, and they matched. I did not compare the middle by eye. "Pensionable age" and "State Pension age" appear to be the same thing but are never said to be.
- **Stop 7.** "encoder", "runner" and "`--case R009`" are not explained. The bare answer "no" gives no reasons, which is a big drop from stops 1–2.
- **Stop 9.**
  - "part 6", "U6", "sg_s", "sn", "R1", "R3's '-1'" and "resok/outok/workok" are unexplained jargon.
  - "It flags part 6… It raised 3 other flags: part 6 (low)…" lists part 6 twice.
  - "It raised 3 of them (same part, kind and confidence) on the translation as written too" is hard to parse.
  - The page calls these "two separate checks", yet the first check's reader is from the same AI family as the translators.
- **Stop 12.** "oewn-2025" is not explained. "Sentence 4 (line 5)" confused me until the page explained the numbering below it. "ONE meaning throughout" is a warning I only half understood.

I saw no output differences from the page. Stops 3, 8 and 12 print `[exit code 2]` as the page says, and the scripts themselves exit 0.

## B. Errors

None. Every command finished and its output matched the page. The only error-like text was the intended "SyntaxError" wording in stop 10 and the expected `[exit code 2]` lines.

## C. Answers

1. **A "Yes" answer.** VE names the sentences the answer rests on, and only those. In stop 1 that's sentences 1 and 3, not 2 or 4. The proof behind it is replayed by VE's checker, a program written in Lean. There is no separate "checked" line, because a "Yes" is only printed after the checker has accepted the proof.

2. **"Not necessarily" versus "No".**
   - "Not necessarily" means the text doesn't settle the question, and nothing rules the answer out. VE backs it with a concrete counter-example: a situation where every sentence holds but the answer fails. In stop 2, Bo is junior and supervised but not active, so not eligible. Anything not listed in that situation is false there.
   - "No" is for when the text rules the answer out. Stop 12 shows "No. The document rules this out", and it names the sentences.

3. **Undefined words and ambiguity.**
   - For a question with undefined words (stop 8), VE refuses. It says there is no reading, names the unknown phrase and suggests nearest known wordings. A suggested wording is a different question.
   - For a text with an undefined word (stop 12), VE refuses the whole text and offers a `Words:` line that would fix it.
   - For a question with two readings (stop 3), VE won't pick one. It offers one question per reading.
   - For a text sentence with several readings (the longer example), VE keeps all of them and answers under each reading separately.

4. **The planted mistake.** Lean checks that answers follow from the rules it is given, not that the rules say what the policy says. The planted rules were valid, so Lean would accept them and give the wrong answer. Two other checks catch it. One is an AI reader that compares the translation with the policy part by part. The other is answers written in advance from the policy alone, by an AI of a different family. The planted copy said "yes" where those answers said "no". The reader also raised the same three other flags on the unmodified translation, so a person still has to read its flags.

5. **Two things VE cannot do yet.**
   - It can't multiply amounts or take percentages. Stop 10 refuses both.
   - On long real texts it can't answer your own question in your own words. It only answers the questions written with each case, word for word (stop 7).

   Other limits the page names are that "may" and "must" are handled only in part, and that no person has signed off any translation.
