# Use case: eligibility (Winter Fuel Payment, winter 2026 to 2027)

This use case tests whether VE gets the **right answer** on a real benefit rule,
not only whether it can state the rule. It is also the first real-document test
of the W6a quantities and dates feature.

- **Rule set.** The Social Fund Winter Fuel Payment Regulations 2025
  (SI 2025/969, England and Wales), with the GOV.UK guide and two linked
  provisions. All four texts are pinned byte for byte with SHA-256 hashes in
  [PLAN.md](PLAN.md) section 1 and [`source/`](source/).
- **Cases.** 69 applicant profiles in [`cases.json`](cases.json). Each has an
  answer key that was written by hand before VE was run on it. A separate
  program, [`reference.py`](reference.py), was written from the source text
  and agrees with the key on all 69. Profiles B15 to B19 were added after the
  first run, by the eligibility review, and B20 to B23 and C25 to C27 by the
  eligibility recheck (see "Review fixes" below).
- **Questions.** For each profile: Q1, is the applicant entitled? For an
  entitled applicant, also: Q2, how much? Q3, does HMRC take it back because
  income is over £35,000? Q4, how much does the applicant keep? That makes
  231 scored questions (PLAN.md section 3).

The detailed figures are in [RESULTS.md](RESULTS.md), which `run.py` generates.

## Agreement with the answer key

| Route | Correct | Answered | Disagreements |
|---|---|---|---|
| Staged (the plan's fallback) | **231/231** questions, **69/69** profiles | 231/231 | none |
| Single shot (the whole problem in one proof search) | 0/231 | 0/231 | none; every answer is OPEN |

- **Staged route.** Every answer rests on proof certificates that Lean checked.
  All 1,608 step certificates were accepted by the Lean `ve_quantity` checker.
  All 231 answer documents were admitted by Lean.
- **Official answers.** On the 38 profiles whose answer the GOV.UK guide states
  directly, the staged route is correct on 131 of 131 questions.
- **Unflagged profiles.** On the 60 profiles without a flag, it is correct on
  198 of 198 questions.
- **Flagged profiles.** Each of the 9 flagged profiles is also correct. This
  means VE followed the reading the key adopted (PLAN.md section 4.2). It does
  not settle which reading of the law is right.
- **Disagreements.** There are none, so no disagreement needs a cause. No
  existing key was changed after any VE run; the review and the recheck only
  added profiles.

**Why this is not full independence.** One author wrote the key, the reference
program and the VE translation, all from the same adopted readings. The 38
guide-answered profiles are the part of the key that does not depend on this
author's reading.

**Does the case set catch translation errors?** Yes, for the 25 planned
mutants. Each mutant is a deliberate error in the translation, such as ">"
written as "≥" or one benefit removed from the list. Every mutant changed the
answer of the profile the plan named for it, so 25/25 were caught. The first
run had 19 mutants, and the case set missed two real errors that the review
then found, and a third that the recheck found. Mutants M20 to M25 now
reproduce those errors.

## Review fixes

The eligibility review (verdict FIX) found two places where the key's reading,
`reference.py` and the translation all misread the regulations the same way.
The three agreed with each other, so no test could see the errors. No existing
profile's answer depended on either one, which is why the first run scored
189/189 regardless.

- **A. Moving to Scotland or Northern Ireland (reg. 4(4), rule R11).** The
  regulation says "having been ordinarily resident in England or Wales on any
  day falling within the qualifying week, P becomes ordinarily resident in
  Scotland or Northern Ireland". That fixes an order: England or Wales first,
  then the move. R11 had dropped the order. So a person who lived in Scotland
  from 20 September and in England from 22 September got a Lean-certified NO.
  R11 now needs the move to fall on or after the first day of the week on
  which the person lives in England or Wales (reading AR6). That day is the
  later of the week's first day and the start of residence in England or
  Wales, and each bound decides one new profile.
  - B15: the review's case; now YES, £200.
  - B16: flagged `ambiguous-source`; decides the week's first day.
  - B19: decides the start of residence.
- **B. "Lives with" (reg. 1(4)(b), rule R6).** "They are not in residential
  care" describes the person who lives with someone, not the other person. R6
  also required the other person to be out of residential care. Two new
  profiles show the effect:
  - B17: a new care-home resident shares the home with an entitled sister who
    is in residential care. The amount is £100, not £200.
  - B18: the same, but with a partner who gets Pension Credit. The applicant
    is excluded under reg. 4(2)(a), where the old R6 said entitled.

Each new key was written by hand from the regulations before VE was run on the
profile. `reference.py` was corrected in the same way. A regression test puts
back each old reading and checks that it changes exactly the profiles added
for it.

The eligibility recheck (verdict FIX) found a third error, this time in the
translation alone. `reference.py` had it right.

- **C. The end of a care stay (reg. 1(4)(a), rule R5).** Residential care
  needs the person in the care home "throughout the qualifying week". The
  translation never read the stay's end date (`care.until`). So a stay from
  29 June to 26 September got a Lean-certified £100, where the regulation
  gives £200. No profile had an end date, so no test could see this. R5 now
  needs a stay with an end date to last until 27 September, the last day of
  the week. Seven new profiles cover it:
  - C25: the recheck's case; C27 ends before the week; both £200. C26 ends on
    27 September and is still £100.
  - B20 to B23 end a long stay on 24 September. Each shows one place where
    residential care matters: reg. 4(3) with Pension Credit (B20, now YES),
    the over-80 amount (B21, £300 not £150), a housemate's reg. 4(3) (B22,
    £100 not £200), and "lives with" and so reg. 4(2)(a) (B23, now NO).

  The underlying class of error is a profile field that no fact carries. The
  translation and `reference.py` now reject any field they do not read. The
  one exception is `home` on B08 and B09, which is listed as unread with its
  reason. A test changes each field of each profile in turn and checks that
  the facts change.

## What stayed OPEN and why

**Single shot is OPEN on every profile.** Each single-shot problem holds all
44 rules and the profile's facts. The prover works through the premises in
order, one branch at a time. Each "exactly when" rule costs several levels on a
branch: one to separate its two directions, then one split for each direction.
On profile A01 the search reached the tableau depth limit of 124 levels at its
124th step, so no branch had closed. Every other single-shot search also ended
without a certificate (status `NotFound`). A larger step budget would not help,
because the certificate format fixes the depth limit. The plan named this risk
as O9.
Its fallback is the staged route, which proves one derived fact at a time. Each
step uses only the rules that define that fact, the facts those rules mention,
and earlier steps. A fixed program chooses these premises from the formulas;
it never reads the key.

**The staged route has no OPEN answer.** Some steps about the housemate are
OPEN when the applicant lives alone, because no housemate facts exist then.
Those steps never decide an answer.

**Parts of the rule VE cannot state yet.** These enter as bridges, and the key
uses the same bridges. So the accuracy figure does not test VE on these steps.

- **The qualifying week (O1).** "The week beginning on the third Monday in
  September" needs weekday arithmetic, which W6a lacks. The week enters as the
  dates 2026-09-21 to 2026-09-27. VE checks only that they are 6 days apart.
- **Pensionable age and age 80 (O2).** Every birth date is before 1970, and
  W6a dates cannot go earlier than 1970-01-01. Probe P1 confirms this in Python
  and Lean. W6a also has no month or year durations. So each birth date enters
  as a pensionable-age date and an 80th birthday, worked out by hand from the
  Pensions Act 1995.
- **Weeks as days.** "52 weeks" and "12 weeks" enter as 364 and 84 days,
  because W6a has no week unit.

## Check status of each rule

| Rule (PLAN 4.1) | Source | Status | Notes |
|---|---|---|---|
| R1 qualifying week | reg. 1(3) | LABELLED, with O1 OPEN | the dates are a bridge; "third Monday" is not computed |
| R2 pensionable age reached | reg. 2(a) | CHECKED | the comparison is checked; the pensionable-age date is a LABELLED bridge (O2 OPEN) |
| age 80 reached | reg. 3 | CHECKED | the 80th birthday is a LABELLED bridge (O2 OPEN) |
| R3 resident on a day of the week | reg. 2(b) | CHECKED | "ordinarily resident" is LABELLED as a fact (O3) |
| R4 relevant benefit list | reg. 1(3) | CHECKED | all five benefits decide some profile |
| R5 residential care, 12 weeks | reg. 1(4)(a) | CHECKED | "care home" is LABELLED as a fact; a stay's end date must be no earlier than the week's last day (recheck C) |
| R6 lives with | reg. 1(4)(b) | CHECKED | "mutual home" is LABELLED as a fact; the care condition is on the subject only (review B) |
| R7 partner paid a relevant benefit | reg. 4(2)(a) | CHECKED | "partner" is LABELLED as a fact |
| R8 hospital over 52 weeks | reg. 4(2)(b), SI 2005/3360 reg. 2(5) | CHECKED | "free in-patient treatment" is LABELLED as a fact |
| R9 custody under a sentence | reg. 4(2)(c) | CHECKED | under reading AR1 |
| R10 care home and relevant benefit | reg. 4(3) | CHECKED | |
| R11 moved to Scotland or Northern Ireland | reg. 4(4) | CHECKED | under reading AR6: the move comes after a day of residence in England or Wales in the week (review A) |
| R12 no claim by 31 March | reg. 4(5), (6), 5(1) | CHECKED | payment without a claim is LABELLED as a fact |
| R13 entitlement | regs. 2 and 4(1) | CHECKED | |
| R14 and R15 amounts | reg. 3(1) to (6) | CHECKED | each "subject to" is an explicit negated condition |
| R16 income charge | GOV.UK guide | CHECKED | its legal basis is not pinned (O6 OPEN) |
| reg. 5(2) to (4), polygamous marriage | regs. 1 and 5 | UNFORMALISED | out of scope (O4) |
| Scotland and Northern Ireland schemes | other instruments | UNFORMALISED | out of scope (O7) |
| two or more other people in the home | reg. 3 | UNFORMALISED | needs a third role (O5) |

## Conflicts and gaps found in the sources

These were found while writing the key, and the run confirms that VE follows
the statutory reading on each.

- **Remand (B06).** The regulations exclude custody "under a sentence" only.
  The guide says anyone "in prison for the whole of the week" is not eligible.
- **Northern Ireland (B09).** These regulations give nothing in Northern
  Ireland. The guide says a person there is eligible under that scheme.
- **Care home under 12 weeks (C11, C12).** The regulations give £200. The
  guide's care-home row gives £100. For C12, the guide's own benefit row gives
  £200, so the guide conflicts with itself.
- **Hospital for exactly 52 weeks (C14).** The regulations exclude only "more
  than 52 weeks". The guide's "the year before" can be read to exclude it.
- **Living abroad from the first day of the week (C19).** The regulations need
  residence on any day of the week. The guide's "usually live outside the UK"
  can be read the other way.
- **Two readings in the regulations themselves (B10, C24).** B10 depends on
  whether an excluded person counts as "entitled under regulation 2". C24
  depends on whether release on the last day of the week ends custody
  "throughout" the week. The key and VE both use the readings in PLAN.md
  section 4.2.
- **Residence in Scotland that began before the week (B16).** Under the order
  in reg. 4(4), this person did not move to Scotland after living in England
  in the week, so reg. 4(4) does not apply. A reader who ignores "having been"
  would exclude them.

## English

- **Facts.** 69 of 127 distinct fact statements have a controlled English
  wording. Each of those parses back to the same statement with exactly one
  reading. Example: "The applicant's pensionable-age date is no later than
  2018-12-05." The other 58 are yes-or-no facts about a person, such as being a
  partner. The W6a surface has no wording for these.
- **Money.** "£35000.01" is accepted as input. The canonical wording is "GBP
  35000.01". "£35,000.00" is rejected, because the surface has no thousands
  separator.
- **Rules.** The rules have no controlled English, because W6a has no wording
  for an "if" rule over quantities (O8). Each rule instead carries a plain
  gloss and its source citation in [`rules.json`](rules.json).

## Differences from the plan

- **Staged steps are graph nodes, not cited lemmas.** A cited lemma must be
  proved from all the facts it finally rests on. So a lemma would need the same
  one large proof search that fails. A graph node is proved from earlier nodes,
  which keeps each search small. The documents are still `documents@1`
  quantity documents admitted by Lean.
- **Vocabulary.** "Lives with" is derived from a fact `shares_home`, so that
  R6 is part of the checked translation. Custody uses two facts,
  `detained_in_custody` and `under_sentence`, so that mutant M9 can be written.
  The benefit list in R4 is a five-way "or" over the named benefits. Each
  profile states, for all seven named benefits, whether that benefit is paid.
  This avoids a quantifier over benefits, which would need a closure fact.
- **Probe P6.** The plan expected single-shot certificates for profile A01.
  None were found, as explained above. The staged route answers A01 correctly.
- **Mutant M13** (counting the partner's income) changes 47 profiles, not
  only D05. A household with no housemate has no housemate income, so under
  M13 the question about the payment being taken back becomes OPEN.

## Files and how to run

| Path | Content |
|---|---|
| [`PLAN.md`](PLAN.md) | the plan, the adopted readings and the frozen key |
| [`cases.json`](cases.json) | the 69 profiles and their keys |
| [`reference.py`](reference.py) | the independent reference program |
| [`translation.py`](translation.py) | the VE translation: environment, rules, facts |
| [`environment.json`](environment.json), [`rules.json`](rules.json) | the generated environment and rules |
| [`run.py`](run.py) | runs VE on every profile and scores the answers |
| [`results.json`](results.json), [`RESULTS.md`](RESULTS.md) | the recorded run |
| [`../../tests/test_eligibility_wfp.py`](../../tests/test_eligibility_wfp.py) | fails on any mismatch or change |

Run `PATH=~/.elan/bin:$PATH lake build` in `lean/` first. Then run
`uv run python usecases/eligibility/run.py` from the repository root (about
5 minutes). No model calls are made.
