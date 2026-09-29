# Use case: eligibility (Winter Fuel Payment, winter 2026 to 2027)

> Status: **PLAN**, 2026-09-29, branch `usecase/eligibility`. No VE translation
> exists yet and VE has not been run on any case. The answer key in section 5
> and `cases.json` is frozen at the commit that adds this file. A later change to
> a key must be a separate commit that says why; it must not be folded into a
> results commit. No model calls were made.
>
> **Plan review applied** (`eligibility-planreview.final.md`, verdict FIX):
> A, one scoring definition with the same denominators everywhere (sections 3
> and 9); B, Q2 to Q4 are not applicable after a certified NO, and the fallback
> trigger no longer needs to know why a search failed (section 8); C, four
> profiles B11 to B14 make each relevant-benefit membership decisive, with
> deletion mutants M15 to M19 (sections 5 and 8). The new keys were written
> before any VE run, in the same way as the others.
>
> **Eligibility review applied** (`eligibility-review.final.md`, verdict FIX),
> after the first run. The review found two misreadings shared by the key's
> reading, `reference.py` and the translation. No existing key depended on
> either, so all 57 existing keys stand.
>
> - **A:** R11 lost the order in reg. 4(4). The move to Scotland or Northern
>   Ireland must come on or after a day of QW on which x is resident in
>   England or Wales (new reading AR6).
> - **B:** R6 required the *other* person to be out of residential care. In
>   reg. 1(4)(b), "they are not in residential care" qualifies only the person
>   who lives with another.
>
> Profiles B15 to B19 cover both (section 5). Mutants M20 to M23 restore the
> old readings, or drop one bound of AR6 (section 8). Their keys were written by hand from S1 before
> VE was run on them.

This use case measures VE's **accuracy**, not only its coverage. VE checks a
published benefit rule on 62 applicant profiles, and its answers are compared
with an answer key worked out beforehand from the source. It is also the first
real-document test of the merged W6a quantities and dates feature
([units-schema.md](../../docs/spec/units-schema.md),
[W6A-STATUS.md](../../docs/W6A-STATUS.md)).

## 1. Source (pinned)

The rule set is the **Social Fund Winter Fuel Payment Regulations 2025**
(SI 2025/969, England and Wales), applied to the winter 2026 to 2027 qualifying
week. Three companion texts supply what the regulations point to. All four
files were retrieved on **2026-09-29 (UTC)** with `curl` and are stored byte for
byte in [`source/`](source/). The `.txt` files are the main-content text
extracted by [`source/extract_text.py`](source/extract_text.py), which uses
only the standard library.

| Id | Document | URL | Raw file, SHA-256 | Extracted text, SHA-256 |
|---|---|---|---|---|
| S1 | SI 2025/969 **as made** (regs. 1–7 and Explanatory Note) | `https://www.legislation.gov.uk/uksi/2025/969/made/data.xht?view=snippet&wrap=true` | `uksi-2025-969-made.xht` `d59a3858f58c743eac845a392e287ec994d7cdb524769158c27f3a00e56ddfee` | `6c1f40186307980ec7052af0131d9c9e205dea26e9dce920c87b7bcd1d577b26` |
| S2 | GOV.UK guide "Winter Fuel Payment", printable version (winter 2026 to 2027 text) | `https://www.gov.uk/winter-fuel-payment/print` | `wfp-print.html` `2e9d267c1da1c2e4620eaac3bfe8018950c81f1b1540f37d31c4a35d75015b98` | `befb46871c1ad7d7a00b2f11a5e3466dcabd5233d19916d10095af7bc62f8d0f` |
| S3 | Social Security (Hospital In-Patients) Regulations 2005 (SI 2005/3360), reg. 2 (latest revised version at retrieval) | `https://www.legislation.gov.uk/uksi/2005/3360/regulation/2/data.xht?view=snippet&wrap=true` | `uksi-2005-3360-reg2.xht` `8c81ae4c80dfa372f5207464bc7be1486e9ba6435434f38086c6ee2698c695d5` | `555de928335a3a8875db068978b0d9c0c3646ab706d78b466e37ce4e0f46c72b` |
| S4 | Pensions Act 1995, Sch. 4 (latest revised version at retrieval) | `https://www.legislation.gov.uk/ukpga/1995/26/schedule/4/data.xht?view=snippet&wrap=true` | `ukpga-1995-26-sch4.xht` `d50a2ee81b8e0a3a7fc83dc65daba90feaee4bef704b9a47e20840932af8e6ae` | `4d1fe57c20e9e0778cb28514bd2bea66d32d500614f9d925a8e1419a6d129815` |

All four are Crown copyright under the Open Government Licence v3.0, which
permits storing and republishing these copies with attribution.

**Why this rule set.**

- **Official, public and stable.** S1 is an enacted statutory instrument.
  Its "as made" text never changes, and it is short: seven regulations, all
  pinned. S3 and S4 are revised versions, so their bytes can change; the stored
  copies are the reference.
- **Numbers, dates and exceptions.** The rule has money amounts (£100, £150,
  £200, £300), an income threshold (£35,000), a fixed qualifying week, two
  ages, a 52-week hospital period, a 12-week residential-care period, a
  31 March claim deadline, and exceptions stated with "subject to".
- **An official answer for many profiles.** S2's section 3 ("How much you'll
  get") is a table of 12 household situations with the amount for each. Its
  section 2 turns the regulations' age tests into birth-date cut-offs for this
  winter (27 June 1960 and 28 September 1946), a check we can repeat
  independently from S4. These are the official worked examples used below.
- **Independently computable.** Every answer follows from dates and amounts by
  a short chain of rules, so it can be worked by hand and by a small program
  written from the text.
- **It stresses W6a where it is weakest.** Birth dates fall before 1970, and
  "age 80" is a year duration. Both lie outside the W6a slice (section 7).

S1 governs where S1 and S2 differ. S2 is authoritative only for the income
charge, whose legal basis is not pinned here (section 7, O6).

## 2. Scope

**In scope.** Entitlement under S1 regs. 2 and 4, and the amount under reg. 3,
for one applicant P for the qualifying week **21–27 September 2026**. P lives
alone, in a care home, or with **one** other person H, who is either P's
partner or not. There is also the S2 income question: does HMRC take the
payment back, and how much does P keep?

**Out of scope, with reasons.**

- **Northern Ireland and Scotland schemes.** Other instruments cover these.
  One profile (B09) records that S1 gives no entitlement in Northern Ireland.
- **Households with two or more other people.** They need a third role
  instance of the rules; see the vocabulary in section 6.
- **Reg. 5(2) (immigration decisions) and reg. 5(3)–(4) (evidence and
  revision).** They do not change a first-instance answer for these profiles.
- **Polygamous marriages and "temporary absence".** These are legal
  classifications that are taken as facts.
- **HMRC collection mechanics.** This covers S2's "£30 to £33 more tax each
  month" example, which is approximate and depends on tax codes.

## 3. Questions

For each profile, four questions:

| Q | Question | Answer form |
|---|---|---|
| Q1 | Is P entitled to a winter fuel payment for winter 2026 to 2027 (S1 regs. 2 and 4)? | YES / NO |
| Q2 | If entitled, what is the amount (S1 reg. 3)? | one of £100.00, £150.00, £200.00, £300.00 |
| Q3 | If entitled, does HMRC take the payment back (S2: P's total income over £35,000)? | YES / NO |
| Q4 | If entitled, how much does P keep after that? | £ amount |

The profiles contain 48 entitled and 14 not-entitled cases. **Scoring
definition** (used everywhere in this plan and in the results):

- Q1 is scored on every profile.
- Q2, Q3 and Q4 are scored only on the profiles whose key is entitled. On a
  not-entitled profile they are **not applicable**, and neither the key nor VE
  gives them an answer. VE's NO on Q1 is scored as Q1 only.
- That gives 62 + 48 + 48 + 48 = **206 scored questions**. The same 206 are
  the denominator for accuracy, coverage and precision. (Before the
  eligibility review added B15 to B19, it was 57 + 44 × 3 = 189.)

A disagreement on Q1 still costs the Q2 to Q4 points of an entitled profile.
If VE answers NO or OPEN there, it gives no amount, and those three questions
count as wrong.

## 4. Rules, adopted readings and bridges

This is the reading the key uses. The VE translation must follow the same
reading, rule by rule, with the source citation carried on each formula.

### 4.1 Rules

Notation: QW = the qualifying week, [QW₀, QW₁] = [2026-09-21, 2026-09-27].
"RB(x)" means a relevant benefit has been, or falls to be, paid to x for the
qualifying week.

| Rule | Source | Content |
|---|---|---|
| R1 | S1 reg. 1(3) "qualifying week" | QW is the week beginning on the third Monday in September 2026. |
| R2 | S1 reg. 2(a) | x reached pensionable age in or before QW. |
| R3 | S1 reg. 2(b) | x is ordinarily resident in England or Wales on **any** day of QW: residence began no later than QW₁, and it continues or its last day is no earlier than QW₀. |
| R4 | S1 reg. 1(3) "relevant benefit" | The closed list: income support, income-based JSA, state pension credit, income-related ESA and universal credit. State Pension and Attendance Allowance are not on it. |
| R5 | S1 reg. 1(4)(a) | x is **in residential care** when x resides in a care home (or independent hospital, or Polish resettlement accommodation) throughout QW and for at least 12 weeks (84 days) ending immediately before QW. Care must have begun no later than 2026-06-29. |
| R6 | S1 reg. 1(4)(b) | x **lives with** y when they share accommodation as their mutual home and **x** is not in residential care. The condition is on x only; y may be in residential care. So R6 is not symmetric. |
| R7 | S1 reg. 4(2)(a) | Excluded: throughout QW, x is a partner of and living with y, where y has reached pensionable age and RB(y). |
| R8 | S1 reg. 4(2)(b) and S3 reg. 2(5) | Excluded: throughout QW, x receives free in-patient treatment, and has done so for **more than 52 weeks** (more than 364 days) ending immediately before QW. A treatment period begins the day **after** admission and ends on the day of leaving. So "throughout QW" means admission ≤ 2026-09-20 and discharge ≥ 2026-09-27, and "more than 52 weeks" means admission ≤ 2025-09-20. |
| R9 | S1 reg. 4(2)(c) | Excluded: throughout QW, x is detained in custody **under a sentence** imposed by a court. |
| R10 | S1 reg. 4(3) | Excluded: x is in residential care (R5) and RB(x). |
| R11 | S1 reg. 4(4) | Excluded: x is resident in England or Wales on a day d of QW, and **afterwards** becomes ordinarily resident in Scotland or Northern Ireland: d ≤ the first day of that residence ≤ QW₁ (AR6). With d the earliest such day, this is: R3, and max(start of E&W residence, QW₀) ≤ start of Scotland/NI residence ≤ QW₁. |
| R12 | S1 reg. 4(5)–(6), reg. 5(1) | Excluded: x made no claim on or before 2027-03-31, and was not paid without a claim. |
| R13 | S1 regs. 2 and 4(1) | **entitled(x)** ⇔ R2 ∧ R3 ∧ none of R7–R12. |
| R14 | S1 reg. 3(1)–(3), P not 80 by QW₁ | £100 if ¬RB(P) and (P lives with an entitled person, or P is in residential care) [3(2)]. Otherwise £300 if RB(P) and P is the partner of, and lives with, someone who has reached 80 by QW₁ [3(3)]. Otherwise £200 [3(1)]. |
| R15 | S1 reg. 3(4)–(6), P 80 by QW₁ | £150 if ¬RB(P) and (P lives with an entitled person who has reached 80, or P is in residential care) [3(6)]. Otherwise £200 if ¬RB(P) and P lives with an entitled person who has not reached 80 [3(5), "subject to paragraph (6)"]. Otherwise £300 [3(4)]. |
| R16 | S2 §7 "If your income is over £35,000" | Recovered ⇔ entitled(P) and P's total income > £35,000.00; a partner's income does not count. Kept = amount − recovered amount, where the recovered amount is the whole payment or £0.00. |

### 4.2 Adopted readings (where the text leaves a choice)

- **AR1: day granularity of "throughout the qualifying week" for custody
  (R9).** P is detained throughout QW when custody began before QW₀ and release
  is after QW₁. Release *on* 2026-09-27 does not count as throughout; the other
  reading would count it. Profile C24 is flagged `ambiguous-source`. For
  hospital, S3 reg. 2(5) fixes the day rule, so R8 has no such choice.
- **AR2: "a person entitled to a winter fuel payment under regulation 2"
  (reg. 3(2), (5), (6)).** Reg. 4(1) says regulation 2 "does not apply" to an
  excluded person. So a person excluded by reg. 4 is **not** "entitled under
  regulation 2". Profile B10 is flagged `ambiguous-source`; the other reading
  gives £100 instead of £200.
- **AR3: a new care-home resident (under 12 weeks).** Such a person is not in
  residential care (R5). They are also not taken to "live with" the other
  residents under R6, because the profile gives no mutual home with an entitled
  person. Profile C11 is flagged `ambiguous-source` and `guide-divergence`: the
  S2 care-home row would give £100, S1 as read here £200. When the profile does
  give a mutual home (B17, B18), such a person lives with the housemate under
  R6, even when the housemate is in residential care.
- **AR4: relevant benefit paid to a couple.** "Paid to x" is a per-person fact
  in the profile. For Pension Credit, it is paid to the claimant of the couple.
  In B03, universal credit is recorded as paid to the partner only. The
  joint-UC question stays OPEN (O3).
- **AR5: household extent.** A housemate listed in a profile shares P's home
  during QW. P lives with no one else.
- **AR6: order in reg. 4(4)** (added by the eligibility review). "Having been
  ordinarily resident in England or Wales on any day falling within the
  qualifying week, P becomes ordinarily resident in Scotland or Northern
  Ireland" puts the E&W day first. Residence in Scotland or Northern Ireland
  that began before every E&W day of QW is not a move under 4(4). A move on
  that same day counts, since a person can be resident in both places on the
  day of moving. B15 and B19 (moved from Scotland to England, before or
  during QW) follow from the text. B16 is flagged `ambiguous-source`: it is resident in Scotland from
  before QW while still resident in England on its first two days. The
  unordered reading, which ignores "having been", would exclude all three.

### 4.3 Bridges (facts derived outside VE, with their derivation)

VE cannot state these (section 7). The key and the VE input both use them. So
the accuracy figure does **not** test VE on these steps; the probes in
section 8 record why.

- **B1, the qualifying week.** The third Monday of September 2026 is
  2026-09-21 (1 September 2026 is a Tuesday), so QW = 2026-09-21 to
  2026-09-27. This agrees with S2 ("21 to 27 September 2026"). VE can check
  only that QW₁ is 6 days after QW₀.
- **B2, the pensionable-age date** (S4 para. 1; a person attains an age at
  the start of the anniversary, Family Law Reform Act 1969 s. 9).

  | Birth date | Rule in S4 | Pensionable-age date given to VE |
  |---|---|---|
  | before 1953-12-06 (1942-01-15, 1944-05-02, 1946-09-26/27/28) | paras (1)–(4): at the latest 2018-12-05, whatever the sex | "no later than 2018-12-05" (a bound) |
  | 1955-03-14 | para (6): 66 | 2021-03-14 |
  | 1957-11-02 | para (6): 66 | 2023-11-02 |
  | 1960-02-29 | para (6): 66; 2026 has no 29 February | "no later than 2026-03-01" (either reading) |
  | 1960-06-27 | para (7) table 3: 66 years 3 months | 2026-09-27 |
  | 1960-06-28 | para (7) table 3: 66 years 3 months | 2026-09-28 |
  | 1970-08-19 | para (8): 67 | 2037-08-19 |

- **B3, the 80th birthday.** Birth date plus 80 years: 1942-01-15 → 2022-01-15;
  1944-05-02 → 2024-05-02; 1946-09-27 → 2026-09-27; 1946-09-28 → 2026-09-28;
  1955-03-14 → 2035-03-14; 1957-11-02 → 2037-11-02; 1960-02-29 → 2040-02-29;
  1960-06-27 → 2040-06-27; 1960-06-28 → 2040-06-28; 1970-08-19 → 2050-08-19.
  This agrees with S2's "born before 28 September 1946".
- **B4, weeks as days.** 52 weeks = 364 days and 12 weeks = 84 days. W6a has
  no week unit and no conversion between units, so the translator multiplies.

## 5. Answer key (written before any VE run)

**Defaults** for every person unless the profile says otherwise:

- ordinarily resident in England since 1990 and remains so;
- paid State Pension only (no relevant benefit);
- no care home, hospital stay or custody;
- paid without a claim;
- total income £20,000.00.

**"Std"** in the justification column means: R2 and R3 hold and no exclusion
among R7–R12 applies, so the person is entitled. Q3 is NO and Q4 equals Q2
because £20,000.00 is not over £35,000.00.

**Basis:**

- `guide`: S2 states this answer for this situation (an official example).
- `SI`: derived from S1 (with S3 and S4); S2 is silent or coarser.
- `SI≠guide`: S1 and S2 point to different answers, and the key follows S1.

| Id | Profile | Q1 | Q2 | Q3 | Q4 | Justification | Basis |
|---|---|---|---|---|---|---|---|
| A01 | alone, b. 1955-03-14 | YES | £200 | NO | £200 | Std; under 80, ¬RB, no housemate, no care → 3(1) | guide |
| A02 | alone, b. 1944-05-02 | YES | £300 | NO | £300 | Std; 80 on 2024-05-02 → 3(4) | guide |
| A03 | b. 1955, partner b. 1957, no RB | YES | £100 | NO | £100 | Std; partner entitled (Std); P under 80, ¬RB, lives with entitled → 3(2) | guide |
| A04 | b. 1955, partner b. 1944, no RB | YES | £100 | NO | £100 | as A03; P's age decides 3(2) | guide |
| A05 | b. 1944, partner b. 1955, no RB | YES | £200 | NO | £200 | P 80; lives with entitled person under 80 → 3(5) | guide |
| A06 | b. 1944, partner b. 1942, no RB | YES | £150 | NO | £150 | P 80; lives with entitled person aged 80 → 3(6)(b)(i) | guide |
| A07 | b. 1955, Pension Credit claimant; partner b. 1957 | YES | £200 | NO | £200 | Std (R7 concerns the partner, not P); RB(P), partner under 80 → not 3(3) → 3(1) | guide |
| A08 | b. 1955, Pension Credit claimant; partner b. 1944 | YES | £300 | NO | £300 | RB(P), partner 80 → 3(3) | guide |
| A09 | b. 1944, Pension Credit claimant; partner b. 1955 | YES | £300 | NO | £300 | P 80, RB(P) → not 3(5)/(6) → 3(4) | guide |
| A10 | alone, b. 1955, Pension Credit | YES | £200 | NO | £200 | RB, not in residential care → 3(1) | guide |
| A11 | alone, b. 1944, Pension Credit | YES | £300 | NO | £300 | → 3(4) | guide |
| A12 | care home since 2025-01-10, b. 1955, no RB | YES | £100 | NO | £100 | R5 holds (well over 84 days); ¬RB → R10 no; 3(2)(b)(ii) | guide |
| A13 | care home since 2025-01-10, b. 1944, no RB | YES | £150 | NO | £150 | 3(6)(b)(ii) | guide |
| B01 | b. 1957, partner b. 1955 is Pension Credit claimant | NO | — | — | — | R7: partner reached PA (2021-03-14) and RB(partner) | guide ("one of you") |
| B02 | b. 1957, lives with brother b. 1955 (not partner) who gets Pension Credit | YES | £100 | NO | £100 | R7 needs a partner → no; brother entitled (R7 for him needs a partner too); P ¬RB lives with entitled → 3(2) | SI |
| B03 | b. 1955, partner b. 1970 paid universal credit | YES | £200 | NO | £200 | R7: partner PA date 2037-08-19 → not reached → no exclusion; partner not entitled (R2) → 3(2) no → 3(1) | SI |
| B04 | care home since 2025-01-10, Pension Credit | NO | — | — | — | R10: residential care and RB | guide |
| B05 | care home since 2025-02-01, Attendance Allowance only | YES | £100 | NO | £100 | Attendance Allowance not on the R4 list → ¬RB → 3(2)(b)(ii) | guide |
| B06 | on remand (no sentence) 2026-08-01 to 2026-11-30 | YES | £200 | NO | £200 | R9 needs custody "under a sentence" → no; 3(1). S2 says "in prison for the whole of the week" → not eligible | SI≠guide |
| B07 | sentenced, custody 2026-03-01 to 2027-01-15 | NO | — | — | — | R9 | guide |
| B08 | has always lived in Scotland | NO | — | — | — | R3 fails | guide |
| B09 | has always lived in Northern Ireland | NO | — | — | — | R3 fails under S1 (E&W only); S2 says eligible under the NI scheme (flag `scope`) | SI≠guide |
| B10 | b. 1955, lives with sister b. 1957 who leaves E&W 2026-09-23 and is resident in Scotland from 2026-09-24 | YES | £200 | NO | £200 | sister excluded by R11 → not entitled (AR2) → 3(2) no → 3(1) (flag `ambiguous-source`; other reading £100) | SI |
| B11 | care home since 2025-01-10, b. 1955, paid income support | NO | — | — | — | income support is on the R4 list → RB(P); R10: residential care and RB | SI |
| B12 | b. 1957, partner b. 1955 paid income-based JSA | NO | — | — | — | income-based JSA is on the R4 list; R7: partner reached PA and RB(partner) | SI |
| B13 | b. 1955 paid income-related ESA, partner b. 1957, no RB | YES | £200 | NO | £200 | ESA is on the R4 list → RB(P) → not 3(2); partner under 80 → not 3(3) → 3(1). Without ESA on the list: £100 | SI |
| B14 | b. 1955 paid universal credit, partner b. 1944, no RB | YES | £300 | NO | £300 | universal credit is on the R4 list → RB(P); partner 80 → 3(3). Without it on the list: £100 | SI |
| B15 | b. 1955, resident in Scotland from 2026-09-20, resident in England from 2026-09-22 and remains | YES | £200 | NO | £200 | R3: resident 2026-09-22 to QW₁; R11 (AR6): the Scotland residence began before the first E&W day of QW → no; alone → 3(1). Unordered R11: NO | SI |
| B16 | b. 1955, resident in Scotland from 2026-09-10, last day resident in England 2026-09-22 | YES | £200 | NO | £200 | R3: resident 2026-09-21 and 22; R11 (AR6): the Scotland residence began before 2026-09-21 → no; → 3(1) (flag `ambiguous-source`; unordered R11: NO) | SI |
| B17 | b. 1955, care home from 2026-06-30, no RB; shares it with sister b. 1957 in residential care since 2025-01-10, no RB | YES | £100 | NO | £100 | P: 83 days → not R5; R6 conditions P only → P lives with sister; sister: R5 holds, ¬RB → R10 no → entitled; P under 80, ¬RB, lives with entitled → 3(2). Condition on both: £200 | SI |
| B18 | as B17, but the housemate is P's partner and gets Pension Credit | NO | — | — | — | P lives with partner (R6 on P only); partner reached PA (2023-11-02) and RB(partner) → R7. Condition on both: YES £200 | SI |
| B19 | b. 1955, resident in Scotland from 2026-09-22, resident in England from 2026-09-24 and remains | YES | £200 | NO | £200 | R3: resident 2026-09-24 to QW₁; R11 (AR6): the Scotland residence began within QW but before the first E&W day → no; → 3(1). Unordered R11: NO | SI |
| C01 | alone, b. 1960-06-27 | YES | £200 | NO | £200 | PA date 2026-09-27 = QW₁ → R2 holds | guide |
| C02 | alone, b. 1960-06-28 | NO | — | — | — | PA date 2026-09-28 > QW₁ | guide |
| C03 | alone, b. 1960-02-29 | YES | £200 | NO | £200 | PA 2026-02-28 or 2026-03-01; both ≤ QW₁ | guide |
| C04 | alone, b. 1946-09-27 | YES | £300 | NO | £300 | 80 on 2026-09-27 = QW₁ → 3(4) | guide |
| C05 | alone, b. 1946-09-28 | YES | £200 | NO | £200 | 80 on 2026-09-28 > QW₁ → under 80 → 3(1) | guide |
| C06 | b. 1946-09-27, partner b. 1946-09-28, no RB | YES | £200 | NO | £200 | P 80; partner entitled, not 80 → 3(5) | guide |
| C07 | b. 1946-09-28, partner b. 1946-09-27, no RB | YES | £100 | NO | £100 | P under 80, ¬RB, lives with entitled → 3(2) | guide |
| C08 | b. 1946-09-28 Pension Credit claimant, partner b. 1946-09-27 | YES | £300 | NO | £300 | RB(P), partner 80 on QW₁ → 3(3) | guide |
| C09 | b. 1955 Pension Credit claimant, partner b. 1946-09-28 | YES | £200 | NO | £200 | partner turns 80 on 2026-09-28 → not 3(3) → 3(1) | guide |
| C10 | care home from 2026-06-29, no RB | YES | £100 | NO | £100 | 84 days before QW → R5 holds → 3(2)(b)(ii) | guide |
| C11 | care home from 2026-06-30, no RB | YES | £200 | NO | £200 | 83 days → not R5; AR3 → 3(1) (flag `ambiguous-source`; S2 care row gives £100) | SI≠guide |
| C12 | care home from 2026-06-30, Pension Credit | YES | £200 | NO | £200 | not R5 → R10 no; RB → 3(1). S2 eligibility agrees; S2's care row (£100) conflicts with its benefit row (£200) | SI≠guide |
| C13 | in-patient, admitted 2025-09-20, discharged 2026-10-20 | NO | — | — | — | period from 2025-09-21: 365 days before QW > 364, and throughout QW → R8 | guide |
| C14 | in-patient, admitted 2025-09-21, discharged 2026-10-20 | YES | £200 | NO | £200 | period from 2025-09-22: 364 days = 52 weeks, not more → R8 no. S2's "the year before" arguably excludes | SI≠guide |
| C15 | in-patient, admitted 2024-01-10, discharged 2026-09-26 | YES | £200 | NO | £200 | the period ends 2026-09-26 < QW₁ → not throughout QW | guide |
| C16 | in-patient, admitted 2024-01-10, discharged 2026-09-27 | NO | — | — | — | the period ends on the day of leaving (S3 reg. 2(5)) = QW₁ → throughout; more than 52 weeks → R8 | SI |
| C17 | resident in England from 2026-09-27 | YES | £200 | NO | £200 | resident on QW₁ ("any day") → R3 | SI |
| C18 | resident in England from 2026-09-28 | NO | — | — | — | no day of QW → R3 fails | SI |
| C19 | last day resident in England 2026-09-21, then Spain | YES | £200 | NO | £200 | resident on QW₀ → R3; Spain is not Scotland or NI → R11 no. S2's "usually live outside" may read otherwise | SI≠guide |
| C20 | last E&W day 2026-09-26, resident in Scotland from 2026-09-27 | NO | — | — | — | R11: on or before QW₁ | SI |
| C21 | last E&W day 2026-09-27, resident in Scotland from 2026-09-28 | YES | £200 | NO | £200 | R11: 2026-09-28 > QW₁ → no | SI |
| C22 | not paid automatically, claimed 2027-03-31 | YES | £200 | NO | £200 | R12: claim on or before 31 March | guide |
| C23 | not paid automatically, claimed 2027-04-01 | NO | — | — | — | R12 | guide |
| C24 | sentenced, custody 2026-03-01, released 2026-09-27 | YES | £200 | NO | £200 | AR1: released during QW → not throughout (flag `ambiguous-source`) | SI |
| D01 | alone b. 1955, income £35,000.00 | YES | £200 | NO | £200 | not over £35,000 | guide |
| D02 | alone b. 1955, income £35,000.01 | YES | £200 | YES | £0 | over → whole payment recovered | guide |
| D03 | alone b. 1955, income £34,999.99 | YES | £200 | NO | £200 | not over | guide |
| D04 | couple no RB; P £40,000, partner £10,000 | YES | £100 | YES | £0 | 3(2); P's income alone counts | guide |
| D05 | couple no RB; P £30,000, partner £90,000 | YES | £100 | NO | £100 | partner's income does not count | guide |
| D06 | alone b. 1944, income £35,000.01 | YES | £300 | YES | £0 | 3(4); over → recovered | guide |

**Summary.**

- **Profiles.** There are 62: 13 in group A (S2 amount-table rows), 19 in group
  B (exclusions and combinations), 24 in group C (date boundaries, each with
  both sides) and 6 in group D (the income threshold with one penny either
  side).
- **Basis.** 38 are `guide` cases, 18 are `SI` cases and 6 are `SI≠guide`
  cases.
- **Flags.** 9 profiles carry a flag in `cases.json`, so 53 are unflagged.
  4 are flagged `ambiguous-source` (B10, B16, C11, C24); C11 is also `SI≠guide`.
- **Benefit list.** Each of the five relevant benefits decides the answer of
  at least one profile: income support B11, income-based JSA B12, state
  pension credit B01 and B04, income-related ESA B13, universal credit B14.
  B11 to B14 were added by the plan review (finding C), because deleting any
  of those four from the reference changed no key. Such a profile is
  hypothetical, since few people over pension age get these benefits, but the
  rule applies to it.
- **Review profiles.** B15 to B19 were added by the eligibility review. Under
  the old readings of R11 (no order) and R6 (both persons out of residential
  care), each of them has a different key, and no earlier profile did. B15
  is the review's own example. AR6 takes the later of two bounds, and each
  bound decides one profile alone: QW₀ decides B16, and the start of E&W
  residence decides B19.
- **Size.** The brief asked for about 40 profiles. The extra 22 come from
  covering both sides of every date boundary, every benefit on the list, and
  the two readings the review corrected.

**Independent check of the key.** [`reference.py`](reference.py) is a
stdlib-only reading written from S1–S4. It imports nothing from `ve` and was
not derived from any VE text. It computes the qualifying week from "the third
Monday in September", pensionable age from S4's tables, anniversaries under
both leap-day readings, and each rule in 4.1. Running
`uv run python usecases/eligibility/reference.py` at the plan commit printed
`qualifying week 2026-09-21 to 2026-09-27` and **53/53 agree with the hand key**.
After B11 to B14 were added, it printed **57/57**. Deleting any one of the five
relevant benefits from its list now changes at least one key. The review
corrected its R6 and R11 in the same way as the rules in 4.1. After B15 to B19
were added, it printed **62/62**. Restoring its old R11 changes the answers
for B15, B16 and B19, and restoring its old R6 changes them for B17 and B18.

**Limits of this independence.**

- The same author wrote the key, the reference and (next) the translation.
  Both the key and the reference encode the readings in 4.2.
- The `guide` cases are the part of the key that does not depend on this
  author's reading.
- The flagged cases isolate where a reading choice decides the answer.

## 6. Planned VE translation

**Route.** One `ve-units@1` environment on the quantity route. It uses the
profiles `order@0`, `relational-fol@0` and `time@0`, plus `documents@1` for
the staged fallback. Each profile becomes one entailment problem per question:
premises = rules + bridges + that profile's facts; conclusion = the question.
Nothing in the harness reads `key` fields. A test will strip them from
`cases.json` before building problems.

**Units.**

- `day`: the reserved record.
- `elapsed_day`: the reserved record.
- `gbp_penny`: `{"scale": "100", "display": {"kind": "money", "currency": "GBP", "input_symbol": "£"}}`.

**Vocabulary.**

- **Sorts.** `person` and `benefit`.
- **Object constants.**
  - `applicant` and `housemate`;
  - `state_pension`, `attendance_allowance`, `pension_credit`,
    `universal_credit`, `income_related_esa`, `income_support` and
    `income_based_jsa`.
- **Predicates.**
  - Facts: `partner_of`, `lives_with`, `paid_for_week(person, benefit)`,
    `relevant(benefit)`, `in_care_setting`, `inpatient`,
    `in_custody_under_sentence`, `ever_resident_ew`, `remains_resident_ew`,
    `moved_to_scotland_or_ni`, `claimed`, `paid_without_claim`.
  - Derived: `reached_pa`, `reached_80`, `resident_in_week`, `has_rb`,
    `in_residential_care`, `excluded`, `entitled`, `recovered`.
- **Integer constants, per role r ∈ {applicant, housemate}.**
  - `day`: `r_pa_date`, `r_eightieth`, `r_ew_from`, `r_ew_last_day`,
    `r_scot_ni_from`, `r_care_from`, `r_admitted`, `r_treatment_start`,
    `r_discharged`, `r_custody_from`, `r_release`, `r_claim_date`.
  - `elapsed_day`: `r_care_before_week` and `r_treatment_before_week`.
  - `gbp_penny`: `r_income`.
  - Applicant only, `gbp_penny`: `amount`, `recovered_amount` and `kept`.

**Why per-role constants.** W6a rejects integer binders (gated on numbers2).
So a rule cannot say "for every person p with birth date d". Each rule in 4.1 is
therefore instantiated for both roles, with a closure fact: "every person the
applicant lives with is the housemate". Quantifiers range over `person` and
`benefit` only. For example, R4 becomes
`has_rb(r) ⇔ ∃b. paid_for_week(r, b) ∧ relevant(b)`, together with each
profile's closed list of benefits paid to each role.

**Rule shapes** (annotated `ve-quantity@1` trees; literals via `["date", …]`
and `["decimal", "gbp_penny", …]`):

- **R2:** `reached_pa(r) ⇔ date_no_later(r_pa_date, 2026-09-27)`. The bridge
  fact is either an equality or a `date_no_later` bound (B2).
- **R3:** `resident_in_week(r) ⇔ ever_resident_ew(r) ∧ date_no_later(r_ew_from, 2026-09-27) ∧ (remains_resident_ew(r) ∨ ¬date_before(r_ew_last_day, 2026-09-21))`.
- **R5:** `in_care_setting(r) → elapsed_days(r_care_from, 2026-09-21, r_care_before_week)`,
  and `in_residential_care(r) ⇔ in_care_setting(r) ∧ r_care_before_week ≥ 84 elapsed days`.
  Every care stay in the profiles runs through QW.
- **R8:**
  - `inpatient(r) → shift_days(r_treatment_start, r_admitted, 1)`, the day
    after admission, by S3 reg. 2(5);
  - `inpatient(r) → elapsed_days(r_treatment_start, 2026-09-21, r_treatment_before_week)`;
  - excluded when `inpatient(r) ∧ date_no_later(r_treatment_start, 2026-09-21) ∧ date_no_later(2026-09-27, r_discharged) ∧ r_treatment_before_week > 364 elapsed days`.
- **R9 (AR1):** `in_custody_under_sentence(r) ∧ date_before(r_custody_from, 2026-09-21) ∧ date_after(r_release, 2026-09-27)`.
- **R11 (AR6):** `resident_in_week(r) ∧ moved_to_scotland_or_ni(r) ∧ date_no_later(r_ew_from, r_scot_ni_from) ∧ date_no_later(2026-09-21, r_scot_ni_from) ∧ date_no_later(r_scot_ni_from, 2026-09-27)`.
- **R12:** `¬paid_without_claim(r) ∧ ¬(claimed(r) ∧ date_no_later(r_claim_date, 2027-03-31))`.
- **R14–R15:** one implication per paragraph, each concluding `amount = £…`.
  - Every "subject to" is compiled into explicit negated guards; the norms
    and defaults layers are not on the quantity route.
  - In 3(5), "subject to paragraph (6)" cannot fire with a single housemate,
    because R6 makes (6)(b)(ii) and (5)(b) disjoint. No profile tests that
    precedence.
- **R16:**
  - `entitled(applicant) ∧ applicant_income > £35000.00 → recovered(applicant) ∧ recovered_amount = amount`;
  - `entitled(applicant) ∧ applicant_income ≤ £35000.00 → ¬recovered(applicant) ∧ recovered_amount = £0.00`;
  - `entitled(applicant) → kept = amount − recovered_amount`, using same-tag
    subtraction.
- **B1:** `shift_days(2026-09-27, 2026-09-21, 6)` is included as a checked
  premise about the literals.

**English.**

- **Atomic facts** use the W6a controlled wordings
  ([`ve/surface/time.py`](../../ve/surface/time.py)) and must round-trip, for
  example:
  - "The applicant's pensionable-age date is no later than 2018-12-05."
  - "The applicant's total income equals £35000.01."
  - "The elapsed duration from the applicant's care start date to 2026-09-21 equals the applicant's care days before the week."
- **Compound rules** (implications with quantities) have no W6a English
  wording. They are approved as annotated trees with a hand gloss, and
  counted as OPEN for English (O8).

**Feature map.**

| Part | VE feature needed | Status at plan time |
|---|---|---|
| Qualifying-week literals, R3, R9, R11, R12 | `day` literals; `date_no_later`, `date_before`, `date_after` | W6a, Lean-admitted |
| R5, R8 periods | `elapsed_day`, `elapsed_days`, `shift_days` | W6a |
| R2, B2 | `date_no_later` with a bound or an equality on a bridge date | W6a (the bridge itself is outside VE) |
| Amounts, threshold, Q4 | `gbp_penny` money literals, `<`, `≤`, `=`, same-tag subtraction | W6a |
| Relevant-benefit list, households | `relational-fol@0`: user sorts, ∃ over `benefit`, single-step object equality | order@0 tableau |
| Exceptions ("subject to", "does not apply") | ordinary connectives inside `ve-quantity@1` | order@0 tableau |
| Answers | `prove_quantity` → `ve-quantity-certificate@1`, replayed by Lean `ve_quantity` | W6a |
| Non-vacuity | Lean evaluation of all premises in one fixture model per profile | W6a |
| Staged fallback | `documents@1` quantity documents with `cite:` lemmas | W6a loop fix 2 |

## 7. What is expected to stay OPEN

These are decided now, before any run.

- **O1: the qualifying week from "third Monday in September".** Weekday
  arithmetic needs residues and integer binders (W6b `sunday`, gated on
  numbers2). QW enters as bridge B1.
- **O2: pensionable age and age 80 from birth dates.**
  - W6a date literals must lie between 1970-01-01 and 9999-12-31, and every
    birth date here is earlier. Probe P1 must show `DateRange`.
  - W6a has no month or year durations, so "66 years and 3 months" and
    "age 80" cannot be computed.
  - Both enter as bridges B2 and B3. As a result the birth-date boundaries
    (C01–C09) test VE's comparison against QW₁ but not the age arithmetic.
- **O3: legal classifications taken as facts.** These are "ordinarily
  resident", "partner" and "couple", "lives with" (mutual home, temporary
  absence), "care home" and "independent hospital", "free" in-patient
  treatment and the linking of stays, "under a sentence", "paid to" for joint
  universal credit (AR4), and reg. 5(1) automatic payment (a discretion).
- **O4: reg. 5(2) and polygamous households.** Not translated.
- **O5: two or more housemates.** This needs a third role instance of the
  rules. It is mechanical but outside the profiles, and the 3(5) versus 3(6)
  precedence goes untested.
- **O6: the income charge.** S2 is the only pinned basis. The statutory
  definition of "total income" and the charge's legal basis are not pinned,
  and income is supplied as a fact.
- **O7: Northern Ireland and Scotland schemes.** Out of scope (B09).
- **O8: compound rules have no controlled English.** Only atomic facts can be
  checked for round trips.
- **O9: proof-search incompleteness.** The order tableau is incomplete by
  design, and its budget is 10,000 steps. An exhausted or NotFound search is
  OPEN, never an answer.

**Predictions.**

- **Answers.** With the bridges, every one of the 189 questions should be
  answerable. The main risk is O9: about 30 biconditional rules per problem may
  exhaust the tableau budget.
- **Accuracy.** No disagreement is expected on unflagged profiles, since the
  translation follows 4.1 and 4.2. A disagreement is therefore evidence of a
  translation error, a VE fault, or an error in this key. Each is reported
  under its cause; the key is not quietly edited.

## 8. Run protocol (next stage)

**Stage 0 probes.** Expected results are recorded here.

| Probe | Input | Expected |
|---|---|---|
| P1 | `date_no_later(applicant_birth_date, ["date","1960-06-27"])` | rejected, `DateRange(1960-06-27)` |
| P2 | an implication mixing a user-sort atom with `date_no_later` and a `gbp_penny` comparison | admitted; if not, the whole translation is blocked and reported as a VE limitation |
| P3 | the three English facts in section 6; an English "If … then …" sentence over a date constant | facts parse uniquely and round-trip; the conditional is rejected |
| P4 | `£35,000.00` (thousands separator), `£35000.001` | rejected (separator outside the surface; `UnitPrecision`) |
| P5 | `elapsed_days` and `shift_days` on constants | admitted |
| P6 | A01 end to end | a certificate for `entitled(applicant)` and for `amount = £200.00`, accepted by Lean `ve_quantity` |

**Per profile and question:**

1. Build the premises from the profile fields, the bridge tables in 4.3, and
   the rules. Never read the key.
2. **Consistency.** Run `prove_quantity(premises, ⊥)`. A certificate means
   INCONSISTENT, which counts as a translation error for every question of the
   profile. Separately, in Lean, evaluate all premises in the fixture model
   built from the profile, where the derived predicates take the reference's
   values. If a premise is false in it, record a translation or key error.
3. **Q1.** Run `prove_quantity` on `entitled(applicant)` and on its negation.
   One certificate gives YES or NO; neither gives OPEN. Replay every
   certificate in Lean `ve_quantity` (certificate mode). A Python certificate
   that Lean does not accept counts as OPEN, and the rejection is reported as
   a VE fault.
4. **Q2.** Only after Q1 is certified YES. For each a ∈ {100, 150, 200, 300},
   try `amount = £a.00`. Exactly one certified value is the answer; none gives
   OPEN, and two or more count as an inconsistency (a translation error). After
   a certified NO, Q2 to Q4 are **not applicable** and are not attempted; after
   an OPEN Q1 they are OPEN. The harness decides this from VE's Q1 answer, never
   from the key. The claim that no amount follows from a NO is therefore never
   made, so it needs no countermodel.
5. **Q3 and Q4.** Try `recovered(applicant)` and its negation. For Q4, try
   `kept = £k` where k is the certified amount or £0.00.
6. **Fallback.** The trigger is simply that the single-shot search certified
   no answer for a question: neither polarity for Q1 or Q3, and no value for
   Q2 or Q4. `prove_quantity` returns `None` for every inconclusive search,
   whether the step budget, the depth limit or a stuck search caused it, so the
   trigger does not depend on the cause. For the report, the harness also
   records the status and step count of the underlying `prove_entailment`
   search. Then run the **staged** version, planned now: a `documents@1`
   quantity document with checked lemmas in this order:
   1. `reached_pa`, `reached_80`, `resident_in_week`, `has_rb` and
      `in_residential_care` per role;
   2. each exclusion;
   3. `entitled` per role;
   4. the amount.

   Staged results are reported in their own column and never merged into the
   single-shot figure.

**Mutation check** (does the case set catch translation errors?). Run each
mutated translation on all profiles. The profile that must change is given for
each.

| Mutant | Profile(s) that must change |
|---|---|
| M1: R8 "> 364" as "≥ 364" | C14 |
| M2: R8 counting the admission day | C14 |
| M3: R5 "≥ 84" as "> 84" | C10 |
| M4: R16 "> £35,000" as "≥" | D01 |
| M5: R2 "no later than" as "before" | C01 |
| M6: R15 age 80 strict | C04 |
| M7: R7 without "partner" | B02 |
| M8: R7 without the partner's pensionable age | B03 |
| M9: R9 without "under a sentence" | B06 |
| M10: R11 "before" for "on or before" | C20 |
| M11: R12 "before" 31 March | C22 |
| M12: R3 "every day" for "any day" | C17, C19 |
| M13: R16 counting the partner's income | D05 |
| M14: R14 without 3(3) | A08 |
| M15: R4 without income support | B11 |
| M16: R4 without income-based JSA | B12 |
| M17: R4 without state pension credit | B01, B04 |
| M18: R4 without income-related ESA | B13 |
| M19: R4 without universal credit | B14 |
| M20: R11 without the order of AR6 (the first run's reading) | B15, B16, B19 |
| M21: R11 without the QW₀ bound of AR6 | B16 |
| M22: R11 without the E&W-start bound of AR6 | B19 |
| M23: R6 also requiring the other person out of residential care (the first run's reading) | B17, B18 |

Kill rate = mutants killed / 23; 23/23 is expected. (M20 to M23 were added by
the eligibility review; the first run had M1 to M19.)

**Gates.** Every command runs in the foreground with
`PATH=~/.elan/bin:$PATH`:

- `lake build`;
- the new `tests/test_eligibility_wfp.py`;
- `uv run python usecases/eligibility/reference.py`;
- the W6a test files listed in `docs/W6A-STATUS.md`.

No model calls.

## 9. Metrics to report (`RESULTS.md`)

- **Accuracy.**
  - Strict, per profile: every scored question correct, x/62. OPEN counts as
    wrong.
  - Per question (section 3): Q1 x/62; Q2 x/48; Q3 x/48; Q4 x/48; total
    x/206.
  - The same figures on the 53 unflagged profiles, on the 38 `guide`
    profiles (official answers), and for each flagged profile individually.
- **Coverage.** Scored questions answered (certified YES/NO/amount) out of
  206, and precision = correct / answered, over the same 206.
- **Evidence.** Certificates produced, and certificates replayed by Lean
  (must equal the number produced). Also profiles whose premises are
  consistent, and non-vacuity models accepted by Lean.
- **Disagreements.** One row per disagreement with profile, question, key, VE
  answer, and cause: `translation error`, `VE limitation`, `VE fault`,
  `ambiguous source` or `key error`. For `key error`, give the corrected
  reasoning and the separate commit that changes the key.
- **OPEN.** Every OPEN answer with its reason (O1–O9 or a new one), and
  single-shot versus staged counts.
- **Probes and mutants.** Results of P1–P6, compared with section 8, and the
  mutation kill rate with any surviving mutant.
- **English.** Atomic fact sentences that round-trip out of all fact
  sentences, and the rules left without English (O8).

## 10. Files

| Path | Content |
|---|---|
| `PLAN.md` | this plan and the frozen key |
| `cases.json` | the 62 profiles with their `key` (same as section 5) |
| `reference.py` | the independent reference reading and key check |
| `source/` | the pinned raw files, extracted text, and `extract_text.py` |

Planned for the next stage:

- `environment.json`, the rules as annotated trees, and a problem builder that
  reads no keys;
- `run.py`, which writes `results.json`;
- `RESULTS.md`;
- `tests/test_eligibility_wfp.py`.
