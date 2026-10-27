# ap-3c delta: elaboration and the split map (`VE.Acts.Elaborate`)

Base: `git merge-base HEAD main` (`2b13707e7`). ap-3c is the third part of batch AP-3 of
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) (section 4, "AP-3"); see [REPORT.md](REPORT.md).

**Public output: none.** ap-3c adds `lean/VE/Acts/Elaborate.lean` and its fixtures `ElaborateExamples.lean`. Nothing
imports them except the fixtures and the library root `lean/VE.lean`. No service mode, route, decoder, command or
diagnostic reaches them (the `acts-elaborate` relay and `decodeElaboratedU` are ap-3d's), and `_lean_route` is
unchanged. No Python or Rust product code changes. No verdict, diagnostic, fault order, English line or CPU figure
changes, so the only row is the trust growth. The new diagnostics (D-20 to D-27) are Lean texts no entry point
reaches yet.

## User-visible deltas

Trust growth, re-measured with `python3 tools/trust_map.py --check` on the final code: K +0, S +71, V +75, trusted
+146, against the merge base. It is recorded as two allowances (S 71, V 75) in `docs/trust-baseline.json` with
`trust_map.py --allow`, and `trust_map.py --check` passes. The ties-pass row R16 asks for is in manage-agents
FOLLOW-UPS.md, section "## ap-3c".

| # | File | Trusted lines (class: declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Acts/Elaborate.lean` | +146: S +71 `ActsDoc`, `SplitMap`, `partPred`, `partRule`, `dualOf`, `readingOf`, `splitAtoms`, `partNames`, `elaborateMap`, `elaborate` (spec 6.3, 6.6); G[V] +75 `ruleReading`, `partsOf`, `splitMap`, `splitReg`, `splitNode`, `splitEnv`, `splitDoc`, `refsOk`, `namesOk`, `partsDistinct` | the `#guard`s of `ElaborateExamples.lean` (E1 to E10 and E16; both sides of D-20 to D-27, of step 5 at E12's boundary and of the backstop; the order of the steps; each position of each list a check reads); [`mutants.json`](mutants.json): 39 seeded bugs, at least one in each new definition, all killed with the theorems cut; [`trust-mutants.json`](trust-mutants.json): 273 killed, 0 survivor, 0 unknown, 54 invalid, 68 allowed ([`trust-mutants-allow.json`](trust-mutants-allow.json): 6 equivalent drops, 62 that do not elaborate) | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
