# et-5b delta: Lean's document route admits `events@0` on the soft chain; the open anchor term

Base: `git merge-base HEAD main` (`c94ad399b`). et-5b is the second part of batch ET-5 of
[events-time-causation-PLAN.md](../../spec/events-time-causation-PLAN.md) (etc-rev, a7e426fa9); see [REPORT.md](REPORT.md).

**Everything else: no change.**
- A document or route case whose environment lists no `events@0` takes the base's path: `environmentOf`'s profile
  check names the same profile (`events@0` is only ever named where the base named it), `eventsView` returns the
  environment unchanged, `Env.events` is `none`, and `check` calls `layeredOf` as before. Evidence: the document goldens
  and `tests/data/route-cases.jsonl` in the selected run, and `tools/regen_generated.py --write` leaving
  `lean/VE/Route/examples/route-cases.json` unchanged (REPORT "Tests").
- A list with `events@0` off the soft chain (no `soft-norms@0`, or `rights@0` or `readings@1`, or senses), or read on a
  path with no document open terms (the scope block's), gets the base's refusal by the base's own expression
  (`undecided environment "document checks under events@0 need its Lean profile route"`: the environment's own fault
  first, as at base). DRI 2026-11-10 (reviews/dri-decisions-20261110-et-5b.md item 1) keeps these lists refused; the
  plain norm-defaults chain is et-5d's and the rights chain et-5e's. Tests:
  `test_a_list_off_the_soft_chain_stays_unavailable` (the plain list with and without its block, `rights@0` with and
  without), the guards beside "keeps the base's refusal" in `EventsDocumentExamples.lean` and RouteExamples' scope-path
  guard.
- `layeredOf`, `requestOf` and their theorems are unchanged; no theorem statement is added or changed
  (`git diff c94ad399b -- lean/statements.txt` is empty). The English `actions_version` is unchanged (46): the new rows
  are in `SourceWords.lean`, which the grammar's action hashes exclude.
- The catalogue's new rows are read by no Python entry (`ve/english.py` reads the `fixed` rows only) and not by
  `advice` (it reads the `authored` frame only; the twelve-row advice guard in `SourceWordsExamples.lean` is
  unchanged). The legend is a Lean definition with guards; no answer shows it (et-5c, DRI 2026-11-10 item 2).
- No limit changed. Pilot bytes: 0 expected (an estimate: no pilot document lists `events@0` on the soft chain).

## User-visible deltas

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | A document listing `events@0` with `soft-norms@0` (no `rights@0`, `readings@1` or senses) was refused before decoding (`undecided`: the environment's own fault, for example `fields do not match: expected [language, profiles, spec_revision, vocabulary], got [events, ...]`, else `CheckerUnavailable: document checks under events@0 need its Lean profile route`) and is now checked by Lean's document mode: `Events.eventsHook` over the document's `open_terms` (the composition gate's row, `UnsupportedProfile: events@0 requires <p>` / `with <p>`; the block in spec 4's order, items 2-7 with `LinkNotOpen: <p>` after item 5, their texts unchanged), then `AnchorNotOpen: date_of_this_document` and `AnchorOpen: <candidate>`; a document that passes is CHECKED as the soft chain checks it, with the block's pack, its identities bound to the environment as written | one document per spec 2.9 item 1-8 in `lean/VE/Service/EventsDocumentExamples.lean` (section "Spec 2.9"), T15-T17's shapes there; `tests/test_events_document.py` (the relay end to end, the date limit at 64/65, malformed block members) | SIGNED by the DRI 2026-11-10 (reviews/dri-decisions-20261110-et-5b-df-5b.md item 1) |
| 2 | Trust growth, measured with `uv run python tools/trust_map.py --check` against `c94ad399b7b1`: K +0, S +0, untied V +76, unclassified 0, PASS with one allowance in `docs/trust-baseline.json`. Per file: `VE/Service/Document.lean` +45 (D[V]: `eventsView`, `eventsLayeredOf`, the `environmentOf`, `Env` and `check` hunks), `VE/EnglishGrammar/SourceWords.lean` +31 (G[V]: the five rows). `VE/Events/Anchor.lean` is D[R]/G[R] (not trusted). Every new definition has a mutant a named guard kills (`mutants.json`, L1-L20); the ties pass is FOLLOW-UPS.md "## et-5b (2026-11-10)" | `mutants.json`; `tools/trust-classes.json` | R16 |
