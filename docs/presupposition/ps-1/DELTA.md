# ps-1: user-visible delta

Feature item ps-1 (PS-1 of `docs/spec/presupposition-PLAN.md` at 3a3ab2afd, first part: spec 4.1 and 4.2 at
db2a9e712; acting DRI dri-featurefeed).

**No existing output changes.** `uniqueD` and `assertive` are now wrappers over `uniqueAt` and `assertiveAt`, and
each is `rfl`-equal to its old body (the two `example`s in `lean/VE/Discourse/Descriptions.lean`). So every term that
discourse builds is the same term, and every discourse answer is the same bytes (S11, REPORT "S11"). The new frame
file and its fixtures add no service mode, wire field, diagnostic or limit; nothing outside `lean/` reads them. The one
delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | Trust budget: **trusted +73** (K +0, S +64, untied D[V] +9), measured with `uv run python tools/trust_map.py --check` against the merge base c3d9ea938: `VE/Presupposition/Frame.lean` S +64 (`Frame`, `plug`, `binders`, `goal`, `close`, `Reach`, `PositionClass`, `cls`, `shallow`); `VE/Discourse/Descriptions.lean` D[V] +9 (`uniqueAt`, `assertiveAt`, `raise1`, `uniqueOpen`, `assertiveOpen`). | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour (the presupposition frames and the generalised description builders), 73 lines, none in K | Allowance in `docs/trust-baseline.json`. Every new trusted definition is exercised by a check or proof that fails: `docs/presupposition/ps-1/trust-mutants.json` (68 mechanical mutants: 29 KILLED, 39 ALLOWED, each with a reason in `trust-mutants-allow.json`; exit 0) and the 16 hand mutants of `docs/presupposition/ps-1/mutants.json`, one or more per definition. The ties pass is the "## ps-1" row of FOLLOW-UPS.md. |
