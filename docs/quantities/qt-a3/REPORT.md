# qt-a3 report: the `ve-cardinality@1` decoders (quantities QT-A3, first part)

No DRI signature is reserved: DELTA row 1 (trust) cites R16. The item is cut by the size rule. Here: the environment
and statement decoders of spec 4.1–4.3 with spec 4.2's diagnostics in their order, `CEnv.WellFormed` established by
the decoder, admission and identities, and their fixtures. Next: **qt-a3b**, the certificate check
(`checkCertificate_sound`) and the case runner. Then **qt-a3c**, the mode and its shape, and **qt-a3d**, the document
and the paraphrase (the "Not delivered" section).

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
`wellFormed_of`, `profileLists_projected`, `finiteSorts_length`, `decodeEnvironment_sound` and
`decodeStatement_identity`. `lean/statements.txt` only gains lines.

## Plan rows (QT-A3, task order)

| Row | Delivered | Where, checked by |
|---|---|---|
| `Wire.lean`: `CardEnv` with the W6a projection `projectW6` decoded by `VE.Time.Wire.decodeEnvironment` | yes, spec 4.3's text. `CardEnv.w6` is W6a's decoding of the projection, with its two W6a identities. `environmentId` is over the original environment, with `cardinality@0` in its profiles. `decodeEnvironment_sound` states all three | `lean/VE/Cardinality/Wire.lean`, `WireTheorems.lean`; FA11 guards (golden identities, the `documents@1` list, draft 1's E4 refused by W6a) |
| `CAdmission` | yes (spec 4.3). `CAdmission.sound`: the formula satisfies the independent `Admitted` | same |
| `CardCertificate` | **qt-a3b**, with `checkCertificate`, its only reader: an unused trusted structure could not be exercised (R16) | |
| The decoder proves the decoded `CEnv` `WellFormed` | yes. E5–E8 run as checks with their texts, then a final guard whose proof fills `wf` (`wellFormed_of`) | E5–E8 guards; `trust_mutants`: every mutant of that guard fails to elaborate |
| Limits in 2.4's order | partly: envelope and size (S1, S2) first, then one depth-first, left-to-right pass with S3–S10 at each node; E6 64 finite sorts; S7 64 terms; W6a's 40-digit and 10,000-node limits. **P1–P3** (8 counted sorts, 6 predicates per sort, the erased aggregate) are problem limits, so they go to qt-a3b with the runner (`problemLimits` itself is QT-A1's) | FA13 guards; each text of 4.2 once |
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

Three texts that spec 4.2 does not name (spec wording, C; FOLLOW-UPS):
- "Invalid cardinality formula": a known operator in the wrong shape (S3).
- "TypeMismatch: Ratio needs quantity terms": an operand of an object sort (S9).
- "InvalidInput: cardinality environment is not well formed": the proof-carrying guard after E7 and E8, which those
  checks make unreachable.

### Trust classes

The classes follow W6a's wire (`tools/trust-classes.json`).
- **Trusted:** the decoders that build the environment and the admission record are D[V]. `CardEnv` and
  `CAdmission` are tied by `CAdmission.sound`.
- **C, as `VE.Time.Wire.elabFormula` is:** the elaborators (`elabFormula`, `elabBody`, `elabOperand`, `elabRatio`
  and the name tables). Their output passes the proved `admits`, and its identity is over its canonical encoding,
  which reads back as the request's formula (a guard).
- **Reject-only:** `countedSort`, `admittedRule` and `checkDeclarations`. A missed refusal there is still refused by
  `admits` or by the `WellFormed` proof.
- **D[I]:** the identity encoders.

## Seeded bugs

[`mutants.json`](mutants.json): 18 of 18 killed, all in Lean (`lean/VE/Cardinality/Wire.lean`). No Python or Rust
product code changed. `uv run python tools/mutants.py docs/quantities/qt-a3/mutants.json --no-baseline`, evidence
[`evidence/mutants-run.json`](evidence/mutants-run.json). Each mutant is applied alone and
`lake build VE.Cardinality.WireExamples` fails at a `#guard`, never at a proof. `WireExamples.lean` does not import
`WireTheorems.lean`, whose step-by-step proofs also break under most of these mutants. Line numbers are in
`WireExamples.lean`.

| Mutant | Definition | First failing guards |
|---|---|---|
| `plan-count-not-finite` (the plan's) | `countedSort` | :127 FA8 count over `user`; :230 FA13 |
| `projectW6-profiles` | `projectW6` | every decoding guard (W6a refuses the projection) |
| `profileLists-docs` | `profileLists` | :79 the `documents@1` list |
| `finiteSorts-limit` | `finiteSorts` | :216 64 names pass E6 |
| `finiteSorts-fields` | `finiteSorts` | :210 an extra member |
| `environmentId-original` | `decodeEnvironment` | :73 golden identities; :98 golden meaning id |
| `environment-schema` | `decodeEnvironment` | :203 E3 |
| `environment-declarations` | `decodeEnvironment` | :150 E8; :216 E7 |
| `checkDeclarations-sorts` | `checkDeclarations` | :150, :152 a reserved sort and predicate |
| `statement-size` | `decodeStatement` | :244 S2 before S3 |
| `statement-format` | `decodeStatement` | :185 S1 |
| `meaningId-profiles` | `decodeStatement` | :98 golden meaning id |
| `countedSort-atoms` | `countedSort` | :128, :130 S6 texts |
| `ratio-day` | `elabRatio` | :159 dates |
| `admittedRule` | `admittedRule` | :162, :163 `down`, `up` |
| `proportion-order` | `elabFormula` | :230 S5 before S8 |
| `relNames-eq` | `relNames` | :95 FA1 decodes to the core's |
| `encPrinted-places` | `encPrinted` | :119 printed numbers read back |

Mechanical mutants (R16, build checklist 13a): `mac-pytest.sh --trustmut -- --max-mutants 1000 --jobs 6 --allow ...`
on the final Lean change (`84484c6d3`, ve-mac-1) found 5 trusted definitions and 87 mutants: 58 KILLED, 0 SURVIVOR,
0 UNKNOWN, 29 ALLOWED, exit 0 ([`trust-mutants.json`](trust-mutants.json)).

The first run had 4 survivors and 26 unknowns. One survivor was `projectW6` with `profiles.drop 1`, which survived
because every test environment lists `cardinality@0` first; the guard "removes `cardinality@0` wherever it is listed"
now kills it. The allowed mutants, each with its reason in [`trust-mutants-allow.json`](trust-mutants-allow.json):
- Mutants of the two dependent `if h :` conditions, whose proofs take `h` at its exact type, so they do not elaborate.
- `finiteSorts`'s `[]`, whose element type cannot be inferred.
- S2's fuel 256, 257 or 258: equivalent under the JSON reader's 256-depth cap. W6a uses 257.
- `projectW6` keeping `profiles` in its base: equivalent, since the re-added member replaces it.

## Trust, size and evidence

- Trust (`tools/trust_map.py --check` on the final HEAD, against `110b3bf3a`, after the sync): K +0, S +0, untied
  V +51, all in `Wire.lean` (`decodeEnvironment` 17, `decodeStatement` 13, `finiteSorts` 10, `projectW6` 8,
  `profileLists` 3). The allowance is signed by R16. FOLLOW-UPS "## qt-a3" asks for the ties pass.
- Size: about 790 hand-written lines over the merge base before this report and DELTA, and about 880 with them.
  Lean is 617 (`Wire.lean` 290, `WireExamples.lean` 249, `WireTheorems.lean` 78), side tables 102
  (`trust-classes.json` 81, the manifest 20, `VE.lean` 1), evidence 69 (`mutants.json` 42, the allow file 20, the
  allowance 7), and ROADMAP 1.

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
5. PASS (inputs): undeclared sorts (`UnknownSort(users)`), predicates of another sort or arity, an unknown constant,
   duplicates, and reserved names are refused (guards :127–:152, :216–:221). No relayed answer to bind yet.
6. PASS: synced with main (`110b3bf3a`) and regenerated; the chain runs the gate on the final HEAD.
7. PASS: DELTA row 1 cites R16 with per-file counts; FOLLOW-UPS "## qt-a3" has the ties-pass row.
8. PASS: DELTA states that no answer moves: `checkers.lock` and `route-cases.json` are the base's.
9. PASS: the selected plan included `test_cardinality_exercised.py`, which caught the missing theorems.
10. PASS: `checkCertificate_sound`'s text equals the plan's and the spec's (for qt-a3b); the new theorems'
    statements are about the returned values (`decodeEnvironment_sound`, `decodeStatement_identity`); the first
    mutants run, when they still shared `Wire.lean`, showed the decoders' mutants breaking their proofs.
11. PASS: limits at and past their values (64 and 65 finite sorts, 64 and 65 terms, depth 64 and 65, 10,002 nodes);
    no budget or deadline code; no timing in tests.
12. N.A.: no runtime path changes; the decoder is one pass, bounded by S2's 10,000 nodes before it starts.
13. PASS: no test removed or renamed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
