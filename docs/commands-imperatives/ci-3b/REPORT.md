# ci-3b: the `String.splitOn` lemma library and `preposed_eq` (commands-imperatives section 7, CI-3's proof part)

Status: built. 1 of the 2 statements is proved: `preposed_eq`. `readStep_conservative` moves whole, unproved, to
**ci-3bb**. The size cut forces the move (see "Size"), not a ruling. No route calls `readStep`, so no verdict, wording or
pilot byte changes. There is no DELTA row: the item adds theorems only. Next item: ci-4, after ci-3 and ci-3bb.

## Delivered (spec 9a12df17a section 7; plan CI-3)

- `lean/VE/Commands/SplitOnLemmas.lean`: `String.splitOn` with a separator of any length, stated over `List Char`
  (`splitOnL`) and over `String`. Each `String` lemma has a `#guard` on a concrete string.
  - `splitOn_data` is the bridge: `s.splitOn t = (splitOnL t.data s.data).map String.mk` for every `t ≠ ""`. It is
    proved by following `String.splitOnAux` byte by byte, including the restart after a partial match. Two `#guard`s
    check it on a partial and an overlapping match.
  - `splitOn_none`: a separator that does not occur gives the whole string.
  - `intercalate_splitOn`: `t.intercalate (s.splitOn t) = s`.
  - `splitOn_free`: the pieces hold no occurrence of the separator.
  - `splitOn_first`: the first-occurrence decomposition `s = a ++ t ++ b`, with `a` free of `t` and the pieces `a`
    followed by the pieces of `b`.
  - `splitOn_two`: there are at least two pieces exactly when the separator occurs.
  - The `List Char` twins: `splitOnL_none`, `intercalate_splitOnL`, `splitOnL_free`, `splitOnL_first`, `splitOnL_two`.
  - `VE.Acts.Lexical.splitOn_space` (one space) and `VE.Readings`' `splitOn_dunder` (`"__"`) are special cases.
    They are left in place: their files are outside this item's file list.
- `lean/VE/Commands/StepsProofs.lean`:
  - `preposed_eq` is proved, with no `sorry`. It uses `shapes_preposed` (`<x>` is a piece of the split at `, `),
    `hasThen_preposed` (so `<x>.` holds no `, then `), ci-3a's `readStep_one` and `lift_one`.
  - `readStep_core` is `readStep_conservative` restricted to a body that begins with neither `If ` nor `Then `. It is
    the `splitOn` half of the statement, proved here so that ci-3bb only adds the act linter's half.
  - Four `#guard`s: the shape of "If draft is approved, click Ask.", its `hasThen`, its rewritten wording, and the
    merged shape of "Click Check rule conflict.".
- `lean/VE.lean` imports StepsProofs. `tools/layer_policy.py` puts both modules in Steps.lean's layer, 4.
- Generated inventories are refreshed through `uv run python tools/regen_generated.py --write` (R12).
- Not edited: no file of ci-3's (Steps, StepsExamples, Read, Run, Texts, Examples, RunExamples, RunSplit;
  SpeechActs/; Source/).

### Statement comparison

`preposed_eq` equals section 7's text after whitespace normalisation (checked mechanically), with one addition after
`h`: `(hb : (trimmed s).utf8ByteSize ≤ maxWordingBytes)`. This is SIGNED by the DRI 2026-11-09,
reviews/dri-decisions-20261109-ci-3a-wording.md item 1. No other change.

## Moved to ci-3bb: `readStep_conservative`

The statement moves unchanged and is not committed here in any form. Its proof is
`readStep_core` plus one fact: a wording that `readCommand` reads as `one` has a body that begins with neither `If ` nor
`Then `. That fact traces the decoder, as follows.
- `readCommand_one_iff` and `candidate_reads_back` give an act `a` of a decoded predicate, with
  `fold (filled a fs) = fold body`.
- `splitLastIf`'s plain part begins with `If `/`Then ` when the wording does.
- `a` is `" ".intercalate (words …)` under both act checks: `canonicalAct`, and `Acts.Lexical.check` under `acts@0`.
- `actVerb a` relates its second word to `a` through `surfaceWords`. That needs `split_data` and `splitOn_space`.
- That word is not `if` or `then`: `actReserved` for `canonicalAct`, `check_no_clause` under `acts@0`.
- `checkTemplates` (`slotsApart`) keeps a slot from joining that word, and `fillHoles` copies the word unchanged.
  Without `slotsApart` the statement fails: the act `{0} then{1}` passes `canonicalAct`, and a definite " draft" in the
  free `sc` would read "Then draft." as `one`.

The estimate is about 300 more lines, which would take this item to about 800 hand-written lines.

**Does W1's act linter make `hs` unnecessary?** No; `hs` stays. This follows from what is proved.
- `readStep_core` uses `hs` once, and only to rule out the `seq` shape (`hsq`: the body has no `, then `).
- The act linter is needed only for the `If `/`Then ` shapes.
- The linter constrains the act phrase, which is the part before the last `, if `. It says nothing about the condition,
  so a `, then ` inside the condition is still possible, and only `hs` excludes it.
- This agrees with the spec's computed answer. ci-3bb proves the linter's half.

## Seeded bugs and mutants (`mutants.json`)

Each was planted, shown failing, and restored:
1. **S1 (Lean, `preposed_eq` fixture):** `capitalise` lower-cases the first letter (`c.toLower`) in
   `lean/VE/Commands/Steps.lean`. `lake build` fails at `StepsProofs.lean:122` (the rewritten wording
   "Click Ask, if draft is approved.") and at `StepsExamples.lean:40`.
2. **S2 (Lean, splitOn `#guard`):** the separator `", then "` is shortened to `", "` in the `#guard` at
   `lean/VE/Commands/SplitOnLemmas.lean:282`. That `#guard` fails to evaluate to `true`.
3. **S3 (Lean, the bridge):** `splitOnL` drops `sep.length - 1` characters at a cut instead of `sep.length`
   (`lean/VE/Commands/SplitOnLemmas.lean`). The bridge `#guard`s at lines 284-285 fail, and so do the proofs
   (lines 25 and 41).
4. **S4 (Python, `tools/layer_policy.py`):** the two modules are left out of layer 4.
   `python3 tools/check_lean_imports.py` exits 1 with "new outward Lean import: VE.Commands.StepsProofs ->
   VE.Commands.Steps". Restored, it exits 0.

## Trust, size, overlap

- Trust: pending. `tools/trust_map.py --check` is re-measured after the regen and recorded here.
- Size: `git diff --numstat` against the merge base. After deliverable (1), SplitOnLemmas.lean was 300 lines when first
  committed and is 287 now; StepsProofs.lean is 125; lean/VE.lean 1; tools/layer_policy.py 3. With this report and
  `mutants.json`, the item is about 520 hand-written lines.
- Overlap: lean/VE.lean (cmp-s3a-cfr-1, rights-cfr-4, sc-7, me-1) and tools/layer_policy.py (et-5, rights-cfr-4) are
  edited in flight elsewhere. Each change here is a one-line addition in its own place.
- Pilot bytes moved: 0 (proofs only).

FOLLOW-UP: ci-3bb readStep_conservative: the act linter's half (a read command begins with neither If nor Then)
