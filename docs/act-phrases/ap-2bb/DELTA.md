# ap-2bb delta: `Atom.canon`, `normalOk` and the render fixtures (`VE.Acts.Linearize`, `VE.Acts.RenderExamples`)

Base: `git merge-base HEAD main` (`432763b06`). ap-2bb is the rendering part of batch AP-2 of
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) (section 4, "AP-2"; named ap-2d in the AP-2 reports). `read_normal`'s
general proof is ap-2bc ([REPORT.md](REPORT.md)).

**Public output: none.** ap-2bb adds `Atom.canon` to `lean/VE/Acts/Linearize.lean` and `normalOk`, `Filler.parts` and
`longEnd` to `lean/VE/Acts/Meaning.lean` (beside `atomOk`), and adds the fixtures in `lean/VE/Acts/RenderExamples.lean`. `Atom.normal`
now reads its argument order from `Atom.canon`. That is the same order it wrote before (the object, then the others
in their order; the object's marker `""` has no words), so its output is unchanged: every existing `#guard` on a
normal form or paraphrase text passes (`lake build`, 1168 jobs, exit 0). `applyRule` now calls `longEnd`, the D9 (i)
test it had written inline, so no meaning changes: every `MeaningExamples` guard passes. No service mode, route,
decoder, command or diagnostic reaches `normalOk` or `Atom.canon`. No Python or Rust product code changes. No
verdict, diagnostic, fault order, English line or CPU figure changes, so the only row is the trust growth.

## User-visible deltas

Trust growth, re-measured on the final code with `uv run python tools/trust_map.py --check`: K +0, S +29, D +0,
G +0, unclassified +0, trusted +29 against the merge base. It is recorded as one allowance (S 29) in
`docs/trust-baseline.json` with `trust_map.py --allow`, and `trust_map.py --check` passes. The ties-pass row R16 asks
for is in manage-agents FOLLOW-UPS.md, section "## ap-2bb". The guard line numbers are
`lean/VE/Acts/RenderExamples.lean`'s.

| # | File | Trusted lines (class: declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Acts/Meaning.lean`, `lean/VE/Acts/Linearize.lean` | +29, all S. Meaning.lean +22: `normalOk` (lines 143-157), `Filler.parts` (139-142), `longEnd` (76-79), less the inline test `longEnd` replaces in `applyRule`. Linearize.lean +7: `Atom.canon` (39-43), and `Atom.normal`'s argument line now reads `a.canon.args` | `#guard`s 23-33 (G6's render pair, N1 to N5), 41-48 (`Atom.canon`), 56-98 (each `normalOk` condition accepted and refused, FR3 to FR5), 108-128 (two or more parts and D9 (i), C1 to C4, G7 with the marker repeated); MeaningExamples 112-120 (D9 (i) in the meaning, through `longEnd`); TableExamples 170, 202 and 207 (normal-form texts). Every new trusted definition has a plant that a guard kills ([mutants.json](mutants.json): 18 plants, all killed). `tools/trust_mutants.py` exits 0 ([trust-mutants.json](trust-mutants.json): 176 killed, 8 invalid, 34 allowed with reasons in [trust-mutants-allow.json](trust-mutants-allow.json), 0 survivors) | R16 |
