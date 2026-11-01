# sc-2d delta

Base: `git merge-base HEAD main` (`4d9a0eeb0`). No answer changes: `git diff main...HEAD -- lean/VE/Scope/Govern.lean
lean/VE/Scope/Effects.lean lean/VE/Scope/Wire.lean` is empty, and no Python or Rust product file changed. The one
delta is the approved statements' new premise.

## User-visible deltas

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | changed approved theorem statements: spec 5.4's five effect theorems gain (hw : JsonWF o) | `reguard_applies`, `restrict_applies`, `carveOut_applies` and `applyEffect_typed` take it after `hN`, `commute_applies` before `h₁`; spec 5.4's text (docs/spec/scope.md) is the proved statements, and nothing else in 5.4 changed (`own_congr` and `order_refused` as sc-2c proved them). `tests/test_scope_5_4_statements.py` (the five equal spec 5.4's text; their binders are pinned, so a statement without `hw` or with another premise fails; mutant `restrict_applies_drops_hw`); F-raw-effect (`lean/VE/Scope/Examples.lean`, section SC2c) stays as the reason; `baseObj_jsonWF` and the example in `lean/VE/Service/ScopeExamples.lean` discharge `hw` from the boundary check | SIGNED by the DRI 2026-10-31 (reviews/dri-decisions-20261031-sc-2c.md item 1) |

Trust growth is not a user-visible delta and has no row: S +3 (`VE.Scope.Typed`, the definition spec 5.4 states), K +0,
recorded with `tools/trust_map.py --allow` under standing ruling R16; per file and its test in [REPORT.md](REPORT.md)
"Trust".
