# en-s6b build report: the S6 reader of authored W1 rule blocks (EN-1, second part)

Status: EN-1 complete in authoring mode (no mode, no relay, no Python product change); no DRI signature reserved.
Lean reads 103 of the 103 pinned W1 blocks, and f21, to Python's exact node; the 17 `should` blocks have no derivation.
Nine section 4 statements are proved; `readNorm_authoring` and `readNorm_regulated` are decided by `authored` on every
text the fixtures read (spec 4's substitution), their proofs filed as en-s6c. Trust +149 (K +0, R16); `actions_version` 36 -> 37 (DRI item 3).
Size: 1,379 hand-written lines before this report, over the DRI's "about 1,250" (decision 20261102-en-s6b item 1; see Size).

Decisions: reviews/dri-decisions-20261102-en-s6b.md items 1-5 (in /home/seyran/code/manage-agents). The full gate is
not run by me; the chain runs it on the final HEAD.

## Rows delivered, and not

| Task line | Delivered | Where / test |
|---|---|---|
| (1) `Norm/Rules.lean` (2.5): `normGrammar`, `normActs`, `normTy`, `normMeaning`, consequence rows, norm actions | yes. `grammar E L` first and unchanged, then the generated norm table, then one consequence row per variant of `_consequence`'s wording (each, any, No; the plain negative or universal form). A norm action reads each argument once (`args`); each condition is read once, under the consequence's bindings in a fresh state (R4). | `Norm/Examples.lean` f1-f24 |
| (1) `ve/english_grammar/norms@0.json` and generated `Fixed/Norms.lean` | yes: its own row type (`NormRow`, `NormSym`, `NormAct`), numbered from `(grammar E L).rank.size`. No `Catalogue.lean` hunk. The generator checks the source (actions, fields, nonterminals, W3, tags) and renders the table. | `tests/test_english_grammar_gen.py::test_malformed_norm_rows`, `::test_an_edited_norm_table_fails_the_check`, `::test_the_repository_is_in_sync` |
| (1) shared hunks | one hunk each in `Syntax.lean` (`Ty`: `norm`, `consequence`, `refs`) and `Actions.lean` (`Sem`, plus the `Norm.Value` import); appended imports in `lean/VE.lean`; `Audit.lean` regenerated. `layer_policy.py` needs no row (`VE.EnglishGrammar.*` is layer 3). Spec R6's one-line `Lexicon.lean` comment (`Env.source` now has a second reader). | — |
| (2) `Norm/Read.lean` (2.6) with `readNorm_sound` | yes | `lean_statements --check` |
| (2) `Norm/Elab.lean` (2.7) from 37c5fcb2f, its #guards and the `long 5000` limit fixture | `Elab.lean` is unchanged from 37c5fcb2f. Its guards live in that commit's `Norm/Examples.lean`, and 25 of the 40 left the file as written: 24 have an equivalent that reads the text or comes from the pinned-block test, and the one that had none, `over`'s order (header targets, then precedence lines), is restored (review F2). 4999 carve-outs pass, 5000 give `ResourceLimit` (`decodeNorm`'s `maxNodes`). | `Examples.lean` `long` (:380-388); `over`'s order :331-333 and `test_lean_orders_over_as_python` |
| (3) the ten remaining section 4 statements | nine proved word for word (`prefixMap_ok`, `condition_same`, `start_norm`, `normMeaning_unmarked`, `readNorm_complete`, `readNorm_unique`, `readNorm_numbered`, with `readNorm_sound` and `toNode_fields`). `readNorm_authoring` and `readNorm_regulated` are decided by `authored` as spec 4's closing note allows: `rd`, the one reading of `Examples.lean`, runs it on every text that reads (so on f1, f2, f5, f7, f8, f10-f12 and f23), and `readings` on each pinned block and f21 (f20-f22). A section 6 fixture that reads cannot leave it out (review F1). Their proofs are en-s6c (DRI item 1). | `tools/lean_statements.py --diff` against main: added 30, removed 0, changed 0 |
| (4) the DRI's condition: f1-f24 as `Norm/Examples.lean` #guards, each with its accepting and refusing side | f1-f19, f23, f24 read their texts with `readNorm`, through `rd` (:209-356, with the mutant fixtures :284-348). f20 and f21's environments are too large for a #guard file: their clauses are checked at the node level there (:358-377), and the pinned-block test reads f20's blocks and f21 through `readNorm`. f22 is the pinned-block test. | `lake build VE.EnglishGrammar.Norm.Examples` |
| (4) the full 120-block comparison | `test_lean_reads_each_pinned_block_as_python`: each block read with `readNorm` in its use case's environment and Python's lexicon, `toNodes`' node compared with Python's in Lean (`decodeNorm` on both sides); `DIFFERENT` is empty. It replaces en-s6's baseline test (trailers in ea8d15a61). `test_the_comparison_fails_on_a_changed_node` refuses a changed and an empty node. Every pinned node has `over = []`, so `test_lean_orders_over_as_python` compares that field with Python's node read live: f7, f8 and rule 5 over every order of four targets, at every split between header and precedence lines. | `tests/test_english_statement_blocks.py` |
| (5) spec 5's lock line | the four `Norm/*.lean` definition files, `norms@0.json` and `Fixed/Norms.lean` join the lock; `actions_version` 36 -> 37 once. Same formulas, new identities: the senses runner's 12 pins, the ask fixtures and the S3 comparison were regenerated, each differing only in `actions_version` (and a recording time, and Lark's token order in two Python messages). | `english_grammar_gen.py --check --base <merge base>`; DELTA row 1 |
| Seeded bugs: `unless` read as `if`; a consequence row dropping its exception; Elab skipping `decodeNorm` | all KILLED | below |
| Plan edits (syn2) | implements edit 3 (the E3 norm step) only, as en-s6 did. | — |

## Corrections and deviations (recorded on the branch)

- **R7** (spec 1.2, 2.5; DRI item 2): `regulatedOf` decodes an environment that names `soft-norms@0` after
  `VE.SoftNorms.Wire.stripSoft`. Both pinned environments name it, and W1's decoder refuses it, so the spec's text
  would read no pinned block. Other environments decode as R6 states (`Examples.lean` R7 guards, :277-283).
- **R8** (spec 1.2; DRI item 4): `Polarity.fits` is the `authored` guards' oracle in `Norm/Examples.lean`, classified T;
  it moves to `Rules.lean` with `readNorm_regulated`'s proof (en-s6c).
- `normTy` reads `baseSize` (`= (grammar E L).rank.size`, `baseSize_eq`) and `readNorm` binds the grammar and actions
  once: each was rebuilt on every call (the typing check took 86 s on the RSP environment, then 0.8 s).
- The fixtures read under `workBudget`, the English service's budget.
- `tests/test_question_differential.py` reads the profile tables `ve.english_grammar.TABLES` lists, not every
  `*@*.json`; `english_grammar_gen.check` names the generated extras by path (the commit hook's snapshot has no
  norm source); `Norm/Elab.lean` and `Norm/Examples.lean` join the assurance manifest's `other_json`.

## Seeded bugs (each planted alone, then restored; `mutants.json`)

Lean (`lake build VE.EnglishGrammar.Norm.Examples`):
- `unless` read as `if` (task, spec 6): `norms@0.json` row `norm.clause-unless` with `"guard": true`, regenerated
  `Fixed/Norms.lean`: KILLED by `Examples.lean:244`.
- a consequence row dropping its exception (spec 6): `NormAct.step` keeps no carve-out (`Rules.lean`): KILLED by :243-244, :296.
- a header dropping its exception list (`Rules.lean`): KILLED by :212, :214, :239-240, :324-327.
- Elab skipping `decodeNorm` (task): `Clause.toNode` decodes each formula alone (`Elab.lean`, proof cut): KILLED by :385.
- an except-when condition read with scope `[]` (spec 6, `Rules.lean`): KILLED by :251, :254, :296, :343.
- `.mustNot` given a true sign (spec 6, `Value.lean`): KILLED by :75, :212, :217, :373.
- `stripSoft` applied unconditionally (DRI item 2, `Rules.lean`): KILLED by :279-280.
- `fits` refusing `.modal .must` on an obligation (DRI item 4, `Examples.lean`): KILLED by :212, :251.
- the soft profile read from the last profile only (`Rules.lean`, trust mutant M456's form): KILLED by :283.
- a condition read as an atom, not a formula (row `norm.clause-if`, `.base 2` -> `.base 3`): KILLED by :274, :296.
- `overOf` with its two lists swapped (review F2's probe; `Elab.lean`): survived 7473dc8d0, KILLED by :331, :332.
- `authored` refusing what only an unguarded fixture shows (review F1; `Examples.lean`). Each survived 7473dc8d0's guards:
  a binary predicate, KILLED by f5 and f23 (:225, :229); a precedence line, by f7 (:234-235); two header targets, by f8
  (:239-240); a carve-out without a guard, by f10 (:243-244).
- `fits` refusing a plain role of sign false (review F1; `Examples.lean`): KILLED by f12's two forms (:260, :261);
  7473dc8d0 saw only the universal one.

Python (`tools/english_grammar_gen.py`):
- a norm nonterminal rendered one higher: KILLED by `test_the_norm_table_parses_and_names_its_nonterminals` and
  `test_the_repository_is_in_sync`.
- the W3 check of `parse_norms` skipped: KILLED by `test_malformed_norm_rows[changes4-not well-founded]` and `[changes5-…]`.

No Rust changed.

Mechanical mutants (`trust-mutants.json`): a full run on 2d7348985 (611 mutants of the 16 new or changed trusted
definitions; `--test Norm/Examples.lean`, so the generated table's mutants are judged by the reader's fixtures), then
one more fixture (M456's) and `--rescore` in its checks mode on d22d05cba (511 reused, 100 rerun): 462 KILLED,
0 SURVIVOR, 0 UNKNOWN, 50 INVALID, 99 ALLOWED. Each allowed one has its reason in `trust-mutants-allow.json`: lists of
at most one element (a predicate has one or two arguments, `VE/Route/Wire.lean:172`; one argument after a header's
number; at most one inline carve-out), ranks W3 does not bind, the deduplicated `No` variant, `any`/`all` on profiles
no decoder reads, `NormOneReading` (a Prop) by the section 4 proofs each mutant breaks, and mutants Lean refuses to
elaborate. The first runs' survivors were real gaps, closed by the fixtures at :284-348 and :283.

After review F1 and F2 (`Examples.lean` changed, no trusted definition): `--rescore` in its checks mode against that
record on fe1cad4f5, sharded over four parts (three on GitHub Actions, one on the VM): 555 rerun, 56 carried, 462
KILLED, 0 SURVIVOR, 0 UNKNOWN, 50 INVALID, 99 ALLOWED; no allow entry changed. The parts' `--merge` first refused them
because part 4 named the same PREV by its worktree-relative path and the others by its absolute path; the merge was
run on copies with that one string made absolute (every other field, the head, tree, inputs and options, already
agreed). A full run on the VM was stopped at about 240 of 611 mutants after 6.4 h (VM load 70-95).

## Trust, size, overlap

- `tools/trust_map.py --check`: K +0, S +88, untied V +61, trusted +149 (Rules +94, Fixed/Norms +25, Elab +18, Read +7,
  Actions +3, Syntax +2); PASS with the allowance "SIGNED by standing ruling R16 (DRI-RULINGS.md), en-s6b, 2026-10-18",
  DELTA row 2 and the FOLLOW-UPS.md row under "## en-s6b". Ties to proved statements: `readNorm`, `NormOutcome`,
  `normGrammar`, `normActs`, `prefixMap`, `normTy`, `baseSize`, `normMeaning`, `Clause.toNode`.
- Size: `git diff --numstat $(git merge-base HEAD main)`, generated and recorded files excluded: 1,379 added, 73 removed
  before this report: Rules 313, Examples +300, Read 143, Elab 97, the pinned-block test +145/-38, the generator +109/-11
  and its tests +42, the trust side table +161, the spec +16/-3, `norms@0.json` 16, DELTA 9, the shared hunks 10,
  re-pins 12/12, the manifest 2, the differential test +4/-2. The DRI signed about 1,250 (item 1). The growth after that
  decision is R16's: fixtures that kill the trust mutants' survivors (+79 in Examples), the generator's both-sides
  tests (+42), the trust side table (+160), and the lines the version raise forces. The review round adds 49 (F1 and F2:
  Examples +11, the `over` differential +38). No new deliverable.
- Overlap: `lean/VE.lean` and `Audit.lean` (generated) gain appended lines, as do several branches; no in-flight branch
  touches `Syntax.lean`, `Actions.lean`, `Lexicon.lean`, `tools/english_grammar_gen.py` or the test files.
- Pilot bytes: 0 (authoring mode; nothing outside the reader's tests reads it).

## Next

en-s6c (filed by the DRI): the proofs of `readNorm_authoring` and `readNorm_regulated`, with `Polarity.fits` back in
`Rules.lean` and `regulatedOf` tied. Then en-e3 (EN-2 onward, after en-e3-norm-PLAN's review) and en-s7.

## Commands and their outputs (final code)

- On fe1cad4f5 (after review F1, F2): `lake build` (1235 jobs, through `regen_generated.py --write`) succeeded. `python3 lean/audit.py`: "PASS: 727 source
  files; 8040 named theorem declarations audited".
- `uv run python tools/lean_statements.py --diff <main's statements.txt> lean/statements.txt`: added 30, removed 0,
  changed 0; `--check`: changed 0.
- `uv run python tools/english_grammar_gen.py --check --base $(git merge-base HEAD main)`: exit 0.
- `uv run python tools/trust_map.py --check`: "PASS: K, S and untied [V] within 3b4e471f8c29 and the allowances
  introduced since".
- `uv run pytest -q tests/test_english_statement_blocks.py`: 4 passed (496 s) before the review, 5 after it (the Mac
  run below: 75 s); `tests/test_english_grammar_gen.py`:
  104 passed; `tests/test_ask_fixtures.py tests/test_ask_relay.py tests/test_ask_cli.py`: 106 passed.
- After review F1, F2: `mac-pytest.sh --select -- --base <merge base> --run` on ve-mac-1, HEAD fe1cad4f (clean),
  3710 s: exit 0, 0 failed or error ids. `regen_generated.py --check`: 35 entries; `gate_collection.py --check
  --prebuilt`: 15 added, 2 removed by a trailer, 0 refused, 0 stale, 0 malformed. Before the review:
  `mac-pytest.sh --select -- --base <merge base> --run`: 6 shards; failures fixed above, and the 64 units `--maxfail`
  left unrun were run with the fixed ids: 13,438 passed, 1 failed
  (`tests/test_english_lean_s3_compare.py::test_committed_report_counts_are_derived_from_individual_records`, fixed by
  re-recording the S3 comparison). The first run's failures, all fixed: `test_assurance_manifest` (other_json),
  `test_question_differential` (the glob), `test_precommit_hook` (the hook's snapshot), the ask fixtures (re-recorded).
  After the last fixtures: `tests/test_english_statement_blocks.py tests/test_english_grammar_gen.py
  tests/test_question_differential.py`: 114 passed; `regen_generated.py --check`: 35 entries checked, rc 0;
  `tools/gate_collection.py --check --prebuilt`: 0 stale, 0 malformed (the two `Test-removed` trailers restated in the
  final commit's trailer block).
- Spec re-read: section 4's statements against `docs/spec/english-lean-s6.md:438-497`, word for word
  (`lean_statements` shows each as written); 2.5-2.7's definitions against :259-384, with R7 and R8 recorded; section
  6's fixtures against :537-578, f1-f24 each mapped above; the DRI decision's conditions against items 1-5.
- Pre-existing failures on main (`main-known-red.txt`): none met.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed (no mode, no relay). The pinned-block test's Lean answer is compared in Lean.
2. PASS: each task line and where it is delivered is in the table above; no Python copy of a Lean decision (the
   comparison asks Lean's `decodeNorm` on both sides); no permanent report test.
3. PASS: eighteen seeded bugs KILLED (`mutants.json`); `trust-mutants.json` 462 KILLED, 0 SURVIVOR, 0 UNKNOWN, 99 ALLOWED; the comparator refuses a changed
   and an empty node (`test_the_comparison_fails_on_a_changed_node`).
4. PASS: Lean's node equals Python's for all 103 W1 pinned blocks and f21 (`test_lean_reads_each_pinned_block_as_python`);
   f1, f11, f12 and f20's node guards compare with Python's recorded nodes.
5. N.A.: no relayed field. Inside Lean, unknown rule references are refused (`Examples.lean` f14, f24).
6. PASS: generated files regenerated on this tree (`regen_generated.py --write`); the chain's gate runs on the final HEAD.
7. PASS: DELTA row 1 cites the DRI's item 3, row 2 cites R16 with the per-file counts; no reserved signature.
8. PASS: no route changes; the version raise is DELTA row 1 with its re-recorded goldens (ask, S3, senses pins).
9. PASS: `tools/select_tests.py` selected `tests/test_english_statement_blocks.py` and `tests/test_english_grammar_gen.py`
   (changed first in shard 6's order), and the seeded generator bug fails a selected test.
10. PASS: each proof's statement is about `readNorm`'s returned value; `lean_statements --diff`: 0 changed. Cutting
    `toNode_fields`' proof under the Elab seed shows the proof refutes it first.
11. PASS: `readNorm` with budget 0 stops (`Examples.lean` :351 "stopped 0 budget"); the long block hits `maxNodes`.
12. PASS: the per-call rebuilding found on the RSP environment is fixed (86 s -> 0.8 s for the typing check); no
    pilot path changes.
13. PASS: the two removed tests carry `Test-removed` trailers in the final commit's trailer block (ea8d15a61 had them
    outside it, and `gate_collection.py --check --prebuilt` refused them); the check is rerun on that commit.
14. PASS: every new guard has its accepting and refusing side (`Examples.lean` :209-356); every claim above cites its
    command; the spec was re-read as listed.
