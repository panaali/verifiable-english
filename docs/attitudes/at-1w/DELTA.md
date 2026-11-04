# at-1w delta: `reports@0`'s `wants` test moved into Lean (`VE.Reports.wantsPhrase?`)

Base: `git merge-base HEAD main` (94580b39b). Plan: docs/spec/attitudes-PLAN.md "AT-1w" (at 7c5c13cf0); spec
docs/spec/attitudes.md section 10 item 6 (at 03732731e).

**No `reports@0` English answer changes.** The parity table `tests/data/reports_wants_parity.json` is the deleted
`_infinitive` and `_finite` on every phrase the suite's `reports@0` English cases reach (3 of each), plus 83 probes
of their branches (`docs/attitudes/at-1w/record_parity.py`, run on a checkout of 94580b39b). Lean's kind answers every
row the same (`tests/test_reports_wants.py::test_the_kind_answers_the_parity_table_on_every_row`), and
`tests/test_report_english.py` with `tests/test_reports.py` give 55 passed both on 94580b39b (the recorder's own
pytest run) and on this branch. No verdict, diagnostic, fault order or English line changes, so none is a row below.

## User-visible deltas

| # | Delta | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted Lean V +47 in `lean/VE/Attribution/Words.lean` (`wantsPhrase?`, `finitePhrase`, `baseOf`, `headRest`, `vowel`), replacing `ve/report_english.py`'s `_infinitive` and `_finite`, deleted in the same change | `uv run python tools/trust_map.py --check` on the final code; allowance in `docs/trust-baseline.json`; trust mutants `docs/attitudes/at-1w/trust-mutants.json` | R6 |
| 2 | Trusted Lean V +38 for the kind's relay plumbing: `lean/VE/Attribution/Run.lean` +23 (`runWants`, its dispatch line in `runCase`), `lean/ResponseShape/Schemas/Reports.lean` +15 (`wants` and its `kind`, `row` and `file` entries); K +0, S +0; every selected trusted definition has killed mutants (204 KILLED, 0 SURVIVOR, 0 UNKNOWN); ties-pass row in manage-agents FOLLOW-UPS.md "## at-1w" | the same measurement and evidence file | R16 |
| 3 | The `reports` mode answers one new kind, `reports-wants` (`{"phrases", "infinitives"}`, lists of strings): one row per phrase sent, `{"phrase", "infinitive": string or null}`, and one per infinitive, `{"infinitive", "finite"}`, typed in `reports.json` and bound to the request by `x-zip`/`x-equals`; Python checks the binding again (`ve/reports.py` `_bound`): each phrase answered once, in order, nothing extra. A malformed list is `InvalidInput: reports-wants <field> must be a list of strings`; a request over `max_source_bytes` (its strings' UTF-8 bytes, one more per string) is `ResourceLimit: reports-wants phrases exceed max_source_bytes` | `tests/test_reports_wants.py::test_every_retyped_or_rebound_row_is_refused_by_the_schema`, `::test_every_rebound_row_is_unavailable_to_the_document`, `::test_a_malformed_request_is_invalid_input`, `::test_the_request_is_charged_against_max_source_bytes`; `lean/VE/Attribution/Run.lean` `#guard`s | R8 |
| 4 | Generated files: `ve/backends/lean_service_schema/reports.json`, `lean/checkers.lock`, the Lean inventories (`lean/declarations.txt`, `lean/axioms.txt`, `lean/predicates.txt`, `lean/ResponseShapeAudit.lean`), the code map and the binding census, through `uv run python tools/regen_generated.py --write` | `uv run python tools/regen_generated.py --check` | R12 |
