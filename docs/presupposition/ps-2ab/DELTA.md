# ps-2ab: user-visible delta

Feature item ps-2ab (PS-2a part 3; plan `docs/spec/presupposition-PLAN.md` "PS-2a", spec 4.7).

**No rows.** The item adds Lean only: `lean/VE/Presupposition/Admit.lean` (`admit`), `Admit/Facts.lean` and
`Admit/Statements.lean` (proofs), and fixtures in `Examples.lean`. Nothing on a route calls `admit` until PS-4:
`grep -rl 'Presupposition.Admit' lean/VE lean/*.lean --include=*.lean` lists only `lean/VE.lean`, `lean/VE/Audit.lean`
(generated) and files under `lean/VE/Presupposition/`, and no Python, Rust, `Protocol.lean` or schema file changes
(`git diff --name-only main...HEAD`). No answer, diagnostic or verdict a user can see changes, so no ruling is needed
and no signature is reserved. The diagnostics `admit` writes (spec 5) are new texts that no route emits yet; PS-4
puts them in the document mode's answer.
