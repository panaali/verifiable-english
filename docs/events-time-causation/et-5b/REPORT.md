# et-5b build report: Lean's document route admits `events@0`; the open anchor term; "always" and "eventually"

**Status:** second part of batch ET-5, deliverables 1-4 built (T18 and deliverable 5 moved to **et-5c**, below). No DRI
signature is reserved: DELTA row 1 is the DRI's signature of 2026-11-10, row 2 the jt-3p precedent, row 3 R16.
**HEAD:** the branch's last commit (the chain gates it).
**What changed:** Lean's document mode reads an `events@0` document on the soft chain (block decoded once, the route's
view, `LinkNotOpen`, `AnchorNotOpen`, `AnchorOpen`); the catalogue gains "always"/"eventually" with their no-anchor
rows and soft-norms' rule row, and a reader applies the DRI's "always" owner rule. **Open:** et-5c.

Item: feature item et-5b (acting DRI dri-featureplan 2026-11-10). Branch `feature/et-5b` from main `c94ad399b`.

## Inputs, statement gate

- Plan and spec on main (`docs/spec/events-time-causation-PLAN.md` ET-5 :971-995, 2.9 item 8 :461;
  `docs/spec/events-time-causation.md` 1.3, 2.3, 2.4, 4, 8.1/8.2 T15-T18), et-5 having copied etc-rev a7e426fa9.
- Statement gate: et-5 is on main; etc-rev's statement review accepted ET-5's section (et-5 REPORT, "Inputs"). No
  theorem statement is added or changed (`git diff $(git merge-base HEAD main) -- lean/statements.txt` is empty).
- Decisions: reviews/dri-decisions-20261110-et-5b-df-5b.md item 1 (the widening, SIGNED, with conditions i-iv);
  20261109-et-5.md items 1-2 (the moved set; the "always" tests); 20261103-fp-events-time-causation-r2.md item 3 (the
  "always" owner rule); 20261102-jt-3p.md item 3 (the `actions_version` precedent).

## Design: why `eventsLayeredOf`, not `layeredOf`

The task's sketch was to admit the block through `requestOf`/`layeredOf`. Two theorems on main state that
`layeredOf` is the soft branch with no events hook (`DocumentChain.layeredOf_soft`: `∃ environment norms,
decodeSoftU environment norms = .ok L`, with the hook's default `none`; `layeredOf_ids`: packs `["soft"]`). Routing
the block through `layeredOf` makes both false, which needs a statement change. So `layeredOf` and `requestOf` are
unchanged, and an events document goes through a new definition beside them:

- `environmentOf` calls `eventsView`: a list with `events@0` and `soft-norms@0` (no `rights@0`) passes the
  composition gate (`gateOf profileTable`, item 1), its block is decoded **once** (`Events.decodeEvents`, items 2-7),
  and the rest of the mode reads `Events.routeView` of it (no block, no `events@0`, a constant per named date).
  `Env.events` keeps the written environment and the decoded block; `Env.profiles` and `Env.envId` are the written
  environment's, so identities bind the bytes as written (guard "Identities read the environment as written").
- `check`'s soft branch calls `eventsLayeredOf` when `Env.events` is set: `LinkNotOpen` against the front matter's
  `open_terms`, then `eventsAnchorChecks`, then `decodeSoftU` (the soft branch of `decodeLayered`) on the written
  environment with the hook built from the block already decoded, never a second decoding.
- Shared file: this touches `check` (one `match` in its soft branch), which sa-checked-view and qt-a4b also edit, and
  the `Env` structure and its two anonymous constructors (`decodedEnvironment`, `cardinalityEnv`), near qt-a4b's
  `Env.version` hunk. Whichever merges second rebases (FEED_REBASE_SECOND).

## Plan rows and directive lines

| Row (task deliverables, ET-5 plan lines, DRI conditions) | Delivered | Where; test |
|---|---|---|
| 1. The document route admits `events@0`: `ownedProfiles`, the layered decoders on main, the composition gate decides, no Python mirror | yes, on the soft chain (`soft-norms@0` without `rights@0`); other lists keep the base refusal. No Python file changed (Python's `_lean_only` already sends the soft chain to Lean only) | `Document.lean` `ownedProfiles`, `eventsView`, `eventsLayeredOf`; EventsDocumentExamples "The route admits"; `test_an_events_document_is_checked_where_it_was_unavailable` |
| 1. The guard at RouteExamples ("object expected") replaced with the new answer; the guards beside it kept | yes: "refused by name" becomes the decoded `Env` (view without `events@0`, written profiles); "object expected" becomes `eventsLayeredOf`'s packs `["soft"]`; the `ownedLists` guards (`layeredOf` refuses an `Env` that lists `events@0`; `requestOf` is `null`) and the control are kept | `lean/VE/Events/RouteExamples.lean` |
| 1. Backlog row events0-owned-named-refusal | closed: the route now exists, so no named refusal is needed | as above |
| 2. `date_of_this_document` as 1.3 declares it | yes: `Events.anchorConstant`, `anchorWording` (also `routeView`'s, one owner) | `lean/VE/Events/Anchor.lean` |
| 2. Its legend line (2.3) | yes, as `Events.legend` (the day line, the state line, the link line when links are declared, the open anchor's line). Not shown in any answer: no display reads the legend yet, and the ISO anchor's line needs the long date form, which is the date-literal class's (1.3) → **et-5c** | EventsDocumentExamples T15 legend guards |
| 2. 2.9 item 8 on the document route, `AnchorNotOpen`, `AnchorOpen`; one fixture per 2.9 item 1-8 (condition ii) | yes: items 1 (two), 2, 3, 4, 5 (`LinkNotOpen`), 6, 7 (the pack's charge at 256/257), 8 (`AnchorNotOpen` four ways, `AnchorOpen` A2 and E2, and the other direction A1/E1 and no constant) | EventsDocumentExamples "Spec 2.9"; `test_a_broken_2_9_check_gets_its_diagnostic_on_the_document_route`, `test_an_anchor_dependent_reading_is_refused_while_the_anchor_is_open`, `test_an_unopened_link_is_refused_and_an_opened_one_is_checked` |
| 3. "always"/"eventually" no-anchor rows (rows only, X9) | yes: `alwaysReadings`, `eventuallyReadings` (frame `source`, {A1, A2}, {E1, E2}), `alwaysNoAnchorReadings`, `eventuallyNoAnchorReadings` (frame `source no anchor`: the refused candidate, its advice, the one reading), soft-norms' `softAlwaysReadings` (frame `rule`, {strict, default}) | `SourceWords.lean`; the choice among rows is `SourceReader.lean` |
| 3. The two "always" tests (condition iii) | yes: "Claude should always <act>" gives {strict, default} and no A1/A2 at every anchor state; a descriptive "<x> always <verb>" with no ISO anchor gives A1 only; undecidable context gives `always-owner` | `SourceWordsExamples.lean` section "always and eventually" |
| 4. T15 | partial: both assertions CHECKED (and with `judgments@0` listed), 3 calendar premises and no `date` premise, the one named date 2030-01-01, the legend's open-anchor line. NOT ENTAILED and its calendar countermodels need the prover: not checked here | EventsDocumentExamples T15 |
| 4. T16 | partial: the document loads with no GAP; `link_weaker` holds C2 ⇒ C1. The reading set {C1, C2} is the causal words' row → **et-5c** | EventsDocumentExamples T16 |
| 4. T17 | yes: {A1} and {E1} in T15's document; `AnchorOpen: A2`; {A1, A2} and {E1, E2} with an ISO anchor; `AnchorNotOpen` twice | EventsDocumentExamples T17 |
| 4. T18 ("if it fits") | no → **et-5c** (needs status replays on day-typed rules) | |
| 4. T9's "one derivation each" of 2.2's wordings through the reader | not reached: a fenced English unit in an events document stops at Python's lexicon step (`ve/document/lean.py` builds `Environment(environment)`, which refuses the block: `InvalidInput: invalid environment envelope`, probed on this tree); the derived-wording grammar is item 5 → **et-5c** | |
| 5. by, until-date, while, since, the causal words, their T-rows, derived-wording grammar | no, past the size line → **et-5c** | |
| Condition i (conservativity) | by construction (DELTA "Everything else") and the selected run | REPORT "Tests" |
| Condition iv (et-5's conditions stay selected) | yes: none of their files changed except the guard file, whose "always" refusal guard is kept | `test_named_binding_faults_are_unavailable`, `test_every_single_fault_mutant_*`, `test_every_two_fault_mutant_*`, `test_role_wordings_stay_under_the_author_lint`; SourceWordsExamples advice guard |
| Evaluators: every value read once, charged | the block is decoded once (`Env.events`); its size is charged by `decodeEvents` (64 dates, the pack's charge, `MAX_NODES` per premise) | `test_the_dates_are_charged_at_their_limit`; `counted 256/257` |

## Seeded bugs (`mutants.json`; each planted alone, its module rebuilt, the fixtures run, then restored)

One per new trusted definition and per claimed behaviour, all killed by a named `#guard`:
L1 `ownedProfiles` (drop `events@0`) → EventsDocumentExamples.lean:89; L2 `eventsView` (forget the block) → :89;
L3 `environmentOf` (the view's id) → :92; L4 `eventsLayeredOf` (no `LinkNotOpen`) → :115; L5 `eventsAnchorChecks`
(no `AnchorOpen`) → :129; L6 `openAnchor` (an ISO anchor beside the constant) → :127; L7 `legend` → :156; L8-L12
`sourceReadings`, `ruleContext`, `ruleVerbs`, `rowOf`, `anchorCandidates` → SourceWordsExamples.lean :158, :148, :148,
:154, :165; L13-L17 the five rows → SourceWordsExamples.lean :156, EventsDocumentExamples.lean :211, SourceWordsExamples
:165, :160, :148. Python (tooling only; no Python product file changed): P1 below.

## Trust, size, tests

- Trust (DELTA row 3): K +0, S +0, V +104; `tools/trust_map.py --check` PASS with the R16 allowance.
- Size: 616 added, 29 deleted hand-written lines before this report and DELTA (`git diff --numstat` outside generated
  files): product Lean 186, fixtures and guards 297, Python tests 140, registration 4. Over the ~600 line with the
  docs; the DRI's line for the item is ~700 product lines, so deliverable 5 and T18 go to et-5c.
- Tests: PENDING (selected run, regen, lake build, audit, trust_mutants).

## Spec re-read

- `AnchorNotOpen: date_of_this_document` against spec 4 (:583-584) and plan 2.9 item 8 (:461-464): "declared, and it
  lacks the day sort or the fixed verbalisation, or the block has an `anchor`" — `openAnchor` checks exactly these
  three (and a missing block, which has no day sort).
- `AnchorOpen: <candidate>` against spec 4 (:585) and 1.3: only "in a document with that constant"; candidates A2 and
  E2 (2.4 :514-515) — `anchorCandidates == ["A2", "E2"]`.
- The rows against 2.4 :514-515 (A1 "on each day", A2 "on each day on or after the date of this document", E1
  "there is a day such that", E2 "a day after the date of this document"; situations "a day before the anchor").
- The owner rule against reviews/dri-decisions-20261103-fp-events-time-causation-r2.md item 3: inside a rule
  soft-norms only, outside {A1, A2} (A1 only while open), undecidable `always-owner`, never both.
- The legend's lines against 2.3 (:490-498), in its order.
- 1.3: the term is no named date (no `dateName`, no `date` premise, not in `maxDates`) — T15 guards.

## Next items

- **et-5c**: the other reading sets of 2.4 (by, until-date, while, since, the causal words with "cause"/"lead to"),
  their T-rows, T16's reading set {C1, C2}, T18, the derived-wording grammar and T9 through the reader (with fenced
  English in an events document), and the legend shown in an answer with the ISO anchor's long-form line.
- et-6 and et-9 now have their route.

FOLLOW-UP: et-5c events reading sets by/until-date/while/since/cause, their T-rows, derived-wording grammar
