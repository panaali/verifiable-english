# A tour of Verifiable English

Verifiable English (VE) reads rules written in English and answers questions about them. Each answer comes with
the sentences it rests on. A program called Lean checks the reasoning step by step. Lean is a proof checker: a small,
well-tested program that accepts a step only if it follows exactly from what came before. When VE cannot answer, it
says so and says why. It does not guess.

This page has ten stops. Each stop is one thing VE can do (the last one is what it cannot do yet). Every stop has the
same four parts:

1. **The text**: the rules, in plain English.
2. **Run it**: one command.
3. **What you should see**: copied from a real run.
4. **What just happened**: a few plain sentences.

Reading the page takes about 15 minutes. Running every stop takes about a minute, once the install has finished.
The first install takes about an hour (measured times are at the end of this page).

## Before you start: install (once)

You need a Linux machine (Ubuntu 24.04 was used) with about 15 GB of free disk space and `git`. The install script
adds anything else that is missing. That means Python's package tool `uv`, Lean and Rust. When it needs system
packages it runs `sudo apt-get`. From a fresh copy of the project, run:

```sh
git clone --branch tour-1126 https://github.com/panaali/verifiable-english.git verifiable-english
cd verifiable-english
sh tour/install.sh
```

The install builds Lean's checker. **The first build takes 20 to 40 minutes and prints nothing while it runs.**
Measured times from a clean copy are at the end of this page.

**Two branches.** Stops 1, 2, 3, 6 and 8 run on the project's main branch. Stops 4, 5, 7, 9 and 10 use features that
are still on a branch called `after-release`. They will run from there until those features reach main. The install
makes a second copy of the project for that branch, in the folder `.tour-after-release/`. Those stops move into it
by themselves and say so in their first line of output.

> Draft note (Nov 26): the branches `tour-1126` and `after-release` are not yet on GitHub. Until they are, clone the
> project's own copy instead of the URL above.

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
needed, so VE does not list them.

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

## Stop 3: a sentence that can be read in more than one way

**The text.** Part of the Universal Declaration of Human Rights, articles 23 to 26
(`usecases/question-answering/udhr-part07.ve.md`). Its sentence 1 is article 23(4):

> Everyone has the right to form and to join trade unions for the protection of his interests.

**Run it.**

```sh
sh tour/stops/03-two-readings.sh
```

**What you should see.**

<!-- output 03-two-readings -->
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
the text leaves the question open. Each such situation also says how it reads sentence 10 ("Everyone has the right
to education"), which has readings of its own; that choice does not change this answer. The note "(VE has not checked this wording)" means that the English shown for
that reading was written by the translation and was not read back by VE. The last line says that 9 of the 19
sentences could not be put into VE's form, so the answer does not use them.

## Stop 4: a date question

**The text.** A library's loan rule (written for this tour):

> If the return date is after the last day of the period of 21 days beginning with the borrowing date, then the
> person is late.

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
The rule: If the return date is after the last day of the period of 21 days beginning with the borrowing date, then the person is late.
Borrowed on Tuesday 3 November 2026.
Lean works out the last day of the loan: Monday 23 November 2026.
Ann returned the book on Tuesday 24 November 2026. Is Ann late? Yes: Lean checked it.
Bo returned the book on Monday 23 November 2026. Is Bo late? Not shown: no proof that Lean accepts.
```
<!-- /output -->

**What just happened.** VE turned the date words of the rule ("the last day of the period of 21 days beginning
with ...") into date arithmetic. Lean itself worked out that the last day is 23 November, not a Python script.
VE then asked Lean to check "Ann is late", and Lean accepted the proof. For Bo, who returned the book on the last
day, there is no such proof, so VE does not say Bo is late. This stop runs from branch `after-release` until date
arithmetic reaches main.

## Stop 5: a sum of amounts

**The text.** A travel policy's refund rule (written for this tour), and one trip's three receipts:

> The refund equals the sum, over each receipt that is approved, of the amount of the receipt.

**Run it.**

```sh
sh tour/stops/05-sum.sh
```

**What you should see.**

<!-- output 05-sum -->
```text
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python ../tour/stops/sums.py
The rule: The refund equals the sum, over each receipt that is approved, of the amount of the receipt.
The trip's receipts:
  r1: train ticket, £84.50, approved
  r2: hotel night, £212.00, approved
  r3: hotel minibar, £18.75, not approved
VE's reading of the rule for this trip:
  The receipts of this case are exactly r1, r2 and r3.
  If "r1" is approved, then the amount counted for the receipt (r1) equals the amount of the receipt (r1).
  If it is not the case that "r1" is approved, then the amount counted for the receipt (r1) equals GBP 0.00.
  If "r2" is approved, then the amount counted for the receipt (r2) equals the amount of the receipt (r2).
  If it is not the case that "r2" is approved, then the amount counted for the receipt (r2) equals GBP 0.00.
  If "r3" is approved, then the amount counted for the receipt (r3) equals the amount of the receipt (r3).
  If it is not the case that "r3" is approved, then the amount counted for the receipt (r3) equals GBP 0.00.
  The refund equals the sum of the amount counted for the receipt (r1), the amount counted for the receipt (r2) and the amount counted for the receipt (r3).
Is the refund £296.50? Yes: Lean checked the addition.
Is the refund £315.25? Not shown: no proof that Lean accepts.
```
<!-- /output -->

**What just happened.** VE turned the rule into one addition over exactly the receipts the trip lists. It printed
its own reading of that addition, line by line, so you can check that nothing was left out. An unapproved receipt
counts as £0.00. Lean checked that the refund is £296.50 (£84.50 + £212.00). The wrong total, with the minibar
included, cannot be proved. This stop runs from branch `after-release` until sums reach main.

## Stop 6: the eligibility checker, on one made-up person

**The text.** The Social Fund Winter Fuel Payment Regulations 2025, a real UK law. In short, a person gets a
payment for winter 2026 to 2027 if two things are true. First, they have reached State Pension age by the end of the
qualifying week (21 to 27 September 2026). Second, they live in England or Wales on at least one day of that week.
The payment is £200, or £300 in some cases involving people aged 80 or over. HMRC takes it back if the person's
income is over £35,000. The made-up person (`usecases/eligibility/demo/b15.json`) was born on 14 March 1955,
moved from Scotland to England on 22 September 2026, lives alone, gets only the State Pension, and has a total
income of £20,000.

**Run it.**

```sh
sh tour/stops/06-checker.sh
```

**What you should see.** The full output is long (it quotes every clause), so this page shows only parts of it:

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
or not) within a calendar year". The two made-up cases are both based in Toronto. Ana spends 181 days of 2027 in
Spain. Ivo spends 184 days of 2028 in Spain (1 January to 2 July, in a leap year).

**Run it.**

```sh
sh tour/stops/07-company-policy.sh
```

**What you should see.**

<!-- output 07-company-policy -->
```text
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python -m ve ask usecases/gitlab_relocation "Does Ana meet the policy’s requirement to reside in their primary location in 2027?" --case R001
yes
$ uv run --frozen python -m ve ask usecases/gitlab_relocation "Does Ivo meet the policy’s requirement to reside in their primary location in 2028?" --case R009
no
```
<!-- /output -->

**What just happened.** VE answered from its translation of the policy into rules. Ana is in Toronto for 184 days,
so yes. Ivo is in Toronto for 366 − 184 = 182 days, so no. Every step behind each answer was checked by Lean. On
these long real texts, VE answers only the questions written with each case, matched word for word. You cannot yet
ask your own question in your own words, as you could in stops 1 to 3. Unlike stop 6, this route prints only the
answer, not the clauses and assumptions. This stop runs from branch `after-release` until questions on policies reach
main.

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
outside them gets a refusal, not a guess. Exit code 2 means "the question was not read". The other stops that answer
end with exit code 0, which the stop scripts do not print.

## Stop 9: a planted mistake in a translation, caught by an independent check

**The text.** GitLab's relocation policy again (stop 7), and Ivo's case: 184 days in Spain in 2028, which leaves 182
days in Toronto.

**Run it.**

```sh
sh tour/stops/09-planted-mistake.sh
```

**What you should see.**

<!-- output 09-planted-mistake -->
```text
(this stop runs from branch after-release, in .tour-after-release/)
$ uv run --frozen python ../tour/stops/planted.py
The case: Ivo is a GitLab employee, not a GitLab Federal team member, whose primary, permanent and contractual location in Workday is Toronto, Canada. Ivo started at GitLab on 1 January 2025. The question date is 1 January 2028. The stay in Spain is from 1 January 2028 to 2 July 2028, inclusive, lasting 184 days. Every unstated day of each named calendar year is spent in the Workday location; working time is spread evenly over the days of that year. Arrival days count in the place of arrival. No country or state in this case has a threshold below 183 days.
The planted mistake: COUNT: the stay's days counted without the last day (no +1)

Question: Does Ivo meet the policy’s requirement to reside in their primary location in 2028?
  answer written from the policy alone, before the translation ran: no
  the translation as written: no (agrees)
  the translation with the planted mistake: yes (DISAGREES: the planted mistake is caught)

Question: May Ivo live and work outside their primary location for the stays described in 2028?
  answer written from the policy alone, before the translation ran: no
  the translation as written: no (agrees)
  the translation with the planted mistake: yes (DISAGREES: the planted mistake is caught)

Caught on 2 of 2 questions.
```
<!-- /output -->

**What just happened.** A real policy has to be translated into VE's rules, by a person or an AI, and a translation
can be wrong. Here we planted a typical mistake: counting a stay's days without its last day. That gives 183 days
in Spain and 183 in Toronto, which wrongly makes the answer "yes". Lean would not catch this, because Lean checks
that answers follow from the rules it is given, not that the rules say what the policy says. What catches it is a
separate check. Before the translation was ever run, a different writer read only the policy and wrote down the
answers. The run with the planted mistake disagrees with that writer, so the mistake shows up. The translation as
written agrees. (This stop runs the translation's rules without Lean, both times. It runs from branch `after-release`
until this policy reaches main.)

## Stop 10: what VE cannot do yet

**The text.** A library's late fee:

> The late fee equals the daily fee times the number of days late.

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
```
<!-- /output -->

**What just happened.** VE can add amounts (stop 5) but cannot multiply them yet, so it refuses the second rule
instead of guessing. Other things VE cannot do yet, in the same plain terms:

- **No multiplication.** A rate times a number of days, or a percentage of an amount, is refused.
- **No duties over time.** VE can say whether a text makes someone eligible, or whether a rule says someone must or
  may do something. It cannot yet follow a duty through time: was it done by the deadline, and what follows if it was
  not? On real policies, many questions of that kind are refused.
- **Translations are only as good as their check.** For a real law or policy, Lean checks the reasoning from the
  translated rules, not the translation itself (stop 9). How far to trust an answer depends on how well its
  translation was checked against the source.
- **Narrow English.** Questions in your own words work only on short texts written in VE's English (stops 1 to 3 and
  8). On long real texts, VE answers only the questions written with each case (stop 7).

---

## How long it takes (MEASURED)

<!-- timings -->
Measured on 2026-11-26, 08:34 to 09:44 UTC, by `sh tour/measure.sh` from a clean copy of commit 4454de2d3f
(after-release at a5dde317c4). The machine was a 32-core Linux cloud machine shared with other work (load average 45
to 73 during the run). The run used a fresh home directory, so uv, Lean and Rust were downloaded as on a new machine;
git and a C compiler were already installed.

| step | time |
|---|---|
| clone | 6 s |
| install (`sh tour/install.sh`) | 69 min 18 s (4158 s) |
| of which: the main Lean build | 39 min 55 s (2395 s) |
| of which: the after-release copy and its Lean build | 28 min 7 s (1687 s) |
| **time to first answer** (from the start of the clone to the end of stop 1) | **69 min 27 s (4167 s)** |
| all ten stops | 41 s |
| **total** | **70 min 5 s (4205 s)** |

Every stop's output in that run was identical to the output shown on this page. On a quieter machine the Lean
builds should be faster. Stops 1, 2, 3, 6 and 8 need only the main build: you can run them as soon as the install
prints "all steps done", about 41 minutes into this run.
<!-- /timings -->

## Where the pieces are

- `tour/stops/`: one script per stop. The `.py` files are the small programs behind stops 4, 5, 9 and 10.
- `tour/expected/`: the full output of every stop, written by `tour/make_expected.py` from a real run.
  `tests/test_tour.py` fails if any stop's output, or this page, drifts from them.
- `tour/texts/`: the club rules (stop 1), written by `tour/texts/build_texts.py`.
- `tour/TEXTS.md`: every text the tour uses and where it comes from.
