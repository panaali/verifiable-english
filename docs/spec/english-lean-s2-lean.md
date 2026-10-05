# English in Lean, S2: the Lean work item (record)

Status: record of branch `english-lean-s2/lean`, 2026-10-05, for the S2 plan ([english-lean-S2-PLAN.md](english-lean-S2-PLAN.md),
draft 6) and its statement spec ([english-lean-s2.md](english-lean-s2.md), draft 5, the **spec**). It covers the Lean
rows S2.1, S2.2 and S2.3. The Python rows (S2.0, S2.5, S2.6) and S2.4 are not in it.

## 1. What was built

| Plan row | Done | Where |
|---|---|---|
| S2.1 grammar construction | yes: the catalogue, `ty`, the ranks, the 88 fixed rows, `lexRules`, `grammar`, `Env.decode` with the signatures; `grammar_rules`, `start_sentence`, `lexRules_terminatorFree` proved; spec 8.1 b1 to b55, d1 to d4, k1, k2 and the obligations c1 to c3 reproduce | `lean/VE/EnglishGrammar/Catalogue.lean`, `Fixed/RelationalFol.lean`, `Rules.lean`, `Encode.lean` |
| S2.2 actions and meaning | yes: the action library of spec 2.7 as `fixedActs ++ lexActs E L`, the context, the side conditions with the four new codes; spec 8.2 e29 to e53 reproduce, e51 to e53 included; the two source tests | `Actions.lean`, `Read.lean`, `tests/test_english_lean_s2.py` |
| S2.3 readers and statements | yes: `read`, `translate`, `checkRendering`, `EnglishOneReading`; all fourteen statements of spec 5.6 proved, each equal to the approved text up to whitespace (a test), standard axioms only | `Read.lean`, `Extends.lean`, `VE/Audit.lean`, `lean/axioms.txt` |
| S2.4 service | no (section 4) | |

Every fixture of spec section 8 that names Lean is a `#guard` in `lean/VE/EnglishGrammar/ReadExamples.lean`: the
verdicts of 8.1 (117 rules, `|G|` = 479, 37 nonterminals, the longest fixed right-hand side 28), the meanings of
8.2, l1 to l4 and m1 to m5 of 8.3, tr1 to tr4 of 8.4, w1 to w7 of 8.5 on `GF` plus the three proposed rows, the
steps of 8.6 (7,331, 13,162 and 2,514, unchanged), q5 to q7 of 8.7 on the decidable parts of `Extends`, and
the wire form of every AST constructor against Python's `_to_data`. The tier B changes the spec names are in:
`Reject` gains the four codes, `Ty` the ten types, `Terminal` gains `kwMid`, `Env` the signatures and `source`,
and V3 the one-sentence condition (Q6), in Lean and in the Python reference `conformance/english_lean_lexicon.py`.

A throwaway differential ran Python's dispatched unit (hand parser, Lark audit, `check_document`) on the 88
fixture sources of `F` and its variants: acceptance, formulas and marks agree wherever Python's producer selects
the fixture's wording. e51, e52 and e53 differ only because Python's producer refuses those constructed
wordings (`TEMPLATE_SHAPE`) and selects the quoted fallback; under the fixture lexicons Lean gives the spec's
expected outcomes.

## 2. Elaboration choices

The spec fixes statements, fixtures and behaviour; these are the choices it left to the implementation.

| # | Choice | Why |
|---|---|---|
| L1 | A module `Catalogue.lean` holds the catalogue, `ntTy`, `ranks`, `FixedAct` and `FixedRow` (spec 5.1 puts the catalogue in `Rules`) | the generated table names the actions and the nonterminal indices, and `Rules` imports the table |
| L2 | `fixedActs` has one action per fixed row, so a fixed rule's `act` is its row index; a row carries its action's name and data, as the JSON's `act` field does | `fixedActs` stays one closed array; the generator needs no index table |
| L3 | `Fixed/RelationalFol.lean` was written in the generator's output format by a script that is not committed; S2.0's `tools/english_grammar_gen.py` must write the same `FixedRow` literals or replace the file | S2.0 is the Python implementer's |
| L4 | An action's argument types are its rule's right-hand-side types; when the children do not have the shape the action reads, the action is `unfit` (no arguments, type `unit`), which `Grammar.typed` refuses, so `read` reports `invalidGrammar notTyped` | no action needs a fallback value, so none names `Reject.internal` |
| L5 | A clause's first term keeps `leftmost` only when the rule begins with a term | the hand parser drops an alternative whose `it` is not at the formula's start (`english.py:1071–1073`); spec 2.7's "the first term keeps `leftmost`" would otherwise resolve `it` in a wording that begins with a word, which Python refuses |
| L6 | A lexical row is built from one lexicon entry and, where the family needs a sort, from every declaration of that name; repeated rows are dropped (the engine's `dedup`), and so are rows with a terminal that accepts a terminator | `grammar_extension` then holds for every environment, repeated declaration names included, and `lexRules_terminatorFree` holds by construction |
| L7 | A hole is lexed as a placeholder word (U+E000 and its number); a wording that contains U+E000 gives no rule | a mark next to a hole keeps the spacing flags a term gives it |
| L8 | The object relative is the wording with ` {1}` deleted, lexed again; its value is `pred p [t, var 0]` | Lark's and the hand parser's cut (`english.py:1056`, `:1926`) |
| L9 | The copula rules need a selected noun for the sort, as the natural-subject rules do | `_natural_grammar` builds all three under that condition (`english.py:1946–1950`) |
| L10 | `typedDocument` calls the layer-2 decoders that `VE.Service.Standalone.decodeTyped` and `legacyTyped` call, family by family, without `validated`'s statement-profile relaxations | `VE.Service` is layer 4, which `VE.EnglishGrammar` (layer 3) may not import; those relaxations concern profiles outside the base profile |
| L11 | `Env.decode` applies the English vocabulary overlay (nouns, wordings with their negatives, constant displays), so `read` is called with the empty `Overlay` | Python's lexical view is the display environment (`conformance/english_lean_lexicon.py`, `lexical_view`) |
| L12 | `listMarkers` checks the first marker, reads the first clause, then checks the second marker | the hand parser's order (`english.py:1413–1419`): a rejection inside the first clause is reported before a wrong second marker |
| L13 | `nest` compares with the literal 64 | Python's `MAX_DEPTH` (`ve/limits.py`); the frozen formula decoders use the same literal (`VE.Bridge.decodeFormula 64`) |
| L14 | `pred p order negated` places arguments in declaration order, as spec 2.7 says | the hand parser takes written order (`english.py:1082–1097`); the two differ only for `{1}`-first wordings, which `TEMPLATE_SHAPE` keeps out of Python's lexicons (`Bob alice are related.` gives `related(alice, bob)` in Lean). The open candidate of the third verification pass, for the DRI |

## 3. Proofs

`grammar_extension` maps a fixed rule to itself and a lexical rule to the first rule of the larger grammar with the
same row (`extensionMap`). The proof shows every lexical row of `E`, `L` is a row of `E2`, `L2` family by family
(`lexRowsAll_sub`), then injectivity from the rows having no repeats (`lexRows_nodup`). The readers' statements
come from the engine's `doc_sound`, `doc_complete`, `doc_stopped`, `doc_unique`, `readings_exact` and
`sem_total`. `lean/audit.py` lists 34 new theorems; the fourteen of spec 5.6 depend on `propext`,
`Classical.choice` and `Quot.sound` at most.

## 4. Not done

| Item | State | Needs |
|---|---|---|
| S2.4: `EnglishMain.lean`, `ve_english_route`, modes `english.read` and `english.grammar`, the six identities, the export of spec 4.4 | not started | `grammar_id` hashes S2.0's JSON source and `actions_version` is S2.0's `LOCK.json`; the response's `canonical` field needs a decision: a Lean port of Python's printer, or the adapter renders Lean's `ast` with the printer (one owner) |
| The rejection texts of spec 3.2 | not in Lean | S2.4 or the adapter |
| G2, the reverse corpus, mutation replay, the owed budgets | S2.6 | Python implementer |
| The DRI's rulings on Q2 (the four codes), Q5 (`kwMid`), Q6 (V3) | implemented as proposed | DRI |
