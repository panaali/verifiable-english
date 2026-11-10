# ps-2ac: Run.lean, the presuppositions report value (spec 4.7, PS-2a part 4) (build report)

No DRI signature is reserved in this item. There are no DELTA rows (DELTA.md): no route reads the report until PS-4.
Status: built at HEAD_LINE: `lean/VE/Presupposition/Run.lean`: `shown`, the `presuppositions` field PS-4 puts in the
document mode's answer, read off `admit`, with 32 guards (on A-fixture documents, and on the line and lexicon checks).
Trust: V +109, K +0 (R16); TRUST_MUTANTS_SUMMARY. Selected tests: SELECTED_SUMMARY. DRI rulings:
reviews/dri-decisions-20261110-ps-2ac-layer.md items 1-2 and -ps-2ac-report.md items 1-2. Next: ps-4.

Feature item ps-2ac (task: prompts/task-ps-2ac.txt, deliverable (4) of task-ps-2ab.txt; plan
`docs/spec/presupposition-PLAN.md` "PS-2a" (:847-864) and 4.6 (:498-501); spec `docs/spec/presupposition.md` 4.7
(:837-839), 2.3 (:345-363) and 5 (:1303-1321)). Branch `feature/ps-2ac`, merge base a5088a09b (main, ps-2ab merged).
Command outputs: `evidence/tests.txt`.

## Preconditions

- **ps-2ab merged.** `admit : PDoc → Except String Report`, `admitWith`, `admitWrapped` and A1-A28 are on main
  (Admit.lean:282-293, Examples.lean:734-1130). No type Run.lean needs was missing.
- **Statement gate.** PASSED, as the task states. Probe (`evidence/probe.py`, output in `evidence/tests.txt`): Run.lean's
  39 declarations, comments stripped and whitespace normalised, against every Lean block of the spec and the PS-S stub:
  none is named there (the spec and stub define no Run.lean declaration), so none can differ. ps-2ab's probe rerun:
  the 19 statements are still 19/19 equal to spec 4.7. This item adds no theorem.
- **Read-only files.** Admit.lean, Wire.lean, Frame, Reading, Rows, Rules, Agree, `Protocol.lean` and
  `service_schema.py` are unchanged ("Final checks": the changed-file list). No guard exposed an `admit` bug; the
  shallow-frame observation below is spec behaviour (DRI ps-2ac-report item 2).
- **In-flight overlap.** No branch in flight touches `lean/VE/Presupposition/Run.lean`. feature/cmp-s3-cfr-1,
  feature/en-e3a and feature/ps-7 also add entries to `tools/trust-classes.json` and `docs/trust-baseline.json`;
  this item inserts its trust-classes entry beside Admit.lean's, away from the end where they append.

## Plan rows delivered

| Row (plan PS-2a :854-858; task "Deliver") | Where (Run.lean) | Guards (Run.lean) and mutants |
|---|---|---|
| one row per obligation, in the block's order | `shownOf` | :163, reversed block :165; S1 |
| `id`, `unit`, `carrier` | `checkedRow` | :163 (A18b), :170 (A24); S2, M-Row-order |
| `goal`: the P0 wire formula, and its English line rendered by Lean | `Goal`, `Line`, `englishLine`, `lineOf`, `lexiconOk` | A24 row :170; `admit`'s goals :173; lines :176-201; M-englishLine, M-lexicon and 12 more |
| `outcome` (checked, or the diagnostic) | `Outcome`, `outcomeOf`, on `Shown` (deviation, below) | checked :167; refused :205-207; A15 UNKNOWN :209; M-outcomeOf, M-shownOf-error, M-rows-under-refusal |
| unresolved: the emitted readings, each with its aliases | `checkedRow` | A1 :217; none on a proved row of an open unit :224; alias `inPlace` :240 |
| `PresuppositionRefuted` lines from the existing inconsistency report | `Inconsistency`, `docPremise`, `refutedLines` | :256-276; S3 and 7 more |
| no runMode line, no MODES entry, no schema, no Python relay (DRI PS-C9) | — | changed-file list ("Final checks") |
| `tools/trust-classes.json` rows; `lean/VE.lean` import; generated inventories | side table; `regen_generated.py --write` | "Trust", "Final checks" |

## What the value is

`shown L inc D := shownOf L inc D (admit D)`, absent without the block (as `admitWrapped`, guard :214). PS-4 passes the
request's lexicon `L` (`VE.English.Run.decodeLexicon` decodes one) and the document's inconsistency report `inc`; for
the document's situations it calls `shownOf` on `admitWith`, as ps-2ab's REPORT says.

- **Outcome, on the field (deviation from the plan text; DRI ps-2ac-report item 1, ACCEPTED).** `admit` is all or
  nothing, so `Shown.outcome` is the block's: `checked`, `refused <admit's diagnostic>` (it names its obligation), or
  `unknown "ResourceLimit: presuppositions"` (spec 5: UNKNOWN, never a refusal). Rows exist only under `checked`; a
  refused or unknown block has none and is not walked (:205-209). The plan puts `outcome` on each row; copying the
  block's diagnostic onto rows `admit` never reached would be false (doc18 [0,0]: p1 would show "…Position: p2").
  The strings are `admit`'s own (`budget`); Run.lean writes none. FOLLOW-UPS row: align the plan text.
- **The goal.** The formula is kept typed (`VE.Formula`); PS-4's encoder writes P0's wire form. The English line is
  three-way (`Line`): `shown <text>`, `notShown`, or `unknown` (over a limit). The text is the core renderer's clause
  (`renderStatement … |>.yield`, without the full stop so that 2.3's lines can quote it). It is shown only when the
  lexicon passes `lexiconOk` and the sentence parses back, in the document's environment, to exactly the goal
  (checklist 9). `lexiconOk` is checked once per report: at most `maxLexicon` (512) entries and no template of more
  than two places (UNKNOWN otherwise), then `VE.English.admissible`, the hypothesis of the renderer's round trip and
  unique reading (`checked_parse_render`, lean/VE/English/Proofs.lean:179). Guards: an uncovered predicate (:186), a
  lexicon that words "ready" as "owner" or "owner" as "ready" (:190-191; the second would otherwise read "… is ready"
  for an owner goal), a goal of 203 nodes (:197), a lexicon of 513 entries or a three-place template (:201).
- **Refuted.** The existing inconsistency report is P0's: a premise list and a certificate of `⊥` on it
  (`PremiseStatus.inconsistent`, lean/VE/SpeechActs/Run.lean:242-246). When every premise is the document's (a
  background formula or an asserted claim, `docPremise`) and the certificate checks, an admitted assumed obligation
  gets `PresuppositionRefuted: <o>: <unit>` if the refutation uses its goal: a premise equals the goal, and the
  certificate no longer checks with those premises replaced by `⊤`. The other premises then refute the goal. Block
  order. Guards (:256-276): both goals used, one used, a background premise; none for a contradiction that uses neither
  goal, a premise not the document's or only in an unasserted unit, a certificate that does not close, no report, a
  proved carrier, a refused block. A certificate that does not check gives no line, and no line claims nothing.
- **Readings.** An admitted unresolved obligation's row lists its unit's readings (`RReading`: candidate, aliases,
  content, premise), which `admit` has checked are exactly `expectedReadings`; any other row lists none.

## DRI rulings

- **Layer (reviews/dri-decisions-20261110-ps-2ac-layer.md items 1-2).** The only Lean renderer of a formula is
  `VE.English.render` (layer 3). I asked before building. Item 1 signed a first-line layer-3 declaration;
  `tools/check_lean_imports.py` refused it ("VE.Presupposition.Run's role fixes its layer at 4 … remove the layer
  declaration", `tools/layer_policy.py:357`); item 2 corrected the rule: no declaration, layer 4 by role, so the import
  of `VE.English.Render` is inward. Conditions: no `layer_policy` edit and no ledger exception; no layer-2 importer
  (the grep in DELTA.md finds only `lean/VE.lean`); the check passes ("Final checks"); the renderer and lexicon guards
  (:170, :176) have mutants (M-englishLine, M-lexicon).
- **Outcome on the field (-ps-2ac-report item 1).** Above. Its conditions: refused A-fixture with its diagnostic and no
  rows (:205, :207); A15 `unknown` and no rows (:209); an admitted fixture `checked` with rows in block order (:163,
  :167); mutants M-rows-under-refusal and M-shownOf-error break them.
- **Shallow frame (-ps-2ac-report item 2).** At a negated or antecedent frame `¬U` entails `B` (the strong reading
  implies `U`), so the assumed reading `B` and the conditioned `U → B` are equivalent and step 5 never separates them.
  The fixture table's negated cell `[assumed, conditioned, inPlace]`, the only one that gives an alias, therefore gives
  an open set that is never admitted: guard :234 (both witness orders, `notSeparatedText`). The alias guard uses a cell
  `[conditioned, asserted, inPlace]` (:239-240). Design row ps-shallow-sep (filed by the DRI).

## Seeded bugs (Lean only; this item changes no Python or Rust product code)

Each of the 36 mutants in `mutants.json` was applied alone and `lake build VE.Presupposition.Run` was run; the first
error is in `evidence/tests.txt`; then the file was restored. **31 break a named guard; 5 are INVALID** (they do not
elaborate, and BUILDER-CHECKLIST item 3 does not count them).

| Id | Behaviour | Definition | Breaks |
|---|---|---|---|
| S1-drop-row (task) | one row per obligation, block order | `shownOf` | :163 block-order guard |
| S2-unit-carrier (task) | unit and carrier are the obligation's | `checkedRow` | :163 field guard |
| S3-no-refuted (task) | the PresuppositionRefuted line | `refutedLines` | :256 refuted guard |
| M-rows-under-refusal | a refused or unknown block has no rows | `shownOf` | :205 A20 |
| M-refuted-unused | only a goal the refutation uses | `refutedLines` | :260 (p2's goal is a premise the refutation does not use) |
| M-englishLine-parse | a line is shown only if it parses back | `englishLine` | :186 |
| M-lexiconOk-admissible | the lexicon must be admissible | `lexiconOk` | :190 |
| M-englishLine-nodes | a goal is charged before it is rendered | `englishLine` | :197 |

S2: a literal swap of `carrier` (a `Carrier`) and `unit` (a `String`) does not elaborate, so the mutant reads the
unit off the carrier (`c.ob.carrier.unitName`). Every other new definition has at least one mutant that breaks a named
guard (`mutants.json`, field `test`), except the data types `Outcome`, `Line`, `Goal`, `Shown` and `Inconsistency`:
their mutants (a constructor or field dropped) are INVALID. `Row` has one that breaks a guard (fields `id` and `unit`
swapped, :170). The data types are read by named guards (`Outcome` :167 and :205-209, `Line` :186-201, `Goal` :170,
`Shown` :205-209, `Inconsistency` :256-276).

## Trust

`tools/trust_map.py --check` PASS against a5088a09b523: trusted +109 (all G[V], Run.lean), K +0, S +0, tied +0,
unclassified +0. Classes in `tools/trust-classes.json`: untied G[V] `Outcome`, `Line`, `Goal`, `Row`, `Shown`,
`Inconsistency`, `lexiconOk`, `lineOf`, `englishLine`, `outcomeOf`, `checkedRow`, `docPremise`, `refutedLines`,
`shownOf`, `shown`; G[R] the limits `maxLexicon`, `maxLineNodes`; T the 21 guard fixtures. `docs/trust-baseline.json`
gains the allowance V +109, "SIGNED by standing ruling R16 (DRI-RULINGS.md), ps-2ac, 2026-10-18": within 150, no K
growth, every new trusted definition exercised by a guard that can fail ("Seeded bugs"; the R16 sweep in "Final
checks"). FOLLOW-UPS.md "## ps-2ac" has the ties-pass row.

## Size, bytes, evaluators

- **Size** (`git diff --numstat a5088a09b`, without generated files): SIZE_LINE
- **Pilot bytes.** 0: no route reads the report yet.
- **Evaluators** (the DRI's rule of 2026-10-27). `shown` reads `admit`'s answer once. `admit` has charged the block
  (256 obligations) and each goal (W1's 10,000 nodes); a refused or unknown block is not walked (:209: 257 obligations,
  no rows). The lexicon is charged once per report (`lexiconOk`) before any line, and each goal against `maxLineNodes`
  before it is rendered: rendering and the parse back grow faster than the goal (probe, interpreted, not a benchmark:
  a 9,611-node goal took 3.5 s to parse back against 55 ms at 611 nodes; the self-reviewer measured 10.5 s to render
  an 8,003-node goal). The parser's work per atom is `pool ^ arity` per template, so a template of more than two
  places is refused before parsing. Fixtures: 256 obligations give 256 lines (:211); 191 and 203 nodes (:196-197);
  506 and 507 constants (:201). The certificate is checked once per report, plus once per assumed obligation whose
  goal is a premise (at most 256).

## Spec re-read

- Rows against plan PS-2a `presupposition-PLAN.md:854-858`: id, unit, carrier; goal with its wire formula and its
  English line rendered by Lean; outcome (on the field: DRI ps-2ac-report item 1); for unresolved obligations the
  emitted readings with aliases; the `PresuppositionRefuted` lines. Each has a row above.
- `PresuppositionRefuted: <o>: <unit>` against `presupposition.md:361-362` and `:1321`: obligation id, then the
  assumed unit; "when the existing inconsistency report shows that the premises refute an assumed goal"; a report
  line, not a diagnostic (in `refuted`, not in `outcome`).
- "Where the report goes" `:837-839`: no mode, runner or schema of its own. The field is absent without the block, as
  `admitWrapped` (Admit.lean:293); guard :214.
- Spec 5 `:1320`: `ResourceLimit: presuppositions` is UNKNOWN, never a rejection: `Outcome.unknown`, guard :209.
- 2.3 `:345-363`: no symbols or ids by default: the line is English only; obligation ids are row fields, for the
  provenance view.

## Final checks

FINAL_CHECKS

## Self-review against BUILDER-CHECKLIST

SELF_REVIEW
