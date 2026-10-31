# sc-5rd: three of SC-5's four `JsonWF` statements proved, discharged on the route

**Status:** built, ready for review. No DRI signature is needed.
**Commits:** the final commit is the one that adds this report (`git log -1 -- docs/scope/sc-5rd/REPORT.md`); main was merged at 56cc350e5.
**What changed:** these are proofs only. `governSets_preserves`, `governSets_strings` and `governSets_readings_refused` are proved as the stub writes them. `decodeBlock_sets` gives all three on the route from sc-1af's boundary check; it also proves the payloads' `JsonWF`. No answer changes; DELTA is none.
**Open:** `governSets_every_choice` is false as written (counterexample below). The DRI signed fix (b) and moved it, unproved here, to sc-5rdb.
**Next:** `FOLLOW-UP: sc-5rdb governSets_every_choice with distinct unit ids and decodeBlock's repeated-id refusal`.

## Plan rows (task deliverables) and where each is delivered

| Task row | Delivered | Commit | Evidence |
|---|---|---|---|
| (1) the four `Pinned.JsonWF` statements proved in `ReadingsTheorems.lean` | **3 of 4.** `governSets_preserves` (`ReadingsTheorems.lean:114`), `governSets_strings` (`:202`) and `governSets_readings_refused` (`:90`) are proved. Their lemmas are in the new `ReadingsLemmas.lean` (296 lines: the theorems file would otherwise pass ~400 lines). The `atChoiceOn` and `setObjVal!` lookup lemmas are `atChoiceOn_units`, `atChoiceOn_sets`, `getD_set2` and `jsonWF_atChoiceOn`. **`governSets_every_choice` is not proved:** see "The fourth statement". | a7c34faa2 | `lake build` passes (1185 jobs, after the merge of main) |
| (2) the route corollary beside `decodeBlock_jsonWF` | `decodeBlock_sets` (`ScopeAdmission.lean:226`): when `decodeBlock` succeeds, the three statements' conclusions hold for the decoded document, with no `JsonWF` hypothesis. The payloads' `JsonWF` comes from `decodeBlock_payloads` (`:211`), which reads `decodeParts`/`decodeGovernor`/`decodeEffect` and finds every payload is a member of the scope block. `every_choice`'s corollary goes to sc-5rdb. | f405cfad5 | build; seeded bugs M3 and M7 |
| (3) statements dumped, no new axioms | `lean/statements.txt` and `lean/axioms.txt` are regenerated (`regen_generated.py --write`). `axioms.txt` only gains per-theorem rows, and each new theorem shows `[propext, Classical.choice, Quot.sound]` (e.g. `axioms.txt` rows for `governSets_preserves`, `governSets_strings`, `governSets_readings_refused`, `decodeBlock_sets`). | e1dad03de, 3cf2833a6 | `python3 lean/audit.py`: `PASS: 687 source files; 7769 named theorem declarations audited ... only the declared standard axiom allowlist.` |
| (4) fixtures: SR-1 and SR-1-pc on the proved statements, a refusing case for `governSets_readings_refused` | SR-1 and SR-u: `preserved` computes `governSets_preserves`' conclusion. It holds on the answer, and fails once a member it must keep is changed: the title, a unit's `kind`, a set's `id`, a reading's `id` (`ReadingsExamples.lean`, `preservesOn` guards). `governSets_readings_refused`'s hypotheses and conclusion are checked on both sides of `hn`: refused when u0165.s03's part is written, so its set is not governed; refused for a set on the governor's own unit; admitted for SR-1, where the set is governed. **SR-1-pc** is `every_choice`'s fixture (spec 11.6), so it moves with it; sc-5rb's `perChoice` guard on SR-1 stays as it is. | f21969fa8 | the guards build |
| (5) seeded bugs: `atChoiceOn` key, `governSetsWith` drops a set, the check removed from `decodeBlock` | M1, M2 and M3, plus five more (below). | 2ecad4247 | `docs/scope/sc-5rd/mutants.json` |
| The stub test, extended | `test_each_statement_sc5rb_proves_is_the_stubs_text`: `LEFT = {"governSets_every_choice"}`. The three proved statements equal the stub's text after whitespace normalisation. | f21969fa8 | probe below |

Files outside the task's list, each a consequence of the new module or of the newly named definitions:
- `lean/VE.lean`: one import.
- `tools/trust-classes.json`: the module entry, and the six new example helpers as T.
- `ve/assurance-manifest.json`: two `other_json` reasons, needed by `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`.
- `tests/test_scope_lean.py`: twelve scope definitions that the new lemma statements now name leave its "not yet stated" lists (`test_every_trusted_scope_definition_is_used_by_a_theorem`).

No protected file was edited: `Document.lean`, `Theorems.lean`, `Examples.lean`, `Govern.lean` and `Effects.lean` are untouched (`git diff --name-only main...HEAD`).

## The fourth statement (`governSets_every_choice`) and the DRI's rulings

The statement as written is false. The evidence is `docs/scope/sc-5rd/every-choice-counterexample.md` and `EveryChoiceCounterexample.lean`. The `#guard`s are checked with `lake env lean ../docs/scope/sc-5rd/EveryChoiceCounterexample.lean` from `lean/` (rc 0, 0 errors). They stay out of `lake build` because evaluating the unit `5` makes `setObjVal!` panic and print a trace, though it answers `null`.

- **The counterexample.** `{"units": [{"id": "a"}, 5, {}], ...}`: two units read the id `""`, and `assemble` reads the first one's content. The route does not exclude it.
- **The ruling.** The DRI (reviews/dri-decisions-20261031-sc-5rd.md item 1, SIGNED) chose fix (b): add `(hd : (unitIds D.doc).Nodup)`. Item 2 adds a proved `firstDup` refusal in `decodeBlock`.
- **The split.** The addendum, item 3 (SIGNED), moves items 1 and 2 to **sc-5rdb**: this item would otherwise reach about 1,000 hand-written lines. So `governSets_every_choice` stays in the stub, the spec and the stub test exactly as on main, and sc-5rd has no DELTA row.
- **Handoff.** `/home/seyran/code/manage-agents/scratch/sc-5rdb/` holds:
  - the checked tree lemmas `insert_insert` and `insert_swap`: structural `Json` equality after `setObjVal!` twice on a balanced tree, which `every_choice` needs;
  - the proof plan under `hd`, with what `governSets_ok` and `assemble_ok` must add.

Two points for the spec, with no statement changed:
- Spec 11.3 says `governSets_strings` needs the payloads' `JsonWF`. The proof does not use it, because `govern_strings` (sc-1ae) holds without it. The premise is kept as written, and the theorem carries `set_option linter.unusedVariables false`. The route corollary still proves the premise (`decodeBlock_payloads`), as task row (2) asks.
- `edits-scope.md` (plan synthesis round 2): none of its seven edits or DEC 10/16 concerns these statements. This item implements none of them.

## Seeded bugs (`docs/scope/sc-5rd/mutants.json`; each applied alone, built, restored)

For each mutant: `lake build VE.Scope.ReadingsExamples VE.Service.ScopeAdmission` from `lean/`, rc 1. `git status` was clean after each restore.

| Id | File | Mutation | What fails |
|---|---|---|---|
| M1 | lean/VE/Scope/Readings.lean | `atChoiceOn` writes the reading under `"contents"` | `ReadingsLemmas.lean:68` (`unitsOf_atChoiceOn`) and 3 more; 14 `#guard`s in `ReadingsExamples.lean` (SR-1 at 50, 60, 62, …) |
| M2 | lean/VE/Scope/Readings.lean | `governSetsWith`'s answer drops its first reading set | `ReadingsLemmas.lean:192` (`governSets_ok`, read by `governSets_preserves`); `ReadingsExamples.lean:202-206` (`preservesOn`) and SR-1's guards |
| M3 | lean/VE/Scope/Wire.lean | `decodeBlock` without the `illFormed` (`jsonWF?`) check | `ScopeAdmission.lean:97` (`decodeBlock_ok`) and 2 more: the corollary chain no longer builds |
| M4 | lean/VE/Scope/Readings.lean | `readingIn` answers `.str "fresh"` | `ReadingsLemmas.lean:251` (`assemble_ok`, read by `governSets_strings`); SR-1's guards |
| M5 | lean/VE/Scope/Readings.lean | under a choice every reading set leaves | `ReadingsLemmas.lean:75, 84` (`atChoiceOn_sets`, `atChoiceOn_units`); `ReadingsExamples.lean:217` (the refusal on the governor's own unit), `:94`, `:157` |
| M6 | lean/VE/Scope/ReadingsExamples.lean | `preserved` loses its top-member conjunct | `ReadingsExamples.lean:202-203` |
| M7 | lean/VE/Service/ScopeAdmission.lean | `decodeBlock_sets` takes the block's `JsonWF` instead of the document's | `ScopeAdmission.lean:243-245` |
| M8 | lean/VE/Scope/ReadingsLemmas.lean | `atChoiceOn_units` claims every member is kept, `content` included | `ReadingsLemmas.lean:100, 106` |

Python product code is unchanged (only tests and JSON tables), and so is Rust: no seeded bug is needed there. The stub test can fail. A probe ran the test function on mutated copies of `ReadingsTheorems.lean`, without lake:

    {'premise dropped': 'FAILED (mutant caught)', 'premise added': 'FAILED (mutant caught)',
     'every_choice proved': 'FAILED (mutant caught)', 'unchanged': 'PASSED'}

## Trust, size, pilot bytes

- **Trust.** `uv run python tools/trust_map.py --check`: `against 56cc350e586c ... PASS: K, S and untied [V] within 56cc350e586c` (before the merge: `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`). No trusted definition is added: the new lines are theorems and T-class example helpers. So there is no R16 growth, no allowance, no FOLLOW-UPS row, and `trust_mutants` was not run (no trusted Lean changed).
- **Size** (`git diff --numstat $(git merge-base HEAD main)`, generated files excluded):

  | Part | Lines |
  |---|---|
  | Lean proofs (`ReadingsLemmas.lean` 296, `ReadingsTheorems.lean` +181/−5, `ScopeAdmission.lean` +128, `VE.lean` +1) | 611 |
  | fixtures (`ReadingsExamples.lean`) | +45 |
  | tests (`test_scope_lean.py` +8/−9, `test_scope_sc5r_stub.py` +4/−3) | 24 |
  | tables (`trust-classes.json` +7, `assurance-manifest.json` +2) | 9 |
  | evidence (counterexample md and lean, `mutants.json`) | 68 |
  | this report | — |

  That is over the ~600 guide even after the DRI's split. The proofs were measured as ~440 in scratch; the route corollary and the payload lemmas add ~130.
- **Pilot bytes:** 0 (proofs only; no answer changes). Nothing is claimed before a pilot audit.

## Commands run (final code; main merged at a43528360)

| Command | Result |
|---|---|
| `lake build` | `Build completed successfully (1185 jobs)`, after the merge |
| `uv run python tools/regen_generated.py --write` | `wrote 34 entries`, after the merge, committed 3cf2833a6 |
| `uv run python tools/regen_generated.py --check` | rc 0, `checked 34 entries`, before the merge; the post-merge `--write` regenerated every entry |
| `python3 lean/audit.py` | PASS (above) |
| `uv run python tools/repo_map.py --check` | `PASS: 40 modes, each with its schema file` |
| `mac-pytest.sh --select -- --base 32b03d5c0 --run` (HEAD 2ecad424 plus fixes) | Actions gave no result from 1 of 2 shards, so it fell back to the Mac path (`exit=1; failed/error ids=1`): `test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`. The finished Actions shard had failed `test_scope_lean.py::test_every_trusted_scope_definition_is_used_by_a_theorem` and `::test_the_scope_files_are_classified`. All three were fixed (a289dd1dc). 46 slow files were deferred to the chain gate by the selector. |
| `mac-pytest.sh -- <the 3 failed ids>` | `3 passed`, HEAD a289dd1d (clean) |
| `mac-pytest.sh -- tests/test_scope_sc5r_stub.py tests/test_scope_lean.py tests/test_assurance_manifest.py tests/test_scope_readings_document.py tests/test_scope_document.py tests/test_scope_answer.py tests/test_lean_statements_parts.py tests/test_trust_budget.py tests/test_code_map.py tests/test_repo_map.py` | `319 passed`, HEAD 3cf2833a (clean, after the merge) |

What was not run: the full gate (the chain runs it on the final HEAD), and `trust_mutants` (no trusted Lean changed). After 3cf2833a only JSON key order (90b52b77b, 81a29289d: semantically equal to the tested files, asserted) and this report changed.

## Spec re-read

- `governSets_preserves`, against `docs/spec/scope/SpecStubs_sc5r.lean:181-192` and the spec 11.3 table row at `docs/spec/scope.md:2105`: equal after whitespace normalisation (stub test).
- `governSets_strings`, against `SpecStubs_sc5r.lean:200-203` and `scope.md:2107`, and the premise sentence at `scope.md:2097` (see above).
- `governSets_readings_refused`, against `SpecStubs_sc5r.lean:229-232` and `scope.md:2113`: "owns or reaches" is both `u = g.unit ∨ u ∈ us`, with fixtures on each.
- The route corollary, against reviews/dri-decisions-20261028-sc-1af.md item 1: "SC-1b's and later end-to-end statements then discharge `JsonWF` from the check's success and still may not take `JsonWF` as a bare hypothesis". `decodeBlock_sets` takes only `decodeBlock … = .ok D`.

## Self-review against BUILDER-CHECKLIST

1. Lean answer typed and contained: N.A. No response, schema or relay changes (proofs only).
2. Every deliverable built: PASS. See the plan-rows table. Row (1) is 3 of 4 by the DRI's split (dri-decisions-20261031-sc-5rd.md item 3). There is no Python copy of a Lean decision and no new report test, and no in-flight branch's hand-written files are touched (overlap check: only generated `lean/statements.txt` is shared).
3. Tests and gates can fail: PASS. M1-M8 in `docs/scope/sc-5rd/mutants.json`, and the stub-test probe (3 mutants caught).
4. Valid inputs still pass: PASS. `319 passed` (scope, stub, assurance and statements tests after the merge); no answer changes.
5. R8 binding: N.A. No field is read from a Lean answer.
6. Gate evidence matches the final HEAD: PASS for the sync (main merged at a43528360; commit list from `main..HEAD --no-merges` above). The gate is the chain's, on the final HEAD.
7. No unsigned item: PASS. There are no DELTA rows and no trust growth (`trust_map.py --check` PASS, +0).
8. Every user-visible change in DELTA: N.A. No user-visible change; DELTA is none, as the task expects.
9. Test selection finds the tests: PASS. `select_tests.py` selected the failing `test_scope_lean.py` and `test_assurance_manifest.py` tests (run above).
10. Lean statements say what is claimed: PASS. M1-M8 break the build. The theorems are about `governSets D`'s returned value, and the statements equal the stub's (`test_each_statement_sc5rb_proves_is_the_stubs_text`). The one false statement has a mechanised counterexample and a DRI ruling.
11. Budgets and limits fail closed: N.A. No budget or limit code changed.
12. No CPU or memory regression: N.A. No executable code changed (only proofs, `#guard` fixtures and tables).
13. `Test-removed` trailers: N.A. No test removed or renamed (`gate_collection` ids unchanged).
14. Both directions, cited evidence, spec re-read: PASS. `governSets_readings_refused` has accepting and refusing fixtures, and `preserved` is shown failing on 4 changed members. Each claim cites its command above, and the spec re-read section lists each statement.

## Commits (`git log --oneline --no-merges main..HEAD`, saved before this report)

    90b52b77b sc-5rd: assurance manifest as main's text plus this item's two entries
    81a29289d sc-5rd: trust-classes.json as main's text plus this item's two entries (the merge had reordered it)
    3cf2833a6 Regenerate the Lean inventories and codemap after the merge of main
    a289dd1dc sc-5rd: classify ReadingsLemmas/ReadingsTheorems; the scope definitions the new statements name leave the unexercised lists
    2ecad4247 sc-5rd: seeded-bug evidence (eight mutants, each killed by a proof or #guard)
    e1dad03de sc-5rd: regenerate the Lean inventories and codemap; classify the new example helpers as T
    f21969fa8 sc-5rd: fixtures for the proved statements on SR-1/SR-u and the refusing case; stub test for the three
    f405cfad5 sc-5rd: route corollary decodeBlock_sets, JsonWF from sc-1af's boundary check and the decoded payloads
    a7c34faa2 sc-5rd: prove governSets_preserves, governSets_strings and governSets_readings_refused under JsonWF
    e5d602ee2 sc-5rd: mechanise governSets_every_choice's counterexample (docs evidence)
    c5758e520 sc-5rd: record governSets_every_choice's counterexample for the DRI
