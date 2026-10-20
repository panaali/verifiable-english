# pk-1b: user-visible delta

Feature item pk-1b (the kind-table part of PK-1, `docs/spec/premise-packs.md` 2.10 and 2.6; SYNTHESIS 2.1 and 4.2;
acting DRI dri-featurefeed, 2026-10-18).

**What users see does not change.** `runLayered` now dispatches a layered `norm-defaults-*` case through the kind
table (`kindCase`: `Packs.dispatch legacyRows` over the source's pack ids) instead of calling `layeredCase` directly.
Today's four rows need no pack and call `layeredCase`, whose body is unchanged. `Packs.kindCase_eq` proves that
`kindCase` answers every kind exactly as `layeredCase` does, so `runLayered`'s answer, refusal and text are today's
for every input. The new refusal `UnsupportedProfile: case kind <k> needs the <pack> premise pack` needs a row with a
pack, and no such row exists yet. The base-against-head output differential agrees:

- `tools/lean_output_diff.py --build --recorded`, base `main` 20aa836fd (the merge base after the sync), head this
  branch: 445 invocations, 366 run on both builds, **0 differences**, 0 timed out. The invocations cover every
  conformance corpus and the `ve_service` sessions recorded at head by 8 test files (layered, report, soft kinds,
  switch, readings nd/sd/s2 and alternatives fill). Those sessions hold 76 `norm-defaults-elaborate`, 54 `-conflict`,
  93 `-status` and 2,693 `-report` cases, plus 68 `readings-choice` cases (`evidence/ab_full.txt`,
  `evidence/ab_recorded_kinds.txt`).

No response shape, generated schema, relay, Python or Rust product file changes. `softLabelledU_labels_nodup` is a
theorem and changes no output. Nothing is deleted, so no row is under R6. The one delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| T1 | Trust budget: **V +22** (K +0, S +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, 20aa836fd. `VE/NormDefaults/Packs.lean` +17 (untied G[V]: `KindRow`, `dispatch`). `VE/NormDefaults/Layered.lean` +5 (untied G[V]: `legacyKinds`, plus 2 docstring lines of `layeredCase`). `kindCase` is tied to `kindCase_eq` and `legacyRows` to `dispatch_legacy`. The check passes with the recorded allowance. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, at most 150 lines, none in K. Every new trusted definition is exercised by a `#guard` that can fail: `tests/test_packs_guard_mutants.py` kills 9 mutants of `dispatch`, `legacyKinds`, `legacyRows` and `kindCase` at guards of `PacksExamples.lean` and `PacksLegacyExamples.lean`, with the theorems stripped (`mutants.json`); `KindRow` is a type. The ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## pk-1b"). The allowance is recorded with `tools/trust_map.py --allow` (V 22 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), pk-1b, 2026-10-18"). | `uv run python tools/trust_map.py --check` exit 0; `tools/regen_generated.py --check` checked 32 entries |
