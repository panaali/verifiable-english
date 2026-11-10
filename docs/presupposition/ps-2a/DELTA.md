# ps-2a: user-visible delta

Feature item ps-2a (PS-2a's second part, after ps-2aa; plan `docs/spec/presupposition-PLAN.md` "PS-2a").

**No rows.** The item adds Lean only: the readings block of `lean/VE/Presupposition/Wire.lean` and the filled
`candidateTable`, with their `#guard`s in `Examples.lean`. Nothing on a route reads them until PS-4.
`grep -rl Presupposition.Wire lean/VE --include=*.lean` lists only files under `lean/VE/Presupposition/`, and no
Python, Rust, `Protocol.lean` or schema file changes (`git diff --name-only main...HEAD`). No answer, diagnostic or
verdict changes, so no ruling is needed and no signature is reserved.
