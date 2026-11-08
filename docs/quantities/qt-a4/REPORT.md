# qt-a4 REPORT: the `cardinality@0` relay and its document hook (quantities QT-A4)

Status: all four deliverables built. `ve document check` admits a part document under W6a's lists with `documents@1`, and refuses the constitution's four-profile list at the gate.
Changed: `ve/cardinality.py` (new relay), Lean's `document` mode reads `cardinality` content, `tests/test_cardinality_{lean,answer}.py`, two route cases, the layer row.
Open: the four-profile list stays refused, so the constitution's 29 units stay blocked until qt-a4b's first row, which changes an approved statement (`gate_cardinality`) and needs the DRI's ruling then. HEAD: the commit holding this file.
DRI signature needed: none (DELTA cites R1, R8, R16). Size: 1,306 hand-written, accepted to about 1,350 (`reviews/dri-decisions-20261103-qt-a4-size3.md`).
Pre-existing red: none met in this item's selected run (below). Report tests: none added (D4).

## Statement gate and edits

The quantities statement review accepted QT-A3 and QT-A4. No statement changed: `uv run python tools/lean_statements.py --check` PASS (run before the merge), and `git diff $(git merge-base HEAD main) -- lean/VE/Cardinality lean/VE/Compose` is empty. Synthesis round 2 (`edits-quantities.md`): none of its seven edits concerns this item; none is implemented here. Deviation from the plan's list: the six test files and the deletion of `ve/surface/count.py` are qt-a4a, as the task says.

## The provenance rules (qt-a3d left this to this item): needed, the asserted half is in

`VE.Time.Document`'s rule is that asserted leaves formalise asserted units, and quoted units enter only through bridge leaves. Without it a graph node could rest on an attributed unit, a quotation silently becoming a premise. So `Service.Document.cardinalityReport` binds every node to an **asserted** unit holding its statement: `tests/test_cardinality_lean.py::test_every_graph_node_is_a_unit_holding_its_statement` (a quoted leaf refused, the same unit without a graph admitted), guards in `CardinalityExamples.lean`. The bridge half needs a label the graph's nodes do not have (`Document.decodeNode` refuses the member), so it is qt-a4b's second row; QT-A5's plan needs it (`bridge:accepts(fomc, ...)`).

## Plan rows

| Row (plan :766-782, task) | Delivered by | Check |
|---|---|---|
| (1) `ve/cardinality.py` sends cases with `rows`, binds names to the request | `admission`, `check_certificate`, `countermodel`, `document`, `paraphrase` | `tests/test_cardinality_answer.py` |
| (1) recomputes `report_id` as qt-a3d says | `bind_report`, through `ve.admission.report_identity` (see "Identities") | `::test_every_one_fault_mutant_is_refused_or_changes_nothing[document]` |
| (1) `prove_quantity` on Lean's regenerated problem, the certificate sent back | `prove`, with the claimed table and problem | `tests/test_cardinality_lean.py::test_a_found_certificate_is_lean_s_and_an_open_problem_has_none`, `tests/test_cardinality_answer.py::test_a_search_s_verdict_is_lean_s_and_typed` |
| (2) fuzz: dropped, emptied, retyped, duplicated, reordered, out of range, one and two faults | `_mutants` over each case kind and the document row | `::test_every_one_fault_...`, `::test_two_faults_...`, `::test_every_mutant_of_a_document_row_...` |
| (2) the duplicated-leaf row (qt-a3d's gap) | `bind_report` | `::test_a_report_s_rows_are_bound_with_and_without_a_matching_id[duplicated]` |
| (3) the hook, through Lean's `document` mode | `Service/Document.lean`, `ve/document/lean.py` (`report.py`, `render.py`, one branch each) | `tests/test_cardinality_lean.py`, `VE/Service/CardinalityExamples.lean` |
| (3) dr-qt-cardinality-doc: four-profile part document admitted | **not admitted**: see below, as the task rules | `::test_the_gate_refuses_a_list_cardinality_does_not_compose_with`, route case `cardinality-four-profiles` |
| (4) `tools/layer_policy.py` (one row), route cases | `cardinality` in layer 4; `cardinality-part`, `cardinality-four-profiles`, captured with `-p tests.route_case_recorder` (`VE_RELAY_CASES`), appended | `::test_the_route_cases_answer_as_recorded`, `tests/test_route_row_schemas.py` |
| Seeded bug: the binding skips the region table, a renamed region is accepted | `region-table-skipped` | `tests/test_cardinality_answer.py::test_a_renamed_region_is_refused_by_the_relay_itself` |

Files beyond the task's list, each forced by a check: `lean/VE/Service/CardinalityExamples.lean` and `lean/VE.lean` (R16's mutants score only Lean checks), `lean/ResponseShape/Schemas/Document.lean` and its pinned fingerprint (the row's shape), `ve/document/{report,render}.py`, `ve/admission.py`, `tools/relay_lint.py`, `tools/identity-sites.json`, `tools/trust-classes.json`, `docs/ARCHITECTURE-LAYERS.md`, `ve/assurance-manifest.json` (the document decoder's pin) and two lines of `tests/test_route_row_schemas.py` (`document` joins the corpus; a report is optional there, the relay binds it).

## The refusal: first row of qt-a4b

The refusal comes from the gate, so `Dispatch.lean` is not edited. Probe through `ve document check` (`::test_the_gate_refuses_...`): `[cardinality@0, norm-defaults@0, norms@0, readings@1]` answers `UnsupportedProfile: Missing profile relational-fol@0`; with W6a's list added, `cardinality@0 with norm-defaults@0`. The missing gate fact has three parts: `VE.Compose.cardinalityOthers` refuses `norm-defaults@0`, `norms@0` and `readings@1`; `Wire.profileLists` (spec 4.2's E2) admits W6a's two lists only; and `VE.Cardinality.gate_cardinality` states the gate admits exactly E2's lists, so the change is to an approved statement. The DRI noted this (`reviews/dri-decisions-20261102-qt-a4-size.md`, item 2): the ruling waits for qt-a4b's task file, which must name it as its stop point. The decoder also needs composing: those three profiles are first-order, and cardinality's environment is W6a's order family.

## Not delivered: qt-a4b

1. The gate fact above, with its ruling, then the four-profile part document admitted. Closes dr-qt-cardinality-doc with the next constitution pilot.
2. Bridge leaves: labels on the graph's nodes (W6a's provenance rule's quoted half); QT-A5 needs it.
3. `open_terms`, `reading_sets` and `narrowings` beside `cardinality@0`: refused by name today (`::test_what_the_chain_does_not_compose_is_refused_by_name`). `senses` likewise.
4. A Lean route for the premise set's status: `ve document check` says `premises: UNKNOWN`, never a Python verdict.
5. A proved shape for the row's report: `document.json` types it, but it is `copied`, so the encoder theorem proves it `any` (FOLLOW-UPS "## qt-a4", with the ties pass).
6. `tools/relay_mutation_gate.py`: a `cardinality` reader and a recorded `cardinality@0` document fixture. Today the gate fuzzes that mode at the schema (`service:cardinality`), and the binder is fuzzed by this item's tests.

## What the relay binds, and what it leaves to Lean

| Member | Treatment |
|---|---|
| Statements and claims | `formula` equal to the one sent in Lean's spelling (`Identities.spelled`: a literal lowered on the request's scale, an omitted tag written, a printed negative zero unsigned), so another number, tag or statement is refused. See "Review fix round" |
| Region table | each sort finite in the request, predicates distinct, declared, unary on that sort; each row `cardinality__<sort>__<bits>`, one bit per predicate, one row per region; order tied to the problem's region premises; then Lean confirms the claimed table and problem (`_confirmed`, spec 4.1), which also covers what the request cannot say (predicate order, bridges) |
| Report | root, leaves as the request graph's reachable leaves, each once, in submitted order, statements, `report_id` recomputed |
| W6a identities | equal to the request projection's, through `Environment` |
| Sizes, ids | sizes typed and in the table's order; `environment_id` and meaning ids typed as hex64 |
| Left to Lean (R8) | a line's wording, `refutes`, a size's value, which valid digest an identity is |

### Identities (D7)

My first version recomputed the meaning and environment identities, and `tests/test_identity_lint.py` refused those new sites: Lean owns those domains and a new site needs a DRI signature. They are typed now, as sibling relays type them. `report_id` is the one recomputation, as the task and qt-a3d's report ask. It goes through `ve.admission.report_identity`, the one existing Python `ve-report` site moved out of `bound_admission` (`tools/identity-sites.json` scope updated; `uv run python tools/identity_lint.py --base $(git merge-base HEAD main)`: PASS, 45 sites, no growth). That is a second caller of a Lean-owned preimage, removed with the site by AR-15; the reviewer may want to look at it.

## Evaluate once, and what is charged

Each unit's statement is decoded once (`contentOf`), under S2's per-statement limit, in a document bounded by the service's request size; the graph is `Document.admitGraph`, unchanged: 1,000 nodes and 50,000 statement nodes, charged first. `cardinalityReport` builds one hash map of the units and reads each node once. Fixture: `tests/test_cardinality_lean.py::test_a_large_well_formed_graph_ends_within_its_limit` (1,000 nodes answered, 1,001 `ResourceLimit`). The relay asks Lean twice for `admission` and `countermodel` (`_confirmed`), a constant factor. Not timed against the pilots (no pilot lists the profile yet); no whole-document run.

## Seeded bugs

`docs/quantities/qt-a4/mutants.json`: 17 Python and 6 Lean, each planted alone, its named test failing, restored. Three Python ones first **survived**, Lean's confirmation hiding the binder's own checks, which is why `::test_the_relay_s_own_checks_hold_when_lean_cannot_confirm` exists. The Lean ones ran against a mutated service pinned in a temporary `lean/checkers.lock`, so each kill is the test's assertion (`DID NOT RAISE`, a regex mismatch), not the pin. The six ran before the merge and before the asserted-unit line; that line's mutants are in the sweep below.

## Trust

`uv run python tools/trust_map.py --check`: PASS, K +0, S +0, trusted +67: `VE/Service/Document.lean` V +54, `ResponseShape/Schemas/Document.lean` V +13. SIGNED by standing ruling R16; two `--allow` records in `docs/trust-baseline.json`; FOLLOW-UPS "## qt-a4" asks for the ties pass. `CardinalityExamples.lean` is T.

`zsh .../mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/quantities/qt-a4/trust-mutants.json --allow docs/quantities/qt-a4/trust-mutants-allow.json --rescore ...` exit 0 at 7163aafe6: 141 killed, 0 survivors, 0 unknown, 4 allowed. The last full run was at eb5b4f1e7 on the Mac, then two rescores after an allow-only edit and the main merge. Per definition, in `mutants.json`. The four allowed: three do not build; `environmentOf`'s `take 1` is equivalent where it survives (probe: `acts@0` and `alternatives@0` before `cardinality@0` get the same gate text on both paths).

The first sweep's kills all read UNKNOWN: each guard through `check` walks about 10,000 constants for the probe (83 s under load, measured), and 27 of them did not finish in 30 minutes. The guards now read their definition (5 s), with the `check` cases folded into two: 15 checks, 263 s.

## Tests and gates

- Selected, fix round: the same command at b24ce6647 (`tests/test_cardinality_answer.py` and `tests/test_cardinality_lean.py` first, as changed): exit 0, 493 units over 6 GitHub Actions shards, 0 failed, 2,853 s, run `qt-a4-b24ce664-t695483`. Only this report changed after it. `lake build`, `lean/audit.py` (8,211 theorems), `tools/regen_generated.py --check` (35 entries), `tools/relay_lint.py` and `tools/identity_lint.py` pass at the same commit. No test on `main-known-red.txt` was met.
- Selected, before the fix round: `zsh .../mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, on the Mac at 9deb1aefa: exit 0, 478 units, 0 failed, 4,660 s. Only this report and `mutants.json` changed after it. Two earlier runs at earlier commits stopped or failed on this item's own faults (the identity lint, the layer map, the seeded fault's text, the pending allowance, the schema corpus), each fixed and its ids rerun (205 passed).
- `uv run python tools/relay_mutation_gate.py` rc 0 on the final code: 46 routes, 148,149 mutants, 0 failures (`service:document` 13 fixtures, `service:cardinality` 13 fixtures).
- Not run: the full gate (the chain runs it on the final HEAD), and Rust (no Rust changed).
- `python3 lean/audit.py --check`: PASS (737 source files, on the merged tree). `tools/regen_generated.py --check`: 35 entries.

## Review fix round (`qt-a4-review.final.md`, F1 and F2, both B)

**F1: the relay refused statements Lean admits.** The earlier claim in this report, that no canonical form differed, held only because the route cases have no decimal or date. The sweep found more than the review listed: `["num","1"]`, `add`, `scale` and a plain `const` gain the `dimensionless` tag, and failed the same way. `Identities.spelled` is the one rule, at the one place every caller goes through (`problem`, `paraphrase`, `bind_report`, `bind_document`).

It calls `ve.units.decimal_exact` and `day_number`, the existing Python lowerings, so a lowered number stays bound to the request's literal and its scale. This is a relation to the request (R8, D1), not a derived value Python answers with: the row returned is Lean's, and where the lowerings differ the answer is refused, never replaced. Only typing the number would have let `150` become `151`. A difference between the lowerings would be `CheckerUnavailable`, and `::test_the_relay_and_lean_agree_at_each_literal` compares them with Lean at the limits and on bad spellings.

**F2: checks no test could fail.** The fuzz now also runs against a service answering every call alike, and exempts only another wording of the same type. `::test_every_check_of_the_relay_is_one_a_test_can_fail` drops each check in turn, enumerated from the module's AST (each conjunct of a `_require`, each statement calling one of the module's binders, each respelling rule), and requires some answer to be treated otherwise, so a new check is covered without being listed. Beyond the review's three instances it found these, each now with an isolating case: the report's own checks hidden behind `report_id`, the outer answer's shape, the not-admitted and no-graph paths, and `premises` and `assumptions` retyped as mappings.

Two product changes came from it. `regions.constants` was untyped, and retyping it as `{}` on a problem with no counted sort was accepted when Lean could not confirm; it is typed now. `type(a) is str and a and a.encode()` became `a.encode()`: the first two conjuncts could never decide anything, as `.encode()` refuses every other JSON value through `MALFORMED`, and an empty line through its falsy result. Refusals are unchanged (`::test_the_relay_s_own_checks_hold_when_lean_cannot_confirm[lines-text]`, `[lines-empty]`).

Probes: F1 raised `CheckerUnavailable` before and prints Lean's line after. F2 exited 1 before (62 passed with the check removed) and exits 0 after (8 failed). Seeded bugs: ten more in `mutants.json`, each planted alone and killed. No Lean or Rust changed, so none is seeded there, and the trust mutants are unaffected. F3 to F6 are on `FOLLOW-UPS.md`, "## qt-a4".

## Size

`git diff --numstat $(git merge-base HEAD main)`, generated files out: 1,306 lines at b24ce6647, as the DRI measured them: product 443, tests 746 (`test_cardinality_answer.py` 456, `test_cardinality_lean.py` 285, `test_route_row_schemas.py` 5), Lean guards 117. Before the fix round it was +992/-20 (product about 420, tests 476); I measured that late, after the second half, and the DRI accepted it twice. The fix round passed that ruling's ~1,050, so it asked again, and `reviews/dri-decisions-20261103-qt-a4-size3.md` accepts up to about 1,350 with no cut, which overrides the earlier two for this item's tests only. Its conditions hold: both test files stay whole and selected, with the fuzz against a service answering alike and the AST-enumerated test, plus the 11-03 conditions.

## Pilot bytes

0 (estimate; nothing claimed before a pilot audit): the constitution's 29 units list the four profiles, refused until qt-a4b. A document under W6a's lists can now carry counts.

## Spec re-read

- Content and report: `docs/spec/quantities.md:744-769` (4.1: environment, statement, "reports carry both ... and bind both", case kinds) against `cardinalityEnv`, `contentOf`, `bind_report`. A unit's `{"cardinality": S}` wrapper is this item's choice: the spec names the statement, not its key beside `ast`, `norm` and `quantity`.
- E2's text: `docs/spec/quantities.md:778` against `::test_lean_s_diagnostics_reach_the_caller_verbatim`.
- "a claimed region table or erased problem must equal the regenerated one": `:766` against `_confirmed`.
- Plan: `docs/spec/quantities-PLAN.md:768-775` against "Plan rows"; `:781-782` against `region-table-skipped`. The plan's "Bytes: 0" holds.
- `VE.Time.Document`'s provenance header (`lean/VE/Time/Document.lean:14-15`) against the asserted-unit bind.

## Self-review against BUILDER-CHECKLIST

1. PASS: `tests/test_cardinality_answer.py::test_every_one_fault_mutant_is_refused_or_changes_nothing` (7, true, null, [], {}, 1.5, a lone surrogate, deep lists, each kind). Not the bad stdout byte: that is the service client's, unchanged.
2. PASS: "Plan rows"; `tools/identity_lint.py`, `tools/relay_lint.py` PASS; the cut is named.
3. PASS: `mutants.json` 33/33 killed; `trust-mutants.json` exit 0, evidence and allow file committed.
4. PASS: `tests/test_cardinality_lean.py`, key order `tests/test_cardinality_answer.py::test_object_key_order_is_no_part_of_an_answer`. No Rust; no Python decision added.
5. PASS: `::test_the_region_table_and_problem_are_bound`, `::test_a_report_s_rows_are_bound_with_and_without_a_matching_id`, `::test_a_renamed_region_is_refused_by_the_relay_itself`.
6. PASS: main merged at f448ffa45; the chain gates the final HEAD. Main has moved since; the train syncs.
7. PASS: DELTA cells cite R1, R8, R16; the size rulings are in "Size"; no signature reserved.
8. PASS: `DELTA.md` rows 1-5, and base behaviour probed at the start (`fields do not match`).
9. PASS: `tools/select_tests.py --base ...` chose units, not all, including both new files; it caught this item's real failures on its first runs.
10. PASS: `tools/check_*_statements.py` rc 0; no theorem added or changed; `ResponseShape.Encoders.Document` rebuilt; the report arm is `copied` (not delivered, row 5).
11. PASS: `max_steps=0` is `None`, never a refutation (`::test_a_found_certificate_is_lean_s_and_an_open_problem_has_none`); 1,000/1,001 nodes; no wall-clock use.
12. N.A. for pilots: no pilot document lists the profile before qt-a4b; the node map is one pass, and `test_cardinality_document_leaves_joined_once` is unchanged.
13. N.A.: no test removed or renamed (`tools/gate_collection.py` runs at the gate).
14. PASS: both directions per check in `tests/test_cardinality_lean.py` and `CardinalityExamples.lean`; "Spec re-read" above; claims name their commands.
