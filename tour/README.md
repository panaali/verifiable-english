# A tour of Verifiable English

Verifiable English (VE) reads rules written in English and answers questions about them. A program called Lean
checks the reasoning step by step. Lean is a proof checker: a small, well-tested program that accepts a step only if
it follows exactly from what came before. When VE cannot answer, it says so and says why. It does not guess. When
VE's `ask` command answers a question about a short text (stops 1 and 2), it names the sentences the answer rests on,
and Lean has already accepted the proof behind the answer; there is no separate "checked" line. The other stops say
what Lean checked.

Short texts can be written directly in VE's English, so VE reads the sentences themselves (stops 1, 2, 3 and 8). A
real law or policy is first translated, by a person or an AI, into rules VE can read: that is "the translation" on
this page (stops 6, 7 and 9, and the longer example at the end). Stops 4, 5, 9 and 10 run small Python programs (in
`tour/stops/`) that call VE directly, because those features have no command of their own yet.

This page has ten stops and an optional longer example at the end. Each stop is one thing VE can do (stop 10 is what
it cannot do yet). Stop 9 shows how a translation is checked against its source by an independent reader, an AI model
that compares the two. Every stop has the same four parts:

1. **The text**: the rules, in plain English.
2. **Run it**: one command.
3. **What you should see**: copied from a real run.
4. **What just happened**: a few plain sentences.

Reading the page takes about 15 minutes. Running every stop takes about a minute, once the install has finished.

## Before you start: install (once)

You need a Linux machine (x86-64; Ubuntu 24.04 was used) with about 6 GB of free disk space, `git` and `curl`. The
install script adds Python's package tool `uv` if it is missing, then fetches VE's two checker programs already built
(Lean's checker and a Rust one), so nothing has to be compiled: it took 17 seconds in our measurement (end of this
page). It never runs `sudo`: if `git` or `curl` is missing, it stops and prints the `apt-get` command to run. From a
fresh copy of the project, run:

```sh
git clone https://github.com/panaali/verifiable-english.git verifiable-english
cd verifiable-english
sh tour/install.sh
```

The install checks the downloaded programs against the checksums recorded in `tour/prebuilt.json` before it uses
them. **The second option** builds the checker programs from source instead (about an hour; it also installs Lean and
Rust, and needs a C compiler); it prints a progress line every minute while it builds:

```sh
sh tour/install.sh --from-source
```

The fast install uses the prebuilt programs only when your copy's Lean and Rust sources are the ones they were built
from; otherwise it says so and builds from source. Measured times for both options are at the end of this page.

> Measured locally (26 November 2026): the archive's download address (printed by `uv run python tour/prebuilt.py
> url`) goes live when the project publishes it. Until then, if you were given a copy of the archive, run the install
> as `VE_TOUR_PREBUILT=/path/to/ve-tour-prebuilt-linux-x86_64.tar.gz sh tour/install.sh` (the same checksum check).

**Two branches.** Stops 1, 2, 3, 6 and 8 run on the project's main branch. Stops 4, 5, 7, 9 and 10 use features that
are still on a branch called `after-release`. They will run from there until those features reach main. The install
makes a second copy of the project for that branch, at a fixed commit (`tour/AFTER_RELEASE_COMMIT`), in the folder
`.tour-after-release/`. Those stops move into it by themselves and say so in their first line of output.

Every command below is run from the `verifiable-english` folder. If the shell says `uv: command not found`, run
`export PATH="$HOME/.local/bin:$PATH"` first.

---

## Stop 1: ask a yes/no question and get the sentences that prove it

**The text.** A club's voting rules (`tour/texts/club.ve.md`). "Eligible" means eligible to vote at the club's
meeting:

> Every member who is active is eligible.
> Every member who is junior is supervised.
> Ann is active.
> Bo is junior.

**Run it.**

```sh
sh tour/stops/01-yes.sh
```

**What you should see.** The first line is the command the stop runs. The rest is VE's answer.

<!-- output 01-yes -->
```text
$ uv run --frozen python -m ve ask tour/texts/club.ve.md "Is Ann eligible?"
You asked whether Ann is eligible.
Yes.
Sentence 1 says: "Every member who is active is eligible."
Sentence 3 says: "Ann is active."
```
<!-- /output -->

**What just happened.** VE read the question as the sentence "Ann is eligible" and found that it follows from the
rules. It names the two sentences the answer uses: sentence 3 says Ann is active, and sentence 1 says every active
member is eligible. Lean checked that these two sentences really do give the answer. Sentences 2 and 4 are not
needed, so VE does not list them. (Sentence 2, about junior members, matters in stop 2.)

## Stop 2: ask a question whose answer does not follow

**The text.** The same club rules as stop 1.

**Run it.**

```sh
sh tour/stops/02-not-necessarily.sh
```

**What you should see.**

<!-- output 02-not-necessarily -->
```text
$ uv run --frozen python -m ve ask tour/texts/club.ve.md "Is Bo eligible?"
You asked whether Bo is eligible.
Not necessarily.
Here is a situation the document allows where it fails: ann is a member; bo is a member; ann is active; ann is eligible; bo is junior; bo is supervised.
```
<!-- /output -->

**What just happened.** The rules say Bo is junior and therefore supervised. They never say Bo is active, so they do
not make Bo eligible. VE does not answer "no", because nothing rules it out either. It answers "not necessarily" and
proves it with a concrete counter-example. In this situation every rule holds, yet Bo is not eligible. (The situation
lists what is true in it, with names in lower case. Anything not listed is false there; for example, Bo is not
active.) Lean checked that this situation obeys every sentence of the text.

## Stop 3: a question that can be read in two ways

**The text.** The same club rules as stop 1. The question is "Is a member eligible?": does "a member" mean every
member, or some member?

**Run it.**

```sh
sh tour/stops/03-every-or-some.sh
```

**What you should see.**

<!-- output 03-every-or-some -->
```text
$ uv run --frozen python -m ve ask tour/texts/club.ve.md "Is a member eligible?"
VE cannot tell whether "a" here means every or some. Ask one of these instead:
Is every member eligible?
Is some member eligible?
[exit code 2]
```
<!-- /output -->

**What just happened.** The question has two readings, and they have different answers. VE does not pick one. It
says it cannot tell which one you mean and gives you the two questions to ask instead, one per reading. (Try them:
"Is some member eligible?" gets a yes, because Ann is; "Is every member eligible?" gets "not necessarily", because of
Bo.) The last line, `[exit code 2]`, is printed by the stop script: it is the exit code of VE's command, and 2 means
"the question was not read". The stop script itself goes on and ends normally. The scripts print a VE command's exit
code only when it is not 0. An optional longer example at the end of this page shows a sentence of a real text with
three readings, where VE answers under each one.

## Stop 4: a date question

**The text.** A library's two loan rules (written for this tour):

> If the return date is after the last day of the period of 21 days beginning with the borrowing date, then the
> person is late.
>
> If the return date is on or before the last day of the period of 21 days beginning with the borrowing date, then
> the person is on time.

A book is borrowed on Tuesday 3 November 2026. Ann returns it on 24 November and Bo returns it on 23 November.

**Run it.**

```sh
sh tour/stops/04-date.sh
```

**What you should see.**

<!-- output 04-date -->
```text
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python ../tour/stops/dates.py
Rule 1: If the return date is after the last day of the period of 21 days beginning with the borrowing date, then the person is late.
Rule 2: If the return date is on or before the last day of the period of 21 days beginning with the borrowing date, then the person is on time.
Borrowed on Tuesday 3 November 2026.
Lean works out the last day of the loan: Monday 23 November 2026.
Ann returned it on Tuesday 24 November 2026. Is Ann late? Yes: Lean checked it.
Bo returned it on Monday 23 November 2026. Is Bo on time? Yes: Lean checked it.
Ann returned it on Tuesday 24 November 2026. Is Ann on time? VE has no proof that Lean accepts, so it does not say Ann is on time.
```
<!-- /output -->

**What just happened.** VE turned the date words of the rules ("the last day of the period of 21 days beginning
with ...") into date arithmetic: the borrowing date plus 20 days. That reading of the words is made by VE's own
Python code, which is tested but not checked by Lean; Lean then did the arithmetic itself and worked out that the
last day is 23 November. VE asked Lean to check "Ann is late" (rule 1) and "Bo is on time" (rule 2), and Lean accepted
both proofs. The last line shows what VE does when no rule covers a question: no rule says a late person is not on
time, so VE has no proof that Ann is on time, and it does not say so. It does not say "Ann is not on time" either. It
only says what a rule gives. This stop runs from branch `after-release` until date arithmetic reaches main.

## Stop 5: a sum of amounts

**The text.** A pizza shop's bill rule and its delivery promise (written for this tour), and one order of three
pizzas:

> The bill equals the sum, over each pizza that is charged, of the price of the pizza.
>
> A pizza is free if it arrives more than 30 minutes after the order.

VE reads the first sentence. It does not read the promise here: the order itself says which pizzas are charged (the
four cheese came after 41 minutes, so it is free). The stop asks whether the bill is £20.50 (the two charged pizzas)
or £31.00 (all three).

**Run it.**

```sh
sh tour/stops/05-sum.sh
```

**What you should see.**

<!-- output 05-sum -->
```text
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
```
<!-- /output -->

**What just happened.** VE turned the rule into one addition over exactly the pizzas the order lists. It printed its
own reading of that addition, line by line, so you can check that nothing was left out. A pizza that is not charged
counts as £0.00. Lean checked that the bill is £20.50 (£9.50 + £11.00). The wrong total, with the free pizza included,
cannot be proved. This stop runs from branch `after-release` until sums reach main.

## Stop 6: the eligibility checker, on one made-up person

**The text.** The Social Fund Winter Fuel Payment Regulations 2025, a real UK law. In short, a person gets a
payment for winter 2026 to 2027 if two things are true. First, they have reached State Pension age by the end of the
qualifying week (21 to 27 September 2026). Second, they live in England or Wales on at least one day of that week.
Some people are excluded (for example, people in prison for the whole week). The payment is usually £200, from £100
to £300 depending on age, benefits and household. HMRC takes it back if the person's income is over £35,000. The
made-up person (`usecases/eligibility/demo/b15.json`) was born on 14 March 1955, moved from Scotland to England on 22
September 2026, lives alone, gets only the State Pension, and has a total income of £20,000.

**Run it.**

```sh
sh tour/stops/06-checker.sh
```

**What you should see.** The full output is long (374 lines: it quotes every clause), so this page shows its start,
the start of the assumptions, and the last line of each of the four answers:

<!-- output 06-checker -->
```text
$ uv run --frozen python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json
Entitled: YES
Payment: £200.00
Taken back by HMRC: NO
Kept: £200.00

Winter Fuel Payment, winter 2026 to 2027: the answers for one applicant, with the clauses
and assumptions each answer rests on.

Question 1. Is the applicant entitled to a Winter Fuel Payment for winter 2026 to 2027?
Answer: YES

Clauses used:
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 2(a)
    Source text:
      “2. Subject to regulation 4, the Secretary of State must pay a winter fuel payment out of the
        social fund to a person (“P”) where—”
      “(a)in or before the qualifying week, P has reached pensionable age, and”
    Read as:
      - The applicant has reached pensionable age in or before the week exactly when the applicant's
          pensionable-age date is no later than 2026-09-27.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 2(b)
    Source text:
      “2. Subject to regulation 4, the Secretary of State must pay a winter fuel payment out of the
        social fund to a person (“P”) where—”
      “(b)in respect of any day falling within the qualifying week, P is ordinarily resident in
        England or Wales.”
    Read as:
      - The applicant is ordinarily resident in England or Wales on a day of the week exactly when
...
Assumptions (taken as given, not checked):
  - The qualifying week, 21 to 27 September 2026, is worked out in Python from the rule “the week
      beginning on the third Monday in September” (2026 being the year of the payment); the checker
      checks only that its last day is 6 days after its first.
...
Lean check: this answer rests on 15 proof steps; 15 of 15 proof steps accepted by Lean; the answer was checked by Lean and accepted.
...
Lean check: this answer rests on 18 proof steps; 18 of 18 proof steps accepted by Lean; the answer was checked by Lean and accepted.
...
Lean check: this answer rests on 19 proof steps; 19 of 19 proof steps accepted by Lean; the answer was checked by Lean and accepted.
...
Lean check: this answer rests on 21 proof steps; 21 of 21 proof steps accepted by Lean; the answer was checked by Lean and accepted.
... (374 lines in all: tour/expected/06-checker.txt)
```
<!-- /output -->

**What just happened.** The checker answered four questions: entitled, how much, taken back, and how much is kept.
For each answer it quotes the clauses of the law it used. Each quote shows the law's own words, then how the checker
read them. It lists the assumptions it took as given. For example, some dates are worked out in Python and not by
Lean, and legal facts such as where someone "ordinarily resides" are taken from the profile. At the end of each
answer it reports how many proof steps Lean checked and accepted.

## Stop 7: the same kind of question, on a real company policy

**The text.** GitLab's staff handbook page on where staff may live and work (a real company policy, CC BY-SA 4.0).
The rule asked about here says that staff "must reside in their primary location for at least 183 days (consecutive
or not) within a calendar year", and may be away from it "for a maximum total of 183 days". The made-up case: Ivo is
based in Toronto and spends 184 days of 2028 in Spain (1 January to 2 July, in a leap year).

**Run it.**

```sh
sh tour/stops/07-company-policy.sh
```

**What you should see.**

<!-- output 07-company-policy -->
```text
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python -m ve ask usecases/gitlab_relocation "Does Ivo meet the policy’s requirement to reside in their primary location in 2028?" --case R009
no
$ uv run --frozen python -m ve ask usecases/gitlab_relocation "May Ivo live and work outside their primary location for the stays described in 2028?" --case R009
no
```
<!-- /output -->

**What just happened.** VE answered from its translation of the policy into rules. Ivo is in Toronto for
366 − 184 = 182 days, fewer than 183, so both answers are no. Every step behind each answer was checked by Lean; when
a step fails, VE prints no answer. This route cannot yet print the sentences an answer rests on, only the answer
(stop 6's checker does print its clauses), so the case was chosen for its one-line explanation. `--case R009` names
the made-up case. On these long real texts, VE answers only the questions written with each case, and the question
must match the written one word for word. You cannot yet ask your own question in your own words, as you could in
stops 1 to 3. This stop runs from branch `after-release` until questions on policies reach main.

## Stop 8: a question the text does not cover

**The text.** The club rules of stop 1. They say nothing about retirement.

**Run it.**

```sh
sh tour/stops/08-outside-the-text.sh
```

**What you should see.**

<!-- output 08-outside-the-text -->
```text
$ uv run --frozen python -m ve ask tour/texts/club.ve.md "Is Ann retired?"
The question has no reading with the current vocabulary. Closest sentence tried: "Ann is retired.". Unknown English phrase 'is retired'. Nearest declared wordings: 'is active'; 'member'; 'is junior'.
[exit code 2]
```
<!-- /output -->

**What just happened.** VE refused the question and said why: "is retired" is not a word the text knows. It also
suggested the nearest words the text does know. VE answers only in the words a text defines. A question that steps
outside them gets a refusal, not a guess. As in stop 3, exit code 2 means "the question was not read".

## Stop 9: a planted mistake in a translation, caught by an independent check

**The text.** GitLab's relocation policy again (stop 7), and Ivo's case. We planted one typical mistake in a copy of
the translation: a stay's days are counted without its last day. Ivo's stay in Spain then counts as 183 days instead
of 184.

**Run it.**

```sh
sh tour/stops/09-planted-mistake.sh
```

**What you should see.**

<!-- output 09-planted-mistake -->
```text
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python ../tour/stops/planted.py
The planted mistake: a stay's days are counted without its last day, so Ivo's 184 days in Spain count as 183.
The reader read exactly this planted file: yes (same SHA-256)

1. The independent reader's check (recorded 2026-11-26; running it again needs an AI model account).
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
  It raised 3 other flags, on parts the planted mistake does not touch (it raised them on the translation as written too).

2. The answers, compared with answers written from the policy alone before the translation ran:
  Does Ivo meet the policy’s requirement to reside in their primary location in 2028?
    policy alone: no; translation as written: no; with the mistake: yes (caught)
  May Ivo live and work outside their primary location for the stays described in 2028?
    policy alone: no; translation as written: no; with the mistake: yes (caught)
```
<!-- /output -->

**What just happened.** A real policy has to be translated into VE's rules, by a person or an AI, and a translation
can be wrong. Lean would not catch this mistake: Lean checks that answers follow from the rules it is given, not that
the rules say what the policy says. Two separate checks catch it:

1. **An independent reader.** An AI model was given only the policy, a short brief and the files of the planted
   translation. It was not told that anything was planted, or where. It compared the translation with the policy,
   part by part, and flagged the 183-day part with high confidence, quoting the policy's words and the translation's
   rule side by side and saying which answers could come out wrong. Its other three flags are on parts the mistake
   does not touch; it raised those on the translation as written too, where they were judged separately
   (`tour/TEXTS.md`). The stop shows
   this reader's recorded output (running the reader again needs an AI model account) and checks that the planted
   file it makes now is exactly the file the reader read.
2. **Answers written in advance.** Before the translation was ever run, a different writer read only the policy and
   wrote down the answers to the case's questions. The translation as written agrees with them; the planted copy
   answers "yes" twice, so the mistake shows up. Here the answers are worked out from the rules without asking Lean
   to check them: Lean would accept the planted rules anyway, so it is not the safeguard against this kind of
   mistake.

The `’` in the questions is the policy's own apostrophe. This stop runs from branch `after-release` until this
policy reaches main.

## Stop 10: what VE cannot do yet

**The text.** Three ways a library might write its late fee. The first adds, the second multiplies, the third takes
a percentage:

> The late fee equals the daily fee plus the daily fee.
>
> The late fee equals the daily fee times the number of days late.
>
> The late fee equals 10 percent of the price of the book.

**Run it.**

```sh
sh tour/stops/10-not-yet.sh
```

**What you should see.**

<!-- output 10-not-yet -->
```text
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python ../tour/stops/not_yet.py
The rule: The late fee equals the daily fee plus the daily fee.
  VE reads it (one reading).
The rule: The late fee equals the daily fee times the number of days late.
  VE refuses to read it (SyntaxError): it has no reading of this sentence.
The rule: The late fee equals 10 percent of the price of the book.
  VE refuses to read it (SyntaxError): it has no reading of this sentence.
```
<!-- /output -->

**What just happened.** VE can add amounts (stop 5) but cannot multiply them or take a percentage yet, so it refuses
the second and third rules instead of guessing. "SyntaxError" is VE's name for "this sentence has no reading in VE's
English"; nothing crashed. What VE cannot do yet, each with the stop that shows it:

- **No multiplication, no percentages.** A rate times a number of days, or a percentage of an amount, is refused
  (this stop).
- **Must and may, only in part.** The one checked answer to a "May ...?" question on this page is in stop 7 ("May Ivo
  live and work outside ...?"), on branch `after-release`, for a question written with the case. On main, the one
  "May ...?" answer on this page (the longer example) holds only under one of three readings, and VE says it has not
  checked that reading's wording.
- **Translations are only as good as their check.** For a real law or policy, Lean checks the reasoning from the
  translated rules, not the translation itself (stop 9). How far to trust an answer depends on how well its
  translation was checked against the source.
- **Narrow English.** Questions in your own words work only on short texts written in VE's English (stops 1 to 3
  and 8). On long real texts, VE answers only the questions written with each case (stop 7).

---

## A longer example (optional): one sentence, three readings

**The text.** Part of the Universal Declaration of Human Rights, articles 23 to 26
(`usecases/question-answering/udhr-part07.ve.md`), translated into VE's rules. Its sentence 1 is article 23(4) (the
output quotes it with the article's own paragraph number, "4."):

> Everyone has the right to form and to join trade unions for the protection of his interests.

**Run it.**

```sh
sh tour/stops/11-longer-example.sh
```

**What you should see.**

<!-- output 11-longer-example -->
```text
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
```
<!-- /output -->

**What just happened.** "Has the right to" can mean different things in law. VE kept three readings of sentence 1
instead of picking one, and it answers under each reading in turn:

- "Is classified as ..." is the cautious reading. It records that the right exists but draws nothing from it.
- "Must be left free to" means others must not stop you.
- "May" means you are permitted to.

Only under the third reading does the text say yes. Under the other two, VE shows a made-up person, `e0`, for whom
the text leaves the question open (the `"..."` names in those lines are the translation's own labels). Each such
situation also says how it reads sentence 10 ("Everyone has the right to education"), which has readings of its own;
that choice does not change this answer. Lean checked each reading's answer and each situation, as in stops 1 and 2.
The note "(VE has not checked this wording)" means that the English shown for that reading was written by the
translation and was not read back by VE. The last line says that 9 of the 19 sentences could not be put into VE's
form, so the answer does not use them. The question is worded the way the translation words sentence 1 under its
"may" reading ("form as well as join trade unions to protect their interests").

---

## How long it takes (MEASURED)

<!-- timings -->
Measured on 2026-11-26 by `sh tour/measure.sh` from a clean copy (commit 0d184debe9; after-release at a5dde317c4),
with a fresh home directory, so uv, Python and every Python package were downloaded as on a new machine (git and curl
were already installed). The machine was a 32-core Linux cloud machine with a fast network, shared with other work.

**The fast install (prebuilt programs), 12:59 UTC, load average 14:**

| step | time |
|---|---|
| clone (from a copy on the same machine) | 5 s |
| install (`sh tour/install.sh`) | 17 s |
| of which: uv, Python and the Python packages (both checkouts) | 6 s |
| of which: the prebuilt programs (132 MB archive: fetch, check, unpack) | 6 s |
| **time to first answer** (from the start of the clone to the end of stop 1) | **23 s** |
| all ten stops and the longer example | 26 s |
| **total** | **48 s** |

Every stop's output in that run was identical to the output shown on this page. What this run did not measure:
cloning from GitHub (the repository is about 2.3 GB) and downloading the archive from GitHub; those take longer on a
home connection. The archive was served from this machine (the same file, with the same checksum check), because
its download address goes live only when the project publishes it.

**Building from source** (`sh tour/install.sh --from-source`), same commit, 13:00 to 14:26 UTC, load average 50 to
97 (other work, including a large test run, shared the machine):

| step | time |
|---|---|
| clone (from a copy on the same machine) | 6 s |
| install (`sh tour/install.sh --from-source`) | 85 min 0 s (5100 s) |
| of which: the main Lean build | 48 min 4 s (2884 s) |
| of which: the after-release copy and its Lean build | 35 min 35 s (2135 s) |
| **time to first answer** | **85 min 9 s (5109 s)** |
| all ten stops and the longer example | 35 s |

Every stop's output in that run was identical to the output shown on this page too. An earlier run of the same
builds on a less loaded moment took 69 min to the first answer. During each build the install printed a progress
line every minute.
<!-- /timings -->

## Where the pieces are

- `tour/stops/`: one script per stop. The `.py` files are the small programs behind stops 4, 5, 9 and 10.
- `tour/expected/`: the full output of every stop, written by `tour/make_expected.py` from a real run.
  `tests/test_tour.py` fails if any stop's output, or this page, drifts from them.
- `tour/texts/`: the club rules (stops 1, 2, 3 and 8), written by `tour/texts/build_texts.py`.
- `tour/data/`: the answers written from the policy alone (stop 9) and the independent reader's recorded flags.
- `tour/install.sh`, `tour/prebuilt.py`, `tour/prebuilt.json`: the install, and the prebuilt checker programs it
  fetches and checks. `tour/measure.sh` times the install and every stop from a clean copy.
- `tour/TEXTS.md`: every text the tour uses, where it comes from, and how its translation was checked.
