# fsf-repair-f7-govadequacy-1119: build notes

Notes the builder wrote about this item's own build, moved here unchanged from REPORT.md on 2026-11-25
(relc-scan-buildnote-fix-1125). They are not omission records: they say nothing the translation leaves out. The omission
counter's record scan reads every REPORT.md sentence that has a drop or merge word and names a unit, so in REPORT.md the
third sentence below was counted as an omission record (record 1 of reviews/pathf-q3/relc-r35-flag-analysis-20261125.md).
This file is not one the scan reads.

The VE commit this merges at is the merge train's merge commit of this branch (on main after f03cafb9d2). The R16 C2/C3 pins are per commit, so the counted read must re-pin at that commit. A merge
after the R16 diagnostic voids that diagnostic for the answers that read the touched units: f3, f8, f9-acc, f10-acc,
f11-acc, f12-p, f12-u, f13-p and f13-u (`c5check.log`). These include A-L*-EXT/GOV, C5 and the R family (R*/ACCEPTABLE).
