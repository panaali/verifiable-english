# fid-mech-b5: parallel runner, kill tables, report, first measured run (build report)

**Status:** built, and the first measured run is done: RSP in full, FSF and PF partly (the rest is not-run and resumable; section 5). **HEAD:** the branch head the chain gates (`git log -1`); base main d2573fc9a0.
**What changed:** tools/fidmech/{runner,report,manifests}.py are new. worker.py reaps each fresh run with os.wait4. records.py gives L1-L4 and D an `error` verdict. The CLI gets `batch` and `report`. The first report (counts only) is docs/usecases/fidmech/20261117/.
**Open:** FSF has 192 and PF 415 mutants not run: admission held them back under other jobs' load (section 5.4). This is no blocker: the task allows not-run with a resume command. No FOLLOW-UP is filed.
**DRI signature:** none reserved. DELTA is none and trust is +0.

SIZE: 1296 product, 615 tests, 218 other hand-written lines.
- Product: runner.py 583, report.py 446, manifests.py 190, worker.py +44/−11, `__main__.py` +30/−2, records.py +3/−2.
- Tests: test_fidmech_runner.py 373, test_fidmech_report.py 240, test_fidmech_records.py +2/−1.
- Other: the two fixture manifests under tests/data/fidmech/b5/ (174, written by a script) and the seeded-bug script (44).
- Not counted: the generated report (docs/usecases/fidmech/20261117/), the evidence JSON and tests/history-dependent.json (generated).
- Counted with `git diff --numstat main...HEAD` at bedc92e470.
- No seam cut. The operations seat's override 1 sets no line cap, every run could start, and every deliverable passes its own tests.

## 1. Deliverables (task DO list; plan rev 2 sections 2e, 5.3, 7, 8, 10, 11; decision item 1)

| task line | delivered by | test |
|---|---|---|
| (1) `batch --doc --jobs auto --out [--budget] [--resume]` | `runner.run`, `runner.main`, `__main__` batch (663f970b99) | the tests below |
| (1) admission before each dispatch: workers < 16, 1-min load < 24, cgroup memory.max − memory.current ≥ one worker's measured peak RSS, MemAvailable > 4 GB; else wait and log the wait seconds | `runner.admission`, `wait_admitted`, `schedule`. The peak RSS is the baseline run's, read by os.wait4 | `test_admission_waits_at_load_30_logs_the_wait_and_dispatches_at_10`, `test_the_admission_limits_are_the_plans` |
| (1) exit 75, nothing run, while the 5-min load ≥ 44 | `refuse_if_loaded`, which runs before mutant generation | `test_a_five_minute_load_of_50_exits_75_and_runs_nothing` |
| (1) --budget stops dispatch; the rest is not-run | `schedule` (budget_end); the not-run lines in `run` | `test_the_budget_stops_dispatch_and_the_rest_is_not_run`, `test_a_budget_of_zero_runs_no_mutant_and_reads_not_run_never_a_verdict` |
| (1) --resume continues only on a matching inputs_sha256; a mismatch refuses | `read_resume` (EXIT_MISMATCH 65) | `test_resume_on_a_matching_inputs_sha256_continues_and_a_mismatch_refuses`, `test_a_batch_that_dies_leaves_its_confirmed_results_and_resumes_from_them` |
| (1) the per-batch measurements of plan 7, set beside the 2.8 CPU-h/100 estimate, with "not like for like" | `run` → batch.json "measurements"; `report.CHALLENGER` | section 5.3 (measured) |
| inputs loaded by sha256; a mismatch refuses, nothing run | `manifests.load` with the four pinned SHA256 values from the task. It runs first in `run` and in `report.main` | `test_an_inputs_file_whose_sha256_differs_is_refused_before_anything_runs` |
| (2) kill tables K/L1-L4/D/CR/any/none per op and per document; denominators of 2e; "none" split | `report.kill_row`, `kill_table`, `score` | `test_each_instruments_denominator_leaves_out_what_did_not_run_and_none_is_split` |
| (2) a unit passes only when every applicable mutant ran to a decided verdict; incomplete and untested apart | `report.unit_status` | `test_an_incomplete_unit_is_never_passing_and_an_untested_one_never_passes_vacuously`, `test_a_unit_with_a_baseline_text_hit_fails_and_l2_reaches_it_through_the_predicates_users` |
| (2) stillborn listed, never scored | `runner.run` (runnable = parse ok), `report.scored` | `test_a_stillborn_mutant_is_listed_never_run_and_never_scored`, `test_a_stillborn_mutant_is_listed_and_never_scored` |
| (2) D (Opus 3): an uncovered word plus every `loss` entry; the sidecar is a lever; a sidecar-less document also prints its headline without D | B2's `sentchecks.d` (read, unchanged); `report.unit_hits(with_d)`; the "without D (no sidecar)" variant | `test_d_hits_are_every_uncovered_word_and_every_loss_entry_and_a_sidecarless_document_has_a_headline_without_d` |
| (2) K (point 9): "every mutant of an unprobed rule survives K", with the real count | `prepare` → selection; `report` "unprobed rules" | section 5.2. The measured count is 39 of 76 RSP rule blocks. The line is printed as an expectation, because FSF's whole-document item C-doc killed one such mutant (section 7) |
| (2) levers (point 9) and scores under declared-as-survivor | sentchecks' lever-off rerun (textcheck.json); `kill_table(declared_as_survivor=True)` | `test_syntactic_and_declared_equivalents_are_unscored_and_declared_ones_count_as_survivors_when_asked`; section 5.2 |
| (2) L1m, L1u, L1a, L2q, L2a and L4l have no allegation class: always unadjudicated | `report.NO_ALLEGATION` | `test_the_six_classes_without_an_allegation_are_always_unadjudicated` |
| (3) report.py: lever-off reruns, adjudication matching, `--cr` by fp-1 from fp1.json | `report.document_report`, `adjudicate`, `fill_cr`, `_cr_entries` | `test_a_hit_is_confirmed_or_contradicted_only_by_its_own_class_word_and_unchanged_unit[8]`, `test_cr_fills_a_wording_mutant_only_on_its_unit_kind_text_and_fp1` |
| (3) plants and defects through the loader, rebased by unit text; "not applicable" with the reason; "no repair yet" unscored; a later change never read as a repair | `manifests.plant_records`, `defect_records`, `rebase`, `environment_text` | `test_plants_rebase_by_unit_text_and_a_gone_unit_is_not_applicable_with_its_reason`, `test_a_defect_without_a_repair_is_unscored_and_a_later_change_is_never_read_as_its_repair`, `test_a_changed_line_that_stands_twice_is_not_rebased`, `test_a_vocabulary_edit_regenerates_the_environment_from_the_edited_module` |
| (3) old figures "6/12 plants, 0/14 real" beside the new ones; headline "units passing the stated checks", never "faithful" | `report.OLD_FIGURES`, `HEADLINE`, `render` | `test_the_report_says_units_passing_the_stated_checks_and_never_calls_them_faithful` |
| (3) per-plant rows only to manage-agents; VE gets counts | `report.main --rows`; VE gets `reason_class` and K error classes only | manage-agents reviews/fid-mech-harness/b5-run-20261117/rows.json (617616 bytes). `grep -cE 'PL:\|CTL:\|"P[0-9]{2}\|f20-notify\|AJ:'` on the VE report.json and REPORT.md gives 0 and 0 |
| (4) first measured run of RSP, FSF and PF on VM1, one iso scope each | section 5 | the batch dirs ~/code/fidmech-b5-runs/{rsp,fsf,pf} (outside VE) |
| (5) this REPORT | this file | |

Every new test fails on main. main has no tools/fidmech/runner.py, report.py or manifests.py (`git ls-tree main tools/fidmech/`), so both new test files fail at import there. The fresh-run test reads `Worker.usage`, which main's Worker lacks. The seeded bugs (section 9) show that each test also fails on a wrong behaviour.

## 2. Inputs (decision item 3; Opus point 5)

- `manifests.SHA256` pins the four values the task names. `manifests.load(DIR)` reads each file, hashes it and refuses on any difference (InputsError → exit 65, before mutant generation or any run).
- The real directory loads cleanly. The run's report.json records the four values (`inputs_sha256`).
- Nothing in VE writes these files. VE keeps no copy of them: its tests use tests/data/fidmech/b5/{plants,defects}.json, and `load` takes their pins as an argument.

## 3. The runner (plan 7)

- **Order of work in `run`:**
  1. refusal (5-min load);
  2. inputs by sha256;
  3. an out dir holding results is refused;
  4. mutant generation (B4's `document_mutants` plus the plants and defects; one inputs_sha256 over all of them);
  5. `--resume`;
  6. the baseline text-check report with every lever off (textcheck.json);
  7. the baseline kernel run;
  8. the schedule.
- **Slots and sentinels:**
  - Each of up to 16 slots is a B3 `Worker` (fresh process) in a thread.
  - A slot runs a sentinel after every 20 of its mutants, and a last one.
  - A failed sentinel re-queues that slot's results since its last good sentinel, once.
  - A slot whose last sentinel failed makes the batch INVALID. This is worker.run_batch's rule, applied per slot.
- **Per-run cost.** `worker.evaluate_fresh` now starts the run in its own session and reaps it with os.wait4. The CPU and peak RSS of that run and of what it reaped (its Lean service) are its own, even with 16 runs in one process. Past its limit, the whole session is killed, so no Lean service outlives its run.
- **Text verdicts** (`TextChecks.verdicts`). They run in the mutant's thread after its kernel run. A check kills when the mutant tree has a hit, keyed by (class, block or predicate, quote), that the baseline lacks and that lies on one of:
  - the mutated unit;
  - a predicate whose entry the mutation changed;
  - a block using such a predicate;
  - a sentence the unit quoted at baseline (L4's location).
- **Partial results.** results.partial.jsonl gets each result as a good sentinel confirms it (0fa12fb080). A batch that dies can resume from it. I added this after seeing that the final sentinels wait for admission and that results were written only at the end. The FSF and PF runs started before it existed.

## 4. The report (plan 8)

- **Headline:** "Units passing the stated checks (L1, L2, L3, D, K-structural)", in these variants:
  - all ops;
  - without flip-force;
  - declared equivalents counted as survivors;
  - without D, for a document with no sidecar (FSF);
  - beside them, "K-structural alone" as a decomposition, never the headline.
- **Units.** A unit with a decided K survivor fails. A unit with no survivor but an inconclusive, error or not-run mutant is incomplete. A unit with no applicable structural mutant is untested.
- **Adjudication.** A hit is confirmed or contradicted only by a REAL-by-both or NOT-by-both finding that meets all of these:
  - same allegation class;
  - same unit;
  - overlapping text (the same word, for D and L3w);
  - the unit's fp-1 unchanged since adjudication.
- **VE gets counts only:** the not-applicable reasons as classes and the K errors as exception classes. Unit lists, adjudication rows and per-plant and per-defect rows go to `--rows`.

## 5. First measured run (plan 7)

### 5.1 Commands and commits

- **RSP:**
  - `zsh ~/code/manage-agents/iso.sh exp-fidmut-rsp-20261117T1137 24G -- uv run python -m tools.fidmech batch --doc RSP --jobs auto --out ~/code/fidmech-b5-runs/rsp --budget 10800 --inputs ~/code/manage-agents/reviews/fid-mech-harness/inputs`
  - Commit 9f62a9f039, clean tree. Ran 11:37-12:22Z; exit 0, log rsp.log.
- **PF and FSF:** the same command with `--doc PF` and `--doc FSF`, scopes exp-fidmut-{pf,fsf}-20261117T1223, at commit bb37738b33 (clean). They ran side by side, 12:23-15:55Z and 12:24-15:37Z.
- **Changes between the two commits:** tests only, plus a runner change that moves the out-dir check earlier. The worker, adapters and text-check code are the same at both.
- **The report:** `uv run python -m tools.fidmech report ~/code/fidmech-b5-runs/{rsp,fsf,pf} --out docs/usecases/fidmech/20261117 --inputs <inputs> --rows ~/code/manage-agents/reviews/fid-mech-harness/b5-run-20261117` at 13189f1fd0.
- **Where the full numbers are:** that REPORT.md and report.json hold the full tables. The figures below are copied from report.json.

### 5.2 Per document (RSP in-sample; FSF and PF out-of-sample under the freeze rule)

| | RSP | FSF | PF |
|---|---|---|---|
| batch status | ok | ok | ok |
| mutants / stillborn / scored | 467 / 10 / 436 (+21 plant and defect runs) | 256 / 0 / 256 | 518 / 7 / 511 |
| run / not-run | 457 / 0 | 64 / 192 | 96 / 415 |
| mutation score K (killed / decided) | 50 / 408 (28 K errors left out) | 30 / 64 | 50 / 96 |
| any-instrument (any / scored) | 216 / 436 | 108 / 256 | 148 / 511 |
| L1 / L2 / L3 / L4 / D killed (of scored) | 0 / 48 / 3 / 0 / 148 | 0 / 0 / 5 / 0 / 93 | 0 / 9 / 19 / 0 / 83 |
| units passing the stated checks, all ops | 0 of 85 (76 failing, 9 untested) | 0 of 61 (45 failing, 16 untested) | 0 of 101 (88 failing, 3 incomplete, 10 untested) |
| same without flip-force; with declared as survivors | 0; 0 | 0; 0 (without D: 0) | 0; 0 |
| K-structural alone (decomposition) | 1 of 85 (75 with a K survivor) | 0 of 61 (23 failing, 22 incomplete) | 0 of 101 (36 failing, 55 incomplete) |
| rule blocks in no item (Opus 9) | 39 of 76; their 167 scored mutants: K survived 160, error 7 | 11 of 45; K survived 9, killed 1, not-run 40 | 0 of 91 |
| baseline hits (D; all other classes) | 1232; 205 | 386; 179 | 665; 162 |
| adjudication of baseline hits | 0 confirmed, 0 contradicted, 1437 unadjudicated | 0 / 0 / 565 | 0 / 0 / 827 |
| findings whose unit's fp-1 is unchanged | 0 of 33 | 0 of 8 | 0 of 49 |
| control false alarms (syntactic equivalents) | 0 (no syntactic mutant) | 0 | 0 |

**Reading the table (judgement, not a result):**
- No unit passes in any document. Almost every unit has a baseline text hit. The causes are in the report's "failing units by cause" (RSP: D 58, L2 47, L1 31, L3 12; 74 also have a K survivor).
- The lever-off reruns show what the frozen choices clear:
  - RSP: footnotes 164, sidecar 173, furniture 87, extra 65;
  - PF: sidecar 549, unformalised 262;
  - FSF: footnotes 48, unformalised 33.
- The FSF and PF K figures cover the first mutants in generation order: mostly drop-conjunct (PF 96 of 139 drop-conjunct ran, no other op ran). They are not a sample of all ops.
- **Adjudication: 0 confirmed or contradicted.** Every adjudicated unit's fp-1 changed after its adjudication. fp-1 covers facts.d1.ve and the translation module, which the fix rounds changed, so the plan's rule makes every hit unadjudicated. The report prints "false-discovery proportion among hits not measured", and offers item 32's seeded adjudication sample to the DRI (not run).

### 5.3 Run cost (measured; tokens 0)

| | RSP | FSF | PF |
|---|---|---|---|
| wall s | 2754 | 11605 | 12562 |
| summed child CPU s (getrusage of the children) | 35592 | 16439 | 40417 |
| peak / mean concurrency | 16 / 15.72 | 16 / 2.91 | 16 / 6.96 |
| admission-wait s | 0 | 9369 | 6597 |
| per-mutant s (mean / median / max) | 78.3 / 82.3 / 101.6 | 416.7 / 337.6 / 750.7 | 714.7 / 791.8 / 1008.4 |
| baseline s | 59.1 | 170.4 | 296.7 |
| one worker's peak RSS | 298 MB | 148 MB | 336 MB |
| Lean service start (first parse minus second) | 0.277 s | 0.319 s | 0.448 s |
| CPU-h per 100 mutants | 2.16 | 7.13 | 11.69 |
| wall min per 100 mutants, at the concurrency reached | 10.0 | 302.2 | 218.1 |

**Notes on these figures:**
- The challenger's 2.8 CPU-h per 100 mutants is an estimate for a 280-question set. RSP has 126 questions, so the figures are not like for like.
- RSP ran on a quiet host (load about 2-18). Its 2.16 CPU-h per 100 is the representative figure.
- FSF and PF ran at host loads of 30-75: other agents' trust-mutant sweeps and gates (`ps` at 13:51Z). That cost them:
  - admission waits;
  - per-mutant times 2.4x their baselines;
  - CPU counts that include the contention.
- So their per-100 figures measure that afternoon, not the harness.

### 5.4 Not run, and how to resume

- FSF has 192 and PF 415 mutants not run. The 10800 s budget ran out while admission held them back. FSF waited 9369 s in all, one wait of 6787 s at 1-min loads up to 77; PF waited 6597 s. The logs (fsf.log, pf.log) list each wait.
- The batches printed these commands:
  - `uv run python -m tools.fidmech batch --doc safety-framework --jobs auto --out <new dir> --resume ~/code/fidmech-b5-runs/fsf/results.jsonl --inputs <inputs>`
  - the same with `--doc openai-preparedness` and `pf/results.jsonl`.
- **Run them from a checkout of bb37738b33.** inputs_sha256 binds every file under tools/fidmech/, so from a later commit the runner refuses the resume by design (exit 65).
- Not chained here, because the task fixes about 3 h per document.

### 5.5 Plants and real defects (plan 5.3; counts only, rows in manage-agents)

| | entries | applied | not applicable | excluded / no repair yet | K killed / decided | any instrument | text only |
|---|---|---|---|---|---|---|---|
| plants (RSP) | 24 | 11 | 1 (the unit text is gone at the tree under test) | 12 controls excluded by name | 5 / 11 | 7 | 6 have a text kill |
| real RSP defects | 14 | 10 | 4 (the repair deleted text the defect needs) | 0 no repair yet | 1 / 10 | 10 | 10 have a text kill |

- **Old figures:** the old joint-run figures (item 49: the joint K + CR run before this harness, not isolated) were 6/12 plants and 0/14 real RSP defects. The new figures are isolated runs on main d2573fc9a0's translation:
  - 11 plants apply: K kills 5 and any instrument 7;
  - 10 defects apply: K kills 1 and any instrument (all by text checks) 10.
- **The 4 not-applicable defects.** For each, the repair deleted the legend of a predicate the defective rule names: two legends, each shared by two defects. No unit text marks where the deleted legend stood, and the predicate is gone at HEAD. So putting the defective block back could only fail to parse (judgement call 3).
- The 12 controls are not applied. Their equivalence is the calibration record's.

### 5.6 The K kill row (Opus point 8)

- I wrote no fixture that asserts the "f20-notify-board drop-conjunct → killed" value.
- The K kill fixture is `test_an_answer_turning_undecided_is_inconclusive_and_a_decided_change_kills`: a decided changed answer reads `killed`.
- **The measured value** (RSP run, ~/code/fidmech-b5-runs/rsp/results.jsonl, outside VE):
  - `anthropic-rsp:f20-notify-board:drop-conjunct:1` survived;
  - `:drop-conjunct:2` was killed (item G7 changed).
- So "drop-conjunct of f20-notify-board → killed" holds for one of its two conjuncts, not both.

## 6. Escapes of plan 11 that apply (with what the run shows)

- **K cannot see act or legend wording (opaque atoms).** On RSP, K killed none of the decided wording mutants: qualifier 0/88, quantity 0/40, actor 0/44, attachment 0/5. Wording kills come from L2, L3 and D.
- **Force flips survive where the projection carries no force (RSP).** flip-force: K 0/70 decided, and no instrument kills one (any 0/73).
- **add-guard-true survives where every probing case satisfies the guard.** RSP: K 5/10.
- **Every mutant of an unprobed rule survives K** (point 9). RSP: 39 of 76 rule blocks; 160 of their 167 scored mutants survived and 7 were errors. FSF: 11 of 45; one mutant on such a rule was killed through C-doc, a whole-document item that names no rule ids. So the line is printed as an expectation, with the measured verdicts.
- **L1 sees header quotes only.** No structural or wording mutant edits a header quote, so L1 kills none (0/436, 0/256, 0/511). L1 acts on plants and defects that edit headers.
- **D cannot see dropped stop words; one word set per block.** D kills come from words the rule line or act no longer accounts for (RSP 148).
- **L4 sees only uncovered obligation sentences.** A mutant never uncovers a sentence that another quote still covers. L4 killed 0 in all three documents, rule-drop included.
- **Levers.** The lever-off reruns are in the report (sections 5.2 and 5.3). The hand footnote pairs, spans.json, actors.json, the sidecar, ruled_out and UNFORMALISED coverage are frozen in the commit and in inputs_sha256 (fidmech/ files) or rerun as levers.
- **Seen in this run, not in plan 11.** 28 RSP mutants that B4's parse check let through are refused by VE when run.py runs the whole document:
  - 22 "no single declared reading" (a wording edit makes an act phrase ambiguous across rules);
  - 3 SoftOverHard (a flip-force on a rule a PRECEDENCE pair puts over a hard rule);
  - 3 others.
  
  They are K `error`, outside K's denominator, and counted by class (Notes 3).

## 7. Fixture plants of plan 10 killed (test → class)

| plan 10 row | test | class |
|---|---|---|
| text-check kill | `test_a_mutant_on_a_unit_whose_legend_is_bare_at_baseline_does_not_kill_by_l2` (and the opposite direction: the same edit on a clean baseline kills) | L2 survived on a bare baseline; L2 killed on a clean one |
| K inconclusive | `test_an_answer_turning_undecided_is_inconclusive_and_a_decided_change_kills` | inconclusive (Q1), never killed |
| K kill | the same test (`m-kill` → killed); the f20 value is measured, section 5.6 | killed |
| sentinel | `test_a_worker_with_a_leaked_module_global_makes_the_batch_invalid` | batch INVALID, the mutant re-queued once |
| admission | `test_a_five_minute_load_of_50_exits_75_and_runs_nothing` | exit 75, nothing generated, written or run |

## 8. Tests

- **New files:**
  - tests/test_fidmech_runner.py: 17 tests;
  - tests/test_fidmech_report.py: 14 tests, 21 ids.
- **No new test needs Lean.** The kernel run is an injected evaluator. The fresh-run test runs B3's toy use case in a real process, and the toy needs no Lean.
- **Hermetic:** writes go under tmp_path, waits advance an injected clock, and there is no sleep.
- **Changed:** tests/test_fidmech_records.py, one assertion: the L1-L4/D vocabulary now holds `error`.
- **Condition tests (stay selected).** `tools/select_tests.py --base d2573fc9a0` selects all of these (output /tmp/b5-sel.log):
  - test_fidmech_segment, test_fidmech_l1, test_fidmech_b2, test_fidmech_data, test_fidmech_bindings, test_fidmech_adapters, test_fidmech_worker and test_fidmech_records;
  - B4's test_fidmech_structural, test_fidmech_mutants, test_fidmech_wording and test_fidmech_prune;
  - test_rsp_fidelity_fix;
  - this batch's test_fidmech_runner and test_fidmech_report.

## 9. Seeded bugs (Python is the only language changed)

- **Method.** 20 bugs were planted, each run against its named test and restored. All 20 were killed.
- **Script and evidence:** docs/infra/fid-mech-b5/seeds.py.txt and seeded-bugs.json (each record has file, bug, test, killed and the FAILED line).
- **Final run:** on the final code (13189f1fd0, report.py and the tests unchanged since); the tree was clean after it.

| # | file | bug | failing test |
|---|---|---|---|
| S1 | tools/fidmech/runner.py | the refusal is never checked | test_a_five_minute_load_of_50_exits_75_and_runs_nothing |
| S2 | runner.py | admission ignores the 1-min load | test_admission_waits_at_load_30_logs_the_wait_and_dispatches_at_10 |
| S3 | runner.py | the budget never stops dispatch | test_the_budget_stops_dispatch_and_the_rest_is_not_run |
| S4 | runner.py | resume ignores inputs_sha256 | test_resume_on_a_matching_inputs_sha256_continues_and_a_mismatch_refuses |
| S5 | tools/fidmech/manifests.py | inputs loaded without the sha256 check | test_an_inputs_file_whose_sha256_differs_is_refused_before_anything_runs |
| S6 | runner.py | a standing baseline hit kills | test_a_mutant_on_a_unit_whose_legend_is_bare_at_baseline_does_not_kill_by_l2 |
| S7 | runner.py | inconclusive read as killed | test_an_answer_turning_undecided_is_inconclusive_and_a_decided_change_kills |
| S8 | runner.py | a failed last sentinel leaves the batch ok | test_a_worker_with_a_leaked_module_global_makes_the_batch_invalid |
| S9 | runner.py | stillborn mutants are run | test_a_stillborn_mutant_is_listed_never_run_and_never_scored |
| S10 | tools/fidmech/report.py | every verdict counts as decided | test_each_instruments_denominator_leaves_out_what_did_not_run_and_none_is_split |
| S11 | report.py | an incomplete unit can pass | test_an_incomplete_unit_is_never_passing_and_an_untested_one_never_passes_vacuously |
| S12 | report.py | adjudication ignores a changed fp-1 | test_a_hit_is_confirmed_or_contradicted_only_by_its_own_class_word_and_unchanged_unit |
| S13 | report.py | the no-sidecar headline keeps D | test_d_hits_are_every_uncovered_word_and_every_loss_entry_and_a_sidecarless_document_has_a_headline_without_d |
| S14 | manifests.py | a defect without a repair is applied | test_a_defect_without_a_repair_is_unscored_and_a_later_change_is_never_read_as_its_repair |
| S15 | manifests.py | rebase takes the first of several occurrences | test_a_changed_line_that_stands_twice_is_not_rebased |
| S16 | tools/fidmech/worker.py | a fresh run's resource use is not recorded | test_a_fresh_run_is_reaped_with_its_own_cpu_and_peak_rss_and_its_stderr_names_a_failure |
| S17 | worker.py | a failed run's stderr is dropped | the same test |
| S18 | report.py | VE gets the reason, which names the unit | test_a_defect_without_a_repair_is_unscored_and_a_later_change_is_never_read_as_its_repair |
| S19 | runner.py | a new hit anywhere kills | test_a_new_hit_away_from_the_mutated_unit_kills_nothing |
| S20 | runner.py | confirmed results are not written as confirmed | test_a_batch_that_dies_leaves_its_confirmed_results_and_resumes_from_them |

**Light lane and trust mutants.** No Lean or Rust changed, so there is no trust_mutants sweep (none is required for Python-only tooling, as in B4).

## 10. Test runs

- **While iterating:** the new and changed test files, run locally.
  - `uv run pytest -q tests/test_fidmech_runner.py`: 17 passed.
  - tests/test_fidmech_report.py: 21 passed.
  - tests/test_fidmech_records.py and tests/test_fidmech_worker.py: 71 passed.
- **First selected run.** `mac-pytest.sh --select -- --base d2573fc9a0 --run` at 10483571c7 failed in its fast stage on one test: `tests/test_hang_guards.py::test_no_short_wait_outside_the_reviewed_allowlist`. My fresh-run test asserted on a CPU value.
  - Fixed in 8d254252c7 (the assert reads the peak RSS only).
  - Reran: the hang guard and that test, 3 passed.
- **Final selected run:** section 11.
- **Pre-existing red** (main-known-red.txt): untouched.

## 11. Final checks

- **Selected run.** `zsh ~/code/manage-agents/mac-pytest.sh --select -- --base d2573fc9a0 --run` at bedc92e470 (tree fef7c7e940):
  - ran on ve-cloud-2 (REMOTE_FIRST): 190 of 648 test units, 0 failed, exit 0, 2744 s (log /tmp/b5-selected2.log, "recorded 190 units ... 0 failed");
  - every condition test ran in it and exited 0: test_fidmech_segment, l1, b2, data, bindings, adapters (1214 s, Lean), worker, records, structural, mutants and wording, test_rsp_fidelity_fix, and the new test_fidmech_runner and test_fidmech_report.
- **test_fidmech_prune** (B4) was not among the 190 units. `uv run pytest -q tests/test_fidmech_prune.py` locally: 10 passed.
- **Deferred to the chain gate** by select_tests: 21 test files over 120 s selected only for weak reasons, none of them a fidmech file. The list is on line 8 of the log.
- **Generated files.** `uv run python tools/regen_generated.py --check` exits 0.
  - Its only warning is "codemap is stale (regenerated on merge)", which is advisory on branches.
  - tests/history-dependent.json was regenerated by its generator (10483571c7).
- **Not run here:** the full gate (the chain runs it on the final HEAD), a trust_mutants sweep (no Lean) and lake build (no Lean change).
- **Free disk:** 126 GB (`df -h ~`).

## 12. DELTA

None. This is Python tooling and data: no Lean line, no Rust line, no `ve/` file, no translation, answer or verdict changed, and no decision path replaced. Trust +0 and no signature is reserved. No DELTA.md is written because there is no row. The harness only reports and gates nothing.

**Protected files are untouched:** quote_evidence.py, every conftest, fidquote-gate.py, every translation file, every run.py, B3's bindings.json and the manifests. `git diff --stat main...HEAD` lists only tools/fidmech/, tests/, tests/data/fidmech/b5/, tests/history-dependent.json (generated) and docs/. The new tests contain neither the text DEFAULT_SOURCE nor "pinned source" (`grep -c` gives 0 on both files).

## 13. Judgement calls (conservative choices, not asked)

1. **Text checks run on every scorable mutant, a not-run one included.** They need no Lean. "not-run" is a K verdict.
2. **A text check that raises gets `error`.** It is outside its denominator, as plan 2e puts it. It never reads as survived. 0 such errors occurred in the run.
3. **Plant and defect rebase is strict:**
   - the whole parent block when it stands once;
   - otherwise each changed line by its text, which must stand once;
   - otherwise "not applicable".
   
   For defects:
   - text the repair only added is deleted;
   - text the repair deleted makes the defect not applicable;
   - a vocabulary edit regenerates environment.d1.json from the edited module's text(), so the text checks read what the kernel reads.
4. **Adjudication overlap:**
   - for D and L3w, the same word: the hit's words meet the finding's word set;
   - for the sentence classes, one text holds the other, or they share a run of 4 words;
   - L2b matches the units that use the predicate;
   - L4u matches any unit whose finding's cited text overlaps the sentence;
   - split verdicts never match.
5. **CR by fp-1.** A recall-gate entry fills CR only when its fp-1 equals both fp1.json's measured row and the batch's fp-1 of the unit. Old and new must sit in one edit's find and replace. No `--cr` file was given in this run, so CR reads not-read everywhere.
6. **A decided K survivor fails a unit** even when another of its mutants did not run. "Incomplete" is for units with no decided survivor. Both are never passing (plan 8).
7. **Declared equivalents counted as survivors** read survived on every instrument in that variant. Every equivalents.json is `[]`, so the variant equals the plain one.
8. **One resume round was not chained** for FSF and PF (section 5.4).

## 14. Notes for the DRI (no action asked)

1. **No unit passes in any document.** The baseline text checks alone fail most units: D on unaccounted words, L2 on bare legends and quote classes. Whether D or L2 should count in the headline before sidecar entries and legend quotes are written is the DRI's later call (plan 0: the harness reports only).
2. **0 hits are adjudicated.** Every adjudicated unit's fp-1 changed after its adjudication. fp-1 covers facts.d1.ve and the translation module, so one edit there makes every finding stale. Item 32's seeded sample (two blind adjudicators, about 20 hits per document) is the way to a false-discovery figure.
3. **28 RSP mutants pass B4's per-line parse check and are refused when the whole document runs.** A later generator could move those checks into the parse step, so they are listed as stillborn instead of K error.
4. **Plan 5.3 does not cover deleted legends.** The 4 defects whose repair deleted a predicate's legend cannot be put back on HEAD by unit text. An inputs-seat revision could add the predicate's own vocabulary entry to each such defect.
5. **FSF and PF want a quiet host.** At loads of 30-77 the admission rule (1-min load < 24) held them back for 2.6 h (FSF) and 1.8 h (PF) of their 3 h budgets.
6. **Open from the inputs seat** (README, "Open for B5 or the DRI"):
   - per-claim verdicts of multi-claim REAL entries;
   - whether after_relay may ever count as an adjudication.
   
   B5 reads `verdict` only and never after_relay.

## 15. Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer and no new route. The runner reads the adapters' projections and B3's records, not a Lean response.
2. PASS: section 1 maps every DO line to a commit and a test. Rule-break checks on the diff:
   - no Python copy of a Lean decision: K compares the adapters' projections through B3's `kernel_verdict`;
   - no permanent report test: the run's numbers are saved evidence and no test reads them;
   - no protected file touched (section 12).
3. PASS: 20 seeded bugs, each failing its named test (section 9, seeded-bugs.json).
   - The comparators fail on a changed value: S4 (a resume digest), S5 (an inputs sha256), S6 (a standing hit), S12 (a changed fp-1).
   - Empty and zero inputs: `test_a_budget_of_zero_runs_no_mutant_and_reads_not_run_never_a_verdict`.
4. N.A.: no Python, Lean or Rust path pair. worker.py's run result is unchanged (`test_a_fresh_process_gives_the_warm_projection` in the selected run, exit 0).
5. N.A.: no Lean answer field is read. Input binding: plants and defects bind to unit text, and a changed line that stands twice is refused (`test_a_changed_line_that_stands_twice_is_not_rebased`). A mismatched inputs sha256 or resume digest is refused (S4, S5).
6. PASS: the selected run ran on the committed tree (section 11). Evidence is saved, never read from a live diff. The chain runs the gate on the final HEAD.
7. PASS: no DELTA row and no trust growth (section 12). Each exit code is tested:
   - 75: `test_a_five_minute_load_of_50_exits_75_and_runs_nothing`;
   - 65: the resume and inputs tests;
   - 0, 1 and 2: `test_the_exit_code_is_0_for_an_ok_batch_1_for_an_invalid_one_and_2_when_the_out_dir_holds_results`;
   - INVALID: the sentinel test.
8. PASS: no user-visible VE output changed. The diff touches no `ve/`, Lean, Rust or use-case file (section 12).
9. PASS: `tools/select_tests.py --base d2573fc9a0` selects all 14 fidmech test files and test_rsp_fidelity_fix (/tmp/b5-sel.log). The seeded bugs each failed a test in a selected file.
10. N.A.: no Lean statement or proof.
11. PASS: a budget of 0 gives K not-run, never a verdict (`test_a_budget_of_zero_runs_no_mutant_and_reads_not_run_never_a_verdict`). Tests use an injected clock and no sleep; `test_hang_guards.py` passed in the selected run, after the fix of 8d254252c7.
12. PASS: no product path of VE changed. The harness's own cost is measured (section 5.3: RSP 2.16 CPU-h per 100 mutants). The text checks run once per mutant, in the mutant's thread beside its kernel run. A full text-check run takes 0.6 s on RSP and 1.1 s on PF (/tmp/b5-tc.py), against 59-297 s for a kernel run.
13. N.A.: no test removed or renamed.
14. PASS:
    - Both directions:
      - bare and clean legend (L2 survives and kills);
      - a hit on and off the mutated unit;
      - a matching and a mismatched digest;
      - an applied and a not-applicable plant;
      - confirmed, contradicted and unadjudicated;
      - CR filled and not filled.
    - Every number cites its file or command: report.json, the logs and seeded-bugs.json.
    - Spec re-read:
      - plan 2e (verdict vocabularies, kill rules, denominators, the "none" split);
      - plan 7 (the four admission conditions, exit 75 at 44, budget, resume, the measurement list);
      - plan 8 (the unit-passing rule, the variants, the allegation map, the three outcomes, the uncertainty line);
      - plan 5.3 (rebase by unit text, no repair yet, later change);
      - Opus round 2 points 3, 5, 8 and 9;
      - the task's inputs sha256 values (manifests.SHA256 equals SHA256SUMS).
15. PASS:
    - No overclaim. "every", "none" and "all" in this report each cite a count (report.json) or a test. FSF and PF are written as partial (section 5.4).
    - No silent cut: every DO line is built, and the not-run part is the task's own rule.
    - Every new check can fail: 20 seeds.
    - Limits before work: admission, refusal and the inputs check all run before generation (`test_an_inputs_file_whose_sha256_differs_is_refused_before_anything_runs` and the exit-75 test assert that prepare is never called).
