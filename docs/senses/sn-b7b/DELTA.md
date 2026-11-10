# sn-b7b DELTA: user-visible changes of `ve render --view ve_english --senses`

The two new commands (`ve senses resolve`, `ve senses propose-readings`) and the two new options (`--glossary`,
`--json`) are new outputs, not deltas. The rows below are the changes to the existing `ve render --senses` output
(reviews/dri-decisions-20261110-sn-b7b-delta.md, which corrects item 3 of reviews/dri-decisions-20261110-sn-b7b.md).

| # | Delta | Ruling | Evidence (tests that stay selected) |
|---|---|---|---|
| 1 | New members `text` and `body_status` (the checked body: Lean's preamble lines, then the rendering, re-read by Lean), and `renderings[].lacking` (the last len(choice) lines of Lean's `lines`, the choice's lines by `senses_candidate_sound`). Nothing removed or renamed | R3 | `tests/test_senses_display.py::test_the_body_is_leans_preamble_then_the_rendering_reread`, `::test_the_lines_a_candidate_lacks_are_those_not_in_leans_preamble` |
| 2 | A candidate of a document whose other sentences use other words was exit 5 (`CheckerUnavailable`: sn-b7 re-read its lines and its sentence alone) and is now shown, exit 3: the re-read is sn-b6d's Lean `reread` member under the candidate's own projection | SIGNED by the DRI 2026-11-10 (reviews/dri-decisions-20261110-sn-b7b-delta.md item 2) | `::test_a_two_sentence_candidate_rereads_and_a_patched_projection_is_refused` (a patched projection is still refused), `::test_a_tampered_rendering_is_checker_unavailable` |
| 3 | A status-one document gains the body re-read: a body whose rendering does not re-read now exits 5, and one whose re-read ends its budget exits 4, where both exited 0 | SIGNED by the DRI 2026-11-10 (reviews/dri-decisions-20261110-sn-b7b-delta.md item 3) | `::test_the_body_is_leans_preamble_then_the_rendering_reread`, `::test_render_senses_cli_tampered_rendering_is_checker_unavailable`; the budget exit: `::test_a_reread_bound_to_another_formula_or_projection_is_refused[status-budget]` (body) and `::test_a_candidate_is_shown_only_when_leans_reread_is_same[unknown-ResourceLimit]` (candidate) |
