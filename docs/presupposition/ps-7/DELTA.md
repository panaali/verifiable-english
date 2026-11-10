# ps-7: user-visible delta

Feature item ps-7 (plan `docs/spec/presupposition-PLAN.md` "PS-7. Change of state, continuation and iteration").

**No rows.** The item adds Lean only: `lean/VE/Presupposition/Events.lean` (the PS-7 `pre` builders and their
`generic` readings) and its fixtures `lean/VE/Presupposition/Events/Examples.lean`, plus a trust-class move for
`Frame.locate` (`tools/trust-classes.json`, a side table no route reads). No route reads Events.lean: the English rows
come later in the English queue, after PS-6. `grep -rl "Presupposition.Events" lean/VE --include=*.lean` lists only
the two new files and the generated `lean/VE.lean` and `lean/VE/Audit.lean`, and no Python, Rust, `Protocol.lean`
or schema file changes (`git diff --name-only $(git merge-base HEAD main)`; REPORT "Files"). No answer, diagnostic
or verdict changes, so no ruling is needed and no signature is reserved.
