# ci-3a: the step reader (commands-imperatives section 7, CI-3's first part)

Status: built; six of section 7's eight statements proved, two moved whole to ci-3. Three DRI rulings shaped the
item: `Form`, the charged `.seq` product, and `readStep`'s byte charge (DELTA row 1, signed). No route calls `readStep`
yet, so no verdict, wording or pilot byte changes. No signature is reserved. Next item: ci-3 (the wiring,
`preposed_eq` and `readStep_conservative`).

## Delivered (spec 9a12df17a section 7; plan "CI-3. Steps and conditions written first")

- `lean/VE/Commands/Steps.lean`: `Shape` through `reads`.
  - Before the wording ruling, a probe compared all 14 definitions and the 6 proved statements with spec lines
    782-1126 after whitespace normalisation: 20 of 20 equal.
  - The only deviations since are signed (reviews/dri-decisions-20261109-ci-3a-wording.md item 1): `readStep`
    starts `if maxWordingBytes < (trimmed s).utf8ByteSize then .limit else`, and `hb` is added to `after_eq`,
    `seq_eq` and `shapes_ambiguous`.
  - There is no new limit literal (N7).
- `Form` is section 10's text; `Alt` names it (reviews/dri-decisions-20261109-ci-3a-form.md).
- The `.seq` product is charged before it is built (reviews/dri-decisions-20261109-ci-3a.md item 1).
  `shapeOutcomeCharged` counts `productSize` against `maxCandidates`, and the kernel-checked
  `@[csimp] shapeOutcome_charged` makes compiled code use it. The block sits before `readStep`, so its code calls the
  charged form. A first build with the block after `readStep` ran out of memory.
- Proved, with no `sorry` (`python3 lean/audit.py`: PASS, standard axioms only): `after_eq`, `seq_eq`,
  `shapes_ambiguous`, `seq_ambiguous`, `shapes_limit` and `shapes_complete`.
- `lean/VE/Commands/StepsExamples.lean`:
  - every row of "Fixtures (computed over `E_web`)";
  - the constructed aggregation rows: `[one, limit]`, `[one, one, limit]`, `many`-then-`one`, a stopped or refused
    step;
  - finding (d) (O8: code only);
  - the charges: the gate `#guard charge_installed%` (144); 8 steps of 64 readings give `limit`, read only when the
    charge is installed and counts (148); a 6 KB `If a, a, …` wording gives `limit`; 400 bytes read and 401 give
    `limit` (164-165); the `readingsBound` accept side.
- `lean/VE.lean` imports the module. `tools/layer_policy.py` puts the new modules on layer 4, like Read.
- `tools/trust-classes.json`: Steps.lean is G[V] (`conditionScope` is G[R]); `productSize` and
  `shapeOutcomeCharged` are tied; the fixtures are T.

## Moved to ci-3 (reviews/dri-decisions-20261109-ci-3a.md item 2)

`preposed_eq` needs `String.splitOn` lemmas for multi-character separators, which core Lean 4.24 does not have (about
200 lines). `readStep_conservative` also needs the act linter traced through `decodeSpeechEnvironmentFull`. Neither is
committed unproved or weakened. **Does W1's act linter make `hs` unnecessary?** ci-3a proved nothing about
`readStep_conservative`, so the spec's computed answer stands: `hs` stays. ci-3 answers it with the proof.

## Seeded bugs and mutants (Lean is the only product language changed)

`mutants.json` holds 21 hand mutants, each with its exact `old` and `new` text, and every one fails a fixture
(StepsExamples.lean lines):
- the task's four seeded bugs:
  - `shapes` dropping `preposed`'s condition fails 60-61;
  - the generic refusal for one shape fails 64;
  - `many` beside a `limit` fails 88;
  - first-step-only tuples fail 107-109 and 79;
- `readStep`'s byte test dropped fails 165; the `.one` arm of `combineShapes` dropped fails 100-101;
- `capitalise` 40, `hasThen` 42, `lift` 57-58, `conditionScope` 70-72, `shapeAlts` 174, `reads` 180-181;
- the constructor drops of `Form`, `Alt` and `StepOutcome` fail 177-179;
- `shapeOutcome` fails 72-73 and 144 with `@[csimp]` blanked, as trust_mutants does;
- `@[csimp]` dropped fails 144 and 148; the pre-count dropped runs out of memory under a 6 GB cap;
- `productSize` fails 133 and 148.

Trust mutants (`mac-pytest.sh --trustmut`, ve-cloud-3):
- the full run, `trust-mutants-full.json`: 175 KILLED, 20 SURVIVOR, 107 UNKNOWN, 36 INVALID;
- with `trust-mutants-allow.json` (36 entries), `--rescore`, `trust-mutants.json`: 175 KILLED, 127 ALLOWED,
  36 INVALID, exit 0.

The allowed mutants are:
- equivalent (`take 1` of a list of at most one, `isEmpty`);
- text Lean refuses;
- mutants that break `@[csimp] shapeOutcome_charged`. Every check computes through that lemma, so the tool judges
  them by proofs only, and the hand mutants above show the fixtures kill them;
- `shapeAlts` inlined into `combineShapes`.

## Trust (R16), size, pilot bytes

`uv run python tools/trust_map.py --check` against d55d24faab75: K +0, S +0, trusted +136 (lean/VE/Commands/Steps.lean).
It passes with the allowance in docs/trust-baseline.json, SIGNED by standing ruling R16; FOLLOW-UPS.md "## ci-3a" asks
for the ties pass. Size is 915 hand-written lines (`git diff --numstat $(git merge-base HEAD main)`, generated
files and tool outputs excluded), against the DRI's cap of about 850. Pilot bytes moved: 0; CI-3's +2 segments / 46 B
are counted when ci-3 wires the entry.
