# ps-2ac: Run.lean, the presuppositions report value (spec 4.7, PS-2a part 4) (build report)

No DRI signature is reserved in this item. There are no DELTA rows (DELTA.md): no route reads the report until PS-4.
Status: built: `lean/VE/Presupposition/Run.lean`: `shown`, the value PS-4 puts in the document mode's answer, read off
`admit`, with 28 guards over A1-A28 documents. Trust: TRUST_SUMMARY. Selected tests: SELECTED_SUMMARY.
DRI ruling: reviews/dri-decisions-20261110-ps-2ac-layer.md (the layer; see "Layer"). Next: ps-4.

Feature item ps-2ac (task: prompts/task-ps-2ac.txt, deliverable (4) of task-ps-2ab.txt; plan
`docs/spec/presupposition-PLAN.md` "PS-2a" (:847-864) and 4.6 (:498-501); spec `docs/spec/presupposition.md` 4.7
(:837-839), 2.3 (:345-363) and 5 (:1303-1321)). Branch `feature/ps-2ac`, merge base a5088a09b (main, ps-2ab merged).
Command outputs: `evidence/tests.txt`.

## Preconditions

- **ps-2ab merged.** `admit : PDoc → Except String Report`, `admitWith`, `admitWrapped` and A1-A28 are on main
  (Admit.lean:282-293, Examples.lean:734-1130). No type Run.lean needs was missing.
- **Statement gate.** PASSED, as the task states. Probe (`evidence/probe.py`, output in `evidence/tests.txt`): Run.lean's
  25 declarations, comments stripped and whitespace normalised, against every Lean block of the spec and the PS-S stub:
  **none is named there** (the spec and stub define no Run.lean declaration), so none can differ. ps-2ab's probe rerun:
  the 19 statements are still 19/19 equal to spec 4.7. No statement changed.
- **Read-only files.** Admit.lean, Wire.lean, Frame, Reading, Rows, Rules, Agree, `Protocol.lean` and
  `service_schema.py` are unchanged (`git diff --name-only main...HEAD`). No guard exposed an `admit` bug.
- **In-flight overlap.** No branch in flight touches `lean/VE/Presupposition/Run.lean`. feature/cmp-s3-cfr-1,
  feature/en-e3a and feature/ps-7 also add entries to `tools/trust-classes.json` and `docs/trust-baseline.json`;
  this item inserts its entry beside Admit.lean's, away from the end where they append.

## Plan rows delivered

| Row (plan PS-2a :854-858; task "Deliver") | Where | Evidence |
|---|---|---|
| one row per obligation, in the block's order | `shownOf` (Run.lean) | block-order guard and its reverse (Run.lean:129-131); S1 |
| `id`, `unit`, `carrier` | `checkedRow`, `refusedRow` | Run.lean:129 (A18b), :161 (A20); S2, M-refusedRow-unit |
| `goal`: the P0 wire formula and its English line, rendered by Lean | `Goal`, `englishLine`, `lineOf` | A24 row :135; `admit`'s goals :138; lines :141-157; M-englishLine, M-lexicon |
| `outcome` (checked, or the diagnostic) | `Outcome`, `outcomeOf` | :133 (checked), :161-164 (refused), :166-168 (A15: UNKNOWN) |
| unresolved: the emitted readings, each with its aliases | `checkedRow` | A1 :175; R-1 alias `inPlace` on the conditioned reading :184-186 |
| `PresuppositionRefuted` lines from the existing inconsistency report | `Inconsistency`, `refutedLines` | :196-202; S3 |
| no runMode line, no MODES entry, no schema, no Python relay (DRI PS-C9) | — | `git diff --name-only main...HEAD` ("Final checks") |
| `tools/trust-classes.json` rows; `lean/VE.lean` import; generated inventories | side table; `regen_generated.py --write` | "Trust", "Final checks" |

## What the value is

`shown L inc D := shownOf L inc D (admit D)`, `none` without the block (as `admitWrapped`). PS-4 passes the request's
lexicon `L` (`VE.English.Run.decodeLexicon` decodes one) and the document's inconsistency report `inc`; for the
document's situations it calls `shownOf` with `admitWith` (as ps-2ab's REPORT says). Choices the plan leaves open:

- **Outcome per row.** `admit` answers the block's first failing step, so every row carries the block's outcome:
  `checked`, `refused <diagnostic>`, or `unknown "ResourceLimit: presuppositions"` (spec 5: UNKNOWN, never a refusal).
  A refused block has no regenerated goal, so its rows carry `goal := none`. Naming only the obligation the diagnostic
  names would mean parsing `admit`'s text; the diagnostic itself names it.
- **The goal.** The formula is kept typed (`VE.Formula`); PS-4's encoder writes P0's wire form (`encodeFormula`). The
  English line is the core renderer's clause (`renderStatement … |>.yield`, no full stop, so 2.3's lines can quote it),
  shown only when the sentence parses back, in the document's environment, to exactly the goal (checklist 9: nothing
  is displayed without passing the parser). Otherwise it is `none` (guards: an uncovered predicate, a wording that
  reads as another predicate's).
- **Refuted.** The existing inconsistency report is P0's: a premise list and an inconsistency certificate on it
  (`PremiseStatus.inconsistent`, lean/VE/SpeechActs/Run.lean:242-246). When the certificate checks, each admitted
  assumed obligation whose goal is one of those premises gets `PresuppositionRefuted: <o>: <unit>`, in block order:
  the other premises refute that goal. Not for other carriers, a refused block, or a certificate that does not check.
- **Readings.** An admitted unresolved obligation's row lists its unit's readings (`RReading`: candidate, aliases,
  content, premise). `admit` has checked that they are exactly `expectedReadings`.

## Layer (reviews/dri-decisions-20261110-ps-2ac-layer.md)

The only Lean renderer of a formula is `VE.English.render` (layer 3). I asked the DRI before building (msg.sh dri
ps-2ac). It signed option (1): Run.lean declares layer 3 on its first line. `tools/check_lean_imports.py` refused that
declaration: "VE.Presupposition.Run's role fixes its layer at 4 (an entry point, a runner or the service); remove the
layer declaration" (`tools/layer_policy.py:357`: every module ending `.Run` is layer 4). So Run.lean has no declaration
and is at layer 4 by role, and its import of `VE.English.Render` is inward. The ruling's conditions hold: no
`layer_policy` edit and no ledger exception; no layer-2 module imports Run (the check refuses any lower-layer importer);
the check passes ("Final checks"); and the renderer and lexicon guards have mutants (M-englishLine, M-lexicon). I told
the DRI (msg.sh, 2026-11-10T10:48Z).

## Points for the DRI (no ruling needed for this item)

- **An open set with assumed and conditioned at a shallow frame is never admitted.** At a negated or antecedent frame
  the assumed reading's content `B` and the conditioned `U → B` are equivalent (B implies U there), so no situation
  separates them and step 5 answers `distinguishing model does not separate readings`. That holds for the fixture
  table's negated cell `[assumed, conditioned, inPlace]`, which is the only cell that gives an alias. The aliases
  guard therefore uses a cell `[conditioned, asserted, inPlace]` (Run.lean:179-186). FOLLOW-UPS row under "## ps-2ac".
- **Run.lean imports `VE.Presupposition.Examples`** for its guards over A1-A28 (the task puts the guards in
  Run.lean). PS-4's import of Run therefore also brings in the fixtures. A `RunExamples.lean` split is a one-file move.

## Seeded bugs (Lean only; this item changes no Python or Rust product code)

Each mutant in `mutants.json` was applied alone and `lake build VE.Presupposition.Run` was run; the first failing
guard is in `evidence/tests.txt`; then the file was restored. 27 mutants, all fail.

| Id | Behaviour | File, definition | Fails |
|---|---|---|---|
| S1-drop-row (task) | one row per obligation, block order | Run.lean `shownOf` | Run.lean:129 block-order guard |
| S2-unit-carrier (task) | unit and carrier are the obligation's | Run.lean `checkedRow` | Run.lean:129 field guard |
| S3-no-refuted (task) | the PresuppositionRefuted line | Run.lean `refutedLines` | Run.lean:196 refuted guard |
| M-englishLine | the line is the clause, no full stop (renderer) | `englishLine` | :135 A24 row |
| M-englishLine-parse | a line is shown only if it parses back | `englishLine` | :147 uncovered predicate |
| M-lexicon | the line follows the lexicon's wording | `lexA` (fixture) | :135 A24 row |
| M-outcomeOf | ResourceLimit is UNKNOWN | `outcomeOf` | :166 A15 |

S2: a literal swap of `carrier` (a `Carrier`) and `unit` (a `String`) does not elaborate, so the mutant reads the
unit off the carrier (`c.ob.carrier.unitName`). One mutant per other new definition is in `mutants.json`:
`refutedLines` (3 more), `checkedRow` (3), `refusedRow` (2), `shownOf` (2), `shown`, `lineOf` (2), `maxLineTokens`,
`englishLine` (limit), `Row` (fields `id` and `unit` swapped). `Outcome`, `Goal`, `Shown` and `Inconsistency` are data
types: dropping a constructor or field does not elaborate, and no change that elaborates alters behaviour. Each is
read by named guards (`Outcome` :133 and :166, `Goal` :135, `Shown` :172 and :198, `Inconsistency` :196-202).

## Trust

TRUST_SECTION

## Size, bytes, evaluators

- **Size** (`git diff --numstat a5088a09b`, without generated files): SIZE_LINE
- **Pilot bytes.** 0: no route reads the report yet.
- **Evaluators** (the DRI's rule of 2026-10-27). `shown` reads `admit`'s answer once. `admit` has already charged the
  block (256 obligations: A15) and each goal (W1's 10,000 nodes). Each goal is rendered once. Its line is charged
  against `maxLineTokens` (400) before it is parsed, because the core parser's work grows faster than the line:
  interpreted, a 9,611-node goal took 3.5 s to parse back, against 55 ms at 611 nodes (`lake env lean` probe, not a
  benchmark). Fixtures: 256 obligations give 256 parsed lines (:169); 257 give 257 UNKNOWN rows and no parse
  (:166-168); a 376-token line is parsed and a 431-token one is not (:154-156). The inconsistency certificate is
  checked once per report, not per row.

## Spec re-read

- Rows against plan PS-2a `presupposition-PLAN.md:854-858`: id, unit, carrier; goal with its wire formula and English
  line rendered by Lean; outcome (checked, or the diagnostic); for unresolved obligations the emitted readings with
  aliases; the `PresuppositionRefuted` lines. Each has a row above.
- `PresuppositionRefuted: <o>: <unit>` against `presupposition.md:361-362` and `:1321`: obligation id, then the
  assumed unit; a report line, not a diagnostic (it is in `refuted`, not in an outcome).
- "Where the report goes" `:837-839`: no mode, runner or schema of its own; the field is absent without the block, as
  `admitWrapped` (Admit.lean:293), guard :172.
- Spec 5 `:1320`: `ResourceLimit: presuppositions` is UNKNOWN, never a rejection: `Outcome.unknown`, guard :166.

## Final checks

FINAL_CHECKS

## Self-review against BUILDER-CHECKLIST

SELF_REVIEW
