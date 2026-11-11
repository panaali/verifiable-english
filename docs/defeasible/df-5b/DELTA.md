# df-5b: user-visible delta

Feature item df-5b (batch DF-5's command-line part; `docs/spec/defeasible-PLAN.md` DF-1b and DF-5, spec
`docs/spec/defeasible.md` 8.6). No Lean line changes, so there is no trust row. Bytes 0.

**What changes for users:** `ve document readings PATH --conclusion Q --assume-no-exception`, where Q is a JSON object
naming a `situation`, is asked at that situation. Every other call prints the same bytes as on main
(`docs/defeasible/df-5b/fixtures/unchanged.json`, recorded with main's Python;
`test_every_other_call_prints_what_it_printed_before`; the document corpus's saved answers,
`tests/test_document_chain.py::test_f2_3_every_answer_equals_the_retained_loaders`).

**Fault order (R2), within the new path:** the document loads (Lean's checks, including the `weighing@0` refusal), then
the flag's refusals (`--under`/`--sentence`/`--narrowing`, the document's kind, the question's members, asserted
facts), then Lean's layered `norm-defaults-elaborate` row (X's labels, which a `noCompletion` answer binds to), then
Lean's answer to the zone request.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| D1 | On main, a question object with `situation` was refused: `SyntaxError: AST nodes must be nonempty tagged JSON arrays` on a soft-norms document, `CheckerUnavailable: ReadingsConformance: Lean refused the readings-verdicts case Python built: array expected` on one with a content-bearing set (now the flag's existing `--assume-no-exception applies to a soft-norms@0 document without open reading sets`). Now df-5's `defaults-zone` request is sent through `ve.defaults` (`ask_zone`: R8 schema and binding only) and Lean's bound answer is printed as `{"question": "default", "kind": "defaults-zone", "answer", "english"}`. The English is the DE10/DE10′/DE10″, DE10f, DE11 and DE13 rows Lean chose, each passed through W7's all-derivations gate (an ambiguous sentence is refused with W7's `InvalidInput: S2 wording <row> has <n> derivations: <text>`; the gate also reads DE11 after DE6′, whose sentences on every fixture are unchanged). The route's own refusals are `InvalidInput: a question at a situation has the members situation, record, observations, query`, `InvalidInput: a question at a situation takes its facts from the situation; the document asserts some`, and the existing flag refusals. A `weighing@0` document is refused with Lean's text, as the service mode refuses it (condition (iii) as restated, reviews/dri-decisions-20261110-df-5b.md item 3) | SIGNED by the DRI 2026-11-10 (reviews/dri-decisions-20261110-et-5b-df-5b.md item 2) | `tests/test_defaults_zone_cli.py`: `test_every_cli_fixture_answers_as_the_service_mode` (condition (ii), DF-μ, DF-μ′, DF-μ″, DF-δz, DF-ξ, DF-ξ′, DF-π′, plus a record and X's labels), `test_situated_routing_and_refusals`, `test_weighing_documents_are_refused_by_lean_on_the_cli_path`, `test_w7_*` |
