# at-1c delta: the attitudes Lean core, part three (spec 2.7-2.9, seven statements of 6.1)

Base: `git merge-base HEAD main` (53fdabfde). Plan: docs/spec/attitudes-PLAN.md "AT-1. Lean core"; spec
docs/spec/attitudes.md sections 2.7, 2.8, 2.9, 6.1, 7.2-7.5.

**No user-visible answer changes.** The item adds `lean/VE/Attitudes/Frame.lean`, `Semantics.lean` and `Route.lean` and
appends to `Theorems.lean` and `Examples.lean`; no service mode, route, relay or command reads them: `grep -rn
"VE.Attitudes" lean/VE/Service lean/VE/Route lean/Main.lean ve/` finds none (REPORT, "Runs"). `attitudesRow` is defined,
not registered (AT-3a registers it); `attitudesPack` is on no pack list. The generated inventories changed only through
`uv run python tools/regen_generated.py --write` (R12). The one row below is the trusted-base growth R16 asks to record.

## User-visible deltas

| # | Delta | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted Lean +109 (K +0, S +87, untied G[V] +22, unclassified +0): `lean/VE/Attitudes/Semantics.lean` +41, `lean/VE/Attitudes/Frame.lean` +39, `lean/VE/Attitudes/Route.lean` +36 (S `SettledAsX`, `UnsaidFree` and AT-2's stand-in `labelOrigin`, classed S by reviews/dri-decisions-20261108-at-1c.md item 1; G[V] `toU`, `attitudesPack`, `attitudesRow`), less `lean/VE/Attitudes/Syntax.lean` -7 (at-1a-tie's second half: `baseEnvAtt` S to D[V] tied to `frame_wellFormed`; `tied +7`). `Examples.lean`'s fixtures are T, `Theorems.lean` is P | `uv run python tools/trust_map.py --check` on the final HEAD (`PASS`; `K +0, S +87, D +7, G +22, tied +7, unclassified +0, trusted +109`); every new trusted definition fails a named check when mutated: `docs/attitudes/at-1c/mutants.json` (27 hand mutants, one or more per definition), `docs/attitudes/at-1c/trust-mutants.json` (140 KILLED, 0 SURVIVOR, 0 UNKNOWN; the 90 ALLOWED are Lean refusals and Prop definitions whose pinning examples they break, `trust-mutants-allow.json`); FOLLOW-UPS.md row "## at-1c" | R16 (DRI-RULINGS.md): at most 150 K+S+V, K +0, each new trusted definition exercised by a check that can fail, a FOLLOW-UPS ties row |
