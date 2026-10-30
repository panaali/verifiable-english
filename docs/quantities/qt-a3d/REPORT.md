# qt-a3d REPORT: the cardinality document case (quantities QT-A3, fourth part)

Status: partial by the size rule; review round 1 (`qt-a3d-review.final.md`, F1 to F4, all B) fixed, see "Review round 1". (3), the paraphrase, is still cut to **qt-a3db**.
Changed in round 1: the document row's `report_id` (F1); leaves as node positions and entries by name (F2); guards for the premise count and the root's name (F3); the cardinality encoders and graph types are [V], V +72 in all, R16 (F4).
Open: the paraphrase (local branch `wip/qt-a3db-render`, `f44a84d54`); `check_response` types `report_id` but does not recompute it, which is QT-A4's relay; over the ~600-line rule (below).
Deviation: `admitDocument` is in `Run.lean` and the theorem in `RunTheorems.lean`, not `Document.lean` (below). Pre-existing red: `test_fsf_r2_probes_rerun_equals_saved_probes` (below).
DRI signature needed: none (both DELTA rows cite R16). Next: qt-a3db, then QT-A4.

## Review round 1 (`manage-agents/qt-a3d-review.final.md`)

| Finding | Fix | Regression test | Probe before, after |
|---|---|---|---|
| F1 (B) no report identity | `Run.reportId`: the `ve-report` digest, in the cardinality environment's identity version, of `environment_id`, `w6_environment_id`, `w6_target_environment_id`, the document as sent and the report; the row carries it and `cardinality.json` requires it (hex64). The class is the report's binding: `report_id` changes with every tampering the review lists (leaves emptied, dropped, duplicated, reordered; meaning ids or formulas swapped; a leaf as the root) and with the document. Recomputing it is a relay's binding check, which the cardinality mode does not have until QT-A4 (as `ve/admission.py`'s `bound_admission` does for `quantity`); a new dialect keyword would add to `PENDING_D1` (`tests/test_architecture_docs.py`), the DRI's | `RunExamples.lean` `docReportId` guards; `tests/test_cardinality_service.py::test_document_report_id_binds_both_identities_the_document_and_the_report`; `::test_document_rows_are_typed_and_bound` (dropped and retyped `report_id`) | fails (`AssertionError`), passes |
| F2 (B) leaf sets re-read per premise | An entry's leaves are a `Nat` bit set over node positions, joined by a bitwise or (`Nat.lor`, at most 1,000 bits per premise); entries are a `Std.HashMap` by name, so a lookup hashes the premise's name once instead of comparing it with every earlier name; `checkGraph_sound` re-proved over positions. The S2 recount of `decodeNode` (`Document.lean:119`) is left: one linear pass per statement, as `sourceFits`'s own two | `RunExamples.lean`: "mid" reused 200 times, and two middle nodes over the same leaves, give FA1's leaves once; `tools/bench/test_perf.py::test_cardinality_document_leaves_joined_once` (CPU, not in the suite) | none (timing). The review's shape, 996 leaves with 5,000-byte names: 1.84 s and 10.27 s (one, then 2,633 reuses per deduction) before; 3.68 s and 4.62 s after. Both now include the `report_id` digest of the 10 MB document, about 2.4 s (the same case refused before the digest: 1.28 s) |
| F3 (B) premise-count check untested | Guards: 50,001 dangling premises are `deductionLimit`, 50,000 `graphRejected`; the report's root keeps a name other than `root`. Sweep: `Graph.leaves`'s `deduction.isNone` could never change an answer (only a leaf's position is set), so it is gone | `RunExamples.lean:432` and `:382`; `mutants.json` `premise-count`, `root-name` | the build passes with the check deleted, then fails at `RunExamples.lean:432` |
| F4 (B) `reportJson`, `claimJson` D[I] | D[V], with `statementJson`; sweep: `encode`, `encBody`, `encOperand`, `encPrinted` (`Wire.lean`, D[I], as `Time.Wire`'s encoders are D[V]) and `CNode`, `Entry`, `Graph` (G[I] to G[V]). V +72 over the merge base, recorded with `--allow` under R16 (DELTA row 2). The reclassified encoders had never been mutated (D[I] is untrusted); four hand mutants survived every guard, so `WireExamples.lean:181` now checks that each pinned formula encodes to its source | `tests/test_trust_budget.py::test_formula_and_report_encoders_are_verdict_bearing`; `mutants.json` `encode-and-order`, `encode-proportion-parts`, `encBody-or`, `encOperand-count-body`, `encPrinted-places`, `statementJson-formula` | fails (`AssertionError`), passes |

The follow-ups F5 to F10 (C) are in manage-agents `FOLLOW-UPS.md` under "## qt-a3d round 1".

## Statement gate

The quantities statement review accepted QT-A3 (`docs/quantities/qt-a3/REPORT.md`, "Statement gate": QT-0, ten
corrections, verified in `quantities-p3ver1.final.md`). `admit_cardinality_report_sound`, `CardReport` and
`CardReport.Sound` equal spec 4.3's text after whitespace normalisation: a script over `docs/spec/quantities.md` and
the Lean sources printed `True` for all three. The plan's shorter form (`(d : Json)`, `res.Sound`) is superseded by
spec 4.3's (QT-0's correction C10), as qt-a3's report says. `Wire.lean` is unchanged, so qt-a3's `CardEnv`, `CAdmission` and `projectW6`
keep their text; `checkCertificate_sound` and the certificate code of `Run.lean` are unchanged, and
`tools/check_*_statements.py` exit 0.

Synthesis round 2 (`edits-quantities.md`): none of its seven edits concerns this item; none is implemented here.

## Plan rows

| Row | Delivered | Where, checked by |
|---|---|---|
| (1) `CardReport`, `CardReport.Sound` | yes, spec 4.3's text | `lean/VE/Cardinality/Document.lean` |
| (1) `admitDocument`, the claim graph following `VE.Time.Document` | yes, but **not** in `Document.lean`: see "Deviations". The graph is `Document.admitGraph` | `Run.lean`, `Document.lean`; guards below |
| (1) `admit_cardinality_report_sound` | yes, proved, in `RunTheorems.lean`; `python3 lean/audit.py`: PASS, standard axioms only | `RunTheorems.lean` |
| (2) `document` case, its row in `cardinality.json`, `runCaseReported_fits` kept | yes | `Run.lean`, `ResponseShape/Schemas/Cardinality.lean`, `ResponseShape/Encoders/Cardinality.lean` |
| (3) `Render.lean`, the `paraphrase` case and the table rows as guards | **no: qt-a3db** (size rule). Built and passing its guards before the cut, on `wip/qt-a3db-render` | |
| (4) Route cases and hostile set | document half: `document-fa1`, `document-leaf-dropped`, `document-unproved`, `document-no-profile`; boundaries as guards. Paraphrase half: qt-a3db | `tests/test_cardinality_service.py`, `RunExamples.lean` |
| (4) Seeded bugs: a leaf dropped, a root with an unproved leaf | yes (below) | `mutants.json` |
| (4) Seeded bugs: "at least one" left out, `ties_up` as `half_even` | **no: qt-a3db**, with the code they mutate | |
| One mutant per new trusted definition | yes | `mutants.json`, `trust-mutants.json` |
| Evaluate once, size charged (DRI rule of 2026-10-27) | yes: see below; not moved | |
| Not edited: `Protocol.lean`, `Registry.lean`, `ve/document/`, Python relays | none edited: `git diff $(git merge-base HEAD main) --stat` over `lean/VE/Service`, `ve/document` and `ve/backends/relay.py` is empty | |

### Evaluate once, and what is charged

- Each node's statement is decoded once, by `decodeNode`; its size is S2's count of that source.
- Each deduction's problem is built once: `checkDeduction` runs `checkedProblem`, `idsOf` and `checkErased`, and
  answers as `checkCertificate` (`checkErased_eq`, used by `checkDeduction_sound`). It does not call
  `checkCertificate`, which rebuilds the problem.
- An entry's leaves are a set of node positions (a `Nat` bit set; review F2: it was a set of names, re-read at each
  premise), so a reused premise does not double them, as `VE.Time.Document`'s lists would, and joining a premise's
  leaves reads at most 1,000 bits, whatever the names' lengths. Entries are found by name in a hash map. The report
  reads the set once, over the submitted nodes.
- Charged: at most 1,000 nodes, before any is decoded; the statements the deductions read, at most 50,000 nodes over
  the whole graph. A deduction's premise count is charged before its premises are looked up, its sizes before its
  problem is built. The sum is a `foldl`: `List.sum` overflowed the interpreter's stack at 25,000 premises, found by the guard.

### What the claim graph does not have

`VE.Time.Document` also has units, labels with provenance rules, lemmas and citations, reading sets and open terms.
This graph has nodes, premises, certificates and a root only: `CardReport` has no place for the rest, and QT-A4 owns
the document hook. **Whether QT-A4 needs the provenance rules here is for its builder to settle.** The report is sound
over its leaves; nothing here says where a leaf came from.

## Deviations

1. **Module of `admitDocument` and the theorem.** The task places them in `Document.lean`. `Protocol.lean` imports
   `Run.lean`, which must call the graph, and `checkCertificate` and `CardCertificate` are in `Run.lean`, so
   `Document.lean` cannot import them. Moving the certificate code below it counts about 300 lines. So the graph is
   generic over the certificate check (`Checks`); `Run.lean` supplies it and defines `admitDocument`, and
   `RunTheorems.lean`, the first module with `checkErased_eq`, has the theorem. The statements' text is unchanged.
2. **Size.** Measured with `git diff --numstat $(git merge-base HEAD main)` on the hand-written files, added lines: 499
   of Lean and tests (`Document.lean` 286), 125 in `tools/trust-classes.json` and `ve/assurance-manifest.json`, 1 in
   `docs/CONSOLIDATION-PLAN.md`, 317 of this item's docs and mutant lists: about 940 in all against the rule's ~600.
   I measured only after writing all four deliverables, not before the second half as the rule says (about 730 of
   code then, which is why the paraphrase was cut). Cutting further would have left the graph without its fixtures.

## Seeded bugs (`mutants.json`, 24 of 24 killed; `uv run python tools/mutants.py docs/quantities/qt-a3d/mutants.json --no-baseline`, `evidence/mutants-run.json`)

Lean is the only language with product changes (Python and Rust: none; the Python changes are tests and a benchmark).
Each line of "killed by" is the first error in the run on the final Lean tree (commit `230618076`, before the docs).
Two round-1 mutants were moved to the new code (`leaf-dropped-union`, `duplicate-name`); the last 13 are round 1's.

| Mutant | File | Killed by |
|---|---|---|
| `leaf-dropped-report` | `Run.lean` | `RunExamples.lean:379` FA1's leaves |
| `leaf-dropped-union` | `Document.lean` | proof `checkGraph_sound` (`Document.lean:237`) |
| `unproved-root-runner` | `Run.lean` | `RunExamples.lean:404` FA1b's certificate refused |
| `unproved-root-graph` | `Document.lean` | proof `checkGraph_sound` (`Document.lean:102`, `Checks`) |
| `duplicate-name` | `Document.lean` | `RunExamples.lean:407` |
| `deduction-premises` | `Document.lean` | proof `decodeNode_statement` (`Document.lean:255`) |
| `profile` | `Document.lean` | `RunExamples.lean:411` |
| `node-limit` | `Document.lean` | `RunExamples.lean:418` 1,000 nodes admitted |
| `charge-boundary` | `Document.lean` | `RunExamples.lean:426` 50,000 read |
| `charge-cumulative` | `Document.lean` | `RunExamples.lean:427` 50,001 refused |
| `card-report` | `Document.lean` | `Graph.report` does not elaborate |
| `report-id-document` (F1) | `Run.lean` | `RunExamples.lean:359` the whole answer's `report_id` |
| `report-id-identities` (F1) | `Run.lean` | `RunExamples.lean:359` |
| `report-id-report` (F1) | `Run.lean` | `RunExamples.lean:380`, each tampered report's identity |
| `leaf-position` (F2) | `Document.lean` | proof `checkGraph_sound` (`Document.lean:218`) |
| `leaf-position-advanced` (F2) | `Document.lean` | proof `checkGraph_sound` (`Document.lean:216`) |
| `premise-count` (F3) | `Document.lean` | `RunExamples.lean:432` 50,001 dangling premises |
| `root-name` (F3) | `Run.lean` | `RunExamples.lean:382` the root named `total` |
| `encode-and-order` (F4) | `Wire.lean` | `WireExamples.lean:181` each pin encodes to its source |
| `encode-proportion-parts` (F4) | `Wire.lean` | `WireExamples.lean:181` |
| `encBody-or` (F4) | `Wire.lean` | `WireExamples.lean:181` |
| `encOperand-count-body` (F4) | `Wire.lean` | `WireExamples.lean:181` |
| `encPrinted-places` (F4) | `Wire.lean` | `WireExamples.lean:119` the printed numbers read back |
| `statementJson-formula` (F4) | `Run.lean` | `RunExamples.lean:44` |

Five kills are proofs and `card-report` is a build failure, so those six show that a theorem or the type depends
on the line, not a behavioural test. The four `encode` mutants survived every guard before round 1's read-back guard.
The F4 class has a data mutant too, run by hand: `reportJson` put back in D[I] fails
`tests/test_trust_budget.py::test_formula_and_report_encoders_are_verdict_bearing`.

Per trusted definition: `CardReport` is `card-report`; `CardReport.Sound` and `runCase` are `trust-mutants.json`.

## Trust

`uv run python tools/trust_map.py --check` on the final HEAD against the merge base `1f28dddfb`: PASS. K +0, S +7,
untied V +72, within R16's 150 lines; per file in DELTA row 2 (`Document.lean` S +7, V +24; `Run.lean` V +18;
`Wire.lean` V +30). Round 0 recorded V +4; round 1's V +68 is review F4's reclassification (`statementJson`,
`claimJson`, `reportJson`, `encode`, `encBody`, `encOperand`, `encPrinted` to D[V]; `CNode`, `Entry`, `Graph` to G[V])
and `report_id`'s lines, recorded with `--allow`, SIGNED by standing ruling R16; the ties-pass row is in manage-agents
`FOLLOW-UPS.md` under "## qt-a3d round 1".

`mac-pytest.sh --trustmut` (a full run on the final Lean tree, `230618076`): TRUSTMUT_RESULT. Round 1's first full run
(`35a71d7f5`) had 0 survivors and 2 UNKNOWN: `[]` for `g.leaves` in `reportJson` does not elaborate (the element type
is lost), allowed with that reason (`trust-mutants-allow.json`); the whole member list's `[]` is killed. The other
allowed ones do not elaborate either: `True` or `False` for `CardReport.Sound`'s body drops its universe, so the
approved statement's `.{v}` fails, and `[]` for `runCase`'s decoded premises has no element type. So `CardReport.Sound`
has no evaluated check: it is a proposition, and only the proofs read it. `trust_mutants` selects changed lines, so the
reclassified encoders, whose lines did not change, are `mutants.json`'s hand mutants (above).

## Tests

- `zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, second run: exit 0, 6 shards on
  GitHub Actions, 400 units, 400 passed (`SHARD n/6` lines). Only `DELTA.md` and this report changed after it.
- The first run, on the VM, stopped early with 3 failing units and 338 not run. Two were this item's and are fixed:
  `tests/test_assurance_manifest.py` (`Document.lean` unpinned, `Run.lean`'s pin stale) and
  `tests/test_consolidation_tools.py::test_committed_ledger_names_real_declarations` (step 7, 711 to 715).
- **Pre-existing, not fixed:** `tests/test_safety_framework.py::test_fsf_r2_probes_rerun_equals_saved_probes` failed on the VM
  and is **skipped, not passed**, in the Actions run, which has no pinned source. Rerunning `measure_r2.py` differs from the
  saved `probes.json` in one line, the diagnostic of `DF-a`, whose text came from main (df-3, `97e36e510`); this item does not touch it. I did
  not run it on a main checkout, and it is not in `main-known-red.txt`.
- The full gate is the chain's; it has not run.
- `uv run python tools/gate_collection.py --check --prebuilt`: 1 added, 0 removed, 0 refused, 0 stale, 0 malformed.

## Pilot bytes

0 (estimate; nothing is claimed before a pilot audit): the case reaches documents only through QT-A4, and the reader's line
for P6 and the constitution's 31 units is qt-a3db's.

## Not delivered (next items)

- **qt-a3db**: `Render.lean`, the `paraphrase` case and shape, its guards and route cases, the seeded bugs "at least one"
  left out and `ties_up` as `half_even`. Its builder should review three choices on the branch: a sort's plural adds "s", W6a
  parts are shown as canonical JSON, and a line starting with a connective starts with "(the".
- **QT-A4**: the relay, which binds the report to the request by recomputing `report_id` (as `ve/admission.py`'s
  `bound_admission`), so a duplicated, dropped or reordered leaf row is refused; `cardinality.json` alone types
  `report_id` (hex64) and binds the root's and leaves' names, and the shape language has `uniqueStrings` only.

## Spec re-read

- `admit_cardinality_report_sound`, `CardReport`, `CardReport.Sound` against `docs/spec/quantities.md:863-881`: equal.
- The `document` case against `docs/spec/quantities.md:768` ("`document` (claim graph)") and `docs/spec/quantities-PLAN.md:724`.
- The report's identities against spec 4.1 ("reports carry both, under separate names, and bind both"): the row
  carries all three (round 0 stopped there, and called it binding: review F1); `report_id` binds them, the document
  and the report, as `VE.Time.Document.runDocument`'s does, and `docReportId` spells it out.
- The row's bindings against `VE.Time.Document`'s shape (`lean/ResponseShape/Schemas/Quantity.lean:219`): root name and leaf names.

## Self-review against BUILDER-CHECKLIST

1. PASS: `tests/test_cardinality_service.py::test_document_rows_are_typed_and_bound` deletes and retypes each member with 7, true, null, [], {}, 1.5, a lone surrogate and a nested list. Not the 10k-deep list or the bad stdout byte.
2. PASS: "Plan rows" above; the cut is named. The module deviation is listed, not ruled on.
3. PASS: `mutants.json` 24/24 on the final Lean tree; `trust-mutants.json` exit 0, evidence and allow file committed. Round 1: four hand mutants of the reclassified encoders survived until the read-back guard.
4. PASS: `tests/test_cardinality_service.py::test_route_cases_answer_as_recorded`, the 19 earlier cases unchanged. No Python or Rust product change.
5. PASS, one gap: `test_document_rows_are_typed_and_bound` refuses an unknown leaf name, a rebound root and a dropped or retyped `report_id`; a duplicated leaf row is **not** refused by the schema; `report_id` names it (`test_document_report_id_binds_both_identities_the_document_and_the_report`), and QT-A4's relay recomputes it. An empty leaf list is genuine for a deduction from no premises.
6. PASS: synced with main at `0ff460a1d`; the chain runs the gate on the final HEAD.
7. PASS: `DELTA.md` rows cite R16; no signature reserved.
8. PASS: `DELTA.md` rows 1 and 2; the only change of answer is the kind `document`, `test_route_cases_answer_as_recorded`.
9. PASS: `tools/select_tests.py` chose 400 units, not all, including `tests/test_cardinality_service.py`, and it caught this item's two real failures in its first run.
10. PASS: `mutants.json` `unproved-root-graph`, `leaf-dropped-union`; `tools/check_*_statements.py` exit 0.
11. PASS: `RunExamples.lean` 1,000/1,001 nodes, 50,000/50,001 statement nodes, charged before reading. There is no zero budget here to test.
12. N.A. for pilots (no document reaches the case until QT-A4). Round 1 timed the review's hostile shape (above) and added `tools/bench/test_perf.py::test_cardinality_document_leaves_joined_once` (CPU, 1 and 2,633 reuses: 2.66 s and 3.77 s in its baseline); the guards show a premise reused 200 times and two middle nodes give the leaves once.
13. PASS: `tools/gate_collection.py --check --prebuilt`: 0 removed, 0 refused.
14. PASS: each check has both sides in `RunExamples.lean`; "Spec re-read" above; each claim here names its command.
