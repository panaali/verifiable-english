# en-e3a build report: EN-2's owner pieces and the Lean mode `english.statement` (kind `blocks`), first part

Status: cut at the size measurement (common rules): this item delivers EN-2 step 0 and the mode's Lean runner with
every section 4 part A statement proved and its fixtures; the route recipe's steps 1-4 and the route fixtures are the
next item, **en-e3ab**, before en-e3b. No DRI signature is reserved. No route answer changes (nothing calls the mode).

Spec and plan: `docs/spec/en-e3-norm.md` and `docs/spec/en-e3-norm-PLAN.md`, copied verbatim from `64e75bd53` (blob
hashes equal; the commit is only on VM1's checkout, so the copies were read there with `git show`). Statement gate:
en-e3-norm-p3ver4 PASS; DRI 2026-11-02 items 1-3.

## Rows delivered, and not

| Task line | Delivered | Where / test |
|---|---|---|
| (1) `Norm/Owners.lean`: `Force.op`, `Polarity.op?`, `opOf_agrees`, `Mode.soft`, `soft_strict_iff`, `sourceView`, `sourceView_nil`, `UnformalisedSpan`, `Clause.toNodeChecked`, `toNodesChecked` | yes, the spec's text; with `toNodeChecked_ok`, `toNodesChecked_ok` and `toNodesChecked_authoring` (premise `ReadNormAuthoring`, the stub's statement of en-s6b's `readNorm_authoring`, which main decides by `#guard`s). All proved. | `Norm/OwnersExamples.lean` O1-O8 |
| (1) no merged statement changes | none changed | `lean_statements --check` |
| (2) `Norm/Run.lean`: request (`statementRequest`), `answerWith`, `answer`, `statementCase` (kind `blocks` alone), `statementCaseReported`, rule rows' byte spans from `lexSpans` (M10) | yes, the spec's text (2.3). The plan's `runStatement`/`runStatement_ok_reads` are bound in the spec as `statementCase`, `answer_one_iff` and `answer_one_rows` (plan line 598): those are delivered. | `Norm/RunExamples.lean` E1-E14, E16, E17 |
| (2) section 4 part A for EN-2 | all proved: `statementStatusCodes_classed`, `statementFields_statuses` (`decide`), `answer_one_iff`, `answer_one_rows`, `answer_partial_no_node`, `answer_stopped`, `answer_misplaced` (one lemma: a lookup in `Json.mkObj l` is the key's last binding in `l`). `statementCaseReported_fits` and `runMode_englishStatement` need the shape and the registry: en-e3ab. | `lake build`; `lean/audit.py` |
| (2) `Run.lean`'s code hunk (M8, M9) | `statementCodeRows` (appended to `codeClasses`, the one table), `renderCodeRows` (EN-3 appends it), `statementStatusCodes`, `statementFields`, `statementUnsentenced`; the `english.grammar` export writes the last three as `statement_statuses`, `statement_fields`, `statement_unsentenced` | E1-E16 (every coded row carries its class) |
| (2) OPEN-2 | `Norm/Rules.lean` exposed no tags: `normTags` added there, one hunk, `(normGrammar E L).rules.map (·.tag)` | E10 (the tags reach the witnesses); en-e3ab's R-f18 |
| (2) size measured | 683 changed lines (+671 -12) outside the verbatim spec and plan after (2): over the ~600 cap, so the item is cut here | `git diff --numstat` |
| Evaluators rule (DRI 2026-10-27) | `readNorm` is charged against `workBudget`; every other pass (`lexSpans` for the spans, `spansOf`, the rows) is linear in a source the lexer bounds (`maxTextChars` 10,000). E17: 300 blocks (9,791 characters) through the real reader answer `one` with 300 rows; 330 are `TextTooLong`. | E17 |
| (3) route recipe steps 1-4: registry and protocol, `RegistryExamples`, the shape and `Skeletons`, the encoder theorem, `Audit`/`ResponseShapeAudit` lines for them, `tools/english_codes.py` and its reader, `DEADLINES`, `_SCHEMA_SEEDS` | **not delivered: en-e3ab** | — |
| (3) layer rows, `lean/VE.lean` | `Norm.RunExamples` among the runner-boundary fixtures (`Owners` and `Run` need no row: `VE.EnglishGrammar.*` is layer 3, `*.Run` layer 4); four imports | `tools/check_lean_imports.py` |
| (4) route fixtures in `tests/data/route-cases.jsonl` | **not delivered: en-e3ab** (R-f1..R-f24 need the registered mode) | — |
| (4) the 120 pinned blocks through the mode, R-stale | measured here, through the mode's Lean entry (below) | `tests/test_english_statement_blocks.py::test_each_pinned_block_through_the_mode` |

**The 120 pinned blocks through the mode** (`Norm.Run.answer`, the case decoded once per 20 blocks; three requests
through `statementCaseReported` give the same rows): 121 records (76 RSP, 44 FSF, f21). 104 answer `one` (103 W1
blocks and f21), each with Python's recorded node byte for byte and the span `[0, bytes]` of the block; the 17 blocks
headed by `should` answer `none`, `NoDerivation`, sentence 1 (EN-4's). No block answers `NodeRefused` or `NodeLimit`,
and none is `Internal`. R-stale: the RSP environment with the FSF lexicon gives `decodeCase`'s refusal, status
`error`. Cost on this host (ve-cloud-3, loaded): `decodeCase` of a use-case environment about 5 s, `readNorm` about 3.2 s
per block, `answer` about 3.6 s (`normTags` rebuilds `normGrammar`, about 12% per answer; the spec's `answer` reads
both, so it is recorded, not changed).

## Deviations and corrections (recorded here, never in the copied spec)

- **`Polarity.fits` moved to `Norm/Rules.lean`** (in the OPEN-2 hunk). On main it is a fixture oracle in
  `Norm/Examples.lean` (DRI 20261102-en-s6b item 4: "beside the fixture until a theorem states it"); `opOf_agrees`
  states it now, and `Owners.lean` cannot import a fixture file. Same name and body; classified S. en-s6c's row
  (which carries it back with `readNorm_regulated`) finds it already there.
- **`Owners.lean` imports `Norm/Read.lean`** besides the spec's four imports: `ReadNormAuthoring` names `readNorm`.
- **M9's tables live in `VE.EnglishGrammar.Run`**: the section 4 statements name them `Run.statementStatusCodes` etc.
  from namespace `VE.EnglishGrammar.Norm`, which resolves to them unchanged; `Norm/Run.lean` opens
  `statementUnsentenced` by name.
- **`answer = answerWith leanReader`** as the stub states it (spec 2.3's last paragraph).
- **E15** is EN-3's (the render decoder). **E14** keeps the `lean-unknown` rows (the comparator is Python's,
  en-e3b's `tests/test_english_statement_shadow.py`); the stub's `deltaClasses` partition is not restated.
- `#eval` rows of the stub are `#guard`s here (no output in the build).
- English `actions_version` 45 -> 46: `Run.lean` and `Norm/Rules.lean` are hashed, and `Norm/Owners.lean` and
  `Norm/Run.lean` join the lock (DELTA row 1).

## Seeded bugs (each planted alone, shown failing, restored; `mutants.json`)

| Bug (spec 9) | File | Fails as planted | Fails with the proofs cut |
|---|---|---|---|
| `Force.op .needNot` -> `.mustNot` | Owners.lean | `opOf_agrees` | O1 (:21, :22), O2 (:26) |
| the gate passes a clause with a span | Owners.lean | `toNodeChecked_ok`, `toNodesChecked_ok` | O7 (:55, :57) |
| the runner answers `one` when `readNorm` stops | Norm/Run.lean | `answer_stopped`, `answer_one_iff`, `answer_partial_no_node` | E6, E8, E10, E14, E16 |
| a block fault without `sentence` | Norm/Run.lean | E4, E9 (:47, :52, :55), the sentence rule (:119) | same |
| every decoder refusal `NodeRefused` | Norm/Run.lean | E3 (:40, :42), E14 (:85) | same |
| a stop's rejection always names its sentence | Norm/Run.lean | `answer_stopped` | E16 (:89, :93, :103), :119 |
| (Python) `Norm/Run.lean` dropped from the lock's trusted files | tools/english_grammar_gen.py | `test_english_grammar_gen.py::test_the_repository_is_in_sync` | — |
| (Python) the `Norm.RunExamples` layer row removed | tools/layer_policy.py | `tools/check_lean_imports.py` (new outward import) | — |

Mechanical mutants per new trusted definition: the trust-mutants sweep (below).

## Trust (R16)

Measured on the final HEAD with `tools/trust_map.py --check`: see DELTA row 2 (filled in after the regenerated
declarations). Every new trusted definition is exercised: the owner pieces by O1-O8, the gate by O6-O7 and E2, the
runner's encoder by E1-E16, `answer`/`leanReader`/the real reader by E17 and the pinned-block test, the request
decoder and `statementCaseReported` by the pinned-block test's three whole-mode requests. FOLLOW-UPS row "## en-e3a"
asks for the ties pass.

## Pilot bytes

0 expected (EN-2 changes no answer; nothing relays to the mode until en-e3b, and Python decides until EN-3).

## Next items

- **en-e3ab**: the route recipe's steps 1-4 for `english.statement` (registry, protocol, `RegistryExamples`, the shape
  from `statementFields`, `Skeletons`, `statementCaseReported_fits` and the every-mode case, the audit lines,
  `english_codes.py`'s `from_lean`/`render` and the reader beside `codes()`, `DEADLINES`, `_SCHEMA_SEEDS` and the
  `wrong-row-type` list) and spec 8's route fixtures R-f1..R-f24 and R-stale in `tests/data/route-cases.jsonl`.
- then en-e3b (the shadow relay and the delta report), then en-e3 (EN-3).
