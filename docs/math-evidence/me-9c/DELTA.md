# me-9c delta: the identity runner's work budget

Base `3432611041` (`git merge-base HEAD main`). **Public output: none.** me-9c changes `lean/VE/Calc/Poly.lean`,
`lean/VE/Calc/Identity.lean` and fixtures: no service mode, command, route, schema, Python product code or Rust file.
The identity row reaches users only through ME-2's `calc` mode, which does not serve it yet.

Trust, re-measured on the final code with `uv run python tools/trust_map.py --check`: K +0, S +0, untied V +0,
trusted +0 against `3432611041bf` (G +1: the budget's line of `IdentityStop.text`, G[R]). Every new declaration is
C: its answer is tied to the unbudgeted one by a theorem (`identityDecideB_eq` and the `_eq` lemmas). No allowance and
no R16 row are needed.

The one change in what the (unserved) row says is the budget's own unknown:

| # | Change | Tests | Ruling |
|---|---|---|---|
| 1 | A row whose work runs past `VE.Limits.maxEvaluations` units is the unknown row `budgetRow` (`limit .polyTerms`, stop `.budget`, text "unknown: the budget of 1000000 evaluation steps ran out") instead of `holds`, `fails` or `identityNotShown`; only when the budget forbids the deciding step (`identityDecideB_within`, `identityRun_exhausted`) | each case: `test_fixture[budget-f5-zeros]`, `[budget-f5-node-limit]`, `[budget-power-2048]`, `[budget-points]`, `[budget-binom-113]`, `[budget-binom-105]`, `[budget-binom-104]`, `[budget-binom-0]`, `[budget-literal-0]`, `[budget-literal-10]`; the same query with an adequate budget: `[budget-binom-114]`, `[budget-literal-11]`, and within the row's budget `[budget-four]`, `[budget-power-64]`, `[budget-nested-divisors]`, `[budget-points-within]`, H-1 to H-4 and R-6 unchanged (`[h4]`, `[h4-stated]`, `[r6-h1]`, `[r6-sq]`) | R5 (standing ruling, DRI-RULINGS.md) |
