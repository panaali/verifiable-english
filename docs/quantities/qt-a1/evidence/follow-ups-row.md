# FOLLOW-UPS.md row for qt-a1 (R16 ties pass)

Appended to `manage-agents/FOLLOW-UPS.md` with `>>` (fix round 2, recheck F7: the first append had been overwritten by another writer). If it goes missing again, re-append these lines verbatim. Probe: `grep -A2 '^## qt-a1' ~/code/manage-agents/FOLLOW-UPS.md | grep -q 'R16 ties pass (qt-a1'`.

```
## qt-a1 (2026-10-18)
- R16 ties pass (qt-a1, ve-qt-a1 docs/quantities/qt-a1/DELTA.md row 1, S +137, K +0, V +0: lean/VE/Cardinality/Syntax.lean +81 (Body 9, Rel 4, CountAtom 8, Cmp 5, Proportion 10, CFormula 11, CEnv 5, regionPrefix 2, CEnv.WellFormed 6, BodyTyped 8, Admitted 13), lean/VE/Cardinality/Semantics.lean +56 (Body.holds 7, HasCount 5, Rel.holds 5, Cmp.holds 8, Counts 6, CountAtom.holds 4, Proportion.holds 5, CFormula.holds 9, Admissible 4, CEntails 3)) -> infra item ties-qt-a1: bind these lines to the existing render/wire/encoder theorems (candidates already in the tree: admits_iff ties Admitted to CFormula.admits and bodyCheck_iff ties BodyTyped to bodyCheck; hasCount_exists_unique ties HasCount and Counts; proportion_holds_iff restates Proportion.holds; qt-a1b's erase_iff ties erasure and CEntails, and its count_*_agree theorems tie CountAtom.holds to VE.Time's counting forms). Also add a fixture with a `whole` other than `.any` in a true case, so C-population, C-part-only and X2 are caught by more than proportion_holds_iff.
```
