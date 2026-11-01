# sn-b7b8 REPORT: senses B7 (the display) and B8 (starter packs and the measurement), one stack

Status: both rows built and cut at their size lines; sn-b7 as the DRI cut it (reviews/dri-decisions-20261101-sn-b7b8.md
and `-reread`); review F1 (B) fixed ("Fix round" at the end). HEAD: see `git log -1`. What changed: `ve render --senses`
shows each open unit's candidates, rendered and re-read by Lean under their own projections; two starter packs, pinned,
and the 7.2 coverage table. Open: sn-b7b, sn-b7c (needs the R3 decision), sn-b8b (rights@1, risk@1, the propose tool).
No DRI signature is reserved; DELTA.md has no row; trust +0 in both rows (`tools/trust_map.py --check`).

## sn-b7

Row start: the merge base `e63bae651`. Row end: `f5308e9ff` (its REPORT section; the code ends at `375109c1b`).
Lines: `git diff --numstat e63bae651 f5308e9ff` without generated files (codemap, `.importlinter`): 479 added, 4
deleted (378 before this REPORT section).

### What was delivered, and the DRI's two decisions

B6 shipped fewer `senses.read` members than B7's plan row assumes. The DRI ruled (dri-decisions-20261101-sn-b7b8.md
item 1, SIGNED) that sn-b7 delivers only the part that needs none of them: each candidate of an open unit rendered
under the projection `senses.project` returns for its resolving lines, re-read by Lean under that same projection,
`CheckerUnavailable` on a mismatch, shown with its Lean lines. The rest is sn-b7b (after sn-b6b and the new Lean
row sn-b6c) and sn-b7c (the four fixtures that need the spec's request R3 to S2). The building found one more gap:
Lean's `english.check` (`checkRendering`) runs S2's `policyOk` and refuses every projection's decorated wordings
(`invalidGrammar lexicon: V6 predicate sense__funny_2`). The DRI's follow-up (dri-decisions-20261101-sn-b7b8-reread.md,
SIGNED) has the re-read done by Lean's senses reader instead: `senses.read` on the candidate's Lean lines, a newline
and the rendering, accepted only with status `one`, one unit of exactly the candidate's formula and mark, and the
candidate's projection identities. The edits of debates/plan-synthesis-2/edits-senses.md (D7: senses has its own
route) are as B6 applied them; this row implements none of them anew.

| Plan item (senses-PLAN.md 837, 884-891; 6.8) | State | Where | Test |
|---|---|---|---|
| (1) `ve render --view ve_english --senses PACK`: preamble lines, the body rendered, `checkRendering` | partly: the option exists and prints Lean's reading with the candidates' renderings; the body and preamble need the preamble-lines member: **sn-b7b** (a) | `ve/__main__.py` `_render_senses` | `tests/test_senses_display.py::test_render_senses_cli_shows_leans_reading_and_the_checked_candidates`, `::test_render_senses_cli_refuses_another_view`, `::test_render_senses_cli_tampered_rendering_is_checker_unavailable` |
| (2) each candidate rendered under `senses.project` of its resolving lines, re-read under the same projection, never the base one | yes (as the DRI cut it) | `ve/senses/display.py` `candidates`, `reread` | `::test_two_candidates_each_reread_under_its_own_projection`, `::test_one_candidate_reread_under_its_own_projection`, `::test_a_base_projection_rendering_fails`, `::test_a_base_projection_is_not_the_candidates`, `::test_a_reread_under_another_projection_is_refused` |
| shown with the lines the document lacks | the candidate's resolving lines (Lean's `lines`) are shown; which of them the document lacks needs the preamble member or the Unresolved text: **sn-b7b** (a, c) | | |
| (3) `--glossary`, `--json` with byte spans | **sn-b7b** (b, e) | | |
| (4) `ve senses resolve`, `ve senses propose-readings` | **sn-b7b** (d, f) | | |
| (5) the web-app JSON contract | yes, for the members on main; the members to come are listed, not specified | `docs/spec/senses.md` 2.7.1 | |
| evaluated once, against a stated limit | yes: one `senses.project` per distinct resolving lines; at most `MAX_CANDIDATES` (64) candidates per call, charged before any service call | `display.MAX_CANDIDATES` | `::test_each_lines_is_projected_once_within_the_limit` (limit and limit+1) |
| both sides | a rendering that re-reads and one that does not (tampered, unreadable), two candidates and one | | `::test_a_tampered_rendering_is_checker_unavailable`, `::test_a_rendering_that_does_not_read_is_checker_unavailable` |
| R8 binding of what the display reads | the re-read's status, unit count, formula, mark (`True` vs `0`) and three projection identities, each rebound | | `::test_a_reread_bound_to_another_formula_or_projection_is_refused` (8 cases) |

Fixtures g1 to g10:

| Fixture | State |
|---|---|
| g1 (J renders with its preamble and one gloss) | sn-b7c: J reads `none` as merged; needs R3 (and (a) for the preamble) |
| g2 (`--glossary`) | sn-b7b (e) |
| g3 (`--json` byte spans) | sn-b7b (b) |
| g4 (s2's two candidates) | sn-b7c (R3); its mechanism is delivered on the as-merged two-candidate fixture `The riddle is funny.` |
| g5 (s10, S2's `none` text and the suggestion) | sn-b7b (c: GlossedNatural is not computed in Lean) |
| g6 (`ve senses resolve` on s2) | sn-b7c (R3) and (f) |
| g7 (`propose-readings` on s2) | sn-b7c (R3) and (d) |
| g8 (the mixed warning) | sn-b7b (c: no Mixed text in Lean) |
| g9 (s16 through the CLI) | the candidate's rendering and re-read: delivered (`::test_one_candidate_reread_under_its_own_projection`); the one-candidate text and `resolve`: sn-b7b (c, f) |
| g10 (s17's CandidatesDiverge text) | sn-b7b (c: no CandidatesDiverge text in Lean; the fault carries code and details only) |

Not duplicated: no Python text of a sense outcome (`uv run python tools/relay_lint.py`: "4 senses module(s), no
English reader", `ve/senses/display.py` added to its senses path); no Python projection (the environment comes from
`senses.project`); `suggest_vocabulary` and `ve propose` are not touched.

Found for sn-b7b: Python's renderer cannot word a decorated sense (`{0} is funny (meaning strange)`); it writes
`The riddle is classified as "sense__funny_2".` (probe in `::test_a_base_projection_rendering_fails`'s setup).
So today the re-read catches a base-projection rendering because that text does not read. Once the renderer words
glossed forms, a glossed default re-reads to the same formula (spec s8), and only the exact-text assertion of
`::test_two_candidates_each_reread_under_its_own_projection` would catch it.

### Seeded bugs (docs/senses/sn-b7/mutants.json; Python only, no Lean or Rust changed)

| Id | Bug in `ve/senses/display.py` | Failing test |
|---|---|---|
| S1 | candidate rendered under the base projection (the plan's seeded bug) | `::test_two_candidates_each_reread_under_its_own_projection` ("does not re-read under its projection") |
| S2 | the projection's identities not bound to the candidate's | `::test_a_base_projection_is_not_the_candidates` |
| S3 | the re-read's mark not bound | `::test_a_reread_bound_to_another_formula_or_projection_is_refused[mark-True]` |
| S4 | the re-read's projection identities not bound | `::test_a_reread_under_another_projection_is_refused` |
| S5 | the candidate limit off by one | `::test_each_lines_is_projected_once_within_the_limit` |

Each was planted, its one test run alone failed ("1 failed"), and the file was restored (`cmp` with the saved copy).

### Trust, bytes, runs

- Trust: `uv run python tools/trust_map.py --check` on `e178d5cbd`: "K +0, S +0, D +0, G +0, tied +0, unclassified
  +0, trusted +0 … PASS". No Lean changed.
- Pilot bytes: 0 expected (display only; no unit's status changes).
- `uv run python tools/regen_generated.py --write` once (layer row): exit 0; `tools/repo_map.py --check` PASS;
  `tools/check_python_layers.py`: "Contracts: 1 kept, 0 broken".
- Selected tests (`mac-pytest.sh --select -- --base e63bae651 --run`, ve-mac-1, `e178d5cbd`, 239 units): 235 units
  exit 0; `tools/test_layer_policy.py` failed (`senses.display` missing from docs/ARCHITECTURE-LAYERS.md), fixed in
  the next commit and rerun (`mac-pytest.sh -- tools/test_layer_policy.py`: "48 passed", on the VM, the Mac being
  unreachable). The run's wrapper was stopped at its time limit before chunk 3/4 of `tests/test_trust_mutants.py`
  finished (Lean trust mutants; row 1 changes no Lean); not rerun, the chain gate runs it.
- Not run: the full gate (the chain runs it on the final HEAD).

### Next

sn-b7b (after sn-b6b and sn-b6c): the rendered body with Lean's preamble lines, `--glossary`, `--json` hover,
the 3.2 texts, `ve senses resolve`, `propose-readings`. sn-b7c: g1, g4, g6, g7 after the R3 decision
(sn-r3-decision).

## sn-b8

Row start: `f5308e9ff`. Commits: `b58ff3283`, `c76a9f466` and this REPORT section. Lines: `git diff --numstat
f5308e9ff c76a9f466` without generated files: 526 added, 1 deleted, plus 85 lines of `coverage.json` (written by
the coverage script) and about 90 of this section. That is about the ~600 line, so the rest is cut, as below.

### What was delivered, and what is cut to sn-b8b

The edits of debates/plan-synthesis-2/edits-senses.md: this row implements none of them (D7's route is B6's).

| Plan item (senses-PLAN.md 838, 893-895; 7.2; Q3) | State | Where | Test or evidence |
|---|---|---|---|
| (1) `policies@1` (agent-policy, cedar-attributes) | yes: 6 sorts, 16 senses, each cited | `ve/senses/packs/policies@1.json`, `docs/senses/sn-b8/SOURCES.md` | `tests/test_senses_packs.py::test_each_pack_decodes_by_leans_wf[policies@1]`, `::test_a_malformed_copy_reaches_the_cli_with_leans_text[policies@1]` |
| (1) `software-services@1` (fluent, assist) | yes: 2 sorts, 4 senses; the readability eval not located as a source | `ve/senses/packs/software-services@1.json` | the same two tests `[software-services@1]` |
| (1) `rights@1` (UDHR pilot) | **sn-b8b**: size line. The pilot's vocabulary is spread over the companion environments of its readings (76 predicates, 13 with a simple wording, e.g. `{0} is entitled to a nationality`, `{0} is protected by law`), and its readings are norms, not sentences S2 reads, so its table rows need their own input step | | |
| (1) `risk@1` | **sn-b8b**: the last pack. No surveyed risk source (openai-preparedness, safety-framework, anthropic-rsp, asimov) declares `severe`, `avoidable` or `leads to` with a simple wording (`severe` is "{0} meets the severe-harm criterion", no verbalisation) | | |
| one fixture per pack that decodes, one malformed copy whose Lean text reaches the CLI unchanged | yes | | the four tests above: the CLI's reading equals the relay's, `InvalidDictionary` with Lean's W3 failure |
| (2) each pack pinned in `ve/senses/reviewed-packs.json` (digest, reviewer, date, file, scope) | yes; the digest is Lean's `dictionary_id` of the pack alone (Q9); the reviewer is `sn-b7b8 chain review (sn-b7b8-review.final.md)`, which reads every entry against SOURCES.md; a pack the review changes is re-pinned in the fix round | | `::test_each_pin_is_leans_identity_of_the_pack_bytes` (reviewed, and one changed byte unreviewed), `::test_every_starter_pack_is_pinned_and_the_fixture_pack_is_not` |
| i4's unreviewed path unchanged | yes (`ve.senses.review_status` untouched) | | `tests/test_senses_pack.py::test_fixture_pack_is_unreviewed` |
| (3) `conformance/senses_usecases.py` and its table | yes, for the two packs' use cases | `docs/senses/sn-b8/coverage.json` | `::test_a_sentence_that_reads_the_same_under_the_pack`, `::test_a_sentence_that_needs_a_line`, `::test_a_sentence_that_no_longer_reads_keeps_leans_reason`, `::test_a_sentence_the_base_does_not_read_is_counted_apart`, `::test_same_formula_up_to_renaming`, `::test_a_renaming_is_one_sense_id_per_predicate_over_the_use_case` |
| declaration lines and negatives (7.2) on the same inputs | yes (after: the pack lines, F1) | `coverage.json` `declaration_lines`, `negatives_removed` | `::test_after_counts_the_pack_lines_the_covered_predicates_need`, `::test_the_saved_table_counts_the_pack_lines_after`, `::test_a_covered_word_that_is_not_one_sense_line_stops_the_measure`, `::test_declaration_lines_and_negatives_count_the_covered_entries` |
| read per sentence, every value once, within the existing limits | yes: each sentence once on each side, through the relays' limits (work budget 2,100,000; `MAX_SOURCE_BYTES`); the largest input, agent-policy's 533 sentences, ended in 4 min 59 s | | the `--write` run below |
| Q3 | counted: 0 in the two packs' sources (SOURCES.md, Q3) | | |
| (4) `tools/senses_propose.py` | **sn-b8b** (the cut order puts it first); and the repository's OEWN file has lemmas, classes and sense keys but no glosses (`ve/lexicon/oewn-2025.json` columns), so its gloss drafts need another source | | |

### The table (7.2), from `docs/senses/sn-b8/coverage.json`

Run: `uv run python conformance/senses_usecases.py --write` (4 min 59 s), output
`{"agent-policy": {"sentences": 533, "base_unread": 74, "same": 459}, "cedar-attributes": {"sentences": 1, "same": 1},
"fluent": {"sentences": 6, "same": 6}, "assist": {"sentences": 5, "same": 2, "base_unread": 3}}`.

| Use case (pack) | Sentences | Same up to renaming | Need a line | Switched | No longer read | Base does not read | Declaration lines before / after | Negatives removed |
|---|---|---|---|---|---|---|---|---|
| agent-policy (policies@1) | 533 | 459 | 0 | 0 | 0 | 74 | 74 / 22 | 9 |
| cedar-attributes (policies@1) | 1 | 1 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| fluent (software-services@1) | 6 | 6 | 0 | 0 | 0 | 0 | 14 / 5 | 1 |
| assist (software-services@1) | 5 | 2 | 0 | 0 | 0 | 3 | 9 / 4 | 0 |

Every sentence the base reads also reads with the pack, with the same formula up to renaming each covered
predicate to its sense id (the renamings are in `coverage.json`). No sentence needs a line or a switch, because no
word of the two packs has two senses (Q3: 0). The base's own refusals are kept with Lean's code and text: the 26
policy rules are norm sentences ("may be performed") that S2's relational reader does not read; in assist, "the web
front end" is refused by S2's spelling policy, and the claim read alone has no premise (`ConclusionWithoutPremise`).
cedar's one predicate is not packable (a `$string` kind), so its sentence reads unchanged with no renaming.
Declaration lines (plan 7.2's use-case measure, fixed in the review round, F1): before, one per declared field of
each covered predicate (environment and overlay); after, the pack lines those predicates need, each one's sense line
(its word tied to its sense id by Lean's `senses.project`) and the sort lines those senses name: agent-policy 16 + 6,
fluent 3 + 2, assist 3 + 1, cedar none (`pack_senses`, `pack_sorts` in `coverage.json`). The preamble lines the
sentences need are counted apart (`preamble_lines`: 0 in every use case). What this does not measure: the rights and risk use cases (sn-b8b);
readability or comprehension (plan L1).

### Seeded bugs (docs/senses/sn-b8/mutants.json; data and Python only)

| Id | File | Bug | Failing test |
|---|---|---|---|
| B1 | `ve/senses/packs/policies@1.json` | a wording that drops its word (the plan's) | `::test_each_pack_decodes_by_leans_wf[policies@1]`, with Lean's text "the wording {0} sees {1} of reads does not contain reads exactly once" |
| B2 | `ve/senses/reviewed-packs.json` | a pin digest that is not the pack's (the plan's) | `::test_each_pin_is_leans_identity_of_the_pack_bytes[policies@1]` |
| B3 | `conformance/senses_usecases.py` | a renamed formula counted as different (the plan's) | `::test_a_sentence_that_reads_the_same_under_the_pack` |
| B4 | `conformance/senses_usecases.py` | an open reading's candidates ignored | `::test_a_sentence_that_needs_a_line` |
| B5 | `conformance/senses_usecases.py` | the sort lines left out of "after" (review F1) | `::test_after_counts_the_pack_lines_the_covered_predicates_need[agent-policy]`, `[fluent]`, `[assist]` |
| B6 | `conformance/senses_usecases.py` | the sense lines left out of "after" (review F1) | the same three |
| B7 | `conformance/senses_usecases.py` | a renaming to another sense accepted as the predicate's line | `::test_a_covered_word_that_is_not_one_sense_line_stops_the_measure` |
| B8 | `docs/senses/sn-b8/coverage.json` | the table before the fix (after = preamble lines, 0) | `::test_the_saved_table_counts_the_pack_lines_after` (PROBE F1) |
| B9 | `conformance/senses_usecases.py` | the overlay's fields left out of "before" (review F4) | `::test_declaration_lines_and_negatives_count_the_covered_entries` |

The plan's fourth seeded bug (the propose tool imported from `ve/`) goes to sn-b8b with the tool.

### Trust, bytes, runs

- Trust: `uv run python tools/trust_map.py --check` on `b58ff3283`: "K +0, S +0, D +0, G +0, tied +0, unclassified
  +0, trusted +0 … PASS".
- Pilot bytes: 0 expected (packs and a measurement; no unit's status changes).
- `uv run python tools/regen_generated.py --write` once (new files in the code map): exit 0.
- Selected tests (`mac-pytest.sh --select -- --base f5308e9ff --run`, Claude cloud, 6 shards, `b58ff3283`): 219 of
  220 units passed; `tests/test_regen_generated.py::test_every_script_with_a_writing_mode_is_registered_or_excluded_with_a_reason`
  failed (the script's `--write` mode was not listed). Fixed in `c76a9f466` and rerun (`mac-pytest.sh -- <id>`: "1
  passed", on the VM).
- Not run: the full gate (the chain runs it on the final HEAD).

### Next

sn-b8b: `rights@1` and `risk@1` with their table rows, `tools/senses_propose.py` with its import test; then sn-b10
(the report, G-S2) after sn-b7b, sn-b8b and sn-b9.

## The stack

- Row starts: sn-b7 at the merge base `e63bae651`; sn-b8 at `f5308e9ff`. Every row commit carries `Row: <row>`.
- DRI decisions: reviews/dri-decisions-20261101-sn-b7b8.md (row 1's cut; sn-b6c, sn-b7b, sn-b7c, sn-r3-decision
  filed by the DRI) and reviews/dri-decisions-20261101-sn-b7b8-reread.md (the re-read by Lean's senses reader).
  Their named-test conditions are met in `tests/test_senses_display.py`.
- DELTA.md: no row. Trust: +0 in both rows, so no R16 allowance and no FOLLOW-UPS ties row.
- Known red on main (main-known-red.txt): their files ran in row 1's selection and exited 0
  (`tests/test_lean_service.py`, `tests/test_readings_defaults_rd8_report.py`); none is touched here.
- Follow-ups: sn-b7b (filed by the DRI), sn-b7c (filed by the DRI as part of the R3 path), sn-b8b (below).

## Spec re-read

- senses-PLAN.md:408-412 ("the base projection is never used to render a candidate"): `display.candidates` renders in
  the environment `senses.project` returns for the candidate's `lines`, and binds its identities to the candidate's.
- senses-PLAN.md:356-361 (each candidate's projection is `project D (A.extend choice) E L used`, through
  `senses.project` with its resolving lines): the projection is called with the reading's `used` and the candidate's
  `lines`; the re-read's identities must equal the candidate's.
- senses-PLAN.md:1076-1085 (g1 to g10): each row's state is in the sn-b7 table; no Lean text is printed that Lean did
  not return.
- senses-PLAN.md:838 and 7.2 ("same formula up to the renaming of predicate names to sense ids", "need a preamble
  line", "need a switch", "no longer read, with the reasons"): the four classes of `classify`, plus the base's own
  refusals counted apart.
- senses.md 2.2 W2, W5: the glosses and the dropped negative follow Lean's refusals, quoted in SOURCES.md.
- ve/reviewed-overlays.json's record (digest, reviewer, date, file, scope): each pin has `dictionary_id` (Lean's
  digest, the key `review_status` reads), `reviewer`, `date`, `pack` and `scope`, plus `name`.

## Self-review against BUILDER-CHECKLIST

1. PASS: the display reads only answers the B6 relays have already typed and bound; what it reads from the re-read
   is bound: `tests/test_senses_display.py::test_a_reread_bound_to_another_formula_or_projection_is_refused`.
2. PASS: every plan row and fixture is in the row tables, delivered or cut to a named item by the DRI's decisions
   (sn-b7) or the size line and the task's cut order (sn-b8); `relay_lint.py` PASS; no in-flight branch touches
   these files (checked at the start).
3. PASS: seeded bugs S1-S5 (`docs/senses/sn-b7/mutants.json`) and B1-B9 (`docs/senses/sn-b8/mutants.json`), each
   failing a named test; no trusted Lean, so no trust mutants.
4. PASS: one implementation (Lean); existing `ve render` paths are unchanged (the branch runs only with
   `--senses`; `tests/test_cli.py` exit 0 in row 1's selection); `::test_render_senses_cli_refuses_another_view`.
5. PASS: rebound formula, mark (`True`, `0`), status, extra unit and each identity refused
   (`::test_a_reread_bound_to_another_formula_or_projection_is_refused`); another projection refused
   (`::test_a_base_projection_is_not_the_candidates`, `::test_a_reread_under_another_projection_is_refused`).
6. PASS: synced with main (`d018243cc`, main's jt-e1s docs and test only); regen `--check`: "checked 35 entries"; the
   chain gate runs on the final HEAD.
7. PASS: DELTA.md has no row; trust +0 (`tools/trust_map.py --check`); no signature reserved.
8. PASS: no existing output changes (new option, new files); `ve render` without `--senses` takes its old path.
9. PASS: row 1's selection held `tests/test_senses_display.py` and caught `tools/test_layer_policy.py`; row 2's held
   `tests/test_senses_packs.py` and caught `tests/test_regen_generated.py`.
10. N.A.: no Lean statement or proof changed.
11. PASS: the display charges `MAX_CANDIDATES` before any service call (`::test_each_lines_is_projected_once_within_the_limit`,
    limit and limit+1); budget 0 is the relay's (`tests/test_senses_route.py::test_zero_budget_never_admits`); no
    sleeps or literal timeouts.
12. PASS: one `senses.project` per distinct resolving lines, counted (`::test_each_lines_is_projected_once_within_the_limit`);
    no existing path changed.
13. PASS: no test removed; `tools/gate_collection.py --check --prebuilt`: "38 added, 0 removed by a trailer, 0
    refused, 0 stale and 0 malformed trailers".
14. PASS: both directions for every check (two and one candidate against tampered, unreadable, base and other
    projections; packs that decode against malformed copies; pins reviewed against one changed byte; same, needs a
    line, no longer reads, base unread); claims cite their commands; spec re-read above.

## Fix round (sn-b7b8-review.final.md)

| Finding | Fix | Regression tests | Commit |
|---|---|---|---|
| F1 (B): 7.2's "after" on a use case counted the preamble lines (the joke's measure) | `pack_lines` counts the pack lines the covered predicates need: each predicate names its pack word in `USECASES` (SOURCES.md's last column), Lean's `senses.project` over that word alone gives its one sense id, a renaming the sentences gave must be that id, and the sort lines those senses name are added; a word that is not one sense line stops the measure. The preamble lines are kept apart (`preamble_lines`). Table re-measured: 74 / 22, 0 / 0, 14 / 5, 9 / 4 | `tests/test_senses_packs.py::test_the_saved_table_counts_the_pack_lines_after` (PROBE F1), `::test_after_counts_the_pack_lines_the_covered_predicates_need[agent-policy]`, `[cedar-attributes]`, `[fluent]`, `[assist]`, `::test_a_covered_word_that_is_not_one_sense_line_stops_the_measure` | `dda65fae6` |
| F4 (C, same class: the measure's counts had no test) | tests only | `::test_declaration_lines_and_negatives_count_the_covered_entries` | `dda65fae6` |

- PROBE F1: before the fix `AssertionError: 0`; after it, exit 0 (it is the first test above, over all four rows).
- Seeded bugs B5-B9 (table above, `docs/senses/sn-b8/mutants.json`): each planted, its tests run, the file restored.
  Python and data only; no Lean or Rust changed, so no Lean or Rust mutants.
- DELTA: no row (a batch measurement and its evidence; no user-visible output changes).
- Runs: `--write` 4 min 16 s; `lake build` "Build completed successfully (1211 jobs)"; `python3 lean/audit.py` PASS;
  `regen_generated.py --check` "checked 35 entries"; selected tests (`mac-pytest.sh --select -- --base <merge base>
  --run`, Claude cloud, 4 shards): 241 of 241 units passed. Not run: the full gate (the chain runs it).
- Known red on main (main-known-red.txt): not touched.
- Not fixed here (C, FOLLOW-UP): F2, F3, F5, F6, F7.
