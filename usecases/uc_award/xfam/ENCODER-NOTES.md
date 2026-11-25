# Encoder notes: cases_xfam.py

## Counts
- Award records: 40. That is 30 single-award cases plus 5 two-award cases (U017, U018, U019, U034, U035), each giving records a and b.
- Probes: 10 (U041-U050, all scope "out").
- Unsupported: 0.

## Conventions
- C1-C5 of encode.py apply. Closed world: a fact stated as not holding, or not stated at all, is absent.
- Anchor (C5): the first person the question names. U034b is anchored on cara, U035b on bob.
- Integers (C3): every person with a stated age or income is in the `adults` dict, children included. Their stated ages and 0.00 incomes are copied as written. Housing is the stated element amount, or 0.00 where the facts say the award has none.
- Child and qualifying-young-person statuses, and all other unary facts, are copied from the facts text. "X normally lives with Y", for a child or qualifying young person X, becomes lives(x, y). Couples between adults are recorded only as couple links; no lives link is added for them.
- Stated judgments (C4) are entered only where the facts state them in those words: same_household, temp_absent, abs_over6, abs_over1m, living_couple and main_judged. For example, abs_over1m is not inferred from dates, or from "exceeded six months" (U022, U023, U027, U030).
- Statements that a nomination or a Secretary of State determination was made become nom_any / nominated and sos_any / sos_det.
- No amount, element value, work allowance, deduction or answer was computed.

## Judgements
- U007: dan's care component of child disability payment at the highest rate (reg. 11(5) DACYP) is read as dis_lower (entitled to CDP) and dis_higher (reg. 24(2)(b)(i)).
- U007: eva, certified blind, is read as dis_higher (reg. 24(2)(b)(ii)). No benefit entitlement is stated, so she has no dis_lower.
- U010: cara's ADP daily living component at the standard rate is read as dis_lower only.
- U010: dan's PIP daily living component at the enhanced rate is read as dis_lower and dis_higher.
- U015: bob, a "severe conditions criteria claimant", is entered as pre2026 (the fact covers all three statuses).
- U016: ann, "terminally ill", is entered as pre2026 (the fact covers all three statuses).
- U020: lives(bob, ann) comes from "Ann and Bob ... normally live with each other" (Bob is a qualifying young person).
- U034a: same_household is set on all three people, from "are living in the same household".
- U034a: earlier(bob, ann). Bob's marriage to Ann (2018) came before his marriage to Cara (2020) and still subsists.
- U034b: same_household is set on all three people, from "are living in the same household".
- U034b: earlier(bob, ann), on the same reading as U034a.
- U035a: earlier(bob, ann), on the same reading as U034a.
- U035a: same_household is false for bob and cara (Ann is stated not to be in their household).
- U035b: earlier(bob, ann), on the same reading as U034a.
- U035b: temp_absent and abs_over6 stay on bob as stated (Bob is absent from Ann's household); ann has neither. same_household is false for ann (stated) and not stated for cara.
