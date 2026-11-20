# fsf-repair-f7-govadequacy-1119 REPORT (row F7: GOV adequacy criterion, R-family risk acceptance, "no T/CCL")

No DRI signature is reserved: DELTA.md has no rows (no user-visible change of VE).

**Merge commit.** The branch commits are:
- b540787792: the legends and the regenerated files;
- c5fba4282d: the condition test;
- 4b454ca49a: the docs;
- 1530594a48: a merge of main at 0ce720e46b.

That merge brought in fsf-repair-f5-lowrisk-1119's `low_risk` legend. vocabulary.py merged cleanly. The generated files
were taken from main and regenerated with their generators: results.json is still 257/262 against the key, and its diff
against main is certificate hashes only. After the merge, the new tests plus tests/test_safety_framework.py,
tests/test_english_lean_lexicon.py and the route-fixture test ran on ve-mac-1 through mac-pytest.sh at HEAD 1530594a:
"108 passed", exit 0. `trust_map.py --check` against 0ce720e46b7f gives "trusted +0, PASS".

**Pre-review round 2 (gate at ed5e3852 not usable).** No test failed in the chain's selected run of ed5e3852. The Mac
slot timed out and the run fell back to the VM. There it passed 366 of 422 units, all exit 0, and was stopped by its
timeout (exit 124, 11,237 s). 55 test files never ran.
- Then: `da126c5a0d` merges main at f03cafb9d2 (fsf-repair-f9, rsp-repair-r1, the defs-repair rows).
  - vocabulary.py and environment.d1.json merged cleanly.
  - The three conflicts were all in generated files: lexicon-report.json, route-cases.jsonl and coverage.json. Each was
    taken from main and regenerated with the generators in section 4. Each differs from main by one hash line.
  - results.json: 257/262 against the key, the same 5 DISAGREE rows as main; its diff from main is 2 certificate hashes.
  - `regen_generated.py --check` exit 0. `trust_map.py --check` against f03cafb9d2: "trusted +0, PASS".
- At HEAD da126c5a, mac-pytest.sh on ve-mac-1 ran these together: "2062 passed", exit 0.
  - the 55 test files the timed-out run never reached;
  - the new test file, tests/test_safety_framework.py and tests/test_english_lean_lexicon.py;
  - the route-fixture tests: test_route_row_schemas, test_pk1_route_case_differential and
    test_english_statement_blocks.
- c5check.py rerun at f03cafb9d2..HEAD gives the same result as before: each sentence is in the counted carrier,
  and the units' growth sums to 6,629 bytes (`c5check-f03cafb9d2.log`).

The VE commit this merges at is the merge train's merge commit of this branch (on main after f03cafb9d2). The R16 C2/C3 pins are per commit, so the counted read must re-pin at that commit. A merge
after the R16 diagnostic voids that diagnostic for the answers that read the touched units: f3, f8, f9-acc, f10-acc,
f11-acc, f12-p, f12-u, f13-p and f13-u (`c5check.log`). These include A-L*-EXT/GOV, C5 and the R family (R*/ACCEPTABLE).

## 1. What is delivered (row F7)

All text is copied from the pinned source `fsf-3.1.txt` (text_sha256 18e3375b…3946, `usecases/pinned_sources.json`;
read through `tests/pinned_source.py`). No reader, flag, diagnostic or analyst output was used. "S:n" is line n of that
text, which is PDF page n.

| # | Source passage (verbatim) | Location | Carrier |
|---|---|---|---|
| 1 | "In particular, we will deem deployment mitigations adequate if the evidence suggests that for the T/CCLs the model has reached, the increase in likelihood of harm from the proposed external deployment has been reduced to an acceptable level." | S:10, 2.1.2 step 2 "Pre-deployment review of residual risk assessment", the sentence after "... (including a safety case where a CCL has been reached)." | the GOV legend: `governance_found_acceptable_with_safety_case_where_ccl_reached` (OT3), vocabulary.py:133 |
| 2 | "We assess that the deployment mitigations have brought the residual risk of harm to an acceptable level, based on considerations such as the effectiveness of mitigations, the scope of the deployment, what capabilities and mitigations are available on other publicly available models (e.g. if other models are similarly capable and have few mitigations, then the marginal risk added by our external deployment is likely low), and the historical incidence and severity of related events." | S:7, 1.3.5 "To summarize", bullet 2 (misuse T/CCL), first ○ | `mitigates` legend (OT2, the "We assess" finding the f9-acc / f10-acc / f11-acc determinations use), vocabulary.py:103 |
| 3 | "We assess that the deployment mitigations have brought the residual risk of severe harm to an acceptable level, based on considerations such as the effectiveness of mitigations, and information pertaining to model propensities and the severity of related events." | S:7, 1.3.5 bullet 3 (ML R&D CCL), first ○; footnote mark 5 follows the period in the source | `mitigates` legend |
| 4 | "We assess that the deployment mitigations have brought the residual risk of significant harm to an acceptable level, based on considerations such as the effectiveness of mitigations, and information pertaining to model propensities and the severity of related events, or if we assess that the model is very unlikely to possess the propensities that would be required for material risk of significant harm through misalignment risk." | S:8, 1.3.5 bullet 4 (the TCL for ML R&D and misalignment risk), first ○ | `mitigates` legend |
| 5 | "A model for which inherent risk assessment indicates no T/CCL is reached will be deemed to pose an acceptable level of risk for further development and deployment, because it should not possess the capabilities required to substantially contribute to significant or severe risk scenarios." | S:7, 1.3.5 "To summarize:", bullet 1 (the full sentence) | `acceptable` legend: the determination the f8 / f9-acc / f10-acc / f11-acc rules conclude, vocabulary.py:224 |

- **"The R-family risk-acceptance sentences."** I took these as the three 1.3.5 "We assess that the deployment mitigations
  have brought the residual risk ..." sentences. compare-report.md row F7 quotes them, and a-report/b-report cite them for
  R3, R5, R7, R9a and R9b. Each sentence is quoted whole, to its own period.
- **Footnote mark.** Sentence 3 ends at its period. The footnote mark "5" that follows it in the source, and footnote 5's
  own text, are not part of the sentence and are not carried. The row's "with the table's footnote marks" is about table
  text, and none of these sentences is a table entry.
- **"As facts on the determination."** The carrier is the legend of the determination's predicates (`acceptable`, and
  `mitigates`, which carries the determination's "We assess" finding), not a new VE fact line. A fact line is a formal VE
  statement: adding one would change a decision path, and the row is LANGUAGE only. A legend of a predicate the block
  uses is a counted carrier under the CARRIER GUARD. This is the conservative choice; no ruling was asked.
- **Carrier fix in `acceptable`.** The counter reads a legend with `legend_raw`: the vocabulary.py lines of the entry, which
  stop at the next `"name":` line. In the `acceptable` entry, the description stood on its own `"description":` line, so
  that reader never saw it (r16-counter-build-1119.md decider point 2: "legend_raw also misses the description of {...}
  entries such as fsf `acceptable`"). The entry now opens its description on the key line, so its text follows that line,
  and the dict value is the same. Seeded bug S3 shows that the old layout fails the carrier test.
- **Fallback.** Not used. The carrier check passed (section 3).
- **Unchanged.** No predicate name, argument list, verbalisation, open term or decider changes. Each old legend text stays
  as a prefix of its new legend; only text is appended.

### Which kind call the reviewer should check
The row carries both calls, and no action turns on them. The reviewer should check the **GOV at L1+** call, which is
A's TEXT against B's UNCERTAIN-CRITERION:
- A holds that the A-L1..L7 GOV answers depend on S:10.
- B holds that the adequacy criterion may be a separate property of the governance decision.

What the VE shows the reviewer:
- GOV is asked with the OT3 finding absent (run.py:191, reference.py:70-71). The answer turns on whether that one
  stipulated finding is present.
- S:10 now sits in that finding's legend, as the criterion the determination applies to deployment mitigations. It is not
  a separate VE condition.

So a flag left on a GOV answer at L1+ after this row counts against the reader under B's call and against the text under
A's.

## 2. Condition test
New file `tests/test_fsf_repair_f7_govadequacy_1119.py`:
- **`test_each_f7_legend_quotes_its_source_sentence_byte_for_byte`** (the condition test). It finds each sentence in the
  pinned source, between its first and last words, exactly once. It then asserts that the sentence stands whole, in
  double quotes, after the quote normalisation (whitespace collapsed, curly quotes made straight), in two places:
  `vocabulary.environment()` and the committed `environment.d1.json`.
- **`test_each_f7_sentence_sits_in_the_lines_of_its_vocabulary_entry[...]`** (3 cases, no source needed). It checks the
  carrier guard: each quote lies in one string of the lines that a line reader takes for the predicate's vocabulary.py
  entry.
- **Fails before.** With vocabulary.py and environment.d1.json taken from main, and again from 7cbec4b340b8, all 4 tests
  fail. With HEAD's files, all 4 pass. Logs: /tmp/f7-old-main.log and /tmp/f7-old-7cbec4b340b8.log ("4 failed").
  Command: `uv run pytest -q tests/test_fsf_repair_f7_govadequacy_1119.py`, "4 passed".
- **Selected.** `tools/select_tests.py --base d8758ce968` selects the file (its plan lists
  tests/test_fsf_repair_f7_govadequacy_1119.py). The selected run ran it first: "exit 0 in 1.7 s".

## 3. Carrier guard and prompt size (R16 C5)
- **The counter.** reads-1119 is installed: tools-local/uc-audit.py.reads-1119, sha256 d618d963…01dc, as in
  r16-counter-build-1119.md.
- **Why the full dry-run did not run.** `omission-seq-read.py.reads-1119 --dry-run-all` needs a uc-audit run dir at this
  commit and a pins entry for it. The pins file has entries only for da0822ae80 and f2de63a404, and "at any new commit the
  plan fails closed until an entry for that commit is appended" (decider point 4). So the full dry-run is the decider's
  step at the counted read.
- **What ran instead.** `c5check.py` (saved with its output, `c5check.log`) loads the installed counter and calls the
  counter's own C5 functions at the base and at HEAD:
  - `seq_unit_legends`, the prompt's legend part of each unit;
  - `legend_raw` + `_omit_legend_segments`, the counted legend carrier, its meaning text with citations cut.
- **Result** (`python3 -I c5check.py <counter> <worktree> d8758ce968 HEAD <fsf-3.1.txt>`):
  - Each of the 5 sentences is rendered in every unit whose block uses its predicate:
    - GOV: 5/5 (f3, f12-p, f12-u, f13-p, f13-u);
    - `mitigates`: 3/3 (f9-acc, f10-acc, f11-acc);
    - `acceptable`: 4/4 (f8, f9-acc, f10-acc, f11-acc).
  - Each sentence is in the counted carrier at HEAD ("counted carrier head=True") and was not at the base ("base=False").
- **Prompt size.** The legend parts of all units together grow by 6,629 bytes:
  - per unit: f9-acc, f10-acc and f11-acc +1,646 each; f8 +331; f3, f12-p, f12-u, f13-p and f13-u +272 each.
  - No prompt can grow by more than this sum. Against the counter build's FSF maximum of 113,909 bytes (D3, at
    da0822ae80), the maximum with this row's appends is at most 120,538 bytes, under the 131,000 limit.
  - This bound is for this row alone. The sibling rows add their own appends, so the decider re-checks with all appends at
    the counted read.

## 4. Regenerated files (generators only)
- `environment.d1.json`: from `python usecases/safety-framework/vocabulary.py`.
- `coverage.json`: from `build_document.py --source <a /tmp copy of the pinned text>`; only the document hash changes.
- `results.json`: from `run.py`. Only two `certificate_sha256` values change; every answer is the same.
  - `git diff main -- usecases/safety-framework/results.json` shows 2 changed lines, both hashes.
  - run.py prints "agreement with the answer key: 257/262". The 5 DISAGREE rows (K2-L1/PROXIMITY, K2-L5/PROXIMITY, C3,
    C-doc, G3) are on main too: their answers in results.json did not change.
- `tests/data/route-cases.jsonl`: from `docs/en-e3-norm/en-2b/route_fixtures.py --write`; the R-stale case's
  environment hash.
- `conformance/english-lean/lexicon-report.json`: from `conformance/english_lean_lexicon.py`; its environment hash.
- `tools/regen_generated.py --check` fails on route-cases and checker-pins, for one reason only: this worktree has no
  pinned Rust release binary ("checker-pins: the Rust release binary is missing or not pinned"). The route-cases
  traceback ends in `ve/search.py` `rust`. Neither failure comes from this item's files.

## 5. Tests
- **The new test file:** 4 passed (above).
- **The selected run:** `zsh mac-pytest.sh --select -- --base d8758ce968 --run`, log /tmp/f7-select.log, exit 0.
  - No Mac slot was free, so it ran on the VM.
  - It recorded 75 units for tree dd00914249, with "0 failed". test_safety_framework.py and test_safetyfw_usecases.py
    were among them.
- **Not run by me:** the full gate, as the task says. The chain runs it on the final HEAD.
- **Pre-existing failures:** none seen in the selected units.

## 6. Seeded bugs
Recorded in `mutants.json`. Each bug was planted, run with
`uv run pytest -q tests/test_fsf_repair_f7_govadequacy_1119.py`, then restored. Python is the only language of changed
product code.

| id | file | change | failing test |
|---|---|---|---|
| S1 | usecases/safety-framework/vocabulary.py | GOV legend: "proposed external deployment" → "proposed deployment" | test_each_f7_legend_quotes_its_source_sentence_byte_for_byte; test_each_f7_sentence_sits_in_the_lines_of_its_vocabulary_entry[governance_found_…] |
| S2 | usecases/safety-framework/vocabulary.py | `mitigates`: the severe-harm sentence loses "information pertaining to model propensities and" | the condition test; …[mitigates] |
| S3 | usecases/safety-framework/vocabulary.py | `acceptable`: the description goes back to its own `"description":` line (the main layout) | …[acceptable] |
| S4 | usecases/safety-framework/environment.d1.json | the committed environment drifts from vocabulary.py ("will be deemed" → "is deemed") | the condition test |

## 7. Trust and lane
- `uv run python tools/trust_map.py --check`: "against d8758ce96837: K +0, S +0, D +0, G +0, tied +0, unclassified +0,
  trusted +0 … PASS". There is no allowance and no FOLLOW-UPS row.
- **Light lane:** `light-lane.py check` prints "NOT 158 changed lines outside generated files > 150".
- **Trust mutants:** `uv run python tools/trust_mutants.py --plan` prints `"definitions": 0, "mutants": 0, "to_run": 0`.
  A sweep would have nothing to run, so none was run.

SIZE: 33 product (vocabulary.py, 28 added / 5 removed), 109 tests, 292 other hand-written lines (REPORT.md 187,
DELTA.md 10, mutants.json 52, c5check.py 43; plus the saved output c5check.log, 16).

The codemap (docs/codemap/) is not regenerated in this branch. It is refreshed on every merge to main, and
`regen_generated.py --check --only codemap` gives only "WARN: codemap is stale (regenerated on merge)", exit 0. A
branch-side rewrite touched 11 codemap files of other items, so I reverted it to keep the train's rebases clean.

Expected pilot effect (an estimate; nothing is claimed before a pilot audit): the row's ADEQ cluster is "24 touched / 3
alone" (A-L0-EXT/GOV, C5, R1/ACCEPTABLE; converge-AB.md F7). The text this row adds can clear those 3 when the reader's
other verdicts stay fixed. B reads C5 as READER-SEPARATE.

## Notes for the DRI
- The counter's `legend_raw` misses a description that stands on its own `"description":` line in a `{...}` entry
  (decider point 2).
  - This row fixes that for `acceptable` only, because the row needs that entry.
  - The other `{...}` entries in this vocabulary (`proceed`) carry no text of this row.
- Spec re-read:
  - Row F7 ("release S:10 verbatim to the GOV legend ... plus as facts on the determination the R-family risk-acceptance
    sentences and the 'To summarize' sentence") against converge-AB.md:46-54 and compare-report.md:259.
  - The CARRIER GUARD against converge-AB.md:6-11.
  - The carrier rule against uc-audit.py.reads-1119 `omit_carrier_texts` / `legend_raw` / `_omit_legend_segments`:
    - a string that starts with a section citation is provenance, not a carrier;
    - a parenthesis holding a digit, "section", "appendix" or "table" (case-insensitive, so also "acceptable") is cut from
      the meaning.
  - No appended sentence is inside such a parenthesis or at the start of a string; c5check.log shows "counted carrier
    head=True" for all 5.

## Self-review against BUILDER-CHECKLIST
1. Lean answers typed and contained: N.A., no relay or Lean change.
2. Deliverables built, no rule broken: PASS. Section 1 table covers both deliverables. The condition test is in the new
   file.
3. Tests can fail: PASS. Seeded bugs S1-S4 (mutants.json), and the test fails on main and on 7cbec4b340b8 (section 2).
4. Python, Lean and Rust agree: N.A., no product path changed. results.json answers are unchanged (section 4).
5. R8 binding: N.A., no relay.
6. Gate evidence matches final HEAD: PASS, left to the chain's gate on the final HEAD. The selected run ran on this tree.
7. No unsigned item: PASS. DELTA.md has no rows; nothing is reserved.
8. User-visible changes in DELTA: PASS. DELTA.md says none, and the results.json diff is hashes only (section 4).
9. Test selection finds the tests: PASS. The select_tests plan lists tests/test_fsf_repair_f7_govadequacy_1119.py and
   tests/test_safety_framework.py. Seeded S1 fails a selected test.
10. Lean statements: N.A., no Lean change.
11. Budgets and limits: N.A., no evaluator or runner.
12. CPU/memory: N.A. The legend text grows by 6,629 bytes over all FSF units (c5check.log), and no code changed.
13. Test-removed trailer: N.A., no test removed.
14. Both directions, cited evidence, spec re-read: PASS.
    - Both directions: the tests pass on HEAD and fail on main and on 7cbec4b340b8, and S3 fails only the carrier test.
    - Claims cite their commands.
    - The spec re-read is under "Notes for the DRI".
15. Overclaim, silent cut, new checks fail, limits: PASS / N.A.
    - Overclaim: PASS. Universal words cite c5check.log, the results.json diff or the test runs.
    - Silent cut: PASS, none.
    - New checks can fail: PASS, S1-S4.
    - Limits: N.A.
