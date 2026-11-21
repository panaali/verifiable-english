# srccov-rl-udhr-pilot-1121: REPORT

- Status: all 37 units tagged `none: translation omission` were checked. 33 are KEPT and 4 DROPPED. All 33 kept units stay **NOT CARRIED**. Their only carrier is the front matter of the sealed, measured run `run-20261010T1400Z`, and a sealed run is never rewritten in place. No live UDHR translation exists in the repo.
- HEAD: the last commit on `infra/srccov-rl-udhr-pilot-1121`. Base: VE main `cebf4fd24f`. It merges at the merge train's merge commit for this branch. Answers touched: none (no line the reader is shown changed).
- What changed: a saved record `docs/infra/srccov-rl-udhr-pilot-1121/units.json` and its condition test `tests/test_srccov_rl_udhr_pilot_1121.py`. No product code changed, no document text changed and no derived file changed.
- Open: the carry itself. It needs a new live UDHR run (Notes for the DRI). No DRI signature is reserved and there is no DELTA row.

## Deliverable 0: verify table

`T` = `usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md`. Rows are `srccov-udhr-pilot-s4-<n>-1119`. Each KEPT unit:
- is an omission at main: every front-matter unit covering it is `kind: norm` with no `content` (no VE body), and its formal content sits only in a reading set (not a carrier, map amendment 3);
- has a plain `norms@0` content norm that could carry it, the form u074 already uses;
- is NOT CARRIED because the carrier is sealed (section "Why NOT CARRIED").

| unit id | row id | KEPT / DROPPED | one-line reason with file:line |
|---|---|---|---|
| S0014 | s4-3 | KEPT | T:34; u020, no body; rs_u020 |
| S0015 | s4-4 | KEPT | T:38; u022a, u022b, u022c, no body; rs_u022a-c |
| S0016 | s4-5 | KEPT | T:42; u024, no body; rs_u024 |
| S0017 | s4-5 | KEPT | T:42; u025, no body; rs_u025 |
| S0018 | s4-6 | KEPT | T:46; u027, no body; rs_u027 |
| S0019 | s4-7 | KEPT | T:50; u029, no body; rs_u029 |
| S0021 | s4-8 | KEPT | T:54; u033a, u033b, no body; rs_u033a-b |
| S0022 | s4-9 | KEPT | T:58; u035, no body; rs_u035 |
| S0023 | s4-10 | KEPT | T:62; u037, no body; rs_u037 |
| S0028 | s4-13 | KEPT | T:76; u045a, u045b, no body; rs_u045a-b |
| S0029 | s4-13 | KEPT | T:76; u046, no body; rs_u046 |
| S0030 | s4-14 | KEPT | T:80; u048, no body; rs_u048 |
| S0031 | s4-14 | KEPT | T:82; u049, no body; rs_u049 |
| S0032 | s4-15 | KEPT | T:86; u051, no body; rs_u051 |
| S0033 | s4-15 | KEPT | T:88; u052, no body; rs_u052 |
| S0034 | s4-16 | KEPT | T:92; u054, no body; rs_u054 |
| S0035 | s4-16 | KEPT | T:94; u055, no body; rs_u055 |
| S0038 | s4-17 | KEPT | T:100; u059, no body; rs_u059 |
| S0040 | s4-18 | KEPT | T:106; u063, no body; rs_u063 |
| S0041 | s4-18 | KEPT | T:108; u064, no body; rs_u064 |
| S0042 | s4-19 | KEPT | T:112; u066, no body; rs_u066 |
| S0044 | s4-20 | KEPT | T:116; u070, no body; rs_u070 |
| S0046 | s4-21 | KEPT | T:120; u073, no body; rs_u073 |
| S0047 | s4-21 | DROPPED | already carried at main: T:2 u074 is `CHECKED` with `content.norm` "no-compelled-association-membership" (sign false, guard top) over `compel_association_membership_permitted` ("The actor is permitted to compel the person to belong to an association"); source T:122 |
| S0048 | s4-22 | DROPPED | needs a language feature: T:2 u076 is `["unformalised", "other_act_phrase_grammar"]` (a known gap) for "directly or through freely chosen representatives" (T:126) |
| S0049 | s4-22 | KEPT | T:128; u077, no body; rs_u077 |
| S0053 | s4-24 | KEPT | T:138; u084a-d, no body; rs_u084a-d |
| S0056 | s4-24 | KEPT | T:144; u087, no body; rs_u087 |
| S0061 | s4-27 | KEPT | T:158; u096, no body; rs_u096 |
| S0063 | s4-27 | KEPT | T:158; u098, no body; rs_u098 |
| S0064 | s4-27 | KEPT | T:158; u099a, u099b, no body; rs_u099a-b |
| S0065 | s4-27 | KEPT | T:160; u100a, u100b, no body; rs_u100a-b |
| S0068 | s4-28 | KEPT | T:166; u105a-c, no body; rs_u105a-c |
| S0071 | s4-30 | DROPPED | needs possibility modality: "in which alone the free and full development of his personality is possible" (T:176). `norms@0` and `relational-fol@0` do not express it; `modality@0` is a planned slot |
| S0072 | s4-30 | DROPPED | needs a purpose clause: "solely for the purpose of securing ... and of meeting ..." (T:178) restricts limitations by their purpose (causation-purpose). None of the document's declared profiles (T:2) has it |
| S0073 | s4-30 | KEPT | T:180; u112, no body; rs_u112 |
| S0074 | s4-31 | KEPT | T:184; u114, no body; rs_u114 |

How it was checked:
- The 37 ids are the `part-udhr-pilot-s4.tsv` units whose tag column is `none: translation omission`. S0020 (`modality`) and S0039 (`attribution-evaluation`) carry it only as `also:`, so they are out of scope.
- Each unit's text is the in-repo body at the map's byte offsets. The record holds them, and `test_a_units_quote_is_its_source_sentence_byte_for_byte` checks them byte for byte.
- Main against the pin: `git log --oneline e53db4e8fc..main -- usecases/udhr-pilot` is empty, so the carrier did not change.
- Earlier rows: no `srccov-udhr-pilot-1119` item exists on main. defs-repair-udhr-pilot-1119 carried nothing (its REPORT, "All 3 stay NOT CARRIED").
- Of the 130 front-matter units, only u074 has `content` (a one-off count over `fm["units"]`).
- The front-matter profiles are `documents@1, norm-defaults@0, norms@0, readings@1, relational-fol@0`. This is a `norms@0` document, not soft-norms, so none of the three waiting designs (defs beside soft norms, deadline/cadence, attributed) applies to any kept unit.

## Deliverable 1: why NOT CARRIED (sealed run)

The carrier is the recorded output of a run, not a live document. This is the same finding as defs-repair-udhr-pilot-1119, and each point is checked by `test_the_seal_the_not_carried_units_rest_on_still_holds`:
- `migrate.py` pins its input `frozen-run.json` by `FROZEN_SHA256`.
- `metrics.json` `after.document_bytes` equals the file's size.
- `docs/premise-scale/evidence/ab-documents.json` holds its sha256 `5151b58b…`.
- `tests/test_readings_rd5_udhr.py::test_the_migration_reproduces_the_committed_document` requires the committed bytes to be the migration's output.

DRI decision `reviews/dri-decisions-20261119-defs-repair.md` item 1 says: "a sealed run is never rewritten in place". `usecases/udhr-pilot/` holds only this run. The nightly UDHR pilot runs live outside the VE repo, are made by model calls and are not in this item's paths. So no "next read" in the repo shows a line I could add. A line added in place would break the migration-reproduction test and the measured bytes.

## Deliverables 2 and 3

- 2, regeneration: nothing to regenerate, because no source of a derived file changed. `uv run python tools/regen_generated.py --check` gave "checked 43 entries", rc 0. Neither `conformance/english-lean/corpus-seal.json` nor `tools/fidmech/manifests.py` names this run (grep).
- 3, answers touched: none. No line, legend or unit changed, so no answer or question changes status. I did not open the run's `answers/` or `reports/`.

## Deliverable 4: condition test

`tests/test_srccov_rl_udhr_pilot_1121.py` has 76 tests and reads saved files only. It checks five things:
- the record holds exactly the map's 37 units with their rows;
- each quote is the source sentence at its byte offsets and line, and its covering front-matter units are recorded exactly;
- each kept unit is still an omission (no `content`, reading sets as recorded) and NOT CARRIED for the seal;
- each dropped unit's reason holds in the files: S0047's CHECKED negative norm and its legend, S0048's `unformalised` kind, and S0071/S0072's blocking phrase with no `modality@0`/`events@0` declared;
- the seal still holds.

The task's form, "the new line exists in the carrier", cannot apply because no line could be added (see Deliverable 1). The test asserts the NOT CARRIED state in both directions instead: an in-place carry fails it (seeded bug B2).

Results:
- Pre-change main (record removed): `76 failed in 2.75s`.
- HEAD: `76 passed in 2.40s`.
- Selected run (`mac-pytest.sh --select` at `827bc052d5`): 6 shards, each `exit 0`, 0 failed. The plan's "changed" list put this test first.

## Seeded bugs

Each bug was planted alone. I ran `uv run pytest -q tests/test_srccov_rl_udhr_pilot_1121.py`, then restored with `git checkout`. `git status` was clean afterwards.

| # | planted in | bug | failing test(s) |
|---|---|---|---|
| B1 | `docs/infra/srccov-rl-udhr-pilot-1121/units.json` | unit S0061 removed (the "remove one new entry" check) | `test_the_record_holds_exactly_the_maps_omission_units_and_their_rows`, `..._byte_for_byte[S0061]`, `test_a_kept_unit_is_still_an_omission_at_main[S0061]` |
| B2 | `usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md` | a `content` body added in place to u022a (an in-place carry in the sealed run) | `test_a_kept_unit_is_still_an_omission_at_main[S0015]`, `test_the_seal_the_not_carried_units_rest_on_still_holds` |
| B3 | units.json | S0030 quote "movement" changed to "motion" | `test_a_units_quote_is_its_source_sentence_byte_for_byte[S0030]` |
| B4 | translation.ve.md | u074 norm sign `false` changed to `true` | `test_a_dropped_units_reason_holds_in_the_files[S0047]`, seal test |
| B5 | units.json | S0072 marked KEPT | `test_the_record_holds_exactly_the_maps_omission_units_and_their_rows` |

No product code changed in Lean, Python or Rust, so no per-language seeded bug applies.

## Trust, DELTA, size, freeze

- Trust: `uv run python tools/trust_map.py --check` gave "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0" and PASS.
- DELTA: none. Nothing the reader is shown changed, so there is no DELTA.md. Kernel line count unchanged (no Lean).
- Light lane: `light-lane.py check` printed `NOT 907 changed lines outside generated files > 150 (2 files)`. 762 of those lines are the JSON record. I ran no trust_mutants sweep: no trusted file or product code changed (trust +0), and checklist 13a asks for a sweep only on trusted Lean growth.
- SIZE: 0 product, 145 tests, 762 (saved record, written by a one-off script from the map's TSVs) + this report other hand-written lines.
- FREEZE: this item touches no answer and no document byte, so a later read has nothing to re-pin from it. It merges at the merge train's merge commit of this branch.
- Not run: the full gate (the chain runs it on the final HEAD), a Lean build (no Lean changed), a trust_mutants sweep (above), and any whole-document `ve` check (L70).
- Pre-existing red: the 4 tests in `main-known-red.txt` are untouched, and none of them is in this item's selection.

## Spec re-read

- Task deliverable 0 (drop reasons: already carried, needs a feature or undeclared profile) against the four DROPPED rows.
- Deliverable 1 ("never rewrite sealed artefacts; carry where the next read shows the text, or report the unit NOT CARRIED") against Deliverable 1 above.
- The scope line ("ONLY the units tagged 'none: translation omission'") against the exclusion of S0020 and S0039.
- METHOD amendment 3 (reading sets are not carriers) against the kept units' reading sets.
- Section 0 R ("A unit at CHECKED/OPEN with a VE body is a carrier attempt") against S0047.

## Notes for the DRI

- The map is wrong on one point. `udhr-pilot.md` note 1 says the front-matter units have keys id/kind/meaning/span/support only, and note 4 says "no line states the prohibition" for u074. In fact u074 has a CHECKED `content.norm` with `sign: false` over that predicate, which states it. S0047 is dropped as already carried.
- Carrying the 33 kept units needs a new live UDHR document in the repo: a new run, or a re-migration with content norms, and then a re-measurement. Whole-UDHR checks are refused under L70, so measuring needs part documents or a ruling. This joins defs-repair-udhr-pilot-1119b.
- Conservative choices taken without asking:
  - S0071 and S0072 are dropped for the features they need, rather than carried with opaque predicates.
  - S0020 and S0039 stay out because `none` is only their `also:` tag.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no route or relay touched.
2. Deliverables built, no rule broken: PASS. Deliverables 0-4 above. The carry is NOT CARRIED under deliverable 1's own alternative. The test reads saved files and no live git (`test_the_seal_the_not_carried_units_rest_on_still_holds`).
3. Tests can fail: PASS. Seeded bugs B1-B5, and pre-change main gives 76 failed.
4. Py/Lean/Rust agree: N.A., no product code.
5. R8 binding: N.A., no binding changed.
6. Gate evidence matches final HEAD: PASS for the selected run at `827bc052d5`. Commits after it add only this report. The full gate is run by the chain.
7. No unsigned item: PASS, no DELTA row and nothing reserved.
8. Every user-visible change in DELTA: N.A., nothing user-visible changed (no document byte; B2 shows any byte change fails the test).
9. Test selection finds the tests: PASS. select_tests lists `tests/test_srccov_rl_udhr_pilot_1121.py` as changed, and it ran in the selected run.
10. Lean statements: N.A., no Lean.
11. Budgets fail closed: N.A., no budget code.
12. No CPU/memory regression: N.A., a 76-test file that runs in 2.4 s and reads files only.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. Kept units must have no body and dropped S0047 must have one (`test_a_kept_unit_is_still_an_omission_at_main`, `test_a_dropped_units_reason_holds_in_the_files`). Each claim above cites its command. Spec re-read above.
15. No overclaim / no silent cut / checks can fail / limits: PASS. The universal words ("none", "no") cite trust_map, regen --check, grep or the tests. The carry is stated as not done, with a FOLLOW-UP. B1-B5 cover the new checks. No limits are involved.

FOLLOW-UP: srccov-rl-udhr-pilot-1121b carry the 33 kept UDHR omission units in a new live UDHR document (the only carrier is the sealed, measured run-20261010T1400Z)
