# Question answering Q2.4: the ledger of moved wording

Plan 5 and Q2.4: each Python site this batch deletes or turns into a relay, with the Lean definition that owns it
now. Lean words these lines through the `words` service mode (`VE.Words.Run`); Python asks for them with
`ve/words.py` (in `tools/relay_lint.py`'s `RELAYED`). `tests/test_words.py::test_the_python_producers_are_gone`
checks that every deleted producer stays deleted; the relay lint's wording rule refuses a new one.

| Python site (before) | Now | Lean owner |
|---|---|---|
| `ve/readings_s2_wording.py` `S2Wording.situation`, its base part (element lines, author facts, `nothing exists`) | deleted; `S2Wording.shown_situation` relays Lean's line and keeps the suppositions | `VE.Words.situationText` (`words` item `situation`) |
| `ve/readings_route.py` `Wording.situation_text`, its base part | relays Lean's line and keeps the suppositions | `VE.Words.situationText` |
| `ve/readings_route.py` `_article` | deleted | `VE.Words.articleBySound` |
| `ve/readings_s2_wording.py` `filled_gaps`, `S2Wording.plan_gaps` (each point's clause) | relay Lean's clause and filled-gap sentence; which points are shown stays the caller's | `VE.Words.clauseAt`, `VE.Words.fillingSentence` (items `point`, `filling`) |
| `ve/readings_s2_english.py` `gap_sentences` | deleted; `shown_gaps` joins Lean's sentences after the situation | `VE.Words.fillingSentence` |
| `ve/norm_defaults_english.py` `point_clause`, `element_name` and `_negative_modal` | deleted; `_clauses` relays Lean's clauses | `VE.Words.clauseAt`, `VE.Words.nameOf`, `VE.Words.constantName` |
| `ve/norm_defaults_english.py` `filling_sentence` | deleted | `VE.Words.fillingSentence` |
| `ve/norm_english.py` `pair_sentence` (the legend's pair sentence and the readings P1 line) | deleted; `_pair_sentences` and `S2Wording.pair_premise` relay Lean's | `VE.Words.pairSentence`, `VE.Words.bindings` |
| `ve/norm_defaults.py` `fill_description` | deleted; the filled vocabulary takes the elaboration row's `unsaid[].description` | `VE.NormDefaults.unsaidDescription` (DELTA D14) |

What stays Python's, and why (each is listed in `tools/relay_lint.py`'s `WORDING_FRAMES`):

| Site | Why |
|---|---|
| `norm_defaults_english.status_sentence`, `_inherited_reason`, `latent_conflict_sentence`, `gap_sentence` | frames around Lean's clause, Python's until their own move (plan 5) |
| `norm_defaults_english._completion_clause`, `silence_sentence`, `constant_name` | the legend's own sentences (norm-defaults 4.1), outside Q2.4's list |
| `norm_defaults_english.legend_grammar`; `readings_s2_english`'s `_GAPS` and R7 production | gates' grammars, which read Lean's lines back and word nothing |
| `readings_s2_english.result_sentence` (R7) | a frame around Lean's clause |
| the soft and rights suppositions (`suppose …`) of both readings situations | plan 4.5: they move with the batch that brings those chains into Q2's scope |
