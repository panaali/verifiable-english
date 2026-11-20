# defs-carried-oos-measure-1119: REPORT (out-of-sample measure of tools/defs_carried.py, report only)

**Out-of-sample recall: 135 of 149 findings (90.6%, 95% Wilson 84.8-94.3%); 511 of 819 (rule, term) pairs (62.4%, 59.0-65.6%).** Here the case's source passage is given to the tool (`--known`), which is how the in-sample "60 of 61" was measured. **Unaided (the default run): 0 of 149 findings (0-2.5%)**: the tool does not inventory PF, FSF or RSP (coverage PARTIAL, the 9 repair terms only), so it never reaches an out-of-sample case on those documents.
**False-alarm rate: 50 of 120 judged flags (41.7%, 95% Wilson 33.2-50.6%)**, judged by a separate Opus 5.5 seat (`claude -p --model claude-opus-5-5`, 6 fresh sessions, each on the account its own pick-claude-account.sh call returned, all of the 5x account class). UNSURE: 0, so the rate is the same whether UNSURE counts as a false alarm or not. A supplementary pass by the same kind of seat also asked whether each flagged passage defines anything. Counting a flag as false when its passage is shown anyway **or** defines nothing gives 104 of 120 (86.7%, 79.4-91.6%) (section 3c).
**Measured at:** VE main `d5f402140f` (this branch's merge base) for both numbers. Recall was also measured at the audit rows' pin `e53db4e8fc`, with identical results. **Seed:** 20261120. **Matching key:** (document, rule, term).
**Changed:** no tool behaviour. New: `docs/infra/defs-carried-oos-measure-1119/` (this report, `measure.py`, `judge.sh`, `judge/`, `evidence/`, `mutants.json`); `tests/data/defs_carried/oos_cases.json`, `oos_flags.json`, `oos_audit/` (the three row files, verbatim); `tests/test_defs_carried_oos.py`; `tests/history-dependent.json` (regenerated). Edited: the Numbers line of `docs/infra/defs-carried-gate-stage1-1119/REPORT.md`, now marked IN-SAMPLE with a pointer here (deliverable 3; no other edit).
**Binding limits (ADV-2):** no row, count or sentence here takes the tool's CARRIED as evidence that a definition is carried. A tool CARRIED on an out-of-sample case is counted as a miss. A tool flag is a false alarm only when the judge says CARRIED. `tools/defs_carried.py` and `tests/test_definitions_carried.py` are unchanged. `tools/trust_map.py --check` on this branch: K +0, S +0, trusted +0. No DELTA row. No repair-row file touched (no `usecases/` file, `vocabulary.py`, `tests/test_safety_framework.py` or `tests/data/route-cases.jsonl`).

## 1. Out-of-sample recall (deliverable 1)

### a. The cases
- **Source:** the three audit row files written after the 61-case fixture, all at VE `e53db4e8fc`: `rows-openai-preparedness.tsv` (PF, 50 rows), `rows-safety-framework-x.tsv` (FSF, 46), `rows-anthropic-rsp-x.tsv` (RSP, 63). They are copied verbatim to `tests/data/defs_carried/oos_audit/`, and their sha256 values are in the fixture.
- **Which rows count:** all 159 rows. Each records a definition the reader is not shown in the file's own terms: NOT CARRIED 127, PARTIAL-FRAGMENT 18, PARTIAL-PARAPHRASE 7, PARTIAL-ELSEWHERE 5, PARTIAL-FORMALISED 2.
- **Build:** `python3 docs/infra/defs-carried-oos-measure-1119/measure.py fixture --pin e53db4e8fc --out tests/data/defs_carried/oos_cases.json`. It makes one case per (row, rule), resolved at the pin with the known-case builder's own functions (`tools/defs_carried_known.py`: `expand_rules`, `carrier_keys`, `choose_term`, `recut`).
  - **Term:** an identifier written in the row's `carrier_key` cell that the pin declares (for example `stage0.py harms["harm_of_automated_rd"]` gives `harm_of_automated_rd`; `(R5: plans_in_place, rows T1)` gives `plans_in_place`), then the builder's own `carrier_keys`. Choice: 514 cases use a carrier key the rule uses, 302 a carrier key the rule does not use, 2 a lexical match, 1 none.
  - **Rules:** the rows' rules column, split on commas or spaces. **Wildcards resolved: 0.** These rows have none, and every rule token is a rule id of the pin except `FACTS` (see the misses).
  - **Re-cuts: 28 quotes**, each listed in the fixture's `recut` (quote, passages, dropped words), all mechanical (`recut`: the maximal runs of 3 or more words that the pinned source holds, cut verbatim):
    - 13 split into 2 passages, 4 into 6, 2 into 5, 1 into 7, 1 into 3, and 5 cut to the source passage;
    - 2 not found: RSP x62 and x63 quote no source text, only a pointer ("the four middle-column cells, rows T1-T4, L6-L10 ...").
    - There is no other judgement.
- **In-sample exclusion:** a case is in-sample when its (document, rule, term) is a key of `tests/data/defs_carried/known_cases.json`. The whole fixture counts (389 cases: the 61 known findings plus P2 and D7). This is the wider exclusion, so nothing the tool was built against counts as out of sample. **Excluded: 74 pairs.**
  - **10 rows are wholly in-sample:** FSF x1, x16, x17, x19, x23, x24, x26, x39, x40, x45.
  - **7 rows are partly in-sample** (excluded pairs in brackets): x28 (9), x29 (9), x30 (9), x31 (7), x33 (5), x34 (5), x35 (9). Their in-sample pairs are F6's `recommends` cases.
  - All of them are FSF rows that the F1-F9 repairs overlap.
  - Every excluded case is listed in the fixture's `excluded_in_sample`.
- **Count: 819 out-of-sample cases from 149 rows (findings)**: PF 336 cases / 50 findings, FSF 343 / 36, RSP 140 / 63; 487 distinct (document, rule, term) keys.

### b. The run
- **Commands:**
  - `python3 tools/defs_carried.py --ref d5f402140f --known tests/data/defs_carried/oos_cases.json --doc openai-preparedness --doc safety-framework --doc anthropic-rsp --json ...`
  - the same with `--ref e53db4e8fc`
  - `measure.py recall`, which tabulates both runs.
- **Evidence:** `evidence/recall.json` (totals), `evidence/recall.cases.jsonl` (each case at both trees, with reach, verdict and reason), and `evidence/tool-oos-at-main.txt` / `tool-oos-at-rows-pin.txt` (the tool's own summaries).
- **Hit:** the tool reaches the pair (reach `parsed` or `unparsed-rule`) and its verdict is below CARRIED-ASSUMED. This is the in-sample T1 definition, with one tightening: a case with no passage (verdict None) is a miss here, although the tool's own `hit` flag passes it (Notes).
- A finding is detected when at least one of its pairs is.

| tree | findings detected | pairs hit | misses: term not in rule | rule missing (`FACTS`) | no passage | no VE term | tool CARRIED |
|---|---|---|---|---|---|---|---|
| main `d5f402140f` | **135 / 149** | **511 / 819** | 250 | 52 | 4 | 1 | 1 |
| rows' pin `e53db4e8fc` | 135 / 149 | 511 / 819 | 250 | 52 | 4 | 1 | 1 |

By document (main): PF 47/50 findings (176/336 pairs), FSF 29/36 (219/343), RSP 59/63 (116/140). Unaided default run at main (`python3 tools/defs_carried.py --ref d5f402140f`): the three documents print "marker grep not run: coverage PARTIAL (the 9 repair terms only)", so **0 of 149 findings (95% 0-2.5%), 0 of 819 pairs (0-0.47%)**. Evidence: `evidence/tool-all-docs-at-main.txt`.

What the misses are made of. These are diagnostics, not the recall definition. In 814 of the 819 pairs the passage verdict on the rule's own surface is below CARRIED (146 of 149 findings), with reach ignored. So 302 of the 308 missed pairs are **term-link misses**, not verbatim-check misses:
- **term not in rule (250 pairs).** The row's carrier key is the audit's proposed carrier, and the target rule does not use it. Mostly it is a predicate shown in the FACTS unit, which reaches every PF answer: `high`, `critical`, `in_category`, `reached`. On FSF it is `recommends` on `f9-sec`/`f10-sec`, `concerns` and `ml_rd_and_misalignment`. The audit pairs a rule with a definition when the rule relies on the defined phrase (for example `c2-misalignment-default` says "severe-harm risk"). The tool links a known case only through the named term.
- **rule missing (52 pairs, one per affected row).** The rows name the counter's `FACTS` unit (all fact lines plus their legends, shown with every answer). The tool's counter adapter splits `facts.d1.ve` into its blocks and has no `FACTS` rule.
- **no passage (4).** RSP x62 and x63 point at table cells and quote no text.
- **no VE term (1).** RSP x31, "coverage date", carried in `stage0.py`'s D3 check, names no declared identifier.
- **tool CARRIED (1).** RSP x44 (RSO) on `f18-rso`. The 4.1 sentence sits in `rso_maintained`'s citation-led string ("4.1 at {0}: \"We will maintain the position of RSO, ...\""), which the tool's counter surface includes and compares. The audit's method (METHOD-READDOCS amendment 2) treats such a provenance string as shown but never counted, so the audit records NOT CARRIED. Counted as a miss.

**The 14 missed findings, each with its reason:**

| finding | pairs | reason |
|---|---|---|
| defs-anthropic-rsp-x31 | 1 | no VE term: the coverage-date check in `stage0.py` (D2D3) has no declared identifier |
| defs-anthropic-rsp-x44 | 1 | tool CARRIED: the passage is in a citation-led provenance string of `rso_maintained` (counted by the tool's surface, not by the audit's method) |
| defs-anthropic-rsp-x62 | 2 | no passage: the row points at the table's middle-column cells, quotes no text |
| defs-anthropic-rsp-x63 | 2 | no passage: the row points at the right-column cells, quotes no text |
| defs-openai-preparedness-18, -21, -22 | 4, 7, 9 | carrier `reached` (FACTS): `FACTS` is not a tool rule; the listed rules do not use `reached` |
| defs-safety-framework-x28, x29, x30 | 3 each | carrier `recommends`: `FACTS` is not a tool rule; `f9-sec`/`f10-sec` do not use `recommends` (their F6 pairs on `levels-*` are in-sample) |
| defs-safety-framework-x31, x33, x34, x35 | 1 each | carrier `recommends` on `FACTS` only (the other pairs are in-sample F6 cases) |

Run time (MEASURED on this VM): 2.9 s wall per tree for the three documents (2.86 s at the pin, 2.94 s at main); fixture build 6.0 s.

## 2. Independent false-alarm rate (deliverable 2)

### a. The draw
- **Population:** every pair flag of the tool's default run over all the documents it covers, at main `d5f402140f`. A pair flag is any verdict other than CARRIED or CARRIED-ASSUMED. The run is `python3 tools/defs_carried.py --ref d5f402140f --json ...`; its summary is `evidence/tool-all-docs-at-main.txt`.
  - 501 flags in total. Minus the 287 whose (document, rule, term) is a known-case key, that leaves **214**: eligibility 156, bluedot-grant 40, claude-constitution-pilot 16, claude-constitution-excerpt 1, udhr-pilot 1.
  - The known-case evaluations themselves are the tool's input, not its findings, and are not in the population.
  - Document-level findings (VISIBILITY-UNESTABLISHED, UNPARSED) name no term and no passage, so they cannot be judged on this question and are not in the population.
  - PF, FSF and RSP have no auto flags (no inventory).
- **Draw:** `measure.py draw --n 120 --seed 20261120`, using `random.Random(20261120).sample` over the population in its listed order, uniform and without replacement. The seed (the date) was fixed before the draw, and this was the only draw.
  - Drawn: **120 flags**: eligibility 85, bluedot-grant 25, claude-constitution-pilot 9, claude-constitution-excerpt 1. Tool verdicts: NOT CARRIED 76, FRAGMENT 44.
  - Every drawn flag (id, doc, rule, term, verdict, source line, passage) is in `tests/data/defs_carried/oos_flags.json`.

### b. The judge
- **Seat:** a separate Claude Opus 5.5 seat that did not build the tool and is not this builder: 6 fresh `claude -p --model claude-opus-5-5` sessions, one per packet.
  - Each session ran on the account its own `pick-claude-account.sh` call returned. All 6 picks were 5x-class accounts; no account name is recorded.
  - No fallback model was used: each meta file lists only `claude-opus-5-5`.
  - The sessions ran with `--tools ""` (no tools) and `--safe-mode` (no CLAUDE.md, skills, hooks or plugins), from an empty temporary directory (`judge.sh`).
- **Input** (`measure.py packets`; the packets are `judge/<doc>-<n>.prompt.txt`):
  - the flag list (id, rule, term, source line), each flag's source passage, and each rule's carrier surface (the tool's reader-visible texts for that rule, with a text shared by several rules printed once);
  - the question: "is this term's definition (the source passage given for the flag) shown to the reader of the rule, in the rule's carrier surface? CARRIED / NOT CARRIED / UNSURE, one line of evidence".
  - **The tool's verdict was not given** (conservative choice: the judge is not anchored on it).
  - The judge's raw outputs are saved unedited in `judge/<packet>.raw.json`, `.reply.txt` and `.meta.json`.
- **Tally** (`measure.py tally`, `evidence/tally.json`): all 120 flags were judged, with one parseable line each. Verdicts were only counted, never edited.

### c. Result

| | count | rate | 95% Wilson |
|---|---|---|---|
| judge CARRIED (false alarm) | **50 / 120** | 41.7% | 33.2-50.6% |
| judge NOT CARRIED | 70 / 120 | 58.3% | |
| judge UNSURE | 0 | | |
| false alarms, UNSURE counted as false alarm | 50 / 120 | 41.7% | 33.2-50.6% |
| false alarms, UNSURE dropped | 50 / 120 | 41.7% | 33.2-50.6% |

- **By document:** eligibility 42/85, bluedot-grant 5/25, claude-constitution-pilot 2/9, claude-constitution-excerpt 1/1.
- **By tool verdict:** FRAGMENT 24/44, NOT CARRIED 26/76.
- **Clustering:** the flags are not independent. the 50 false alarms come from 10 distinct source passages, so the interval is narrower than the evidence warrants. Read the per-cause counts below.

**False-alarm causes** (`evidence/false-alarm-causes.json`; group 1 is computed, the others are grouped by passage shape and the judge's evidence line):

| # | cause | flags |
|---|---|---|
| 1 | **The citation strip erases the definition in executed code.** In eligibility `translation.py`, `DEFINITIONS["qualifying week"]` is `" ".join((...))`, a parenthesised tuple of strings that holds a digit ("21 to 27 September 2026"). `cite_strip`'s `_CITE_PAREN` deletes the whole tuple, so the normalised code surface reads `" ".join( )`. The passage is whole on the surface before the strip (MECHANICAL check), and the judge saw it. | 12 |
| 2 | **A longer sentence that uses the term in passing** (the explanatory note's restatement of regulation 2 at uksi-2025-969-made.txt:113 and :116). The judge found the term's meaning on the surface. | 18 |
| 3 | **A lead-in cut at the line end** ("“relevant benefit” means—", 3 tokens). The list that follows is in the R4 gloss. | 5 |
| 4 | **A pointer to a definition** ("See section 7A(6)(d) ..."). The definition it points to is in the gloss. | 4 |
| 5 | **An abbreviation or an inflection.** The carrier has the words without "(ESA)" or "(CSAM)", or has "generating" for "Generate". | 5 |
| 6 | **A paraphrase in the legend** (bluedot `matched_cost`: "count authoring, formalisation, proof production, compute and review for both arms"). The verbatim check needs the words whole. The stage-1 builder's hand check called this group TRUE (S7); this judge disagrees. | 5 |
| 7 | **Commentary that quotes a clause**, which the legend names (claude-constitution-excerpt source.md:43). | 1 |

**Supplementary definition pass** (not the task's question; why it was added: the main question presents each passage *as* the term's definition, so it cannot see the stage-1 hand check's main false-alarm kinds, mention, amendment or pointer):
- A fresh session of the same seat (`judge/definition/`, its own pick, 5x class, Opus 5.5 only) was asked whether each passage states what the matched phrase means, "as opposed to only using it, mentioning it, amending another text's definition of it, or pointing to a definition elsewhere".
- **Answers:** DEFINES 50, DOES NOT DEFINE 70, UNSURE 0.
- **Crossed with the main pass:**
  - NOT CARRIED / DOES NOT DEFINE: 54. This covers the 11 bluedot "unresolved" flags (a quoted label in a risk sentence) and the 43 eligibility "pensionable age" amendment and pointer lines.
  - CARRIED / DEFINES: 34.
  - CARRIED / DOES NOT DEFINE: 16.
  - NOT CARRIED / DEFINES: 16.
- **Broad false-alarm rate** (main CARRIED or DOES NOT DEFINE): **104/120, 86.7% (79.4-91.6%)**.
- **Superseded first version:** it asked about "the named term" and was answered against the VE identifier ("It defines 'qualifying week', not home_start_dated"). It is kept unedited in `judge/definition-v1-superseded/` and not counted.

**True flags and candidate repairs.** These are the 16 flags the judge called NOT CARRIED and the definition pass DEFINES. They are listed here only; nothing is repaired.
- **9 bluedot VEX flags** (source.md:8, :11, :53).
  - u007, u056 and u074 are already in the stage-1 report's new finding 1 (listed, not filed).
  - **u058 (`vex_result`) is new:** the VEX definition is not carried there either. Candidate repair: add u058 to that finding.
- **7 claude-constitution-pilot flags** (the Operators and Users entries, probe.md:95-96). These carry the passages of known rows defs-claude-constitution-pilot-3 and -4, on other (rule, term) keys. They are already known.

Run time (MEASURED): the tool over all 15 documents at main took 7.8 s; the 6 judge sessions took 81 s wall in total; the definition pass took 48 s, and its superseded first version 56 s.

## 3. Comparison with the stage-1 numbers
- **Recall.** In-sample, 60 of 61 findings were detected with the passage given. Out of sample, with the passage given, 135 of 149 were (90.6%). The out-of-sample pair rate (62.4%) is far below the in-sample one (363/389 = 93.3%).
  - Almost all of the gap is the term link: 302 of the 308 missed pairs are cases where the audit's carrier key is a FACTS-unit predicate the rule does not use, or the `FACTS` unit itself.
  - The verbatim verdict alone was below CARRIED on 814 of 819 pairs.
- **Unaided.** Without the passage the tool detects nothing on PF, FSF or RSP, which are the three documents it does not inventory.
- **False alarms.**
  - The stage-1 hand check, by the builder, found 10 of 24.
  - The independent judge, on the task's question, found 50 of 120.
  - The broad sense, adding passages that define nothing, gives 104 of 120.
  - The largest single cause (12 flags, group 1) and most of groups 2-4 come from one document, eligibility, whose 40 KB executed code is the carrier. That document is 85 of the 120 drawn flags.

## 4. Checks, tests and seeded bugs
- **Condition tests:**
  - `tests/test_defs_carried_oos.py::test_oos_fixture_and_flags_load_and_are_disjoint_from_the_known_cases` (new). Both files load, their counts match, and no case or flag has a known (document, rule, term) key.
  - Five more tests pin the script's counting rules: the Wilson interval, the recall hit rule, the seeded draw and its exclusions, and the reply parser and tally.
  - `tests/test_definitions_carried.py` is unchanged. The local plan (`uv run python tools/select_tests.py --base d5f402140f`, 45 test files) does not list it, because no changed file reaches it through the local coverage map. The selected run on the test runner (363 test files) did include it, and it passed (section 7). The full gate runs it too.
- **Selected run and explicit runs:** see section 7.
- **`tools/trust_map.py --check`:** PASS, K +0, S +0, trusted +0.
- **Trust mutants:** light-lane says NOT, because the committed evidence and data are 34,646 lines. `tools/trust_mutants.py --plan` gives 0 definitions and 0 mutants (no Lean changed), so there is nothing to sweep.
- **`tools/regen_generated.py --check`:** pass. The code-map warning is already present on main and is regenerated on merge.
- **Seeded bugs** (`mutants.json`; Python and data only, the only languages changed). Each was planted alone, the named test failed, and the file was restored with git checkout:
  1. `measure.py` `wilson()` drops the z²/4n² term: `test_wilson_interval` fails.
  2. `measure.py` `tabulate_recall()` counts the tool's own hit, so a case with no passage is a hit: `test_recall_counts_a_hit_only_when_reached_with_a_verdict_below_carried` fails.
  3. `measure.py` `flag_population()` keeps known keys: `test_draw_excludes_known_keys_and_passing_pairs_and_is_seeded` fails.
  4. `measure.py` `parse_judge()` keeps a repeated id's last line: `test_judge_replies_are_parsed_and_tallied_without_edits` fails.
  5. `measure.py` `tally()` counts UNSURE as a false alarm in the "not" rate: `test_judge_replies_are_parsed_and_tallied_without_edits` fails.
  6. `tests/data/defs_carried/oos_cases.json`: a case given a known safety-framework key: `test_oos_fixture_and_flags_load_and_are_disjoint_from_the_known_cases` fails.

## 5. Cost
- **Judge seat (MEASURED, `delegate-cw.py` over its 8 session transcripts):** 0.25M CW. This is 6 main-question sessions, the definition pass and its superseded first version.
- **This builder (MEASURED, `delegate-cw.py` on this session's transcript):** 1.20M CW at 2026-11-20T14:24Z (113 calls), taken before the last report edit and commit, so a few calls are not included.
- **Total:** about 1.45M CW, within the task's estimate.
- **Estimate in the task:** 1.0-2.0M CW plus 0.3-0.6M for the judge.

SIZE: 0 product, 156 tests, 503 other hand-written lines (measure.py 455, judge.sh 48), plus this report and the one-line relabel. Generated or copied data (the fixture, flags, row copies, judge packets and replies, evidence) is not counted.

## 6. Notes for the DRI
- **Two tool defects make verdicts wrong** (both are FOLLOW-UPs; this item changes no tool behaviour):
  - (a) `cite_strip` runs on executed code and deletes a parenthesised tuple of definition strings: a false NOT CARRIED, 12 of the 50 false alarms.
  - (b) The counted-document surface compares a citation-led provenance string, which the counter shows but never counts: a false CARRIED, RSP x44.
- **Latent:** `evaluate_known` sets `hit` for a case with no passages (`worst([])` is None, and None is not in PASSING). No known case has an empty passage list, so the in-sample T1 count is not affected. This report counts such cases as misses.
- **The out-of-sample recall depends on the term link.** For stage 2, a ledger record that names the audit's carrier key on a rule that does not use it would be unreachable in the same way (302 of 819 pairs here). The `FACTS` unit has no tool rule.
- **The main question cannot count "not a definition" false alarms,** because it presents the passage as the definition. The supplementary pass shows that 70 of the 120 flagged passages state no meaning of the matched phrase. The stage-2 ruling may want the broad rate (104/120) next to the task's rate (50/120).
- **Conservative choices taken without asking:**
  - all 389 fixture cases were excluded, not only the 61 findings;
  - a no-passage case counts as a miss;
  - a `FACTS` rule counts as a miss;
  - the tool's verdict was withheld from the judge;
  - the main judge pass was not re-run or re-worded after its results were seen.
- **Disagreement with the stage-1 hand check:** bluedot `matched_cost` (stage-1 S7, TRUE) is CARRIED for this judge (paraphrase). Bluedot "unresolved" (stage-1 S3, a false alarm) is NOT CARRIED for this judge on the main question, and DOES NOT DEFINE on the definition pass.

## 7. Final runs (MEASURED)
- **Selected tests:** `zsh mac-pytest.sh --select -- --base d5f402140f --run`. It ran on ve-cloud-2: exit 0, 1819 s. 363 test files plus `tools/test_layer_policy.py` all exited 0; 29 slow files selected for weak reasons were deferred to the chain gate.
  - `tests/test_defs_carried_oos.py`: exit 0 in 2.7 s.
  - `tests/test_definitions_carried.py`: exit 0 in 19.5 s.
  - `tests/test_history_tests.py`: exit 0.
  - `tests/test_hang_guards.py`: exit 0.
  - No test failed, so none is in main-known-red.
- **Local:** `uv run pytest -q tests/test_defs_carried_oos.py` gives 6 passed.
- **Gate collection:** `cd lean && lake build` (1478 jobs, built), then `uv run python tools/gate_collection.py --check --prebuilt`: "36378 collected, 36372 at d5f402140f; 6 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers".
- **Full gate:** not run here (task rule). The chain runs it on the final HEAD.

## 8. Self-review against BUILDER-CHECKLIST
1. N.A. No Lean answer or relay is added or changed.
2. PASS.
   - Deliverables:
     - 1: section 1, `oos_cases.json`, `evidence/recall*.json*`;
     - 2: section 2, `oos_flags.json`, `judge/`, `evidence/tally.json`;
     - 3: the stage-1 Numbers line;
     - 4: this report.
   - Rule grep: no Python copy of a Lean decision and no new permanent report test (D4). The tests read only the fixture, the flags and made-up inputs. No repair-row file is touched (`git diff --stat d5f402140f` lists no `usecases/` path).
3. PASS. `mutants.json`: 6 seeded bugs, each failing its named test in `tests/test_defs_carried_oos.py`. The comparator tests have both sides: the recall test (hit and three kinds of miss) and the tally test (UNSURE both ways).
4. N.A. No Python, Lean or Rust behaviour is changed. `tools/defs_carried.py` is untouched (`git diff d5f402140f -- tools/` is empty).
5. N.A. No relay field and no R8 binding.
6. PASS. Based on `d5f402140f`, which was main at the start. Main has 11 later commits, and none touches `tools/defs_carried*.py`, `tests/data/defs_carried/`, `tests/test_definitions_carried.py`, `tests/history-dependent.json` or the stage-1 report (`git log HEAD..main -- <those paths>` is empty). Not merged, so the measured commit stays the base; the merge train syncs. The evidence commit is named, and no evidence is taken from a live diff. The gate runs on the final HEAD in the chain.
7. PASS. No DELTA row and no trust growth (`tools/trust_map.py --check`: trusted +0), so no signature is needed.
8. N.A. No user-visible output changes (no `ve/`, `lean/`, `rust/` or `usecases/` file).
9. PASS. Local plan of 45 files, runner plan of 363. `tests/test_defs_carried_oos.py` is selected through its own change, and its seeded bugs fail it (item 3).
10. N.A. No Lean statement or proof.
11. N.A. No budget, limit or deadline. The tests use no sleep and no timing (`tests/test_hang_guards.py` passed in the selected run).
12. N.A. No product code path changed. The tool runs are timed in sections 1-2 as information only.
13. PASS. No test was removed or renamed: `tools/gate_collection.py --check --prebuilt` reports 0 refused, 0 stale, 0 malformed (section 7).
14. PASS.
    - Both directions: recall hit and miss; draw kept and excluded; parser accepted and refused lines; disjointness checked on the fixture and on the excluded list.
    - Each claim in sections 1-5 names its command or evidence file.
    - Spec re-read: deliverables 1-4 and the ADV-2 limits, against the task text (`defs-carried-oos-measure-1119` task, DELIVERABLES and BINDING LIMITS).
15. PASS.
    - No overclaim. "unchanged": `git diff d5f402140f -- tools/defs_carried.py tests/test_definitions_carried.py` is empty. "0 of 149 unaided": `evidence/tool-all-docs-at-main.txt`, where all three documents print "marker grep not run". "all 120 judged": `evidence/tally.json`, `unjudged` is [].
    - No silent cut: all four deliverables are built.
    - Every new check can fail: item 3.
    - Limits before work: N.A. (no limits).

FOLLOW-UP: defs-carried-cite-strip-code-1120 the citation strip erases parenthesised definition strings in executed code (eligibility translation.py DEFINITIONS), giving a false NOT CARRIED
FOLLOW-UP: defs-carried-provenance-carried-1120 the counted-document surface counts a citation-led provenance string (RSP rso_maintained, 4.1 RSO sentence) as carrying, giving a false CARRIED
