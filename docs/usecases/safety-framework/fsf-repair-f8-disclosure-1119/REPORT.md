# fsf-repair-f8-disclosure-1119 REPORT

Repair row F8 (reviews/pathf-q3/flag-analysis-1119/converge-AB.md "F8", compare-report.md row F8; Amendment R16).
LANGUAGE only: three vocabulary legends quote the pinned source verbatim. No Lean, Python decision or Rust change,
trust +0, no DELTA row (DELTA.md).

**Kind call your reviewer should check (the row says KIND CALLS STILL DIFFER).** For B-L0/DISC and B-L4/DISC (key
NONE): A calls them TEXT (they depend on S:17); B calls them UNCERTAIN (these keys say no disclosure duty applies).
This item carries the text either way, and no action turns on the call. The reviewer should check B's reading, i.e.
whether a NONE key on DISC is cleared by the disclosure conditions at all. K6/YEARLY_REVIEW and K8/FREQUENT_REVIEW
are TEXT on both sides once B's correction holds (they quote 5.1, not S:17).

**Merges at.** The branch is rebased onto main 9b72137abf (after fsf-repair-f5-lowrisk-1119 merged). The VE commit
that freezes the text is cce9cc345f, and the branch HEAD is the commit that holds this REPORT. The merge train makes
the merge commit. The R16 C2/C3 pins are per commit, so the counted read re-pins at that merge. A
merge after the R16 diagnostic voids that diagnostic for the touched answers (B-L0/DISC, B-L4/DISC, K6/YEARLY_REVIEW,
K8/FREQUENT_REVIEW, and the other DISCL answers whose prompts show these legends).

## 1. Deliverables

| # | Deliverable | Status |
|---|---|---|
| 1 | S:17 passage and the 5.1 sentence, verbatim, in a counted carrier | done: `usecases/safety-framework/vocabulary.py` (`DISCLOSED_INFORMATION`, `REVIEW_PROCESS`) |
| 2 | Condition test in a new file | done: `tests/test_fsf_repair_f8_disclosure_1119.py` |

No fallback was used. The carrier check passes in the sense the counter's code defines (see section 3). The dry-run
itself could not run, because the counter is not installed.

### Source (pinned `fsf-3.1.txt`, SHA-256 18e3375b…3c946, 54,373 bytes; line 17 = PDF page 17)

5.2 Disclosures, second sentence and its three bullets (S:17):

> Where appropriate, and subject to adequate confidentiality and security measures and considerations around
> proprietary and sensitive information, this information may include: ● Model information : characteristics of the
> AI model relevant to the risk it may pose with its critical capabilities. ● Evaluation results : such as details
> about the evaluation design, the results, and any robustness tests. ● Mitigation plans : descriptions of our
> mitigation plans and how they are expected to reduce the risk.

5.1 Updates, second sentence:

> The process will involve (i) an assessment of the Framework’s appropriateness for the management of significant
> and severe risk, drawing on information sources such as record of adherence to the framework, relevant
> high-quality research, information shared through industry forums, and evaluation results, as necessary, and (ii)
> an assessment of our adherence to the Framework.

Both were taken from the source file with a regex over its whitespace-collapsed text (the command is in section 4),
not from any reader, flag or diagnostic output. The text keeps the source's own characters: the `●` bullets, the
` : ` after each bullet label and the curly `’`. Each sentence is written once in vocabulary.py, in a module
constant.

### Carriers (CARRIER GUARD, converge-AB.md section 0)

| Sentence | Predicate legend | Block that uses it (rules.d1.ve) | Answers |
|---|---|---|---|
| S:17 | `shared` (obligation; act "share relevant information with appropriate government authorities") | `f19-default` Rule 1 | B-L0/DISC, B-L4/DISC (DISCL) |
| 5.1 | `yearly_review` | `f18-yearly` Rule 1 | K6/YEARLY_REVIEW |
| 5.1 | `frequent_review` | `f18-frequent` Rule 1 | K8/FREQUENT_REVIEW |

Each legend ends `(5.1: "<sentence>")` or `(5.2: "<sentence>")` after its earlier text, which is unchanged. The
sentences sit in legends of predicates the blocks use, so not in a header or citation run and not in a constant table.
The 5.1 sentence is in both review legends because K6 and K8 are separate answers on separate blocks.

## 2. Condition test

`tests/test_fsf_repair_f8_disclosure_1119.py::test_each_new_legend_quotes_the_source_sentence_byte_for_byte[S:17|5.1]`:
- It reads each sentence from the pinned source through `tests/pinned_source.py`, using the same quote normalisation
  as fsf-repair-f5 (whitespace runs collapse to one space; curly quotes become straight).
- It checks the sentence's SHA-256, which is frozen in the test.
- In both `vocabulary.environment()` and the committed `environment.d1.json`, it asserts that each carrier legend
  quotes exactly those bytes.
- It also asserts that the carrier is an obligation whose act is stated by its block's Rule line.
- Without the stored source (the gate runner, tools/gate-optional.json), the frozen hash still pins the quote, so the
  test runs instead of skipping.

| Run | Result |
|---|---|
| this branch (`uv run pytest -q tests/test_fsf_repair_f8_disclosure_1119.py`, /tmp/f8-t1.log) | 2 passed |
| this branch, `HOME=/tmp/nohome` (no pinned source; /tmp/f8-t2.log) | 2 passed |
| legends of 7cbec4b340b8 (`git checkout 7cbec4b340b8 -- vocabulary.py environment.d1.json`; /tmp/f8-base-7cbec4b340b8.log) | 2 failed |
| legends of main d8758ce968 (/tmp/f8-base-main.log) | 2 failed |

`tools/select_tests.py --base d8758ce968` (before the rebase) selects the test (/tmp/f8-plan.log: 67/649 units, including
tests/test_fsf_repair_f8_disclosure_1119.py, tests/test_safety_framework.py and tests/test_english_statement_blocks.py).

## 3. Prompt size (R16 C5 dry-run)

The counter version reads-1119 is **not installed**. `tools-local/uc-audit.py` differs from
`uc-audit.py.reads-1119` (`cmp`), and the installed file says `SEQ_COUNTER_VERSION = 'oseq-bind-1'`. So no dry-run
was run, and the decider re-checks at the counted read. Measured growth of each legend, as C5 renders it (whitespace
collapsed, UTF-8 bytes, main vs this branch):
- `shared`: 99 to 614 (+515)
- `yearly_review`: 72 to 455 (+383)
- `frequent_review`: 74 to 457 (+383)

A unit's prompt grows by at most +515 bytes (f19-default). The FACTS unit's prompt does not show these legends,
because it uses none of these predicates. The max prompt size with all appends is UNVERIFIED until the reads-1119
dry-run.

The carrier, as `seq_unit_legends` in `uc-audit.py.reads-1119` (lines 1202-1222) defines it, is the description in
environment.d1.json of each predicate `used_predicates` finds in the block body. That is where these sentences are.

## 4. Commands and regenerated files

- Source extraction:
  `re.search(r"Where appropriate, and subject to adequate.*?how they are expected to reduce the risk\.", t)` and
  `re.search(r"The process will involve \(i\).*?an assessment of our adherence to the Framework\.", t)`, where
  `t = " ".join(fsf-3.1.txt.split())`.
- `uv run python tools/regen_generated.py --write` (after `tools/rust_build.py` and `lake build`): wrote 41 entries.
  It changed only docs/codemap/**, which is stale on main for files outside this item. That check is advisory on
  branches and regenerated on merge, so those changes were reverted.
- The use case's own outputs, regenerated the way fsf-repair-f5 did:
  - `python usecases/safety-framework/vocabulary.py` wrote environment.d1.json.
  - `python usecases/safety-framework/run.py` left results.json unchanged (`git status`).
  - `build_document.py --source /tmp/f8-src/fsf-3.1.txt` wrote coverage.json (document hash only).
  - `docs/en-e3-norm/en-2b/route_fixtures.py --write` wrote tests/data/route-cases.jsonl (the `stale` case embeds the
    environment).
  - `conformance/english_lean_lexicon.py` wrote lexicon-report.json (a hash).

Files: usecases/safety-framework/{vocabulary.py, environment.d1.json, coverage.json}, tests/data/route-cases.jsonl,
conformance/english-lean/lexicon-report.json, tests/test_fsf_repair_f8_disclosure_1119.py, and this directory.

## 5. Seeded bugs (Python, in `usecases/safety-framework/vocabulary.py` unless named; each restored with `git checkout`)

| Seed | Mutation | Failing test (log) |
|---|---|---|
| s1 | drop the third bullet ("● Mitigation plans : …") from `DISCLOSED_INFORMATION` | `[S:17]` (/tmp/f8-seed-s1-drop-bullet.log) |
| s2 | paraphrase 5.1: drop "as necessary," from `REVIEW_PROCESS` | `[5.1]` (/tmp/f8-seed-s2-paraphrase-51.log) |
| s3 | `frequent_review` legend loses its 5.1 quote (only `yearly_review` keeps it) | `[5.1]` (/tmp/f8-seed-s3.log) |
| s4 | stale committed `environment.d1.json`: "any robustness tests" becomes "robustness tests" | `[S:17]` (/tmp/f8-seed-s4-stale-environment.log) |
| s5 | `shared` legend loses its quote (S:17 in no carrier) | `[S:17]` (/tmp/f8-seed-s5-wrong-carrier.log) |

Lean and Rust: no product code changed, so no seed is needed there. Trust mutants: the light lane printed `LIGHT 119
changed lines outside generated files <= 150 (6 files), no trusted-core file, against d8758ce9`, and the task file
asks for no trust_mutants record, so no sweep was run.

## 6. Trust, DELTA, size

- Trust +0: no file under lean/, ve/, rust/ or tools/ changed.
- DELTA: no rows (DELTA.md).
- SIZE: 22 product (vocabulary.py), 85 tests, 0 other hand-written lines outside this directory (generated files
  excluded).

## 7. Selected run

`zsh mac-pytest.sh --select -- --base d8758ce968 --run` (log /tmp/f8-select.log; rc file 0):
- Ran on ve-cloud-2, from a snapshot at HEAD c5781618. That is the code and test of this item; this REPORT and DELTA
  were added after it, as docs only.
- `recorded 349 units for tree e9005138bf; ... 0 failed`, `exit=0, 6399s`.
- These units passed: tests/test_safety_framework.py (exit 0, 626.5 s), tests/test_english_statement_blocks.py (exit 0,
  984.3 s), tests/test_pinned_sources.py and tests/test_fsf_repair_f8_disclosure_1119.py.
- No test listed in main-known-red.txt failed, because none failed at all.

After the run, main moved: fsf-repair-f5-lowrisk-1119 merged and changes the same generated files. The branch was
rebased onto 9b72137abf:
- The three conflicted hash-only files (coverage.json, route-cases.jsonl, lexicon-report.json) were taken from main and
  regenerated with the commands of section 4. results.json is unchanged.
- The vocabulary merged cleanly, and environment.d1.json equals vocabulary.py's output.
- After the rebase, these 9 tests pass (/tmp/f8-post-rebase.log, "9 passed in 694.24s"):
  - the new test file;
  - test_safety_framework.py's test_environment_file_is_generated, test_the_low_risk_legend_quotes_the_glossary_sentence_whole,
    test_build_check_writes_nothing_beside_the_source, test_rerun_equals_committed_results and
    test_the_open_predicates_are_the_environment_legend_s_open_terms;
  - test_english_statement_blocks.py::test_the_route_fixtures_are_recorded;
  - test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon.

The chain's gate runs on the final HEAD.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A. No relayed answer or schema changed.
2. Deliverables built, no rule broken: PASS. Deliverables 1 and 2 are in section 1. Generated files come only from
   their generators (section 4). The test is a new file. route-cases.jsonl changed only by its generator.
3. Tests can fail: PASS. Seeds s1-s5 (section 5). The test fails on 7cbec4b340b8 and on main (section 2).
4. Python, Lean and Rust agree; valid inputs pass: PASS. The selected run is 0 failed (section 7), including the
   use case's Lean-backed tests/test_safety_framework.py.
5. R8 binding: N.A. No binding changed.
6. Gate evidence matches the final HEAD: PASS. The selected run covers c5781618, and the rebase onto 9b72137abf is
   covered by the 9 tests in section 7. The chain runs the gate on the final HEAD.
7. No unsigned item: PASS. DELTA.md has no rows; no SIGNED and no reserved cell.
8. Every user-visible change in DELTA: PASS. VE behaviour is unchanged; the legend text is a use-case change
   (DELTA.md, as fsf-r1 and fsf-repair-f5).
9. Test selection finds the tests: PASS. /tmp/f8-plan.log selects the new test and tests/test_safety_framework.py.
   Seeds s1-s5 break the selected new test.
10. Lean statements: N.A. No Lean changed.
11. Budgets and limits fail closed: N.A. No evaluator, runner or limit changed. The prompt-size limit is the counter's
    check (section 3).
12. CPU or memory: N.A. Three longer legend strings, no code path.
13. Removed or renamed tests: N.A. None.
14. Both directions, cited evidence, spec re-read: PASS.
    - Directions: the test passes on this branch and fails on the base legends (section 2).
    - Every claim cites a command or log.
    - Spec re-read: "S:17 passage … with its bullets" against converge-AB.md:55-61 and compare-report.md:260 (the
      three bullets included, ending at "reduce the risk.").
    - Spec re-read: "the 5.1 sentence 'The process will involve (i) … (ii) an assessment of our adherence to the
      Framework.'" against converge-AB.md:58 (one sentence, whole).
    - Spec re-read: carriers against converge-AB.md section 0 and `seq_unit_legends` in uc-audit.py.reads-1119 lines
      1202-1222.
15. Four classes: PASS.
    - Overclaim: "unchanged" (results.json) is from `git status` after run.py. "no product code" is from the file
      list in section 4. The max prompt size is marked UNVERIFIED.
    - No silent cut: none.
    - New checks can fail: s1-s5.
    - Limits: N.A.

## Notes for the DRI

- The legend rule of reviews/dri-decisions-20261114-uc-split-precedent.md item 4 says a legend carries what a
  predicate means and never its condition. S:17 opens with a qualifier ("Where appropriate, and subject to adequate
  confidentiality …"), but it qualifies what the shared information may include, not when the duty applies. The row
  orders this text into this legend verbatim, and it is carried as a quotation after the legend's own meaning.
- docs/codemap is stale on main (advisory on branches; see section 4). That is not this item's concern.
- The sibling fsf-repair-f5-lowrisk-1119 changes the same generated files (environment.d1.json, coverage.json,
  route-cases.jsonl, lexicon-report.json) at one-line hash fields. Whichever merges second rebases and regenerates
  them with the commands of section 4.
