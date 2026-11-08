# sc-6: UDHR rights reach (scope spec 5.8, 7.8)

Status: delivered as the DRI cut it (reviews/dri-decisions-20261102-sc-6.md item 1, R9): the Lean part, its fixtures, (5) and (6); the document route moves to sc-6b. HEAD: the last commit on feature/sc-6.
Changed: `lean/VE/Scope/Reach.lean` (`Pinned.rightOf`, `rightNames`, `wholeRights`, `withReach`, `withBarReach`; `limitation_scope_of_reach` as 5.8 states it, plus `bar_reach_every_right`); `ReachExamples.lean` (F14, F14′, F14″, u0218.s18); `tests/test_scope_rights_reach.py`.
Open: sc-6b, the route (an effect word in `Wire.lean`, `govern` writing `scope` through `withReach`, F14/F14′ on the document route). No answer changes; trusted +18 under R16.
DRI signature needed: none.

## (1) What main had

- **The reach a governor computes.** `VE.Scope.covered` (`lean/VE/Scope/Govern.lean:112`), through `coveredLayout` (`:83`). An anchor's reach is `VE.Layout.anchorReach`: its units after its heading.
- **`VE.Rights.Limitation.scope`.** Defined at `lean/VE/Rights/Tree.lean:45` (`none` = all). Today only rights@0's decoder fills it, from the written `"scope"` (`"all"` or a list; `VE.Rights.Wire.decodeLimitation`, `Wire.lean:202-215`). It is checked at `Correlate.lean:393-398` and read by `inScope` (`Tree.lean:219`). Composition S2b's fixtures write u111 as `l29`, scope `all` (`lean/VE/Readings/RightsFixtures.lean:45`).
- **Where the stand-in `rights_and_freedoms_set_forth` comes from.** No code produces it (grep over `ve/`, `lean/`, `rust/`, `tools/`). It appears only in recorded data: the frozen pilot translation `usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md` (in `open_terms`, and in the `meaning.open` of u100b, u112 and u114), `usecases/question-answering/udhr-part07.ve.md`, `tests/data/relay-gate-cases.jsonl:527-528`, `docs/perf/inputs/prefix-*.ve.md` and `docs/judgment-terms/jt-e3/`.

## Plan rows (task "Deliver, in this order")

| Row | Delivered | Evidence |
|---|---|---|
| (1) the survey | yes | above |
| (2) `Pinned.rightNames`, `Pinned.withReach`, `limitation_scope_of_reach` | yes: rights' files only read (rights@0's `Limitation`/`Bar` and decoders); the scope is written once, by `withReach` | `test_limitation_scope_of_reach_is_spec_5_8s_text` (the whole statement, both conjuncts: review F1); `lake build` |
| (3) the stand-in removed from what the UDHR route produces | empty in sc-6: no code produces it; the frozen pilot data stays as recorded (DRI item 1). This item's part documents name a reach instead | `ReachExamples.lean:63`; `test_the_part_documents_name_no_stand_in_term` |
| (4) F14, F14′, F14″ | as Lean fixtures on a UDHR part document (Art. 3, 13, 29, 30, the pilot's ids and words); the document-route side is sc-6b (DRI items 1-2) | F14 `ReachExamples.lean:79-85`; F14′ `:89-97`; F14″ `:120-122` (two choices through `setChoices`/`atChoice`, SC-5's parts on main); `test_each_fixture_of_7_8_is_a_lean_section_with_guards` |
| (5) syn2code-scope-dec16: u0218.s18 | yes: lead-in guard over one unsplit act, 2 × 1 choices, blocker `embedded act frame: modality MD-6`. u0218.s17 has no colon, so it is no label (1.2): it heads s18 as an anchor's heading | `ReachExamples.lean:154-158`; `test_u0218_s18_records_its_blocker_and_two_by_one_choices` |
| (6) syn2code-scope-4 | already done on main: `decodeListName` decodes discourse's `ContentName` (`Wire.lean:73-77`); `SDoc.listNames` holds it (`Govern.lean:36`); the `list_name` reach compares `cn.units` (`Govern.lean:85-88`). No second table is left. **The row can close.** | `test_list_names_are_discourses_content_names` |

Synthesis round 2 (edits-scope.md): this item implements DEC 16 (row 5) and checks item 4 (row 6). It implements none of items 1-3 or 5-7, and not DEC 10.

Spec re-read: `limitation_scope_of_reach` against `docs/spec/scope.md:1564-1566` (main's 5.8 and 7.8 equal b2e050be2's, by `diff`); F14-F14″ against `:1767-1769`; the `Pinned` names and owner against `:1787`; DEC 16 against `:241-242`; and 1.5.1's `ScopeNotARule` for a rights content (`:207-213`), which is why no existing effect can carry the reach (DRI-QUESTION.md).

## Seeded bugs (Lean only: no Python or Rust product code changed)

All are in `lean/VE/Scope/Reach.lean`. Each was planted, built with `lake build VE.Scope.ReachExamples` and restored (`docs/scope/sc-6/mutants.json`, all 7 KILLED):

| Definition | Bug | Caught by |
|---|---|---|
| `withReach` | keeps the limitation's old scope | `limitation_scope_of_reach`'s proof; with the proof set aside, F14 `:80`, `:84` and F14″ `:122` |
| `rightNames` | drops the last right line | `:60`, F14 `:80`, `:85`, F14′ `:95` (`barRights`) |
| `rightOf` | reads no `right_lines` unit | F14 `:85`, F14′ `:97` |
| `wholeRights` | admits a right reached in part | F14 `:85` |
| `withBarReach` | admits a reach that misses a right line | `bar_reach_every_right`'s proof; with the proof set aside, F14′ `:96`, `:97` |

The u0218.s18 regression guards main's code, not code this item adds, so it has no seeded bug of its own. Trust mutants (`mac-pytest.sh --trustmut`, on the final Lean): `docs/scope/sc-6/trust-mutants.json`, exit 0. Counts: 17 KILLED, 0 SURVIVOR, 0 UNKNOWN, 8 INVALID, 1 ALLOWED (it does not elaborate; see `trust-mutants-allow.json`).

## Trust, size, bytes, tests

- **Trust.** `trust_map.py --check` against f1c306460476 gives K +0, S +10 and untied V +8, all in `lean/VE/Scope/Reach.lean`: trusted +18, PASS with the R16 allowance (DELTA.md). The ties pass is in FOLLOW-UPS.md under `## sc-6`. `python3 lean/audit.py`: "PASS: 733 source files; 8160 named theorem declarations audited".
- **Size.** `git diff --numstat $(git merge-base HEAD main)`, generated files, inventories and recorded answers excluded: 637 hand-written lines with this report (563 before it; ~600 is the size line, the fixtures file is 160 of them).
- **Bytes (estimate, not claimed).** 0 new. The 683 B of u111 (337), u112 (121) and u114 (225) become faithful only when sc-6b routes the reach and the pilot's next translation writes it.
- **Tests.**
  - The selected tests ran once (`mac-pytest.sh --select`, HEAD 761653cf): 1 failed. That was `test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`: the new files were not classified. Fixed in 7e7af9723, and the rerun of that test passed ("2 passed").
  - Everything else passed: 138 in the final chunk, and 77 + 643 + 564 in the chunked files.
  - No test from `main-known-red.txt` was hit.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer or route is added (DRI item 1); the document answer is unchanged (`test_a_document_without_a_rights_reach_answers_byte_for_byte_as_main`).
2. PASS: the plan-rows table above. The route moved by DRI item 1; no Python copy of a Lean decision; no report test; no file overlaps an in-flight branch beyond the shared import lists and ledgers (`lean/VE.lean`, `Audit.lean`, `tools/trust-classes.json`, `docs/trust-baseline.json`, `ve/assurance-manifest.json`, all append-only rows).
3. PASS: `mutants.json` (7 KILLED); `trust-mutants.json` exit 0.
4. N.A.: no Python or Rust product code changed; base and HEAD answer the fixture alike (the byte-identity test).
5. N.A.: Python reads no new Lean field.
6. N.A.: the chain runs the gate on the final HEAD; this item saves no commit-list evidence.
7. PASS: DELTA.md's one row cites R16; the move is SIGNED by DRI item 1.
8. PASS: no answer changes (byte-identity test); DELTA says so.
9. PASS: `select_tests.py --base $(git merge-base HEAD main)` selects `tests/test_scope_rights_reach.py`, `tests/test_scope_lean.py` and `tests/test_assurance_manifest.py`, the last of which caught the unclassified files.
10. PASS: `test_limitation_scope_of_reach_is_spec_5_8s_text`, which compares the whole statement since the F1 fix below; the `withReach` and `withBarReach` mutants break the two proofs.
11. N.A.: no budget, limit or deadline is added.
12. N.A.: no route change. `withReach` reads `covered` once and computes the reached rights once (`wholeRights`); sc-6b measures the route.
13. PASS: `gate_collection.py --check --prebuilt`: "6 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed".
14. PASS, both directions. `withReach` accepts (`:80`) and refuses (`:85`); `withBarReach` accepts (`:89`) and refuses (`:96`, `:97`); the spec re-read is listed above.

## Review fixes (`sc-6-review.final.md`)

- **F1 (B): the statement gate stopped at the first `:=`.** That `:=` was the one inside `{ L' with scope := L.scope }`, so the second conjunct of `limitation_scope_of_reach` was never compared. The same truncation affected main's `reguard_applies`, `restrict_applies`, `carveOut_applies` and `commute_applies`. `title_identity` is not in any statement gate.
  - **The class.** Every statement gate that cut a theorem at its first `:=`. The fix is one function, `proof_cut` in `tools/check_readings_defaults_statements.py`, which finds the `:=` outside every bracket.
  - **Who reads it.** That checker's `declarations` (RD and RD-9), `tools/check_pc3_statements.py`, and the scope helper `statement()` in `tests/test_scope_5_4_statements.py`. `tests/test_scope_answer.py` used a copy of that helper; it now imports the helper instead.
  - **Today's statements.** Compared whole, they still equal the spec's text: the four 5.4 effects, 5.3, 5.8, and the RD, RD-9 and PC-3 blocks. None of the 116 theorems in those blocks has a `:=` inside its statement today.
  - **Regression tests.** `tests/test_scope_rights_reach.py::test_the_statement_gate_compares_the_conjunct_after_the_record_update` (the review's probe), `tests/test_scope_5_4_statements.py::test_the_statement_runs_past_a_record_update` (4 cases), and `test_a_theorem_is_cut_at_its_proofs_assignment_not_one_inside_the_statement` in `tests/test_readings_defaults_statements.py` and `tests/test_pc3_statements.py`.
  - **Seeded bug.** `proof_cut` was planted cutting at the first `:=` at any depth; all 7 of these tests failed, then it was restored.
- **F2 to F7 (C)** are follow-ups, filed in FOLLOW-UPS.md under `## sc-6`.

Next item: sc-6b, then sc-7 (authoring wordings).
