# defs-repair-claude-constitution-pilot-1119 REPORT

- **Status.** All 15 P1 rows KEPT and carried. No DRI signature is needed; the one DELTA row cites R3. Built on main `f5553bc894`, no merge commit. Tests last ran at code HEAD `0b0c6f23`; this report is the only later commit.
- **What changed.** A new run directory `usecases/claude-constitution-pilot/run-20261119-defs-carry/`, per the DRI decision of 2026-11-19 (item 1; manage-agents `reviews/dri-decisions-20261119-defs-repair-claude-constitution-pilot-1119.md`). Its probe's 15 legends end with the source's definition of their term, word for word. Run-20261104T0716Z is byte-identical to main.
- **Answers touched.** 10 of 10 keyed answers: queries c6-denial, c7-clarification, c9 x3 and claim-human, and comprehension C1-C4. This is the union of the rows' `answers_touched`. Later reads should re-pin to the new probe.
- **Open.** Nothing is left undone in this item. The pilot reader has to read the new directory's probe (DRI decision: "The next pilot read uses the new probe"). The reader itself is out of this item's scope.

SIZE: 143 product (the run's two scripts; no `ve/`, `lean/` or `rust/` line), 262 tests, 33 other hand-written lines (SUMMARY.md and DELTA.md) plus this report. Tool-written outputs, not counted: the probe (756 lines) and the answers and records (24,229 lines).

## 0. Verification (orchestrator item 1)

The source is the probe's body, which is the pinned translation's body (`tests/ce4.py`: sha256 and blob checked). It is not hash-pinned in `usecases/pinned_sources.json` (METHOD amendment 8). The frozen text the reader is shown is that probe's front matter at main. Each quote was checked by `/tmp/defs1119/verify2.py`. After the list and bold marks are dropped, every quote word is in its cited source lines, in order. None occurs anywhere in the front matter. Each rule uses its carrier term (`verify3.py`). After the carry, `cmp.py` printed `EQUAL raw-equal` for all 15: the appended text equals the audit's quote byte for byte. Line numbers below are file lines of `usecases/claude-constitution-pilot/run-20261104T0716Z/probe-translation.probe.md`.

| row id | KEPT / DROPPED | reason |
|---|---|---|
| defs-claude-constitution-pilot-1-1119 | KEPT | probe:655 defines the name Claude; sort `claude_instance` legend lacks it; R1, R2, R4, R8-R17 and R19 use the sort through their predicates |
| defs-claude-constitution-pilot-2-1119 | KEPT | probe:655; constant `claude` legend lacks it; the English fence at probe:754-756 ("Claude is not human.") names Claude, whose only vocabulary entry is that constant |
| defs-claude-constitution-pilot-3-1119 | KEPT | probe:98, 99, 101; sort `operator` legend says only "in the source's sense"; R3, R5-R7 use it |
| defs-claude-constitution-pilot-4-1119 | KEPT | probe:99, 101; sort `user` legend is "A user of Claude."; R9 uses it |
| defs-claude-constitution-pilot-5-1119 | KEPT | probe:292 (second sentence); `instruction_deceptive_tactics_harming_users` legend lacks it; R3, R5-R7 use it |
| defs-claude-constitution-pilot-6-1119 | KEPT | probe:292; `system_prompt_deception_permitted` legend lacks it; R9 uses it |
| defs-claude-constitution-pilot-7-1119 | KEPT | probe:111 and probe:113 (last sentence); `judgment_use_required` legend names conversational inputs only; R2 uses it |
| defs-claude-constitution-pilot-8-1119 | KEPT | probe:282-290 (from "There are many different components of honesty" to the list's end); `instruction_dishonest_looking_within_honesty` names the principles only; R5 uses it |
| defs-claude-constitution-pilot-9-1119 | KEPT | probe:34, 247 (first sentence), 97 (first sentence); `instruction_act_against_guidelines` lacks them; R3, R5-R7 use it |
| defs-claude-constitution-pilot-10-1119 | KEPT | same passages; `compliance_against_guidelines` lacks them; R4 uses it |
| defs-claude-constitution-pilot-11-1119 | KEPT | probe:32; `compliance_unsafe` legend lacks it; R4 uses it |
| defs-claude-constitution-pilot-12-1119 | KEPT | probe:33; `compliance_unethical` legend lacks it; R4 uses it |
| defs-claude-constitution-pilot-13-1119 | KEPT | probe:609 (second sentence), 41 (last sentence), 97; `clear_and_substantial_undermining_of_oversight` carries a fragment only; R13 uses it |
| defs-claude-constitution-pilot-14-1119 | KEPT | probe:476-480; `illegitimate_absolute_control` legend lacks it; R15 uses it |
| defs-claude-constitution-pilot-15-1119 | KEPT | probe:436-444, 446, 456 and 460 (first sentences); `seemingly_compelling_argument_to_cross_line` lacks them; R17 uses it |

## 1. Carrier: the DRI's ruling

There is no `frozen-run.json` and no seal hash. Even so, run-20261104T0716Z is a recorded measurement. Legend descriptions are part of the environment's identity (`ve/environment.py:1`). Candidate meaning ids hash that identity (`ve/norms.py:342`), and so do situation ids (`ve/readings_s1.py:126`). So an append in place would change identities its 17 saved whole-translation answers name, and those cannot be re-measured (L70). I asked the DRI (inbox `20261119T144023Z`, recommending in place). The ruling was REJECTED in place, APPROVED a new run directory. The first draft, an edit to the old `migrate_soft.py`, was reverted before any commit.

- `carry_definitions.py` imports the old run's `migrate_soft.py` unchanged. Its `rewrite` is the old rewrite followed by rule 7, which cuts each passage from the pinned body by its first and last words. No text comes from the audit. Run, it writes the probe, `answers/search.json` (7.7 s; no pair without a situation; no limit), `answers/meaning-ids.json` and `changed_units.json`. It does this through `migrate_soft.main` with that module's output paths pointed here.
- `point_status.py` runs the old run's `measure.py` with only the `point-status-c9` steps (after, strict; 36.7 s and 32.6 s, under systemd MemoryMax=16G). It was re-run at commit `c8e097e9e3` and wrote byte-identical outputs (`git status` showed only `measurements.json`).
- The whole-translation steps were not run (L70). SUMMARY.md says they remain measured on the old probe, environment `5164a9a5…`; the new one is `8c2e30a8…`.
- The carried text keeps the source's words, punctuation and links. It drops Markdown list marks and `**` bold marks, as the audit's quotes did. Passages are joined by one space and appended after the old description. The `claude_instance` legend keeps its sentence "The source does not say whether this is a model, a version or a running instance". The audit's planner note suggested replacing it. Appending is the conservative choice: nothing is removed, and the source passage does not name a model, a version or an instance either.

## 2. Derived files

Regenerated only with the run's own tools (above): probe, search, candidate ids, changed units and point status, plus `measurements.json`. `conformance/english-lean/corpus-seal.json` names no file of this item: its five `claude-constitution-pilot` entries are 2026-09 pilot translations outside the repository. `tools/regen_generated.py --check` exits 0. Its only warning is the code map, stale already on main ("regenerated on merge"). A `--write` rewrote 12 code-map files, mostly for drift already on main and for the test partitions the new test file shifts, so I reverted it and left it to the merge train. The two new code-map lines are the scripts' first docstring sentences. `tools/history_tests.py --check` exits 0, because the condition test loads no git-calling code: `point_status.py` holds the `measure.py` import. The new JSON files are classified by `usecases/*-pilot/run-*/*.json` as pilot-run artefacts (`difffuzz_corpus.excluded`).

## 3. Tests

- Condition test `tests/test_defs_repair_claude_constitution_pilot_1119.py`, 37 tests. On main's tree (the new run directory moved aside) none passes: "4 failed, 33 errors" (`/tmp/defs1119/t-main.log`). Its first draft read main's own probe and failed there too, "16 failed, 15 passed", each at the legend assertion (`/tmp/defs1119/t1.log`). With the change: "37 passed in 19.59s" (`/tmp/defs1119/t5.log`).
- Selected run: `mac-pytest.sh --select -- --base f5553bc894 --run` gave 59/649 units, exit 0, 0 failed ids, 1530 s, HEAD `0b0c6f23` (clean). It included the condition test, `test_difffuzz`, `test_code_map` and `test_history_tests`.
- `tests/test_sc9_migrate.py` is unchanged and not selected, since the old run did not change. Run once: "14 passed in 24.56s".
- Full gate: left to the chain (task rule).

## 4. Seeded bugs (Python; each planted, the file then restored from git, tree clean)

| # | file | bug | failing test |
|---|---|---|---|
| S1 | run-20261119-defs-carry/carry_definitions.py | `passage` keeps one character less | test_the_committed_probe_is_the_drivers_rewrite |
| S2 | same | a start that occurs twice is accepted | test_rule_7_refuses_a_passage_it_cannot_cut |
| S3 | same | bold marks kept when the body is read | test_the_committed_probe_is_the_drivers_rewrite |
| S4 | same | the description is replaced, not appended | test_the_committed_probe_is_the_drivers_rewrite |
| S5 | same | a legend the vocabulary lacks is not refused | test_rule_7_refuses_a_passage_it_cannot_cut |
| S6 | run-20261119-defs-carry/probe-translation.probe.md | one carried sentence taken out of `compliance_unsafe` | test_the_legend_carries_…[defs-claude-constitution-pilot-11-1119], test_the_legends_only_grow, test_only_the_rows_legends_and_the_identities_change, test_the_committed_probe_is_the_drivers_rewrite |
| S7 | run-20261119-defs-carry/answers/after/point-status-c9.out | one UNDECIDED saved as SETTLED no | test_c9_point_status_is_the_old_runs_but_for_identities[after] |

Commands: `/tmp/defs1119/seed.py` (S1-S6) and an inline edit (S7); results quoted from their output. Lean and Rust: no product code changed, so there are no seeded bugs there.

## 5. Trust

`tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0; PASS". Light lane printed NOT: the tool-written answers count as changed lines. `trust_mutants.py --plan` gives `{"definitions": 0, "mutants": 0}`, so no sweep was run; there is nothing to mutate. No FOLLOW-UPS.md row, since R16 does not apply.

## 6. Pilot bytes expected to move (estimate; nothing is claimed before a pilot audit)

9,913 bytes of source text are added to 15 legends. If the next read uses the new probe, the 15 (rule, term) gaps should go from NOT CARRIED, FRAGMENT or ELSEWHERE to CARRIED: 47 NOT CARRIED pairs and 2 PARTIAL pairs, per the audit's counts.

## Notes for the DRI

- Spec re-read: deliverable 0 against the task text, METHOD.md amendments 3 (full span), 7 and 8; the DELTA row against DRI-RULINGS.md R3 (information added, nothing removed or renamed; a test checks the field against the true source text). The carrier follows decision item 1, word by word: a new directory, a driver importing the old rewrite unchanged, point status re-measured, SUMMARY's three statements, and R3.
- `measure.py` is reused by pointing its module globals (`ANSWERS`, `migrate_soft.PROBE`) at the new run. This keeps one owner of each step, and the old run's files do not change.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean route or relayed answer is added or changed.
2. PASS: deliverables 0-3 are in sections 0-3. The diff has no Python copy of a Lean decision, no permanent report test and no shared file (overlap scan of every in-flight branch: empty). Test: test_defs_repair_claude_constitution_pilot_1119.
3. PASS: S1-S7 each fail a named test (section 4).
4. N.A.: no Python, Lean or Rust path changes. Point status is the same on both probes, hashes masked (test_c9_point_status_is_the_old_runs_but_for_identities).
5. N.A.: no Lean answer field is read by new code. The saved C9 records are bound to the new probe's requests (test_c9_point_status_records_are_bound_to_the_carried_probe).
6. PASS: main has not moved (`git log HEAD..main`: 0). The selected run was on clean HEAD `0b0c6f23`. Only this report was committed after it.
7. PASS: the DELTA row cites R3, as decision item 1 says. Trust is +0 (trust_map --check).
8. PASS: one DELTA row; the changes it lists are shown by test_only_the_rows_legends_and_the_identities_change.
9. PASS: select_tests picks the condition test (59/649 units, not all). Seeding S1-S7 broke that selected test.
10. N.A.: no Lean statement or proof.
11. N.A.: no budget or limit is added. The scripts ran under MemoryMax=16G (measure.py) or `ulimit -v 16G` (the driver).
12. N.A.: no product path changes. The search took 7.7 s (old run 5.9 s), and point status 36.7 and 32.6 s (old run 25.2 and 23.3 s) on a host at load 91.
13. N.A.: no test removed or renamed.
14. PASS: each check is tested both ways. On the accepting side, 37 pass on the carried probe. On the refusing side, none passes on main's tree, S1-S7 fail, and test_rule_7_refuses_a_passage_it_cannot_cut covers a missing start, a repeated start, a missing end and an unknown legend. Every claim here cites its command or log.
15. PASS: universal words ("every", "none", "byte-identical") are each backed by cmp.py, the masked comparison test, or `git diff --stat main -- run-20261104T0716Z` (empty). No deferred deliverable. Every new check has a seeded bug. No limits are added.
