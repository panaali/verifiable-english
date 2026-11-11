# et-5b build report: Lean's document route admits `events@0` on the soft chain; the open anchor term; "always"/"eventually"

**Status:** deliverables 1-3 built; 4 built except what the DRI moved (T15's NOT ENTAILED, T18, the legend in an
answer: DRI 11-10 et-5b item 2) and T9 through the reader (a seam, below); 5 built as catalogue rows with their T-row
guards (T11c, T16's {C1, C2}, by, while, since), except the derived-wording grammar (the same seam). No DRI signature
is reserved. DELTA row 1 carries the DRI's signature of 2026-11-10 and row 2 cites R16.
**SIZE:** 201 product, 582 tests, 615 other hand-written lines (against `git merge-base HEAD main`; product: Lean only).
**Merge:** main merged on 2026-11-11 (rebase-second after qt-a4b; base `0295df174`). `check` then exceeded the
heartbeat limit with the events `match` inline, so the match moved to `DocumentChain.chainLayeredOf` and `check`'s
hunk is one line.
**HEAD:** the branch's last commit (the chain gates it).
**What changed:** Lean's document mode now reads an `events@0` document on the soft chain. It runs `Events.eventsHook` over
the document's open terms, decodes the block once, then runs `AnchorNotOpen` and `AnchorOpen` and the soft chain's checks.
The catalogue gains the "always"/"eventually" rows, their no-anchor rows and soft-norms' rule row.
**Open:** et-5c (the seam and the DRI's item-2 moves), et-5d and et-5e (rulings: reviews/dri-decisions-20261110-et-5b.md items 1-2).

Item: feature item et-5b (acting DRI dri-featureplan 2026-11-10). Branch `feature/et-5b` from main `c94ad399b`, main merged at `0295df174`.

## Inputs, statement gate, decisions

- Plan and spec on main: `docs/spec/events-time-causation-PLAN.md` (ET-5 :971-995, 2.9 item 8 :461) and
  `docs/spec/events-time-causation.md` (1.3, 2.3, 2.4, 4, 8.1/8.2 T15-T18). et-5 copied them from etc-rev a7e426fa9.
- Statement gate: et-5 is on main, and etc-rev's statement review accepted ET-5's section (et-5 REPORT, "Inputs"). No
  theorem statement was added or changed: `tools/lean_statements.py` reports `changed: 0` on the final Lean.
- Decisions read: reviews/dri-decisions-20261110-et-5b-df-5b.md item 1 (the widening, SIGNED, conditions i-iv);
  20261109-et-5.md items 1-2; 20261103-fp-events-time-causation-r2.md item 3 (the "always" owner rule).
- Decision asked and given: **reviews/dri-decisions-20261110-et-5b.md**.
  - Item 1: admit `events@0` on the soft chain only. Every other list keeps the base refusal. The plain norm-defaults
    chain moves to et-5d and the rights chain to et-5e.
  - Item 2: T15's NOT ENTAILED and the legend shown in an answer move to et-5c.

## Design

- **Not through `layeredOf`.** On main, `DocumentChain.layeredOf_soft` and `layeredOf_ids` state that `layeredOf` is the
  soft branch with no events hook. Routing the block through `layeredOf` would make both false, so `layeredOf` and
  `requestOf` are unchanged.
- **`environmentOf` → `eventsView`.** `check` passes the front matter's `open_terms`, or `none` on the scope path.
  For a list with `events@0` and `soft-norms@0` (and no `rights@0`, `readings@1` or senses), `eventsView` calls
  `Events.eventsHook`:
  - That is the layered decoders' own reading: the composition gate's row, then the block in spec 4's order with
    `LinkNotOpen` after item 5. It is the one owner, decoded once.
  - The rest of the mode reads the hook's view.
  - `Env.events` keeps the written environment and the hook. `Env.profiles` and `Env.envId` are the written
    environment's, so identities bind the bytes as written.
  - Every other `events@0` list gets the base's refusal through the base's own expression (`undecided`).
- **`check` → `eventsLayeredOf`.** This is `eventsAnchorChecks`, then `decodeSoftU` with that same hook, on the
  environment as `requestOf` sends it (`E.lower` of the written environment). The block is never decoded a second
  time. DocumentChain.lean's docstring says so, and the R16 ties pass asks for its theorem.
- **Shared files.** The change touches `check` (one `environmentOf` argument, and `chainLayeredOf` in place of
  `layeredOf`) and the `Env` structure with its anonymous constructors (`cardinalityEnv`'s kept both sides at the merge). sa-checked-view (`check`, `Checked`) and qt-a4b (`Env.version`, `check`) also edit
  these. Whichever merges second rebases (FEED_REBASE_SECOND). No hunk is in rights-cfr-1's definitions.
- **The reader of source words is fixture code, not product code.** No product route turns a source word into a
  reading set yet: the DRI's 11-09 et-5 item 2 says so, and that translation route is et-5c's. So the 11-03 owner rule
  is stated once, over the rows, in `SourceWordsExamples.lean` (`ruleContext`, `sourceReadings`). The catalogue stays
  rows only (X9), and the English `actions_version` is unchanged.

## Plan rows and directive lines

| Row (task deliverables, ET-5 plan lines, DRI conditions) | Delivered | Where; test |
|---|---|---|
| 1. The document route admits `events@0`: `ownedProfiles`, the layered decoders on main, the composition gate decides, no Python mirror | yes, on the soft chain (DRI 11-10 et-5b item 1). No Python file changed: `ve/document/lean.py`'s `_lean_only` already sends the soft chain to Lean only | `Document.lean` `ownedProfiles`, `eventsView`, `eventsLayeredOf`; EventsDocumentExamples "The route admits"; `test_an_events_document_is_checked_where_it_was_unavailable` |
| 1. The RouteExamples guard "object expected" replaced with the new answer; the guards beside it kept | yes. "Refused by name" now checks the decoded `Env` (the view without `events@0`, with the written profiles). "Object expected" becomes `eventsLayeredOf`'s packs `["soft"]`. The `ownedLists` guards (`layeredOf` refuses an `Env` that lists `events@0`; `requestOf` is `null`) and the control are kept. A scope-path guard (no open terms gives the base text) is added | `lean/VE/Events/RouteExamples.lean` |
| 1. Backlog row events0-owned-named-refusal | closed: the route exists | as above |
| 2. `date_of_this_document` as 1.3 declares it | yes: `Events.anchorConstant`, `anchorWording` (`routeView` uses the same wording, one owner) | `lean/VE/Events/Anchor.lean`; mutants L13, L14 |
| 2. Its legend line (2.3) | yes, as the Lean definition `Events.legend` with guards. Showing it in an answer, with the ISO anchor's long-form line, is et-5c's (DRI 11-10 et-5b item 2) | EventsDocumentExamples T15 legend guards |
| 2. 2.9 item 8 on the document route; one fixture per 2.9 item 1-8 (condition ii) | yes: item 1 (requires, with time@0, with alternatives@0), 2, 3, 4, 5 (`LinkNotOpen`, and its place before item 6 as `eventsHook` gives it), 6, 7 (the charge at 256/257 and the pack sum at 30/60 link pairs), 8 (`AnchorNotOpen` four ways, `AnchorOpen` A2 and E2; the other direction: A1, E1, and no constant) | EventsDocumentExamples "Spec 2.9"; `test_a_broken_2_9_check_gets_its_diagnostic_on_the_document_route`, `test_an_anchor_dependent_reading_is_refused_while_the_anchor_is_open`, `test_an_unopened_link_is_refused_and_an_opened_one_is_checked` |
| 3. The "always"/"eventually" no-anchor rows (rows only, X9) | yes: `alwaysReadings` and `eventuallyReadings` (frame `source`: {A1, A2}, {E1, E2}); `alwaysNoAnchorReadings` and `eventuallyNoAnchorReadings` (frame `source no anchor`: the refused candidate, its advice, the one reading); soft-norms' `softAlwaysReadings` (frame `rule`: {strict, default}) | `SourceWords.lean`; mutants L15-L20 |
| 3. The two "always" tests (condition iii) | yes. "Claude should always <act>" gives {strict, default} and no A1/A2, at every anchor state and under a lead-in. A descriptive "<x> always <verb>" with no ISO anchor gives A1 only. An undecidable context gives `always-owner`. "need" and "may" alone are not a rule ("People always need water" gives A1) | `SourceWordsExamples.lean` section "always and eventually" |
| 4. T15 | partial (DRI 11-10 et-5b item 2). Delivered: both assertions CHECKED, also with `judgments@0`; 3 calendar premises and no `date` premise; the one named date 2030-01-01; the legend's open-anchor line. NOT ENTAILED → et-5c | EventsDocumentExamples T15 |
| 4. T16 | yes: the document loads with no GAP, and `link_weaker` holds (C2 ⇒ C1); the causal words' reading set {C1, C2} is the link wordings Lean checks (`linkCandidate`, one owner: `Events.linkWording`), with C3 only under a decision model | EventsDocumentExamples T16; SourceWordsExamples "The other reading sets" |
| 4. T17 | yes: {A1} and {E1} in T15's document; `AnchorOpen: A2`; {A1, A2} and {E1, E2} with an ISO anchor; `AnchorNotOpen` twice | EventsDocumentExamples T17 |
| 4. T18 ("if it fits") | no → et-5c | |
| 4. T9's "one derivation each" through the reader | no: a seam (needs the English reader to read an events environment). A fenced English unit in an events document stops at Python's lexicon step: `ve/document/lean.py` builds `Environment(environment)`, which refuses the block with `InvalidInput: invalid environment envelope` (probed before the main merge, unchanged from base). The derived-wording grammar needs the same reader → et-5c | |
| 5. by, until-date, while, since, the causal words (source forms "cause" and "lead to"), their T-rows | yes, as rows (X9): `untilDateReadings` (T11c: four candidates, told apart on <date> and the day after), `byReadings` (B1/B2), `whileReadings` (temporal/contrast), `sinceReadings` (S1/S2), `causalReadings` (C1, C2; C3 "leads to" only under a decision model; no row for "leads to"/"causes"), `linkCandidate` | `SourceWords.lean`; SourceWordsExamples "The other reading sets"; mutants L21-L28 |
| 5. The derived-wording grammar | no: the seam above (the reader refuses an events environment before any grammar runs) → et-5c | |
| Condition i (conservativity) | yes. The code path is unchanged when the list has no `events@0` (DELTA "Everything else"). `tools/regen_generated.py --write` left `lean/VE/Route/examples/route-cases.json` unchanged (`git status` after the regen commit) | DELTA; selected run below |
| Condition ii | yes | row 2.9 above |
| Condition iii | yes | row 3 above |
| Condition iv (et-5's conditions stay selected) | yes. Those files are unchanged, except the guard file, where the authored "always" refusal guard stays | `test_named_binding_faults_are_unavailable`, `test_every_single_fault_mutant_*`, `test_every_two_fault_mutant_*`, `test_role_wordings_stay_under_the_author_lint`; the SourceWordsExamples advice guard |
| DRI 11-10 et-5b item 1 condition: off-chain lists keep the base text | yes: the plain list with and without its block, and `rights@0` with and without | `test_a_list_off_the_soft_chain_stays_unavailable`; EventsDocumentExamples "keeps the base's refusal" |
| Evaluators: every value read once and charged | yes. The block is decoded once (`Env.events` holds the hook) and charged by the hook (64 dates, the pack's charge, `MAX_NODES`) | `test_the_dates_are_charged_at_their_limit`; `counted 256/257`; `weaker 30/60` |

## Seeded bugs (`mutants.json`)

Each bug was planted alone, its module rebuilt, the fixture files run with `lake env lean`, then the file restored.
All 28 are killed by a named `#guard`. Only Lean product code changed (no ve/, tools/ .py, conformance/ or rust/
file), so every seeded bug is in Lean.

- **Document mode** (`Document.lean`):
  - L1 `ownedProfiles`, L2 `eventsView` (forget the hook), L3 the written identity, L4 the document's open terms.
  - L5 and L6 `eventsAnchorChecks`, L7 `eventsLayeredOf`, L8 `chainLayeredOf` (`check`'s events branch; re-planted
    there after the main merge, killed at `EventsDocumentExamples.lean:169`).
  - L9 `events@0` named first, L10 off the soft chain.
- **Anchor** (`Anchor.lean`): L11 `openAnchor`, L12 `legend`, L13 `anchorConstant`, L14 `anchorWording`.
- **Catalogue** (`SourceWords.lean`): L15-L19 the five rows, L20 the row list; L21 `untilDateReadings`, L22
  `byReadings`, L23 `whileReadings`, L24 `sinceReadings`, L25 `linkCandidate`, L26-L27 `causalReadings`, L28
  `eventsReadingSets` (each killed by a guard of SourceWordsExamples "The other reading sets" or D11's count).
- **Profile check** (the 18 sweep survivors, after the self-review fixes): planted by hand (S1-S18, `/tmp` runner).
  - The new section "The mode's profile check" kills 17 of them.
  - S18 (a list ending in `events@0`) is equivalent; its reason is in `trust-mutants-allow.json`.
- **Equivalent, recorded in `mutants.json`:** `check`'s choice of open terms on the scope path, because `decodeScope`
  refuses first.

## Trust, size, tests

- **Trust** (DELTA row 2): K +0, S +0, V +122 against `0295df174375`: `Document.lean` +50 and `SourceWords.lean` +72
  (the R16 cap is 150). The new declarations of the reading sets and their fixtures are classed in
  `tools/trust-classes.json` (G[V] rows, T fixtures, D[V] `chainLayeredOf`); unclassified 0.
  - `uv run python tools/trust_map.py --check` prints "PASS: K, S and untied [V] within c94ad399b7b1 and the allowances
    introduced since".
  - The allowances (+76, then +46) are recorded in `docs/trust-baseline.json`, and the ties-pass row is in
    FOLLOW-UPS.md "## et-5b (2026-11-10)", updated to +122.
  - `tools/trust-classes.json`'s text diff against the base is larger than its content: earlier tool writes reordered
    its modules. Parsed, it only adds this item's 80 entries (none removed or changed).
- **Trust mutants:**
  - First sweep: `mac-pytest.sh --trustmut` ran 131 mutants and was cut at the remote limit (exit 124, 11945 s, no
    JSON). It printed 25 SURVIVOR and 4 UNKNOWN lines, all on the profile-check and literal lines listed above.
  - Second sweep, with the fixtures and `trust-mutants-allow.json`, at `7bfb5176c` (default cap of 60): 50 KILLED,
    7 ALLOWED, 2 UNKNOWN, 1 INVALID, 0 SURVIVOR, 71 NOT RUN past the cap (3346 s).
  - Third run, `--rescore` of the second on the final Lean (after the main merge and the reading sets): TM_RESULT.
- **Size** (`git diff --numstat $(git merge-base HEAD main)`, generated files left out; see the SIZE line above):
  - Product Lean: 201 added, 18 deleted (`Document.lean` 76/11, `SourceWords.lean` 75/3, `Anchor.lean` 41,
    `DocumentChain.lean` 5/3, `Wire.lean` 2/1, `VE.lean` 2).
  - Tests: 582 (Lean guards: `EventsDocumentExamples.lean` 261, `SourceWordsExamples.lean` 126, `RouteExamples.lean`
    25/14; Python: `tests/test_events_document.py` 169, `tests/test_events_wire_mutants.py` 1/1).
  - Other: 615 (DELTA, REPORT, `mutants.json`, the allow file, the trust-mutant record, the class and baseline entries).
  - Under the standing size override (2026-11-11) nothing was cut for size. Deliverable 5's reading sets, first moved
    to et-5c at the earlier size line, are delivered here.
- **Checks run once on the finished code (after the main merge):**
  - `lake build`: "Build completed successfully (1393 jobs)".
  - `python3 lean/audit.py`: "PASS: 847 source files; 9479 named theorem declarations audited".
  - `tools/lean_statements.py`: `changed: 0` (no theorem statement added or changed).
  - `tools/regen_generated.py --write`: "wrote 39 entries". Against main, the grammar data changes only in
    `LOCK.json`'s `SourceWords.lean` and `source_words.json` hashes and in `source_words.json` itself
    (`actions_version` is main's). `tests/data/route-cases.jsonl` and `lean/VE/Route/examples/route-cases.json` are
    unchanged.
  - `tools/trust_map.py --check`: PASS (above).
  - Trust-mutant sweep: TM_RESULT.
  - The selected run: SELECTED_RESULT.

## Spec re-read

- **`AnchorNotOpen: date_of_this_document`**, against spec 4 (:583-584) and plan 2.9 item 8 (:461-464). The spec reads
  "declared, and it lacks the day sort or the fixed verbalisation, or the block has an `anchor`". `openAnchor` checks
  exactly these three. A document with the constant and no block has no day sort.
- **`AnchorOpen: <candidate>`**, against spec 4 (:585) and 1.3. The check applies only "in a document with that
  constant". The candidates are A2 and E2 (2.4 :514-515), each named by its reading's `id`. That convention is the
  catalogue's candidate names.
  - An unrelated reading named `A2` in such a document is refused.
  - A reading with A2's content under another id is not.
  - Binding a reading to its catalogue row is the translation route's, et-5c's.
- **The rows**, against 2.4 :514-515:
  - A1 "on each day"; A2 "on each day on or after the date of this document".
  - E1 "there is a day such that"; E2 "a day after the date of this document".
  - The distinguishing situations are "a day before the anchor".
- **The owner rule**, against reviews/dri-decisions-20261103-fp-events-time-causation-r2.md item 3. Inside a rule
  soft-norms owns "always"; outside, {A1, A2}, with A1 only while the anchor is open. An undecidable context gives
  `always-owner`, never both.
- **The legend's lines**, against 2.3 (:490-498), in its order.
- **1.3**: the term is no named date (no `dateName`, no `date` premise, not counted in `maxDates`), as the T15 guards
  show.
- **2.4's other rows** (:507-517), word for word as candidates: "until D", four candidates in the order exclusive
  silent, exclusive with the opposite, inclusive silent, inclusive with the opposite (R2), told apart on D and the day
  after (T11c guards); "by" B1 before, B2 no later than; "while" the temporal reading and the contrast; "since" S1
  after, S2 on or after E's day; the causal words and the source forms "lead to" and "cause": C1, C2, and C3 only
  under a decision model, with no row for the third-person "leads to" and "causes" (2.4 :524-527).
- **4's document-route list**: `LinkNotOpen` comes after item 5, as `eventsHook` places it.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. The document answer's schema is unchanged and no field was added. Malformed block
   members reach Lean's diagnostics, or the reader's pre-existing unavailable texts: `test_only_a_ve_error_escapes_a_malformed_block_member`.
2. Deliverables: PASS. The plan-rows table above lists every cut: the DRI's 11-10 et-5b items 1-2, and one seam (the
   English reader of an events environment: the derived-wording grammar and T9). Nothing was cut for size. There is no Python copy of a Lean decision (no Python product file changed), and no
   permanent report test.
3. Tests can fail: PASS. `mutants.json` L1-L28 are all killed. The trust-mutant survivors are killed or allowed with
   reasons (`trust-mutants-allow.json`).
4. Agreement and valid inputs: PASS. LinkNotOpen's order matches `eventsHook` (the EventsDocumentExamples guard). Empty
   lists are accepted, the off-chain lists are byte-identical, and the route-cases are unchanged after the regen.
5. R8 binding: N.A. No relayed answer or field was added. The document relay is unchanged.
6. Gate evidence: PASS for what ran on this HEAD; the chain runs the full gate.
7. Unsigned items: PASS. DELTA row 1 is SIGNED by the DRI (11-10 item 1) and row 2 cites R16.
8. Every user-visible change is in DELTA: PASS. The base texts were probed:
   `test_a_list_off_the_soft_chain_stays_unavailable` and the EventsDocumentExamples naming guards.
9. Test selection: PENDING (the selected run).
10. Lean statements: N.A. No theorem was added or changed (`tools/lean_statements.py`: `changed: 0`).
11. Budgets and limits: PASS: `test_the_dates_are_charged_at_their_limit`, `counted 256/257`, `weaker 30/60`.
12. CPU: PASS by construction. The block is decoded once per document (`Env.events`), and no pilot lists `events@0`.
13. Test-removed trailers: N.A. No pytest test was removed or renamed. The two `#guard`s replaced in RouteExamples are
    no collected tests.
14. Both directions: PASS. Each check has its accepting side (A1/E1, no constant, open terms given, the owned profiles
    read) and its refusing side.
15. No overclaim and no silent cut: PASS. T15 is marked partial and T9 not reached, each with its reason; the cuts are
    ruled or at the seam; limits are charged before work (the hook).

SELF-REVIEW: 4 A, 6 B, 7 C; fixed 16. The 17th (C6: the `OWNED` copy in `conformance/document_wrapper.py`) stays.
That set is checked against Python's profile registry, which has no `events@0` row
(`tests/test_lean_document_wrapper.py::test_owned_profiles_are_the_lean_modes`).

## Next items

- **et-5c** (the seam, and the DRI's 11-10 item-2 moves):
  - the derived-wording grammar of 2.2, and T9's "one derivation each" through the reader, with fenced English in an
    events document. This needs the English reader to read an `events@0` environment, which today stops at Python's
    `Environment` (`InvalidInput: invalid environment envelope`), so it cannot pass its own tests in this item;
  - T18, and T15's NOT ENTAILED;
  - the legend in a document answer, with the ISO anchor's long-form line.
- **et-5d**: the events hook on the plain norm-defaults chain. R1 and the UDHR pilot read through this list, so et-6
  waits for it.
- **et-5e**: the rights chain, after PC-2c.

FOLLOW-UP: et-5c events derived-wording grammar and T9 through the reader, T18, T15 NOT ENTAILED, legend in the document answer
FOLLOW-UP: et-5d events@0 hook on the plain norm-defaults chain of the document route (R1 and UDHR pilot lists)
FOLLOW-UP: et-5e events@0 hook on the rights chain of the document route (after the document mode composes rights@0 with norm-defaults@0)
