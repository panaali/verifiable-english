# pc-9 delta: typed priority checks and the "no exception" statements

Base: `git merge-base HEAD main` (d8f58bf3b). Plan and spec at 3dfadd302 (docs/spec/profile-composition-PLAN.md PC-9,
docs/spec/profile-composition.md 1.8, 1.9, 3.8).

**Public output: no answer on main changes.** The one new behaviour is a refusal that no request on main reaches:
`runLayered` reaches `defaultsRows` only through its own `decodeLayered`, and `decodeLayered_uniform`
(lean/VE/Defaults/UniformExamples.lean) proves `providerConditions L.packs = false` and
`dfltUniform L.D L.packs = dfltPremises L.D` for every value it decodes (pk-1-conditions exports `conditions = []` on
every pack). F9.4 (`#guard`s at UniformExamples.lean:130, :132), F9.5 (:150) and F9.7 (:160, :162) show today's
answers unchanged, on the defaults kinds and on every other kind. No Python or Rust product file changes.

## User-visible deltas

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | The defaults kinds (`defaults-elaborate`, `-coherence`, `-certificate`, `-model`: the `--assume-no-exception` question) refuse a document some of whose packs state a sufficient condition, with `UnsupportedProfile: defaults with provider conditions is not implemented` (`providerRefusal`; its English E1d is `providerE1d`, spec 2.1 :1341). Unreachable on main (above). Trust growth for this new Lean-owned behaviour, re-measured with `uv run python tools/trust_map.py --check` on the final code ("PASS: K, S and untied [V] within d8f58bf3be47 and the allowances introduced since"): K +0, S +56, untied V +3, trusted +59, recorded with `trust_map.py --allow` in docs/trust-baseline.json. S: `lean/VE/Defaults/Uniform.lean` +56 (`packConditions`, `noneOr`, `dfltUniformOf`, `dfltUniformLabelled`, `dfltUniform`, `leastUniform`, `ConditionsExact`, `DfltUniformSound`). V (untied G[V]): `lean/VE/Defaults/Route.lean` +3 (the guard line and docstring of `defaultsRows`). | F9.3 (UniformExamples.lean:64-66), F9.6 (:154, :155), F9.7 (:160, :162), `decodeLayered_uniform`, tests/test_defaults_uniform.py; every new trusted definition has a failing mutant: mutants.json (18 hand seeds) and trust-mutants.json (rescored, exit 0: 91 KILLED, 52 ALLOWED with reasons in trust-mutants-allow.json, 12 INVALID, 0 SURVIVOR, 0 UNKNOWN); ties-pass row in manage-agents FOLLOW-UPS.md "## pc-9". The DRI confirmed the citation (reviews/dri-decisions-20261102-pc-9.md item 4). | SIGNED by standing ruling R16 (DRI-RULINGS.md) |

Not a delta: `DfltUniformSound` holds the statement of `dfltUniform_sound` as a Prop definition (DRI decision
2026-11-02 pc-9 item 1: form only, no user-visible delta); `precedence_apart`, `dfltUniform_legacy`,
`leastUniform_legacy`, `conditionsExact_legacy` and the lock `dfltUniformSound_iff` are proofs. R16 stops at the
first pack that states a non-empty condition: that change makes the refusal reachable and needs its own DELTA row.
