# ps-2ac: user-visible delta

Feature item ps-2ac (PS-2a part 4; plan `docs/spec/presupposition-PLAN.md` "PS-2a" and 4.6, spec 4.7, 2.3 and 5).

**No rows.** The item adds Lean only: `lean/VE/Presupposition/Run.lean` (the report value `shown` and its guards),
its import in `lean/VE.lean`, side-table entries and regenerated inventories. No route reads the report until PS-4:
`grep -rlw 'VE.Presupposition.Run' lean --include=*.lean` lists only `lean/VE.lean`, and `git diff --name-only
main...HEAD` lists no Python, Rust, `Protocol.lean`, `Document.lean` or schema file (the list is in the REPORT's
"Final checks"). No answer, diagnostic, verdict or display line a user can see changes, so no ruling is needed and no
signature is reserved. PS-4 puts the value in the document mode's answer.
