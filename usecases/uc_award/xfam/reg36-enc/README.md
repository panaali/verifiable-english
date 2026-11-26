# reg. 3(6) household of an absence, encoded (row statute-xfam-wrong-uc-award-1)

The fix (translation.absent6) reads absent_from(x, y), the household a temporary absence is from, which no frozen encoder
stated. One fresh Opus 5.5 encoder session (claude-opus-5-5, account claude-worker-account-2: the picker's pick),
2026-11-24 02:28:45-02:29:24Z, in manage-agents tools-local/xfam-enc/sandbox.sh (network only api.anthropic.com:443,
proxy.log 4 ALLOW / 2 DENY; the sandbox's sealed-file guard passed). Its stage held only prompt.txt (copied here),
the Codex set's questions-enc.jsonl (c633faa30eb1903c...) and uc2013.txt (the build's source.txt, b28e1d46408a23b0...).
It never saw uc-award/xfam/sealed/, a questions.jsonl, the same-family set or answers, the frozen records or any answer.

| file | sha256 |
|---|---|
| absences.jsonl (verbatim seat output) | 6e22f945e43ffc2bc57ec6040fc52030f674262bc0f7387d3cdadc095f5a2f36 |
| transcript (workdir <home>/xfam-enc-runs/uca36-enc-20261124T022845Z) | 113e49e68889c971a2d4a3db98c597fbc0fd62d5d7b377986501b51a6f4f02bf |
| prompt.txt | 0f02424570e76feaaa47fa8eef9f8ff15560cdc652059a6225d6fec2b54422f0 |

Applied mechanically by ../reg36_overlay.py (cases_xfam.py unchanged), only for an absent person who is a member of a
stated couple: U030 absent_from(bob, ann) (Bob a member of one couple: the same as the unstated default), U035a and U035b
absent_from(bob, ann) (Bob a member of two couples: the field decides which couple reg. 3(6) ends). The seat's
over_6_months agrees with the frozen abs_over6 on every applied line (U030 false, U035 true). The seat's other 8 lines
(children: U021-U027) are not applied (reg. 4(7) reads the frozen unary facts only).

The same-family set needs no re-encoding: no same-family record has an absent person who is a member of two couples, so
the fix never reads absent_from there.
