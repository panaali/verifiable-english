# refusal-number-build-1126: user-visible delta

Row plain-vocab-refusal-number-1126. Design reviews/refusal-number-design-1126.md (manage-agents; Codex design
challenge 0 SERIOUS, reviews/refusal-number-design-challenge-1126.md); orchestrator ruling 2026-11-26T21:02Z
(inbox/dri/done/20261126T210203Z-orchestrator-137562.md: Lean writes every sentence number, hard stop at 10 measured
trusted lines).

**What changes.** A document's English fence was read alone (`Service/Document.lean` `contentOf`, and Python's own
path `ve/document/load.py`), so a refused fence's text always said "Sentence 1", whichever fence it was. Now
`english.read` takes an optional `sentence_base` (a natural number, the sentences before the source; absent = 0), and
every per-sentence refusal text of authoring mode counts from it: NoDerivation, Ambiguous, every sentence rejection
(and a lexical `EmptySentence`), ConclusionWithoutPremise, IllTyped and Budget. The `sentence` field, the spans, the
diagnosis and the advice still index the source sent. `contentOf` sends the fence's index in the body (the order of
the ```` ```ve ```` fences, `Loader.bodyScan`); Python's own path sends the same index from the same order
(`list(fences).index(unit id)`, only when it is not 0); Python never edits Lean's text.

| before (3-fence document, 2nd fence unreadable) | after |
| --- | --- |
| `SyntaxError: Sentence 1 has no reading with the current vocabulary. ...` | `SyntaxError: Sentence 2 has no reading with the current vocabulary. ...` |

Unchanged: the first fence's text, a single-fence document's text, every request without the field (translation
mode, `senses.read`, every other caller), the texts that name no sentence (UndeclaredEvaluative, the other lexical
texts). `english.grammar`, `english.check` and `english.question` refuse the field as an unknown field (it is
`english.read`'s alone, as `judgments` is; jt-3 review F1), so it is read in `readCase`, not `optionalFields`.
Known limit (design (a)): the number counts each earlier fence as one sentence, which the loader enforces for every
fence it accepts ("each VE fence must contain exactly one sentence"). The senses route's numbering under
`senses.defaults` is not in this item (row senses-defaults-sentence-number).

Generated files that move: the grammar `actions_version` 50 -> 51 (`Fixed/Version.lean`, `ve/english_grammar/LOCK.json`:
`EnglishGrammar/Run.lean` is a hashed file), checker pins, lean/declarations.txt and the other outputs of
`tools/regen_generated.py --write`.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | `VE/EnglishGrammar/Run.lean`: **+5 V** (measured, `tools/trust_map.py --since main` on the final HEAD): `readCase` +3 (reads `sentence_base`; the field list entry is a changed line), `authoring` +2 (the `EmptySentence` shift) and changed lines passing `base` (`budgetFields` 0, 1 changed). Diagnostic-only G[R] (not counted): `noReadingFields`, `rejectionText`. No new definition. K +0, S +0. | R16 | tests/test_refusal_sentence_number.py; `#guard`s in lean/VE/EnglishGrammar/JudgmentRunExamples.lean |
| 2 | `VE/Service/Document.lean`: **+1 V** (measured): `contentOf` sends the fence's index (`(fences.map Prod.fst).idxOf id`). | R16 | tests/test_refusal_sentence_number.py (Lean document mode) |

R16 ties pass: asked for in manage-agents FOLLOW-UPS.md ("## refusal-number-build-1126").
