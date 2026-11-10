# sa-checked-view: build report

No DRI signature is reserved. There is no DELTA row: no answer changes (`checkDocSetsView_answer`).

## What it delivers

The typed checked-document view of spec 5.1 ("The checked view", docs/spec/purpose-explanation.md lines 770-822).
It lives in a new module, `lean/VE/Service/DocumentView.lean` (namespace `VE.Service.Document`, imports
`VE.Service.Document`).

| Plan / task row | Delivered by |
|---|---|
| (1) `CheckedView`, `checkDocSetsView` (one run, two outputs) | `DocumentView.lean` `CheckedView`, `checkDocSetsView`. It reads one typed run (`checkedRun`). The answer is the fold's JSON and the view is `viewOf` over the same `Checked` and the folded rows. |
| (1) `checkDocSets` is its first component | by theorem: `checkDocSetsView_answer : (checkDocSetsView j).map (·.1) = checkDocSets j` |
| (1) `activeKinds` | `DocumentView.lean` `activeKinds` |
| (1) `checkDocSetsView_rows` | proved (rows after the governor fold: `foldGovernors_rows`, `foldedRows`, `readStatus`) |
| (2) `checkDocSetsView_candidates` | proved (`unitSets`, `firstPerUnit_nodup`, `unique_key`) |
| (3) `checkDocSetsView_readings` (PE-R8) | proved |
| (3) `checkDocSetsView_packs` (PE-R11) | proved: `packSources = []` on a list with no pack. On a list with a pack, `packSources` stays empty. `packSources_complete` is that pack's owner's obligation (the paragraph after 5.1's block), not this item's. |
| Equality test through the service | `tests/test_sa_checked_view.py::test_the_view_first_component_is_check_doc_sets_byte_for_byte_and_the_services`. It covers 5 fixtures: plain, `scope@0` with a governed set, two versions of a set, a request refused by scope, and one refused by the check. Each is run by `view_bytes.lean` and by the service. |
| Statement gate | `docs/document-model/sa-checked-view/spec_text_check.py`: 8 of 8 statements are found. Each equals the spec's text after whitespace normalisation, followed by ` :=`. The test `test_the_eight_statements_equal_the_spec_and_a_changed_one_fails` shows that a changed statement fails. |

All five theorems are proved with no `sorry`. `python3 lean/audit.py` reports PASS: 825 source files, 9314 theorems,
and only the standard axiom allowlist.

**Statement gate finding.** The plan's change log (docs/spec/purpose-explanation-PLAN.md lines 21-24, "pe-rev, DRI
2026-11-02 fp-purpose-explanation item 1") says pe-rev applied PE-R6 to PE-R11. That includes the changed PE-2
statements (PE-R8 `readings`, PE-R11 `packSources`). The spec carries them as written. 5.1 on main is that reviewed
text, and every statement here equals it. No statement had to change.

**Document.lean edits** (task regions `checkCore` and `checkDocSets`; 4 lines added and 1 changed):
- `Checked` gets one field: `active : List (FrontSet × List Bool) := []`. It holds the active reading sets that
  the status fold read (`Loader.activeOf`).
- `check` stores that `active` value. The view reads the sets from that one evaluation rather than calling
  `activeOf` a second time.
- `checkCore` and `checkDocSets` are unchanged. The typed mirrors (`checkBodyChecked`, `checkCoreChecked`) are in
  `DocumentView.lean`, tied to them by `checkBodyChecked_encode` and `checkCoreChecked_encode`.

**Assurance manifest** (`ve/assurance-manifest.json`, `docs/spec/assurance-manifest.md` via
`tools/assurance_manifest.py --write`):
- Document.lean's whole-file decoder pin was reviewed and re-pinned: 2896 lines, `total_lines` 44268. The 3 added
  lines are a `Checked` field and its store, not a decoder change.
- `DocumentView.lean` is classified under `other_json`. Its typed mirrors read only `checkBody`'s request fields, and
  they are tied to it by `checkBodyChecked_encode`.
- In the selected run, the three `test_assurance_manifest.py` failures came from these two pins.

**Trust table.** `tools/trust-classes.json` classifies the 12 new definitions of `DocumentView.lean` as untied G[V], as `checkBody`, `checkCore` and `checkDocSets` are. They still count as trusted (+97), and the ties are the FOLLOW-UPS row's pass. `tests/test_scope_lean.py` drops `VE.Scope.statusOf` from its list of scope definitions that no theorem states, because `statusOf_known` now states it.

**Overlap.** The merge note says qt-a4b edits `Checked` in the same file. This item adds a field at the structure's
end, and the merge note's rebase-second rule applies to whichever branch merges second. Neither branch was present
locally at the time of writing.

## Seeded bugs (Lean; no Python or Rust product code changed)

All are in docs/document-model/sa-checked-view/mutants.json (file, definition, mutant, test). Each was planted, the
named test failed, and the file was restored.

| Seeded bug | File | Failing test |
|---|---|---|
| view rows taken before the governor fold | lean/VE/Service/DocumentView.lean (`checkDocSetsView`) | `checkDocSetsView_rows` |
| `activeKinds` read from a different active-set function (open sets only) | lean/VE/Service/DocumentView.lean (`activeKinds`) | `checkDocSetsView_candidates` |
| `readings` in a different order from `candidates` | lean/VE/Service/DocumentView.lean (`viewOf`) | `checkDocSetsView_readings` |
| `packSources` filled on a list with no pack | lean/VE/Service/DocumentView.lean (`viewOf`) | `checkDocSetsView_packs` |
| `Checked.active` stores every set, not the active ones | lean/VE/Service/Document.lean (`check`) | `tests/test_sa_checked_view.py::test_candidates_and_readings_name_the_active_set_in_order` |

There are 10 more mutants, at least one in each new trusted definition. They are all listed in mutants.json, and all
are killed.

## Trust (R16)

`tools/trust_map.py --check` against c94ad399b reports: K +0, S +0, trusted +100
(`VE/Service/DocumentView.lean` +97, `VE/Service/Document.lean` +3). That is within R16's cap of 150. The allowance is
in docs/trust-baseline.json, signed "SIGNED by standing ruling R16". The FOLLOW-UPS.md row under
"## sa-checked-view (2026-11-10)" asks for the ties pass.

Trust-mutant sweep (`docs/document-model/sa-checked-view/trust-mutants.json`, a rescore at 393a2869c over the test
file `view_guards.lean`): 109 killed, 0 survivors, 0 unknown, 31 invalid, and 39 allowed. Each allowed mutant has its
reason in `trust-mutants-allow.json`. After the sweep, main was merged (d093894f9). The merge changed no file in
`VE.Service.DocumentView`'s import closure (386 modules, checked), so the record was not rerun.

## Size

About 750 hand-written lines (`DocumentView.lean` 397, the test 139, the evidence `.lean` files 109,
`spec_text_check.py` 51, mutants and allow 39, plus a few others). That is over the ~600 guide. The extra comes from
the helper lemmas in the governor-fold proof of `checkDocSetsView_rows` and from the guard file that kills the sweep's
survivors. Every row in the task was required, so none was cut.

## Pilot bytes

An estimate of 0: the answer is unchanged by theorem. Nothing is claimed before a pilot audit.

## Next item

sa-wire-purposes0 (if not merged), then pe-2 (the purposes block in the document mode, which reads this view).
lm1 (ve-limits) also reads it.

SELF-REVIEW: the self-reviewer ran in this build's earlier session, and its findings were fixed in 4fba99718. The
count line it returned was not kept with the work.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A. There is no new relayed field or route; the document mode's answer is
   unchanged (`checkDocSetsView_answer`).
2. Deliverables and rules: PASS. The table above maps each row to its test. There is no Python copy of a Lean decision
   and no permanent report test.
3. Tests can fail: PASS. See mutants.json (14 mutants, all killed) and the sweep (0 survivors).
4. Python, Lean and Rust agree: PASS. `test_the_view_first_component_is_check_doc_sets_byte_for_byte_and_the_services`
   checks the fixture answers against the service's.
5. R8 binding: N.A. Python reads no new field.
6. Gate evidence matches HEAD: PASS. main was synced (d093894f9), generated files were regenerated, and the gate runs
   on the final HEAD in the chain.
7. No unsigned item: PASS. The R16 allowance is signed; there are no DELTA rows.
8. Every user-visible change in DELTA: PASS. There is none (theorem `checkDocSetsView_answer`, plus the byte equality
   test).
9. Test selection: PASS. `tools/select_tests.py` selects `tests/test_sa_checked_view.py`.
10. Statements say what is claimed: PASS. `spec_text_check.py` and
    `test_the_eight_statements_equal_the_spec_and_a_changed_one_fails`. The seeded mutants break the theorems' builds.
11. Budgets and deadlines: N.A. There is no new mode or evaluator; the view reads the one `checkedRun`.
12. CPU and memory: N.A. There is one run with two outputs, and `active` is the value the fold already computed.
