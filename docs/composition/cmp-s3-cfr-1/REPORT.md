# cmp-s3-cfr-1: the right-clauses wire, the `clauses-elaborate` mode and the registration (cmp-s3b part 1)

Status: deliverables (1) to (5) built. 8.5's `decode_unstructured` and `elaborate_plain` are proved, with no `sorry`.
No DRI signature is reserved. Decisions read: reviews/dri-decisions-20261104-cmp-s3.md (Q1 A1, Q2),
dri-decisions-20261109-lp0801.md item 1, dri-decisions-20261109-l1-c-regrade-rights.md item 3,
dri-decisions-20261109-adv0838.md item 3, dri-decisions-20261109-adv0947.md item 1,
dri-decisions-20261031-spec-right-clauses.md item 2, and this item's own size rulings
(dri-decisions-20261109-cmp-s3-cfr-1-size.md item 1, dri-decisions-20261109-cmp-s3-cfr-1-proofsize.md item 1).
HEAD: the branch tip (the chain's gate records the commit it ran on in gate-result.json).

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
  `clauseSlot_wellFormed`.
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
  (reviews/dri-decisions-20261109-cmp-s3-cfr-1.md item 2); the spec erratum is a FOLLOW-UPS line. cmp-s3-cfr-1b's
  relay must match both.
- **Order (4.1 step 2, 7).** Units in document order. In each unit, every line object goes through `decodeLine` on
  the object without the three keys (this gives `<n>`), then `elided`, `clauses` (each clause in order) and
  `relation`; then rights' own `addUnit` runs on the unit without its span and keys.
- **Cost.** A line object is decoded twice by the head (`headLine`, `addUnit`) and once more by the rights decoder on
  the plained document. `plainLineJson`'s `D.lines.find?` makes elaboration quadratic in the number of named lines.
  Units are capped at 1,024; lines per unit are not. cmp-s3-cfr-1b's large-document fixture (W1) must cover lines per
  unit, not only units.
- **Environments.** No refusal text moves. `right-clauses@0` beside `acts@0` stays refused by the base rows, as before
  (Standalone keeps that gate's whole-table read for `readings@1` only). With `rights@0`, the environment mode now
  accepts the list, where the base refused it as an unregistered profile, and answers as without the profile but for
  the echoed list and the identity. The model mode still refuses the name (DELTA row 1;
  test_right_clauses_environment_and_model_answer_as_without_the_profile). Python's model view drops the profile. Probe: all 154 lists `relational-fol@0, right-clauses@0` with up to two
  more environment profiles answer the same text on this build and on the base build (0 differences: docs/composition/cmp-s3-cfr-1/environment-texts.json,
  written by environment_texts_probe.py in both worktrees). Before the acts gate was kept on the base rows, 15 `acts@0`
  lists differed; that was the self-review's B4.
- **What the proof changed in this item's code.** Members are rewritten with `Std.TreeMap.Raw.map` (`mapMember`)
  rather than `setObjVal!`, which keeps every other member and the tree's shape. `lineWith` rebuilds the `norm` and
  `liberty` objects, which the soft decoder reads through their member lists. A parsed object is its own
  rebuilding, so no answer moves: the K1 bytes and the 9.3 evidence are unchanged.
- **`NoClauseKeys`** quantifies over every `lines` member of every `right`/`right_lines` member of every unit. That
  is 8.5's "no line object has `clauses` or `relation`" for any JSON value, including one whose object tree holds a
  key twice.

## Seeded bugs (each planted alone, restored; test run on a build of the change)

| Bug | Language, file | Fails |
|---|---|---|
| The decoder accepts a structured line with two relations (an array, first taken) | Lean, lean/VE/RightClauses/Wire.lean `decodeRelation` | tests/test_right_clauses.py::test_right_clauses_k_fixtures_service (`two-relations`) |
| Registration dropped (`environmentWrappers := ["readings@1"]`) | Lean, lean/VE/Compose/Dispatch.lean | tests/test_right_clauses.py::test_right_clauses_k1_service_identity (the environment is refused: `UnsupportedProfile`); also the `environmentProfiles` #guard of lean/VE/Compose/Examples.lean at build |
| Plained bytes changed for an unstructured document (`elided` kept in the plained line) | Lean, lean/VE/RightClauses/Wire.lean `plainLineJson` | tests/test_right_clauses.py::test_right_clauses_k1_service_identity (the bytes assertion, line 111) |
| No model reduction for `right-clauses@0` | Python, ve/profiles.py `MODEL_REDUCTIONS` | tests/test_model_environment.py::test_every_registered_profile_has_one_model_reduction (and ::test_the_oracle_reaches_every_profile_and_display_field) |
| No deadline for `clauses-elaborate` | Python, ve/backends/lean_service.py `DEADLINES` | tests/test_lean_service.py::test_the_deadline_keys_are_the_handshakes_modes |
| DELTA's negative test: a profile-off rights record changes (a rights refusal text edited) | Lean, lean/VE/Rights/Run.lean (frozen; planted for this run only and restored) | tests/test_right_clauses.py::test_right_clauses_profile_off_regression (the saved-digest assertion, line 184) |

Each was planted alone by /tmp's seed script: plant, `lake build ve_service`, run the named test with the build
pinned in a temporary lock, restore, rebuild. The Python ones needed no build. mutants.json lists them. One mutant per new trusted definition: trust mutants, below.

## Trust mutants (R16: a mutant per new trusted definition)

`zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/RightClauses/RunExamples.lean --allow
docs/composition/cmp-s3-cfr-1/trust-mutants-allow.json --rescore <the previous JSON> --json
docs/composition/cmp-s3-cfr-1/trust-mutants.json` exits 0: "206 KILLED, 0 SURVIVOR, 0 UNKNOWN, 10 INVALID, 57
ALLOWED, 0 NOT RUN" over 24 definitions and 273 mutants. It ran on the VM, because ve-mac-1 was unreachable.

- Every D[V] and G[V] definition has a killed mutant, except two. `unitsOf` is read only inside the S predicate
  `NoClauseKeys`. `VE.Service.Mode`'s only mutant is a constructor drop, which does not elaborate.
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
`lineName`. Proof modules are P. FOLLOW-UPS row: "## cmp-s3-cfr-1".

## Size

Exempt proof lines, measured with `git diff --numstat` against the merge base: WireDecode.lean 324, WireName.lean
161 and WireTheorems.lean 912, which is 1,397. That is past the ~800 trigger of
dri-decisions-20261109-cmp-s3-cfr-1-size.md item 1. The DRI accepted them as delivered: exempt, with no cut and no
compaction (reviews/dri-decisions-20261109-cmp-s3-cfr-1-proofsize.md item 1).

Counted hand-written lines:
- Product, about 410: Wire.lean 230, Run.lean 37, the response shape and encoder 50, Dispatch 21, Standalone 15,
  Registry/Protocol/RegistryExamples 17, Compose/Examples 4, VE.lean 5, Python 5.
- Tests, evidence and side tables: tests/test_right_clauses.py 202, other test and corpus edits 28, relay-gate rows
  and allow-list 23, the evidence script 20, tools/trust-classes.json 168.
- Docs: RIGHT-CLAUSES.md 23, this REPORT and DELTA.md.

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

## Pilot bytes

None are expected from this item: no relay sends a document to the mode yet (cmp-s3-cfr-1b), and with the profile
off nothing changes. The UDHR figure of spec 9.3 is cmp-s3-cfr-1b's estimate.

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
3. Tests can fail: PASS. Six seeded bugs, each killed by a named test (table above; mutants.json). Trust mutants:
   206 killed, 0 survivors, exit 0 (trust-mutants.json, trust-mutants-allow.json; section "Trust mutants").
4. Python/Lean agree: N.A. No Python decoder (Lean only); the differential is cmp-s3-cfr-1b's.
5. R8 binding: N.A. No relay yet (cmp-s3-cfr-1b). The schema is closed and typed, and the relay gate passes.
6. Gate evidence matches HEAD: PASS. The chain runs the gate on the final HEAD. The 9.3 evidence is saved
   (profile-off.json), and no test reads live git.
7. No unsigned item: PASS. The DELTA rows cite the 10-31 DRI signature and R16; the statement change cites cmp-s3 Q1.
   The size overrun is ruled (proofsize item 1).
8. DELTA: PASS. Profile off: test_right_clauses_profile_off_evidence. Environment texts: the probe and
   test_right_clauses_environment_texts_kept (0 of 154 lists differ). Profile on: test_right_clauses_profile_on_regression.
9. Test selection: PASS. tests/test_right_clauses.py imports the service corpus and the fixtures; the selected run
   on the final HEAD is recorded by the chain.
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
