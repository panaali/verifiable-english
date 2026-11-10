# at-1b delta: the attitudes Lean core, part two (spec 2.5, 2.6, five statements of 6.1)

Base: `git merge-base HEAD main` (9672601e3). Plan: docs/spec/attitudes-PLAN.md "AT-1. Lean core"; spec
docs/spec/attitudes.md sections 2.5, 2.6, 5.2, 6.1, 7.1, 7.4, 7.5.

**No user-visible answer changes.** The item appends to `lean/VE/Attitudes/Syntax.lean` and adds
`lean/VE/Attitudes/Theorems.lean`, which no service mode, route, relay or command reads yet: `grep -rn
"VE.Attitudes" lean/VE/Service lean/VE/Route lean/Main.lean ve/` finds none (REPORT, "Runs"). The generated inventories
changed only through `uv run python tools/regen_generated.py --write` (R12), and `lean/VE.lean` gains one import line (its
union list has no writer). The one row below is the trusted-base growth, which the DRI's decision asks to record here.

## User-visible deltas

| # | Delta | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted Lean S +165, K +0, untied D[V]/G[V] +0, unclassified +0: `lean/VE/Attitudes/Syntax.lean` +165 (spec 2.5-2.6 verbatim but for D14c's signed line; `Examples.lean`'s fixtures are T, `Theorems.lean` is P). Stated separately, the tie move at-1a-tie's first half: `keys`, `name`, `keyOf`, `envAtt` S to D[V] tied, -15 (`tools/trust_map.py --check`: `S +165, D +15, tied +15`), so S before it is +180 | `uv run python tools/trust_map.py --check` on the final HEAD; `docs/attitudes/at-1b/trust-mutants.json` (0 SURVIVOR, 0 UNKNOWN), `docs/attitudes/at-1b/mutants.json`, `lean/VE/Attitudes/Examples.lean`'s `#guard`s; FOLLOW-UPS.md row "## at-1b" | SIGNED by the DRI 2026-11-05 (reviews/dri-decisions-20261105-at-1b-trust.md item 1) |
