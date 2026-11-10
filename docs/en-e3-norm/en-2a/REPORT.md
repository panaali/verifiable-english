# en-e3a build report: EN-2's owner pieces and the Lean mode `english.statement` (kind `blocks`), first part

**DRI rulings on this item (no signature reserved, nothing open):** `reviews/dri-decisions-20261109-en-e3a.md` items 1
(the cut after deliverable (2), next item en-e3ab) and 2 (the status word `unformalised`);
`reviews/dri-decisions-20261109-en-e3a-2.md` items 1 (the span code classed G[V]; trusted +167 SIGNED by the DRI),
2 (the rule tags a thunk forced only for `many`, a signed spec edit, built here) and 3 (the second lex moves to row
en-e3a-cutback).

Status: cut at the size measurement the task names after deliverable (2) ("Measure size now ... and record it"; the
common rules: "measure it before you start the second half of the work, and cut there"). This item delivers EN-2 step 0
and the mode's Lean runner with every EN-2 section 4 part A statement that needs no registry proved, and its fixtures;
the route recipe's steps 1-4 and the route fixtures are the next item, **en-e3ab**, before en-e3b. The cut was put to
the DRI decider before it was recorded (BUILDER-CHECKLIST 15) and is SIGNED by the DRI 2026-11-09
(`reviews/dri-decisions-20261109-en-e3a.md` item 1; backlog row en-e3ab applied there, en-e3b now waits for it). Its
condition holds: `tests/test_english_statement_blocks.py`, the EN-2 answer `#guard`s and O1-O7 stay selected, and the
six section 9 seeded bugs are shown failing (below). No DRI signature is reserved. No route answer changes (nothing
calls the mode).

Spec and plan: `docs/spec/en-e3-norm.md` and `docs/spec/en-e3-norm-PLAN.md`, copied verbatim from `64e75bd53` (blob
hashes equal; the commit is only on VM1's checkout, so the copies were read there with `git show`). Statement gate:
en-e3-norm-p3ver4 PASS; DRI 2026-11-02 items 1-3.

## Rows delivered, and not

| Task line | Delivered | Where / test |
|---|---|---|
| (1) `Norm/Owners.lean`: `Force.op`, `Polarity.op?`, `opOf_agrees`, `Mode.soft`, `soft_strict_iff`, `sourceView`, `sourceView_nil`, `UnformalisedSpan`, `Clause.toNodeChecked`, `toNodesChecked` | yes, the spec's text; with `toNodeChecked_ok`, `toNodesChecked_ok` and `toNodesChecked_authoring` (premise `ReadNormAuthoring`, the stub's statement of en-s6b's `readNorm_authoring`, which main decides by `#guard`s). All proved. | `Norm/OwnersExamples.lean` O1-O8 |
| (1) no merged statement changes | none changed | `lean_statements --check` |
| (2) `Norm/Run.lean`: request (`statementRequest`), `answerWith`, `answer`, `statementCase` (kind `blocks` alone), `statementCaseReported`, rule rows' byte spans from `lexSpans` (M10) | yes, the spec's text (2.3). The plan's `runStatement`/`runStatement_ok_reads` are bound in the spec as `statementCase`, `answer_one_iff` and `answer_one_rows` (plan line 598): those are delivered. | `Norm/RunExamples.lean` E1-E14, E16, E17 |
| (2) section 4 part A for EN-2 | all proved: `statementStatusCodes_classed`, `statementFields_statuses` (`decide`), `answer_one_iff`, `answer_one_rows`, `answer_partial_no_node`, `answer_stopped`, `answer_misplaced`, with four helper theorems in `Norm/Run.lean` (`findSome_lookup`, `getD_mkObj`: a lookup in `Json.mkObj l` is the key's last binding in `l`, `lookup_append`, `lookup_none`) and a local `answer_simp` macro. `ReadNormAuthoring_eq` (`Iff.rfl`) guards `ReadNormAuthoring` against edits: it restates english-lean-s6.md 4's `readNorm_authoring` as copied (the copy is checked against the spec by review: "spec re-read" below, not by a tool). `statementCaseReported_fits` and `runMode_englishStatement` need the shape and the registry: en-e3ab. | `lake build`; `lean/audit.py` |
| (2) `Run.lean`'s code hunk (M8, M9) | `statementCodeRows` (appended to `codeClasses`, the one table), `renderCodeRows` (EN-3 appends it), `statementStatusCodes`, `statementFields`, `statementUnsentenced`; the `english.grammar` export writes the last three as `statement_statuses`, `statement_fields`, `statement_unsentenced` | E1-E16 (every coded row carries its class) |
| (2) OPEN-2 | `Norm/Rules.lean` exposed no tags: `normTags` added there, one hunk, `(normGrammar E L).rules.map (·.tag)` | E10 (the tags reach the witnesses); en-e3ab's R-f18 |
| (2) size measured | 683 changed lines (+671 -12) outside the verbatim spec and plan after (2), at `62fe76254`: over the ~600 cap, so the item is cut there. The final count and what grew after the cut: section "Size" | `git diff --numstat 9f5dd46ab 62fe76254` |
| Evaluators rule (DRI 2026-10-27) | `readNorm` is charged against `workBudget`; the other passes are at most quadratic in the statement count (`statementSpans`' fold appends to its list, `statementRow` calls `overOf` per row; the spec's text, kept) over a source the lexer bounds (`maxTextChars`, 10,000 characters). E17: 300 blocks (9,791 characters) through the real reader answer `one` with 300 rows and the last span `[9759, 9791]`; 330 are `TextTooLong`. | E17 (`RunExamples.lean:178-187`); the thunk test above |
| (3) route recipe steps 1-4: registry and protocol, `RegistryExamples`, the shape and `Skeletons`, the encoder theorem, `Audit`/`ResponseShapeAudit` lines for them, `tools/english_codes.py` and its reader, `DEADLINES`, `_SCHEMA_SEEDS` | **not delivered: en-e3ab** | — |
| (3) layer rows, `lean/VE.lean` | `Norm.RunExamples` among the runner-boundary fixtures (`Owners` and `Run` need no row: `VE.EnglishGrammar.*` is layer 3, `*.Run` layer 4); four imports | `tools/check_lean_imports.py` |
| (4) route fixtures in `tests/data/route-cases.jsonl` | **not delivered: en-e3ab** (R-f1..R-f24 need the registered mode) | — |
| (4) the 120 pinned blocks through the mode, R-stale, and one ambiguous condition with both trees | measured here, through the mode's Lean entry (below); the ambiguous condition is f18 through the real reader (`Run.answer`, `leanReader`): `many`, sentence 1, both trees with `normGrammar`'s tags | `tests/test_english_statement_blocks.py::test_each_pinned_block_through_the_mode`; `RunExamples.lean:229-243` |

**The 120 pinned blocks through the mode** (`Norm.Run.answer`, the case decoded once per 20 blocks; three requests
through `statementCaseReported` give the same rows): 121 records (76 RSP, 44 FSF, f21). 104 answer `one` (103 W1
blocks and f21), each with a node equal as JSON to Python's recorded node and the span `[0, bytes]` of the block; the 17 blocks
headed by `should` answer `none`, `NoDerivation`, sentence 1 (EN-4's). No block answers `NodeRefused` or `NodeLimit`,
and none is `Internal`. R-stale: the RSP environment with the FSF lexicon gives `{"status": "error", "error": "InvalidInput: the lexicon
names another environment"}` (asserted exactly). The test passed in 414.5 s on ve-cloud-3 (`pytest --durations`).
Cost (UNVERIFIED as a benchmark: one run each on a loaded host, `lake env lean` over generated files that print ten
answers on the RSP environment): decoding the case alone 4.99 s, ten `readNorm` reads 36.61 s, ten `answer`s 40.57 s;
so `normTags`, which rebuilds `normGrammar` beside `readNorm`, adds about 12% per answer. The spec's `answer` reads
both. Since DRI 2026-11-09 (`dri-decisions-20261109-en-e3a-2.md` item 2) `answerWith` hands `outcomeFields` the tags
as a thunk that only a `many` answer forces (`tests/test_english_statement_blocks.py::test_the_rule_tags_are_forced_only_for_many`:
a reader whose tags panic answers `one`, `none`, `rejected` and `unformalised` under `LEAN_ABORT_ON_PANIC=1`, and
`many` aborts). The second lex in `statementSpans` and the `many` branch's grammar rebuild are moved to row
en-e3a-cutback by item 3 of that ruling.

## Deviations and corrections (recorded here, never in the copied spec)

- **`Polarity.fits` moved to `Norm/Rules.lean`** (in the OPEN-2 hunk). On main it is a fixture oracle in
  `Norm/Examples.lean` (DRI 20261102-en-s6b item 4: "beside the fixture until a theorem states it"); `opOf_agrees`
  states it now, and `Owners.lean` cannot import a fixture file. Same name and body; classified S. en-s6c's row
  (which carries it back with `readNorm_regulated`) finds it already there. Item 4's own condition for the move
  ("until a theorem states it") is met by `opOf_agrees`; that is why it is no new ruling.
- **`Owners.lean` imports `Norm/Read.lean`** besides the spec's four imports: `ReadNormAuthoring` names `readNorm`.
- **M9's tables live in `VE.EnglishGrammar.Run`**: the section 4 statements name them `Run.statementStatusCodes` etc.
  from namespace `VE.EnglishGrammar.Norm`, which resolves to them unchanged; `Norm/Run.lean` opens
  `statementUnsentenced` by name.
- **`answer = answerWith leanReader`** as the stub states it (spec 2.3's last paragraph).
- **E15** is EN-3's (the render decoder). **E14** keeps the `lean-unknown` rows (the comparator is Python's,
  en-e3b's `tests/test_english_statement_shadow.py`); the stub's `deltaClasses` partition is not restated.
- `#eval` rows of the stub are `#guard`s here (no output in the build).
- **The status of an answer with unformalised spans is `"unformalised"`**, not the spec's keyword-spelled word:
  `lean/audit.py` refuses that token anywhere in a Lean source, strings and comments included. 2.3's tables,
  `outcomeFields`, the fixtures and the one statement literal that names it (`Run.answer_partial_no_node`'s
  `.str "unformalised"`; its name and every other word unchanged) use it. SIGNED by the DRI 2026-11-09,
  `reviews/dri-decisions-20261109-en-e3a.md` item 2 (its condition: E2's `#guard`, status `unformalised` with no
  `statements`, and `python3 lean/audit.py` passing on the final HEAD). The spec erratum is the FOLLOW-UPS row under
  "## en-e3a"; en-e3ab's schema inherits the word from `statementFields`.
- **`statementStatusCodes` already lists `rendered` and the four render codes** (the spec's text), and so does the
  `english.grammar` export, while `codeClasses` gains `renderCodeRows` only at EN-3: en-e3ab's schema admits the seven
  EN-2 statuses (recipe step 2) and its class checks skip the render codes until EN-3.
- **E15's kind-`blocks` rows** are here (another kind, an extra member, and a well-formed request that reaches
  `decodeCase`); its render rows are EN-3's.
- English `actions_version` 45 -> 46: `Run.lean` and `Norm/Rules.lean` are hashed, and `Norm/Owners.lean` and
  `Norm/Run.lean` join the lock (DELTA row 1).
- **`outcomeFields` and `stoppedFields` take the rule tags as `Thunk (Array String)`**, forced only for `many`, and
  `answerWith` passes `Thunk.mk fun _ => R.tags c.E c.L`: SIGNED by the DRI 2026-11-09,
  `reviews/dri-decisions-20261109-en-e3a-2.md` item 2 (spec erratum: the FOLLOW-UPS row under "## en-e3a"). No
  answer changes; `test_the_rule_tags_are_forced_only_for_many` is the condition's test.
- **`statementSpans`, `sentenceBytes`, `opensStatement` are G[V]** (they were G[I]): `dri-decisions-20261109-en-e3a-2.md`
  item 1.
- **The main merge re-pins `lean/VE/EnglishGrammar/Run.lean` in `ve/assurance-manifest.json`** (whole file, 800
  lines): this item's code hunk had left main's 759-line pin stale, which `tests/test_assurance_manifest.py` refuses.

## Seeded bugs (each planted alone, shown failing, restored; `mutants.json`)

| Bug | File | Fails as planted | Fails with the proofs cut |
|---|---|---|---|
| Force.op .needNot mapped to .mustNot (spec 9; O1) | Norm/Owners.lean | Norm/Owners.lean:29 theorem opOf_agrees | Norm/OwnersExamples.lean:22 O1; Norm/OwnersExamples.lean:23 O1; Norm/OwnersExamples.lean:27 O2 |
| the gate passes a clause with a span (toNodeChecked := toNode; spec 9; O7 and E2) | Norm/Owners.lean | Norm/Owners.lean:79 theorem toNodeChecked_ok; Norm/Owners.lean:85 theorem toNodesChecked_ok | Norm/OwnersExamples.lean:57 O7 (toNodeChecked); Norm/OwnersExamples.lean:59 O7 (toNodesChecked) |
| the runner answers one when readNorm stops (spec 9; E8) | Norm/Run.lean | Norm/Run.lean:247-248 theorem Run.answer_stopped (and answer_one_iff, answer_partial_no_node) | Norm/RunExamples.lean:60 E6; Norm/RunExamples.lean:62 E6; Norm/RunExamples.lean:76 E10; Norm/RunExamples.lean:122 E14; Norm/RunExamples.lean:126-131 E16; Norm/RunExamples.lean:140 E16 (every Reject); Norm/RunExamples.lean:152 E8; Norm/RunExamples.lean:156 every row's class; Norm/RunExamples.lean:235-236 f18 through the real reader |
| a block fault without `sentence` (spec 9; E4) | Norm/Run.lean | Norm/RunExamples.lean:48 E4; Norm/RunExamples.lean:53 E9; Norm/RunExamples.lean:56 E4 (NoConsequence, StrayCarveOut); Norm/RunExamples.lean:171 the sentence rule | Norm/RunExamples.lean:48 E4; Norm/RunExamples.lean:53 E9; Norm/RunExamples.lean:56 E4 (NoConsequence, StrayCarveOut); Norm/RunExamples.lean:171 the sentence rule |
| every decoder refusal coded NodeRefused (spec 9; E3 and E14) | Norm/Run.lean | Norm/RunExamples.lean:41 E3 (depth); Norm/RunExamples.lean:43 E3 (node budget); Norm/RunExamples.lean:122 E14 (lean-unknown) | Norm/RunExamples.lean:41 E3 (depth); Norm/RunExamples.lean:43 E3 (node budget); Norm/RunExamples.lean:122 E14 (lean-unknown) |
| a stop's rejection always names its sentence (spec 9; E16) | Norm/Run.lean | Norm/Run.lean:247 theorem Run.answer_stopped | Norm/RunExamples.lean:126 E16 (Internal); Norm/RunExamples.lean:130 E16 (EmptyDocument); Norm/RunExamples.lean:140 E16 (every Reject); Norm/RunExamples.lean:171 the sentence rule |
| fewer blocks than statements is Internal, never a one answer that zip shortens (self-review B) | Norm/Run.lean | Norm/RunExamples.lean:103 fewer blocks than statements | same |
| a rule row's span is in bytes, not code points (M10; self-review B) | Norm/Run.lean | Norm/RunExamples.lean:105 non-ASCII byte spans through answerWith | same |
| a retyped source is refused (self-review B) | Norm/Run.lean | Norm/RunExamples.lean:217 a retyped id, kind or source is an error row | same |
| the rule tags are forced only for many (DRI 2026-11-09 en-e3a-2 item 2) | Norm/Run.lean | tests/test_english_statement_blocks.py::test_the_rule_tags_are_forced_only_for_many (the `one` case aborts: exit 134) | same |
| (Python) Norm/Run.lean dropped from the English lock's trusted files | tools/english_grammar_gen.py | tests/test_english_grammar_gen.py::test_the_repository_is_in_sync | — |
| (Python) Norm.RunExamples left at layer 3 (its runner-boundary row removed) | tools/layer_policy.py | tools/check_lean_imports.py (gate step): new outward Lean import: VE.EnglishGrammar.Norm.RunExamples -> VE.EnglishGrammar.Norm.Run | — |

Mechanical mutants per new trusted definition: the trust-mutants sweep (section "Trust-mutants sweep").

## Size

`git diff --numstat $(git merge-base HEAD main)` (base `2d1f04743` after the main merge), hand-written files only (the
verbatim spec and plan, every file `tools/regen_generated.py --owner` names a generator for, and the tool-written sweep
record `trust-mutants.json` are excluded), on the final code: **+1,424 -12 = 1,436 lines**. Lean product 491
(`Norm/Run.lean` 303, `Norm/Owners.lean` 121, `Run.lean` +42 -1, `Norm/Rules.lean` 13, `Norm/Examples.lean` -11); Lean
fixtures 328 (`RunExamples.lean` 245, `OwnersExamples.lean` 83); tests 84 (`tests/test_english_statement_blocks.py`);
tools 7; evidence 526 (`mutants.json` 213, REPORT 192, `trust-mutants-allow.json` 109, DELTA 12). Besides, the
hand-reviewed pin of `EnglishGrammar/Run.lean` in the generated `ve/assurance-manifest.json` (5 lines, merge commit).
At the cut point (`62fe76254`) it was 683; the DRI's cut (`dri-decisions-20261109-en-e3a.md` item 1) stops the item
after deliverable (2) and moves (3) and (4) to en-e3ab. The growth after the cut is no new deliverable: guards the
self-review and the trust-mutants sweep asked for (E17, the request decoder, f18 through the real reader, byte spans,
the sweep's survivors), the pinned-block and thunk tests, and evidence.

## Trust (R16 and the DRI's signature)

`uv run python tools/trust_map.py --check` on the final code: PASS; against `a0102f0e5`: K +0, S +46, D +42, G +176,
tied +26, trusted **+167** (`Norm/Run.lean` +110, `Norm/Owners.lean` +36, `Norm/Rules.lean` +13, `Run.lean` +8).
17 over R16's 150: SIGNED by the DRI 2026-11-09 (`dri-decisions-20261109-en-e3a-2.md` item 1, below its +170 stop),
recorded with `tools/trust_map.py --allow` in `docs/trust-baseline.json`; DELTA row 2 itemises it; the cut-back is row
en-e3a-cutback. Every new trusted definition is exercised: the owner pieces by O1-O8, the gate by O6-O7 and E2, the
runner's encoder by E1-E16, the spans by E1, E13, E17 and the non-ASCII guard, `answer`/`leanReader`/the real reader by
E17, f18 and the pinned-block test, the request decoder and `statementCaseReported` by the whole-mode guards and the
pinned-block test's three whole-mode requests; mechanically by the sweep below. FOLLOW-UPS row "## en-e3a" asks for the
ties pass.

## Trust-mutants sweep

`zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/en-e3-norm/en-2a/trust-mutants-allow.json --json
docs/en-e3-norm/en-2a/trust-mutants.json --test lean/VE/EnglishGrammar/Norm/OwnersExamples.lean --test
lean/VE/EnglishGrammar/Norm/RunExamples.lean` (the VM; the Mac and the cloud pools were unreachable): 18 definitions,
366 mutants, the three span definitions selected (G[V]).

- Full run at `a9d5d29ed` (16,575 s): 263 KILLED, 39 SURVIVOR, 10 UNKNOWN, 27 INVALID, 27 ALLOWED. Each survivor got a
  guard (`e171fe8c2`: two `over` entries, two span rows, both optional request members, the error row's `id`, the
  export's `identities`/`advice`/`policy`, a translation statement first or last, a quote- or numeral-led sentence),
  or an allow reason when it is equivalent (`isEmpty` of a cut list; an `Option.toList` cut; `getLast?` of a
  one-element reverse; `InvalidInput`, which is no `Reject`'s code) or `ReadNormAuthoring`, a Prop no check can
  evaluate (exercised by `ReadNormAuthoring_eq` and `toNodesChecked_authoring`). Eight UNKNOWNs were Lean refusing the
  mutated text (type errors), allowed with that reason; two were build timeouts under load.
- Rescore on the final code (`--rescore` of that record, `--build-timeout 3600`, at the merge `9b74a4d2d`; mode
  "checks": 231 verdicts carried, 135 run, 3,760 s): **288 KILLED, 0 SURVIVOR, 0 UNKNOWN, 27 INVALID, 51 ALLOWED,
  0 NOT RUN; exit 0**. Every ALLOWED row is one of the reasons in `trust-mutants-allow.json`; every `outcomeFields`
  mutant of line 123 (the span rows) is KILLED. The record is `trust-mutants.json`.

## Pilot bytes

0 expected (EN-2 changes no answer; nothing relays to the mode until en-e3b, and Python decides until EN-3).

## Next items

- **en-e3ab**: the route recipe's steps 1-4 for `english.statement` (registry, protocol, `RegistryExamples`, the shape
  from `statementFields`, `Skeletons`, `statementCaseReported_fits` and the every-mode case, the audit lines,
  `english_codes.py`'s `from_lean`/`render` and the reader beside `codes()`, `DEADLINES`, `_SCHEMA_SEEDS` and the
  `wrong-row-type` list) and spec 8's route fixtures R-f1..R-f24 and R-stale in `tests/data/route-cases.jsonl`
  (R-f18, the ambiguous condition with both trees, is already a `#guard` here through `Run.answer`).
- **en-e3a-cutback** (DRI `dri-decisions-20261109-en-e3a-2.md` item 3, row applied there): `readNorm` (or a wrapper)
  returns the sentence byte positions and its built grammar, so `statementSpans` stops lexing a second time and the
  `many` branch stops rebuilding `normGrammar`; at least 17 trusted lines back. It merges before en-e3 (EN-3).
- then en-e3b (the shadow relay and the delta report), then en-e3 (EN-3).

## Final checks (on the merge `9b74a4d2d` with main `2d1f04743`)

- `cd lean && lake build`: "Build completed successfully (1348 jobs)".
- `python3 lean/audit.py`: "PASS: 816 source files; 9101 named theorem declarations audited".
- `uv run python tools/regen_generated.py --check`: "checked 38 entries" (exit 0); `--resolve` for the merge's
  generated conflicts.
- `uv run python tools/trust_map.py --check`: PASS (above); `uv run python tools/english_grammar_gen.py --check
  --base <merge base>`: exit 0 (lock at 46).
- `tools/gate_collection.py --check --prebuilt` (before the merge): "1 added, 0 removed by a trailer, 0 refused, 0 stale
  and 0 malformed".
- Trust-mutants rescore: exit 0 (above).
- Selected tests: SELECTED_PLACEHOLDER

## Spec re-read (BUILDER-CHECKLIST 14)

Each new section 4 statement compared with the spec after whitespace normalisation (a script over
`docs/spec/en-e3-norm.md` and the two Lean files; `Run.` prefixes dropped): equal unless stated.

- spec re-read: `opOf_agrees` against docs/spec/en-e3-norm.md:1066 (Norm/Owners.lean:28): equal.
- spec re-read: `soft_strict_iff` against :1069 (Norm/Owners.lean:40): equal.
- spec re-read: `sourceView_nil` against :1071 (Norm/Owners.lean:49): equal.
- spec re-read: `toNodeChecked_ok`, `toNodesChecked_ok` against :1073, :1076: equal.
- spec re-read: `Run.statementStatusCodes_classed`, `Run.statementFields_statuses` against :1084, :1088 (Norm/Run.lean:217, :221): equal.
- spec re-read: `Run.answer_one_iff`, `Run.answer_one_rows`, `Run.answer_stopped`, `Run.answer_misplaced` against :1091, :1096, :1112, :1119: equal.
- spec re-read: `Run.answer_partial_no_node` against :1106: one word differs, `.str "partial"` is `.str "unformalised"`: SIGNED by the DRI 2026-11-09, reviews/dri-decisions-20261109-en-e3a.md item 2.
- spec re-read: the definitions `Force.op` (:213), `Polarity.op?` (:221), `Mode.soft` (:227), `sourceView` (:233), `UnformalisedSpan` (:237), `Clause.toNodeChecked` (:252), `toNodesChecked` (:258), `statementCodeRows` (:337), `statementStatusCodes` (:349), `statementFields` (:359), `statementUnsentenced` (:370), `statementSpans` (:399), `outcomeFields` (:451), `statementRequest` (:466), `answerWith` (:518): the spec's text, except the status word (item 2 above) and `outcomeFields`/`stoppedFields`/`answerWith`'s tags thunk (SIGNED by the DRI 2026-11-09, reviews/dri-decisions-20261109-en-e3a-2.md item 2; FOLLOW-UPS erratum row).
- spec re-read: `ReadNormAuthoring` against english-lean-s6.md 4's `readNorm_authoring`: equal (read by hand; `ReadNormAuthoring_eq` only guards the copy).
- DELTA rows against base spec 2.12 (the version raise) and R16/the DRI's item 1 (trust): re-read.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS for the Lean side: a retyped `id`, `kind` or `source` is an error row (`RunExamples.lean:217`), E15's other kind and extra member; the relay schema and its fuzz tests are N.A. here (the mode is not registered: en-e3ab/en-e3b).
2. Deliverables: PASS: "Rows delivered, and not" lists each task line with its commit area and test; (3) and (4) moved by the DRI's item 1.
3. Tests can fail: PASS: `mutants.json` (13 seeded bugs, each failing a named guard, theorem or test), `trust-mutants.json` (the sweep), the thunk test's both directions.
4. Python, Lean agree: PASS: `tests/test_english_statement_blocks.py::test_each_pinned_block_through_the_mode` (121 records; 104 `one` with Python's node, 17 `none`).
5. R8 binding: N.A.: no relay reads the mode in this item (en-e3b).
6. Gate evidence: PASS: main merged before the final checks (section "Final checks"); the chain runs the gate on the final HEAD.
7. No unsigned item: PASS: DELTA row 1 cites the DRI's 2026-11-02 jt-3p item 3, row 2 the DRI's 2026-11-09 en-e3a-2 item 1; `review-ready.py`'s [delta] form.
8. Every user-visible change in DELTA: PASS: no route answer changes (the mode is unregistered); the version raise and the code-table rows are DELTA's rows and prose.
9. Test selection: PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects 466 units, not every unit, and includes `tests/test_english_statement_blocks.py` (its run log: "changed ['tests/test_english_statement_blocks.py']").
10. Statements say what is claimed: PASS: the spec re-read above; `answer_*` are about `Run.answer`'s returned row; the seeded runner bugs break `answer_stopped`/`answer_one_iff` (`mutants.json`).
11. Budgets fail closed: PASS: `readNorm` at `workBudget`, its `.budget` outcome is `budget` (E14's `lean-unknown` rows); E17 at the text limit (330 blocks `TextTooLong`).
12. No CPU or memory regression: PASS: no existing route changes; the tags thunk removes `normTags` from every non-`many` answer (`test_the_rule_tags_are_forced_only_for_many`); the second lex is row en-e3a-cutback.
13. Test-removed trailers: PASS: `tools/gate_collection.py --check --prebuilt`: "1 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed".
14. Both directions, cited evidence, spec re-read: PASS: each new guard has its opposite (`wholeRow` answers `ok` beside the retyped rows; `oneSpans` refuses fewer and more blocks; the thunk test answers four statuses and aborts on `many`); claims cite commands above.
15. No overclaim, no silent cut, checks can fail, limits charged: PASS: the `ReadNormAuthoring_eq` wording fixed; the cut and both deferrals are DRI rulings; every new guard shown failing on a mutant (`mutants.json`); E17.

SELF-REVIEW: 1 A, 8 B, 6 C; fixed 15 (it listed seven C rows; A: the span code reclassed G[V] under the DRI's item 1; B: trust numbers
re-measured, the tags thunk built under the DRI's item 2, the size line, the self-review and spec re-read sections, the
sweep run to exit 0, the non-ASCII byte-span, retyped-member and fewer-blocks guards; C: line references refreshed,
`Polarity.fits`'s ruling cited, `ReadExamples.LF` reused, both codes.json files named, `ReadNormAuthoring_eq`'s
wording, the span-unit note for en-e3b in FOLLOW-UPS; not fixed: `BlockFault.code`'s tie, kept as recorded in DELTA
row 2). The first self-review's line was lost with the expired session; this is the second call's (its fixes did not
rewrite a third of the diff).

FOLLOW-UP: en-e3ab english.statement's route recipe steps 1-4 (registry, shape, encoder theorem, codes reader, DEADLINES, schema seeds) and spec 8's route fixtures
FOLLOW-UP: en-e3a-cutback readNorm returns sentence positions and its grammar; statementSpans and the many branch stop re-lexing and rebuilding (trusted lines back under 150)
