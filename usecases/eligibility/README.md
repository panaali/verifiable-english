# Use case: eligibility (Winter Fuel Payment, winter 2026 to 2027)

This use case tests whether VE gets the **right answer** on a real benefit rule,
not only whether it can state the rule. It is also the first real-document test
of the W6a quantities and dates feature.

- **Rule set.** The Social Fund Winter Fuel Payment Regulations 2025
  (SI 2025/969, England and Wales), with the GOV.UK guide and two linked
  provisions. All four texts are pinned byte for byte with SHA-256 hashes in
  [PLAN.md](PLAN.md) section 1 and [`source/`](source/).
- **Cases.** 80 applicant profiles in [`cases.json`](cases.json). Each has an
  answer key that was written by hand before VE was run on it. A separate
  program, [`reference.py`](reference.py), was written from the source text
  and agrees with the key on all 80. Profiles B15 to B19 were added after the
  first run, by the eligibility review, B20 to B23 and C25 to C27 by the
  eligibility recheck, B24 to B30 for the review's finding C, and B31 to B34
  by the R7 recheck (see "Review fixes" below).
- **Questions.** For each profile: Q1, is the applicant entitled? For an
  entitled applicant, also: Q2, how much? Q3, does HMRC take it back because
  income is over £35,000? Q4, how much does the applicant keep? That makes
  269 scored questions (PLAN.md section 3).

The detailed figures are in [RESULTS.md](RESULTS.md), which `run.py` generates.

## Agreement with the answer key

| Route | Correct | Answered | Disagreements |
|---|---|---|---|
| Staged (the plan's fallback) | **269/269** questions, **80/80** profiles | 269/269 | none |
| Single shot (the whole problem in one proof search) | 0/269 | 0/269 | none; every answer is OPEN |

- **Staged route.** Every answer rests on proof certificates that Lean checked.
  All 2,352 step certificates were accepted by the Lean `ve_quantity` checker.
  All 269 answer documents were admitted by Lean.
- **Official answers.** On the 38 profiles whose answer the GOV.UK guide states
  directly, the staged route is correct on 131 of 131 questions.
- **Unflagged profiles.** On the 67 profiles without a flag, it is correct on
  226 of 226 questions.
- **Flagged profiles.** Each of the 13 flagged profiles is also correct. This
  means VE followed the reading the key adopted (PLAN.md section 4.2). It does
  not settle which reading of the law is right.
- **Disagreements.** There are none, so no disagreement needs a cause. No
  existing key was changed after any VE run; the review, the recheck, the
  finding C fix and the R7 recheck only added profiles.

**Why this is not full independence.** One author wrote the key, the reference
program and the VE translation, all from the same adopted readings. The 38
guide-answered profiles are the part of the key that does not depend on this
author's reading.

**Does the case set catch translation errors?** Yes, for the 32 planned
mutants. Each mutant is a deliberate error in the translation, such as ">"
written as "≥" or one benefit removed from the list. Every mutant changed the
answer of the profile the plan named for it, so 32/32 were caught. The first
run had 19 mutants, and the case set missed three real errors that the review
then found, a fourth that the recheck found, and a fifth that the R7 recheck
found. Mutants M20 to M32 now reproduce those errors.

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

The review's third finding (C) was left open by the first fix round and is
now fixed. It was in all three: the key's reading, `reference.py` and the
translation.

- **C. "Throughout the qualifying week" for a partner (reg. 4(2)(a), rule
  R7).** Reg. 4(2) excludes P when, "throughout the qualifying week", P is a
  partner of and living with a partner who gets a relevant benefit. R7 used
  `partner_of`, which had no time, and `shares_home`, which holds on some day
  of the week. So a couple who moved in together on 23 September would have
  been excluded, and calling R7 CHECKED hid that. No profile gave a date for
  the household, so no test could see this.
  - The profiles now say it: a housemate's home and partnership last the
    whole week unless the housemate's `shared_home` or `partnership` record
    gives a first or last day (reading AR5). R7 needs both periods to begin no
    later than 21 September and end no earlier than 27 September (reading
    AR7). VE checks these dates; they are not a bridge.
  - B24 to B27 start or end the shared home, or the partnership, inside the
    week. Each is YES, £100, where the old R7 would say NO.
  - B28 and B29 start both on the first day of the week, or end both on the
    last day. Both stay NO. They are flagged `ambiguous-source`, because a
    reading that needs the whole of each day would say YES.
  - B30 checks that the fix did not spread. Reg. 3(3) says "in that week",
    not "throughout". A partner over 80 who moves in during the week still
    gives £300.

  `reference.py` also had a second, harmless gap of the same kind. It looked
  for the couple on the applicant, but `cases.json` records it on the
  housemate, so the housemate's own reg. 4(2)(a) never applied. It now reads
  the housemate's record for both persons. This changed no key, because the
  housemate's reg. 4(2)(a) needs the applicant to get a relevant benefit, and
  every amount that depends on the housemate's entitlement needs the
  applicant not to. The translation always read the couple both ways.
  Mutants M26 to M30 drop each whole-week test, make its bounds strict, or
  read "throughout" into reg. 3(3); each changes the profiles named for it.

The R7 recheck (verdict FIX) found that the B30 check was too weak. The error
was in all three: the key's reading, `reference.py` and the translation.

- **D. One day for "the partner of and living with" (reg. 3(3), rule R14).**
  Reg. 3(3) gives £300 when "in that week, P is the partner of and living
  with" a person aged 80. R14 asked for a partnership on some day of the week
  and a shared home on some day, not necessarily the same one. So B30 with the
  partnership ending on 22 September, a day before the partner moves in, got
  a Lean-admitted £300, where the regulation gives £200. Every premise was
  true in the reference model, because the reference read 3(3) the same way.
  - Reading AR8: some day of the week must lie in both periods. Since each
    period includes a day of the week (AR5), that is two bounds: the home
    begins no later than the partnership ends, and the partnership begins no
    later than the home ends. A new rule R14a derives this, and R14's 3(3)
    uses it. `reference.py` computes the intersection of the two periods and
    the week directly, and a test checks that the two agree, in Python, Lean
    and Rust, on every household of a grid of first and last days.
  - B31 (the recheck's case) and B32 (the other order) share no day: £200.
  - B33 and B34 share only one day, the last of one period and the first of
    the other: £300. They are flagged `ambiguous-source`, because a reading
    that needs the whole of that day would give £200.
  - Mutant M31 restores the old 3(3) and changes B31 and B32; M32 makes both
    bounds strict and changes B33 and B34.

  The other paragraphs of reg. 3 ask "in that week" about one period only,
  the shared home with a person whose entitlement is for the week, so AR8
  concerns 3(3) alone.

## What stayed OPEN and why

**Single shot is OPEN on every profile.** Each single-shot problem holds all
49 rules and the profile's facts. The prover works through the premises in
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
| R7 partner paid a relevant benefit | reg. 4(2)(a) | CHECKED | "partner" is LABELLED as a fact; the partnership and the shared home must each cover every day of the week, under reading AR7 (review C). An undated household is taken to cover the whole week (AR5) |
| R8 hospital over 52 weeks | reg. 4(2)(b), SI 2005/3360 reg. 2(5) | CHECKED | "free in-patient treatment" is LABELLED as a fact |
| R9 custody under a sentence | reg. 4(2)(c) | CHECKED | under reading AR1 |
| R10 care home and relevant benefit | reg. 4(3) | CHECKED | |
| R11 moved to Scotland or Northern Ireland | reg. 4(4) | CHECKED | under reading AR6: the move comes after a day of residence in England or Wales in the week (review A) |
| R12 no claim by 31 March | reg. 4(5), (6), 5(1) | CHECKED | payment without a claim is LABELLED as a fact |
| R13 entitlement | regs. 2 and 4(1) | CHECKED | |
| R14 and R15 amounts | reg. 3(1) to (6) | CHECKED | each "subject to" is an explicit negated condition; 3(3) needs the partnership and the shared home on one common day of the week (R14a, reading AR8, R7 recheck) |
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
- **Two readings in the regulations themselves (B10, C24, B28, B29).** B10
  depends on whether an excluded person counts as "entitled under regulation
  2". C24 depends on whether release on the last day of the week ends custody
  "throughout" the week. B28 and B29 depend on whether moving in on the first
  day, or separating after the last day, counts as "throughout" for a couple.
  The key and VE both use the readings in PLAN.md section 4.2.
- **Residence in Scotland that began before the week (B16).** Under the order
  in reg. 4(4), this person did not move to Scotland after living in England
  in the week, so reg. 4(4) does not apply. A reader who ignores "having been"
  would exclude them.

## English

- **Facts.** 86 of 166 distinct fact statements have a controlled English
  wording. Each of those parses back to the same statement with exactly one
  reading. Example: "The applicant's pensionable-age date is no later than
  2018-12-05." The other 80 are yes-or-no facts about a person, such as being a
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
- **Mutant M13** (counting the partner's income) changes 62 profiles, not
  only D05. A household with no housemate has no housemate income, so under
  M13 the question about the payment being taken back becomes OPEN.

## Files and how to run

| Path | Content |
|---|---|
| [`PLAN.md`](PLAN.md) | the plan, the adopted readings and the frozen key |
| [`cases.json`](cases.json) | the 80 profiles and their keys |
| [`reference.py`](reference.py) | the independent reference program |
| [`translation.py`](translation.py) | the VE translation: environment, rules, facts |
| [`environment.json`](environment.json), [`rules.json`](rules.json) | the generated environment and rules |
| [`run.py`](run.py) | runs VE on every profile and scores the answers |
| [`results.json`](results.json), [`RESULTS.md`](RESULTS.md) | the recorded run |
| [`../../tests/test_eligibility_wfp.py`](../../tests/test_eligibility_wfp.py) | fails on any mismatch or change |

Run `PATH=~/.elan/bin:$PATH lake build` in `lean/` first. Then run
`uv run python usecases/eligibility/run.py` from the repository root (about
6 minutes with the default six workers). No model calls are made.
