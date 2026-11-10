# et-5b delta: Lean's document route admits `events@0`; the open anchor term; "always" and "eventually"

Base: `git merge-base HEAD main` (`c94ad399b`). et-5b is the second part of batch ET-5 of
[events-time-causation-PLAN.md](../../spec/events-time-causation-PLAN.md) (etc-rev, a7e426fa9); see [REPORT.md](REPORT.md).

**Everything else: no change.** A document or route case whose environment lists no `events@0` takes the same path
as before: `eventsView` returns its environment unchanged, `Env.events` is `none`, and `check` calls `layeredOf` as
before (guard: `RouteExamples.lean`, the control `layeredCase ndListed`; the document goldens and
`tests/data/route-cases.jsonl` in the selected run, REPORT "Tests"). A list with `events@0` but without `soft-norms@0`,
or with `rights@0`, or a senses document, keeps the base's refusal word for word
(`test_a_list_off_the_soft_chain_stays_unavailable`). `layeredOf`, `requestOf` and their theorems
(`DocumentChain.layeredOf_soft`, `layeredOf_ids`, `requestOf_environment`) are unchanged; no theorem statement is added
or changed. The catalogue's new rows are read by no Python entry: `ve/english.py` reads the `fixed` rows only, and
`advice` reads the `authored` frame only (guard: the twelve-row advice list in `SourceWordsExamples.lean`, unchanged).
The legend lines are a Lean definition with guards; no answer shows them yet (REPORT, not delivered). No limit changed.
Pilot bytes: 0 expected (an estimate: no pilot document lists `events@0` yet).

## User-visible deltas

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | A document listing `events@0` with `soft-norms@0` (and no `rights@0`) was `CheckerUnavailable: document checks under events@0 need its Lean profile route` and is now checked by Lean's document mode: the composition gate's row (`UnsupportedProfile: events@0 requires <p>` / `with <p>`), the block through `decodeEvents` (spec 4 items 2-7, their texts unchanged), then on the document route `LinkNotOpen: <p>` against the front matter's open terms, `AnchorNotOpen: date_of_this_document` and `AnchorOpen: <candidate>`; a document that passes is CHECKED as the soft chain checks it, with the block's pack. A list the route does not compose (for example with `readings@1`) gets that route's existing `CheckerUnavailable` text | one document per spec 2.9 item 1-8 in `lean/VE/Service/EventsDocumentExamples.lean` (section "Spec 2.9"), T15-T17's shapes there; `tests/test_events_document.py` (relay end to end, the date limit at 64/65, malformed block members) | SIGNED by the DRI 2026-11-10 (reviews/dri-decisions-20261110-et-5b-df-5b.md item 1) |
| 2 | English answers carry `actions_version` 47 (was 46) in their identities: base spec 2.12 raises it on every change to a trusted grammar file (here `SourceWords.lean`, and `SourceReader.lean`, which joins the hashed list). Nothing is removed or renamed | `uv run python tools/english_grammar_gen.py --check` passes; the goldens that carry the version are from `tools/regen_generated.py --write` | SIGNED by the DRI 2026-11-02 (reviews/dri-decisions-20261102-jt-3p.md item 3) |
| 3 | Trust growth, measured with `uv run python tools/trust_map.py --check` against `c94ad399b7b1`: K +0, S +0, untied V +104, unclassified 0; one allowance in `docs/trust-baseline.json`. Per file: `VE/Service/Document.lean` +40 (D[V]: `eventsView`, `eventsLayeredOf`, the `environmentOf` and `check` hunks), `VE/EnglishGrammar/SourceReader.lean` +33 (G[V]: `ruleVerbs`, `RuleContext`, `ruleContext`, `AnchorState`, `rowOf`, `sourceReadings`), `VE/EnglishGrammar/SourceWords.lean` +31 (G[V]: the five rows). Every new trusted definition has a mutant a named guard kills (`mutants.json`, L1-L17); the ties pass is FOLLOW-UPS.md "## et-5b (2026-11-10)" | `mutants.json`; `tools/trust-classes.json` | R16 |
