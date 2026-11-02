# dr-sc-readingset-ids REPORT: the reading-set id rebuild step takes a `scope@0` part

- **Status:** fix round 1 done (review F1, B); selected tests passed (147 units, 6 shards, 0 failed). No DRI signature
  outstanding: DELTA rows 1-2 are signed in `reviews/dri-decisions-20261101-dr-sc-readingset-ids.md`, and row 3 plus row 2's
  no-frame case in `reviews/dri-decisions-20261102-dr-sc-readingset-ids.md`. Full gate not run by the fixer (the chain runs it).
- **HEAD:** the branch's last commit (feature/dr-sc-readingset-ids, base main 1edb74de2).
- **What changed:** `tools/readings_s1_pilot.py --rebuild-reading-ids` computes ids on the environment Lean's chain
  reads (`chain_environment`, Lean's `lowerScope`), checks a rebuilt `scope@0` document as `ve document check` does, and completes
  situation bases over Lean's filled frame instead of every model predicate: a no-op on UDHR parts 1 to 4, with or
  without `scope@0`.
- **Open:** the six UDHR governors are not written here (deliverable 5 below); two FOLLOW-UPs.

## Fix round 1 (review `dr-sc-readingset-ids-review.final.md`)

- **F1 (B):** the gate was Lean's `scope` explain mode, which runs plain `govern` and refuses every set on a governed
  unit. The document mode governs those sets per choice. The class is that the rebuild and `ve document check` give
  different answers on a `scope@0` document. It is removed by making the check itself the gate: the rebuilt text
  (`ve.document.check_document(path, raw=...)`) is checked, or the text as written when the ids cannot be rebuilt,
  and the check's answer is raised. That also removes the explain mode's cell limit (the sweep) and its acceptance of
  `judgments@0` with `scope@0` (F2). The second fault: `filled` is read only where Lean answers it, and without a
  frame a base is kept as written. Python builds no frame there (R8).
  Probe F1: before, `VEError: ScopeReadings: u0165.s03`; after, `ok`. Its regression tests:
  `test_a_set_governed_per_choice_rebuilds_as_a_noop_lean_admits`, plus
  `test_a_scope_document_the_check_refuses_is_refused_with_its_answer[a-choice-conflicts, past-the-choice-limit,
  with-judgments]`. All 4 fail on the tool before the fix (swapped in and restored: "4 failed"). DELTA row 3 is
  SIGNED by the DRI (2026-11-02 file, item 1), and row 1's text is rewritten as that decision asks.
- **F2 to F4 (C):** F2 is resolved by the new gate (the `with-judgments` case). F3 and F4 stay the reviewer's
  FOLLOW-UPs; F4 is noted in DELTA row 2, as the DRI asked.

## Plan rows and directive lines

| Deliverable (task) | Delivered | Commit | Test / evidence |
|---|---|---|---|
| (1) Reproduce on a part document | UDHR part01 (pilot/udhr-20261101T0600Z, run-20261101T0600Z) with `scope@0` and one governor: the rebuild with `--check-noop` exits 1 with `ve.errors.UnsupportedProfile: UnsupportedProfile: Unsupported profile scope@0`. Raised by Lean's `environment` mode (`ve/backends/relay.py` `decided`), reached from `tools/readings_s1_pilot.py` `rebuild_reading_ids` (`env = _environment(meta["environment"])`) through `ve/document/source.py` `_environment`, `ve/environment.py` `Environment.__init__` and `ve/backends/validation.py` `validated_environment`. So the fault was Python's: the rebuild built its environment from the profile list as written. The document mode never sends `scope@0` to that mode, because it lowers it first (`chain_environment`, which is Lean's `Service.Document.lowerScope`, `lean/VE/Service/Document.lean:101`). | n/a | `evidence/parts-noop.json` (the `main` side of every `+scope@0` row) |
| (2) Fix it where the decision is | The rebuild reads the environment through `chain_environment`, the one existing place Python lowers `scope@0` (as `ve/document/lean.py` does for the ids Lean answered). No new copy: it deletes the rebuild's use of the environment as written. Lean's readings route was never asked, so it needed no change and no route case. Under the DRI's condition (decision item 1), and since fix round 1, the rebuilt `scope@0` document is checked by `ve document check` (`check_document` with `raw`), or the text as written when its ids cannot be rebuilt. The rebuild therefore refuses what that check refuses, with its answer, and admits what it admits (DELTA row 3). Documents without `scope@0` are rebuilt as on main, apart from row 2 of the DELTA. | e865c8fbe, c86a471b7, ccf6da1e0 | `test_a_scope_part_with_a_reading_set_rebuilds_as_a_noop_lean_admits`, `test_a_scope_list_the_document_mode_refuses_is_refused_with_leans_text` (3 cases), `test_a_set_governed_per_choice_rebuilds_as_a_noop_lean_admits`, `test_a_scope_document_the_check_refuses_is_refused_with_its_answer` (3 cases), `test_rebuild_command_is_noop_on_unchanged_environment`, `test_rebuild_preserves_companion_identities_on_unchanged_udhr` |
| (3) Fixture: a part with `scope@0`, `readings@1` and one reading set rebuilds, then passes `--check-noop` | F-ND1's shape (`norm-defaults@0`, one set, one situation over the `unsaid__` tables) between two rules, with governor g1 re-guarding u2. It is built in the test under `tmp_path`, not committed, so it reads no git history. | e865c8fbe, 04d4beaab | `test_a_scope_part_with_a_reading_set_rebuilds_as_a_noop_lean_admits`, `test_an_edited_scope_part_rebuilds_to_the_ids_lean_accepts` (an edited scoped part: `--check-noop` exits 2, the rebuild's output passes `--check-noop` and `ve document check`, and its ids equal the unscoped part's) |
| (4) The no-op defect on parts 1, 2, 4 | Cause, in the rebuild: `_reidentified.extended` completed each situation's base over the models' environment (`_reading_evaluation`), which keeps the regulated predicates. Lean decodes a base with exactly the frame's author vocabulary (`lean/VE/Readings/Wire.lean:18`; under the completion, the filled frame with `unsaid__p`, `lean/VE/Readings/UnspecifiedWire.lean:18`). Part01's bases lack its 9 regulated predicates, so the rebuild added them and every situation id changed. Part 3 has no situation, which is why it was a no-op (parts 1-4 have 3, 2, 0 and 2 situations). Fix: complete bases over `S1Environment(data, filled).author_environment()`, with `filled` from Lean's `readings-elaborate` (`base_vocabulary`), and add missing keys after the base's own. Probe: Lean's filled author vocabulary equals part01's stored base exactly (symmetric difference empty, sorts and predicates). | e865c8fbe | `test_rebuild_is_a_noop_on_a_situation_over_the_filled_frame`, `test_rebuild_adds_a_new_base_predicate_and_no_regulated_one`; `evidence/parts-noop.json` |
| (5) The six governors over reading sets | Not built (task). See the next section. | n/a | n/a |
| DELTA | 2 rows, both signed by the DRI. | this commit | `DELTA.md` |
| Trust | Python only. `uv run python tools/trust_map.py --check`: "against 1edb74de258f: K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0 ... PASS". No R6 or R16 allowance and no FOLLOW-UPS.md row are needed. | n/a | command output above |
| Overlap | At the start no `lean-first/*`, `feature/*`, `infra/*` or `foundation/*` branch changed `tools/readings_s1_pilot.py`, `ve/readings_s1.py` or `tests/test_readings_s1*` (`git diff --name-only main...<branch>` loop). `ve/readings_s1.py` is untouched, so there is no overlap with ap-1bg. | n/a | n/a |
| Plan edits (synthesis round 2, `edits-scope.md`, b2e050be2) | None of its seven edits or DEC 10/16 concerns this step. This item implements none of them. | n/a | n/a |
| Evaluators | No evaluator, runner or mode is added. The rebuild makes one Lean `readings-elaborate` call per document, and only when a rekeyed set has situations under `norm-defaults@0`. Every limit is the route's own. | n/a | n/a |

Size: `git diff --numstat $(git merge-base HEAD main)` before the docs: 123+2 (tests), 52+18 (tool). Docs and evidence
come on top. The total stayed under 600 at the build (584, review). Fix round 1 adds the B fix on top (see "Tests run").

## Deliverable 5: the six UDHR governors (pilot tally `scope-tally.json`, run 20261101T0600Z)

| Governor | Reach, effect | Which item covers it |
|---|---|---|
| u111 (29(2), limitations) | frontier, carve-out | **SC-6** (fixture F14: its limitation reaches every right line) |
| u112 ("These rights and freedoms") | frontier, carve-out | **SC-6** (F14″, a two-candidate reading set, after SC-5) |
| u114 (Article 30) | `rules`, carve-out over every unit, the reading-set units among them | **SC-6** (F14′: its bar reaches every right line); the sets it covers are governed per choice, and **sc-5rdb** (`governSets_every_choice`) carries the per-choice statement for them |
| u019 ("without distinction of any kind") | frontier (3 candidates), frame; a pilot judgement | **SC-5** makes the frontier a reading set, then **PC-5b** puts that reach set beside `readings@1`; the sets inside it (u025, u027, u037) go per choice under **sc-5rdb** |
| u052 ("This right may not be invoked ...") | anchor, carve-out over u051 | none of the three: FOLLOW-UP below |
| u108 (social and international order) | frontier, no effect; a pilot judgement | none of the three, and it changes no rule: FOLLOW-UP below |

FOLLOW-UP: dr-sc-u052-anchor write UDHR u052's anchor carve-out over u051 with sc-3a's anchor reach on a part document
FOLLOW-UP: dr-sc-u108-noeffect decide whether UDHR u108 (a frontier reach with no effect) is a governor at all, or a `title`-like no-op

## Seeded bugs (Python: the only product language changed; `mutants.json`)

Each bug (its `replace` pair in `mutants.json`) was applied to its file, the test file was run, and the file was
restored. Command: `uv run --frozen pytest -q tests/test_readings_s1_pilot_rebuild.py`, once per mutant. In fix round 1
all 12 were rerun on the fixed code, and all 12 were killed. M7 to M12 are new; M4 is now "no document check":

| Mutant | Definition | Killed by |
|---|---|---|
| M1 ids on the environment as written | `_rebuilt` | `test_a_scope_part_with_a_reading_set_rebuilds_as_a_noop_lean_admits`, `test_an_edited_scope_part_rebuilds_to_the_ids_lean_accepts`, `test_a_set_governed_per_choice_rebuilds_as_a_noop_lean_admits` |
| M2 bases completed over the models' environment (main's padding) | `_reidentified` | 4 tests, among them `test_rebuild_is_a_noop_on_a_situation_over_the_filled_frame` |
| M3 bases not completed | `_reidentified` | `test_rebuild_adds_a_new_base_predicate_and_no_regulated_one` |
| M4 no document check of a `scope@0` rebuild | `rebuild_reading_ids` | 5 tests: `test_a_scope_document_the_check_refuses_is_refused_with_its_answer` (3 cases), `test_a_scope_list_the_document_mode_refuses_is_refused_with_leans_text[with-risk]`, `[with-discourse]` |
| M5 added keys placed before the base's own | `_reidentified.extended` | `test_rebuild_adds_a_new_base_predicate_and_no_regulated_one` |
| M6 Lean's filled frame not asked | `base_vocabulary` | 4 tests, among them `test_rebuild_is_a_noop_on_a_situation_over_the_filled_frame` |
| M7 the file as written checked, not the rebuilt text | `rebuild_reading_ids` | `test_an_edited_scope_part_rebuilds_to_the_ids_lean_accepts` |
| M8 the loader ignores `raw` | `ve/document/load.py` `_load` | `test_an_edited_scope_part_rebuilds_to_the_ids_lean_accepts`, `test_a_scope_list_the_document_mode_refuses_is_refused_with_leans_text` (3 cases) |
| M9 no check of the text as written when its ids fail | `rebuild_reading_ids` | `test_a_scope_list_the_document_mode_refuses_is_refused_with_leans_text[with-risk]`, `[with-discourse]` |
| M10 `filled` read unchecked (the review's `KeyError`) | `base_vocabulary` | `test_a_set_governed_per_choice_rebuilds_as_a_noop_lean_admits`, `test_a_scope_document_the_check_refuses_is_refused_with_its_answer[a-choice-conflicts]`, `[past-the-choice-limit]` |
| M11 bases completed when Lean answers no frame | `_rebuilt` | `test_a_set_governed_per_choice_rebuilds_as_a_noop_lean_admits` |
| M12 the explain gate back | `rebuild_reading_ids` | the 4 tests of fix round 1 |

Base against head: on main's `tools/readings_s1_pilot.py` the 4 new tests of the first commit fail and the 5 old ones
pass (`git show main:tools/readings_s1_pilot.py` swapped in and then restored: "4 failed, 5 passed").

## Evidence

- `evidence/parts-noop.json`: `--rebuild-reading-ids --check-noop`, main against head, on UDHR parts 1-4, each also
  with `scope@0` and no governor, and on part01 with governor g1. Main: parts 1, 2 and 4 exit 2 ("rebuild is not a
  no-op"), part 3 exits 0, every `scope@0` part exits 1 (`UnsupportedProfile`). Head: all 9 exit 0 with `"no_op":
  true`. `--out` writes the input's bytes for part01, part04 and part01+scope (`cmp`).
- `evidence/part01-scope-check.json`: `ve document check` on part01 and on part01 with `scope@0` and g1 (u020 re-guards
  u024); both exit 0. The same coverage (CHECKED 192, LABELLED 265, OPEN 1264, UNFORMALISED 3003), premises `model`,
  and the same three sets. Only `document_id` and `readings.sizes.nodes` differ (138 against 140: the composed guard).
  Two governors I tried first were refused by Lean (`NotALeadIn: u019` for a `list` reach, and `ScopeNoEffect: g1` for
  `precedes` across predicates). Those were my governors' faults, not the route's.
- Pilot bytes this item is expected to move: 0 (the task claims 0). The pilot can now write governors on a part with
  reading sets; their bytes belong to SC-6 and PC-5b. Nothing is claimed before a pilot audit.

## Spec re-read

- `chain_environment` against `lean/VE/Service/Document.lean:101-103` (`lowerScope`: the environment the chain reads
  under `scope@0`, without it) and `:1752-1764` (the governed case hands the chain `lowerScope`'s environment).
- The base vocabulary against `lean/VE/Readings/Wire.lean:18` ("`base` is the finite-model wire form with exactly the
  base predicates") and `lean/VE/Readings/UnspecifiedWire.lean:18` ("over the filled frame's author vocabulary,
  `unsaid__p` included").
- The gate against `lean/VE/Service/Document.lean:1977-1983` (`checkDocSets`: `gateOf profileTable`, `decodeScope`,
  `governSetsWith governFast`, then the chain); before fix round 1 it was `lean/VE/Scope/Run.lean:239-245` (`explainCase`), and
  `ve/profile_table.json`'s `scope@0` row (requires `norms@0`; refuses `risk@0`, `alternatives@0`, `speech-acts@0`,
  `reports@0`, `ve.discourse@1`).
- The sets the fixture carries against `docs/spec/scope.md` 11.1 ("Carried unchanged: a set on a unit no governor
  covers"): rs_1 is on u1, which g1 does not cover.

## Tests run

- While iterating: `uv run --frozen pytest -q tests/test_readings_s1_pilot_rebuild.py` gave "12 passed in 5.50s" on the
  final test file; `uv run python tools/history_tests.py --check` gave "every test that reads history is listed".
- Selected tests, once, on the finished code: `zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base
  $(git merge-base HEAD main) --run` gave exit 0, "73/526 test units"; shards "29 units, 29 passed", "22 units, 22
  passed", "22 units, 22 passed" (tree caf0c9a2be; run dr-sc-readingset-ids-a23441e7-t575817). After it only the code map
  was regenerated and the REPORT edited.
- `uv run python tools/gate_collection.py --check --prebuilt` gave "7 added, 0 removed by a trailer, 0 refused, 0 stale and
  0 malformed trailers".
- `uv run python tools/regen_generated.py --check` gave exit 0. It was then run once with `--write` (the code map only).
- Fix round 1, on the fixed code (ccf6da1e0, docs uncommitted): `uv run --frozen pytest -q
  tests/test_readings_s1_pilot_rebuild.py` gave "16 passed"; the selected tests (same command) gave exit 0 with 6
  shards (26, 26, 25, 25, 24 and 21 units, all passed; run dr-sc-readingset-ids-62cef17c-t578920); `lake build` "Build
  completed successfully (1223 jobs)"; `python3 lean/audit.py` PASS; `tools/regen_generated.py --check`,
  `tools/trust_map.py --check` and `tools/repo_map.py --check` PASS; `gate_collection.py --check --prebuilt`: "11
  added, 0 removed by a trailer, 0 refused, 0 stale". The head side of `evidence/parts-noop.json` was rerun on the
  fixed tool: all 9 runs are unchanged (exit 0, no-op), so the file has the same bytes. Size after the round: 620
  hand-written lines (`git diff --numstat` without the code map), 20 over the ~600 line, all of it the B fix and its
  evidence.
- Not run: the full gate (the chain runs it) and trust_mutants (no trusted Lean changed). Following L70, no
  whole-UDHR check was run.

## Next item

SC-6 (the UDHR rights reach) and PC-5b (a governor's own reading set beside readings).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: PASS. No new relay: the rebuild calls the existing typed and bound relays
   (since fix round 1 `ve.document.check_document`, the document mode's relay and its binding;
   `ve.readings_route.elaborate` with `_completion_elaborate` and its
   mutation tests in `tests/test_readings_nd_document.py::test_a_mutated_elaborate_row_is_unavailable`). An unbound
   row is `CheckerUnavailable` before the rebuild uses it.
2. Deliverables and rules: PASS. The plan rows table above. No Python copy of a Lean decision: the frame is Lean's
   `filled` (where Lean answers one), the gate is `ve document check` itself, and the lowering is the existing
   `chain_environment`. No report test
   was added.
3. Tests can fail: PASS. `mutants.json` (12 killed, rerun in fix round 1); on main's tool the 4 new tests of the
   build fail, and on the build's tool the 4 tests of fix round 1 fail.
4. Agreement and valid inputs: PASS. Main against head on UDHR parts 1-4 (`evidence/parts-noop.json`); documents
   without `scope@0` as on main (`test_rebuild_command_is_noop_on_unchanged_environment`,
   `test_rebuild_preserves_companion_identities_on_unchanged_udhr`).
5. R8 binding, undeclared names refused: N.A. No field of a Lean answer is newly read. The `filled` environment is
   bound by the existing `_bind_completion` (`test_filled_environment_is_typed_by_the_schema_and_bound_to_the_request`).
6. Gate evidence on the final HEAD: N.A. for the builder (the chain runs the gate). The evidence names its commands
   and the base 1edb74de2.
7. No unsigned item: PASS. `DELTA.md` rows 1-3 are SIGNED by the DRI (decision files cited). Trust +0
   (`tools/trust_map.py --check` PASS).
8. Every user-visible change in DELTA: PASS. Rows 1 and 3 cover the tool's newly accepted input, row 2 its changed ids. No
   checker answer changes (`evidence/part01-scope-check.json`).
9. Test selection: PASS. The selection ran `tests/test_readings_s1_pilot_rebuild.py` first ("changed [...]"), the
   file that kills every seeded bug. 73 of 526 units, not everything.
10. Lean statements: N.A. No Lean changed and no statement was added (statement gate: nothing to ask).
11. Budgets and deadlines: N.A. No new evaluator or budget. The one `readings-elaborate` call keeps the route's own
    limits, and a refusal or `ResourceLimit` there is raised, never a rebuilt id.
12. CPU and memory: PASS. One extra Lean call per rebuild, and only under `norm-defaults@0` with situations (0.4 s on
    part01, probe). Nothing on the check or render path changes.
13. Test-removed trailers: PASS. None removed (`gate_collection.py --check --prebuilt`: 0 removed, 0 stale, 0
    malformed).
14. Both directions, cited evidence, spec re-read: PASS. Admit and refuse
    (`test_a_scope_part_with_a_reading_set_rebuilds_as_a_noop_lean_admits` and
    `test_a_scope_list_the_document_mode_refuses_is_refused_with_leans_text`); keep and add
    (`test_rebuild_is_a_noop_on_a_situation_over_the_filled_frame` and
    `test_rebuild_adds_a_new_base_predicate_and_no_regulated_one`); "Spec re-read" above.
