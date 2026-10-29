# sc-5rc build report

**DRI signature needed for DELTA rows 2 and 3.** The prescribed `msg.sh dri sc-5rc` request failed because the sandbox cannot write `/home/seyran/code/manage-agents/inbox/dri`; these rows remain unsigned.
Status: document answers and rendering built; four `Pinned.JsonWF` proofs moved to sc-5rd because sc-1af's route check is not on main.
Code HEAD: `815a2e5f9` (plus the collection-trailer commit `15e00a8c0`). Open: DRI ruling and the sc-5rd dependency. No full gate run; the chain runs it on committed HEAD.

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
