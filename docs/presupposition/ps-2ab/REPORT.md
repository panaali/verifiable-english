# ps-2ab: `admit`, its 19 statements and A1-A28 (spec 4.7, PS-2a part 3) (build report)

No DRI signature is reserved in this item. There are no DELTA rows (DELTA.md): no route calls `admit` until PS-4.
Status: built: (1) `admit`; (2) the 19 statements, all proved with standard axioms only, each also over `admitWith`
for every table and fixed input; (3) A1-A28. Run.lean (4) is cut to ps-2ac by the task's pre-approved seam ("Cut").
Trust: V +123 untied, K +0, within R16; R16 sweep 0 SURVIVOR, 0 UNKNOWN; selected tests 115 units, 0 failed.
DRI rulings: reviews/dri-decisions-20261109-ps-2ab.md and -ps-2ab-2.md (separation inputs, fixtures, A10 is `clause`,
size ~830 accepted; it is ~1,130 after the sweep's fixtures, DRI told 2026-11-10T02:57Z). Next: ps-2ac, then ps-2b.

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
| (2) the 19 statements, proved, no sorry | `Admit/Statements.lean` (helpers in `Admit/Facts.lean`) | `#print axioms`: `propext`, `Classical.choice`, `Quot.sound` only (`evidence/tests.txt`); `lean/audit.py` PASS. Each spec statement is the instance at `admit` of an `admitWith_*` twin proved for every table `t` and fixed inputs `fx`. So none is vacuous for the instance PS-4 passes, although `admit`'s own inputs refuse every open set (see "Points for the DRI") |
| (2) ties | `tools/trust-classes.json` | `admit` tied to its 17 statements; `admitWith`, `regen`, `carrierOk`, `openOk`, `unitsOk`, `bases3`, `basesOf` tied to their read-back lemmas (see "Trust") |
| (3) A1-A28 as `#guard`s (A5u-allow/deny, A19-A21, A24-A28 included; A26 soft and rights) | Examples.lean:734-1046 | the guards build; each claimed behaviour has a mutant that breaks one (see "Seeded bugs") |
| (4) Run.lean | cut to ps-2ac | "Cut" |

All 19 statements closed in one step, so the per-statement fallback commits were not needed. The proofs were committed
(c70ede785) before A1-A28 (4d6d40119), not after as the task's order says, because they were done first.
Proof lines: `Admit/Facts.lean` 299, `Admit/Statements.lean` 358 (657 in total, under the ~800 stop).

## Cut (task: pre-approved seam; reviews/dri-decisions-20261109-ps-2a.md item 1)

Measured at 7faec40ab, before Run.lean: counted lines (Admit.lean, VE.lean, the non-A guards, `trust-classes.json`,
`mutants.json` and the docs) would pass ~600 (see "Size"). The seam cuts Run.lean (deliverable 4) to **ps-2ac**. I sent
the DRI the measured numbers (msg.sh dri ps-2ab, 2026-11-09T18:25Z). `admit`, its statements and A1-A28 are not cut.

FOLLOW-UP: ps-2ac Run.lean report value (PS-2a part 4)

## DRI rulings (reviews/dri-decisions-20261109-ps-2ab.md, reviews/dri-decisions-20261109-ps-2ab-2.md)

- **`admit`'s fixed separation inputs: ACCEPTED** (ps-2ab item 1; ps-2ab-2 item 1 keeps `admitInputs` and accepts
  readings@1's texts and the `admitWith_*` twins). Its conditions are guarded: `admitWith fixtureTable admitInputs`
  refuses S7's open rule with `needsModelText`, `admitWith fixtureTable fx1 docA1` is admitted, and the
  `notSeparatedText` guards cover a non-separating situation and a reversed witness. `admit` itself refuses PS-E1's
  generic consequent set for want of a situation (guard). As ruled, spec section 5 now names the two texts as step 5's
  refusal (one row). What was built: `PDoc` holds no readings@1 document and no
  situations. In readings@1 the situations come with each set, in the document (`SetJ.situations`). The spec makes
  them a fixed input of `admit` (4.7 step 5, `:1104-1108`). I built: `Fixed` holds the readings environment's `chain`
  and the situations `sits` (unit, witness, other, situation). `readingsDoc` builds the open unit's readings@1 document
  from `PDoc`: its vocabulary and regulated predicates, the background and the other units as fixed contents, and the
  set. `separated` asks each pair for a recorded situation on which `separates` holds; with `norm-defaults@0` it asks
  `separates (fillDoc N)` and `fillHolds` on the witness (`:1101-1103`). Failures use readings@1's texts: "each
  other reading needs a distinguishing model id" and "distinguishing model does not separate readings"
  (`lean/VE/Readings/Run.lean:209-220`). They are copied there as `needsModelText` and `notSeparatedText`, because
  readings@1 writes them inline (FOLLOW-UPS: give them one owner). `admitInputs` is the norms chain with no
  situation, so `admit` itself refuses every set of two or more readings until PS-4 passes the document's situations
  through `admitWith` (PS-4's task file says so). `Fixed` holds the chain, not a whole
  `ReadingsEnvironment`: building one needs a `RouteVocabulary`, and step 5 reads only `re.chain`. `readingsDoc`'s
  rules are strict W1 rules and its frame has no soft or rights block, so no decision key is generated and
  `separates`' 12-cell bound is never reached (guards: `cells … = 0`).
- **A10's outcome is `clause` (ps-2ab-2 item 2, SIGNED: the spec's step order wins).** A conditioned carrier recorded
  `B → G` peels (one antecedent) to `G`. Step 4 then finds `G`, not `strong`, at the path, and answers
  `PresuppositionMismatch: p1: clause`, on `admit` and under the fixture table. As ruled, I edited spec 7.3's A10 row.
  A11 (a nesting that does not peel) and a peeled but different content give `content`.
- **Size: ACCEPTED** (ps-2ab item 3, ps-2ab-2 item 3). Counted lines are over ~600 after the Run.lean cut ("Size").

## Deviations (no ruling needed)

- **Fixtures on `admitWith fixtureTable`.** PS-E1's table has one candidate in every cell except generic's consequent,
  so A1, A4, A5u-allow/deny, A22 and A26 cannot reach their 7.3 outcome on `admit`. Spec 7.3 says "The fixture table
  of the stub stands in for PS-E1's". Those guards run on `admitWith fixtureTable <inputs>`, and beside each I added
  what `admit` itself answers (for example A1 on `admit`: `PresuppositionCandidates: p1`). A2, A6, A10, A11, A21 and
  A23 reach their outcome on `admit` too, and are guarded on both. All 19 statements are on `admit`, word for word.
- **A27 runs on readings@1's `abstention`.** It is not `admit`'s answer: the spec puts the rights-chain refusal in
  `abstention`, before PS-2a's check. The guard builds a `ReadingsEnvironment` on the rights chain with
  `norm-defaults@0` and checks the text, and that the norms and soft chains do not abstain. On the rights chain,
  `admit` itself does not refuse A26's set.
- **`admitWrapped` and `admitBase`.** The spec names them in `no_block_unchanged` without bodies. Here they are the
  document mode's `presuppositions` field: `admitBase` is absent (`none`); `admitWrapped` is `admit D` when the block
  is present. `no_block_unchanged` is therefore true by definition here. That S11's discourse@1 answers are
  byte-identical is PS-4's to show, on the document mode it builds (carried to ps-2ac and PS-4).
- **Fault order inside step 4** (R2: deterministic, documented here). Pass 1 checks, per obligation in block order,
  position, arguments and carrier (spec order). Pass 2 then checks, per obligation in block order, an unresolved
  obligation's regenerated readings against W1's budget, then the readings, then that it is its unit's first
  unresolved one, because `expectedReadings` reads the whole report. Budget: the block's size is charged first
  (step 1). Each regenerated goal is charged where pass 1 builds it, each open set's regenerated readings in pass 2,
  and each unit's regenerated content in step 5. Step 3 reads only the unit's first unresolved obligation as the
  reading's candidate, as `claimReading` does, so a second one reaches step 4's diagnostic.
- **A19's heading unit records the carried form.** A heading with a conditioned carrier, on a unit whose content is
  just `pre`, does not peel in step 3 (`content`). A19's guard records `pre → pre` (and `pre ∧ pre` for asserted),
  which peels, so step 4's `PresuppositionCandidates: p1` is reached.
- **The own-unit refusal.** It applies to assumed and unconditional carriers at a path or a rule act (spec 5's
  table), not at a heading. A heading's unconditional carrier on its own unit is answered by R-10
  (`PresuppositionCandidates`; guard).
- **Diagnostics name an obligation of the request.** When no obligation fits (an ill-formed fixed tree beside claim
  obligations only), `firstOb` names the block's first obligation (guard).

## Seeded bugs (Lean only; this item changes no Python or Rust product code)

`mutants.json` lists 38 hand mutants with `file`, `find`, `replace` and `test`: at least one per new trusted
definition, and more on the tied ones. I applied each alone, ran `lake build VE.Presupposition.Examples
VE.Presupposition.Admit.Statements` and restored the file. All 38 fail on the final Lean (`evidence/tests.txt` lists
each failing file:line). Two type mutants (`Base`, `Fixed`) fail Admit.lean's own build. Survivors along the way each got a
fixture: W1's `separates` in place of the completion's (where `unsaid__p` holds, `F_p` decides `p` under both
readings); `fillHolds` dropped (F-ND1 as an open rule: no filling of `help_permitted` breaks the witness's
`Fill_T`); pass 2's budget (readings that differ from the expected ones over a base past W1's budget); an assumed
rule act in a cell that lists conditioned (`needsUnspec`). The claimed behaviours:

| Id | Behaviour | Mutant | Fails |
|---|---|---|---|
| M2-proved-unchecked | M2 (7.5): proved needs a certificate that checks against `premisesBefore` | `provedOk` accepts any named certificate | A7, Examples.lean:949-950; `admit_proved_sound`'s proof (Statements.lean:154) |
| M-drop-candidate | R-D3: the unit carries exactly the emitted readings | `openOk` compares with one candidate dropped | A2 (:787), A1 (:771), and 35 more guards |
| M-soft-chain | A26: the soft chain refuses a conditioned rule reading before separation | the refusal removed | A26 soft (:905), the cell with conditioned first (:1222) |

**R16 mechanical mutants.** `tools/trust_mutants.py` through `mac-pytest.sh --trustmut`: see "Final checks".

## Trust

`tools/trust_map.py --check` PASS against a0102f0e5350: trusted +123 (all G[V], Admit.lean), K +0, S +0, tied +104,
unclassified +0. Classes in `tools/trust-classes.json`:
- **Tied G[V]:** `admit`, to its 17 statements on `admit`. `admitWith` is tied to `admitWith_ok`, `regen` to
  `regen_ok`, `carrierOk` to `carrierOk_ok`, `openOk` to `openOk_ok`, `unitsOk` to `unitsOk_ok`, `bases3` to
  `bases3_mem` and `basesOf` to `mem_basesOf`. Each lemma reads every check of its step back in terms of the spec's
  definitions (`entersRestriction`, `carrierAllowed`, `expectedReadings`, `ruleConditions`, `carried`, W1's node
  budget) and of the untied definitions that hold the rest (`softOk`, `separated`, `baseOf`). So no check of a tied
  step is left out of its lemma (self-review B).
- **C:** `ensure`, `mapE`, `allE`, with `ensure_ok`, `mapE_mem`, `mapE_map`, `allE_ok`.
- **G[R]:** the diagnostic texts and limits: `maxObligations`, `budget`, `softText`, `needsModelText`,
  `notSeparatedText`, `readingNodes`, `firstOb`, `rulePred`, `Carrier.unitName`, `isRuleUnit`.
- **Untied G[V] (the +123):** `Base`, `rootsWith`, `peelWith`, `peelRule`, `allSame`, `baseOf`, `withObligations`,
  `baseTreeOf`, `provedOk`, `needsUnspec`, `checkIds`, `Fixed`, `admitInputs`, `readingsDoc`, `separated`, `softOk`,
  `admitBase`, `admitWrapped`.
- Examples.lean's new fixtures are T.

`docs/trust-baseline.json` gains two allowances, V +116 and V +7 (after the self-review fixes), each "SIGNED by
standing ruling R16 (DRI-RULINGS.md), ps-2ab, 2026-10-18". The "## ps-2ab" ties-pass row is in FOLLOW-UPS.md. Every untied definition has a mutant that fails a
guard (table above and `mutants.json`). ps-2aa's and ps-2a's ties-pass rows can now point at these statements.

## Size, bytes, evaluators

- **Size** (`git diff --numstat a0102f0e5`, without the generated inventories and code map, and without the sweep's
  output `trust-mutants.json`). Counted: Admit.lean 295, VE.lean 3, Examples.lean's guards beyond A1-A28 193 (step 2-5
  and separation guards, and the trust-mutants survivor fixtures), `trust-classes.json` 192, `mutants.json` 40,
  `trust-mutants-allow.json` 29, `evidence/` (probe.py 23, tests.txt 83), DELTA.md 11, `trust-baseline.json` 14, the
  spec's two edited rows 3, and this REPORT (~245). That is about 1,130. The DRI accepted ~830 (ps-2ab-2 item 3); the
  growth since is the survivor fixtures and the sweep's allow file, which the R16 sweep required. Exempt (DRI ps-2a
  item 1; size rule adv1207 item 3): the proofs, 657 lines (Facts.lean 299, Statements.lean 358), and A1-A28 with their
  fixture definitions, 290 lines of Examples.lean.
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

- **Regenerated files.** `uv run python tools/regen_generated.py --write --skip route-cases`: rc 0, 37 entries
  (793f033fe). `route-cases` needs the Rust release binary, which this worktree does not have, and it reads no
  presupposition file; ps-2a and ps-2aa skipped it the same way. The chain's gate checks it.
- **Lean.** `lake build` (all default targets): "Build completed successfully (1331 jobs)". `python3 lean/audit.py`:
  "PASS: 799 source files; 8862 named theorem declarations audited …; only the declared standard axiom allowlist"
  (rerun after each later Lean edit, same result).
- **Layers.** `tools/check_lean_imports.py`: "Lean layer graph kept (799 modules, 18 reviewed legacy edges)".
- **Trust.** `tools/trust_map.py --check`: "PASS: K, S and untied [V] within a0102f0e5350 and the allowances introduced
  since" (trusted +123, K +0).
- **R16 trust mutants** (`mac-pytest.sh --trustmut`, on the VM because ve-mac-1 was unreachable; `--test
  lean/VE/Presupposition/Examples.lean`, `--allow trust-mutants-allow.json`). The full run at dc1277393 took 11,712 s:
  234 KILLED, 13 SURVIVOR, 10 UNKNOWN, 56 INVALID, 43 ALLOWED. Its survivors were positions inside lists my guards
  did not move: a second unit, a third reading, a second situation, a fixed rule first or last in the tree, a cell with
  conditioned first. Each now has a guard ("Positions inside lists" in Examples.lean). The UNKNOWNs either do not
  elaborate, or fail more than 100 guards (Lean's `maxErrors`). The survivors left are equivalent: the outer index range
  of the pairs, `isEmpty` or `head?` of a cut list, `hard` on a strict node, and the set's version number. Each of those
  is allowed with its reason. The rescore at 439f196bd (288 verdicts carried, 68 rerun, 731 s): **240 KILLED, 0 SURVIVOR, 0 UNKNOWN, 56 INVALID, 60 ALLOWED, exit 0** (`trust-mutants.json`, `trust-mutants-allow.json`).
- **Selected tests** (final, on the committed tree f25ee6364, clean): `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select --
  --base a0102f0e5 --run`, on the VM (ve-mac-1 unreachable): "recorded 106 units for tree 83742a7929; … 0 failed",
  115 units, exit 0 in 8,004 s. `tools/select_tests.py` selects 484/560 units without a recorded Lean build; the runner
  ran the 115 its map records for this tree. No test of main-known-red.txt was among the failures (there were none).
- Two sweeps were stopped by the harness's 2-hour limit before they wrote a result. The full run above is the one
  recorded.

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 4 A, 7 B, 8 C; fixed 19 (self-reviewer agent, one call, on 31f7bb1aa). The four A: readings@1's texts in
place of a new one; the 12-cell bound (unreachable: `cells … = 0` guards); `admitInputs`' vacuity (`admitWith_*`
twins, and the DRI ruled); unconditional at a heading. The seven B: `firstOb`'s fallback; the rule act's own rule;
complete read-back lemmas for every tied step; the background in `readingsDoc`; A2/A6/A10/A11/A21/A23 on `admit`;
A10 and the size to the DRI. Each fix has a guard and a hand mutant (`mutants.json`).

1. Every Lean answer typed and contained: N.A. No relayed answer, schema or route; `admit`'s `Report` is consumed by
   Lean only, until PS-4 and ps-2b.
2. Every required deliverable built: PASS. (1)-(3) are built; (4) is cut by the pre-approved seam, and the DRI noted it
   (reviews/dri-decisions-20261109-ps-2ab.md item 3); `FOLLOW-UP: ps-2ac`.
3. Tests and gates can fail: PASS. 38 hand mutants, each failing a named guard (`evidence/tests.txt`); the
   trust-mutants sweep (`trust-mutants.json`, "Final checks").
4. Python, Lean and Rust agree: N.A. Lean only; no Python or Rust path decides presuppositions.
5. R8 binding: N.A. No relay. The diagnostics name an obligation of the request (`firstOb` guard), for ps-2b's
   binding.
6. Gate evidence matches the final HEAD: PASS. `evidence/tests.txt` is regenerated on the final Lean commit; the
   trust-mutants input hashes are for the committed HEAD ("Final checks").
7. No unsigned item: PASS. The three DRI questions are ruled (two decision files); DELTA has no rows.
8. Every user-visible change in DELTA: PASS. None is user-visible (DELTA.md, with the grep and `git diff
   --name-only` it cites).
9. Test selection: PASS. `tools/select_tests.py --base a0102f0e5` selects 484/560 units ("lean cutoff: no record of
   the base and head build", the conservative path for a Lean change), including `lean/audit.py` and `lake build`,
   which build every guard of this item.
10. Statements say what is claimed: PASS. The probe gives 19/19 equal to spec 4.7; M2 breaks `admit_proved_sound`
    (Statements.lean) as well as A7; no hypothesis was added.
11. Budgets fail closed: PASS. 257 obligations, a goal over 10,000 nodes, a unit content and an open set's readings
    over budget each answer `ResourceLimit: presuppositions` (UNKNOWN), with guards (A15 and the step-5/pass-2
    guards).
12. No CPU or memory regression: N.A. for pilots (no route calls `admit`). Inside `admit` each obligation is
    regenerated once; R-D6 reads the block once per obligation (at most 256²); `fillDoc` is built once per open set.
13. Test-removed trailers: N.A. No test removed.
14. Both directions, cited evidence, spec re-read: PASS. Each refusal has its accepted twin (A1/A2, A4/A5, A9,
    A14, A18/A18b, A22/A23, separation, background, `fillHolds`); "Spec re-read" lists the lines.
15. Overclaim, silent cut, checks that can fail, limits charged first: PASS. The cut is the task's seam; the
    universal words were checked against the guards cited; budgets are charged before comparison (pass 2, step 5).
