# pk-1: user-visible delta

Feature item pk-1 (PK-1, premise packs, `docs/spec/premise-packs.md`; SYNTHESIS 2.1 and 4.2; acting DRI
dri-featurefeed, 2026-10-18).

**What users see does not change.** The layered norm-defaults route's extra base premises `X` are now the premises of
a pack list (`lean/VE/NormDefaults/Packs.lean`) instead of `labelled` and `rightsCount`, and the soft and rights
routes build `[soft]` and `[soft, rights]` through `Packs.assemble`. On those lists every answer, array and
diagnostic is today's:

- base-against-head output differential (`tools/lean_output_diff.py`, base `main` 93131f967, head this branch):
  452 invocations, 378 run on both builds, **0 differences**, 0 timed out, over every conformance corpus, the
  `ve_service` sessions of 17 test files recorded at head (279 `norm-defaults-elaborate`, 715 `-conflict`, 219
  `-status`, 2,705 `-report`, 55 `-certificate` cases and about 900 readings cases), including the
  `InvalidModel(soft)` and `InvalidModel(rights)` cases of `tests/test_norm_defaults_layered.py`
  (`evidence/ab_full.txt`, `evidence/ab_recorded_kinds.txt`);
- the 33 `norm-defaults` cases of `tests/data/route-cases.jsonl`, one session each: 0 differences
  (`evidence/ab_route_cases.txt`).

The checks `assemble` adds (unknown or repeated pack, repeated label, generated names, vocabulary limit) cannot fail
on a decoded soft or rights source: today's packs generate no names, `checkAuthorN` already bounds the vocabulary,
and today's labels are distinct on decoded documents (predicate names are identifiers). The new `packFault` text
with a label is reached only by a non-legacy pack list, which no decoder builds yet. No response shape, generated
schema, relay, Python or Rust product file changes. The one delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| T1 | Trust budget: **V +78** (K +0, S +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, 93131f967: `VE/NormDefaults/Packs.lean` +73 (untied G[V]/D[V]: packOrder, reservedPrefixes, Pack.names, ownPrefixIn, ownPrefix, ordered, labelledX, X, names, packPremises, extendEnv, fullEnv, envX, firstRepeat, declaredIn, coherenceLabels, Pack, PackKind, RequestPath, labelledJson; tied: assemble to assemble_order/assemble_fresh, assembleIn to assembleIn_ok, packFault to packFault_legacy_rights/soft, elaborateArrays to elaborateArrays_legacy/keys, xWithout to xWithout_nil/sub), `VE/NormDefaults/Layered.lean` +5 (softPack, rightsPack and the two assemble calls; the `labelled`/`rightsCount` fields, the take/drop arrays and filledX's soft-prefix text are deleted). The check passes with the recorded allowance. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, at most 150 lines, none in K; every new trusted definition is exercised by a `#guard` of `lean/VE/NormDefaults/PacksExamples.lean` or `PacksLegacyExamples.lean` that can fail: `tests/test_packs_guard_mutants.py` kills a mutant of each trusted definition of `Packs.lean` and of `softPack`/`rightsPack` at a guard, with the theorems stripped (seeded bugs M1 to M8 in `mutants.json`); the ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## pk-1"). The allowance is recorded with `tools/trust_map.py --allow` (V 78 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), pk-1, 2026-10-18") | `uv run python tools/trust_map.py --check` exit 0; `tools/regen_generated.py --check` checked 31 entries |
