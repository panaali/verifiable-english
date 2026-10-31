# pc-3 REPORT: the composition contract (profile-composition PC-3, first part)

Status: built, ready for review; no DRI signature needed. HEAD: the last commit on `feature/pc-3`.
Changed: the `interface` field on every row of AR-10's table (synthesis round 2 edits 1 and 6), C1 to C3,
`Compose/Stack.lean`, and `Compose/Contract.lean` (G2, scope's typed route evidence and `listed_evidence`), with
fixtures F3.1, F3.1b and F3.4 to F3.7. No answer changes (DELTA has only the R16 trust row).
Open: G1 with G4 (`composed_superpose_all`) is the next item, pc-3b. G1b and F3.2 to F3.3 belong to PK-1's owner.

## Inputs

- Plan and spec copied verbatim from 938e148cb (`docs/spec/profile-composition-PLAN.md`, `docs/spec/profile-composition.md`):
  plan PC-3 (lines 826-904), spec 1.1 to 1.5, 3.3 and 5.3.
- Synthesis round 2 (`debates/plan-synthesis-2/edits-profile-composition.md`): this item implements **edit 1** (the
  AR-10 slot `"pack"`, `slotAgrees (.pack _) "pack" = true`) and **edit 6** (the interface values of the wave
  profiles: `presupposition@0`, `cardinality@0` and `modality@0` `.layer`; `weighing@0`, `attitudes@0`, `scales@0`
  and `events@0` `.pack id`; `risk@0` and `alternatives@0` `.outside`; `hedges@0`, `purposes@0` and `examples@0`
  `.layer`; `commitments@0` `.outside`; the definitions field has no row).
- Statement gate: the plan's change log records the pc-d2 FIX and its confirmation, and one review each of
  pc-fid-rev and pc-fid-rev2. pc-fid-rev3 (DRI 2026-10-31) concerns writer rules and changes none of PC-3's
  statements; structure rows do not wait on it (I2).
- In-flight overlap: only `feature/jt-2c` edits `lean/VE/Compose/Dispatch.lean`, at its hunks after
  `withoutDocumentLayers`, after `gateOf` and after `gate_judgments`. It is not on main. This item edits `ProfileRow`,
  the row literals and their proofs, and adds `slotAgrees`, C1 and C2 directly after `profileTable`, away from
  those hunks. Other branches touch `lean/VE.lean` (imports only).

## Plan rows delivered

| Plan / task row | Where | Evidence |
|---|---|---|
| (1) `Interface`, the `interface` field, a value on every row of `baseRows` and `wrapperRows` (spec 1.1), slot `"pack"`, `slotAgrees` exactly as spec 1.2, the new component in `gate_legacy`, `gate_acts`, `gate_scope` and `VE.Cardinality.gate_cardinality` (it writes a row) | `lean/VE/Compose/Dispatch.lean`, `lean/VE/Cardinality/Gate.lean` (d79c2f86c) | `lake build` passes; ContractExamples guard "the values of main's rows" pins every profile's value |
| (2) C1 to C3 by `decide` | `interface_slot`, `interface_functional` (Dispatch.lean), `rewriter_ranks_distinct` (Stack.lean) | F3.4 examples; seeds 2, 6 |
| (3) `Stack.lean`: `rewriters`, `stackOf`, `listedStacks` (imports only `VE.Compose.Dispatch`) | `lean/VE/Compose/Stack.lean` | F3.5, F3.6; seeds 5, 6, 7 |
| (4) `Rewriter`, `Rewriter.Laws`, `pipeline`, `pipelineOf`, G2 (`pipeline_preserves`, `pipeline_off`, `pipeline_names`) by induction | `lean/VE/Compose/Contract.lean` | seed 1 |
| (5) `scopeRewriter`, `docRewriters`, `ScopeRunsOf`, `ScopeRuns`, `checkDocSets_pipeline` (from `scope_admission_sets` and `governSetsFast_eq`), `refuseAll_runs` | Contract.lean | F3.1, F3.7; seeds 8, 9, 10 |
| (6) `ScopeFaithful`, `ScopePreserves`, `ScopeSetsFaithful`, each proved from main's theorems (`scopeFaithful`, `scopePreserves`, `scopeSetsFaithful`); `RouteFacts` with its two PC-3 entries; `listed_evidence` | Contract.lean | seeds 11, 12, 13 |
| (7) `ContractExamples.lean`: F3.1, F3.1b, F3.4, F3.4b, F3.4c, F3.5, F3.6, F3.7; `lean/VE.lean` imports | `lean/VE/Compose/ContractExamples.lean` | `lake build VE.Compose.ContractExamples`. F3.1 also runs on a document with one governed reading set (`governedSet`), and a recording rewriter (`tagRewriter`) pins the order `pipelineOf` and `pipeline` give on four rewriters |
| Regenerated `lean/statements.txt`, `lean/axioms.txt` (and declarations, predicates, Audit.lean, codemap, checker pins) | `uv run python tools/regen_generated.py --write` (5e3e98fb1, 73a0da680) | `python3 lean/audit.py`: "PASS: 685 source files; 7647 named theorem declarations audited" |

Not delivered here: G1 with G4 (`composed_superpose_all`, spec 1.6), which the task assigns to **pc-3b**. G1b and
fixtures F3.2 to F3.3 belong to PK-1's owner (plan PC-3, spec 5.3). No route theorem is restated.

## Statements

Every PC-3 statement equals the spec's text after whitespace normalisation. `tools/check_pc3_statements.py` (new;
`tests/test_pc3_statements.py`) prints "PC-3: 27 declarations equal the approved text (RouteFacts staged); later
batches: 16". That covers the 25 declarations of 1.2 to 1.5 that this item builds, plus `ProfileRow` and `RouteFacts`.
Comments are dropped on both sides. The test also shows that the check fails on a weakened theorem, on an unstaged
`RouteFacts` and on a later batch's declaration built early.

Deviations, none of them a changed statement:
- `RouteFacts` has only the two PC-3 entries, and its last clause is `| _ => False` where the spec has PC-6b's,
  PC-7b's and PC-4b's entries (the task's instruction). Each of those batches adds its entry. The checker records
  this as `STAGED`.
- `pipelineOf` is in `Contract.lean`, as task row (4) and spec 1.4's block put it. The plan's obligations list
  names it beside `Stack.lean`. Nothing below `Contract.lean` reads it.
- Helper lemmas not in the spec: `filterMap_docRewriters`, `pipelineOf_scope`, and the three proofs `scopeFaithful`,
  `scopePreserves` and `scopeSetsFaithful`. Each conjunct of the three proofs is main's theorem itself
  (`governFast_eq`, `governSetsFast_eq`, `governorsOf_iff`, `govern_identity`, `scope_set_choices`,
  `governSets_choice_refused`).
- The planned rows' values (F3.4b, F3.4c) are written as `ContractExamples.plannedRows`, a fixture list that is not
  in `profileTable`. The stub's `ProfileRow.interface` was a function; the value is now a field. The gate still
  refuses a planned profile (`Unsupported profile presupposition@0`, guard).
- F3.1 uses `VE.Service.ScopeExamples.doc`: one `frame` governor over the two items `i1` and `i2`, with a lead-in
  and a closing unit beside them. "Two-unit" is read as the two governed units.
- `tools/layer_policy.py`: `VE.Compose.Contract` and `VE.Compose.ContractExamples` are at the runner layer (4),
  like `VE.Norms.FlaggedSpec` and `VE.Route.RunSound`, because they state theorems on
  `Service.Document.checkDocSets`. Spec 1.3 and 3.4 place `Contract.lean` above `Document.lean`. `Stack.lean`
  stays at Compose's layer.

Spec re-read:
- `slotAgrees` against spec `:251-258`;
- `Interface` and `ProfileRow` against `:227-237`;
- every row's value against 1.1's table `:172-183` and the planned rows' table `:194-204`;
- `rewriters`, `stackOf` and C3 against `:287-299`;
- G2 against `:316-347`;
- the scope block against `:356-391`;
- `ScopeFaithful`, `ScopePreserves`, `ScopeSetsFaithful`, `RouteFacts` (first two clauses), `listedStacks` and
  `listed_evidence` against `:405-428` and `:521-541`;
- F3.1 to F3.7 against `:2661-2673`.

## Evaluators and runners

N.A. This item adds no service mode, and no product path calls a new runner. `pipeline` and `scopeRewriter` are
specification functions. `checkDocSets` is unchanged and still evaluates its scope branch once. Each fixture runs
`scopeRewriter` once.

## Seeded bugs (Lean; the only product language changed)

`docs/profile-composition/pc-3/mutants.json` lists 13. Each was applied alone, built or checked, shown to fail,
and restored (`git diff` clean):

1. `pipeline` skips the last rewriter, the plan's seed (Contract.lean). `lake build` fails at `pipeline_preserves`,
   `pipeline_off`, `pipeline_names` and `checkDocSets_pipeline`. A scratch copy with those four proofs replaced by
   `sorry` shows the fixtures: F3.1's answer guard and its two non-identity guards fail, and `pipeline_off`'s
   example still passes.
2. `data@0` `.base` -> `.chain` (Dispatch.lean): `interface_slot` (C1) fails.
3. `ve.discourse@1` rank 10 -> 25 (Dispatch.lean): `pipelineOf_scope`'s `decide` fails (F3.5 and F3.6 pin the same
   list).
4. `slotAgrees (.pack _)` reads `"layer"` (Dispatch.lean): F3.4b's guards (ContractExamples.lean:60, :63) fail.
5. `stackOf` sorts descending (Stack.lean): F3.6's guards (:88, :89, :92) fail.
6. `rewriters` without `eraseDups` (Stack.lean): `rewriter_ranks_distinct` (C3) fails.
7. `listedStacks` lists `["acts@0", "scope@0"]` (Stack.lean): `listed_evidence` fails.
8. `scopeRewriter` swaps `withUnits` and `withSets` (Contract.lean): `checkDocSets_pipeline` fails.
9. `docRewriters` keyed on `scope@1` (Contract.lean): `filterMap_docRewriters` fails.
10. `pipelineOf` prepends the reversed stack (Contract.lean): `pipelineOf_scope` fails.
11. `RouteFacts ["scope@0"]` drops `ScopePreserves` (Contract.lean): `listed_evidence` fails.
12. `ScopeRunsOf` drops its fold conjunct, so every proof still holds: `tools/check_pc3_statements.py` reports
    "ScopeRunsOf: def differs" (`tests/test_pc3_statements.py`).
13. `ScopeSetsFaithful` drops `K.constraints = [] → cs' = cs`, and the proof still holds: the checker reports
    "ScopeSetsFaithful: def differs".

Trust mutants (checklist 13a): the final evidence is `docs/profile-composition/pc-3/trust-mutants.json`, an
allow-only `--rescore` of `trust-mutants-run2.json`. Command: `mac-pytest.sh --trustmut -- --max-mutants 1000 --allow
docs/profile-composition/pc-3/trust-mutants-allow.json --rescore …/trust-mutants-run2.json --json …/trust-mutants.json`.
It ran at db95e866c; later commits change no file under `lean/`. Result: exit 0, 16 definitions, 253 mutants.

| Verdict | Count |
|---|---|
| KILLED | 122 |
| ALLOWED | 117 |
| INVALID | 14 |
| SURVIVOR, UNKNOWN, NOT RUN | 0 |

Killed, by definition: `slotAgrees` 34, `wrapperRows` 29, `stackOf` 20, `rewriters` 13, `listedStacks` 13,
`pipelineOf` 10, `scopeRewriter` 2, `docRewriters` 1.

The 117 allowed, by reason (47 entries in `trust-mutants-allow.json`, one line each):
- 88 are mutants of the S propositions (`ScopeSetsFaithful` 20, `ScopeFaithful` 16, `ScopeRunsOf` 15,
  `Rewriter.Laws` 13, `RouteFacts` 12, `ScopePreserves` 10, `ScopeRuns` 2). A `Prop` has no decidable check, so the
  tool cannot count a kill. Each mutant breaks a named proof or does not elaborate, and `tests/test_pc3_statements.py`
  fails on any change to their text (seeds 12, 13).
- 11 are `wrapperRows` mutants of AR-10's existing data, whose lines change only by the new component. ScopeExamples'
  and Scope/Examples' `#guard`s refute them, but the tool's probe cannot elaborate those guards.
- 16 do not elaborate: `slotAgrees` 8, `rewriters` 3, `stackOf` 3, `scopeRewriter`'s list-empty 1, `Interface`'s
  `ctor-drop` 1.
- 2 `scopeRewriter` mutants are equivalent: `(l.take 1).isEmpty` and `(l.reverse.take 1).isEmpty` both equal
  `l.isEmpty`.

Run 1 (VM, stopped part-way and replaced by run 2) found three live mutants that needed checks, not allowances:
- `pipelineOf` `.take 1`: killed by the `tagRewriter` guards;
- `scopeRewriter` `.dropLast`: killed by the `governedSet` guards;
- `stackOf` `≤ → <`: killed by the tie-table guard.

These checks are in e57002047.

## Trust

`uv run python tools/trust_map.py --check`: "PASS: K, S and untied [V] within e73ded83483a and the allowances
introduced since". Against e73ded834: K +0, S +62, V +52, trusted +114, under R16's 150. By file:
- `Contract.lean` +82: S +55, V +27;
- `Dispatch.lean` +17: S +7, V +10;
- `Stack.lean` +15: V +15.

The classes are in `tools/trust-classes.json`. The allowance is recorded in `docs/trust-baseline.json`, SIGNED by
standing ruling R16. The FOLLOW-UPS.md row "## pc-3" asks for the ties pass.

## Tests

- Selected tests, once on the finished code: `zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base
  $(git merge-base HEAD main) --run` ran on GitHub Actions (6 shards, run pc-3-69e3b5eb-t421436): 407 units, 406
  passed. The one failure was mine: `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`
  needed `Contract.lean` and `ContractExamples.lean` under `other_json`. Fixed in bf8b76bf, and the rerun of that id
  passed (`mac-pytest.sh -- <id>`: "ran on ve-mac-1 … HEAD bf8b76bf (clean) … exit=0"). No failure is listed in
  main-known-red.txt.
- After that run, Lean changed only in `ContractExamples.lean` (the checks that kill trust-mutant survivors), plus
  `tools/trust-classes.json` and the allow file. `lake build` (full) and `python3 lean/audit.py` passed again, and
  `uv run pytest -q tests/test_assurance_manifest.py tests/test_pc3_statements.py tests/test_trust_budget.py`
  reports 147 passed.
- Main has moved 214 commits since the base e73ded834. jt-2c has not landed, and `Dispatch.lean` is unchanged on
  main. Every statement PC-3 uses is unchanged on main: a `git grep` hash of `governFast_eq`, `governSetsFast_eq`,
  `governorsOf_iff`, `govern_identity`, `scope_set_choices`, `governSets_choice_refused`, `scope_admission_sets`,
  `withGoverned` and `checkDocSets` is equal at the base and at main. `git merge-tree --write-tree HEAD main` exits 0
  with no conflict, so the merge train's sync merges cleanly.

- `uv run pytest -q tests/test_pc3_statements.py`: 2 passed.
- `uv run python tools/gate_collection.py --check --prebuilt`: "30737 collected, 30735 at e73ded834…; 2 added,
  0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers".
- `uv run python tools/regen_generated.py --check --only layer-ledgers`: "Lean layer graph kept (685 modules, 22
  reviewed legacy edges)".
- Not run: the full gate (the chain runs it on the final HEAD).

## Pilot bytes

0 B directly (plan). PC-3 gives later batches the stack order and the typed evidence their route statements fit
into. This is an estimate; nothing is claimed before a pilot audit.

## Next item

pc-3b: G1 with G4, `composed_superpose_all` in `Contract.lean` (spec 1.6), by `superpose_all_extra` and
`transfers_X`. Then pc-4 once pc-2c lands, and pc-9.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed route, response field or schema is added or changed, and no
   Python reads a new Lean answer.
2. Every deliverable built, no rule broken: PASS. See the plan-rows table above, each row with its commit and
   check. G1 with G4 moves to pc-3b on the task's own instruction. The diff has no Python or Rust product code
   (`git diff --stat e73ded834 -- ve/ rust/` is empty), and no Python copy of a Lean decision. Its one new test,
   `tests/test_pc3_statements.py`, checks statement fidelity (checklist 17), not a report. In-flight overlap was
   checked (jt-2c only).
3. Tests and gates can fail: PASS. `mutants.json` lists 13 hand mutants, each with its failing theorem, `#guard` or
   test. `trust-mutants.json`: exit 0 (122 killed, 117 allowed with reasons, 0 survivors). `tests/test_pc3_statements.py::test_a_changed_statement_or_a_later_declaration_fails` shows that
   the statement check fails.
4. Python, Lean and Rust agree: N.A. No Python or Rust product code changed, and no answer changes. `ve/` and
   `lean/VE/Route/examples/` are unchanged, and `ve/profile_table.json` stays byte-identical after the regen.
5. R8 binding: N.A. Python reads no new field.
6. Gate evidence matches the final HEAD: PASS for this builder's part. The full gate is the chain's, run on the final
   HEAD. The base comes from `git merge-base`. A sync with main is not merged here (jt-2c has not landed), but
   `git merge-tree` shows that it merges cleanly and that every statement PC-3 uses is unchanged on main (Tests).
7. No unsigned item: PASS. DELTA row 1 cites R16, with its evidence (per-file counts, mutants, the ties-pass row).
   No DRI signature is needed.
8. Every user-visible change in DELTA: PASS. No answer changes: the gate proofs still hold, `ve/` and the route
   cases are unchanged, and the profile table JSON is byte-identical. DELTA says so, and its only row is the trust
   growth.
9. Test selection finds the tests: PASS. `uv run python tools/select_tests.py --base $(git merge-base HEAD main)`
   includes `tests/test_pc3_statements.py`, which fails on a seeded statement change (seeds 12, 13).
10. Lean statements say what is claimed: PASS. `tools/check_pc3_statements.py` reports "27 declarations equal the
    approved text". Each new proof breaks under a wrong output (seeds 1, 7, 8, 9, 10, 11), and no hypothesis was
    added.
11. Budgets, limits and deadlines: N.A. PC-3 adds no budget, limit or deadline, and no service mode.
12. CPU or memory: N.A. No runtime path changed (`checkDocSets` and `gateOf` are untouched). C1 and C2 are `decide`
    proofs, checked at build time only. Their build time was not measured.
13. Test-removed trailers: PASS. `uv run python tools/gate_collection.py --check --prebuilt`: "2 added, 0 removed by
    a trailer, 0 refused, 0 stale and 0 malformed".
14. Both directions, cited evidence, spec re-read: PASS.
    - `slotAgrees`: accepts every planned row (F3.4b) and refuses eight other pairs.
    - `stackOf`: keeps the listed rewriters and drops the rest (F3.6, including `[]`).
    - `ScopeRunsOf` holds for the document mode and for a refuse-all entry (F3.7).
    - `RouteFacts` holds on the listed stacks (`listed_evidence`) and is false on an unlisted one
      (`¬ RouteFacts ["acts@0", "scope@0"]`).
    - The statement check passes on the tree and fails on three mutations.
    - F3.1 is identity-free on `doc` and the identity on a case without scope (`full`).
    - The spec re-read list is above.
