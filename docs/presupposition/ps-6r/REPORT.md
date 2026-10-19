# ps-6r: wording rows for the four pilot nouns (build report)

No DRI signature is reserved in this item. DELTA row 1 (trust V +4) cites R16.

Feature item ps-6r, rank 24 of the feature feed (acting DRI dri-featurefeed). The batch is PS-6r of
`docs/spec/presupposition-PLAN.md` at 30fcd8520, with PS-0p-r and section 2. It also applies SYNTHESIS O15 (plans add
catalogue rows only) and 4.2 (the English queue), and DRI-DECISIONS-PHASE2 "Presupposition phase 2" X1 (b), which
gives PS-6r an earlier slot in the English queue. Branch `feature/ps-6r`, base main 702ff7429.

## Preconditions

- **Statement gate.** PS-6r has no Lean statement. The plan says it "depends on nothing in this plan" (no Lean row,
  no candidate table, no PS-E1 result). PS-S's open stub gate blocks PS-1, not this item. Passed.
- **Where the catalogue is.** It is still where the plan says. The idiom list is `IDIOMS` in `ve/english_vocabulary.py`.
  english-lean has not moved it into Lean, but Lean keeps an equal copy, `idioms1`/`idioms2` in
  `lean/VE/EnglishGrammar/Lexicon.lean`. That copy is not a mirror only: Lean's lexicon check (V6) reads it on every
  English read, and `tests/test_english_lean_tables.py` keeps the two equal. A row in Python alone is refused at run time
  ("The vocabulary selection was not accepted (invalidGrammar lexicon: V6 predicate core_value_of)"). So each row goes
  into both tables, as every earlier idiom did. This adds no new copy of a decision. The two equal tables existed
  before this item; making them one is the ties row in FOLLOW-UPS.
- **In-flight overlap.** I ran `git diff --name-only main...<branch>` for every branch matching `lean-first/*`,
  `feature/*`, `infra/*` and `foundation/*`. No branch edits `ve/english_vocabulary.py`, `lean/VE/EnglishGrammar/*`,
  `ve/english_grammar/*` or `tests/test_english_lean_tables.py`. `foundation/me-1` and `lean-first/b18` edit
  `ve/english.py`, which this item does not touch. No English-queue item (AP-1 hunk, AT-5, QT-A6, ME-11, QT-B3, SC-7)
  is in flight on `lean/VE/EnglishGrammar/*`.
- **Existing wordings' lint.** The rows change no existing wording's lint (the stop condition did not trigger; see
  DELTA.md). An idiom row is read only for a predicate whose wording is exactly that row. No vocabulary in the
  repository declares one of the four wordings.
- The plan and spec were not on main. They are copied verbatim from 30fcd8520: `docs/spec/presupposition-PLAN.md`
  (blob 42c03405) and `docs/spec/presupposition.md` (blob 2d40b1fa).

## Plan rows

| Plan row (PS-6r) | Delivered | Commit | Test |
| --- | --- | --- | --- |
| "{0} is a N of {1}" for core value, guideline, mission, nature, as idiom-list rows, so that "Some thing is a N of {1}." parses | yes: four rows in `IDIOMS[2]` and `idioms2` | f36e8d3f0 | `test_each_pilot_wording_is_admitted[*]`, `test_existence_sentence_parses_exactly_and_round_trips[*]` |
| admitted by the lint without changing any existing wording's lint (the `human` collision is a fixture) | yes | f36e8d3f0 | `test_the_four_wordings_leave_human_unchanged` |
| preferably the one-line uniqueness sentence "{1} has exactly one N." | **no**, moved to **ps-6rb** (below) | — | — |
| Fixture: each new wording parses and round-trips | yes (parse → exact formula; render → "There is a thing that is a N of X." → the same formula) | f36e8d3f0 | `test_existence_sentence_parses_exactly_and_round_trips[*]` |
| Fixture: "Some thing is a core value of Claude." parses to exactly `∃x core_value_of(x, claude)` | yes, with the constants' display forms "Claude"/"Anthropic" (an English overlay, a document field) | f36e8d3f0 | `test_the_plan_sentence_with_capitalised_display_parses_exactly` |
| Fixture: the enumerated and the one-line uniqueness sentences give the same formula | partly: the enumerated form with "is a mission of" / "is a nature of" parses to exactly `U(D)` and round-trips. The one-line form is ps-6rb | f36e8d3f0 | `test_enumerated_uniqueness_parses_to_exactly_u_of_d[mission_of, nature_of]` |
| Fixture: declaring the four wordings beside "{0} is human" leaves its lint unchanged | yes: same wording, same negative, no issue; "Claude is not human." parses | f36e8d3f0 | `test_the_four_wordings_leave_human_unchanged` |
| Fixture: the quoted fallback is not produced for them | yes | f36e8d3f0 | `test_existence_sentence_parses_exactly_and_round_trips[*]` (asserts no "recorded relation"), `test_each_pilot_wording_is_admitted[*]` |
| Seeded bug: the collision check stops treating the new rows as its own, so "{0} is human" falls back; the collision fixture fails | yes, as PY3 (below) | — | `test_the_four_wordings_leave_human_unchanged` |

**Phase 1's `human` break does not reproduce on main.** Phase 1 (ended 458cc0cb, 2026-10-14 13:04Z) saw
"{0} is human" fall back with SYMBOL_COLLISION once the four binaries were declared. The cause was the printer's head
reservation. A binary wording's head is "is", and a template the lint rejects still reserved that head, so "is human"
collided with it. Commit 7080d6d04 ("Keep rejected predicate templates from reserving head words", 14:34Z the same
day) fixed that. On 702ff7429, `human` is unchanged with the pilot's environment, with or without the rows, and with
either noun (scratch probe over `run-20261012T1800Z/translation.ve.md`; it was not committed because it reads a pilot
file outside the repository). The fixture pins this. Seeded bug PY3 reverts 7080d6d04's line and reproduces phase 1's
exact symptom: `'{0} is classified as "human"' != '{0} is human'`.

**Not delivered: ps-6rb, the one-line uniqueness sentence.** Today "Anthropic has exactly one mission." and "Exactly
one thing is a mission of anthropic." are both refused ("Unknown English phrase 'has exactly one mission'" and
"'Exactly one thing'"). A sentence form for "exactly one" with an owner-first relational noun is grammar: a new
production that reads to `U(D)`, in `lean/VE/EnglishGrammar/*` and the Python reader. It is not a catalogue row, so it
is outside "rows only" (O15, X1 (b)). The plan marks it "preferably". Until ps-6rb lands, VE's enumerated form is the
English of a uniqueness `pre` (plan 2.1). That form is tested above with the new wordings and is enough for PS-0p-r's
u0002 and u0235.

## Other changes

- **Generated files**, all through `tools/regen_generated.py --write`:
  - `ve/english_grammar/LOCK.json` and `lean/VE/EnglishGrammar/Fixed/Version.lean`. The grammar generator requires a
    new `actions_version` when `Lexicon.lean` changes, so it is raised from 30 to 31 (`tools/english_grammar_gen.py
    --write --actions-version 31`). If another branch also takes 31, the second to merge regenerates with the next
    number.
  - `lean/checkers.lock`: the new ve_service is pinned.
  - `lean/declarations.txt`.
  - `docs/trust-baseline.json`, through `trust_map.py --allow`.
- **Ask fixtures re-recorded** (afe33b4f9) with `tools/ask_fixtures.py --write`, for the new actions_version. They are
  recorded evidence that holds the grammar identity. Every answer differs from main's only in
  `identities.actions_version`, 30 to 31; the recorder's `seconds` field also moves. This is the same step as main's
  1a704d381.
- **S3 comparison report re-recorded** with its own tool, for the new actions_version (above).
- `ProfileExamples.lean`: the `#guard` on the idiom-table lengths is now 13/29 (it was 13/25).

## Size

`git diff --numstat $(git merge-base HEAD main)`, hand-written lines only: `ve/english_vocabulary.py` +5,
`lean/VE/EnglishGrammar/Lexicon.lean` +4, `ProfileExamples.lean` 1, `tests/test_presupposition_wordings.py` +101, and
docs (`docs/presupposition/ps-6r/`: DELTA, REPORT, mutants.json, evidence). The total is well under 600. Not counted:
the plan and spec (copied verbatim) and the generated files (lock, version, pins, declarations, trust baseline,
re-recorded ask fixtures and S3 comparison report).

## Seeded bugs

`docs/presupposition/ps-6r/mutants.json`. The Python mutants were run with
`uv run python tools/mutants.py docs/presupposition/ps-6r/mutants.json --evidence docs/presupposition/ps-6r/evidence/mutants-run.json`:
3/3 killed. Each was restored afterwards.

| Id | Language, file | Bug | Fails |
| --- | --- | --- | --- |
| PY1-drop-nature | Python, `ve/english_vocabulary.py` (changed) | the nature row is dropped | `test_each_pilot_wording_is_admitted[nature_of]`, `test_existence_sentence_parses_exactly_and_round_trips[nature_of]`, `test_enumerated_uniqueness_parses_to_exactly_u_of_d[nature_of]`, `test_english_lean_tables.py::test_idiom_tables_equal_python` |
| PY2-core-value-typo | Python, `ve/english_vocabulary.py` (changed) | "core values" in place of "core value" | `test_each_pilot_wording_is_admitted[core_value_of]`, `test_the_plan_sentence_with_capitalised_display_parses_exactly`, `test_idiom_tables_equal_python` |
| PY3-rejected-heads-reserved | Python, `ve/printer.py` (the plan's seeded bug; the collision check lives there, not in a file this item changes) | `eligible = set(env.predicates)`: rejected templates reserve their heads again | `test_the_four_wordings_leave_human_unchanged` (`'{0} is classified as "human"' != '{0} is human'`) |
| LEAN1-mission-row (manual) | Lean, `lean/VE/EnglishGrammar/Lexicon.lean` (changed) | "{0} is a mission for {1}" in `idioms2`. It has the same length, so the length `#guard` still passes | with `lake build` and the mutant build pinned (`regen_generated.py --write --only checker-pins`, so the kill is not a hash refusal): 9 failed, 7 passed. Every test that declares `mission_of` fails with "invalidGrammar lexicon: V6 predicate mission_of", and so does `test_idiom_tables_equal_python`. Restored; rebuilt; `lean/checkers.lock` restored |

R16 mutants per new trusted definition: this item adds **no new trusted definition**
(`tools/trust_map.py --check`). The one changed trusted definition, `idioms2`, carries LEAN1.

## Trust

`uv run python tools/trust_map.py --check` exits 0 on the final tree. Against the merge base 702ff7429: K +0, S +0,
V +4, all in `VE/EnglishGrammar/Lexicon.lean` (the four rows). It is recorded with `--allow` and signed "SIGNED by
standing ruling R16 (DRI-RULINGS.md), ps-6r, 2026-10-18". The FOLLOW-UPS row is "## ps-6r" in
`manage-agents/FOLLOW-UPS.md` (text in `evidence/follow-ups-row.md`).

## Tests

- New: `tests/test_presupposition_wordings.py`, 12 tests. With `tests/test_english_lean_tables.py` that makes 16, and
  all pass.
- `tests/test_ask_cli.py`, `tests/test_ask_relay.py` and `tests/test_ask_fixtures.py` pass after the re-record (106).
- `tools/gate_collection.py --check --prebuilt` exits 0: 12 tests added, 0 removed, 0 refused, 0 stale, 0 malformed.
- Selected tests (`mac-pytest.sh --select`, 355 of 446 units: every English path reads `Lexicon.lean`):
  - First run, on 405a11953: stopped at maxfail on `test_ask_cli` and `test_ask_relay` (the actions_version above). Fixed in afe33b4f9.
  - Second run, on afe33b4f9: see "Selected run" below.
- I did not run the full gate, as the task says. The chain runs it on the final HEAD.
- Pre-existing failures on main (`main-known-red.txt`) are not touched.

### Selected run

Second run, on afe33b4f9. No Mac slot was free, so it ran on the VM under load; 359 of 446 units were selected. My
background wait hit its one-hour limit and the run was stopped before its summary printed. By then:

- 357 units had exited 0.
- `tests/test_english_lean_s3_compare.py` had exited 1. Its `test_committed_report_counts_are_derived_from_individual_records`
  failed with `{'30'} == {'31'}`: `conformance/english-lean/s3-fixture-comparison.json` records the grammar's
  actions_version. I regenerated it with `python -m conformance.english_lean_s3_compare`: exit 0, 170 cases, 0
  unexplained. Besides 30 → 31, the only change is the order of Lark's "Expected one of" token list in two
  messages (the order of a set, which depends on the hash seed). After that `tests/test_english_lean_s3_compare.py`
  and `tests/test_english_e2_report.py` pass (9).
- `tests/test_acts_vocab_mutants.py` (Lean mutants of the Acts grammar, untouched here) had not finished. Rerun alone
  on ve-mac-1: 643 passed in 140 s.

No other record in the repository still holds actions_version 30 (`git grep` and the `.gz` files).

## Pilot bytes (estimate; nothing is claimed before a pilot audit)

The item moves 0 B itself. It removes the one blocker of PS-0p-r's **+116 B** (u0013 24, u0095 36, u0002 37,
u0235 19), which with PS-0p makes +145 B. All of it is audit-gated. With these rows, `core_value_of`, `guideline_of`,
`mission_of` and `nature_of` keep their wordings in the pilot's own environment (noun "thing", constant `anthropic`).
"Some thing is a core value of claude." and the three others parse to exactly the plan's formulas. A pilot run still
has to declare the constants' display forms if it writes "Claude"/"Anthropic" mid-sentence, regenerate its separating
situations (X3) and pass the audit.

## Next item

PS-0p-r: the heading units over the four pilot nouns, a pilot step through the merged pilot prompts. Then PS-E2
after PS-E1. ps-6rb (the one-line uniqueness sentence, a grammar production) can follow in the English queue.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No route, schema or relay changes. The existing English relay and its fuzz tests run unchanged in the selection.
2. Every deliverable built: PASS. The plan rows table above gives commit and test per row; the one-line form is named ps-6rb. Diff grep: no new Python copy of a Lean decision (the rows go into the two pre-existing equal tables, kept equal by `test_idiom_tables_equal_python`); no permanent report test; no file overlap with in-flight branches.
3. Tests can fail: PASS. `mutants.json` (3/3 Python killed, `evidence/mutants-run.json`) plus LEAN1, killed by V6 with the build pinned, not at a hash step.
4. Py/Lean agree, valid inputs still pass: PASS. `test_idiom_tables_equal_python`; LEAN1 shows that a Lean/Python row mismatch is refused; `test_the_four_wordings_leave_human_unchanged`; the selected English suites (`test_english_lean_*`, `test_english_e2_*`).
5. R8 binding: N.A. No Lean-answer field is read newly.
6. Gate evidence matches the final HEAD: PASS. The final-HEAD gate is the chain's. The trust number is measured on the final tree (`trust_map.py --check` exit 0), and no saved commit list is needed.
7. No unsigned item: PASS. DELTA row 1 cites R16 with its conditions (`DELTA.md`); there are no other rows.
8. Every user-visible change in DELTA: PASS. DELTA.md says why existing outputs do not change (the idiom read is exact-match; the repository has no declaration of the four; `test_the_four_wordings_leave_human_unchanged`). The ask-fixture identity change is recorded evidence of the grammar version, not product output.
9. Test selection finds the tests: PASS. `tools/select_tests.py --base 702ff7429` selects `test_presupposition_wordings.py` and `test_english_lean_tables.py`, which PY1, PY2 and LEAN1 fail. 355 units, because `Lexicon.lean` feeds every English path.
10. Lean statements and proofs: N.A. No new theorem. The changed `#guard` (table lengths 13/29) fails at build on a dropped row.
11. Budgets, limits and deadlines: N.A. None touched; the new test has no waits.
12. No CPU or memory regression: N.A. Four rows in a 29-entry list read with `.contains`; no new enumeration.
13. Test-removed trailers: PASS. No test removed or renamed; `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale, 0 malformed.
