# ENCODER-NOTES: cases_xfam.py (29 CFR 825.110)

`python3 -I check.py out/cases_xfam.py` → `OK: 35 cases, 8 probes, 0 unsupported`

## Counts
- Cases (scope "in", encoded): 35 (F001–F035), 100 questions
- Probes (scope "out"): 8 (F036–F043): airline crew (825.801), a worksite outside the U.S. (825.105(b)), covered employer (825.104), amount of leave, pay
- Unsupported: 0

## Conventions used
- C1 closed world: only stated-true facts are listed. Anything stated as not holding is left out: no USERRA or rehire agreement on the personal-travel and education breaks, and `practice` is absent where the employer "omits earlier employment…".
- C2 items:
  - One leave item `l1` per leave asked about.
  - One period per stated employment period. A period that runs past the leave's start is cut at the day before the leave starts. This is the only date I wrote that is not copied word for word from the facts, and it is what C2 requires.
  - Each USERRA break is also a `userra_abs` period item with the break's own dates (F012–F015).
  - One break item per stated break. `precedes` links each earlier period to each later break.
  - One block per stated hours figure, including 0-hour figures. The USERRA "would have worked" hours are `h_userra` blocks.
- C3:
  - Typed values: leave starts, the employee count on the notice day, block hours and dates.
  - No period states a number of weeks, so every period's weeks are bridged (`None`).
  - The 12-month window start, months and break lengths come from the bridge only.
- C4: the "can clearly demonstrate" judgment enters as `shows_below` (F018, F020); "cannot" leaves it absent.
- C5: `employee` and `covered` are true for every leave.
- Other facts:
  - `payroll` is on every employment period: the facts say the employee was continuously on the payroll, or on it for part of every week, with payroll kept during leave.
  - `casual` applies in F005–F011 and F034.
  - `REC` (`acct` and `acc_record`) applies wherever the employer keeps an accurate record.
  - `b_userra` is on F012–F015 and `b_rehire` on F011.

## Judgements (one line each)
- F010: `practice` true: the stated practice (count employment before personal-travel breaks of any length) covers this personal-travel break.
- F017, F018, F019, F020, F021: `acct` false: no accurate record is kept, and the facts say the stipulated actual hours are not the employer's evidence.
- F022: the compensation-agreement hours are not entered ((c)(1)); only the recorded actual hours are blocks.
- F026, F027: intermittent episodes under one notice are one leave item at the first episode (2026-01-01).
- F030: the leave item starts at the requested FMLA portion (2026-01-01), as the question asks; the absence from 2025-12-15 counts as payroll time in p1.
- F033: the earlier September notice and October leave are not an item; the count is the one on the December notice day (separate need).
- F034: `practice` true: the stated practice (count employment before education breaks of any length) covers the long break b2, which is an education break.
- F035: the leave item starts 2026-02-01, as the question asks; the count is the one on the 2025-12-01 notice day (the February episode is under that notice).
