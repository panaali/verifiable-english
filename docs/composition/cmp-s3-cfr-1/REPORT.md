# cmp-s3-cfr-1: the right-clauses wire, the `clauses-elaborate` mode and the registration (cmp-s3b part 1)

Status: deliverables (1)-(5) built; 8.5's `decode_unstructured` and `elaborate_plain` proved, no `sorry`. No signature reserved.
Fix round of b8d143bc's review: F1 FOLLOW-UPS row filed, F2 model-mode text corrected and swept, F-ready1 relay gate builds first ("Review fixes").
HEAD: last code commit is the one before this REPORT's final edit (the chain's gate-result.json records the HEAD it ran on).
Ruled 11-10: the 37 moved rights-list environment answers are DELTA row 1's, and `PlainOnWire`'s form is confirmed
(dri-decisions-20261110-cmp-s3-cfr-1-env.md items 1-2). Size: ~1,660 counted plus 1,409 exempt proof lines, accepted (-count.md item 1). Signatures used: cmp-s3 Q1 A1 (`hd`), 10-31 item 2 with 11-09 cmp-s3-cfr-1 items 2 and 4 (DELTA row 1), R16 (trust).

## Deliverables

| Task row | Delivered | Evidence |
|---|---|---|
| (1) Wire.lean (8.5): the decoder, `decode_unstructured`, `elaborate_plain` with the signed `hd` | yes. `decode_unstructured` is word for word; `elaborate_plain` has `(hd : PlainOnWire D)` after `hp` (Q1 A1) | lean/VE/RightClauses/Wire.lean; proofs in WireDecode.lean, WireName.lean, WireTheorems.lean |
| (2) the `clauses-elaborate` mode: input the document; output the plained document's canonical bytes and `clauseSlotLabelled` | yes: Registry, `runMode_clausesElaborate`, response shape, encoder theorem `runCaseReported_fits`, schema, deadline, relay-gate fixtures. `elided_bytes` is **not** emitted: no product code computes it yet (row cmp-s3a-cfr-3) | lean/VE/RightClauses/Run.lean; `tools/relay_mutation_gate.py --route service:clauses-elaborate`: 528 mutants, 0 failures |
| (3) `right-clauses@0` in the registered list, ve/profile_table.json regenerated | yes: `VE.Compose.environmentWrappers`. D29, D33, D41 and D52 keep their values (their rows are unchanged; tests/test_compose_dispatch.py) | ve/profile_table.json (+1 line) |
| (4) test_right_clauses_k1_service_identity | yes; it fails on main (no mode, no registration) | tests/test_right_clauses.py |
| (5) the profile-off regression as saved evidence (9.3) | yes. Profile off: the evidence script's digests at the base build and at this item's build are saved side by side and equal. Profile on with `elided: []`: a live test, so it survives a sync with main | docs/composition/cmp-s3-cfr-1/profile-off.json (written by profile_off_evidence.py at 6db6ee16d and at this item's head); test_right_clauses_profile_off_evidence, test_right_clauses_profile_on_regression |

Not delivered here:
- cmp-s3-cfr-1b: the relay, the Python differential, the remaining 9.1/9.2 fixtures, W1's budget fixture and
  `clauseSlot_wellFormed`. Once its relay's `RightsEnvironment` reads the profile, it also records the b15b model
  oracle's `right-clauses@0` environments (`python -I tests/b15b_model_cases.py record ... --profile
  right-clauses@0`). It then drops the exclusion this item put in
  tests/test_model_environment.py::test_the_oracle_reaches_every_profile_and_display_field, whose fixture
  tests/data/right-clauses-environment.json the oracle already finds.
- **cmp-s3-cfr-1c (filed by the DRI, reviews/dri-decisions-20261109-cmp-s3-cfr-1.md item 1):** reading candidates under the profile, that is, 4.1 steps 2-4 for
  candidates, `decodeClauseDoc` filling `cands`, and K12. Until then the head refuses a list with `readings@1` by
  name (`UnsupportedProfile: right-clauses@0 with readings@1 is not implemented`); before this item, such a list had
  no head at all.

## The wire (readings made here; for the reviewer and cmp-s3-cfr-1b)

- **Document.** The rights route's array of units (rights 3.2). Spec 8.5 builds each entry's `unitSpan` "from its
  unit", but the rights wire has no unit span. So a unit under the profile may carry `span: [a, b]`, and
  `stripElided` drops it. A unit without one has `[0, 0)`, so a non-empty clause or elided span on it is refused
  (`ClauseSpan`). A malformed span is `InvalidInput: invalid unit span`, the one text section 7 does not list. The
  key mirrors a W2 unit's `span` (docs/spec/document.md:21); cmp-s3-cfr-1b's relay must send it.
- **`total: null`.** The service's restricted JSON has no null; rights' `_wire` writes an optional null by omission.
  So a relation without `total` reads as `total: null`. An explicit null is read too, if one arrives. Spec 7 says
  a missing key is `invalid relation`, so this is a deviation the wire forces. The DRI signed both wire readings
  (reviews/dri-decisions-20261109-cmp-s3-cfr-1.md item 2); the spec erratum is the FOLLOW-UPS line (evidence/follow-ups-row.md). cmp-s3-cfr-1b's
  relay must match both.
- **Order (4.1 step 2, 7).** Units in document order. In each unit, every line object goes through `decodeLine` on
  the object without the three keys (this gives `<n>`), then `elided`, `clauses` (each clause in order) and
  `relation`; then rights' own `addUnit` runs on the unit without its span and keys. So the head's line texts come
  before rights' unit texts: a `right_lines` unit of an unknown right whose line has no `elided` gets
  `InvalidInput: elided missing on rule equal-access`, not `UnknownRight` (a RunExamples `#guard` pins this).
- **Cost.** A line object is decoded twice by the head (`headLine`, `addUnit`) and once more by the rights decoder on
  the plained document. `plainLineJson`'s `D.lines.find?` makes elaboration quadratic in the number of named lines.
  Units are capped at 1,024; lines per unit are not. cmp-s3-cfr-1b's large-document fixture (W1) must cover lines per
  unit, not only units. Run.lean also decodes the environment twice (`decodeClauseDoc`, then `decodeRightsSource` on
  the plained document) and reads `profilesOf` twice. Each is bounded by the environment's size; cmp-s3-cfr-1b's W1
  fixture measures it.
- **Environments.** `right-clauses@0` beside `acts@0` stays refused by the base rows, as before (Standalone keeps that
  gate's whole-table read for `readings@1` only). With `rights@0`, the environment mode answers as for the same list
  without the profile, but for the echoed list and the identity. The base refused every such list as an unregistered
  profile. The model mode decides no model under the profile: Lean checks the environment, then the model's tables,
  then the profile list, so a well-formed model is refused by the name, as in the base, and a faulty model gets the
  answer it gets without the profile, where the base refused it by the name (review F2;
  test_right_clauses_model_mode_faulty_models_answer_as_without_the_profile). Python's model view drops the profile,
  and the model path answers the same with and without it (DELTA row 1;
  test_right_clauses_environment_and_model_answer_as_without_the_profile).
  Probe (environment_texts_probe.py, run at the base build and at this item's; docs/composition/cmp-s3-cfr-1/environment-texts.json):
  - All 154 lists `relational-fol@0, right-clauses@0` with up to two more environment profiles: 0 texts move.
  - All 106 lists norms, relational-fol, right-clauses, rights and soft-norms with up to two more profiles, on 9.1's
    environment: 37 move. 16 become `ok`. 21 become `UnsupportedProfile: the norms route admits FOL documents only`
    (with closure@0, nary@0 or order@0). Each of the 37 equals the same list's answer without `right-clauses@0`.
    The other 69 keep the base text, which refuses the profile by name.
  The first self-review's probe held only the 154 lists. This item's second self-review found the 21 moved refusals
  (its A). They are DELTA row 1's condition ("answers exactly as the same request without it"). The DRI confirmed
  this (dri-decisions-20261110-cmp-s3-cfr-1-env.md item 1). Before the acts gate was kept on the base rows, 15 `acts@0` lists differed
  (the first self-review's B4).
- **What the proof changed in this item's code.** Members are rewritten with `Std.TreeMap.Raw.map` (`mapMember`)
  rather than `setObjVal!`, which keeps every other member and the tree's shape. `lineWith` rebuilds the `norm` and
  `liberty` objects, which the soft decoder reads through their member lists. A parsed object is its own
  rebuilding, so no answer moves: the K1 bytes and the 9.3 evidence are unchanged.
- **`NoClauseKeys`** quantifies over every `lines` member of every `right`/`right_lines` member of every unit. That
  is 8.5's "no line object has `clauses` or `relation`" for any JSON value, including one whose object tree holds a
  key twice.

## Review fixes (review of b8d143bc, cmp-s3-cfr-1-review.final.md)

- **F1 (A).** The R16 ties-pass row and the spec-erratum line (11-09 item 2) were claimed but not filed. Filed in
  FOLLOW-UPS.md as `## cmp-s3-cfr-1`; the same text is evidence/follow-ups-row.md. The review's probe passes. It is
  not a pytest: FOLLOW-UPS.md lives outside the tree, and tests are hermetic.
- **F2 (A).** The records said the model mode "refuses the name as on main". Lean checks the environment, then the
  model's tables, then the profile list, so a faulty model gets the answer it gets without the profile (main refused
  it by the name). DELTA row 1, "Environments" above and the test docstring now say so. The class: every one-node
  mutation of a valid model (126 replacements and the dropped keys, at least twelve `InvalidModel` texts) answers as without
  the profile when that is a fault, and is refused by the name when the model holds
  (test_right_clauses_model_mode_faulty_models_answer_as_without_the_profile); the review's two models are pinned in
  test_right_clauses_environment_and_model_answer_as_without_the_profile. Behaviour unchanged; inside DELTA row 1's
  condition, as the review says.
- **F-ready1 (B).** review-ready's relay mutation gate ran a `ve_service` older than the tree, so the handshake failed
  for every route. On a fresh build the gate passes (48 routes, 150,599 mutants, 0 failures). The class: the gate now
  builds the service and every one-shot runner before it asks any (`build_executables`, skipped under
  `VE_LEAN_PREBUILT` and without lake, as tests/lean_build.py does), and a failed build fails the gate.

## Seeded bugs (each planted alone, restored; test run on a build of the change)

| Bug | Language, file | Fails |
|---|---|---|
| The decoder accepts a structured line with two relations (an array, first taken) | Lean, lean/VE/RightClauses/Wire.lean `decodeRelation` | tests/test_right_clauses.py::test_right_clauses_k_fixtures_service (`two-relations`) |
| Registration dropped (`environmentWrappers := ["readings@1"]`) | Lean, lean/VE/Compose/Dispatch.lean | tests/test_right_clauses.py::test_right_clauses_k1_service_identity (the environment is refused: `UnsupportedProfile`); also the `environmentProfiles` #guard of lean/VE/Compose/Examples.lean at build |
| Plained bytes changed for an unstructured document (`elided` kept in the plained line) | Lean, lean/VE/RightClauses/Wire.lean `plainLineJson` | tests/test_right_clauses.py::test_right_clauses_k1_service_identity (the bytes assertion, line 111) |
| No model reduction for `right-clauses@0` | Python, ve/profiles.py `MODEL_REDUCTIONS` | tests/test_model_environment.py::test_every_registered_profile_has_one_model_reduction |
| No deadline for `clauses-elaborate` | Python, ve/backends/lean_service.py `DEADLINES` | tests/test_lean_service.py::test_the_deadline_keys_are_the_handshakes_modes |
| DELTA's negative test, profile off: a rights record changes (`runCaseReported` appends `!` to every refusal) | Lean, lean/VE/Rights/Run.lean (frozen; planted for this run only and restored) | tests/test_right_clauses.py::test_right_clauses_profile_off_evidence. Planted; ve_service built; profile_off_evidence.py rerun into profile-off.json as `head_answers` (6 of 28 answers move); the test fails ("At index 0 diff"); file and source restored |
| DELTA's negative test, environments: the rights decoder reads the frame with the profile (`withoutClauses` dropped) | Lean, lean/VE/Service/Standalone.lean `validatedLayerEnvironment` | tests/test_right_clauses.py::test_right_clauses_environment_texts_kept |
| The composed gate (document layers) reads the base rows | Lean, lean/VE/Service/Standalone.lean `validatedComposedEnvironment` | tests/test_right_clauses.py::test_right_clauses_environment_texts_kept (after the `documents@1, judgments@0` fixture; the probe lists alone missed it) |
| Review F2: the model mode skips a model's table fault (`\| .error _ => reported modelCase j`), so a faulty model under the profile is refused by the name, as on main | Lean, lean/VE/Service/Standalone.lean `reportedModel` | tests/test_right_clauses.py::test_right_clauses_model_mode_faulty_models_answer_as_without_the_profile and ::test_right_clauses_environment_and_model_answer_as_without_the_profile (both fail; the build pinned in a temporary copy of lean/checkers.lock) |
| Review F-ready1: the relay gate asks without building (`failure = None`) | Python, tools/relay_mutation_gate.py `main` | tests/test_relay_mutation_gate.py::test_the_gate_builds_every_executable_it_asks_before_asking |

Each was planted alone by /tmp's seed script: plant, `lake build ve_service`, run the named test with the build
pinned in a temporary lock, restore, rebuild. The Python ones needed no build. mutants.json lists them. One mutant per new trusted definition: trust mutants, below.

## Trust mutants (R16: a mutant per new trusted definition)

`zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/RightClauses/RunExamples.lean --allow
docs/composition/cmp-s3-cfr-1/trust-mutants-allow.json --rescore <the previous JSON> --json
docs/composition/cmp-s3-cfr-1/trust-mutants.json` exits 0: "206 KILLED, 0 SURVIVOR, 0 UNKNOWN, 10 INVALID, 57
ALLOWED, 0 NOT RUN" over 24 definitions and 273 mutants. It ran on the VM, because ve-mac-1 was unreachable.
The sweep was not rerun after the second self-review's Lean edits. Those edits added only a P definition and its
lemma (`plainOnWireB`, `plainOnWire_of_check`), T fixtures and `#guard`s. No trusted definition changed, and a new
`#guard` can only kill more mutants. `trust_map.py --check` still gives trusted +137.

- The sweep did not reach every new or changed trusted definition. It made no killed mutant for `rebuild`,
  `decodeRelationOpt`, `ResponseShape.Skeletons.clausesElaborate`, `VE.Service.Mode.name`, `VE.Service.runMode` or
  `validatedComposedEnvironment`. `unitsOf` is read only inside the S predicate `NoClauseKeys`.
  `VE.Service.Mode`'s only mutant is a constructor drop, which does not elaborate.
- Each of those six has a hand mutant, killed (mutants.json):
  - `decodeRelationOpt`: the K2 `#guard` (RunExamples.lean:45).
  - `rebuild`: test_right_clauses_k_fixtures_service.
  - `Mode.name`: the RegistryExamples.lean `#guard`.
  - The skeleton: Skeletons.lean's own `#guard`.
  - `runMode`: `runMode_clausesElaborate`, by `rfl`.
  - `validatedComposedEnvironment`: test_right_clauses_environment_texts_kept.
- The killing checks are the `#guard`s of lean/VE/RightClauses/RunExamples.lean (9.1's documents and section 7's
  texts), Compose/Examples.lean and RegistryExamples.lean.
- The first two sweeps' survivors that a check could kill now have fixtures in RunExamples.lean: a clause without
  `formula`, an extra member sorting first or last, two units with two premises, overlapping elided spans, the error
  row, and a wrapper in the middle of a list.
- The allow file gives each remaining survivor a one-line reason:
  - equivalent mutants: one-element lists, the canonical writer's fuel, a sorted list's first or last profile, and
    a check later refusing with the same text;
  - S predicates that only the 8.5 proofs read;
  - mutants that do not elaborate.

## Trust (R16)

`uv run python tools/trust_map.py --check` on the final tree: "against 6db6ee16ddb1: K +0, S +16, ... trusted +137",
"PASS: K, S and untied [V] within 6db6ee16ddb1 and the allowances introduced since". So S +16 and untied [V] +121,
recorded with `--allow ... --signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), cmp-s3-cfr-1, 2026-10-18"` in
docs/trust-baseline.json. Per file: Wire.lean S +16 and V +77, Run.lean +29, Dispatch.lean +11, Skeletons +2,
Schemas +1, Registry +1, Protocol +1, Standalone -1. Untied [V] is Wire.lean's clause, relation and elided readers (`decodeSpan`, `decodeRole`,
`hasKeys`, `decodeClause`, `decodeRelation`, `decodeElided`, `decodeClauses`, `decodeRelationOpt`, `unitSpanOf`,
`rebuild`, `mapDoc`, `unitsOf`), Run.lean (G[V]) and Dispatch's `environmentWrappers`, `withoutClauses` and
`environmentRows`. S is `NoClauseKeys`, `NoReadingSets` and `PlainOnWire`. Tied D[V]: `decodeClauseDoc`,
`elaborateJson`, `stripElided` and `stripProfile` to the 8.5 theorems; `plainLineJson`, `lineWith`, `headKeys`,
`mapUnit`, `headStep`, `headUnit`, `headLine`, `unitBody`, `dropKeys`, `bodyLines`, `mapMember`, `mapArr`,
`members`, `bodyRight` and `jsonLineName` to the forward lemmas that state them against `plainSource`, `CLine` or
`lineName`. Proof modules are P. FOLLOW-UPS row: "## cmp-s3-cfr-1" (filed in the fix round, review F1; its text is
docs/composition/cmp-s3-cfr-1/evidence/follow-ups-row.md: the ties pass and the spec erratum of 11-09 item 2).

## Size

Exempt proof lines, measured with `git diff --numstat` against the merge base: WireDecode.lean 324, WireName.lean
161 and WireTheorems.lean 912, which is 1,397. That is past the ~800 trigger of
dri-decisions-20261109-cmp-s3-cfr-1-size.md item 1. The DRI accepted them as delivered: exempt, with no cut and no
compaction (reviews/dri-decisions-20261109-cmp-s3-cfr-1-proofsize.md item 1).

Counted hand-written lines, from `git diff --numstat` against the merge base (2026-11-10), about 1,660 in all:
- Product, 418: Wire.lean 230, Run.lean 40, response shape and encoder 50, assurance manifest 26, RIGHT-CLAUSES.md 21,
  Dispatch 16, Standalone 6, VE.lean 6, Registry/Protocol/Schemas 11, Python 5.
- Tests, 530: tests/test_right_clauses.py 278, RunExamples.lean 143, tests/data/right-clauses-environment.json 71,
  other test and corpus edits 38.
- Side tables, 209: tools/trust-classes.json 182, relay-gate allow 20, lean-mode deps 6, layer policy 1.
- Docs and evidence, 500: this REPORT 212, mutants.json 159, trust-mutants-allow.json 46, the two evidence scripts 59,
  DELTA.md 20, other docs 4.
This is far past the ~600 line. The earlier figure, about 410, counted product lines only. The proof exemption covers
the three proof modules alone. Most of the overrun is fixtures, mutants and evidence that the reviews and R16 asked
for. The DRI accepted it as delivered, with no cut (dri-decisions-20261110-cmp-s3-cfr-1-count.md item 1).

Generated, not counted: statements.txt, predicates.txt, declarations.txt, Audit, the schemas, profile_table.json, the
binding answers and profile-off.json (the evidence script's output).

## Generated and recorded files

`regen_generated --write` wrote 37 entries; `python3 lean/audit.py` gives "PASS: 797 source files; 8836 named theorem
declarations audited ... only the declared standard axiom allowlist". `binding_census --answers` re-asked every
recorded relay-gate case on this build. That also rewrote some rows of other modes in
tests/data/binding-answers.jsonl.gz (for example the `actions_version` field and document rows, which moved on main
since that file was recorded). A merge with main should regenerate the file rather than merge it.

## Spec re-read

- `decode_unstructured` against docs/spec/right-clauses.md:528-533: word for word (names qualified as in the file).
- `elaborate_plain` against :534-541: word for word, plus `(hd : PlainOnWire D)` after `hp` (cmp-s3 Q1 A1).
  `PlainOnWire` states Q1 A1's "within maxDepth / maxNodes as the wire counts them" as "W1's `budgetFormula` reads
  the plain guard's encoding back". That is stronger than a bound on depth and nodes alone, because it also asks
  the decoder to return the same formula. No lemma derives it from the bounds. To show it is not vacuous,
  `plainOnWireB` (sound by `plainOnWire_of_check`, WireTheorems.lean) holds on K2 and K4 and fails on the depth-64
  counterexample (RunExamples.lean `#guard`s). The DRI confirmed this form (dri-decisions-20261110-cmp-s3-cfr-1-env.md item 2).
- 8.5's notes :543-548: `stripElided` removes `elided` (and the unit `span`, see "The wire"); `stripProfile` removes
  `right-clauses@0` from the profile list; `NoClauseKeys`, `NoReadingSets` and `elaborateJson` are as the notes
  describe. `elaborateJson` writes each structured line's guard as `plainGuard`, and candidates are cmp-s3-cfr-1c's.
- 8.1 :306-315: the mode's input and output, except `elided_bytes` (cmp-s3a-cfr-3, task (2)). The rows of
  `right-clauses@0` are unchanged; D29, D33, D41 and D52 are checked by tests/test_compose_dispatch.py.
- Section 7 :275-302: each text is a `#guard` in RunExamples.lean and a fixture in tests/test_right_clauses.py.
- 9.1 :562-584: K1-K9 and K15 on the service and as `#guard`s. K10 is the rights decoder's text. K11-K14 are
  cmp-s3-cfr-1b's (K12 cmp-s3-cfr-1c's).
- 9.3 :596-605: profile off as saved evidence; profile on with `elided: []` as a live comparison, the rights
  mode's answers (verdicts, statuses) included.

## Not changed

Rights/*, SoftNorms/*, Norms/*, Route/* and Plain.lean are untouched. No import of `VE.Readings`: the transitive
imports of Run.lean and the proof modules hold no `VE.Readings.*` or `VE.Scope.*` module. `route-cases.jsonl` has no
rows for the mode: it holds the case-kind route modes (`ROUTE_MODES`), and `clauses-elaborate` has no kinds, like
`words` and `english.command`. Its fixtures are tests/test_right_clauses.py and the relay-gate rows.

## 9.3's fixture set

Spec 9.3 names "rights' seventeen fixture shapes". The profile-off evidence uses the 28 rights rows of
tests/data/route-cases.jsonl. The profile-on test uses the 21 of those whose document is an array under `rights@0`.
These rows are not mapped one to one onto rights.md 10's seventeen shapes, so this item claims only the recorded
rows. The mapping is left to cmp-s3-cfr-1b, whose task holds the remaining 9.x fixtures.

## Pilot bytes

None are expected from this item: no relay sends a document to the mode yet (cmp-s3-cfr-1b), and with the profile
off nothing changes. The UDHR figure of spec 9.3 is cmp-s3-cfr-1b's estimate.

## Decisions read

reviews/dri-decisions-20261104-cmp-s3.md (Q1 A1, Q2), dri-decisions-20261109-lp0801.md item 1,
dri-decisions-20261109-l1-c-regrade-rights.md item 3, dri-decisions-20261109-adv0838.md item 3,
dri-decisions-20261109-adv0947.md item 1, dri-decisions-20261031-spec-right-clauses.md item 2,
dri-decisions-20261109-cmp-s3-cfr-1.md items 1-4, the size rulings dri-decisions-20261109-cmp-s3-cfr-1-size.md and
-proofsize.md item 1, and dri-decisions-20261110-cmp-s3-cfr-1-env.md items 1-2 and -count.md item 1.

## Next items

cmp-s3-cfr-1b (relay, differential, fixtures, W1, `clauseSlot_wellFormed`) and cmp-s3a-cfr-3 (`elided_bytes`).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained answers: PASS. `clauses-elaborate.json` types every leaf (plained and labels non-empty text,
   ast `generated_formula`), and `runCaseReported_fits` proves the runner's rows fit it.
   `tools/relay_mutation_gate.py --route service:clauses-elaborate`: "528 mutants, 526 refused, 2 allowed,
   0 failures". The two allowed (empty or repeated slot) are genuine forms, allow-listed as CFR1A/CFR1B for
   cmp-s3-cfr-1b's binding.
2. Deliverables: PASS. The table above covers (1)-(5). Reading candidates are cmp-s3-cfr-1c, asked of the DRI
   (inbox 20261109T170709Z) before any cut. `elided_bytes` is cmp-s3a-cfr-3's by the task.
3. Tests can fail: PASS. Eight seeded bugs in the table and six hand mutants, each killed by a named test or `#guard`
   (mutants.json). Trust mutants: 206 killed, 0 survivors, exit 0 (trust-mutants.json, trust-mutants-allow.json;
   section "Trust mutants").
4. Python/Lean agree: N.A. No Python decoder (Lean only); the differential is cmp-s3-cfr-1b's.
5. R8 binding: N.A. No relay yet (cmp-s3-cfr-1b). The schema is closed and typed, and the relay gate passes.
6. Gate evidence matches HEAD: PASS. The chain runs the gate on the final HEAD. The 9.3 evidence is saved
   (profile-off.json), and no test reads live git.
7. No unsigned item: PASS. The DELTA row cites the 10-31 DRI signature with 11-09 item 4. 11-10 -env item 1 confirms
   the 37 moved answers. Trust cites R16. The statement change cites cmp-s3 Q1, and -env item 2 confirms its form. Both
   overruns are ruled: the proof lines by proofsize item 1, the counted lines by 11-10 -count item 1.
8. DELTA: PASS. Profile off: test_right_clauses_profile_off_evidence. Environment texts: the probe and
   test_right_clauses_environment_texts_kept (0 of 154 lists move; 37 of 106 rights lists move, each to its answer
   without the profile). Profile on: test_right_clauses_profile_on_regression.
9. Test selection: PASS. tests/test_right_clauses.py imports the service corpus and the fixtures. The final selected
   run (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select`, on the VM, as `MAC_LAST` chose) on committed b2f4dbf7f
   (tree 2a40536e8b) recorded 557 units, 0 failed, exit 0. After it, one test file changed:
   test_right_clauses_environment_and_model_answer_as_without_the_profile now pins one refused list, the condition of
   11-10 -env item 1. tests/test_right_clauses.py then gave 7 passed. The chain's gate reruns the selection.
   The earlier run's two failures, on committed 2d2b08d8c, were fixed then: test_assurance_manifest's
   classification and a `clauses-elaborate` seed.
10. Statements: PASS. "Spec re-read" above; `python3 lean/audit.py` PASS.
11. Budgets fail closed: PASS, as far as this item reaches. Units are checked at most 1,024 before decoding; W1's
    budget applies to each clause formula and plain guard (RunExamples' depth-65 `#guard` gives `ResourceLimit`).
    W1's large-document fixture is cmp-s3-cfr-1b's (asked, point 3).
12. CPU/memory: PASS with a stated cost ("The wire": lines decoded twice plus once; quadratic in named lines). No
    route calls the mode yet.
13. Test-removed trailers: N.A. No test removed; `test_right_clauses_profile_off_regression` was renamed before any
    merge, inside this branch.
14. Both directions, cited evidence, spec re-read: PASS. Acceptance (K1-K4, roles, profile on) and refusal (each
    section 7 text) are both tested; outputs are cited in this REPORT; spec re-read above.
15. Overclaim: PASS. Universal words in REPORT/DELTA name their probe or test. No silent cut: candidates asked.
    Every new check can fail: seeded bugs and trust mutants. Limits charged before work: units before decoding;
    clause formulas by W1 as decoded.

SELF-REVIEW: 1 A, 5 B, 8 C; fixed 12. The A and all five B are fixed (A: evidence over the rights lists, DELTA
corrected, DRI asked). Two C are left: the corpus importing test_right_clauses (a cycle that works today), and
binding-answers.jsonl.gz's rows of other modes, which a merge regenerates.
