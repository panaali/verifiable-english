# srccov-rl-safety-framework-1121: REPORT

DRI signature needed: none. DELTA.md has no row and reserves no signature. Trust is +0: no Lean, Rust, `ve/` or
`tools/` file changed, and `tools/trust_mutants.py --plan` plans 0 definitions and 0 mutants.

- **Status:** both in-scope units are KEPT. S0083 and S0085 (row srccov-safety-framework-s10-36-1119) are each carried by a
  new rule line in `usecases/safety-framework/rules.d1.ve`, read always, in the document's own profile (soft-norms@0).
  Each rule's predicate has a legend that quotes the source word for word. The spans.json records route each unit to
  its rule, and the units move from UNFORMALISED to CHECKED.
- **Answers:** no keyed answer or item verdict moves (section 3).
- **Merges at:** the branch is rebased onto VE main `7bb317174b`. The merge commit is the merge train's, made after this
  report. Later FSF reads re-pin to it (FREEZE note, section 3).
- **Open items:** none. No FOLLOW-UP.

## 0. Verify table

Inputs I read: manage-agents `reviews/source-coverage-1119/` METHOD.md (with its amendments, in particular 4, 13, 14 and
15c), safety-framework.md, rows-safety-framework.tsv, part-safety-framework-s10.tsv and units-safety-framework.tsv. I
also read the architect page row 'none: translation omission'. From VE I read `usecases/safety-framework/` rules.d1.ve,
facts.d1.ve, vocabulary.py, translation.py, build_document.py, run.py and spans.json (only the fields id, span, kind,
status, reason and rule), and the pinned `fsf-3.1.txt` at the two byte spans. I opened no readings/, answers/, reports/,
counted-read, sealed or diagnostic file, and not answer-key.json.

| unit id | row id | KEPT / DROPPED | reason |
|---|---|---|---|
| S0083 | srccov-safety-framework-s10-36-1119 | KEPT | The text is in the pinned source at bytes 15691-15783 ("We will use various processes to evaluate the effectiveness and limitations of mitigations:"); its heading "1.3.4 Residual Risk Assessment" is the meta record `s134-heading`. At main nothing carries it. The record is `spans.json:857-865` `s134-various`, UNFORMALISED, reason `unspecified_process`, from `build_document.py:293`. No legend, rule or fact at main holds "various processes" (`git show main:usecases/safety-framework/<f> \| grep -c` gives 0 for vocabulary.py, rules.d1.ve, facts.d1.ve, environment.d1.json and translation.py). A plain soft-norms obligation carries it. It needs no definition, no deadline or cadence, and no attributed content. |
| S0085 | srccov-safety-framework-s10-36-1119 | KEPT | The text is in the pinned source at bytes 16018-16220 ("● Deployment mitigations : we will use a combination of threat modeling, empirical testing, and other sources of information to assess the effectiveness and limitations of our deployment mitigations."). At main nothing carries it. The record is `spans.json:894-902` `s134-deployment`, UNFORMALISED, reason `unspecified_process`, from `build_document.py:298`. The same grep finds "empirical testing" nowhere at main. A plain soft-norms obligation carries it, as for S0083. |

The map tags both units with known-gap `unspecified_process`, which is amendment 13. That reason names an
unspecified process, not a missing language feature. The commitment itself, "we will use ... to evaluate/assess", is a
plain obligation. Under the N1 narrowing in `translation.py:15-17`, a "will" sentence about the developer's own
process is a commitment. The unnamed means ("various processes"; "threat modeling, empirical testing, and other
sources of information") go in the act's legend. f6 and f6-tcl at main carry "as needed" and their means the same way
(`rules.d1.ve` f6/f6-tcl headers).

## 1. Units carried

| unit | rule block (rules.d1.ve) | rule line | predicate (vocabulary.py) | legend quote (source, verbatim) |
|---|---|---|---|---|
| S0083 | `f7-eval` (:25-26), `always` | Rule 1. Every proposal must have its mitigations evaluated. | `mitigations_evaluated` (:431-435) | "We will use various processes to evaluate the effectiveness and limitations of mitigations:" |
| S0085 | `f7-eval-dm` (:27-28), `always` | Rule 1. Every proposal must have its deployment mitigations assessed. | `deployment_mitigations_evaluated` (:436-441) | "Deployment mitigations : we will use a combination of threat modeling, empirical testing, and other sources of information to assess the effectiveness and limitations of our deployment mitigations." |

Choices I made inside the task's scope, each the conservative one:

- **No condition was added.** Neither sentence states one, so neither rule has a guard. I did not borrow S0086's "Models
  reaching TCLs or CCLs", which would be my reading, not the source's.
- **Short act phrases.** The norms@0 act check refuses the words "and" and "for", and any act over 80 characters
  (`lean/VE/Acts/LexicalBase.lean:7-9`, `lean/VE/Norms/Wire.lean:30-36`). So the act phrases are "have its
  mitigations evaluated" and "have its deployment mitigations assessed". "The effectiveness and limitations" and the
  means are in the legend: that is the source quote, shown with the block (`tests/omission_rule.py` `used_predicates`
  and `carrier`).
- **The F7 feature.** Both blocks are headed F7 (1.3.4), which is already in `WILL_FEATURES` (`translation.py:72`). No
  new reading set and no new profile.
- **Each legend has one quote, outside any parenthesis.** The counter cuts parenthesised citations, and `legend_raw`
  reads the raw lines, so I wrote no variable.

## 2. Derived files (each from its own writer, never by hand)

| file | writer | change |
|---|---|---|
| usecases/safety-framework/environment.d1.json | `python usecases/safety-framework/vocabulary.py` | 2 predicates added |
| usecases/safety-framework/results.json | `python usecases/safety-framework/run.py` (234.6 s; "agreement with the answer key: 257/262") | see section 3 |
| usecases/safety-framework/spans.json, coverage.json | `python usecases/safety-framework/build_document.py` | s134-various, s134-deployment: UNFORMALISED → CHECKED (norm, rule f7-eval / f7-eval-dm); CHECKED bytes 2851 → 3145 (master 3959 → 4253), UNFORMALISED 6684 → 6390; `unspecified_process` count 2 → 0 |
| conformance/english-lean/lexicon-report.json | `python -m conformance.english_lean_lexicon` | `lexicon_id` of the FSF environment |
| tests/data/route-cases.jsonl | `docs/en-e3-norm/en-2b/route_fixtures.py --write` | the `stale` fixture's environment |
| conformance/english-lean/corpus-seal.json | `python -m conformance.english_lean_seal` (`--check` exits 0 afterwards) | sha256 of environment.d1.json and of tests/test_english_statement_blocks.py; seal_id |
| tests/data/norm-blocks/fsf.jsonl | `capture_blocks.capture("safety-framework", "translation")`, numbered rule blocks only, as d255cbd9f4 (f6-tcl) did | 47 rows; f7-eval and f7-eval-dm added; no other row changed except its `commit` (a script compared the rows without the `commit` key: "added ['f7-eval', 'f7-eval-dm'] removed [] changed []") |

`build_document.py --check` exits 0 on the final tree. `regen_generated.py --check` reported these stale before I
regenerated them: english-lexicon-report and recorded-route-cases. It also reported route-cases and checker-pins.
Those two fail only because this worktree has no Rust release binary ("the Rust release binary is missing or not
pinned"). That is environmental, not this change.

Not regenerated, by design (the srccov-safety-framework-1119 precedent): `tests/data/fidmech/wording-golden.json` and
`wording-inputs/`/`fp1-inputs/` pin frozen copies of the inputs, not the live files. Their generator is a manage-agents
tool, not a repo regen tool. `tools/fidmech/manifests.py` pins no FSF file (`grep safety-framework` finds nothing).

Two count pins in tests follow the change. Each one failed in the selected run and passes after the fix:
- `tests/test_safety_framework.py:454`: CHECKED bytes 3959/2851 → 4253/3145.
- `tests/test_english_statement_blocks.py`: fsf 45 → 47; 121 → 123 pinned; 122 → 124 with f21; 105 → 107 strict.

## 3. Answers touched

I computed statuses only with the document's own entry points (`run.py`, `build_document.py`).

- **Keyed answers and items:** none change. `results.json`'s `comparison` is equal to main's. A structural diff
  (main against HEAD, every key) lists only these:
  - `cost` counts: documents 87 → 89, prover calls 1732 → 1918, rule candidates 45 → 47;
  - `document_conflicts/mitigations_evaluated` and `.../deployment_mitigations_evaluated` are added, both CONFLICT-FREE;
  - `items/N3` counts 47 rules and adds witnesses f7-eval and f7-eval-dm (A-L0-DEV), with verdict NONE and
    without_witness [] as before;
  - `lint/rules_per_source/F7` adds the two rules.

  The run prints the same 5 disagreements as main: K2-L1/PROXIMITY, K2-L5/PROXIMITY and G3 are recorded in PLAN 12
  item 27; C3 and C-doc are RS9 = same, excluded. No CHECKED answer changed status or verdict, so no unit stops.
- **Span records whose status changes:**
  - `s134-various` goes UNFORMALISED → CHECKED, justified by "We will use various processes to evaluate the
    effectiveness and limitations of mitigations:".
  - `s134-deployment` goes UNFORMALISED → CHECKED, justified by "Deployment mitigations : we will use a combination
    of threat modeling, empirical testing, and other sources of information to assess the effectiveness and
    limitations of our deployment mitigations."
- **FREEZE:** the item merges after VE main `7bb317174b` (rebase base). The answers it touches are the two span
  records above and results.json's N3 witnesses and two conflict rows. A read pinned before the merge commit does not
  see rules f7-eval and f7-eval-dm. The Monday 2026-11-23 freeze takes them only if the merge lands before the commit
  the orchestrator names.

## 4. Condition test and seeded bugs

`tests/test_srccov_rl_safety_framework_1121.py` is new and has 8 tests, 4 per kept unit:
- `test_the_rule_line_stands_in_the_carrier`: the block is in rules.d1.ve, headed `always | F7, 1.3.4`, with its one
  rule line.
- `test_the_span_record_routes_to_the_rule`: the record covers the unit's bytes and has `rule` = the block. It is
  CHECKED, kind norm, with no reason and no open terms. S0083's heading bytes are the `s134-heading` meta record.
- `test_the_legend_quotes_the_pinned_source_sentence`: the sentence is read from the pinned text at its UTF-8 span
  (`tests/pinned_source.py`) and normalised with `safetyfw_accounting.norm`. It must equal a quoted passage of the
  legend in environment.d1.json.
- `test_the_counter_shows_the_legend_with_the_block`: `omission_rule.used_predicates` of the block is exactly the
  predicate; it is not in `OPEN_PREDICATES` and is an obligation; every content word of the quote is in the counter's
  `legend_raw` read of vocabulary.py.

Results:
- **On main's files:** with `git checkout main --` rules.d1.ve, spans.json, environment.d1.json and vocabulary.py, the
  run gives "8 failed in 0.29s" (/tmp/sf-t0.log). The files were then restored.
- **After the change:** "8 passed".

Seeded bugs. Each was planted, the test was run, and then it was restored, after which "8 passed". The only product
language changed is Python (use-case code), plus the .ve translation:

| # | file | bug | failing test |
|---|---|---|---|
| 1 | usecases/safety-framework/rules.d1.ve | delete f7-eval's rule line | `test_the_rule_line_stands_in_the_carrier[S0083]`, `test_the_counter_shows_the_legend_with_the_block[S0083]` (2 failed, 6 passed) |
| 2 | usecases/safety-framework/build_document.py:298 | route `s134-deployment` to `rule("f7-eval")`, then run build_document.py | `test_the_span_record_routes_to_the_rule[S0085]` (1 failed, 7 passed) |
| 3 | usecases/safety-framework/vocabulary.py:440 | the quote's "empirical testing" → "empirical tests", then run vocabulary.py | `test_the_legend_quotes_the_pinned_source_sentence[S0085]` (1 failed, 7 passed) |

No Lean or Rust file changed, so no seeded bug is owed there. Trust mutants: `light-lane.py check` printed "NOT 284
changed lines outside generated files > 150". `uv run python tools/trust_mutants.py --plan` printed `{"definitions":
0, "mutants": 0, "to_run": 0, "not_run": 0}`, so there is nothing to sweep.

## 5. Tests run

- Selected run on 1a92ffa549, before the rebase (`mac-pytest.sh --select`, ran on ve-cloud-2, exit 1). It had 2
  failures, both count pins this change moves:
  - `tests/test_english_statement_blocks.py::test_every_pinned_block_has_its_python_node[fsf]`;
  - `tests/test_safety_framework.py::test_a_unit_whose_rule_or_premise_uses_an_open_predicate_is_open_with_its_term`.

  Every other selected file passed (log /tmp/sf-sel.log).
- After the fix, run locally: those two ids, `test_lean_reads_each_pinned_block_as_python` and
  `test_each_pinned_block_through_the_mode` gave "5 passed in 1071.93s".
- First selected run on the rebased HEAD 53dca160b2 (fast stage, exit 1): one failure,
  `tests/test_english_statement_shadow.py::test_the_saved_delta_report_records_every_disagreement_with_its_class`.
  The saved W1 delta evidence named 121 pinned blocks, and the recapture made it 123. Fixed as 3f1974bb8c did:
  `docs/en-e3-norm/en-2/w1_delta.py --workers 8` at 53dca160b2 on a clean tree (pytest "4729 passed"). All 123
  pinned blocks agree. A script compared the 137 non-agree rows by corpus, class and both answers, and they are the
  same records as before. The en-2c REPORT's table and a rerun paragraph follow the run (`check_report` reads them).
  The shadow file's five saved-evidence tests: "5 passed".
- Final selected run: section 7.
- Commits named by saved evidence are pre-rebase. `tests/data/norm-blocks/fsf.jsonl` names 2d09151f21, which is
  b7502d1486 on the branch. The W1 delta was run at 53dca160b2, which is 76d67d09fd on the branch. For both pairs,
  `git diff --stat <old> <new> -- usecases/safety-framework tests/data/norm-blocks` is empty, so the files the
  evidence read are identical.

SIZE: 17 product (use-case translation: vocabulary.py 11, rules.d1.ve 4, build_document.py 2), 139 tests (131 new
file, 8 edited pins), 0 other hand-written lines (the rest is regenerated or captured data, plus this report and
DELTA.md).

Files (`git diff --numstat main...HEAD`): conformance/english-lean/corpus-seal.json, lexicon-report.json;
tests/data/norm-blocks/fsf.jsonl, tests/data/route-cases.jsonl; tests/test_english_statement_blocks.py,
tests/test_safety_framework.py, tests/test_srccov_rl_safety_framework_1121.py; usecases/safety-framework/
build_document.py, coverage.json, environment.d1.json, results.json, rules.d1.ve, spans.json, vocabulary.py; this
directory; docs/en-e3-norm/en-2/DELTA.md, delta.json (w1_delta.py) and docs/en-e3-norm/en-2c/REPORT.md. These are
outside the task's path list: tests/data/norm-blocks/fsf.jsonl, tests/data/route-cases.jsonl, the W1 delta evidence
and its en-2c REPORT, and the two count pins in tests/test_english_statement_blocks.py and tests/test_safety_framework.py.
Each one is regenerated, or is a pin or saved-evidence citation that the change moves. The f6-tcl precedent
(d255cbd9f4, 3f1974bb8c, a26d347f57) touched the same files.

## 6. Notes for the DRI

- The map's 'none: translation omission' held for both units. Their records' reason, `unspecified_process`, names an
  unnamed means, not a missing feature.
- The act-phrase limits (no "and"/"for", 80 characters) push "the effectiveness and limitations" into the legend.
  The rule line is shorter than the sentence, and the legend carries the rest.
- Pre-existing, not touched: `tests/test_ownership_floor.py::test_the_safety_framework_adapter_records_plan_12_item_27`
  is in main-known-red.txt (order-dependent).

## 7. Final selected run

(filled in below after the run on the final HEAD)

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relay, schema or Lean answer changed.
2. Deliverables built: PASS. 0 is the verify table (section 0); 1 is the rules and spans (section 1); 2 is the
   regenerated files (section 2); 3 is the answers (section 3); 4 is `tests/test_srccov_rl_safety_framework_1121.py`
   plus the seeded bugs (section 4). The diff adds no Python copy of a Lean decision and no report test.
3. Tests can fail: PASS. Seeded bugs 1-3 (section 4), and 8 failed on main's files.
4. Py/Lean/Rust agree: PASS for the pinned blocks. `test_lean_reads_each_pinned_block_as_python` and
   `test_each_pinned_block_through_the_mode` passed on the 47 FSF blocks: Lean's node equals Python's for f7-eval and
   f7-eval-dm.
5. R8 binding: N.A. No relayed field was added.
6. Gate evidence matches the final HEAD: PASS. The branch is rebased onto main 7bb317174b and the shared files are
   regenerated after it (corpus seal `--check` exits 0). The chain runs the full gate on the final HEAD.
7. No unsigned item: PASS. DELTA.md has no row; trust +0 (`trust_mutants.py --plan`: 0 definitions).
8. Every user-visible change in DELTA: PASS. The results.json structural diff (section 3) shows no verdict, diagnostic
   or availability change. Only use-case records changed, and they are described in DELTA.md.
9. Test selection: PASS. The selected run picked `tests/test_safety_framework.py` and
   `tests/test_english_statement_blocks.py`, the two files the change broke (section 5).
10. Lean statements: N.A. No Lean changed.
11. Budgets and deadlines: N.A. No budget path changed, and the new test has no sleep or timeout.
12. CPU and memory: N.A. No engine change. results.json `cost`: prover calls 1732 → 1918 for the two added rules.
13. Test-removed trailers: N.A. No test was removed or renamed (the new file adds 8; the edits only change pins).
14. Both directions, cited evidence, spec re-read: PASS.
    - Both directions: the test fails on main's files and passes on HEAD.
    - Every count in this report names its command.
    - Spec re-read: the S0083 and S0085 quotes against the pinned text at bytes 15691-15783 and 16018-16220
      (`test_the_legend_quotes_the_pinned_source_sentence`). The 'none: translation omission' class against the
      architect page row and METHOD amendment 14. The F7 "will" commitment against `translation.py:15-17`.
15. Overclaim, silent cut, checks can fail, limits: PASS / N.A.
    - Overclaim: each "no"/"none" above names its diff or test.
    - Silent cut: no deliverable was cut.
    - Checks can fail: seeded bugs 1-3.
    - Limits: N.A., no limit changed.
