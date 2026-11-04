# at-1w report: `reports@0`'s `wants` test moved into Lean

- **Status:** built, all plan deliverables (1)–(5); no DRI signature needed or reserved.
- **HEAD:** the branch's final commit (feature/at-1w over main 94580b39b); the chain's gate runs on it.
- **What changed:** new `lean/VE/Attribution/Words.lean` (`VE.Reports.wantsPhrase?`, `finitePhrase`); kind `reports-wants` of the `reports` mode; Python relays and binds it; `_infinitive` and `_finite` deleted from `ve/report_english.py`.
- **Open:** none for this item; one reading for AT-1 (section "For AT-1").
- **Next item:** at-1 (attitudes Lean core).

Plan: docs/spec/attitudes-PLAN.md "AT-1w" (7c5c13cf0, lines 762–790); spec docs/spec/attitudes.md (03732731e) section 10
item 6, section 1 rows 'Their English verbs' and 'The `wants` verb-phrase test', section 15 RC-4; stub S0. Main had
none of them: copied verbatim into docs/spec/ (blobs cc36b10, 11f3d2b, fd08011; commit 68e40af8c). Synthesis round 2
(debates/plan-synthesis-2/edits-attitudes.md): 0 lines name this item; its one order line (:63, AT-0 → at-1w → AT-1)
holds. The plan's statement review accepted this section; no statement changed.

## Deliverables

| Plan or task line | Delivered | Commit | Test or check |
|---|---|---|---|
| (1) record `_infinitive`/`_finite` on every phrase the suite's `reports@0` cases reach, by a committed script | `tests/data/reports_wants_parity.json` by `docs/attitudes/at-1w/record_parity.py`: 3 reached rows of each function (pytest of `tests/test_report_english.py` and `tests/test_reports.py`, wrapped) plus 53 + 30 branch probes, last run on a checkout of 94580b39b (`git worktree add --detach /tmp/at1w-main 94580b39b`) | 68e40af8c, 1a4609c50, 28350ef28 | the recorder's own run: `55 passed`; reached rows `audits service`, `is safe`, `publishes service` and their infinitives |
| (2) `Words.lean`, module `VE.Attribution.Words`, namespace `VE.Reports`: `wantsPhrase?` and the finite form, `_infinitive`'s behaviour, nothing else; `#guard`s on the table's rows | `wantsPhrase?`, `finitePhrase` and private helpers `headRest`, `vowel`, `joined`, `baseOf`; `#guard`s at :60 (C-e), :65/:68 (reached rows), :71/:83 (probes) | 20156dfd8 | `lake build VE.Attribution.Words` |
| (3) one new kind of `reports`: per phrase its infinitive (absent when refused), per infinitive its finite form; row in Schemas/Reports.lean typed to the leaves; `runCaseReported_fits` keeps its statement, skeleton gains the row | `reports-wants` (`Run.runWants`, dispatched before the document decode: it reads no environment or document); `reports.json#/$defs/wants`; `wants_fits` and one `runCase_fits` branch; `runCaseReported_fits` unchanged | 20156dfd8, 0e42fe2e6 | `lake build ResponseShape.Encoders.Reports`; `#guard`s in Run.lean and Schemas/Reports.lean |
| (4) Python relays the kind and checks schema and binding only (R8); `report_english.py` reaches it through the `reports` object; `_infinitive`, `_finite` deleted | `ve/reports_route.py` `wants_forms` (relay, schema checked by `decide_once`); `ve/reports.py` `ReportsDocument.wants_forms`/`infinitive`/`finite` and `_bound`; `_subject_split` and the three "to VP" readings call `reports.infinitive`/`reports.finite` | 20156dfd8 | `tests/test_reports_wants.py` |
| (5) every `reports@0` English test keeps its answer | `tests/test_report_english.py`, `tests/test_reports.py` unchanged | — | 55 passed on 94580b39b and on this branch (`uv run pytest -q tests/test_report_english.py tests/test_reports.py`) |
| (5) Lean's kind equals the parity table on every row | | 20156dfd8 | `test_the_kind_answers_the_parity_table_on_every_row` |
| (5) fuzz: drop, empty, retype, duplicate, reorder each row's members; a row for a phrase not sent | `mutations()`: each member dropped, emptied, retyped (`7`, `true`, `[]`, `{}`, `1.5`, deep list, `null` for the bound member); each list dropped, emptied, duplicated, reordered, shifted, given a row for `flies` | 20156dfd8 | `test_every_retyped_or_rebound_row_is_refused_by_the_schema`, `test_every_rebound_row_is_unavailable_to_the_document`, `test_the_english_reads_both_forms_from_the_kind_and_refuses_a_dropped_row` |
| (5) C-e's phrase as a `#guard` and as a test through the kind, `c_e` in its name | `Words.lean:60`; `is classified as "mass_casualty_weapon_uplift"` ↔ `be classified as …` | 20156dfd8 | `test_c_e_phrase_gives_its_infinitive_and_back_through_the_kind` |
| (5) the existing test that `reports@0` beside the chain is refused stays selected and unchanged | `tests/test_reports.py::test_reject_unsupported_act_and_profile_composition` (`reports@0 with norms@0`), file untouched | — | in `tools/select_tests.py --base 94580b39b` |
| Generated files through `regen_generated.py --write` (R12); no committed gate collection | `reports.json`, `checkers.lock`, inventories, code map, binding census | 20156dfd8 and the final regen commit | `regen_generated.py --check` |
| evaluator rule: every value read once, size charged against a stated limit, a large request as a fixture | each string is decoded once and tested once; its UTF-8 bytes + 1 summed against `max_source_bytes` | 0e42fe2e6, 1a4609c50 | `test_the_request_is_charged_against_max_source_bytes` (9361 phrases + 1 infinitive, at the limit; one byte over); the limit `#guard` in Run.lean (one or two strings of each field, both sides) |
| at-rev follow-ups written as readings | section below | — | — |

`lean/VE.lean` is unchanged: it lists roots, and `VE.Attribution.Words` is reached through `VE.Attribution.Run`.

## Wire reading

The plan says the infinitive is "absent when the test refuses it". The row carries it as JSON `null`
(`{"phrase": "is not safe", "infinitive": null}`), so every member is required and a dropped member is refused by
the schema, which the fuzz test asks for; Python reads `null` as `None`.

## For AT-1

`wantsPhrase?` now has `_infinitive`'s behaviour, so it takes the finite verb phrase, as spec :1734 reads it
("`wantsPhrase?` of `is classified as …` is `be classified as …`"), not the stub S0's whole wording
`{0} is classified as …`: `lake env lean` gives `none` on `"{0} is classified as \"mass_casualty_weapon_uplift\""`
and `some "be classified as …"` on the phrase. D14c's text (spec :671–673,
`(A.lex.lexicon.wordings.lookup p).bind VE.Reports.wantsPhrase?`) therefore needs the wording's `{0} ` subject
removed before the call; AT-1 takes that reading (no plan text changed here).

## at-rev follow-ups

C points on the plan text (at-rev item 4, run-log/at-rev/review.final.md FOLLOW-UP list); no plan text changes. The
readings AT-1, AT-2 and AT-5 take:

1. AT-R1's three units gain no closed `wants` part.
2. The one-candidate set choice (plan :1758, :1793) is conservative, not a PC fact.
3. Plan :1788 'its' has no candidate.
4. Plan :536 'the first batch that emits' reads 'PC-11 first decodes a part'.
5. `renderable` is false on an admitted closed `wants` part.
6. AT-5's fixture list omits C-e's part, and its evidence row cites `condsOf` alone.
7. Plan :416 cites spec 3.1, not plan 3.7.
8. attitudes.md:2315 `envAtt` is AT-1's.
9. docs/research/attitudes.md:244 still says AT-8 report units (withdrawn).

## Seeded bugs (`docs/attitudes/at-1w/mutants.json`)

| Language | File | Bug | Failing check |
|---|---|---|---|
| Lean | lean/VE/Attribution/Words.lean | `baseOf` without `"is" => some "be"` (plan section 4's bug) | `Words.lean:60` (C-e), `:65` (reached rows), `:71` (probes): `lake build VE.Attribution.Words` fails |
| Lean | lean/ResponseShape/Schemas/Reports.lean | the `wants` row's `finite` renamed `finites` (with its render guard) | `ResponseShape/Encoders/Reports.lean:111` unsolved goals in `wants_fits` |
| Lean | trusted definitions (trust_mutants) | 206 mechanical mutants | `docs/attitudes/at-1w/trust-mutants.json`: 204 KILLED, 2 INVALID, 0 SURVIVOR, 0 UNKNOWN |
| Python | ve/reports.py | `finite` keeps a local `_finite` fallback when the row is absent (the plan's bug) | `test_the_english_reads_both_forms_from_the_kind_and_refuses_a_dropped_row` |
| Python | ve/reports.py | `_bound` compares the rows as a multiset (order unbound) | `test_every_rebound_row_is_unavailable_to_the_document` |
| Python | ve/report_english.py | `_subject_split` keeps the finite phrase when Lean refuses it | `test_a_phrase_the_test_refuses_has_no_wants_wording` (it survived the 55 existing English tests, so this test was added) |

Each was restored (`git diff --stat` empty after each). No Rust code changed.

## Trust

`uv run python tools/trust_map.py --check` (exit 0) against 94580b39b2aa: K +0, S +0, trusted +85, all V:
Words.lean +47 (R6: replaces the deleted `_infinitive`/`_finite`), Run.lean +23 and Schemas/Reports.lean +15 (R16:
+38 ≤ 150). One allowance (V 85) in `docs/trust-baseline.json`; the R16 ties-pass row is in manage-agents
FOLLOW-UPS.md "## at-1w". Trust mutants: `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --json
docs/attitudes/at-1w/trust-mutants.json` (first run 47 SURVIVOR, 12 UNKNOWN: killed by guards that call `runWants`
directly, the size limit's two sides with one or two strings of each field, and the schema's kind table, row and
definitions; the UNKNOWNs were mutator artefacts, removed by `vowel` as a list membership, unqualified list
functions under `open List`, and a dispatch guard that compares `runCase` with `runWants`), then `--rescore`: exit 0,
204 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 ALLOWED; per definition every one of the 11 selected has killed mutants.

## Size

`git diff --numstat $(git merge-base HEAD main)`, hand-written files only (generated files, the verbatim plan, spec
and stub, the trust-mutant evidence, the trust baseline and the script-written parity table excluded): +669 −42 = 711
changed lines (this measurement included), of which REPORT.md and DELTA.md are 162; product code, tests, guards and
the recorder are 549. That is about 110 over the ~600 guide, all in the mandated report and evidence files; every deliverable is in, so no `at-1wb`
is named. At the seam after (3) the count was about 460.

## Pilot bytes

0 expected (the plan's "Bytes unlocked: 0"); nothing is claimed before a pilot audit.

## Runs

- `uv run pytest -q tests/test_reports_wants.py`: 25 passed; `tests/test_nested_pytest.py`: 36 passed.
- `uv run pytest -q tests/test_report_english.py tests/test_reports.py`: 55 passed (as on 94580b39b).
- Selected tests, once on the finished code (`zsh mac-pytest.sh --select -- --base 94580b39b --run`, run
  at-1w-acc1762e-t771698): its fast stage ran 308 of 442 units, `1 failed, 10194 passed, 6 skipped, 83 xfailed`. The
  failure, `tests/test_nested_pytest.py::test_every_pytest_command_is_built_by_the_builder`, was the new recorder
  missing from that test's list of files that build a pytest command themselves; fixed, and the one id rerun
  (`zsh mac-pytest.sh -- <id>`, VM fallback): `1 passed`. The runner took the fast stage's failure as its answer, and
  its 6 shards with the other 134 units never reported: all still `dispatched` at 07:06Z, near their 07:10Z deadline.
  **Not run here:** those 134 units; the chain's gate on the final HEAD runs them.
- `python3 lean/audit.py`: `PASS: 757 source files; 8386 named theorem declarations audited`.
- `uv run python tools/regen_generated.py --write` after the last Lean and doc edit: `wrote 35 entries`, no file
  changed (`git status` clean).
- Not run here: the full release gate (the chain runs it on the final HEAD).
- The chain's gate on 20fe12347 (`gate-result.json`): `3 failed, 32001 passed`. All three were this item's, and
  none is on main-known-red. Fixed:
  - `test_committed_trust_table_covers_every_declaration` failed because 80 lines were unclassified. The eight new
    declarations are now in `tools/trust-classes.json`, all in V classes, so the recorded allowance (V +85, K/S +0)
    is unchanged:
    - `VE/Attribution/Words.lean`'s six definitions are G[V];
    - `runWants` is G[V], beside `runCase`;
    - `wantsStrings` is D[V];
    - `ResponseShape.Schemas.Reports.wants` is G[V].
  - `test_committed_ledger_names_real_declarations` failed because consolidation step 7 now measures 729 removable
    lines, not 727: `runCase` gained the kind's dispatch line. The ledger row in `docs/CONSOLIDATION-PLAN.md` now
    reads 729 / net 669 / score 55.8.
  - `test_corpus_reaches_every_answer_kind_of_every_route` failed because the corpus had no `reports-wants` case.
    Two genuine cases are added to `tests/data/route-cases.jsonl`, recorded with `tests/route_case_recorder.py`
    from `tests/test_reports_wants.py`: C-e's phrase alone, and a refusal beside both fields.
  - Reran on the Mac runner (`zsh mac-pytest.sh --`): the three ids plus `tests/test_route_row_schemas.py`,
    `tests/test_lean_handles.py` and `tests/test_lean_service_schema.py`, which read the whole corpus. Result:
    `234 passed`. `tools/trust_map.py --check`: PASS.

## Spec re-read

- `wantsPhrase? : String → Option String` in `VE.Reports`, module `VE.Attribution.Words`: spec :194, :207, :2040; stub :38.
- `wantsPhrase?` takes the finite phrase: spec :1734.
- One kind of the existing `reports` mode, relayed by `ve/reports_route.py`, schema and binding only; reached through the `reports` object: spec :2042–2045; plan :770–776, :781–782.
- `runCaseReported_fits` keeps its statement, its skeleton gains the row: spec :2046; plan :772–773.
- R8 binding "each phrase it sent answered once, in order, nothing extra": plan :781–782.
- Fuzz list "drop, empty, retype, duplicate and reorder each row's members and add a row for a phrase not sent": plan :786–787.
- C-e's phrase "c0 wants s1 to be classified as …": spec :1738.

## Self-review against BUILDER-CHECKLIST

1. PASS: `test_every_retyped_or_rebound_row_is_refused_by_the_schema` (each member deleted, `7`, `true`, `[]`, `{}`, `1.5`, a nested list, `null` on the bound member); `test_every_rebound_row_is_unavailable_to_the_document` (CheckerUnavailable, also for a non-object answer); request decoder: `test_a_malformed_request_is_invalid_input`.
2. PASS: the Deliverables table; `git diff main...HEAD` has no Python copy of the test (`grep -n "_infinitive\|_finite" ve/` gives nothing), no report test, no file an in-flight branch edits (checked at start over `lean-first/*`, `feature/*`, `infra/*`, `foundation/*`).
3. PASS: seeded bugs table; trust mutants exit 0 (`docs/attitudes/at-1w/trust-mutants.json`).
4. PASS: `test_the_kind_answers_the_parity_table_on_every_row` (Lean against the Python recording, 89 rows); English unchanged, 55 passed on base and head.
5. PASS: `test_every_rebound_row_is_unavailable_to_the_document` (a phrase not sent, shifted, extra, duplicated, dropped, empty).
6. N.A. here: the chain runs the gate on the final HEAD; evidence is saved (`trust-mutants.json`, the parity table), not live git.
7. PASS: DELTA.md rows cite R6, R16, R8, R12; no signature reserved.
8. PASS: no English answer changes (55 passed on base and head; parity table); the new kind is DELTA row 3.
9. PASS: `tools/select_tests.py --base 94580b39b` selects `tests/test_reports_wants.py`, `tests/test_reports.py`, `tests/test_report_english.py`.
10. PASS: the `finites` seeded rename breaks `wants_fits`; `runCaseReported_fits` statement unchanged.
11. PASS: `test_the_request_is_charged_against_max_source_bytes`; the limit `#guard` in Run.lean; no deadline or sleep in the tests.
12. PASS: `test_one_wants_sentence_asks_lean_three_times` (a step count: printing asks twice, parsing once); `decide_once` answers a repeated request from its cache.
13. PASS: no test removed or renamed.
14. PASS: both directions: `test_c_e_phrase_gives_its_infinitive_and_back_through_the_kind` (accepted and the `not ` refusal), `test_a_phrase_the_test_refuses_has_no_wants_wording` (refused); each claim names its command; spec re-read above.
