# rights-cfr-4 delta: a right whose act is a declared open term is OPEN (`lean/VE/Rights/Run.lean`)

Base: `git merge-base HEAD main` (268829b1a). Spec: docs/spec/rights.md 7.2 ("one with an open standard in a guard,
act, limitation or condition is OPEN"). DRI decision: reviews/dri-decisions-20261109-lp0801.md item 1 (in
manage-agents), which signs ahead the CHECKED -> OPEN rows of this item "only for units whose act is a declared open
term", and the restated `nodeOpen_eq` (task file prompts/task-rights-cfr-4.txt, deliverable 2).

Only Lean product code changes (`nodeOpen`, one line of its body, and `nodeOpen_eq`'s statement). No Python or Rust
product file changes; Python relays Lean's `unit_open` as before.

## Who can move

`unitOpen` reads `nodeOpen` with the names of `unitStatuses`: the declared open terms, rights' generated names
(`rights__lim__*`, `rights__cond__*`, `rights__bar__*`) and the soft decision names (`soft__*`). An authored
predicate can never be one of the generated names: `InvalidInput: author predicate <p> begins with rights__`
(lean/VE/Rights/Correlate.lean:372) and `InvalidInput: invalid soft name <p>` (lean/VE/SoftNorms/Soften.lean:620,
lean/VE/SoftNorms/Once.lean:57). So the act scan opens a unit only when its act predicate is a declared open term:
exactly the units the DRI's row covers. No existing fixture holds such a unit (REPORT.md, "Fixtures that move").

## User-visible deltas

| # | Delta | Where | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | A `right` unit, or a `norm` unit of a rights document, whose act predicate is a declared open term moves from CHECKED to OPEN. This shows in its unit status, in `coverage.bytes_by_status` of `ve document check`, and in `unit_open` of `rights-elaborate`. It claims less. With it, `VE.Rights.Run.nodeOpen_eq` is restated to the new body: the disjunct `openNames.contains N.pred` is added (lean/statements.txt) and proved, and its docstring no longer calls the scan byte-neutral. Task rights-cfr-4 deliverable 2: "`nodeOpen_eq` ... restated to the new body and proved: this is the DRI-signed change (item 1 of the decision file above), not a new statement". | `ve document check` and the `document` and `rights-elaborate` service modes; lean/VE/Rights/Run.lean | tests/test_rights_open_act_is_open.py::test_rights_open_act_is_open (the condition test; fails on main, see REPORT.md), ::test_rights_open_act_reads_each_rights_own_act, ::test_rights_document_norm_unit_with_open_act_is_open; the negative test ::test_rights_closed_act_stays_checked (fails on seeded m3 and m4); `#guard`s in lean/VE/Rights/OpenActExamples.lean; the Lean build (the proof) | SIGNED by the DRI 2026-11-09, reviews/dri-decisions-20261109-lp0801.md item 1 (CHECKED to OPEN only for units whose act is a declared open term; the restatement is that change, task rights-cfr-4 deliverable 2); condition test tests/test_rights_open_act_is_open.py::test_rights_open_act_is_open; negative test tests/test_rights_open_act_is_open.py::test_rights_closed_act_stays_checked |
| 2 | Trusted Lean growth: lean/VE/Rights/Run.lean TRUST-ROW-PENDING | lean/VE/Rights/Run.lean | `#guard`s at lean/VE/Rights/OpenActExamples.lean:31-38; 4 seeded bugs, all killed ([mutants.json](mutants.json)); trust mutants ([trust-mutants.json](trust-mutants.json)) | R16 (DRI-RULINGS.md) |
