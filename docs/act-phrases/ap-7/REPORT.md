# ap-7 report: AP-7, do derivations find the auditors' readings?

- **Result: FAIL** on the first bar (recall 23 / 105 = 21.9%); the other two pass (1 / 26 Lean readings judged "not a
  reading" by both seats; no skipped middle). [RESULTS.md](RESULTS.md). No second run. The DRI was told
  (`msg.sh dri ap-7`, 14:46Z, inbox/dri/20261031T144621Z-ap-7-3466439.md); the plan revises D3 or D4 before AP-3 or
  AP-4 merges. D3 and D4 do **not** freeze.
- **No DRI signature reserved; no DELTA** (no product path changes: `git diff --stat main...HEAD -- lean ve rust` is
  empty). Statement gate: no Lean statement added or changed. Pilot bytes moved: 0 (evidence; no unit's status
  changes).
- **Calls:** 144 of 160, 2,227,754 of 4M CW, all Claude Opus 5.5 (`modelUsage` is `claude-opus-5-5` in every
  record), no failed call, no paid fallback, no Sonnet proxy (`runner.py --score`: `"calls": 144`, `"failed": []`).

## Plan rows delivered (plan `80f056f9e`, AP-7)

| Deliverable | Where | Evidence |
|---|---|---|
| (1) Pre-registration before any call: sample, three bars verbatim, matching rule, call limits | [PRE-REGISTRATION.md](PRE-REGISTRATION.md), commit `2fb97f321`; draw [draw.py](draw.py), [draw.json](draw.json), [population.json](population.json) | `test_draw_is_reproducible_and_feeds_the_sample`, `test_preregistration_names_three_sessions_and_the_caveat` |
| (2) Lean's side: `phraseReadings` per phrase with its modal; refused and `none` listed | [dump.py](dump.py) → [lean-readings.json](lean-readings.json), commit `d8b811d49`, before the first call | 20 phrases read, 10 refused, 16 none (`test_sample_is_bound_to_its_sources_and_lean`) |
| (3) Blind calls, raw records, `--score` | [runner.py](runner.py), [raw/](raw/) (144 records), [results.json](results.json) | `test_score_recomputes_from_the_saved_records` |
| (4) RESULTS with one gate line, and beside it the share with a reading and D9's refusals | [RESULTS.md](RESULTS.md) | gate line checked against the score by the same test |
| (5) Tests in jt-e1r's style | `tests/test_ap7.py` (7 tests) | `uv run pytest -q tests/test_ap7.py`: 7 passed |

The two-reading cells are in the sample, but only one is read: *has the right* (as *may*) with *or* gets its two
readings on u076; *may* with a shared *and* (u0283.s04) parses with no meaning, and *must not* with *and* (u0114.s03)
is refused (clause word *is*), so neither tests its cell.

## Deviations and judgement calls (each recorded before the first call unless marked)

1. **Second listing seat:** Opus 5.5, not Codex (Codex at its credit cap until 2026-11-04). DRI ruling
   `reviews/dri-decisions-20261031-ap-7.md` item 1, SIGNED there; its caveat sentence is in the pre-registration and
   in RESULTS, and its condition test is `test_preregistration_names_three_sessions_and_the_caveat`.
2. **"15 units":** the plan's list names 14 unit ids; u105a–c are one sentence, so one phrase (spec G8).
3. **"*and*/*or* inside the verb phrase"** is made mechanical: a join word after the excerpt's first modal or wish
   word (195 of 669 eligible). It also admits joins between clauses, so 12 of the 30 drawn act phrases hold no join.
4. **Vocabularies** for 33 phrases have no registration; the builder wrote them by rule V from the source alone, and
   only `checkVocab` ran before they were frozen. The 13 registered phrases take their AP-2 corpus rows unchanged.
5. **Judging Lean's readings** ("by both") is a separate step after all listing calls, in batches of 8 (6 calls), to
   stay within 160 calls. A failed judgement says NO to all its readings; a failed matching counts min(|A|, |B|)
   agreed readings and none matched (conservative; the plan says only "scored as no reading listed").
6. *(after the pre-registration, before any call, commit `f47df9631`)* the picker is called with `PICK_LIGHT=1`
   (short work, as the readability blind-call harness): load was at the picker's gate. No prompt changed.
7. **Size:** about 740 hand-written lines (PRE-REGISTRATION 88, RESULTS 43, draw 65, dump 107, runner 267, sample 48,
   tests 125; `git diff --numstat` against the merge base), above the ~600 line. Not measured before the run, and an
   experiment that has run once cannot be cut afterwards; nothing else is in the item.

## Seeded bugs (Python; no Lean or Rust code changed)

[mutants.json](mutants.json): 7 plants, 7 killed, restored run 7 passed.

| Plant | File | Killed by (tests/test_ap7.py) |
|---|---|---|
| draw-seed (`"act-phrases-AP7x"`) | draw.py | test_draw_is_reproducible_and_feeds_the_sample |
| eligible-any-join (a join before the modal counts) | draw.py | test_draw_is_reproducible_and_feeds_the_sample |
| failed-match-agrees-none | runner.py | test_failed_calls_score_as_no_reading |
| failed-judge-says-yes | runner.py | test_failed_calls_score_as_no_reading |
| lean-index-unbound (no upper bound on `L<k>`) | runner.py | test_answers_are_typed_and_bound |
| list-prompt-shows-lean | runner.py | test_seats_are_blind_and_within_the_call_limit |
| recall-bar-moved (0.9 to 0.2) | runner.py | test_score_recomputes_from_the_saved_records |

## Trust, generated files, overlap

- `uv run python tools/trust_map.py --check`: K +0, S +0, D +0, G +0, trusted +0, PASS. No allowance, no FOLLOW-UPS row.
- `tools/regen_generated.py --write` once (the new runner's `git show` enters `tests/history-dependent.json`; the
  codemap gains this directory and ap-4a's missing ReadingsExamples line); committed.
- Selected tests on the finished code (`mac-pytest.sh --select -- --base <merge-base> --run`, run
  ap-7-870b9fe5-t458301 on GitHub Actions): 4 shards, 183 units passed, exit 0. The full gate is the chain's.
- No in-flight branch touches `docs/act-phrases/ap-7/` or `tests/test_ap7.py` (`git diff --name-only main...<b>`).

Spec re-read: the three bars and the zero-reading rule against the plan at `80f056f9e`, lines
1063-1068 (verbatim in PRE-REGISTRATION); the sample against lines 1050-1055; the beside-the-bar items against
1069-1070; "D3 or D4 is revised" against 1072-1073; the table cells against section 2.3 (plan 239-246).

**Next item:** the D3/D4 revision (the plan's, before AP-3 or AP-4 merges), then ap-4b and ap-4.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: PASS — every call's answer is parsed and bound (`runner.matched`, `judged`,
   `listed`); `test_answers_are_typed_and_bound` retypes and rebinds each field (12 matcher, 5 judge, 3 list cases).
2. Deliverables and rules: PASS — table above; Files rule kept (`docs/act-phrases/ap-7/`, `tests/test_ap7.py`, and
   generated inventories only).
3. Tests can fail: PASS — 7 seeded bugs killed (mutants.json).
4. Python, Lean and Rust agree: N.A. — no product path; Lean alone decides every reading (`dump.py`).
5. R8 binding: PASS — matcher indices bound to A, B and L, judge ids bound to the batch; `test_answers_are_typed_and_bound`.
6. Gate evidence on final HEAD: PASS for the item's own tests; the full gate is the chain's.
7. No unsigned item: PASS — no DELTA row; the one ruling (seat B) is the DRI's signed decision.
8. DELTA: N.A. — no user-visible change.
9. Selection: PASS — `select_tests.py --base <merge-base>` picks 214 of 512 units, `tests/test_ap7.py` among them.
10. Lean statements: N.A. — no Lean change.
11. Budgets fail closed: PASS — the run refuses a call at 160 calls or 4M CW (`runner.run`); an uncalled step scores
    as failed (`test_failed_calls_score_as_no_reading`, the missing-record case).
12. CPU or memory: N.A. — no product code.
13. Test-removed trailers: N.A. — no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS — each parser test accepts a good answer and refuses bad
    ones, the draw's eligibility is tested both ways; claims cite commands above; spec re-read listed above.
