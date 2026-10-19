# df-1a: user-visible delta

Feature item df-1a (batch DF-1a of `docs/spec/defeasible-PLAN.md`, first part; spec `docs/spec/defeasible.md` 7.1;
acting DRI dri-featurefeed, 2026-10-18).

**What users see does not change.** `lean/VE/Defaults/` is new and no service mode, executable, response shape,
schema, relay, Python or Rust product file reaches it: `ve_service`'s pin in `lean/checkers.lock` is unchanged, and
`tools/regen_generated.py --check` passes with no schema or pin rewritten. The one other Lean edit moves the theorem
`bindAll_wellFormed_inv` from `Norms/FlaggedSpec.lean` to `Norms/Elaborate.lean` with its statement unchanged; it
computes nothing. The one delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| T1 | Trust budget: **S +18, V +26** (K +0; 44 lines), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, 702ff7429: all in `VE/Defaults/Premises.lean`. S: `dfltOf`, `dfltLabelled` (what the no-exception premises say). Untied G[V]: `dfltPremises`, `dfltLabels`, `defaultX`, `withoutDefaults`, `bareExceptionLabels`, `Basis`, `Form`. Tied (not counted): `basisOf` to `basis_strict_sound`, `followsForm` to `followsForm_short`. C (not counted): `certChecks`, `assumptionsOf`. The check passes with the recorded allowance. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, 44 lines, at most 150, none in K; every new definition of `Premises.lean` is exercised by a `#guard` of `lean/VE/Defaults/Examples.lean` that can fail: `docs/defeasible/df-1a/evidence/run_mutants.py` runs a mutant of each (M1 to M14 in `mutants.json`, the two types excepted) against the guards with every theorem removed, and each fails a named guard (`evidence/mutants.out`); the ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## df-1a"). The allowance is recorded with `tools/trust_map.py --allow` (S 18 and V 26 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), df-1a, 2026-10-18") | `uv run python tools/trust_map.py --check` exit 0; `tools/regen_generated.py --check` checked 31 entries |
