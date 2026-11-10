# cmp-s3a-cfr-3: user-visible deltas

One delta: an `ok` row of the `clauses-elaborate` mode gains two fields. No Python relay reads this mode yet (that is
cmp-s3-cfr-1b), so no released answer used it. No existing field changes value: `plained`, `clause_slot` and every
error text are byte for byte the base build's. The negative test compares them with the answers saved at the base
commit 3395d655 (base-answers.json, written by base_answers_probe.py). So the row the DRI signed ahead for a changed
existing answer (reviews/dri-decisions-20261109-lp0801.md item 1) is not used. Still, the negative test checks its
condition: the only values that differ are the two added fields, at spec :207/K4's value.

| Delta | Detail | Evidence (negative tests) | Ruling |
|---|---|---|---|
| `clauses-elaborate` `ok` rows carry `elided_bytes` and `unit_elided_bytes` | `elided_bytes` is the document total of spec 6 (:271): the sum of `b - a` over every structured line's elided spans, as 4.1 step 5 (:207) computes it, from the decoded document. `unit_elided_bytes` is one count per unit of the request's `document`, in document order, with 0 printed (6, 9.3 :602). Both are typed (`common.json#/$defs/nat`). The list is bound to the request with `x-length: "/document"`. Nothing is removed or renamed. | `test_right_clauses_k4_product_elided_bytes`: K4 through the route reports 10, with unit list `[10]`; with no span, 0 and `[0]`; two units give `[10, 26]` and 36; two overlapping elisions are refused (`ClauseSpan`). `test_right_clauses_existing_answers_unchanged`: on K1 and the 22 K fixtures (23 saved answers), the answer without the two fields equals the saved base answer byte for byte. Errors are unchanged and gain nothing. The two fields are K4's 10, and 0 elsewhere. It fails on seeded bugs S1 (K4's value becomes 11) and S4 (an existing field changes); see REPORT "Seeded bugs". Goldens: the schema is regenerated, and K1's exact answer and the schema seed of test_lean_service.py are updated. Binding: `tools/relay_mutation_gate.py --route service:clauses-elaborate` gives 597 mutants and 0 failures. | R3 (added information; DRI-RULINGS.md) |
