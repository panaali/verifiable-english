# sc-1cb: `ve scope explain` per choice of a reading set governed per choice (SC-1c's cut part). Build report

- **Status:** built; no DRI signature is reserved. DELTA row 1 is SIGNED by the DRI (reviews/dri-decisions-20261101-sc-1cb.md item 1), row 2 cites R16 (K +0, S +0, trusted +0).
- **What changed:** for a document with a reading set governed per choice (scope 11.1) the `scope` mode answers one row group per joint choice, labelled, gated as `governSets` gates it; `ve scope explain` prints each group under its label. Every other answer is main's, byte for byte.
- **Open:** deliverable (4) (spec 2.3's generated-rule row, `explain_generated`, the rule written in full, plan 1.6) is cut to **sc-1cc**, by the size line.
- HEAD: the last commit of `feature/sc-1cb` (base main `3148e87c4`); the full gate is the chain's (not run here).

Branch `feature/sc-1cb`, worktree `/home/seyran/code/ve-sc-1cb`. Read: plan SC-1c (`docs/spec/scope-PLAN.md:725-`), spec 2.3, 5.3, 11;
sc-1c's REPORT and FOLLOW-UPS "## sc-1c"; `lean/VE/Scope/Readings.lean` (sc-5rb). Plan edits of synthesis round 2
(`b2e050be2`, `debates/plan-synthesis-2/edits-scope.md`): none touches SC-1c; this item implements none of them.

## Statement gate

PASS: 5.3 accepted, sc-5r's addendum merged. `uv run python tools/lean_statements.py --check`: "added: 0, removed: 0,
changed: 0, PASS". Against main, `lean/statements.txt` only gains two lemmas (`git diff $(git merge-base HEAD main) --
lean/statements.txt`: 14 `+` lines, 0 `-`): `VE.Scope.explainOut_effect` and `VE.Scope.Run.explainSetsWithin_effect`,
the per-choice twin of sc-1c's `explainWithin_effect`, used only by `runCaseReported_fits`. `explainRows`,
`explainFast_eq`, `explain_bound`, `explainRows_effect`, `explain_rows_iff` keep their text; `explainFast` is now
`(·.2) <$> explainOut D` and `explainFast_eq` is proved unchanged. No new spec statement was added or asked for.

## Deliverables

| Task line | Delivered | Where, checked by |
|---|---|---|
| (1) one group per joint choice, lf-14d's order, at most `choiceLimit`, `explainRows (atChoice D ch)` | yes: `Run.explainSetsWithin` (setChoices, then `explainOut` once per choice's document) | `RunExamples.lean:86-95` (SR-1: wide, narrow; coupled: 4 groups, s03 first; each group equals `explainRows (atChoice D ch)` on SR-1, the coupled sets, SR-dep's admitted form, `[g1, gR]`) |
| (1) labelled by `choiceText` | yes, typed: `choice` is the list of `{unit, set, version, reading}` that `choiceText` writes (`Run.choiceJson`, over `governedSets` read once) | `RunExamples.lean:98` (the picks written in 11.5's form equal `choiceText`, every choice of the coupled sets) |
| (1) a fault under any choice refused with 11.5's text, as `governSets` refuses it; uncovered sets `ScopeReadings` | yes: `faultOf`, then `assemble` (called, never copied) on `explainOut`'s `govern` answers | `RunExamples.lean:107` (same outcome as `governSets` on SR-c, SR-c-nr, SR-g twice, SR-dep, 72 and 65 choices, a second version, SR-u, the coupled sets), `:118` |
| (1) no governed set: today's rows, byte for byte | yes: `Run.answerOf` keeps the old branch | `RunExamples.lean:130` (F-ex); route cases, below |
| (1) evaluated once, summed cells against the stated limit (DRI 2026-10-27) | yes: each choice's document is explained once, its `govern` answer and its rows from one `explainOut` (the gate reads that answer, not a second `govern`); quotes read once; the cells `cellBound D (Σ rows)` refused past `cellLimit` (524,288) as `ResourceLimit` | `RunExamples.lean:123` (112 answers, 111 and 0 UNKNOWN), `:126` (64 choices answered, 64 × 7 × 8 ≤ the limit), `:128` (65 refused) |
| (2) `ResponseShape.Schemas.Scope`, `runCaseReported_fits`, generated `scope.json` | yes: `pick`, `choiceGroup`, a third row alternative; the encoder closes both branches | `lake build`; `tools/response_schemas.py --write`, `regen_generated.py --write` |
| (2) relay binds each label and every unit and governor id (R8); CLI prints each group under its label | yes: `ve/scope.py` `choices_problem` (each pick a set of the request by id and version, its unit, one of its readings; every group the same sets, in the document's order, once; the groups every choice once in lf-14d's order), each group's rows by `rows_problem` (sc-1c's checks, unchanged); `lines` | `test_each_choices_rows_are_shown_under_its_label`; `ve/__main__.py` needed no change (the display is `ve/scope.py`'s) |
| (3) route cases | 6: `sets-u0165-s03` (the hard-constraint part document F1 with u0165.s03's set), `sets-two-coupled`, `sets-64`, `refused-sets-choice-fault`, `refused-sets-65`, `refused-sets-uncovered` | `test_a_set_governed_per_choice_is_explained_per_choice_and_every_other_answer_is_mains` (also: the 12 earlier cases equal main's saved answers) |
| (3) fuzz | yes: the structural mutants and sc-1c's rebound mutants per group, plus each label's picks reversed, relabelled as the next group's, reading/set out of range, version moved, unit rebound, one pick over every pick, two groups' labels swapped, groups reversed, on `sets` and `coupled` | `test_every_mutant_of_a_genuine_answer_is_refused_or_changes_nothing_shown[sets,coupled]`; `test_every_binding_check_has_a_mutant_only_it_refuses` (now runs the whole weakened module, so helpers' checks are deleted too) |
| (4) generated-rule row, rule in full | **not delivered: sc-1cc** (size) | — |

Deviations: (a) the wire carries the label typed (`choiceText`'s picks), not its text, so the relay binds each id; the
display writes it in 11.5's form. (b) `governedSetUnits` is evaluated a constant number of times per request (the
branch, `setChoices`, `atChoiceOn`'s argument once, `assemble`), never per choice; `setChoices` and `assemble` are
Readings.lean's, which this item may not edit. (c) The relay checks the groups are the product of the named sets
(a count binding); which sets are governed and a coordinated rewrite of every label is Lean's (as sc-1c's
`explain_rows_iff`).

## Evidence

- Base and HEAD side by side: main's answers to all 17 route cases (12 earlier, 5 new) were recorded before any change
  (`tests/data/scope/explain-main-answers.jsonl`, through main's relay and Lean); main refuses all 5 new ones with
  `ScopeReadings: u0165.s03`. On HEAD the 12 are equal and the new ones answer as DELTA row 1 lists (probe and test above).
- Tests run on the final relay and Lean: `tests/test_scope_answer.py` all 20 (14 + 5 + 1 passed, the deletion test
  339 s); `tests/test_route_row_schemas.py -k "corpus_reaches or genuine_route or dropped_retyped or mutations_agree or
  no_answer_object"` 5 passed; `tests/test_assurance_manifest.py` 139 passed.
- Selected tests (`mac-pytest.sh --select`, 422 of 521 units): the fast stage ran 10,073: 1 failed,
  `test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` (RunExamples.lean newly reads JSON);
  fixed in the manifest and rerun alone: 1 passed. The heavy shards were not waited for (the runner stops at the first answer).
- `lake build` (1214 jobs) and `python3 lean/audit.py` PASS (7916 theorems); `regen_generated.py --write` (35 entries).

## Seeded bugs

[mutants.json](mutants.json): 13, each planted alone, the named check run, restored; all killed.
- **Lean (9):** L1 one choice's rows dropped and L2 two choices' labels swapped (`RunExamples.lean:86`), L3 one
  choice's cells for the sum (`:123`), L4 the no-set path through the choice loop (`:130`), L5 the gate fed the
  document for `govern`'s answer (`:107`, SR-dep), L6 the fault under one choice skipped (`:107`, SR-c), L7 the label's
  next reading (`:98`), L8 `pick.version` typed as text (through the regenerated `scope.json`: the route-case test
  raises `CheckerUnavailable ... version: expected string`), L9 `choiceGroup` without `governed` (`runCaseReported_fits`).
- **Python (4):** P1 a label's unit unbound (fuzz `[sets]`), P2 the groups shown reversed (display test), P3 the
  product check deleted (fuzz `[coupled]`), P4 a group's rows unbound (fuzz `[sets]`).
- Every new definition is mutated: `explainOut` L5, `explainSetsWithin` L1-L3, L6, `answerOf` L4, `choiceJson` L7,
  `pick` L8, `choiceGroup` L9, `choices_problem` P1, P3, P4, `lines` P2. `trust-mutants.json`: 0 trusted definitions.

## Trust

`uv run python tools/trust_map.py --check`: "against 3148e87c47dc: K +0, S +0, D +9, G +42, tied +0, unclassified +0,
trusted +0 … PASS". Classes follow sc-1c's twins (DELTA row 2); no `--allow` was needed. FOLLOW-UPS.md "## sc-1cb"
asks for the ties pass (a theorem that `explainSetsWithin` refuses exactly when `governSetsWith governFast` does).

## Pilot bytes

0 claimed (the reader's view). The constitution pilot's `ve scope explain` refusal `ScopeReadings: u0165.s03` should
become two groups of the seven hard-constraint rows; the pilot re-runs explain on its own.

## Spec re-read

- 11.1's governed sets against `lean/VE/Scope/Readings.lean:33` (`governedSetUnits`, called): the branch and `atChoiceOn`.
- 11.5's texts against `docs/spec/scope.md:2150-2160`: `ScopeChoice`, `<fault>`, `ResourceLimit: scope choices`, `differs between choices`, all from `faultOf`/`assemble`/`setChoices`, unchanged.
- The label against `Readings.lean:86` (`choiceText`): unit, then `set@version:reading`, joined by `, `, in `governedSets`' order.
- 5.3's rows and `cellBound` against `lean/VE/Scope/Run.lean` (unchanged statements); the DRI's conditions (a)-(e) against reviews/dri-decisions-20261101-sc-1cb.md: each cited in DELTA row 1.

## Next

dr-sc-readingset-ids (scope@0 in a multi-part document, governors over reading sets), then SC-E2 on this route.

## Self-review against BUILDER-CHECKLIST

1. PASS: every field of a choice answer dropped, emptied, duplicated, retyped (`_structural_mutants`' values) → refused or nothing shown changes (`test_every_mutant…[sets,coupled]`).
2. PASS: deliverables table above; (4) cut to sc-1cc by the size line (task: "cutting at the size line"); no Python copy of a Lean decision (the relay binds only).
3. PASS: 13 seeded bugs killed (`mutants.json`); `trust_mutants` run per 13a (`trust-mutants.json`, exit 0, 0 trusted definitions).
4. PASS: base and HEAD side by side on all 17 route cases (`explain-main-answers.jsonl`, the route-case test).
5. PASS: labels refuse an undeclared set (`scope-x`), reading (`r9999`), moved version, rebound unit, duplicated and dropped groups and picks (fuzz `[sets,coupled]`).
6. PASS: main has not moved (`git log HEAD..main`: 0); the gate is the chain's on the final HEAD.
7. PASS: DELTA row 1 SIGNED by the DRI's decision file, row 2 R16.
8. PASS: DELTA row 1 lists every changed answer; the other 12 route cases are byte-identical (the route-case test).
9. PASS: `tools/select_tests.py --base …` selects `test_scope_answer.py`, `test_route_row_schemas.py`, `test_lean_service.py`, `test_scope_readings_document.py`.
10. PASS: the encoder theorem breaks when the shape loses `governed` (L9); the new lemmas are about the returned value.
11. PASS: limit 0 and 111 are `ResourceLimit` (UNKNOWN), 65 choices `ResourceLimit: scope choices` (`RunExamples.lean:123`, `:128`).
12. PASS: one `explainOut` per choice (the gate reuses its `govern` answer), at most 64; no timing test added.
13. N.A.: no test removed or renamed.
14. PASS: both directions: 64 answered / 65 refused, 112 / 111, no set / sets, admitted / refused per fixture (`:107`); claims cite commands above.
