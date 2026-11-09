# rights-cfr-5 delta: single right lines carry the renderer's header options

Base: `git merge-base HEAD main` (`49f1682dc`). Only `ve/surface/rights.py` (`render_line`, `parse_line`)
changed in product code; no verdict changes; Lean, Rust, schemas and generated files are untouched.

Saved evidence: [header-delta.json](header-delta.json) (`header_delta.py`) runs `parse_line` at the base and on
this item's code over 25 header variants, each with and without a body. 46 inputs answer the same and 4 differ,
listed below. [line-roundtrip-before.json](line-roundtrip-before.json) and
[line-roundtrip-after.json](line-roundtrip-after.json) (`line_roundtrip.py 200`) record what `render_line`
now renders: 71 generated lines that it refused at the base render now.

## User-visible deltas

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | A claim, liberty or immunity with a switch (`alterable`) now renders as `<Kind> of right <r> (<parties> may turn off). …`. At the base, `render_line` refused it with `InvalidInput: rights incident must have one rule`. `parse_line` now reads that line back with its switch. The header is the one norm_english renders (`_SOFT_HEADER` plus `render_header_options((), parties)`, rights.md :228, :436). No other header is accepted: no option, a precedence option, any other spelling, spacing, order, NBSP, tab, CR or full-width parentheses are all refused with the base's text. | header-delta.json rows 3-4 (accepted: `(user may turn off)`, `(operator and user may turn off)`). Condition test: `tests/test_rights.py::test_rights_incident_roundtrip_with_switch`. Negative test: `tests/test_rights.py::test_rights_incident_header_the_renderer_never_writes_is_refused`, which fails on seeded bugs S2, S3 and S6 (REPORT, Seeded bugs). Generated: `tests/test_rights.py::test_generated_rights_lines_round_trip_one_by_one`. | SIGNED by the DRI 2026-11-09 (reviews/dri-decisions-20261109-lp0801.md item 1) |
| 2 | Some headers are in the rendered spelling but name parties the checker refuses: unsorted (`(user and operator may turn off)`) or undeclared (`(guest may turn off)`). They now reach the soft checker, which refuses them with its own diagnostic (`InvalidInput: alterable of rule rule-1 must be sorted and distinct`; `UnknownSymbol: party guest`). The base refused them with `SyntaxError: expected Claim, Liberty or Immunity of right`. They are still refused. The new text keeps every name the base quoted (the base quoted none, and neither side has a path), and it is more specific, because it names the party. | header-delta.json rows 1-2. `tests/test_rights.py::test_rights_incident_header_delta_keeps_base_names_r1` recomputes each saved head answer and checks that the base's quoted names are kept. | R1 |
