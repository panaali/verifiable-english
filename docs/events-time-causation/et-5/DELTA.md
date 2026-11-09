# et-5 delta: `events@0`'s source-word rows, their advice, the lint registration, the bound relay

Base: `git merge-base HEAD main` (`c2ff64751`). et-5 is the first part of batch ET-5 of
[events-time-causation-PLAN.md](../../spec/events-time-causation-PLAN.md) (etc-rev, a7e426fa9); see
[REPORT.md](REPORT.md).

**Everything else: no change.** Lean's environment mode still refuses an `events` block (`InvalidInput: invalid
environment envelope`), and Python's `Environment` is built only after it, so no document, English reading or pilot
output moves. The lint registration in `ve/english.py` applies only where Python holds an events block. That happens
only in `ve.events.english`, a new entry that reads a document only after Lean's norm-defaults route has accepted
it. No lint answer of any existing entry changes. `ve/events.py` is a new relay of fields et-4b already answers. It
only refuses: a row that fails its schema or its binding is `CheckerUnavailable`. No verdict, statement or limit
changed. Bytes 0.

## User-visible deltas

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | Trust growth, measured on the final tree with `uv run python tools/trust_map.py --check` against `c2ff64751`: K +0, S +0, untied V +93, one allowance in `docs/trust-baseline.json`. Per file: `VE/EnglishGrammar/SourceWords.lean` +65 (the rows), `VE/EnglishGrammar/SourceWordsExamples.lean` +19 (the guards' helpers), `VE/EnglishGrammar/Advice.lean` +9 (`sourceWordAdvice`, `adviceTable`). The FOLLOW-UPS row "## et-5" asks for the ties pass | [trust-mutants.json](trust-mutants.json); [mutants.json](mutants.json) (one hand mutant per behaviour, each killed); the guards of `SourceWordsExamples.lean` | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 2 | Added advice. A sentence with no reading, or one that names a sentence in its refusal, under a list with `events@0` now gets Lean's advice for the twelve source words of plan 2.7: `{"id": "events-<word>", "text": <2.7's advice>}`. The `english.grammar` export lists those twelve rows after the existing ones. The status, code, text and span are unchanged, and no row is removed or renamed. The advice names no id or position | `SourceWordsExamples.lean`: one sentence per word gets its row's id, "until" its exact text, and a list without the profile gets none. `tests/test_events_wordings.py::test_the_fixed_rows_are_read_from_leans_catalogue` reads the twelve rows from the generated view | SIGNED by standing ruling R3 (DRI-RULINGS.md) |
