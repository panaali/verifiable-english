# sa-no-exception delta: `dfltUniform_sound` proved (DF-U)

Base: `git merge-base HEAD main` (90807e7f7). Ruling: reviews/dri-decisions-20261102-pc9-decide-check.md.

**No user-visible delta, so no row.** The change is a theorem, a hypothesis inside `ConditionsExact` (a Prop that no
route evaluates), and fixtures. No route, answer, refusal or text changes. E1d's refusal of provider-condition
defaults (`providerConditions`, read by `defaultsRows`) still stands, and lifting it belongs to EXP-D3 (task: "no
row while E1d's refusal stands"). F9.3, F9.4, F9.6 and F9.7 (`#guard`s in lean/VE/Defaults/UniformExamples.lean) are
unchanged and build. No Python or Rust product file changed: `tools/check_pc9_statements.py` is a statement check.
