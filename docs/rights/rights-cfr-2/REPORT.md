# rights-cfr-2 (also row rights-cfr-3): REPORT

**Status:** both rows are delivered on branch feature/rights-cfr-2. HEAD is the commit that adds this file. No DRI signature is reserved.
**What changed:** a CONFLICT-FREE rights-conflict answer now gives every report part of rights.md 7.3: the labels, the weighing points, and the exhibited situation or UNKNOWN with its budget. `UnlicensedLimitation` and `ProtectedInCone` findings now carry their line's span, and the report shows it beside the text. Python only types and binds the new fields (R8).
**Open:** the full gate (the chain runs it on the final HEAD) and the R16 ties pass (FOLLOW-UPS "## rights-cfr-2").
**Size:** above the ~600 line. The DRI accepted it up to ~850 hand-written lines (reviews/dri-decisions-20261110-rights-cfr-2-size.md).

## Rows delivered

| Row / deliverable | Where | Test |
|---|---|---|
| rights-cfr-2 (1): the CONFLICT-FREE answer gives 7.3's parts in the spec's words. The first sentence is kept byte for byte, and every existing field is kept. | `Run.lean` `conflictAnswerOf` (verdict, first failure and premise use as arguments), `conflictAnswer`, `exhibit`, `situationTables`, `conflictBudget` | `test_rights_conflict_free_report_evidence` |
| rights-cfr-3 (2): both finding kinds carry the span of the source line, from the located lines. The report shows it beside the text, and the text field is kept. | `Tree.lean` `RightsDoc.located`; `Scope.lean` `lineSpan`, `limitationScope`; `Distinction.lean` `noDistinction`; `Run.lean` `locate`, `findingJson`, `located_findings` | `test_rights_findings_preserve_source_spans` |
| (3) Both named tests fail on main | see "Failing on main" | |
| (4) Python relays and binds only (R8): typed schema; each span is a unit of the request's `located`, bound to the line's unit | `ve/rights_route.py` `_located_rules`, `_bind_findings`, `_bind_conflict`, `report_rights(located=)`; `ve/document/report.py` | `tests/test_rights_report_parts.py` (62 tests) |

A span is a source unit id, as W2 `reason_spans` are (rights.md 3.2 :389, 3.3 :409). The relay sends `located` (one id per unit after `source_units`); a request without it gets null spans. `limitationScope_texts` and `noDistinction_texts` prove that locating moves only the spans. So the scope answer's `findings` and `licensed` are the replay's, and `rights_wire_scope_sound` covers them.

Readings of 7.3 to note:
- `<j> weighing points open` counts the colliding default pairs that no ranking resolves (`openCoherence`, soft-norms 6.2 WP(T) with no pair classified). This case takes no pair evidence. The soft route writes j = |conditional_on| instead, so the two routes can give different counts for one document, and a line can read "0 coherence premises ...; 2 weighing points open".
- `UNKNOWN (budget 10000)` means the request supplied no situation for Lean to check. No situation search runs on this route (`conflictBudget` docstring).
- `situation` shows the checked model's decision and rights-generated tables. The rest of the situation is the request's own model, which Lean checked whole (`backgroundValidR`).
- An invalid `situation` is refused even when the verdict is UNKNOWN. This is input validation, the same as the projections model.

## Failing on main (before the fix)

Command: `uv run pytest -q tests/test_rights_report_parts.py -k 'test_rights_conflict_free_report_evidence or test_rights_findings_preserve_source_spans'`, run in a worktree of 33fe04615 with its shared Lean build and this branch's test file. Result: `2 failed`. The first fails with `KeyError: 'weighing_points'`. The second fails with `TypeError: report_rights() got an unexpected keyword argument 'located'`. On HEAD both pass (`64 passed`, the whole file).

## Seeded bugs (each restored; one per claimed behaviour and language)

| # | Lang | File | Mutant | Failing test (output) |
|---|---|---|---|---|
| S1 | Lean | lean/VE/Rights/Run.lean | the situation dropped: `return conflictAnswer id res none` | `test_rights_conflict_free_report_evidence`: `CheckerUnavailable: Lean rights conflict is not bound to the request: unbound conflict status text or report part` |
| S1b | Lean | lean/VE/Rights/Run.lean | one-character break of the 7.3 line, `weighing points` -> `weighing point` (the DRI-signed row's negative test) | `test_rights_conflict_free_report_evidence`: `AssertionError ... - hing points open ... + hing point open` at the raw ve_service comparison with the spec |
| S2 | Lean | lean/VE/Rights/Distinction.lean | `ProtectedInCone`'s span back to `""` (`lineSpan { D with located := [] } hit.1`, so the build still passes) | `test_rights_findings_preserve_source_spans`: `CheckerUnavailable: Lean rights elaboration is not bound to the request: unbound finding or finding span` |
| S3 | Python | ve/rights_route.py | the relay drops each span (`finding["span"] = None` after `decide_once`), which the R8 binding check refuses | `test_rights_findings_preserve_source_spans`: same `unbound finding or finding span` |
| S4 | Python | ve/rights_route.py | `_bind_conflict` no longer binds `weighing_points` | `test_a_mutated_conflict_report_part_is_refused[weighing point added/dropped/renamed]`: `3 failed` |

Each mutant ran against a ve_service built from it and pinned in a scratch lock (`VE_NATIVE_PREBUILT=1`). The committed lock pins only the final build.

## Trust (R16)

`uv run python tools/trust_map.py --check` against 33fe04615107 passes: K +0, S +3 (`Tree.lean` `RightsDoc.located`), V +83 (`Run.lean` +50, `Schemas/Rights.lean` +33), trusted +86, all under 150. Recorded with `--allow` as "SIGNED by standing ruling R16 (DRI-RULINGS.md), rights-cfr-2, 2026-11-09" (two records, +78 then +5, in docs/trust-baseline.json). The FOLLOW-UPS row asks for the ties pass. `lineSpan` is G[I] and `locate` is D[I] (span provenance). The checks in `ResponseShape/Schemas/RightsChecks.lean` are T.

The trust_mutants sweep is in docs/rights/rights-cfr-2/trust-mutants.json (`mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/ResponseShape/Schemas/RightsChecks.lean --rescore ...`), with its allow file trust-mutants-allow.json. Result: exit 0 on ve-cloud-3. It ran 451 mutants over 13 definitions: 404 KILLED, 20 INVALID, 27 ALLOWED, 0 SURVIVOR and 0 UNKNOWN. The 10 allow lines cover 4 (definition, operator) pairs whose survivors are equivalent and 6 whose mutants do not type-check (two `regenerated` mutants that a check refutes are UNKNOWN only because they also break `elaborate_fits`). mutants.json lists the seeded bugs and one killed mutant per definition, with the check that kills it. The kills come from RightsChecks.lean: the located findings, three conflict answers and a premise-use variant, each pinned exactly; each genuine answer is accepted by rights.json, and every variant with a member added, dropped or retyped (`DefaultsExamples.variants`) is refused, along with each branch's negatives.

## Notes

- `runRightsKind_packages` (an encoder theorem from fu-rd9-checks, not a spec statement) now also states the four CONFLICT-FREE fields. `conflictAnswer_fits` is added. `conflictAnswer` is locally irreducible in `runRightsKind_fits`, so the other alternatives do not unfold it.
- `lean/VE/Readings/Wire.lean` and `lean/VE/Rights/Wire.lean` each get `, []` for the new field in their anonymous `RightsDoc` constructors (nothing else changes). Their whole-file pins in ve/assurance-manifest.json are re-pinned after review (same line counts). The new check module is listed under `other_json`.
- In-flight overlap: feature/qt-a4b also edits ve/document/report.py, in other hunks (:199, :451; mine are :116-176 and :349).
- The status-line binding in Python keeps the wording, as it did before this item. The relay binding inventory classifies `status_text` BOUND, which needs this.
- Size, from `git diff --numstat` without generated files and evidence JSON: 709 hand-written lines added and 74 deleted before this REPORT (89 lines) and DELTA (12 lines), so about 810 in all, within the DRI's ~850. Lean checks are 76 lines, within the ruling's 150, and product code (Lean outside the checks, plus ve/) is about 255, within its ~350.
- Pilot bytes expected to move: 0 (report content only; no unit status or verdict changes). This is an estimate.
- Next item: none on these files.

## Spec re-read

- The CONFLICT-FREE line, against docs/spec/rights.md:766-767 (`[, under couplings <ids>]` is left out: no couplings here).
- The exhibited situation or UNKNOWN with the budget, against rights.md:697-698 and soft-norms.md:577.
- A finding's span, against rights.md:799-800 ("Findings are report lines with the line's span") and 3.2 :389.
- The R8 binding, against DRI-RULINGS.md R8: each span names a unit of the request's `located`; each row is bound to its finding; no row is empty or extra.

## Tests run

- New and touched files: tests/test_rights_report_parts.py, test_rights_lean.py, test_rights_licence_relay.py, test_rd9_followup_bindings.py, test_rights.py, and test_relay_binding_inventory.py -k rights. All pass, except the stale-inventory test before the regen, which passes after it.
- `lake build` passes (1342 jobs). `python3 lean/audit.py` gives PASS (810 files, 9084 theorems).
- Selected tests (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base 33fe04615 --run` at 3b397f4b6+pins, clean tree; it ran on ve-cloud-2): 465 units, one failure. `tests/test_shape_binding_mutants.py::test_the_generic_checker_gives_every_mutant_the_verdict_its_shape_decides[rights]` replays recorded answers, which lacked `located_findings` (`Invalid: ... missing field located_findings`). The fix was `uv run python tools/binding_census.py --answers` (596 answers re-asked of this build) and the binding-census regen. The failed id plus tests/test_binding_census.py were then rerun on ve-mac-1 at 9667237e: `9 passed`, exit 0.
- `uv run python tools/regen_generated.py --check`: 38 entries checked, rc 0. `tools/gate_collection.py --check --prebuilt`: 64 added, 0 refused, 0 stale, 0 malformed.
- Not run: the full gate (the chain runs it).

## Self-review against BUILDER-CHECKLIST

1. PASS. Every Lean answer is typed and contained: `test_a_mutated_finding_span_is_refused` (7, true, [], {}, "", dropped), `test_a_mutated_conflict_report_part_is_refused`, and RightsChecks `refusesAll`.
2. PASS. Every deliverable is in "Rows delivered" with its test. No Python copy of a Lean decision: the binding recomputes ids and counts only.
3. PASS. Seeded bugs S1-S4 and S1b, and the trust_mutants evidence.
4. PASS. Old inputs give the same answers: the existing rights tests pass, and a request without `located` or `situation` changes only as DELTA rows 1-4 say.
5. PASS. A span naming an absent unit, a shifted span, an extra, duplicated or dropped row, and an emptied list are all refused: `test_a_mutated_finding_row_is_refused`, `test_a_span_where_no_line_is_located_is_refused`.
6. PASS. The commit list comes from `git log main..HEAD --no-merges`, and the merge base is 33fe04615.
7. PASS. DELTA rows cite R3, or the DRI decision with its condition test and negative test.
8. PASS. DELTA rows 1-4 cover the status line, the new fields, the refusals and the report keys.
9. PASS. `tools/select_tests.py` selects tests/test_rights_report_parts.py.
10. PASS. Encoder theorems: S1b and S2 show the statements are about the returned value; `limitationScope_texts` and `noDistinction_texts` are proved.
11. PASS. `located`'s length is compared before its items are decoded (`test_lean_refuses_located_lines_the_request_does_not_have`). There is no new budget input.
12. N.A. No new search or enumeration: the new outputs are list maps over the existing elaboration.
13. N.A. No test removed or renamed.
14. PASS. Each new check is tested both ways (genuine accepted, mutants refused), and each claim names its command.
15. PASS. No overclaim (UNKNOWN means none supplied; `j` reading stated); no silent cut (size asked of the DRI); every new check can fail (S1-S4); `located` is length-checked before it is decoded.

SELF-REVIEW: 0 A, 2 B, 11 C; fixed 10
