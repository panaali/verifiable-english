# anthropic-rsp-fidelity-fix: the T fixes of the RSP use-case audit

Status: built; all five steps of the task delivered, nothing left for a follow-up item. No DRI signature needed.
What changed: 30 UNFAITHFUL units and 7 UNFAITHFUL items fixed in the translation and the harness; no ve/, lean/ or rust/ change.
Answers: 111/126 match the frozen key, as before; only C-doc's SOME condition is restated over its wider cone.
Open items: none (F list empty, no K finding). Next item: `usecase-rsp-reaudit` (`zsh uc-audit.sh anthropic-rsp main 3`).
HEAD: the branch's final commit (see `git log`); the chain's gate result is written to gate-result.json.

Inputs: `reviews/ucfix-classify-20261111.{md,tsv}` (37 RSP rows), `reviews/dri-decisions-20261111-ucfix-cycle.md` item 2,
the pinned source `rsp-3.4.txt` (each changed header quotes its whole sentence from it). PLAN section 12 item 19 records
the fixes; sections 1 to 11 and `answer-key.json` are unchanged.

## Changes by checklist class (prompts/translation-fidelity-checklist.md)

A unit can answer several classes; each is listed under each class it answers.

| Class | Units and items changed | Fix |
|---|---|---|
| 1 dropped clause | f5-evidence-strict, f5-evidence-default, f8-internal, f12-internal-feedback, f12-external-default, f12-share, f13-minimize-default, f13-redact-p, f13-disclose, f13-justify-default, f16-ask-commentary, f16-before-board-default, f16-split-p, f16-only-legal, f19-brief-ltbt, f20-process, f20-investigate, f20-notify-board, f21-no-impeding, f22-internal-review, f22-third-party-review, f24-delay, f25-meet, f25-delay, f26-effort, D2D3 | the clause in the act ("promptly", "regularly", "of receipt", "with relevant expertise", "anonymous as well as identified", "by subject matter expertise", "about once a year", "as best we can tell"), as a guard (F5's "in which case", F8's publication cutoff, F21's "in a way that could impede", the two releases as `unless`) or in the legend with the full sentence (F12's focus list, F20's corrective action, F22's assessed commitments); D3 holds F16's 30 days of receipt |
| 3 exclusive "only" | f16-only-legal | a prohibition on redacting the reviewed version unless either legal ground holds (`unless either ... or ..., or both`) |
| 4 one predicate reused | f9-public, f9-internal, f13 x4, f24-delay, f25-meet, f25-delay, f26-effort, f26-need-not-delay | own evidence and as-needed predicates per Appendix A scenario; F9's own deployment predicates; F13's acts on the public version |
| 7 invented guard | f8-internal, f9-public, f9-internal, f21-no-impeding, f24-argument, f24-delay | f24's `highly_capable` dropped; F9 no longer needs F8's coverage date; F21's qualifier is the guard, not an act |
| 11 elided quote | f5-evidence x2 and every block above | each changed header quotes the whole source sentence |
| crit-a/b/c (items) | K2, K4 (case model: F9's own predicates), K20 (no own fix: stays ALL), C4 (`basis`: different acts), C-doc (named pairs, M2 cone), G1 (`delay`), N3 (RS5 enumerated) | run.py only; `cases.json` is unchanged (its hash is pinned) |

Kept blocks: the other 47 rule blocks and the 11 fact blocks are unchanged; the audit judged them FAITHFUL. Classes 2, 5,
6, 8, 9 and 10 had no finding: no case fact was added to `cases.json` (class 8; K2, K4 and B-INTD's case facts are the
case's own words, set in run.py's `SITUATIONS`), and no reading was added (class 9).

Where the .tsv's wording was not followed, and why:
- F25's scenario keeps its fact predicate `competitors_strong_measures` beside its own evidence predicate, as F24 and
  F26 do. RS5 stays a case premise, as `build_document.READINGS` already records ("case: at least one such
  competitor"), not a second F25 rule: the vacuous release over each competitor makes the import and noimport rules
  coincide, so a rule split would only duplicate a block.
- F16's two legal grounds and F5's, F21's conditions are situation classifications (like `redaction_reason_listed`), not
  open terms: the source names no decider for them. The open terms added follow the source's own decider (OT7, OT8, OT9,
  OT23). No unit changes status (`build_document.py --check`, `measure.py --check` pass).
- F5's act reads "with thorough care" (80-character limit) and the legend quotes the sentence in full.

## Answers, old -> new

From `uv run python usecases/anthropic-rsp/run.py` (prints `111 / 126 (446.7 s)`), compared with main's results.json:

| Item | Old | New | Unit that caused it |
|---|---|---|---|
| C-doc | SOME(RS4=rel&RS7=exec \| RS4=rel&RS7=final) | the same condition, RS4 = rel, over (RS1, RS4, RS5, RS7): 12 of 24 choices | C-doc (PLAN M2's cone) |

Every other verdict is unchanged; the routes of G1 (`delay`), N3 (RS5 rows), K2, K3, K4, G4 (F9's own predicates), B-INTD
(the cutoff) and C4 (`basis`) changed under the same answer. The six section-11 mutants still change exactly their named
results (`results.json` `mutants`: m1 C2, C-doc; m2 G1; m3 C1, C7, C-doc, N2; m4 G3; m5 T1, T2b, T5; m6 D4). The
section-9 counterfactuals: N1 changes 54 items (C-doc newly among them, through its wider cone), N2 G1 and N5, N3 K13.
Up to 34 items become countable at the re-audit (the classification's ceiling); this item claims no audit result.

## Regulated predicates

64 of 64 (`test_regulated_predicates_stay_within_lean_limit`). The vocabulary went from 108 to 120 predicates; all 12 new ones
are classifications or open terms, and `clear_evidence`, `delay_needed` and `significant_lead` were replaced by their
per-scenario predicates. `posture_matched` became 2-ary (situation, competitor).

## F list

Empty: no unit needed a language feature, and N3's route (an act over a competitor sort) was admitted by VE as it is.

## Tests

New: `tests/test_rsp_fidelity_fix.py`, 11 tests (`uv run pytest -q tests/test_rsp_fidelity_fix.py`: 11 passed), including
`test_every_answer_key_cell_equals_its_section_6_cell` (126 cells) and its opposite direction
`test_cell_check_catches_a_changed_or_missing_cell`. No test of `tests/test_safetyfw_usecases.py` was edited:
`uv run pytest -q tests/test_safetyfw_usecases.py -k "rsp and not run_recomputes and not six_mutants and not
invention_audit_checks_the_actual"` gives 48 passed; the full-run tests are in the selected run below.

## Seeded bugs (each planted, the named test run, then restored)

| # | File | Planted | Failing test |
|---|---|---|---|
| a | usecases/anthropic-rsp/rules.d1.ve | `highly_capable` back on f24-delay | test_f24_has_no_added_guard_and_both_delays_carry_their_release |
| b | usecases/anthropic-rsp/rules.d1.ve | f26-effort on `lead_evidence` (two scenarios share one evidence predicate) | test_each_appendix_a_scenario_has_its_own_evidence_and_as_needed |
| c | usecases/anthropic-rsp/run.py | K2's case on the coverage-date `publicly_deployed` | test_f9_and_its_cases_state_no_coverage_date |
| d | usecases/anthropic-rsp/run.py | `G1_ACT = "proceed"` | test_g1_asks_the_translated_delay_act |
| e | usecases/anthropic-rsp/run.py | C4's pair dropped from `c_doc_pairs` | test_c_doc_checks_the_f13_f16_pair_over_plan_m2s_cone |
| f | usecases/anthropic-rsp/answer-key.json (scratch edit) | N3's cell ALL -> NONE | test_every_answer_key_cell_equals_its_section_6_cell |
| g | usecases/anthropic-rsp/rules.d1.ve | f25-delay's release removed | test_f25_quantifies_over_each_competitor_and_n3_enumerates_rs5 |

Each run printed `1 failed, 10 deselected`; `git status` was clean after each restore. Only Python (and the case's VE
text) changed; no Lean or Rust product code, so no Lean or Rust seed.

## DELTA

None: no product code (ve/, lean/, rust/) changed; the use case's own outputs are regenerated by its scripts
(`rsp_vocabulary.py`, `run.py`, `stage0.py`, `build_document.py`).

## Size

SIZE: 465 product, 207 tests, 140 other hand-written lines.

From `git diff --numstat $(git merge-base HEAD main)` without generated files (added + removed): the case's product
files 465 (rsp_vocabulary.py 181, run.py 148, rules.d1.ve 116, stage0.py 11, build_document.py 9), tests 207
(tests/test_rsp_fidelity_fix.py), other 140 (PLAN section 12 item 19: 27, this report: 113).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer schema or relay changed.
2. PASS: each task step maps to a commit and a test (Changes table; tests above).
3. PASS: seeded bugs a-g, each with its failing test.
4. N.A.: no Python/Lean/Rust parity surface changed; the case's own routes are rerun (`test_rsp_run_recomputes_every_key_item_and_records_causes`).
5. N.A.: no new relay field; the case model's new atoms are checked by `check_premises` on every query.
6. PASS: the chain gates the committed final HEAD; no evidence from a moving HEAD (results.json is regenerated by run.py).
7. PASS: no DELTA row and no trust-budget growth.
8. PASS: DELTA none; the use-case answers diff is above (C-doc only).
9. PASS: the selected run below includes tests/test_rsp_fidelity_fix.py and the rsp_* tests.
10. N.A.: no Lean statement or proof.
11. N.A.: no budget or deadline code.
12. PASS: C-doc's W1 checks are memoised per applicable rule set (one check per distinct document: 51 s, not 369 s, for 24 choices).
13. PASS: no test removed or renamed.
14. PASS: opposite directions (`test_cell_check_catches_a_changed_or_missing_cell`, C7's conflict beside N3's silence, B-INT without the cutoff); spec re-read: section 6 cells against PLAN.md 6.1-6.9, RS5 against PLAN 3.1 line 98 and READINGS `rs5_all_competitors`, M2's cone against the task text.
15. PASS: universal words in this report each name the command or test above; nothing deferred.
