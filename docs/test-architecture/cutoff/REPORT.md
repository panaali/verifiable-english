# tarch-cutoff: answer-level early cutoff, an R1 experiment (plan rank 8)

DRI signature needed: one, for reading the `answers` measurement (task: "default off until the DRI reads
that measurement"); nothing else. No standing ruling is invoked: the [delta](DELTA.md) records no VE
user-visible change.

- **ts-B2's per-mode narrowing is on for R1 only** (`answer_cutoff.R1_RULE = "modes"`: a
  `select_tests.py --run` that names no `--cutoff`). Its activation gate is met: 30 behavioural Lean seeds
  are caught through the service, each by a test the narrowed selection keeps (26 required), and the ten
  contemporaneous shadow comparisons show no failure outside any selection. A plan print (which
  verify.sh's legacy fast gate reads), `--full`, `tools/gate.py`, the merge train and the nightlies select as
  before; `--cutoff off` turns it off for one run.
- **The `answers` rule stays opt-in** (`--cutoff answers=DIFF`), off by default, for the DRI to read: on the
  30 caught seeds it kept every catching test with a median 23% of today's units (modes 39%), and on the ten
  real changes it was never above today's and missed nothing; its cost is a recording per main commit and a
  replay per build (below).
- **On real changes neither rule saves much yet,** for causes outside this batch (findings 1-3): every
  `ve_service` user reads the pin file, most merges change it, and 6 of 10 changes edit a shared manifest field
  that selects the whole suite. The saving shows on Lean edits alone: S01's selection ran in 33.1 min today,
  15.8 min under `modes`, 8.9 min under `answers` on the Mac.

The [delta](DELTA.md) records no VE user-visible change: this batch changes developer test
selection and recording only. Nothing here is used by `tools/gate.py` (R2), the merge train or the
nightlies (R3); `tests/test_answer_cutoff.py::test_the_gate_and_the_maps_never_reach_the_cutoff`
checks that the gate and the map tools import neither module.

Plan: reviews/test-architecture-2026-10-14.md draft 2, section 3.5 "Answer-level early cutoff is an
R1 experiment", rank 8; Astra's re-check point 6 (ADOPT WITH CHANGES), whose order this batch
follows: first the activation evidence for ts-B2's per-mode narrowing, then request-level recording.

## What the plan asked, and where it is

| Plan or directive line | Owner | Delivered | Evidence |
|---|---|---|---|
| (1) 26 behavioural Lean seeds, each caught by a test the narrowed selection keeps | AGENT | `seeds.json` (46 candidates), `seeds.py`; each seed planted in a Lean runner, `ve_service` rebuilt alone, catching tests run, a catch re-checked with the source restored and the unseeded binary as control (`seeds.py verify`) | `evidence/seeds.json`; table below |
| (1) 10 contemporaneous shadow comparisons of the narrowed selection against the full run on real Lean changes | AGENT | `changes.json` (3 newest Lean merges, 7 Lean branches in flight on 2026-10-16), `measure.py --full-suite` (the gate's collection on ve-mac-1), `shadow.py` | `evidence/shadow.json`; table below |
| (1) Turn ts-B2's narrowing on only for R1, and only if every seed is caught and no comparison has a failure outside the selection | AGENT | `answer_cutoff.R1_RULE = "modes"`, read by the hook for `--run` only; the dropped tests of the six seeds no test caught were run with each seed planted (below) | `::test_a_feedback_run_takes_the_r1_rule_and_nothing_else_does`; `seeds.py check`, `shadow.py check` |
| (2) Record per test unit the `ve_service` request keys it sent | AGENT | `tools/test_map_recorder.py` (opt-in, `VE_TESTMAP_REQUESTS`; the coverage map is unchanged), `tools/answer_cutoff.py record` | `tests/test_answer_cutoff.py::test_recorder_records_each_case_the_client_sent`, `::test_request_records_leave_the_map_as_it_was`, `::test_a_child_and_a_nested_recording_send_for_the_outer_unit`; `evidence/recording.json` |
| (2) Select the union of today's selection for every input but `ve_service`'s answers and the files that sent a request whose answer changed | AGENT | `tools/answer_cutoff.py` (`answers` rule), `tools/answer_replay.py` (replay and diff) | `::test_answers_rule_selects_changed_and_unknown_users_only` |
| (2) One-shot executables keep the module rule; lake/lean, Lean source readers and pins select by file | AGENT | only `select_tests.service_impact` is replaced; one-shot runners, `lake`/`lean`, file readers and pin data readers are today's rules | `::test_answers_rule_selects_changed_and_unknown_users_only` (the `ve_metered` runner stays selected), `::test_a_pin_change_selects_only_data_readers_when_the_new_build_is_pinned` |
| (2) A unit with no request recording, or with randomised inputs, is UNKNOWN and selected | AGENT | `answer_cutoff.unknown_units`, `randomised` | `::test_randomised_inputs_make_a_unit_unknown`, `::test_seeded_randomness_is_not_unknown`, `::test_service_uses_the_record_cannot_replay_make_the_unit_unknown`, `::test_a_unit_that_read_an_answer_the_base_build_changed_is_unknown` |
| (2) Measure against R2 for the Lean changes available (target 10); default off until the DRI reads it | AGENT, then HUMAN (DRI) | the same ten comparisons; `answers` is never a default | `evidence/shadow.json`; the DRI reads this report |
| Touch select_tests.py through one small, marked, opt-in hook | AGENT | `--cutoff RULE` and one call into `answer_cutoff.select` (`tools/select_tests.py`, "tarch-cutoff hook") | `::test_the_hook_passes_its_rule_and_is_off_by_default` |
| Never used by tools/gate.py, the merge train or the nightlies | AGENT | neither module is imported there | `::test_the_gate_and_the_maps_never_reach_the_cutoff` |
| Measure the effect before/after on the Mac | AGENT | selection sizes and their recorded Mac seconds per seed and per change; the recording's and the replays' cost | tables below |
| Full release gate on the committed final HEAD | EXTERNAL (chain) | run by the chain on the test runner, per the task | `gate-result.json` |

## How it works

**Request keys** (`tools/test_map_recorder.py`). With `VE_TESTMAP_REQUESTS` set (`answer_cutoff.py record`),
the recorder reads, at the `ve.service.mode` audit event that `LeanService.exchange` raises, that call's
arguments: per case its key (SHA-256 of the mode, a newline and the case text as the client sent it),
whether the request had an explicit timeout, and the case and environment texts. It also classes each read
of `lean/checkers.lock` as the client's pin check (`LeanService._spawn`) or data. A mode event outside the
client's `exchange`, a request to another executable and a `ve_service` started outside the client leave a
`u` record: the unit is unknown. Requests count for the outermost recording's unit
(`VE_TESTMAP_REQUESTS_UNIT`), so a Python child or a nested recording sends for the test that started it.
The coverage map those runs produce is the map the recorder writes today; request recording is opt-in and
adds no edge. No product file changed: `ve/backends/lean_service.py` is read, not edited.

**Replay** (`tools/answer_replay.py`). Every recorded case is sent to one build, in batches of one mode
(the same batches for every build), each case inline: a case that named its environment by handle carries
that environment instead, the form the client resends when the service lacks a handle. A case's answer is
its bound entry without its positions (`index`, and `case_index` in an error result), hashed over its compact
JSON with Lean's key order, so `1` and `1.0`, `true` and `1` differ. A batch the service refuses is asked one
case at a time; a refusal or the class of what was raised is then the answer. The client's schema and
binding checks run on every response, so a wrong position is a `raised` answer, never a hidden one. A case
the replay could not send (its environment was not recorded, it does not fit a line) is "unreplayable" and
always counts as changed.

The answer format went through four versions while measuring, each forced by evidence:
- format 1 asked one case per request with handles: 28 min for the 601,610 cases on the VM;
- format 2 batched them; the Mac's and the VM's replays of the same source then disagreed on 47 answers;
- format 3 dropped `case_index`, which an error result carries and which differs when one side's batch falls
  back to single cases; two Mac replays of the same build through two client versions still disagreed on 10;
- format 4 sends every case inline, because a handle-named request's bytes, and so its error offsets, depend
  on which environments the process already holds, which varies from run to run.
Format 4 agrees with itself across machines and clients: the VM's x86 build and the runner's aarch64 build of
the recorded source give the same answer to all 601,610 cases, and so do two runner replays of one build
through the 2a4fbf708 and dae12d5ff clients. `diff` refuses replays of different formats or recordings.

**The rules** (`tools/answer_cutoff.py`). Both replace only `select_tests.service_impact`, the part of today's
selection that runs because a test sent requests to `ve_service`; every other rule runs as today, on the map
R1 reads.
- `modes` is ts-B2's per-mode rule (`proposed_service_impact`), unchanged.
- `answers=DIFF` selects the users of the cases whose answers differ between the base and the new build, and
  every unknown service user: not recorded (failed or opaque), a `u` record, an explicit timeout, randomised
  inputs (hypothesis in the unit's file or a test helper; an unseeded call of `random`, `secrets`, `uuid4`,
  `os.urandom` in its test code, read with Python's parser), code changed since the recording, or an answer
  that differs between the recording's build and the base's (a test that reads such an answer may send, on
  the base, a request the recording lacks). The recording supplies the requests only: today's rules read
  today's map, so the `answers` selection is never above today's (`shadow.py check` asserts it on every row).
  A change to lean/VE/Service/Protocol.lean, lean/Serve.lean, lean/VE/Json.lean or the Lean project selects
  every user: the replay cannot show the request loop, batch budgets or case splitting. A pin change selects
  a unit whose only pin reads were the client's pin check only when the new build is not pinned.
- `off` is today's selection. `R1_RULE` is the rule of `select_tests.py --run` (R1) when it names none.

## Evidence

### The recording

<!-- table:recording -->
| Measure | Value |
|---|---|
| Commit recorded | `f9a8b63bd4` (main `dae12d5ff` and this batch's tools) |
| Units / `ve_service` users | 394 / 288 |
| Distinct cases recorded | 601,611 |
| Most cases, by mode | check 135,238, environment 87,564, norm-defaults 40,790, model 39,612, soft-norms 38,334, quantity 35,504, diagnose 26,839, risk 24,060 |
| Pin reads by unit (`lean/checkers.lock`) | client: 173, none: 103, client and data: 115, data: 3 |
| Units not recorded (failed or opaque) | test_hang_guards.py, test_nested_pytest.py, test_run_order.py, test_select_tests.py |
| Unknown units at the recording's own commit | 22, 572.8 s of 7,297.5 s of service users' recorded time |
| Mac job (record, replay, emit) | 2,433.92 s |

Why units are unknown there: a request to another executable (9); property tests (hypothesis) (5); a request with an explicit timeout (3); recorded with exit 0 and opaque (2); lean/.lake/build/bin/ve_service started outside ve/backends/lean_service.py (1); a case whose text or environment was not recorded (1); recorded with exit 1 (1).
<!-- /table:recording -->

### Behavioural Lean seeds

Each seed edits one Lean runner so that it answers differently (a verdict flipped, a field negated, a
diagnostic reworded), rebuilds `ve_service` alone (the one-shot executables keep the unseeded code, so a catch
goes through the service), and computes the three selections for that one file with the recording's map.
`verify` then rebuilds the seeded service, restores the source, and runs the candidate files (the units that
sent a changed case, the files that name the seed's text, else the users of its modes): a catch counts when a
test fails there and passes again on the unseeded build with the same pins. This excludes tests that fail
only because they read the Lean source (trust counts, the English runner's generated copy, statement dumps).
The `answers` columns are lower bounds: a seed replays only the modes whose `runMode` roots import its file,
and the rest keep the base's answers, which can only shrink the selection. The seeds' replays use answer
format 2 on the VM; the 47 answers that format gave differently on the runner make their readers unknown,
which the `answers` columns include. Seconds are each selection's recorded Mac seconds.

<!-- table:seeds -->
| Seed | File | Edit | Outcome | Caught through the service by | Changed answers | Today | `modes` | `answers` (at least) |
|---|---|---|---|---|---:|---|---|---|
| S01 | VE/Alternatives/Run.lean | `NONE-PERMITTED: every available action…` | caught (kept by today, modes, answers) | test_risk_fixtures.py, test_risk_lean_route.py | 65 | 309 / 7748 s | 125 / 4143 s | 73 / 2320 s |
| S02 | VE/Ask/Run.lean | `  \| _ => "by_reading"` | caught (kept by today, modes, answers) | test_ask_cli.py, test_ask_fixtures.py, test_ask_relay.py | 15 | 309 / 7748 s | 59 / 2170 s | 71 / 2339 s |
| S03 | VE/Service/FamilyBundle.lean | `Reading label is not bound to its regi…` | seen by no service test |  | 0 | 309 / 7748 s | 56 / 2134 s | 68 / 2232 s |
| S04 | VE/CertificateWire.lean | `ResourceLimit: certificate replay exce…` | caught (kept by today, modes, answers) | test_w6a_certificate_steps.py | 65 | 311 / 7750 s | 311 / 7750 s | 161 / 6054 s |
| S05 | VE/Service/Diagnose.lean | `InvalidInput: a diagnose case names it…` | caught (kept by today, modes, answers) | test_wire_contract_lean.py, test_wire_gate_corpus.py | 2 | 309 / 7748 s | 73 / 2709 s | 68 / 2232 s |
| S06 | VE/Discourse/Run.lean | `  \| some (.proved n) => "proved (" ++ …` | seen by no service test |  | 0 | 309 / 7748 s | 61 / 2227 s | 68 / 2232 s |
| S07 | VE/Service/Document.lean | `ResourceLimit: Verbalisation exceeds 2…` | seen by no service test |  | 0 | 311 / 7749 s | 108 / 3725 s | 70 / 2232 s |
| S08 | VE/Service/EnglishRun.lean | `    ("roundtrip", .bool (checked && pa…` | caught only by a reader of the Lean source |  | 0 | 309 / 7748 s | 53 / 2042 s | 68 / 2232 s |
| S09 | VE/EnglishGrammar/Run.lean | `No text was read.` | caught (kept by today, modes, answers) | test_english_e2_overlay.py, test_english_e2_responses.py, test_question_reading.py, test_risk_english.py | 67 | 310 / 7749 s | 159 / 5461 s | 77 / 2321 s |
| S10 | VE/Question/Run.lean | `def questionVersion : String := s!"que…` | caught (kept by today, modes, answers) | test_ask_cli.py, test_ask_fixtures.py, test_ask_null_free.py, test_ask_relay.py, test_question_answering_measure_report.py, test_question_reading.py, test_relay_mutation_gate.py | 1921 | 310 / 7749 s | 61 / 2214 s | 75 / 2360 s |
| S11 | VE/Order/ProfileGate.lean | `      ("status", .str "error"), ("erro…` | build failed | | | | | |
| S12 | VE/Service/FamilyNorms.lean | `UnsupportedProfile: norms@0 is required` | caught only by a reader of the Lean source |  | 0 | 309 / 7748 s | 55 / 2048 s | 68 / 2232 s |
| S13 | VE/Service/Family.lean | `graph rejected: a certificate in the r…` | seen by no service test |  | 0 | 309 / 7748 s | 91 / 4447 s | 68 / 2232 s |
| S14 | VE/NormDefaults/Run.lean | `s!"invalid certificate for {t.1}"` | seen by no service test |  | 0 | 309 / 7748 s | 123 / 3856 s | 68 / 2232 s |
| S15 | VE/Norms/Run.lean | `("verdict", .str (if w.conflict then "…` | caught (kept by today, modes, answers) | test_agent_policy_rerun.py, test_consolidation_tools.py, test_lean_service_schema.py, test_norms.py, test_norms_three_way.py, test_stage2_norms.py, test_wire_gate_corpus.py | 15 | 309 / 7748 s | 171 / 4660 s | 72 / 2306 s |
| S16 | VE/Order/Surface.lean | `("for every " ++ s` | caught (kept by today, modes, answers) | test_lean_first_b13a.py, test_order.py, test_order_grammar.py, test_order_round2.py, test_stage2_parse.py | 110 | 310 / 7749 s | 310 / 7749 s | 157 / 5972 s |
| S17 | VE/Service/Standalone.lean | `SyntaxError: the source is not accepte…` | not caught |  | 37 | 309 / 7748 s | 305 / 7576 s | 130 / 5592 s |
| S18 | VE/Time/Wire.lean | `" percentage points"` | caught (kept by today, modes, answers) | test_units_lean_w6a.py, test_units_relay_w6a.py, test_w6a_review_regressions.py | 49 | 309 / 7748 s | 309 / 7748 s | 134 / 5604 s |
| S19 | VE/Service/ReadingsChoices.lean | `duplicate reading set version` | caught (kept by today, modes, answers) | test_stage2_readings.py | 1 | 309 / 7748 s | 63 / 2368 s | 69 / 2271 s |
| S20 | VE/Readings/Run.lean | `distinguishing model does not separate…` | caught (kept by today, modes, answers) | test_readings_nd_lean.py, test_readings_s1_lean.py | 6 | 309 / 7748 s | 115 / 3756 s | 70 / 2234 s |
| S21 | VE/Attribution/Run.lean | `s!"unreviewed act {act} in {u.id}"` | caught (kept by today, modes, answers) | test_reports.py, test_reports_lean.py | 105 | 309 / 7748 s | 63 / 2222 s | 72 / 2325 s |
| S22 | VE/Rights/Run.lean | `(if X.mode == .strict then "strict" el…` | caught (kept by today, modes, answers) | test_compose_integration.py, test_english_unambiguity.py, test_norm_defaults.py, test_norm_defaults_layered.py, test_norm_defaults_report.py, test_readings_defaults_english.py, test_rights_lean.py, test_rights_render_status.py, test_rights_three_way.py, test_soft_candidate_economy.py | 855 | 309 / 7748 s | 121 / 3808 s | 82 / 2462 s |
| S23 | VE/Risk/Run.lean | `SufficientOutsideNecessary: ` | caught (kept by today, modes, answers) | test_risk_every_diagnostic.py, test_risk_lean_route.py | 2 | 309 / 7748 s | 122 / 4118 s | 70 / 2236 s |
| S24 | VE/Risk/Eval.lean | `("possible", .bool (possibleE b c))` | caught (kept by today, modes, answers) | test_risk_differential.py | 162 | 309 / 7748 s | 56 / 2054 s | 69 / 2233 s |
| S25 | VE/SoftNorms/Run.lean | `InvalidInput: exception condition of r…` | seen by no service test |  | 0 | 309 / 7748 s | 135 / 4070 s | 68 / 2232 s |
| S26 | VE/SpeechActs/Run.lean | `UNKNOWN (no premise-status evidence); …` | caught (kept by today, modes, answers) | test_speech_acts_lean.py | 13 | 309 / 7748 s | 58 / 2128 s | 69 / 2235 s |
| S27 | VE/Words/Run.lean | `s!"the rows of {p} are not a list"` | not caught |  | 1 | 309 / 7748 s | 75 / 2468 s | 68 / 2232 s |
| S28 | VE/Service/Standalone.lean | `ResourceLimit: domain exceeds entity l…` | not caught |  | 58 | 309 / 7748 s | 305 / 7576 s | 132 / 5679 s |
| S29 | VE/Alternatives/Run.lean | `("verdict", .str (if conflict then "CO…` | not caught |  | 1 | 309 / 7748 s | 125 / 4143 s | 68 / 2232 s |
| S30 | VE/Discourse/Run.lean | `(if e.startsWith "ResourceLimit" then …` | caught (kept by today, modes, answers) | test_discourse_lean.py | 2 | 309 / 7748 s | 61 / 2227 s | 69 / 2301 s |
| S31 | VE/NormDefaults/Run.lean | `("verdict", .str (if w.conflict then "…` | caught (kept by today, modes, answers) | test_agent_policy_unspecified.py, test_lean_handles.py, test_norm_defaults.py, test_norm_defaults_relay_english.py, test_norm_defaults_switch.py, test_norm_defaults_three_way.py, test_readings_nd_lean.py, test_route_row_schemas.py, test_wire_gate_corpus.py | 681 | 309 / 7748 s | 123 / 3856 s | 74 / 2316 s |
| S32 | VE/Rights/Run.lean | `("verdict", .str (if w.conflict then "…` | seen by no service test |  | 0 | 309 / 7748 s | 121 / 3808 s | 68 / 2232 s |
| S33 | VE/Risk/Run.lean | `("verdict", .str (if conflict then "CO…` | caught (kept by today, modes, answers) | test_risk_fixtures.py | 4 | 309 / 7748 s | 122 / 4118 s | 69 / 2256 s |
| S34 | VE/SoftNorms/Run.lean | `("verdict", .str (if w.conflict then "…` | caught (kept by today, modes, answers) | test_lean_handles.py, test_readings_budget_zero.py, test_readings_defaults_english.py, test_readings_s2_document.py, test_route_row_schemas.py, test_soft_norms_lean.py, test_wire_gate_corpus.py | 15 | 309 / 7748 s | 135 / 4070 s | 72 / 2344 s |
| S35 | VE/SpeechActs/Run.lean | `("verdict", .str (if w.conflict then "…` | caught (kept by today, modes, answers) | test_speech_acts_lean.py | 2 | 309 / 7748 s | 58 / 2128 s | 69 / 2235 s |
| S36 | VE/Service/FamilyNorms.lean | `("verdict", .str (if conflict then "CO…` | caught (kept by today, modes, answers) | test_stage2_norms.py | 404 | 309 / 7748 s | 55 / 2048 s | 69 / 2234 s |
| S37 | VE/Attribution/Run.lean | `return Json.mkObj (base ++ [("status",…` | caught (kept by today, modes, answers) | test_reports.py, test_reports_lean.py, test_reports_status.py | 49 | 309 / 7748 s | 63 / 2222 s | 71 / 2280 s |
| S38 | VE/SoftNorms/Run.lean | `VE.Route.Wire.ok id [("admitted", .boo…` | caught (kept by today, modes, answers) | test_lean_handles.py, test_nested_pytest.py, test_route_row_schemas.py, test_soft_norms_conformance.py, test_soft_norms_lean.py, test_softnorms_public_contract.py, test_wire_contract_three_way.py, test_wire_gate_corpus.py | 10 | 309 / 7748 s | 135 / 4070 s | 72 / 2237 s |
| S39 | VE/Discourse/Run.lean | `if (readingVerdicts res).isEmpty then …` | caught (kept by today, modes, answers) | test_discourse.py, test_discourse_answer.py, test_discourse_constitution.py, test_discourse_lean.py, test_discourse_three_way.py | 688 | 309 / 7748 s | 61 / 2227 s | 72 / 2396 s |
| S40 | VE/Service/Standalone.lean | `  pure (VE.Route.Wire.ok id [("valid",…` | caught (kept by today, modes, answers) | test_b17_owner.py, test_background.py, test_closure_witnesses.py, test_conformance.py, test_constitution_w6a_controls.py, test_data_flags.py, test_evaluate_search.py, test_nary.py, test_norms.py, test_readings_defaults_rd6a.py, test_readings_rd5_plain_probe.py, test_rust_jsonl_schema.py | 36934 | 309 / 7748 s | 305 / 7576 s | 207 / 7049 s |
| S41 | VE/Route/Wire.lean | `  return ok id [("valid", .bool (VE.Ta…` | caught (kept by today, modes, answers) | test_b15b_evidence.py, test_background.py, test_bundle.py, test_data_flags.py, test_definitions_english.py, test_norm_defaults.py, test_norm_defaults_layered.py, test_p0_three_way.py, test_readings_nd_lean.py, test_stage2_bundle.py, test_vacuity.py | 1880 | 310 / 7749 s | 310 / 7749 s | 164 / 6083 s |
| S42 | VE/Route/Run.lean | `[("valid", .bool false)] else []))` | caught (kept by today, modes, answers) | test_b15b_evidence.py, test_definitions_differential.py, test_english_e26_ab.py, test_lean_service_schema.py, test_p0_three_way.py, test_soft_review_regressions.py, test_stage2_evaluation.py, test_w6a_certificate_steps.py | 315 | 310 / 7749 s | 310 / 7749 s | 156 / 5963 s |
| S43 | VE/Time/Wire.lean | `        \| some (value, work) => pure […` | caught (kept by today, modes, answers) | test_eligibility_wfp.py, test_fret_w6a_rerating.py, test_news_w6a_fixtures.py, test_units_lean_w6a.py, test_w6a_documents.py, test_w6a_looprecheck1.py, test_w6a_looprecheck2.py | 669 | 309 / 7748 s | 309 / 7748 s | 137 / 5683 s |
| S44 | VE/Rights/Run.lean | `    ("in_scope", .bool (D.limits.any (…` | not caught |  | 533 | 309 / 7748 s | 121 / 3808 s | 76 / 2408 s |
| S45 | VE/Norms/Run.lean | `    return VE.Route.Wire.ok id [("vali…` | caught (kept by today, modes, answers) | test_agent_policy_rerun.py, test_norms_three_way.py, test_readings_s2_document.py, test_stage2_norms.py, test_wire_gate_corpus.py | 194 | 309 / 7748 s | 171 / 4660 s | 72 / 2412 s |
| S46 | VE/EnglishGrammar/Run.lean | `      status "many" ++ coded "Ambiguou…` | not caught |  | 44 | 310 / 7749 s | 159 / 5461 s | 73 / 2281 s |

46 seeds: caught 30; seen by no service test 7; caught only by a reader of the Lean source 2; build failed 1; not caught 6.
<!-- /table:seeds -->

Six seeds changed recorded answers but no candidate test failed. For each, every test file the `modes` rule
drops (today's selection minus `modes`') ran on the Mac with the seed planted: none failed, so no test the
narrowing drops catches a seed it does not. This holds by construction too: a mode's answers depend only
on the code its `runMode` roots import (Lean sees nothing it does not import), every module of the service
but `VE.Service.Protocol` lies in some mode's import closure, and a unit with no recorded mode is never
dropped.

<!-- table:dropped -->
| Seed | Dropped test files | Run with the seed planted | Failures |
|---|---:|---|---:|
| S17 | 4 | 154 passed in 45.70s | 0 |
| S27 | 234 | 11140 passed, 8 skipped, 83 xfailed, 68 warnings in 1466.82s (0:24:26) | 0 |
| S28 | 4 | 154 passed in 39.85s | 0 |
| S29 | 184 | 5656 passed, 7 skipped, 67 warnings in 733.52s (0:12:13) | 0 |
| S44 | 188 | 5745 passed, 8 skipped, 68 warnings in 1188.91s (0:19:48) | 0 |
| S46 | 151 | 4914 passed, 6 skipped, 6 warnings in 420.01s (0:07:00) | 0 |
<!-- /table:dropped -->

### Ten contemporaneous shadow comparisons

The three newest Lean merges on main, against their first parents, and the seven Lean branches in flight on
2026-10-16, against their merge bases (`changes.json`, heads pinned). Each head's full run is the gate's own
collection (`-m "not live"`, the nightly tests included) on ve-mac-1, run for this comparison; the selections
are those `select_tests.py` makes on that head with the version-7 main map nearest below the base.

<!-- table:shadow -->
| Change | Kind | Paths | Full run on the Mac | Failures | Today | `modes` | `answers` | Misses (today / modes / answers) |
|---|---|---:|---|---:|---|---|---|---|
| tarch-b8 | merge | 21 | 15640 passed, 9 skipped, 83 xfailed in 1410.57s (0:23:30) | 0 | 131 / 4729 s | 131 / 4729 s | 131 / 4729 s | 0 / 0 / 0 |
| lf-14a | merge | 52 | 15444 passed, 9 skipped, 83 xfailed in 1966.32s (0:32:46) | 0 | 388 / 7923 s | 388 / 7923 s | 388 / 7923 s | 0 / 0 / 0 |
| qa-q2 | merge | 151 | 15376 passed, 9 skipped, 83 xfailed in 1842.93s (0:30:42) | 0 | 384 / 7911 s | 384 / 7911 s | 384 / 7911 s | 0 / 0 / 0 |
| premise-scale | branch | 102 | 15722 passed, 9 skipped, 83 xfailed in 2805.98s (0:46:45) | 0 | 398 / 7937 s | 398 / 7937 s | 398 / 7937 s | 0 / 0 / 0 |
| lf-16e | branch | 42 | 15708 passed, 9 skipped, 83 xfailed in 2961.71s (0:49:21) | 0 | 395 / 7937 s | 395 / 7937 s | 395 / 7937 s | 0 / 0 / 0 |
| rd-9 | branch | 104 | 16088 passed, 9 skipped, 83 xfailed in 2277.07s (0:37:57) | 0 | 408 / 7937 s | 408 / 7937 s | 408 / 7937 s | 0 / 0 / 0 |
| lf-14c | branch | 69 | 15672 passed, 9 skipped, 83 xfailed in 1565.72s (0:26:05) | 0 | 395 / 7937 s | 395 / 7937 s | 395 / 7937 s | 0 / 0 / 0 |
| jt-crossplan | branch | 50 | 18 failed, 15593 passed, 9 skipped, 83 xfailed in 2434.35s (0:40:34) | 18 | 393 / 7932 s | 393 / 7932 s | 393 / 7932 s | 0 / 0 / 0 |
| me-1 | branch | 36 | 1 failed, 15588 passed, 9 skipped, 83 xfailed in 2472.38s (0:41:12) | 1 | 169 / 5762 s | 169 / 5762 s | 169 / 5762 s | 0 / 0 / 0 |
| qs-1 | branch | 21 | 3 failed, 15180 passed, 9 skipped, 83 xfailed in 2039.66s (0:33:59) | 3 | 58 / 1920 s | 58 / 1920 s | 58 / 1920 s | 0 / 0 / 0 |
<!-- /table:shadow -->

### What it costs and saves

<!-- table:costs -->
Replay of all recorded cases on one build (format 4, 6 service processes, ve-mac-1): 14 builds, 285-489 s, median 417 s; the runner's Lean build of each tree before it: 170-466 s.

| S01's selection | Test files | Mac pytest, 6 workers | Result |
|---|---:|---:|---|
| today | 308 | 1987 s | 2 failed, 14349 passed, 8 skipped, 83 xfailed, 74 warnings in 1986.61s (0:33:06) |
| modes | 124 | 948 s | 2 failed, 8697 passed, 1 skipped, 83 xfailed, 6 warnings in 948.28s (0:15:48) |
| answers | 72 | 537 s | 2 failed, 3654 passed, 6 warnings in 536.54s (0:08:56) |
<!-- /table:costs -->

## Findings for the DRI

1. **The pins defeat per-mode narrowing on real changes.** All 288 `ve_service` users read
   `lean/checkers.lock` (the client's pin check at every spawn), and a Lean change that rebuilds the service
   adds its pin: 7 of the 10 changes changed the file. Today's file rule then selects every service user, so
   the `modes` rule never narrowed a real change: for the Lean inputs alone, `modes` equals today in all ten
   rows. The `answers` rule drops a unit whose only pin reads were the client's when the new build is pinned,
   and narrowed three changes' Lean part (lf-16e 321 to 217 units, rd-9 333 to 245, lf-14c 313 to 223). 115
   units also read the pins as data, almost all through the Rust checker's own pin check
   (`rust_jsonl.run`); classing that read as the Rust client's, selected only when the `rust_jsonl` pins
   change, is a follow-up (the recording this batch measured keeps it as data, conservatively).
2. **Most changes still select everything for reasons outside this batch.** 6 of the 10 changes edit a
   shared field of `ve/assurance-manifest.json`, which selects the whole suite ("no safe operation map", rank
   4 item 5); with those, every rule selects all units. lf-14a selects all 388 units through its other paths
   and a map 12 commits old. The other three (tarch-b8, me-1, qs-1) rebuilt a byte-identical `ve_service`,
   which rank 4's binary-level cutoff covers without any recording; their selections are not the service's.
3. **`find_map`'s newest-30 window lost qa-q2's base map during this batch,** as other maps were published
   (rank 4 item 2). The shadow comparisons therefore pin each change's map by name and SHA-256.
4. **The full runs were green or failed inside every selection.** Seven heads passed the gate's collection
   with no failure; jt-crossplan failed 18 tests, me-1 one and qs-1 three, all in units each selection kept
   (me-1 and qs-1 selected 169 and 58 of about 390 units). Ten such runs bound a miss rate only weakly; the
   seeds are the power evidence.
5. **Seven seeds changed no recorded answer** (table: "seen by no service test"): a diagnostic or field that
   no test's `ve_service` request reaches. They are gaps of the suite, not misses of a selection, and are
   listed for their owners.
6. **The answers rule needs a fresh recording.** A unit that ran code changed since the recording, or read an
   answer that differs between the recording's build and the base's, is unknown: 29 units for the branches
   on dae12d5ff, 112 for tarch-b8, whose base is older than the recording, and 280 for qa-q2, whose base
   build answers 3,894 cases differently. In R1 it would need a recording per main commit (the Mac job above)
   and a replay per build, on the base's build and on the branch's.
7. **Answers are deterministic only when replayed inline** (format 4); handles and batch positions made
   earlier formats differ between runs and machines (see "Replay" above).

## Seeded bugs in the code this batch changed (Python)

Each was planted in a changed file, the named test failed, and the file was restored (`mutants.py`,
`evidence/mutants.json`). No Lean or Rust product code changed; the behavioural Lean seeds above test the
rules, not code of this batch.

<!-- table:mutants -->
| Bug | File | Seeded fault | Failing test |
|---|---|---|---|
| M1 | tools/test_map_recorder.py | requests with an explicit timeout are recorded as untimed | `test_timeouts_and_data_reads_of_the_pins_are_recorded` |
| M2 | tools/test_map_recorder.py | every read of the pins counts as the client's pin check | `test_timeouts_and_data_reads_of_the_pins_are_recorded` |
| M3 | tools/test_map_recorder.py | a nested recording's requests count for its own output, not the outer unit | `test_a_child_and_a_nested_recording_send_for_the_outer_unit` |
| M4 | tools/test_map_recorder.py | a mode event from outside the client is not marked unknown | `test_service_uses_the_record_cannot_replay_make_the_unit_unknown` |
| M5 | tools/answer_cutoff.py | record files split at U+2028 inside a case text | `test_recorder_records_each_case_the_client_sent` |
| M6 | tools/answer_cutoff.py | unknown service users are not selected | `test_answers_rule_selects_changed_and_unknown_users_only` |
| M7 | tools/answer_cutoff.py | a change to request decoding (lean/VE/Json.lean) narrows by answers | `test_request_handling_and_project_changes_select_every_service_user` |
| M8 | tools/answer_cutoff.py | a pin change selects no pin reader at all | `test_a_pin_change_selects_only_data_readers_when_the_new_build_is_pinned` |
| M9 | tools/answer_cutoff.py | a unit with an explicitly timed request is not unknown | `test_answers_rule_selects_changed_and_unknown_users_only` |
| M10 | tools/answer_cutoff.py | a diff of another build than the one the tests run is accepted | `test_select_answers_refuses_a_diff_it_cannot_trust` |
| M11 | tools/answer_replay.py | a case neither side could replay counts as unchanged | `test_diff_finds_changed_missing_and_unreplayable_answers` |
| M12 | tools/answer_replay.py | the answer digest equates true with 1 | `test_diff_finds_changed_missing_and_unreplayable_answers` |
| M13 | tools/answer_cutoff.py | unseeded calls of the random module are not unknown | `test_randomised_inputs_make_a_unit_unknown` |
| M15 | tools/answer_cutoff.py | a unit that read an answer the base build changed is not unknown | `test_a_unit_that_read_an_answer_the_base_build_changed_is_unknown` |
| M16 | tools/answer_cutoff.py | a diff from another base build than the recording's is accepted without its stale answers | `test_select_answers_refuses_a_diff_it_cannot_trust` |
| M17 | tools/answer_replay.py | an error result's batch position counts in its answer | `test_a_case_answers_alike_alone_and_in_a_batch` |
| M18 | tools/answer_cutoff.py | today's rules read the recording's map, not the one R1 reads | `test_answers_read_todays_map_and_count_the_recordings_staleness` |
| M19 | tools/answer_cutoff.py | a unit that ran code changed since the recording keeps its recorded requests | `test_answers_read_todays_map_and_count_the_recordings_staleness` |
| M20 | tools/select_tests.py | a plan print, which verify.sh's legacy fast gate reads, takes R1's rule | `test_a_feedback_run_takes_the_r1_rule_and_nothing_else_does` |
| M21 | tools/answer_cutoff.py | R1 takes the answers rule before the DRI has read its measurement | `test_r1_never_takes_the_answers_rule` |
| M14 | tools/select_tests.py | the hook ignores the rule it was given | `test_the_hook_passes_its_rule_and_is_off_by_default` |
<!-- /table:mutants -->

## Tests and runs

- New: `tests/test_answer_cutoff.py`, 33 tests (recorder capture with the real service, fail-closed `u`
  records, nested attribution, fold and store, replay and diff, the rules, the hook and its R1 default, the
  gate never importing the cutoff). Locally they pass with `tests/test_select_tests.py`,
  `tests/test_nested_pytest.py` and `tests/test_regen_generated.py` (272 passed on the merged tree).
- Selected tests for the branch on ve-mac-1 (`mac-pytest.sh --select -- --base <merge base> --run`): 153
  units, 0 failed, on 4555583f before the sync with main; <!-- final-selected -->
- `tools/gate_collection.py --check --prebuilt` on the merged tree: 33 tests added, 0 removed, 0 refused,
  stale or malformed trailers. `tools/regen_generated.py --check`: 27 entries fresh after the sync.
- The measurement runs (all on ve-mac-1 through `mac-pytest.sh`, except the seeds, which ran on the VM in
  scratch worktrees): one recording (`J1`), 14 replays in format 4, 10 full runs of the gate's collection,
  3 timing runs, the dropped-test runs above, 46 seeds and their verification.
- Not run here: `tools/gate.py` (the chain runs it on the final HEAD, per the task); a second recording to
  measure the recorder's own run-to-run variation (the randomised-input rule stands in for it, and format 4's
  replay agreed with itself across runs, machines and clients).
- Known red on main (main-known-red.txt): the two sub-tick deadline tests of `tests/test_lean_service.py` and
  the RD8 report test belong to their own items; this batch does not touch them.

## Self-review against BUILDER-CHECKLIST

1. N.A. - no relayed Lean answer or schema changed; the replay reads every response through the client's
   own schema and binding checks (`test_a_case_answers_alike_alone_and_in_a_batch`).
2. PASS - every plan and directive line is in the first table with its delivery and test; no new Python copy
   of a Lean decision (mode reachability is Lean's generated table, answers are Lean's), no new permanent
   report test (evidence is checked by `check_evidence.py` at the batch gate, D4), no authority switch;
   in-flight files: `tools/select_tests.py` (tarch-select) gets one hook, `tools/regen_generated.py` one
   `NOT_REGENERATED` line, merged with main's (`test_the_hook_passes_its_rule_and_is_off_by_default`).
3. PASS - 20 seeded Python bugs, each failing its named test (`evidence/mutants.json`); the answer diff
   catches a changed value, `true` against `1`, `1` against `1.0`, a missing case and an unreplayable one,
   and refuses an empty replay and two recordings (`test_diff_finds_changed_missing_and_unreplayable_answers`).
4. N.A. - no checker or parser changed; the replay's answers agree across machines and clients (format 4).
5. N.A. - no relayed field read by Python changed.
6. PASS - synced with main (`50f784e10`); the saved commit list is `main..HEAD --no-merges` from the
   merge base (`evidence/summary.json`, `check_evidence.py`); the chain gates the final HEAD.
7. PASS - DELTA holds no user-visible change; the one DRI item (reading the answers measurement) is in the
   first line.
8. PASS - DELTA lists the developer-tooling changes; no VE output changed
   (`test_request_records_leave_the_map_as_it_was`).
9. PASS - `select_tests.py --paths tools/answer_cutoff.py` (and `answer_replay.py`, `test_map_recorder.py`)
   selects `tests/test_answer_cutoff.py` and `tests/test_select_tests.py`; the branch's selected run is above.
10. N.A. - no Lean statement or proof changed.
11. N.A. - no public budget or deadline changed; the replay's explicit wall timeout keeps a loaded machine
    from turning an answer into `CheckerUnavailable` (`answer_replay.REPLAY_TIMEOUT`).
12. N.A. - no check or render path changed; the recorder does extra work only with `VE_TESTMAP_REQUESTS`.
13. PASS - no test removed or renamed: `tools/gate_collection.py --check --prebuilt` reports 33 added and 0
    removed, refused, stale or malformed.

Sibling lessons (tarch-b8 review): F1, a conflict with main, was resolved by the sync above
(`tools/regen_generated.py`); F2, fixtures copying the repository per worker, does not occur here: the
recorder tests run one child process rooted at the checkout and copy nothing.
