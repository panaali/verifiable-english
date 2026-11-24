# ENCODER-NOTES: cases_xfam.py

`python3 -I check.py out/cases_xfam.py` → `OK: 35 cases, 5 probes, 0 unsupported`

## Counts
- Cases (in scope, encoded): 35 (N001–N035)
- Probes (out of scope): 5. N036 (s. 120 FWC reduction), N037 (s. 121(4)–(7) small business in liquidation), N038 (notice given by the employee under an award), N039 (small business status to be decided from the headcount; not stated), N040 (State law, not a national system employer)
- Unsupported: 0

## Conventions used
- C1 closed world: only facts the case states as true are listed. Facts stated as never holding (e.g. "not an apprentice", "not small business") are left out.
- C2: service at notice / end of notice day / termination, casual period, days, clock times and weekly rates are copied as stated. Age is never typed: it comes from DOB through bridge/age.py.
- C3: stated judgments enter as stated. `turnover` is true only in N029. `avoid` is true in N024 and N026 and false in N023 (stated "was not to avoid").
- C4: "immediately before termination and on termination" service is entered as the termination service (`ncy_trm`/`ncd_trm`). "No periods of casual employment" is entered as casual (0, 0).
- Clock times: 17:00 = 1020 minutes. Rates are copied as AUD decimal strings (e.g. "1010.00").
- STD (`written_notice`, `emp_init`, `not_required`) is used wherever the facts state written notice and a termination because the job is no longer required by anyone. N020 and N022 instead list only the facts they state.
- HOURS (`same_hours`) is used in every case: each states 35 ordinary hours each week at the full weekly rate, with no other hours.
- Q3 form: "least payment in lieu of notice" → `piln` (N001-3, N014-3, N030-3). "Amount of redundancy pay" → `red`.

## Judgements (one line each)
- N002: casual period stated as "a single period of 1 calendar year" entered as 1 year 0 days.
- N020: "initiates the termination solely because of its bankruptcy" read as `emp_init` and `insolv` (job still required, so `not_required` is absent).
- N025: casual period stated as "a single period of 2 calendar years" entered as 2 years 0 days.
- N026: "his employment lasts for that arrangement only" read as `tr_limited`.
- N027: "repairing buildings" read as `bci_conn` (with `bci`, both stated).
- N028: "working in the meat industry" also read as `meat_conn` (he is not a weekly hire employee).
