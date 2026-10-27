# qt-a3b report: the cardinality certificate check and case runner (quantities QT-A3, second part)

No DRI signature is reserved: DELTA row 1 (trust, V +44) cites R16. Delivered: `CardCertificate`, `checkCertificate`
and `checkCertificate_sound` (the plan's text), P1–P3, the `admission` and `certificate` cases with the region table
and the regenerated problem with its W6a identities, claimed tables and problems refused, W6a's shared helpers owned by
W6a, and the fixtures, with the plan's seeded bug. Next: **qt-a3c** (the `cardinality` mode, its shape and the
`cardinality@0` row), then **qt-a3d** (the document and the paraphrase) and QT-A4.

## Statement gate

The statements were reviewed in QT-0 (manage-agents `quantities-p3ver1.final.md`). `checkCertificate_sound` and
`CardCertificate` equal the plan's (`docs/spec/quantities-PLAN.md`, QT-A3) and spec 4.3's text after whitespace
normalisation (checked by a script over the three files). qt-a3's decoders and their theorems are unchanged
(`Wire.lean` gains only a docstring line). `lean/statements.txt` only gains lines. The new helper theorems name no plan
statement: `decodeCertificate_sound`, `runCaseReported_ok`, `runCaseReported_error` (`RunTheorems.lean`).

## Plan rows (the task's order)

| Row | Delivered | Where, checked by |
|---|---|---|
| (1) `CardCertificate`, `checkCertificate`, `checkCertificate_sound` in `lean/VE/Cardinality/Run.lean` | yes, restored from `b0b8f730a`/`fa3c92578` and built on the merged decoders (fix round 1's `sourceFits` untouched). `checkCertificate` runs P1–P3, binds the cardinality identities, then W6a's annotated and core bindings to the regenerated problem in the projection's environment, the 10,000-step limit, then the frozen order replay of the erased problem; the theorem goes through `cardinality_elab_sound`. `decodeCertificate` reads `ve-cardinality-certificate@1` with W6a's `decodeW6Certificate` inside | `Run.lean`; `RunExamples.lean` FA1/FA1b, binding and step-limit sections |
| (2) P1–P3 | yes: `problemChecks` = QT-A1's `problemLimits` (P1, P2) then W6a's `quantityLimits.aggregate` on the erased problem (P3), after every statement and before any claim or certificate | P section: 8/9 counted sorts, 6/7 predicates (one statement, and spread over two), P1 before P2, 10,000/10,001 erased nodes, P3 in a certificate case and inside `checkCertificate`, a statement's fault before P2 |
| (2) the runner | yes: `runCase`/`runCaseReported` (`VE.Cardinality.Run`), kinds `admission` (default) and `certificate`; another kind refused. The answer carries the cardinality `environment_id`, `w6_environment_id`, `w6_target_environment_id`, each statement's meaning id and canonical formula; admission adds `regions` and `erased` (each erased formula with `Q`, `core`, `meaning_id`, `core_meaning_id`); a certificate case adds `valid`, and its refusal row says `valid: false` | FA1 section (golden identities, region table, 10 erased premises), kind guards |
| (2) claimed tables and problems refused | yes: `claimed` compares canonical texts; a claim the canonical writer refuses is refused; the regenerated ones are accepted; claims are checked before the certificate is read | forged-claims section |
| (3) W6a's shared helpers | yes, defined once in `lean/VE/Time/Wire.lean` and used by `decodeQuantity`/`quantityLimits`/`checkW6Certificate` and by `Run.lean`: `statementIds`, `quantityLimits.aggregate`, `staleW6`, `staleCore`. W6a's answers unchanged: its 37 recorded `quantity` cases, base build against head, byte-identical (DELTA) | DELTA; spec-text guard of the two texts |
| (4) fixtures | FA1's certificate through the runner (`valid: true`, the whole row pinned), FA1b (`valid: false`, 8 erased premises), FA11's binding mismatches (each of the 3 identities of each of the 3 bindings, and FA1's certificate for FA1b), the forged region table, the erased problem with a premise dropped, malformed certificates (format, extra member, a bare W6a certificate, W6a's own format text inside) | `RunExamples.lean` |
| (4) the plan's seeded bug | yes: `plan-count-not-finite` (a count over a sort not in `finite_sorts`) | mutants below |
| (4) one mutant per new trusted definition | yes, plus mechanical mutants | below |

Not in this item, by the task: `Protocol.lean`, `service_schema.py`, `Dispatch.lean`, `Registry.lean`,
`ResponseShape` (qt-a3c). The `countermodel` case is qt-a3c's (REPORT of qt-a3).

## Seeded bugs

[`mutants.json`](mutants.json): 25 of 25 killed (`uv run python tools/mutants.py docs/quantities/qt-a3b/mutants.json
--no-baseline`, [evidence/mutants-run.json](evidence/mutants-run.json)). Every kill is a `#guard` that "did not
evaluate to `true`", never a type or proof error: `RunExamples.lean` does not import `RunTheorems.lean`, and for a
mutant of `Run.lean` the command first replaces `checkCertificate_sound`'s proof by `sorry` (the binding mutants break
that proof too). All are Lean; no Python or Rust product code changed (`tools/layer_policy.py`, a tool, gains two
module names).

| Mutant | File, definition | Failing guards (section of `RunExamples.lean`) |
|---|---|---|
| `plan-count-not-finite` (the plan's) | `Cardinality/Wire.lean`, `countedSort` | `WireExamples.lean` :191, :326 (imported, so it fails first; the runner's guard is the last of `RunExamples.lean`) |
| `problemChecks-limits` | `Run.lean`, `problemChecks` | P1, P2 |
| `problemChecks-aggregate` | `problemChecks` | P3 |
| `erasedIds-conclusion` | `erasedIds` | golden erased identities |
| `decodeCertificate-format`, `-fields` | `decodeCertificate` | malformed certificates |
| `checkCertificate-environment`, `-premises`, `-w6-premises`, `-core-conclusion` | `checkCertificate` | the three bindings |
| `checkCertificate-steps` | `checkCertificate` | step limit (10,000 allowed, 10,001 refused) |
| `stale-text` | `stale` | spec texts |
| `statementJson-formula` | `statementJson` | FA1 echo |
| `regionsJson-order` | `regionsJson` | FA1 predicates, forged claims |
| `erasedJson-ids` | `erasedJson` | FA1 certificate, bindings |
| `claimed-same`, `claimed-uncanonical` | `claimed` | forged claims |
| `runCase-kind`, `runCase-default`, `runCase-claims` | `runCase` | kinds, forged claims |
| `runCaseReported-valid` | `runCaseReported` | malformed certificates (`valid: false`) |
| `statementIds-target` | `Time/Wire.lean`, `statementIds` | golden erased identities |
| `aggregate-bound` | `quantityLimits.aggregate` | P3 at 10,000 nodes |
| `staleW6-text`, `staleCore-text` | `staleW6`, `staleCore` | spec texts |

Mechanical mutants (R16): `mac-pytest.sh --trustmut -- --max-mutants 1000 --jobs 6` on `6cd95cd5d` (ve-mac-1):
3 trusted definitions, 62 mutants: 60 KILLED, 0 SURVIVOR, 2 UNKNOWN. The two (`ps` → `[]` in `runCase`, where the
element type comes only from `ps`, so the declaration does not elaborate) are allowed in
[trust-mutants-allow.json](trust-mutants-allow.json); the run with the allow file (a full rerun, on the VM: no Mac
slot) is [trust-mutants.json](trust-mutants.json): 60 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 2 ALLOWED, exit 0.

## Trust, size and evidence

- Trust (`tools/trust_map.py --check`, final tree, against `a274d9488`): K +0, S +0, untied V +44 (DELTA row 1, R16;
  FOLLOW-UPS "## qt-a3b"). Consolidation ledger rows 7 (+29, the runner) and 8b (−2) of `docs/CONSOLIDATION-PLAN.md`
  re-measured from `trust_map.py --ledger`, as `test_committed_ledger_names_real_declarations` asks.
- Size: about 690 hand-written lines before this report and DELTA, about 790 with them. Lean 528 (`Run.lean` 172,
  `RunExamples.lean` 285, `RunTheorems.lean` 36, `Time/Wire.lean` +21/−9, `Wire.lean` 2, `VE.lean` 3), side tables and
  pins about 120 (`trust-classes.json` 75 — the fixture file's 37 T names —, the manifest about 30, the allowance 7,
  `layer_policy.py` 10, the ledger 4), `mutants.json` 31. Over the ~600 guide: nothing coherent could be cut, since each
  of (1)–(4) needs the others to be exercised (the check needs W6a's helpers, the runner needs the check, and every
  check needs fixtures on both sides), and the task's own size cut already moved the mode and documents out.
  `evidence/mutants-run.json` (379 lines) is the harness's output.
- Tests:
  - Selected plan (`mac-pytest.sh --select`, ran locally on the VM: no Mac slot), 375 units on `e1c41540e`: 374 pass;
    `test_consolidation_tools.py::test_committed_ledger_names_real_declarations` failed on the two ledger rows this item
    moves, fixed in `b56f374b7` (288 of 288 pass).
  - After the later commits: `test_cardinality_exercised`, `test_assurance_manifest`, `test_trust_budget`,
    `tools/test_layer_policy.py`, `test_lean_audit_record`, `test_frozen_sources`, `test_lean_limits`: 223 pass.
  - `regen_generated.py --check` (33 entries), `gate_collection.py --check --prebuilt` (0 added, 0 removed, 0 refused,
    0 stale, 0 malformed), `repo_map.py --check` (38 modes), `check_lean_imports.py`, `lean/audit.py` (640 files),
    `trust_map.py --check`, full `lake build`.
  - The step-limit fixture first used a 10,000-child trace node; Lean on aarch64 crashed on it (exit 134, stack), so it
    is now 1 + extra + 99 × 101 steps, two levels deep (`6cd95cd5d`).
  - Not run: the full gate (the chain runs it), `relay_mutation_gate.py` (no relayed answer). No test of
    `main-known-red.txt` touched.
- Pilot bytes: 0 expected (plan: "Bytes: 0"); nothing claimed. The check and runner are what qt-a3c serves and QT-A4
  brings to documents (Asimov extended's P6 and 31 constitution units, 5,387 B, research share).
- Overlap: no in-flight branch edits `lean/VE/Cardinality/` or `lean/VE/Time/Wire.lean`. Union files also edited
  elsewhere: `lean/VE.lean` and `lean/VE/Audit.lean` (`feature/ap-2b`, `feature/ap-3b`, `foundation/me-1`; Audit also
  `feature/jt-2`, `infra/arch-AR-1`), `tools/trust-classes.json` (those and `feature/me-2c`, `feature/q1-4`),
  `ve/assurance-manifest.json` (`feature/jt-2`, `feature/me-2c`, `feature/q1-4`, `foundation/me-1`).

## Not delivered (next items)

- **qt-a3c**: the `cardinality` mode (registry, dispatch, `runMode_cardinality`, `DEADLINES`), `cardinality.json`
  with `runCaseReported_fits`, the `cardinality@0` table row, route cases, the `countermodel` case.
- **qt-a3d**: `Document.lean` (`admitDocument`, `admit_cardinality_report_sound`) and `Render.lean`.
- Then QT-A4. No qt-a3bb: nothing of this item's scope was cut.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed to Python yet (qt-a3c/QT-A4); the runner's own inputs are refused when malformed
   (certificate `{}`, extra member, wrong formats, deep claims: `RunExamples.lean` malformed-certificate and
   forged-claims guards).
2. PASS: plan-row table above; no Python copy of a Lean decision; W6a stays the one owner of the shared helpers; no
   permanent report test; overlap listed.
3. PASS: `mutants.json` 25/25 killed by `#guard`s (`evidence/mutants-run.json`); `trust-mutants.json` 0 survivors.
4. PASS: base against head on W6a's 37 recorded cases, byte-identical (DELTA); FA1 replays, FA1b does not
   (`RunExamples.lean` FA1/FA1b guards).
5. PASS: every identity the certificate names is bound, each refused when shifted, reordered or taken from the other
   environment (binding section, 9 guards plus FA1's certificate for FA1b's statements).
6. PASS: merge base is main's HEAD `a274d9488`; regenerated; the chain runs the gate on the final HEAD.
7. PASS: DELTA row 1 cites R16 with per-definition counts; FOLLOW-UPS "## qt-a3b".
8. PASS: DELTA states no answer moves, with the base/head digest of W6a's answers.
9. PASS: the selected plan caught the ledger rows (`test_consolidation_tools.py`).
10. PASS: `checkCertificate_sound` equals the plan's text; the binding mutants break its proof as well as the guards;
    `decodeCertificate_sound` and `runCaseReported_error` are about the returned values (`RunTheorems.lean`).
11. PASS: limits at and past their values (8/9 sorts, 6/7 predicates, 10,000/10,001 erased nodes, 10,000/10,001
    steps); no budget or deadline code; no timing in tests.
12. PASS: no runtime path a mode reaches changes (W6a's answers identical); the step fixture avoids a deep recursion
    that crashed Lean on aarch64.
13. PASS: no test removed or renamed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
