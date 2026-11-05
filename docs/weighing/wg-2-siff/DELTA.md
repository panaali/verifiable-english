# wg-2-siff delta: `strength_iff` with the DRI's hypothesis (`lean/VE/Weighing/{Conditions,Examples}.lean`)

Base: `git merge-base HEAD main` (14e200f24).

**Public output: none changes.** No service mode, runner, decoder or encoder reads `VE.Weighing.Conditions` or
`Examples` (wg-2's DELTA; this item adds theorems, fixtures and docs only, and no definition outside `Examples.lean`).
No Python, Rust, decoder or diagnostic file changes, so no verdict, text, fault order or byte changes. The added
hypothesis is the decoder's identifier rule, so no wire document is excluded by it (the decoder guard,
`Examples.lean:211`). Trust: `uv run python tools/trust_map.py --check` on the final code reports "K +0, S +0, D +0,
G +0, tied +0, unclassified +0, trusted +0" against 14e200f24: the new Lean is theorems (P) and fixtures classified T
in `tools/trust-classes.json`, so R16 records no allowance (`--allow`: "nothing to allow").

## Changed approved statement

Changing an approved Lean theorem statement is never covered by a standing ruling (DRI-RULINGS.md, "Never covered").
This row is signed by the DRI's decision for this item.

| # | File | Row | Evidence | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Weighing/Conditions.lean`, `docs/spec/weighing.md` 5.1 | `strength_iff` gets one hypothesis, `hr : ∀ r ∈ Wd.D.T.regulated, ∃ c cs, r.name.data = c :: cs ∧ c.isAlpha` (every regulated name begins with an ASCII letter), the wider of item 2's two forms. The narrow form (on the queried `a` alone) is false: F19's mirror (`mxW`, real triple `(_x_permitted, l, c)`, query `(x_permitted, l, c_)`), which reviews/dri-decisions-20261105-wg-2-siff.md item 2 confirms under item 2. Nothing else in the statement changes | the unrestricted statement refuted on `cxW` (`Examples.lean:243`), the narrow form on `mxW` (`:257`); both directions on W-β1 (`:236`), W-β2 and W-γ (`:238`, `:240`); `lean/axioms.txt`: `strength_iff` uses propext, Classical.choice, Quot.sound only | SIGNED by the DRI 2026-11-04 (reviews/dri-decisions-20261104-wg-2-strength.md item 2) |
