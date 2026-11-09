# cmp-s3a-cfr-2: DELTA

Refusal text only. No verdict changes: every input refused on main is still refused, and no accepted input
changes. The changed inputs are `ClauseDoc`s (`checkClauses`, `checkCandidates` in
lean/VE/RightClauses/Plain.lean) where an entry's rule `<n>` is the rule of more than one source line (of
`D.doc`, or of a `.right` candidate's own right) and rights' first fault on that document (`VE.Rights.checkRights`,
lean/VE/Rights/Correlate.lean:358-370) is a `DuplicateDeclaration`. The head is reached only from Lean: there is no
right-clauses service mode, relay or wire decoder yet (cmp-s3-cfr-1), so no corpus record or golden changes.

Base text on these inputs: `InvalidInput: invalid clauses of rule <n>`. Fault order is unchanged: the entry is
refused at the same place in 4.1 step 3's order as before; only its text changed.

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | Rights' first fault is the duplicate of `<n>` itself as a rule: the text is `DuplicateDeclaration: rule <n>` (was `InvalidInput: invalid clauses of rule <n>`). It keeps the quoted rule name `<n>` (R1 (a)). The base had no path or span (R1 (b)). It is more specific: it names the fault, a second line with the rule (R1 (c)). | `tests/test_right_clauses_duplicate.py::test_clause_entries_preserve_duplicate_rule_diagnostic` (two structured lines `equal-access`, one entry each: the head's text is `DuplicateDeclaration: rule equal-access`, the rule name kept; fails on main); `#guard`s lean/VE/RightClauses/Examples.lean:221-224 (fixed lines) and :247 (a `.right` candidate) | SIGNED by standing ruling R1 (DRI-RULINGS.md) |
| 2 | Rights' first fault is another `DuplicateDeclaration` (`right <n>` when the rule is named like a right, or `limitation <n>`, `bar`, `rule <m>` for an earlier duplicate, `holder <s>`, `bearer <s>`, `alters <a>` from rights' block check): the text is that rights text, unchanged (was `InvalidInput: invalid clauses of rule <n>`). | Condition test: `tests/test_right_clauses_duplicate.py::test_clause_entries_take_rights_first_duplicate_text` (rule named `r21`, like its right: the head's text equals `VE.Rights.checkRights`' text `DuplicateDeclaration: right r21` byte for byte). Negative tests: the same test and `test_clause_entries_preserve_duplicate_rule_diagnostic` fail on the seeded one-character edit S2 (`e ++ "."`, [mutants.json](mutants.json)); `test_same_bytes_refuses_every_one_character_edit` shows the comparison refuses every one-character deletion or substitution and an appended character; `test_clause_entries_keep_invalid_clauses_when_rights_faults_first` and the `#guard` at Examples.lean:226 show that a rights first fault other than `DuplicateDeclaration` keeps the base text (seeded S3 fails them) | SIGNED by the DRI 2026-11-09 (reviews/dri-decisions-20261109-lp0801.md item 1) |
