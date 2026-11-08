# at-1a delta: the attitudes Lean core, part one (spec 2.1-2.4)

Base: `git merge-base HEAD main` (f67a18feb). Plan: docs/spec/attitudes-PLAN.md "AT-1. Lean core"; spec
docs/spec/attitudes.md sections 2.1-2.4, 7.1, 7.5.

**No user-visible answer changes.** The item adds new Lean modules (`lean/VE/Attitudes/Scale.lean`, `Syntax.lean`,
`Examples.lean`) that no service mode, route, relay or command reads yet: no verdict, diagnostic, wording, fault
order or route changes. The generated inventories changed only through `uv run python tools/regen_generated.py
--write` (R12), and `lean/VE.lean` gains one import line (its union list has no writer). The one row below is the
trusted-base growth, which the DRI's decision asks to record here.

## User-visible deltas

| # | Delta | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted Lean S +221, K +0, untied D[V]/G[V] +0, unclassified +0: `lean/VE/Attitudes/Syntax.lean` +145, `lean/VE/Attitudes/Scale.lean` +76 (spec 2.1-2.4 verbatim); `Examples.lean`'s fixtures are T. Every trusted definition the tool selects has killed mutants (328 KILLED, 0 SURVIVOR, 0 UNKNOWN); the rest are hand-planted or recorded in `docs/attitudes/at-1a/mutants.json`. Cut-back row `at-1a-tie` (decision item 3) and a ties-pass row in manage-agents FOLLOW-UPS.md "## at-1a" | `uv run python tools/trust_map.py --check` on the final HEAD; allowance in `docs/trust-baseline.json`; `docs/attitudes/at-1a/trust-mutants.json` | SIGNED by the DRI 2026-11-04 (reviews/dri-decisions-20261104-at-1a.md item 1) |
