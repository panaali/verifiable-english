# rights-cfr-4 delta: a right whose act is a declared open term is OPEN (`lean/VE/Rights/Run.lean`)

Base: `git merge-base HEAD main` (268829b1a). Spec: docs/spec/rights.md 7.2 ("one with an open standard in a guard,
act, limitation or condition is OPEN"). DRI decision: reviews/dri-decisions-20261109-lp0801.md item 1 (in
manage-agents), which signs ahead the CHECKED -> OPEN rows of this item "only for units whose act is a declared open
term", and the restated `nodeOpen_eq` (task file prompts/task-rights-cfr-4.txt, deliverable 2).

Only Lean product code changes (`nodeOpen`, one line of its body, and `nodeOpen_eq`'s statement). No Python or Rust
product file changes; Python relays Lean's `unit_open` as before.

## Who can move

`unitOpen` reads `nodeOpen` with the names of `unitStatuses`: the declared open terms, rights' generated names
(`rights__lim__*`, `rights__cond__*`, `rights__aimed__*`) and the soft decision names (`soft__*`). An authored
predicate can never be one of the generated names: `InvalidInput: author predicate <p> begins with rights__`
(lean/VE/Rights/Correlate.lean:372) and `InvalidInput: invalid soft name <p>` (lean/VE/SoftNorms/Soften.lean:620,
lean/VE/SoftNorms/Once.lean:57). So the act scan opens a unit only when its act predicate is a declared open term:
exactly the units the DRI's row covers. No existing fixture holds such a unit (REPORT.md, "Fixtures that move").

## User-visible deltas

| # | Delta | Where | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | A rights source unit (a `right`/`right_lines` unit, or a `norm` unit of a rights document) whose act predicate is a declared open term moves from CHECKED to OPEN: its unit status, `coverage.bytes_by_status` of `ve document check`, and `unit_open` of `rights-elaborate`. Claims less. | `ve document check`, `ve document render`, the `document` and `rights-elaborate` service modes | tests/test_rights_open_act_is_open.py::test_rights_open_act_is_open (the condition test; fails on main, REPORT.md), ::test_rights_open_act_reads_each_rights_own_act, ::test_rights_document_norm_unit_with_open_act_is_open; the controls ::test_rights_closed_act_stays_checked; `#guard`s in lean/VE/Rights/OpenActExamples.lean | SIGNED by the DRI 2026-11-09, reviews/dri-decisions-20261109-lp0801.md item 1 (CHECKED to OPEN only for units whose act is a declared open term); condition test tests/test_rights_open_act_is_open.py::test_rights_open_act_is_open |
| 2 | `VE.Rights.Run.nodeOpen_eq` restated to the new body: the disjunct `openNames.contains N.pred` is added (lean/statements.txt) and proved; its docstring no longer calls the scan byte-neutral | lean/VE/Rights/Run.lean | the Lean build (the proof) and python3 lean/audit.py | SIGNED by the DRI 2026-11-09, reviews/dri-decisions-20261109-lp0801.md item 1 (task rights-cfr-4 deliverable 2: the DRI-signed restatement); condition test tests/test_rights_open_act_is_open.py::test_rights_open_act_is_open |
| 3 | Trusted Lean growth: lean/VE/Rights/Run.lean trusted +4 (G; K +0, S +0), measured with `uv run python tools/trust_map.py --check` on the final code; recorded with `trust_map.py --allow` in docs/trust-baseline.json; ties-pass row in manage-agents FOLLOW-UPS.md under "## rights-cfr-4" | lean/VE/Rights/Run.lean | `#guard`s at lean/VE/Rights/OpenActExamples.lean:31-38; 3 seeded bugs, all killed ([mutants.json](mutants.json)); trust mutants ([trust-mutants.json](trust-mutants.json)) | R16 (DRI-RULINGS.md) |
