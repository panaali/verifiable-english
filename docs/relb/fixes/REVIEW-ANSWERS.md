# relb-fixes: answers to the Opus review (docs/relb/fixes/REVIEW-opus.md, verdict CHANGES)

Reviewer: Opus 5.5 on account saeedi.danial (Read/Grep/Glob only), reviewing ffcf506834. Answers are in the next commit.

| # | grade | answer |
|---|---|---|
| 1 | A | FIXED. Each refusal test is pinned to its own message (`pytest.raises(ValueError, match=...)`, 7 cases); the module docstring now says the refusal tests also pass on main for another reason, and that only the behaviour tests fail there. On a base copy (main + the folded pieces) 29 of 30 tests now fail; the one that passes, test_no_hand_tables_left, fails on main (the tables were removed by the folded cutoffs piece). |
| 2 | B | FIXED. test_every_profile_field_reaches_a_fact lists the six expected refusals by (case, role, path) (RELB_FIXES_REFUSALS) and asserts the refused set equals it; any other refusal fails. New test_other_benefits_reach_a_fact shows `claim.other_benefits` and `must_claim` decide the paid-without-claim fact. |
| 3 | B | FIXED. The paid_without_claim legend no longer cites reg. 5(1): "The person is paid a winter fuel payment without a claim, on the unclaimed payment date."; R12 says which payments count. |
| 4 | B | FIXED. Three reference-side rows in test_review_profiles_decide_the_corrected_readings: reg51_paid without the date bound -> {C30}; excluded_custody with the custody start -> {C33}; paid_without_claim only as stated -> {C28, C32}; each changes exactly those profiles. |
| 5 | B | FIXED. The undated bound has its own label, "assumption F8", apart from "assumption O3" (the guide's list); explain.py prints them as two assumptions, the undated one citing S2:105 ("Most payments are made automatically in November or December"). It is printed for every profile with an undated payment, because each such answer rests on it. |
| 6 | B | FIXED (said). README and PLAN.md section 5 say C28 and C32 reach the guide's answer through encoding rule O3, the author's reading of "do not need to claim" as a reg. 5(1) payment. |
| 7 | B | FIXED (said). RERUN.md says the re-run exercises F1, F2 and F7 only (no encoded profile uses the new claim or custody fields), and that no fixture-model check was run on the 40 profiles (reference.py has no table 2 or post-1977 working; three keys fall there). The reference bounds of FAULTS.md take-first 1 were not added: reference.py stays the earlier independent reading; listed in FAULTS.md. |
| 8 | B | FIXED. The sex test runs men to 5 Dec 1953 (rule (1)); its docstring says table 1 women have no independent working here (one key, and tests/test_spare_ages_dates.py's reading of the table). |
| 9 | C | DONE. README: `sex` makes the dates exact and cannot change a Q1-Q4 answer for this winter. |
| 10 | C | DONE. README: the contrapositive of S2:88 is not taken; such a person is refused. explain.py's assumption says the same. |
| 11 | C | DONE. The twelve item lines S2:76-87 are pinned word for word; a planted "Housing Benefit" in place of an item is refused (test). |
| 12 | C | DONE. manage-agents FAULTS.md: "another benefit of the list (S2:80-82, S2:84-87)". |
