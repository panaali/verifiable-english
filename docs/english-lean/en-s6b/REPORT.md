# en-s6b build report: the S6 reader of authored W1 rule blocks (EN-1, second part)

Status: EN-1 complete in authoring mode (no mode, no relay, no Python product change); no DRI signature reserved.
Lean reads 103 of the 103 pinned W1 blocks, and f21, to Python's exact node; the 17 `should` blocks have no derivation.
Nine section 4 statements are proved; `readNorm_authoring` and `readNorm_regulated` are `#guard`s over every fixture
(spec 4's substitution), their proofs filed as en-s6c. Trust +149 (K +0, R16); `actions_version` 36 -> 37 (DRI item 3).
Size: 1,321 hand-written lines before this report, over the DRI's "about 1,250" (decision 20261102-en-s6b item 1; see Size).

Decisions: reviews/dri-decisions-20261102-en-s6b.md items 1-5 (in /home/seyran/code/manage-agents). The full gate is
not run by me; the chain runs it on the final HEAD.

## Rows delivered, and not

| Task line | Delivered | Where / test |
|---|---|---|
| (1) `Norm/Rules.lean` (2.5): `normGrammar`, `normActs`, `normTy`, `normMeaning`, consequence rows, norm actions | yes. `grammar E L` first and unchanged, then the generated norm table, then one consequence row per variant of `_consequence`'s wording (each, any, No; the plain negative or universal form). A norm action reads each argument once (`args`); each condition is read once, under the consequence's bindings in a fresh state (R4). | `Norm/Examples.lean` f1-f24 |
| (1) `ve/english_grammar/norms@0.json` and generated `Fixed/Norms.lean` | yes: its own row type (`NormRow`, `NormSym`, `NormAct`), numbered from `(grammar E L).rank.size`. No `Catalogue.lean` hunk. The generator checks the source (actions, fields, nonterminals, W3, tags) and renders the table. | `tests/test_english_grammar_gen.py::test_malformed_norm_rows`, `::test_an_edited_norm_table_fails_the_check`, `::test_the_repository_is_in_sync` |
| (1) shared hunks | one hunk each in `Syntax.lean` (`Ty`: `norm`, `consequence`, `refs`) and `Actions.lean` (`Sem`, plus the `Norm.Value` import); appended imports in `lean/VE.lean`; `Audit.lean` regenerated. `layer_policy.py` needs no row (`VE.EnglishGrammar.*` is layer 3). Spec R6's one-line `Lexicon.lean` comment (`Env.source` now has a second reader). | — |
| (2) `Norm/Read.lean` (2.6) with `readNorm_sound` | yes | `lean_statements --check` |
| (2) `Norm/Elab.lean` (2.7) from 37c5fcb2f, its #guards and the `long 5000` limit fixture | yes, unchanged from 37c5fcb2f. 4999 carve-outs pass, 5000 give `ResourceLimit` (`decodeNorm`'s `maxNodes`). | `Examples.lean` `long` (:361-369) |
| (3) the ten remaining section 4 statements | nine proved word for word (`prefixMap_ok`, `condition_same`, `start_norm`, `normMeaning_unmarked`, `readNorm_complete`, `readNorm_unique`, `readNorm_numbered`, with `readNorm_sound` and `toNode_fields`). `readNorm_authoring` and `readNorm_regulated` are decided by `authored` over every section 6 fixture and every pinned block, as spec 4's closing note allows; their proofs are en-s6c (DRI item 1). | `tools/lean_statements.py --diff` against main: added 30, removed 0, changed 0 |
| (4) the DRI's condition: f1-f24 as `Norm/Examples.lean` #guards, each with its accepting and refusing side | f1-f19, f23, f24 read their texts with `readNorm` (:204-337, with the mutant fixtures :278-328). f20 and f21's environments are too large for a #guard file: their clauses are checked at the node level there (:339-358), and the pinned-block test reads f20's blocks and f21 through `readNorm`. f22 is the pinned-block test. | `lake build VE.EnglishGrammar.Norm.Examples` |
| (4) the full 120-block comparison | `test_lean_reads_each_pinned_block_as_python`: each block read with `readNorm` in its use case's environment and Python's lexicon, `toNodes`' node compared with Python's in Lean (`decodeNorm` on both sides); `DIFFERENT` is empty. It replaces en-s6's baseline test (trailers in ea8d15a61). `test_the_comparison_fails_on_a_changed_node` refuses a changed and an empty node. | `tests/test_english_statement_blocks.py` (4 tests) |
| (5) spec 5's lock line | the four `Norm/*.lean` definition files, `norms@0.json` and `Fixed/Norms.lean` join the lock; `actions_version` 36 -> 37 once. Same formulas, new identities: the senses runner's 12 pins, the ask fixtures and the S3 comparison were regenerated, each differing only in `actions_version` (and a recording time, and Lark's token order in two Python messages). | `english_grammar_gen.py --check --base <merge base>`; DELTA row 1 |
| Seeded bugs: `unless` read as `if`; a consequence row dropping its exception; Elab skipping `decodeNorm` | all KILLED | below |
| Plan edits (syn2) | implements edit 3 (the E3 norm step) only, as en-s6 did. | — |

## Corrections and deviations (recorded on the branch)

- **R7** (spec 1.2, 2.5; DRI item 2): `regulatedOf` decodes an environment that names `soft-norms@0` after
  `VE.SoftNorms.Wire.stripSoft`. Both pinned environments name it, and W1's decoder refuses it, so the spec's text
  would read no pinned block. Other environments decode as R6 states (`Examples.lean` R7 guard pair, :272-276).
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
  `Fixed/Norms.lean`: KILLED by `Examples.lean:239`.
- a consequence row dropping its exception (spec 6): `NormAct.step` keeps no carve-out (`Rules.lean`): KILLED by :238-239.
- a header dropping its exception list (`Rules.lean`): KILLED by :207, :209, :234-235, :311-314.
- Elab skipping `decodeNorm` (task): `Clause.toNode` decodes each formula alone (`Elab.lean`, proof cut): KILLED by :366.
- an except-when condition read with scope `[]` (spec 6, `Rules.lean`): KILLED by :246, :249, :324.
- `.mustNot` given a true sign (spec 6, `Value.lean`): KILLED by :75, :207, :212, :354.
- `stripSoft` applied unconditionally (DRI item 2, `Rules.lean`): KILLED by :274-275.
- `fits` refusing `.modal .must` on an obligation (DRI item 4, `Examples.lean`): KILLED by :207, :246.

Python (`tools/english_grammar_gen.py`):
- a norm nonterminal rendered one higher: KILLED by `test_the_norm_table_parses_and_names_its_nonterminals` and
  `test_the_repository_is_in_sync`.
- the W3 check of `parse_norms` skipped: KILLED by `test_malformed_norm_rows[changes4-not well-founded]` and `[changes5-…]`.

No Rust changed.

Mechanical mutants (`trust-mutants.json`): TRUSTMUT_SUMMARY

## Trust, size, overlap

- `tools/trust_map.py --check`: K +0, S +88, untied V +61, trusted +149 (Rules +94, Fixed/Norms +25, Elab +18, Read +7,
  Actions +3, Syntax +2); PASS with the allowance "SIGNED by standing ruling R16 (DRI-RULINGS.md), en-s6b, 2026-10-18",
  DELTA row 2 and the FOLLOW-UPS.md row under "## en-s6b". Ties to proved statements: `readNorm`, `NormOutcome`,
  `normGrammar`, `normActs`, `prefixMap`, `normTy`, `baseSize`, `normMeaning`, `Clause.toNode`.
- Size: `git diff --numstat $(git merge-base HEAD main)`, generated and recorded files excluded: 1,321 added, 73 removed
  before this report: Rules 313, Examples +281, Read 143, Elab 97, the pinned-block test +107/-38, the generator +109/-11
  and its tests +42, the trust side table +160, the spec +16/-3, `norms@0.json` 16, DELTA 9, the shared hunks 10,
  re-pins 12/12, the manifest 2, the differential test +4/-2. The DRI signed about 1,250 (item 1). The growth after that
  decision is R16's: fixtures that kill the trust mutants' survivors (+70 in Examples), the generator's both-sides
  tests (+42), the trust side table (+160), and the lines the version raise forces. No new deliverable.
- Overlap: `lean/VE.lean` and `Audit.lean` (generated) gain appended lines, as do several branches; no in-flight branch
  touches `Syntax.lean`, `Actions.lean`, `Lexicon.lean`, `tools/english_grammar_gen.py` or the test files.
- Pilot bytes: 0 (authoring mode; nothing outside the reader's tests reads it).

## Next

en-s6c (filed by the DRI): the proofs of `readNorm_authoring` and `readNorm_regulated`, with `Polarity.fits` back in
`Rules.lean` and `regulatedOf` tied. Then en-e3 (EN-2 onward, after en-e3-norm-PLAN's review) and en-s7.

## Commands and their outputs (final code)

- `lake build` (1235 jobs, through `regen_generated.py --write`) succeeded. `python3 lean/audit.py`: "PASS: 727 source
  files; 8040 named theorem declarations audited".
- `uv run python tools/lean_statements.py --diff <main's statements.txt> lean/statements.txt`: added 30, removed 0,
  changed 0.
- `uv run python tools/english_grammar_gen.py --check --base $(git merge-base HEAD main)`: exit 0.
- `uv run python tools/trust_map.py --check`: "PASS: K, S and untied [V] within 3b4e471f8c29 and the allowances
  introduced since".
- `uv run pytest -q tests/test_english_statement_blocks.py`: 4 passed (496 s); `tests/test_english_grammar_gen.py`:
  104 passed; `tests/test_ask_fixtures.py tests/test_ask_relay.py tests/test_ask_cli.py`: 106 passed.
- `mac-pytest.sh --select -- --base <merge base> --run`: 6 shards; failures fixed above, and the 64 units `--maxfail`
  left unrun were run with the fixed ids: SELECT_SUMMARY
- Spec re-read: section 4's statements against `docs/spec/english-lean-s6.md:438-497`, word for word
  (`lean_statements` shows each as written); 2.5-2.7's definitions against :259-384, with R7 and R8 recorded; section
  6's fixtures against :537-578, f1-f24 each mapped above; the DRI decision's conditions against items 1-5.
- Pre-existing failures on main (`main-known-red.txt`): none met.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed (no mode, no relay). The pinned-block test's Lean answer is compared in Lean.
2. PASS: each task line and where it is delivered is in the table above; no Python copy of a Lean decision (the
   comparison asks Lean's `decodeNorm` on both sides); no permanent report test.
3. PASS: ten seeded bugs KILLED (`mutants.json`); `trust-mutants.json` TRUSTMUT_SHORT; the comparator refuses a changed
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
11. PASS: `readNorm` with budget 0 stops (`Examples.lean` :332 "stopped 0 budget"); the long block hits `maxNodes`.
12. PASS: the per-call rebuilding found on the RSP environment is fixed (86 s -> 0.8 s for the typing check); no
    pilot path changes.
13. PASS: the two removed tests carry `Test-removed` trailers (ea8d15a61).
14. PASS: every new guard has its accepting and refusing side (`Examples.lean` :204-337); every claim above cites its
    command; the spec was re-read as listed.
