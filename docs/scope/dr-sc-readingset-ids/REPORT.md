# dr-sc-readingset-ids REPORT: the reading-set id rebuild step takes a `scope@0` part

- **Status:** built; selected tests: see "Tests run". No DRI signature outstanding (both DELTA rows signed,
  `reviews/dri-decisions-20261101-dr-sc-readingset-ids.md`). Full gate not run by the builder (the chain runs it).
- **HEAD:** the branch's last commit (feature/dr-sc-readingset-ids, base main 1edb74de2).
- **What changed:** `tools/readings_s1_pilot.py --rebuild-reading-ids` computes ids on the environment Lean's chain
  reads (`chain_environment`, Lean's `lowerScope`), after Lean's `scope` mode admits a `scope@0` document, and completes
  situation bases over Lean's filled frame instead of every model predicate: a no-op on UDHR parts 1 to 4, with or
  without `scope@0`.
- **Open:** the six UDHR governors are not written here (deliverable 5 below); two FOLLOW-UPs.

## Plan rows and directive lines

| Deliverable (task) | Delivered | Commit | Test / evidence |
|---|---|---|---|
| (1) Reproduce on a part document | UDHR part01 (pilot/udhr-20261101T0600Z, run-20261101T0600Z) with `scope@0` and one governor: the rebuild with `--check-noop` exits 1 with `ve.errors.UnsupportedProfile: UnsupportedProfile: Unsupported profile scope@0`. Raised by Lean's `environment` mode (`ve/backends/relay.py` `decided`), reached from `tools/readings_s1_pilot.py` `rebuild_reading_ids` (`env = _environment(meta["environment"])`) through `ve/document/source.py` `_environment`, `ve/environment.py` `Environment.__init__` and `ve/backends/validation.py` `validated_environment`. So the fault was Python's: the rebuild built its environment from the profile list as written. The document mode never sends `scope@0` to that mode, because it lowers it first (`chain_environment`, which is Lean's `Service.Document.lowerScope`, `lean/VE/Service/Document.lean:101`). | n/a | `evidence/parts-noop.json` (the `main` side of every `+scope@0` row) |
| (2) Fix it where the decision is | The rebuild reads the environment through `chain_environment`, the one existing place Python lowers `scope@0` (as `ve/document/lean.py` does for the ids Lean answered). No new copy: it deletes the rebuild's use of the environment as written. Lean's readings route was never asked, so it needed no change and no route case. Under the DRI's condition (decision item 1), a `scope@0` document is first sent to Lean's `scope` mode (`ve.scope.explain`: `explainCase` runs `gateOf profileTable` and decodes the block). The rebuild therefore refuses every list the document mode refuses, with Lean's text. Documents without `scope@0` are rebuilt as on main, apart from row 2 of the DELTA. | e865c8fbe, c86a471b7 | `test_a_scope_part_with_a_reading_set_rebuilds_as_a_noop_lean_admits`, `test_a_scope_list_the_document_mode_refuses_is_refused_with_leans_text` (3 cases), `test_rebuild_command_is_noop_on_unchanged_environment`, `test_rebuild_preserves_companion_identities_on_unchanged_udhr` |
| (3) Fixture: a part with `scope@0`, `readings@1` and one reading set rebuilds, then passes `--check-noop` | F-ND1's shape (`norm-defaults@0`, one set, one situation over the `unsaid__` tables) between two rules, with governor g1 re-guarding u2. It is built in the test under `tmp_path`, not committed, so it reads no git history. | e865c8fbe, 04d4beaab | `test_a_scope_part_with_a_reading_set_rebuilds_as_a_noop_lean_admits`, `test_an_edited_scope_part_rebuilds_to_the_ids_lean_accepts` (an edited scoped part: `--check-noop` exits 2, the rebuild's output passes `--check-noop` and `ve document check`, and its ids equal the unscoped part's) |
| (4) The no-op defect on parts 1, 2, 4 | Cause, in the rebuild: `_reidentified.extended` completed each situation's base over the models' environment (`_reading_evaluation`), which keeps the regulated predicates. Lean decodes a base with exactly the frame's author vocabulary (`lean/VE/Readings/Wire.lean:18`; under the completion, the filled frame with `unsaid__p`, `lean/VE/Readings/UnspecifiedWire.lean:18`). Part01's bases lack its 9 regulated predicates, so the rebuild added them and every situation id changed. Part 3 has no situation, which is why it was a no-op (parts 1-4 have 3, 2, 0 and 2 situations). Fix: complete bases over `S1Environment(data, filled).author_environment()`, with `filled` from Lean's `readings-elaborate` (`base_vocabulary`), and add missing keys after the base's own. Probe: Lean's filled author vocabulary equals part01's stored base exactly (symmetric difference empty, sorts and predicates). | e865c8fbe | `test_rebuild_is_a_noop_on_a_situation_over_the_filled_frame`, `test_rebuild_adds_a_new_base_predicate_and_no_regulated_one`; `evidence/parts-noop.json` |
| (5) The six governors over reading sets | Not built (task). See the next section. | n/a | n/a |
| DELTA | 2 rows, both signed by the DRI. | this commit | `DELTA.md` |
| Trust | Python only. `uv run python tools/trust_map.py --check`: "against 1edb74de258f: K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0 ... PASS". No R6 or R16 allowance and no FOLLOW-UPS.md row are needed. | n/a | command output above |
| Overlap | At the start no `lean-first/*`, `feature/*`, `infra/*` or `foundation/*` branch changed `tools/readings_s1_pilot.py`, `ve/readings_s1.py` or `tests/test_readings_s1*` (`git diff --name-only main...<branch>` loop). `ve/readings_s1.py` is untouched, so there is no overlap with ap-1bg. | n/a | n/a |
| Plan edits (synthesis round 2, `edits-scope.md`, b2e050be2) | None of its seven edits or DEC 10/16 concerns this step. This item implements none of them. | n/a | n/a |
| Evaluators | No evaluator, runner or mode is added. The rebuild makes one Lean `readings-elaborate` call per document, and only when a rekeyed set has situations under `norm-defaults@0`. Every limit is the route's own. | n/a | n/a |

Size: `git diff --numstat $(git merge-base HEAD main)` before the docs: 123+2 (tests), 52+18 (tool). Docs and evidence
come on top. The total stays under 600.

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

Each bug was applied to `tools/readings_s1_pilot.py`, the test file was run, and the file was restored. Command:
`uv run --frozen pytest -q tests/test_readings_s1_pilot_rebuild.py`, once per mutant. All 6 were killed:

| Mutant | Definition | Killed by |
|---|---|---|
| M1 ids on the environment as written | `rebuild_reading_ids` | `test_a_scope_part_with_a_reading_set_rebuilds_as_a_noop_lean_admits`, `test_an_edited_scope_part_rebuilds_to_the_ids_lean_accepts` |
| M2 bases completed over the models' environment (main's padding) | `_reidentified` | 4 tests, among them `test_rebuild_is_a_noop_on_a_situation_over_the_filled_frame` |
| M3 bases not completed | `_reidentified` | `test_rebuild_adds_a_new_base_predicate_and_no_regulated_one` |
| M4 no `scope` mode admission | `rebuild_reading_ids` | `test_a_scope_list_the_document_mode_refuses_is_refused_with_leans_text[with-risk]`, `[with-discourse]` |
| M5 added keys placed before the base's own | `_reidentified.extended` | `test_rebuild_adds_a_new_base_predicate_and_no_regulated_one` |
| M6 Lean's filled frame not asked | `base_vocabulary` | 4 tests, among them `test_rebuild_is_a_noop_on_a_situation_over_the_filled_frame` |

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
- The refusal against `lean/VE/Scope/Run.lean:239-245` (`explainCase`: `gateOf profileTable` before `readSplit`) and
  `ve/profile_table.json`'s `scope@0` row (requires `norms@0`; refuses `risk@0`, `alternatives@0`, `speech-acts@0`,
  `reports@0`, `ve.discourse@1`).
- The sets the fixture carries against `docs/spec/scope.md` 11.1 ("Carried unchanged: a set on a unit no governor
  covers"): rs_1 is on u1, which g1 does not cover.

## Tests run

- While iterating: `uv run --frozen pytest -q tests/test_readings_s1_pilot_rebuild.py` gave "12 passed in 5.50s" on the
  final test file; `uv run python tools/history_tests.py --check` gave "every test that reads history is listed".
- Selected tests: see the section added after the run.
- Not run: the full gate (the chain runs it) and trust_mutants (no trusted Lean changed). Following L70, no
  whole-UDHR check was run.

## Next item

SC-6 (the UDHR rights reach) and PC-5b (a governor's own reading set beside readings).
