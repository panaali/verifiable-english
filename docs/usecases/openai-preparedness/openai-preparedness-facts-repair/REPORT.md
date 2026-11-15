# openai-preparedness-facts-repair: two fact-block accounting tags, and Table 1's column titles

**Status:** done, ready for the gate. No DRI signature is reserved, and no DRI question was sent.
**What changed:** the two mistagged fact-block entries now resolve under the installed counter (exposure.py: 8 -> 6 on
the fact and case units, and the two mistags are the only change). Table 1's header span is five units, and RS1's
column title is its own OPEN unit (folded ruling). The fix-2 REPORT sentence stays as written (DRI answer, item 3).
**Open:** the true records listed under "Honest records left" wait for the per-answer reads (row facts-cases-omission-reads).

Ruling: orchestrator re-plan ruling 2026-11-14 item A3; reviews/dri-decisions-20261114-replan-ruling.md;
reviews/facts-cases-diag-20261114.md section 1. Folded: architect ruling pf-table1-header-20261115.md section 5,
signed by reviews/dri-decisions-20261114-facts-void.md item 4. Base: main ceb42aabd9.

## Deliverables

| # | Task | Done | Evidence |
|---|---|---|---|
| 1 | the 4.2 Critical-safeguards entry of `rs2-nest` names a block whose carrier holds every word | tagged `rule f3-reminder` | see "Step 1" |
| 2 | the 4.4 sentence quoted in its predicate's legend | `existing_at_publication`'s legend quotes it verbatim | see "Step 2" |
| 3 | the fix-2 REPORT sentence at line 102 | left as written, as the DRI answered (reviews/dri-decisions-20261114-facts-void.md item 1); no question sent | `git diff main -- docs/usecases/openai-preparedness/openai-preparedness-fidelity-fix-2/REPORT.md`: empty |
| F1 | `segments()` gives the header bytes 13,460-13,821 five units | done | spans.json p6-u65 to p6-u69; test_table_1_header_is_five_units_and_the_fourth_title_is_rs1_open |
| F2 | the fourth title is a `readings` unit of RS1 (`rs1-header`), OPEN | done, preferred content: `strict` lists the seven `-strict` blocks and `default` the seven `-default` blocks (the format takes a block in two sets: the build and VE's check accept it) | same test; spans.json p6-u68 status OPEN |
| F3 | second title placed as `hedged_claim` (AT), the definition as `unmapped_claim` | done; the first and third titles are UNFORMALISED `unmapped_claim` too (the ruling's "if in doubt" choice; none LABELLED) | spans.json p6-u65, p6-u66, p6-u67, p6-u69 |
| F4 | no change to the `reading RS1` tags, no legend quotes the title | done | `git diff main -- usecases/openai-preparedness/accounting.d1.txt`: one line, the 4.2 entry; the header test asserts no legend holds "guidelines" |
| F5 | PLAN 12, one item | item 28; it names no rule or fact block | the after output has no plan12 row from it |
| F6 | acceptance | below | |

## Step 1: the 4.2 sentence

The sentence is "Systems that reach Critical capability also require safeguards that sufficiently minimize associated
risks during development". The act legend of `safeguards_during_development` has quoted it in full since fix-5. The block
`f3-reminder` regulates that act, has no reading condition (`always`), and requires it of every situation that has reached
a Critical level and is further development, which is what the sentence says. Its carrier (body statements plus the
legends of the predicates it uses) holds every word in one segment, the act legend. So no legend changed for this
step: only the tag moved, from `reading RS2` to `rule f3-reminder`. The `rs2-nest` block keeps its RS2 header, which
reads the sentence's "also" as the nesting, and that is what its formula states.

## Step 2: the 4.4 sentence

The formula of `no-critical-models` says that no situation classified `existing_at_publication` has reached a Critical
level, and the predicate is dated 2025-04-15. The predicate's legend now reads: "the model at {0} is one OpenAI possessed
at publication (2025-04-15), the time of 4.4's “We do not currently possess any models that have Critical levels of
capability”". The quote is the source text word for word (`grep -c` in the pinned text: 1), and it is part of the
block's header quote, which quote-hashes.json pins. The tag was already `restates`. It now resolves, because the legend
is a segment of the block's carrier. The regulated count stays 61 of 64, since the predicate is not regulated
(test_regulated_predicates_stay_within_64).

## Accounting entries, before -> after

The verbatim lines are not copied here: they hold the accounting tags, and the REPORT scan would read them as records.
`git diff main -- usecases/openai-preparedness/accounting.d1.txt` shows the one changed line. In words: the `rs2-nest`
line's only entry kept its words, and its tag went from `reading RS2` to `rule f3-reminder`. The `no-critical-models`
line did not change; its first entry resolves through the new legend.

## Exposure (exposure.py, before and after)

Command: `python3 -I /home/seyran/code/manage-agents/reviews/facts-cases-diag/exposure.py openai-preparedness <commit>`
(installed counter sha256 f4345f44; the script resolves a ref in the main checkout, so the commit sha is passed). The
outputs are saved verbatim beside this file: `exposure-before.txt` (main ceb42aabd9, 8 on the fact and case units) and
`exposure-after.txt` (this branch, 6). Rows gone: the two mistag rows. Rows left: the same records as before, with
one id moved by the header split (the span p13-u212 is now p13-u216). The D2D3 row (no accounting line) is in both
outputs and is not counted.

Every unit, not only the shared ones: `/tmp/pffr/scripts/allexp.py` (written for this check; it calls the installed
`omit_exposure` on both commits and compares) gives 253 rows on main and 251 on d4d72cfe2a. The rows only on main are
the two mistags and 13 span records under their old ids; the rows only on the branch are the same 13 under their new
ids. No row is new. That run was before this REPORT existed. `exposure-after.txt` is from the commit that adds this
REPORT, so it covers the REPORT's own sentences too.

## Honest records left (each stays an exposure for the per-answer read)

These are true records, and this item does not reword them:
- the 4.4 entry "and we expect to further update this Preparedness Framework …" of `no-critical-models`, tagged
  `exposition` (the counter counts any tag outside the three carrier tags as an exposure);
- the span p13-u216 (old id p13-u212): the 4.4 sentence's unit, waiting for AT (held);
- PLAN 12 items at PLAN.md:485 and PLAN.md:596, which name the two fact blocks (three rows);
- the fix-2 REPORT sentence at line 102 (DRI answer: stays; record-level adjudication or the per-answer read).

## Table 1 header: acceptance (ruling section 5 step 6)

- `uv run python usecases/openai-preparedness/build_document.py` wrote spans.json and coverage.json:
  `{'LABELLED': 5327, 'UNFORMALISED': 52586, 'OPEN': 9335, 'CHECKED': 170}`. On main: UNFORMALISED 52,621, OPEN 9,300.
  UNFORMALISED bytes fell by 35, exactly the fourth title ("Risk-specific safeguard guidelines ", bytes 13,557-13,592),
  and no title is LABELLED. `build_document.py --check` passes inside
  test_pf_checked_has_no_wait_or_unmapped_source_clause (it calls `main(["--check"])`).
- measure.py and stage0.py rewrote gaps.json, units.json and stage0.json; `usecases/safetyfw_accounting.py ... --check
  --report` rewrote accounting.json ("100 blocks, 524 unaccounted words in 73 blocks ... 0 of 117 quotes unanchored";
  the three 4.4 words now accounted are "capabil", "current" and "posses").
- run.py rewrote results.json ("236 / 239", 1,672.6 s). Answers: `items` and `comparison` equal main's
  (python comparison of /tmp/pffr/results-before.json with the new file: "items equal True comparison equal True"); the
  only key that differs is `metrics`: M3's byte counts above, M3's unresolved reading sets 31 -> 32 (the new RS1 unit),
  and M10's units 389 -> 393. Not byte for byte the same file, because those metrics read coverage.json and spans.json.
  No answer moved (moved: []).
- The five spans and the header unit's reading set: test_table_1_header_is_five_units_and_the_fourth_title_is_rs1_open
  (status OPEN, never CHECKED or LABELLED; the rebuilt records equal spans.json when the pinned source is present).
- Unit ids: old p6-u65 is now p6-u65 to p6-u69. The old p6-u66 to p22-u389 are now p6-u70 to p22-u393, every
  id + 4. The full map, with spans and statuses, is `unit-ids.tsv` beside this file (329 rows). Apart from the id (and
  the residual names that hold it) no unit after the header changed (python comparison of the main and branch
  spans.json: "changed beyond id: []"). Hand-written ids that moved with them: two comments in build_document.py, the
  README's 4.1 sentence, and the pinned ids of the PF tests in tests/test_safetyfw_usecases.py and
  tests/test_pf_fidelity_fix.py. The PLAN 12 items before 28 keep the ids of their own date; item 28 says so.
- The README's coverage tables and the PF row of docs/usecases/safetyfw/REPORT.md hold the new numbers
  (test_pf_every_byte_has_ve_status_and_one_unit pins both to coverage.json and gaps.json).

## Tests

New in tests/test_pf_fidelity_fix.py:
- test_retagged_facts_entries_are_carried_by_the_block_their_tag_names: a local carrier (`tag_carrier`, built on the
  helpers of tests/omission_rule.py, the counter's port) and the counter's tag rule: every token but articles in one
  segment. Each entry is carried by exactly the legend named, the rule really means the sentence (act, guard, `always`;
  the fact formula), and the port finds no mistag on the fact blocks.
- test_a_carrier_without_the_words_does_not_hold_the_entry: the opposite direction; the 4.2 words against the block
  the tag used to name, and the 4.4 words with the legend quote cut, are carried by no segment.
- test_retagged_legend_quotes_are_verbatim_source_text: both legend quotes are the whole sentence, part of the block's
  pinned header quote, and source text under quote_evidence's check when the pinned source is present.
- test_table_1_header_is_five_units_and_the_fourth_title_is_rs1_open (above).

Runs: `uv run pytest -q tests/test_pf_fidelity_fix.py tests/test_safetyfw_usecases.py -k "test_pf or fidelity_fix"`:
111 passed (28:30).

Selected run: `MAC_PYTEST_NO_DEFER=1 zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`.
The first run (commit cfe1cfa649, before the lexicon report) failed one test in its fast stage,
`tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon`. The committed
`conformance/english-lean/lexicon-report.json` pins each corpus environment's lexicon id, and the new legend moves the
PF environment's id. `uv run python -m conformance.english_lean_lexicon` rewrote that one id (`{"valid": 43, "invalid": 0,
"failures_by_condition": {}}`), commit 3f56fc5ff6. The second run, on 3f56fc5ff6 (tree 4f32fdd17d, clean), exit 0:
"recorded 255 units for tree 4f32fdd17d; ... 0 failed" (ran on ve-cloud-2, 11,711 s). No test of main-known-red.txt was hit.

## Seeded bugs (each planted, the named test failed, restored with `git checkout`)

| # | Language, file | Bug | Failing test |
|---|---|---|---|
| a | Python, usecases/openai-preparedness/pf_vocabulary.py | the new 4.4 legend phrase taken out | test_retagged_facts_entries_are_carried_by_the_block_their_tag_names (`assert [] == ['legend existing_at_publication']`) |
| b | data, usecases/openai-preparedness/accounting.d1.txt | the 4.2 entry tagged back to `reading RS2` | test_retagged_facts_entries_are_carried_by_the_block_their_tag_names (the tag assertion) |
| c | Python, usecases/openai-preparedness/pf_vocabulary.py | one word of the legend quote: "currently" -> "presently" | test_retagged_legend_quotes_are_verbatim_source_text |
| d | Python, usecases/openai-preparedness/build_document.py | the boundary before the fourth title taken out of `segments()` | test_table_1_header_is_five_units_and_the_fourth_title_is_rs1_open (the rebuild refuses: "two translations in one source unit") |
| e | Python, usecases/openai-preparedness/build_document.py | the fourth title placed as `unmapped_claim` instead of RS1's reading set | test_table_1_header_is_five_units_and_the_fourth_title_is_rs1_open (rebuilt record 3 differs) |

Seeded bug (e) survived the first form of the header test, which compared only ids and spans. The test now compares the
five rebuilt records whole (commit 0bc8f76667).

## Trust, DELTA, size

- No ve/, lean/, rust/, run.py or stage0.py change. `uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0,
  tied +0, unclassified +0, trusted +0 ... PASS". No trust_mutants sweep: light-lane printed NOT, but only because it
  counts the case scripts' outputs (spans.json, results.json, units.json) as hand-written; the item changes no trusted
  Lean, and neither the task nor checklist 13a (trusted Lean growth) asks for a sweep.
- DELTA: none. VE's behaviour is the same; only use-case records, their generated outputs and tests change.
- SIZE: 28 product (accounting.d1.txt 1/1, pf_vocabulary.py 3/1, build_document.py 19/3: added/removed), 163 tests
  (test_pf_fidelity_fix.py 121/2, test_safetyfw_usecases.py 20/20), 35 other hand-written lines (PLAN.md 10, README.md
  13/10, docs/usecases/safetyfw/REPORT.md 1/1), plus this REPORT and its saved outputs. Command:
  `git diff --numstat $(git merge-base HEAD main)`, without the generated files.

## Spec re-read

- The 4.2 tag against reviews/facts-cases-diag-20261114.md section 1 (PF row 1) and the task's step 1: a block whose
  carrier holds every word; it is the act legend of the rule's own act.
- The 4.4 legend against the task's step 2: verbatim, and the formula states exactly that, dated 2025-04-15.
- The header units against pf-table1-header-20261115.md section 5 steps 1-6: five boundaries; family id `rs1-header`;
  strict/default lists; the second title explicitly AT; the definition `unmapped_claim`; no accounting or legend change
  for the title; the PLAN 12 item names no unit; acceptance as above.

## Answers old -> new

None moved. results.json `items` and `comparison` are identical to main's (above). 236 of 239 agree, as before.

## Notes for the DRI

- Files beyond the task's list, each because a test pins it: usecases/openai-preparedness/README.md (coverage numbers,
  one sentence, the two moved ids), docs/usecases/safetyfw/REPORT.md (the PF coverage row), tests/test_safetyfw_usecases.py
  (unit ids), conformance/english-lean/lexicon-report.json (the PF lexicon id, from its own generator). `tools/regen_generated.py --write` also refreshed docs/codemap/ (two files that lagged main's own changes).
- Every UNFORMALISED residual name after the header holds its unit id, so those names moved with the ids. Reads bound to
  old ids or residual names (reviews/uc-audit-omission/*-pf.tsv) need the new ids. They are commit-bound and must be
  redone anyway.
- The second title had a residual name on main (the fallback gives one); its explicit placement, like every explicit
  hedged placement in the file, gives none.
- Notes: none filed as follow-ups.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relay or schema change.
2. Every deliverable built, no rule broken: PASS, deliverables table above; no ve/lean/rust/run.py edit (`git diff --stat main`).
3. Tests and gates can fail: PASS, seeded bugs a-e above, each with its failing test.
4. Python, Lean and Rust agree: N.A., no checker change; results.json answers equal main's (comparison above).
5. R8 binding: N.A., no relay.
6. Gate evidence matches final HEAD: PASS, the selected run passed on tree 4f32fdd17d (commit 3f56fc5ff6); later commits touch only this REPORT.
7. No unsigned item: PASS, no DELTA row and no reserved signature.
8. Every user-visible change in DELTA: N.A., no VE behaviour change (trust_map --check +0; answers identical).
9. Test selection finds the tests: PASS, `tools/select_tests.py --base <merge-base>` lists test_pf_fidelity_fix.py and test_safetyfw_usecases.py.
10. Lean statements: N.A., no Lean change.
11. Budgets fail closed: N.A., no evaluator or limit.
12. No CPU or memory regression: N.A., run.py's work is the same (documents_built 352, prover_calls 13 in results.json, unchanged).
13. Test-removed trailers: N.A., no test removed or renamed (`git diff main -- tests | grep '^-def '`: none).
14. Both directions, cited evidence, spec re-read: PASS, test_a_carrier_without_the_words_does_not_hold_the_entry (refuse side) with the carried tests (accept side); claims cite commands; "Spec re-read" above.
15. Overclaim, silent cuts, checks that can fail, limits: PASS, universal words in this REPORT cite a command or test; nothing cut; seeded bugs a-e; limits N.A.
