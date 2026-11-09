# cmp-s3a-cfr-2: DELTA

Refusal text only. There are no verdict changes: every input main refuses is still refused, and no accepted input
changes.

Which inputs change. They are `ClauseDoc`s checked by `checkClauses` or `checkCandidates`
(lean/VE/RightClauses/Plain.lean, `entryError`) that meet both of these conditions:

- an entry that fails `entryOk` has a rule `<n>` that is the rule of more than one line of the rights document that
  holds its right. That document is `D.doc` for the fixed lines and for a `.rightLines` candidate. For a `.right`
  candidate it is `D.doc` with the candidate's own right;
- rights' first fault on that document (`VE.Rights.checkRights`, lean/VE/Rights/Correlate.lean:358-370) is a
  `DuplicateDeclaration`.

The base text on these inputs was `InvalidInput: invalid clauses of rule <n>`.

What does not change. A `.rightLines` candidate whose own lines repeat a rule keeps the base text, because those lines
are not in the rights document (Examples.lean:255, 257). Every other `entryOk` failure keeps the base text too.

Reach. The head is reached only from Lean. There is no right-clauses service mode, relay or wire decoder yet
(cmp-s3-cfr-1), so no corpus record or golden changes. For that reason, R1's evidence below is the Lean fixtures and
the probe test, not a saved corpus delta.

Order. The entry is refused at the same place in 4.1 step 3 as before, and no other check moves. In row 2 the
answer names rights' first fault, which can be a different fault from the entry's (a duplicate holder, or an earlier
duplicate rule): at that place, rights' fault is reported in place of the entry's.

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | Rights' first fault is the duplicate of `<n>` itself as a rule. The text is `DuplicateDeclaration: rule <n>` (was `InvalidInput: invalid clauses of rule <n>`). (a) It keeps the quoted rule name `<n>`. (b) The base had no path or span. (c) It is more specific: it names the fault, a second line with the rule. | `tests/test_right_clauses_duplicate.py::test_clause_entries_preserve_duplicate_rule_diagnostic` (two structured lines `equal-access`, one entry each: the head's text is `DuplicateDeclaration: rule equal-access`, and the rule name is kept; fails on main). `#guard`s lean/VE/RightClauses/Examples.lean:221-224 (fixed lines) and :252 (a `.right` candidate) | SIGNED by standing ruling R1 (DRI-RULINGS.md) |
| 2 | Rights' first fault is another `DuplicateDeclaration`: `right <n>` when the rule is named like a right, or `limitation <n>`, `bar`, or `rule <m>` for an earlier duplicate, or `holder <s>`, `bearer <s>` or `alters <a>` from rights' block check. The text is that rights text, unchanged (was `InvalidInput: invalid clauses of rule <n>`). | Condition test: `tests/test_right_clauses_duplicate.py::test_clause_entries_take_rights_first_duplicate_text`. The rule is named `r21`, like its right, and the head's text equals `VE.Rights.checkRights`' text `DuplicateDeclaration: right r21` byte for byte. Negative test: the seeded one-character edit S2 (`e ++ "."`, [mutants.json](mutants.json)) makes that test and `test_clause_entries_preserve_duplicate_rule_diagnostic` fail (`2 failed, 2 passed`). The boundary: `test_clause_entries_keep_invalid_clauses_when_rights_faults_first` and the `#guard`s at Examples.lean:226, 230 and 257 show that the base text is kept when rights' first fault is not a `DuplicateDeclaration` (S3 fails them) and when the rule is on one line only (S4 fails them) | SIGNED by the DRI 2026-11-09 (reviews/dri-decisions-20261109-lp0801.md item 1) |
