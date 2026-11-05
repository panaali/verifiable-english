# ci-1 delta: the command reader, no mode

Base `ea108ea4e` (`git merge-base HEAD main`). **Public output: none.** No service mode, route, wire row, schema, Python
or Rust product file changes: `git diff --name-only main...HEAD` lists no `rust/` path and no `ve/` path but `ve/assurance-manifest.json`,
which classifies the two new Lean files (ci-1 review F2, fixed in ci-2), and nothing calls
`VE.Commands` until CI-2. `readingsBound` names the literal `64` of `Wire.readingCandidates`; `readingCandidates` keeps
its verdicts (`#guard`s on 0, 1, 2, 64 and 65 readings). So the A/B has no record to compare. The one row is the
trusted-base growth.

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted base: K +0, S +0, untied V +131: `lean/VE/Commands/Read.lean` +131, nothing else (`uv run python tools/trust_map.py --check`: PASS with the allowance in `docs/trust-baseline.json`). `Texts.lean` and the refusal definitions are G[R], `declared` P, `Examples.lean` T | Every new trusted definition is exercised: `docs/commands-imperatives/ci-1/trust-mutants.json`, its allow file and `mutants.json`; the ties pass is the FOLLOW-UPS.md row under "## ci-1" | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
