# pc-3 DELTA: the composition contract (profile-composition PC-3, first part)

Feature item pc-3 (plan `docs/spec/profile-composition-PLAN.md` PC-3, spec `docs/spec/profile-composition.md` 1.1 to
1.5, 3.3 and 5.3, copied verbatim from 938e148cb). Base: main at e73ded834.

PC-3 changes no answer, so there is no answer row. The `interface` field admits nothing by itself. `gateOf`,
`routeOf` and `checkDocSets` are unchanged, and `ve/profile_table.json` does not carry the field (`ProfilesMain.rowJson`
is unchanged, and `uv run python tools/regen_generated.py --write` left it byte-identical). Every proof about the
gate still holds with the new component (`gate_legacy`, `gate_acts`, `gate_scope`, `VE.Cardinality.gate_cardinality`),
and no fixture shows a changed answer. The only row is the trusted-base growth, which R16 asks to be itemised.

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted base: K +0, S +62, untied V +52, trusted +114 (`uv run python tools/trust_map.py --check` on the final HEAD: PASS with the allowance recorded in `docs/trust-baseline.json`). S: `lean/VE/Compose/Contract.lean` +55 (`Rewriter`, `Rewriter.Laws`, `ScopeRunsOf`, `ScopeRuns`, `ScopeFaithful`, `ScopePreserves`, `ScopeSetsFaithful`, `RouteFacts`) and `lean/VE/Compose/Dispatch.lean` +7 (`Interface` and the field). V (untied G[V]): `lean/VE/Compose/Contract.lean` +27 (`pipeline`, `pipelineOf`, `scopeRewriter`, `docRewriters`), `lean/VE/Compose/Stack.lean` +15 (`rewriters`, `stackOf`, `listedStacks`) and `lean/VE/Compose/Dispatch.lean` +10 (`slotAgrees`). This is new Lean-owned behaviour, with no Python or Rust copy. | Every new trusted definition is exercised by a test that can fail: `docs/profile-composition/pc-3/mutants.json` lists 13 hand mutants, one or more per definition, each with its failing theorem, `#guard` or test. `docs/profile-composition/pc-3/trust-mutants.json` is the mechanical run. The S statements equal the approved text (`tests/test_pc3_statements.py`). The ties pass is asked for in FOLLOW-UPS.md under "## pc-3". | R16 |
