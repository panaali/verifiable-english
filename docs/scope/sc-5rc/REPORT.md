# sc-5rc build and review-fix report

**STOP: DRI signatures for DELTA rows 2 and 3 and the external F2 R16 ties-pass registration are still required.** The sandbox cannot write `/home/seyran/code/manage-agents/FOLLOW-UPS.md` or its DRI inbox.
Status: F1's cited composed readings are encoded, bound, checked and rendered. F2's tracker entry is prepared below; its probe remains blocked on the external write. The four `Pinned.JsonWF` proofs remain assigned to sc-5rd pending sc-1af.
Checks: the F1 probe and 10 targeted regressions pass; the Lean build and audit pass. The selected run is pending. No full gate was run, per this fix task.

## Review fixes (2026-10-29)

F1: `composedReadingRow` decodes the norm member and relays `cites` from the governed reading. The response shape permits the optional citation member, its encoder theorem covers both branches, and Python binds the whole citation value to the authored reading. One `norm_rule_input` projection supplies norm-only content to the lower checkers while the reading keeps citations for display. `test_f1_composed_reading_preserves_authored_cites` covers frame, reguard and carve-out with empty and populated citations in answer, load, check and render; `test_f1_composed_cites_are_bound_to_authored_reading` rejects dropped, added, changed and retyped citations. The original F1 probe now passes. A seeded Python bug that passed citations to the lower checker failed all six citation-view cases; a seeded Lean bug that dropped citations failed the `composedReadingRow` guard. Both were restored.

F2: the required global registration is not present and the original probe still fails. It cannot be a repository regression test: the tracker is outside the checkout and hermetic tests cannot depend on that mutable external file. The exact entry to add to `/home/seyran/code/manage-agents/FOLLOW-UPS.md` is:

```text
## sc-5rc (2026-10-29)
- R16 ties pass: tie the +36 D[V] lines in lean/VE/Service/Document.lean and +21 G[V] lines in lean/ResponseShape/Schemas/Document.lean to the existing render, wire and encoder theorems; retain tests that can fail for each new trusted definition. Owner: scope ties pass.
```

The current trust measurement is K +0, S +0, V +57 against `314b23a42c21`; its existing signed allowances total +50, leaving +7 to record after the F2 entry meets R16's condition. This report does not claim that the missing registration is signed.

## Initial build record

The original `sc-5rc` build ended at `c7016b755`; its initial report follows. Its test and trust counts describe that commit, before the review fixes above. DELTA rows 2 and 3 still require the DRI's decision.

## Scope and plan rows

The sc-5r statement review and its recheck ended MERGE (`manage-agents/sc-5r-looprecheck1.final.md`). The proposed statements remain those in `docs/spec/scope/SpecStubs_sc5r.lean`; no approved statement was changed here. I read the pinned SC-5 plan, scope spec 1.7, 5.7 and 11.7, the two sc-5rb DRI decisions, the sc-1af amendment, sc-5rb's report, SYNTHESIS 4.2/4.3 and the phase-2 decisions. No `feature/jt-2c` branch was present locally. This item is restricted to part documents, including F1's u0165.s03 set built by the test.

| Task row | Result | Check |
|---|---|---|
| (1) Four `Pinned.JsonWF` proofs | **sc-5rd.** sc-1af's `jsonWF?_sound` and boundary check are not on main. The DRI requires deriving `JsonWF` from that check, not a bare hypothesis; proving the statements before that merge would violate the condition. | `git log main` and sc-1af decision item 1 |
| (2) Composed readings in the document answer, schema and encoder theorem | Added `composed_readings`, typed through `ResponseShape.Schemas.Document`, produced in Lean by `checkDocSetsAnswered`, and covered by `checkDocSetsAnswered_fits`/`runCaseReported_fits`. The preexisting `checkDocSets_fits` and `scope_admission_sets` statement remain intact. | `lake build VE.Service.ScopeExamples`; `python3 lean/audit.py`; `test_render_shows_a_set_composed_per_choice_naming_its_unit` |
| (3) Relay, binding and render | The relay requires exactly the governed sets, set ids, versions, units and reading ids in the request and replaces authored content only with Lean's encoded reading. Render shows the bound reading. | `test_f1_the_composed_sets_are_bound_to_the_request`; `test_render_shows_a_set_composed_per_choice_naming_its_unit`; `test_render_keeps_an_unrelated_set_as_authored` |
| (4) sc-5rb unavailable rows become answers | The part document renders; F1's `carve_out` and `reguard` rules answer in every view. The two availability changes await DELTA signatures. | `test_render_shows_a_set_composed_per_choice_naming_its_unit`; `test_f1_a_composed_set_of_rules_in_full_answers_every_view` |
| (5) Seeded bugs and R16 mutants | Three Python behavior mutants and a Lean sign mutant were planted separately, failed their named test or guard, and were restored. The R16 mutation run killed 125 mutants and allowed 3 equivalents, with no survivors or unknowns. | `mutants.json`, `trust-mutants.json`, `trust-mutants-allow.json` |

Encoder naming deviation: the established `checkDocSets_fits` proves the unchanged `checkDocSets` value, which the approved `scope_admission_sets` statement names. The route now returns `checkDocSetsAnswered`; its new `checkDocSetsAnswered_fits` and `runCaseReported_fits` prove the actual returned value. This preserves the approved statement while extending the route's encoder proof.

## Seeded bugs

| File | Mutant | Failing check |
|---|---|---|
| `ve/document/lean.py` | Ignore a supplied set version. | `test_f1_the_composed_sets_are_bound_to_the_request[version-2]` refused to raise `CheckerUnavailable`. |
| `ve/document/lean.py` | Keep the authored rule instead of relaying Lean's composed rule. | `test_f1_a_composed_set_of_rules_in_full_answers_every_view[carve_out]` observed the written rule instead of the composed rule. |
| `ve/document/render.py` | Render only governed sets, dropping an unrelated set. | `test_render_keeps_an_unrelated_set_as_authored` counted one reading instead of two. |
| `lean/VE/Service/Document.lean` | Flip the canonical norm sign in `composedReadingRow`. | `lake build VE.Service.Document` failed the true/false `#guard`. |

No Rust product code changed. The three old unavailable tests were renamed to answer tests; the commit carries `Test-removed:` trailers. The structural response fuzz test retypes nested fields and the identity test rebinds set/version/unit/reading ids, extra rows and missing readings. Both accepting and refusing fixtures cover the new field and the ungoverned boundary.

CLI probe: `.venv/bin/python -m ve document render` on the small part document exited 0 and printed one `One reading is:` and one `Another reading is:`.

## Trust, size and evidence

R16 allowance: K +0, S +0, V +50 (`VE/Service/Document.lean` +31, `ResponseShape/Schemas/Document.lean` +19), below the +150 cap. `tools/trust_map.py --allow` recorded the standing ruling; the requested ties pass belongs in FOLLOW-UPS.md, but that file is outside this sandbox's writable roots. The pilot's expected u0164.s02 movement is **+22 B**, an estimate only; no pilot audit or whole-constitution run was made. The next item is the pilot hard-constraint rewrite after DRI AT3's audit; SC-2 is adjacent at rank 107.

Size: about 500 hand-written added or deleted lines against main, counting product code, tests, the assurance pin, this report, DELTA, mutants and the allow file; generated files are excluded. No whole-constitution or pilot check was run. A small part document's service answer took 0.214 s wall in a local probe; this is an observation, not a timing assertion.

`trust_mutants` on ve-mac-1, with `--test lean/VE/Service/ScopeExamples.lean` and `--rescore` against the initial evidence, ran all 128 mutants: **125 KILLED, 3 ALLOWED, 0 SURVIVOR, 0 UNKNOWN, 0 NOT RUN**. The three allowed replacements change only the emptiness test of `governedSetUnits`: `take 1` and `reverse.take 1` preserve emptiness, while `[]` does not elaborate without an element type. The singleton and two-set guards catch `drop 1` and `dropLast` respectively. `trust-mutants.json` and `trust-mutants-allow.json` record the full run and reasons; `trust-mutants-initial.json` preserves the first run's surviving mutants (named `trust-mutants.json` when `--rescore` ran). The passing run rescored all 128 mutants, reusing none.

The selected run covered 401 units on ve-mac-1. The changed scope document file passed. Three `tests/test_assurance_manifest.py` IDs failed because the manifest still pinned Document.lean at 2016 lines and its old digest. I reviewed and updated its whole-file pin to 2069 lines and `c4047790…`, added the four decoder declarations, and regenerated the assurance document. The required retry of only those three IDs passed (3/3); `tools/assurance_manifest.py --check` passed. `tools/gate_collection.py --check --prebuilt` reported 4 removed test IDs covered by trailers, 0 refused, 0 stale and 0 malformed. The full release gate was not run by this worker.

The pre-review check at `0a67f5697`, with a writable uv cache, passed clean-tree, commits, seeded-mutant and relay-mutation checks. It reported two remaining stops: the final-HEAD full gate is assigned to the chain, and DELTA rows 2–3 need a DRI signature.

## Self-review against BUILDER-CHECKLIST

1. PASS — `test_every_structural_mutant_of_the_sr1_answer_is_refused`, `test_f1_the_composed_sets_are_bound_to_the_request`.
2. PASS — plan table above, `git diff --stat`, statement gate and no copied Python composition.
3. PASS — seeded bugs above and `trust-mutants.json` (125 killed, 3 allowed, 0 survivors).
4. PASS — `test_f1_a_composed_set_of_rules_in_full_answers_every_view` and existing sc-5rb fixtures.
5. PASS — `test_f1_the_composed_sets_are_bound_to_the_request` and structural mutants.
6. N.A. — the user directed the chain to run the final-HEAD full gate after this build.
7. N.A. — DELTA rows 2 and 3 await a DRI signature; this is the declared stop reason.
8. PASS — DELTA.md records the new field and both availability changes.
9. PASS — `select_tests.py --base` chose 401 units; `mac-pytest.sh --select` ran them, then the three failed assurance IDs passed on their targeted retry.
10. PASS — Lean `#guard`s, `checkDocSetsAnswered_fits`, `runCaseReported_fits`, `python3 lean/audit.py`.
11. N.A. — no budget, limit or deadline semantics changed.
12. N.A. — no whole-constitution or pilot timing run is permitted for this item; part-document checks pass.
13. PASS — `Test-removed:` trailers and `tools/gate_collection.py --check --prebuilt` (4 covered, 0 refused/stale/malformed).
