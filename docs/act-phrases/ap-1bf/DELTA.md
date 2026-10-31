# ap-1bf delta: the `acts@0` wire contract, in shadow

Base: `git merge-base HEAD main` (`11de39bd8`). Edit 2 of plan synthesis round 2: the contract is written and run in
shadow; it reports, it refuses nothing, and no route reads it.

**Everything else: no change.** No product path asks for the new `diagnose` unit: `ve/backends/soft_relay.py:47`, the
only caller of `diagnose` in `ve/`, names `soft-norms@0` (`grep -rn diagnose ve/`). The recorded route cases are
unchanged: `tools/regen_generated.py --write` rewrote no file under `lean/VE/Route/examples/` or `tests/data/`
(`git diff --stat 11de39bd8 -- lean/VE/Route/examples tests/data` is empty). No theorem statement changed.

## User-visible deltas

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | Trust growth, measured on the final tree with `uv run python tools/trust_map.py --check` against `11de39bd8`: K +0, S +0, untied V +61, recorded as one allowance in `docs/trust-baseline.json`. Per file: `WireContract/Hooks/Acts.lean` +57 (G[V] `decoded`, `refusedWith`, `fixedOf`, `actsOf`, `member`, `classifier`, `hooks`, `inDomain`, `adapter`, `registered`), `WireContract/Diagnose.lean` +2 (the `acts@0` row), `WireContract/Tables/Acts.lean` +2 (generated). | [trust-mutants.json](trust-mutants.json): 109 KILLED, 0 SURVIVOR, 0 UNKNOWN, 26 ALLOWED ([trust-allow.json](trust-allow.json), one reason each), 7 INVALID; every new trusted definition has a killed mutant (`hooks`, which no operator mutates, by hand: [mutants.json](mutants.json) `lean-hooks-no-classifier`). FOLLOW-UPS.md row "## ap-1bf" asks for the ties pass. | R16 |
