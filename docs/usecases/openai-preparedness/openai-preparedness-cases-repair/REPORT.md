# openai-preparedness-cases-repair: an accounting line for the Preparedness case records

**Status:** built; target met; no DRI signature reserved; no DRI question sent.
**What changed:** `usecases/openai-preparedness/accounting.d1.txt` gets one line for the case records (cases.json), and that line reads "nothing". The accounting tool `usecases/safetyfw_accounting.py` gets anthropic-rsp-cases-repair's extension for collection-unit lines, byte for byte (step 2). The saved report `docs/usecases/safetyfw/openai-preparedness/accounting.json` is regenerated with the tool's own `--report`.
**Target:** exposure.py goes from 9 to 8 on FACTS/CASES. The `CASES <- CASES no-record` row is gone, and no row is new (see the exposure section below).
**Open items:** none. No D2D3 line was added (deliverable 3).
**Gate:** the chain runs it on the final HEAD.

Ruling: orchestrator re-plan ruling 2026-11-14 22:48Z, item A3; decision reviews/dri-decisions-20261114-replan-ruling.md;
diagnosis reviews/facts-cases-diag-20261114.md, section 1, PF row (both in manage-agents).

## Deliverables

| # | task line | delivered | evidence |
|---|---|---|---|
| 1 | one accounting line for the case records, true, checked against PLAN 5 first | the last line of accounting.d1.txt; it reads "nothing"; the case check is below | `uv run python usecases/safetyfw_accounting.py usecases/openai-preparedness --source ~/code/manage-agents/pilots/openai-preparedness/source/pf-v2.txt --check --report docs/usecases/safetyfw/openai-preparedness/accounting.json`: exit 0, "100 blocks, 527 unaccounted words in 73 blocks, 15 blocks with a loss {'1': 17, '3': 1, 'limit 21': 1}, 0 of 117 quotes unanchored" |
| 2 | the tool takes the line: the same extension as anthropic-rsp-cases-repair, or none | that branch is in its gate stage, not on main, so its diff of `usecases/safetyfw_accounting.py` and `tests/test_safetyfw_accounting.py` (`git -C ~/code/ve-anthropic-rsp-cases-repair diff main...HEAD`, its HEAD fa7f574a55) is applied with `git apply`, unchanged. The two hunks are identical on both branches, so whichever goes second sees the same change | `git apply --check` exit 0; `uv run pytest -q tests/test_safetyfw_accounting.py`: 72 passed |
| 3 | no D2D3 line | none added | `grep -c '^D2D3' usecases/openai-preparedness/accounting.d1.txt` = 0 |
| (a) | test: the line exists and parses | `test_cases_accounting_line_exists_and_parses` | tests/test_pf_fidelity_fix.py |
| (b) | test: every case text is PLAN text, or on a named allow-list with its reason | `test_every_case_text_is_plan_text_or_an_allowed_transcription` | tests/test_pf_fidelity_fix.py |

Test (a) checks four things. The case-records line is the only one and the last one. The tool reads the file with no problem
and lists the line as a collection with no entries. The installed omission rule's port (`tests/omission_rule.py`) gives the
case records no path other than `report`; that path reads batch reports, which no permanent test pins (D4). Last, the line's
text is exact. Test (b) is described in the next section.
`uv run pytest -q tests/test_pf_fidelity_fix.py -k 'cases_accounting_line or every_case_text'`: 2 passed.

## The case check (why "nothing" is true)

A read-only probe compared cases.json with PLAN.md and with the pinned text
`~/code/manage-agents/pilots/openai-preparedness/source/pf-v2.txt` (sha256 d2e3dd5b80e5…, the hash PLAN 1 pins). Test (b) checks
the PLAN half without the source, which the repository does not hold.

1. **The 67 records are PLAN wording.** cases.json has 67 records: A 28, B 7, K 20, T 2, G 10. Families C, N, S and D have no
   record there.
   - A and B: the situations are PLAN 5's table (PLAN.md:204-205: *L* in the seven levels, *X* in the four activities) read
     with PLAN 5's case-facts sentence (PLAN.md:197-200), in the forms "<L> reached; activity <X>" and "<L> reached; a major
     deployment (OT13)". L0 is written "no threshold reached" (PLAN 2, PLAN.md:48). The test checks every id, level,
     activity and finding against that table.
   - K, T and G: 30 records. 28 are the first Situation cell of their PLAN 6 row, word for word (K6 is scored as K6a-c, and
     its first row states the situation). The other two are on the test's allow-list `SITUATION_ALLOWED`, each with its
     reason. K8: PLAN 6.3's cell is "the same", and the record writes "the same (as K7)". T2: PLAN 6.4's cell is "5 weeks
     against 20", and the record writes it in T1's form; `quantities` holds 5 and 20, and the test checks both numbers.
   - `source` is PLAN 5's case-facts sentence (PLAN.md:197-200, whitespace joined) with the record convention appended.
     `activities` are PLAN 2's four activities (PLAN.md:50-51).
   - No record has a field beyond `id, family, levels, activity, situation, findings, quantities`. The RSP records have a
     `source_sentence` field; the Preparedness records have no such field, and the test refuses one.
2. **Shared word runs with the source are rule antecedents, not transcriptions.** The probe found the longest run of the
   source's words in each text. 11 texts share a run of 4 or more words: 10 situations and the LINT activity name. The
   longest are K1 (8 words, "a covered system appears likely to cross a"), K2 and K13 (7 each), then K9, K11 and K14 (5
   each). None is a whole source sentence. Each situation run is the condition of the rule the case triggers, which PLAN 6
   restates to set up the hypothetical. Each run lies inside the source quote of a block header, and each of those blocks
   has its own accounting line: f8-start (K1), f7-recommend (K2), f6-rel (K4), f10-validate and f10-review (K5), the six
   f3-develop* and f3-inuse* blocks (K7, K9), f5-ambiguous (K11), f16-chair-strict, f16-chair-default and f16-fast-track
   (K13), f15-third-party (K14), f12-ara and f12-ara-unscoped (K19), and f1-alignment-cyb-strict and -default (LINT, "large-scale
   internal deployment", also PLAN's open term OT8). Each case text states its run whole. None is a source passage cut
   short. So the expected DRI question 1 ("a case transcribes source words") does not arise, and none was sent.

## Exposure (exposure.py, before and after)

Command: `python3 -I ~/code/manage-agents/reviews/facts-cases-diag/exposure.py openai-preparedness <sha>`. A sha is passed
because the script resolves `HEAD` in the main checkout, not in this worktree. With `HEAD` it read commit 9fe83bcc6e and
printed "VE files unreadable". The verbatim outputs are saved beside this file, because their rows quote the accounting tags
and the REPORT scan would read those tags as records: `exposure-before.txt` (main a84c072d76) and `exposure-after.txt`
(02d4011acd, the last product commit).

| row (unit, record unit, path) | main a84c072d76 | 02d4011acd |
|---|---|---|
| FACTS, rs2-nest, mistag | 1 | 1 |
| FACTS, no-critical-models, mistag | 1 | 1 |
| FACTS, no-critical-models, the tagged entry (p. 13 sentence) | 1 | 1 |
| FACTS, rs2-nest, plan12 | 2 | 2 |
| FACTS, no-critical-models, plan12 | 1 | 1 |
| FACTS, FACTS, report (fix-2 REPORT.md:102) | 1 | 1 |
| FACTS, no-critical-models, unformalised p13-u212 | 1 | 1 |
| CASES, CASES, no-record | 1 | 0 |
| total on FACTS/CASES (the script's last line) | 9 | 8 |

The D2D3 row (no accounting line) is in both outputs and is not counted by the script; deliverable 3 leaves it.

The installed counter changed while this item ran: sha256 1c7cc4f7 at the first run on main, 28966da1 at the second. Both
counters give main the same 9 rows (`diff` of the two outputs without their first line is empty). Both saved files come from
28966da1.

**Every unit.** A read-only script (`/tmp/pfexpall/expall.py`, not committed) runs the same counter's `omit_exposure` over
all 90 units of the PF manifest at two commits and prints the row difference. Main a84c072d76 against 02d4011acd gives
"units 90; exposures 254 -> 253", and the only row that left is ('CASES', 'CASES', 'no-record'). No row is new. The same check
on the REPORT's own commit is in the last section.

## Answers old -> new

None moved. results.json, cases.json, PLAN.md and answer-key.json are byte-identical to main
(`git diff --quiet main -- <those four files>`, exit 0), and run.py reads neither accounting.d1.txt nor
safetyfw_accounting.py (`grep -rln 'accounting.d1\|safetyfw_accounting' usecases/ tools/`: only the tool itself and tools/fidmech,
which uses only the tool's folding table and block reader).

## The saved accounting report

The regenerated `accounting.json` has two kinds of change. (1) The new `collections` key holds the case-records line with no
entries. (2) Two blocks, f9-risk-paths and f15-third-party, list fewer unaccounted words, so the total is 527 where main's
saved copy says 539. That second change is not from this item: main's own tool (`git show main:usecases/safetyfw_accounting.py`)
run on main's own accounting file today also gives "527 unaccounted words", and its report equals the new one key for key
apart from `collections` (probe output: "same except collections: True"). Main's saved copy predates fix-6's legend edits.

## Seeded bugs (each planted, the named test failed, restored with `git checkout`)

| # | language, file | bug | failing test |
|---|---|---|---|
| a | data, usecases/openai-preparedness/accounting.d1.txt | the case-records line deleted | `tests/test_pf_fidelity_fix.py::test_cases_accounting_line_exists_and_parses` (the omission rule's port returns the no-record path) |
| b | data, usecases/openai-preparedness/cases.json | K14's situation "warrants deeper testing" -> "warrants further testing" | `tests/test_pf_fidelity_fix.py::test_every_case_text_is_plan_text_or_an_allowed_transcription` (AssertionError: K14) |
| c | data, usecases/openai-preparedness/accounting.d1.txt | the line given a quoted phrase with an empty tag, `"a major deployment"` | `tests/test_pf_fidelity_fix.py::test_cases_accounting_line_exists_and_parses` (the tool: "line 101: unreadable entry") |
| d | Python, usecases/safetyfw_accounting.py | the refusal of the restates tag on a collection line switched off (`if False and ...`) | `tests/test_safetyfw_accounting.py::test_a_collection_unit_has_one_line_after_the_blocks[lines11-a collection has no rule text that restates it]` |
| e | Python, usecases/safetyfw_accounting.py | a collection line read but not kept (`collections[block_id] = entries` -> `pass`) | `tests/test_pf_fidelity_fix.py::test_cases_accounting_line_exists_and_parses` (KeyError: 'collections') |

No Lean or Rust file changed, so no bug was seeded there.

## Trust, DELTA, size

- Trust: `uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0", PASS.
- trust_mutants: not run. No Lean or trusted file changed (trust +0), and the task does not ask for a sweep. Checklist 13a
  applies to trusted Lean growth only. The light-lane check printed "NOT 197 changed lines outside generated files > 150".
- DELTA: none. The change is to use-case files and the use-case accounting tool only: no ve/, lean/ or rust/ change, and no
  verdict or answer moved.
- SIZE: 44 product (accounting.d1.txt 1; safetyfw_accounting.py 43, the sibling's change), 124 tests (test_pf_fidelity_fix.py
  84; test_safetyfw_accounting.py 40, the sibling's change), other hand-written lines: this REPORT and the two saved outputs.
  Generated: accounting.json 29. From `git diff --numstat $(git merge-base HEAD main)`. The planner's ~5-30 lines + tests
  (ASSUMED) holds for this item's own lines. The sibling's tool change is the rest.

## Spec re-read

- The case-records line against the task's DELIVER 1 and the diagnosis row "PF CASES | no accounting line (216 answers)".
- The A/B templates against PLAN.md:197-200 (case facts) and PLAN.md:202-207 (table rows A, B).
- The K/T/G situations against PLAN.md:262-325 (6.3, 6.4, 6.6), K6a-c at PLAN.md:271-273, K8 at :275, T1/T2 at :293-294.
- The activity names against PLAN.md:50-51.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer and no ve/ or lean/ change.
2. PASS: deliverables 1-3 and tests (a), (b) are in the table above. The overlap rules hold: run.py, tests/test_safetyfw_usecases.py and PLAN 12 are untouched.
3. PASS: seeded bugs a-e, each with its failing test.
4. N.A.: no Python/Lean/Rust decision path. Valid input still passes: `tests/test_safetyfw_accounting.py` 72 passed, including `test_case_sidecar_passes_in_form` for both cases.
5. N.A.: no relay binding.
6. PASS: the gate is run by the chain on the final HEAD; the exposure outputs name their commits.
7. PASS: no DELTA row, no reserved signature.
8. N.A.: no user-visible checker change.
9. PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects test_pf_fidelity_fix.py and test_safetyfw_accounting.py (and not every unit). Seeded bugs (a), (b), (c) and (e) fail in test_pf_fidelity_fix.py, and (d) fails in test_safetyfw_accounting.py, both in the selection.
10. N.A.: no Lean.
11. N.A.: no budget, limit or deadline.
12. N.A.: no runtime path changed (the tool's extra loop is over the collection lines, at most two).
13. N.A.: no test removed or renamed.
14. PASS: both directions. The tool's 16 parametrised cases accept six collection lines and refuse ten. Test (a) accepts the true line and refuses bugs (a), (c) and (e). Test (b) accepts the 67 records and refuses (b). Every claim above names its command. Spec re-read is listed.
15. PASS: overclaim check of "every", "no" and "none" above: each names its test or probe. No deliverable is cut. Every new check has a seeded bug. Limits: N.A.

## Notes for the DRI

- exposure.py resolves `HEAD` in the main checkout, so in a worktree it needs a sha. With `HEAD` it read 9fe83bcc6e and
  printed "VE files unreadable at the run commit".
- Main's saved `docs/usecases/safetyfw/openai-preparedness/accounting.json` was stale (539 against 527 unaccounted words)
  before this item. It is current now.
- The 23 old read rows on the case records (pf-reads.tsv, even rows 4-48) are for the decider's row facts-cases-omission-reads,
  as the task says. This item did not touch them.
- When anthropic-rsp-cases-repair and this item both reach main, the tool hunks are identical, so the second needs only
  its own sidecar line and test lines (merge note 2026-11-14T23:41Z).

## Final-commit check

(Filled after the REPORT's commit.)
