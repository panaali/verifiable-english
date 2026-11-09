# et-5 delta: `events@0`'s source-word rows, their advice, the lint registration, the bound relay

Base: `git merge-base HEAD main` (`61a11aa21`, after the main merge of 2026-11-09). et-5 is the first part of batch ET-5 of
[events-time-causation-PLAN.md](../../spec/events-time-causation-PLAN.md) (etc-rev, a7e426fa9); see
[REPORT.md](REPORT.md).

**Everything else: no change.** Lean's environment mode still refuses an `events` block (`InvalidInput: invalid
environment envelope`), and Python's `Environment` is built only after it, so no document, English reading or pilot
output moves. The lint registration in `ve/english.py` applies only where Python holds an events block. That happens
only in `ve.events.english`, a new entry that reads a document only after Lean's norm-defaults route has accepted
it. No lint answer of any existing entry changes. Lean's own English policy (`policyOk`) has no such registration yet;
the two lints can disagree only on an events block, which no Lean mode accepts before et-5b. `ve/events.py` is a new
relay of fields et-4b already answers. It only refuses: a row that fails its schema or its binding is `CheckerUnavailable`. No verdict, statement or limit
changed. Bytes 0.

## User-visible deltas

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | Trust growth, measured on the final tree with `uv run python tools/trust_map.py --check` against `61a11aa21edc`: K +0, S +0, untied V +76, unclassified 0, PASS, one allowance in `docs/trust-baseline.json`. Per file: `VE/EnglishGrammar/SourceWords.lean` +67 (the rows, G[V] in `tools/trust-classes.json`), `VE/EnglishGrammar/Advice.lean` +9 (`sourceWordAdvice`, `adviceTable`, G[V]); the helpers of `SourceWordsExamples.lean` are T. The FOLLOW-UPS row "## et-5" asks for the ties pass | [trust-mutants.json](trust-mutants.json) with [trust-mutants-allow.json](trust-mutants-allow.json); [mutants.json](mutants.json) (one hand mutant per behaviour, each killed); the guards of `SourceWordsExamples.lean` | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 2 | Added advice. A sentence with no reading, or one that names a sentence in its refusal, under a list with `events@0` now gets Lean's advice for the twelve source words of plan 2.7: `{"id": "events-<word>", "text": <2.7's advice>}`. The `english.grammar` export lists those twelve rows after the existing ones. The status, code, text and span are unchanged, and no row is removed or renamed. The advice names no id or position. The patterns are the words of 2.5's table, so "by", "while" and "since" also match a passive, contrastive or causal use: advice is text only and is given only to a sentence that already has no reading | `SourceWordsExamples.lean`: one sentence per word gets its row's id, "until" its exact text, and a list without the profile gets none. `tests/test_events_wordings.py::test_the_fixed_rows_are_read_from_leans_catalogue` reads the twelve rows from the generated view | SIGNED by standing ruling R3 (DRI-RULINGS.md) |
| 3 | English answers carry `actions_version` 46 (was 45) in their identities: base spec 2.12 raises it on every change to a trusted grammar file (here `Advice.lean`, `Run.lean`, `SourceWords.lean`). Nothing is removed or renamed | `uv run python tools/english_grammar_gen.py --check` passes; the goldens that carry the version are from `tools/regen_generated.py --write` | SIGNED by the DRI 2026-11-02 (reviews/dri-decisions-20261102-jt-3p.md item 3) |
