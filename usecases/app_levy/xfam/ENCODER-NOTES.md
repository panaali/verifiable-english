# Encoder notes: cases_xfam.py (FA 2016 ss. 99-101, apprenticeship levy)

## Counts
- Cases in questions-enc.jsonl: 39 (the brief said 43; the file holds 39). In scope: 35 (L001-L035). Out of scope: 4.
- Records: 35 (one per case; every case is in the tax year 2026-27, so no case needed a record per year).
- Probes: 4 (L036 charity; L037 s. 103 applies; L038 s. 100(4) continental-shelf certificate; L039 a one-month period).
- Unsupported: 0.
- `python3 -I check.py out/cases_xfam.py` -> `OK: 35 records, 4 probes, 0 unsupported`.

## Conventions used
- C1 closed world. Only stated true facts are listed. Facts stated as not holding (no notice, no return, an action not taken) are simply left out.
- C3: `co` for a company within CTA 2010 s. 1121(1), `llp` for an LLP (L025 Alma), `ind` for an individual employer.
- C4: one earnings item per earner, with the stated amount. "Incurs a liability" (including a GBP 0 liability) -> `liab`. "Would incur but for s. 6(1)(b)" -> `butfor`. "Neither" -> sec only.
- C5: one group `g` for the companies stated as connected at 00:00 on 6 April 2026. A company stated as not connected is in no group.
- C6:
  - The determination and any alteration are encoded as stated (det/alt).
  - Returns made on the entitled basis use ret, which sets ret9 + aware.
  - Written notices are notified8 / notified13, and the remedial action not taken is not_taken8 / not_taken13.
  - Amounts paid and due are paid_/due_ as stated. `dues_stated:g` is set where a group's amounts due are stated.
  - `noreturns:g` is set where the facts say the group made no return.
- C7: no case states the half-up convention, and no case states a s. 101(12) rounding. So halfup and rnd_* are never set.

## Judgements (one line each)
- L028: the members' 1 February 2027 agreement "instead to assign" is read as an alteration of the determination.
- L030: HMRC is aware of the returns at the assessment time. It knows from 2 March 2027, which is before 5 April 2027 (date compared).
- L031: HMRC is aware of the returns at the assessment time (same date comparison as L030).
- L031: the remedial action was taken on 10 March 2027, inside the 2-16 March 2027 period (date compared), so not_taken8 is left out. The corrections are not returns, so the returns' amounts stand.
- L032: HMRC is aware of the returns at the assessment time (same date comparison as L030).
- L032: the remedial action was not taken within the notice period. The period ends 16 March 2027, before the assessment time, and no action was taken up to then.
- L033: HMRC is aware of the returns at the assessment time (same date comparison as L030).
- L033: the remedial action was not taken within the notice period (same as L032).
- L033: HMRC's stated s. 101(7) roundings (Alma 2,142.86 up, Bea 12,857.14 down) are not encoded. The vocabulary's rnd_* facts cover only s. 101(12) shares.
- L034: the amounts paid and due and payable at 2 March 2027 (stated as used in the notice decision) are taken as s. 101(13)(a)'s amounts.
- L034: the remedial action was not taken within the notice period (same as L032).
- L035: `insufficient:g` is set. Alma's only return sets out GBP 0, says nothing about Bea or Cora, and the determination was not communicated. This is read as returns that do not let HMRC determine how the whole GBP 15,000 is to be used (s. 101(13)(b)).
- L035: the amounts paid and due and payable at 2 March 2027 are taken as s. 101(13)(a)'s amounts.
- L035: HMRC is aware of Alma's return, because it knows the return facts on 2 March 2027.
- L035: the remedial action was not taken within the notice period (same as L032).
