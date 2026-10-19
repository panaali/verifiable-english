# FOLLOW-UPS.md row for qt-a2 (R16 ties pass)

Appended to `manage-agents/FOLLOW-UPS.md` with `>>`. If it goes missing, re-append these lines verbatim. Probe: `grep -A1 '^## qt-a2 (2026-10-19)' ~/code/manage-agents/FOLLOW-UPS.md | grep -q 'R16 ties pass (qt-a2'`.

```
## qt-a2 (2026-10-19)
- R16 ties pass (qt-a2, ve-qt-a2 docs/quantities/qt-a2/DELTA.md row 1, S +35, K +0, V +0: lean/VE/Cardinality/Syntax.lean +25 (CTerm 6, CTermTyped 6, admittedRules 3, CFormula +4, Admitted +6), lean/VE/Cardinality/Semantics.lean +10 (CTerm.Denotes 5, CFormula.holds +5)) -> infra item ties-qt-a2: bind these lines to existing theorems (candidates in the tree: tagOf_iff ties CTermTyped to CTerm.tagOf and ratioTyped_iff to ratioTyped; admits_iff ties the ratio cases of Admitted; roundsTo_holds_iff, percentOf_holds_iff and percentRoundsTo_holds_iff restate the ratio cases of CFormula.holds through roundsTo_ratio_agree; cterm_erase ties CTerm.Denotes to the erased operand; admittedRules_cases states admittedRules).
```
