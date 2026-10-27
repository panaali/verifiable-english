# qt-a3 report: the `ve-cardinality@1` decoders (quantities QT-A3, first part)

No DRI signature is reserved: DELTA row 1 (trust) cites R16 (V +124 after fix round 1). The item is cut by the size rule. Here: the environment
and statement decoders of spec 4.1–4.3 with spec 4.2's diagnostics in their order, `CEnv.WellFormed` established by
the decoder, admission and identities, and their fixtures. Next: **qt-a3b**, the certificate check
(`checkCertificate_sound`) and the case runner. Then **qt-a3c**, the mode and its shape, and **qt-a3d**, the document
and the paraphrase (the "Not delivered" section).

## Fix round 1 (review `qt-a3-review.final.md` of `1c24e1ac8`)

| Finding | Fix | Regression tests | Commit |
|---|---|---|---|
| F1 (B): no test pinned which `CFormula` a statement decodes to; 11 hand mutants (`lt`↔`le`, `gt`↔`ge`, `ties_up`↔`half_even`, body `and`→`or`, body `not` dropped, whole↔part, `percent_of` and `percent_rounds_to` operands swapped, `implies`→`or`, an operand's body replaced by `any`, the object-ratio check removed) survived; the elaborators' parts were classed C | The class: every operator name and argument order of the wire is pinned against the `CFormula` written out (`pins`, with arguments that differ so a swap shows), `ctor` makes `CFormula`'s constructors exhaustive there (a new constructor fails to build until pinned), and every known operator in another shape is pinned to S3's text. The parts (`elabBody`, `elabOperand`, `elabRatio`, `items`, the three name tables, `elabName`, `elabRule`, `printed`) are D[V], as W6a classes `elabTerm`; `elabFormula` stays C, as W6a's does. Each is stated about by a theorem of `WireTheorems.lean`: the `*_spelled` theorems say each name decodes to exactly its constructor (an exhaustive match in the statement), `elabBody_cases`, `elabOperand_cases`, `elabRatio_sound` (both operands of one quantity tag, not `day`), `items_ok`, `printed_eq`. Trust V +73 (R16) | `WireExamples.lean` `pins` and `ctor` guards (:178–:187), wrong-shape guards (:245–:256); `tests/test_cardinality_exercised.py::test_each_qt_a3_f1_helper_is_trusted_and_stated_about_by_its_theorem`; `mutants.json` `f1-*` (10 of 10 killed); PROBE F1 exits 0 | `8e94e7bd0`, `3df54d939`, `4f95e50b4` |
| F2 (B): S2 counted nodes only; depth 64 was each elaborator's fuel, which restarts in bodies and W6a parts, so `["and", ["bogus"], <depth 65>]` gave S3's text and 62 levels around a 62-deep body were admitted | S2 is `sourceFits`: at most 10,000 array nodes, nested at most 64 arrays deep (`arrayDepth`), over the whole formula, before the pass (spec 4.2 rule 1, correction E6a). Depth is counted over the same array nodes S2 counts, so a count, whose terms add two arrays, is 4 deep. `decodeStatement_fits` and `sourceFits_iff` state it | `WireExamples.lean` S2-depth section (:269–:293): the probe's statement, depth 64 and 65 at the formula, in a body and in a W6a part (which W6a alone admits at 65), 62 around 62; the 10,000/10,001-node boundary (:349–:353); `mutants.json` `f2-*` (3 of 3); PROBE F2 exits 0 | `8e94e7bd0`, `4f95e50b4` |
| F3 (C): size | not changed: fix round 1 adds about 330 lines (fixtures, theorems, evidence); see "Trust, size and evidence" | | |
| F4 (C): no guard pinned "TypeMismatch: Ratio needs quantity terms" | pinned, with an object-sorted constant; and, as a class, every refusal text of `Wire.lean` now has a guard except the unreachable "cardinality environment is not well formed" | `WireExamples.lean` :264–:267; `mutants.json` `f4-ratio-object` | `8e94e7bd0` |

Sweep (F2): W6a's `VE.Time.Wire.decodeQuantity` has the same per-elaborator depth. It is outside this item, and fixing it changes W6a's route answers, so it is a FOLLOW-UPS row ("## qt-a3 fix1"). Probes: both failed before the fix (F1: 3 surviving mutants; F2: the guard did not evaluate to `true`) and pass after it. PROBE F1 cannot be a pytest (it rebuilds Lean three times); its three mutants are in `mutants.json`.

## Statement gate

QT-A3's statements were reviewed in QT-0 (ten corrections, verified in manage-agents `quantities-p3ver1.final.md`).
Plan and spec are main's (`docs/spec/quantities-PLAN.md`, `docs/spec/quantities.md`, unchanged).

This item proves none of the plan's four theorems (rows below), so no approved statement is touched. It does deliver
`projectW6`, `CardEnv` and `CAdmission`, and these equal spec 4.3's text after whitespace normalisation, checked by
a script over `quantities.md` and `Wire.lean`. Following the plan's block (`namespace VE.Cardinality`), they are
`VE.Cardinality.projectW6`, `VE.Cardinality.CardEnv` and `VE.Cardinality.CAdmission`.

`checkCertificate_sound` was also built and proved; it is kept for qt-a3b (below). Its text equals both the plan's and
spec 4.3's after whitespace normalisation, and QT-0's correction C10 is in the spec form of
`admit_cardinality_report_sound`. The new theorems are helpers that no plan statement names: `CAdmission.sound`,
`wellFormed_of`, `profileLists_projected`, `finiteSorts_length`, `decodeEnvironment_sound`,
`decodeStatement_identity`, and (fix round 1) `decodeStatement_fits`, `sourceFits_iff`, `elabName_mem`,
`relNames_spelled`, `cmpNames_spelled`, `ruleNames_spelled`, `items_ok`, `elabBody_cases`, `elabOperand_cases`,
`elabRatio_sound` and `printed_eq`. `lean/statements.txt` only gains lines.

## Plan rows (QT-A3, task order)

| Row | Delivered | Where, checked by |
|---|---|---|
| `Wire.lean`: `CardEnv` with the W6a projection `projectW6` decoded by `VE.Time.Wire.decodeEnvironment` | yes, spec 4.3's text. `CardEnv.w6` is W6a's decoding of the projection, with its two W6a identities. `environmentId` is over the original environment, with `cardinality@0` in its profiles. `decodeEnvironment_sound` states all three | `lean/VE/Cardinality/Wire.lean`, `WireTheorems.lean`; FA11 guards (golden identities, the `documents@1` list, draft 1's E4 refused by W6a) |
| `CAdmission` | yes (spec 4.3). `CAdmission.sound`: the formula satisfies the independent `Admitted` | same |
| `CardCertificate` | **qt-a3b**, with `checkCertificate`, its only reader: an unused trusted structure could not be exercised (R16) | |
| The decoder proves the decoded `CEnv` `WellFormed` | yes. E5–E8 run as checks with their texts, then a final guard whose proof fills `wf` (`wellFormed_of`) | E5–E8 guards; `trust_mutants`: every mutant of that guard fails to elaborate |
| Limits in 2.4's order | partly: envelope and size (S1, S2: 10,000 array nodes nested at most 64 deep, over the whole formula) first, then one depth-first, left-to-right pass with S3–S10 at each node; E6 64 finite sorts; S7 64 terms; W6a's 40-digit limit. **P1–P3** (8 counted sorts, 6 predicates per sort, the erased aggregate) are problem limits, so they go to qt-a3b with the runner (`problemLimits` itself is QT-A1's) | FA13 guards; each text of 4.2 once |
| `Run.lean` with `checkCertificate_sound` | **qt-a3b**: built and proved (`checkCertificate` binds the cardinality identities, then W6a's two bindings to the regenerated problem in the projection's environment, the step limit, and the frozen replay; through `cardinality_elab_sound`), with the admission and certificate runner and its fixtures (FA1's certificate replays through the runner, FA1b's does not, FA11's two binding mismatches, the forged region table and erased problem). It is on the local branch `wip/qt-a3b-run` (`fa3c92578`). Cut because it brings the item to about 1,150 lines | |
| `Protocol.lean`/`Registry.lean` constructor, name, list entry, dispatch, `runMode_cardinality`; `MODES` | **qt-a3c** (needs the runner) | |
| The `cardinality@0` row of AR-10's table with its composition proof | **qt-a3c**. A base row puts `cardinality@0` in every route's gate and in Python's generated `BY_NAME` (ap-1b's `acts@0` row brought four DELTA rows), so it lands with the mode. Until then E2 is spec 4.2's fixed text over `profileLists` (`cardinality@0` with one of W6a's two lists); `profileLists_projected` shows such a list projects onto W6a's own. When the row lands, E2 comes from `gateOf` and `profileLists` is deleted (FOLLOW-UPS) | |
| `Document.lean` (`admitDocument`, `admit_cardinality_report_sound`), `Render.lean` | **qt-a3d** (the task's example cut) | |
| `Schemas`/`Encoders/Cardinality.lean` with `runCaseReported_fits` | **qt-a3c** (they describe the runner's rows) | |
| `ve/assurance-manifest.json` decoder pins | yes: `lean/VE/Cardinality/Wire.lean` pinned whole (four declarations); `WireExamples.lean` under `other_json` (fixtures only) | `tests/test_assurance_manifest.py` |
| `ROADMAP.md` trust-cost line | yes | |
| Generated files via regen | yes: `regen_generated.py --write`, then `--check` (33 entries) | |
| Fixtures FA1, FA1b | at the decoder: the wire decodes exactly the core's FA1 premises and conclusion, and FA1b's premises (`DecidableEq` against `VE.Cardinality.Examples.fa1`), so `fa1_entails` and `fa1b_not_entails` are about the decoded statements. As route cases: qt-a3b (runner) and qt-a3c (service) | `WireExamples.lean` |
| QT-A1's hostile set at the wire, each diagnostic in 2.4's order | yes: FA8 (count over a sort not declared finite, a binary predicate, another sort's predicate, proportions 3 in 2, 0 in 0, −1 in 2) and FA9 (a declared region-prefixed constant, sort or predicate; ratios of dates, mixed tags, `down` and `up`). FA8's seven-predicate problem limit is P2 (qt-a3b) | same |
| A forged region table and a forged erased problem | **qt-a3b**: they are claims on a case, checked by the runner | |
| FA11 | the projection decodes with W6a's first and second lists; the three identities differ, golden-pinned; draft 1 refused. The two binding mismatches are certificate cases (qt-a3b) | same |
| FA13 | all five: S5 before S8 and S9 before S10 in one node; two faulty nodes either way round; an operand's fault before its node's tag mismatch; S2 before an unknown operator; statements in request order | same |
| The plan's seeded bug | yes: `plan-count-not-finite` (below) | `mutants.json` |

### Diagnostics and order

Environment E1–E8 and statement S1–S10 run as spec 4.2 says. E4 is W6a's decoder on `projectW6`, with its own texts.
S4 is W6a's `elabFormula` or `elabTerm`, unchanged. A ratio's operands are each elaborated in full, left to right,
before S9 compares their tags. S10 comes last. After the pass, the decoded formula must pass the proved
`CFormula.admits`. The meaning id is over `{"format": "ve-cardinality@1", "formula": F}`, with `F` the canonical
encoding (`encode`), in the cardinality environment's identity (`decodeStatement_identity`). A printed number keeps
its written places, so "0.30" and "0.3" are different ids. W6a's canonical decimal spelling makes `-0.0` and `0.0`
the same id.

S2's depth is the nesting of the formula's arrays, the nodes S2 counts (fix round 1, F2); the elaborators' fuel
restarts in bodies and W6a parts and is not this limit.

Three texts that spec 4.2 does not name (spec wording, C; FOLLOW-UPS); the first two are pinned by guards:
- "Invalid cardinality formula": a known operator in the wrong shape (S3).
- "TypeMismatch: Ratio needs quantity terms": an operand of an object sort (S9).
- "InvalidInput: cardinality environment is not well formed": the proof-carrying guard after E7 and E8, which those
  checks make unreachable.

### Trust classes

The classes follow W6a's wire (`tools/trust-classes.json`).
- **Trusted:** the decoders that build the environment and the admission record, S2 (`sourceFits`, `arrayDepth`),
  and the elaborators' parts (`elabBody`, `elabOperand`, `elabRatio`, `items`, `relNames`, `cmpNames`, `ruleNames`,
  `elabName`, `elabRule`, `printed`) are D[V], as W6a classes `elabTerm`: `admits` checks typing only, so what a
  name or argument decodes to is trusted (review F1). `CardEnv` and `CAdmission` are tied by `CAdmission.sound`.
- **C, as `VE.Time.Wire.elabFormula` is:** `elabFormula`. What each of its operators decodes to is pinned by the
  `pins` guards; the FOLLOW-UPS row asks whether both wires' `elabFormula` should stay C.
- **Reject-only:** `countedSort`, `admittedRule` and `checkDeclarations`. A missed refusal there is still refused by
  `admits` or by the `WellFormed` proof.
- **D[I]:** the identity encoders.

## Seeded bugs

[`mutants.json`](mutants.json): 32 of 32 killed, all in Lean (`lean/VE/Cardinality/Wire.lean`): the first 18, the
reviewer's 11 hand mutants of F1 (`f1-*`, `f4-*`) and 3 of F2 (`f2-*`). No Python or Rust product code changed.
`uv run python tools/mutants.py docs/quantities/qt-a3/mutants.json --no-baseline`, evidence
[`evidence/mutants-run.json`](evidence/mutants-run.json), on the final Lean. Each mutant is applied alone and
`lake build VE.Cardinality.WireExamples` fails at a `#guard`, never at a proof (every error in each output is a
guard's). `WireExamples.lean` does not import `WireTheorems.lean`, whose proofs also break under most of these
mutants. Line numbers are in `WireExamples.lean`.

| Mutant | Definition | First failing guards |
|---|---|---|
| `plan-count-not-finite` (the plan's) | `countedSort` | :191; :326 |
| `projectW6-profiles` | `projectW6` | :344; :347 |
| `profileLists-docs` | `profileLists` | :79 |
| `finiteSorts-limit` | `finiteSorts` | :319 |
| `finiteSorts-fields` | `finiteSorts` | :313 |
| `environmentId-original` | `decodeEnvironment` | :73; :98 |
| `environment-schema` | `decodeEnvironment` | :306 |
| `environment-declarations` | `decodeEnvironment` | :214; :216 |
| `checkDeclarations-sorts` | `checkDeclarations` | :214; :216 |
| `statement-size` | `decodeStatement` | :347; :353 |
| `statement-format` | `decodeStatement` | :261 |
| `meaningId-profiles` | `decodeStatement` | :98 |
| `countedSort-atoms` | `countedSort` | :192; :194 |
| `ratio-day` | `elabRatio` | :223 |
| `admittedRule` | `admittedRule` | :226; :227 |
| `proportion-order` | `elabFormula` | :333 |
| `relNames-eq` | `relNames` | :95; :101 |
| `encPrinted-places` | `encPrinted` | :119 |
| `f1-rel-lt-le` | `relNames` | :178 |
| `f1-cmp-gt-ge` | `cmpNames` | :178 |
| `f1-rule-ties` | `ruleNames` | :178; :179 |
| `f1-body-and` | `elabBody` | :178 |
| `f1-body-not` | `elabBody` | :178 |
| `f1-proportion-order` | `elabFormula` | :178 |
| `f1-percent-of-order` | `elabFormula` | :178 |
| `f1-percent-rounds-order` | `elabFormula` | :178 |
| `f1-implies` | `elabFormula` | :178 |
| `f1-operand-body` | `elabOperand` | :178 |
| `f4-ratio-object` | `elabRatio` | :265 |
| `f2-depth` | `decodeStatement` | :277; :279 |
| `f2-depth-limit` | `sourceFits` | :277; :280 |
| `f2-depth-max` | `arrayDepth` | :276; :277 |

Mechanical mutants (R16, build checklist 13a): `mac-pytest.sh --trustmut -- --max-mutants 1000 --jobs 6 --allow ...`
on the final Lean change (`290c6a591`, ve-mac-1) found 15 trusted definitions and 191 mutants: 114 KILLED,
0 SURVIVOR, 0 UNKNOWN, 8 INVALID, 69 ALLOWED, exit 0 ([`trust-mutants.json`](trust-mutants.json)).

The first fix-round run (`4f95e50b4`'s parent, on the VM) had 14 survivors and 39 unknowns. The survivors were
S2's node count at exactly 10,000 (`≤`→`<`), an operand count's S6 list, and the "known operator in another shape"
lists of `elabBody` and `elabOperand`; the guards for the 10,000/10,001-node boundary, an operand's S6 and every
known operator in another shape now kill them (`4f95e50b4`). The allowed mutants, each with its reason in
[`trust-mutants-allow.json`](trust-mutants-allow.json):
- Mutants of the two dependent `if h :` conditions, whose proofs take `h` at its exact type, so they do not elaborate.
- `finiteSorts`'s `[]`, whose element type cannot be inferred.
- Match patterns edited into terms Lean refuses as patterns, or `[]` unbinding a branch's names; fuel patterns that
  stop terminating or miss a case; `Body.all`, which does not exist; `VE.Order.lookup` edited to `[]`.
- S2's fuel one higher (`jsonNodes` 258, `arrayDepth` 66) or `jsonNodes`' one lower (256): equivalent, since
  `arrayDepth` with fuel at least 65 bounds the depth exactly and within depth 64 `jsonNodes` counts every node.
  `arrayDepth`'s fuel 64 is KILLED.
- `projectW6` keeping `profiles` in its base: equivalent, since the re-added member replaces it.
The 8 INVALID mutants edit the namespace `VE.Order` of `VE.Order.lookup` into a list (`VE.Order.take` does not exist).

## Trust, size and evidence

- Trust (`tools/trust_map.py --check` on the final HEAD, against `110b3bf3a`, after the sync): K +0, S +0, untied
  V +124, all in `Wire.lean` (per definition in DELTA row 1): +51 in the first round, +73 in fix round 1. Both
  allowances are signed by R16. FOLLOW-UPS "## qt-a3" and "## qt-a3 fix1" ask for the ties pass.
- Size: about 790 hand-written lines over the merge base before this report and DELTA, and about 880 with them.
  Lean is 617 (`Wire.lean` 290, `WireExamples.lean` 249, `WireTheorems.lean` 78), side tables 102
  (`trust-classes.json` 81, the manifest 20, `VE.lean` 1), evidence 69 (`mutants.json` 42, the allow file 20, the
  allowance 7), and ROADMAP 1.

  Fix round 1 adds about 330 more (`WireExamples.lean` +114, `WireTheorems.lean` +125, `Wire.lean` +14,
  `mutants.json` +28, the allow file +20, side tables and tests about 40), so about 1,210 in all.

  That is over the ~600 guide after one cut, which moved the runner, `checkCertificate_sound` and their fixtures
  (about 360 lines) to qt-a3b. What remains is one fixture per text and order rule of spec 4.2, the plan's fixture
  list, and `WireTheorems.lean`, which `tests/test_cardinality_exercised.py` requires: every trusted definition of
  `lean/VE/Cardinality/` must be stated about by a theorem. A smaller part, only the environment decoder, would leave
  statements undecoded and is not a coherent unit.
- Tests:
  - Selected plan on ve-mac-1, 76 units. First run on `bc171d4ad`: 2 failures, both in
    `test_cardinality_exercised.py` (the decoders were stated about by no theorem); fixed in `84484c6d3`. Then on
    `a417f1766`: 76 of 76 pass, exit 0.
  - After syncing main (`110b3bf3a`, ap-1f), the files the merge and this item touch pass: 287 tests in
    `test_cardinality_exercised`, `test_assurance_manifest`, `test_trust_budget`, `test_trust_ratchet`,
    `test_lean_limits`, `test_frozen_sources` and `test_lean_audit_record`.
  - Also run on the merged HEAD: `regen_generated.py --check` (33 entries), `gate_collection.py --check --prebuilt`
    (0 added, 0 removed, 0 refused, 0 stale, 0 malformed), `repo_map.py --check` (38 modes), `check_lean_imports.py`,
    `lean/audit.py` (621 files, 7,053 theorems) and `trust_map.py --check`.
  - Not run: the full gate (the chain runs it on the final HEAD) and `relay_mutation_gate.py` (no relayed answer).
    No test in `main-known-red.txt` was touched.
- Pilot bytes: 0 expected (plan: "Bytes: 0"); nothing claimed.
- Overlap: no in-flight branch edits `lean/VE/Cardinality/` or `ROADMAP.md`. `lean/VE.lean` (a union import list) is
  also edited by `feature/ap-3`, `feature/df-1ae`, `feature/sc-1b` and `foundation/me-1`. `ve/assurance-manifest.json`
  (its merge keeps each side's pins) is also edited by `feature/df-1ae`, `feature/jt-2`, `feature/q1-4`,
  `feature/sc-1b`, `foundation/me-1` and two `infra/arch-20261026-*` branches. `lean/VE/Time/Wire.lean` is the
  base's, since W6a's shared helpers go to qt-a3b.

## Not delivered (next items)

- **qt-a3b**: `CardCertificate`, `checkCertificate` and `checkCertificate_sound`; P1–P3; the runner (`admission`
  and `certificate` cases, the region table, the regenerated problem with its W6a identities, claimed tables and
  problems refused); W6a's shared helpers (`statementIds`, `quantityLimits.aggregate`, `staleW6`, `staleCore`, so W6a
  stays their one owner); the fixtures above. It is built on `wip/qt-a3b-run` and needs a rebase onto this item.
- **qt-a3c**: the `cardinality` mode (registry, dispatch, `runMode_cardinality`, `DEADLINES`), `cardinality.json`
  with `runCaseReported_fits`, the `cardinality@0` table row with its composition theorem, route cases (FA1, FA1b,
  the hostile set), the `countermodel` case (budgeted, as W6a's `refutesB`).
- **qt-a3d**: `Document.lean` (`admitDocument`, `admit_cardinality_report_sound`) and `Render.lean` (the
  `paraphrase` case).
- Then QT-A4 (the relay and document hook).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed yet; the decoders' malformed inputs (wrong types, extra members, unknown
   operators, wrong shapes, depth 65, 10,002 nodes) are refused with their texts (`WireExamples.lean`, E1–E8 and
   S1–S10 guards).
2. PASS: plan-row table above, each row delivered or named for qt-a3b/c/d; no Python copy of a Lean decision; no
   permanent report test; overlap listed.
3. PASS: `mutants.json` 18/18 killed by `#guard`s (`evidence/mutants-run.json`); `trust-mutants.json` exit 0.
4. PASS: FA1 decodes to the core's statements (`DecidableEq`); the canonical encoding reads back as the request's
   formulas (`WireExamples.lean` :103, :119). No Rust change.
5. PASS (inputs; S2's depth over the whole statement in fix round 1): undeclared sorts (`UnknownSort(users)`), predicates of another sort or arity, an unknown constant,
   duplicates, and reserved names are refused (guards :127–:152, :216–:221). No relayed answer to bind yet.
6. PASS: synced with main (`110b3bf3a`) and regenerated; the chain runs the gate on the final HEAD.
7. PASS: DELTA row 1 cites R16 with per-file counts; FOLLOW-UPS "## qt-a3" has the ties-pass row.
8. PASS: DELTA states that no answer moves: `checkers.lock` and `route-cases.json` are the base's.
9. PASS: the selected plan included `test_cardinality_exercised.py`, which caught the missing theorems.
10. PASS: `checkCertificate_sound`'s text equals the plan's and the spec's (for qt-a3b); the new theorems'
    statements are about the returned values (`decodeEnvironment_sound`, `decodeStatement_identity`); the first
    mutants run, when they still shared `Wire.lean`, showed the decoders' mutants breaking their proofs.
11. PASS: limits at and past their values (64 and 65 finite sorts, 64 and 65 terms, array depth 64 and 65 at the
    formula, in a body and in a W6a part, 10,000 and 10,001 nodes);
    no budget or deadline code; no timing in tests.
12. N.A.: no runtime path changes; the decoder is one pass, bounded by S2's 10,000 nodes before it starts.
13. PASS: no test removed or renamed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
