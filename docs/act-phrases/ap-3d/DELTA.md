# ap-3d delta: the act check, step 6 and the decoder after AP-3 (`VE.Acts.Wire`, `VE.Acts.Decode`)

Base: `git merge-base HEAD main` (`d422a29ca`). ap-3d is the fourth part of batch AP-3 of
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) (section 4, "AP-3"); see [REPORT.md](REPORT.md).

**Public output: none.** No route reads the new code yet:

- `checkAct`, `decodeElaboratedU` and their fixtures are imported only by `DecodeExamples.lean` and the library root.
- The norms decoder's act hook (`Norms/Wire.lean`, `canonicalActIn`) still calls `Lexical.check`, so every route
  refuses a joined act exactly as before, with D-4 or D-5. A fixture pins this: `DecodeExamples.lean`, the last
  `#guard`.
- `Lexical.check` is now `checkWith (joinCheck name)`. Its body is unchanged and only split in two. The AP-1 proofs
  pass with only their `unfold` line changed: `check_iff` against the independent `Accepts`, `check_no_join` and
  Compat's `check_extends`.
- `checkAuthorN` is now `reservedNamesOk *> authorLimits` (`checkAuthorN_split`, `rfl`), with the same checks,
  order and texts.
- No Python or Rust product code changes.

So no verdict, diagnostic, fault order, English line or CPU figure changes, and the only row is the trust growth.

## User-visible deltas

Trust growth was re-measured with `uv run python tools/trust_map.py --check` on the final code against the merge
base:

- K +0, S −2, V +104, trusted +102.
- It is recorded as one allowance (V 104) in `docs/trust-baseline.json` with `trust_map.py --allow`, and
  `trust_map.py --check` passes.
- The ties-pass row that R16 asks for is in manage-agents `FOLLOW-UPS.md`, section "## ap-3d".

| # | File | Trusted lines (class: declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Acts/Decode.lean` +35, `lean/VE/Acts/Wire.lean` +26, `lean/VE/Acts/Lexical.lean` +25, `lean/VE/Acts/Elaborate.lean` +16 | D[V]: `ElaboratedU`, `actsOf`, `elaborateSource`, `decodeElaboratedU` (6.4); `joinedAct`, `checkAct` (6.4, D-15 to D-18); `checkWith`, `joinCheck` (`check`'s body, moved: the tie through `check_spec` names `check` only). G[V]: `atomsOf`, `splitsOf`, `partNamesIn`, `declaredAfter` and `elaborateMap`'s step 6 (6.3). `authorLimits` and `reservedNamesOk` are C, as `checkAuthorN` is; `meaningTexts` is G[R] | The `#guard`s of `DecodeExamples.lean`: `checkAct` on A6, A7 and A14 from their text, A14's residual, and D-15 (G5d's exact text), D-16, D-17 (L7) and D-18 at the start, middle and end; the pilot units through `actsOf` and `elaborateMap`; E13 to E15 on both sides; the order of steps 5, 6 and 7; a request at the limits; `decodeElaboratedU` over the wire, with and without `acts@0`. [`mutants.json`](mutants.json): 22 seeded bugs, at least one in each new or changed definition, all killed by a fixture with the theorems cut. [`trust-mutants.json`](trust-mutants.json) (full run on `40d31bcae`): 162 killed, 0 survivor, 0 unknown, 54 invalid, 44 allowed; [`trust-mutants-allow.json`](trust-mutants-allow.json) gives one reason per entry | SIGNED by standing ruling R16 (DRI-RULINGS.md), ap-3d, 2026-10-31 |
