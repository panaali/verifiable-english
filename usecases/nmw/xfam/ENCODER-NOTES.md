# Encoder notes: cases_xfam.py

`python3 -I check.py out/cases_xfam.py` prints `OK: 36 records, 0 unsupported, 6 probes`.

## Counts
- **Records:** 36. That is 35 in-scope cases, N001-N035. N013 asks about two periods, so it has two records, N013.1 (June) and N013.2 (July).
- **Probes:** 6 (N036-N041), covering 8 qids.
- **Unsupported:** 0. The record format can state every in-scope question.

## Conventions used
- encode.py C1-C5 as written:
  - closed world over FACTS;
  - `unknown` only for a fact the question does not settle without arithmetic;
  - the bridge alone supplies the age and within-12-months facts (from dob/start/prior_start);
  - the following period comes from the calendar.
- Monthly cases use the template's JUNE/JULY constants and CAL_MONTH. The weekly case N016 uses the next Monday-Sunday week (CAL_WEEK).
- `w` gets `nlw` only where the facts say the worker qualifies. Apprenticeship and arrangement facts are added only as stated.
- Basic pay for work done in the period asked about uses `PAY` (`emp_payment`, `as_prp`), with the stated amount and payment day.
- Item names:
  - Accommodation is the single item `acc`, with the entitled amount as `amt_acc` and the deduction or payment day as `paid_acc`.
  - Stated runs of days are named `run1`... and linked by `run_of`.
- Deductions and worker payments get `as_prp` only where the facts tie them to June, for example "for that June accommodation".
- `due_contract` is stated only where reg. 10(c) is in play (N017).
- Amounts, dates and day counts are copied exactly as stated. No age, total, rate or answer is computed.

## Judgements (one line each)
- N005: the apprenticeship agreement within ASCLA 2009 s. 32 is stated as `contract_appr`.
- N007: `start` is the move to Bob Ltd (1 May 2026); `prior_start` is the Green Farm commencement (1 May 2025).
- N008, N010, N012: arrangements made by the Secretary of State under ETA 1973 s. 2, so every `made_*` fact whose wording covers that maker is stated.
- N009: "engaged under that agreement in England" is stated as `eng_england`.
- N013.1: p3 (pay for July work) is as respects a later period, so it has no `as_*` fact.
- N013.2: p1 and p2 (pay for June work) are as respects the period immediately before July, so `as_prev`.
- N017: the £300.00 settlement is split into its two stated parts: £271.00 contractual (`x_court`, `due_contract`) and £29.00 not (`x_court`).
- N017: the advance of wages for July work has no `as_prp`. The other June items do.
- N017: `monthend` is not stated, and every payment is on the termination day.
- N018: the bicycle and the voucher are employer items (`emp_payment`, value as `amt`), because reg. 10(f) and (g) list them among payments.
- N019: the night-pay excess over the £12.00 lowest rate is not stated as its own amount, so `part_excluded`.
- N020: the s. 338 travel payment also meets Ann's employment travel expenditure, so `expenditure` as well.
- N021: the unpaid charge due on 30 June is a payment due from the worker (`wpay_emp`); its day is the due day.
- N023: the gloves and apron were bought from Bob Ltd as required for the employment, so `purchase_emp` and `expenditure`.
- N024: the £40.00 tools paid to Bob Ltd as required: `purchase_emp`, `purchase_required`.
- N024: Bob Ltd intended on 21 June to meet the training expenditure, so `met_by_emp`.
- N025: 14 June 2026 (accommodation only from 2 pm) is a run of 1 day, not whole.
- N028: a county council in England is a local housing authority (the words of reg. 14(3)).
- N032: the private tenancies are not accommodation provided by the employer, so there is no `acc` item and no runs.
- N032: Green County Council and River Housing are read as `payee_lha` (the words of reg. 14(3)).
- N033: River Housing, a private registered provider of social housing, is a registered social landlord.
- N034, N035: `c15b` is left unknown, because whether the absence pay is not less than the entitlement needs arithmetic.
- N034, N035: `c15c` comes from the stated 120 against 160 hours, with the difference entirely due to the absence.

## Calendar readings
- All monthly records: the following period is the next calendar month (CAL_MONTH).
- N014: the record was given on 27 July 2026 (July period) and p2 was paid on 10 August 2026 (the period after), so `rec_paid_window`.
- N015: the record was given on 26 July 2026 (July period) and p2 was paid on 10 August 2026 (the period after), so `rec_paid_window`.
- N016: the following period is 15-21 June 2026, the next Monday-Sunday week. It is read from the weekly pattern even though the contract terminated on 14 June.

## Probes
- N036: the period begins 1 March 2026, before the window in which the supplied text is in force.
- N037: the Part 5 hours of work are not supplied.
- N038: volunteer; worker status is not stated.
- N039: an enforcement penalty.
- N040: neither the age nor the national living wage status is supplied.
- N041: statutory arrears under s. 17 of the Act.
