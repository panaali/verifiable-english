# sn-b7b REPORT: the rest of B7, the senses display (Python only)

Status: all four deliverables are built and tested. The selected tests exit 0 on the committed code at `5de455d23`.
No DRI signature is reserved.
HEAD: the commit that adds this report. The code ends at `5de455d23`, and only REPORT.md and DELTA.md come after it.
What changed:
- `ve render --senses` now prints the checked body, the lines each candidate lacks, `--glossary` and `--json`.
- New commands `ve senses resolve` and `ve senses propose-readings`.
- The web-app contract in docs/spec/senses.md 2.7.1.
Open: sn-b7c (g1, g4-g7 and g2's printed line, behind R3, sn-b6e and sn-b6f) and sn-b7d (the renderer for glossed senses).
DRI decisions: reviews/dri-decisions-20261110-sn-b7b.md and reviews/dri-decisions-20261110-sn-b7b-delta.md (both in
/home/seyran/code/manage-agents).

## Deliverables (task order; plan B7 :837, :884-891; 2.8 :396; 6.8 :1065)

| Task deliverable | State | Where | Tests |
|---|---|---|---|
| (1) `ve render --senses`: Lean's preamble lines (a), then Python's renderer over the projected environment, then Lean's re-read; a mismatch is `CheckerUnavailable` | yes, for a body whose occurrences are all defaults. A switched occurrence gives `text: null` with `body_status: switched-occurrence-not-rendered` (DRI 20261110 item 2), because the renderer cannot word a glossed sense (sn-b7d). The body re-read is a `senses.read` of the rendered text: status `one`, every unit's formula and mark (`is`), the three projection identities. A budget end is a ResourceLimit | `ve/senses/display.py` `body`; `ve/__main__.py` `_render_senses` | `tests/test_senses_display.py::test_the_body_is_leans_preamble_then_the_rendering_reread`, `::test_a_body_with_a_switched_occurrence_is_not_rendered`, `::test_a_body_rendered_under_another_projection_is_checker_unavailable`, `::test_a_reread_bound_to_another_formula_or_projection_is_refused` (11 cases) |
| (1) each candidate re-read by sn-b6d's re-read | yes: `senses.read` with `reread` (sentence, candidate, rendering) on the same source. Lean's `outcome` must be `same`; `unknown` is a ResourceLimit. The `senses.project` identities stay bound to the candidate's. Re-read bytes are charged before any call (`MAX_REREAD_BYTES` 262,144, and `MAX_CANDIDATES` 64) | `display.candidates`, `reread` | `::test_two_candidates_each_reread_under_its_own_projection`, `::test_one_candidate_reread_under_its_own_projection`, `::test_a_two_sentence_candidate_rereads_and_a_patched_projection_is_refused`, `::test_a_candidate_is_shown_only_when_leans_reread_is_same` (3), `::test_a_base_projection_rendering_fails`, `::test_each_lines_is_projected_once_within_the_limit` (limit and limit+1, for both limits) |
| (1) the candidate view shows the resolving lines the document lacks (a, c) | yes: `lacking` is the last len(`choice`) lines of Lean's `lines`. `senses_candidate_sound` (lean/VE/Senses/Read.lean:973) proves them `Assignment.lines D (A.extend choice)`, and `extend` appends the choice. Lean's own `Unresolved` text is relayed in `reading.units[].text` | `display.candidates` | `::test_the_lines_a_candidate_lacks_are_those_not_in_leans_preamble` (a preamble written with two spaces, and one wrapped over two lines) |
| (1) fixtures g8, g10 | yes (g table) | | `tests/test_senses_display_cli.py::test_g8_…`, `::test_g10_…` |
| (2) `--glossary`, `--json` from the sense map: glosses (e), byte spans (b) | yes, as data rows with no English frame (DRI 20261110 item 1). `glossary`: one row per used sense with `symbol`, `written` (the source bytes at Lean's span), `gloss`, `description` (the projected environment's), `is_default` and `sentences`, then Lean's `unused`. `hover`: one row per sense-map entry | `display.glossary`, `hover` | `::test_g2_the_glossary_is_the_sense_maps`, `::test_g3_hover_spans_cut_the_source_at_token_boundaries` (a source with NBSP and a double space), `::test_the_glossary_and_hover_follow_the_reading_not_the_pack`, `::test_glossary_and_json_need_senses` |
| (3) `ve senses resolve FILE --word W --gloss G` | yes: Lean's `line` member, put first, then Lean's re-check. The file is rewritten (atomically) only when Lean gives the line and admits the new text. A Lean code relays the first reading. Standard input is refused | `_senses_resolve` | `::test_g9_…`, `::test_g10_…`, `::test_resolve_writes_nothing_lean_does_not_give_or_admit`, `::test_the_error_exits_write_nothing[resolve]` |
| (3) `ve senses propose-readings FILE` | yes. There is one `open` set per open unit with two or more candidates whose every pair Lean distinguishes. Each set has `admission.who: senses`, `why` (the unit's Lean text) and `distinguishing_models` (the flip models by model id). It is validated by `ve.readings.validate_reading_sets` over the projected environment. Each reading's text is its candidate's checked rendering. A one-candidate unit gets `resolving` (its lacking line and Lean's text). A pair that is `undistinguished` or `unknown` gives `unproposed` | `display.propose_readings`, `_senses_propose_readings` | `::test_propose_readings_writes_a_set_the_readings_validation_accepts`, `::test_a_flip_model_that_does_not_separate_is_refused` (2), `::test_propose_readings_has_no_set_for_a_resolved_reading`, `::test_g9_…`, `::test_the_error_exits_write_nothing[propose-readings]` |
| (4) the web-app JSON contract, members on main only | yes: docs/spec/senses.md 2.7.1 (render members, `resolve`, `propose-readings`, exit codes) | | |
| both sides of each check | a rendering that re-reads and a tampered one; two candidates and one; a set and no set; a written file and an unchanged one | | the tests above |

### Fixtures g1 to g10

| Fixture | State |
|---|---|
| g1 (J with its preamble and one gloss) | **sn-b7c**: J reads `none` as merged (R3). Its glossed body also needs sn-b7d's renderer. The mechanism on an as-merged all-default body: `::test_the_body_is_leans_preamble_then_the_rendering_reread` |
| g2 (`--glossary`) | delivered as rows (`::test_g2_the_glossary_is_the_sense_maps`). The printed line `funny: amusing (the default)` is **sn-b7c** after **sn-b6f** (a Lean text; DRI 20261110 item 1) |
| g3 (`--json` byte spans) | delivered: `::test_g3_hover_spans_cut_the_source_at_token_boundaries` |
| g4 (s2's two candidates) | **sn-b7c** (R3). The mechanism on `The riddle is funny.`: `::test_two_candidates_each_reread_under_its_own_projection` |
| g5 (s10, GlossedNatural) | **sn-b7c** after **sn-b6e** (GlossedNatural is not built) |
| g6 (`resolve` on s2) | **sn-b7c** (R3). The command is delivered (g9, g10) |
| g7 (`propose-readings` on s2) | **sn-b7c** (R3). On `The riddle is funny.`: `::test_propose_readings_writes_a_set_the_readings_validation_accepts` |
| g8 (the Mixed warning) | delivered on the as-merged Mixed fixture `GLOSSED` (tests/test_senses_display.py): s1 reads `none` as merged (`tests/test_senses_route.py:101`), and a refused reading has no warnings. The warning is Lean's text, once; exit 0; `body_status` `switched-occurrence-not-rendered`: `::test_g8_the_mixed_warning_is_leans_printed_once` |
| g9 (s16 through the CLI) | delivered: `::test_g9_one_candidate_through_the_cli` |
| g10 (s17) | delivered: `::test_g10_diverging_candidates_through_the_cli` (resolve with `beside` gives s18, one reading of `sense__near_2`) |

## Deviations

1. **The glossary and hover are data rows** (DRI 20261110 item 1, SIGNED). Python writes no `(the default)` or
   `W (meaning G):` frame. Condition: `::test_g2_…` and `::test_the_glossary_and_hover_follow_the_reading_not_the_pack`, plus seeded bug S2.
2. **A body with a switched occurrence is not rendered** (DRI 20261110 item 2, SIGNED). Python's renderer lints the
   projection's `{0} is funny (meaning strange)` (PHRASE_SYNTAX, UNARY_MODIFIER) and falls back to `is classified as
   "sense__funny_2"`, which Lean does not re-read. The renderer work is sn-b7d.
3. **g8 runs on an as-merged Mixed fixture, not s1.** The DRI's condition (20261110 item 2) names s1, but s1 reads
   `none` as merged and so carries no warnings.
4. **`lacking` comes from Lean's `lines`, not from the source.** The self-review showed that comparing source preamble strings
   is wrong for a line written with two spaces or wrapped. The lines of the choice are the tail of Lean's `lines`
   (`senses_candidate_sound`). The DRI checked this reading (20261110-delta item 1).
5. **Lean's `unknown` re-read and a `budget` body re-read are a ResourceLimit (exit 4)**, never a refusal or a reading.

## Seeded bugs (docs/senses/sn-b7b/mutants.json; Python only, no Lean or Rust changed)

Each bug was planted alone, its test was run alone (`uv run pytest -q <test>`, "1 failed" or more), and the file was
restored. The run was at `2799c7657`, by the script whose results the JSON records.

| Id | File | Bug | Failing test |
|---|---|---|---|
| S1 | `ve/senses/display.py` | a gloss printed on a default occurrence (`is funny (meaning amusing).`; Lean re-reads it to the same formula, spec s8, so the body's exact text is what catches it) | `test_senses_display.py::test_the_body_is_leans_preamble_then_the_rendering_reread` |
| S2 | `display.py` | the glossary built from the source text instead of the sense map | `::test_g2_the_glossary_is_the_sense_maps` |
| S3 | `display.py` | propose-readings writes a set for a one-candidate unit | `test_senses_display_cli.py::test_g9_one_candidate_through_the_cli` |
| S4 | `display.py` | a hover byte span cut inside a token | `test_senses_display.py::test_g3_hover_spans_cut_the_source_at_token_boundaries` |
| S5 | `ve/__main__.py` | the Mixed warning printed from a Python string | `test_senses_display_cli.py::test_g8_the_mixed_warning_is_leans_printed_once` |
| S6 | `display.py` | the lacking lines taken from the head of `lines` | `test_senses_display.py::test_the_lines_a_candidate_lacks_are_those_not_in_leans_preamble` |
| S7 | `display.py` | the body re-read's mark compared by `==` (0 for False) | `::test_a_reread_bound_to_another_formula_or_projection_is_refused[mark-0]` |
| S8 | `display.py` | an `unknown` re-read reported as `CheckerUnavailable` | `::test_a_candidate_is_shown_only_when_leans_reread_is_same[unknown-ResourceLimit]` |
| S9 | `ve/__main__.py` | resolve writes the file when Lean refuses the new text | `test_senses_display_cli.py::test_resolve_writes_nothing_lean_does_not_give_or_admit` |
| S10 | `display.py` | the re-read byte limit charged one byte late | `test_senses_display.py::test_each_lines_is_projected_once_within_the_limit` |
| S11 | `display.py` | the body re-read compared on its first unit only | `::test_a_reread_bound_to_another_formula_or_projection_is_refused[formula-last-…, mark-last-True]` |

## Trust, mutants, size, bytes

- Trust: `uv run python tools/trust_map.py --check` at `5de455d23` prints "K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0 ... PASS". No Lean changed, and no FOLLOW-UPS row is needed (no R16).
- Trust mutants: `light-lane.py check` prints "NOT 875 changed lines outside generated files > 150". The sweep has
  nothing to run: `uv run python tools/trust_mutants.py --plan` prints `{"definitions": 0, "mutants": 0, "to_run": 0}`
  (no trusted Lean definition is added or changed).
- Size (`git diff --numstat c94ad399b 5de455d23`, codemap out): 786 added and 89 deleted. Of these:
  - product code: 290 added (`display.py` 180, `__main__.py` 110)
  - tests: 370
  - contract: 31
  - seeded-bug JSON: 95

  This is over the ~600 line. The DRI ruled that the item stays whole up to ~900 (reviews/dri-decisions-20261110-sn-b7b-delta.md
  item 4). With this REPORT and DELTA.md (not counted there), it is about 920.
- Pilot bytes: 0 expected (display only; no unit's status changes; nothing claimed before a pilot audit).

## Tests run

- While iterating: `uv run pytest -q tests/test_senses_display.py` (34 passed) and `tests/test_senses_display_cli.py`
  (10 passed); `uv run python tools/relay_lint.py`: "PASS ... 4 senses module(s), no English reader";
  `tools/check_python_layers.py`: "Contracts: 1 kept, 0 broken".
- `uv run python tools/regen_generated.py --write` once (the codemap), committed in `5de455d23`.
- Final selected run, on the committed, clean tree: `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base
  c94ad399b --run`. It ran on GitHub Actions, 4 shards (25, 33, 24 and 22 units). Result: "exit=0; 1017s", "recorded … units
  for tree 96360f1a7f; … 0 failed". No test of main-known-red.txt failed or was touched.
- Not run: the full gate (the chain runs it), lake build and `lean/audit.py` (no Lean changed).

## Spec re-read

- The body is Lean's preamble lines, then the renderer over the projected environment, then the re-read. Checked against
  docs/spec/senses-PLAN.md:837 and 2.8 :400.
- The candidate is rendered under `senses.project` of its lines and never the base. Checked against :411-412.
- The re-read is Lean's. Checked against reviews/dri-decisions-20261101-sn-b7b8-reread.md item 1 and docs/senses/sn-b6d/REPORT.md (1).
- The reading set has `status: open`, `who: senses`, `why` from Lean's text and the models by id. Checked against
  senses-PLAN.md:837 and ve/readings.py:146-311.
- A one-candidate unit gets no set. Checked against 6.8 g9 (:1084).
- The `undistinguished` rule. Checked against 2.6 step 7 (:348-353).
- The contract has only the members on main. Checked against the task's (4).

## Self-review (SELF_REVIEW_SUBAGENT)

SELF-REVIEW: 2 A, 5 B, 9 C; fixed 15. The fixes:
- `lacking` now comes from Lean (A1). Re-read bytes are charged (A2).
- DELTA rows, signed by the DRI (B1).
- ResourceLimit for budget ends (B2).
- A real gloss-on-default seeded bug (B3).
- Error-exit tests (B4).
- The size ruling (B5).
- Eight of the nine C notes: the rename, last-unit fuzz, `unproposed`, `review_status`, stdin, atomic write, the help text, and the glossary-follows test. The codemap note was covered by the regen.

Open: C "an old `--output` file is left in place" is answered by `output_written` rather than by deleting the file.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: PASS. No new relay field; the members are typed by `ve/backends/senses.py` (sn-b6b/c/d's fuzz tests). The display's own reads fail closed: `::test_a_reread_bound_to_another_formula_or_projection_is_refused`, `::test_a_candidate_is_shown_only_when_leans_reread_is_same`.
2. Every deliverable built, no rule broken: PASS. Deliverables table above; relay_lint PASS; no overlapping branch (checked with `git diff --name-only main...<branch>`).
3. Tests can fail: PASS. 11 seeded bugs, each failing its test (mutants.json).
4. Valid inputs still pass: PASS. The genuine fixtures above, and a preamble written with two spaces or wrapped (`::test_the_lines_a_candidate_lacks_…`).
5. R8 binding: PASS. Re-read fields are rebound (formula, mark `0`, units, the last unit, identities, status): `::test_a_reread_bound_…` (11). A patched projection is refused: `::test_a_two_sentence_candidate_…`.
6. Gate evidence matches the final HEAD: PASS. The selected run was on the committed tree `5de455d23`; the full gate is run by the chain.
7. Deadlines and budgets: PASS. Limits are charged before any call: `::test_each_lines_is_projected_once_within_the_limit`. Budget ends are ResourceLimit: `[status-budget]`, `[unknown-ResourceLimit]`.
8. Kind folds: N.A. No kind fold.
9. Nothing displayed without passing the parser: PASS. Every rendering is re-read by Lean before it is shown (body and candidates; tests above).
10. Entry points: PASS. The render view and both commands call the same `display` functions; `::test_render_senses_cli_shows_leans_reading_and_the_checked_candidates` compares the CLI with `display.glossary`/`hover`.
11. No regex of a real language: PASS. No regex is added.
12. State machine: N.A.
13. Test-removed trailers: PASS. The rename has a trailer in `2799c7657`.
14. Both directions, cited evidence, spec re-read: PASS. "Both sides" row, the commands cited above, and the spec re-read section.
15. No overclaim, no silent cut, checks can fail, limits before work: PASS.
    - The cuts carry DRI rulings: g2's line goes to sn-b6f/sn-b7c, the switched body to sn-b7d, and the size has its ruling.
    - Each check has a seeded bug.
    - Both limits are charged before any service call.

FOLLOW-UP: sn-b7c senses display: g1, g4, g6, g7 after the R3 decision, g5 after sn-b6e, g2's printed glossary line after sn-b6f
FOLLOW-UP: sn-b7d renderer wording for glossed senses, so a body with a switched occurrence renders and re-reads
