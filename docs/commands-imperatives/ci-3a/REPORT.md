# ci-3a: the step reader (commands-imperatives section 7, CI-3's first part)

Status: built; six of section 7's eight statements proved, two moved whole to ci-3. Two charges were added by DRI
ruling: the `.seq` product, and the wording's bytes. No route calls `readStep` yet, so no verdict, wording or pilot
byte changes. DELTA.md has one signed row (changed approved statements). No signature is reserved.
Next item: ci-3 (the wiring, `preposed_eq` and `readStep_conservative`).

## Delivered (spec 9a12df17a section 7; plan "CI-3. Steps and conditions written first")

- `lean/VE/Commands/Steps.lean`: `Shape` through `reads`. All 14 definitions and the 6 proved statements were
  compared with spec lines 782-1126 after whitespace normalisation (probe, before the wording ruling: 20 of 20
  equal). Since then the only deviations are the ones the DRI signed:
  - `readStep` starts `if maxWordingBytes < (trimmed s).utf8ByteSize then .limit else`;
  - `hb` is added to `after_eq`, `seq_eq` and `shapes_ambiguous` (reviews/dri-decisions-20261109-ci-3a-wording.md
    item 1; DELTA row 1).
  No new limit literal (N7): `maxCandidates`, `readingsBound`, `maxWordingBytes`.
- `Form` is section 10's text, defined here because `Alt` names it (reviews/dri-decisions-20261109-ci-3a-form.md).
- The product is charged before it is built (reviews/dri-decisions-20261109-ci-3a.md item 1):
  - `shapeOutcome` stays as section 7 writes it;
  - `shapeOutcomeCharged` counts `productSize choices` against `maxCandidates` before it builds `readingTuples`;
  - `@[csimp] shapeOutcome_charged` (a kernel-checked equation) makes compiled code use the charged form;
  - the block comes before `shapeAlts`, so that `readStep` and `reads`, compiled after it, call the charged form.
    A first build with the block after `readStep` was killed for running out of memory (exit 137).
- Proved, with no `sorry`: `after_eq`, `seq_eq`, `shapes_ambiguous`, `seq_ambiguous`, `shapes_limit` and
  `shapes_complete`.
- `lean/VE/Commands/StepsExamples.lean`:
  - every row of "Fixtures (computed over `E_web`)": `Then` gives `afterPrevious`; "If draft is approved, click
    Ask." equals `readCommand` of "Click Ask, if draft is approved."; the approvable row equals the rewritten form's
    `NoDerivation`, whose text names 'is approvable'; the two `ConditionScope` rows give the exact text; "Review the
    meaning, then click Ask." is `many` with two `.seq` alternatives, each ending in `click_ask_required`;
  - the constructed aggregation rows: `[one, limit]` gives `limit`; `[one, one, limit]` gives `many`; a `many`
    step then a `one` step keeps the second reading in every tuple; a stopped step at budget 0 gives `limit`,
    unless a step refused;
  - finding (d): step outcomes [`one click_ask_required`, `InvalidInput`], with only the code checked (O8);
  - the charges: 8 steps of 64 readings give `limit`, read only after the `#eval` (line 132) sees the `@[csimp]`
    installed and `productSize` counting; a 6 KB `If a, a, …` wording gives `limit`; two steps over 400 bytes give
    `limit`; the `readingsBound` accept side is tested through both `combineShapes` and `.seq`.
- `lean/VE.lean` imports the new module. `tools/layer_policy.py` puts Steps and StepsExamples on layer 4, like Read.
  In `tools/trust-classes.json`, Steps.lean is G[V] (`conditionScope` is G[R]), `productSize` and
  `shapeOutcomeCharged` are tied to `readingTuples_length` and `shapeOutcome_charged`, and the fixtures are T.

## Moved to ci-3 (reviews/dri-decisions-20261109-ci-3a.md item 2)

`preposed_eq` needs `String.splitOn` lemmas for multi-character separators: a `splitOn ", "` piece holds no `, `, so
`hasThen (x ++ ".") = false`. Core Lean 4.24 has none (about 200 lines). `readStep_conservative` also needs the act
linter traced through `decodeSpeechEnvironmentFull`. Neither is committed unproved or weakened. **"Does W1's act linter
make `hs` unnecessary?"**: ci-3a proved nothing about `readStep_conservative`, so the spec's computed answer stands
(`hs` stays); ci-3 answers it with the proof. The conservative fixture row holds: "Click Check rule conflict." is
`one click_check_required false`.

## Seeded bugs and mutants (Lean is the only product language changed)

`mutants.json` holds 21 hand mutants, each with its exact `old` and `new` text. For each it lists the
`StepsExamples.lean` checks that fail and the proofs that break, with Steps.lean's proofs cut and the charge's
`@[csimp]` kept. Every mutant fails a fixture. The task's four seeded bugs:
- `shapes` dropping `preposed`'s condition fails 60-61 ("If draft is approved");
- the generic refusal for one shape fails 64 (approvable);
- `many` beside a `limit` fails 88 (`[one, limit]`);
- first-step-only tuples fail 102-104 and 79.

The other definitions:
- `capitalise` 40, `hasThen` 42 and 70, `lift` 57-58 and 158, `conditionScope` 70-72, `shapeAlts` 163, `reads`
  169-170;
- `combineShapes` (its `.one` arm) 100;
- `readStep` (the byte test) 154;
- `shapeOutcome` 72 and 73 (with `@[csimp]` blanked, as trust_mutants does);
- `Form`, `Alt` and `StepOutcome` (constructor drops) 166-168; `Shape` (constructor drop) does not compile;
- `shapeOutcomeCharged`: without `@[csimp]`, 132; without the pre-count, out of memory under a 6 GB cap;
- `productSize` 128 and 132.

## Trust (R16), size, pilot bytes

`uv run python tools/trust_map.py --check` against d55d24faab75 gives K +0, S +0, trusted +136, all in
lean/VE/Commands/Steps.lean, and passes with the allowance in docs/trust-baseline.json. That allowance is SIGNED by
standing ruling R16, and the FOLLOW-UPS.md row "## ci-3a" asks for the ties pass. Every new trusted definition fails a
fixture under its mutants (above). The `trust_mutants` sweep is in `trust-mutants.json`.

Size, by `git diff --numstat $(git merge-base HEAD main)` without generated files: 849 hand-written lines at
7077a3447 plus this REPORT's edits, under the DRI's raised cap of about 850 (wording ruling, item 2). Pilot bytes moved: 0. CI-3's +2 segments / 46 B are counted when ci-3 wires the entry.
