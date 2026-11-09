# et-5 build report: `events@0`'s source-word rows, their advice, the lint registration, the bound relay

**Status:** first part of batch ET-5, stopped at the size line as the task directs; the rest is **et-5b**. No DRI
signature reserved (DELTA row 1 R16, row 2 R3). **HEAD:** the branch's last commit (the chain gates it).
**What changed:** Lean's source-word catalogue gains `events@0`'s rows: the twelve authored refusals, U1's and T11d's
reading sets and the profile-fixed wordings. Lean's advice reads the refusals. `ve/english.py` leaves the fixed
wordings unjudged by the author lint. `ve/events.py` relays et-4b's `events_premises` and date constants, bound to the
request. **Open:** et-5b (below). Pilot bytes 0.

Item: feature item et-5 (rank 130, acting DRI dri-featurefeed). Branch `feature/et-5` from main `c2ff64751`.

## Inputs, statement gate, synthesis edits

- **Plan and spec at design/etc-rev a7e426fa9.** No local repository has that commit any more (`git cat-file -e`
  fails in every repository under `~/code`). The two files are the frozen copies in
  `reviews/fidelity-pilot-20261103/events-time-causation/plans/`, whose `plans-manifest.tsv` records them as
  `design/etc-rev a7e426fa9`, 142947 and 127523 bytes. `wc -c` gives the same sizes. Main's copies were 32ffc3ec9's
  unchanged (`cmp`), so they were replaced, not merged (commit `c987cc585`).
- **Statement gate:** ET-E1, et-4 and et-4b are on main (`git log main`: `5fc9d8c7f` merges et-4b). etc-rev's review
  passed (`dri-etc-rev.final.md`). No theorem statement was added or changed.
- **Catalogue owner** (dri-decisions-20261028-catalogue-owner item 2): en-sw is on main (`bf28108dc`), so the rows are
  in `lean/VE/EnglishGrammar/SourceWords.lean` and no `et-5-sw` row is needed.
- **Synthesis round 2:** this item implements none of the edits; none touches ET-5's English or relay.
- **Plan 11 item 2 stays open for the synthesis.** As 2.7's Meanwhile says, the exemption is a hunk in the owner of
  wordings (`ve/english.py`, beside alternatives@0's and rights@0's). The wordings it exempts are the catalogue's
  `fixed` rows, the row kind en-sw added for this purpose. So the data is rows only and the mechanism is a code hunk.
  Which of the two carries the exemption is still the synthesis's question.

## Plan rows and directive lines

| Row (ET-5, plan lines 971-994, and the task) | Delivered | Where; test |
|---|---|---|
| The twelve source words refused in authored text with 2.7's advice (rows only, X9) | yes, with a rewrite each; Lean's `advice` reads them | `SourceWords.lean` `eventsRefusals`; `SourceWordsExamples` T9 guards |
| Reading sets, U1 in ET-E1's rewording | yes: "until <event>" (U1 states its silence, U2 the opposite modality) | `untilEventReadings`; the U1 guard |
| T11d's reading set (SR-B4) | yes: W1-W3, each with both end dates named | `withinDateReadings`; the T11d guard |
| The other reading sets of spec 2.4 ("by", "until <date>", "while", "since", "always", "eventually", the causal words with the source forms "cause" and "lead to") | **→ et-5b** (size) | |
| Profile wordings registered so the author lint does not judge them; role wordings still judged; lexicon unchanged | yes, for `before` and the two link forms (the `fixed` rows). The derived wordings are grammar forms, not declared wordings, so the lint never sees them; their grammar rows are et-5b's | `ve/english.py`; `tests/test_events_wordings.py` |
| `ve/events.py` relays the report fields and binds them (dates, labels, links; no extra row) | yes, for the fields et-4b answers (`events_premises`, the date constants). et-4c's `named_dates`, `causal_links` and `calendar_days` are not on main | `tests/test_events_answer.py` |
| Fuzz, one and two faults (dropped, emptied, retyped, duplicated, reordered, an index out of range) | yes, also a rebound label, name or date, and 1.5, a lone surrogate and a 10,000-deep list | `test_every_*_fault_mutant_*` |
| T9 | yes: the role wording checks, the lint judgments and the twelve words | `test_role_wordings_stay_under_the_author_lint` and the T9 guards |
| Binding fixtures | yes, one per relation | `test_named_binding_faults_are_unavailable` |
| The plan's two seeded bugs | yes: L1 and P1 below | `mutants.json` |
| etc-rev: `date_of_this_document`, its legend line, `AnchorNotOpen`/`AnchorOpen` (2.9 item 8), the no-anchor rows, T15-T18 | **→ et-5b**: Lean's environment and document modes refuse an events block today; accepting it is a widening | |
| Python reads AR-10's data; no `ve/profiles.py` row, no gate mirror | yes: no profile row or gate added | `git diff --stat` |
| Shared files | `tools/layer_policy.py` (layer 4 for `ve/events.py`); `ve/document.py` not touched | |

**R8 binding inventory (`ve/events.py`)**, each relation with a fixture: constants are the request's plus exactly one
`date__…` per named date, of the day sort, described by its own date (the anchor's wording is Lean's and is not
shown). Labels are each once and exactly the request's set: the order axioms; consecutive dates and those one day
apart; each sort's conventions; each link; each necessary/contributed pair over the same declared sorts. Every
formula names only the request's sorts, predicates and bound constants, with every index under a binder. The fuzzer
found the two unbound relations (adjacency and weaker pairs) before `_labels` bound them; both have fixtures.

## Seeded bugs (`mutants.json`; each planted alone, then restored)

| Id | Language, file | Bug | Failing test |
|---|---|---|---|
| L1 | Lean, `SourceWords.lean` | the contributed link's fixed wording is alternatives' "{0} leads to {1}" (plan bug 1) | `SourceWordsExamples.lean:150` D11 disjointness |
| L2 | Lean, `Advice.lean` | advice ignores the catalogue's refusals | `SourceWordsExamples.lean:117` |
| L3 | Lean, `SourceWords.lean` | U1 loses its silence sentence | `SourceWordsExamples.lean:128` |
| P1 | Python, `ve/english.py` | a role wording exempted from the lint (plan bug 2) | `test_role_wordings_stay_under_the_author_lint` |
| P2 | Python, `ve/events.py` | a missing premise row accepted | `test_every_single_fault_mutant_is_unavailable_or_changes_nothing_shown[rich]` |
| P3 | Python, `ve/events.py` | an out-of-range index accepted | `test_named_binding_faults_are_unavailable` |
| P4 | Python, `ve/events.py` | a date constant's sort and day unbound | `test_named_binding_faults_are_unavailable` |

## Trust, size, tests

- **Trust** (`uv run python tools/trust_map.py --check`): K +0, S +0, V +93 (`SourceWords.lean` +65,
  `SourceWordsExamples.lean` +19, `Advice.lean` +9); allowance recorded under R16; FOLLOW-UPS "## et-5" asks for the
  ties pass. Trust mutants: TBD.
- **Size** (`git diff --numstat` over the merge base, without the copied plan and spec and the generated files):
  TBD hand-written lines, over the ~600 rule; the item stopped there and moved the rest to et-5b.
- **Tests:** TBD.

## Next items

- **et-5b** (blocked on Lean accepting an events block in the environment and document modes, which is a widening,
  and on et-4c for situations):
  - the open anchor term (`date_of_this_document`, its legend line, `AnchorNotOpen`/`AnchorOpen`);
  - the remaining reading sets with the no-anchor rows;
  - the derived-wording grammar rows (`profiles=("events@0",)`) and the Lean English reader's registration of the
    fixed wordings;
  - T15-T18, and T11/T11d through the service;
  - the DRI's two "always" tests (asked of the DRI decider, inbox `20261109T034126Z-et-5`).
- **et-6** (the UDHR pilot), after et-5b and `infra/oom-rootcause`.

Acceptance items: all AGENT.
