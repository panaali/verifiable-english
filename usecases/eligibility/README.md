# Use case: eligibility (Winter Fuel Payment, winter 2026 to 2027)

This use case tests whether VE gets the **right answer** on a real benefit rule,
not only whether it can state the rule. It is also the first real-document test
of the W6a quantities and dates feature.

- **Rule set.** The Social Fund Winter Fuel Payment Regulations 2025
  (SI 2025/969, England and Wales), with the GOV.UK guide and two linked
  provisions. All four texts are pinned byte for byte with SHA-256 hashes in
  [PLAN.md](PLAN.md) section 1 and [`source/`](source/).
- **Cases.** 57 applicant profiles in [`cases.json`](cases.json). Each has an
  answer key that was written by hand before VE was run. A separate program,
  [`reference.py`](reference.py), was written from the source text and agrees
  with the key on all 57.
- **Questions.** For each profile: Q1, is the applicant entitled? For an
  entitled applicant, also: Q2, how much? Q3, does HMRC take it back because
  income is over £35,000? Q4, how much does the applicant keep? That makes
  189 scored questions (PLAN.md section 3).

The detailed figures are in [RESULTS.md](RESULTS.md), which `run.py` generates.

## Agreement with the answer key

| Route | Correct | Answered | Disagreements |
|---|---|---|---|
| Staged (the plan's fallback) | **189/189** questions, **57/57** profiles | 189/189 | none |
| Single shot (the whole problem in one proof search) | 0/189 | 0/189 | none; every answer is OPEN |

- **Staged route.** Every answer rests on proof certificates that Lean checked.
  All 1,328 step certificates were accepted by the Lean `ve_quantity` checker.
  All 189 answer documents were admitted by Lean.
- **Official answers.** On the 38 profiles whose answer the GOV.UK guide states
  directly, the staged route is correct on 131 of 131 questions.
- **Unflagged profiles.** On the 49 profiles without a flag, it is correct on
  160 of 160 questions.
- **Flagged profiles.** Each of the 8 flagged profiles is also correct. This
  means VE followed the reading the key adopted (PLAN.md section 4.2). It does
  not settle which reading of the law is right.
- **Disagreements.** There are none, so no disagreement needs a cause. The
  key was not changed after any VE run.

**Why this is not full independence.** One author wrote the key, the reference
program and the VE translation, all from the same adopted readings. The 38
guide-answered profiles are the part of the key that does not depend on this
author's reading.

**Does the case set catch translation errors?** Yes, for the 19 planned
mutants. Each mutant is a deliberate error in the translation, such as ">"
written as "≥" or one benefit removed from the list. Every mutant changed the
answer of the profile the plan named for it, so 19/19 were caught.

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
| R5 residential care, 12 weeks | reg. 1(4)(a) | CHECKED | "care home" is LABELLED as a fact |
| R6 lives with | reg. 1(4)(b) | CHECKED | "mutual home" is LABELLED as a fact |
| R7 partner paid a relevant benefit | reg. 4(2)(a) | CHECKED | "partner" is LABELLED as a fact |
| R8 hospital over 52 weeks | reg. 4(2)(b), SI 2005/3360 reg. 2(5) | CHECKED | "free in-patient treatment" is LABELLED as a fact |
| R9 custody under a sentence | reg. 4(2)(c) | CHECKED | under reading AR1 |
| R10 care home and relevant benefit | reg. 4(3) | CHECKED | |
| R11 moved to Scotland or Northern Ireland | reg. 4(4) | CHECKED | |
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

## English

- **Facts.** 62 of 119 distinct fact statements have a controlled English
  wording. Each of those parses back to the same statement with exactly one
  reading. Example: "The applicant's pensionable-age date is no later than
  2018-12-05." The other 57 are yes-or-no facts about a person, such as being a
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
- **Mutant M13** (counting the partner's income) changes 43 profiles, not
  only D05. A household with no housemate has no housemate income, so under
  M13 the question about the payment being taken back becomes OPEN.

## Files and how to run

| Path | Content |
|---|---|
| [`PLAN.md`](PLAN.md) | the plan, the adopted readings and the frozen key |
| [`cases.json`](cases.json) | the 57 profiles and their keys |
| [`reference.py`](reference.py) | the independent reference program |
| [`translation.py`](translation.py) | the VE translation: environment, rules, facts |
| [`environment.json`](environment.json), [`rules.json`](rules.json) | the generated environment and rules |
| [`run.py`](run.py) | runs VE on every profile and scores the answers |
| [`results.json`](results.json), [`RESULTS.md`](RESULTS.md) | the recorded run |
| [`../../tests/test_eligibility_wfp.py`](../../tests/test_eligibility_wfp.py) | fails on any mismatch or change |

Run `PATH=~/.elan/bin:$PATH lake build` in `lean/` first. Then run
`uv run python usecases/eligibility/run.py` from the repository root (about
5 minutes). No model calls are made.
