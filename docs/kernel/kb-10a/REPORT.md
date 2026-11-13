# kb-10a build report: the soft route's `soft-selected` kind

Status: all deliverables done; READY for the chain gate. No DRI signature is needed. Code HEAD `a94432c861` (merged with main `2086e5b997`).
Changed: Lean kind `soft-selected` with `selected_semantics` and `soft_wire_selected`; shape, encoder theorem, schema, relay `ve.soft_route.selected_at`.
Differential (d): **5,880 queries, 0 mismatches, 0 refusals** (A, B, K and G families of the RSP harness, deny and allow; list empty).
Kernel +48 lines (9,504 to 9,552), inside the pre-signed +300. Trust K +0, S +42, V +23 (R16). Five frozen keys unchanged.
Open: none. The full release gate is the chain's (not run here).

SIZE: 527 product, 771 tests, 483 other hand-written lines (and 642 generated) (`git diff --numstat $(git merge-base HEAD main) HEAD`, classified as in the section "Size").

## Deliverables

| Task line | Where | Evidence |
|---|---|---|
| (1) `selectedAt`, `mem_selectedAt` as given | `lean/VE/SoftNorms/Selected.lean` | `lake build VE.SoftNorms.Selected`; seeded bug S1 |
| (1) `outcomeAt`, `outcomeAt_iff` | same file | the `#guard`s `specAt …` of `lean/VE/SoftNorms/SelectedExamples.lean` |
| (1) the semantic theorem | `selected_semantics` (same file) | statement below; S6 |
| (2) kind `soft-selected` in `runSoftKind` | `lean/VE/SoftNorms/Run.lean` (dispatch line); the runner `runSelected`, decoder `decodeSelectedQuery`/`decodeQueries`, row `selectedRow` in `Selected.lean` | `tests/test_soft_selected.py`; `SelectedExamples.lean` guards |
| (3) runner theorem `soft_wire_selected` | `lean/VE/SoftNorms/SelectedSound.lean` (with `runSelected_answer`) | seeded bugs S2, S2b, S4, S5 |
| (4) shape, schema, encoder-fits, registration | `lean/ResponseShape/Schemas/SoftNorms.lean` `selected`; `ve/backends/lean_service_schema/soft-norms.json`; `ResponseShape.Encoders.SoftNorms.selected_fits`, `runSelected_fits`, `runSoftKind_fits`; the mode was already registered (`soft-norms`) | `lake build ResponseShape`; `lean/ResponseShape/SoftSelectedExamples.lean` guards; S7 |
| (4) registry `tools/kernel-paths.json` | `soft_wire_selected` added to `softNorms.theorems`; the `uncovered` entry's reason now says `soft-selected` is covered (see "Registry" below) | `tests/test_kernel_closure.py` 27 passed |
| (4) closure baseline and ALLOWANCES | `docs/kernel/closure-baseline.json`, `docs/kernel/ALLOWANCES.md` row "kb-10a, door C, pre-signed by the architect seat up to +300 lines" | `python3 tools/kernel_closure.py`: kernel 9,552, problems [] |
| Python relay `selected_at` | `ve/soft_route.py` (`selected_at`, `bind_selected`, `_query`) | `tests/test_soft_selected.py` (forged-answer, retyped-field and malformed-request tests); `tests/test_relay_binding_inventory.py` route `soft-selected` |
| Fixtures (a) three-rule document, two tuples, deny and allow | Lean `SelectedExamples.lean`; Python `test_selected_rules_and_outcomes_of_the_three_rule_document[deny/allow]` | tuples a, b, c, e (below) |
| Fixtures (b) a model violating an exception premise | `#guard … r#"[["e"]]"#` and `test_a_model_violating_an_exception_premise_is_answered_with_background_false` | answered, `background: false` |
| Fixtures (c) unknown predicate, wrong sort, empty `queries` | `test_refused_queries_name_their_diagnostic` (5 cases), Lean refusal guards | diagnostics below |
| Fixtures (d) the differential | `tests/soft_selected_diff.py`; output `docs/kernel/kb-10a/differential.txt` | 0 mismatches |
| Seeded bugs (i), (ii), (iii) | `docs/kernel/kb-10a/seeded-bugs.json` S1, S2 (and S2b), S3 | below |

The three-rule document (`h` strict on `x_required`, guard `v`; `d` default with an exception whose sufficient
condition `s` holds at a and e; `o` a default of the other sign, guard `w`, that `d` overrides). The answers, checked
by `#guard` and by the Python test (`uv run pytest -q tests/test_soft_selected.py`: 170 passed):

| tuple | selected | outcome, deny | outcome, allow |
|---|---|---|---|
| a (`d` excepted, `w`) | `o` | false | false |
| b (`v`) | `h` (both defaults blocked by the strict rule) | true | true |
| c (`w`, `d` not excepted) | `d` (overrides `o`) | true | true |
| e (`d` excepted) | none | false | true |

Two strict rules on one tuple give `["h", "h2"]` in rule order (`twoStrictText` guards).

## The semantic theorem

```lean
theorem selected_semantics (D : SoftDoc) (h : WellFormedSoft D = true)
    (M : VE.FiniteModel VE.Bridge.Entity) (hM : M.Valid (envAt (soften D) 0))
    (p : String) (vs : List VE.Bridge.Entity) (hvs : VE.TupleTyped M.asStructure (sortsOf D p) vs)
    (rel : String → List VE.Bridge.Entity → Prop)
    (hbase : ∀ r ws, r ∉ layerNames (soften D).T → (rel r ws ↔ M.asStructure.relation r ws))
    (ha : AgreesBelow (soften D) (size (soften D)) (fullOver M rel)) :
    (∀ name, name ∈ selectedAt D M p vs ↔
      ∃ N ∈ D.T.nodes, N.name = name ∧ N.pred = p ∧ (selects' D N).denote (fullOver M rel) (tupleVal vs)) ∧
    (outcomeAt D M p vs = true ↔ (atom p (sortsOf D p)).denote (fullOver M rel) (tupleVal vs))
```

- The structures S: `fullOver M rel = { M.asStructure with relation := rel }`, so S has the model's carrier, domains
  and constants, and any relations. Every structure whose base restriction is `M.asStructure` is of this form
  (restriction keeps carrier, domains and constants); writing it this way avoids casting the tuple between carriers.
  `fullOver_restrict` proves that `hbase` is exactly the task's "base restriction is `M.asStructure`":
  `hbase ↔ restrictAll (soften D).T (fullOver M rel) = M.asStructure`, for a model valid over `envAt (soften D) 0`.
- The layer premises: `AgreesBelow … (size (soften D))` as the task names it. `ConstantsTyped` is discharged from
  `hM` (the constants are the model's). I did not use the soft route's admissibility predicate `PrefixAdmissible'`
  (`Coherence.lean`): it implies `AgreesBelow` but also assumes the soft premises, and the kind answers models that fail
  them (SPEC 4.2), so it would make the theorem say less.
- No extra hypothesis remains. An earlier version assumed `p` regulated. The final one drops it: an unregulated `p`
  has no sorts, and `atom p []` is `⊥` on both sides (commit `4a26e3460b`).
- Not vacuous: `selected_semantics_nonvacuous` gives, for every valid model, a `rel` meeting `hbase` and `ha`
  (`canon`, each layer read as its expansion).
- No executable evaluator appears in the statement. `selectedAt` and `outcomeAt` are its subjects, and
  `mem_selectedAt` and `outcomeAt_iff` bridge them to `denote`.

## The runner theorem

`soft_wire_selected (j answer) (h : runCase j = .ok answer) (hk : caseKind j = .ok "soft-selected") (hn : usesSoftPath j = true)`
gives the id, `environment`, `src` (`decodeSoftSource environment (j.getObjValD "norms") = .ok src`), the model
(`decodeModel src j = .ok ⟨M, hM⟩`), the request's `queries` array (non-empty) and the decoded queries, one per
request query (`qs.length = raws.size`), each `QueryDecoded` against the request object at its position (predicate
and ids as sent, a regulated predicate, the tuple its sorts zipped with the ids, typed in `M`), and
`SelectedAnswer id src.D M qs answer`. That is the closed equation `answer = Wire.ok id [("background", .bool
(classificationBackgroundValid src.D M)), ("results", …)]`, each result `{"predicate", "tuple", "selected": selectedAt …,
"outcome": outcomeAt …}`. No open tail exists, so the kb-7 F1 class cannot recur: `tests/test_kernel_closure.py::
test_no_kernel_statement_leaves_answer_fields_open` passes with the theorem listed.

The runner expands each rule's selection formula and each regulated atom **once per case**. `circ`'s closure table
recomputed every layer at every use: 70 RSP queries took 32.4 s, now 0.6 s (`uv run python -c …` timing, session log).
`expList` builds the table as a list; `expList_lookup`, `expanded_circ` and `selectedRow_eq` prove the row is
`selectedAt`/`outcomeAt`, which is what `runSelected_answer` reads. SPEC 4.4 (one call per document and model) is
the relay's shape, tested by `test_one_lean_call_per_document_and_model`.

## Registry

The registry has no per-kind "covered" table yet (kb-1 adds it). It has `covered_writers`, but only for verdict-token
writers, and `runSelected` writes no verdict token (an entry would be reported as "not a verdict writer"). So the
kind's coverage is recorded where the file records it today: `soft_wire_selected` in the path's `theorems`, and the
`uncovered` entry for `runSoftKind` (which keeps its kinds list without `soft-selected`) says `soft_wire_selected`
covers it. `python3 tools/kernel_closure.py`: problems [].

## Kernel closure

`python3 tools/kernel_closure.py --out …` on the merged tree: softNorms 4,761 to 4,920 lines; **kernel 9,504 to
9,552 (+48)**; keyed 16,150 to 16,198. That is below +300, so the ten largest spec modules are not needed. Saved in
`docs/kernel/closure-baseline.json`. The spec table, `frozen-keys-20261111.md` and ALLOWANCES quote it
(`tests/test_kernel_closure.py`: 27 passed). The candidate paths that reach `runSoftKind` (document, discourse,
readingsRoute) gained the new runner's lines, as measured.

## Trust (R16)

`uv run python tools/trust_map.py --check` against `2086e5b997a3` (main): **K +0, S +42, V +23, trusted +65**. The
lines by file:
- `Selected.lean` +25 (S: `selectedAt`, `outcomeAt`, `fullOver`, `SelectedQuery`);
- `SelectedSound.lean` +17 (S: `QueryDecoded`, `SelectedAnswer`);
- `Schemas/SoftNorms.lean` +22 (G[V]: the `selected` shape and its `kind`/`row`/`file` entries);
- `Run.lean` +1.

The decoders, the expansion and the runner are tied by their theorems. The allowances are recorded in
`docs/trust-baseline.json`, signed under R16. Trust mutants on the final Lean (`4a26e3460b`, `mac-pytest.sh
--trustmut`, both example files as `--test`): **108 KILLED, 0 SURVIVOR, 0 UNKNOWN, 10 INVALID, 65 ALLOWED, exit 0**
(`docs/kernel/kb-10a/trust-mutants.json`; reasons in `trust-mutants-allow.json`). What is allowed:
- `QueryDecoded` and `SelectedAnswer`: 53 mutants. Both are Props no check can evaluate, read by the runner theorems,
  which S2b, S4 and S5 break.
- Shape mutants equivalent under `.zip`/`.equals`: 6.
- The row's `admission` entry: 1. No Lean check reads it (Python checks admission rows against the generated schema).
- The file-defs `UNKNOWN`s: 3. They are killed in substance; the imported `DefaultsExamples` probe cannot elaborate.
- Two text refusals Lean rejects (`fullOver` lit-plus, `selectedAt` list-empty).

The ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## kb-10a") and in `docs/kernel/kb-10a/FOLLOW-UPS.md`.

## The differential (task fixture d)

`uv run python <kb-10/dump.py> OUT A-T0,…,G8` (all 42 A, B, K and G cases of `usecases/anthropic-rsp/run.py`; the
harness has no N cases), then `uv run python tests/soft_selected_diff.py OUT`. One `selected_at` call per document
and case.

```
TOTAL: 5880 queries, 2641 with a selected rule (Python), 0 mismatches
```

84 document×case entries, every one `background True`, 0 refused; the full listing is
`docs/kernel/kb-10a/differential.txt`. **Mismatch list: empty.** Before the main merge the same run gave 2,559
queries with a selected rule and also 0 mismatches. Main's RSP fidelity fixes changed the documents.

Not reproduced: the architect's exact 420-query subset (3 cases, 2 defaults). `dump.py` takes the cases as an
argument, and SPEC.md does not name them; three triples gave 180 to 182 selected, not 187. The full family set
contains every such subset. Selection is compared as sets (`dump.py` sorts Python's names); Lean's list is in rule
order.

## Frozen keys

`.venv/bin/python usecases/<key>/…` as `docs/kernel/frozen-keys-20261111.md` lists them, run on `e3c3170d3c` (before
the merge with main; not re-run after it). No product or harness file calls the kind: `grep -rln
"selected_at\|soft-selected" --include=*.py ve usecases tools conformance` names only `ve/soft_route.py` and a comment in
`tools/layer_policy.py`.

| Key | Command | Exit | Printed |
|---|---|---:|---|
| RSP | `run.py --check` | 0 | 110 / 126 |
| Preparedness | `run.py --check --base-only` | 0 | (comparison) |
| FSF | `run.py --check` | 0 | (comparison) |
| agent-policy | `check.py base` | 0 | seconds 99.9 |
| eligibility | `run.py --no-write --no-mutants` | 0 | `"open": []` |

`--check` compares with the committed `results.json`, so the answers are byte-identical. No caller uses the kind.

## Seeded bugs (`docs/kernel/kb-10a/seeded-bugs.json`)

| Id | Lang | File | Bug | Fails |
|---|---|---|---|---|
| S1 (i) | Lean | `lean/VE/SoftNorms/Selected.lean` | `selectedAt` filters on `N.sign` | `mem_selectedAt` (Selected.lean:40, :42) |
| S2 (ii) | Lean | same | the row answers the negated outcome | `selectedRow_eq`, so `soft_wire_selected` |
| S2b (ii) | Lean | same | `runSelected` negates every expanded atom | `runSelected_answer` (SelectedSound.lean:108), so `soft_wire_selected` |
| S3 (iii) | Python | `ve/soft_route.py` | `bind_selected` skips the tuple binding | `test_a_forged_answer_is_unavailable[a tuple not sent]`, `[a tuple of another query]`, `[a longer tuple]` |
| S4 | Lean | `Selected.lean` | the decoder accepts an unregulated predicate | `decodeSelectedQuery_ok` |
| S5 | Lean | `Selected.lean` | `background` from `backgroundValid'` | `runSelected_answer` |
| S6 | Lean | `Selected.lean` | `fullOver` with every domain true | `selected_semantics` |
| S7 | Lean | `lean/ResponseShape/Schemas/SoftNorms.lean` | `outcome` typed string | the generated schema refuses the genuine rows (`test_soft_selected.py`). The encoder theorem does not see it, because skeletons read booleans as `Skel.any` |
| S8, S9 | Lean | the two example files | a guard's expected value changed | the guard |

Each was planted, its check run, and the file restored with `git checkout`. For S3, the relay mutation gate
(`test_relay_binding_inventory.py -k soft-selected`) still passes: the schema's `x-equals` refuses those mutants first.

## Tests run

- While iterating: `tests/test_soft_selected.py`, `tests/test_relay_binding_inventory.py`,
  `tests/test_kernel_closure.py`, `tests/test_route_row_schemas.py`, `tests/test_assurance_manifest.py`, and
  `lake build` of the edited modules.
- Final tree: `test_soft_selected.py` + `test_kernel_closure.py` 197 passed;
  `test_relay_binding_inventory.py -k soft` 21 passed; `test_assurance_manifest.py` 157 passed.
- `lake build` (1,435 jobs) passes. `python3 lean/audit.py`, run through the regen: PASS, only the standard axioms.
- `uv run python tools/regen_generated.py --check`: 40 entries fresh.
- `uv run python tools/gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
- The 8 `tools/check_*_statements.py`: exit 0.
- Selected run on committed code (`mac-pytest.sh --select`, `9c0e52be36`, ran on ve-cloud-2): 508 units, 3 failed.
  - `test_assurance_manifest::test_every_json_handling_lean_file_is_classified`: the new Lean files were unclassified.
  - `test_route_row_schemas::test_corpus_reaches_every_answer_kind_of_every_route`: the route-case corpus had no
    `soft-selected` case (ROUTE-RECIPE step 6).
  - `test_wire_gate_corpus::test_gate_corpus_holds_every_test_input_of_every_unit`: the new tests' `pytest.skip`
    calls, then the new soft sources missing from the contract corpus.
  - All three are fixed (`f5d99187c1`, `546d2d43c5`). Reruns of the failed ids: 2 passed + 1 failed, then
    `test_wire_gate_corpus` + `test_wire_contract_faults` 185 passed.
  - An earlier selected run (`ad24401bb2`) stopped at setup: the x86 host had no pin for the branch's `ve_service`.
    `lean/checkers.lock` is now regenerated and committed.
- Not run by me: the full release gate (the chain runs it on the final HEAD).

## Notes for the DRI

- Conservative choices, taken without asking:
  - `queries` is counted against `VE.Limits.maxTuples` (100,000) before any query is decoded, so a longer request is a
    `ResourceLimit`. The task set no limit, and refusing is the narrower reading.
  - The relay binds every selected name to the document's rules on that predicate, in rule order, once.
  - The relay sends a malformed query as given, so Lean refuses it. It had crashed with `TypeError`, which
    `test_a_malformed_request_value_is_refused_with_a_diagnostic` caught.
- `soft_wire_elaborate`'s proof gained one `bind_ok` step and one kind inequality, because the new branch comes first
  in `runSoftKind`. Its statement is unchanged.
- The `atom` of a predicate of arity other than 1 or 2 is `⊥` (`Norms.Basic.atom`). So `outcomeAt` is false there, as
  the layer body's atom is. The theorem holds for every arity.
- `tests/soft_selected_diff.py` is a script, not a collected test (D4).
- `conformance/wire-contract/soft-norms@0-test-inputs.json` gains the two sources `test_soft_selected.py` submits.
  That file's recorder also rewrote `soft-norms@0-gate.json` with `boundary_problems` in unrelated checks
  (`r0-guard-nodes`, `r0-condition-syntax`, …) on this host. I did not keep that rewrite. It looks environmental, but I
  did not check it on main.

## Spec re-read

- "does NOT refuse a model that fails the soft background" against SPEC.md 4.2: `background: false`, test (b).
- Answer `Wire.ok id [("background", …), ("results", […])]`, the result keys and "rule names in the source's rule
  order", against the task (2): `SelectedAnswer`; the two-rule guard checks the order.
- "naming the query index" against the task (2): `query <i>:` in each per-query diagnostic. The two whole-request
  ones (empty, not an array) name no index; they are not about one query.
- "state S's hypotheses with … `ConstantsTyped`, `AgreesBelow … (size (soften D))`" against the task (1):
  `AgreesBelow` stated, `ConstantsTyped` discharged. `fullOver_restrict` gives the restriction equation.
- "`selected = selectedAt src.D M p vs` and `outcome = outcomeAt …` and `background = classificationBackgroundValid`"
  against the task (3): `SelectedAnswer`.
- Registry "a `covered` entry … in whatever form the registry then has" against `tools/kernel-paths.json`'s comment
  and `kernel_closure.py` (`covered_writers` is for verdict writers only): see "Registry".
- ROUTE-RECIPE steps 1 to 7: mode already registered; shape; encoder theorem in `ResponseShapeAudit.lean`
  (regenerated); schema; relay; `tests/data/route-cases.jsonl` cases; fuzz (inventory and own tests).

## Size

Product: `Selected.lean`, `SelectedSound.lean`, `Run.lean`, `ElaborateSound.lean`, `Schemas/SoftNorms.lean`,
`Encoders/SoftNorms.lean`, `ve/soft_route.py`, `VE.lean`. Tests: `tests/`, the two Lean example files, the conformance
inputs. Other: docs, the registry, the trust side table, the assurance manifest, `layer_policy.py`. Generated: the
inventories, schema, code map, census, closure baseline, trust baseline and the mutants record.

## Commits (`git log --oneline --no-merges main..HEAD`, saved)

```
a94432c861 trust-mutants record on the final Lean (4a26e3460b): exit 0
4a26e3460b selected_semantics needs no regulated-predicate hypothesis
546d2d43c5 record the soft-selected test's two soft sources in the wire-contract gate's test inputs
f5d99187c1 classify the new Lean files in the assurance manifest; record soft-selected route cases; no skips
9c0e52be36 pin this branch's ve_service build in lean/checkers.lock (regenerated, R12)
ad24401bb2 the differential re-run on the merged tree: 5,880 queries, 0 mismatches
101ae3dfd2 trust-mutants rescore on the merged tree: exit 0
4a89b58675 DELTA (R8, R16, R12), follow-ups and the seeded-bug record
da72bd51db trust-mutants record on the final Lean (f0443cdcac): exit 0
f0443cdcac charge queries against maxTuples; the relay sends malformed queries for Lean to refuse; non-vacuity
e3c3170d3c trust-mutants rescore with the allow file
0da14093dd guards for two selected rules and the soft-norms row's other entries; record and allow file
309ad0e8dc guards on the soft-selected shape with the mode's own answers
3a4b7e6e6e guards that read selectedAt and outcomeAt directly on the decoded fixture
9a54791002 record the trust growth (S +42, V +23) under standing ruling R16
a66066b970 tie runSelected by runSelected_answer; classify the new declarations; regenerate the audit manifests
2946307138 kernel closure re-measured: +48 kernel lines (9,552), within the pre-signed +300 (door C)
2ef17a7ed1 regenerate the generated files
874874b34a document soft-selected in the soft-norms and kernel-boundary specs; save the differential
899b158db8 expand each rule once per case; relay mutation gate and differential script
3b5bb162ac the soft route's soft-selected kind, its semantic and runner theorems, shape and relay
```

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. `test_every_answer_field_retyped_is_unavailable` (7, true, null, [], {}, 1.5, a lone
   surrogate, a 10k-deep list and "absent" at 11 paths), `test_a_malformed_request_value_is_refused_with_a_diagnostic`,
   and `test_relay_binding_inventory.py` route `soft-selected`.
2. Every deliverable built: PASS. The "Deliverables" table.
3. Tests can fail: PASS. Seeded bugs S1 to S9; trust mutants exit 0 (`trust-mutants.json`).
4. Agreement: PASS. The differential, 5,880 queries, 0 mismatches (`differential.txt`); a fixture of two
   simultaneously selected rules (`twoStrictText`).
5. R8 binding: PASS. `test_a_forged_answer_is_unavailable` (a tuple not sent, another query's tuple, a dropped,
   added or reordered result, a name that is no rule, a rule of another predicate, a duplicate, rule-order breaks,
   another id); inputs: `test_refused_queries_name_their_diagnostic`.
6. Gate evidence on the final HEAD: PASS for this item's evidence. The merge with main is in (`fc3ba838fa`). The
   commit list is from `main..HEAD --no-merges`. The full gate is the chain's.
7. No unsigned item: PASS. DELTA rows cite R8, R16 and R12. Trust follows R16 with the allowance recorded. The
   kernel rise is pre-signed by the architect seat (ALLOWANCES).
8. Every user-visible change in DELTA: PASS. Row 1 (refused on main with `UnsupportedProfile`, now answered, with
   every new diagnostic); `test_refused_queries_name_their_diagnostic`.
9. Test selection: PASS. `select_tests.py --paths ve/soft_route.py` (and `Selected.lean`, `Schemas/SoftNorms.lean`)
   select `test_soft_selected`, `test_relay_binding_inventory` and `test_kernel_closure`. The seeded S3 fails
   `test_soft_selected`.
10. Statements say what is claimed: PASS. S2b and S5 break `runSelected_answer`, S1 breaks `mem_selectedAt`, S6
    breaks `selected_semantics`. The runner theorem is about the returned value (`SelectedAnswer` is a closed
    equation). `tools/check_*_statements.py`: all exit 0. No hypothesis was added to an approved statement.
11. Budgets fail closed: PASS. `test_queries_are_charged_against_max_tuples_before_any_is_decoded` (at the limit
    answered; one over is `ResourceLimit`, even with malformed queries). The kind has no budget parameter, and its
    verdict fields are booleans of a total evaluator.
12. CPU: PASS. One expansion per case (32.4 s to 0.6 s on 70 RSP queries), one Lean call per document and model
    (`test_one_lean_call_per_document_and_model`). The pilots do not reach the kind.
13. Test-removed trailers: N.A., no test removed or renamed (`gate_collection.py --check --prebuilt`: 0 refused,
    0 stale, 0 malformed).
14. Both directions and cited evidence: PASS. Accepted and refused sides: `test_the_genuine_answer_is_bound` with
    `test_a_forged_answer_is_unavailable`; limit and limit+1; `background` true and false. The spec re-read section
    lists each statement.
15. Four classes: PASS.
    - No overclaim: the docstrings name only what the theorems state; `selected_semantics_nonvacuous`.
    - No silent cut: every numbered deliverable is built.
    - Every new check can fail: S8, S9 and the 108 KILLED mutants.
    - Limits before work: the `maxTuples` test.
