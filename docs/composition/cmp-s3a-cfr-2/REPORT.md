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
reads `Dr`'s own lines, and the `#guard`s at Examples.lean:260 and 262 pin that case.

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
| Trust under R16 | yes, V +15 under two signed R16 allowances | Trust below |

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
| S1 the duplicate check removed | `… then e` → `… && false then e` (main's text) | `test_clause_entries_preserve_duplicate_rule_diagnostic`, `test_clause_entries_take_rights_first_duplicate_text` (`2 failed, 2 passed`); `#guard`s Examples.lean:222, 223, 224, 256 |
| S2 a one-character edit of rights' text (the DRI's negative test) | `then e` → `then e ++ "."` | the same two tests (`2 failed, 2 passed`); `#guard`s Examples.lean:222, 223, 224, 256 |
| S3 any rights fault relayed | the conjunct `e.startsWith "DuplicateDeclaration: "` removed | `test_clause_entries_keep_invalid_clauses_when_rights_faults_first` (`1 failed, 3 passed`); `#guard` Examples.lean:226 |
| S4 one line counts as a duplicate | `.length > 1` → `.length > 0` (on the earlier filter-and-length count) | `test_clause_entries_keep_invalid_clauses_when_rights_faults_first` (`1 failed, 3 passed`); `#guard`s Examples.lean:234, 262 |

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

`uv run python tools/trust_map.py --check` against 6db6ee16ddb1 (the merge base) gives `K +0, S -1, D +0, G +0,
tied +0, unclassified +15, trusted +14`. Per file: lean/VE/RightClauses/Plain.lean +12 (`entryError`, unclassified)
and lean/VE/RightClauses/Examples.lean +3 (the fixtures `twice`, `twoHolders` and `across`, unclassified). The check
prints `PASS: K, S and untied [V] within 6db6ee16ddb1 and the allowances introduced since`.

Two allowances are recorded in docs/trust-baseline.json, V +14 and V +1, for 15 lines in all. Both are signed "SIGNED
by standing ruling R16 (DRI-RULINGS.md), cmp-s3a-cfr-2, 2026-10-18". That is within R16: at most 150 lines and no K
growth. The FOLLOW-UPS.md row "## cmp-s3a-cfr-2" asks for the ties pass and for the classes (S for `entryError`, T
for the fixtures).

R16's "every new trusted definition exercised by a test that can fail" is met:
- Hand mutants: [mutants.json](mutants.json), S1-S4, all killed.
- Mechanical mutants: `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --json
  docs/composition/cmp-s3a-cfr-2/trust-mutants.json --test lean/VE/RightClauses/Examples.lean`.
  - The first run (head d989168f) gave `29 KILLED, 2 SURVIVOR, 2 UNKNOWN`, all in `entryError`. The survivors were
    `Dr.rs` → its first or last right only, and no fixture had the duplicate across two rights. The unknowns were two
    `list-empty` mutants that did not elaborate, because the lambdas were untyped.
  - The fixes: the `across` fixture (Examples.lean:228-230, the rule on a line of each of two rights), and a count
    written as `countP` with typed lambdas, so the `list-empty` mutants elaborate and are killed.
  - The second run used `--rescore` on the first run's evidence. The tool made it a full run because Examples.lean
    changed (head 7d9a17e79): `36 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 0 ALLOWED, 0 NOT RUN`, exit 0. Its
    evidence is [trust-mutants.json](trust-mutants.json). No allow file is needed.

Hand bugs S1-S4 were run on the filter-and-length form of the count, before it became `countP`. The final form is
covered by the second trust-mutants run above.

## Final checks (on the final code)

- `cd lean && lake build`: `Build completed successfully (1320 jobs)`.
- `python3 lean/audit.py`: `PASS: 790 source files; 8746 named theorem declarations audited`.
- These two ran on the code before the `across` fixture and the `countP` count. That later change was built with
  `lake build VE.RightClauses.Examples` (`Build completed successfully`), and the trust-mutants run built it again.
- `uv run python tools/regen_generated.py --write`: rc 0. Only the docs/codemap files changed; they are committed.
- Selected tests: see the last section.

## Pilot bytes

Estimate: 0. Right-clauses has no service mode or relay yet, so no pilot document reaches this head. Nothing is
claimed before a pilot audit.

## Next item

None.

## Selected tests

PENDING: the final selected run on the committed tree.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A. This item adds no relayed answer, service mode or response field; the head
   is reached only from Lean.
2. Every deliverable built, no rule broken: PASS. See the task-line table above. One owner: rights' text is read from
   `VE.Rights.checkRights` and not copied. In-flight overlap was checked with `git diff --name-only main...<branch>`
   over feature/*, lean-first/*, infra/* and foundation/*. Only cmp-s3a-cfr-1 is near: it adds new PlainWellFormed
   files and tests/test_right_clauses_lean.py. This item uses its own test file, and the `entry_typed` proof shape is
   checked above.
3. Tests can fail: PASS. Hand bugs: [mutants.json](mutants.json), S1-S4, each failing a named test and `#guard`s.
   Mechanical bugs: trust-mutants.json, 36 KILLED, 0 SURVIVOR.
4. Python, Lean and Rust agree; valid inputs still pass: PASS. Lean only. The accepting `#guard`s of Examples.lean
   still hold (`lake build`). The candidate `ok` guards at Examples.lean:249 and 270 are unchanged.
5. R8 binding: N.A. No Python reads a field of this answer.
6. Gate evidence matches the final HEAD: PASS. The final selected run is on the committed final tree (below), and
   the chain runs the gate.
7. No unsigned item: PASS. DELTA row 1 cites R1. Row 2 is SIGNED by the DRI 2026-11-09 (lp0801 item 1), with the
   condition test and S2 as the negative test. The trust growth is under R16, signed. No signature is reserved.
8. Every user-visible change in DELTA: PASS. There are two rows, and the inputs whose text does not change are named
   (DELTA.md "What does not change"). No corpus reaches the head (no mode).
9. Test selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` maps the changed Lean and
   tests/test_right_clauses_duplicate.py (the final selected run includes that file; see below).
10. Lean statements: PASS. No theorem statement changed. `checkEntry_ok`, `entry_facts` and `plain_guard` build
    unchanged. `lean/audit.py` PASS.
11. Budgets fail closed: N.A. No budget, limit or deadline is touched. `entryError` evaluates `checkRights Dr` once,
    only on the refusal path.
12. CPU or memory: N.A. The new work runs only when an entry is already refused.
13. Test-removed trailer: N.A. No test that exists on main is removed or renamed. `test_same_bytes_refuses_every_one_character_edit`
    was added and dropped within this branch, and the merge base never collected it.
14. Both directions, cited evidence, spec re-read: PASS. Each change has its opposite-direction fixture: the duplicate
    on two lines (changed) against one line, a non-duplicate first fault, and a `.rightLines` candidate (kept). Each
    claim cites its command above. The spec re-read is the section above.
15. Overclaim, silent cut, every check can fail, limits: PASS.
    - The universal words in REPORT and DELTA ("no verdict changes", "every other `entryOk` failure keeps the base
      text") rest on `entryError` returning `invalid` in every branch but one, and on `checkEntry`'s unchanged
      `if`/`else`.
    - No deliverable is cut.
    - Every new `#guard` and test has a killing mutant (S1-S4, trust-mutants).
    - Limits are N.A.
