# cmp-s3a-cfr-2: a duplicate rule name gets rights' DuplicateDeclaration text

No DRI signature is reserved. DELTA row 1 cites R1. Row 2 is pre-signed by the DRI 2026-11-09
(reviews/dri-decisions-20261109-lp0801.md item 1), and its condition and negative tests are named in DELTA.md.

Item: L1-graded follow-up of right-clauses@0 (regrade #9, reviews/l1-c-regrade-rights-20261109.md, an overclaim).
The plan is docs/spec/right-clauses.md on main, and the diagnostic order is rights' `checkRights`
(lean/VE/Rights/Correlate.lean:358-370).

## The defect

docs/composition/cmp-s3a/REPORT.md:44 and the docstring of `entryOk` in lean/VE/RightClauses/Plain.lean both said:
"the wire decoder builds one entry per line, so a decoded document never shows `InvalidInput: invalid clauses of rule
<n>`". That is false. Two source lines with one rule name, each with its entry (the shape a one-entry-per-line decoder
builds), fail `entryOk`. They got `InvalidInput: invalid clauses of rule <n>` where rights says
`DuplicateDeclaration: rule <n>`. The wire decoder the claim names does not exist yet (cmp-s3-cfr-1).

## Which deliverable (task (1)): the Lean fix, without the wire decoder

The fix needs no wire decoder. `checkEntry` is reached from `checkClauses` and `checkCandidates` on a `ClauseDoc`.
When an entry fails `entryOk`, it now answers with `entryError Dr <n>` (lean/VE/RightClauses/Plain.lean), where `Dr`
is the rights document that holds the entry's right.

- If `<n>` is the rule of more than one line of `Dr`'s rights (the lines rights' own name check reads), and rights'
  first fault on `Dr` (`VE.Rights.checkRights Dr`) is a `DuplicateDeclaration`, the answer is that text, unchanged.
  It is rights' text in rights' order (8). Lean reads it from rights' function, so it is not a copy.
- Otherwise the answer is still `InvalidInput: invalid clauses of rule <n>`. That covers an entry of an unknown
  right, an entry that names no line of its right, two entries for one line, a `.rightLines` candidate whose own
  lines repeat a rule (they are not in `Dr`), and a rule on two lines where rights faults first on something else.

Rights' diagnostics are strings, so `entryError` reads the kind from the text's `DuplicateDeclaration: ` prefix
(noted in its docstring). A structured rights result would need a change in Correlate.lean, whose `checkRights` is
restated by `rfl` in lean/VE/Readings/Lines.lean (`checkRights_steps`). That change is out of this item's paths.

The first draft counted the duplicate in the entry's source lines (`src`). The self-review found that for a
`.rightLines` candidate those lines are not in `Dr`, so an unrelated fault of `D.doc` could come back. The count now
reads `Dr`'s own lines, and the `#guard`s at Examples.lean:255 and 257 pin that case.

The other step-3 checks of 4.1 keep their order. The entry is refused at the same place as before, and
`checkEntry`'s `if`/`else` shape is unchanged. So `checkEntry_ok`, `entry_facts` and `plain_guard` compile without
edits (`lake build VE.RightClauses.Examples`: `Build completed successfully`). cmp-s3a-cfr-1 (in flight) has an
`entry_typed` that unfolds `checkEntry` the same way:
`git show feature/cmp-s3a-cfr-1:lean/VE/RightClauses/PlainWellFormed/Clauses.lean`, lines 224-229
(`unfold checkEntry at he; split at he; · rename_i Rt _; split at he; · cases he`). That proof does not depend on
the error text. No theorem statement changed.

lean/VE/RightClauses/Examples.lean is outside the Paths column, but this item has to touch it. Its `#guard` at the
old :217 pinned `InvalidInput: invalid clauses of rule equal-access` for two lines with one rule. The build fails
until that guard says rights' text, and the new fixtures live beside it.

The corrections (task (3)):
- docs/composition/cmp-s3a/REPORT.md:44 gets a correction line. The false sentence is withdrawn, and the line says
  what is now true.
- Plain.lean: `entryOk`'s docstring no longer says the text is never shown. The module docstring no longer names a
  `Wire.lean`; it gives the decoding texts to the right-clauses wire decoder (cmp-s3-cfr-1). `entryError` documents only what the code does.
- lean/VE/RightClauses/Examples.lean: the section heading "Entries (never shown for a decoded document)" is withdrawn
  for the same reason.

## Plan rows and task lines

| Task line | Delivered | Where |
|---|---|---|
| (1) a duplicate rule name in a structured document gets rights' DuplicateDeclaration diagnostic (Lean, the rights owner's order); say which | yes, the Lean fix, no decoder needed | `entryError`, `checkEntry` (Plain.lean) |
| (2) test `test_clause_entries_preserve_duplicate_rule_diagnostic`, failing on main first | yes | tests/test_right_clauses_duplicate.py. With main's Plain.lean it fails: `FAILED …::test_clause_entries_preserve_duplicate_rule_diagnostic`, `FAILED …::test_clause_entries_take_rights_first_duplicate_text`, `2 failed, 2 passed` (main's Plain.lean checked out, `lake build VE.RightClauses.Plain`, `VE_NATIVE_PREBUILT=1 VE_LEAN_PREBUILT=1 uv run pytest -q tests/test_right_clauses_duplicate.py`, then restored) |
| (3) the REPORT and Plain.lean docstrings say only what is proved | yes | the corrections above |
| Seeded bug: Lean, the duplicate check removed | yes | S1 below |
| DELTA: R1 when the text keeps the rule name, path and specificity; else SIGNED by the DRI only at rights' exact text, with a negative test | yes | DELTA.md rows 1 and 2 |
| Trust under R16 | see Trust | |

The tests live in their own file, because cmp-s3a-cfr-1 (in flight) adds tests/test_right_clauses_lean.py. The Lean
probe imports `VE.RightClauses.Plain` and `VE.Rights.Examples` only, so a seeded bug shows as a failed assertion and
not as a build failure of Examples.lean's `#guard`s.

## Seeded bugs (Lean; no Python or Rust product code changed)

Each bug was planted in lean/VE/RightClauses/Plain.lean (`entryError`) and tested two ways:

1. `lake build VE.RightClauses.Plain`, then `VE_NATIVE_PREBUILT=1 VE_LEAN_PREBUILT=1 uv run pytest -q
   tests/test_right_clauses_duplicate.py`.
2. `lake build VE.RightClauses.Examples`, which fails on the listed `#guard`s.

Each bug was then restored, and `cmp` against the saved original matched. Full list: [mutants.json](mutants.json).
With main's Plain.lean, the condition test fails as well (task (2)).

| Bug | Mutation | Fails |
|---|---|---|
| S1 the duplicate check removed | `… then e` → `… && false then e` (main's text) | `test_clause_entries_preserve_duplicate_rule_diagnostic`, `test_clause_entries_take_rights_first_duplicate_text` (`2 failed, 2 passed`); `#guard`s Examples.lean:222, 223, 224, 252 |
| S2 a one-character edit of rights' text (the DRI's negative test) | `then e` → `then e ++ "."` | the same two tests (`2 failed, 2 passed`); `#guard`s Examples.lean:222, 223, 224, 252 |
| S3 any rights fault relayed | the conjunct `e.startsWith "DuplicateDeclaration: "` removed | `test_clause_entries_keep_invalid_clauses_when_rights_faults_first` (`1 failed, 3 passed`); `#guard` Examples.lean:226 |
| S4 one line counts as a duplicate | `.length > 1` → `.length > 0` | `test_clause_entries_keep_invalid_clauses_when_rights_faults_first` (`1 failed, 3 passed`); `#guard`s Examples.lean:230, 257 |

## Spec re-read

- 4.1 step 3 ("the first failure is the answer") against docs/spec/right-clauses.md:203-205. The duplicate entry is
  refused at its place in that order, as before.
- 4.1 step 6 ("the rights checks run there with their own texts") against docs/spec/right-clauses.md:208-210. The
  new text is rights' own text from `checkRights`.
- Section 7's `InvalidInput: invalid clauses of rule <n>` row ("`clauses` is `[]` or not a list", a decoding row)
  against docs/spec/right-clauses.md:283. No row of section 7 covers a duplicate rule. Rights' 8 order is
  lean/VE/Rights/Correlate.lean:358-370 (checkBlock, ResourceLimit, the `rights-` prefix, then `DuplicateDeclaration`
  right / limitation / bar / rule).

## Trust (R16)

PENDING (written after the regen): measured with `uv run python tools/trust_map.py --check` on the final HEAD.

## Pilot bytes

Estimate: 0. Right-clauses has no service mode or relay yet, so no pilot document reaches this head. Nothing is
claimed before a pilot audit.

## Next item

None.
