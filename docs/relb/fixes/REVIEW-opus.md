1. **A** · `tests/test_relb_fixes.py:11`, `:362-373`, `:401-405`. The module docstring says "Each test fails on main before this change". That is not true for seven test cases:
   - All six cases of `test_claim_records_the_guide_does_not_decide_are_refused` pass on main.
   - `test_sentence_start_outside_a_sentence_is_refused` passes on main.

   Why: on main, `RECORD_FIELDS` makes `claim.automatic` required and allows only `claimed_on`, and custody has no optional field. So every one of these records already raises `ValueError` at `check_fields` ("fields … expected …"). That is a missing or unknown field, not the check the test names.

   On the branch these tests still only ask for some `ValueError`. Suppose `check_claim` dropped one of its branches, for example "a payment day without a payment". An unrelated `ValueError` from somewhere else would still pass the test, so it does not pin the refusal it describes.

   What to do: add `pytest.raises(ValueError, match=...)` on each `check_claim` and sentence-start message ("a payment day without a payment", "on no guide list and must_claim not said", "not on the guide's list", "a sentence start needs a sentence within the custody", and so on). Also correct the docstring: these cases are refused on main, for a different reason.

2. **B** · `tests/test_eligibility_wfp.py:304-309`. The field-reach test now accepts any `ValueError` for any `claim.*`, `custody.*` or `benefits` perturbation on any profile.
   - That would hide a real regression: an old profile's claim or custody field that is wrongly refused, or that no longer reaches a fact.
   - `claim.must_claim` (C29) and `claim.other_benefits` (C32) are now only ever "checked" through a refusal. `_perturbed` adds `"pension_credit"` to `other_benefits`, which is refused as not on the list. Neither field is ever shown to change a fact.

   What to do: list the expected refusals by (case, role, path), for example {(C29, must_claim), (C29, benefits), (C30/C31, automatic), (C32, other_benefits), (C33, sentenced)}, and assert that any other refusal fails. Add one perturbation that swaps a PIP entry for another listed benefit, so `other_benefits` is shown to reach a fact.

3. **B** · `translation.py` `FACT_PREDICATES["paid_without_claim"]` (patch :999). The new gloss reads: "The person is paid a winter fuel payment without a claim (S1 reg. 5(1)), on the unclaimed payment date."
   - On C30 the predicate is true with a payment date of 2027-04-01, which by the branch's own reading is not a reg. 5(1) payment. Reg. 5(1) says "The Secretary of State may, on or before the 31st March following the qualifying week, pay…".
   - So the gloss says reg. 5(1), while R12 then has to add the 31 March bound, as if the predicate did not already mean a 5(1) payment.

   What to do: drop "(S1 reg. 5(1))" from the gloss, for example "is paid a winter fuel payment without a claim, on the unclaimed payment date". Leave it to R12 to say which of those payments count under reg. 4(6)(a).

4. **B** · `tests/test_eligibility_wfp.py:212-235` (no new rows). Each earlier fix (findings A to C, the recheck, the R7 recheck) has a reference-side check: putting the old reading back into `reference.py` changes exactly the profiles added for it. relb-fixes adds none, so M33 and M34 are checked on the translation only, and only on their named profile (`test_each_mutant_changes_its_profiles` checks the named profiles only).

   What to do: add three rows:
   - `reg51_paid` without the date bound → {C30}
   - `excluded_custody` with `c["from"]` → {C33}
   - `paid_without_claim` as `claim.get("automatic")` → {C28, C32}. With `automatic` absent this gives None. `reference.excluded_no_claim` then sees no claim and excludes both, so they turn NO and no earlier profile changes.

5. **B** · `translation.py` role_facts, the undated-payment branch (patch :1140-1142), and `explain.py:735`. Two different assumptions both get the kind "assumption O3":
   - an undated payment taken to be made by 31 March;
   - the guide's list deciding who is paid without a claim.

   This also applies to every old profile with `automatic: true`, so every default profile's explanation now lists the "undated_payment" assumption (see DEMO.md).

   For a stated `automatic: true` meaning "paid by virtue of reg. 5(1)", the bound follows from reg. 5(1) itself ("on or before the 31st March"). For an O3 profile it is an assumption, which S2:105 supports: "Most payments are made automatically in November or December".

   What to do: give the undated bound its own label, or say in the README and the assumption text that it is entailed for a stated reg. 5(1) payment and assumed only under O3. Cite S2:105 for the O3 case.

6. **B** · `run.py` `GUIDE` (patch :885-887), and README "The 41 guide-answered profiles are the part of the key that does not depend on this author's reading". The new keys are right, but this claim does not hold for all of them:
   - C28 and C32 count as `guide` profiles. Their SI answer depends on the author's encoding rule O3, that "do not need to claim" (S2:75) means "a payment has been made by virtue of regulation 5(1)" (S1:92).
   - The guide's own answer is YES, so the keys are right. But in the SI reading the step from "no need to claim" to "paid under 5(1)" is the author's assumption.

   What to do: say this in the README sentence and in PLAN.md section 5, or mark C28 and C32 as resting on assumption O3.

7. **B** · `RERUN.md:16-19`. The re-run reports certificates and documents only. The model-premise check that `run.py` applies to `cases.json` profiles is not run on the 40 encoded profiles. It could not be as things stand: `run.py` `fixture_model` uses `reference.pensionable_age_dates`, which still raises `NotImplementedError` for Sch. 4 table 2 births (1953-12-06) and for births from 1977. Three bridge keys in the re-run (1953-12-06, 1977-04-06, 1978-04-06) fall there.
   - So in the re-run, nothing shows that each profile's facts are consistent.
   - The reference bounds that FAULTS.md "Take first" 1 suggested were not added.

   What to do: say in RERUN.md that no model check was run, or add the reference bounds. Also note that the re-run's 40 profiles exercise only the F1/F2/F7 changes, not O3, F8 or F3: W034 is still entered as the sentenced part only, and W005 has no payment date.

8. **B** · `tests/test_relb_fixes.py:255-262`. The sex test compares with reference.py only for births before 6 April 1950. Two groups are covered only by a key or two each:
   - men born 6 Apr 1950 to 5 Dec 1953 (rule (1), 65): two keys;
   - women in table 1 (6 Apr 1950 to 5 Dec 1953): the single key 1950-04-06 → 2010-05-06, and `run.py:313` takes their fixture day from `T.age_bounds` itself, which is not independent.

   What to do: run the men's loop to 5 Dec 1953. For table 1 women, either check against an independent table or say in the docstring that they are covered only by the one key.

9. **C** · README relb-fixes "Ages" and RERUN.md:37-38. Be explicit that `sex` cannot change any Q1 to Q4 answer for winter 2026/27. Everyone born before 6 December 1953 reached pensionable age by 5 December 2018 whatever their sex (reference.py:62-66), and Sch. 4 does not depend on sex after that date. The fix makes the bridge exact; it does not change an answer.

10. **C** · `translation.py` `check_claim`. A person on no list with `must_claim` false is refused. S2:88 ("If you do not get any of these, you need to claim if either of the following apply") arguably implies that someone who had the payment before and has not deferred does not need to claim. Refusing is defensible, since the guide does not say so in terms. Add one sentence in the README saying the contrapositive was not taken.

11. **C** · `translation.py` `guide_no_claim`. Item lines are only checked to be a short name without " if ". A planted extra benefit such as "Housing Benefit" in place of an item is accepted silently as an "other" benefit. Pin the 12 item lines word for word, as is already done for the lead-in and S2:88-90.

12. **C** · manage-agents FAULTS.md:218 says "another benefit of S2:79-87", but S2:79 is Attendance Allowance, which is one of the constants. The other benefits are S2:80-82 and S2:84-87; make it say that.

Points checked and found right:
- **R12.** It is faithful to S1:90-92 and 5(1).
- **R9.** It is faithful with `sentence_from`, on reg. 4(2) "throughout the qualifying week, P is— … (c) detained in custody under a sentence imposed by a court". An unsentenced custody gets no sentence-start fact, and R9 still needs `under_sentence`.
- **Sch. 4 sex rules.** Rule (1) gives a man born before 6 Dec 1953 pensionable age at 65, and rule (2) a woman born before 6 Apr 1950 at 60. The 21 keys match the schedule.
- **Keys for C28 to C33.** All six are right by the source: C28 YES £200, C29 NO, C30 NO, C31 YES £200, C32 YES £200, C33 YES £200.
- **Mutants.** M33 kills C30 and M34 kills C33.
- **Regressions.** None for the old profiles. Each has `automatic` stated, so `paid_without_claim` is a stated fact as before. The undated bound comes out true for them, and `sentence_from` equals `custody_from` whenever a custody is sentenced.
- **Contradictory profiles.** No path found. The new facts are all `date_on` or `date_no_later` on fresh numbers, and records that conflict are refused.
- **Counts.** README and PLAN.md agree: 86/67/19, 287 scored answers, 41/39/6, 140/140, 244/244, 354 documents. RERUN.md's 132 documents = 109 + 23.
- **Not re-reviewed:** `folded-pieces.patch` (the pieces folded in from the two earlier branches) was not reviewed line by line; I read `pensionable_age.py` only as it stands at the commit.

VERDICT: CHANGES
