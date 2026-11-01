# en-s6 build report: S6's first layer, part a (the EN-0 remainder, the norm values and their assembly)

- **Status:** part a of EN-1 is delivered, cut under R16 at the seam the DRI signed (reviews/dri-decisions-20261101-en-s6.md
  item 1). No DRI signature is reserved, and DELTA has one row, signed by R16.
- **What changed:** `lean/VE/EnglishGrammar/Norm/Value.lean` (spec 2.2-2.4 and `assemble_numbered`), `Norm/Examples.lean`,
  Python's node for each of the 120 pinned blocks, `tests/test_english_statement_blocks.py`, and the EN-0 stub.
- **Open:** en-s6b, which is the grammar, the reader, Elab, ten of the eleven section 4 statements and the reading
  fixtures. The full gate has not been run by me; the chain runs it on the final HEAD.

## Rows delivered, and not

| Task line | Delivered | Where / test |
|---|---|---|
| (1) EN-0: stub elaborated under Lean 4.24.0 | yes: 2.2-2.4 as built `Norm/Value.lean`. 2.7 as `Norm/Elab.lean` at 37c5fcb2f, which proved `toNode_fields`. 2.5, 2.6 and all eleven section 4 statements word for word in `Stub.lean` (exit 0). Its one placeholder is `Ty.norm`. | `docs/english-lean/en-s6/Stub.lean` |
| (1) EN-0: Python's node for the 120 pinned blocks | yes: RSP 76, FSF 44, 0 refused, 17 `should` blocks with their soft nodes. Captured once at d05822548. | `tests/data/norm-blocks/{rsp,fsf}.jsonl`, `capture_blocks.py` |
| (1) EN-0: source fixtures' outcomes by hand | the outcomes for EN-1 are in spec section 6. Those for EN-5 to EN-9 are already written by hand in en-e3-norm-PLAN (:676-694, :751-769, :804-817, :846-862, :887-897), and this item adds none. `constitution.jsonl` is not part of this task, so it is not built. | — |
| (1) EN-0: the `Catalogue.lean` question | no edit. The norm table goes in en-s6b. Its nonterminals are numbered from `(grammar E L).rank.size`, which varies by environment, so its rows cannot use the catalogue's absolute `FixedRow` format. en-s6b's generator gives the table its own row type, so no `Catalogue.lean` hunk is expected. | — |
| (2) EN-1 2.2-2.4: `Value.lean` | yes, as the spec writes it. `Force.sign` has one arm per line so its arm mutants run. `Open`, `close` and `assembleFrom` are `assemble`'s helpers. | `Norm/Examples.lean` |
| (2) EN-1 2.5, 2.6, 2.7, `norms@0.json`, `Fixed/Norms.lean`, the shared `Ty`/`Sem` hunks | **en-s6b** (DRI decision item 1). Elab.lean moved there as the decision's fallback, because Value + Elab measured 162 trusted lines, over 150. | — |
| (2) the section 4 statements | `toNode_fields` was proved, but moved with Elab (37c5fcb2f). The other ten need the reader, so they are en-s6b's. `assemble_numbered` is `readNorm_numbered`'s conclusion for every assembled list. | `lean_statements --check`: 0 removed, 0 changed |
| (3) DRI condition: `Examples.lean` and the pinned-block test | the piece-level fixtures f13-f16 and f24, the statements of f7 and f8, and the carve-outs of f10/f11, each with an accepting and a refusing side. The test checks that all 120 Python nodes are present, match the text of their use case and decode through Lean's `decodeNorm` (with a retyped node refused), and it records the 0/120 baseline. | `tests/test_english_statement_blocks.py` (4 tests) |
| (3) the long well-formed block within a stated limit | `long 5000` assembles in one pass. en-s6 adds no evaluator, runner or mode. The limit a block is charged against is the reader's budget plus `decodeNorm`'s `maxNodes` (10000). Its fixture (4999 carve-outs pass, 5000 give `ResourceLimit`) was written and passed at 37c5fcb2f, and it moves with Elab. | `Examples.lean` `long` |
| (4) seeded bugs | see below | `mutants.json` |
| Plan edits (syn2) | this item implements edit 3 ("the E3 norm step": en-e3-norm as one S6 layer), as english-lean-PLAN section 11 and spec 1.1 state it | — |

Spec section 5's line "the new `Norm/*.lean` files join the `actions_version` lock" is deferred to en-s6b on purpose. No
reading reads `Value.lean` yet, so it is listed as untrusted in `tools/english_grammar_gen.py`, with that reason.
`actions_version`, `grammar_id` and every recorded English identity therefore stay as they are (risk 1). en-s6b
raises the version once, together with the reader.

## Seeded bugs (each planted alone, then restored; `docs/english-lean/en-s6/mutants.json`)

Lean, `lean/VE/EnglishGrammar/Norm/Value.lean`. Every plant was KILLED by named `Norm/Examples.lean` guards. Where
`assemble_numbered` refutes a plant first, its proofs were cut so that the guards are what gets judged:
- `need not` given a true sign. As written, the task's seed is an identity: `need not` and `must not` already share the
  sign false (`norm_english.py:97-100`). `Examples.lean:73` catches the plant.
- an exception's rule list loses its last number: :43, :44, :59 and 3 more.
- the rule number not carried to the next block (`k` not raised): :29, :35 and 8 more.
- the number check skipped (spec 6's seed): :27, :29 and 1 more.
- an except-when sentence drops its carve-out: :39, :67 and 2 more.
- the unknown-reference check skipped: :31, :43 and 5 more.
- `unless` read as `if` belongs to the reader (en-s6b), because en-s6 has no grammar rows.

Python, `tools/english_grammar_gen.py`: deleting `Norm/Value.lean`'s classification fails
`tests/test_english_grammar_gen.py::test_every_lean_file_of_the_two_directories_is_classified`. No Rust changed.

Mechanical mutants (`trust-mutants.json`, run on the cloud pool with `--rescore` over the first run): 82 KILLED,
0 SURVIVOR, 0 UNKNOWN, 25 ALLOWED. The allowed ones are 22 constructor drops that leave no executable mutant, `ruleCount`'s
untyped `[]`, and two equivalent `assembleFrom` mutants (`close` returns at most one statement). The reasons are in
`trust-mutants-allow.json`. The first run's 3 survivors: two are those equivalents, and the third (`assemble`
checking only the last statement's references) is killed by `Examples.lean:46-47`.

## Trust, size, overlap

- `tools/trust_map.py --check`: K +0, S +142 (`Norm/Value.lean`), V +0. `Examples.lean` is T. It is recorded with
  `--allow` as "SIGNED by standing ruling R16 (DRI-RULINGS.md), en-s6, 2026-10-18", with DELTA row 1 and the
  FOLLOW-UPS.md row under "## en-s6" (the ties pass).
- Size, hand-written: 537 lines (Value 241, Examples 94, test 97, capture script 52, trust classes 40, DELTA 8,
  generator 3, VE.lean 2), plus this report. Not counted: the stub (spec text copied, with placeholders),
  `mutants.json` (script output), and the captured data and generated files.
- Overlap: `lean/VE.lean` and `Audit.lean` get appended lines only (as do several in-flight branches).
  `tools/english_grammar_gen.py` also changes in feature/jt-3a, in a different hunk. `layer_policy.py`, `Syntax.lean`,
  `Actions.lean` and `Catalogue.lean` are untouched (sn-b7b8 is not crossed).
- Pilot bytes: 0, the authoring baseline. Lean reads 0 of the 120 pinned blocks.

## Next

en-s6b: `Norm/Rules.lean`, `norms@0.json`, `Fixed/Norms.lean`, `Norm/Read.lean`, Elab.lean (from 37c5fcb2f), the
`Ty`/`Sem` hunks, the section 4 statements, fixtures f1-f24 and the 120-block comparison, which replaces this item's
baseline test. After it: en-e3 and en-s7.

## Commands and their outputs (final code)

- `lake build` (all 1216 jobs) succeeded. `python3 lean/audit.py` gave "PASS: 712 source files; 7917 named theorem
  declarations audited". `tools/lean_statements.py --check` gave "removed: 0, changed: 0".
- `tools/trust_map.py --check` gave "PASS: K, S and untied [V] within 3148e87c47dc and the allowances introduced
  since" (S +142).
- `tools/regen_generated.py --check` gave rc 0, "checked 35 entries".
- `tools/gate_collection.py --check --prebuilt` gave "4 added, 0 removed by a trailer, 0 refused, 0 stale and 0
  malformed".
- `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` exited 0: 6 shards, 393 units, all passed
  (run en-s6-65597613-t538240), `test_english_statement_blocks.py` included.
- `mac-pytest.sh --trustmut … --allow … --rescore …` exited 0, with the counts above (`trust-mutants.json`).
- Spec re-read: each declaration of spec 2.2-2.4 appears in `Value.lean` word for word after whitespace
  normalisation (a script over the spec's first three Lean blocks found no difference). Each section 4 statement
  elaborates word for word in `Stub.lean`.
- Pre-existing failures on main (`main-known-red.txt`): none met in the selection.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed (no mode, no relay).
2. PASS: each task line, and where it is delivered or which DRI ruling moved it, is in the table above. The diff has
   no Python copy of a Lean decision: the pinned-block test asks Lean's `decodeNorm`.
3. PASS: six Lean seeds and one Python seed were KILLED (`mutants.json`). `trust_mutants` reported 0 SURVIVOR and 0
   UNKNOWN (`trust-mutants.json`). The pinned-block comparator refuses a retyped node
   (`test_every_recorded_node_decodes_in_lean`).
4. N.A.: no Python or Rust path computes these values yet, and `Examples.lean` pins Python's recorded statement
   shapes. The comparison with Lean's reading is en-s6b's.
5. N.A.: there is no relayed field to bind. Inside Lean, `assemble` refuses an undeclared rule reference
   (`Examples.lean:31-47`).
6. PASS: the evidence is on this HEAD's tree. The chain's gate runs on the final HEAD.
7. PASS: the one DELTA row cites R16, the allowance is recorded, and FOLLOW-UPS.md has its row under "## en-s6".
8. PASS: no user-visible change. `actions_version` and the lock are unchanged (`english_grammar_gen.py --check`), and
   nothing reads the new module.
9. PASS: `repo_map.py file lean/VE/EnglishGrammar/Norm/Value.lean` lists `tests/test_english_statement_blocks.py`,
   whose `lake build VE` fixture fails on a Lean seed.
10. PASS: the plants of `mutants.json` with `proofs_cut: true` are refuted by `assemble_numbered`'s proofs first.
    Those proofs are about `assemble`'s returned list.
11. PASS: assembly has no budget. The `long 5000` fixture ends, and the tests use `HANG_TIMEOUT` only.
12. N.A.: no pilot path changes.
13. PASS: no test was removed (`gate_collection.py --check --prebuilt`: 0 stale, 0 malformed).
14. PASS: every fault fixture in `Examples.lean` has its accepting side next to it. Every claim here cites a command
    above. The spec was re-read as stated above.
