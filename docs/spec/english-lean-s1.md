# English in Lean: S1a and S1b report, with the Lean part of the English instance

**Status:** report of the Lean work item of [english-lean-PLAN.md](english-lean-PLAN.md) and
[english-lean.md](english-lean.md) (the **spec**), 2026-10-04, branch `english-lean/lean` from `d3910cf4`.
It applies the DRI's rulings on the S0 measurements of 2026-10-04 (section 5). Nothing here changes a
verdict, an identity, a public code, a frozen file or an existing theorem statement: every Lean file is
new, and `english.admission` keeps `authority: python`.

In one paragraph: the generic engine of spec 5.2 to 5.7 is written, measured and proved. Every budget of
G1a that can be measured without S2 is met, with deterministic step counts equal to the Python reference
of S0. Every statement of spec 5.3 to 5.7 is a theorem, with only the standard axioms (G1b). Their
elaboration forced instance-argument and body corrections only, listed in section 3 for the DRI's check.
Of the English instance (tier B), the tokens with the `glued` flags, the lexer, the rejections, the
folding agreement, `wordingKey`, `negativeTemplate` and `Lexicon.valid` are written and tested. The
rule construction, the action library, `read` and the theorems of spec 5.8 are S2 and not started
(section 6).

## 1. What was built

| File | Content | State |
|---|---|---|
| `lean/VE/Grammar/Basic.lean`, `Derives.lean` | spec 5.2, 5.3 | `yield_ne_nil` proved |
| `lean/VE/Grammar/Table.lean` | the parser of spec 2.6: rows from the last start position, rules in increasing rank, rule-suffix entries, shared witnesses, the cap invariant, the step counter, the last pass; indexing of every rule and suffix position by its first symbol (a terminal or a nonterminal) | executable |
| `lean/VE/Grammar/TableInvariant.lean` | the cap invariant, in four layers: buckets (`Bucket.addAll_spec`), one combination (`combine_ok`), one row (`ntRowGo_ok`, `sufGroups_ok`, `rowAt_ok`), the rows (`fill_ok`) | proved |
| `lean/VE/Grammar/TableProofs.lean` | the statements of spec 5.4 | proved |
| `lean/VE/Grammar/Meaning.lean` | spec 5.5, `sem_total` | proved |
| `lean/VE/Grammar/Reading.lean` | spec 5.6 | proved |
| `lean/VE/Grammar/Extension.lean` | spec 5.7 | proved |
| `lean/VE/EnglishGrammar/Token.lean` | tokens, terminals, `Terminal.accepts`, `terminatorFree` (W4) | tier B, tested |
| `lean/VE/EnglishGrammar/Lexer.lean` | `lex`, `lexSpans` (spec 2.2 with the S0 choices) | tier B, tested |
| `lean/VE/EnglishGrammar/Syntax.lean` | `ETerm`, `EFormula`, `Reject` with `Reject.code`, `DState`, `Ty` | tier B drafts |
| `lean/VE/EnglishGrammar/Lexicon.lean` | `wordingKey`, `negativeTemplate`, `Env`, `Overlay`, `Lexicon`, `Lexicon.failures`, `Lexicon.valid`, `workBudget` | tier B, tested |
| `lean/VE/EnglishGrammar/FoldAgree.lean` | `foldChar_agrees`: the English folding table equals the discourse one (R13) | proved |
| `lean/VE/EnglishGrammar/Examples.lean`, `EngineExamples.lean` | the fixtures of spec 8.1 to 8.5 and e27 as `#guard` checks | pass |
| `lean/EnglishLeanBenchMain.lean`, `bench/english_lean_g1a.py` | the G1a measurement (`ve_english_lean_bench`, not a default target) and the lexer differential (`--lex`) | measurement only |
| `tests/test_english_lean_tables.py` | the copied idiom, irregular-verb, past-verb and whitespace tables equal Python's | pass |

`VE.Grammar.*` and `VE.EnglishGrammar.*` are layer 3 (`tools/layer_policy.py`, spec section 6). Every new
file under `lean/VE/` has its line in `lean/VE/Route/frozen-sources.sha256`, and every theorem (134) its
`#print axioms` line in `lean/VE/Audit.lean`. `lean/audit.py` passes: standard axioms only.

## 2. G1a: measurements

Input: `bench/english_lean_g1a.py` writes, from the S0 tools of branch `english-lean/py`, 51 grammars over
the English tokens with 1,225 sentences: the rendered corpus of S0 (17 configurations, 60 texts each, over
Python's grammar converted to word tokens); the 20 longest of them made to fail at their end; 51
rendered sentences of 280 to 564 tokens; 100 sentences over the synthetic limit environments of S0, with
the attribute-property product factored as spec 2.10 prescribes (largest: 1,640 rules); and a saturating
ambiguous grammar on runs of 10 to 300 tokens. Each sentence is parsed with cap 2; time is the least
thread CPU time of three repetitions.

**Steps are deterministic and equal the Python reference.** On all 1,225 sentences, Lean's step counter
gives the same count as the reference engine of S0 (`conformance/english_lean_engine.py`). The engine
fixtures g16 (no result below 49 steps, the result of g5 from 49 on) and g17 (599 steps on forty `a`)
give S0's figures.

Latency was measured twice: run 1 before the change of `fold` to the spec's definition (section 3, E7),
at an unrecorded load; run 2 after it, at a load average of 67 on 32 CPUs. Thread CPU time still rises
under such load (shared caches), so run 2 is an upper figure.

| Kind | Sentences | Longest (tokens) | Steps max | ms p50 / p95 / max, run 1 | run 2 |
|---|---|---|---|---|---|
| corpus | 1,020 | 266 | 208,248 | 0.48 / 1.93 / 8.0 | 0.87 / 3.36 / 12.7 |
| failing prefixes | 40 | 267 | 208,986 | 2.96 / 6.75 / 7.0 | 5.43 / 12.45 / 12.7 |
| long (280 to 564 tokens) | 51 | 564 | 525,742 | 6.25 / 14.5 / 16.0 | 11.2 / 28.2 / 31.0 |
| limit environments | 100 | 162 | 1,031,756 | 2.87 / 20.4 / 33.8 | 4.05 / 26.0 / 38.0 |
| ambiguous (saturating) | 7 | 300 | 271,503 | 39.0 / 234 / 234 | 47.0 / 224 / 224 |

| Budget (plan section 5, DRI ruling 5) | Measured | Verdict |
|---|---|---|
| corpus sentence p95 ≤ 20 ms | 1.93 ms (run 2: 3.36 ms) | met |
| 150-token sentence ≤ 50 ms | worst sentence of 140 tokens or more (95 of them, up to 564 tokens): 33.8 ms (run 2: 37.8 ms), at limit size | met |
| design point 300 tokens (ruling 5) | 26 sentences of 250 to 320 tokens: at most 276,242 steps, 10.2 ms (run 2: 15.7 ms) | met |
| work budget 2,100,000 steps (ruling 5) | no sentence above 1,031,756 steps | met |
| grammar preparation ≤ 100 ms | 28.8 ms at 1,640 rules and 596 distinct terminals | met |
| peak memory (no budget fixed) | above the runtime's 88 MB baseline: under 1 MB on corpus and long sentences, 5 MB at limit size, 14 MB on the 300-token saturating input | recorded |
| BlueDot document ≤ 1 s | not measured: the pilot documents are not yet read through the S2 harness | open (S2) |
| Lean build ≤ 60 s for generated rule modules | no generated module exists yet | open (S2) |

**Time per step.** The median is 33 ns per step (run 1). It rises to 0.6 to 0.94 µs per step on the
saturating grammar, where every step is a combination that builds a tree (on English grammars most steps
are failed attempts). At the work budget that is at most about 2 s per sentence, against Python's
30-second wall clock. A run-aware merge sort in place of `List.mergeSort` saved only about 20% there and
was not kept, because the proof uses `mergeSort_perm`.

**Indexing.** Each row computes once per distinct terminal whether it accepts the row's token, and fills
only the suffix entries whose first symbol has something at the row. A skipped attempt is still charged
as a step, so the counter is that of spec 2.6 without indexing; the proof covers the indexed parser.

## 3. Elaboration of spec 5.2 to 5.7 (for the DRI's check)

Every definition and theorem type of 5.2 to 5.7 elaborated under Lean 4.24.0. The corrections that
elaboration forced are listed below. None changes the meaning of a statement. The theorems were proved
after G1a's measurement passed, and before the DRI checked this list; if the DRI rejects an item, the
proofs that depend on it are redone.

| # | Correction | Where | Kind |
|---|---|---|---|
| E1 | `parse`, `verdict`, `readSentence`, `readDocument` and the statements about them also take `[DecidableEq K]`: the parser indexes the distinct terminals of the grammar | `Table.lean` and on | instance argument |
| E2 | `OneReading`, `DocOneReading`, `one_reading_unique`, `one_reading_single` and `doc_unique` take no `[DecidableEq T]` (spec 5.1: an instance argument belongs to the declarations that use it) | `Reading.lean` | instance argument |
| E3 | `DecidableEq (Tree T)` is written by hand (`Tree.decEq`): the type is nested | `Derives.lean` | allowed by spec 5.3 |
| E4 | bodies of signatures: `parse` (the algorithm of section 1), `Grammar.typed` (the text of spec 5.5), `toArgs` (a cast along the type equality that `S.decEq` decides), `readDocument` (structural recursion; `stopped` returns the state before the sentence), `RuleMap.tree` (with a mutual `RuleMap.trees`) | | definitions |
| E5 | the invariant lemma is stated over buckets, as `BOk` (sorted end positions, each at most `w.size`; per end position the four clauses of `EntryOk`); `Span` and `EntryOk` are defined exactly as in spec 5.4 | `TableInvariant.lean` | internal, as spec 5.4 allows |
| E6 | after every `mutual … end` block the namespace is closed and reopened, as spec section 6 asks | | audit |

No item of 5.2 to 5.7 is still a `Prop`-valued definition: all are theorems.

Tier B changes from the spec's 5.8 block, all inside the English instance:

| # | Change | Reason |
|---|---|---|
| T1 | `Tok.punct` carries `gluedBefore` and `gluedAfter`; `terminator` becomes the list `terminators` of the four spacings of `.`; `terminatorFree` checks all four | DRI ruling 1 (O1) |
| T2 | `Reject` gains `coefficientNotNumeral`; `blockedWordingIds` lists `natural-negation` and `risk-every-cannot`; `Reject.code` gives the public codes of spec 4.2 | DRI ruling 3 |
| T3 | `Env` and `Overlay` are the lexical views that `Lexicon.valid` reads (declared wordings, nouns, display forms, arities, and the forms the profile blocks fix); S2 decodes them, S3 computes the profile forms | spec gave signatures only |
| E7 | `fold` is `s.map foldChar`, as the spec writes it; a copy-free variant measured 10 to 25% faster on the 596-terminal limit grammar and was not kept | spec 5.8 |

## 4. Fixtures and differentials

- **Engine corpus** (spec 8.1 to 8.3, 8.7) on the Lean parser with the English tokens: g1 to g17, g20,
  m1 to m5, r1 to r10, q1 to q3 pass (`EngineExamples.lean`). g18 (random grammars against an exhaustive
  enumerator) stays with the Python harness of S0. q4 is a statement about `RuleMap.Ok`, a `Prop` with no
  decision procedure; q5 and q6 need the S2 rule construction.
- **Lexer** (spec 8.4): x1 to x17 pass, with the `glued` flags (`Examples.lean`). Differential against the
  Python reference lexer of S0 (`ve_english_lean_bench --lex`, run for this report, not a suite test): on
  6,080 sources (the 1,020 rendered corpus texts, the lexer fixtures, 3,000 random strings over quotes,
  escapes, punctuation, digits and five non-ASCII characters, and 2,040 comma-spacing mutants) every
  token, byte span, rejection and offset agrees, and every `glued` flag equals the adjacency in the
  source.
- **Matching** (spec 2.3, g11 to g14) and W4 (e27) pass.
- **Lexicon validity** (spec 8.5): v1 to v12 pass, with each case's failing conditions exactly as the spec
  lists them, and a V1 case for an unworded generated predicate (ruling 2).
- **Folding**: `foldChar_agrees` is a theorem, not a test.

## 5. The DRI's rulings of 2026-10-04, as applied here

| Ruling | Applied |
|---|---|
| 1. O1 spacing: no silent widening; `glued` flags | T1. `deployed , it`, `deployed,it`, `non - compliant` and `non -compliant` lex to tokens other than the accepted spellings' (fixtures in `Examples.lean`), so a rule written for the accepted spelling does not read them. The Python reference lexer does not yet carry the flags; it must add them before S2 compares tokens (section 6) |
| 2. No V1 exemption for `risk__more_severe` | `Lexicon.valid` exempts no generated symbol; a fixture checks it. Listing `usecases/asimov-extended` as a known V1 failure belongs to the measurement file on `english-lean/py` |
| 3. `coefficientNotNumeral`; ids `natural-negation`, `risk-every-cannot` | T2 |
| 4. Lint sort | The ported codes are V3 (holes of `TEMPLATE_SHAPE`), V4 (`DUPLICATE_TEMPLATE`, `SORT_COLLISION`) and V5 (`NEGATIVE_NOT_NEGATION`, `NEGATIVE_WITHOUT_POSITIVE`) of `Lexicon.valid`; the rest stay Python checks |
| 5. Design point 300 tokens; budget 10 times the largest reference parse | `workBudget` = 2,100,000 steps (largest corpus parse: 208,248 steps); section 2 |

## 6. Not done

S2 and later, not started on this branch:

- the fixed rules: the JSON sources under `ve/english_grammar/`, their generator and `--check`, the
  generated `VE/EnglishGrammar/Fixed/*.lean`, and the lock file with `actions_version` (Python side
  first);
- `lexRules`, `grammar`, `ty`, `acts`, `sig`, the action library and `meaning`; `EFormula.encode` and
  `typedDocument`; `read`, `EnglishOneReading`, `checkRendering`;
- the statements of spec 5.8 (`read_ok`, `read_complete_english`, `english_reading_unique`,
  `start_sentence`, `meaning_total`, `checked_rendering`): they need the definitions above;
- the service modes `english.read` and `english.grammar`, the identities of spec 2.12, the Python
  adapter and the shadow wiring;
- the `glued` flags in the Python reference lexer and in `conformance/english_lean_tokens.py`, so that
  the S2 comparison runs on equal tokens;
- the remaining G1a figures: the BlueDot document and the build time of generated modules.

Known test failure under load: `tests/test_w6a_limit_generator.py::test_lean_authority_reports_resource_limit_on_every_generated_case`
fails on the Rust checker's 5-second wall clock at load averages above 60 (recorded before this item);
it touches nothing this branch changes.
