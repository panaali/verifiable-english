# ENCODER NOTES: 14 CFR 61.23, cross-family set (questions-enc.jsonl)

`python3 -I check.py out/cases_xfam.py` -> `OK: 39 cases, 4 probes, 43 ids`

## Counts
- Cases: 39 (F001-F035, F037, F038, F040, F042)
- Probes: 4 (F036, F039, F041, F043)

## Conventions used
- C1 domain closure: each stated medical certificate is cert1 and was issued on an eligible application app1 (ISSUED); stated later applications are app2.
- C2 closed facts: a status the facts don't state is false. Statuses the facts say "must be decided" go in unknown: F037 `under_113i`, F038 `meets_316`.
- C5: an application's date, set only where two applications must be ordered (F024, F027, F035), is the examination date of the certificate issued on it. A later application gets its own stated date.
- C3 and C4 were not needed: required-crew status is stated outright in F013 and F017, and no case is a solo flight.
- Every date is transcribed as stated. Derived dates are left to bridge/bridges.py.

## Judgements (one per line)
- F008: a balloon is an aircraft, so `examiner_aircraft` is true alongside `examiner_gbsf`.
- F009: a glider is an aircraft, so `taking_test_aircraft` is true alongside `taking_test_gbsf`.
- F023: "rely on their U.S. driver's license" is read as `holds_dl`.
- F027: the pending application app2 is neither found eligible nor denied.
- F029: the failed medical restriction of the license sets `dl_med_complied` false. `dl_complied` (other restrictions, judicial orders) is true.
- F035: app2 is dated by its stated submission day (1 April 2027), not its denial day.
- F040: the pending application app1 is neither found eligible nor denied. The premise about part 67 findings is not encoded.
- F042: the flight is outside U.S. airspace, so `domestic_us` is false. No other fact states it.

## Probes
- F036: a foreign pilot licence and foreign medical certificate have no fact name.
- F039: a remote pilot certificate and unmanned aircraft have no fact name.
- F041: the special issuance authorization's own time limit has no fact name or date slot.
- F043: another country's medical rules have no fact name.
