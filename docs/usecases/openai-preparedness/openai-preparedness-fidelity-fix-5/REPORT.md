# openai-preparedness-fidelity-fix-5: K13's fast-track words (PF round B, part 3)

No DRI signature is reserved, there is no DELTA, and no question was sent: neither STOP RULE question arose.

- **Task:** prompts/task-openai-preparedness-fidelity-fix-5.txt.
- **Ruling:** orchestrator ruling 2026-11-13 17:23Z (B), on reviews/dri-decisions-20261113-lp1701.md item 1. A documented
  omission earns no credit, and K13 depends on the words the f16-chair units recorded as "loss 1".
- **Branch:** feature/openai-preparedness-fidelity-fix-5. It starts from main 2114035c8c and has main 0f6d59d441 merged in.
- **Scope:** only use-case files changed. Nothing changed in ve/, lean/ or rust/, and there is no key edit: PLAN section 6
  and answer-key.json are untouched.

## Review fix (F1, review of f85aa30ddb)

The probe's f16-fast-track clause still fails, by design: see the third bullet under "What the installed rule says".
Its REPORT clause passes.

**Finding.** Test (c)'s `omission_records` said it applied the omission rule's record paths, but it applied only some
of them. It counted only a `loss` tag as a loss, while the rule counts any other or empty tag as a loss too. The
REPORT also said the rule was not installed, but omission-1 went in at 21:55Z, before this branch's 22:17Z commit.

**Class and fix.** The class is a test's copy of the rule drifting from the installed rule. The fix is structural:
- tests/omission_rule.py is now the one copy in this repository. It ports the installed rule's exposure step whole
  (`omit_exposure`, omission-2, sha256 1c7cc4f79bce94e8), takes the case as a parameter, and reads the working tree.
- test_pf_fidelity_fix.py keeps no rule logic of its own.
- tests/test_omission_rule.py has 48 scenarios on a synthetic case, each with its exact records. They cover every
  record path and the fail-closed answers. test_every_record_path_has_a_scenario fails if a path has no scenario.
  The regression for F1 is the scenarios tag-exposition, tag-dropped, tag-empty and tag-unknown-case, plus
  test_an_exposition_tag_records_its_words_as_a_loss.
- Test (c) is renamed test_k13_units_carry_only_their_exposition_and_plan12_records. It pins the exact records.

**Differential evidence** (omission-differential.json). The installed rule was run in manage-agents; tests cannot read
it.
- All 48 scenarios: the installed rule gives each scenario's expected records, and the port's exposure tuples equal
  the installed rule's.
- The three use cases at dc4348580c, every rule block plus FACTS: the port equals the installed rule on all 397 exposures
  (openai-preparedness 280, anthropic-rsp 93, safety-framework 24).

**What the installed rule says.** The review (22:34Z) ran omission-1. omission-2 replaced it at 22:59Z
(reviews/dri-decisions-20261113-uc-audit-omission-bind.md item 1). In PLAN section 12, omission-2 records every
sentence that names a unit, bare or in backticks, drop word or not, and it widens the drop-word list. At dc4348580c:
- Each chair unit has its two exposition entries, as the review found, and PLAN 12 item 26's sentence naming it.
  K13 is therefore not scored audited until an omission-audit seat's reads clear them.
- No record holds the fast-track words.
- f16-fast-track has item 26's two sentences naming it. So the probe's `set(r) == {chair units}` clause fails under
  the installed rule. Item 26 is the PLAN 12 entry the task requires. Naming the new rule there is the traceable
  record, and dropping the id only to clear the scan would hide a deviation from the rule, so I kept it.
- The README sentence on this fix began in lower case, so the rule's splitter joined it to the sentence before, which
  says "UNFORMALISED". That made a `report` record on f16-fast-track. The sentence now begins "In
  openai-preparedness-fidelity-fix-5". The scenarios readme-lowercase-start and readme-new-sentence pin the boundary.
- Four sentences of this REPORT named a K13 unit next to a drop word: seeded-bug rows c and e, a quoted test output
  and the note for the DRI. They were not omission records, and they are rephrased. Test (c) pins that no `report`
  record names these units.

**Notes.** C1 is fixed (the act is 72 characters). For C2, the "drop sentence" control is now the scenarios
plan12-bare and readme-drop, and test (c)'s comment no longer promises it. C3 and C4 are unchanged (not filed).

## What changed, and the class each fix answers

| Unit | Before | After | Class (translation-fidelity checklist) |
|---|---|---|---|
| f16-fast-track (new rule block) | the fast-track sentence (span p16-u291, 227 bytes) was UNFORMALISED, `unmapped_duty` | Rule 1. Every situation may have a fast track requested so the SAG processes the report urgently, if that situation is classified as "rapid_risk". The block's header quotes the sentence, and its `when` is `always`. | 1 (dropped clause) |
| fast_track_request (new act) | — | A `permission()` act (role permission, default allow): "{0} have a fast track requested so the SAG processes the report urgently". It is 72 characters, letters only, with no reserved word. Its legend quotes the whole sentence. | 1, 11 |
| f16-chair-strict, f16-chair-default (accounting) | the fast-track words carried `loss 1` | The fast-track words are tagged `rule f16-fast-track`. "In the rare case that" and the "(e.g., ...)" example stay exposition. | 1 |
| chair_coordination (legend) | "Appendix B: fast track" (a pointer legend) | The legend quotes its own sentence, "The SAG Chair should also coordinate with OpenAI Leadership for immediate reaction as needed to address the risk." The rule and its RS9 strict/default modals are unchanged. | 11 |
| build_document.py | the sentence was unplaced | `PLACEMENTS` places it as ("rule", "f16-fast-track", ("JT",)). `OPEN_FOR` gets "f16-fast-track": ("ot18",). | — |
| run.py | — | `COMMITMENTS["F16"]` gains the part ("f16-fast-track",). This is needed for N3's inventory, because a rule outside every part counts as a dead commitment. | — |

**Why a separate block.** The task's (a) asks for "a rule or a full-sentence legend of f16-chair-strict and
f16-chair-default". A rule block of this case holds exactly one rule:
- `pf_translation.read_blocks` pairs one header with one sentence.
- `parsed_rule` refuses anything but one rule.

So the permission cannot be a second rule inside the two chair blocks without changing the block format, and the case's
build, run and accounting tools all read that format. The fast-track sentence is also its own source unit (p16-u291),
separate from the Chair's sentence (p16-u292). It therefore got its own rule on its own unit. The chair blocks name that
rule in their accounting.

I did not take the alternative, putting the fast-track sentence into chair_coordination's legend. That would be
documentation, not a rule (the ruling), and it would misdescribe the Chair's act.

The condition test checks that the rule applies under both RS9 choices of the chair blocks, statically and live (test
names below). That is the sense in which it is "of" both blocks.

**Translate what the text grants and no more (PLAN 3.3):**
- "Can" grants OpenAI a permission. The act's subject is the situation, as for every act in this case, and the legend
  names OpenAI ('we') as the one who may request.
- "for the SAG to process the report urgently" is what the request asks for, and it is part of the act.
- I added no duty on the SAG. This is the narrower reading, taken as the conservative option (operations override 2).
  It is recorded here and in PLAN 12 item 26.
- No reading set was added. PLAN 3.1 has none for this "can", and only section 12 may be edited. The rule is `always`.

## K13 and the other items that read these units

`run.py` (full) printed "236 / 239 (1458.4 s)", the same as main's 236 / 239. I compared main's results.json with
HEAD's by script: `comparison` is identical, and the `mutants` and `without_narrowings` sections are unchanged.

| Item | Before (main) | After (HEAD) | Key |
|---|---|---|---|
| K13 | ALL. RS9=strict holds, f16-chair-strict; RS9=default holds soft, f16-chair-default | ALL, unchanged: the same choices, rules and soft flags | ALL, soft under RS9 = default (agree) |
| N3 (inventory, not a key answer) | NONE | NONE. f16-fast-track joins `commitments`, `selected_rules` and `witnesses` (witness: rapid_risk with every level reached) | NONE (agree) |

No other item selects f16-chair-* or f16-fast-track. I checked this by script over results.json items.

K13 stays on its key, so STOP RULE question 1 did not arise.

The headline count is the ruling's estimate: PF 86 -> 87/239 if the re-read audits K13. This item claims nothing
before that re-read.

Metrics changed:
- M3: OPEN 9,073 -> 9,300 bytes and UNFORMALISED 52,848 -> 52,621 (the same change in `bytes_by_kind` norm and
  unformalised).
- M5: regulated_predicates 60 -> 61.
- M10: rules 89 -> 90.

## Regulated predicates

There are 61 of 64. Before this item there were 60; fast_track_request is new.

The count is checked by `test_regulated_predicates_stay_within_64`, which now pins 61 <= 64, and by stage0.json P7.
STOP RULE question 2 did not arise.

## Accounting before -> after

`uv run python usecases/safetyfw_accounting.py openai-preparedness --source <pinned pf-v2.txt> --check` exits 0.

| | Before (main) | After (HEAD) |
|---|---|---|
| Output | 99 blocks, 539 unaccounted words in 75 blocks, 17 blocks with a loss {'1': 19, '3': 1, 'limit 21': 1}, 0 of 116 quotes unanchored | 100 blocks, 539 unaccounted words in 75 blocks, 15 blocks with a loss {'1': 17, '3': 1, 'limit 21': 1}, 0 of 117 quotes unanchored |

- Before is fix-4's REPORT. After is this run.
- The fast-track words no longer carry a `loss` tag on the two chair lines, and the new block's line is "omits:
  nothing". The chair lines' two exposition entries stay, and the omission rule counts them as losses (test (c)).
- The saved report docs/usecases/safetyfw/openai-preparedness/accounting.json was regenerated with `--report`.

## Generated files (each by the case's own script)

- `pf_vocabulary.py` wrote environment.d1.json.
- `build_document.py` wrote spans.json and coverage.json. p16-u291 is now `kind: norm`, `rule: f16-fast-track`,
  `open_terms: [ot18]`, `waits: [JT]`, status OPEN. Totals: {'LABELLED': 5327, 'UNFORMALISED': 52621, 'OPEN': 9300,
  'CHECKED': 170}.
- `stage0.py` and `measure.py` wrote stage0.json, units.json and gaps.json. AP goes from 119 units / 21,554 bytes to
  118 / 21,327, and JT from 34 / 6,282 to 35 / 6,509.
- `source/quote_evidence.py` added the new block to quote-hashes.json.
- `run.py` wrote results.json.
- Hand-edited numbers that the tests pin to these files:
  - README.md: the status and blocker tables, plus one sentence on this fix.
  - The OpenAI PF v2 row of docs/usecases/safetyfw/REPORT.md, updated in place as earlier fixes did, now labelled
    "Nov 13 (openai-preparedness-fidelity-fix-5)".
  - `test_pf_every_byte_has_ve_status_and_one_unit` failed until these were updated. It then gave "1 passed".

## Condition tests (tests/test_pf_fidelity_fix.py)

**(a) test_fast_track_sentence_is_carried_by_a_permission_rule_under_both_chair_readings**
- Both chair headers quote the whole passage.
- Both accounting lines tag the fast-track words `rule f16-fast-track`.
- f16-fast-track is `always`, a "may" rule on fast_track_request, guarded by rapid_risk only.
- The act is a permission within the act limits, and its legend quotes exactly the full sentence, not a pointer.
- chair_coordination's legend quotes its own sentence.
- The chair rules keep must/should and their three predicates, and F16 lists the new part.

**(a, live) test_a_rapid_risk_case_may_request_the_fast_track_under_both_readings** (needs Lean)
- Under RS9 strict and RS9 default, the rapid-risk case selects {f16-fast-track}, with nothing of the opposite sign.
- With OT18 false, nothing is selected.
- f16-fast-track is the only block on the act.

**(b) test_accounting_has_no_loss_for_the_fast_track_words**
- No block has a loss entry on the fast-track words.
- "In the rare case that" and the "(e.g., ...)" example stay exposition on both chair lines.
- f16-fast-track's accounting line is empty.

**(c) test_k13_units_carry_only_their_exposition_and_plan12_records** (rewritten in the F1 fix, see "Review fix")
- The omission rule IS installed. omission-1 went in at 2026-11-13 21:55Z
  (reviews/dri-decisions-20261113-uc-audit-omission-install.md item 1), before this branch's commit 15650040db at 22:17Z;
  omission-2 replaced it at 22:59Z (reviews/dri-decisions-20261113-uc-audit-omission-bind.md item 1). The first version
  of this test wrongly said the rule was absent, and it applied only part of the rule's record paths.
- tests/omission_rule.py now ports the installed rule's exposure step (omission-2, manage-agents tools-local/uc-audit.py,
  sha256 1c7cc4f79bce94e8) whole, every record path included. In particular, any accounting tag other than `restates`,
  `rule` or `reading` counts as a loss, and so does an empty tag.
- Under that rule K13's units (results.json K13 selected_rules = the two chair units) still carry exposures:
  - each chair unit: its two exposition entries, "In the rare case that" and the "(e.g., ...)" example, which count as
    losses, and the PLAN 12 item 26 sentence that names it (in PLAN section 12 every sentence naming a unit is a
    record);
  - f16-fast-track: the two item 26 sentences that name it, and nothing else.
- The test pins exactly these records: the path list per unit, the two exposition words, and that every other record
  is an item 26 sentence. No record holds the fast-track words.
- So K13 is NOT scored audited yet. An omission-audit seat must read K13 and clear each exposure: the dependency read
  must find that K13 does not rest on "In the rare case that" or on the "(e.g., ...)" example, and must cite item 26's
  record sentence. The exposition tags stay, as the task requires.
- The fast-track span is OPEN and adjoins the chair span, which has no untranslated clause.
- Positive control: c3-access-default's exposition entry is found as a loss.

**Unchanged and passing:**
- test_section_6_is_the_frozen_key and test_transcription_is_pinned (tests/test_usecase_key_transcription.py).
- test_answer_key_equals_section_6_cell_by_cell.
- `uv run pytest -q tests/test_pf_fidelity_fix.py tests/test_usecase_key_transcription.py` gave "83 passed".

**Changed test:** test_regulated_predicates_stay_within_64 pinned 60. It now pins 61 <= 64. It pinned a count, not
unfaithful text. No pf_* test in tests/test_safetyfw_usecases.py changed, and no test was removed.

## Seeded bugs (Python use-case files and the Python test helper; no Lean or Rust product code changed)

Each was planted, run against its test, and restored. They are also recorded in mutants.json. Rows a, b, d and g
were run on 15650040db. Rows c, e and f were run again on the F1 fix against the rewritten test (c), and rows h, m5
and p1 to p4 are new with that fix. The rows name the chair units by their accounting line and the PLAN item instead of by
block id, because a REPORT sentence that names a unit next to a word like "loss" is itself an omission record.

| # | File | Bug | Failing test (output) |
|---|---|---|---|
| a | usecases/openai-preparedness/rules.d1.ve | the new permission restricted to RS9=default (absent from the strict chair reading) | test_a_rapid_risk_case_may_request_the_fast_track_under_both_readings ("AssertionError: strict") |
| b | usecases/openai-preparedness/rules.d1.ve | the new permission restricted to RS9=strict (absent from the default chair reading) | the same test ("AssertionError: default") |
| c | usecases/openai-preparedness/accounting.d1.txt | line 63's tag for the fast-track words set back to "loss 1" | test_accounting_has_no_loss_for_the_fast_track_words (AssertionError naming line 63's unit, its words and "loss 1") and test_k13_units_carry_only_their_exposition_and_plan12_records |
| d | usecases/openai-preparedness/rules.d1.ve | the permission made a duty ("Every situation must have a fast track requested ...") | test_fast_track_sentence_is_carried_by_a_permission_rule_under_both_chair_readings (startswith "may" is False); the live test (ve.errors.SyntaxError: no declared reading) |
| e | usecases/openai-preparedness/PLAN.md | a new PLAN 12 item 27 naming line 63's unit in backticks with a drop word | test_k13_units_carry_only_their_exposition_and_plan12_records (a third `plan12` record) |
| f | usecases/openai-preparedness/build_document.py | the sentence's placement removed (spans.json and coverage.json regenerated; p16-u291 back to UNFORMALISED) | test_k13_units_carry_only_their_exposition_and_plan12_records (StopIteration: no span carried by the new rule) |
| g | usecases/openai-preparedness/pf_vocabulary.py | fast_track_request declared with duty() | test_fast_track_sentence_is_carried_by_a_permission_rule_under_both_chair_readings (ve.errors.SyntaxError) |
| h | usecases/openai-preparedness/accounting.d1.txt | line 63's fast-track words tagged as carried by the strict chair rule itself | test (c) (a `mistag` record) |
| m5 | usecases/openai-preparedness/accounting.d1.txt | line 63's "In the rare case that" retagged `dropped` (the review's mutant M5) | test (c) (the record list holds "(dropped)", not "(exposition)") |
| p1 | tests/omission_rule.py | the "any other or empty tag = loss" branch removed (F1's class) | 5 test_each_record_path_of_the_omission_rule scenarios (tag-exposition, tag-dropped, tag-empty, tag-unknown-case, line-unparseable), test_an_exposition_tag_records_its_words_as_a_loss and test (c) |
| p2 | tests/omission_rule.py | a tag resolves when ANY of its words is in a carrier segment, not all | 4 scenarios (restates-missing-word, restates-negation-counts, restates-across-segments, rule-not-carried) |
| p3 | tests/omission_rule.py | PLAN 12 sentences record only with a drop word | 5 scenarios (plan12-bare, plan12-h3, gaps-text, ...) and test (c) |
| p4 | tests/omission_rule.py | gaps / coverage files not scanned | 4 scenarios (gaps-json, gaps-json-key, gaps-text, gaps-unparseable) |

## Checks run

- `lake build` (after lean-prep.sh): "Build completed successfully (1438 jobs)". Lean is unchanged; the build is for the
  service that run.py uses.
- `run.py` (full): "236 / 239 (1458.4 s)".
- The accounting check is in the section above.
- `tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0 … PASS".
- light-lane.py: "NOT 390 changed lines outside generated files > 150 (18 files) against 2114035c". The count includes
  results.json, spans.json, coverage.json, environment.d1.json and the stage-0 and accounting evidence, which the case's
  scripts generate.
  - No trusted-core or Lean file changed, trusted growth is +0, and the task asks for no trust_mutants record.
  - Build checklist 13a applies only to trusted Lean growth.
  - So no sweep was run, as in fix-4.
- `tools/select_tests.py --base <merge-base>` selects test_pf_fidelity_fix.py, test_safetyfw_usecases.py,
  test_safetyfw_accounting.py and test_usecase_key_transcription.py, among 55 files. It does not select every unit.
- `conformance/english_lean_lexicon.py` regenerated conformance/english-lean/lexicon-report.json (commit 9dff05b37c):
  only the openai-preparedness environment.d1.json row moves (symbols 137 -> 138, its lexicon_id). The first selected
  run found it stale (test_every_corpus_environment_has_a_valid_selected_lexicon, as fix-4 did); after the rewrite
  that test gave "1 passed". `tools/regen_generated.py --check` was clean ("checked 41 entries"): the report is not
  one of its entries.

## Final selected run

1. On 15650040db: `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base <merge-base> --run` exited 1 in its fast
   stage ("FAILED tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon",
   "1 failed, 512 passed"); its five shards were not waited for, so the other units gave no answer.
2. On 9dff05b37c (clean tree, the lexicon fix committed): the same command exited 0. "fast first: the cheap units
   passed after 148 s"; "SHARD 1/5: exit 0 ... 18 units, 18 passed", "SHARD 2/5: ... 14 units, 14 passed",
   "SHARD 3/5: ... 13 units, 13 passed", "SHARD 4/5: ... 11 units, 11 passed", "SHARD 5/5: ... 11 units, 11 passed";
   "summary: selected tests ran on GitHub Actions (5 shards, run openai-preparedness-fidelity-fix-5-9dff05b3-t606631);
   exit=0; 1615s". Only this REPORT changes after it.

3. F1 fix, on a9206bfc9b (clean tree): `zsh mac-pytest.sh --select -- --base <merge-base> --run` exited 0. "47/616
   test units"; changed tests ran first (tests/test_omission_rule.py, tests/test_pf_fidelity_fix.py); "fast first: the
   cheap units passed after 105 s"; "SHARD 1/2: exit 0 in 1000.9 s; 27 units, 27 passed", "SHARD 2/2: exit 0 in
   1163.0 s; 20 units, 20 passed"; "summary: selected tests ran on GitHub Actions (2 shards, run
   openai-preparedness-fidelity-fix-5-a9206bfc-t615550); exit=0; 1299s". Before it, on the same tree:
   `lake build` (after lean-prep.sh) "Build completed successfully (1438 jobs)", `python3 lean/audit.py` "PASS: 872
   source files; 9965 named theorem declarations audited", and `tools/regen_generated.py --check` "checked 41
   entries". Only this REPORT changes after it.

## Open list

- K13 is not scored audited yet: an omission-audit seat's reads must clear the four exposition exposures and the
  two PLAN 12 item 26 records on the chair units (test (c)). The re-read decides, not this branch.
- The pf-split-relay-astra row (Astra seat of the four-class relay on the 15 PF split units) has no result: there is
  no reviews/pf-split-relay* in manage-agents at the time of writing. So no REAL unit was added (deliverable 3), and it
  is named as the next item.
- C6, C-doc and G9 remain key findings, unchanged (PLAN 12 items 19, 20 and 25).
- Out of scope, untouched: K15 and K20 (the lp1701 item 1 read says they do not depend).

## Budget readings

The launcher's reading is in the task. At 2026-11-13T19:20Z the joint cap had 5.69M of 14M left, and the round budget
was 1.00M (ALLOCATED: START). No openai-preparedness-fidelity-fix-5 loop log exists in manage-agents, so I took no
further reading. I did not run ucfix-budget.py, as the task says.

## Size

SIZE: 18 product, 159 tests, about 190 other hand-written lines.
- Product: rules.d1.ve 2, pf_vocabulary.py 10, build_document.py 2, run.py 1 and accounting.d1.txt 3 added lines, with
  5 lines removed.
- Other: PLAN 18, README 7, the safetyfw REPORT 1, this REPORT and mutants.json.
- Generated files are not counted.
- The F1 fix adds 500 test lines (tests/omission_rule.py 281, tests/test_omission_rule.py 183, test_pf_fidelity_fix.py
  36 added and 62 removed) and 3 README lines. It changes no product line.

## Next item

- After merge, the DRI decider launches two things:
  - the production checklist pass, which re-reads ONLY the changed units (f16-chair-strict, f16-chair-default and
    f16-fast-track);
  - the full union audit at the Nov 23 checkpoint.
- pf-split-relay-astra: when its result lands and the decider rules units REAL, a fix-6 adds them in the order of
  answers regained, under the same rules as fix-4.

## Notes for the DRI

- The task's condition (a) assumed a block could carry the permission. The case's format allows one rule per block,
  so the permission is its own block on its own source unit, and the chair blocks' accounting names it. See "Why a
  separate block" above. If the audit's manifest for K13 should list the new rule among its uses, its only records
  are PLAN 12 item 26's two sentences (test (c) pins them).
- The narrower reading was taken: no duty on the SAG to process the report urgently.

## Spec re-read

- "we can request a fast track for the SAG to process the report urgently": checked against the pinned pf-v2.txt
  (byte 51430, the Fast-track paragraph) and usecases/openai-preparedness/PLAN.md 3.3 ("No permission the text does not
  grant").
- The record paths: tests/omission_rule.py is checked against the installed manage-agents tools-local/uc-audit.py
  omit_exposure (omission-2, sha256 1c7cc4f79bce94e8, lines 1681-1827) by the differential in omission-differential.json
  (see "Review fix").
- The act-phrase limits: checked against lean/VE/Acts/LexicalBase.lean:7 actReserved, and against
  reviews/ucfix-classify-20261111.md (80 characters; the 64 cap counts regulated predicates only).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer, relay or schema changed (use-case files only).
2. PASS. Deliverables 1 and 2 are built (commits 294fa87046 and the tests commit). Deliverable 3 waits on a result that
   has not landed, so it is the next item, as the task allows. The diff has no Python copy of a Lean decision and no
   report test. Overlap was checked: main's merged branches touch no PF file.
3. PASS. Thirteen seeded bugs, each with its failing test (mutants.json). Test (c) has a positive control, and
   test_omission_rule.py has a scenario for every record path (test_every_record_path_has_a_scenario).
4. PASS: run.py's comparison against the key is identical before and after, 236/239.
5. N.A.: no binding changed.
6. PASS. Main was merged before the final selected run. The gate runs on the final HEAD in the chain.
7. PASS: no DELTA, no trust growth (trust_map +0).
8. PASS. No user-visible VE output changed: no ve/, lean/ or rust/ change, and DELTA is none. The use-case outputs
   are in this REPORT.
9. PASS: select_tests selects the four PF test files.
10. N.A.: no Lean statement.
11. N.A.: no budget or limit code. The new tests use no sleep or deadline.
12. N.A.: no evaluator change. run.py took 1458 s against fix-4's 1126 s. That is a whole-case run on a shared VM and
    not a measurement.
13. PASS: no test was removed or renamed.
14. PASS. Both directions are covered: the rapid-risk case selects the permission and the calm case selects none; the
    record-path test has a positive control. Each claim here names its command.
15. PASS. No overclaim: K13's credit is left to the re-read. No silent cut: deliverable 3 is named. Every new check has
    a mutant (a to g). N.A. for limits.
