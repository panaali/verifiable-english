# jt-3p report: phrase rows in the evaluative catalogue, the "good judgment" row, and the decider rename

Status: built. No DRI signature is reserved: every DELTA row is signed (DRI 2026-10-31 item 3; DRI 2026-11-02 items 1-4; R3; R16).
A catalogue row's word is now a phrase, `undeclaredEvaluative_iff` reads `row.word <:+: ws`, and the catalogue has "good judgment".
The decider token is now `unstated`, and `JudgmentDecider` refuses `unresolved_decider` (syn2code-judgment-terms-1).
Open: FOLLOW-UP jt-3pb (the rename in pc-1's new chain files, after pc-1 lands). Bytes: 0 (a review list).
The chain runs the full gate on the final HEAD. The selected tests pass after the two fixes (see "Tests").

Plan: docs/spec/judgment-terms.md 7 (`EvaluativeRow`, `otherSenses`), 8.4 and 11.7; docs/spec/judgment-terms-PLAN.md
"JT-3"; docs/judgment-terms/jt-3a/REPORT.md. Plan edits: design/syn2-judgment-terms at 4d1da4e6f (section 12) and
`manage-agents/debates/plan-synthesis-2/edits-judgment-terms.md`. **This item implements edit 1** (C2: the decider token
`unstated`; plan row `syn2code-judgment-terms-1`) in JT-1's code, tests, data, the item-1 spec and `lean/JUDGMENTS.md`.
Edit 3 (no sense-tied rows) still holds: the new row carries no sense of its own. Edits 2 and 4 concern JT-4.

## DRI decisions

- reviews/dri-decisions-20261031-jt-3a.md item 3 (before this item): signs the phrase-row statement change and states its
  conditions (all met, see "Conditions").
- reviews/dri-decisions-20261102-jt-3p.md, asked through msg.sh at the start and while building:
  1. SIGNED: the rename's verdict change (`unstated` passes check 5, `unresolved_decider` is refused).
  2. SIGNED: `faultOf_none_iff`'s literal `"unstated"` becomes `"unresolved_decider"`, in this item, not jt-3pb.
  3. SIGNED: the English `actions_version` raise 36 -> 37 (base spec 2.12).
  4. SIGNED: `matches_iff` (jt-3a's helper lemma) changes the same way as `undeclaredEvaluative_iff`. The condition now
     reads three changed statements, one added, 0 removed.

## Plan rows

| Row | Delivered | Where | Checked by |
|---|---|---|---|
| (1) `EvaluativeRow.word : List String`; `matches` uses `hasPhrase row.word ws`; jt-3a's rows become one-element lists with `otherSenses` unchanged; `undeclaredEvaluative_iff` restated and proved | yes | `lean/VE/Judgments/Undeclared.lean`, `lean/VE/EnglishGrammar/Evaluative.lean` | `undeclaredEvaluative_iff`, `matches_iff`, `singleton_infix_iff` (proved); the #guards in `lean/VE/Judgments/Examples.lean` "Phrase rows" |
| (2) The "good judgment" row, in spec 7's exclusion style | yes: `⟨["good", "judgment"], []⟩`. No phrase in the pilots gives "good judgment" another sense, so it lists no other senses (the docstring says so) | `lean/VE/EnglishGrammar/Evaluative.lean` | `lean/VE/EnglishGrammar/Examples.lean`:200-227; `tests/test_judgments_undeclared.py::test_the_good_judgment_phrase_row_is_listed_only_where_written_in_order` |
| (3) The DRI's conditions as #guards or tests that stay selected | yes | see "Conditions" | |
| (4) syn2code-judgment-terms-1: rename `unresolved_decider` to `unstated` in JT-1's code, tests, data, the item-1 spec and `lean/JUDGMENTS.md`; a test that the old token is refused | yes, except pc-1's files (jt-3pb) | `lean/VE/Judgments/Decl.lean` (check 5 and `faultOf_none_iff`), `lean/VE/Judgments/Examples.lean`, `tests/test_judgments_document.py`, `tests/data/relay-gate-cases.jsonl` (the 2 recorded `judgments@0` requests, 5 tokens), `docs/spec/judgment-terms.md` (2.2, 8.2, 9.1, 11), `lean/JUDGMENTS.md` | J-η (old token refused) and J-eta-unstated (new token admitted) in `tests/test_judgments_document.py::test_admission_of_each_record_in_record_order`; `lean/VE/Judgments/Examples.lean`:131, :133 |
| Not this item: reader-facing or authoring wording (jt-3), `lean/VE/Service/Document.lean` (pc-1 in flight) | not touched | | |

### Conditions (DRI 2026-10-31 item 3; DRI 2026-11-02 items 1-4)

- `[w] <:+: ws ↔ w ∈ ws`: theorem `VE.Judgments.singleton_infix_iff` (`lean/VE/Judgments/Undeclared.lean`) and the
  #guard at `lean/VE/Judgments/Examples.lean`:388.
- Every jt-3a 11.7 fixture gives the same list after the change: a #guard (Examples.lean:406) compares
  `undeclaredEvaluative rows117` with `jt3aList`, which writes out jt-3a's word rows and word match on their own. It runs
  over `preds117`, `regulated117` and `preds117x` with `J` = `[]`, `[arbitrary]` and `[arbitrary, reasonable_grounds]`. The
  four 11.7 #guards (Examples.lean:361-366) keep their exact values.
- `good_judgment` is listed when unbound and not listed when in `J`, and `good_conduct` is not listed: Examples.lean:425-427
  (an inline row), the catalogue's row at `lean/VE/EnglishGrammar/Examples.lean`:227, and through the service in
  `tests/test_judgments_undeclared.py::test_the_good_judgment_phrase_row_is_listed_only_where_written_in_order[unbound]`
  and `[bound]`. These test runs pass (see "Tests").
- Seeded bug "match the phrase's first word only": `good_conduct` is listed and the fixture fails (S1 below).
- The rename: the J-η test (old token refused) and the test that `unstated` passes check 5 (J-eta-unstated; #guard at
  Examples.lean:133) are both selected.
- Statements: `git diff 3b4e471f8 -- lean/statements.txt` shows three changed statements, one added and 0 removed. The
  one-term diffs:
  - `faultOf_none_iff`: `… ∧ r.fst.decidedBy ≠ "unstated"` → `… ∧ r.fst.decidedBy ≠ "unresolved_decider"`
  - `matches_iff`: `row.matches ws = true ↔ row.word ∈ ws ∧ …` → `… ↔ row.word <:+: ws ∧ …`
  - `undeclaredEvaluative_iff`: `… ∃ row, row ∈ rows ∧ row.word ∈ ws ∧ …` → `… ∧ row.word <:+: ws ∧ …`
  - added: `singleton_infix_iff : ∀ (w : String) (ws : List String), [w] <:+: ws ↔ w ∈ ws`

  `uv run python tools/lean_statements.py --check` printed "added: 0 removed: 0 changed: 0 PASS" against the
  regenerated inventory (the committed `lean/statements.txt` matches the build).
- `actions_version`: `uv run python tools/english_grammar_gen.py --check` passes (exit 0, no output); the version is 37.
  These goldens were re-recorded by their own tools:
  - `conformance/english-lean/s3-fixture-comparison.json`, by `python -m conformance.english_lean_s3_compare`. The diff
    is 170 × `actions_version` plus Lark's expected-token order in two messages, as in jt-3a's re-record.
  - 17 ask fixtures, by `tools/ask_fixtures.py --write <ids>`. Only the version and the recorded seconds change.

  The 12 pins in `lean/VE/Senses/RunExamples.lean` have no generator (`tools/regen_generated.py --owner` prints `-`). I
  computed them with Lean's `#eval` on a temporary copy, which printed old hash, new hash, and whether the answer with
  "37" set back to "36" hashes to the old value. The result was 12 changed and all `true true`, and 20 unchanged.

## Deviations, recorded here only

- Spec 7's text is updated to the signed statement (the code block, a paragraph, and an 11.7 row). The change log has a
  jt-3p row. The rename also updates 2.2, 8.2's table, 9.1's record column and 11's fixtures. 0.2's phase-1 evidence
  (line 104, "all `unstated`") is a measurement and stays as it is.
- `lean/VE/EnglishGrammar/Examples.lean` was not in the task's file list. It holds jt-3a's catalogue #guards, which pinned
  15 rows and `good_judgment` as not listed, so it had to change. The catalogue-based "good judgment" fixtures live there
  because `VE.Judgments.Examples` (layer 2) may not import english-lean (layer 3). The first selected run failed
  `tools/check_lean_imports.py` on that import, and the fixtures were moved.
- `lean/VE/Senses/RunExamples.lean` (sn-b6's pins) changes because of the version raise, as it did in jt-3a.
- Not renamed, because they are not JT-1 and are not read under `judgments@0`: reports' `assessments[*].decided_by`
  (`tests/test_reports*.py`, `tests/reports_fault_corpus.py`, `tests/data/route-cases.jsonl`), attribution
  (`lean/VE/Attribution/Content.lean`, `docs/spec/attribution*.md`), and the pilot and perf documents whose open-term
  records say `unresolved_decider` without the profile (`docs/perf/inputs/*`, `tests/data/tarch-b8/*`,
  `tests/data/scope/*`, `tests/data/readings_s2/*`, `tests/data/et7/*`). Edit 1 gives attitudes and attribution their own
  renames; none of these is refused by `judgments@0`.

## Overlap with branches in flight

Checked with `git diff --name-only $(git merge-base main <b>) <b>` for every `feature/*`, `lean-first/*`, `infra/*` and
`foundation/*` branch ahead of main:
- `feature/pc-1`: `tests/test_judgments_document.py`. pc-1's only hunk there is at line 346, and this item changes lines
  72, 172-173 and 178. pc-1's new files (`lean/VE/Judgments/Chain.lean`, `ChainExamples.lean`,
  `tests/test_judgments_chain.py`) write `decided_by: "unresolved_decider"` in judgment records, and after both merge,
  check 5 refuses those records. They are left untouched here: FOLLOW-UP jt-3pb renames them once pc-1 lands. The
  DRI's item 2 says jt-3pb needs no new ruling for the token.
- `feature/sn-b6b`: `lean/VE/Senses/RunExamples.lean`. sn-b6b re-pins 8 of the same lines, so the second branch to merge
  recomputes those pins under the version it finds (the same `#eval` check).
- `lean-first/b14b-evidence` (2026-10-12, older than jt-3a) lists the judgment files, but it is not a live branch for
  this work.

## Seeded bugs (`mutants.json`; Lean is the only product language changed: no Python or Rust product file)

| Id | File | Mutation | Fails |
|---|---|---|---|
| S1 | `lean/VE/Judgments/Undeclared.lean` | `matches` reads the phrase's first word only (the DRI's seeded bug) | Judgments/Examples.lean:425-427 (`good_conduct` listed), EnglishGrammar/Examples.lean:212, :227 |
| S2 | `lean/VE/Judgments/Undeclared.lean` | `otherSenses` ignored (jt-3a's seeded bug) | Judgments/Examples.lean:361, 362, 365, 372, 378, 406, 409; EnglishGrammar/Examples.lean:206, 212 |
| S3 | `lean/VE/Judgments/Undeclared.lean` | a phrase matches in any order (`row.word.all (ws.contains ·)`) | Judgments/Examples.lean:425-426 (`judgment_good` listed), EnglishGrammar/Examples.lean:212, 227 |
| S4 | `lean/VE/Judgments/Decl.lean` | check 5 refuses `unstated` again | Judgments/Examples.lean:131 (J-η), 133, and the admitted fixtures 117, 134, 136, 138 |
| S5 | `lean/VE/EnglishGrammar/Evaluative.lean` | the "good judgment" row removed | EnglishGrammar/Examples.lean:200, 204, 212, 227 |

Each was applied to the committed file, built with `lake build VE.Judgments.Examples VE.EnglishGrammar.Examples`, and
restored. For S1-S4 the proofs that read the mutated definition were replaced by `sorry` during the run, so the #guards
are shown to fail, not only the proofs.

## Trust (R16)

`uv run python tools/trust_map.py --check` against `3b4e471f8c29`: K +0, S +4, D +0, G +0, unclassified +0, trusted +4:
- `lean/VE/Judgments/Undeclared.lean`: S +1
- `lean/VE/EnglishGrammar/Evaluative.lean`: S +3

The new fixtures (`jt3aList`, `preds117x`, `goodPreds`) are T in `tools/trust-classes.json`. The first selected run's
`test_committed_trust_table_covers_every_declaration` found them unclassified (23 lines).

The allowance is recorded with `--signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), jt-3p, 2026-11-02"`.
`FOLLOW-UPS.md` has a "## jt-3p" row that asks for the ties pass.

Trust mutants (`docs/judgment-terms/jt-3p/trust-mutants.json`, run by `mac-pytest.sh --trustmut`, last full run on
bb0adc081, then rescored after an allow-only edit, exit 0):
- 85 killed, 0 survivors, 0 unknown, 4 invalid, 6 allowed.
- The allowed mutants are `evaluativeRows` list cuts that do not elaborate (`trust-mutants-allow.json`, one reason per
  operator).
- Earlier full runs found 36 and then 4 survivors in fixture data. Each was killed by a new fixture:
  - `jt3aList` now has its own literal rows.
  - `preds117x` exercises every row's word with and without each other sense.
  - Two contrast #guards show each negative example holds the row's word.

## Size

Hand-written lines changed (`git diff --numstat $(git merge-base HEAD main)`, generated and tool-recorded files left out):
about 160 in code, fixtures, tests and the spec, plus this report, DELTA and mutants.json. That is under the ~600 limit.

## Tests

- While iterating: `uv run pytest -q tests/test_judgments_document.py tests/test_judgments_undeclared.py
  tests/test_judgments_answer.py`, 102 passed; `lake build` of the edited modules.
- After the code was done, regen once: `uv run python tools/regen_generated.py --write`, rc=0. It ran again after each
  later Lean fix. Also `lake build` (1230 jobs, ok), `python3 lean/audit.py` (PASS, 723 files, 8011 theorems),
  `python3 tools/check_lean_imports.py` (kept), and `uv run python tools/gate_collection.py --check --prebuilt`
  (3 added, 0 removed, 0 refused/stale/malformed).
- Selected tests, once: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, 425 of 527 units in 6
  cloud shards. Shards 2, 3, 5 and 6 passed. Shard 4 failed
  `tests/test_consolidation_tools.py::test_committed_trust_table_covers_every_declaration` (unclassified fixtures) and
  `tests/test_precommit_hook.py::test_large_staged_change_passes` (the outward import). Shard 1 stopped at
  `check_lean_imports.py` on the same import, before its 79 units ran. Both causes are fixed (bb0adc081).
- Rerun: shard 1's 79 units, the two failed ids, and `tests/test_judgments_{undeclared,document,exercised}.py`, through
  `mac-pytest.sh -- <ids>`. Result: 3155 passed, 6 skipped (missing optional modules `llguidance` and `xgrammar`, the FOLIO corpus not downloaded, three Rust-scope skips), exit 0, at 12a2e263. It ran on the VM because no Mac slot was free (log summary: "ran LOCALLY (VM) … exit=0"). After 12a2e263 only this report changed.
- Not run: the full gate (the chain runs it on the final HEAD). No whole-UDHR or whole-constitution run (L70).

Known red on main (`main-known-red.txt`): none of the failures above is listed there. Both were caused by this branch
and are fixed.

## Spec re-read

- `undeclaredEvaluative_iff` against reviews/dri-decisions-20261031-jt-3a.md item 3 ("reads `row.word <:+: ws` where it
  now reads `row.word ∈ ws`"): matches, with no other change to the statement.
- `faultOf_none_iff` and check 5 against the plan at 4d1da4e6f, 2.1 check 5 ("`decided_by` is `unresolved_decider`") and
  3.1 ("not `unresolved_decider`"): match.
- J-η against the plan at 4d1da4e6f line 399 ("J-α's record with `decided_by: "unresolved_decider"`" → `JudgmentDecider:
  arbitrary`): matches (Examples.lean:131; the test's J-eta).
- The good-judgment row against plan 2.4's catalogue row ("good judgment"; no sense-tied rows, edit 3): matches.
- DELTA rows against DRI 2026-11-02 items 1-4: each Ruling cell is the decision's text.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A. (no response shape or relay changed; `undeclared_evaluative`'s schema and
   binding are jt-3a's, and its relay is exercised by `tests/test_judgments_undeclared.py`, including the new good-judgment test).
2. Every deliverable built: PASS. Plan rows table above; the rename's remaining files are FOLLOW-UP jt-3pb (pc-1 in
   flight, as the task directs); overlap section above.
3. Tests can fail: PASS. `mutants.json` S1-S5 (Lean, the only product language changed); trust mutants 0 survivors
   (`trust-mutants.json`).
4. Agreement with the base: PASS. `jt3aList` #guard at Judgments/Examples.lean:406 (the base rule against the new one on
   every 11.7 fixture), J-eta and J-eta-unstated (both directions of the rename).
5. R8 binding: PASS. No new field; `test_the_good_judgment_phrase_row_is_listed_only_where_written_in_order` checks
   `relayed(case, row)` for the new matches.
6. Gate evidence matches the final HEAD: PASS. The chain runs the gate on the final HEAD; the trust mutants JSON is
   from the code at bb0adc081 (rescored at 34581cf7 after an allow-only edit).
7. No unsigned item: PASS. `DELTA.md`, every Ruling cell cites a DRI decision file or R3/R16.
8. Every user-visible change in DELTA: PASS. Theorem rows, the good-judgment matches, the rename, `actions_version`,
   and trust.
9. Test selection: PASS. `tools/select_tests.py --base …` selected 425 of 527 units, including
   `tests/test_judgments_{undeclared,document,exercised}.py`, `tests/test_ask_fixtures.py`, `tests/test_english_e2_report.py`
   and `tests/test_senses_*`; the seeded import fault was caught by the selected shard 1 command.
10. Statements say what is claimed: PASS. S1-S4 run with the proofs stubbed and also break the proofs without the
    stub; the statement diff is above.
11. Budgets and deadlines: N.A. (no operation, limit or deadline changed; the report reads each predicate once, as jt-3a).
12. CPU or memory: N.A. (`hasPhrase` on a two-word phrase in place of `contains`; no new traversal).
13. Test-removed trailers: PASS. `tools/gate_collection.py --check --prebuilt`: 0 removed, 0 refused, 0 stale,
    0 malformed (no test removed).
14. Both directions, cited evidence, spec re-read: PASS. Old token refused and new admitted; listed when unbound and
    not when bound; phrase in order and not out of order, nor when only half is present; "Spec re-read" above.
