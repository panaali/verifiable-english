# sn-b7b8 REPORT: senses B7 (the display) and B8 (starter packs and the measurement), one stack

Status: row 1 (sn-b7) built as cut by the DRI (reviews/dri-decisions-20261101-sn-b7b8.md and `-reread`); row 2
(sn-b8) below. HEAD: see `git log -1`. No DRI signature is reserved; DELTA.md has no row (no existing output
changes). Trust +0 in both rows (`tools/trust_map.py --check`). Cut: sn-b7b (and sn-b7c on R3); see each row.

## sn-b7

Row start: the merge base `e63bae651`. Row end: `375109c1b` (this REPORT section is the row's last commit).
Lines: `git diff --numstat e63bae651 375109c1b` without generated files: 378 added, 4 deleted.

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
