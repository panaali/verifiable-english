# en-e3a-cutback: the statement mode lexes the text and builds the grammar once

No DRI signature is reserved. **The trusted cut-back of at least 17 lines was not reached: trusted lines grew by +6
(K +0, S +0, V +6), which misses the target by 23 lines.** "Trust" below gives the per-definition numbers and the
reason: the three span definitions duplicate nothing `readNorm` computes. Everything else the task asks for is
delivered. No answer changes. The one DELTA row is the English `actions_version` raise that base spec 2.12 forces,
signed by precedent (jt-3p item 3).

Task: `prompts/task-en-e3a-cutback.txt`; ruling `reviews/dri-decisions-20261109-en-e3a-2.md` item 3 (moved here),
item 1 (the signature this cut-back was meant to reduce). Branch `feature/en-e3a-cutback`; merge base with main
`08f3c2af9` (main was merged once, `ad377e955`; main has since moved by one merge, norm-defaults-cfr-1b, which touches
none of these files).

SIZE: 143 product, 28 tests, 232 other hand-written lines. Measured with
`git diff --numstat $(git merge-base HEAD main)`, generated files excluded. Product: `Norm/Read.lean` +19 -8,
`Norm/Run.lean` +40 -31, `Norm/Rules.lean` -3, `ResponseShape/Encoders/EnglishStatement.lean` +24 -18. Tests:
`Norm/RunExamples.lean` +22 -6. Other: `tools/trust-classes.json` +9 -1, `ve/assurance-manifest.json` +5 -5, `mutants.json` 174,
`trust-mutants-allow.json` 19, DELTA 12, `docs/trust-baseline.json` +7 (written by the tool). This REPORT is not
counted.

## Step 1: measured before any edit (tree `c81d6a9d9`, the branch's first base)

- **Trust**, per definition (`tools/trust_map.walk`, the classification `tools/trust_map.py` reports; probe script
  below): `Norm/Run.lean` G[V] `opensStatement` 8, `sentenceBytes` 6, `statementSpans` 14, `oneSpans` 6, `Reader` 4,
  `leanReader` 2; D[V] `answerWith` 7, `outcomeFields` 16. `Norm/Rules.lean` G[V] `normTags` 3. `readNorm` is G[V]
  tied (by `readNorm_sound`, `readNorm_complete` and `readNorm_numbered`), so it counts 0. Total over these
  definitions: 66. Whole tree: trusted 63,309.
- **E17 through the mode** (`Run.answer "c" caseTwo (big 300)`: 300 blocks, 9,791 characters, `one` with 300 rows).
  Run with `lake env lean --run /tmp/cutback/E17Time.lean`, i.e. **interpreted, not compiled**, on the VM (32 cores,
  load average 47/56/59 at the start and 45/54/58 at the end): 22,181 ms, 22,167 ms and 22,202 ms. Parts, with the
  input made to depend on the clock so that no closed term is hoisted (`E17Parts.lean`): the second lex plus the
  span fold (`statementSpans source`) took 64 ms and 75 ms; the grammar rebuild (`normTags`) took 29 ms and 8 ms;
  `answer` took 22,538 ms and 21,682 ms. So the duplicates cost about 0.3% of E17; the rest is `readNorm`.
- After the change, on the same host at a much lower load (2.3 at the start, 12.7 at the end): 14,629 ms, 15,045 ms
  and 21,908 ms. That is UNVERIFIED as a comparison: the load differs and the run-to-run spread is larger than the
  0.3% saved. The claim is "each value is computed once", shown in the code below, not a speed-up.

```
# /tmp/cutback/perdef.py (the per-definition probe)
import sys; sys.path.insert(0, "tools"); import trust_map
for d in trust_map.walk()[0]:
    if "EnglishGrammar/Norm/" in d.module and d.trusted: print(d.module, d.cls, d.decl.lines, d.decl.name)
```

## What was built (task deliverables)

| Deliverable | Delivered by | Evidence |
|---|---|---|
| (1) The reader shares the sentence byte positions and the grammar: no second `lexSpans`, no second `normGrammar E L` per request | `Norm/Read.lean:20` `readNormOn`: `readNorm`'s checks, `readDocument` and `assemble` on a given grammar `G` and the `lexSpans` sentences (it erases the positions itself). `readNorm` (`:38`) is `readNormOn E O L b (normGrammar E L) (lexSpans s)`, and `readNorm_on` (`:42`, `rfl`) states it. `Norm/Run.lean:148` `answerWith` builds `normGrammar c.E c.L` (`:153`) and `lexSpans source` (`:154`) once and hands both to the reader (`Reader.read`), to `outcomeFields` (`oneSpansOf lexed`, `:73`, then `statementSpans`, `:62`) and to the tags (`Thunk.mk (R.tags G)`, forced only for `many`). `leanReader` (`:160`) is `readNormOn` at `workBudget` and `G`'s rule tags. `normTags` is deleted. | The code, one call of each per answer; E1-E17; `tests/test_english_statement_blocks.py::test_the_rule_tags_are_forced_only_for_many` (1 passed); f18 (many through the real reader, `RunExamples.lean:252`) |
| (2) No answer changes | Every E-fixture's expected value is unchanged. The span guards of E1, E13 and the non-ASCII text now pass the sentences (`sents s`, `RunExamples.lean:20`) to `statementSpans`, since it reads positions: same values. `tests/test_english_statement_blocks.py` is not edited. | `lake build` (1406 jobs) with every `#guard`; the final selected run (below) |
| (2) New `#guard`: the spans read from the shared positions equal en-e3a's `statementSpans source` | `RunExamples.lean:120-133`: `lexedTwice` is en-e3a's `statementSpans` verbatim (it lexes the source again). The guard checks it against `Run.statementSpans (sents s)` on E1, E13, "Rule 1. Zoë.\nRule 2. Y." and "Rule 1. Café.\nExcept when ü.\nRule 2. 日本.", and checks that the span count equals the number of "Rule " headers, so that an empty answer cannot pass. | It fails under seeded bugs 1 and 2 (`mutants.json`) |
| (3) Trust cut-back of at least 17 lines | **Not reached: +6** (see "Trust") | `uv run python tools/trust_map.py --check` |
| Seeded bugs (the task's three, plus one per changed trusted definition) | `docs/english-lean/en-e3a-cutback/mutants.json` (9 bugs, all caught) | below |
| Trust-mutants sweep | `docs/english-lean/en-e3a-cutback/trust-mutants.json` (with the `-allow.json` file) | below |
| Condition tests stay selected | `tests/test_english_statement_blocks.py`, E17, and the span-equality guard (in `RunExamples.lean`, built by `lake build` and through `test_english_statement_blocks`' `lean_build("VE")`) | `tools/select_tests.py --base 08f3c2af9` lists `tests/test_english_statement_blocks.py` |

**Deviation (recorded here, not in the spec): the direction of sharing is inverted.** The ruling asks that
`readNorm`, or a wrapper the reader calls, *return* the positions and the grammar. Here the mode computes both once
and *hands them to* the reader. The reason: `Run.Reader`'s shape is fixed by
`tests/test_english_statement_blocks.py` (which the task forbids editing except to name a guard). Its
`panicking` reader is `⟨fun _ _ _ _ _ => o, fun _ _ => panic! …⟩` with `o : NormOutcome`, so `read` must return
the outcome alone. Lean's anonymous constructor refuses a third (defaulted) field: probe `/tmp/cutback/Anon.lean`
gave "Insufficient number of fields for `⟨...⟩` constructor: Constructor `S.mk` has 3 explicit field, but only 2
were provided". The effect is the same: one `lexSpans`, one `normGrammar` per request. Evaluation order changes
slightly: the grammar and the lex now happen before `readNorm`'s lexicon check, so an `invalidGrammar .lexicon`
answer also pays for them. That is a cost on an error answer, bounded by the request; no byte changes.

**Theorem statements.** None of `Run.lean`'s answer theorems (`answer_misplaced`, `answer_stopped`,
`answer_one_iff`, `answer_one_rows`, `answer_partial_no_node`) changes; their proofs add `← readNorm_on`.
`Run.oneSpans s rs` keeps its statement form: `oneSpans` (`Run.lean:78`) is now `oneSpansOf (lexSpans source) rs`,
which is exactly what the answer computes, by `rfl`. `lean/statements.txt` against the merge base (`git diff
08f3c2af9 -- lean/statements.txt`) shows one added theorem (`readNorm_on`). It also shows `readNorm_eq`'s entry
with the same statement text but a different `uses` line and `expr` hash: its `match lex s` now names the auxiliary
matchers `readNormOn.match_*` and `readNorm_eq.match_1` instead of `readNorm.match_*`, because the body moved. I
read this as no statement change (same text, same meaning); "Notes for the DRI" flags it. The encoder file from
main (`ResponseShape/Encoders/EnglishStatement.lean`, en-e3b) needed its proofs adapted: its section lemmas
(`outcome_fits` and the per-outcome lemmas) take `outcomeFields`' new `lexed` argument, and `noSource_of_oneSpans`
keeps its statement, proved from a new `noSource_of_oneSpansOf`. `statementCaseReported_fits`, the only one the spec
names (en-e3-norm.md 4), is unchanged.

## Trust

`uv run python tools/trust_map.py --check` on the final code, against `08f3c2af9`: **K +0, S +0, D +4, G +8, tied
+6, trusted +6** (`Norm/Run.lean` +9, `Norm/Rules.lean` -3). This is recorded with `tools/trust_map.py --allow`
(`docs/trust-baseline.json`), signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), en-e3a-cutback, 2026-10-18".
R16's conditions hold: at most 150, no K growth, and every new or changed trusted definition is exercised by a check
that can fail (`mutants.json`, the sweep). FOLLOW-UPS.md has its row under "## en-e3a-cutback".

| Definition (class) | before | after | change |
|---|---|---|---|
| `Run.opensStatement` (G[V]) | 8 | 8 | 0 |
| `Run.sentenceBytes` (G[V]) | 6 | 6 | 0 |
| `Run.statementSpans` (G[V]) | 14 | 12 | -2 (no `lexSpans` call) |
| `Run.oneSpans` (G[V]) | 6 | 3 | -3 (now `oneSpansOf (lexSpans source)`, the statements' vocabulary) |
| `Run.oneSpansOf` (G[V], new) | - | 6 | +6 (old `oneSpans`' body on the shared sentences) |
| `Run.Reader` (G[V]) | 4 | 6 | +2 (field types and a docstring) |
| `Run.answerWith` (D[V]) | 7 | 10 | +3 (the grammar and the lex, once) |
| `Run.leanReader` (G[V]) | 2 | 4 | +2 (`readNormOn` at `workBudget`, the grammar's tags, `normTags`' docstring) |
| `Run.outcomeFields` (D[V]) | 16 | 17 | +1 (the `lexed` parameter) |
| `normTags` (G[V], Rules.lean) | 3 | - | -3 (deleted) |
| `readNormOn` (G[V], new) | - | 19 tied | 0 (the body `readNorm` held, tied by `readNorm_on`; `readNorm` stays tied) |
| **total** | 66 | 72 (+19 tied) | **+6** |

**Why the cut-back was not reached (under 17 by 23).** Ruling item 3 expected the cut to come from "these three
definitions' duplicate of what `readNorm` already computes". They duplicate nothing `readNorm` computes. `readNorm`
reads `lex`, which erases the positions; it never decides where a statement's bytes begin or end. `opensStatement`,
`sentenceBytes` and the fold in `statementSpans` turn positions into spans, and the answer needs that wherever the
positions come from. The real duplicates were the `lexSpans` call in `statementSpans` (2 lines) and the grammar
rebuild in `normTags` (3 lines), and both are gone. Sharing the values instead costs glue: the reader's field
types, the two `let`s in `answerWith`, and `oneSpans` kept as the vocabulary of `answer_one_iff`/`answer_one_rows`,
whose statements this item may not change. I found two ways to reach -17, and neither is honest:
- Collapse the three definitions into one dense fold. `tools/trust_changes.py` flags trusted code written onto
  fewer, longer lines, and the code would be harder to review.
- Mark the span code "tied" with theorems that restate the definitions. That moves trust out of the count without
  removing any.

Neither was done. A real reduction needs the span logic tied to a theorem about the reader, for example that every
header or precedence sentence of a `one` reading opens with "Rule". That is new proof work.

## Seeded bugs (`docs/english-lean/en-e3a-cutback/mutants.json`; all Lean, each planted, built, restored)

| # | File, definition | Bug | Caught by |
|---|---|---|---|
| 1 | `Norm/Run.lean` `statementSpans` | a continued block's span drops its period byte (`b - 1`) | `RunExamples.lean`:29, 30 (E1), 107 (non-ASCII), 113, 115 (E13), **132 (the new span-equality guard)**, 200 (E17) |
| 2 | `Norm/Run.lean` `opensStatement` | reads the second token (`sent[1]?`) | `RunExamples.lean`:29, 30 (E1), 92, 107, 113, 115 (E13), 132, 200 |
| 3 | `Norm/Run.lean` `leanReader` | the tags side returns an empty array | `RunExamples.lean`:252 (f18, `many` through the real reader) |
| 4 | `Norm/Run.lean` `oneSpansOf` | accepts a translation-mode statement | `RunExamples.lean`:84 (E11), 87, 168, 172 |
| 5 | `Norm/Run.lean` `oneSpans` | lexes another text than the answer | `Run.answer_one_iff`, `Run.answer_one_rows` (the build stops) |
| 6 | `Norm/Run.lean` `outcomeFields` | reads no sentences for the spans | `Run.answer_one_iff`, `answer_one_rows`, `answer_partial_no_node` |
| 7 | `Norm/Run.lean` `answerWith` | hands `outcomeFields` other sentences than the reader's | the same three theorems |
| 8 | `Norm/Run.lean` `leanReader` | reads at budget 0, not `workBudget` | `Run.answer_misplaced`, `answer_stopped`, `answer_one_iff` |
| 9 | `Norm/Read.lean` `readNormOn` | drops each sentence's last token when erasing positions | `readNorm_eq` (`Read.lean:91`) |

`Run.Reader` (a structure) was not mutated: changing a field's type is refused by Lean wherever the field is used.
Its contract is exercised by every bug above and by the thunk test. No Python or Rust product code changed.

## Trust-mutants sweep

`zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/english-lean/en-e3a-cutback/trust-mutants.json
--test lean/VE/EnglishGrammar/Norm/RunExamples.lean` selected 2 definitions (`statementSpans` 40 mutants,
`leanReader` 10). The other changed definitions have no line the operators mutate; seeded bugs 4-9 cover them by
hand.
- First run at `abc280a49` (cloud, GitHub Actions shards): 44 KILLED, 1 SURVIVOR, 3 UNKNOWN, 2 INVALID.
  - The SURVIVOR is M043, `(acc.reverse.take 1).getLast?` for `acc.getLast?`: equivalent; en-e3a allowed the same
    class.
  - The UNKNOWNs are M002, M006 and M011: Lean refusing the mutated text (`[]` with no element type, "Type
    mismatch", "contains metavariables").
  - All are allowed with reasons in `trust-mutants-allow.json`; the rescore exited 0.
- Final record, after the main merge (`--rescore` of that run; it ran in full because the tool's inputs changed),
  on ve-cloud-2: **44 KILLED, 0 SURVIVOR, 0 UNKNOWN, 2 INVALID, 4 ALLOWED, 0 NOT RUN; exit 0**.

## DELTA

`docs/english-lean/en-e3a-cutback/DELTA.md` has one row: English `actions_version` 47 -> 48. Base spec 2.12
requires the raise because `Norm/Read.lean`, `Rules.lean` and `Run.lean` are hashed in `ve/english_grammar/LOCK.json`
(`tools/english_grammar_gen.py` refuses the changed hashes otherwise). Ruling cell: SIGNED by the DRI 2026-11-02
(jt-3p item 3, the standing precedent for this class). The task expected no DELTA row; this one is forced by the
lock, not by a change of behaviour. The goldens that carry the version (`s3-fixture-comparison.json`, 170 rows,
the version alone) were regenerated by `tools/regen_generated.py --write`.

## Checks run on the final code

- `cd lean && lake build`: "Build completed successfully (1406 jobs)" (after the main merge).
- `python3 lean/audit.py`: "PASS: 854 source files; 9562 named theorem declarations audited".
- `uv run python tools/trust_map.py --check`: passes with the allowance (above).
- `uv run python tools/english_grammar_gen.py --check`: no output, exit 0.
- `uv run python tools/regen_generated.py --write`: exit 0; `tools/lean_statements.py`: "removed: 0, changed: 0"
  against the merged inventory.
- `uv run python tools/gate_collection.py --check --prebuilt`: "33793 collected … 0 refused, 0 stale and 0
  malformed".
- `uv run pytest -q tests/test_english_statement_blocks.py -k forced_only_for_many`: 1 passed.
- Final selected run, on committed code (`MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base 08f3c2af9 --run`,
  HEAD `7f83b4f49`, ran on ve-cloud-3, 11,882 s): "recorded 465 units for tree 018ea78c7e; … 1 failed". The failed
  unit is `tests/test_assurance_manifest.py` (3 failed, 149 passed): its whole-file pin of `Norm/Run.lean` was 303
  lines, and the file is now 312. Fixed in `b81b56f9b`: re-pinned in `ve/assurance-manifest.json` after a review of
  the ranges (the whole file stays pinned, and every listed declaration is still there), and
  `docs/spec/assurance-manifest.md` regenerated. The 3 failed ids were rerun on ve-mac-1: "3 passed".
- `6aefd9a7e`: `tools/trust-classes.json` and `docs/trust-baseline.json` rewritten in the merge base's order (the
  merge had reordered modules and allowances). Compared as JSON with the base, only this item's entries differ.
  `trust_map.py --check` and `regen_generated.py --check` both exit 0 after it. Neither commit changes Lean, so the
  sweep record and the selected run stand for the code.

## Pilot bytes expected to move

None of the statement mode's: it is not the authority yet (en-e3). Every English answer that carries
`actions_version` changes that one string, "47" to "48" (DELTA).

## Next item

en-e3 (EN-3: the statement mode becomes the authority), after en-e3b. Nothing of this item is left undone except
the trust target, which this item cannot reach honestly (above).

## Notes for the DRI

- Item 1 of `dri-decisions-20261109-en-e3a-2.md` signed en-e3a's +167 on the condition that this cut-back would
  follow. It returns -5 of the duplicated lines but adds +11 of glue, net +6 (above). Whether en-e3a's signature
  stands, or a ties pass (the FOLLOW-UPS row) is required, is your call. No reserved signature is written.
- `readNorm_eq`: the statement text is unchanged; only the matcher names in its dump moved, because the body is
  now in `readNormOn`. I took the conservative reading (no statement change) and did not ask.
- E17 costs about 22 s interpreted, and 99.7% of it is `readNorm`. The duplicates were about 0.3%.

## Spec re-read

- M10 (lexer's sentences and the opening "Rule" sentence) against `docs/spec/en-e3-norm.md:166-172`: unchanged
  semantics; `statementSpans` takes `lexSpans`' sentences, as M10 says.
- `oneSpans source rs = some sps` in `answer_one_iff`/`answer_one_rows` against `docs/spec/en-e3-norm.md:1093-1099`:
  text unchanged.
- 2.3's `answer = answerWith ⟨readNorm, normTags⟩` (`docs/spec/en-e3-norm.md:517-518`) is now
  `answerWith ⟨readNormOn · · · workBudget, the grammar's tags⟩`. This is a stub deviation, recorded here.
  `normTags` (`:129`, an `opaque` in the stub) is deleted in the product.
- `statementCaseReported_fits` against `docs/spec/en-e3-norm.md:1126`: unchanged.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained answers: N.A. No schema, relay or wire field changes; `statementCaseReported_fits` still
   holds (lake build).
2. Deliverables: PASS except (3), which is reported as not reached ("Trust"); the table above maps each
   deliverable to its evidence. No Python copy of a Lean decision; en-e3b's test file is untouched.
3. Tests can fail: PASS, `mutants.json` (9 seeded bugs) and `trust-mutants.json` (exit 0).
4. Python, Lean and Rust agree: N.A. No Python or Rust product change; the E-fixtures' expected bytes are
   unchanged (lake build).
5. R8 binding: N.A. No new answer field.
6. Gate evidence: PASS. Main merged at `ad377e955`; the final selected run is on committed HEAD `7f83b4f49`.
   Two commits follow it: `b81b56f9b` (the manifest re-pin; its 3 failed ids rerun, 3 passed) and `6aefd9a7e`
   (trust tables in base order). Both are listed above; the chain's gate runs on the final HEAD.
7. Unsigned items: PASS. The DELTA row cites jt-3p item 3; trust +6 cites R16; the missed target is in the first
   line.
8. User-visible changes in DELTA: PASS. The `actions_version` raise is the only one; `s3-fixture-comparison.json`
   regenerated.
9. Selection: PASS. `tools/select_tests.py --base 08f3c2af9` selects 466/593 units, including
   `tests/test_english_statement_blocks.py`.
10. Lean statements: PASS. Seeded bugs 5-9 break `answer_one_iff`, `answer_one_rows`, `answer_partial_no_node`,
    `answer_misplaced`, `answer_stopped` and `readNorm_eq`.
11. Budgets fail closed: PASS. Seeded bug 8 (budget 0) breaks the answer theorems; E17 ends `one` and 330 blocks
    give `TextTooLong` (`RunExamples.lean:200-203`).
12. No CPU or memory regression: PASS. One `lexSpans` and one `normGrammar` per answer (`Run.lean:153-154`); E17
    timings above (UNVERIFIED as a benchmark).
13. Test-removed trailers: N.A. No test removed (`gate_collection.py --check --prebuilt`: 0 removed).
14. Both directions, cited evidence, spec re-read: PASS. The span guard holds on four texts and fails under bugs 1
    and 2; claims cite commands; spec re-read above.
15. Overclaim, silent cut, checks fail, limits: PASS. The missed cut-back is stated, not hidden; every new guard
    has a bug that breaks it; values are read once (`answerWith`).
