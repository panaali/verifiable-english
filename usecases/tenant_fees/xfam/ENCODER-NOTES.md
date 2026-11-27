# Encoder notes: Tenant Fees Act 2019, cross-family question set

`python3 -I check.py out/cases_xfam.py out/inputs.jsonl` -> `OK: 40 cases, 0 unsupported, 10 probes`.

## Counts
- Cases in CASES: 40 (T001-T040, every in-scope case)
- UNSUPPORTED: 0
- PROBES: 10 (T041-T050, all scope "out"; their qids are in PROBE_QIDS)
- Bridge inputs (out/inputs.jsonl): 5 late-rent items (T014 late; T015 hint, mint; T016 mint, hint)

## Conventions used
- encode.py C1-C4 as stated: closed world over FACTS; links exactly as listed; integer constants only where stated;
  stated judgements (STATED) set only where the facts state them.
- Amounts are GBP strings with two decimals and dates are ISO, copied from the facts. Deadlines, caps, week's rent,
  repayment amounts and dates are never typed: the build derives them.
- The template bundles are used as given: HD for a holding deposit (plus to_landlord or to_agent), SEC for a tenancy
  deposit, PAY_T for a payment required of the tenant. DL / DL_AGENT is a late-rent default charge under a tenancy term.
- annual_rent is entered in every in-scope case (it is stated in each one).
- Late-rent caps come only from the bridge script: one input line per late-rent item, giving the stated instalment, due
  date, part payments and base rates.
- Question forms: "Is X a permitted payment?" -> permitted; "Does section 1 allow ..." -> s1; Q2 -> amount; Q3 -> repay.

## Judgements (one line each)
- T005 the electricity and communication contracts are read as contracts for the provision of a service (s. 1(3)); the renewal condition as s. 1(6)(a).
- T006 the continuance condition on the loan is read as s. 1(6)(a).
- T007 the storage term is read as s. 1(6)(d) (other circumstances); the painting term as s. 1(6)(b) (an act of the tenant), not a default.
- T008 the renewal condition is read as s. 1(6)(a); Omar is stated only to act for North Council, so payer_for_tenant is not set for him.
- T009 the form delivery, the insurance contract and the attendance are entered as the other requirements each option is linked to; the renewal conditions are read as s. 1(6)(a).
- T013 no base rate is stated, so no bridge input (late-rent cap) is given.
- T018 the council-tax and administration terms are read as s. 1(6)(d); the assignment charge as s. 1(6)(a).
- T024 Nora (acting on Leo's behalf) is the payer; Leo's consent is not the payer's consent, so applied_with_consent is not set.
- T027 the stated employment end date that differs from the actual one is read as false or misleading information.
- T028 the forged employer letter is read as false or misleading information (the stated entitlement concerns the action of supplying it).
- T036 the fee condition on the grant is read as s. 1(6)(a), imposed on Nora (guarantor, a relevant person) in relation to the deposit's proposed tenancy.
- T037 Mira's stated behaviour of 3 March 2025 (towards Nora, acting for Leo) is entered as unreasonable_behaviour, read as before the deadline.
- T039 the 1 March deposit's notification day is the first withdrawal (5 March 2025); the 8 March deposit's is the withdrawal after its receipt (10 March 2025).
