# Demo: the Winter Fuel Payment checker on a clean machine

Release B, checklist item 5 (reviews: definition of done, part B). Follow these steps word for word on a fresh
Ubuntu 24.04 machine. The demo asks the checker about one applicant and prints the four answers, every clause of
the Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969) each answer uses (quoted, with its plain
reading), the assumptions it rests on in plain English, and how many proof steps Lean checked.

## 0. The machine

- Ubuntu 24.04 (x86_64), a user who can run `sudo`, and internet access (GitHub, astral.sh, rustup.rs).
- About 10 GB of free disk: the clone is about 2.3 GB, the Lean toolchain and build about 5 GB, Rust about 0.7 GB,
  the Python environment about 0.3 GB.
- Time: the first Lean build is the long step. On the project's 32-core build machine, busy with other jobs, it
  took 40 minutes (2026-11-22); `uv sync` and the Rust build took under a minute together there (the tools were
  already installed). The time on a clean machine is recorded by the clean run, not here.

## 1. Get git, if the machine has none

```sh
command -v git || (sudo apt-get update && sudo apt-get install -y git)
```

## 2. Clone the release

```sh
git clone --branch ve-elig-b1 https://github.com/panaali/verifiable-english.git ve && cd ve
```

## 3. Install

```sh
sh usecases/eligibility/demo/install.sh
```

It installs what is missing (a C toolchain, curl, uv, elan for Lean, rustup for Rust), then runs the three build
commands: `uv sync --locked`, `(cd lean && lake build)` and `uv run python tools/rust_build.py`. Each step prints
its time in seconds. Running it again is safe and quick.

## 4. Ask about one applicant

```sh
export PATH="$HOME/.local/bin:$PATH"
uv run python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json
```

The applicant (`usecases/eligibility/demo/b15.json`, case B15 of the eligibility review): born 14 March 1955, so
over pensionable age; ordinarily resident in Scotland from 20 September 2026, then in England from 22 September
2026, a day of the qualifying week; lives alone; State Pension only; total income £20,000.

It takes about ten seconds. The same applicant can be given with flags instead of a file:

```sh
uv run python usecases/eligibility/ask.py --birth 1955-03-14 --scot-ni-from 2026-09-20 --ew-from 2026-09-22
```

Other flags: `--ew-last-day`, `--benefit NAME` (repeat for each benefit), `--income 40000.00`, `--no-lean`.
A housemate or partner, a care stay, hospital or custody need a profile file: the fields are described in
`usecases/eligibility/cases.json` ("description"), and its 80 cases are examples.

## 5. Expected output

The command prints exactly the text below. The first four lines are the answers: entitled, £200, not taken back
by HMRC, £200 kept. Then, per question: the clauses used, among them regulation 2(a) (pensionable age),
2(b) (resident in England or Wales on a day of the week), 3(1) (the £200 amount) and 4(4) (the move to Scotland
or Northern Ireland, which does not apply here: the applicant moved to Scotland before living in England, not
after); for questions 3 and 4,
the GOV.UK guide's "If your income is over £35,000" section, shown as an assumption because its legal basis is not
pinned down; and each answer's Lean check.

<!-- expected-output: tests/test_relb_demo_cli.py compares this block with the command's output -->
```text
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
          that residence began no later than 2026-09-27 and either continues or has a last day no
          earlier than 2026-09-21.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 1(3), “relevant
    benefit”
    Source text:
      ““relevant benefit” means—”
      “(a)”
      “income support under Part 7 of the Social Security Contributions and Benefits Act 1992;”
      “(b)”
      “an income-based jobseeker’s allowance under the Jobseekers Act 1995(10);”
      “(c)”
      “state pension credit under the State Pension Credit Act 2002(11);”
      “(d)”
      “an income-related employment and support allowance under Part 1 of the Welfare Reform Act
        2007(12);”
      “(e)”
      “universal credit under Part 1 of the Welfare Reform Act 2012(13).”
    Read as:
      - A relevant benefit is paid to the applicant for the week exactly when income support,
          income-based jobseeker's allowance, state pension credit, income-related employment and
          support allowance or universal credit is paid to the applicant for the week.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 1(4)(a),
    “residential care”
    Source text:
      “(4) In these Regulations, a person—”
      “(a)is in residential care if, disregarding any period of temporary absence, they reside in—”
      “(i)a care home,”
      “(ii)an independent hospital, or”
      “(iii)accommodation provided under section 3(1) of the Polish Resettlement Act 1947(14),”
      “throughout the qualifying week and the period of at least 12 weeks ending immediately before
        the qualifying week;”
    Read as:
      - If the applicant is in a care setting, the elapsed duration from the applicant's care start
          date to 2026-09-21 equals the applicant's care days before the week.
      - The applicant is in residential care exactly when the applicant is in a care setting, the
          applicant's care days before the week are at least 84 days (12 weeks), and the applicant's
          care stay either has no end date or ends no earlier than 2026-09-27.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 1(4)(b), “lives
    with”
    Source text:
      “(4) In these Regulations, a person—”
      “(b)lives with a person if, disregarding any period of temporary absence, they share
        accommodation with one or more persons as their mutual home and they are not in residential
        care.”
    Read as:
      - The applicant lives with the housemate exactly when they share a mutual home and the
          applicant is not in residential care.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 4(2)(a)
    Source text:
      “(2) This paragraph applies where, throughout the qualifying week, P is—”
      “(a)a partner of and living with a person (“P’s partner”) who has reached pensionable age in
        or before the qualifying week and P’s partner is a person to whom a relevant benefit has
        been, or falls to be, paid in respect of the qualifying week,”
    Read as:
      - The applicant and the housemate share a mutual home throughout the week exactly when they
          share a mutual home, and the home either began before the week or has a start date no
          later than 2026-09-21, and either continues or has an end date no earlier than 2026-09-27.
      - The applicant is a partner of the housemate throughout the week exactly when the applicant
          is a partner of the housemate, and the partnership either began before the week or has a
          start date no later than 2026-09-21, and either continues or has an end date no earlier
          than 2026-09-27.
      - Regulation 4(2)(a) applies to the applicant exactly when, throughout the week, the applicant
          is a partner of the housemate and shares a mutual home with the housemate, the applicant
          lives with the housemate, and the housemate has reached pensionable age and is paid a
          relevant benefit for the week.
  The Social Security (Hospital In-Patients) Regulations 2005 (SI 2005/3360), regulation 2(5)
    Source text:
      “(5) For the purposes of paragraph (4), a period during which a person is regarded as
        receiving or having received free in-patient treatment shall be deemed to begin on the day
        after the day on which he enters a hospital or similar institution referred to in that
        paragraph and to end on the day on which he leaves such a hospital or similar institution.”
    Read as:
      - If the applicant is an in-patient, the applicant's treatment start date is 1 day after the
          applicant's hospital admission date.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 4(2)(b)
    Source text:
      “(2) This paragraph applies where, throughout the qualifying week, P is—”
      “(b)receiving free in-patient treatment and has been receiving free in-patient treatment for a
        period of more than 52 weeks ending immediately before the qualifying week, or”
    Read as:
      - If the applicant is an in-patient, the elapsed duration from the applicant's treatment start
          date to 2026-09-21 equals the applicant's treatment days before the week.
      - Regulation 4(2)(b) applies to the applicant exactly when the applicant is an in-patient
          whose treatment began no later than 2026-09-21, whose discharge is no earlier than
          2026-09-27, and whose treatment days before the week are more than 364 days (52 weeks).
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 4(2)(c)
    Source text:
      “(2) This paragraph applies where, throughout the qualifying week, P is—”
      “(c)detained in custody under a sentence imposed by a court.”
    Read as:
      - Regulation 4(2)(c) applies to the applicant exactly when the applicant is detained in
          custody under a sentence, the custody began before 2026-09-21, and the release is after
          2026-09-27.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 4(3)
    Source text:
      “(3) This paragraph applies where P is in residential care and a relevant benefit has been, or
        falls to be, paid to P in respect of the qualifying week.”
    Read as:
      - Regulation 4(3) applies to the applicant exactly when the applicant is in residential care
          and is paid a relevant benefit for the week.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 4(4)
    Source text:
      “(4) This paragraph applies where, having been ordinarily resident in England or Wales on any
        day falling within the qualifying week, P becomes ordinarily resident in Scotland or
        Northern Ireland on or before the last day of that week.”
    Read as:
      - Regulation 4(4) applies to the applicant exactly when the applicant is resident in England
          or Wales on a day of the week and, no earlier than the applicant's first day of that
          residence and no earlier than 2026-09-21, became ordinarily resident in Scotland or
          Northern Ireland no later than 2026-09-27.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulations 4(5) and (6) and
    5(1)
    Source text:
      “(5) Subject to paragraph (6), this paragraph applies where P has not made a claim for a
        winter fuel payment on or before the 31st March following the qualifying week.”
      “(6) Paragraph (5) does not apply where—”
      “(a)a winter fuel payment has been made by virtue of regulation 5(1) in respect of the
        qualifying week, or”
      “(b)regulation 5(2) applies.”
      “5.—(1) The Secretary of State may, on or before the 31st March following the qualifying week,
        pay to P a winter fuel payment if (disregarding regulation 4(5)) P appears to the Secretary
        of State to be entitled to a winter fuel payment under regulation 2.”
    Read as:
      - Regulation 4(5) applies to the applicant exactly when the applicant is not paid without a
          claim and made no claim on or before 2027-03-31.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 4(1)
    Source text:
      “4.—(1) Regulation 2 does not apply to P if any of the circumstances in paragraphs (2) to (5)
        applies.”
    Read as:
      - The applicant is excluded exactly when one of regulations 4(2)(a), 4(2)(b), 4(2)(c), 4(3),
          4(4) and 4(5) applies to the applicant.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 2, read with
    regulation 4(1)
    Source text:
      “2. Subject to regulation 4, the Secretary of State must pay a winter fuel payment out of the
        social fund to a person (“P”) where—”
      “4.—(1) Regulation 2 does not apply to P if any of the circumstances in paragraphs (2) to (5)
        applies.”
    Read as:
      - The applicant is entitled exactly when the applicant has reached pensionable age, is
          resident in England or Wales on a day of the week, and is not excluded.

Assumptions (taken as given, not checked):
  - The qualifying week is taken as 21 to 27 September 2026. The rule “the week beginning on the
      third Monday in September” is not worked out; only the 6-day span of the week is checked.
  - Each person's pensionable-age date and 80th birthday are worked out by hand from the birth date
      (Pensions Act 1995, Schedule 4, paragraph 1, plus 80 years) and given as dates; the age
      arithmetic itself is not checked. The hand working takes a person to reach an age at the start
      of the birthday, and a birth date of 29 February 1960 as giving pensionable age no later than
      1 March 2026. Dates used here: the applicant's pensionable-age date is 2021-03-14.
  - These legal statuses are taken as stated in the profile, not decided from other circumstances:
      ordinarily resident in England or Wales, and from when; ordinarily resident in Scotland or
      Northern Ireland, and from when; a partner (a member of a couple); sharing a mutual home;
      living in a care home or independent hospital; receiving free in-patient treatment; detained
      in custody; who a benefit is paid to for the qualifying week; paid without a claim; the date
      of a claim.
  - At most one other person shares the home; “a person” in regulations 3 and 4(2)(a) is read as
      that one person.
  - The Scotland and Northern Ireland schemes are not modelled; a person not ordinarily resident in
      England or Wales on any day of the qualifying week gets no payment under these Regulations.
  - The rules have no checked English wording; each is shown above as a plain gloss next to its
      source text, and the gloss is taken to state the rule.
  - “52 weeks” and “12 weeks” are taken as 364 and 84 days.
  - In “lives with”, the words “they are not in residential care” apply only to the person who lives
      with someone; the other person may be in residential care.
  - Residential care needs the stay to begin no later than 29 June 2026, and a stay with a last day
      counts only if that day is no earlier than 27 September 2026.
  - For hospital, “throughout the week” means admitted no later than 20 September 2026 and leaving
      no earlier than 27 September 2026, and “more than 52 weeks” means admitted no later than 20
      September 2025, because a treatment period begins the day after admission.
  - Custody is “throughout the qualifying week” only if it began before 21 September and release is
      after 27 September; release on 27 September does not count.
  - A relevant benefit is paid to a named person; pension credit is paid to the claimant of a
      couple.
  - A listed housemate shares the home on at least one day of the week; an undated shared home or
      partnership began before the week and continues after it, and a dated one includes a day of
      the week.
  - Regulation 4(4) applies only if the move to Scotland or Northern Ireland comes on or after a day
      of the week on which the person lived in England or Wales; a move on that same day counts.
  - For regulation 4(2)(a), the partnership and the shared home each last throughout the week when
      they begin no later than 21 September and end no earlier than 27 September; a first or last
      day inside the week counts as a day of it.

Lean check: this answer rests on 15 proof steps; Lean checked 15 certificates, 15 accepted; the answer document was admitted.


Question 2. How much is the payment?
Answer: £200.00

Clauses used: those listed above, plus:
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 3 (the age of 80 in
    or before the qualifying week)
    Source text:
      “(4) Subject to paragraphs (5) and (6), where P has reached the age of 80 in or before the
        qualifying week, the amount of a winter fuel payment is £300.”
    Read as:
      - The applicant has reached the age of 80 in or before the week exactly when the applicant's
          80th birthday is no later than 2026-09-27.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 3(3)
    Source text:
      “(3) Where P has not reached the age of 80 in or before the qualifying week, the amount of a
        winter fuel payment is £300 where—”
      “(a)a relevant benefit has been, or falls to be, paid to P in respect of the qualifying week,
        and”
      “(b)in that week, P is the partner of and living with a person who has reached the age of 80
        in or before that week.”
    Read as:
      - The applicant is a partner of the housemate and they share a mutual home on one day of the
          week exactly when the applicant is a partner of the housemate, they share a mutual home,
          the home either began before the week or began no later than the partnership's end date if
          the partnership has one, and the partnership either began before the week or began no
          later than the home's end date if the home has one.
      - If the applicant is entitled, has not reached 80, is paid a relevant benefit, and, on one
          day of the week, is the partner of and lives with a person who has reached 80, the amount
          is GBP 300.00.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 3(2)
    Source text:
      “(2) Where P has not reached the age of 80 in or before the qualifying week, the amount of a
        winter fuel payment is £100 where—”
      “(a)a relevant benefit has not been, nor falls to be, paid to P in respect of the qualifying
        week, and”
      “(b)P is—”
      “(i)in that week, living with a person entitled to a winter fuel payment under regulation 2 in
        respect of the qualifying week, or”
      “(ii)in residential care.”
    Read as:
      - If the applicant is entitled, has not reached 80, is paid no relevant benefit, and either
          lives with an entitled person or is in residential care, the amount is GBP 100.00.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 3(1)
    Source text:
      “3.—(1) Subject to paragraphs (2) and (3), where P has not reached the age of 80 in or before
        the qualifying week, the amount of a winter fuel payment is £200.”
    Read as:
      - If the applicant is entitled, has not reached 80, and neither regulation 3(2) nor 3(3)
          applies, the amount is GBP 200.00.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 3(6)
    Source text:
      “(6) Where P has reached the age of 80 in or before the qualifying week, the amount of a
        winter fuel payment is £150 where—”
      “(a)a relevant benefit has not been, nor falls to be, paid to P in respect of the qualifying
        week, and”
      “(b)P is—”
      “(i)in that week, living with a person entitled to a winter fuel payment under regulation 2 in
        respect of the qualifying week and that person has reached the age of 80, or”
      “(ii)in residential care.”
    Read as:
      - If the applicant is entitled, has reached 80, is paid no relevant benefit, and either lives
          with an entitled person who has reached 80 or is in residential care, the amount is GBP
          150.00.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 3(5)
    Source text:
      “(5) Subject to paragraph (6), where P has reached the age of 80 in or before the qualifying
        week, the amount of a winter fuel payment is £200 where—”
      “(a)a relevant benefit has not been, nor falls to be, paid to P in respect of the qualifying
        week, and”
      “(b)in that week, P is living with a person entitled to a winter fuel payment under regulation
        2 in respect of the qualifying week and that person has not reached the age of 80.”
    Read as:
      - If the applicant is entitled, has reached 80, is paid no relevant benefit, lives with an
          entitled person who has not reached 80, and regulation 3(6) does not apply, the amount is
          GBP 200.00.
  The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), regulation 3(4)
    Source text:
      “(4) Subject to paragraphs (5) and (6), where P has reached the age of 80 in or before the
        qualifying week, the amount of a winter fuel payment is £300.”
    Read as:
      - If the applicant is entitled, has reached 80, and neither regulation 3(6) nor 3(5) applies,
          the amount is GBP 300.00.

Assumptions: those listed above, plus:
  - Each person's pensionable-age date and 80th birthday are worked out by hand from the birth date
      (Pensions Act 1995, Schedule 4, paragraph 1, plus 80 years) and given as dates; the age
      arithmetic itself is not checked. The hand working takes a person to reach an age at the start
      of the birthday, and a birth date of 29 February 1960 as giving pensionable age no later than
      1 March 2026. Dates used here: the applicant's pensionable-age date is 2021-03-14; the
      applicant's 80th birthday is 2035-03-14.
  - A person excluded by regulation 4 is not “entitled under regulation 2”, so living with them does
      not lower the amount.
  - Regulation 3(3) needs one day of the week on which the person is both the partner of and living
      with the person aged 80; one shared day is enough.

Lean check: this answer rests on 18 proof steps; Lean checked 18 certificates, 18 accepted; the answer document was admitted.


Question 3. Does HMRC take the payment back because the applicant's total income is over £35,000?
Answer: NO

Clauses used: only those listed for the questions above.

Assumptions: those listed above, plus:
  - Whether HMRC takes the payment back follows the GOV.UK guide's £35,000 test on the total income
      the profile gives; the legal basis of the charge and the definition of total income are not
      pinned down. The guide's section is read as follows:
      The GOV.UK guide “Winter Fuel Payment”, section 7, “If your income is over £35,000”
        “7. If your income is over £35,000”
        “If your total income is over £35,000, HM Revenue and Customs (HMRC) will take your Winter
          Fuel Payment back.”
        “Your partner’s income does not count towards your total income.”
      Read as:
        - If the applicant is entitled and the applicant's total income is more than GBP 35000.00,
            HMRC takes the payment back and the recovered amount equals the amount.
        - If the applicant is entitled and the applicant's total income is at most GBP 35000.00,
            HMRC does not take the payment back and the recovered amount equals GBP 0.00.
  - The applicant has not opted out of the payment, so a person over the income limit receives it
      and HMRC takes it back.
      The guide: “If you do not opt out and your total income is over £35,000, you’ll receive the
        Winter Fuel Payment but HMRC will take it back.”

Lean check: this answer rests on 19 proof steps; Lean checked 19 certificates, 19 accepted; the answer document was admitted.


Question 4. How much does the applicant keep after that?
Answer: £200.00

Clauses used: only those listed for the questions above.

Assumptions: those listed above, plus:
  - HMRC takes back the whole payment or nothing, so the amount kept is the payment or £0.00.

Lean check: this answer rests on 21 proof steps; Lean checked 21 certificates, 21 accepted; the answer document was admitted.
```

The clauses list every rule the answer's proof reads, including the exclusions of regulation 4 that do not apply
(the proof shows each one does not). An answer whose proof Lean does not admit would print OPEN, never a guess.
