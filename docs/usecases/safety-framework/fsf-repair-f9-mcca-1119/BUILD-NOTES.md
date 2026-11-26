# fsf-repair-f9-mcca-1119: build notes

Notes the builder wrote about this item's own build, moved here unchanged from REPORT.md on 2026-11-25
(relc-scan-buildnote-fix-1125). They are not omission records: they say nothing the translation leaves out. The omission
counter's record scan reads every REPORT.md sentence that has a drop or merge word and names a unit, so in REPORT.md two
of these sentences were counted as omission records (records 2 and 4 of
reviews/pathf-q3/relc-r35-flag-analysis-20261125.md). This file is not one the scan reads.

## Seeded bugs: the mutant that survived (was after the seeded-bug table in REPORT.md)

A first carrier mutant ("... assessments" without "on various checkpoints") survived: it is still a prefix of f5's
rule wording, so the counter's own match still counts it; it is not a carrier break and was replaced by #4.

## Commit this merges at (was a REPORT.md section)

The legend change is commit 3d208f9253 (on main f5553bc894); the branch head is the docs commit that adds this file.
The R16 C2/C3 pinned lists are per commit: the counted read re-pins at the merge commit the train makes, and a merge
after the R16 diagnostic voids the diagnostic for G6 and K4/CHECKPOINT_MCCA (and for any answer reading f2, f3 or f5,
whose rendered units change).
