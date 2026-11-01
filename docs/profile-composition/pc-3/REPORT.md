# pc-3 REPORT: the composition contract (profile-composition PC-3, first part)

Status: built, ready for review; no DRI signature needed. HEAD: the last commit on `feature/pc-3`.
Changed: the `interface` field on every row of AR-10's table (synthesis round 2 edits 1 and 6), C1 to C3,
`Compose/Stack.lean`, and `Compose/Contract.lean` (G2, scope's typed route evidence, `listed_evidence`), with
fixtures F3.1, F3.1b and F3.4 to F3.7. No answer changes (DELTA has only the R16 trust row).
Open: pc-3b (G1 with G4). G1b and F3.2 to F3.3 belong to PK-1's owner. Size: 870 hand-written lines, over the
~600 line; the Lean is 425, and the rest is the evidence the checklists ask for (see Size).

## Inputs

- Plan and spec copied verbatim from 938e148cb: plan PC-3 (826-904), spec 1.1 to 1.5, 3.3, 5.3.
- This item implements synthesis round 2 **edit 1** (the AR-10 slot `"pack"`, `slotAgrees (.pack _) "pack" = true`)
  and **edit 6** (the wave profiles' values; see `ContractExamples.plannedRows` and the table guard below).
- Statement gate: the plan's change log records the pc-d2 FIX and its confirmation, and the pc-fid-rev and
  pc-fid-rev2 reviews. pc-fid-rev3 changes writer rules only; structure rows do not wait on it (I2).
- Overlap: only `feature/jt-2c` (not on main) edits `Dispatch.lean`, at hunks after `withoutDocumentLayers`,
  `gateOf` and `gate_judgments`. This item edits `ProfileRow`, the rows and their proofs, and adds `slotAgrees`, C1
  and C2 after `profileTable`.

## Plan rows delivered

| Row | Where (commit) | Evidence |
|---|---|---|
| (1) `Interface`, the field, every row's value (1.1), slot `"pack"`, `slotAgrees` as 1.2, the component in `gate_legacy`, `gate_acts`, `gate_scope`, `gate_cardinality` | `Dispatch.lean`, `Cardinality/Gate.lean` (d79c2f86c) | `lake build`; ContractExamples pins each profile's value |
| (2) C1 to C3 by `decide` | Dispatch.lean, Stack.lean | F3.4; seeds 2, 6 |
| (3) `Stack.lean`: `rewriters`, `stackOf`, `listedStacks`; imports only Dispatch | Stack.lean | F3.5, F3.6; seeds 5-7 |
| (4) `Rewriter`, `Rewriter.Laws`, `pipeline`, `pipelineOf`, G2 by induction | Contract.lean | seed 1 |
| (5) `scopeRewriter`, `docRewriters`, `ScopeRunsOf`, `ScopeRuns`, `checkDocSets_pipeline`, `refuseAll_runs` | Contract.lean | F3.1, F3.7; seeds 8-10 |
| (6) `ScopeFaithful`, `ScopePreserves`, `ScopeSetsFaithful` from main's theorems; `RouteFacts` (two entries); `listed_evidence` | Contract.lean | seeds 11-13 |
| (7) F3.1 (also on a governed reading set), F3.1b, F3.4 to F3.7; `VE.lean` imports | ContractExamples.lean (e57002047) | `lake build` |
| Regenerated statements, axioms, declarations, audit manifest, codemap, checker pins | 5e3e98fb1, 73a0da680 | `lean/audit.py`: PASS, 7647 theorems |

Not here: G1 with G4 (`composed_superpose_all`, spec 1.6), which the task assigns to pc-3b. No route theorem is
restated.

## Statements and deviations

`tools/check_pc3_statements.py` (`tests/test_pc3_statements.py`) prints "PC-3: 27 declarations equal the approved
text (RouteFacts staged)": every declaration of 1.2 to 1.5 this item builds, after whitespace normalisation, with
comments dropped on both sides. None of the following changes a statement:
- `RouteFacts` ends `| _ => False` in place of PC-6b's, PC-7b's and PC-4b's entries (the task's instruction; the
  checker's `STAGED`).
- `pipelineOf` is in `Contract.lean`, as task row (4) and spec 1.4 place it.
- Helpers not in the spec: `filterMap_docRewriters`, `pipelineOf_scope`, and `scopeFaithful`, `scopePreserves`,
  `scopeSetsFaithful`, whose conjuncts are main's theorems themselves.
- The planned rows' values are the fixture `plannedRows` (not in `profileTable`); the gate still refuses
  `presupposition@0` (guard).
- F3.1's document is `ScopeExamples.doc`: one governor over the two items `i1` and `i2`, beside a lead-in and a
  closing unit.
- `tools/layer_policy.py` puts `Contract` and `ContractExamples` at the runner layer (4), like
  `VE.Norms.FlaggedSpec`: they state theorems on `checkDocSets` (spec 1.3, 3.4).

Spec re-read (copied spec): `Interface`/`ProfileRow` :227-237, `slotAgrees` :251-258, the values :172-204,
`rewriters`/`stackOf`/C3 :287-299, G2 :316-347, the scope block :356-391, the scope facts, `RouteFacts` and
`listed_evidence` :405-428 and :521-541, F3.1-F3.7 :2661-2673.

Evaluators and runners: N.A. No service mode is added, and `checkDocSets` is unchanged.

## Seeded bugs and mutants

`mutants.json` lists 16 hand seeds, each applied alone and restored. Ids 1-13 are Lean, the only product language
changed. Ids 14-16 are in the two changed Python tool files:
- 14, `tools/check_pc3_statements.py`: the LATER check skipped (`if found:` -> `if False:`). It fails
  `tests/test_pc3_statements.py::test_a_changed_statement_or_a_later_declaration_fails`.
- 15, `tools/check_pc3_statements.py`: theorems compared together with their proofs (the `:=` split dropped). It fails
  `tests/test_pc3_statements.py::test_pc3_statements_equal_the_approved_text` (`refuseAll_runs: theorem differs`).
- 16, `tools/layer_policy.py`: the Contract modules put at layer 2, not 4. `tools/check_lean_imports.py` (the
  layer-ledgers check of `regen_generated.py --check`) then exits 1 on three new outward imports into `VE.Service`.

The plan's seed (`pipeline` skips the last rewriter) breaks G2 and `checkDocSets_pipeline`. A scratch copy
with those proofs replaced by `sorry` shows F3.1's answer and non-identity guards failing while `pipeline_off`'s
example passes. Every other new definition has a seed that fails C1, C3, F3.4b, F3.6, `listed_evidence`,
`pipelineOf_scope`, `checkDocSets_pipeline` or, for weakened propositions, the statement check.

`trust-mutants.json` (checklist 13a) is an allow-only `--rescore` of `trust-mutants-run2.json`, run at db95e866c
(later commits touch no `lean/` file). Result: exit 0, 253 mutants: 122 KILLED, 117 ALLOWED, 14 INVALID, and 0
SURVIVOR, UNKNOWN or NOT RUN.

The 117 allowed (`trust-mutants-allow.json`, 47 one-line reasons):
- 88 are in the S propositions. A `Prop` has no decidable check, so the tool counts no kill. Each mutant breaks a
  named proof or does not elaborate, and the statement test fails on its text.
- 11 are `wrapperRows` mutants. Existing `#guard`s refute them, but the probe cannot elaborate those guards.
- 16 do not elaborate.
- 2 `scopeRewriter` mutants are equivalent: `(l.take 1).isEmpty` and `(l.reverse.take 1).isEmpty` both equal
  `l.isEmpty`.

Run 1 (VM, stopped and replaced) found three live mutants. Each got a new check in e57002047:
- `pipelineOf` `.take 1`: the `tagRewriter` guards;
- `scopeRewriter` `.dropLast`: the `governedSet` guards;
- `stackOf` `≤ → <`: the tie-table guard.

## Trust

`tools/trust_map.py --check`: PASS. Against e73ded834: K +0, S +62, V +52 (trusted +114, under R16's 150).
- `Contract.lean`: S +55, V +27;
- `Dispatch.lean`: S +7, V +10;
- `Stack.lean`: V +15.

The allowance is in `docs/trust-baseline.json` (SIGNED by standing ruling R16). FOLLOW-UPS.md "## pc-3" asks for the
ties pass.

## Tests

- Selected tests, once on the finished code (`mac-pytest.sh --select`, GitHub Actions run pc-3-69e3b5eb-t421436):
  407 units, 406 passed. The one failure was this item's: `test_assurance_manifest.py::
  test_every_json_handling_lean_file_is_classified` needed the two new files under `other_json`. Fixed in
  bf8b76bf, and the id's rerun passed (ve-mac-1, exit 0). No failure is in main-known-red.txt.
- After that, Lean changed only in `ContractExamples.lean`. The full `lake build` and `lean/audit.py` passed again,
  and `pytest tests/test_assurance_manifest.py tests/test_pc3_statements.py tests/test_trust_budget.py` reports 147
  passed.
- `tools/gate_collection.py --check --prebuilt`: 2 added, 0 removed, refused, stale or malformed.
- Main has moved 214 commits; jt-2c has not landed. The statements PC-3 uses (`governFast_eq`,
  `governSetsFast_eq`, `governorsOf_iff`, `govern_identity`, `scope_set_choices`, `governSets_choice_refused`,
  `scope_admission_sets`, `withGoverned`, `checkDocSets`) hash equal at the base and at main. `git merge-tree
  --write-tree HEAD main` exits 0 with no conflict.
- Not run: the full gate (the chain runs it).

## Size

`git diff --numstat` against the merge base counts 870 hand-written lines. That excludes the verbatim plan and spec,
generated files and the tool's two trust-mutants JSON outputs. It breaks down as:
- Lean: 425 (`Contract.lean` 192, `ContractExamples.lean` 133, `Dispatch.lean` +65 -37, `Stack.lean` 31, `VE.lean`
  3, `Gate.lean` 1);
- the statement checker and its test: 115;
- side tables: 41 (`trust-classes.json` 37, `layer_policy.py` 2, the assurance manifest 2);
- docs and evidence: 289 (this report 168, `trust-mutants-allow.json` 49, `mutants.json` 58, DELTA 14).

The Lean deliverables were 434 lines when measured before the second half (`git diff --numstat` after the Lean
commits). The overage is evidence required by checklist 13a, checklist 17 and R16. No deliverable was grown, and
nothing is cut to a later item beyond pc-3b, which the task names.

## Pilot bytes and next item

0 B directly (plan; an estimate, nothing claimed before a pilot audit).

Next item: pc-3b, G1 with G4 (`composed_superpose_all` in `Contract.lean`, spec 1.6, by `superpose_all_extra` and
`transfers_X`). Then pc-4 once pc-2c lands, and pc-9.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed route, response field or schema changes.
2. Deliverables built, no rule broken: PASS. See the plan-rows table. `git diff --stat e73ded834 -- ve/ rust/` is
   empty. The new test checks statements (checklist 17); it is not a report test.
3. Tests can fail: PASS. `mutants.json` lists 16 seeds (13 Lean, 3 Python); `trust-mutants.json` exits 0; and
   `test_pc3_statements.py::test_a_changed_statement_or_a_later_declaration_fails` shows the check failing.
4. Python, Lean and Rust agree: N.A. No Python or Rust product code changed. `ve/profile_table.json` and the route
   cases are unchanged after the regen.
5. R8 binding: N.A. Python reads no new field.
6. Gate evidence: PASS. The chain runs the gate on the final HEAD, and the base comes from `git merge-base`. The sync
   with main merges cleanly, and the statements PC-3 uses are unchanged (Tests).
7. No unsigned item: PASS. DELTA row 1 cites R16 with its evidence.
8. Every user-visible change in DELTA: PASS. No answer changes (`ve/` and the route cases are unchanged, the gate
   proofs hold).
9. Test selection: PASS. `select_tests.py --base $(git merge-base HEAD main)` includes `tests/test_pc3_statements.py`,
   which fails on seeds 12 and 13.
10. Lean statements: PASS. `check_pc3_statements.py` passes (27 declarations); each proof breaks under a wrong
    output (seeds 1, 7-11); no hypothesis was added.
11. Budgets and deadlines: N.A. None is added.
12. CPU and memory: N.A. No runtime path changed. C1 and C2 are build-time `decide` (not timed).
13. Test-removed trailers: PASS. `gate_collection.py --check --prebuilt`: 0 removed, stale or malformed.
14. Both directions: PASS.
    - `slotAgrees`: accepts the planned rows and refuses 8 pairs.
    - `stackOf`: keeps and drops profiles (F3.6, including `[]`).
    - `ScopeRunsOf`: holds for the document mode and for a refuse-all entry (F3.7).
    - `RouteFacts`: holds on the listed stacks and is false on `["acts@0", "scope@0"]`.
    - The statement check passes on the tree and fails on 3 mutations.
    - F3.1: not the identity on `doc`; the identity on `full`.
