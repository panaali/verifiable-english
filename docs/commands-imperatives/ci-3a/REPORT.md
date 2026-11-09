# ci-3a: the step reader (commands-imperatives section 7, CI-3's first part)

Status: built; six of section 7's eight statements proved, two moved whole to ci-3 (DRI ruling below). No route calls
`readStep` yet, so no verdict, wording or pilot byte changes, and there is no DELTA.md. No DRI signature is reserved.
Next item: ci-3 (wiring, plus `preposed_eq` and `readStep_conservative`).

## Delivered (spec 9a12df17a section 7; plan "CI-3. Steps and conditions written first")

- `lean/VE/Commands/Steps.lean`: `Shape` through `reads`, each equal to section 7's text after whitespace
  normalisation (a probe compared all 14 definitions and the 6 proved statements with spec lines 782-1126: 20 of 20
  equal). `many` holds at most `readingsBound`; the product is capped at `maxCandidates`; there are no new literals.
- `Form` is section 10's text, defined here because section 7's `Alt` names it (reviews/dri-decisions-20261109-ci-3a-form.md:
  CI-6 reuses it; ci-3a defines no `forms`).
- Charged product (reviews/dri-decisions-20261109-ci-3a.md item 1): `shapeOutcome` stays as section 7 writes it.
  `shapeOutcomeCharged` counts `productSize choices` against `maxCandidates` before it builds `readingTuples`. The
  kernel-checked `@[csimp] shapeOutcome_charged` proves the two equal, so compiled code (`#guard`, later the runner)
  evaluates the charged form. The block sits before `shapeAlts`: `readStep` and `reads` are compiled after it, and
  only code compiled after a `csimp` lemma uses it. The first build, with the block after `readStep`, ran out of memory.
- Proved, with no `sorry`: `after_eq`, `seq_eq`, `shapes_ambiguous`, `seq_ambiguous`, `shapes_limit` and
  `shapes_complete`, with helper lemmas (`readingTuples_single`, `seq_many`, `shapeOutcome_many`,
  `readStep_one`, `readStep_combine`).
- `lean/VE/Commands/StepsExamples.lean` (`#guard`s):
  - every row of "Fixtures (computed over `E_web`)": the `Then` rows have `afterPrevious`; "If draft is approved,
    click Ask." equals `readCommand` of "Click Ask, if draft is approved."; the approvable row's code and text equal the
    rewritten form's (`NoDerivation`); both `ConditionScope` rows give the exact text; "Review the meaning, then click
    Ask." is `many` with two complete `.seq` alternatives, each ending in `click_ask_required`;
  - the constructed aggregation rows (`[one, limit]` gives `limit`; `[one, one, limit]` gives `many` with both; a
    `many` step followed by a `one` step keeps the second reading in every tuple; a stopped step at budget 0 gives
    `limit`, and a refusal wins);
  - finding (d): "Click Ask, then add an exception or precedence." has step outcomes [`one click_ask_required`,
    `InvalidInput`], and only the code is checked (O8);
  - the charge (`wideEnv`, 64 spellings of `review`): eight steps of 64 readings (64^8 products) give `limit` in
    about 22 s of build time, and two steps (4096 products) give `limit` by the `readingsBound` check.
- `lean/VE.lean` imports the module. `tools/trust-classes.json`: Steps.lean is G[V] (`conditionScope` is G[R]) and the
  fixtures are T.

## Moved to ci-3 (reviews/dri-decisions-20261109-ci-3a.md item 2, under the task's seam clause)

`preposed_eq` needs `String.splitOn` lemmas for multi-character separators: a `splitOn ", "` piece holds no `, `, so
`hasThen (x ++ ".") = false`. Core Lean 4.24 has none (about 200 lines). `readStep_conservative` also needs the act
linter traced through `decodeSpeechEnvironmentFull`. Neither is committed, unproved or weakened. **"Does W1's act linter
make `hs` unnecessary?"** ci-3a proved nothing about `readStep_conservative`, so the spec's computed answer stands
(`hs` stays). ci-3 answers it with the proof. The fixtures confirm the conservative row: "Click Check rule conflict."
is `one click_check_required false`.

## Seeded bugs and mutants (Lean is the only language changed)

`mutants.json` has 18 hand mutants, at least one per new trusted definition, and each one fails. Four are the task's
seeded bugs:
- `shapes` dropping `preposed`'s condition fails the "If draft is approved" equality guards (StepsExamples.lean 60-61);
- `readStep` returning the generic refusal for one shape fails the approvable guard (64);
- `combineShapes` giving `many` from one alternative beside a `limit` fails `[one, limit]` (86);
- `readingTuples` keeping only the first step's readings fails the `many`-then-`one` guards (96-97, 77).

Without `@[csimp]`, the 8-step guard runs out of memory under a 6 GB address-space cap. Dropping the pre-count breaks
`shapeOutcome_charged`. Every mutant of `shapeOutcomeCharged`'s term breaks that proof before the fixtures build, so
no sweep mutant can run the eager product.

## Trust (R16), size, pilot bytes

TRUST-PLACEHOLDER

Size: `git diff --numstat $(git merge-base HEAD main)`, hand-written lines (SIZE-PLACEHOLDER). The DRI allows about
700 for the charge (ruling item 1). Pilot bytes moved: 0. CI-3's +2 segments / 46 B are counted when ci-3 wires the
entry.
