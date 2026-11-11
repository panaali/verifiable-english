# ps-3: user-visible delta

Feature item ps-3 (plan `docs/spec/presupposition-PLAN.md` "PS-3. Proved coupling of equal goals", spec 1.9 and 4.8).

**No rows.** The item adds Lean only: `lean/VE/Presupposition/Couple.lean` (picks, groups, coupling, the generated
`requires` constraints and the source-identity choice), `Couple/Statements.lean` (proofs) and `CoupleExamples.lean`
(fixtures). Nothing on a route calls `admit`, the coupling or the report until PS-4: no Python, Rust, `Protocol.lean`
or schema file changes (`git diff --name-only main...HEAD`), and only `lean/VE.lean`, the generated `lean/VE/Audit.lean`
and files under `lean/VE/Presupposition/` import the new modules. lf-14d's `compatibleChoices`, `Constraint` and
`satisfiesAll` are called, never edited. No answer, diagnostic or verdict a user can see changes, so no ruling is
needed and no signature is reserved.
