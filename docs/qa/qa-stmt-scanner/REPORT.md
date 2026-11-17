# qa-stmt-scanner: the question-answering statement gate reads declarations with the shared scanner

No DRI signature needed. DELTA: none (gate tool only; every statement checker's real-tree output is byte-identical
before and after). Trust +0 in every class (`tools/trust_map.py --check`: K +0, S +0, D +0, G +0, tied +0).

Source: reviews/dri-decisions-20261111-sc-2d-f1.md item 4 (LEVER 1, text-only F5) and sc-2d-f1's "Outside this item";
held row 5 of prompts/held-20261116/README.md. Python only; no Lean file and no approved statement changed.

SIZE: 98 product (tools: +98 −89), 320 tests (+320 −21), 135 other hand-written lines (this report and mutants.json;
the saved outputs under evidence/ are tool output, not hand-written).

## Deliverables

| # | Task row | Delivered | Test |
|---|---|---|---|
| 1 | `tools/question_statements.py` uses the shared scanner; the private one is deleted (one owner) | bc477d60e7: `statements`, `definitions` and `types` are now thin readers over `check_readings_defaults_statements.declarations` (`scan`, `across`). The line loops that stopped at a blank line, a column-0 `/--`, `end ` or a ```` ``` ```` line are gone. The spec side is read from its ```` ```lean ```` blocks. | tests/test_question_statements_scanner.py (all), tests/test_question_statements.py, tests/test_question_reading.py::test_a_changed_predicate_body_is_noticed |
| 2 | Failing-first probes: a changed line after a blank line and after a column-0 doc comment in a lean/VE/Question or Ask declaration copy | `test_q1_compares_a_predicate_line_after_a_gap` (5 predicates × blank line, doc comment), `test_q2_compares_a_definition_line_after_a_blank_line` (37 approved Q2 definitions with bodies), `test_q2_compares_a_field_or_constructor_after_a_column_0_doc_comment` (14 approved Q2 structures and inductives; a column-0 field or constructor after a column-0 doc comment is valid Lean, sc-2d-f1 F3). On main's tools: **70 failed, 29 passed**; the gate passed every changed copy (evidence/failing-first-on-main.txt). On HEAD: all pass. | same |
| 2 | Real-source gate output byte-identical before and after (save both) | evidence/before/ and evidence/after/: `question_statements.py` (Q1), `--q2 --no-lean`, `--q2` with the Lean check (46 statements and signatures elaborated, PASS): identical. | `cmp` of each pair |
| 3 | F5: drop `lemma`, `coinductive`, `prelude` from COMMANDS; fix the records | Dropped (the safe direction: the text gets longer, never shorter). Checked first with `lean` v4.24.0: `structure S where\nprelude : Nat\nx : Nat`, `def f (lemma : Nat) : Nat :=\nlemma + 1` and `def coinductive : Nat := 1` all elaborate, so they are names, not keywords. A grep of the v4.24.0 sources finds every remaining COMMANDS word as a parser token. The records now say COMMANDS holds that version's keywords only: the COMMANDS comment, the module docstring, the `declarations()` docstring and tests/test_statement_scanner.py:11-14. | tests/test_statement_scanner.py::test_the_scanner_reads_a_declaration_as_lean_does[F5 field named prelude-*, F5 binder named lemma-*, F5 binder named coinductive-*] (6 ids; all 6 fail on main) |
| 4 | Every statement checker that imports the shared scanner still reports the same on the real tree | Before and after outputs saved and byte-identical, each exit 0: `check_readings_defaults_statements.py`, `check_rd9_sc1_statements.py`, `check_pc3_statements.py`, `check_pc9_statements.py`, `check_pc2a_statements.py`, `check_ap56_statements.py`, `question_statements.py` (Q1, Q2 text, Q2 with Lean). The scope 5.4 gate is a test file (tests/test_scope_5_4_statements.py, which reads `declarations` and `proof_cut`): it passed in the selected run. | evidence/before/*.txt = evidence/after/*.txt |

### Changes the deliverables needed (inside the item's files)

- **`proof_cut` keeps a `let`'s or a `have`'s own `:=`** (tools/check_readings_defaults_statements.py). Two Q1
  statements, `mapSpan_valid` and `mapSpan_codepoints_valid`, contain `let span := …`. The old Q1 reader cut at
  `:= by`. The shared `proof_cut` cut at the first top-level `:=`, the `let`'s, so switching the reader alone would have
  stopped comparing their text after `let span :=` (on both sides, so the output stayed identical and hid it). Now
  each top-level `let`/`have`/`letI`/`haveI` takes the next top-level `:=` as its own. A stray one (inside a string,
  or `let x ← e`) only moves the cut later, never earlier. Every gate's real-tree output is unchanged, and every
  approved Q1/Q2 statement reads exactly as main's reader read it (checked name by name).
  Tests: `test_proof_cut_keeps_a_let_or_have_binding`, `test_q1_compares_the_statement_after_a_let[*]`.
- **A name declared twice keeps every text.** The old reader kept the last copy (in one file and across files), so an
  approved predicate could be changed and a second, unchanged copy in another namespace placed after it. Now each
  copy's text is kept, one per line, and that equals no single approved text. On the real tree no approved name is
  declared twice. Test: `test_a_name_declared_twice_equals_no_approved_text[4 cases]`.
- tests/test_question_statements.py: one call updated to the new signature (`statements(spec)`; the unused
  `source`/`proof` parameters are gone).

## Review fixes (qa-stmt-scanner-review.final.md)

| Finding | Fix | Regression tests | Commit |
|---|---|---|---|
| F1 (B): `lean_blocks` read a `.lean` source only from a ```` ```lean ```` fence in its doc comment | Structural: the readers (`statements`, `definitions`, `types`, through `scan`) take only a `Code` value, built by `spec_code` (a spec section's fences; a section without one is an error, never prose read as code) or `source_code` (whole files). Raw text is a `TypeError`. `across()` is folded into `scan()`, which merges every code unit the same way. Every source reader goes through `source_code`: Q1 statements and predicates, Q2 statements, definitions, structures and inductives. The module docstring is corrected. | `tests/test_question_statements_scanner.py::test_a_source_is_read_whole_not_through_a_doc_fence[*]` (103 ids: 15 Q1 theorems, 5 Q1 predicates, 32 Q2 theorems, 37 Q2 bodies, 14 Q2 types; a doc fence quotes the approved text and the declaration changes, so the gate must fail by name). Also `test_a_doc_fence_quoting_every_approved_declaration_changes_nothing[q1, q2]` (a quote is not read as a second copy) and `test_the_readers_take_only_spec_or_source_code`. The review's PROBE F1 fails on d2c38652da (the gate passed "5 of 5 equal") and passes after the fix ("Changed or missing predicates: HasReading"). | d5da3181ed |
| C4 (note, same class): `tests/test_scope_5_4_statements.py` `statement()` fell back to a source's fences | `statement()` reads Lean code only. Spec callers pass `spec_5_4_lean()` (the spec's fences; asserts at least one). | `tests/test_scope_5_4_statements.py::test_a_source_is_read_whole_not_through_a_doc_fence[*]` (8 theorems) | d5da3181ed |
| C2 (note): the `statements` docstring said "the first `:=` outside every bracket" | The docstring now says the cut skips a `let`/`have` binding's own `:=`. | none (docstring only) | d5da3181ed |
| C3 (note): comment text is no longer compared | Recorded here. Q1 and Q2 now compare declarations with their comments left out, by the shared scanner's design; main compared `--` text. Meaning is unchanged. | none (record only) | this report |

C1 (`let_fun` not in `BINDS`) is left as noted. No approved statement uses it, and adding it would change the
shared `proof_cut` of every gate.

The other gates (RD, RD-9, PC-3, PC-9, PC-2a, AP56, English S3/E2) read fences in spec sections only. A grep of
tools/ and tests/ found no other source read through a fence.

## Seeded bugs (Python; no Lean or Rust product code changed)

Each was planted alone in the committed tree, its tests were run, and then it was restored (`git checkout HEAD --`).
Full list: mutants.json.

| Bug | File | Failing test |
|---|---|---|
| blank-line stop restored (`scan` inserts a command at every blank line) | tools/question_statements.py | test_q1_compares_a_predicate_line_after_a_gap[*-blank line], test_q2_compares_a_definition_line_after_a_blank_line[*]: 42 failed |
| column-0 doc-comment stop restored | tools/question_statements.py | test_q2_compares_a_field_or_constructor_after_a_column_0_doc_comment[*]: 14 failed |
| `"prelude"` restored in COMMANDS | tools/check_readings_defaults_statements.py | test_the_scanner_reads_a_declaration_as_lean_does[F5 field named prelude-rd] and [-pc3] |
| `proof_cut` ignores `let` (`binds += 0`) | tools/check_readings_defaults_statements.py | test_proof_cut_keeps_a_let_or_have_binding, test_q1_compares_the_statement_after_a_let[*]: 3 failed |
| last copy of a duplicated name wins / first wins / later file wins | tools/question_statements.py | test_a_name_declared_twice_equals_no_approved_text[same file before] / [same file after] / [other file before] (the later-file case re-run against `scan` after `across` was folded in: 1 failed) |
| F1: `source_code` reads a source through its ```` ```lean ```` fences again | tools/question_statements.py | test_a_source_is_read_whole_not_through_a_doc_fence[q1 asked_reads_back, q1 HasReading, q2 holds_iff, HoldsU, LeadHoldsU, ReasonHoldsU, ZeroAsked]: 7 of 7 failed |
| C4: `statement()` reads through fences again | tests/test_scope_5_4_statements.py | test_a_source_is_read_whole_not_through_a_doc_fence[*]: 8 of 8 failed |

The first version of the duplicate test let "last wins" survive, because its copy came last. It now places the copy
before and after the approved one, in the same file and in another (2157efa34c), and all three variants are caught.

## Tests run

- Selected run (`mac-pytest.sh --select`, ran on ve-cloud-2): 288 units, 0 failed, exit 0, on tree 2df3262e29
  (= bc477d60e7 + 2157efa34c's test; later commits are docs only).
- `tools/regen_generated.py --check`: 41 entries, exit 0. `tools/repo_map.py file tools/question_statements.py`
  selects tests/test_question_statements_scanner.py and tests/test_statement_scanner.py.
- `tools/gate_collection.py --check`: 77 added. The 3 ids removed by F5 (`test_every_command_ends_a_declaration_after_a_doc_comment[lemma|coinductive|prelude]`)
  carry `Test-removed:` trailers in the report commit. The first commit had them in a paragraph that git does not read
  as trailers.
- Trust: `tools/trust_map.py --check` PASS, +0 in every class. The light lane printed NOT (534 lines, the saved
  evidence included). `tools/trust_mutants.py --plan` selects 0 definitions and 0 mutants (no Lean change), so the
  sweep has nothing to run; no trust_mutants record.
- After the review fixes (d5da3181ed): selected run (`mac-pytest.sh --select`, GitHub Actions run
  qa-stmt-scanner-d5da3181-t877702): 54 units in 3 shards, 0 failed, exit 0. `lake build`: 1475 jobs, success.
  `lean/audit.py`: PASS. `tools/gate_collection.py --check`: 191 added, 3 removed by a trailer, 0 refused. The tool's
  real-tree output (Q1, Q2 text) is byte-identical to evidence/after.
- Full gate: not run by the builder (the chain runs it on the final HEAD).

Pre-existing failures (main-known-red.txt): none met in this item's tests.

Pilot bytes expected to move: none (a gate tool; no checker, relay or Lean change).

## Notes for the DRI

- `proof_cut` lies outside the item's named regions (COMMANDS, declarations) but in a named file. The item needed
  the change: without it, moving to the shared scanner would have dropped part of two approved Q1 statements from
  the comparison. Every gate that reads `proof_cut` reports the same.
- PC-3's `declarations()` docstring (tools/check_pc3_statements.py, outside this item's paths) still says the named
  early-end cases are "every such case in Lean v4.24.0's built-in syntax (`COMMANDS` …)". With the non-keywords
  gone, that claim is now true, so the docstring is unchanged.
- The Q gate now takes about 0.8 s (Q1) and 1.1 s (Q2 text), up from 0.14 s, because the shared lexer reads every
  character. This is a gate tool, not a product path.

## Next item

None in this line.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay or Lean answer touched).
2. Every deliverable built: PASS (table above; one owner: the private scanner is deleted, the shared one is the only reader). Tests: tests/test_question_statements_scanner.py, tests/test_statement_scanner.py F5 cases.
3. Tests can fail: PASS (9 seeded bugs, all caught; the probes fail on main: evidence/failing-first-on-main.txt).
4. Base and HEAD agree, valid inputs pass: PASS (byte-identical before/after outputs of all 7 checkers; every approved Q1/Q2 statement read as main read it).
5. R8 binding: N.A. (no relayed field).
6. Gate evidence matches final HEAD: PASS (evidence is saved checker output and a saved test run, not live git; the full gate runs on the chain).
7. No unsigned item: PASS (no DELTA rows; trust +0).
8. Every user-visible change in DELTA: N.A. (gate tool; outputs identical).
9. Test selection finds the tests: PASS (repo_map maps both changed tools to tests/test_question_statements_scanner.py; the selected run ran it).
10. Lean statements say what is claimed: PASS (all `tools/check_*_statements.py` that read the shared scanner were run, all exit 0 and unchanged; no statement changed).
11. Budgets, limits, deadlines: N.A. (no evaluator or budget; the tests use no sleeps or timeouts).
12. No CPU or memory regression: N.A. for the product (gate tool only; timings in the notes).
