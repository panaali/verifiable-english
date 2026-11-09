# ps-2ab: `admit`, its 19 statements and A1-A28 (spec 4.7, PS-2a part 3) (build report)

No DRI signature is reserved in this item. There are no DELTA rows (DELTA.md): no route calls `admit` until PS-4.
Status: deliverables (1) `admit`, (2) the 19 statements, all proved (standard axioms only), and (3) A1-A28 are built.
Run.lean (4) is cut to ps-2ac by the task's pre-approved seam (see "Cut"). Trust: V +116 untied, K +0, under R16.
Open: the DRI's answer on step 5's separation inputs (asked 2026-11-09T17:55Z; my proposal is built, see "Deviations").
Next items: ps-2ac (Run.lean), then ps-2b.

Feature item ps-2ab (plan `docs/spec/presupposition-PLAN.md` "PS-2a" and 4.6; spec `docs/spec/presupposition.md` 4.7,
5, 7.2, 7.3, 7.5). Branch `feature/ps-2ab`, merge base a0102f0e5 (main's tip at launch, ps-2a merged). Command outputs:
`evidence/tests.txt`.

## Preconditions

- **ps-2a merged.** Wire.lean on main has every type and definition `admit` needs (`RContent` … `expectedReadings`),
  and `candidateTable` is PS-E1's (Table.lean). Nothing was missing.
- **Statement gate.** PASSED, as the task states. ps-2aa's probe form, rerun over this item's statements
  (`evidence/probe.py`, output in `evidence/tests.txt`): the 19 theorems of `Admit/Statements.lean`, comments stripped
  and whitespace normalised, against spec 4.7's statements block (`presupposition.md:1120-1191`). **19 of 19 are
  equal**; three helpers (`admit_pass1`, `buildPre_body`, `admit_ids_nodup`) are not in the spec. `admit` has the type
  `PDoc → Except String Report` and is `admitWith candidateTable admitInputs` (DRI ps-2a item 2; spec 4.7 step 5,
  `:1104-1108`).
- **Layers.** `tools/check_lean_imports.py`: "Lean layer graph kept (799 modules, 18 reviewed legacy edges)". Admit.lean
  imports `VE.Presupposition.Table` and `VE.Readings.Unspecified` (for `separates`, `fillDoc`, `fillHolds`), and
  Examples.lean imports `VE.Readings.Wire` (A27's `abstention`). I made no `layer_policy` edit.
- **In-flight overlap.** No branch in flight touches `lean/VE/Presupposition/`. Shared hand-written files:
  `tools/trust-classes.json` (added entries) and `docs/trust-baseline.json` (one allowance). The rest are generated
  inventories (R12).

## Plan rows delivered

| Row (task "Deliver") | Where | Evidence |
|---|---|---|
| (1) `admit` in spec 4.7's five steps, with the spec 5 diagnostics it owns | `lean/VE/Presupposition/Admit.lean` | A1-A28 and the step guards, Examples.lean:734-1046 |
| (2) the 19 statements, proved, no sorry | `Admit/Statements.lean` (helpers in `Admit/Facts.lean`) | `#print axioms`: `propext`, `Classical.choice`, `Quot.sound` only (`evidence/tests.txt`); `lean/audit.py` PASS |
| (2) ties | `tools/trust-classes.json` | `admit` tied to its 17 statements; `admitWith`, `regen`, `carrierOk`, `openOk`, `unitsOk`, `bases3`, `basesOf` tied to their read-back lemmas (see "Trust") |
| (3) A1-A28 as `#guard`s (A5u-allow/deny, A19-A21, A24-A28 included; A26 soft and rights) | Examples.lean:734-1046 | the guards build; each claimed behaviour has a mutant that breaks one (see "Seeded bugs") |
| (4) Run.lean | cut to ps-2ac | "Cut" |

All 19 statements closed in one step, so the per-statement fallback commits the task allows for were not needed.
Proof lines: `Admit/Facts.lean` 278, `Admit/Statements.lean` 242 (520 in total, under the ~800 stop).

## Cut (task: pre-approved seam; reviews/dri-decisions-20261109-ps-2a.md item 1)

Measured at 7faec40ab, before Run.lean: counted lines (Admit.lean, VE.lean, the non-A guards, `trust-classes.json`,
`mutants.json` and the docs) would pass ~600 (see "Size"). The seam cuts Run.lean (deliverable 4) to **ps-2ac**. I sent
the DRI the measured numbers (msg.sh dri ps-2ab, 2026-11-09T18:25Z). `admit`, its statements and A1-A28 are not cut.

FOLLOW-UP: ps-2ac Run.lean report value (PS-2a part 4)

## Deviations and points for the DRI

- **Step 5's separation inputs (asked 2026-11-09T17:55Z, no answer when I finished).** `PDoc` has no readings@1
  document and no situations, and readings@1 has no separation diagnostic (separation is its own request). I built my
  proposal: `Fixed` (admit's fixed inputs) holds the readings environment's `chain` and the separating situations
  `sits` (unit, witness, other, situation). `readingsDoc` builds the open unit's readings@1 document from `PDoc`
  itself. For each pair of the set's readings, `separated` asks for a recorded situation on which `separates` holds,
  or, with `norm-defaults@0`, `separates (fillDoc N)` and `fillHolds` on the witness (spec 4.7 step 5, `:1101-1103`).
  Otherwise the answer is `PresuppositionCandidates: <o>: readings <i> and <j> are not separated` (new Lean text).
  `admitInputs` is the norms chain with no situation, so `admit` itself refuses every two-reading set until PS-4
  passes the document's situations through `admitWith`. `Fixed` holds the chain, not a whole `ReadingsEnvironment`:
  building one needs a `RouteVocabulary`, and step 5 reads only `re.chain`. A different ruling changes only step 5's
  refusal; no statement reads it.
- **A10's outcome is `clause`, not 7.3's `content`.** A conditioned carrier recorded `B → G` peels (one antecedent) to
  `G`. Step 4 then finds `G`, not `strong`, at the path. So the spec's own step order answers
  `PresuppositionMismatch: p1: clause` (Examples.lean:940-944); no document reaches `content` in that shape. A11 (the
  nesting that does not peel) and a peeled but different content (:952) give `content`. I did not change the order.
- **Fixtures on `admitWith fixtureTable`.** PS-E1's table has one candidate in every cell except generic's consequent,
  so A1, A2, A4, A5u-allow/deny, A21, A22, A26 cannot reach their 7.3 outcome on `admit`. Spec 7.3 says "The fixture
  table of the stub stands in for PS-E1's". Those guards run on `admitWith fixtureTable <inputs>`, and beside each I
  added what `admit` itself answers (for example A1 on `admit`: `PresuppositionCandidates: p1`). All 19 statements are
  on `admit`, word for word.
- **A27 runs on readings@1's `abstention`.** It is not `admit`'s answer: the spec puts the rights-chain refusal in
  `abstention`, before PS-2a's check. The guard builds a `ReadingsEnvironment` on the rights chain with
  `norm-defaults@0` and checks the text, and that the norms and soft chains do not abstain (Examples.lean:1037-1060).
  On the rights chain, `admit` itself does not refuse A26's set (:868).
- **`admitWrapped` and `admitBase`.** The spec names them in `no_block_unchanged` without bodies. Here they are the
  document mode's `presuppositions` field: `admitBase` is absent (`none`); `admitWrapped` is `admit D` when the block
  is present. PS-4 builds the document mode on them.
- **Fault order inside step 4** (R2: deterministic, documented here). Pass 1 checks, per obligation in block order,
  position, arguments and carrier (spec order). Pass 2 then checks, per obligation in block order, an unresolved
  obligation's readings and that it is its unit's first unresolved one, because `expectedReadings` reads the whole
  report. Budget: the block's size is charged first (step 1). Each regenerated goal is charged where pass 1 builds it,
  and each unit's regenerated content where step 5 builds it. Step 3 reads only the unit's first unresolved
  obligation as the reading's candidate, as `claimReading` does, so a second one reaches step 4's diagnostic.
- **A19's heading unit records the carried form.** A heading with a conditioned carrier on a unit whose content is
  just `pre` does not peel in step 3 (`content`). A19's guard records `pre → pre` (and `pre ∧ pre` for asserted), which
  peels, so step 4's `PresuppositionCandidates: p2` is reached.
- **Unconditional also refuses its own unit.** The diagnostics table (spec 5) names "the assumed or unconditional
  unit … the obligation's own unit". So `carrierOk` refuses an unconditional carrier on its own unit as well.

## Seeded bugs (Lean only; this item changes no Python or Rust product code)

`mutants.json` lists 30 hand mutants with `file`, `find`, `replace` and `test`: at least one per new trusted
definition, and more on the tied ones. I applied each alone, ran `lake build VE.Presupposition.Examples
VE.Presupposition.Admit.Statements` and restored the file. All 30 fail (`evidence/tests.txt`, file:line of each
failure). The first run left one survivor: `separated` with W1's `separates` in place of the completion's. The guard
at Examples.lean:853-859 kills it: where `unsaid__p` holds, `F_p` decides `p` under both readings. The claimed
behaviours:

| Id | Behaviour | Mutant | Fails |
|---|---|---|---|
| M2-proved-unchecked | M2 (7.5): proved needs a certificate that checks against `premisesBefore` | `provedOk` accepts any named certificate | A7, Examples.lean:906-907; `admit_proved_sound` (Statements.lean:104) |
| M-drop-candidate | R-D3: the unit carries exactly the emitted readings | `openOk` compares with one candidate dropped | A2 (:785), A1 (:771) |
| M-soft-chain | A26: the soft chain refuses a conditioned rule reading before separation | the refusal removed | A26 soft (:866) |

**R16 mechanical mutants.** `tools/trust_mutants.py` through `mac-pytest.sh --trustmut`: see "Final checks".

## Trust

`tools/trust_map.py --check` PASS against a0102f0e5350: trusted +116 (all G[V], Admit.lean), K +0, S +0, tied +102,
unclassified +0. Classes in `tools/trust-classes.json`:
- **Tied G[V]:** `admit`, to its 17 statements on `admit`. `admitWith` is tied to `admitWith_ok`, `regen` to
  `regen_ok`, `carrierOk` to `carrierOk_ok`, `openOk` to `openOk_ok`, `unitsOk` to `unitsOk_ok`, `bases3` to
  `bases3_mem` and `basesOf` to `mem_basesOf`. Each lemma reads the step's result back in terms of the spec's S
  definitions (`entersRestriction`, `carrierAllowed`, `expectedReadings`, `ruleConditions`, `carried`).
- **C:** `ensure`, `mapE`, `allE`, with `ensure_ok`, `mapE_mem`, `mapE_map`, `allE_ok`.
- **G[R]:** the diagnostic texts and limits: `maxObligations`, `budget`, `softText`, `firstOb`, `rulePred`,
  `Carrier.unitName`, `isRuleUnit`.
- **Untied G[V] (the +116):** `Base`, `rootsWith`, `peelWith`, `peelRule`, `allSame`, `baseOf`, `withObligations`,
  `baseTreeOf`, `provedOk`, `needsUnspec`, `checkIds`, `Fixed`, `admitInputs`, `readingsDoc`, `separated`, `softOk`,
  `admitBase`, `admitWrapped`.
- Examples.lean's new fixtures are T.

`docs/trust-baseline.json` gains one allowance, V +116, "SIGNED by standing ruling R16 (DRI-RULINGS.md), ps-2ab,
2026-10-18". The "## ps-2ab" ties-pass row is in FOLLOW-UPS.md. Every untied definition has a mutant that fails a
guard (table above and `mutants.json`). ps-2aa's and ps-2a's ties-pass rows can now point at these statements.

## Size, bytes, evaluators

- **Size** (`git diff --numstat a0102f0e5`, without the generated inventories). Counted: Admit.lean 275, VE.lean 3,
  the step 2-5 and separation guards in Examples.lean 74, `trust-classes.json` 166, `mutants.json` 32, `evidence/`
  (probe.py 23, tests.txt 71), DELTA.md 10, this REPORT and `trust-baseline.json` 7. That is over the ~600 line, so
  the seam cut Run.lean. Exempt (DRI ps-2a item 1; size rule adv1207 item 3): the proofs, 520 lines
  (Facts.lean 278, Statements.lean 242), and A1-A28 with their fixture definitions, 244 lines of Examples.lean.
- **Pilot bytes.** 0: no route reads `admit` yet.
- **Evaluators** (the DRI's rule of 2026-10-27). `admit` charges the block's size first: 257 obligations is
  `ResourceLimit: presuppositions` (A15, :979), and 256 on one unit are admitted (:980). It charges each regenerated
  goal and each unit's regenerated content against W1's 10,000 nodes where it builds them: a 16,383-node goal is
  `ResourceLimit` (:986). Each obligation is regenerated once (`mapE`). The R-D6 check reads the block once per
  obligation (at most 256 × 256 pairs). Separation is readings@1's `separates`, with its own 12-cell bound
  (`maxCells`).

## Spec re-read

- `admit`'s steps against `presupposition.md:1075-1116`: step 1 (256, W1's nodes, `ResourceLimit: presuppositions`);
  step 2 (id, unit, row, in that order); step 3 (peel per unit, document order; `content` or `rule` on the unit's
  first obligation); step 4 (position, R-D6, arguments, `clause`, then each carrier rule in the listed order); step 5
  (content, rules, `VE.Norms.WellFormed`, soft chain, separation).
- Diagnostics against section 5 (`:1303-1320`): each text (`PresuppositionUnknownRow: <o>: <row>`,
  `…Position: <o>`, `…Mismatch: <o>: <field>`, `…Certificate: <o>`, `…AssumedUnit: <o>: <unit>`,
  `…Default: <o>: <predicate>`, `…Unresolved: <o>`, `…Candidates: <o>`, the soft-chain text, `ResourceLimit:
  presuppositions`) has a guard; the separation text adds `: readings <i> and <j> are not separated`.
- The 19 statements against `:1120-1191` by the probe (19/19 equal).
- 7.2's `admit_*` rows (`:1408-1413`): `admit_unresolved_readings` true A1, false A2 and A21; `admit_conditioned_rule_unspecified`
  true A4, false A5, A5u-allow, A5u-deny; the own-unit clause true A24, false A20; `admit_outside_restrictions` true
  A18b, false A18; `carrierAllowed` true A22, false A23; `no_block_unchanged` A17.
- 7.3 A1-A28 (`:1415-1453`): every row has a guard; A10 differs (see "Deviations").

## Final checks

(filled after the heavy checks)

## Self-review against BUILDER-CHECKLIST

(filled after the heavy checks)
