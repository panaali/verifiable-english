# et-5 build report: `events@0`'s source-word rows, their advice, the lint registration, the bound relay

**Status:** first part of batch ET-5, stopped at the size line as the task directs; the rest is **et-5b**. The DRI
accepted the split (reviews/dri-decisions-20261109-et-5.md item 1) and this part's size, 957 added / 6 deleted
hand-written lines (reviews/dri-decisions-20261109-et-5-size.md item 1). No DRI signature is reserved. Every DELTA row cites R16, R3 or a signed DRI decision (row 3).
**HEAD:** the branch's last commit (the chain gates it).
**What changed:** Lean's source-word catalogue gains `events@0`'s rows: the twelve authored refusals, U1's and T11d's
reading sets and the profile-fixed wordings. Lean's advice reads the refusals. `ve/english.py` leaves the fixed
wordings unjudged by the author lint. `ve/events.py` relays et-4b's `events_premises` and date constants, bound to the
request. **Open:** et-5b (below). Pilot bytes: 0 expected (an estimate; no Lean mode accepts an events block yet).

Item: feature item et-5 (rank 130, acting DRI dri-featurefeed). Branch `feature/et-5` from main `c2ff64751`, synced
with main `61a11aa21` on 2026-11-09 (merge commit after `c2d1f4dbe`; no conflict).

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
| The twelve source words refused in authored text with 2.7's advice (rows only, X9) | yes, with a rewrite each; Lean's `advice` reads them | `SourceWords.lean` `eventsRefusals`; `SourceWordsExamples` T9 guards; `test_the_advice_is_spec_2_5_s` (word for word against spec 2.5's table) |
| Reading sets, U1 in ET-E1's rewording | yes, as rows: "until <event>" (U1 states its silence, U2 the opposite modality) | `untilEventReadings`; the U1 guard |
| T11d's reading set (SR-B4) | **partial**: W1-W3 as rows, both end dates named, pinned by text. Their truth values on 15 Jan, 1 Jan and 5 Jan, the two situations, and "within 10 days of the conviction" UNFORMALISED `duration` need the reader route: **→ et-5b** | `withinDateReadings`; the T11d guard |
| The other reading sets of spec 2.4 ("by", "until <date>", "while", "since", "always", "eventually", the causal words with the source forms "cause" and "lead to") | **→ et-5b** (DRI 20261109-et-5 item 1) | |
| The DRI's two 11-03 "always" tests | **→ et-5b** with the "always" rows (DRI 20261109-et-5 item 2). Its condition for et-5: a source "always" gets its refusal and advice and no events reading | `SourceWordsExamples.lean` "always" guards (the advice list and the one-row filter) |
| Profile wordings registered so the author lint does not judge them; role wordings still judged; lexicon unchanged | yes, for `before` and the two link forms (the `fixed` rows). A fixed wording two links share keeps DUPLICATE_TEMPLATE. The derived wordings are grammar forms, not declared wordings, so the lint never sees them; their grammar rows are et-5b's | `ve/english.py`; `tests/test_events_wordings.py` (7 tests) |
| `ve/events.py` relays the report fields and binds them (dates, labels, links; no extra row) | yes, for the fields et-4b answers (`events_premises`, the date constants). et-4c's `named_dates`, `causal_links` and `calendar_days` are not on main | `tests/test_events_answer.py` (14 tests) |
| Fuzz, one and two faults (dropped, emptied, retyped, duplicated, reordered, an index out of range) | yes: every single fault; two faults on a fixed sample of 2,000 pairs per source (seeded `random.Random(20261109)`), not all pairs. Also a rebound label, name or date, and 1.5, a lone surrogate and a 10,000-deep list. Mutants that only drop or rebind a row Lean chooses (adjacent dates, weaker links) are named as such (`_lean_chosen`), not counted as faults (R8) | `test_every_single_fault_mutant_*`, `test_every_two_fault_mutant_*` |
| T9 | **partial**: the role wording checks, the lint's judgments and the twelve refusals with their advice. Spec 8.1 T9's "one derivation each" of 2.2's wordings through the reader is et-5b's (the reader route) | `test_role_wordings_stay_under_the_author_lint`, `test_the_profile_wordings_are_not_judged_by_the_author_lint`, the T9 guards |
| Binding fixtures | yes, one per relation, and the request side | `test_named_binding_faults_are_unavailable`, `test_a_request_not_of_the_block_s_shape_is_unavailable` |
| The plan's two seeded bugs | yes: L1 and P1 below | `mutants.json` |
| etc-rev: `date_of_this_document`, its legend line, `AnchorNotOpen`/`AnchorOpen` (2.9 item 8), the no-anchor rows, T15-T18 | **→ et-5b** (DRI 20261109-et-5 item 1): Lean's environment and document modes refuse an events block today; accepting it is a widening | |
| ET-E1's U1 legend line ("A rule says nothing about the days its condition excludes", RESULTS.md 72-75) and whether the silence sentence is a profile wording or a display line | **→ et-5b**, with the legend lines | |
| Python reads AR-10's data; no `ve/profiles.py` row, no gate mirror | yes: no profile row or gate added | `git diff --stat $(git merge-base HEAD main)` lists no `ve/profiles.py` |
| Shared files | `tools/layer_policy.py` (layer 4 for `ve/events.py`); `ve/document.py` not touched | |
| Why: the use-case regression R1 (narrowed) becomes runnable | **not yet**: R1 reads dated documents through the document route, which is et-5b's | |

**Overlap check** (`git diff --name-only main...<b>` for every `lean-first/*`, `feature/*`, `infra/*`, `foundation/*`
branch, run by the self-reviewer at `c2d1f4dbe`): no in-flight branch edits a hand-written file this item edits.

**R8 binding inventory (`ve/events.py`)**, each relation with a fixture in `test_named_binding_faults_are_unavailable`:

- Constants: the request's as written, plus exactly one `date__…` per named date, of the day sort, described by its
  own date (the anchor's wording is Lean's and is not shown).
- Labels: each once, of a closed list of kinds, each exactly the label `events.label` renders from the request's
  names (`events:` then the kind and the names; the pairs by `_pair`, every split tried, one reading only): no prefix
  is stripped (review F1). One per request item, none missing: the order axioms, each sort's
  conventions, each link's forward premise. Counted: the date facts, one fewer than the named dates, chaining them
  all. Named only: an adjacency over a date fact's pair, a weaker pair over a necessary and a contributed link.
  Which dates are consecutive or one day apart, and which links are weaker, are Lean's (`calendarLabelled`,
  `weakerPairs`); the self-review (A) found the first draft recomputing them, and they were removed.
- Formulas: only the request's sorts, predicates (applied to their declared number of terms) and bound constants,
  with every index under a binder; walked with an explicit stack.
- Request side: a block not of the shape the bindings read is `CheckerUnavailable`, never a Python error.

## Seeded bugs (`mutants.json`; each planted alone, then restored; all re-run on the tree of `0ac08c7e3`)

| Id | Language, file | Bug | Failing test |
|---|---|---|---|
| L1 | Lean, `SourceWords.lean` | the contributed link's fixed wording is alternatives' "{0} leads to {1}" (plan bug 1) | `SourceWordsExamples.lean:142` (fixed frames) and `:154` (D11 disjointness) |
| L2 | Lean, `Advice.lean` | advice ignores the catalogue's refusals | `SourceWordsExamples.lean:117`, `:119`, `:125` |
| L3 | Lean, `SourceWords.lean` | U1 loses its silence sentence | `SourceWordsExamples.lean:132` |
| P1 | Python, `ve/english.py` | a role wording exempted from the lint (plan bug 2) | `test_role_wordings_stay_under_the_author_lint` |
| P7 | Python, `ve/english.py` | a shared fixed wording loses DUPLICATE_TEMPLATE | `test_two_links_sharing_a_wording_keep_duplicate_template` |
| P2 | Python, `ve/events.py` | a missing one-per-item premise accepted | `test_every_single_fault_mutant_is_unavailable_or_changes_nothing_shown[rich]` |
| P3 | Python, `ve/events.py` | an out-of-range index accepted | `test_named_binding_faults_are_unavailable` |
| P4 | Python, `ve/events.py` | a date constant's sort and day unbound | `test_named_binding_faults_are_unavailable` |
| P5 | Python, `ve/events.py` | the date facts' chain unchecked | `test_named_binding_faults_are_unavailable` |
| P6 | Python, `ve/events.py` | the request's shape unchecked | `test_a_request_not_of_the_block_s_shape_is_unavailable` |
| P8 | Python, `ve/events.py` | fix round 1 (review F1): the pre-fix parse, `events:` stripped and never required | `test_named_binding_faults_are_unavailable`, `test_every_single_fault_mutant_*` (3 sources) |
| P9 | Python, `ve/events.py` | fix round 1: `_pair` finds the kind anywhere and skips the exact re-render | `test_a_label_is_bound_only_as_lean_renders_it` and the four above |

No Rust changed.

## Trust, size, tests

- **Trust** (`uv run python tools/trust_map.py --check`, final tree, against `61a11aa21edc`): K +0, S +0, untied V +76
  (`SourceWords.lean` +67, `Advice.lean` +9), unclassified 0, "PASS: K, S and untied [V] within 61a11aa21edc and the
  allowances introduced since". The new declarations are classified in `tools/trust-classes.json` (the catalogue rows
  and advice G[V], beside `adviceRows`; the example helpers T), which `test_committed_trust_table_covers_every_declaration`
  requires (the first selected run failed on it: 95 unclassified lines). Allowance recorded under R16 in
  `docs/trust-baseline.json`; FOLLOW-UPS.md "## et-5 (2026-11-09)" asks for the ties pass.
- **Trust mutants** (`mac-pytest.sh --trustmut -- --max-mutants 1000 --test
  lean/VE/EnglishGrammar/SourceWordsExamples.lean --allow docs/events-time-causation/et-5/trust-mutants-allow.json
  --json docs/events-time-causation/et-5/trust-mutants.json`; the Mac was unreachable, so it ran on the VM): full run at `a7e9981e5`, "129 KILLED, 1 SURVIVOR, 0 UNKNOWN, 16
  INVALID, 8 ALLOWED"; the survivor (`advice` reading only each row's first pattern, `Advice.lean:83`) is killed by
  the guard added in `fadb85749` ("brings about" is `alternatives-results`' second pattern). `--rescore` of that run on
  `fadb85749` (a check-only change), exit 0: "130 KILLED, 0 SURVIVOR, 0 UNKNOWN, 16 INVALID, 8 ALLOWED, 0 NOT RUN;
  145 carried". Eleven definitions, 154 mutants; the allowed eight are the four allow-file rows.
  A first sweep, stopped when the classes changed its plan, found three survivors: `grammarCase`'s export cut to its
  first row or without its last (killed now by `SourceWordsExamples`' `exportedAdvice` guards and
  `test_the_grammar_export_lists_the_twelve_advice_rows_after_the_others`), and `sourceWordAdvice` on
  `sourceWords.dropLast`, which is equivalent (the last row is fixed, not a refusal) and is in the allow file with
  the `list-empty` mutants that do not typecheck.
- **Size** (`git diff --numstat $(git merge-base HEAD main)`, without the copied plan and spec, the generated files
  and the trust-mutant record), measured twice. When the DRI was asked: 957 added, 6 deleted; ACCEPTED as the first
  coherent part by reviews/dri-decisions-20261109-et-5-size.md item 1 (the relay's fuzz and binding fixtures,
  `tests/test_events_answer.py` 335, are R8 evidence and exempt). Its condition, that the binding, fuzz and
  role-wording tests stay selected, holds: `tools/select_tests.py` selects both files. On the final HEAD: 1,128
  added, 11 deleted: `tests/test_events_answer.py` 335 (exempt), `tests/test_events_wordings.py` 153, `ve/events.py`
  188, Lean 164, `ve/english.py` 21, docs 236 (this report 195), `tools/trust-classes.json` 24, other 7. The growth
  since the ruling is the self-review's and the checks' fixes: the report's required sections, the declaration
  classes, the export and pattern guards, the export test, the layer doc. Without the exempt file that is about 790
  lines, against about 620 at the ruling; the DRI was told (msg.sh, 2026-11-09).
- **Lean:** `lake build` "Build completed successfully (1320 jobs)"; `python3 lean/audit.py` "PASS: 789 source files;
  8708 named theorem declarations audited". `tools/lean_statements.py`: changed 0.
- **Generated:** `tools/regen_generated.py --write` once, then `--check` passes (the assurance doc from
  `tools/assurance_manifest.py --write`; `Run.lean`'s whole-file pin moved to its new hash, range 1-759 unchanged).
  `tools/english_grammar_gen.py --check` passes at `actions_version` 46 (DELTA row 3).
- **Selected tests** (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, on
  the committed, clean `a7e9981e5`; the Mac was unreachable, so the VM ran it): "recorded 466 units for tree
  7b0d524e41 ... 1 failed": `tools/test_layer_policy.py::LayerSelectionTests::test_documented_python_layers_match_policy`
  (`events` missing from layer 4 of `docs/ARCHITECTURE-LAYERS.md`), fixed in `docs/ARCHITECTURE-LAYERS.md` and rerun
  alone: "Ran 1 test ... OK". `tests/test_events_answer.py`, `tests/test_events_wordings.py`,
  `tests/test_consolidation_tools.py`, `tests/test_assurance_manifest.py` and `tests/test_english_grammar_gen.py`
  exit 0. An earlier run, stopped unfinished, had found `test_committed_trust_table_covers_every_declaration` (95
  unclassified lines), fixed by the classes above. After that run, only a Lean `#guard` (the advice-pattern
  survivor), `lean/declarations.txt`, docs and the trust-mutant evidence changed, so the final selected run is on
  the committed, clean `fb1e59bca` (VM; the Mac was unreachable): exit 0, "recorded 460 units for tree 7bba0e77f1;
  1 others left to the static graph until they run; 0 failed", 6,268 s. Only this report changed after it.
- Pre-existing reds (main-known-red.txt): none was hit.

## DRI decisions this item read or asked

- reviews/dri-decisions-20261028-catalogue-owner.md item 2: rows in `SourceWords.lean` (en-sw merged).
- reviews/dri-decisions-20261103-fp-events-time-causation-r2.md item 3 ("always"), as narrowed for et-5 by
  reviews/dri-decisions-20261109-et-5.md item 2.
- reviews/dri-decisions-20261109-et-5.md items 1-3: the split, the "always" tests, row et-5b.
- reviews/dri-decisions-20261102-jt-3p.md item 3: the `actions_version` raise (DELTA row 3).
- reviews/dri-decisions-20261109-et-5-size.md item 1: this part's size accepted (asked 2026-11-09 05:44Z).

## Spec re-read

- spec re-read: the date constant `date__YYYY_MM_DD` of the day sort against docs/spec/events-time-causation.md:191.
- spec re-read: the label kinds and what each names against docs/spec/events-time-causation.md:224-240 (1.4's table;
  adjacency "each consecutive pair with D'.num = D.num + 1" and weaker "on the same sort pair" are Lean's).
- spec re-read: role wordings under the lint, T9's lint expectations against docs/spec/events-time-causation.md:457
  and :1377, :1423.
- spec re-read: the twelve advice texts against docs/spec/events-time-causation.md:526 (2.5's table), checked word
  for word by `test_the_advice_is_spec_2_5_s`.
- spec re-read: the "within" readings W1-W3 against docs/spec/events-time-causation.md:510 and T11d at :1382.
- spec re-read: the Meanwhile registration in `ve/english.py` against docs/spec/events-time-causation-PLAN.md:336
  (2.7) and :1296 (section 11 item 2).

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 2 A, 6 B, 6 C; fixed 12 (both A; all six B, five by a fix and the size one by the DRI's ruling; three C:
predicate arity, the sampled-pairs wording, the policy and R1 notes. Not fixed: the hand-typed alternatives wordings
in `otherProfileWordings`, whose owner keeps them in a local `let`, and the broad "by"/"while"/"since" advice
patterns, now stated in DELTA row 2).

1. Typed and contained: PASS. `test_every_single_fault_mutant_is_unavailable_or_changes_nothing_shown` (7, true, null,
   [], {}, 1.5, a lone surrogate, a 10,000-deep list on every member), `test_a_request_not_of_the_block_s_shape_is_unavailable`
   (request side). The bad stdout byte is the norm-defaults route's (`ve.norm_defaults_route`), unchanged here.
2. Deliverables: PASS with the cuts ruled: the plan-rows table above; et-5b by reviews/dri-decisions-20261109-et-5.md.
3. Tests can fail: PASS. `mutants.json` (10 bugs, 3 Lean, 7 Python) and `trust-mutants.json`.
4. Agree, valid inputs pass: PASS. `test_genuine_answers_are_relayed_with_every_kind_of_label`,
   `test_a_request_at_the_date_limit_with_many_links_is_bound`; no Rust path.
5. R8 binding: PASS. `test_named_binding_faults_are_unavailable` (an undeclared date, link and sort, a shifted date,
   a repeated row, a missing row), and arity in `_bind_formula`.
6. Gate evidence: PASS. Synced with main `61a11aa21`; the final selected run is on the committed HEAD; the chain runs
   the gate.
7. Unsigned items: PASS. `review-ready.py --delta-dri-needed`: "No DELTA row reserved for the DRI".
8. DELTA: PASS. Rows 1-3; no existing entry's output moves (DELTA's first paragraph).
9. Selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` selects both events test files.
10. Lean statements: N.A. No theorem added or changed (`lean_statements.py`: changed 0).
11. Budgets fail closed: PASS. The relay walks each formula once with an explicit stack;
    `test_a_deep_formula_is_walked_to_its_end`, `test_a_request_at_the_date_limit_with_many_links_is_bound`.
12. CPU and memory: N.A. No pilot path changes (no Lean mode accepts an events block yet).
13. Test-removed trailers: PASS. No test removed; `tools/gate_collection.py --check --prebuilt`: "21 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers".
14. Both directions, cited evidence, spec re-read: PASS. Accept and refuse for each check (for example
    `test_two_links_sharing_a_wording_keep_duplicate_template` against `test_the_profile_wordings_are_not_judged_by_the_author_lint`);
    spec re-read above.
15. Four classes: overclaim PASS (T9 and T11d marked partial; R1 not reached); silent cut PASS (cuts ruled by DRI
    20261109-et-5); every new check can fail PASS (`mutants.json`); limits charged before work PASS (the shape check
    precedes every walk; `test_a_request_at_the_date_limit_with_many_links_is_bound`).

## Fix round 1 (review `et-5-review.final.md` of `70ab5fe95`)

- **F1 (B, R8)**: `ve/events.py` now has one label renderer (`label`, Lean's `eventsLabelled` form) and accepts a
  label only as that renderer gives it from the request's names. The one-per-item rows match exactly, as before. The
  pairs go through `_pair`: the prefix and kind are required, every split at a `:` is tried, and exactly one reading
  must name the request. No prefix is stripped. The fuzzer gains `_mangled` (a label's prefix dropped or respelled,
  a segment added, emptied or padded), applied in place and as an extra row beside its genuine twin. `_rebound` could
  not produce that class. Regression tests: the reviewer's probe as
  `test_a_label_is_bound_only_as_lean_renders_it`; the unprefixed twin of each kind (date, adjacent, weaker link, one
  per item, order axiom) in `test_named_binding_faults_are_unavailable`; `_mangled` in both fault fuzzers. Seeded
  bugs P8 and P9 above. Sweep of the class in `ve/`: the readings pair labels require their prefix
  (`readings_verdicts/binding.py`); the `unsaid__` names are prefix-checked by the generated schema; the defaults
  assumptions bind by exact membership in Lean's labels (`defaults.bind_certificate`). None loose.
- **F2 (B)**: the FOLLOW-UPS.md row "## et-5 (2026-11-09)" now exists on this host
  (`/home/seyran/code/manage-agents/FOLLOW-UPS.md`). It asks for the ties pass of the V +76 per file (R16), and it
  also carries F6's plan/spec disagreement on "while". It is no repo test, because the file is outside the repository
  and tests are hermetic; the probe (`grep -q '^## et-5'`) passes.
- **F-ready1 (B)**: the relay mutation gate found no `ve_service` in this worktree. `lake build` (1320 jobs) builds
  it, and the review-ready check reruns on the fix HEAD.
- C findings F3 to F6 are left as follow-ups (F6 is noted in the FOLLOW-UPS row).

## Next items

- **et-5b** (DRI 20261109-et-5 item 3; blocked on Lean accepting an events block in the environment and document
  modes, a widening, and on et-4c for situations):
  - the open anchor term (`date_of_this_document`, its legend line, `AnchorNotOpen`/`AnchorOpen`);
  - the remaining reading sets with the no-anchor rows, and the 11-03 "always" tests;
  - ET-E1's U1 legend line and the silence sentence's owner;
  - the derived-wording grammar rows (`profiles=("events@0",)`) and the Lean English policy's registration of the
    fixed wordings (`policyOk` has none, so the two lints disagree on an events block until then);
  - T15-T18, T9's derivations, and T11/T11d through the reader;
  - the use-case regression R1 (narrowed).
- **et-6** (the UDHR pilot), after et-5b and `infra/oom-rootcause`.

Acceptance items: all AGENT.
